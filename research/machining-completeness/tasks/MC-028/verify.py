#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-028"
CONTRACT = TASK / "native-mesh-boolean-falsification-v1.json"
OUTCOME = TASK / "outcome.json"
REPORT = TASK / "report.md"
DOC = ROOT / "docs" / "machining-completeness" / "20-MC028-NATIVE-MESH-BOOLEAN.md"
REGISTRY = ROOT / "research" / "machining-completeness" / "outcomes-v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "mc1-static.yml"

EXPECTED_BASELINE = "e21aa9fa45959ebc3a6f3a3a56fca26a4cb6af1f"
EXPECTED_DEPS = {
    "MC-010": ("research/machining-completeness/tasks/MC-010/outcome.json", "4960730316f89dbb3fbf958d054127fa4fc0d789", "COMPLETED_RESEARCH"),
    "MC-016": ("research/machining-completeness/tasks/MC-016/outcome.json", "606a7d0b8be61131b2272f2eb161d6a4dbba703a", "COMPLETED_RESEARCH"),
    "MC-018": ("research/machining-completeness/tasks/MC-018/outcome.json", "085f864b4bd58b38f154b6c9d58d9e68b60ee7ec", "COMPLETED_RESEARCH"),
    "MC-019": ("research/machining-completeness/tasks/MC-019/outcome.json", "4456c964315c10b46ce61a5a8d4a45e8025730b7", "COMPLETED_RESEARCH"),
    "MC-020": ("research/machining-completeness/tasks/MC-020/outcome.json", "19504a35f47bca710bb6369abb723de83d1afede", "COMPLETED_RESEARCH"),
}
EXPECTED_UPSTREAM = {
    "repository": "elalish/manifold",
    "version": "v3.5.3",
    "tag_commit": "0edd9d54876f3135e431575214dd6d8a72866fee",
    "release_tarball_sha256": "9545a1c944280673553d0c97602def29f62afa4ade4b27ad1593bb13aa266218",
}
EXPECTED_SOURCE_PINS = {
    "include/manifold/common.h": "4e8ee4202ce10dbc5896259a0936ef0fb9317b43",
    "include/manifold/mesh.h": "984af936d370121878f40a325af52066fe0040cd",
    "include/manifold/manifold.h": "ff4e04b86ddff563d88ef4e85f6e141d4eed4479",
}
EXPECTED_BLOCKERS = {"PB-007-03", "RB-016-02", "RB-016-03", "RB-016-04"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def q(value) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise AssertionError("authority quantity must not be bool/binary float")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    raise AssertionError(f"unsupported authority quantity: {type(value).__name__}")


def reject_binary_float(value) -> None:
    if isinstance(value, float):
        raise AssertionError("binary floating point is forbidden in decisive MC-028 contract data")
    if isinstance(value, dict):
        for item in value.values():
            reject_binary_float(item)
    elif isinstance(value, list):
        for item in value:
            reject_binary_float(item)


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def import_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def overlap_length(a, b) -> Fraction:
    a0, a1 = q(a[0]), q(a[1])
    b0, b1 = q(b[0]), q(b[1])
    assert a0 <= a1 and b0 <= b1
    return max(Fraction(0), min(a1, b1) - max(a0, b0))


def exercise_actual_sweep_controls(contract: dict) -> None:
    controls = contract["exact_controls"]

    mc018 = import_module("mc028_dep_mc018", ROOT / "research" / "machining-completeness" / "tasks" / "MC-018" / "fixed_axis_sweep.py")
    flat = controls["flat_sweep"]
    flat_tool = mc018.FlatEndMill.make(flat["tool"]["radius"], flat["tool"]["length"])
    flat_leaf = mc018.Leaf.make(flat["leaf"]["p0"], flat["leaf"]["p1"], source_class=flat["leaf"]["source_class"])
    assert mc018.exact_sweep_contains(flat["boundary"], flat_tool, [flat_leaf])
    assert not mc018.exact_sweep_contains(flat["outside"], flat_tool, [flat_leaf])

    mc019 = import_module("mc028_dep_mc019", ROOT / "research" / "machining-completeness" / "tasks" / "MC-019" / "ball_round_sweep.py")
    ball = controls["ball_curvature"]
    ball_tool = mc019.BallRoundEndMill.make(ball["tool"]["radius"], ball["tool"]["length"])
    ball_leaf = mc019.Leaf.make(ball["leaf"]["p0"], ball["leaf"]["p1"], source_class=ball["leaf"]["source_class"])
    assert mc019.exact_sweep_contains(ball["exact_boundary"], ball_tool, [ball_leaf])
    assert mc019.exact_sweep_contains(ball["inside_neighbour"], ball_tool, [ball_leaf])
    assert not mc019.exact_sweep_contains(ball["outside_neighbour"], ball_tool, [ball_leaf])
    x = q(ball["witness_not_on_chord"][0]); z = q(ball["witness_not_on_chord"][1])
    assert x * x + (z - 1) * (z - 1) == 1
    assert z != x
    assert (x, z) == (Fraction(3, 5), Fraction(1, 5))

    mc020 = import_module("mc028_dep_mc020", ROOT / "research" / "machining-completeness" / "tasks" / "MC-020" / "form_undercut_sweep.py")
    form = controls["form_union"]
    boxes = [mc020.Box.make(*row) for row in form["boxes"]]
    form_tool = mc020.Tool.make(form["tool_kind"], boxes)
    form_leaf = mc020.Leaf.make(form["leaf"]["p0"], form["leaf"]["p1"], source_class=form["leaf"]["source_class"])
    assert mc020.exact_sweep_contains(form["inside"], form_tool, [form_leaf])
    assert not mc020.exact_sweep_contains(form["reentrant_gap"], form_tool, [form_leaf])

    micro = controls["positive_microfeature"]
    micro_box = mc020.Box.make(*micro["box"])
    micro_tool = mc020.Tool.make(micro["tool_kind"], [micro_box])
    micro_leaf = mc020.Leaf.make(micro["leaf"]["p0"], micro["leaf"]["p1"], source_class=micro["leaf"]["source_class"])
    assert micro_box.x1 - micro_box.x0 == q(micro["required_width"]) == Fraction(1, 1_000_000)
    assert mc020.exact_sweep_contains(micro["probe"], micro_tool, [micro_leaf])

    zero = controls["zero_contact"]
    assert overlap_length(zero["stock_interval"], zero["tangent_sweep_interval"]) == q(zero["tangent_positive_overlap"]) == 0
    assert overlap_length(zero["stock_interval"], zero["penetrating_sweep_interval"]) == q(zero["penetrating_positive_overlap"]) == Fraction(1, 1_000_000)
    assert overlap_length(zero["stock_interval"], zero["separated_sweep_interval"]) == q(zero["separated_positive_overlap"]) == 0


def validate_contract(contract: dict, *, check_files: bool = True, exercise_sweeps: bool = True) -> None:
    reject_binary_float(contract)
    assert contract["schema"] == "radicadsac-mc028-native-mesh-boolean-falsification/1.0"
    assert contract["task"] == "MC-028" and contract["issue"] == 90
    assert contract["source_baseline"] == EXPECTED_BASELINE
    assert contract["result"] == "NEGATIVE_RESULT_AS_TOTAL_MATERIAL_AUTHORITY"
    assert contract["native_execution"] is False and contract["native_or_paid_campaign_run"] is False

    deps = {d["task"]: d for d in contract["formal_dependencies"]}
    assert set(deps) == set(EXPECTED_DEPS)
    for task, (path, blob, result_kind) in EXPECTED_DEPS.items():
        assert deps[task] == {"task": task, "path": path, "blob_sha": blob, "result_kind": result_kind}
        if check_files:
            p = ROOT / path
            assert p.is_file() and git_blob_sha1(p) == blob, f"{task} dependency blob drift"
            assert load(p)["result_kind"] == result_kind

    upstream = contract["upstream_candidate"]
    for key, value in EXPECTED_UPSTREAM.items(): assert upstream[key] == value
    assert {p["path"]: p["blob_sha"] for p in upstream["source_pins"]} == EXPECTED_SOURCE_PINS
    assert all(p.get("fact") for p in upstream["source_pins"])
    assert len(upstream["source_urls"]) == 4 and all("v3.5.3" in u for u in upstream["source_urls"])

    inp = contract["candidate_input_contract"]
    assert inp["uses_independently_qualified_actual_sweeps"] is True
    assert inp["actual_sweep_sources"] == ["MC-018", "MC-019", "MC-020"]
    assert inp["historical_levelset_sampling_used"] is False
    assert inp["candidate_geometry_may_not_reconstruct_or_reinterpret_source_motion"] is True
    assert inp["uncertified_sweep_shell_may_not_be_promoted_to_exact_mesh_truth"] is True

    facts = contract["source_facts"]
    assert facts["representation"] == "FINITE_FLOATING_TRIANGLE_BOUNDARY_MESH"
    assert facts["internal_geometry_precision"] == "double"
    for k in ("single_precision_mesh_io_exists", "double_precision_mesh_io_exists", "mesh_tolerance_is_part_of_representation_contract", "edge_shorter_than_tolerance_may_collapse", "tolerance_may_enlarge_with_roundoff", "baseline_bbox_tolerance_applies_on_mesh_construction", "manifold_output_is_not_synonymous_with_exact_mc1_material_semantics"):
        assert facts[k] is True

    falsification = contract["falsification"]
    assert "sole authoritative" in falsification["hypothesis"]
    assert "external certified relation" in falsification["criterion"]
    assert len(falsification["decisive_observations"]) == 4
    assert falsification["finite_planar_mesh_exact_for_open_spherical_patch"] is False
    assert falsification["mesh_validity_implies_mc1_material_correctness"] is False
    assert falsification["mesh_boolean_success_implies_engineering_output_success"] is False

    role = contract["retained_role"]
    assert role["status"] == "ELIGIBLE_ONLY_AS_BOUNDED_DERIVED_OR_CHALLENGER_PROVIDER"
    assert role["total_material_authority"] is False
    assert role["primary_engineering_output_authority"] is False
    assert role["native_capability_qualified"] is False
    joined = " ".join(role["requirements"]).lower()
    for fragment in ("source-faithful sweep", "error envelope", "positive-volume", "durable body identity", "primary step", "fail closed"):
        assert fragment in joined

    blockers = {b["id"]: b for b in contract["blockers"]}
    assert set(blockers) == EXPECTED_BLOCKERS
    assert blockers["PB-007-03"]["status"] == "OPEN_PROPAGATED"
    assert all(blockers[b]["status"].startswith("OPEN") for b in EXPECTED_BLOCKERS)
    assert contract["capability_state"]["MC-A"] == "ACCEPTED"
    for gate in ("MC-B", "MC-C", "MC-D", "MC-E", "MC-F", "MC-1"):
        assert contract["capability_state"][gate] == "NOT_ESTABLISHED"

    protected = " ".join(contract["protected_semantics"]).lower()
    for fragment in ("source/audio/provenance", "canonical operation journal", "positive-volume", "durable body", "step remains mandatory"):
        assert fragment in protected
    if exercise_sweeps: exercise_actual_sweep_controls(contract)


def validate_repository_bindings() -> None:
    outcome = load(OUTCOME)
    assert outcome["schema"] == "radicadsac-mc-task-outcome/1.0" and outcome["task"] == "MC-028"
    assert outcome["result_kind"] == "NEGATIVE_RESULT" and outcome["source_baseline"] == EXPECTED_BASELINE and outcome["issue"] == 90
    assert outcome["native_execution"] is False and outcome["resources"]["native_or_paid_campaign_run"] is False
    assert {b["id"] for b in outcome["blockers"]} == EXPECTED_BLOCKERS
    assert outcome["review"]["gate_changed"] is False and outcome["review"]["programme_capability_changed"] is False

    registry = load(REGISTRY)["tasks"]["MC-028"]
    assert registry["state"] == "NEGATIVE_RESULT" and registry["issue"] == 90
    expected_artifacts = {
        "research/machining-completeness/tasks/MC-028/native-mesh-boolean-falsification-v1.json",
        "research/machining-completeness/tasks/MC-028/report.md",
        "research/machining-completeness/tasks/MC-028/outcome.json",
        "research/machining-completeness/tasks/MC-028/verify.py",
        "docs/machining-completeness/20-MC028-NATIVE-MESH-BOOLEAN.md",
    }
    assert set(registry["accepted_artifacts"]) == expected_artifacts
    assert {b["id"] for b in registry["blockers"]} == EXPECTED_BLOCKERS

    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "research/machining-completeness/tasks/MC-028/verify.py" in workflow
    assert "python3 tools/mc_workflow.py verify MC-028" in workflow

    report = REPORT.read_text(encoding="utf-8"); doc = DOC.read_text(encoding="utf-8")
    for text in (report, doc):
        low = text.lower()
        for fragment in ("negative_result", "mc-018", "mc-019", "mc-020", "levelset", "1/1000000", "rb-016-02", "rb-016-03", "rb-016-04", "pb-007-03", "not_established", "step", "source/audio/provenance"):
            assert fragment in low


def expect_rejected(mutator) -> None:
    obj = load(CONTRACT); mutator(obj)
    try: validate_contract(obj, check_files=False, exercise_sweeps=False)
    except Exception: return
    raise AssertionError("adversarial mutation was not rejected")


def self_test() -> None:
    validate_contract(load(CONTRACT))
    attacks = [
        lambda x: x.__setitem__("source_baseline", "0" * 40),
        lambda x: x["candidate_input_contract"].__setitem__("historical_levelset_sampling_used", True),
        lambda x: x["candidate_input_contract"].__setitem__("actual_sweep_sources", ["MC-019"]),
        lambda x: x["source_facts"].__setitem__("edge_shorter_than_tolerance_may_collapse", False),
        lambda x: x["source_facts"].__setitem__("representation", "EXACT_ANALYTIC_BREP"),
        lambda x: x["falsification"].__setitem__("finite_planar_mesh_exact_for_open_spherical_patch", True),
        lambda x: x["retained_role"].__setitem__("total_material_authority", True),
        lambda x: x["retained_role"].__setitem__("primary_engineering_output_authority", True),
        lambda x: x["retained_role"].__setitem__("native_capability_qualified", True),
        lambda x: x.__setitem__("blockers", [b for b in x["blockers"] if b["id"] != "RB-016-03"]),
        lambda x: x["formal_dependencies"][3].__setitem__("blob_sha", "0" * 40),
        lambda x: x["capability_state"].__setitem__("MC-B", "ACCEPTED"),
        lambda x: x.__setitem__("native_execution", True),
    ]
    for attack in attacks: expect_rejected(attack)

    obj = load(CONTRACT)
    bad = copy.deepcopy(obj); bad["exact_controls"]["ball_curvature"]["exact_boundary"] = ["3/5", "0", "199999/1000000"]
    try: exercise_actual_sweep_controls(bad)
    except AssertionError: pass
    else: raise AssertionError("outside ball-neighbour corruption was accepted as exact boundary")

    bad = copy.deepcopy(obj); bad["exact_controls"]["positive_microfeature"]["required_width"] = "0"
    try: exercise_actual_sweep_controls(bad)
    except AssertionError: pass
    else: raise AssertionError("positive microfeature was allowed to collapse to zero")
    validate_repository_bindings()


def main() -> int:
    ap = argparse.ArgumentParser(); mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--contract", action="store_true"); mode.add_argument("--self-test", action="store_true"); args = ap.parse_args()
    if args.contract:
        validate_contract(load(CONTRACT)); validate_repository_bindings(); print("MC-028 contract verification passed")
    else:
        self_test(); print("MC-028 adversarial self-test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
