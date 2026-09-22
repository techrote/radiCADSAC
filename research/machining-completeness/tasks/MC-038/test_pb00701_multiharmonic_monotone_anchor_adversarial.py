#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_multiharmonic_monotone_anchor_model as model  # noqa: E402
import pb00701_source_laurent_factor_model as v18  # noqa: E402
import test_pb00701_source_laurent_factor_adversarial as v18test  # noqa: E402


def _trim(poly):
    out = [Fraction(value) for value in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [Fraction(0)]


def _power_spline(poly):
    poly = _trim(poly)
    degree = len(poly) - 1
    if degree == 0:
        return {"degree": 0, "knots": ["0", "1"], "controls": [str(poly[0])]}
    controls = []
    for j in range(degree + 1):
        value = Fraction(0)
        for k in range(j + 1):
            if k < len(poly):
                value += poly[k] * Fraction(comb(j, k), comb(degree, k))
        controls.append(str(value))
    return {
        "degree": degree,
        "knots": ["0"] * (degree + 1) + ["1"] * (degree + 1),
        "controls": controls,
    }


def _spec(cos_polys, sin_polys, *, offset="0", rate="1/4", **extra):
    value = {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": {
            str(h): _power_spline(poly)
            for h, poly in sorted(cos_polys.items()) if _trim(poly) != [0]
        },
        "sin_splines": {
            str(h): _power_spline(poly)
            for h, poly in sorted(sin_polys.items()) if _trim(poly) != [0]
        },
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": offset,
        "phase_turn_rate": rate,
        "source_parameter_id": "source-time-t",
    }
    value.update(extra)
    return value


def _fixture(anchor, *, rate="1/4", c1=None, s2=None):
    return _spec(
        {0: anchor, 1: [Fraction(1, 100)] if c1 is None else c1},
        {2: [Fraction(1, 200)] if s2 is None else s2},
        rate=rate,
    )


