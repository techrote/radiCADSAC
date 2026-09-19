#!/usr/bin/env python3
"""Validate RCS-026 static contracts and generated qualification evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/rcs-026"
PLAN = BASE / "experiment-plan-v1.json"
WORKFLOW = ROOT / ".github/workflows/rcs026.yml"
RUNNER = BASE / "run_campaign.py"
STEP = BASE / "summarize_step_soak.py"
TOOLCHAIN_CMAKE = BASE / "toolchain/CMakeLists.txt"

EXPECTED_PYTHON = "3.12.10"
EXPECTED_GCC_NUMERIC = 130300
EXPECTED_MSVC_NUMERIC = 1951
RESOURCE_COUNT_LEAK_ALLOWANCE = 4
RSS_GROWTH_GUARD_BYTES = 67108864


def fail(message: str) -> None:
    raise SystemExit(f"RCS-026 validation failed: {message}")


def validate_static() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    if plan.get("schema") != "rcs-026-experiment-plan/1.1":
        fail("experiment plan schema")
    if plan.get("status") != "predeclared_before_measured_campaign":
        fail("plan must remain visibly predeclared after measurements as the historical preregistration")
    fixed = plan.get("fixed_inputs", {})
    expected_fixed = {
        "journal_tiers": [10000, 100000],
        "provider_pending_resource_guard": 2,
        "linux_live_step_soak_repetitions": 3,
        "long_soak_epochs": 20,
        "long_soak_events_per_epoch": 5000,
        "resource_count_leak_allowance": RESOURCE_COUNT_LEAK_ALLOWANCE,
        "rss_growth_guard_bytes": RSS_GROWTH_GUARD_BYTES,
    }
    for key, expected in expected_fixed.items():
        if fixed.get(key) != expected:
            fail(f"fixed input {key} drift")

    matrix = plan.get("platform_matrix", {})
    linux = matrix.get("linux", {})
    windows = matrix.get("windows", {})
    if linux.get("github_runner") != "ubuntu-24.04":
        fail("Linux runner pin")
    if windows.get("github_runner") != "windows-2025":
        fail("Windows runner pin")
    if linux.get("compiler_family") != "GCC" or linux.get("compiler_version_numeric") != EXPECTED_GCC_NUMERIC:
        fail("GCC compiler/version pin")
    if windows.get("compiler_family") != "MSVC" or windows.get("compiler_version_numeric") != EXPECTED_MSVC_NUMERIC:
        fail("MSVC compiler/version pin")
    if linux.get("python") != EXPECTED_PYTHON or windows.get("python") != EXPECTED_PYTHON:
        fail("Python runtime pin")
    if matrix.get("occt_baseline", {}).get("version") != "8.0.1":
        fail("OCCT baseline drift")
    build = plan.get("build_profile", {})
    if build.get("cmake_generator") != "Ninja" or build.get("cpp_standard") != "C++17":
        fail("portable C++ build profile")
    if build.get("msvc_cpp_macro_flag") != "/Zc:__cplusplus":
        fail("MSVC language-mode reporting flag")
    deps = plan.get("external_dependency_pins", {})
    if deps.get("step_io") != "0.2.4" or deps.get("vcad_kernel_step") != "0.10.0":
        fail("independent STEP dependency pins")
    if plan.get("qualification_rules", {}).get("layer_d") != "interoperability_unqualified":
        fail("RCS-022 measured Layer-D negative must be preserved")
    if {x.get("id") for x in plan.get("hypotheses", [])} != {"H1", "H2", "H3", "H4", "H5", "H6"}:
        fail("hypothesis/falsification matrix")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "ubuntu-24.04",
        "windows-2025",
        "python-version: '3.12.10'",
        "-G Ninja",
        "compare_platform_results.py",
        "summarize_step_soak.py",
        "research/rcs-022/run_campaign.py",
        "tools/validate_rcs022.py --summary",
        "cargo build --locked",
    ):
        if token not in workflow:
            fail(f"workflow missing {token!r}")

    cmake = TOOLCHAIN_CMAKE.read_text(encoding="utf-8")
    for token in ("cxx_std_17", "CXX_EXTENSIONS OFF", "/Zc:__cplusplus"):
        if token not in cmake:
            fail(f"toolchain CMake contract missing {token!r}")

    runner = RUNNER.read_text(encoding="utf-8")
    for token in (
        'STEP_LAYER_D = "interoperability_unqualified"',
        'OCCT_BASELINE = "8.0.1"',
        "RCS018_WORKER",
        "PENDING_LIMIT = 2",
        "RESOURCE_COUNT_LEAK_ALLOWANCE = 4",
        "RSS_GROWTH_GUARD_BYTES = 64 * 1024 * 1024",
        "LONG_SOAK_EPOCHS = 20",
        "LONG_SOAK_EVENTS_PER_EPOCH = 5_000",
        "process_resource_snapshot",
        "GetProcessHandleCount",
        'os.listdir("/proc/self/fd")',
        "conflicting_configuration_campaign",
        "100_000",
        "cache_is_authoritative",
        "preserved_programme_identity",
    ):
        if token not in runner:
            fail(f"campaign contract missing {token!r}")
    if "backend_topology" in runner or "TopoDS" in runner:
        fail("private kernel identity leaked into programme authority campaign")
    if "interoperability_qualified" in STEP.read_text(encoding="utf-8"):
        fail("STEP soak must not manufacture a positive Layer-D verdict")


def validate_result(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "rcs-026-platform-result/1.1":
        fail("platform result schema")
    platform_data = data.get("platform", {})
    system = platform_data.get("system")
    toolchain = platform_data.get("toolchain", {})
    compiler = toolchain.get("compiler_id")
    compiler_version = toolchain.get("compiler_version_numeric")
    if system == "Windows":
        if compiler != "MSVC" or compiler_version != EXPECTED_MSVC_NUMERIC:
            fail("Windows MSVC pin drift")
    elif system == "Linux":
        if compiler != "GCC" or compiler_version != EXPECTED_GCC_NUMERIC:
            fail("Linux GCC pin drift")
    else:
        fail(f"unexpected platform {system!r}")
    if platform_data.get("python") != EXPECTED_PYTHON:
        fail("platform Python pin drift")
    if int(toolchain.get("cplusplus", 0)) < 201703:
        fail("C++17 language mode not demonstrated")
    build_tools = platform_data.get("build_tools", {})
    if not str(build_tools.get("cmake", "")).startswith("cmake version "):
        fail("CMake version not recorded")
    if build_tools.get("ninja") in {None, "", "unavailable", "unknown"}:
        fail("Ninja version not recorded")

    pins = data.get("pins", {})
    if pins.get("python") != EXPECTED_PYTHON or pins.get("occt") != "8.0.1":
        fail("runtime/baseline pin")
    if pins.get("resource_count_leak_allowance") != RESOURCE_COUNT_LEAK_ALLOWANCE:
        fail("resource leak guard pin")
    if pins.get("rss_growth_guard_bytes") != RSS_GROWTH_GUARD_BYTES:
        fail("RSS guard pin")

    if data.get("canonicalizer", {}).get("status") != "pass":
        fail("canonicalizer result")
    isolation = data.get("configuration_isolation", {})
    if isolation.get("status") != "pass" or not isolation.get("separate_processes") or not isolation.get("low_repeat_equal"):
        fail("conflicting configuration isolation")

    worker = data.get("worker_recovery", {})
    if worker.get("status") != "pass" or not worker.get("post_fault_success"):
        fail("worker recovery")
    if worker.get("tracked_orphan_processes") != 0:
        fail("tracked worker leak")
    if worker.get("resource_observation", {}).get("resource_count_delta", 999) > RESOURCE_COUNT_LEAK_ALLOWANCE:
        fail("worker-cycle coordinator handle/fd growth")
    if not all(x.get("reaped") for x in worker.get("observations", [])):
        fail("unreaped worker child")

    scale = data.get("scale", {})
    if scale.get("highest_completed_journal_tier") != 100000:
        fail("100k tier not completed")
    if {x.get("kind") for x in scale.get("records", [])} != {"lathe", "mill", "mixed"}:
        fail("scale workload families")
    if len(scale.get("records", [])) != 6:
        fail("10k/100k platform scale matrix")
    for row in scale.get("records", []):
        if row.get("journal_event_count") not in {10000, 100000}:
            fail("unexpected scale tier")
        if row.get("material_operation_count") != row.get("journal_event_count") * 3 // 4:
            fail("journal/material operation distinction")
        if row.get("reconciliation", {}).get("peak_pending_units", 999) > 2:
            fail("pending-state resource guard exceeded")
        if row.get("body_ids") != ["body-main"]:
            fail("body mapping changed")
        if row.get("lineage_status") != "preserved_programme_identity":
            fail("lineage authority changed")
        if row.get("throughput_events_per_second", 0) <= 0:
            fail("scale throughput missing")

    soak = data.get("long_soak", {})
    if soak.get("status") != "pass" or soak.get("epochs") != 20 or soak.get("events_per_epoch") != 5000:
        fail("long-soak profile")
    if soak.get("journal_event_count") != 100000 or soak.get("material_operation_count") != 75000:
        fail("long-soak event/material counts")
    if soak.get("query_boundaries") != 20 or soak.get("worker_recycle_successes") != 4:
        fail("long-soak query/recycle coverage")
    if soak.get("peak_pending_units", 999) > 2:
        fail("long-soak pending-state bound")
    if soak.get("body_ids") != ["body-main"] or soak.get("lineage_status") != "preserved_programme_identity":
        fail("long-soak body/lineage authority")
    if soak.get("export_gate_status") != "interoperability_unqualified":
        fail("long-soak export status boundary")
    trend = soak.get("resource_trend", {})
    if trend.get("working_set_delta_bytes", RSS_GROWTH_GUARD_BYTES + 1) > RSS_GROWTH_GUARD_BYTES:
        fail("long-soak RSS growth guard")
    if trend.get("resource_count_delta", RESOURCE_COUNT_LEAK_ALLOWANCE + 1) > RESOURCE_COUNT_LEAK_ALLOWANCE:
        fail("long-soak handle/fd growth guard")

    cache = data.get("cache_recovery", {})
    if not cache.get("delete_recovery") or not cache.get("corruption_recovery"):
        fail("cache recovery")
    if cache.get("cache_is_authoritative") is not False:
        fail("derived cache became authority")
    if cache.get("body_ids") != ["body-main"] or cache.get("lineage_status") != "preserved_programme_identity":
        fail("cache replay body/lineage mapping")

    resources = data.get("coordinator_resource_observations", {})
    if not {"start", "after_canonicalizer", "after_worker_recovery", "after_scale", "after_long_soak", "end"}.issubset(resources):
        fail("coordinator resource trend checkpoints")
    if any(x.get("working_set_bytes", 0) <= 0 for x in resources.values()):
        fail("native RSS observation")
    if any(x.get("resource_count", 0) <= 0 for x in resources.values()):
        fail("handle/fd observation")

    if data.get("step_contract", {}).get("qualification_status") != "interoperability_unqualified":
        fail("Layer-D status drift")
    if len(data.get("logical_signature_sha256", "")) != 64:
        fail("logical signature")


def validate_cross(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "rcs-026-cross-platform-summary/1.0" or data.get("status") != "pass":
        fail("cross-platform comparison")
    if data.get("mismatches") != []:
        fail("cross-platform mismatch")
    linux = data.get("linux", {}).get("toolchain", {})
    windows = data.get("windows", {}).get("toolchain", {})
    if linux.get("compiler_id") != "GCC" or linux.get("compiler_version_numeric") != EXPECTED_GCC_NUMERIC:
        fail("cross-platform Linux compiler pin")
    if windows.get("compiler_id") != "MSVC" or windows.get("compiler_version_numeric") != EXPECTED_MSVC_NUMERIC:
        fail("cross-platform Windows compiler pin")
    if int(linux.get("cplusplus", 0)) < 201703 or int(windows.get("cplusplus", 0)) < 201703:
        fail("cross-platform C++17 proof")


def validate_step(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "rcs-026-step-soak-summary/1.0" or data.get("status") != "pass":
        fail("STEP soak summary")
    if data.get("live_repetitions", 0) < 3:
        fail("STEP soak repetition count")
    if data.get("qualification_status") != "interoperability_unqualified":
        fail("STEP soak Layer-D status")
    projection = data.get("projection", {})
    if projection.get("all_negative_controls_pass") is not True:
        fail("STEP soak adversarial controls")
    if projection.get("all_positive_qualified") is not False:
        fail("STEP soak must preserve measured positive-fixture blockers")
    blocker = data.get("windows_step_soak", {}).get("gate5_blocker", "")
    if data.get("windows_step_soak", {}).get("status") != "not_run":
        fail("unexpected Windows STEP claim")
    if "Windows" not in blocker or "OCCT 8.0.1" not in blocker:
        fail("Windows STEP Gate-5 blocker not explicit")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path)
    parser.add_argument("--cross-summary", type=Path)
    parser.add_argument("--step-summary", type=Path)
    args = parser.parse_args()
    validate_static()
    if args.result:
        validate_result(args.result)
    if args.cross_summary:
        validate_cross(args.cross_summary)
    if args.step_summary:
        validate_step(args.step_summary)
    print("RCS-026 validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
