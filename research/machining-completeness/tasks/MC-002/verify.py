#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-002"
CONTRACT = TASK / "domain-contract-v1.json"

REQUIRED_PHYSICAL = {
    "stock_is_bounded_volumetric_material": True,
    "tool_cutting_and_noncutting_regions_are_distinguished": True,
    "finite_cutter_extent_is_required": True,
    "engaged_motion_is_continuous": True,
    "engaged_teleportation_is_invalid": True,
    "stationary_engaged_motion_is_valid": True,
    "machine_travel_and_kinematic_feasibility_are_witnessed": True,
    "access_and_holder_fixture_clearance_are_witnessed_where_relevant": True,
    "machining_requires_target_body_held_by_current_setup": True,
    "detached_body_requires_workholding_or_explicit_reclamp_before_further_machining": True,
    "parted_body_is_not_magically_fixed": True,
    "candidate_success_is_not_a_physical_validity_oracle": True,
    "point_or_edge_contact_creates_volumetric_connection": False,
    "face_contact_requires_local_interior_analysis": True,
    "durable_bodies_do_not_merge_only_because_boundaries_touch": True,
    "positive_volume_slivers_are_material": True,
    "empty_material_state_is_valid": True,
    "units_frames_tool_revision_setup_revision_and_target_body_are_explicit": True,
}

REQUIRED_OPERATION_CONTROLS = {
    "lathe_parting_cutthrough": ({"body_split", "regularized_removal"}, {"separation", "post_separation_handling"}),
    "lathe_threading_synchronized": ({"phase_synchronization", "timed_phase_motion"}, {"phase_law"}),
    "lathe_eccentric_turning": ({"eccentric_setup", "timed_phase_motion"}, {"eccentric_transform"}),
    "mill_accessible_undercut": ({"mill_accessible_undercut", "regularized_removal"}, {"holder_clearance"}),
    "mill_thread_helix_fixed_axis": ({"helical_arc", "regularized_removal"}, {"workholding", "travel"}),
    "mill_simultaneous_xyz": ({"piecewise_motion", "regularized_removal"}, {"workholding", "travel"}),
    "mill_retrace_self_cross_stationary": ({"stationary", "piecewise_motion"}, {"workholding"}),
    "mill_cutthrough_multibody": ({"body_split", "regularized_removal"}, {"separation", "post_separation_handling"}),
    "reclamp_reorient_continue": ({"reclamp", "rigid_setup_transform", "body_target"}, {"new_workholding", "rigid_transform"}),
    "lathe_mill_lathe_history": ({"machine_transition", "reclamp", "body_target"}, {"workholding_each_setup", "common_frame"}),
    "machine_separated_retained_body": ({"body_split", "reclamp", "body_target"}, {"retention_or_reclamp"}),
    "complete_body_removal": ({"body_disappearance", "regularized_removal"}, {"target_body"}),
}

REQUIRED_BOUNDARIES = {
    "coincidence_or_coplanarity",
    "tangent_or_point_edge_face_contact",
    "sub_tolerance_positive_cut",
    "positive_volume_sliver",
    "self_crossing_retrace_reversal_stationary",
    "large_finite_segment_count",
    "whole_body_removal",
    "no_new_removal",
}

REQUIRED_DECISIONS = {
    "DD-002-01": ("continuous_five_axis_tool_reorientation", "excluded_by_current_mc1_scope"),
    "DD-002-02": ("additive_material_processes", "excluded_by_current_mc1_scope"),
    "DD-002-03": ("deformation_force_chip_dynamics", "excluded_by_current_mc1_scope"),
    "DD-002-04": ("lathe_live_or_driven_tooling_as_one_compound_operation", "open_product_domain_decision"),
    "DD-002-05": ("multiple_simultaneously_controlled_spindles_or_transfer_machine_semantics", "open_product_domain_decision"),
}


def fail(message: str) -> None:
    raise AssertionError(message)


