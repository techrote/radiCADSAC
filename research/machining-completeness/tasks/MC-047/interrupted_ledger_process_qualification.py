#!/usr/bin/env python3
"""MC-047 real-process interrupted JSONL writer controls, MODEL_ONLY only.

No native process execution, campaign resumption, or evidence repair.
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
PROCESS = HERE / "single_writer_process_qualification.py"
PREFLIGHT = HERE / "verify.py"
CHILD_EXIT = 29
TIMEOUT_SECONDS = 12.0


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"required accepted source unavailable: {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_suffix(h, permit, plan, mode: str) -> bytes:
    row = h._attempt(permit, plan, 1, 0, "SUCCEEDED")
    raw = h.canonical_bytes(row) + b"\n"
    if mode == "short":
        return raw[:17]
    if mode == "no-newline":
        return raw[:-1]
    raise ValueError(f"unsupported fault mode: {mode}")


def crashed_writer(ledger: Path, ready: Path, mode: str) -> None:
    process = load_module(PROCESS, "mc047_existing_process_controls")
    h = process.harness()
    permit, plan = process.model_authority(h)
    assert permit["dispatch_class"] == "MODEL_ONLY"
    # This deliberately bypasses the admitted append API to simulate an
    # abruptly terminated OS writer after only part of a durable JSONL line.
    # The fixture must NEVER be used as evidence of a successful native run.
    with h.exclusive_ledger_append_lock(ledger):
        with ledger.open("ab", buffering=0) as stream:
            stream.write(expected_suffix(h, permit, plan, mode))
            os.fsync(stream.fileno())
        ready.write_text(mode, encoding="ascii")
        os._exit(CHILD_EXIT)


def must_refuse(operation, required: str) -> None:
    try:
        operation()
    except ValueError as exc:
        if required not in str(exc):
            raise AssertionError(f"unrelated refusal: {exc!s}, expected {required!r}") from exc
    else:
        raise AssertionError(f"unexpected admission; expected {required!r}")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_fault(mode: str) -> None:
    process = load_module(PROCESS, "mc047_process_controls")
    preflight = load_module(PREFLIGHT, "mc047_readonly_preflight")
    h = process.harness()
    permit, plan = process.model_authority(h)
    h.validate_plan(permit, plan)
    if permit["dispatch_class"] != "MODEL_ONLY":
        raise AssertionError("native execution is forbidden in this control")
    with tempfile.TemporaryDirectory(prefix="mc047-interrupted-ledger-") as tmp:
        root = Path(tmp)
        ledger = root / "attempts.jsonl"
        captures = root / "captures"
        captures.mkdir()
        (captures / "000000.stdout.bin").write_bytes(b"")
        (captures / "000000.stderr.bin").write_bytes(b"")
        first = h._attempt(permit, plan, 0, 0, "SUCCEEDED")
        second = h._attempt(permit, plan, 1, 0, "SUCCEEDED")
        h.append_attempt(ledger, first, permit, plan)
        original = ledger.read_bytes()
        assert h.load_ledger(ledger) == [first]
        good = preflight.audit(permit, plan, ledger, captures)
        assert good["status"] == "PARTIAL_PREFIX_NOT_AUTHORIZED_TO_RESUME"
        assert good["resumption_authorized"] is False
        captures_before = {p.name: digest(p.read_bytes()) for p in captures.iterdir()}

        ready = root / "crashed-after-fsync"
        child = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--worker",
             str(ledger), str(ready), mode],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            out, err = child.communicate(timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            child.kill()
            child.communicate()
            raise AssertionError("interrupted writer exceeded bounded timeout")
        if child.returncode != CHILD_EXIT:
            raise AssertionError(
                f"fault writer exited {child.returncode}, expected {CHILD_EXIT}; "
                f"stdout={out!r}, stderr={err!r}"
            )
        if not ready.is_file() or ready.read_text(encoding="ascii") != mode:
            raise AssertionError("crash marker missing; injection did not reach post-fsync")
        tail = expected_suffix(h, permit, plan, mode)
        damaged = original + tail
        if ledger.read_bytes() != damaged or not tail or tail.endswith(b"\n"):
            raise AssertionError("expected original valid prefix + exact durable torn suffix")
        torn_digest = digest(damaged)
        lock = ledger.with_name(ledger.name + ".append.lock")
        assert lock.is_file(), "crash failed to strand the lock"

        # An untrusted operator must not be able to append under a dead-owner
        # lock; neither read-only inspection nor an append attempt repairs it.
        must_refuse(lambda: h.append_attempt(ledger, second, permit, plan), "locked")
        must_refuse(lambda: preflight.audit(permit, plan, ledger, captures),
                    "unterminated ledger line 2")
        assert ledger.read_bytes() == damaged and lock.is_file()

        # A test-only explicit lock removal models an operator who removed
        # the stale lock. Torn evidence must STILL refuse any new append.
        assert lock.read_text(encoding="ascii").startswith("pid=")
        lock.unlink()
        must_refuse(lambda: h.append_attempt(ledger, second, permit, plan),
                    "unterminated ledger line 2")
        must_refuse(lambda: h.load_ledger(ledger), "unterminated ledger line 2")
        must_refuse(lambda: preflight.audit(permit, plan, ledger, captures),
                    "unterminated ledger line 2")
        assert not lock.exists(), "refused append stranded a new lock"
        assert ledger.read_bytes() == damaged and digest(ledger.read_bytes()) == torn_digest
        assert {p.name: digest(p.read_bytes()) for p in captures.iterdir()} == captures_before

        # Positive control: a separate unchanged source-matched prefix remains
        # parseable and can be extended by the existing model append API.
        # This does NOT authorize resumption of the damaged ledger or native work.
        clean = root / "clean-control.jsonl"
        clean.write_bytes(original)
        h.append_attempt(clean, second, permit, plan)
        assert h.load_ledger(clean) == [first, second]
        assert ledger.read_bytes() == damaged
    print(f"MC-047 {mode} model-only subprocess crash and refusal PASS")


def self_test() -> None:
    for mode in ("short", "no-newline"):
        run_fault(mode)
    print("MC-047 interrupted ledger model/process controls PASS (2 crash modes)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("worker_args", nargs="*")
    args = parser.parse_args()
    if args.worker:
        if len(args.worker_args) != 3:
            parser.error("--worker requires LEDGER READY MODE")
        crashed_writer(Path(args.worker_args[0]), Path(args.worker_args[1]),
                       args.worker_args[2])
        return 0  # unreachable if injection succeeds
    if not (args.contract and args.self_test) or args.worker_args:
        parser.error("use --contract --self-test for synthetic controls")
    self_test()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
