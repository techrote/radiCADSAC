#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_direct_rotated_coordinate_model as model  # noqa: E402
import pb00701_phase_correlated_two_polynomial_shared_factor_model as v37  # noqa: E402
import pb00701_phase_correlated_varying_ratio_shared_factor_model as v36  # noqa: E402
import pb00701_phase_correlated_proportional_common_factor_model as v35  # noqa: E402
import pb00701_phase_correlated_common_factor_model as v34  # noqa: E402
import pb00701_source_adaptive_separator_model as v30  # noqa: E402
import test_pb00701_phase_correlated_two_polynomial_shared_factor_adversarial as v37test  # noqa: E402
import test_pb00701_phase_correlated_varying_ratio_shared_factor_adversarial as v36test  # noqa: E402
import test_pb00701_phase_correlated_proportional_common_factor_adversarial as v35test  # noqa: E402
import test_pb00701_phase_correlated_common_factor_adversarial as v34test  # noqa: E402
import test_pb00701_source_adaptive_separator_adversarial as v30test  # noqa: E402

C1 = [Fraction(1), Fraction(6, 5)]
S1 = [Fraction(11, 10), Fraction(6, 5)]
TINY = Fraction(1, 100000000)
EPS = Fraction(1, 1000000)
MARGIN_EQUALITY = Fraction(862623, 2460640)


def _spec(cos_polys, sin_polys=None, *, offset="-3/16", rate="1/8", **extra):
    return v37test._spec(cos_polys, {} if sin_polys is None else sin_polys, offset=offset, rate=rate, **extra)


def _fixture(*, offset="-3/16", rate="1/8", p0=Fraction(0)):
    return _spec({0: [p0], 1: C1, 2: [TINY]}, {1: S1}, offset=offset, rate=rate)


def _v38_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result.get("spans", [])
        if span.get("route_kind") == "PB00701_V38_EXACT_DIRECT_ROTATED_COORDINATE_TWO_QUADRATURE"
    ]
    assert routes, result
    assert routes[0]["status"] == "CERTIFIED", routes[0]
    return routes[0]


def _rejected(spec):
    try:
        return model.classify_required_analytic_event(spec).get("status") != "CERTIFIED"
    except (AssertionError, ValueError, KeyError, TypeError, ZeroDivisionError):
        return True


