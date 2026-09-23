#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_phase_correlated_proportional_common_factor_model as model  # noqa: E402
import pb00701_phase_correlated_common_factor_model as v34  # noqa: E402
import pb00701_source_adaptive_separator_model as v30  # noqa: E402
import test_pb00701_phase_correlated_common_factor_adversarial as v34test  # noqa: E402
import test_pb00701_source_adaptive_separator_adversarial as v30test  # noqa: E402
import test_pb00701_multiharmonic_monotone_anchor_adversarial as v19test  # noqa: E402

G = [Fraction(1), Fraction(3, 2), Fraction(9, 16)]
LAMBDA = Fraction(9, 10)
CG = [LAMBDA * value for value in G]
TINY = Fraction(1, 100000000)
EPS = Fraction(1, 1000000)
PHASE_GAP_BOUNDARY = Fraction(-7751, 18905)


def _spec(cos_polys, sin_polys=None, *, offset="-3/16", rate="1/8", **extra):
    return v19test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(*, offset="-3/16", rate="1/8", p0=Fraction(0)):
    # G=(1+3s/4)^2, C1=(9/10)G, S1=G.  A tiny live h=2 COS
    # term ensures the non-anchor phase residual remains materially present.
    return _spec(
        {0: [p0], 1: CG, 2: [TINY]},
        {1: G},
        offset=offset,
        rate=rate,
    )


