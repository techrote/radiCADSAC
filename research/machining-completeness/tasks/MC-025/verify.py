#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-025"
CONTRACT = TASK / "adaptive-implicit-falsification-v1.json"
OUTCOME = TASK / "outcome.json"
DOC = ROOT / "docs" / "machining-completeness" / "02-COMPLETENESS-ARGUMENT.md"
REGISTRY = ROOT / "research" / "machining-completeness" / "outcomes-v1.json"

EXPECTED_BASELINE = "9668fa058a97219880897a483ac25c530ccfc67b"
EXPECTED_DEPS = {
    "MC-008": ("research/machining-completeness/tasks/MC-008/outcome.json", "a4b3f3451abedd06f2467a8e11741cdc63826e2b", "COMPLETED_RESEARCH"),
    "MC-010": ("research/machining-completeness/tasks/MC-010/outcome.json", "4960730316f89dbb3fbf958d054127fa4fc0d789", "COMPLETED_RESEARCH"),
    "MC-016": ("research/machining-completeness/tasks/MC-016/outcome.json", "606a7d0b8be61131b2272f2eb161d6a4dbba703a", "COMPLETED_RESEARCH"),
}
EXPECTED_BLOCKERS = {"PB-007-01", "PB-007-02", "RB-016-03", "RB-016-04"}
EXPECTED_CONTROLS = {
    "CTRL-025-EVENT-SPLIT",
    "CTRL-025-MICROWEB",
    "CTRL-025-TANGENT",
    "CTRL-025-EMPTY",
    "CTRL-025-RETRACE",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def reject_binary_float(value) -> None:
    if isinstance(value, float):
        raise AssertionError("binary floating values are forbidden in decisive MC-025 contract data")
    if isinstance(value, dict):
        for item in value.values():
            reject_binary_float(item)
    elif isinstance(value, list):
        for item in value:
            reject_binary_float(item)


def q(token: str) -> Fraction:
    if not isinstance(token, str):
        raise AssertionError("exact quantities must be JSON strings")
    return Fraction(token)


def interval(raw: list[str]) -> tuple[Fraction, Fraction]:
    assert isinstance(raw, list) and len(raw) == 2
    a, b = q(raw[0]), q(raw[1])
    assert a < b
    return a, b


def clipped_endpoint(x: Fraction, stock: tuple[Fraction, Fraction]) -> bool:
    return stock[0] <= x <= stock[1]


def validate_event_cover(control: dict) -> None:
    stock = interval(control["stock"])
    events = {q(x) for x in control["certified_events"]}
    permitted = events | {stock[0], stock[1]}
    for raw in control["removals"]:
        a, b = interval(raw)
        for x in (a, b):
            if clipped_endpoint(x, stock):
                assert x in permitted, f"{control['id']}: removal boundary {x} lacks exact event certificate"


def exact_material_intervals(control: dict) -> list[tuple[Fraction, Fraction]]:
    stock = interval(control["stock"])
    validate_event_cover(control)
    points = {stock[0], stock[1]}
    points |= {q(x) for x in control["certified_events"] if stock[0] <= q(x) <= stock[1]}
    points = sorted(points)
    removals = [interval(r) for r in control["removals"]]
    kept: list[tuple[Fraction, Fraction]] = []
    for a, b in zip(points, points[1:]):
        if a == b:
            continue
        mid = (a + b) / 2
        removed = any(r0 <= mid <= r1 for r0, r1 in removals)
        if not removed:
            kept.append((a, b))
    return kept


def merge_adjacent(items: list[tuple[Fraction, Fraction]]) -> list[tuple[Fraction, Fraction]]:
    if not items:
        return []
    out = [items[0]]
    for a, b in items[1:]:
        pa, pb = out[-1]
        if pb == a:
            out[-1] = (pa, b)
        else:
            out.append((a, b))
    return out


def run_control(control: dict) -> tuple[Fraction, int]:
    kept = merge_adjacent(exact_material_intervals(control))
    measure = sum((b - a for a, b in kept), Fraction(0))
    return measure, len(kept)


def dyadic_cell_containing(event: Fraction, depth: int) -> tuple[Fraction, Fraction]:
    assert 0 <= event <= 1
    den = 2 ** depth
    k = (event.numerator * den) // event.denominator
    left = Fraction(k, den)
    if left == event:
        return left, left
    return left, Fraction(k + 1, den)


def validate_refinement_obstruction(obj: dict) -> None:
    assert obj["refinement"] == "dyadic_bisection"
    event = q(obj["event"])
    assert event == Fraction(1, 3)
    assert interval(obj["stock"]) == (Fraction(0), Fraction(1))
    for depth in obj["checked_depths"]:
        assert isinstance(depth, int) and depth >= 0
        left, right = dyadic_cell_containing(event, depth)
        assert left < event < right, f"1/3 must remain interior at dyadic depth {depth}"
        assert right - left == Fraction(1, 2 ** depth)
    assert obj["exact_event_injection_required_for_zero_uncertainty"] is True
    assert obj["timeout_or_depth_cap_may_be_success"] is False


def validate_contract(contract: dict, *, check_files: bool = True) -> None:
    reject_binary_float(contract)
    assert contract["schema"] == "radicadsac-mc025-adaptive-implicit-falsification/1.0"
    assert contract["task"] == "MC-025"
    assert contract["issue"] == 87
    assert contract["source_baseline"] == EXPECTED_BASELINE
    assert contract["result"] == "NEGATIVE_RESULT_AS_GENERAL_FALLBACK"
    assert contract["native_execution"] is False

    deps = {d["task"]: d for d in contract["formal_dependencies"]}
    assert set(deps) == set(EXPECTED_DEPS)
    for task, (path, blob, result_kind) in EXPECTED_DEPS.items():
        assert deps[task] == {"task": task, "path": path, "blob_sha": blob, "result_kind": result_kind}
        if check_files:
            dep_path = ROOT / path
            assert dep_path.is_file()
            assert git_blob_sha1(dep_path) == blob, f"{task} dependency drift"
            assert load(dep_path)["result_kind"] == result_kind

    candidate = contract["candidate"]
    assert candidate["id"] == "CERTIFIED-ADAPTIVE-IMPLICIT"
    assert candidate["role"] == "BOUNDED_CERTIFIED_MATERIAL_REPRESENTATION_AFTER_EVENT_CERTIFICATE"
    assert candidate["general_fallback_qualified"] is False
    admission = candidate["admission_predicate"]
    assert {
        "source_semantics_preserved",
        "sound_outward_cell_enclosures",
        "exact_or_validated_critical_event_certificate",
        "input_derived_finite_progress_witness",
        "shared_time_feed_phase_correlation_preserved",
        "regularized_removal_semantics_preserved",
    } <= set(admission["requirements"])
    assert admission["binary_float_predicates_allowed"] is False
    assert admission["global_epsilon_predicates_allowed"] is False
    assert admission["fixed_pitch_is_correctness_authority"] is False
    assert admission["max_depth_is_semantic_success"] is False
    assert admission["unknown_cell_may_be_forced_material_or_removed"] is False
    assert "typed blocker" in admission["on_failure"].lower()
    assert "cycle" in admission["on_failure"].lower()

    sound = contract["soundness_contract"]
    assert sound["material_sandwich_required"] == "L_subseteq_M_subseteq_U"
    assert sound["lower_bound_only_from_proved_material"] is True
    assert sound["upper_bound_may_include_unresolved_cells"] is True
    assert sound["unresolved_cells_are_success"] is False
    assert sound["numeric_error_may_compensate_topology"] is False
    assert sound["numeric_error_may_delete_positive_volume"] is False
    assert sound["topology_requires_discrete_certificate"] is True
    assert sound["durable_body_identity_is_cell_identity"] is False
    assert sound["lineage_is_component_label"] is False

    event = contract["critical_event_contract"]
    assert event["event_source_must_be_independent_of_refinement_tolerance"] is True
    assert event["exact_equality_may_stop_on_cell_width_threshold"] is False
    assert event["separated_transversal_case_requires_input_derived_bound"] is True
    assert event["tangent_multiple_singular_case_requires_exact_or_separately_proved_event_decision"] is True
    assert event["shared_time_feed_phase_parameter_must_be_preserved"] is True
    assert event["missing_event_certificate_terminal"] == "PROOF_BLOCKER"

    matrix = {x["id"]: x for x in contract["coverage_matrix"]}
    assert set(matrix) == {f"AI-025-{i:02d}" for i in range(1, 7)}
    assert matrix["AI-025-01"]["status"] == "MODEL_REFERENCE_ELIGIBLE"
    assert matrix["AI-025-02"]["status"] == "CONDITIONAL_REFERENCE_ELIGIBLE"
    assert "input-derived" in matrix["AI-025-02"]["guard"].lower()
    assert matrix["AI-025-03"]["status"] == "BLOCKED" and "PB-007-01" in matrix["AI-025-03"]["basis"]
    assert "shrinking uncertainty" in matrix["AI-025-03"]["guard"].lower()
    assert matrix["AI-025-04"]["status"] == "BLOCKED" and "PB-007-02" in matrix["AI-025-04"]["basis"]
    assert "shared time/feed/spindle-phase" in matrix["AI-025-04"]["guard"].lower()
    assert matrix["AI-025-05"]["status"] == "MATERIAL_MODEL_ONLY_OUTPUT_BLOCKED"
    assert "RB-016-03" in matrix["AI-025-05"]["basis"]
    assert matrix["AI-025-06"]["status"] == "MATERIAL_MODEL_ONLY_OUTPUT_PROFILE_BLOCKED"
    assert "RB-016-04" in matrix["AI-025-06"]["basis"]
    assert "no healing" in matrix["AI-025-06"]["guard"].lower()

    controls = {c["id"]: c for c in contract["machining_controls"]}
    assert set(controls) == EXPECTED_CONTROLS
    for cid, control in controls.items():
        measure, components = run_control(control)
        assert measure == q(control["expected_material_measure"]), f"{cid} material measure mismatch"
        assert components == control["expected_components"], f"{cid} component mismatch"
    retrace = controls["CTRL-025-RETRACE"]
    assert retrace["expected_same_as_single_removal"] is True
    single = copy.deepcopy(retrace)
    single["removals"] = single["removals"][:1]
    assert run_control(retrace) == run_control(single), "exact retrace must be idempotent"
    assert run_control(controls["CTRL-025-MICROWEB"])[0] == Fraction(1, 1_000_000)

    validate_refinement_obstruction(contract["equality_refinement_obstruction"])

    resource = contract["resource_obstruction"]
    assert resource["practical_status"] == "NOT_QUALIFIED_AS_DEFAULT_OR_GENERAL_PRODUCTION_ROUTE"
    assert resource["fixed_depth_may_be_correctness_proof"] is False
    assert resource["timeout_may_be_reported_as_success"] is False

    dispatch = contract["total_dispatch_conclusion"]
    assert dispatch["candidate_can_be_general_fallback"] is False
    assert dispatch["candidate_can_be_bounded_reference"] is True
    assert dispatch["candidate_can_be_optional_provider_after_admission"] is True
    assert dispatch["candidate_avoids_fixed_pitch_floor_when_certified_events_are_available"] is True
    assert dispatch["candidate_solves_generic_exact_equality_by_refinement"] is False
    assert dispatch["unresolved_required_case_is_success"] is False
    assert "may not cycle" in dispatch["noncycling_requirement"].lower()

    blockers = {b["id"]: b for b in contract["retained_blockers"]}
    assert set(blockers) == EXPECTED_BLOCKERS
    assert all(b["status"] == "OPEN" for b in blockers.values())
    assert blockers["PB-007-01"]["source_task"] == "MC-008"
    assert blockers["PB-007-02"]["source_task"] == "MC-008"
    assert blockers["RB-016-03"]["source_task"] == "MC-016"
    assert blockers["RB-016-04"]["source_task"] == "MC-016"
    assert all(b["affected_descendants"] for b in blockers.values())

    assert contract["capability_guard"] == {
        "MC-A": "ACCEPTED",
        "MC-B": "NOT_ESTABLISHED",
        "MC-C": "NOT_ESTABLISHED",
        "MC-D": "NOT_ESTABLISHED",
        "MC-E": "NOT_ESTABLISHED",
        "MC-F": "NOT_ESTABLISHED",
        "MC-1": "NOT_ESTABLISHED",
    }

    if check_files:
        outcome = load(OUTCOME)
        assert outcome["task"] == "MC-025"
        assert outcome["result_kind"] == "NEGATIVE_RESULT"
        assert outcome["source_baseline"] == EXPECTED_BASELINE
        assert {x["id"] for x in outcome["blockers"]} == EXPECTED_BLOCKERS

        registry = load(REGISTRY)["tasks"]["MC-025"]
        assert registry["state"] == "NEGATIVE_RESULT"
        assert registry["issue"] == 87
        assert "research/machining-completeness/tasks/MC-025/adaptive-implicit-falsification-v1.json" in registry["accepted_artifacts"]
        assert {x["id"] for x in registry["blockers"]} == EXPECTED_BLOCKERS

        doc = DOC.read_text(encoding="utf-8")
        assert "### MC-025 adaptive interval/implicit candidate falsification" in doc
        assert "NEGATIVE_RESULT" in doc
        assert "1/3" in doc
        assert "RB-016-03" in doc
        assert "MC-B remains `NOT_ESTABLISHED`" in doc


def adversarial_self_test(contract: dict) -> None:
    mutations = []

    bad = copy.deepcopy(contract)
    bad["candidate"]["general_fallback_qualified"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["candidate"]["admission_predicate"]["global_epsilon_predicates_allowed"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["candidate"]["admission_predicate"]["fixed_pitch_is_correctness_authority"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["candidate"]["admission_predicate"]["max_depth_is_semantic_success"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["soundness_contract"]["unresolved_cells_are_success"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["soundness_contract"]["numeric_error_may_compensate_topology"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["critical_event_contract"]["exact_equality_may_stop_on_cell_width_threshold"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["coverage_matrix"][2]["status"] = "CONDITIONAL_REFERENCE_ELIGIBLE"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["coverage_matrix"][3]["guard"] = "independent phase coverage is acceptable"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["machining_controls"][1]["expected_material_measure"] = "0"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["equality_refinement_obstruction"]["timeout_or_depth_cap_may_be_success"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["retained_blockers"] = [x for x in bad["retained_blockers"] if x["id"] != "PB-007-01"]
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["formal_dependencies"][0]["blob_sha"] = "0" * 40
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["capability_guard"]["MC-B"] = "ACCEPTED"
    mutations.append(bad)

    rejected = 0
    for mutated in mutations:
        try:
            validate_contract(mutated, check_files=False)
        except (AssertionError, KeyError, ValueError, ZeroDivisionError):
            rejected += 1
    assert rejected == len(mutations), f"only rejected {rejected}/{len(mutations)} adversarial mutations"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    contract = load(CONTRACT)
    if args.contract or not args.self_test:
        validate_contract(contract, check_files=True)
        print("MC-025 contract verification passed")
    if args.self_test:
        validate_contract(contract, check_files=True)
        adversarial_self_test(contract)
        print("MC-025 adversarial self-test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
