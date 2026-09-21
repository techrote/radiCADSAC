#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-054"
CONTRACT = TASK / "engineering-output-profile-v1.json"

EXPECTED_SOURCE_BASELINE = "1b86aff77958dd1f0330f0a5aac9631a8ebef1b3"
EXPECTED_DEPS = {
    "MC-005": ("research/machining-completeness/tasks/MC-005/outcome.json", "adec886597a06345fdfdf65ee018596cd396d249", "CAPABILITY_ACCEPTED"),
    "MC-016": ("research/machining-completeness/tasks/MC-016/outcome.json", "606a7d0b8be61131b2272f2eb161d6a4dbba703a", "COMPLETED_RESEARCH"),
    "MC-017": ("research/machining-completeness/tasks/MC-017/outcome.json", "e7dbfce169febd81de5e0025df204ebd7f8cc53f", "COMPLETED_RESEARCH"),
}
EXPECTED_BLOCKERS = {"RB-016-01", "RB-016-02", "RB-016-03", "RB-016-04", "RB-016-05", "XB-017-01"}
EXPECTED_CLASSES = {f"EO-054-{i:02d}" for i in range(1, 7)}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def validate_contract(contract: dict, *, check_files: bool = True) -> None:
    assert contract["schema"] == "radicadsac-mc054-engineering-output-profile/1.0"
    assert contract["task"] == "MC-054"
    assert contract["issue"] == 116
    assert contract["source_baseline"] == EXPECTED_SOURCE_BASELINE
    assert contract["result"] == "COMPLETED_RESEARCH_PROFILE_DECIDED_QUALIFICATION_OPEN"
    assert contract["native_execution"] is False

    deps = {d["task"]: d for d in contract["formal_dependencies"]}
    assert set(deps) == set(EXPECTED_DEPS)
    for task, (path, blob_sha, result_kind) in EXPECTED_DEPS.items():
        dep = deps[task]
        assert dep["path"] == path
        assert dep["blob_sha"] == blob_sha
        assert dep["result_kind"] == result_kind
        if check_files:
            dep_path = ROOT / path
            assert dep_path.is_file()
            assert git_blob_sha1(dep_path) == blob_sha, f"{task} dependency drift"

    standards = {s["id"]: s for s in contract["standards_sources"]}
    assert set(standards) == {"STEP-ABSR", "STEP-MSB"}
    assert "advanced_brep_shape_representation" in standards["STEP-ABSR"]["url"]
    absr_claim = standards["STEP-ABSR"]["claim"].lower()
    assert "requires at least one" in absr_claim
    assert "not restricted to a single" in absr_claim
    assert "manifold_solid_brep" in standards["STEP-MSB"]["url"]
    assert "one outer closed_shell" in standards["STEP-MSB"]["claim"].lower()

    profile = contract["profile"]
    assert profile["id"] == "MC-ENG-OUTPUT/1.0"
    assert profile["status"] == "VERSIONED_PROFILE_DECISION"
    assert profile["binding_manifest"] == "engineering-output-manifest.json"
    authority = profile["authority_rules"]
    assert "nominal material" in authority["canonical_material_authority"]
    assert "durable-body/lineage" in authority["canonical_body_authority"]
    assert authority["step_geometry_is_derived"] is True
    assert authority["step_topology_may_define_body_identity"] is False
    assert authority["consumer_repair_may_change_material"] is False
    assert authority["faceted_or_tessellated_primary_success"] is False

    required_manifest = set(profile["manifest_required_fields"])
    assert {
        "source_material_certificate_digest",
        "source_body_lineage_digest",
        "contact_relations",
        "empty_transition",
    } <= required_manifest

    classes = {c["id"]: c for c in profile["classes"]}
    assert set(classes) == EXPECTED_CLASSES

    regular = classes["EO-054-01"]
    assert regular["material_state"] == "NONEMPTY"
    assert "MANIFOLD_SOLID_BREP" in regular["step_policy"]
    assert "kernel handle is authority" in regular["manifest_policy"]

    multi = classes["EO-054-02"]
    assert multi["material_state"] == "NONEMPTY_GROUPED"
    assert "every retained body" in multi["step_policy"]
    assert "one-to-one binding" in multi["manifest_policy"]
    assert {"FUSE_DURABLE_BODIES", "DROP_SMALL_COMPONENT", "GEOMETRIC_NEAREST_MATCH_AS_IDENTITY"} <= set(multi["forbidden"])

    contact = classes["EO-054-03"]
    assert "separate manifold-solid items" in contact["step_policy"]
    assert "source-certificate-bound" in contact["manifest_policy"]
    assert {"HEAL_CONTACT", "ADD_BRIDGE", "TOLERANCE_FUSE"} <= set(contact["forbidden"])

    singular = classes["EO-054-04"]
    assert "certified finite decomposition" in singular["step_policy"]
    assert "NON_MATERIAL_PARTITION" in singular["manifest_policy"]
    singular_piece = singular["representation_piece_policy"]
    assert "interiors must be disjoint" in singular_piece
    assert "union must equal the canonical material set" in singular_piece
    assert "AUXILIARY_SEAM_BECOMES_MATERIAL" in singular["forbidden"]

    micro = classes["EO-054-05"]
    assert "without rounding a positive feature to zero" in micro["step_policy"]
    assert "TOLERANCE_ERASE_POSITIVE_MATERIAL" in micro["forbidden"]

    empty = classes["EO-054-06"]
    assert empty["material_state"] == "EMPTY"
    assert "no nonempty STEP geometry" in empty["step_policy"]
    assert "step_artifacts must be an empty list" in empty["step_policy"]
    assert "exhausted/disappeared" in empty["manifest_policy"]
    assert {"FAKE_EPSILON_SOLID", "EMPTY_PLACEHOLDER_COUNTED_AS_NONEMPTY_PASS", "DROP_LINEAGE"} <= set(empty["forbidden"])

    grouped = profile["grouped_decomposition_contract"]
    reqs = " ".join(grouped["piece_requirements"])
    assert "certified subset of canonical material" in reqs
    assert "pairwise interior-disjoint" in reqs
    assert "certified union equals" in reqs
    assert "nominal/source certificate" in grouped["contact_semantics"]
    assert grouped["auxiliary_seams"] == "NON_MATERIAL_PARTITION"
    assert grouped["may_change_canonical_body_identity"] is False

    empty_contract = profile["empty_contract"]
    assert empty_contract["success_state"] == "EMPTY_MATERIAL"
    assert empty_contract["step_artifacts"] == []
    assert empty_contract["representation_pieces"] == []
    assert empty_contract["require_exhausted_body_lineage"] is True
    assert empty_contract["consumer_geometry_import"] == "NOT_APPLICABLE_EMPTY"
    assert empty_contract["follow_on_geometry_request"] == "EMPTY_NO_GEOMETRY"
    assert empty_contract["placeholder_step_allowed"] is False
    assert empty_contract["epsilon_solid_allowed"] is False

    consumer = contract["consumer_evidence_plan"]
    nonempty_route = consumer["nonempty_route"].lower()
    assert "mc-017" in nonempty_route and "brl-cad" in nonempty_route
    assert "strict/exact/no-repair" in nonempty_route
    assert "geometric-nearest or largest-body heuristics" in nonempty_route
    controls = " ".join(consumer["required_controls"]).lower()
    for term in ("known-good", "known-bad", "materially-wrong", "exact-zero-contact", "singular decomposition", "micro-feature", "empty manifest-only"):
        assert term in controls
    nonempty_accept = " ".join(consumer["nonempty_acceptance"]).lower()
    assert "no consumer fusion" in nonempty_accept
    assert "downstream operation consumes imported geometry" in nonempty_accept
    empty_accept = " ".join(consumer["empty_acceptance"])
    assert "EMPTY_MATERIAL" in empty_accept
    assert "NOT_APPLICABLE_EMPTY" in empty_accept
    assert "EMPTY_NO_GEOMETRY" in empty_accept
    assert consumer["qualification_owner"] == "MC-043"
    assert consumer["native_campaign_harness_owner"] == "MC-045"
    assert consumer["execution_status"] == "NOT_RUN_BY_MC-054"

    blockers = {b["id"]: b for b in contract["blockers"]}
    assert set(blockers) == EXPECTED_BLOCKERS
    assert all(b["status"] == "OPEN" for b in blockers.values())
    assert "profile-decision portion is resolved" in blockers["RB-016-04"]["remaining_obligation"]
    assert "profile-decision portion is resolved" in blockers["RB-016-05"]["remaining_obligation"]
    assert "MC-043" in blockers["XB-017-01"]["remaining_obligation"]

    assert contract["capability_guard"] == {
        "MC-A": "ACCEPTED",
        "MC-B": "NOT_ESTABLISHED",
        "MC-C": "NOT_ESTABLISHED",
        "MC-D": "NOT_ESTABLISHED",
        "MC-E": "NOT_ESTABLISHED",
        "MC-F": "NOT_ESTABLISHED",
        "MC-1": "NOT_ESTABLISHED",
    }


