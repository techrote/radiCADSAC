#!/usr/bin/env python3
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
import stat
import subprocess
import tempfile
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

PERMIT_SCHEMA = "radicadsac-mc-native-permit/1.0"
PLAN_SCHEMA = "radicadsac-mc-campaign-plan/1.0"
ATTEMPT_SCHEMA = "radicadsac-mc-campaign-attempt/1.0"
ALLOWED_DISPATCH = {"MODEL_ONLY", "NATIVE_BOUNDED"}
ALLOWED_TERMINALS = {
    "SUCCEEDED", "TIMEOUT", "RESOURCE_EXHAUSTED", "REJECTED",
    "ERROR", "CRASH", "NOT_EXECUTED", "INCOMPLETE",
}
NONPASS_TERMINALS = ALLOWED_TERMINALS - {"SUCCEEDED"}
PLACEHOLDERS = {"", "TODO", "TBD", "UNKNOWN", "PENDING", "NONE", "N/A"}
BINDINGS = (
    "permit_id", "source_sha", "candidate_config_digest",
    "fixture_profile_digest", "platform_id",
)
POS_INT_FIELDS = (
    "allocated_vcpus", "max_processes", "threads_per_process", "max_jobs",
    "sequential_repeats", "timeout_seconds", "peak_rss_bytes_max",
    "storage_bytes_max", "egress_bytes_max",
)

class ContractError(ValueError):
    pass


def canonical_bytes(obj: Any) -> bytes:
    def reject_float(value: Any) -> None:
        if isinstance(value, float):
            raise ContractError("binary float forbidden in campaign authority objects")
        if isinstance(value, dict):
            for v in value.values():
                reject_float(v)
        elif isinstance(value, list):
            for v in value:
                reject_float(v)
    reject_float(obj)
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(obj)).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def is_sha256_digest(value: Any) -> bool:
    """Require canonical lowercase SHA-256 evidence digests, not arbitrary text."""
    return (
        isinstance(value, str)
        and len(value) == 71
        and value.startswith("sha256:")
        and all(char in "0123456789abcdef" for char in value[7:])
    )


