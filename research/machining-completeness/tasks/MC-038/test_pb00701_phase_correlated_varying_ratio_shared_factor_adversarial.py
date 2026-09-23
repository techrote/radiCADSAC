#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_phase_correlated_varying_ratio_shared_factor_model as model  # noqa: E402
import pb00701_phase_correlated_proportional_common_factor_model as v35  # noqa: E402
import pb00701_phase_correlated_common_factor_model as v34  # noqa: E402
import pb00701_source_adaptive_separator_model as v30  # noqa: E402
import test_pb00701_phase_correlated_proportional_common_factor_adversarial as v35test  # noqa: E402
import test_pb00701_phase_correlated_common_factor_adversarial as v34test  # noqa: E402
import test_pb00701_source_adaptive_separator_adversarial as v30test  # noqa: E402

G = [Fraction(1), Fraction(3, 2), Fraction(9, 16)]
LAMBDA = [Fraction(9, 10), Fraction(1, 100)]
CG = model._pmul(LAMBDA, G)
TINY = Fraction(1, 100000000)
EPS = Fraction(1, 1000000)
PHASE_GAP_BOUNDARY = Fraction(-7751, 18905)
MARGIN_EQUALITY = Fraction(11021443, 12303200)


def _spec(cos_polys, sin_polys=None, *, offset="-3/16", rate="1/8", **extra):
    return v35test._spec(cos_polys, {} if sin_polys is None else sin_polys, offset=offset, rate=rate, **extra)


def _fixture(*, offset="-3/16", rate="1/8", p0=Fraction(0)):
    return _spec({0: [p0], 1: CG, 2: [TINY]}, {1: G}, offset=offset, rate=rate)