def validate(obj: dict) -> None:
    if obj.get("schema") != "radicadsac-mc-domain-contract/1.1" or obj.get("task") != "MC-002":
        fail("schema/task mismatch")
    if obj.get("status") != "reviewed-domain-artifact":
        fail("domain artifact not reviewable")
    if obj.get("native_geometry_claimed") is not False:
        fail("MC-002 must not claim native geometry evidence")
    if obj.get("evidence_class") != ["REQUIREMENT", "DESIGN_DECISION", "DOCUMENTATION_RECONCILIATION"]:
        fail("MC-002 evidence classes drifted")

    rule = obj.get("domain_rule", {})
    required_rules = {
        "candidate_independent": True,
        "finite_source_description_required": True,
        "solver_success_is_not_validity_or_admissibility": True,
        "missing_constructor_is_gap_not_automatic_exclusion": True,
    }
    for key, expected in required_rules.items():
        if rule.get(key) is not expected:
            fail(f"domain rule violated: {key}")
    if set(rule.get("initial_machine_families", [])) != {"lathe", "mill"}:
        fail("initial machine family drift")
    axis_policy = rule.get("milling_axis_policy", "")
    if "fixed" not in axis_policy or "reorientation" not in axis_policy or "non-cutting" not in axis_policy:
        fail("fixed-axis/reorientation semantics missing")

    constructors = {}
    for category, entries in obj.get("constructors", {}).items():
        if not isinstance(entries, list) or not entries:
            fail(f"empty constructor category: {category}")
        for entry in entries:
            cid = entry.get("id")
            if not cid or cid in constructors:
                fail(f"duplicate/missing constructor: {cid}")
            if not entry.get("semantics"):
                fail(f"constructor lacks semantics: {cid}")
            constructors[cid] = category
    for cid in ("regularized_removal", "body_split", "body_disappearance", "body_target",
                "spindle_rotation", "phase_synchronization", "timed_phase_motion",
                "reclamp", "machine_transition", "drill_cutting_solid", "helical_arc"):
        if cid not in constructors:
            fail(f"required constructor missing: {cid}")

    witnesses = {}
    for entry in obj.get("witness_catalog", []):
        wid = entry.get("id")
        if not wid or wid in witnesses or not entry.get("semantics"):
            fail(f"bad witness catalog entry: {wid}")
        witnesses[wid] = entry["semantics"]

    physical = obj.get("physical_validity", {})
    for key, expected in REQUIRED_PHYSICAL.items():
        if physical.get(key) is not expected:
            fail(f"physical-validity rule violated: {key}")

    operations = {}
    for entry in obj.get("operation_map", []):
        oid = entry.get("id")
        if not oid or oid in operations:
            fail(f"duplicate/missing operation: {oid}")
        if entry.get("status") != "admitted":
            fail(f"required operation not admitted: {oid}")
        if entry.get("machine") not in {"lathe", "mill", "cross_machine"}:
            fail(f"bad machine family: {oid}")
        cids = entry.get("constructors")
        wids = entry.get("witnesses")
        if not cids or not wids:
            fail(f"operation lacks constructors/witnesses: {oid}")
        unknown_c = set(cids) - set(constructors)
        unknown_w = set(wids) - set(witnesses)
        if unknown_c:
            fail(f"{oid} references unknown constructor(s): {sorted(unknown_c)}")
        if unknown_w:
            fail(f"{oid} references unknown witness(es): {sorted(unknown_w)}")
        operations[oid] = entry

    coverage = obj.get("coverage_rule", {})
    required_ids = coverage.get("required_operation_ids", [])
    if len(required_ids) != len(set(required_ids)):
        fail("coverage list contains duplicate operation IDs")
    if set(required_ids) != set(operations):
        fail("required operation coverage and operation map differ")
    if coverage.get("no_provider_narrowing") is not True or coverage.get("open_decisions_are_not_solver_refusals") is not True:
        fail("provider-independent coverage rules weakened")

    for oid, (needed_c, needed_w) in REQUIRED_OPERATION_CONTROLS.items():
        entry = operations.get(oid)
        if entry is None:
            fail(f"required boundary operation missing: {oid}")
        if not needed_c.issubset(set(entry["constructors"])):
            fail(f"{oid} lost semantic constructor controls")
        if not needed_w.issubset(set(entry["witnesses"])):
            fail(f"{oid} lost physical witness controls")

    boundary_ids = {x.get("case") for x in obj.get("boundary_and_pathology_policy", [])}
    if not REQUIRED_BOUNDARIES.issubset(boundary_ids):
        fail("boundary/pathology coverage incomplete")

    decisions = {x.get("id"): x for x in obj.get("named_domain_decisions", [])}
    if set(decisions) != set(REQUIRED_DECISIONS):
        fail("named domain-decision set drifted")
    for did, (topic, status) in REQUIRED_DECISIONS.items():
        d = decisions[did]
        if d.get("topic") != topic or d.get("status") != status or not d.get("basis"):
            fail(f"named domain decision invalid: {did}")
    if "provider" not in decisions["DD-002-04"]["basis"] or "cannot" not in decisions["DD-002-04"]["basis"]:
        fail("live-tool open decision no longer rejects provider-driven narrowing")

    deps = obj.get("dependency_inputs", [])
    if len(deps) != 1 or deps[0].get("task") != "MC-001":
        fail("MC-001 artifact dependency not bound")
    if deps[0].get("blob_sha") != "2efd52cf39102d5722c6bbf281828361e943d6a4":
        fail("MC-001 dependency blob drift")


