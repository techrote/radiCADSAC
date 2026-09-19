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


def fail(message: str) -> None:
    raise SystemExit(f"RCS-026 validation failed: {message}")


def validate_static() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    if plan.get("schema") != "rcs-026-experiment-plan/1.0":
        fail("experiment plan schema")
    if plan.get("status") != "predeclared_before_measured_campaign":
        fail("plan must remain visibly predeclared until measured evidence is frozen")
    fixed = plan.get("fixed_inputs", {})
    if fixed.get("journal_tiers") != [10000, 100000]:
        fail("10k/100k scale tiers")
    if fixed.get("provider_pending_resource_guard") != 2:
        fail("RCS-025 bounded stress guard")
    if fixed.get("linux_live_step_soak_repetitions") != 3:
        fail("live STEP soak repeat count")
    matrix = plan.get("platform_matrix", {})
    if matrix.get("linux", {}).get("github_runner") != "ubuntu-24.04":
        fail("Linux runner pin")
    if matrix.get("windows", {}).get("github_runner") != "windows-2025":
        fail("Windows runner pin")
    if matrix.get("windows", {}).get("compiler_family") != "MSVC":
        fail("MSVC platform requirement")
    if matrix.get("occt_baseline", {}).get("version") != "8.0.1":
        fail("OCCT baseline drift")
    if plan.get("qualification_rules", {}).get("layer_d") != "interoperability_unqualified":
        fail("RCS-022 measured Layer-D negative must be preserved")
    if {x.get("id") for x in plan.get("hypotheses", [])} != {"H1", "H2", "H3", "H4", "H5", "H6"}:
        fail("hypothesis/falsification matrix")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "ubuntu-24.04",
        "windows-2025",
        "python-version: '3.12'",
        "compare_platform_results.py",
        "summarize_step_soak.py",
        "research/rcs-022/run_campaign.py",
        "tools/validate_rcs022.py --summary",
        "cargo build --locked",
    ):
        if token not in workflow:
            fail(f"workflow missing {token!r}")

    runner = RUNNER.read_text(encoding="utf-8")
    for token in (
        'STEP_LAYER_D = "interoperability_unqualified"',
        'OCCT_BASELINE = "8.0.1"',
        "RCS018_WORKER",
        "PENDING_LIMIT = 2",
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
    if data.get("schema") != "rcs-026-platform-result/1.0":
        fail("platform result schema")
    system = data.get("platform", {}).get("system")
    compiler = data.get("platform", {}).get("toolchain", {}).get("compiler_id")
    if system == "Windows" and compiler != "MSVC":
        fail("Windows did not use MSVC")
    if system == "Linux" and compiler not in {"GCC", "Clang"}:
        fail("Linux compiler family")
    if system not in {"Windows", "Linux"}:
        fail(f"unexpected platform {system!r}")
    if data.get("pins", {}).get("occt") != "8.0.1":
        fail("result OCCT baseline")
    if data.get("canonicalizer", {}).get("status") != "pass":
        fail("canonicalizer result")
    worker = data.get("worker_recovery", {})
    if worker.get("status") != "pass" or not worker.get("post_fault_success"):
        fail("worker recovery")
    if worker.get("tracked_orphan_processes") != 0:
        fail("tracked worker leak")
    scale = data.get("scale", {})
    if scale.get("highest_completed_journal_tier") != 100000:
        fail("100k tier not completed")
    if {x.get("kind") for x in scale.get("records", [])} != {"lathe", "mill", "mixed"}:
        fail("scale workload families")
    for row in scale.get("records", []):
        if row.get("reconciliation", {}).get("peak_pending_units", 999) > 2:
            fail("pending-state resource guard exceeded")
        if row.get("body_ids") != ["body-main"]:
            fail("body mapping changed")
        if row.get("lineage_status") != "preserved_programme_identity":
            fail("lineage authority changed")
    cache = data.get("cache_recovery", {})
    if not cache.get("delete_recovery") or not cache.get("corruption_recovery"):
        fail("cache recovery")
    if cache.get("cache_is_authoritative") is not False:
        fail("derived cache became authority")
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


def validate_step(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "rcs-026-step-soak-summary/1.0" or data.get("status") != "pass":
        fail("STEP soak summary")
    if data.get("live_repetitions", 0) < 3:
        fail("STEP soak repetition count")
    if data.get("qualification_status") != "interoperability_unqualified":
        fail("STEP soak Layer-D status")
    blocker = data.get("windows_step_soak", {}).get("gate5_blocker", "")
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
