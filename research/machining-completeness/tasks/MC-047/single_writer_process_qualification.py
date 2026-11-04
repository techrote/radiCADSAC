#!/usr/bin/env python3
"""Bounded real-process MC-045 ledger-lock controls for MC-047.

Process-level evidence with synthetic MODEL_ONLY attempts only. This is NOT
native execution, crash-safe transaction qualification or an MC-F gate result.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


HARNESS = Path(__file__).resolve().parents[1] / "MC-045" / "campaign_harness.py"
TIMEOUT_SECONDS = 12.0


def harness():
    spec = importlib.util.spec_from_file_location("mc045_campaign_harness", HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("MC-045 source-matched harness unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def model_authority(h):
    # Mirror the accepted MC-045 MODEL_ONLY self-test authority; NO dispatch.
    permit = {
        "schema": h.PERMIT_SCHEMA,
        "permit_id": "MC047-CHILD-PROCESS-CONTROL-001",
        "programme": "MC-1",
        "owner_task": "MC-045",
        "dispatch_class": "MODEL_ONLY",
        "approval_authority": "MC-1-programme",
        "approval_evidence": "synthetic MC-047 subprocess regression only; no native or paid dispatch",
        "source_sha": "0" * 40,
        "candidate_config_digest": "sha256:" + "1" * 64,
        "fixture_profile_digest": "sha256:" + "2" * 64,
        "platform_id": "MC047-SYNTHETIC-PROCESS",
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
        "retention_path": "synthetic-process-test-ledger.jsonl",
        "stop_rules": ["binding mismatch", "resource cap", "lost ledger"],
        "expensive_campaign_lock": "HELD_BY_THIS_PERMIT",
    }
    plan = {
        "schema": h.PLAN_SCHEMA,
        "permit_id": permit["permit_id"],
        "source_sha": permit["source_sha"],
        "candidate_config_digest": permit["candidate_config_digest"],
        "fixture_profile_digest": permit["fixture_profile_digest"],
        "platform_id": permit["platform_id"],
        "command": ["python", "-c", "print('not invoked')"],
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
    h.validate_plan(permit, plan)
    if permit["dispatch_class"] != "MODEL_ONLY":
        raise AssertionError("test must never authorize native dispatch")
    return permit, plan


def wait_for_file(path: Path) -> None:
    deadline = time.monotonic() + TIMEOUT_SECONDS
    while not path.is_file():
        if time.monotonic() > deadline:
            raise AssertionError(f"bounded child-process barrier timeout: {path.name}")
        time.sleep(0.02)


def spawn(*args: Path | str) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--worker", *map(str, args)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )


def finish(child: subprocess.Popen[str], *, expected: int = 0) -> None:
    try:
        out, err = child.communicate(timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        child.kill()
        child.communicate()
        raise AssertionError("child process did not terminate within timeout")
    if child.returncode != expected:
        raise AssertionError(
            f"child exited {child.returncode}, expected {expected}; stdout={out!r}; stderr={err!r}"
        )


def require_locked_refusal(h, operation) -> None:
    try:
        operation()
    except h.ContractError as exc:
        if "locked" not in str(exc):
            raise AssertionError(f"unexpected contention refusal: {exc}") from exc
    else:
        raise AssertionError("attempt appended despite another process owning the lock")


def worker(mode: str, ledger: Path, ready: Path, release: Path, result: Path | None) -> int:
    h = harness()
    if mode in {"hold", "crash"}:
        with h.exclusive_ledger_append_lock(ledger):
            ready.write_text("lock-held", encoding="ascii")
            if mode == "crash":
                # Deliberately bypass context-manager cleanup as a crashed process does.
                os._exit(17)
            wait_for_file(release)
        return 0
    if mode == "race":
        if result is None:
            raise AssertionError("race child must supply a result path")
        permit, plan = model_authority(h)
        attempt = h._attempt(permit, plan, 1, 0, "SUCCEEDED")
        ready.write_text("ready", encoding="ascii")
        wait_for_file(release)
        try:
            h.append_attempt(ledger, attempt, permit, plan)
        except h.ContractError as exc:
            # A generic ContractError would make this adversarial control pass
            # for unrelated input/schema failures. Only the expected competing
            # lock or duplicate committed slot is a legitimate loser.
            message = str(exc)
            if not any(marker in message for marker in (
                "locked", "duplicate attempt_id", "duplicate repeat/job slot",
            )):
                raise AssertionError(f"unexpected losing-writer refusal: {message}") from exc
            result.write_text("REFUSED", encoding="ascii")
        else:
            result.write_text("APPENDED", encoding="ascii")
        return 0
    raise AssertionError(f"unknown child mode: {mode}")


def self_test() -> None:
    h = harness()
    permit, plan = model_authority(h)
    with tempfile.TemporaryDirectory(prefix="mc047-process-") as tmp:
        root = Path(tmp)
        ledger = root / "attempts.jsonl"
        lock = ledger.with_name(ledger.name + ".append.lock")
        first = h._attempt(permit, plan, 0, 0, "SUCCEEDED")
        second = h._attempt(permit, plan, 1, 0, "SUCCEEDED")
        third = h._attempt(permit, plan, 2, 0, "SUCCEEDED")
        h.append_attempt(ledger, first, permit, plan)
        initial = ledger.read_bytes()

        # A genuinely separate holder process must exclude a parent-process
        # contender without changing the existing canonical ledger.
        ready, release = root / "held-ready", root / "held-release"
        holder = spawn("hold", ledger, ready, release)
        try:
            wait_for_file(ready)
            assert lock.is_file(), "holder did not create its actual lock file"
            require_locked_refusal(h, lambda: h.append_attempt(ledger, second, permit, plan))
            assert ledger.read_bytes() == initial, "contended append changed ledger"
        finally:
            release.write_text("release", encoding="ascii")
            finish(holder)
        assert not lock.exists(), "normal holder release stranded append lock"

        # Two independent writers attempt the same admissible slot from the
        # same prefix. Exactly one must append; refusal may be lock contention
        # or replay detecting the first writer's accepted row.
        go = root / "race-release"
        winners: list[str] = []
        children = []
        for i in range(2):
            marker, result = root / f"race-ready-{i}", root / f"race-result-{i}"
            children.append((spawn("race", ledger, marker, go, result), marker, result))
        try:
            for _, marker, _ in children:
                wait_for_file(marker)
            go.write_text("release", encoding="ascii")
            for child, _, _ in children:
                finish(child)
            winners = [result.read_text(encoding="ascii") for _, _, result in children]
        finally:
            go.write_text("release", encoding="ascii")
            for child, _, _ in children:
                if child.poll() is None:
                    child.kill()
                    child.communicate()
        assert sorted(winners) == ["APPENDED", "REFUSED"], f"nonunique slot outcomes: {winners}"
        assert h.load_ledger(ledger) == [first, second], "same-slot race corrupted replay"
        assert not lock.exists(), "same-slot race stranded append lock"

        # Dead owner: exclusive-create lock remains on disk and must refuse.
        # Human/manual recovery is intentionally outside the implementation.
        crash_ready, unused_release = root / "crash-ready", root / "never-release"
        crashed = spawn("crash", ledger, crash_ready, unused_release)
        wait_for_file(crash_ready)
        finish(crashed, expected=17)
        assert lock.is_file(), "crashed owner unexpectedly reclaimed stale lock"
        before = ledger.read_bytes()
        require_locked_refusal(h, lambda: h.append_attempt(ledger, third, permit, plan))
        assert ledger.read_bytes() == before, "stale lock mutated evidence"
        # The test-only operator explicitly inspects then removes the stale lock.
        assert lock.read_text(encoding="ascii").startswith("pid=")
        lock.unlink()
        h.append_attempt(ledger, third, permit, plan)
        rows = h.load_ledger(ledger)
        h.validate_ledger_sequence(rows, permit, plan, require_complete=True)
        assert rows == [first, second, third]
        assert ledger.read_bytes() == b"".join(h.canonical_bytes(r) + b"\n" for r in rows)
        assert not lock.exists()

    print("MC-047 actual-process MODEL_ONLY controls PASS: held lock, same-slot race, dead-owner stale lock, manual recovery")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--worker", choices=("hold", "crash", "race"))
    parser.add_argument("worker_args", nargs="*")
    args = parser.parse_args()
    if args.worker:
        if len(args.worker_args) not in (3, 4):
            parser.error("child requires ledger, ready, release, [result]")
        ledger, ready, release = map(Path, args.worker_args[:3])
        result = Path(args.worker_args[3]) if len(args.worker_args) == 4 else None
        return worker(args.worker, ledger, ready, release, result)
    if not (args.contract and args.self_test):
        parser.error("run with --contract --self-test (synthetic process-only)")
    self_test()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