def must_reject(base: dict, mutate, label: str) -> None:
    bad = copy.deepcopy(base)
    mutate(bad)
    try:
        validate(bad)
    except AssertionError:
        return
    fail(f"adversarial control was not rejected: {label}")


def adversarial_self_test(base: dict) -> None:
    must_reject(base, lambda x: x["domain_rule"].__setitem__("candidate_independent", False), "solver-defined domain")
    must_reject(base, lambda x: x["physical_validity"].__setitem__("engaged_teleportation_is_invalid", False), "engaged teleport")
    must_reject(base, lambda x: x["physical_validity"].__setitem__("detached_body_requires_workholding_or_explicit_reclamp_before_further_machining", False), "magically fixed detached body")
    must_reject(base, lambda x: x["physical_validity"].__setitem__("point_or_edge_contact_creates_volumetric_connection", True), "zero-volume bridge")
    must_reject(base, lambda x: x["physical_validity"].__setitem__("positive_volume_slivers_are_material", False), "sliver deletion")
    must_reject(base, lambda x: x["coverage_rule"]["required_operation_ids"].pop(), "dropped ordinary operation")
    must_reject(base, lambda x: x["operation_map"][0]["constructors"].append("provider_private_magic"), "unknown provider-private constructor")
    must_reject(base, lambda x: x["operation_map"][7]["witnesses"].remove("post_separation_handling"), "parting without post-separation handling")
    must_reject(base, lambda x: x["operation_map"][18]["constructors"].remove("helical_arc"), "thread helix without helical motion")
    must_reject(base, lambda x: x["named_domain_decisions"].pop(), "silently dropped open domain decision")
    must_reject(base, lambda x: x.__setitem__("native_geometry_claimed", True), "synthetic contract promoted to native geometry")


def verify_repository_bindings() -> None:
    dep = json.loads((ROOT / "research/machining-completeness/tasks/MC-001/outcome.json").read_text(encoding="utf-8"))
    if dep.get("task") != "MC-001" or dep.get("result_kind") not in {"COMPLETED_RESEARCH", "CAPABILITY_ACCEPTED"}:
        fail("MC-001 artifact dependency is not reviewable")
    outcome = json.loads((TASK / "outcome.json").read_text(encoding="utf-8"))
    if outcome.get("task") != "MC-002" or outcome.get("result_kind") != "COMPLETED_RESEARCH":
        fail("MC-002 outcome state mismatch")
    shared = (ROOT / "docs/machining-completeness/01-DOMAIN-AND-SEMANTICS.md").read_text(encoding="utf-8")
    for marker in (
        "MC-002 reviewed constructor/physical-validity artifact",
        "research/machining-completeness/tasks/MC-002/domain-contract-v1.json",
        "DD-002-04",
        "DD-002-05",
        "MC-A remains `NOT_ESTABLISHED`",
    ):
        if marker not in shared:
            fail(f"shared domain contract lacks MC-002 reconciliation marker: {marker}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.parse_args()
    obj = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate(obj)
    adversarial_self_test(obj)
    verify_repository_bindings()
    print("MC-002 domain contract and adversarial boundary controls passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
