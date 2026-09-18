#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/rcs-022"
EXPECTED_FIXTURES = {
    "metric_block", "metric_cylinder", "inch_equivalent", "analytic_cone",
    "through_hole", "blind_bore", "two_body_parting", "accepted_lathe",
    "accepted_mill", "healed_reconciled", "trimmed_analytic",
}
EXPECTED_NEGATIVE_CODES = {
    "UNIT_OR_SCALE_MISMATCH", "BODY_COUNT_MISMATCH", "VOID_OR_CONNECTIVITY_MISMATCH",
    "ANALYTIC_GEOMETRY_LOST", "GEOMETRIC_DEVIATION_EXCEEDED",
    "INDEPENDENT_PARSE_FAILED", "DOWNSTREAM_CONSUMER_FAILURE",
}


def require(cond: bool, message: str) -> None:
    if not cond:
        raise SystemExit(f"RCS-022 validation failed: {message}")


def validate_static() -> None:
    profile = json.loads((BASE / "profile-v1.json").read_text())
    fixtures = json.loads((BASE / "fixtures-v1.json").read_text())
    readme = (BASE / "README.md").read_text()
    contract = (ROOT / "docs/13-STEP-CONFORMANCE-CONTRACT.md").read_text()
    decision = (ROOT / "docs/decisions/DR-0019-step-layer-d-independent-qualification.md").read_text()
    workflow = (ROOT / ".github/workflows/rcs022.yml").read_text()

    exp = profile["exporter"]
    require(exp["version"] == "8.0.1", "exporter version must remain pinned")
    require(exp["commit"] == "b8f597c677811d1f9f4d8a97f5ae2825c0353a42", "OCCT commit drift")
    require(exp["schema_selector"].endswith("AP242DIS"), "candidate schema selector drift")
    require(exp["model_type"] == "STEPControl_ManifoldSolidBrep", "solid model mode drift")
    require(exp["tessellated"] is False and exp["nonmanifold"] is False, "mesh/nonmanifold fallback enabled")
    require(exp["precision_mode"] == "WriteMode_PrecisionMode_Average", "precision mode drift")
    require(profile["body_policy"]["all_material_bodies_required"] is True, "all-body policy weakened")
    require(profile["body_policy"]["silent_drop_forbidden"] is True, "body drop must remain forbidden")
    require(profile["tolerances"]["no_silent_tolerance_widening"] is True, "tolerance widening permitted")

    parser = profile["layer_d"]["schema_parser"]
    consumer = profile["layer_d"]["solid_consumer"]
    require(parser["commit"] == "ed686ee1d9cb8bf763ab8d61ef6d417c3b45c146", "STEPcode commit drift")
    require(parser["schema_source"] == "data/ap242/242_mim_lf.exp", "AP242 schema source drift")
    require(consumer["commit"] == "eba7a2e6a89ff06801776fbc599d5c8a64036168", "vcad commit drift")
    require("independent" in consumer["independence"].lower(), "consumer independence must be explicit")
    require("AP214" in consumer["documented_protocol_target"], "vcad protocol limitation must be recorded")

    ids = {x["id"] for x in fixtures["positive"]}
    require(ids == EXPECTED_FIXTURES, f"fixture coverage mismatch: {sorted(ids ^ EXPECTED_FIXTURES)}")
    require(set(fixtures["negative_required_codes"]) == EXPECTED_NEGATIVE_CODES, "negative/refusal coverage drift")
    require(next(x for x in fixtures["positive"] if x["id"] == "two_body_parting")["body_count"] == 2, "two-body fixture collapsed")
    require(next(x for x in fixtures["positive"] if x["id"] == "accepted_mill")["body_count"] == 2, "mill cut-through fixture collapsed")
    require(next(x for x in fixtures["positive"] if x["id"] == "inch_equivalent")["export_unit"] == "inch", "inch fixture lost")

    for phrase in ["interoperability_unqualified", "STEPcode", "vcad", "RCS-020", "RCS-021", "AP242DIS", "not an ISO"]:
        require(phrase in readme, f"README missing claim/traceability phrase: {phrase}")
    require("Layer D" in contract and "independent" in contract.lower(), "parent STEP contract no longer preserves Layer-D independence")
    require("interoperability_unqualified" in decision, "decision record must define fail-closed verdict")
    require("SC_BUILD_SCHEMAS" in workflow and "242_mim_lf.exp" in workflow, "workflow does not build pinned AP242 parser")
    require("vcad-probe" in workflow and "run_qualification.py" in workflow, "workflow does not exercise independent solid consumer")


def validate_results(results_dir: Path) -> None:
    path = results_dir / "qualification-results.json"
    require(path.is_file(), f"missing measured results: {path}")
    data = json.loads(path.read_text())
    require(data["profile_id"] == "rcs022-occt-8.0.1-ap242dis-manifold-v1", "measured profile id mismatch")
    require(data["verdict"] in {"qualified", "interoperability_unqualified"}, "invalid verdict")
    require(data["campaign_integrity"] == "pass", "campaign did not complete adversarial gates")
    require({x["id"] for x in data["fixtures"]} == EXPECTED_FIXTURES, "measured fixture matrix incomplete")
    require(data["negative_coverage"]["pass"] is True, "negative/refusal campaign incomplete")
    require(set(data["negative_coverage"]["required"]) == EXPECTED_NEGATIVE_CODES, "measured negative contract mismatch")
    for item in data["fixtures"]:
        if item.get("export_returncode") == 0:
            require(len(item.get("sha256", "")) == 64, f"{item['id']} lacks STEP digest")
            require("stepcode" in item and "consumer" in item, f"{item['id']} lacks Layer-D evidence")
    if data["verdict"] == "qualified":
        require(not data["blockers"], "qualified verdict contains blockers")
        require(all(x.get("pass") for x in data["fixtures"]), "qualified verdict with failed fixture")
    else:
        require(bool(data["blockers"]), "unqualified verdict must name a measured blocker")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=Path)
    ns = ap.parse_args()
    validate_static()
    if ns.results_dir:
        validate_results(ns.results_dir)
    print("RCS-022 validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
