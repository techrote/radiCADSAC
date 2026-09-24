#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_correlated_closed_handoff_model as model  # noqa: E402
import pb00701_orientation_transition_bridge_model as v42  # noqa: E402
import test_pb00701_multiharmonic_monotone_anchor_adversarial as base_test  # noqa: E402

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


def run_weak_sign_controls():
    positive = model._closed_weak_sign([0, 1], "TEST_POSITIVE")
    negative = model._closed_weak_sign([0, -1], "TEST_NEGATIVE")
    crossing = model._closed_weak_sign([Fraction(-1, 2), 1], "TEST_CROSSING")
    zero = model._closed_weak_sign([0], "TEST_ZERO", allow_zero=True)
    assert positive["status"] == negative["status"] == zero["status"] == "CERTIFIED"
    assert positive["sign_number"] == 1 and negative["sign_number"] == -1
    assert zero["sign_number"] == 0
    assert crossing["status"] == "BLOCKED"
    assert "INTERIOR_ROOT" in crossing["reason"]


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
    run_incompatibility_regression()
    run_adversarial()


if __name__ == "__main__":
    run()
