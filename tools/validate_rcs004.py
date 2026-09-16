#!/usr/bin/env python3
"""Validate the durable RCS-004 OCCT audit artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COMMIT = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
EXPECTED_TAG = "V8_0_1"

REQUIRED_FILES = (
    ROOT / "docs/12-OCCT-8.0.1-AUDIT.md",
    ROOT / "research/rcs-004/README.md",
    ROOT / "research/rcs-004/audit-map.json",
    ROOT / "research/rcs-004/probes/verify_occt_source.py",
)

ALLOWED_CLASSIFICATIONS = {
    "reuse",
    "wrap/isolate",
    "modify/fork candidate",
    "replace candidate",
    "research only / insufficient evidence",
}

REQUIRED_SUBSYSTEMS = {
    "brep_topology",
    "entity_tolerances",
    "analytic_geometry",
    "boolean_orchestration",
    "boolean_intersection_classification",
    "general_fuse_cells",
    "same_domain_unification",
    "shape_healing",
    "brep_validation",
    "sweep_pipe_loft",
    "operation_history",
    "durable_programme_provenance",
    "ocaf_tnaming",
    "meshing",
    "step_exchange",
    "data_exchange_global_state",
    "threading_global_parallel",
    "memory_ownership",
    "build_platform",
    "license_boundary",
}

REQUIRED_UNRESOLVED = {
    "baseline_failure_envelope",
    "tolerance_equivalence_mapping",
    "general_fuse_material_semantics",
    "history_semantic_completeness",
    "step_conformance_policy",
    "concurrent_exchange_isolation",
    "windows_toolkit_footprint",
    "production_distribution_compliance",
}

errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def require_nonempty_string(item: dict[str, Any], field: str, where: str) -> None:
    if not isinstance(item.get(field), str) or not item[field].strip():
        error(f"{where}: {field} must be a non-empty string")


for path in REQUIRED_FILES:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")

map_path = ROOT / "research/rcs-004/audit-map.json"
data: dict[str, Any] = {}
if map_path.is_file():
    try:
        loaded = json.loads(map_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            data = loaded
        else:
            error("audit-map.json root must be an object")
    except json.JSONDecodeError as exc:
        error(f"audit-map.json cannot be parsed: {exc}")

if data:
    if data.get("schema") != "rcs-004-occt-audit/1.0":
        error("unexpected audit schema")

    upstream = data.get("audited_upstream")
    if not isinstance(upstream, dict):
        error("audited_upstream must be an object")
    else:
        if upstream.get("repository") != "Open-Cascade-SAS/OCCT":
            error("audited repository must be Open-Cascade-SAS/OCCT")
        if upstream.get("tag") != EXPECTED_TAG:
            error(f"audited tag must be {EXPECTED_TAG}")
        if upstream.get("commit") != EXPECTED_COMMIT:
            error(f"audited commit must be {EXPECTED_COMMIT}")
        if not isinstance(upstream.get("tree"), str) or len(upstream["tree"]) != 40:
            error("audited tree must be a 40-character SHA")
        if upstream.get("release_date") != "2026-07-30":
            error("unexpected audited release date")

    declared = data.get("classification_values")
    if not isinstance(declared, list) or set(declared) != ALLOWED_CLASSIFICATIONS:
        error("classification_values must contain exactly the five RCS-004 classes")

    subsystems = data.get("subsystems")
    subsystem_ids: set[str] = set()
    classifications: set[str] = set()
    if not isinstance(subsystems, list):
        error("subsystems must be a list")
    else:
        for index, item in enumerate(subsystems):
            where = f"subsystems[{index}]"
            if not isinstance(item, dict):
                error(f"{where}: must be an object")
                continue
            subsystem_id = item.get("id")
            if not isinstance(subsystem_id, str) or not subsystem_id:
                error(f"{where}: missing id")
            elif subsystem_id in subsystem_ids:
                error(f"{where}: duplicate id {subsystem_id}")
            else:
                subsystem_ids.add(subsystem_id)

            classification = item.get("classification")
            if classification not in ALLOWED_CLASSIFICATIONS:
                error(f"{where}: invalid classification {classification!r}")
            else:
                classifications.add(classification)

            for field in ("area", "reversibility", "finding", "boundary"):
                require_nonempty_string(item, field, where)

            evidence = item.get("evidence")
            if not isinstance(evidence, list) or not evidence or not all(
                isinstance(url, str) and url.startswith("https://") for url in evidence
            ):
                error(f"{where}: evidence must be a non-empty HTTPS URL list")
            else:
                for url in evidence:
                    if "Open-Cascade-SAS/OCCT/blob/" in url or "Open-Cascade-SAS/OCCT/tree/" in url:
                        if EXPECTED_COMMIT not in url:
                            error(f"{where}: OCCT source evidence is not pinned to audited commit: {url}")

        missing = sorted(REQUIRED_SUBSYSTEMS - subsystem_ids)
        if missing:
            error(f"missing required subsystem classifications: {missing}")
        if classifications != ALLOWED_CLASSIFICATIONS:
            error(
                "subsystem map must exercise all five classification values; "
                f"observed {sorted(classifications)}"
            )

    fork_seams = data.get("fork_candidate_seams")
    if not isinstance(fork_seams, list) or len(fork_seams) < 3:
        error("fork_candidate_seams must contain at least three explicit seams")
    else:
        for index, item in enumerate(fork_seams):
            if not isinstance(item, dict):
                error(f"fork_candidate_seams[{index}] must be an object")
                continue
            require_nonempty_string(item, "id", f"fork_candidate_seams[{index}]")
            require_nonempty_string(item, "trigger", f"fork_candidate_seams[{index}]")

    unresolved = data.get("unresolved")
    unresolved_ids: set[str] = set()
    if not isinstance(unresolved, list):
        error("unresolved must be a list")
    else:
        for index, item in enumerate(unresolved):
            if not isinstance(item, dict):
                error(f"unresolved[{index}] must be an object")
                continue
            require_nonempty_string(item, "id", f"unresolved[{index}]")
            require_nonempty_string(item, "owner", f"unresolved[{index}]")
            require_nonempty_string(item, "question", f"unresolved[{index}]")
            if isinstance(item.get("id"), str):
                unresolved_ids.add(item["id"])
        missing_unresolved = sorted(REQUIRED_UNRESOLVED - unresolved_ids)
        if missing_unresolved:
            error(f"missing required unresolved questions: {missing_unresolved}")

    velocity = data.get("upstream_velocity_evidence")
    if not isinstance(velocity, list) or len(velocity) < 3:
        error("upstream_velocity_evidence must contain release/current-development evidence")

report_path = ROOT / "docs/12-OCCT-8.0.1-AUDIT.md"
if report_path.is_file():
    report = report_path.read_text(encoding="utf-8")
    required_report_terms = (
        EXPECTED_COMMIT,
        "## Initial subsystem/forkability map",
        "## License and derivative-work implications",
        "## Upstream velocity and deep-fork maintenance risk",
        "## Candidate fork seams",
        "## Risks and unresolved questions carried forward",
        "OPEN / NOT LEGAL ADVICE",
        "Interface_Static",
        "DESTEP_Parameters",
        "BRepTools_History",
        "BOPAlgo_CellsBuilder",
        "ShapeUpgrade_UnifySameDomain",
    )
    for term in required_report_terms:
        if term not in report:
            error(f"audit report missing required term/section {term!r}")

if errors:
    print("RCS-004 audit validation failed:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)

print(
    "RCS-004 audit validation passed "
    f"({len(REQUIRED_SUBSYSTEMS)} subsystem areas, {len(REQUIRED_UNRESOLVED)} unresolved questions)"
)
