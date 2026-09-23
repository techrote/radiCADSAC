#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_signed_b_anti_diagonal_model as model  # noqa: E402
import pb00701_signed_a_direct_rotated_coordinate_model as v39  # noqa: E402
import pb00701_direct_rotated_coordinate_model as v38  # noqa: E402
import pb00701_phase_correlated_two_polynomial_shared_factor_model as v37  # noqa: E402
import pb00701_phase_correlated_varying_ratio_shared_factor_model as v36  # noqa: E402
import pb00701_phase_correlated_proportional_common_factor_model as v35  # noqa: E402
import pb00701_phase_correlated_common_factor_model as v34  # noqa: E402
import pb00701_source_adaptive_separator_model as v30  # noqa: E402
import test_pb00701_signed_a_direct_rotated_coordinate_adversarial as v39test  # noqa: E402
import test_pb00701_direct_rotated_coordinate_adversarial as v38test  # noqa: E402
import test_pb00701_phase_correlated_two_polynomial_shared_factor_adversarial as v37test  # noqa: E402
import test_pb00701_phase_correlated_varying_ratio_shared_factor_adversarial as v36test  # noqa: E402
import test_pb00701_phase_correlated_proportional_common_factor_adversarial as v35test  # noqa: E402
import test_pb00701_phase_correlated_common_factor_adversarial as v34test  # noqa: E402
import test_pb00701_source_adaptive_separator_adversarial as v30test  # noqa: E402

C1 = [Fraction(19, 20), Fraction(1, 10)]
S1 = [Fraction(-21, 20), Fraction(1, 10)]
TINY = Fraction(1, 100000000)
EPS = Fraction(1, 1000000)


def _spec(cos_polys, sin_polys=None, *, offset="1/16", rate="1/8", **extra):
    return v39test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(*, offset="1/16", rate="1/8", p0=Fraction(0)):
    return _spec(
        {0: [-p0], 1: C1, 2: [-TINY]},
        {1: S1},
        offset=offset,
        rate=rate,
    )


def _v40_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"]
        for span in result.get("spans", [])
        if span.get("route_kind")
        == "PB00701_V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE"
    ]
    assert routes, result
    assert routes[0]["status"] == "CERTIFIED", routes[0]
    return routes[0]


def _rejected(spec):
    try:
        return model.classify_required_analytic_event(spec).get("status") != "CERTIFIED"
    except (AssertionError, ValueError, KeyError, TypeError, ZeroDivisionError):
        return True


def _integral_of_derivative(poly):
    return [Fraction(0)] + [poly[i] / Fraction(i + 1) for i in range(len(poly))]


