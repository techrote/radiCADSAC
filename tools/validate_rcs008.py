#!/usr/bin/env python3
"""Validate RCS-008 provenance/semantic-identity research and optional runtime evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_OCCT_COMMIT = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
EXPECTED_RELATIONS = {"preserved", "generated", "split", "merged", "replaced", "retired", "ambiguous"}
EXPECTED_ANCHORS = {
    "stock_region",
    "material_body",
    "setup_revision",
    "operation",
    "tool_revision",
    "tool_envelope",
    "material_boundary_role",
    "reconciliation_event",
}
EXPECTED_MODES = {"replay_cut", "split_cut", "overlap_cuts", "same_domain_merge", "repeated_finish"}

REQUIRED_FILES = (
    ROOT / "docs/16-PROVENANCE-SEMANTIC-IDENTITY-RESEARCH.md",
    ROOT / "docs/decisions/DR-0011-semantic-lineage-not-topology-id.md",
    ROOT / "research/rcs-008/README.md",
    ROOT / "research/rcs-008/experiment-plan-v1.json",
    ROOT / "research/rcs-008/harness/CMakeLists.txt",
    ROOT / "research/rcs-008/harness/provenance_worker.cpp",
    ROOT / "research/rcs-008/harness/run_provenance_campaign.py",
)

errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        error(f"{path.relative_to(ROOT)}: cannot load JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        error(f"{path.relative_to(ROOT)}: root must be an object")
        return {}
    return value


for path in REQUIRED_FILES:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")

plan_path = ROOT / "research/rcs-008/experiment-plan-v1.json"
plan = load_object(plan_path) if plan_path.is_file() else {}
if plan:
    if plan.get("experiment_plan_schema") != "rcs-008-experiment-plan/1.0":
        error("unexpected RCS-008 experiment plan schema")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict) or baseline.get("commit") != EXPECTED_OCCT_COMMIT:
        error("RCS-008 baseline must pin the accepted OCCT commit")
    if set(plan.get("lineage_relation_types", [])) != EXPECTED_RELATIONS:
        error("lineage_relation_types must contain the complete RCS-008 relation vocabulary")
    if set(plan.get("semantic_anchor_types", [])) != EXPECTED_ANCHORS:
        error("semantic_anchor_types must contain the complete RCS-008 anchor vocabulary")
    worker_cases = plan.get("worker_cases")
    modes = {
        item.get("mode")
        for item in worker_cases
        if isinstance(worker_cases, list) and isinstance(item, dict)
    } if isinstance(worker_cases, list) else set()
    if not EXPECTED_MODES.issubset(modes):
        error(f"worker experiment modes missing: {sorted(EXPECTED_MODES - modes)}")
    hypotheses = plan.get("hypotheses")
    if not isinstance(hypotheses, list) or len(hypotheses) < 4:
        error("plan must define at least four explicit hypotheses/falsification criteria")
    elif any(not isinstance(item, dict) or not item.get("falsification") for item in hypotheses):
        error("every RCS-008 hypothesis must state a falsification criterion")

report_path = ROOT / "docs/16-PROVENANCE-SEMANTIC-IDENTITY-RESEARCH.md"
if report_path.is_file():
    report = report_path.read_text(encoding="utf-8")
    required_terms = (
        "## Hypotheses and falsification criteria",
        "## Candidate semantic lineage model",
        "## Split, merge, replacement, and ambiguity semantics",
        "## Deterministic replay contract",
        "## Lathe example",
        "## Mill example",
        "## OCCT operation-history evidence",
        "## Naive topology identity failure",
        "## Interaction with RCS-007",
        "## Interaction with RCS-009",
        "## STEP/export traceability",
        "## Architecture recommendation",
        "## Unresolved questions",
        "BRepTools_History",
        "TNaming",
        "ambiguous",
        EXPECTED_OCCT_COMMIT,
    )
    for term in required_terms:
        if term not in report:
            error(f"research report missing required section/term {term!r}")

runner_path = ROOT / "research/rcs-008/harness/run_provenance_campaign.py"
if runner_path.is_file():
    runner = runner_path.read_text(encoding="utf-8")
    for term in (
        "rcs-008-semantic-lineage/1.0",
        "rcs-008-retrace-proof/1.0",
        "symmetric_ambiguous_split",
        "arbitrary_numeric_topology_name_forbidden",
        "intervening_intersecting_material_mutation",
    ):
        if term not in runner:
            error(f"campaign runner missing required concept {term!r}")

worker_path = ROOT / "research/rcs-008/harness/provenance_worker.cpp"
if worker_path.is_file():
    worker = worker_path.read_text(encoding="utf-8")
    for term in (
        "BRepTools_History",
        "ShapeUpgrade_UnifySameDomain",
        "IsSame",
        "SetToFillHistory(true)",
        EXPECTED_OCCT_COMMIT,
    ):
        if term not in worker:
            error(f"OCCT provenance worker missing required concept {term!r}")

parser = argparse.ArgumentParser()
parser.add_argument("--results-dir", type=Path)
args = parser.parse_args()

if args.results_dir is not None:
    results_path = args.results_dir / "results.json"
    summary_path = args.results_dir / "summary.md"
    if not results_path.is_file():
        error(f"runtime results missing: {results_path}")
    if not summary_path.is_file():
        error(f"runtime summary missing: {summary_path}")
    results = load_object(results_path) if results_path.is_file() else {}
    if results:
        if results.get("results_schema") != "rcs-008-results/1.0":
            error("unexpected RCS-008 runtime result schema")
        backend = results.get("backend")
        if not isinstance(backend, dict) or backend.get("commit") != EXPECTED_OCCT_COMMIT:
            error("runtime results do not report the exact OCCT commit")
        records = results.get("worker_records")
        if not isinstance(records, list) or len(records) < 5:
            error("runtime results lack the required worker cases")
        else:
            modes = {item.get("mode") for item in records if isinstance(item, dict)}
            if not EXPECTED_MODES.issubset(modes):
                error(f"runtime worker cases missing modes: {sorted(EXPECTED_MODES - modes)}")
            failures = [item for item in records if not isinstance(item, dict) or item.get("status") != "measured"]
            if failures:
                error(f"runtime evidence contains {len(failures)} worker failures")
            for index, item in enumerate(records):
                if isinstance(item, dict) and item.get("status") == "measured":
                    payload = item.get("payload")
                    if not isinstance(payload, dict) or payload.get("worker_schema") != "rcs-008-provenance-worker/1.0":
                        error(f"worker_records[{index}] lacks a valid worker payload")

        lineage = results.get("semantic_lineage")
        if not isinstance(lineage, dict) or lineage.get("model_schema") != "rcs-008-semantic-lineage/1.0":
            error("runtime results lack the semantic-lineage model")
        else:
            events = lineage.get("events")
            relation_types = {item.get("relation_type") for item in events if isinstance(events, list) and isinstance(item, dict)} if isinstance(events, list) else set()
            if not {"split", "merged", "replaced", "ambiguous"}.issubset(relation_types):
                error("semantic-lineage runtime events lack split/merge/replacement/ambiguity coverage")
            ambiguity = lineage.get("ambiguity_policy")
            if not isinstance(ambiguity, dict) or ambiguity.get("result") != "ambiguous" or not ambiguity.get("arbitrary_numeric_topology_name_forbidden"):
                error("runtime ambiguity policy does not preserve unresolved ambiguity")
            proof = lineage.get("retrace_proof")
            required_proof = {
                "target_material_body",
                "setup_revision",
                "tool_revision",
                "material_removal_envelope",
                "canonical_operation_semantics_equal",
                "intervening_intersecting_material_mutation",
                "journal_event_preserved",
                "geometry_recompute_elision_candidate",
            }
            if not isinstance(proof, dict) or not required_proof.issubset(proof):
                error("runtime retrace proof is incomplete")

        summary = results.get("summary")
        required_summary = {
            "worker_cases",
            "worker_failures",
            "replay_engineering_equivalent",
            "replay_same_face_identity_matches",
            "split_result_solids",
            "split_one_to_many_source_faces",
            "overlap_face_relations",
            "same_domain_faces_before",
            "same_domain_faces_after",
            "same_domain_many_to_one_descendants",
            "repeated_finish_engineering_equivalent",
            "explicit_ambiguous_cases",
            "retrace_proof_candidate",
        }
        if not isinstance(summary, dict) or not required_summary.issubset(summary):
            error("runtime summary is incomplete")
        elif summary.get("worker_failures") != 0:
            error("runtime summary reports worker failures")

if errors:
    print("RCS-008 validation failed:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)

print("RCS-008 validation passed")
