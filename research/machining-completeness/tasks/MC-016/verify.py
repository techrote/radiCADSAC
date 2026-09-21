#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-016"
CONTRACT = TASK / "representability-screen-v1.json"

EXPECTED_BLOCKERS = {
    "RB-016-01",
    "RB-016-02",
    "RB-016-03",
    "RB-016-04",
    "RB-016-05",
}
EXPECTED_CLASSES = [f"OC-016-{i:02d}" for i in range(1, 9)]
FORBIDDEN_PRIMARY_FORMS = {
    "FACETED_BREP_AS_PRIMARY_SUCCESS",
    "TESSELLATED_BREP_AS_PRIMARY_SUCCESS",
    "TRIANGULATE_AND_COUNT_AS_ENGINEERING_SUCCESS",
    "FAKE_EPSILON_SOLID",
    "KEEP_LARGEST_ONLY",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def validate_contract(contract: dict, *, check_files: bool = True) -> None:
    assert contract["schema"] == "radicadsac-mc016-representability-screen/1.0"
    assert contract["task"] == "MC-016"
    assert contract["issue"] == 78
    assert contract["source_baseline"] == "b2fac16b2285b4cb517e3e01c58a9900152327b5"
    assert contract["result"] == "COMPLETED_RESEARCH_WITH_OPEN_REPRESENTABILITY_BLOCKERS"
    assert contract["native_execution"] is False

    deps = {d["task"]: d for d in contract["dependencies"]}
    assert set(deps) == {"MC-002", "MC-003", "MC-010"}
    assert all(d["result_kind"] == "COMPLETED_RESEARCH" for d in deps.values())

    pins = {p["role"]: p for p in contract["historical_source_pins"]}
    assert set(pins) == {
        "native-occt-step-roundtrip-and-negative-controls",
        "independent-material-and-external-comparator-controls",
        "exact-small-material-boundary-controls",
    }
    assert pins["native-occt-step-roundtrip-and-negative-controls"]["evidence_class"] == "MEASURED_NATIVE_GEOMETRY"
    assert pins["exact-small-material-boundary-controls"]["evidence_class"] == "MEASURED_DETERMINISTIC_MODEL"

    if check_files:
        for row in contract["dependencies"] + contract["historical_source_pins"]:
            path = ROOT / row["path"]
            assert path.is_file(), row["path"]
            assert git_blob_sha1(path) == row["blob_sha"], f"source drift: {row['path']}"

        rcs011 = load(ROOT / "research/rcs-011/measured-summary-v1.json")
        assert rcs011["selected_findings"]["step_roundtrip"]["successful_attempt_count"] == 32
        wrong = rcs011["selected_findings"]["retrace_jitter_freehand_batch"]
        assert wrong["candidate_valid_brep"] is True
        assert wrong["classification"] == "geometric tolerance breach"
        assert rcs011["selected_findings"]["sampled_pose_fallback"]["timeout_count"] == 10

        rcs021 = load(ROOT / "research/rcs-021/measured-summary-v1.json")
        cut = rcs021["representative_findings"]["cut_through"]
        assert cut["tridexel_body_count"] == cut["oracle_body_count"] == cut["external_body_count"] == 2
        one_um = rcs021["representative_findings"]["plunge_1um"]
        assert one_um["physical_removal_preserved"] is True
        assert one_um["external_classification"] == "refused_resolution_budget"

        rcs012 = load(ROOT / "research/rcs-012/measured-summary-v1.json")
        cusp = rcs012["decisive_cases"]["tiny-cusp-1um"]
        assert cusp["exact_cell"]["body_count"] == 1
        assert cusp["voxel_0p5"]["body_count"] == 0

    sources = {s["id"]: s for s in contract["standards_sources"]}
    assert set(sources) == {"STEP-ABSR", "STEP-MSB", "STEP-BWV"}
    assert all(s["kind"] == "SOURCE_FACT" and s["url"].startswith("https://") for s in sources.values())

    rules = contract["programme_rules"]
    assert rules["primary_output"] == "STEP"
    assert rules["faceted_or_tessellated_as_primary_engineering_success"] is False
    assert rules["may_drop_positive_volume_material"] is False
    assert rules["may_fuse_durable_bodies_at_contact"] is False
    assert rules["may_invent_residual_solid_for_empty_material"] is False
    assert rules["exact_zero_and_positive_neighbours_must_remain_distinct"] is True
    assert rules["changed_output_semantics_owner"] == "MC-054"
    assert rules["independent_consumer_owner"] == "MC-017"

    blockers = {b["id"]: b for b in contract["blockers"]}
    assert set(blockers) == EXPECTED_BLOCKERS
    assert all(b["status"] == "OPEN" and b["affected_descendants"] for b in blockers.values())

    classes = contract["obstruction_classes"]
    assert [c["id"] for c in classes] == EXPECTED_CLASSES
    assert len({c["name"] for c in classes}) == len(classes)

    for case in classes:
        witness = case["native_witness"]
        blocker_id = case["blocker_id"]
        assert witness["qualifying"] is True or blocker_id in blockers, (
            f"{case['id']} has neither qualifying native witness nor explicit blocker"
        )
        if blocker_id is not None:
            assert blocker_id in blockers
        form = case["strategy"]["step_form"].upper()
        assert not any(token in form for token in FORBIDDEN_PRIMARY_FORMS), (
            f"forbidden primary-output route in {case['id']}: {form}"
        )

    regular = classes[0]
    assert regular["native_witness"]["qualifying"] is True
    assert regular["blocker_id"] is None
    assert "MANIFOLD_SOLID_BREP" in regular["strategy"]["step_form"]
    assert {
        "FACETED_BREP_AS_PRIMARY_SUCCESS",
        "TESSELLATED_BREP_AS_PRIMARY_SUCCESS",
    } <= set(regular["strategy"]["forbidden"])

    cavity = classes[1]
    assert cavity["blocker_id"] == "RB-016-01"
    assert cavity["strategy"]["step_form"] == "BREP_WITH_VOIDS"
    cavity_req = " ".join(cavity["strategy"]["requirements"]).lower()
    assert "disjoint" in cavity_req and "enclosed" in cavity_req

    multi = classes[2]
    assert multi["blocker_id"] == "RB-016-02"
    assert "multiple MANIFOLD_SOLID_BREP items" in multi["strategy"]["step_form"]
    assert {"KEEP_LARGEST_ONLY", "FUSE_COMPONENTS", "DROP_SMALL_COMPONENT"} <= set(multi["strategy"]["forbidden"])

    micro = classes[3]
    assert micro["blocker_id"] == "RB-016-03"
    assert {"TOLERANCE_ERASE_POSITIVE_MATERIAL", "SEW_ACROSS_GAP", "DROP_SLIVER"} <= set(micro["strategy"]["forbidden"])

    contact, touching_void, singular, empty = classes[4:]
    assert all(c["strategy"]["status"] == "PROFILE_DECISION_REQUIRED" for c in (contact, touching_void, singular, empty))
    assert all(c["blocker_id"] == "RB-016-04" for c in (contact, touching_void, singular))
    assert empty["blocker_id"] == "RB-016-05"
    assert "FAKE_EPSILON_SOLID" in empty["strategy"]["forbidden"]
    assert "HEAL_CONTACT" in contact["strategy"]["forbidden"]
    assert "SEPARATE_WITH_FAKE_WALL" in touching_void["strategy"]["forbidden"]
    assert "HEAL_PINCH" in singular["strategy"]["forbidden"]

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
    bad["obstruction_classes"][1]["blocker_id"] = None
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["capability_guard"]["MC-C"] = "ACCEPTED"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["obstruction_classes"][2]["strategy"]["step_form"] = "KEEP_LARGEST_ONLY"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["obstruction_classes"][7]["strategy"]["step_form"] = "FAKE_EPSILON_SOLID"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["obstruction_classes"][4]["strategy"]["forbidden"].remove("HEAL_CONTACT")
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["programme_rules"]["exact_zero_and_positive_neighbours_must_remain_distinct"] = False
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["historical_source_pins"][2]["evidence_class"] = "MEASURED_NATIVE_GEOMETRY"
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
    assert outcome["task"] == "MC-016"
    assert outcome["result_kind"] == "COMPLETED_RESEARCH"
    assert outcome["native_execution"] is False
    assert {b["id"] for b in outcome["blockers"]} == EXPECTED_BLOCKERS
    assert outcome["review"]["gate_changed"] is False

    outcomes = load(ROOT / "research/machining-completeness/outcomes-v1.json")
    record = outcomes["tasks"]["MC-016"]
    assert record["state"] == "COMPLETED_RESEARCH"
    assert {b["id"] for b in record["blockers"]} == EXPECTED_BLOCKERS
    required_artifacts = {
        "research/machining-completeness/tasks/MC-016/representability-screen-v1.json",
        "research/machining-completeness/tasks/MC-016/report.md",
        "research/machining-completeness/tasks/MC-016/outcome.json",
        "research/machining-completeness/tasks/MC-016/verify.py",
        "docs/machining-completeness/04-REPRESENTATION-AND-RECONSTRUCTION.md",
    }
    assert required_artifacts <= set(record["accepted_artifacts"])

    doc = (ROOT / "docs/machining-completeness/04-REPRESENTATION-AND-RECONSTRUCTION.md").read_text(encoding="utf-8")
    assert "MC-016 representability screen" in doc
    assert "MC-C remains **NOT_ESTABLISHED**" in doc
    assert "RB-016-01" in doc and "RB-016-05" in doc
    assert "valid-but-materially-wrong" in doc
    assert "faceted" in doc.lower() and "not" in doc.lower()

    workflow = (ROOT / ".github/workflows/mc1-static.yml").read_text(encoding="utf-8")
    assert "tasks/MC-016/verify.py" in workflow
    assert "tools/mc_workflow.py verify MC-016" in workflow


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract or --self-test")
    verify_integration()
    print("MC-016 representability-screen contract verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
