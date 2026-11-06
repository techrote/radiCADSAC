#!/usr/bin/env python3
"""MC-047 read-only crash-window audit; synthetic evidence, no native dispatch."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Any


CORE_PATH = Path(__file__).resolve().parent.parent / "MC-045" / "campaign_harness.py"


def core_module():
    spec = importlib.util.spec_from_file_location("mc045_campaign_read_only", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("MC-045 source unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fingerprints(ledger: Path, captures: Path, entry_limit: int) -> tuple[Any, ...]:
    """Bound inventory allocation by the validated campaign's capture-slot budget.

    This is a cooperative local-directory budget, not hostile-FS atomic custody.
    """
    if type(entry_limit) is not int or entry_limit < 0:
        raise ValueError("capture inventory limit must be a nonnegative integer")
    def mark(path: Path) -> tuple[int, int, int, int, int, int, int]:
        s = path.lstat()
        # On POSIX, ctime changes for same-size rewrites even when mtime is
        # restored. On Windows ctime may mean creation time: NOT attestation.
        return (s.st_dev, s.st_ino, s.st_mode, s.st_size,
                s.st_mtime_ns, s.st_ctime_ns, s.st_nlink)

    if ledger.is_symlink() or not ledger.is_file():
        raise ValueError("ledger missing, non-file or symlinked")
    if captures.is_symlink() or not captures.is_dir():
        raise ValueError("capture directory missing or symlinked")
    ledger_mark = mark(ledger)
    # An otherwise valid JSONL file may have an external hard-link alias.
    # A digest match does not establish exclusive evidence custody.
    if (not stat.S_ISREG(ledger_mark[2]) or not ledger_mark[1] or
            ledger_mark[6] != 1):
        raise ValueError("ledger filesystem identity unavailable or hard-linked")
    identities = {(ledger_mark[0], ledger_mark[1])}
    entries = []
    for child in captures.iterdir():
        # Refuse on the (limit + 1)th directory entry BEFORE lstat and before
        # adding another tuple. This prevents materializing unbounded surplus
        # entries in an incomplete or otherwise invalid campaign inventory.
        if len(entries) >= entry_limit:
            raise ValueError("capture inventory exceeds planned slot budget")
        # Mode and identity must come from the *same* lstat snapshot. A
        # separate pre-check could approve a regular file replaced by a
        # symlink before mark() (still not a full TOCTOU defense).
        child_mark = mark(child)
        if not stat.S_ISREG(child_mark[2]):
            raise ValueError("capture inventory contains non-regular or symlinked entry")
        identity = (child_mark[0], child_mark[1])
        if identity in identities:
            raise ValueError("ledger/capture inventory contains hard-linked file aliases")
        identities.add(identity)
        entries.append((child.name, child_mark))
    return (ledger_mark, mark(captures), tuple(sorted(entries)))


def audit(permit: dict[str, Any], plan: dict[str, Any], ledger: Path,
          captures: Path, *, allow_native_evidence: bool = False) -> dict[str, Any]:
    """Never repairs, deletes, appends or authorizes resumption of a campaign."""
    h = core_module()
    if not isinstance(permit, dict) or not isinstance(plan, dict):
        raise ValueError("permit and plan must be objects")
    if permit.get("dispatch_class") != "MODEL_ONLY" and not allow_native_evidence:
        raise ValueError("native evidence requires explicit read-only acknowledgement")
    h.validate_plan(permit, plan, allow_native=allow_native_evidence)
    # The MC-045 appender retains this marker after uncertain write/fsync/close.
    # A parsable full ledger is not admissible while custody is quarantined.
    # Like the MC-045 CLI audit, refuse both active and stale append locks.
    h.refuse_ledger_append_lock(ledger)
    # Each planned attempt retains exactly stdout and stderr; the bound is
    # derived from validated plan authority, never observed directory size.
    capture_limit = 2 * plan["max_jobs"] * plan["sequential_repeats"]
    pre = fingerprints(ledger, captures, capture_limit)
    rows, digest = h.load_ledger_with_digest(ledger)
    h.validate_ledger_sequence(rows, permit, plan, allow_native=allow_native_evidence)
    h.verify_retained_captures(rows, captures)
    # A metadata-only final snapshot is insufficient on platforms where ctime
    # means creation time or metadata can be restored. Repeat the bounded,
    # streaming content checks against the *original* expected ledger rows.
    # This narrows a post-hash mutation window; it is not atomic custody.
    h.verify_retained_captures(rows, captures)
    replay_rows, replay_digest = h.load_ledger_with_digest(ledger)
    if replay_digest != digest or replay_rows != rows:
        raise ValueError("ledger bytes changed during inspection; refuse mutable custody")
    if pre != fingerprints(ledger, captures, capture_limit):
        raise ValueError("evidence changed during inspection; refuse retry without frozen custody")
    # A writer may have started (or quarantined) during digest verification;
    # marker state is outside the ledger/capture fingerprint inventory.
    # This double check is cooperative local-process admission, NOT an atomic
    # snapshot or protection from create+remove races on a hostile filesystem.
    h.refuse_ledger_append_lock(ledger)
    expected = plan["max_jobs"] * plan["sequential_repeats"]
    return {
        "schema": "radicadsac-mc047-readonly-recovery-preflight/1.0",
        "status": ("FULL_SLOT_LEDGER_NOT_PROGRAMME_ACCEPTED" if len(rows) == expected
                   else "PARTIAL_PREFIX_NOT_AUTHORIZED_TO_RESUME"),
        "evidence_class": ("DETERMINISTIC_MODEL" if permit["dispatch_class"] == "MODEL_ONLY"
                           else "NATIVE_RECORDS_UNQUALIFIED"),
        "source_sha": permit["source_sha"],
        "ledger_sha256": digest,
        "slots_recorded": len(rows),
        "slots_planned": expected,
        "nonpass_terminals": sum(r["terminal_reason"] != "SUCCEEDED" for r in rows),
        "resumption_authorized": False,
        "programme_acceptance_established": False,
    }


def synthetic_contract() -> tuple[dict[str, Any], dict[str, Any]]:
    permit = {
        "schema": "radicadsac-mc-native-permit/1.0", "permit_id": "MC047-SYNTHETIC",
        "programme": "MC-1", "owner_task": "MC-047", "dispatch_class": "MODEL_ONLY",
        "approval_authority": "MC-1-programme",
        "approval_evidence": "synthetic offline MC-047 control; no campaign dispatch",
        "source_sha": "0" * 40,
        "candidate_config_digest": "sha256:" + "1" * 64,
        "fixture_profile_digest": "sha256:" + "2" * 64,
        "platform_id": "MC047-OFFLINE-SYNTHETIC",
        "retention_path": "synthetic-only", "allocated_vcpus": 2,
        "max_processes": 1, "threads_per_process": 1, "max_jobs": 1,
        "sequential_repeats": 3, "timeout_seconds": 10,
        "peak_rss_bytes_max": 1024, "storage_bytes_max": 2048,
        "egress_bytes_max": 1024,
        "tariff_basis": {"paid": False, "verified_current": False, "basis": "no provider"},
        "stop_rules": ["incomplete or corrupt evidence"],
        "expensive_campaign_lock": "HELD_BY_THIS_PERMIT",
    }
    plan = {
        "schema": "radicadsac-mc-campaign-plan/1.0",
        **{k: permit[k] for k in (
            "permit_id", "source_sha", "candidate_config_digest", "fixture_profile_digest", "platform_id",
            "max_jobs", "sequential_repeats", "max_processes", "threads_per_process",
            "timeout_seconds", "peak_rss_bytes_max", "storage_bytes_max", "egress_bytes_max")},
        "command": ["python3", "-c", "pass"], "shell": False,
        "parallel_repeats": False, "environment": {},
    }
    return permit, plan


def self_test() -> None:
    h = core_module()
    permit, plan = synthetic_contract()
    h.validate_plan(permit, plan)
    rows = [h._attempt(permit, plan, i, 0, "SUCCEEDED") for i in range(3)]
    checks = 0
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        ledger, captures = root / "ledger.jsonl", root / "captures"
        captures.mkdir()

        def write(rows_to_write: list[dict[str, Any]]) -> None:
            ledger.write_bytes(b"".join(h.canonical_bytes(row) + b"\n" for row in rows_to_write))
            for item in captures.iterdir():
                item.unlink()
            for i in range(len(rows_to_write)):
                for stream in ("stdout", "stderr"):
                    (captures / f"{i:06d}.{stream}.bin").write_bytes(b"")

        def reject(label: str) -> None:
            nonlocal checks
            try:
                audit(permit, plan, ledger, captures)
            except (ValueError, OSError, h.ContractError):
                checks += 1
                return
            raise AssertionError("unsafe evidence accepted: " + label)

        write(rows[:1])
        result = audit(permit, plan, ledger, captures)
        assert result["status"] == "PARTIAL_PREFIX_NOT_AUTHORIZED_TO_RESUME"
        assert result["resumption_authorized"] is False
        checks += 1

        write(rows)
        result = audit(permit, plan, ledger, captures)
        assert result["status"] == "FULL_SLOT_LEDGER_NOT_PROGRAMME_ACCEPTED"
        assert result["programme_acceptance_established"] is False
        checks += 1

        # Plan = three slots, hence exactly six permitted capture entries.
        # The seventh real on-disk entry must be refused at the bounded
        # inventory gate before any unbounded tuple/sort materialization.
        write(rows)
        (captures / "unexpected-000000.bin").write_bytes(b"orphan")
        try:
            audit(permit, plan, ledger, captures)
        except ValueError as exc:
            assert "capture inventory exceeds planned slot budget" in str(exc), exc
        else:
            raise AssertionError("over-budget capture inventory accepted")
        checks += 1

        # A complete, valid ledger under a crashed writer's quarantine lock
        # MUST be refused, rather than reported as a qualified full-slot set.
        lock_path = ledger.with_name(ledger.name + ".append.lock")
        unchanged_ledger = ledger.read_bytes()
        marker = b"test-only uncertain durability; not a recovery permit\n"
        lock_path.write_bytes(marker)
        try:
            try:
                audit(permit, plan, ledger, captures)
            except ValueError as exc:
                assert "ledger append active or quarantined" in str(exc), exc
            else:
                raise AssertionError("quarantined complete ledger accepted")
            assert ledger.read_bytes() == unchanged_ledger
            assert lock_path.read_bytes() == marker
            checks += 1
        finally:
            # Test-only cleanup; a real stale marker requires manual review.
            lock_path.unlink()

        # A marker planted only after the second evidence fingerprint must
        # still veto admission. The marker is *not* inventoried by fingerprints.
        write(rows[:1])
        unchanged_ledger = ledger.read_bytes()
        original_fingerprints = fingerprints
        fingerprint_calls = [0]

        def inject_late_quarantine(ledger_path: Path, captures_path: Path, entry_limit: int):
            snapshot = original_fingerprints(ledger_path, captures_path, entry_limit)
            fingerprint_calls[0] += 1
            if fingerprint_calls[0] == 2:
                lock_path.write_bytes(marker)
            return snapshot

        globals()["fingerprints"] = inject_late_quarantine
        try:
            try:
                audit(permit, plan, ledger, captures)
            except ValueError as exc:
                assert "ledger append active or quarantined" in str(exc), exc
            else:
                raise AssertionError("late quarantine marker accepted")
            assert fingerprint_calls[0] == 2, fingerprint_calls
            assert ledger.read_bytes() == unchanged_ledger
            assert lock_path.read_bytes() == marker
            checks += 1
        finally:
            globals()["fingerprints"] = original_fingerprints
            if lock_path.exists():
                lock_path.unlink()

        write(rows[:1]); (captures / "000000.stderr.bin").unlink()
        reject("crash after stdout only")
        write(rows[:1]); (captures / "000001.stdout.bin").write_bytes(b"orphan")
        reject("captures before ledger commit")
        write(rows[:1]); (captures / "000000.stdout.bin").unlink()
        reject("ledger committed but capture absent")
        write(rows[:1]); ledger.write_bytes(ledger.read_bytes()[:-1])
        reject("torn trailing ledger line")
        write(rows[:1]); (captures / "000000.stdout.bin").write_bytes(b"tamper")
        reject("captured content mutation")
        write(rows[:2]); mutated = [rows[0], dict(rows[1], attempt_id=rows[0]["attempt_id"])]
        ledger.write_bytes(b"".join(h.canonical_bytes(x) + b"\n" for x in mutated))
        reject("duplicate attempt identity")
        write(rows[:1]); ledger.write_bytes(h.canonical_bytes(rows[2]) + b"\n")
        reject("skipped repeat")
        write(rows[:1]); (captures / "000000.stdout.bin").unlink()
        (captures / "000000.stdout.bin").symlink_to(ledger)
        reject("capture symlink")
        write(rows[:1]); ledger.unlink(); ledger.symlink_to(root / "not-here")
        reject("ledger symlink")
        ledger.unlink()
        # Two capture filenames must not share one inode, even if both empty
        # streams have valid matching SHA-256 values. A hardlink ties custody.
        write(rows[:1])
        (captures / "000000.stderr.bin").unlink()
        os.link(captures / "000000.stdout.bin", captures / "000000.stderr.bin")
        reject("hard-linked stdout/stderr alias")
        write(rows[:2]); rows_with_fault = [rows[0], dict(rows[1], terminal_reason="CRASH", return_code=139, programme_pass=False)]
        write(rows_with_fault)
        assert audit(permit, plan, ledger, captures)["nonpass_terminals"] == 1
        checks += 1
        # After a valid digest pass, mutate capture bytes before the final
        # metadata snapshot. The read-only admission must refuse this race.
        write(rows[:1])
        original_core = core_module

        def race_injected_core():
            source = original_core()
            original_verify = source.verify_retained_captures

            def mutate_after_verify(*args):
                original_verify(*args)
                (captures / "000000.stdout.bin").write_bytes(b"changed-after-digest")

            source.verify_retained_captures = mutate_after_verify
            return source

        globals()["core_module"] = race_injected_core
        try:
            reject("post-hash/pre-snapshot mutation")
        finally:
            globals()["core_module"] = original_core

        # The old fingerprint used size+mtime and missed an equal-length
        # post-digest rewrite followed by explicit mtime restoration. POSIX
        # inode change-time must detect it, without trusting a second hash.
        if os.name == "posix":
            capture = captures / "000000.stdout.bin"
            modified = dict(rows[0], stdout_sha256=h.sha256_bytes(b"AAAA"),
                            output_bytes=4)
            write([modified])
            capture.write_bytes(b"AAAA")

            def restored_mtime_core():
                source = original_core()
                original_verify = source.verify_retained_captures

                def mutate_after_verify(*args):
                    original_verify(*args)
                    before = capture.stat()
                    capture.write_bytes(b"BBBB")
                    os.utime(capture, ns=(before.st_atime_ns,
                                          before.st_mtime_ns))
                    after = capture.stat()
                    assert after.st_size == before.st_size
                    assert after.st_mtime_ns == before.st_mtime_ns
                    assert after.st_ctime_ns != before.st_ctime_ns

                source.verify_retained_captures = mutate_after_verify
                return source

            globals()["core_module"] = restored_mtime_core
            try:
                reject("equal-length post-hash rewrite with restored mtime")
            finally:
                globals()["core_module"] = original_core
        # Simulate a filesystem with no dependable change-time indication,
        # including Windows creation-time semantics. The fingerprint is held
        # constant deliberately; the *second content pass*, not metadata,
        # must reject a mutation performed after the first digest check.
        original_fingerprints = fingerprints

        def reject_with_masked_metadata(label, mutate_after_first):
            saved_core = core_module
            snapshot = original_fingerprints(
                ledger, captures, 2 * plan["max_jobs"] * plan["sequential_repeats"])
            injection = {"completed": False}

            def injection_core():
                source = saved_core()
                original_verify = source.verify_retained_captures
                injected = False

                def mutate_once(*args):
                    nonlocal injected
                    original_verify(*args)
                    if not injected:
                        injected = True
                        mutate_after_first()
                        injection["completed"] = True

                source.verify_retained_captures = mutate_once
                return source

            globals()["core_module"] = injection_core
            globals()["fingerprints"] = lambda _ledger, _captures, _limit: snapshot
            try:
                reject(label)
                # An early refusal or OSError in fault injection must not
                # masquerade as successful post-hash mutation detection.
                assert injection["completed"], "post-hash fault was not injected: " + label
            finally:
                globals()["core_module"] = saved_core
                globals()["fingerprints"] = original_fingerprints

        modified_capture_row = dict(rows[0], stdout_sha256=h.sha256_bytes(b"AAAA"),
                                    output_bytes=4)
        write([modified_capture_row])
        capture = captures / "000000.stdout.bin"
        capture.write_bytes(b"AAAA")

        def rewrite_capture():
            before = capture.stat()
            capture.write_bytes(b"BBBB")
            os.utime(capture, ns=(before.st_atime_ns, before.st_mtime_ns))
            assert capture.stat().st_size == before.st_size

        reject_with_masked_metadata("metadata-invisible posthash capture replacement",
                                    rewrite_capture)

        write(rows[:1])
        rewritten_row = dict(rows[0], source_sha="f" * 40)
        rewritten_ledger = h.canonical_bytes(rewritten_row) + b"\n"
        assert len(rewritten_ledger) == len(ledger.read_bytes())

        def rewrite_ledger():
            before = ledger.stat()
            ledger.write_bytes(rewritten_ledger)
            os.utime(ledger, ns=(before.st_atime_ns, before.st_mtime_ns))

        reject_with_masked_metadata("metadata-invisible posthash ledger replacement",
                                    rewrite_ledger)
    assert checks == (20 if os.name == "posix" else 19), checks
    print(f"MC-047 read-only crash-window controls passed: {checks}; MODEL_ONLY; no native dispatch")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--permit", type=Path)
    ap.add_argument("--plan", type=Path)
    ap.add_argument("--ledger", type=Path)
    ap.add_argument("--captures", type=Path)
    ap.add_argument("--allow-native-evidence", action="store_true",
                    help="read-only inspection, never a dispatch permit")
    args = ap.parse_args()
    if args.contract or args.self_test:
        self_test()
        return 0
    if not all((args.permit, args.plan, args.ledger, args.captures)):
        ap.error("--permit, --plan, --ledger and --captures must be provided together")
    try:
        h = core_module()
        permit, plan = h.load_json(args.permit), h.load_json(args.plan)
        result = audit(permit, plan, args.ledger, args.captures,
                       allow_native_evidence=args.allow_native_evidence)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "REFUSED", "reason": str(exc),
                          "programme_acceptance_established": False}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
