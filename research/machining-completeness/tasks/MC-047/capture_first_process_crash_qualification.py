#!/usr/bin/env python3
"""MC-047: capture-first hard-exit qualification, synthetic MODEL_ONLY only.

Exercises real accepted MC-045/MC-047 read-only auditors after an independent
process exits with flushed orphan capture bytes but no corresponding ledger row.
This does not exercise a native capture writer or authorize recovery.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "MC-045" / "campaign_harness.py"
PREFLIGHT = HERE / "verify.py"
TIMEOUT_SECONDS = 15
INJECTED_EXIT = 29
UNEXPECTED_EXIT = 31
PARTIAL = b"X" * 17
FULL_STDOUT = b"synthetic complete stdout before ledger commit\n"
FULL_STDERR = b"synthetic complete stderr before ledger commit\n"
MODES = ("partial-stdout", "full-stdout", "both-streams")


def load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"accepted source unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot(captures: Path) -> dict[str, str]:
    return {p.name: sha(p.read_bytes()) for p in captures.iterdir()}


def write_flushed(path: Path, data: bytes) -> None:
    """Create a fresh retained-capture name exclusively and fsync its bytes."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    fd = os.open(path, flags, 0o600)
    try:
        count = os.write(fd, data)
        if count != len(data):
            os._exit(UNEXPECTED_EXIT)
        os.fsync(fd)
    finally:
        os.close(fd)


def crash_worker(mode: str, captures: Path) -> None:
    if mode not in MODES:
        os._exit(UNEXPECTED_EXIT)
    if not captures.is_dir():
        os._exit(UNEXPECTED_EXIT)
    output = PARTIAL if mode == "partial-stdout" else FULL_STDOUT
    write_flushed(captures / "000001.stdout.bin", output)
    if mode == "both-streams":
        write_flushed(captures / "000001.stderr.bin", FULL_STDERR)
    # The child has genuinely flushed file bytes; no ledger row was written.
    # Hard exit avoids Python cleanup and simulates abrupt capture-first death.
    os._exit(INJECTED_EXIT)


def refuse(action, expected: str, label: str) -> None:
    try:
        action()
    except (ValueError, OSError) as exc:
        if expected not in str(exc):
            raise AssertionError(
                f"{label}: wrong refusal {exc!s}; expected {expected!r}"
            ) from exc
    else:
        raise AssertionError(f"{label}: orphan evidence was admitted")


def run_case(mode: str) -> None:
    h = load(CORE, f"mc045_capture_first_{mode.replace('-', '_')}")
    v = load(PREFLIGHT, f"mc047_capture_first_{mode.replace('-', '_')}")
    permit, plan = v.synthetic_contract()
    h.validate_plan(permit, plan)
    assert permit["dispatch_class"] == "MODEL_ONLY"

    with tempfile.TemporaryDirectory(prefix="mc047-capture-first-") as td:
        root = Path(td)
        ledger = root / "ledger.jsonl"
        captures = root / "captures"
        captures.mkdir()
        for stream in ("stdout", "stderr"):
            (captures / f"000000.{stream}.bin").write_bytes(b"")

        first = h._attempt(permit, plan, 0, 0, "SUCCEEDED")
        h.append_attempt(ledger, first, permit, plan)
        baseline = h.canonical_bytes(first) + b"\n"
        assert ledger.read_bytes() == baseline
        capture_prefix = snapshot(captures)

        accepted_audit = h.audit_ledger(permit, plan, ledger, captures)
        accepted_preflight = v.audit(permit, plan, ledger, captures)
        assert accepted_audit["status"] == "LEDGER_REPLAY_VALIDATED_NOT_NATIVE_QUALIFICATION"
        assert accepted_preflight["status"] == "PARTIAL_PREFIX_NOT_AUTHORIZED_TO_RESUME"
        assert accepted_preflight["resumption_authorized"] is False
        assert accepted_preflight["programme_acceptance_established"] is False

        command = [sys.executable, str(Path(__file__).resolve()),
                   "--worker", mode, str(captures)]
        child = subprocess.Popen(command, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
        try:
            stdout, stderr = child.communicate(timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired as exc:
            child.kill()
            child.communicate()
            raise AssertionError(f"{mode}: child exceeded bounded timeout") from exc
        assert child.returncode == INJECTED_EXIT, (
            f"{mode}: wrong child exit {child.returncode}; "
            f"stdout={stdout!r}; stderr={stderr!r}"
        )

        expected = {"000001.stdout.bin": PARTIAL if mode == "partial-stdout" else FULL_STDOUT}
        if mode == "both-streams":
            expected["000001.stderr.bin"] = FULL_STDERR
        actual_names = set(snapshot(captures)) - set(capture_prefix)
        assert actual_names == set(expected), (mode, actual_names)
        for name, data in expected.items():
            assert (captures / name).read_bytes() == data
        assert {name: sha((captures / name).read_bytes())
                for name in capture_prefix} == capture_prefix
        assert ledger.read_bytes() == baseline
        assert h.load_ledger(ledger) == [first]
        lock = ledger.with_name(ledger.name + ".append.lock")
        assert not lock.exists(), "test fabricated an append quarantine lock"

        # A fully valid preceding ledger prefix cannot admit orphaned captures.
        # Both exact accepted auditors must reject for the specific inventory
        # mismatch rather than an unrelated schema/permit/lock error.
        reason = "retained capture inventory has missing or unexpected paths"
        refuse(lambda: h.audit_ledger(permit, plan, ledger, captures),
               reason, f"{mode}: MC-045 audit")
        refuse(lambda: v.audit(permit, plan, ledger, captures),
               reason, f"{mode}: MC-047 preflight")
        assert ledger.read_bytes() == baseline
        assert not lock.exists()
        assert snapshot(captures) == {**capture_prefix,
                                     **{name: sha(data) for name, data in expected.items()}}

    print(f"PASS MC-047 capture-first os._exit: {mode}; "
          "two real auditors refused orphaned MODEL_ONLY evidence")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--worker", choices=MODES)
    ap.add_argument("captures", nargs="?", type=Path)
    args = ap.parse_args()
    if args.worker is not None:
        if args.captures is None or args.contract or args.self_test:
            ap.error("--worker MODE requires a capture directory, no contract flags")
        crash_worker(args.worker, args.captures)
        return UNEXPECTED_EXIT
    if not (args.contract or args.self_test) or args.captures is not None:
        ap.error("use --contract or --self-test; no implicit dispatch")
    for mode in MODES:
        run_case(mode)
    print("MC-047 capture-first fault qualification: 3/3 process modes PASS; "
          "MODEL_ONLY; native/STEP/durability/production NOT_ESTABLISHED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
