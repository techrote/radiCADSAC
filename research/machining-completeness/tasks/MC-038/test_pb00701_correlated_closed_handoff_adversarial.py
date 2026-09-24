#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_correlated_closed_handoff_model as model  # noqa: E402
import pb00701_orientation_transition_bridge_model as v42  # noqa: E402
import test_pb00701_multiharmonic_monotone_anchor_adversarial as base_test  # noqa: E402
import test_pb00701_orientation_transition_bridge_adversarial as v42test  # noqa: E402

v27 = model.v27
TINY = Fraction(1, 100000000)
EPS = Fraction(1, 1000000)

A1 = [Fraction(-1, 8), Fraction(1, 2)]
B1 = [Fraction(-7, 40), Fraction(7, 20)]
C1 = [Fraction(-3, 10), Fraction(17, 20)]
S1 = [Fraction(1, 20), Fraction(3, 20)]
OFFSET = Fraction(-1, 8)
RATE = Fraction(1, 16)
HANDOFF = Fraction(1, 4)


def _spec(*, offset=OFFSET, rate=RATE, **extra):
    return base_test._spec(
        {1: C1, 2: [TINY]},
        {1: S1},
        offset=str(offset),
        rate=str(rate),
        **extra,
    )


def _v43_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"]
        for span in result.get("spans", [])
        if span.get("route_kind") == "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"
    ]
    assert routes, result
    assert routes[0]["status"] == "CERTIFIED", routes[0]
    return routes[0]


def _maps():
    return {1: C1, 2: [TINY]}, {1: S1}


def run_acceptance():
    source = _spec()

    predecessor = v42.classify_required_analytic_event(source)
    assert predecessor["status"] != "CERTIFIED", predecessor

    # V43 by itself must not relabel the parent: A crosses zero in the open
    # parent span, so the exact weak-sign premise is unavailable.
    direct = model.classify_required_analytic_event(source)
    assert direct["status"] != "CERTIFIED", direct

    cos_polys, sin_polys = _maps()
    source_id = source["source_parameter_id"]

    left_spec, left_cos, left_sin = v27._child_spec(
        cos_polys, sin_polys, OFFSET, RATE,
        Fraction(0), HANDOFF, source_id,
    )
    right_spec, right_cos, right_sin = v27._child_spec(
        cos_polys, sin_polys, OFFSET, RATE,
        HANDOFF, Fraction(1), source_id,
    )

    left_predecessor = v42.classify_required_analytic_event(left_spec)
    assert left_predecessor["status"] == "CERTIFIED", left_predecessor

    right_predecessor = v42.classify_required_analytic_event(right_spec)
    assert right_predecessor["status"] != "CERTIFIED", right_predecessor

    right_v43 = model.classify_required_analytic_event(right_spec)
    route = _v43_route(right_v43)
    cert = route["correlated_closed_handoff_certificate"]
    joint = cert["correlated_handoff_residual_certificate"]

    assert cert["direction"] == "INCREASING"
    assert cert["proof_cut_is_physical_event"] is False
    assert joint["eta"] == 1
    assert joint["sigma_A_weak"] == 1
    assert joint["A_weak_sign_certificate"]["left_event"]["relation"] == "ZERO"
    assert joint["A_weak_sign_certificate"]["right_event"]["relation"] == "POSITIVE"
    assert joint["selected_amplitude_derivatives_consumed_jointly"] is True
    assert joint["selected_phase_terms_consumed_jointly"] is True
    assert any(
        item["harmonic"] == 2 and item["kind"] == "phase_C"
        for item in joint["retained_residual_terms"]
    )

    left_summary = v27._single_span_child_summary(
        left_predecessor, left_cos, left_sin,
        OFFSET, RATE * HANDOFF,
    )
    right_offset = OFFSET + RATE * HANDOFF
    right_rate = RATE * (Fraction(1) - HANDOFF)
    right_summary = v27._single_span_child_summary(
        right_v43, right_cos, right_sin,
        right_offset, right_rate,
    )
    assert left_summary["status"] == right_summary["status"] == "CERTIFIED"

    children = [
        {
            "parent_local_interval": ["0", str(HANDOFF)],
            "summary": left_summary,
        },
        {
            "parent_local_interval": [str(HANDOFF), "1"],
            "summary": right_summary,
        },
    ]
    composition = v27._compose_child_summaries(children)
    assert composition["status"] == "CERTIFIED", composition
    assert composition["internal_cut_roots"] == []
    assert composition["internal_cut_root_counted_once"] is True

    print(
        "PB-007-01 v43 acceptance: predecessor parent BLOCKED; "
        "left predecessor child CERTIFIED; right v43 child CERTIFIED; "
        "exact v27 composition CERTIFIED"
    )
    return source, right_v43, composition