def _v35_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result.get("spans", [])
        if span.get("route_kind") == "PB00701_V35_EXACT_PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR"
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
    # Primary acceptance: complete prior executable authority, including v34,
    # blocks solely because the selected quadratures are unequal.  V35 derives
    # lambda from source coefficients and certifies the complete event.
    source = _fixture()
    old = v34.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old

    result = model.classify_required_analytic_event(source)
    route = _v35_route(result)
    assert route["relation"] == model.V35_ROUTE
    anchor = route["phase_correlated_proportional_common_factor_certificate"]
    joint = anchor["phase_correlated_proportional_residual_certificate"]
    proportional = joint["proportional_common_factor_certificate"]
    cell = anchor["phase_cell_certificate"]
    assert anchor["direction"] == "INCREASING"
    assert cell["cell"] == ["-3/16", "-1/16"]
    assert cell["k"] == 0
    assert proportional["derived_lambda"] == "9/10"
    assert proportional["A"] == "19/20"
    assert proportional["B"] == "-1/20"
    assert proportional["phase_gap_P"] == "148593/123032"
    assert proportional["joint_amplitude_upper_Q"] == "2673/4550"
    assert proportional["joint_Y_upper_W"] == "99/70"
    assert all(item["equal"] for item in proportional["coefficient_identities"])
    assert joint["common_factor_polynomial"] == ["1", "3/2", "9/16"]
    assert joint["common_factor_derivative"] == ["3/2", "9/8"]
    assert joint["selected_amplitude_derivatives_consumed_jointly"] is True
    assert joint["selected_phase_terms_consumed_jointly"] is True
    consumed = {(item["harmonic"], item["kind"]) for item in joint["consumed_selected_amplitude_terms"]}
    assert (1, "C_prime") in consumed and (1, "S_prime") in consumed, consumed
    assert not any(
        item["harmonic"] == 1 and item["kind"] in ("C_prime", "S_prime", "phase_C", "phase_S")
        for item in joint["retained_residual_terms"]
    )
    assert any(
        item["harmonic"] == 2 and item["kind"] == "phase_C"
        for item in joint["retained_residual_terms"]
    ), joint["retained_residual_terms"]
    assert all(item["certificate"]["status"] == "CERTIFIED" for item in joint["orthant_certificates"])
    assert route["distinct_roots_open"] == 1, route
    assert route["all_roots_simple"] is True
    assert route["sampling_used"] is False
    assert route["numerical_trigonometry_used"] is False

    # Positive/negative rate and opposite diagonal cells change only the exact
    # expected projection sign.
    forward = model._phase_correlated_proportional_derivative_certificate(
        {1: CG, 2: [TINY]}, {1: G}, Fraction(-3, 16), Fraction(1, 8), 1
    )
    reverse = model._phase_correlated_proportional_derivative_certificate(
        {1: CG, 2: [TINY]}, {1: G}, Fraction(-1, 16), Fraction(-1, 8), 1
    )
    opposite = model._phase_correlated_proportional_derivative_certificate(
        {1: CG, 2: [TINY]}, {1: G}, Fraction(5, 16), Fraction(1, 8), 1
    )
    assert forward["status"] == reverse["status"] == opposite["status"] == "CERTIFIED"
    assert forward["direction"] == "INCREASING"
    assert reverse["direction"] == "DECREASING"
    assert opposite["phase_cell_certificate"]["k"] == 1
    assert opposite["phase_cell_certificate"]["diagonal_projection_sign_number"] == -1
    assert opposite["direction"] == "DECREASING"

    # Exact cell equality is admitted; signed rational neighbours test the
    # closed boundary without tolerance semantics.
    exact_cell = v34._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16))
    left_out = v34._diagonal_phase_cell_certificate(Fraction(-3, 16) - EPS, Fraction(-1, 16))
    left_in = v34._diagonal_phase_cell_certificate(Fraction(-3, 16) + EPS, Fraction(-1, 16))
    right_in = v34._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16) - EPS)
    right_out = v34._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16) + EPS)
    assert exact_cell["status"] == left_in["status"] == right_in["status"] == "CERTIFIED"
    assert left_out["status"] == right_out["status"] == "BLOCKED"

    # Exact proportionality phase-gap boundary P=0 and +/-1/1000000 neighbours.
    equal_gap = model._derive_proportional_common_factor([PHASE_GAP_BOUNDARY], [1])
    inside_gap = model._derive_proportional_common_factor([PHASE_GAP_BOUNDARY + EPS], [1])
    outside_gap = model._derive_proportional_common_factor([PHASE_GAP_BOUNDARY - EPS], [1])
    assert equal_gap["status"] == "BLOCKED", equal_gap
    assert equal_gap["phase_gap_P"] == "0", equal_gap
    assert inside_gap["status"] == "CERTIFIED", inside_gap
    assert outside_gap["status"] == "BLOCKED", outside_gap

    # Strict complete-margin equality fails closed. These +/- controls modify
    # source coefficients exactly; they are not theorem tolerances.
    residual_eq = Fraction(445779, 492128)
    equal = model._phase_correlated_proportional_orthant_certificate(
        {0: [0, residual_eq], 1: [LAMBDA]}, {1: [1]}, Fraction(1, 8), 1
    )
    inside = model._phase_correlated_proportional_orthant_certificate(
        {0: [0, residual_eq - EPS], 1: [LAMBDA]}, {1: [1]}, Fraction(1, 8), 1
    )
    outside = model._phase_correlated_proportional_orthant_certificate(
        {0: [0, residual_eq + EPS], 1: [LAMBDA]}, {1: [1]}, Fraction(1, 8), 1
    )
    assert equal["status"] == "BLOCKED", equal
    assert inside["status"] == "CERTIFIED", inside
    assert outside["status"] == "BLOCKED", outside

    # Preserved endpoint/root authority: v35 itself proves open/zero-root cases,
    # while exact historical v34 endpoint-root cases retain unchanged precedence.
    open_route = model._phase_correlated_proportional_route(
        {1: CG, 2: [TINY]}, {1: G}, Fraction(-3, 16), Fraction(1, 8), "s"
    )
    no_root = model._phase_correlated_proportional_route(
        {0: [10], 1: CG, 2: [TINY]}, {1: G}, Fraction(-3, 16), Fraction(1, 8), "s"
    )
    assert open_route["status"] == "CERTIFIED" and open_route["distinct_roots_open"] == 1
    assert no_root["status"] == "CERTIFIED" and no_root["total_distinct_roots_closed"] == 0

    left_spec = v34test._spec({1: [1], 2: [TINY]}, {1: [1]}, offset="-1/8", rate="1/16")
    right_spec = v34test._spec({1: [1], 2: [TINY]}, {1: [1]}, offset="-3/16", rate="1/16")
    left_old = v34.classify_required_analytic_event(left_spec)
    right_old = v34.classify_required_analytic_event(right_spec)
    left_new = model.classify_required_analytic_event(left_spec)
    right_new = model.classify_required_analytic_event(right_spec)
    assert left_new == left_old and right_new == right_old
    left_route = v34test._v34_route(left_new)
    right_route = v34test._v34_route(right_new)
    assert left_route["left_endpoint_root"] is True and left_route["endpoint_root_multiplicity"] == {"left": 1}
    assert right_route["right_endpoint_root"] is True and right_route["endpoint_root_multiplicity"] == {"right": 1}

    # Structural and source-ownership boundaries fail closed.
    perturbed = list(CG)
    perturbed[-1] += EPS
    nonproportional = model._phase_correlated_proportional_derivative_certificate(
        {1: perturbed}, {1: G}, Fraction(-3, 16), Fraction(1, 8), 1
    )
    nonconstant_ratio = model._phase_correlated_proportional_derivative_certificate(
        {1: [1, 1]}, {1: [1, 2]}, Fraction(-3, 16), Fraction(1, 8), 1
    )
    sign_changing = model._phase_correlated_proportional_derivative_certificate(
        {1: [LAMBDA, -2 * LAMBDA]}, {1: [1, -2]}, Fraction(-3, 16), Fraction(1, 8), 1
    )
    zero_g = model._phase_correlated_proportional_derivative_certificate(
        {1: [LAMBDA]}, {1: [0]}, Fraction(-3, 16), Fraction(1, 8), 1
    )
    unsupported = model._phase_correlated_proportional_derivative_certificate(
        {1: [LAMBDA]}, {1: [1]}, Fraction(0), Fraction(1, 16), 1
    )
    a_nonpositive = model._phase_correlated_proportional_derivative_certificate(
        {1: [-2]}, {1: [1]}, Fraction(-3, 16), Fraction(1, 8), 1
    )
    assert nonproportional["status"] == "BLOCKED"
    assert nonconstant_ratio["status"] == "BLOCKED"
    assert sign_changing["status"] == "BLOCKED"
    assert zero_g["status"] == "BLOCKED"
    assert unsupported["status"] == "BLOCKED"
    assert a_nonpositive["status"] == "BLOCKED"

    # Forged caller lambda/common-factor/cell/bound/margin/root metadata is
    # stripped; source coefficients regenerate identical authority.
    forged = copy.deepcopy(source)
    forged.update({
        "lambda": "999",
        "proportionality_scalar": "999",
        "common_factor": ["999"],
        "common_factor_certificate": {"status": "CERTIFIED"},
        "A": "999",
        "B": "0",
        "phase_gap_P": "999",
        "joint_amplitude_upper_Q": "0",
        "diagonal_phase_cell": ["0", "1"],
        "diagonal_phase_cell_certificate": {"status": "CERTIFIED"},
        "sqrt2_cos_lower": "999",
        "sqrt2_sin_upper": "0",
        "joint_margin": "999",
        "joint_margin_certificate": {"status": "CERTIFIED"},
        "root_count": 0,
        "multiplicity_certificate": 99,
    })
    forged_result = model.classify_required_analytic_event(forged)
    forged_route = _v35_route(forged_result)
    assert forged_result["status"] == result["status"]
    assert forged_route["phase_correlated_proportional_common_factor_certificate"] == anchor

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "independent-u"
    assert _rejected(mismatch)
    floating = copy.deepcopy(source)
    floating["phase_turn_rate"] = 0.125
    assert _rejected(floating)

    # Exact resource refusal remains terminal non-truth.
    saved = model._phase_correlated_proportional_route
    try:
        model._phase_correlated_proportional_route = lambda *args, **kwargs: model.resource_refusal()
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL", refused
    finally:
        model._phase_correlated_proportional_route = saved
    assert model.resource_refusal()["is_truth_value"] is False

    # Historical v30 and v34 successes retain exact precedence.
    historical_v30_spec = v30test._fixture()
    historical_v30 = v30.classify_required_analytic_event(historical_v30_spec)
    assert historical_v30["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(historical_v30_spec) == historical_v30

    historical_v34_spec = v34test._fixture()
    historical_v34 = v34.classify_required_analytic_event(historical_v34_spec)
    assert historical_v34["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(historical_v34_spec) == historical_v34

    assert model.V35_ROUTE.startswith("EXACT_")
    print("PB-007-01 v35 phase-correlated proportional common-factor adversarial tests passed")


if __name__ == "__main__":
    run()
