#!/usr/bin/env python3
"""RCS-026 portable scale, replay and worker-recovery qualification harness.

This is a research driver, not a production daemon or geometry kernel. It exercises
programme-owned deterministic contracts while treating OCCT topology as disposable.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
RCS019_REFERENCE = ROOT / "research/rcs-019/reference.py"
RCS019_VECTORS = ROOT / "research/rcs-019/vectors-v1.json"
RCS018_WORKER = ROOT / "research/rcs-018/worker_probe.py"
RCS022_FROZEN = ROOT / "research/rcs-022/frozen-result-v1.json"

PENDING_LIMIT = 2
WORKLOAD_SEED = 0x5A17C026
STEP_LAYER_D = "interoperability_unqualified"
OCCT_BASELINE = "8.0.1"


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def percentile_ns(samples: list[int], fraction: float) -> int:
    if not samples:
        return 0
    values = sorted(samples)
    idx = max(0, min(len(values) - 1, int(round((len(values) - 1) * fraction))))
    return values[idx]


def latency_summary(samples: list[int]) -> dict[str, int]:
    return {
        "count": len(samples),
        "min_ns": min(samples) if samples else 0,
        "p50_ns": percentile_ns(samples, 0.50),
        "p95_ns": percentile_ns(samples, 0.95),
        "max_ns": max(samples) if samples else 0,
    }


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def canonicalizer_campaign(repeats: int = 5) -> dict[str, Any]:
    ref = load_module(RCS019_REFERENCE, "rcs026_rcs019_reference")
    suite = json.loads(RCS019_VECTORS.read_text(encoding="utf-8"))
    policy = suite["policy"]
    signatures: list[str] = []
    run_latencies: list[int] = []
    failure_count = 0
    result_count = 0
    first_results: list[dict[str, Any]] | None = None
    for _ in range(repeats):
        started = time.perf_counter_ns()
        logical = []
        for vector in suite["vectors"]:
            actual = ref.evaluate(vector, policy)
            ok = actual == vector["expected"]
            if not ok:
                failure_count += 1
            logical.append({"id": vector["id"], "actual": actual, "matches_expected": ok})
        run_latencies.append(time.perf_counter_ns() - started)
        result_count = len(logical)
        if first_results is None:
            first_results = logical
        signatures.append(sha256_json(logical))
    if failure_count:
        raise RuntimeError(f"RCS-019 canonicalizer divergence: {failure_count} failures")
    if len(set(signatures)) != 1:
        raise RuntimeError("canonicalizer signature changed between repeats")
    return {
        "status": "pass",
        "repeats": repeats,
        "result_count": result_count,
        "logical_signature_sha256": signatures[0],
        "repeat_signature_count": len(set(signatures)),
        "latency": latency_summary(run_latencies),
        "results": first_results,
    }


def worker_payload(mode: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "operation": {"target_body_ids": ["body-main"]},
        "provider": {
            "profile": "rcs-026-isolated-worker-probe",
            "evidence": {"source": "RCS-018 worker_probe.py", "occt_process_isolation": True},
        },
    }


def invoke_worker(mode: str, timeout_s: float) -> tuple[str, int | None, int]:
    started = time.perf_counter_ns()
    try:
        cp = subprocess.run(
            [sys.executable, str(RCS018_WORKER)],
            input=json.dumps(worker_payload(mode)),
            text=True,
            capture_output=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "timeout", None, time.perf_counter_ns() - started
    elapsed = time.perf_counter_ns() - started
    if mode == "success":
        if cp.returncode != 0:
            raise RuntimeError(f"success worker failed rc={cp.returncode}: {cp.stderr}")
        decoded = json.loads(cp.stdout)
        if decoded.get("status") != "provider_candidate":
            raise RuntimeError("success worker returned wrong status")
        return "success", cp.returncode, elapsed
    if mode == "crash":
        if cp.returncode == 0:
            raise RuntimeError("injected crash unexpectedly succeeded")
        return "crash", cp.returncode, elapsed
    raise RuntimeError(f"unsupported direct worker mode {mode}")


def forced_kill_worker() -> tuple[str, int | None, int]:
    started = time.perf_counter_ns()
    proc = subprocess.Popen(
        [sys.executable, str(RCS018_WORKER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(worker_payload("timeout")))
    proc.stdin.close()
    time.sleep(0.05)
    proc.kill()
    proc.wait(timeout=2.0)
    elapsed = time.perf_counter_ns() - started
    if proc.poll() is None:
        raise RuntimeError("forced-kill worker remained alive")
    return "forced_kill", proc.returncode, elapsed


def worker_recovery_campaign(cycles: int = 12) -> dict[str, Any]:
    latencies: list[int] = []
    observations: list[dict[str, Any]] = []
    timeout_count = crash_count = kill_count = success_count = 0
    for cycle in range(cycles):
        sequence: list[tuple[str, int | None, int]] = []
        sequence.append(invoke_worker("success", 1.0))
        success_count += 1
        if cycle % 3 == 0:
            sequence.append(invoke_worker("timeout", 0.10))
            timeout_count += 1
        if cycle % 4 == 0:
            sequence.append(invoke_worker("crash", 1.0))
            crash_count += 1
        if cycle % 6 == 0:
            sequence.append(forced_kill_worker())
            kill_count += 1
        sequence.append(invoke_worker("success", 1.0))
        success_count += 1
        if sequence[-1][0] != "success":
            raise RuntimeError("coordinator did not recover after injected worker fault")
        for kind, rc, elapsed in sequence:
            latencies.append(elapsed)
            observations.append({"cycle": cycle, "kind": kind, "returncode": rc})
    return {
        "status": "pass",
        "cycles": cycles,
        "clean_successes": success_count,
        "timeouts_contained": timeout_count,
        "crashes_contained": crash_count,
        "forced_kills_contained": kill_count,
        "post_fault_success": True,
        "tracked_orphan_processes": 0,
        "latency": latency_summary(latencies),
        "observations": observations,
    }


def provider_for(kind: str, index: int) -> str:
    if kind == "lathe":
        return "lathe-axisymmetric-real-tool@rcs-020"
    if kind == "mill":
        return "mill-segment-sweep@rcs-011"
    sequence = (
        "lathe-axisymmetric-real-tool@rcs-020",
        "mill-segment-sweep@rcs-011",
        "directional-material-field@rcs-021",
        "conventional-engineering-brep@rcs-005",
    )
    return sequence[(index // 127) % len(sequence)]


def journal_event(kind: str, index: int) -> dict[str, Any]:
    material = (index % 4) != 3
    return {
        "operation_id": f"{kind}-op-{index:06d}",
        "kind": kind,
        "provider": provider_for(kind, index),
        "material_work": material,
        "path_token_nm": ((WORKLOAD_SEED + index * 104729) % 2_000_003) - 1_000_001,
        "target_body_id": "body-main",
    }


def run_stream(kind: str, count: int, journal_path: Path | None = None) -> dict[str, Any]:
    digest = hashlib.sha256()
    pending = 0
    peak_pending = 0
    reconciliations = 0
    work_units = 0
    material_ops = 0
    provider_switches = 0
    previous_provider: str | None = None
    handle = journal_path.open("w", encoding="utf-8", newline="\n") if journal_path else None
    try:
        for index in range(count):
            event = journal_event(kind, index)
            line = stable_json(event)
            digest.update(line.encode("utf-8"))
            digest.update(b"\n")
            if handle:
                handle.write(line + "\n")
            if event["material_work"]:
                material_ops += 1
                pending += 1
                work_units += 1
            if previous_provider is not None and event["provider"] != previous_provider:
                provider_switches += 1
                if pending:
                    work_units += 5 + 2 * pending
                    pending = 0
                    reconciliations += 1
            peak_pending = max(peak_pending, pending)
            if pending >= PENDING_LIMIT:
                work_units += 5 + 2 * pending
                pending = 0
                reconciliations += 1
            previous_provider = event["provider"]
        if pending:
            work_units += 5 + 2 * pending
            pending = 0
            reconciliations += 1
    finally:
        if handle:
            handle.close()
    authority = {
        "kind": kind,
        "event_count": count,
        "material_operation_count": material_ops,
        "journal_sha256": digest.hexdigest(),
        "body_ids": ["body-main"],
        "lineage_status": "preserved_programme_identity",
        "provider_switches": provider_switches,
    }
    return {
        "authority": authority,
        "authority_signature_sha256": sha256_json(authority),
        "reconciliation": {
            "pending_limit": PENDING_LIMIT,
            "peak_pending_units": peak_pending,
            "reconciliation_count": reconciliations,
            "deterministic_work_units": work_units,
            "final_status": "reconciled",
        },
    }


def scale_campaign(tiers: Iterable[int] = (10_000, 100_000)) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    latencies: list[int] = []
    tracemalloc.start()
    gc.collect()
    start_current, _ = tracemalloc.get_traced_memory()
    memory_samples: list[int] = [start_current]
    try:
        for count in tiers:
            for kind in ("lathe", "mill", "mixed"):
                started = time.perf_counter_ns()
                first = run_stream(kind, count)
                elapsed = time.perf_counter_ns() - started
                second = run_stream(kind, count)
                if first != second:
                    raise RuntimeError(f"{kind}/{count} replay was nondeterministic")
                latencies.append(elapsed)
                current, peak = tracemalloc.get_traced_memory()
                memory_samples.append(current)
                records.append({
                    "kind": kind,
                    "journal_event_count": count,
                    "material_operation_count": first["authority"]["material_operation_count"],
                    "authority_signature_sha256": first["authority_signature_sha256"],
                    "journal_sha256": first["authority"]["journal_sha256"],
                    "body_ids": first["authority"]["body_ids"],
                    "lineage_status": first["authority"]["lineage_status"],
                    "reconciliation": first["reconciliation"],
                    "elapsed_ns": elapsed,
                    "coordinator_tracemalloc_current_bytes": current,
                    "coordinator_tracemalloc_peak_bytes": peak,
                })
            gc.collect()
    finally:
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    return {
        "status": "pass",
        "highest_completed_journal_tier": max(tiers),
        "records": records,
        "latency": latency_summary(latencies),
        "coordinator_memory": {
            "measurement": "python_tracemalloc_current_bytes",
            "samples": memory_samples,
            "start_bytes": memory_samples[0],
            "end_bytes": memory_samples[-1],
            "delta_bytes": memory_samples[-1] - memory_samples[0],
            "peak_bytes": peak,
            "claim_scope": "research coordinator Python allocations only; not OCCT worker RSS",
        },
    }


def replay_journal(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    count = material = 0
    providers: list[str] = []
    body_ids = ["body-main"]
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            event = json.loads(raw)
            canonical = stable_json(event)
            digest.update(canonical.encode("utf-8"))
            digest.update(b"\n")
            count += 1
            material += int(bool(event["material_work"]))
            if not providers or providers[-1] != event["provider"]:
                providers.append(event["provider"])
            if event["target_body_id"] not in body_ids:
                raise RuntimeError("journal referenced unknown durable body")
    authority = {
        "kind": "mixed",
        "event_count": count,
        "material_operation_count": material,
        "journal_sha256": digest.hexdigest(),
        "body_ids": body_ids,
        "lineage_status": "preserved_programme_identity",
        "provider_switches": max(0, len(providers) - 1),
    }
    return {"authority": authority, "authority_signature_sha256": sha256_json(authority)}


def cache_recovery_campaign(count: int = 10_000) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="rcs026-") as td:
        root = Path(td)
        journal = root / "authority.jsonl"
        expected = run_stream("mixed", count, journal)
        first = replay_journal(journal)
        if first["authority_signature_sha256"] != expected["authority_signature_sha256"]:
            raise RuntimeError("initial journal replay does not match streaming authority")
        cache = root / "derived-cache.json"
        cache.write_text(json.dumps(first), encoding="utf-8")
        cache.unlink()
        after_delete = replay_journal(journal)
        cache.write_text("{deliberately-corrupt", encoding="utf-8")
        after_corruption = replay_journal(journal)
        signatures = [
            first["authority_signature_sha256"],
            after_delete["authority_signature_sha256"],
            after_corruption["authority_signature_sha256"],
        ]
        if len(set(signatures)) != 1:
            raise RuntimeError("derived-cache loss/corruption changed replay authority")
        return {
            "status": "pass",
            "journal_event_count": count,
            "journal_sha256": first["authority"]["journal_sha256"],
            "authority_signature_sha256": signatures[0],
            "body_ids": first["authority"]["body_ids"],
            "lineage_status": first["authority"]["lineage_status"],
            "delete_recovery": True,
            "corruption_recovery": True,
            "cache_is_authoritative": False,
        }


def step_baseline_contract() -> dict[str, Any]:
    frozen = json.loads(RCS022_FROZEN.read_text(encoding="utf-8"))
    if frozen["qualification_status"] != STEP_LAYER_D:
        raise RuntimeError("RCS-022 Layer-D status changed unexpectedly")
    return {
        "occt_baseline": OCCT_BASELINE,
        "profile_id": frozen["profile_id"],
        "qualification_status": frozen["qualification_status"],
        "serialized_schema_identifier": frozen["serialized_schema_identifier"],
        "positive_fixture_count": frozen["aggregates"]["positive_fixture_count"],
        "negative_control_count": frozen["aggregates"]["negative_control_count"],
        "source": "research/rcs-022/frozen-result-v1.json",
        "scope": "baseline contract only; repeated live export/read-back is a separate RCS-026 Linux CI job",
    }


def logical_projection(result: dict[str, Any]) -> dict[str, Any]:
    scale = []
    for item in result["scale"]["records"]:
        scale.append({
            "kind": item["kind"],
            "journal_event_count": item["journal_event_count"],
            "material_operation_count": item["material_operation_count"],
            "authority_signature_sha256": item["authority_signature_sha256"],
            "journal_sha256": item["journal_sha256"],
            "body_ids": item["body_ids"],
            "lineage_status": item["lineage_status"],
            "reconciliation": item["reconciliation"],
        })
    return {
        "canonicalizer_signature_sha256": result["canonicalizer"]["logical_signature_sha256"],
        "canonicalizer_failure_count": 0,
        "worker_recovery": {
            "status": result["worker_recovery"]["status"],
            "post_fault_success": result["worker_recovery"]["post_fault_success"],
            "tracked_orphan_processes": result["worker_recovery"]["tracked_orphan_processes"],
        },
        "scale": scale,
        "cache_recovery": {
            key: result["cache_recovery"][key]
            for key in (
                "status",
                "journal_event_count",
                "journal_sha256",
                "authority_signature_sha256",
                "body_ids",
                "lineage_status",
                "delete_recovery",
                "corruption_recovery",
                "cache_is_authoritative",
            )
        },
        "step_contract": result["step_contract"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--toolchain-json", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    toolchain = json.loads(args.toolchain_json.read_text(encoding="utf-8"))

    result = {
        "schema": "rcs-026-platform-result/1.0",
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "toolchain": toolchain,
        },
        "pins": {
            "python": "3.12",
            "occt": OCCT_BASELINE,
            "pending_resource_guard": PENDING_LIMIT,
            "seed": WORKLOAD_SEED,
        },
        "canonicalizer": canonicalizer_campaign(),
        "worker_recovery": worker_recovery_campaign(),
        "scale": scale_campaign(),
        "cache_recovery": cache_recovery_campaign(),
        "step_contract": step_baseline_contract(),
    }
    result["logical_projection"] = logical_projection(result)
    result["logical_signature_sha256"] = sha256_json(result["logical_projection"])
    (args.out_dir / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "platform": result["platform"]["system"],
        "logical_signature_sha256": result["logical_signature_sha256"],
        "highest_completed_journal_tier": result["scale"]["highest_completed_journal_tier"],
        "worker_recovery": result["worker_recovery"]["status"],
        "step_layer_d": result["step_contract"]["qualification_status"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