def _require_text(obj: dict[str, Any], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{key} must be non-empty text")
    return value


def _require_pos_int(obj: dict[str, Any], key: str) -> int:
    value = obj.get(key)
    if type(value) is not int or value <= 0:
        raise ContractError(f"{key} must be a positive integer")
    return value


def validate_permit(permit: dict[str, Any], *, allow_native: bool = False) -> None:
    canonical_bytes(permit)
    if permit.get("schema") != PERMIT_SCHEMA:
        raise ContractError("permit schema mismatch")
    if permit.get("programme") != "MC-1":
        raise ContractError("permit programme mismatch")
    _require_text(permit, "permit_id")
    _require_text(permit, "owner_task")
    dispatch = _require_text(permit, "dispatch_class")
    if dispatch not in ALLOWED_DISPATCH:
        raise ContractError("unsupported dispatch class")
    if dispatch == "NATIVE_BOUNDED" and not allow_native:
        raise ContractError("native dispatch requires an explicit caller opt-in in addition to the permit")
    if permit.get("approval_authority") != "MC-1-programme":
        raise ContractError("approval authority mismatch")
    approval = _require_text(permit, "approval_evidence").strip().upper()
    if approval in PLACEHOLDERS:
        raise ContractError("placeholder approval evidence is not authority")
    for key in ("source_sha", "candidate_config_digest", "fixture_profile_digest", "platform_id", "retention_path"):
        _require_text(permit, key)
    for key in POS_INT_FIELDS:
        _require_pos_int(permit, key)
    if permit["max_processes"] * permit["threads_per_process"] > permit["allocated_vcpus"]:
        raise ContractError("nested process/thread plan oversubscribes allocated vCPUs")
    if type(permit.get("expensive_campaign_lock")) is not str or permit["expensive_campaign_lock"] != "HELD_BY_THIS_PERMIT":
        raise ContractError("expensive-campaign lock mismatch")
    if not isinstance(permit.get("stop_rules"), list) or not permit["stop_rules"]:
        raise ContractError("stop_rules must be a non-empty list")
    if not all(isinstance(x, str) and x.strip() for x in permit["stop_rules"]):
        raise ContractError("stop_rules entries must be non-empty strings")
    tariff = permit.get("tariff_basis")
    if not isinstance(tariff, dict):
        raise ContractError("tariff_basis must be an object")
    # JSON numbers compare equal to booleans in Python (0 == False, 1 == True).
    # Missing or malformed tariff flags must never bypass admission checks.
    if type(tariff.get("paid")) is not bool:
        raise ContractError("tariff_basis.paid must be an explicit boolean")
    if type(tariff.get("verified_current")) is not bool:
        raise ContractError("tariff_basis.verified_current must be an explicit boolean")
    if tariff["paid"] and not tariff["verified_current"]:
        raise ContractError("paid campaigns require a verified-current tariff basis")
    if permit["dispatch_class"] == "MODEL_ONLY" and tariff["paid"]:
        raise ContractError("MODEL_ONLY self-tests cannot consume paid dispatch")


def validate_plan(permit: dict[str, Any], plan: dict[str, Any], *, allow_native: bool = False) -> None:
    validate_permit(permit, allow_native=allow_native)
    canonical_bytes(plan)
    if plan.get("schema") != PLAN_SCHEMA:
        raise ContractError("plan schema mismatch")
    for key in BINDINGS:
        if plan.get(key) != permit.get(key):
            raise ContractError(f"plan/permit binding mismatch: {key}")
    command = plan.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
        raise ContractError("command must be a non-empty argv string array")
    if plan.get("shell") is not False:
        raise ContractError("shell execution is forbidden")
    if plan.get("parallel_repeats") is not False:
        raise ContractError("parallel repeat copies are forbidden")
    repeats = _require_pos_int(plan, "sequential_repeats")
    if repeats != permit["sequential_repeats"]:
        raise ContractError("repeat count must match permit exactly")
    max_jobs = _require_pos_int(plan, "max_jobs")
    if max_jobs > permit["max_jobs"]:
        raise ContractError("job count exceeds permit")
    max_processes = _require_pos_int(plan, "max_processes")
    threads = _require_pos_int(plan, "threads_per_process")
    if max_processes > permit["max_processes"] or threads > permit["threads_per_process"]:
        raise ContractError("nested parallelism exceeds permit")
    if max_processes * threads > permit["allocated_vcpus"]:
        raise ContractError("nested parallelism oversubscribes allocated vCPUs")
    for key in ("timeout_seconds", "peak_rss_bytes_max", "storage_bytes_max", "egress_bytes_max"):
        value = _require_pos_int(plan, key)
        if value > permit[key]:
            raise ContractError(f"{key} exceeds permit")
    env = plan.get("environment", {})
    if not isinstance(env, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in env.items()):
        raise ContractError("environment must be a string:string object")


def reserved_vcpu_seconds(permit: dict[str, Any], plan: dict[str, Any]) -> int:
    validate_plan(permit, plan, allow_native=(permit.get("dispatch_class") == "NATIVE_BOUNDED"))
    return permit["allocated_vcpus"] * plan["timeout_seconds"] * plan["max_jobs"] * plan["sequential_repeats"]


def reserved_vcpu_minutes_fraction(permit: dict[str, Any], plan: dict[str, Any]) -> Fraction:
    return Fraction(reserved_vcpu_seconds(permit, plan), 60)


def accounting_summary(permit: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    value = reserved_vcpu_minutes_fraction(permit, plan)
    return {
        "reserved_vcpu_seconds": reserved_vcpu_seconds(permit, plan),
        "reserved_vcpu_minutes": {"numerator": value.numerator, "denominator": value.denominator},
        "allocated_vcpus": permit["allocated_vcpus"],
        "jobs": plan["max_jobs"],
        "sequential_repeats": plan["sequential_repeats"],
        "timeout_seconds": plan["timeout_seconds"],
    }


def validate_attempt(attempt: dict[str, Any], permit: dict[str, Any], plan: dict[str, Any]) -> None:
    canonical_bytes(attempt)
    if attempt.get("schema") != ATTEMPT_SCHEMA:
        raise ContractError("attempt schema mismatch")
    for key in BINDINGS:
        if attempt.get(key) != permit.get(key):
            raise ContractError(f"attempt/permit binding mismatch: {key}")
    terminal = attempt.get("terminal_reason")
    if not isinstance(terminal, str) or terminal not in ALLOWED_TERMINALS:
        raise ContractError("unknown terminal reason")
    for key in ("attempt_id", "started_utc", "finished_utc", "stdout_sha256", "stderr_sha256"):
        _require_text(attempt, key)
    for key in ("stdout_sha256", "stderr_sha256"):
        if not is_sha256_digest(attempt[key]):
            raise ContractError(f"{key} must be a canonical sha256 digest")
    if "return_code" not in attempt:
        raise ContractError("return_code must be recorded (integer or null)")
    return_code = attempt["return_code"]
    if return_code is not None and type(return_code) is not int:
        raise ContractError("return_code must be an integer or null")
    if terminal == "SUCCEEDED" and return_code != 0:
        raise ContractError("SUCCEEDED requires a zero process return_code")
    for key in ("repeat_index", "job_index", "wall_time_ns", "cpu_time_ns", "allocated_vcpus", "observed_peak_rss_bytes", "output_bytes", "storage_bytes", "egress_bytes"):
        value = attempt.get(key)
        if type(value) is not int or value < 0:
            raise ContractError(f"{key} must be a non-negative integer")
    if attempt["repeat_index"] >= plan["sequential_repeats"]:
        raise ContractError("repeat index outside plan")
    if attempt["job_index"] >= plan["max_jobs"]:
        raise ContractError("job index outside plan")
    if attempt["allocated_vcpus"] != permit["allocated_vcpus"]:
        raise ContractError("attempt allocated_vcpus drift")
    if attempt["observed_peak_rss_bytes"] > plan["peak_rss_bytes_max"]:
        if attempt["terminal_reason"] != "RESOURCE_EXHAUSTED":
            raise ContractError("memory cap violation must be RESOURCE_EXHAUSTED")
    if attempt["storage_bytes"] > plan["storage_bytes_max"] or attempt["egress_bytes"] > plan["egress_bytes_max"]:
        if attempt["terminal_reason"] != "RESOURCE_EXHAUSTED":
            raise ContractError("storage/egress cap violation must be RESOURCE_EXHAUSTED")
    if attempt["terminal_reason"] != "SUCCEEDED" and attempt.get("programme_pass") is True:
        raise ContractError("non-success terminal cannot be promoted to PASS")
    if attempt.get("programme_pass") is not None and type(attempt.get("programme_pass")) is not bool:
        raise ContractError("programme_pass, if present, must be boolean")



def validate_ledger_sequence(
    rows: list[dict[str, Any]], permit: dict[str, Any], plan: dict[str, Any],
    *, require_complete: bool = False, allow_native: bool = False,
) -> None:
    """Validate a strict ordered-repeat prefix; job completions may interleave within one repeat.

    This is an integrity check, not a dispatch authorization or an MC-1 verdict.
    A partial last repeat is retained as evidence, but cannot be followed by a
    later repeat. At most one terminal row is admitted per (repeat, job) slot.
    """
    validate_plan(permit, plan, allow_native=allow_native)
    if not isinstance(rows, list):
        raise ContractError("ledger must be a list of attempts")
    jobs = _require_pos_int(plan, "max_jobs")
    repeats = _require_pos_int(plan, "sequential_repeats")
    expected = jobs * repeats
    if len(rows) > expected:
        raise ContractError("ledger exceeds permit-bound attempt slots")
    ids: set[str] = set()
    slots: set[tuple[int, int]] = set()
    for position, attempt in enumerate(rows):
        if not isinstance(attempt, dict):
            raise ContractError(f"ledger row {position} must be an object")
        validate_attempt(attempt, permit, plan)
        attempt_id = attempt["attempt_id"]
        slot = (attempt["repeat_index"], attempt["job_index"])
        if attempt_id in ids:
            raise ContractError(f"duplicate attempt_id in ledger row {position}")
        if slot in slots:
            raise ContractError(f"duplicate repeat/job slot in ledger row {position}")
        if attempt["repeat_index"] != position // jobs:
            raise ContractError(f"skipped or reordered repeat group at ledger row {position}")
        ids.add(attempt_id)
        slots.add(slot)
    if require_complete and len(rows) != expected:
        raise ContractError("incomplete ledger cannot claim full planned execution")


def sha256_file(path: Path) -> str:
    """Stream retained bytes in bounded chunks rather than materializing whole captures."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def verify_retained_captures(rows: list[dict[str, Any]], capture_dir: Path) -> None:
    """Independently hash retained stdout/stderr bytes, indexed by ledger row.

    Each row i requires i:06d.stdout.bin and i:06d.stderr.bin. Index-derived
    filenames deliberately do not trust user-controlled attempt IDs as paths.
    This binds stored bytes to recorded digests, not to an external attestor.
    """
    if capture_dir.is_symlink() or not capture_dir.is_dir():
        raise ContractError("retained capture directory missing or a symlink")
    expected: set[str] = set()
    identities: set[tuple[int, int]] = set()
    for position, attempt in enumerate(rows):
        for stream in ("stdout", "stderr"):
            name = f"{position:06d}.{stream}.bin"
            expected.add(name)
            capture = capture_dir / name
            try:
                metadata = capture.lstat()
            except OSError as exc:
                raise ContractError(f"missing or inaccessible capture: {name}") from exc
            # An lstat snapshot refuses symlinks and special files without
            # following them. Identical hashes do NOT imply separate custody.
            # This is a static alias check, not protection against concurrent
            # replacement between lstat and the streaming read.
            if not stat.S_ISREG(metadata.st_mode):
                raise ContractError(f"non-regular or symlinked capture: {name}")
            if not metadata.st_ino:
                raise ContractError(f"capture filesystem identity unavailable: {name}")
            # A hard link outside the audited inventory is also unsafe:
            # duplicates *within* this directory are not the only aliases.
            if metadata.st_nlink != 1:
                raise ContractError(f"hard-linked retained capture (link count != 1): {name}")
            identity = (metadata.st_dev, metadata.st_ino)
            if identity in identities:
                raise ContractError(f"hard-linked retained capture alias: {name}")
            identities.add(identity)
            if sha256_file(capture) != attempt[f"{stream}_sha256"]:
                raise ContractError(f"retained capture digest mismatch: {name}")
    actual = {entry.name for entry in capture_dir.iterdir()}
    if actual != expected:
        raise ContractError("retained capture inventory has missing or unexpected paths")


@contextmanager
def exclusive_ledger_append_lock(path: Path):
    """Serialize cooperating appenders; a stale/contended lock refuses admission.

    The adjacent exclusive-create lock is deliberately NOT auto-reclaimed after
    a crash. This is not an atomic capture transaction, a hostile-filesystem
    security boundary, or a distributed-filesystem lease guarantee.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".append.lock")
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ContractError("ledger append locked (active or stale); no append performed") from exc
    except OSError as exc:
        raise ContractError("unable to establish exclusive ledger append lock") from exc
    identity = None
    try:
        try:
            identity = os.fstat(fd)
            os.write(fd, f"pid={os.getpid()}\n".encode("ascii"))
            os.fsync(fd)
        except OSError as exc:
            raise ContractError("ledger append lock initialization failed") from exc
        yield
    finally:
        os.close(fd)
        if identity is None:
            # Ownership cannot be proven if fstat failed. Leave the lock
            # intact for explicit manual review rather than unlinking it.
            raise ContractError("ledger append lock identity unavailable; manual audit required")
        try:
            current = lock_path.lstat()
        except OSError as exc:
            raise ContractError("ledger append lock missing during release") from exc
        if (not stat.S_ISREG(current.st_mode) or
                (current.st_dev, current.st_ino) != (identity.st_dev, identity.st_ino)):
            raise ContractError("ledger append lock replaced during ownership")
        try:
            lock_path.unlink()
        except OSError as exc:
            raise ContractError("ledger append lock release failed") from exc


def _ledger_metadata(path: Path):
    """Admission snapshot for a single, non-aliased regular ledger path.

    A file's link count can be greater than one even when its other aliases
    are outside this directory. Refuse that ambiguity before mutation.
    """
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise ContractError("unable to inspect ledger filesystem identity") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise ContractError("ledger must be a regular file, not a symlink or special file")
    if not metadata.st_ino or metadata.st_nlink != 1:
        raise ContractError("ledger must have a unique available filesystem identity")
    return metadata


def _ledger_fingerprint(metadata):
    return (metadata.st_dev, metadata.st_ino, metadata.st_nlink,
            metadata.st_size, metadata.st_mtime_ns)


def append_attempt(path: Path, attempt: dict[str, Any], permit: dict[str, Any], plan: dict[str, Any]) -> None:
    validate_attempt(attempt, permit, plan)
    # Hold one filesystem descriptor across canonical replay, sequence checking,
    # and durable append. The adjacent lock serializes cooperating processes;
    # neither this path check nor timestamps are hostile-filesystem guarantees.
    with exclusive_ledger_append_lock(path):
        before = _ledger_metadata(path)
        flags = os.O_RDWR | os.O_APPEND | getattr(os, "O_BINARY", 0)
        if before is None:
            # Never follow a newly planted symlink or overwrite a new peer.
            flags |= os.O_CREAT | os.O_EXCL
        else:
            flags |= getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(path, flags, 0o600)
        except OSError as exc:
            raise ContractError("ledger file changed or is inaccessible before append") from exc
        with os.fdopen(fd, "r+b", buffering=0) as fh:
            opened = os.fstat(fh.fileno())
            named = _ledger_metadata(path)
            if (named is None or _ledger_fingerprint(opened) != _ledger_fingerprint(named) or
                    (before is not None and (_ledger_fingerprint(before) != _ledger_fingerprint(opened)
                      or before.st_ctime_ns != named.st_ctime_ns))):
                raise ContractError("ledger identity changed before replay")
            # On Windows fstat and lstat may report different change-time
            # conventions for the same open file. Compare ctime only within
            # the same observation route, never across the two interfaces.
            named_ctime = named.st_ctime_ns
            fh.seek(0)
            prior, _digest = _parse_ledger_stream(fh)
            validate_ledger_sequence(
                prior + [attempt], permit, plan,
                allow_native=(permit.get("dispatch_class") == "NATIVE_BOUNDED"),
            )
            # Detect a name swap, a link-count change, or a normal concurrent
            # in-place modification during replay before any append occurs.
            after = os.fstat(fh.fileno())
            named = _ledger_metadata(path)
            if (named is None or _ledger_fingerprint(after) != _ledger_fingerprint(opened)
                    or _ledger_fingerprint(after) != _ledger_fingerprint(named)
                    or after.st_ctime_ns != opened.st_ctime_ns
                    or named.st_ctime_ns != named_ctime):
                raise ContractError("ledger identity or contents changed during replay")
            line = canonical_bytes(attempt) + b"\n"
            fh.seek(0, os.SEEK_END)
            if fh.write(line) != len(line):
                raise ContractError("short durable ledger append; manual recovery required")
            os.fsync(fh.fileno())


def _parse_ledger_stream(fh) -> tuple[list[dict[str, Any]], str]:
    """Canonical JSONL parse and custody hash from the exact open descriptor."""
    out: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    for lineno, raw in enumerate(fh, 1):
        digest.update(raw)
        if not raw.endswith(b"\n"):
            raise ContractError(f"unterminated ledger line {lineno}")
        try:
            item = json.loads(raw)
            if not isinstance(item, dict) or raw != canonical_bytes(item) + b"\n":
                raise ContractError(f"noncanonical ledger line {lineno}")
        except (ValueError, UnicodeError) as exc:
            raise ContractError(f"invalid ledger line {lineno}") from exc
        out.append(item)
    return out, "sha256:" + digest.hexdigest()


def load_ledger_with_digest(path: Path) -> tuple[list[dict[str, Any]], str]:
    """Read-only strict parser; append uses the same parser on its held descriptor."""
    with path.open("rb") as fh:
        return _parse_ledger_stream(fh)


def load_ledger(path: Path) -> list[dict[str, Any]]:
    """Backward-compatible strict reader for append and deterministic controls."""
    return load_ledger_with_digest(path)[0]


def _attempt(permit: dict[str, Any], plan: dict[str, Any], repeat_index: int, job_index: int, terminal: str, *, peak: int = 0, storage: int = 0, egress: int = 0, return_code: int | None = 0) -> dict[str, Any]:
    stamp = f"2026-09-21T00:00:{repeat_index * plan['max_jobs'] + job_index:02d}Z"
    return {
        "schema": ATTEMPT_SCHEMA,
        "attempt_id": f"selftest-r{repeat_index}-j{job_index}",
        "permit_id": permit["permit_id"],
        "repeat_index": repeat_index,
        "job_index": job_index,
        "terminal_reason": terminal,
        "started_utc": stamp,
        "finished_utc": stamp,
        "wall_time_ns": 1,
        "cpu_time_ns": 1,
        "allocated_vcpus": permit["allocated_vcpus"],
        "observed_peak_rss_bytes": peak,
        "output_bytes": 0,
        "storage_bytes": storage,
        "egress_bytes": egress,
        "return_code": return_code,
        "stdout_sha256": sha256_bytes(b""),
        "stderr_sha256": sha256_bytes(b""),
        "source_sha": permit["source_sha"],
        "candidate_config_digest": permit["candidate_config_digest"],
        "fixture_profile_digest": permit["fixture_profile_digest"],
        "platform_id": permit["platform_id"],
        "programme_pass": terminal == "SUCCEEDED",
    }


def self_test() -> None:
    permit = {
        "schema": PERMIT_SCHEMA,
        "permit_id": "MC045-SELFTEST-001",
        "programme": "MC-1",
        "owner_task": "MC-045",
        "dispatch_class": "MODEL_ONLY",
        "approval_authority": "MC-1-programme",
        "approval_evidence": "repository-reviewed MC-045 deterministic self-test only; no native or paid dispatch",
        "source_sha": "0" * 40,
        "candidate_config_digest": "sha256:" + "1" * 64,
        "fixture_profile_digest": "sha256:" + "2" * 64,
        "platform_id": "MC045-LOCAL-MODEL",
        "allocated_vcpus": 4,
        "max_processes": 2,
        "threads_per_process": 2,
        "max_jobs": 1,
        "sequential_repeats": 3,
        "timeout_seconds": 10,
        "peak_rss_bytes_max": 1024,
        "storage_bytes_max": 2048,
        "egress_bytes_max": 1024,
        "tariff_basis": {"paid": False, "verified_current": False, "basis": "no provider dispatch"},
        "retention_path": "synthetic-self-test-ledger.jsonl",
        "stop_rules": ["binding mismatch", "resource cap", "lost ledger"],
        "expensive_campaign_lock": "HELD_BY_THIS_PERMIT",
    }
    plan = {
        "schema": PLAN_SCHEMA,
        "permit_id": permit["permit_id"],
        "source_sha": permit["source_sha"],
        "candidate_config_digest": permit["candidate_config_digest"],
        "fixture_profile_digest": permit["fixture_profile_digest"],
        "platform_id": permit["platform_id"],
        "command": ["python3", "-c", "print('model-only')"],
        "shell": False,
        "parallel_repeats": False,
        "sequential_repeats": 3,
        "max_jobs": 1,
        "max_processes": 2,
        "threads_per_process": 2,
        "timeout_seconds": 10,
        "peak_rss_bytes_max": 1024,
        "storage_bytes_max": 2048,
        "egress_bytes_max": 1024,
        "environment": {},
    }
    validate_plan(permit, plan)
    assert accounting_summary(permit, plan)["reserved_vcpu_seconds"] == 120
    assert reserved_vcpu_minutes_fraction(permit, plan) == Fraction(2, 1)

    def must_reject(mutator):
        p = json.loads(json.dumps(permit))
        q = json.loads(json.dumps(plan))
        mutator(p, q)
        try:
            validate_plan(p, q)
        except ContractError:
            return
        raise AssertionError("adversarial mutation was accepted")

    must_reject(lambda p, q: p.update({"approval_evidence": "TBD"}))
    must_reject(lambda p, q: q.update({"source_sha": "f" * 40}))
    must_reject(lambda p, q: q.update({"parallel_repeats": True}))
    must_reject(lambda p, q: q.update({"max_processes": 3}))
    must_reject(lambda p, q: q.update({"timeout_seconds": 11}))
    must_reject(lambda p, q: q.update({"peak_rss_bytes_max": 1025}))
    must_reject(lambda p, q: q.update({"storage_bytes_max": 2049}))
    must_reject(lambda p, q: q.update({"egress_bytes_max": 1025}))
    must_reject(lambda p, q: p.update({"expensive_campaign_lock": "FREE"}))
    must_reject(lambda p, q: p.update({"tariff_basis": {"paid": True, "verified_current": False, "basis": "guessed"}}))

    # Tariff flags are exact JSON booleans, not truthy/falsy values or numbers.
    # Missing paid previously bypassed every branch; numeric 0/1 previously
    # impersonated False/True in verified_current membership comparisons.
    for bad in (None, 0, 1, -1, "false", "true", [], {}, [False]):
        must_reject(lambda p, q, value=bad: p["tariff_basis"].__setitem__("paid", value))
        must_reject(lambda p, q, value=bad: p["tariff_basis"].__setitem__("verified_current", value))
    must_reject(lambda p, q: p["tariff_basis"].pop("paid"))
    must_reject(lambda p, q: p["tariff_basis"].pop("verified_current"))
    must_reject(lambda p, q: p.update({"tariff_basis": []}))
    must_reject(lambda p, q: p["tariff_basis"].update({"paid": True, "verified_current": True}))

    # Canonical free MODEL_ONLY permits legitimately record either current
    # verified-free tariff data or an explicitly unverified free/no-dispatch basis.
    verified_free = json.loads(json.dumps(permit))
    verified_free["tariff_basis"]["verified_current"] = True
    validate_plan(verified_free, plan)

    with tempfile.TemporaryDirectory() as td:
        ledger = Path(td) / "attempts.jsonl"
        for repeat in range(3):
            append_attempt(ledger, _attempt(permit, plan, repeat, 0, "SUCCEEDED"), permit, plan)
        rows = load_ledger(ledger)
        assert [x["repeat_index"] for x in rows] == [0, 1, 2]
        assert all(x["terminal_reason"] == "SUCCEEDED" for x in rows)

        fault_ledger = Path(td) / "faults.jsonl"
        append_attempt(fault_ledger, _attempt(permit, plan, 0, 0, "TIMEOUT", return_code=None), permit, plan)
        append_attempt(fault_ledger, _attempt(permit, plan, 1, 0, "RESOURCE_EXHAUSTED", peak=1025), permit, plan)
        append_attempt(fault_ledger, _attempt(permit, plan, 2, 0, "CRASH", return_code=139), permit, plan)
        faults = load_ledger(fault_ledger)
        assert [x["terminal_reason"] for x in faults] == ["TIMEOUT", "RESOURCE_EXHAUSTED", "CRASH"]
        assert all(x["programme_pass"] is False for x in faults)

    # An attempt marked SUCCEEDED cannot carry a failed/unknown process exit
    # or unverifiable stdout/stderr identities into the durable evidence ledger.
    # All controls use MODEL_ONLY synthetic data; this test never dispatches work.
    def must_reject_attempt(mutator):
        attempt = _attempt(permit, plan, 0, 0, "SUCCEEDED")
        mutator(attempt)
        try:
            validate_attempt(attempt, permit, plan)
        except ContractError:
            return
        raise AssertionError("invalid success-attempt evidence was accepted")

    must_reject_attempt(lambda a: a.update({"return_code": 1}))
    must_reject_attempt(lambda a: a.update({"return_code": None}))
    must_reject_attempt(lambda a: a.pop("return_code"))
    must_reject_attempt(lambda a: a.update({"return_code": True}))
    must_reject_attempt(lambda a: a.update({"return_code": "0"}))
    must_reject_attempt(lambda a: a.update({"stdout_sha256": "unknown"}))
    must_reject_attempt(lambda a: a.update({"stdout_sha256": "sha256:" + "g" * 64}))
    must_reject_attempt(lambda a: a.update({"stdout_sha256": "sha256:" + "A" * 64}))
    must_reject_attempt(lambda a: a.update({"stderr_sha256": "sha256:" + "0" * 63}))
    must_reject_attempt(lambda a: a.update({"stderr_sha256": None}))
    must_reject_attempt(lambda a: a.pop("stderr_sha256"))
    must_reject_attempt(lambda a: a.update({"terminal_reason": []}))
    must_reject_attempt(lambda a: a.update({"terminal_reason": "NOT_A_TERMINAL"}))

    # Process execution and programme acceptance are distinct: a zero-exit
    # process may still fail the evidence/certificate check.
    observed = _attempt(permit, plan, 0, 0, "SUCCEEDED")
    observed["programme_pass"] = False
    validate_attempt(observed, permit, plan)
    failed = _attempt(permit, plan, 0, 0, "CRASH", return_code=139)
    validate_attempt(failed, permit, plan)
    failed["return_code"] = ["invalid"]
    try:
        validate_attempt(failed, permit, plan)
    except ContractError:
        pass
    else:
        raise AssertionError("non-integer failure return_code was accepted")


    # MC-045 ledger replay/control qualification. All records and captured bytes
    # are synthetic; no subprocess or native geometry is executed here.
    canonical_rows = [_attempt(permit, plan, i, 0, "SUCCEEDED") for i in range(3)]
    validate_ledger_sequence(canonical_rows, permit, plan, require_complete=True)
    validate_ledger_sequence(canonical_rows[:2], permit, plan)
    def reject_rows(rows, *, complete=False):
        try:
            validate_ledger_sequence(rows, permit, plan, require_complete=complete)
        except ContractError:
            return
        raise AssertionError("corrupt campaign ledger sequence was accepted")
    reject_rows(canonical_rows[:2], complete=True)
    reject_rows(canonical_rows + [canonical_rows[0]])
    reject_rows([canonical_rows[0], canonical_rows[0]])
    reject_rows([canonical_rows[1]])
    reject_rows([canonical_rows[0], canonical_rows[2]])
    reject_rows([canonical_rows[1], canonical_rows[0]])
    reject_rows([canonical_rows[0], dict(canonical_rows[1], attempt_id=canonical_rows[0]["attempt_id"])])
    reject_rows([canonical_rows[0], dict(canonical_rows[1], job_index=0, repeat_index=0)])
    reject_rows([canonical_rows[0], None])
    # Two jobs in the same repeat can finish in either order. Distinct repeat
    # groups must still be sequential, and incomplete prefixes remain visible.
    two_permit = json.loads(json.dumps(permit))
    two_permit["max_jobs"] = 2
    two_jobs = json.loads(json.dumps(plan))
    two_jobs["max_jobs"] = 2
    validate_plan(two_permit, two_jobs)
    alternate = [_attempt(two_permit, two_jobs, 0, 1, "SUCCEEDED"),
                 _attempt(two_permit, two_jobs, 0, 0, "TIMEOUT", return_code=None),
                 _attempt(two_permit, two_jobs, 1, 0, "CRASH", return_code=139)]
    validate_ledger_sequence(alternate, two_permit, two_jobs)
    with tempfile.TemporaryDirectory() as td:
        directory = Path(td)
        captures = directory / "captures"
        captures.mkdir()
        for position, row in enumerate(canonical_rows):
            for stream in ("stdout", "stderr"):
                (captures / f"{position:06d}.{stream}.bin").write_bytes(b"")
        verify_retained_captures(canonical_rows, captures)
        # Standalone MC-045 audit must not accept two names for one retained
        # inode even when both valid empty captures have identical digests.
        def reject_capture_alias(source: str, destination: str) -> None:
            src, dst = captures / source, captures / destination
            dst.unlink()
            os.link(src, dst)
            try:
                try:
                    verify_retained_captures(canonical_rows, captures)
                except ContractError:
                    pass
                else:
                    raise AssertionError("hard-linked retained capture alias admitted")
            finally:
                dst.unlink()
                dst.write_bytes(b"")
            verify_retained_captures(canonical_rows, captures)

        reject_capture_alias("000000.stdout.bin", "000000.stderr.bin")
        reject_capture_alias("000000.stdout.bin", "000002.stderr.bin")
        # No second name need exist *inside* the capture inventory: an
        # external hard link still exposes mutable bytes under another path.
        external_alias = directory / "unregistered-hardlink.bin"
        os.link(captures / "000000.stdout.bin", external_alias)
        try:
            try:
                verify_retained_captures(canonical_rows, captures)
            except ContractError:
                pass
            else:
                raise AssertionError("hard link outside capture inventory admitted")
        finally:
            external_alias.unlink()
        verify_retained_captures(canonical_rows, captures)
        target = captures / "000001.stdout.bin"
        target.write_bytes(b"tampered stdout")
        try:
            verify_retained_captures(canonical_rows, captures)
        except ContractError:
            pass
        else:
            raise AssertionError("altered retained stdout digest was accepted")
        target.write_bytes(b"")
        target.unlink()
        try:
            verify_retained_captures(canonical_rows, captures)
        except ContractError:
            pass
        else:
            raise AssertionError("missing captured stdout was accepted")
        target.write_bytes(b"")
        extra = captures / "unregistered.bin"
        extra.write_bytes(b"")
        try:
            verify_retained_captures(canonical_rows, captures)
        except ContractError:
            pass
        else:
            raise AssertionError("unexpected retained capture was accepted")
        extra.unlink()
        history = directory / "ledger.jsonl"
        history.write_bytes(b"".join(canonical_bytes(row) + b"\n" for row in canonical_rows))
        assert load_ledger(history) == canonical_rows
        parsed, custody_digest = load_ledger_with_digest(history)
        assert parsed == canonical_rows
        assert custody_digest == sha256_bytes(history.read_bytes())
        for corrupt in (
            canonical_bytes(canonical_rows[0]),  # torn/truncated final line
            b" " + canonical_bytes(canonical_rows[0]) + b"\n",
            b'{"attempt_id":"duplicate","attempt_id":"hidden"}\n',
            b"{}\n\n",
        ):
            history.write_bytes(corrupt)
            original = history.read_bytes()
            try:
                append_attempt(history, canonical_rows[1], permit, plan)
            except ContractError:
                pass
            else:
                raise AssertionError("append extended corrupted ledger evidence")
            assert history.read_bytes() == original
        history.write_bytes(canonical_bytes(canonical_rows[0]) + b"\n")
        try:
            append_attempt(history, canonical_rows[0], permit, plan)
        except ContractError:
            pass
        else:
            raise AssertionError("duplicate attempt append was accepted")

        # Ledger evidence must not be appended through an alias. The lock name
        # cannot independently serialize two names for one inode.
        history.write_bytes(canonical_bytes(canonical_rows[0]) + b"\n")
        aliased_prefix = history.read_bytes()
        alias = directory / "aliased-ledger.jsonl"
        os.link(history, alias)
        try:
            for target_path in (history, alias):
                try:
                    append_attempt(target_path, canonical_rows[1], permit, plan)
                except ContractError as exc:
                    assert "identity" in str(exc), f"wrong hardlink refusal: {exc}"
                else:
                    raise AssertionError("hard-linked ledger admitted an append")
            assert history.read_bytes() == aliased_prefix
        finally:
            alias.unlink()

        # Windows may require a symlink privilege. POSIX must execute this
        # control; do not silently classify a privilege skip as passing it.
        symlink = directory / "symlink-ledger.jsonl"
        try:
            symlink.symlink_to(history)
        except OSError:
            if os.name != "nt":
                raise
        else:
            try:
                try:
                    append_attempt(symlink, canonical_rows[1], permit, plan)
                except ContractError as exc:
                    assert "regular file" in str(exc), f"wrong symlink refusal: {exc}"
                else:
                    raise AssertionError("symlinked ledger admitted an append")
                assert history.read_bytes() == aliased_prefix
            finally:
                symlink.unlink()

        # Descriptor continuity must survive the parsing step. A deterministic
        # POSIX source-level fault replaces the named inode after replay; the
        # append must refuse without modifying either old or replacement bytes.
        # Windows generally blocks this rename of an open file.
        if os.name != "nt":
            saved_parser = _parse_ledger_stream
            def swapped_during_replay(stream):
                result = saved_parser(stream)
                replacement = directory / "replaced-ledger.jsonl"
                replacement.write_bytes(aliased_prefix)
                os.replace(replacement, history)
                return result
            globals()["_parse_ledger_stream"] = swapped_during_replay
            try:
                try:
                    append_attempt(history, canonical_rows[1], permit, plan)
                except ContractError as exc:
                    assert "changed during replay" in str(exc), f"wrong swap refusal: {exc}"
                else:
                    raise AssertionError("replaced ledger inode admitted an append")
                assert history.read_bytes() == aliased_prefix
            finally:
                globals()["_parse_ledger_stream"] = saved_parser
        append_attempt(history, canonical_rows[1], permit, plan)
        assert load_ledger(history) == canonical_rows[:2]
        assert not history.with_name(history.name + ".append.lock").exists()

        # The same ledger cannot be extended while another writer holds an
        # exclusive lock, even if the next attempt itself is valid. A stale
        # lock also refuses instead of guessing whether its owner is dead.
        history.write_bytes(canonical_bytes(canonical_rows[0]) + b"\n")
        lock = history.with_name(history.name + ".append.lock")
        lock.write_bytes(b"other writer or stale lock\n")
        original = history.read_bytes()
        try:
            append_attempt(history, canonical_rows[1], permit, plan)
        except ContractError:
            pass
        else:
            raise AssertionError("competing ledger append was admitted")
        assert history.read_bytes() == original
        assert lock.read_bytes() == b"other writer or stale lock\n"
        lock.unlink()
        append_attempt(history, canonical_rows[1], permit, plan)
        assert load_ledger(history) == canonical_rows[:2]
        assert not lock.exists()

        # Refusal after lock acquisition must not strand a lock or change the
        # corrupted ledger. This models interrupted/corrupted replay input.
        history.write_bytes(b"invalid ledger JSONL\n")
        original = history.read_bytes()
        try:
            append_attempt(history, canonical_rows[2], permit, plan)
        except ContractError:
            pass
        else:
            raise AssertionError("corrupt append replay was admitted")
        assert history.read_bytes() == original
        assert not lock.exists()

        # A deleted/recreated lock is not the acquired lease. The original
        # writer must refuse release and must not unlink the replacement.
        if os.name != "nt":
            # Windows normally forbids unlinking a still-open lock handle;
            # forced replacement is only an executable POSIX fault injection.
            try:
                with exclusive_ledger_append_lock(history):
                    lock.unlink()
                    lock.write_bytes(b"replacement owner\n")
            except ContractError:
                pass
            else:
                raise AssertionError("replaced ledger append lock was accepted")
            assert lock.read_bytes() == b"replacement owner\n"
            lock.unlink()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError("top-level JSON object required")
    return value


def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    v = sp.add_parser("validate")
    v.add_argument("--permit", required=True, type=Path)
    v.add_argument("--plan", required=True, type=Path)
    v.add_argument("--allow-native", action="store_true")
    a = sp.add_parser("account")
    a.add_argument("--permit", required=True, type=Path)
    a.add_argument("--plan", required=True, type=Path)
    a.add_argument("--allow-native", action="store_true")
    ledger = sp.add_parser("audit-ledger")
    ledger.add_argument("--permit", required=True, type=Path)
    ledger.add_argument("--plan", required=True, type=Path)
    ledger.add_argument("--ledger", required=True, type=Path)
    ledger.add_argument("--captures", required=True, type=Path)
    ledger.add_argument("--require-complete", action="store_true")
    ledger.add_argument("--allow-native", action="store_true")
    sp.add_parser("self-test")
    args = ap.parse_args()
    if args.cmd == "self-test":
        self_test()
        print("MC-045 campaign harness self-test passed")
        return 0
    permit = load_json(args.permit)
    plan = load_json(args.plan)
    validate_plan(permit, plan, allow_native=args.allow_native)
    if args.cmd == "audit-ledger":
        rows, custody_digest = load_ledger_with_digest(args.ledger)
        validate_ledger_sequence(
            rows, permit, plan,
            require_complete=args.require_complete,
            allow_native=args.allow_native,
        )
        verify_retained_captures(rows, args.captures)
        print(json.dumps({
            "status": "LEDGER_REPLAY_VALIDATED_NOT_NATIVE_QUALIFICATION",
            "attempt_count": len(rows),
            "complete": len(rows) == plan["max_jobs"] * plan["sequential_repeats"],
            "ledger_sha256": custody_digest,
        }, sort_keys=True))
        return 0
    if args.cmd == "account":
        print(json.dumps(accounting_summary(permit, plan), sort_keys=True))
    else:
        print("campaign plan is permit-bound and admitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
