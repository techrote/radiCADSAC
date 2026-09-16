#!/usr/bin/env python3
"""Validate durable RCS-005 STEP conformance artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "research/rcs-005/conformance-v1.json"
FIXTURES_PATH = ROOT / "research/rcs-005/fixtures-v1.json"
REPORT_PATH = ROOT / "docs/13-STEP-CONFORMANCE-CONTRACT.md"
README_PATH = ROOT / "research/rcs-005/README.md"
DECISION_PATH = ROOT / "docs/decisions/DR-0009-step-conformance-and-body-preservation.md"

REQUIRED_FILES = (CONTRACT_PATH, FIXTURES_PATH, REPORT_PATH, README_PATH, DECISION_PATH)
REQUIRED_LAYERS = {
    "pre_export",
    "serialized_file",
    "readback",
    "interoperability_qualification",
}
REQUIRED_RESULT_STATES = {"success", "refused", "failed", "unqualified"}
REQUIRED_FAILURE_CODES = {
    "PREVIEW_STATE_NOT_EXPORTABLE",
    "BODY_SELECTION_INVALID",
    "PREEXPORT_INVALID_TOPOLOGY",
    "PREEXPORT_NONVOLUMETRIC_BODY",
    "RECONCILIATION_UNRESOLVED",
    "HEALING_BUDGET_EXCEEDED",
    "SERIALIZATION_FAILED",
    "SCHEMA_PROFILE_MISMATCH",
    "UNIT_OR_SCALE_MISMATCH",
    "BODY_COUNT_MISMATCH",
    "READBACK_INVALID_TOPOLOGY",
    "GEOMETRIC_DEVIATION_EXCEEDED",
    "ANALYTIC_GEOMETRY_LOST",
    "VOID_OR_CONNECTIVITY_MISMATCH",
    "INDEPENDENT_PARSE_FAILED",
    "PROFILE_NOT_INTEROPERABILITY_QUALIFIED",
    "DOWNSTREAM_CONSUMER_FAILURE",
}
REQUIRED_ANALYTIC = {"plane", "cylinder", "cone", "sphere", "torus", "line", "circle_or_arc"}
REQUIRED_FIXTURES = {
    "step-lathe-analytic-mm-v1",
    "step-block-inch-v1",
    "step-block-mm-equivalent-v1",
    "step-enclosed-cavity-v1",
    "step-lathe-parting-all-bodies-v1",
    "step-mill-cut-through-all-bodies-v1",
    "step-parting-explicit-subset-v1",
    "step-same-domain-cleanup-v1",
    "step-analytic-cone-cylinder-v1",
    "step-freeform-spline-v1",
    "step-near-tolerance-feature-v1",
    "step-invalid-open-shell-refusal-v1",
}

errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        error(f"{path.relative_to(ROOT)} cannot be parsed: {exc}")
        return {}
    if not isinstance(data, dict):
        error(f"{path.relative_to(ROOT)} root must be an object")
        return {}
    return data


for path in REQUIRED_FILES:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")

contract = load_json(CONTRACT_PATH) if CONTRACT_PATH.is_file() else {}
fixtures = load_json(FIXTURES_PATH) if FIXTURES_PATH.is_file() else {}

if contract:
    if contract.get("contract_schema") != "msac-step-conformance/1.0":
        error("unexpected conformance contract schema")

    target = contract.get("protocol_target")
    if not isinstance(target, dict):
        error("protocol_target must be an object")
    else:
        if target.get("family") != "AP242":
            error("protocol target must be AP242")
        if target.get("published_reference") != "ISO 10303-242:2025 Edition 4":
            error("published AP242 reference must be ISO 10303-242:2025 Edition 4")
        if "cert" in str(target.get("claim_boundary", "")).lower():
            # Claim-boundary wording may mention certification only to reject it.
            pass

    baseline = contract.get("baseline_exporter")
    if not isinstance(baseline, dict):
        error("baseline_exporter must be an object")
    else:
        if baseline.get("version") != "8.0.1":
            error("baseline exporter must be OCCT 8.0.1")
        if baseline.get("commit") != "b8f597c677811d1f9f4d8a97f5ae2825c0353a42":
            error("baseline exporter commit is not pinned correctly")
        if baseline.get("profile_id") != "occt-8.0.1-ap242dis":
            error("unexpected baseline profile_id")

    primary = contract.get("primary_geometry")
    if not isinstance(primary, dict):
        error("primary_geometry must be an object")
    else:
        required = set(primary.get("required", []))
        if not {"MANIFOLD_SOLID_BREP", "BREP_WITH_VOIDS"}.issubset(required):
            error("primary geometry must include manifold solid B-rep and B-rep with voids")
        forbidden = set(primary.get("not_sufficient_as_primary", []))
        for item in ("FACETED_BREP", "TESSELLATED_ONLY", "STL_OR_MESH_FALLBACK"):
            if item not in forbidden:
                error(f"primary geometry must reject {item} as sufficient output")

    layers = contract.get("validation_layers")
    observed_layers: set[str] = set()
    if not isinstance(layers, list):
        error("validation_layers must be a list")
    else:
        for index, layer in enumerate(layers):
            if not isinstance(layer, dict):
                error(f"validation_layers[{index}] must be an object")
                continue
            layer_id = layer.get("id")
            if isinstance(layer_id, str):
                if layer_id in observed_layers:
                    error(f"duplicate validation layer {layer_id}")
                observed_layers.add(layer_id)
            checks = layer.get("checks")
            if not isinstance(checks, list) or not checks:
                error(f"validation layer {layer_id!r} has no checks")
        if observed_layers != REQUIRED_LAYERS:
            error(f"validation layers must be exactly {sorted(REQUIRED_LAYERS)}")

    units = contract.get("units")
    if not isinstance(units, dict):
        error("units must be an object")
    else:
        export_units = set(units.get("required_export_units", []))
        if not {"millimeter", "inch"}.issubset(export_units):
            error("millimeter and inch conformance are both required")
        dims = units.get("required_equivalence_dimensions_mm")
        if not isinstance(dims, list) or not {25.4, 12.7, 6.35}.issubset(set(dims)):
            error("unit equivalence dimensions must include 25.4, 12.7 and 6.35 mm")

    analytic = contract.get("analytic_preservation")
    if not isinstance(analytic, dict):
        error("analytic_preservation must be an object")
    elif not REQUIRED_ANALYTIC.issubset(set(analytic.get("required_classes_when_exact_in_source", []))):
        error("analytic preservation class set is incomplete")

    body = contract.get("body_policy")
    if not isinstance(body, dict):
        error("body_policy must be an object")
    else:
        if body.get("default_selection") != "all material bodies in selected committed revision":
            error("default body selection must preserve all material bodies")
        for field in (
            "implicit_primary_body_forbidden",
            "explicit_subset_allowed",
            "silent_fuse_forbidden",
            "silent_drop_forbidden",
            "refuse_if_no_qualified_lossless_strategy",
        ):
            if body.get(field) is not True:
                error(f"body_policy.{field} must be true")
        strategies = set(body.get("qualified_representation_strategies", []))
        if strategies != {"single_product_multi_solid", "explicit_body_product_structure"}:
            error("body representation strategies are incomplete")

    if set(contract.get("result_states", [])) != REQUIRED_RESULT_STATES:
        error("result_states must contain success/refused/failed/unqualified exactly")
    if set(contract.get("failure_codes", [])) != REQUIRED_FAILURE_CODES:
        missing = sorted(REQUIRED_FAILURE_CODES - set(contract.get("failure_codes", [])))
        extra = sorted(set(contract.get("failure_codes", [])) - REQUIRED_FAILURE_CODES)
        error(f"failure code taxonomy mismatch; missing={missing}, extra={extra}")

    interoperability = contract.get("interoperability")
    if not isinstance(interoperability, dict):
        error("interoperability must be an object")
    else:
        if "STEPcode" not in str(interoperability.get("automated_independent_parser", "")):
            error("independent parser strategy must name STEPcode")
        if interoperability.get("vendor_is_not_authoritative") is not True:
            error("no single downstream vendor may be authoritative")

if fixtures:
    if fixtures.get("fixture_matrix_schema") != "msac-step-conformance-fixtures/1.0":
        error("unexpected fixture matrix schema")
    if fixtures.get("contract_ref") != "msac-step-conformance/1.0":
        error("fixture matrix must reference msac-step-conformance/1.0")

    default_accuracy = fixtures.get("default_accuracy")
    required_accuracy = {
        "max_dimension_error_nm",
        "max_surface_deviation_nm",
        "max_angular_error_nrad",
        "max_volume_error_abs_mm3",
        "max_volume_error_rel",
        "volume_rule",
    }
    if not isinstance(default_accuracy, dict) or not required_accuracy.issubset(default_accuracy):
        error("default fixture accuracy declaration is incomplete")

    entries = fixtures.get("fixtures")
    fixture_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(entries, list):
        error("fixtures must be a list")
    else:
        for index, item in enumerate(entries):
            if not isinstance(item, dict):
                error(f"fixtures[{index}] must be an object")
                continue
            fixture_id = item.get("fixture_id")
            if not isinstance(fixture_id, str) or not fixture_id:
                error(f"fixtures[{index}] has no fixture_id")
                continue
            if fixture_id in fixture_by_id:
                error(f"duplicate fixture_id {fixture_id}")
            fixture_by_id[fixture_id] = item
            if not isinstance(item.get("purpose"), list) or not item["purpose"]:
                error(f"fixture {fixture_id} must declare purpose")

        missing = sorted(REQUIRED_FIXTURES - set(fixture_by_id))
        if missing:
            error(f"missing required STEP fixture(s): {missing}")

        for fixture_id in ("step-lathe-parting-all-bodies-v1", "step-mill-cut-through-all-bodies-v1"):
            item = fixture_by_id.get(fixture_id, {})
            if item.get("expected_body_count") != 2 or item.get("expected_connectivity") != "disconnected":
                error(f"{fixture_id} must preserve two disconnected material bodies")
            forbidden = set(item.get("forbid", []))
            if not {"silent_drop", "silent_fuse", "implicit_primary_body"}.issubset(forbidden):
                error(f"{fixture_id} must forbid silent loss/fuse/primary-body selection")

        inch = fixture_by_id.get("step-block-inch-v1", {})
        metric = fixture_by_id.get("step-block-mm-equivalent-v1", {})
        if inch.get("unit") != "inch" or metric.get("unit") != "millimeter":
            error("unit equivalence pair must cover inch and millimeter")
        if inch.get("required_dimensions_mm") != metric.get("required_dimensions_mm"):
            error("unit equivalence pair must describe identical physical dimensions")

        negative = fixture_by_id.get("step-invalid-open-shell-refusal-v1", {})
        if negative.get("expected_result") != "refused":
            error("negative open-shell fixture must be refused")
        if negative.get("expected_failure_code") != "PREEXPORT_NONVOLUMETRIC_BODY":
            error("negative open-shell fixture has wrong failure code")

        cavity = fixture_by_id.get("step-enclosed-cavity-v1", {})
        if cavity.get("expected_void_count") != 1:
            error("enclosed-cavity fixture must require one void")

        subset = fixture_by_id.get("step-parting-explicit-subset-v1", {})
        if subset.get("body_selection") != "explicit_subset" or subset.get("revision_body_count") != 2:
            error("explicit subset fixture must begin from a two-body revision")
        if subset.get("selected_body_count") != 1 or subset.get("expected_body_count") != 1:
            error("explicit subset fixture must export exactly one explicitly selected body")

if REPORT_PATH.is_file():
    report = REPORT_PATH.read_text(encoding="utf-8")
    required_report_terms = (
        "msac-step-conformance/1.0",
        "ISO 10303-242:2025",
        "AP242DIS",
        "## Four-layer validation model",
        "## Geometric and topological acceptance metrics",
        "## Units and scale",
        "## Analytic geometry preservation",
        "## Healing and same-domain cleanup",
        "## One-body and multi-body policy",
        "## Failure and refusal taxonomy",
        "## Minimal RCS-006 conformance fixture matrix",
        "STEPcode",
        "all material bodies",
        "writer return code",
    )
    for term in required_report_terms:
        if term not in report:
            error(f"STEP conformance report missing required term/section {term!r}")

if DECISION_PATH.is_file():
    decision = DECISION_PATH.read_text(encoding="utf-8")
    for term in ("Status: accepted", "all material bodies", "AP242-family", "writer return status"):
        if term not in decision:
            error(f"DR-0009 missing required term {term!r}")

if errors:
    print("RCS-005 STEP conformance validation failed:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)

print(
    "RCS-005 STEP conformance validation passed "
    f"({len(REQUIRED_FIXTURES)} fixtures, {len(REQUIRED_FAILURE_CODES)} failure codes)"
)