def _v36_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [span["route"] for span in result.get("spans", []) if span.get("route_kind") == "PB00701_V36_EXACT_PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR"]
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
    old = v35.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old

    result = model.classify_required_analytic_event(source)
    route = _v36_route(result)
    assert route["relation"] == model.V36_ROUTE
    anchor = route["phase_correlated_varying_ratio_shared_factor_certificate"]
    joint = anchor["phase_correlated_varying_ratio_residual_certificate"]
    derived = joint["varying_ratio_shared_factor_certificate"]
    cell = anchor["phase_cell_certificate"]
    assert anchor["direction"] == "INCREASING"
    assert cell["cell"] == ["-3/16", "-1/16"] and cell["k"] == 0
    assert derived["derived_lambda_polynomial"] == ["9/10", "1/100"]
    assert derived["derived_lambda_derivative"] == ["1/100"]
    assert derived["division_remainder"] == ["0"]
    assert derived["A_polynomial"] == ["19/20", "1/200"]
    assert derived["B_polynomial"] == ["-1/20", "1/200"]
    assert all(item["equal"] for item in derived["coefficient_identities"])
    assert len(derived["phase_gap_sign_family"]["phase_gap_certificates"]) == 2
    assert all(item["certificate"]["status"] == "CERTIFIED" for item in derived["phase_gap_sign_family"]["phase_gap_certificates"])
    assert joint["common_factor_polynomial"] == ["1", "3/2", "9/16"]
    assert joint["common_factor_derivative"] == ["3/2", "9/8"]
    assert joint["lambda_derivative_polynomial"] == ["1/100"]
    assert joint["lambda_derivative_times_G_polynomial"] == ["1/100", "3/200", "9/1600"]
    assert joint["selected_lambda_prime_G_term_retained"] is True
    assert "lambda'*G*cos(theta)" in joint["selected_harmonic_identity"]
    assert joint["selected_amplitude_derivatives_consumed_jointly"] is True
    assert joint["selected_phase_terms_consumed_jointly"] is True
    consumed = {(item["harmonic"], item["kind"]) for item in joint["consumed_selected_amplitude_terms"]}
    assert (1, "C_prime") in consumed and (1, "S_prime") in consumed
    assert not any(item["harmonic"] == 1 and item["kind"] in ("C_prime", "S_prime", "phase_C", "phase_S") for item in joint["retained_residual_terms"])
    assert any(item["harmonic"] == 2 and item["kind"] == "phase_C" for item in joint["retained_residual_terms"])
    assert joint["phase_gap_sigma_B_count"] == 2
    assert joint["orthant_count"] == 2 * joint["orthant_count_per_sigma_B"]
    assert all(item["certificate"]["status"] == "CERTIFIED" for item in joint["orthant_certificates"])
    assert route["distinct_roots_open"] == 1 and route["all_roots_simple"] is True

    forward = model._phase_correlated_varying_ratio_derivative_certificate({1: CG, 2: [TINY]}, {1: G}, Fraction(-3, 16), Fraction(1, 8), 1)
    reverse = model._phase_correlated_varying_ratio_derivative_certificate({1: CG, 2: [TINY]}, {1: G}, Fraction(-1, 16), Fraction(-1, 8), 1)
    opposite = model._phase_correlated_varying_ratio_derivative_certificate({1: CG, 2: [TINY]}, {1: G}, Fraction(5, 16), Fraction(1, 8), 1)
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

    a_equal = model._a_positive_certificate([Fraction(-1), Fraction(1, 100)])
    a_inside = model._a_positive_certificate([Fraction(-1) + EPS, Fraction(1, 100)])
    a_outside = model._a_positive_certificate([Fraction(-1) - EPS, Fraction(1, 100)])
    assert a_equal["status"] == "BLOCKED"
    assert a_inside["status"] == "CERTIFIED"
    assert a_outside["status"] == "BLOCKED"

    gap_equal = model._derive_varying_ratio_shared_factor([PHASE_GAP_BOUNDARY, Fraction(1, 100)], [1])
    gap_inside = model._derive_varying_ratio_shared_factor([PHASE_GAP_BOUNDARY + EPS, Fraction(1, 100)], [1])
    gap_outside = model._derive_varying_ratio_shared_factor([PHASE_GAP_BOUNDARY - EPS, Fraction(1, 100)], [1])
    assert gap_equal["status"] == "BLOCKED" and gap_equal["failed_sigma_B"] == -1
    assert gap_equal["phase_gap_polynomial"][0] == "0"
    assert gap_inside["status"] == "CERTIFIED"
    assert gap_outside["status"] == "BLOCKED"

    equal = model._phase_correlated_varying_ratio_orthant_certificate({0: [0, MARGIN_EQUALITY], 1: LAMBDA}, {1: [1]}, Fraction(1, 8), 1)
    inside = model._phase_correlated_varying_ratio_orthant_certificate({0: [0, MARGIN_EQUALITY - EPS], 1: LAMBDA}, {1: [1]}, Fraction(1, 8), 1)
    outside = model._phase_correlated_varying_ratio_orthant_certificate({0: [0, MARGIN_EQUALITY + EPS], 1: LAMBDA}, {1: [1]}, Fraction(1, 8), 1)
    assert equal["status"] == "BLOCKED"
    assert inside["status"] == "CERTIFIED"
    assert outside["status"] == "BLOCKED"

    open_route = model._phase_correlated_varying_ratio_route({1: CG, 2: [TINY]}, {1: G}, Fraction(-3, 16), Fraction(1, 8), "s")
    no_root = model._phase_correlated_varying_ratio_route({0: [10], 1: CG, 2: [TINY]}, {1: G}, Fraction(-3, 16), Fraction(1, 8), "s")
    assert open_route["status"] == "CERTIFIED" and open_route["distinct_roots_open"] == 1
    assert no_root["status"] == "CERTIFIED" and no_root["total_distinct_roots_closed"] == 0

    left_spec = v34test._spec({1: [1], 2: [TINY]}, {1: [1]}, offset="-1/8", rate="1/16")
    right_spec = v34test._spec({1: [1], 2: [TINY]}, {1: [1]}, offset="-3/16", rate="1/16")
    left_old = v35.classify_required_analytic_event(left_spec)
    right_old = v35.classify_required_analytic_event(right_spec)
    left_new = model.classify_required_analytic_event(left_spec)
    right_new = model.classify_required_analytic_event(right_spec)
    assert left_new == left_old and right_new == right_old
    assert left_new["spans"][0]["route"]["left_event"]["relation"] == "ZERO"
    assert left_new["spans"][0]["route"]["left_event"]["multiplicity"] == 1
    assert right_new["spans"][0]["route"]["right_event"]["relation"] == "ZERO"
    assert right_new["spans"][0]["route"]["right_event"]["multiplicity"] == 1

    perturbed = list(CG)
    perturbed[-1] += EPS
    remainder = model._derive_varying_ratio_shared_factor(perturbed, G)
    constant_ratio = model._derive_varying_ratio_shared_factor(v35test.CG, G)
    sign_g = [Fraction(1), Fraction(-2)]
    sign_c = model._pmul(LAMBDA, sign_g)
    sign_changing = model._phase_correlated_varying_ratio_derivative_certificate({1: sign_c}, {1: sign_g}, Fraction(-3, 16), Fraction(1, 8), 1)
    zero_g = model._phase_correlated_varying_ratio_derivative_certificate({1: LAMBDA}, {1: [0]}, Fraction(-3, 16), Fraction(1, 8), 1)
    unsupported = model._phase_correlated_varying_ratio_derivative_certificate({1: LAMBDA}, {1: [1]}, Fraction(0), Fraction(1, 16), 1)
    assert remainder["status"] == "BLOCKED" and remainder["reason"] == "SELECTED_HARMONIC_POLYNOMIAL_DIVISION_REMAINDER_NONZERO"
    assert remainder["division_remainder"] != ["0"]
    assert constant_ratio["status"] == "BLOCKED" and constant_ratio["reason"] == "VARYING_RATIO_REQUIRES_NONCONSTANT_EXACT_POLYNOMIAL_QUOTIENT"
    assert sign_changing["status"] == zero_g["status"] == unsupported["status"] == "BLOCKED"

    forged = copy.deepcopy(source)
    forged.update({
        "lambda": "999", "lambda_polynomial": ["999"], "lambda_derivative": ["0"],
        "division_quotient": ["999"], "division_remainder": ["0"],
        "polynomial_division_certificate": {"status": "CERTIFIED"},
        "common_factor": ["999"], "common_factor_certificate": {"status": "CERTIFIED"},
        "A_polynomial": ["999"], "B_polynomial": ["0"], "A_positive_certificate": {"status": "CERTIFIED"},
        "phase_gap_sign_family": {"status": "CERTIFIED"}, "diagonal_phase_cell": ["0", "1"],
        "diagonal_phase_cell_certificate": {"status": "CERTIFIED"}, "sqrt2_cos_lower": "999",
        "sqrt2_sin_upper": "0", "joint_margin": "999", "joint_margin_certificate": {"status": "CERTIFIED"},
        "root_count": 0, "multiplicity_certificate": 99,
    })
    forged_result = model.classify_required_analytic_event(forged)
    forged_route = _v36_route(forged_result)
    assert forged_result["status"] == result["status"]
    assert forged_route["phase_correlated_varying_ratio_shared_factor_certificate"] == anchor

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "independent-u"
    assert _rejected(mismatch)
    floating = copy.deepcopy(source)
    floating["phase_turn_rate"] = 0.125
    assert _rejected(floating)

    saved = model._phase_correlated_varying_ratio_route
    try:
        model._phase_correlated_varying_ratio_route = lambda *args, **kwargs: model.resource_refusal()
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL"
    finally:
        model._phase_correlated_varying_ratio_route = saved
    assert model.resource_refusal()["is_truth_value"] is False

    historical_v30_spec = v30test._fixture()
    historical_v30 = v30.classify_required_analytic_event(historical_v30_spec)
    assert historical_v30["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(historical_v30_spec) == historical_v30
    historical_v34_spec = v34test._fixture()
    historical_v34 = v34.classify_required_analytic_event(historical_v34_spec)
    assert historical_v34["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(historical_v34_spec) == historical_v34
    historical_v35_spec = v35test._fixture()
    historical_v35 = v35.classify_required_analytic_event(historical_v35_spec)
    assert historical_v35["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(historical_v35_spec) == historical_v35

    assert model.V36_ROUTE.startswith("EXACT_")
    print("PB-007-01 v36 phase-correlated varying-ratio shared-factor adversarial tests passed")


if __name__ == "__main__":
    run()