def adversarial_self_test(contract: dict) -> None:
    mutations = []

    bad = copy.deepcopy(contract)
    bad["profile"]["authority_rules"]["step_topology_may_define_body_identity"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["profile"]["binding_manifest"] = ""
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["profile"]["classes"][1]["step_policy"] = "keep only the largest body"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["profile"]["classes"][2]["forbidden"].remove("TOLERANCE_FUSE")
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["profile"]["classes"][3]["manifest_policy"] = bad["profile"]["classes"][3]["manifest_policy"].replace("NON_MATERIAL_PARTITION", "PHYSICAL_MATERIAL_BOUNDARY")
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["profile"]["classes"][3]["representation_piece_policy"] = "pieces may overlap and need only approximate the material"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["profile"]["classes"][4]["forbidden"].remove("TOLERANCE_ERASE_POSITIVE_MATERIAL")
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["profile"]["classes"][5]["step_policy"] = "emit a placeholder STEP solid"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["profile"]["empty_contract"]["epsilon_solid_allowed"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["profile"]["empty_contract"]["require_exhausted_body_lineage"] = False
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["blockers"][3]["status"] = "CLOSED"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["capability_guard"]["MC-C"] = "ACCEPTED"
    mutations.append(bad)

    rejected = 0
    for bad in mutations:
        try:
            validate_contract(bad, check_files=False)
        except (AssertionError, KeyError, TypeError):
            rejected += 1
    assert rejected == len(mutations), f"accepted {len(mutations) - rejected} adversarial corruption(s)"


def verify_integration() -> None:
    contract = load(CONTRACT)
    validate_contract(contract, check_files=True)
    adversarial_self_test(contract)

    outcome = load(TASK / "outcome.json")
    assert outcome["schema"] == "radicadsac-mc-task-outcome/1.0"
    assert outcome["task"] == "MC-054"
    assert outcome["result_kind"] == "COMPLETED_RESEARCH"
    assert outcome["native_execution"] is False
    assert {b["id"] for b in outcome["blockers"]} == EXPECTED_BLOCKERS
    assert all(b["status"] == "OPEN" for b in outcome["blockers"])
    assert outcome["review"]["gate_changed"] is False
    assert outcome["review"]["gate"] == "MC-C"
    assert outcome["review"]["gate_status"] == "NOT_ESTABLISHED"
    assert outcome["review"]["programme_capability_changed"] is False

    outcomes = load(ROOT / "research/machining-completeness/outcomes-v1.json")
    record = outcomes["tasks"]["MC-054"]
    assert record["state"] == "COMPLETED_RESEARCH"
    assert {b["id"] for b in record["blockers"]} == EXPECTED_BLOCKERS
    assert all(b["status"] == "OPEN" for b in record["blockers"])
    required_artifacts = {
        "research/machining-completeness/tasks/MC-054/engineering-output-profile-v1.json",
        "research/machining-completeness/tasks/MC-054/report.md",
        "research/machining-completeness/tasks/MC-054/outcome.json",
        "research/machining-completeness/tasks/MC-054/verify.py",
        "docs/machining-completeness/04-REPRESENTATION-AND-RECONSTRUCTION.md",
    }
    assert required_artifacts <= set(record["accepted_artifacts"])

    doc = (ROOT / "docs/machining-completeness/04-REPRESENTATION-AND-RECONSTRUCTION.md").read_text(encoding="utf-8")
    assert "MC-054 engineering-output profile" in doc
    assert "MC-ENG-OUTPUT/1.0" in doc
    assert "NON_MATERIAL_PARTITION" in doc
    assert "EMPTY_MATERIAL" in doc
    assert "NOT_APPLICABLE_EMPTY" in doc
    assert "RB-016-04" in doc and "RB-016-05" in doc
    assert "MC-C remains **NOT_ESTABLISHED**" in doc

    workflow = (ROOT / ".github/workflows/mc1-static.yml").read_text(encoding="utf-8")
    assert "tasks/MC-054/verify.py" in workflow
    assert "tools/mc_workflow.py verify MC-054" in workflow


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract or --self-test")
    verify_integration()
    print("MC-054 engineering-output profile contract verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
