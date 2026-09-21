#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
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
    if tariff.get("paid") is True and tariff.get("verified_current") is not True:
        raise ContractError("paid campaigns require a verified-current tariff basis")
    if tariff.get("paid") is False and tariff.get("verified_current") not in {True, False}:
        raise ContractError("free/model tariff basis must state verified_current explicitly")
    if permit["dispatch_class"] == "MODEL_ONLY" and tariff.get("paid") is True:
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
    if attempt.get("terminal_reason") not in ALLOWED_TERMINALS:
        raise ContractError("unknown terminal reason")
    for key in ("attempt_id", "started_utc", "finished_utc", "stdout_sha256", "stderr_sha256"):
        _require_text(attempt, key)
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


def append_attempt(path: Path, attempt: dict[str, Any], permit: dict[str, Any], plan: dict[str, Any]) -> None:
    validate_attempt(attempt, permit, plan)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = canonical_bytes(attempt) + b"\n"
    with path.open("ab", buffering=0) as fh:
        fh.write(line)
        os.fsync(fh.fileno())


def load_ledger(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            raw = raw.strip()
            if not raw:
                raise ContractError(f"blank ledger line {lineno}")
            item = json.loads(raw)
            canonical_bytes(item)
            out.append(item)
    return out


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
    sp.add_parser("self-test")
    args = ap.parse_args()
    if args.cmd == "self-test":
        self_test()
        print("MC-045 campaign harness self-test passed")
        return 0
    permit = load_json(args.permit)
    plan = load_json(args.plan)
    validate_plan(permit, plan, allow_native=args.allow_native)
    if args.cmd == "account":
        print(json.dumps(accounting_summary(permit, plan), sort_keys=True))
    else:
        print("campaign plan is permit-bound and admitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