def _right_child_material():
    source = _spec()
    cos_polys, sin_polys = _maps()
    source_id = source["source_parameter_id"]
    return v27._child_spec(
        cos_polys, sin_polys, OFFSET, RATE,
        HANDOFF, Fraction(1), source_id,
    )


def _margin_source(m):
    # A=s, B=m*s. At s=0 the adverse transverse phase-B term vanishes,
    # so the critical v43 orthant is exactly L*m-U. m=U/L is equality.
    a = [Fraction(0), Fraction(1)]
    b = [Fraction(0), m]
    c = model._trim(model.v22._padd(a, b))
    sin = model._trim(model.v22._padd(a, model.v22._pscale(b, -1)))
    return {1: c}, {1: sin}


def run_margin_boundary_controls():
    equality = model.X_UPPER / model.Y_LOWER
    inside = equality + EPS
    outside = equality - EPS
    rate = Fraction(1, 1000000)

    equal_cert = model._correlated_orthant_certificate(
        *_margin_source(equality), rate, 1, 1
    )
    inside_cert = model._correlated_orthant_certificate(
        *_margin_source(inside), rate, 1, 1
    )
    outside_cert = model._correlated_orthant_certificate(
        *_margin_source(outside), rate, 1, 1
    )
    assert equal_cert["status"] == "BLOCKED", equal_cert
    assert Fraction(equal_cert["failed_margin_polynomial"][0]) == 0
    assert inside_cert["status"] == "CERTIFIED", inside_cert
    assert outside_cert["status"] == "BLOCKED", outside_cert


def run_phase_boundary_controls():
    cos_polys, sin_polys = _margin_source(Fraction(10))
    tiny_rate = Fraction(1, 1000000)
    exact_left = model._correlated_derivative_certificate(
        cos_polys, sin_polys, Fraction(-3, 16), tiny_rate, 1
    )
    just_left = model._correlated_derivative_certificate(
        cos_polys, sin_polys, Fraction(-3, 16) - EPS, tiny_rate, 1
    )
    exact_right = model._correlated_derivative_certificate(
        cos_polys, sin_polys, Fraction(-1, 16) - tiny_rate, tiny_rate, 1
    )
    just_right = model._correlated_derivative_certificate(
        cos_polys, sin_polys, Fraction(-1, 16) - tiny_rate + EPS, tiny_rate, 1
    )
    assert exact_left["status"] == exact_right["status"] == "CERTIFIED"
    assert just_left["status"] == just_right["status"] == "BLOCKED"


def _reverse_polynomial(poly):
    poly = [Fraction(x) for x in poly]
    out = [Fraction(0)] * len(poly)
    for i, coefficient in enumerate(poly):
        for j in range(i + 1):
            out[j] += coefficient * Fraction(comb(i, j)) * ((-1) ** j)
    return model._trim(out)


def run_reverse_direction():
    right_spec, right_cos, right_sin = _right_child_material()
    right_offset = OFFSET + RATE * HANDOFF
    right_rate = RATE * (Fraction(1) - HANDOFF)
    reverse_cos = {h: _reverse_polynomial(poly) for h, poly in right_cos.items()}
    reverse_sin = {h: _reverse_polynomial(poly) for h, poly in right_sin.items()}
    reverse = base_test._spec(
        reverse_cos,
        reverse_sin,
        offset=str(right_offset + right_rate),
        rate=str(-right_rate),
        source_parameter_id=right_spec["source_parameter_id"],
    )
    predecessor = v42.classify_required_analytic_event(reverse)
    assert predecessor["status"] != "CERTIFIED", predecessor
    result = model.classify_required_analytic_event(reverse)
    route = _v43_route(result)
    assert route["correlated_closed_handoff_certificate"]["direction"] == "DECREASING"


def run_resource_refusal_control():
    _, right_cos, right_sin = _right_child_material()
    right_rate = RATE * (Fraction(1) - HANDOFF)
    saved = model._strict_positive
    try:
        model._strict_positive = lambda *args, **kwargs: {
            "status": "RESOURCE_REFUSAL",
            "reason": "TEST_RESOURCE_REFUSAL",
            "is_truth_value": False,
        }
        refused = model._correlated_orthant_certificate(
            right_cos, right_sin, right_rate, 1, 1
        )
        assert refused["status"] == "RESOURCE_REFUSAL"
        assert refused["is_truth_value"] is False
    finally:
        model._strict_positive = saved


