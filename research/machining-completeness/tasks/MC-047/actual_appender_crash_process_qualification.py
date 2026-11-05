#!/usr/bin/env python3
"""MC-047: real MC-045 append_attempt hard-process-exit qualification (MODEL_ONLY).

This deliberately terminates the child with os._exit after real ledger bytes
have been written. It never dispatches a campaign or certifies durability.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import single_writer_process_qualification as process  # accepted model authority
import verify as preflight  # accepted read-only recovery contract

TIMEOUT_SECONDS = 15
INJECTED_EXIT = 29
UNEXPECTED_RETURN = 31
PARTIAL_BYTES = 17


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture_inventory(captures: Path) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((p.name, digest(p)) for p in captures.iterdir()))


class PartialWriteThenDie:
    """Proxy a *real* unbuffered ledger fd; crash after its first partial write."""
    def __init__(self, inner):
        self.inner = inner

    def __enter__(self):
        self.inner.__enter__()
        return self

    def __exit__(self, *args):
        return self.inner.__exit__(*args)

    def __iter__(self):
        return iter(self.inner)

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def write(self, value: bytes) -> int:
        assert len(value) > PARTIAL_BYTES
        wrote = self.inner.write(value[:PARTIAL_BYTES])
        if wrote != PARTIAL_BYTES:
            os._exit(UNEXPECTED_RETURN)
        # os._exit skips Python finally, lock cleanup, and any ledger fsync.
        os._exit(INJECTED_EXIT)


def worker(mode: str, ledger: Path) -> None:
    h = process.harness()
    permit, plan = process.model_authority(h)
    attempt = h._attempt(permit, plan, 1, 0, "SUCCEEDED")
    if mode == "partial":
        original_fdopen = os.fdopen

        def partial_fdopen(fd, file_mode="r", buffering=-1, *args, **kwargs):
            if file_mode != "r+b" or buffering != 0:
                os._exit(UNEXPECTED_RETURN)
            return PartialWriteThenDie(original_fdopen(
                fd, file_mode, buffering, *args, **kwargs
            ))

        os.fdopen = partial_fdopen
    elif mode == "before-ledger-fsync":
        original_fsync = os.fsync
        calls = 0

        def die_before_second_fsync(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                # The first call is for the exclusive append lock. The second
                # is the real ledger fsync, after the real full-line write.
                os._exit(INJECTED_EXIT)
            if calls > 2:
                os._exit(UNEXPECTED_RETURN)
            return original_fsync(fd)

        os.fsync = die_before_second_fsync
    else:
        raise AssertionError("unknown injection mode")
    h.append_attempt(ledger, attempt, permit, plan)
    os._exit(UNEXPECTED_RETURN)  # fault injection was never reached


def require_refusal(fn, reason: str) -> None:
    try:
        fn()
    except (ValueError, OSError) as exc:
        if reason not in str(exc):
            raise AssertionError(
                f"wrong refusal: expected {reason!r}, received {exc!r}"
            ) from exc
    else:
        raise AssertionError(f"unsafe admission: expected {reason!r}")


def case(mode: str) -> None:
    h = process.harness()
    permit, plan = process.model_authority(h)
    rows = [h._attempt(permit, plan, i, 0, "SUCCEEDED") for i in range(2)]
    with tempfile.TemporaryDirectory(prefix="mc047-real-appender-") as tmp:
        root = Path(tmp)
        ledger = root / "attempts.jsonl"
        captures = root / "captures"
        captures.mkdir()

        for stream in ("stdout", "stderr"):
            (captures / f"000000.{stream}.bin").write_bytes(b"")
        h.append_attempt(ledger, rows[0], permit, plan)
        control = preflight.audit(permit, plan, ledger, captures)
        assert control["status"] == "PARTIAL_PREFIX_NOT_AUTHORIZED_TO_RESUME"
        assert not control["resumption_authorized"]
        prefix = ledger.read_bytes()
        assert prefix == h.canonical_bytes(rows[0]) + b"\n"

        for stream in ("stdout", "stderr"):
            (captures / f"000001.{stream}.bin").write_bytes(b"")
        capture_before = capture_inventory(captures)
        command = [sys.executable, str(Path(__file__).resolve()),
                   "--worker", mode, str(ledger)]
        child = subprocess.Popen(command, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
        try:
            output, error = child.communicate(timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired as exc:
            child.kill()
            child.communicate()
            raise AssertionError(f"crash worker hung: {mode}") from exc
        if child.returncode != INJECTED_EXIT:
            raise AssertionError(
                f"wrong crash exit ({mode}): {child.returncode}, "
                f"stdout={output!r}, stderr={error!r}"
            )

        suffix = h.canonical_bytes(rows[1]) + b"\n"
        expected = (suffix[:PARTIAL_BYTES] if mode == "partial" else suffix)
        assert ledger.read_bytes() == prefix + expected, (
            "actual appender did not write the exactly expected prefix/full line"
        )
        lock = ledger.with_name(ledger.name + ".append.lock")
        assert lock.is_file(), "hard-exited production appender released its lock"
        marker_before = lock.read_bytes()
        assert marker_before.startswith(b"pid="), "not a real appender lock"
        assert capture_inventory(captures) == capture_before

        # Neither writer nor either read-only authority may accept a quarantined
        # ledger, even when full JSONL bytes are present but fsync never ran.
        require_refusal(
            lambda: h.append_attempt(ledger, rows[1], permit, plan),
            "ledger append locked (active or stale)",
        )
        require_refusal(
            lambda: h.audit_ledger(permit, plan, ledger, captures),
            "ledger append active or quarantined",
        )
        require_refusal(
            lambda: preflight.audit(permit, plan, ledger, captures),
            "ledger append active or quarantined",
        )
        assert ledger.read_bytes() == prefix + expected
        assert lock.read_bytes() == marker_before
        assert capture_inventory(captures) == capture_before

        # Test-only simulated manual unlock distinguishes JSONL parseability
        # from durability. It is NOT a recovery recommendation or permission.
        lock.unlink()
        if mode == "partial":
            require_refusal(
                lambda: preflight.audit(permit, plan, ledger, captures),
                "unterminated ledger line 2",
            )
            require_refusal(
                lambda: h.audit_ledger(permit, plan, ledger, captures),
                "unterminated ledger line 2",
            )
        else:
            result = preflight.audit(permit, plan, ledger, captures)
            assert result["status"] == "PARTIAL_PREFIX_NOT_AUTHORIZED_TO_RESUME"
            assert result["slots_recorded"] == 2
            assert not result["resumption_authorized"]
            assert not result["programme_acceptance_established"]
            # Reparseability after a test-only unlock is NOT proof of fsync.
        assert ledger.read_bytes() == prefix + expected
        assert capture_inventory(captures) == capture_before
    print(f"PASS actual MC-045 append_attempt hard exit: {mode}; MODEL_ONLY")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--worker", choices=["partial", "before-ledger-fsync"])
    ap.add_argument("ledger", nargs="?", type=Path)
    args = ap.parse_args()
    if args.worker:
        if args.ledger is None:
            ap.error("--worker requires ledger")
        worker(args.worker, args.ledger)
        return UNEXPECTED_RETURN
    if not (args.contract or args.self_test) or args.ledger is not None:
        ap.error("use --contract or --self-test")
    for mode in ("partial", "before-ledger-fsync"):
        case(mode)
    print("MC-047 actual-appender process crash qualification: 2/2 PASS; "
          "MODEL_ONLY; no native dispatch or durability claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