def run():
    source = _fixture()

    # The acceptance source must genuinely survive all complete v39 authority.
    old = v39.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    old_dump = json.dumps(old, sort_keys=True)
    assert "SIGNED_DIRECT_ROTATED_A_NOT_STRICTLY_NONZERO" in old_dump, old_dump
    assert v37._poly_gcd_monic(C1, S1) == [Fraction(1)]

    result = model.classify_required_analytic_event(source)
    route = _v40_route(result)
    assert route["relation"] == model.V40_ROUTE
    anchor = route["phase_correlated_signed_b_anti_diagonal_certificate"]
    joint = anchor["phase_correlated_signed_b_residual_certificate"]
    derived = joint["signed_b_anti_diagonal_coordinate_certificate"]
    cell = anchor["phase_cell_certificate"]
    assert anchor["direction"] == "DECREASING"
    assert anchor["sigma_B"] == 1
    assert anchor["sign_identity"] == "sign(D)=-sigma_B*sign(h*r)*anti_diagonal_projection_sign"
    assert anchor["orientation_is_proof_bookkeeping_only"] is True
    assert cell["cell"] == ["1/16", "3/16"] and cell["k"] == 0
    assert cell["anti_diagonal_projection_sign_number"] == 1
    assert "quarter-turn" in cell["relation"].lower()
    assert cell["diagonal_symmetry_certificate"]["status"] == "CERTIFIED"
    assert derived["C_polynomial"] == ["19/20", "1/10"]
    assert derived["S_polynomial"] == ["-21/20", "1/10"]
    assert derived["A_polynomial"] == ["-1/20", "1/10"]
    assert derived["B_polynomial"] == ["1"]
    assert derived["A_derivative_polynomial"] == ["1/10"]
    assert derived["B_derivative_polynomial"] == ["0"]
    assert derived["sigma_B"] == 1
    assert derived["Bbar_polynomial"] == ["1"]
    assert derived["Atilde_polynomial"] == ["1/20", "-1/10"]
    assert derived["Bbar_derivative_polynomial"] == ["0"]
    assert derived["Atilde_derivative_polynomial"] == ["-1/10"]
    assert derived["signed_B_orientation_certificate"]["sigma_B"] == 1
    assert derived["source_coordinates_regenerated"] is True
    assert derived["caller_orientation_trusted"] is False
    assert len(derived["phase_gap_sign_family"]["phase_gap_certificates"]) == 2
    assert all(
        x["certificate"]["status"] == "CERTIFIED"
        for x in derived["phase_gap_sign_family"]["phase_gap_certificates"]
    )
    assert joint["issue_243_identity_sign_typo_corrected"] is True
    assert "-Bbar'(s)*Y" in joint["oriented_selected_harmonic_identity"]
    assert "D=A'(s)*X+B'(s)*Y" in joint["physical_selected_harmonic_identity"]
    assert joint["selected_Atilde_prime_term_retained"] is True
    consumed = {
        (item["harmonic"], item["kind"])
        for item in joint["consumed_selected_amplitude_terms"]
    }
    assert (1, "C_prime") in consumed and (1, "S_prime") in consumed
    assert not any(
        item["harmonic"] == 1
        and item["kind"] in ("C_prime", "S_prime", "phase_C", "phase_S")
        for item in joint["retained_residual_terms"]
    )
    assert any(
        item["harmonic"] == 2 and item["kind"] == "phase_C"
        for item in joint["retained_residual_terms"]
    )
    assert joint["phase_gap_sigma_A_count"] == 2
    assert joint["orthant_count"] == 2 * joint["orthant_count_per_sigma_A"]
    assert all(
        item["certificate"]["status"] == "CERTIFIED"
        for item in joint["orthant_certificates"]
    )
    assert route["all_roots_simple"] is True

    # Diagonal sources already owned by v39 must be byte-for-byte unchanged.
    prior_source = v39test._fixture()
    prior_result = v39.classify_required_analytic_event(prior_source)
    assert prior_result["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(prior_source) == prior_result

    # Both strict B orientations and their exact zero/crossing boundary.
    pos = model._derive_signed_b_orientation([EPS])
    neg = model._derive_signed_b_orientation([-EPS])
    zero = model._derive_signed_b_orientation([0])
    crossing = model._derive_signed_b_orientation([-1, 2])
    assert pos["status"] == neg["status"] == "CERTIFIED"
    assert pos["sigma_B"] == 1 and neg["sigma_B"] == -1
    assert zero["status"] == "BLOCKED" and crossing["status"] == "BLOCKED"

    negative_orientation = model._derive_signed_b_anti_diagonal_coordinates(
        [Fraction(-19, 20), Fraction(-1, 10)],
        [Fraction(21, 20), Fraction(-1, 10)],
    )
    assert negative_orientation["status"] == "CERTIFIED"
    assert negative_orientation["sigma_B"] == -1

    # Positive/negative phase rates and opposite anti-diagonal projection cells.
    forward = model._phase_correlated_signed_b_derivative_certificate(
        {1: C1, 2: [-TINY]}, {1: S1}, Fraction(1, 16), Fraction(1, 8), 1
    )
    reverse = model._phase_correlated_signed_b_derivative_certificate(
        {1: C1, 2: [-TINY]}, {1: S1}, Fraction(3, 16), Fraction(-1, 8), 1
    )
    opposite = model._phase_correlated_signed_b_derivative_certificate(
        {1: C1, 2: [-TINY]}, {1: S1}, Fraction(9, 16), Fraction(1, 8), 1
    )
    assert forward["status"] == reverse["status"] == opposite["status"] == "CERTIFIED"
    assert forward["direction"] == "DECREASING" and reverse["direction"] == "INCREASING"
    assert opposite["phase_cell_certificate"]["k"] == 1
    assert opposite["phase_cell_certificate"]["anti_diagonal_projection_sign_number"] == -1
    assert opposite["direction"] == "INCREASING"

    # Exact anti-diagonal cell endpoints and rational in/out neighbours.
    exact_cell = model._anti_diagonal_phase_cell_certificate(
        Fraction(1, 16), Fraction(3, 16)
    )
    left_out = model._anti_diagonal_phase_cell_certificate(
        Fraction(1, 16) - EPS, Fraction(3, 16)
    )
    left_in = model._anti_diagonal_phase_cell_certificate(
        Fraction(1, 16) + EPS, Fraction(3, 16)
    )
    right_in = model._anti_diagonal_phase_cell_certificate(
        Fraction(1, 16), Fraction(3, 16) - EPS
    )
    right_out = model._anti_diagonal_phase_cell_certificate(
        Fraction(1, 16), Fraction(3, 16) + EPS
    )
    assert exact_cell["status"] == left_in["status"] == right_in["status"] == "CERTIFIED"
    assert left_out["status"] == right_out["status"] == "BLOCKED"

    # Exact complementary phase-gap equality plus strict neighbours.
    boundary_atilde = model.ANTI_X_LOWER / model.ANTI_Y_UPPER
    gap_equal = model._derive_signed_b_anti_diagonal_coordinates(
        [1 - boundary_atilde], [-1 - boundary_atilde]
    )
    gap_inside = model._derive_signed_b_anti_diagonal_coordinates(
        [1 - (boundary_atilde - EPS)], [-1 - (boundary_atilde - EPS)]
    )
    gap_outside = model._derive_signed_b_anti_diagonal_coordinates(
        [1 - (boundary_atilde + EPS)], [-1 - (boundary_atilde + EPS)]
    )
    assert gap_equal["status"] == "BLOCKED" and gap_equal["phase_gap_polynomial"] == ["0"]
    assert gap_inside["status"] == "CERTIFIED"
    assert gap_outside["status"] == "BLOCKED"

    # Construct an exact complete-margin equality in one finite orthant.
    atilde = [Fraction(1, 20), Fraction(-1, 10)]
    phase_gap = model.v22._padd(
        [model.ANTI_X_LOWER],
        model.v22._pscale(atilde, -model.ANTI_Y_UPPER),
    )
    phase_base = model.v22._pscale(phase_gap, Fraction(3, 4))
    target_derivative = model.v22._padd(
        phase_base,
        model.v22._pscale([Fraction(-1, 10)], -model.ANTI_X_UPPER),
    )
    p_equal = _integral_of_derivative(target_derivative)
    p_inside = list(p_equal)
    p_outside = list(p_equal)
    p_inside[1] -= EPS
    p_outside[1] += EPS
    equal = model._phase_correlated_signed_b_orthant_certificate(
        {0: p_equal, 1: C1}, {1: S1}, Fraction(1, 8), 1
    )
    inside = model._phase_correlated_signed_b_orthant_certificate(
        {0: p_inside, 1: C1}, {1: S1}, Fraction(1, 8), 1
    )
    outside = model._phase_correlated_signed_b_orthant_certificate(
        {0: p_outside, 1: C1}, {1: S1}, Fraction(1, 8), 1
    )
    assert equal["status"] == "BLOCKED", equal
    assert inside["status"] == "CERTIFIED", inside
    assert outside["status"] == "BLOCKED", outside

    # Preserved exact endpoint/root/multiplicity authority: open and zero-root cases.
    open_route = model._phase_correlated_signed_b_route(
        {1: C1, 2: [-TINY]},
        {1: S1},
        Fraction(1, 16),
        Fraction(1, 8),
        "s",
    )
    no_root = model._phase_correlated_signed_b_route(
        {0: [-10], 1: C1, 2: [-TINY]},
        {1: S1},
        Fraction(1, 16),
        Fraction(1, 8),
        "s",
    )
    assert open_route["status"] == "CERTIFIED"
    assert open_route["all_roots_simple"] is True
    assert no_root["status"] == "CERTIFIED" and no_root["total_distinct_roots_closed"] == 0

    # Historical rational-turn endpoint fixtures retain exact predecessor ownership.
    left_spec = v38test.v34test._spec(
        {1: [1], 2: [TINY]}, {1: [1]}, offset="-1/8", rate="1/16"
    )
    right_spec = v38test.v34test._spec(
        {1: [1], 2: [TINY]}, {1: [1]}, offset="-3/16", rate="1/16"
    )
    for endpoint_spec in (left_spec, right_spec):
        assert model.classify_required_analytic_event(endpoint_spec) == v39.classify_required_analytic_event(endpoint_spec)

    unsupported = model._phase_correlated_signed_b_derivative_certificate(
        {1: C1}, {1: S1}, Fraction(0), Fraction(1, 16), 1
    )
    assert unsupported["status"] == "BLOCKED"

    # Caller orientation/cell/bound/margin/root metadata is never authority.
    forged = copy.deepcopy(source)
    forged.update(
        {
            "sigma_B": -1,
            "B_sign": "NEGATIVE",
            "orientation": -1,
            "Atilde": ["999"],
            "Bbar": ["999"],
            "Atilde_polynomial": ["999"],
            "Bbar_polynomial": ["999"],
            "Atilde_derivative_polynomial": ["0"],
            "Bbar_derivative_polynomial": ["0"],
            "orientation_certificate": {"status": "CERTIFIED"},
            "signed_B_orientation_certificate": {"status": "CERTIFIED", "sigma_B": -1},
            "rotated_coordinate_certificate": {"status": "CERTIFIED"},
            "derivative_certificate": {"status": "CERTIFIED"},
            "phase_gap_sign_family": {"status": "CERTIFIED"},
            "anti_diagonal_phase_cell_certificate": {"status": "CERTIFIED"},
            "anti_diagonal_projection_sign": -1,
            "joint_margin_certificate": {"status": "CERTIFIED"},
            "root_count": 0,
            "multiplicity_certificate": 99,
        }
    )
    forged_result = model.classify_required_analytic_event(forged)
    forged_route = _v40_route(forged_result)
    assert forged_result["status"] == result["status"]
    assert forged_route["phase_correlated_signed_b_anti_diagonal_certificate"] == anchor

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "independent-u"
    assert _rejected(mismatch)
    floating = copy.deepcopy(source)
    floating["phase_turn_rate"] = 0.125
    assert _rejected(floating)

    saved_route = model._phase_correlated_signed_b_route
    try:
        model._phase_correlated_signed_b_route = (
            lambda *args, **kwargs: model.resource_refusal()
        )
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL"
    finally:
        model._phase_correlated_signed_b_route = saved_route

    saved_strict = model._strict_positive
    try:
        model._strict_positive = lambda *args, **kwargs: {
            "status": "RESOURCE_REFUSAL",
            "reason": "TEST_RESOURCE_REFUSAL",
            "is_truth_value": False,
        }
        refused_sign = model._derive_signed_b_orientation([1])
        assert refused_sign["status"] == "RESOURCE_REFUSAL"
        assert refused_sign["is_truth_value"] is False
    finally:
        model._strict_positive = saved_strict
    assert model.resource_refusal()["is_truth_value"] is False

    # Complete predecessor authority owns every established historical success unchanged.
    historical_fixtures = (
        (v30, v30test._fixture()),
        (v34, v34test._fixture()),
        (v35, v35test._fixture()),
        (v36, v36test._fixture()),
        (v37, v37test._fixture()),
        (v38, v38test._fixture()),
        (v39, v39test._fixture()),
    )
    for prior, fixture in historical_fixtures:
        historical = prior.classify_required_analytic_event(fixture)
        assert historical["status"] == "CERTIFIED", (prior.__name__, historical)
        assert model.classify_required_analytic_event(fixture) == v39.classify_required_analytic_event(fixture)

    assert model.V40_ROUTE.startswith("EXACT_")
    print("PB-007-01 v40 signed-B anti-diagonal adversarial tests passed")


if __name__ == "__main__":
    run()