def run_composition_neutrality():
    source, _, composition = run_acceptance()
    assert composition["internal_cut_roots"] == []

    # The handoff is a proof cut, not a physical event.
    cos_polys, sin_polys = _maps()
    event = model.v19._endpoint_relation(
        cos_polys, sin_polys, HANDOFF, OFFSET + RATE * HANDOFF
    )
    assert event["relation"] != "ZERO", (source, event)

    # Conversely, a genuine matching physical root is counted exactly once.
    neutral = [
        {
            "parent_local_interval": ["0", "1/2"],
            "summary": {
                "status": "CERTIFIED",
                "right_event": {"relation": "ZERO"},
                "left_event": {"relation": "POSITIVE"},
                "right_endpoint_multiplicity": 1,
                "left_endpoint_multiplicity": None,
                "distinct_roots_open": 0,
                "multiple_roots_open": 0,
                "all_roots_simple": True,
            },
        },
        {
            "parent_local_interval": ["1/2", "1"],
            "summary": {
                "status": "CERTIFIED",
                "left_event": {"relation": "ZERO"},
                "right_event": {"relation": "POSITIVE"},
                "right_endpoint_multiplicity": None,
                "left_endpoint_multiplicity": 1,
                "distinct_roots_open": 0,
                "multiple_roots_open": 0,
                "all_roots_simple": True,
            },
        },
    ]
    composed = v27._compose_child_summaries(neutral)
    assert composed["status"] == "CERTIFIED"
    assert len(composed["internal_cut_roots"]) == 1
    assert composed["distinct_roots_open"] == 1


def run_precedence():
    prior = v42test._fixture()
    assert model.classify_required_analytic_event(prior) == v42.classify_required_analytic_event(prior)


def run_weak_sign_controls():
    positive = model._closed_weak_sign([0, 1], "TEST_POSITIVE")
    negative = model._closed_weak_sign([0, -1], "TEST_NEGATIVE")
    crossing = model._closed_weak_sign([Fraction(-1, 2), 1], "TEST_CROSSING")
    near_inside = model._closed_weak_sign([EPS, 1], "TEST_NEAR_INSIDE")
    near_cross = model._closed_weak_sign([-EPS, 1], "TEST_NEAR_CROSS")
    zero = model._closed_weak_sign([0], "TEST_ZERO", allow_zero=True)
    assert positive["status"] == negative["status"] == near_inside["status"] == zero["status"] == "CERTIFIED"
    assert positive["sign_number"] == near_inside["sign_number"] == 1
    assert negative["sign_number"] == -1
    assert zero["sign_number"] == 0
    assert crossing["status"] == near_cross["status"] == "BLOCKED"
    assert "INTERIOR_ROOT" in crossing["reason"] and "INTERIOR_ROOT" in near_cross["reason"]


def run_incompatibility_regression():
    L, W = model.Y_LOWER, model.Y_UPPER
    difference = Fraction(44, 7) * W * W - Fraction(6) * L * L
    assert difference == Fraction(100719037899, 41389887175)
    assert difference > 0
    assert L < 2


def run_adversarial():
    source, result, _ = run_acceptance()

    forged = copy.deepcopy(source)
    forged.update({
        "A": [999],
        "B": [999],
        "eta": -1,
        "orientation": -1,
        "weak_sign_certificate": {"status": "CERTIFIED"},
        "correlated_margin": "999",
        "correlated_margin_certificate": {"status": "CERTIFIED"},
        "root_count": 0,
        "multiplicity_certificate": 99,
    })
    assert model.classify_required_analytic_event(forged) == model.classify_required_analytic_event(source)

    floating = copy.deepcopy(source)
    floating["phase_turn_rate"] = 0.125
    try:
        floating_result = model.classify_required_analytic_event(floating)
    except (AssertionError, ValueError, TypeError):
        floating_result = {"status": "REJECTED"}
    assert floating_result.get("status") != "CERTIFIED"

    assert model.resource_refusal()["is_truth_value"] is False


def run():
    run_weak_sign_controls()
    run_margin_boundary_controls()
    run_phase_boundary_controls()
    run_reverse_direction()
    run_resource_refusal_control()
    run_incompatibility_regression()
    run_precedence()
    run_composition_neutrality()
    run_adversarial()


if __name__ == "__main__":
    run()
