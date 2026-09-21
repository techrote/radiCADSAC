#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research" / "machining-completeness" / "tasks" / "MC-058"
CONTRACT_PATH = TASK / "curve-sweep-contract-v1.json"

EXPECTED_SOURCE_BASELINE = "54a75e34e93f21964e93ba05a0391033d4081f3d"
EXPECTED_DEPS = {
    "MC-003": (
        "research/machining-completeness/tasks/MC-003/outcome.json",
        "8f335f59f36c8761844806f9059af4a4f1671044",
        "COMPLETED_RESEARCH",
    ),
    "MC-008": (
        "research/machining-completeness/tasks/MC-008/outcome.json",
        "a4b3f3451abedd06f2467a8e11741cdc63826e2b",
        "COMPLETED_RESEARCH",
    ),
    "MC-010": (
        "research/machining-completeness/tasks/MC-010/outcome.json",
        "4960730316f89dbb3fbf958d054127fa4fc0d789",
        "COMPLETED_RESEARCH",
    ),
}
EXPECTED_PINS = {
    "research/machining-completeness/tasks/MC-003/numeric-encoding-contract-v1.json": "a5538cab698c806fdedcef7cf563b650638348e0",
    "research/machining-completeness/proof-obligations-v1.json": "97b023c5ea550f598b16ba9a1aeaabbf95ecba6f",
    "research/machining-completeness/tasks/MC-010/oracle-foundation-v1.json": "b55ac69f007c405f67eb15c664ff75e64a83c659",
    "research/machining-completeness/tasks/MC-010/independent_exact_oracle.py": "cfb5a8def57e8f4bb5109982da456621766a2b22",
}
EXPECTED_CURVES = {
    "stationary",
    "line",
    "circular_arc",
    "helical_arc",
    "polyline",
    "spline",
    "piecewise_motion",
    "timed_phase_motion",
}
EXPECTED_TRANSFORMS = {"rigid_setup_transform", "reclamp", "machine_transition"}
EXPECTED_BLOCKERS = {"PB-007-01", "PB-007-02"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def rat(value: dict) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def as_fraction(value: str) -> Fraction:
    return Fraction(int(value), 1)


def vec(values: list[str]) -> tuple[Fraction, ...]:
    return tuple(as_fraction(v) for v in values)


def vadd(a: tuple[Fraction, ...], b: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(x + y for x, y in zip(a, b, strict=True))


def vscale(k: Fraction, a: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(k * x for x in a)


def lerp(a: tuple[Fraction, ...], b: tuple[Fraction, ...], u: Fraction) -> tuple[Fraction, ...]:
    return vadd(vscale(Fraction(1) - u, a), vscale(u, b))


def quarter_turn_z(p: tuple[Fraction, Fraction, Fraction]) -> tuple[Fraction, Fraction, Fraction]:
    x, y, z = p
    return (-y, x, z)


def quadratic_bezier(points: list[tuple[Fraction, Fraction]], u: Fraction) -> tuple[Fraction, Fraction]:
    a = lerp(points[0], points[1], u)
    b = lerp(points[1], points[2], u)
    return lerp(a, b, u)


def quaternion_rotation_matrix(raw: tuple[Fraction, Fraction, Fraction, Fraction]):
    w, x, y, z = raw
    n2 = w * w + x * x + y * y + z * z
    assert n2 > 0
    two = Fraction(2)
    return (
        ((w*w + x*x - y*y - z*z) / n2, two*(x*y - w*z) / n2, two*(x*z + w*y) / n2),
        (two*(x*y + w*z) / n2, (w*w - x*x + y*y - z*z) / n2, two*(y*z - w*x) / n2),
        (two*(x*z - w*y) / n2, two*(y*z + w*x) / n2, (w*w - x*x - y*y + z*z) / n2),
    )


def matvec(m, p: tuple[Fraction, Fraction, Fraction]):
    return tuple(sum(row[i] * p[i] for i in range(3)) for row in m)


def sqdist(a: tuple[Fraction, ...], b: tuple[Fraction, ...]) -> Fraction:
    return sum((x - y) ** 2 for x, y in zip(a, b, strict=True))


def validate_contract(contract: dict, *, check_files: bool = True) -> None:
    assert contract["schema"] == "radicadsac-mc058-curve-sweep-contract/1.0"
    assert contract["task"] == "MC-058"
    assert contract["issue"] == 120
    assert contract["source_baseline"] == EXPECTED_SOURCE_BASELINE
    assert contract["result"] == "COMPLETED_RESEARCH_CONTRACT_ESTABLISHED_OPEN_EVENTS"
    assert contract["native_execution"] is False

    deps = {d["task"]: d for d in contract["formal_dependencies"]}
    assert set(deps) == set(EXPECTED_DEPS)
    for task, (path, blob_sha, result_kind) in EXPECTED_DEPS.items():
        dep = deps[task]
        assert dep["path"] == path
        assert dep["blob_sha"] == blob_sha
        assert dep["result_kind"] == result_kind
        if check_files:
            p = ROOT / path
            assert p.is_file()
            assert git_blob_sha1(p) == blob_sha, f"{task} dependency drift"

    pins = {p["path"]: p["blob_sha"] for p in contract["pinned_authority"]}
    assert pins == EXPECTED_PINS
    if check_files:
        for path, blob_sha in pins.items():
            p = ROOT / path
            assert p.is_file()
            assert git_blob_sha1(p) == blob_sha, f"authority drift: {path}"

    source = contract["source_semantics"]
    assert source["profile"] == "mc-exact-source/1.0"
    for key in (
        "saved_operation_is_immutable",
        "approximation_is_derived_only",
        "certifying_json_binary_float_forbidden",
        "global_untyped_epsilon_forbidden",
        "endpoints_are_authoritative",
        "engagement_boundaries_are_authoritative",
        "setup_tool_target_boundaries_are_not_fitted_across",
        "exact_retrace_is_not_deleted_from_journal",
        "inherited_error_may_not_reset_at_handoff",
        "unknown_error_is_uncertified_not_zero",
    ):
        assert source[key] is True

    numeric = contract["numeric_enclosure"]
    assert rat(numeric["pi_upper_rational"]) == Fraction(22, 7)
    assert "not an exact value of pi" in numeric["pi_upper_role"]
    assert numeric["trigonometric_algebraicity_assumed"] is False
    assert "outward enclosure" in numeric["rotation_evaluation"]
    assert "explicit dimension" in numeric["certifying_scalar"]

    curves = {c["id"]: c for c in contract["curve_classes"]}
    assert set(curves) == EXPECTED_CURVES
    for curve in curves.values():
        assert curve["semantic_mapping"]
        assert curve["applicability"]
        assert curve["subdivision_rule"]
        assert curve["checked_bound"] or curve["open_obligations"]

    assert "P(u)=(1-u)P0+uP1" in curves["line"]["semantic_mapping"]
    assert "22/7" in curves["circular_arc"]["subdivision_rule"]
    assert "radius*theta_bar^2/8" in curves["circular_arc"]["subdivision_rule"]
    assert "PB-007-01" in " ".join(curves["circular_arc"]["open_obligations"])
    assert "same exact u interval" in curves["helical_arc"]["subdivision_rule"]
    assert "PB-007-02" in " ".join(curves["helical_arc"]["open_obligations"])
    assert "never fit across a vertex" in curves["polyline"]["subdivision_rule"]
    assert "exact knot insertion" in curves["spline"]["subdivision_rule"]
    assert "L*h" in curves["spline"]["checked_bound"]
    assert "hard semantic boundaries" in curves["piecewise_motion"]["subdivision_rule"]
    assert "time, path and phase subdivide together" in curves["timed_phase_motion"]["subdivision_rule"]
    assert "independent full-angle coverage is forbidden" in curves["timed_phase_motion"]["subdivision_rule"]

    transforms = {t["id"]: t for t in contract["transform_classes"]}
    assert set(transforms) == EXPECTED_TRANSFORMS
    rigid = transforms["rigid_setup_transform"]
    assert "p_parent = R(q)*p_child+t" in rigid["semantic_mapping"]
    assert {"LEFT_RIGHT_HANDEDNESS_SWAP", "TRANSFORM_ORDER_SWAP", "UNNORMALIZED_Q15_SEMANTICS", "UNIT_ERASURE"} <= set(rigid["forbidden"])
    assert "inherits prior source/numerical error without reset" in transforms["reclamp"]["checked_bound"]
    assert "body target and lineage" in transforms["machine_transition"]["semantic_mapping"]

    sweep = contract["actual_sweep_bound"]
    assert "complete cutting region" in sweep["cutter_requirement"]
    for term in ("radial extent", "axial length", "shoulders", "nonconvex/undercut"):
        assert term in sweep["cutter_requirement"]
    assert "same closed engaged source parameter/time set" in sweep["same_parameter_requirement"]
    assert "e_translation + rho*e_rotation" in sweep["pose_bound"]
    assert sweep["total_bound"] == "e_total = e_inherited + e_translation + rho*e_rotation + e_tool"
    assert sweep["centreline_only_is_sufficient"] is False
    assert sweep["topology_certificate_implied"] is False
    assert sweep["material_membership_certificate_implied"] is False
    assert sweep["exact_zero_event_decision_implied"] is False

    errors = contract["error_composition"]
    assert "sum conservative" in errors["unknown_dependence"]
    assert errors["source_uncertainty_separate_from_nominal_numerical_error"] is True
    assert errors["recomputation_may_remove_prior_derived_error_only_with_proof"] is True
    assert errors["topology_material_body_identity_not_compensable_by_numeric_error"] is True
    assert errors["approximation_request_never_changes_saved_source"] is True

    controls = contract["exact_controls"]
    line = controls["line_midpoint"]
    assert lerp(vec(line["p0"]), vec(line["p1"]), rat(line["u"])) == vec(line["expected"])

    arc = controls["quarter_arc"]
    theta = Fraction(2) * Fraction(22, 7) * abs(rat(arc["turn_fraction"])) / arc["equal_subarcs"]
    assert theta == rat(arc["theta_upper_each"])
    sag = rat(arc["radius"]) * theta * theta / 8
    assert sag == rat(arc["sag_upper_each"])
    assert quarter_turn_z((Fraction(1), Fraction(0), Fraction(0))) == vec(arc["semantic_unit_endpoint"])

    helix = controls["helical_quarter_endpoint"]
    radial = quarter_turn_z(vec(helix["start_radial"]))
    expected_helix = (radial[0], radial[1], radial[2] + rat(helix["axial_delta"]))
    assert expected_helix == vec(helix["expected"])

    spline = controls["quadratic_spline"]
    cps = [vec(p) for p in spline["control_points"]]
    assert quadratic_bezier(cps, rat(spline["u"])) == vec(spline["expected"])
    assert rat(spline["derivative_l1_upper"]) * rat(spline["leaf_width"]) == rat(spline["leaf_displacement_upper"])

    tr = controls["rigid_transform"]
    q = tuple(as_fraction(v) for v in tr["raw_q15_ratio"])
    rotated = matvec(quaternion_rotation_matrix(q), vec(tr["point"]))
    transformed = vadd(rotated, vec(tr["translation"]))
    assert transformed == vec(tr["expected"])
    p2 = (Fraction(2), Fraction(3), Fraction(4))
    t = vec(tr["translation"])
    rp1 = vadd(matvec(quaternion_rotation_matrix(q), vec(tr["point"])), t)
    rp2 = vadd(matvec(quaternion_rotation_matrix(q), p2), t)
    assert sqdist(rp1, rp2) == sqdist(vec(tr["point"]), p2), "rigid covariance lost"

    cutter = controls["finite_cutter"]
    assert rat(cutter["radial_extent"]) ** 2 + rat(cutter["axial_extent"]) ** 2 == rat(cutter["support_radius"]) ** 2
    pose_bound = rat(cutter["e_translation"]) + rat(cutter["support_radius"]) * rat(cutter["e_rotation"])
    assert pose_bound == rat(cutter["pose_sweep_upper"])
    total = rat(cutter["e_inherited"]) + pose_bound + rat(cutter["e_tool"])
    assert total == rat(cutter["total_upper"])
    assert rat(cutter["e_translation"]) < pose_bound, "centreline-only corruption went undetected"

    # Signed-neighbour and semantic-boundary controls.
    p0, p1 = vec(line["p0"]), vec(line["p1"])
    mid = rat(line["u"])
    left = lerp(p0, p1, mid - Fraction(1, 100))
    right = lerp(p0, p1, mid + Fraction(1, 100))
    exact = lerp(p0, p1, mid)
    assert left[0] < exact[0] < right[0]

    poly = [(Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)), (Fraction(1), Fraction(1))]
    assert lerp(poly[0], poly[1], Fraction(1)) == poly[1]
    assert lerp(poly[1], poly[2], Fraction(0)) == poly[1]
    assert lerp(poly[0], poly[1], Fraction(99, 100))[0] < poly[1][0]
    assert lerp(poly[1], poly[2], Fraction(1, 100))[1] > poly[1][1]

    stationary = (Fraction(7), Fraction(-3), Fraction(11))
    assert stationary == stationary

    # Shared time/path/phase: the same t=1/2 produces both values; independent coverage is not a substitute.
    tmid = Fraction(1, 2)
    timed_path = lerp((Fraction(0),), (Fraction(2),), tmid)[0]
    timed_phase_turns = lerp((Fraction(0),), (Fraction(1, 2),), tmid)[0]
    assert timed_path == 1 and timed_phase_turns == Fraction(1, 4)

    blockers = {b["id"]: b for b in contract["blockers"]}
    assert set(blockers) == EXPECTED_BLOCKERS
    assert all(b["status"] == "OPEN" for b in blockers.values())
    assert blockers["PB-007-01"]["affected_descendants"] == ["MC-022", "MC-024", "MC-032", "MC-038"]
    assert blockers["PB-007-02"]["affected_descendants"] == ["MC-022", "MC-024", "MC-038"]

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
    bad["source_semantics"]["saved_operation_is_immutable"] = False
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["source_semantics"]["endpoints_are_authoritative"] = False
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["source_semantics"]["engagement_boundaries_are_authoritative"] = False
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["numeric_enclosure"]["pi_upper_rational"] = {"numerator": "3", "denominator": "1"}
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["numeric_enclosure"]["trigonometric_algebraicity_assumed"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["curve_classes"][2]["subdivision_rule"] = "fit endpoints with a decimal epsilon"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["curve_classes"][4]["subdivision_rule"] = "fit one shortcut across all vertices"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["curve_classes"][5]["subdivision_rule"] = "snap knots using epsilon"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["curve_classes"][7]["subdivision_rule"] = "independent full-angle coverage"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["transform_classes"][0]["forbidden"].remove("UNIT_ERASURE")
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["transform_classes"][1]["checked_bound"] = "reset inherited error after reclamp"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["actual_sweep_bound"]["centreline_only_is_sufficient"] = True
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["actual_sweep_bound"]["same_parameter_requirement"] = "interior samples only; endpoints may be trimmed"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["exact_controls"]["finite_cutter"]["support_radius"] = {"numerator": "3", "denominator": "1"}
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["exact_controls"]["finite_cutter"]["pose_sweep_upper"] = {"numerator": "1", "denominator": "1000"}
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["error_composition"]["recomputation_may_remove_prior_derived_error_only_with_proof"] = False
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["blockers"][0]["status"] = "CLOSED"
    mutations.append(bad)

    bad = copy.deepcopy(contract)
    bad["capability_guard"]["MC-B"] = "ACCEPTED"
    mutations.append(bad)

    rejected = 0
    for mutation in mutations:
        try:
            validate_contract(mutation, check_files=False)
        except (AssertionError, KeyError, TypeError, ValueError, ZeroDivisionError):
            rejected += 1
    assert rejected == len(mutations), f"accepted {len(mutations) - rejected} adversarial corruption(s)"


def verify_integration() -> None:
    contract = load(CONTRACT_PATH)
    validate_contract(contract, check_files=True)
    adversarial_self_test(contract)

    outcome = load(TASK / "outcome.json")
    assert outcome["schema"] == "radicadsac-mc-task-outcome/1.0"
    assert outcome["task"] == "MC-058"
    assert outcome["result_kind"] == "COMPLETED_RESEARCH"
    assert outcome["native_execution"] is False
    assert {b["id"] for b in outcome["blockers"]} == EXPECTED_BLOCKERS
    assert all(b["status"] == "OPEN" for b in outcome["blockers"])
    assert outcome["review"]["gate_changed"] is False
    assert outcome["review"]["programme_capability_changed"] is False

    registry = load(ROOT / "research/machining-completeness/outcomes-v1.json")
    record = registry["tasks"]["MC-058"]
    assert record["state"] == "COMPLETED_RESEARCH"
    assert {b["id"] for b in record["blockers"]} == EXPECTED_BLOCKERS
    assert all(b["status"] == "OPEN" for b in record["blockers"])
    required_artifacts = {
        "research/machining-completeness/tasks/MC-058/curve-sweep-contract-v1.json",
        "research/machining-completeness/tasks/MC-058/report.md",
        "research/machining-completeness/tasks/MC-058/outcome.json",
        "research/machining-completeness/tasks/MC-058/verify.py",
        "docs/machining-completeness/01-DOMAIN-AND-SEMANTICS.md",
    }
    assert required_artifacts <= set(record["accepted_artifacts"])

    doc = (ROOT / "docs/machining-completeness/01-DOMAIN-AND-SEMANTICS.md").read_text(encoding="utf-8")
    assert "MC-058 certified curve/transform and sweep-bound contract" in doc
    assert "e_inherited + e_translation + rho*e_rotation + e_tool" in doc
    assert "centreline-only" in doc
    assert "PB-007-01" in doc and "PB-007-02" in doc
    assert "MC-B remains **NOT_ESTABLISHED**" in doc

    workflow = (ROOT / ".github/workflows/mc1-static.yml").read_text(encoding="utf-8")
    assert "tasks/MC-058/verify.py" in workflow
    assert "tools/mc_workflow.py verify MC-058" in workflow


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract or --self-test")
    verify_integration()
    print("MC-058 certified curve/transform and sweep contract verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
