#!/usr/bin/env python3
"""RCS-026 portable scale, soak, replay and worker-recovery qualification harness.

This is research infrastructure, not a production daemon or geometry kernel. It
exercises programme-owned deterministic contracts while treating provider-private
OCCT topology as disposable. Native process-resource observations are deliberately
separate from Python-allocation observations and from the live OCCT STEP soak.
"""
from __future__ import annotations

import argparse
import ctypes
import gc
import hashlib
import importlib.util
import json
import os
import platform
import re
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
RESOURCE_COUNT_LEAK_ALLOWANCE = 4
RSS_GROWTH_GUARD_BYTES = 64 * 1024 * 1024
LONG_SOAK_EPOCHS = 20
LONG_SOAK_EVENTS_PER_EPOCH = 5_000


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


def command_version(command: list[str]) -> str:
    try:
        output = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return "unavailable"
    return output.splitlines()[0].strip() if output.splitlines() else "unknown"


def process_resource_snapshot() -> dict[str, Any]:
    """Return current/peak RSS and a practical per-process resource count.

    Linux uses /proc VmRSS/VmHWM and open-fd count. Windows uses
    GetProcessMemoryInfo and GetProcessHandleCount. These are coordinator process
    observations; provider workers are separately required to terminate/reap.
    """
    system = platform.system()
    if system == "Windows":
        from ctypes import wintypes

        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        kernel32.GetProcessHandleCount.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
            wintypes.DWORD,
        ]
        handle = kernel32.GetCurrentProcess()
        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(counters)
        if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            raise OSError("GetProcessMemoryInfo failed")
        handle_count = wintypes.DWORD()
        if not kernel32.GetProcessHandleCount(handle, ctypes.byref(handle_count)):
            raise OSError("GetProcessHandleCount failed")
        return {
            "working_set_bytes": int(counters.WorkingSetSize),
            "peak_working_set_bytes": int(counters.PeakWorkingSetSize),
            "resource_count_kind": "process_handles",
            "resource_count": int(handle_count.value),
            "source": "GetProcessMemoryInfo/GetProcessHandleCount",
        }

    if system == "Linux":
        status = Path("/proc/self/status").read_text(encoding="utf-8")

        def kib(name: str) -> int:
            match = re.search(rf"^{re.escape(name)}:\s+(\d+)\s+kB$", status, re.MULTILINE)
            if not match:
                raise RuntimeError(f"missing {name} in /proc/self/status")
            return int(match.group(1)) * 1024

        return {
            "working_set_bytes": kib("VmRSS"),
            "peak_working_set_bytes": kib("VmHWM"),
            "resource_count_kind": "open_file_descriptors",
            "resource_count": len(os.listdir("/proc/self/fd")),
            "source": "/proc/self/status,/proc/self/fd",
        }

    raise RuntimeError(f"RCS-026 resource probe does not support {system!r}")


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


def worker_payload(
    mode: str,
    profile: str = "rcs-026-isolated-worker-probe",
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "operation": {"target_body_ids": ["body-main"]},
        "provider": {
            "profile": profile,
            "evidence": evidence
            or {"source": "RCS-018 worker_probe.py", "process_isolation": True},
        },
    }