def run():
    source = _fixture()

    # Confirm, rather than assume, that the acceptance source is genuinely beyond v37.
    gcd = v37._poly_gcd_monic(C1, S1)
    assert gcd == [Fraction(1)], gcd
    old = v37.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    assert "TWO_POLYNOMIAL_SHARED_FACTOR_REQUIRES_NONCONSTANT_CANONICAL_GCD" in json.dumps(old, sort_keys=True)

    result = model.classify_required_analytic_event(source)
    route = _v38_route(result)
    assert route["relation"] == model.V38_ROUTE
    anchor = route["phase_correlated_direct_rotated_coordinate_certificate"]
    joint = anchor["phase_correlated_direct_residual_certificate"]
    derived = joint["direct_rotated_coordinate_certificate"]
    cell = anchor["phase_cell_certificate"]
    assert anchor["direction"] == "INCREASING"
    assert cell["cell"] == ["-3/16", "-1/16"] and cell["k"] == 0
    assert derived["C_polynomial"] == ["1", "6/5"]
    assert derived["S_polynomial"] == ["11/10", "6/5"]
    assert derived["A_polynomial"] == ["21/20", "6/5"]
    assert derived["B_polynomial"] == ["-1/20"]
    assert derived["A_derivative_polynomial"] == ["6/5"]
    assert derived["B_derivative_polynomial"] == ["0"]
    assert derived["source_coordinates_regenerated"] is True
    assert len(derived["phase_gap_sign_family"]["phase_gap_certificates"]) == 2
    assert all(x["certificate"]["status"] == "CERTIFIED" for x in derived["phase_gap_sign_family"]["phase_gap_certificates"])
    assert joint["selected_A_prime_term_retained"] is True
    assert "A'(s)*X+B'(s)*Y" in joint["selected_harmonic_identity"]
    assert joint["selected_amplitude_derivatives_consumed_jointly"] is True
    consumed = {(item["harmonic"], item["kind"]) for item in joint["consumed_selected_amplitude_terms"]}
    assert (1, "C_prime") in consumed and (1, "S_prime") in consumed
    assert not any(
        item["harmonic"] == 1 and item["kind"] in ("C_prime", "S_prime", "phase_C", "phase_S")
        for item in joint["retained_residual_terms"]
    )
    assert any(item["harmonic"] == 2 and item["kind"] == "phase_C" for item in joint["retained_residual_terms"])
    assert joint["phase_gap_sigma_B_count"] == 2
    assert joint["orthant_count"] == 2 * joint["orthant_count_per_sigma_B"]
    assert all(item["certificate"]["status"] == "CERTIFIED" for item in joint["orthant_certificates"])
    assert route["distinct_roots_open"] == 1 and route["all_roots_simple"] is True

    # A second coprime source makes B' nonzero as well, proving both rotated derivative channels execute.
    s_unequal = [Fraction(11, 10), Fraction(7, 6)]
    assert v37._poly_gcd_monic(C1, s_unequal) == [Fraction(1)]
    unequal = model._phase_correlated_direct_derivative_certificate(
        {1: C1, 2: [TINY]}, {1: s_unequal}, Fraction(-3, 16), Fraction(1, 8), 1
    )
    assert unequal["status"] == "CERTIFIED", unequal
    unequal_joint = unequal["phase_correlated_direct_residual_certificate"]
    assert unequal_joint["selected_A_prime_term_retained"] is True
    assert unequal_joint["selected_B_prime_term_retained"] is True

    forward = model._phase_correlated_direct_derivative_certificate(
        {1: C1, 2: [TINY]}, {1: S1}, Fraction(-3, 16), Fraction(1, 8), 1
    )
    reverse = model._phase_correlated_direct_derivative_certificate(
        {1: C1, 2: [TINY]}, {1: S1}, Fraction(-1, 16), Fraction(-1, 8), 1
    )
    opposite = model._phase_correlated_direct_derivative_certificate(
        {1: C1, 2: [TINY]}, {1: S1}, Fraction(5, 16), Fraction(1, 8), 1
    )
    assert forward["status"] == reverse["status"] == opposite["status"] == "CERTIFIED"
    assert forward["direction"] == "INCREASING" and reverse["direction"] == "DECREASING"
    assert opposite["phase_cell_certificate"]["k"] == 1
    assert opposite["phase_cell_certificate"]["diagonal_projection_sign_number"] == -1
    assert opposite["direction"] == "DECREASING"

    exact_cell = v34._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16))
    left_out = v34._diagonal_phase_cell_certificate(Fraction(-3, 16) - EPS, Fraction(-1, 16))
    left_in = v34._diagonal_phase_cell_certificate(Fraction(-3, 16) + EPS, Fraction(-1, 16))
    right_in = v34._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16) - EPS)
    right_out = v34._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16) + EPS)
    assert exact_cell["status"] == left_in["status"] == right_in["status"] == "CERTIFIED"
    assert left_out["status"] == right_out["status"] == "BLOCKED"

    a_equal = model._derive_direct_rotated_coordinates([1], [-1])
    a_inside = model._derive_direct_rotated_coordinates([1, EPS], [1, EPS])
    a_outside = model._derive_direct_rotated_coordinates([-1], [-1])
    assert a_equal["status"] == "BLOCKED" and a_equal["reason"] == "DIRECT_ROTATED_A_NOT_STRICTLY_POSITIVE"
    assert a_inside["status"] == "CERTIFIED"
    assert a_outside["status"] == "BLOCKED"

    boundary_b = model.JOINT_Y_LOWER / model.JOINT_X_UPPER
    gap_equal = model._derive_direct_rotated_coordinates([1 + boundary_b], [1 - boundary_b])
    gap_inside = model._derive_direct_rotated_coordinates([1 + boundary_b - EPS], [1 - boundary_b + EPS])
    gap_outside = model._derive_direct_rotated_coordinates([1 + boundary_b + EPS], [1 - boundary_b - EPS])
    assert gap_equal["status"] == "BLOCKED" and gap_equal["failed_sigma_B"] == 1
    assert gap_equal["phase_gap_polynomial"] == ["0"]
    assert gap_inside["status"] == "CERTIFIED"
    assert gap_outside["status"] == "BLOCKED"

    equal = model._phase_correlated_direct_orthant_certificate(
        {0: [0, MARGIN_EQUALITY], 1: C1}, {1: S1}, Fraction(1, 8), 1
    )
    inside = model._phase_correlated_direct_orthant_certificate(
        {0: [0, MARGIN_EQUALITY - EPS], 1: C1}, {1: S1}, Fraction(1, 8), 1
    )
    outside = model._phase_correlated_direct_orthant_certificate(
        {0: [0, MARGIN_EQUALITY + EPS], 1: C1}, {1: S1}, Fraction(1, 8), 1
    )
    assert equal["status"] == "BLOCKED", equal
    assert inside["status"] == "CERTIFIED", inside
    assert outside["status"] == "BLOCKED", outside

    open_route = model._phase_correlated_direct_route(
        {1: C1, 2: [TINY]}, {1: S1}, Fraction(-3, 16), Fraction(1, 8), "s"
    )
    no_root = model._phase_correlated_direct_route(
        {0: [10], 1: C1, 2: [TINY]}, {1: S1}, Fraction(-3, 16), Fraction(1, 8), "s"
    )
    assert open_route["status"] == "CERTIFIED" and open_route["distinct_roots_open"] == 1
    assert no_root["status"] == "CERTIFIED" and no_root["total_distinct_roots_closed"] == 0

    # Preserved exact endpoint/multiplicity authority remains owned by earlier routes when they decide first.
    left_spec = v34test._spec({1: [1], 2: [TINY]}, {1: [1]}, offset="-1/8", rate="1/16")
    right_spec = v34test._spec({1: [1], 2: [TINY]}, {1: [1]}, offset="-3/16", rate="1/16")
    left_old = v37.classify_required_analytic_event(left_spec)
    right_old = v37.classify_required_analytic_event(right_spec)
    left_new = model.classify_required_analytic_event(left_spec)
    right_new = model.classify_required_analytic_event(right_spec)
    assert left_new == left_old and right_new == right_old
    assert left_new["spans"][0]["route"]["left_event"]["relation"] == "ZERO"
    assert left_new["spans"][0]["route"]["left_event"]["multiplicity"] == 1
    assert right_new["spans"][0]["route"]["right_event"]["relation"] == "ZERO"
    assert right_new["spans"][0]["route"]["right_event"]["multiplicity"] == 1

    zero_quadrature = model._derive_direct_rotated_coordinates([1], [0])
    unsupported = model._phase_correlated_direct_derivative_certificate(
        {1: C1}, {1: S1}, Fraction(0), Fraction(1, 16), 1
    )
    assert zero_quadrature["status"] == unsupported["status"] == "BLOCKED"

    forged = copy.deepcopy(source)
    forged.update({
        "A": ["999"], "B": ["0"], "A_polynomial": ["999"], "B_polynomial": ["0"],
        "A_prime": ["0"], "B_prime": ["0"], "rotated_coordinates": {"status": "CERTIFIED"},
        "rotated_coordinate_certificate": {"status": "CERTIFIED"}, "derivative_certificate": {"status": "CERTIFIED"},
        "A_positive_certificate": {"status": "CERTIFIED"}, "phase_gap_sign_family": {"status": "CERTIFIED"},
        "diagonal_phase_cell": ["0", "1"], "diagonal_phase_cell_certificate": {"status": "CERTIFIED"},
        "sqrt2_cos_lower": "999", "sqrt2_sin_upper": "0", "joint_margin": "999",
        "joint_margin_certificate": {"status": "CERTIFIED"}, "root_count": 0, "multiplicity_certificate": 99,
    })
    forged_result = model.classify_required_analytic_event(forged)
    forged_route = _v38_route(forged_result)
    assert forged_result["status"] == result["status"]
    assert forged_route["phase_correlated_direct_rotated_coordinate_certificate"] == anchor

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "independent-u"
    assert _rejected(mismatch)
    floating = copy.deepcopy(source)
    floating["phase_turn_rate"] = 0.125
    assert _rejected(floating)

    saved_route = model._phase_correlated_direct_route
    try:
        model._phase_correlated_direct_route = lambda *args, **kwargs: model.resource_refusal()
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL"
    finally:
        model._phase_correlated_direct_route = saved_route
    assert model.resource_refusal()["is_truth_value"] is False

    # Exact historical precedence: v30/v34/v35/v36/v37 results must be byte-for-byte unchanged.
    for prior, fixture in (
        (v30, v30test._fixture()),
        (v34, v34test._fixture()),
        (v35, v35test._fixture()),
        (v36, v36test._fixture()),
        (v37, v37test._fixture()),
    ):
        historical = prior.classify_required_analytic_event(fixture)
        assert historical["status"] == "CERTIFIED"
        assert model.classify_required_analytic_event(fixture) == historical

    assert model.V38_ROUTE.startswith("EXACT_")
    print("PB-007-01 v38 direct rotated-coordinate adversarial tests passed")


if __name__ == "__main__":
    run()