def _v19_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span.get("route_kind") == "PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR"
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
    # New direct multi-harmonic coverage. The nonconstant h=0 anchor makes the
    # source genuinely outside constant-modulation v6; h=1 and h=2 are both
    # active. v18 cannot remove a qualifying nonvanishing factor, but v19 proves
    # F'>0 exactly and then decides the endpoint signs exactly.
    source = _fixture([Fraction(-1, 2), 1])
    old = v18.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    route = _v19_route(model.classify_required_analytic_event(source))
    assert route["relation"] == model.V19_ROUTE
    assert route["active_positive_harmonics"] == [1, 2]
    assert route["derivative_certificate"]["direction"] == "INCREASING"
    assert Fraction(route["derivative_certificate"]["strict_margin"]) > 0
    assert route["derivative_certificate"]["pi_upper_theorem"] == "pi < 22/7"
    assert route["left_event"]["relation"] == "NEGATIVE"
    assert route["right_event"]["relation"] == "POSITIVE"
    assert route["distinct_roots_open"] == 1
    assert route["total_distinct_roots_closed"] == 1
    assert route["all_roots_simple"] is True

    decreasing = _v19_route(model.classify_required_analytic_event(_fixture([Fraction(1, 2), -1])))
    assert decreasing["derivative_certificate"]["direction"] == "DECREASING"
    assert decreasing["left_event"]["relation"] == "POSITIVE"
    assert decreasing["right_event"]["relation"] == "NEGATIVE"
    assert decreasing["distinct_roots_open"] == 1

    no_root = _v19_route(model.classify_required_analytic_event(_fixture([Fraction(1, 4), 1])))
    assert no_root["left_event"]["relation"] == "POSITIVE"
    assert no_root["right_event"]["relation"] == "POSITIVE"
    assert no_root["total_distinct_roots_closed"] == 0

    left_root = _v19_route(model.classify_required_analytic_event(_fixture([Fraction(-1, 100), 1])))
    assert left_root["left_event"]["relation"] == "ZERO"
    assert left_root["left_endpoint_root"] is True
    assert left_root["endpoint_root_multiplicity"] == {"left": 1}
    assert left_root["distinct_roots_open"] == 0

    right_root = _v19_route(model.classify_required_analytic_event(_fixture([-1, 1])))
    assert right_root["right_event"]["relation"] == "ZERO"
    assert right_root["right_endpoint_root"] is True
    assert right_root["endpoint_root_multiplicity"] == {"right": 1}
    assert right_root["distinct_roots_open"] == 0

    # A right source endpoint at exactly half a turn is a tangent-half pole for
    # v6's projective coordinate. v19 must use the exact parity shift instead of
    # approximation or epsilon displacement.
    half_turn = _v19_route(model.classify_required_analytic_event(
        _fixture([Fraction(-1, 2), 1], rate="1/2")
    ))
    assert half_turn["right_event"]["original_turn"] == "1/2"
    assert half_turn["right_event"]["evaluation_turn"] == "0"
    assert half_turn["right_event"]["half_turn_parity_shift"] is True
    assert half_turn["right_event"]["relation"] == "POSITIVE"

    # Positive-harmonic modulation need not be constant. Its exact source
    # derivative is included in the Bernstein derivative budget.
    varying = _v19_route(model.classify_required_analytic_event(
        _fixture([Fraction(-1, 2), 1], c1=[0, Fraction(1, 100)])
    ))
    term1 = next(item for item in varying["derivative_certificate"]["terms"] if item["harmonic"] == 1)
    assert Fraction(term1["C_prime_bernstein_abs_bound"]) == Fraction(1, 100)
    assert varying["distinct_roots_open"] == 1

    # Exact strict-dominance threshold. With P'=1, C_1=1 and no other term,
    # the rational 44/7 upper bound is exactly one at r=7/44. Equality is not
    # accepted; signed +/-1/1000000 neighbours discriminate exactly.
    eps = Fraction(1, 1000000)
    equality = model._derivative_dominance_certificate({0: [0, 1], 1: [1]}, {}, Fraction(7, 44))
    below = model._derivative_dominance_certificate({0: [0, 1], 1: [1]}, {}, Fraction(7, 44) - eps)
    above = model._derivative_dominance_certificate({0: [0, 1], 1: [1]}, {}, Fraction(7, 44) + eps)
    assert equality["status"] == "BLOCKED"
    assert equality["oscillatory_derivative_bound"] == "1"
    assert below["status"] == "CERTIFIED" and below["direction"] == "INCREASING"
    assert Fraction(below["strict_margin"]) > 0
    assert above["status"] == "BLOCKED"
    negative = model._derivative_dominance_certificate({0: [0, -1], 1: [1]}, {}, Fraction(7, 44) - eps)
    assert negative["status"] == "CERTIFIED" and negative["direction"] == "DECREASING"

    # Structural and dominance boundaries remain fail-closed.
    assert model._monotone_anchor_route({1: [1], 2: [1]}, {}, 0, Fraction(1, 4), "s") is None
    assert model._monotone_anchor_route({0: [1], 1: [1], 2: [1]}, {}, 0, Fraction(1, 4), "s") is None
    assert model._monotone_anchor_route({0: [0, 1], 1: [1]}, {}, 0, Fraction(1, 4), "s") is None
    insufficient = model._monotone_anchor_route(
        {0: [0, 1], 1: [1], 2: [1]}, {}, 0, Fraction(1, 4), "s"
    )
    assert insufficient["status"] == "BLOCKED"
    assert insufficient["reason"] == "MONOTONE_ANCHOR_DERIVATIVE_DOMINANCE_NOT_CERTIFIED"

    # Historical precedence: a v18-owned source stays v18-owned and is not
    # relabelled merely because the v19 wrapper is present.
    prior_spec = v18test._source_factor_fixture([2, 1])
    prior = model.classify_required_analytic_event(prior_spec)
    assert prior["status"] == "CERTIFIED"
    assert not prior.get("v19_multiharmonic_monotone_anchor_extension", False)

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "different-source-coordinate"
    mismatch_result = model.classify_required_analytic_event(mismatch)
    assert mismatch_result["status"] == "SEMANTIC_BLOCKER"

    # Caller proof claims are stripped before source analysis and cannot alter
    # the exact source-derived certificate.
    forged = copy.deepcopy(source)
    forged.update({
        "anchor_derivative": ["999"],
        "bernstein_certificate": {"status": "CERTIFIED"},
        "derivative_bound": "0",
        "monotonicity": "DECREASING",
        "endpoint_signs": ["POSITIVE", "NEGATIVE"],
        "root_count": 99,
        "pi_upper_bound": "3",
        "strict_margin": "999",
    })
    forged_route = _v19_route(model.classify_required_analytic_event(forged))
    assert forged_route["derivative_certificate"] == route["derivative_certificate"]
    assert forged_route["distinct_roots_open"] == route["distinct_roots_open"]
    assert forged_route["caller_certificate_trusted"] is False

    floating = copy.deepcopy(source)
    floating["cos_splines"]["0"]["controls"][0] = 0.5
    assert _rejected(floating)

    # Exact endpoint isolation refusal remains a non-truth terminal status.
    original_endpoint = model.v6.rational_turn_endpoint
    try:
        def refuse(*_args, **_kwargs):
            raise model.v6.EndpointIsolationRefusal("adversarial endpoint isolation refusal")
        model.v6.rational_turn_endpoint = refuse
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL", refused
        refused_routes = [span["route"] for span in refused["spans"]]
        assert any(item.get("is_truth_value") is False for item in refused_routes)
    finally:
        model.v6.rational_turn_endpoint = original_endpoint

    assert model.resource_refusal()["is_truth_value"] is False
    print("PB-007-01 v19 multi-harmonic monotone-anchor adversarial controls: PASS")


if __name__ == "__main__":
    run()