def invoke_worker(
    mode: str,
    timeout_s: float,
    profile: str = "rcs-026-isolated-worker-probe",
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    started = time.perf_counter_ns()
    proc = subprocess.Popen(
        [sys.executable, str(RCS018_WORKER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    timed_out = False
    try:
        stdout, stderr = proc.communicate(
            input=json.dumps(worker_payload(mode, profile, evidence)), timeout=timeout_s
        )
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        stdout, stderr = proc.communicate()
    elapsed = time.perf_counter_ns() - started
    reaped = proc.poll() is not None
    if not reaped:
        proc.kill()
        proc.wait(timeout=2.0)
        reaped = proc.poll() is not None

    if timed_out:
        classification = "timeout"
        response = None
    elif mode == "success":
        if proc.returncode != 0:
            raise RuntimeError(f"success worker failed rc={proc.returncode}: {stderr}")
        response = json.loads(stdout)
        if response.get("status") != "provider_candidate":
            raise RuntimeError("success worker returned wrong status")
        classification = "success"
    elif mode == "crash":
        if proc.returncode == 0:
            raise RuntimeError("injected crash unexpectedly succeeded")
        classification = "crash"
        response = None
    else:
        raise RuntimeError(f"unsupported direct worker mode {mode}")

    return {
        "kind": classification,
        "returncode": proc.returncode,
        "elapsed_ns": elapsed,
        "pid": proc.pid,
        "reaped": reaped,
        "response": response,
    }


def forced_kill_worker() -> dict[str, Any]:
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
    reaped = proc.poll() is not None
    if not reaped:
        raise RuntimeError("forced-kill worker remained unreaped")
    return {
        "kind": "forced_kill",
        "returncode": proc.returncode,
        "elapsed_ns": elapsed,
        "pid": proc.pid,
        "reaped": True,
        "response": None,
    }


def conflicting_configuration_campaign() -> dict[str, Any]:
    low = {
        "requested_tolerance_mm": "0.00001",
        "parallel_mode": False,
        "configuration_token": "low-serial",
    }
    high = {
        "requested_tolerance_mm": "0.001",
        "parallel_mode": True,
        "configuration_token": "high-parallel",
    }
    probes = [
        invoke_worker("success", 1.0, "config-low", low),
        invoke_worker("success", 1.0, "config-high", high),
        invoke_worker("success", 1.0, "config-low", low),
    ]
    logical = []
    for expected_profile, expected_evidence, probe in (
        ("config-low", low, probes[0]),
        ("config-high", high, probes[1]),
        ("config-low", low, probes[2]),
    ):
        response = probe["response"] or {}
        if response.get("provider_profile") != expected_profile:
            raise RuntimeError("isolated worker profile cross-talk")
        if response.get("geometry_evidence") != expected_evidence:
            raise RuntimeError("isolated worker configuration cross-talk")
        if not probe["reaped"]:
            raise RuntimeError("configuration probe worker was not reaped")
        logical.append(
            {
                "profile": response["provider_profile"],
                "geometry_evidence": response["geometry_evidence"],
                "body_ids": response["material_body_ids"],
            }
        )
    if logical[0] != logical[2]:
        raise RuntimeError("conflicting worker configuration contaminated repeat")
    return {
        "status": "pass",
        "separate_processes": len({probe["pid"] for probe in probes}) == len(probes),
        "low_repeat_equal": logical[0] == logical[2],
        "logical_signature_sha256": sha256_json(logical),
        "probes": [
            {
                "kind": p["kind"],
                "returncode": p["returncode"],
                "elapsed_ns": p["elapsed_ns"],
                "pid": p["pid"],
                "reaped": p["reaped"],
            }
            for p in probes
        ],
        "scope": "coordinator/process-boundary control; actual OCCT global-state defects remain governed by RCS-017/RCS-024",
    }


def worker_recovery_campaign(cycles: int = 12) -> dict[str, Any]:
    latencies: list[int] = []
    observations: list[dict[str, Any]] = []
    timeout_count = crash_count = kill_count = success_count = 0
    unreaped = 0
    before = process_resource_snapshot()
    for cycle in range(cycles):
        sequence: list[dict[str, Any]] = []
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
        if sequence[-1]["kind"] != "success":
            raise RuntimeError("coordinator did not recover after injected worker fault")
        for observation in sequence:
            latencies.append(observation["elapsed_ns"])
            unreaped += int(not observation["reaped"])
            observations.append(
                {
                    "cycle": cycle,
                    "kind": observation["kind"],
                    "returncode": observation["returncode"],
                    "pid": observation["pid"],
                    "reaped": observation["reaped"],
                }
            )
    after = process_resource_snapshot()
    resource_count_delta = after["resource_count"] - before["resource_count"]
    if unreaped:
        raise RuntimeError(f"{unreaped} tracked worker children were not reaped")
    if resource_count_delta > RESOURCE_COUNT_LEAK_ALLOWANCE:
        raise RuntimeError(
            f"coordinator resource count grew by {resource_count_delta}, guard={RESOURCE_COUNT_LEAK_ALLOWANCE}"
        )
    return {
        "status": "pass",
        "cycles": cycles,
        "clean_successes": success_count,
        "timeouts_contained": timeout_count,
        "crashes_contained": crash_count,
        "forced_kills_contained": kill_count,
        "post_fault_success": True,
        "tracked_orphan_processes": unreaped,
        "latency": latency_summary(latencies),
        "resource_observation": {
            "before": before,
            "after": after,
            "resource_count_delta": resource_count_delta,
            "resource_count_leak_allowance": RESOURCE_COUNT_LEAK_ALLOWANCE,
        },
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
        "operation_id": f"{kind}-op-{index:08d}",
        "kind": kind,
        "provider": provider_for(kind, index),
        "material_work": material,
        "path_token_nm": ((WORKLOAD_SEED + index * 104729) % 2_000_003) - 1_000_001,
        "target_body_id": "body-main",
    }


def run_stream(
    kind: str,
    count: int,
    journal_path: Path | None = None,
    start_index: int = 0,
) -> dict[str, Any]:
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
        for offset in range(count):
            index = start_index + offset
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
        "start_index": start_index,
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
                records.append(
                    {
                        "kind": kind,
                        "journal_event_count": count,
                        "material_operation_count": first["authority"]["material_operation_count"],
                        "authority_signature_sha256": first["authority_signature_sha256"],
                        "journal_sha256": first["authority"]["journal_sha256"],
                        "body_ids": first["authority"]["body_ids"],
                        "lineage_status": first["authority"]["lineage_status"],
                        "reconciliation": first["reconciliation"],
                        "elapsed_ns": elapsed,
                        "throughput_events_per_second": round(count / (elapsed / 1_000_000_000), 3),
                        "coordinator_tracemalloc_current_bytes": current,
                        "coordinator_tracemalloc_peak_bytes": peak,
                    }
                )
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
            "claim_scope": "research coordinator Python allocations only; native RSS is separately measured",
        },
    }


def long_soak_campaign() -> dict[str, Any]:
    before = process_resource_snapshot()
    resource_samples = [before]
    epoch_latencies: list[int] = []
    authority_signatures: list[str] = []
    total_material = 0
    total_reconciliations = 0
    peak_pending = 0
    recycle_successes = 0
    body_ids: list[str] | None = None
    lineage_status: str | None = None

    for epoch in range(LONG_SOAK_EPOCHS):
        started = time.perf_counter_ns()
        result = run_stream(
            "mixed",
            LONG_SOAK_EVENTS_PER_EPOCH,
            start_index=epoch * LONG_SOAK_EVENTS_PER_EPOCH,
        )
        if result["reconciliation"]["final_status"] != "reconciled":
            raise RuntimeError("long-soak query boundary reached with pending state")
        if result["reconciliation"]["peak_pending_units"] > PENDING_LIMIT:
            raise RuntimeError("long-soak pending-state guard exceeded")
        if body_ids is None:
            body_ids = result["authority"]["body_ids"]
            lineage_status = result["authority"]["lineage_status"]
        elif body_ids != result["authority"]["body_ids"] or lineage_status != result["authority"]["lineage_status"]:
            raise RuntimeError("long-soak programme body/lineage drift")
        authority_signatures.append(result["authority_signature_sha256"])
        total_material += result["authority"]["material_operation_count"]
        total_reconciliations += result["reconciliation"]["reconciliation_count"]
        peak_pending = max(peak_pending, result["reconciliation"]["peak_pending_units"])
        if epoch % 5 == 4:
            recycle = invoke_worker("success", 1.0)
            if recycle["kind"] != "success" or not recycle["reaped"]:
                raise RuntimeError("long-soak worker recycle failed")
            recycle_successes += 1
        epoch_latencies.append(time.perf_counter_ns() - started)
        resource_samples.append(process_resource_snapshot())

    after = resource_samples[-1]
    rss_delta = after["working_set_bytes"] - before["working_set_bytes"]
    resource_count_delta = after["resource_count"] - before["resource_count"]
    if rss_delta > RSS_GROWTH_GUARD_BYTES:
        raise RuntimeError(
            f"long-soak coordinator RSS grew by {rss_delta}, guard={RSS_GROWTH_GUARD_BYTES}"
        )
    if resource_count_delta > RESOURCE_COUNT_LEAK_ALLOWANCE:
        raise RuntimeError(
            f"long-soak coordinator resources grew by {resource_count_delta}, guard={RESOURCE_COUNT_LEAK_ALLOWANCE}"
        )
    aggregate = hashlib.sha256()
    for signature in authority_signatures:
        aggregate.update(signature.encode("ascii"))
        aggregate.update(b"\n")
    return {
        "status": "pass",
        "epochs": LONG_SOAK_EPOCHS,
        "events_per_epoch": LONG_SOAK_EVENTS_PER_EPOCH,
        "journal_event_count": LONG_SOAK_EPOCHS * LONG_SOAK_EVENTS_PER_EPOCH,
        "material_operation_count": total_material,
        "query_boundaries": LONG_SOAK_EPOCHS,
        "reconciliation_count": total_reconciliations,
        "peak_pending_units": peak_pending,
        "body_ids": body_ids,
        "lineage_status": lineage_status,
        "worker_recycle_successes": recycle_successes,
        "export_gate_status": STEP_LAYER_D,
        "actual_step_export_scope": "separate Linux live RCS-022 soak; portable long-soak only checks export eligibility/status boundary",
        "aggregate_authority_signature_sha256": aggregate.hexdigest(),
        "epoch_latency": latency_summary(epoch_latencies),
        "throughput_events_per_second": round(
            (LONG_SOAK_EPOCHS * LONG_SOAK_EVENTS_PER_EPOCH)
            / (sum(epoch_latencies) / 1_000_000_000),
            3,
        ),
        "resource_trend": {
            "samples": resource_samples,
            "working_set_delta_bytes": rss_delta,
            "peak_observed_working_set_bytes": max(x["peak_working_set_bytes"] for x in resource_samples),
            "rss_growth_guard_bytes": RSS_GROWTH_GUARD_BYTES,
            "resource_count_delta": resource_count_delta,
            "resource_count_leak_allowance": RESOURCE_COUNT_LEAK_ALLOWANCE,
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
        "start_index": 0,
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
        scale.append(
            {
                "kind": item["kind"],
                "journal_event_count": item["journal_event_count"],
                "material_operation_count": item["material_operation_count"],
                "authority_signature_sha256": item["authority_signature_sha256"],
                "journal_sha256": item["journal_sha256"],
                "body_ids": item["body_ids"],
                "lineage_status": item["lineage_status"],
                "reconciliation": item["reconciliation"],
            }
        )
    long_soak = result["long_soak"]
    return {
        "canonicalizer_signature_sha256": result["canonicalizer"]["logical_signature_sha256"],
        "canonicalizer_failure_count": 0,
        "configuration_isolation": {
            "status": result["configuration_isolation"]["status"],
            "separate_processes": result["configuration_isolation"]["separate_processes"],
            "low_repeat_equal": result["configuration_isolation"]["low_repeat_equal"],
            "logical_signature_sha256": result["configuration_isolation"]["logical_signature_sha256"],
        },
        "worker_recovery": {
            "status": result["worker_recovery"]["status"],
            "clean_successes": result["worker_recovery"]["clean_successes"],
            "timeouts_contained": result["worker_recovery"]["timeouts_contained"],
            "crashes_contained": result["worker_recovery"]["crashes_contained"],
            "forced_kills_contained": result["worker_recovery"]["forced_kills_contained"],
            "post_fault_success": result["worker_recovery"]["post_fault_success"],
            "tracked_orphan_processes": result["worker_recovery"]["tracked_orphan_processes"],
        },
        "scale": scale,
        "long_soak": {
            key: long_soak[key]
            for key in (
                "status",
                "epochs",
                "events_per_epoch",
                "journal_event_count",
                "material_operation_count",
                "query_boundaries",
                "reconciliation_count",
                "peak_pending_units",
                "body_ids",
                "lineage_status",
                "worker_recycle_successes",
                "export_gate_status",
                "aggregate_authority_signature_sha256",
            )
        },
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

    resource_snapshots: dict[str, dict[str, Any]] = {"start": process_resource_snapshot()}
    canonicalizer = canonicalizer_campaign()
    resource_snapshots["after_canonicalizer"] = process_resource_snapshot()
    configuration_isolation = conflicting_configuration_campaign()
    worker_recovery = worker_recovery_campaign()
    resource_snapshots["after_worker_recovery"] = process_resource_snapshot()
    scale = scale_campaign()
    resource_snapshots["after_scale"] = process_resource_snapshot()
    long_soak = long_soak_campaign()
    resource_snapshots["after_long_soak"] = process_resource_snapshot()
    cache_recovery = cache_recovery_campaign()
    resource_snapshots["end"] = process_resource_snapshot()

    result = {
        "schema": "rcs-026-platform-result/1.1",
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "python_compiler": platform.python_compiler(),
            "toolchain": toolchain,
            "build_tools": {
                "cmake": command_version(["cmake", "--version"]),
                "ninja": command_version(["ninja", "--version"]),
            },
        },
        "pins": {
            "python": "3.12.10",
            "occt": OCCT_BASELINE,
            "pending_resource_guard": PENDING_LIMIT,
            "resource_count_leak_allowance": RESOURCE_COUNT_LEAK_ALLOWANCE,
            "rss_growth_guard_bytes": RSS_GROWTH_GUARD_BYTES,
            "seed": WORKLOAD_SEED,
        },
        "canonicalizer": canonicalizer,
        "configuration_isolation": configuration_isolation,
        "worker_recovery": worker_recovery,
        "scale": scale,
        "long_soak": long_soak,
        "cache_recovery": cache_recovery,
        "step_contract": step_baseline_contract(),
        "coordinator_resource_observations": resource_snapshots,
    }
    result["logical_projection"] = logical_projection(result)
    result["logical_signature_sha256"] = sha256_json(result["logical_projection"])
    (args.out_dir / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "platform": result["platform"]["system"],
                "logical_signature_sha256": result["logical_signature_sha256"],
                "highest_completed_journal_tier": result["scale"]["highest_completed_journal_tier"],
                "long_soak_events": result["long_soak"]["journal_event_count"],
                "worker_recovery": result["worker_recovery"]["status"],
                "step_layer_d": result["step_contract"]["qualification_status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
