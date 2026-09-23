#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_phase_correlated_common_factor_model as model  # noqa: E402
import pb00701_source_adaptive_separator_model as v30  # noqa: E402
import test_pb00701_source_adaptive_separator_adversarial as v30test  # noqa: E402
import test_pb00701_multiharmonic_monotone_anchor_adversarial as v19test  # noqa: E402

G = [Fraction(1), Fraction(3, 2), Fraction(9, 16)]
TINY = Fraction(1, 100000000)
EPS = Fraction(1, 1000000)


def _spec(cos_polys, sin_polys=None, *, offset="-3/16", rate="1/8", **extra):
    return v19test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(*, offset="-3/16", rate="1/8", p0=Fraction(0)):
    # G=(1+3s/4)^2.  C1=S1=G is a source-owned exact common factor.
    # A nonzero h=2 COS term forces the non-anchor phase residual to remain live.
    return _spec(
        {0: [p0], 1: G, 2: [TINY]},
        {1: G},
        offset=offset,
        rate=rate,
    )


def _v34_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result.get("spans", [])
        if span.get("route_kind") == "PB00701_V34_EXACT_PHASE_CORRELATED_COMMON_FACTOR"
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
    # Primary acceptance: the exact source requested by #231 is genuinely beyond
    # complete v8-v30 authority, yet the phase-correlated v34 route certifies it.
    source = _fixture()
    old = v30.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    global_v30 = v30._source_adaptive_separator_certificate(G, G, "SIN", "COS")
    assert global_v30["status"] == "BLOCKED", global_v30
    assert global_v30["source_projective_ceiling"] == "16/49", global_v30

    result = model.classify_required_analytic_event(source)
    route = _v34_route(result)
    assert route["relation"] == model.V34_ROUTE
    anchor = route["phase_correlated_common_factor_certificate"]
    joint = anchor["phase_correlated_residual_certificate"]
    cell = anchor["phase_cell_certificate"]
    assert anchor["direction"] == "INCREASING"
    assert cell["cell"] == ["-3/16", "-1/16"]
    assert cell["k"] == 0
    assert cell["sqrt2_cos_lower"] == "2856/2197"
    assert cell["sqrt2_sin_abs_upper"] == "99/182"
    assert joint["common_factor_polynomial"] == ["1", "3/2", "9/16"]
    assert joint["common_factor_derivative"] == ["3/2", "9/8"]
    assert joint["selected_amplitude_derivatives_consumed_jointly"] is True
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

    # Positive/negative rate and opposite diagonal cells reverse only the exact
    # expected projection sign; no sampled trigonometric sign is consulted.
    forward = model._phase_correlated_derivative_certificate(
        {1: G, 2: [TINY]}, {1: G}, Fraction(-3, 16), Fraction(1, 8), 1
    )
    reverse = model._phase_correlated_derivative_certificate(
        {1: G, 2: [TINY]}, {1: G}, Fraction(-1, 16), Fraction(-1, 8), 1
    )
    opposite = model._phase_correlated_derivative_certificate(
        {1: G, 2: [TINY]}, {1: G}, Fraction(5, 16), Fraction(1, 8), 1
    )
    assert forward["status"] == reverse["status"] == opposite["status"] == "CERTIFIED"
    assert forward["direction"] == "INCREASING"
    assert reverse["direction"] == "DECREASING"
    assert opposite["phase_cell_certificate"]["k"] == 1
    assert opposite["phase_cell_certificate"]["diagonal_projection_sign_number"] == -1
    assert opposite["direction"] == "DECREASING"

    # Exact cell equality is admitted. Signed rational neighbours distinguish
    # the closed containment boundary without epsilon/tolerance semantics.
    exact_cell = model._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16))
    left_out = model._diagonal_phase_cell_certificate(Fraction(-3, 16) - EPS, Fraction(-1, 16))
    left_in = model._diagonal_phase_cell_certificate(Fraction(-3, 16) + EPS, Fraction(-1, 16))
    right_in = model._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16) - EPS)
    right_out = model._diagonal_phase_cell_certificate(Fraction(-3, 16), Fraction(-1, 16) + EPS)
    assert exact_cell["status"] == left_in["status"] == right_in["status"] == "CERTIFIED"
    assert left_out["status"] == right_out["status"] == "BLOCKED"

    # Strict joint-margin equality fails closed. The +/-1/1000000 controls are
    # exact source coefficients, not tolerances used by the theorem.
    residual_eq = Fraction(2142, 2197)  # 6*(1/8)*(2856/2197)
    equal = model._phase_correlated_orthant_certificate(
        {0: [0, residual_eq], 1: [1]}, {1: [1]}, Fraction(1, 8), 1
    )
    inside = model._phase_correlated_orthant_certificate(
        {0: [0, residual_eq - EPS], 1: [1]}, {1: [1]}, Fraction(1, 8), 1
    )
    outside = model._phase_correlated_orthant_certificate(
        {0: [0, residual_eq + EPS], 1: [1]}, {1: [1]}, Fraction(1, 8), 1
    )
    assert equal["status"] == "BLOCKED", equal
    assert inside["status"] == "CERTIFIED", inside
    assert outside["status"] == "BLOCKED", outside

    # Preserved endpoint/root authority: zero/open/left/right outcomes. Constant
    # G is used for the endpoint controls so the exact joint amplitude term is 0.
    open_route = model._phase_correlated_route(
        {1: G, 2: [TINY]}, {1: G}, Fraction(-3, 16), Fraction(1, 8), "s"
    )
    no_root = model._phase_correlated_route(
        {0: [10], 1: G, 2: [TINY]}, {1: G}, Fraction(-3, 16), Fraction(1, 8), "s"
    )
    left_root = model._phase_correlated_route(
        {1: [1], 2: [TINY]}, {1: [1]}, Fraction(-1, 8), Fraction(1, 16), "s"
    )
    right_root = model._phase_correlated_route(
        {1: [1], 2: [TINY]}, {1: [1]}, Fraction(-3, 16), Fraction(1, 16), "s"
    )
    assert open_route["status"] == "CERTIFIED" and open_route["distinct_roots_open"] == 1
    assert no_root["status"] == "CERTIFIED" and no_root["total_distinct_roots_closed"] == 0
    assert left_root["status"] == "CERTIFIED", left_root
    assert left_root["left_event"]["relation"] == "ZERO" and left_root["left_endpoint_root"] is True
    assert left_root["endpoint_root_multiplicity"] == {"left": 1}
    assert right_root["status"] == "CERTIFIED", right_root
    assert right_root["right_event"]["relation"] == "ZERO" and right_root["right_endpoint_root"] is True
    assert right_root["endpoint_root_multiplicity"] == {"right": 1}

    # Structural boundaries fail closed.
    unequal = model._phase_correlated_derivative_certificate(
        {1: G}, {1: [1, Fraction(3, 2), Fraction(9, 16) + EPS]},
        Fraction(-3, 16), Fraction(1, 8), 1,
    )
    sign_changing = model._phase_correlated_derivative_certificate(
        {1: [-1, 2]}, {1: [-1, 2]}, Fraction(-3, 16), Fraction(1, 8), 1
    )
    zero_g = model._phase_correlated_derivative_certificate(
        {1: [0]}, {1: [0]}, Fraction(-3, 16), Fraction(1, 8), 1
    )
    unsupported = model._phase_correlated_derivative_certificate(
        {1: [1]}, {1: [1]}, Fraction(0), Fraction(1, 16), 1
    )
    assert unequal["status"] == "BLOCKED"
    assert sign_changing["status"] == "BLOCKED"
    assert zero_g["status"] == "BLOCKED"
    assert unsupported["status"] == "BLOCKED"

    # Forged caller common-factor/cell/bound/margin/root metadata is stripped;
    # source coefficients alone reproduce the same authority.
    forged = copy.deepcopy(source)
    forged.update({
        "common_factor": ["999"],
        "common_factor_certificate": {"status": "CERTIFIED"},
        "common_factor_sign": -1,
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
    forged_route = _v34_route(forged_result)
    assert forged_result["status"] == result["status"]
    assert forged_route["phase_correlated_common_factor_certificate"] == anchor

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "independent-u"
    assert _rejected(mismatch)
    floating = copy.deepcopy(source)
    floating["phase_turn_rate"] = 0.125
    assert _rejected(floating)

    # Exact resource refusal is terminal non-truth.
    saved = model._phase_correlated_route
    try:
        model._phase_correlated_route = lambda *args, **kwargs: model.resource_refusal()
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL", refused
    finally:
        model._phase_correlated_route = saved
    assert model.resource_refusal()["is_truth_value"] is False

    # Complete executable v8-v30 precedence is exact: a historical v30 success
    # is returned unchanged rather than being relabelled as v34.
    historical = v30test._fixture()
    historical_v30 = v30.classify_required_analytic_event(historical)
    assert historical_v30["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(historical) == historical_v30

    assert model.V34_ROUTE.startswith("EXACT_")
    print("PB-007-01 v34 phase-correlated common-factor adversarial tests passed")


if __name__ == "__main__":
    run()
