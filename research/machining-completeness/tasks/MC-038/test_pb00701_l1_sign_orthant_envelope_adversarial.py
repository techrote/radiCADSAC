#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_l1_sign_orthant_envelope_model as model  # noqa: E402
import pb00701_pointwise_derivative_envelope_model as v20  # noqa: E402
import pb00701_multiharmonic_monotone_anchor_model as v19  # noqa: E402
import test_pb00701_multiharmonic_monotone_anchor_adversarial as v19test  # noqa: E402
import test_pb00701_pointwise_derivative_envelope_adversarial as v20test  # noqa: E402


def _spec(cos_polys, sin_polys=None, *, offset="0", rate="1/100", **extra):
    return v19test._spec(cos_polys, {} if sin_polys is None else sin_polys, offset=offset, rate=rate, **extra)


def _l1_fixture(anchor=None, *, negate_oscillation=False):
    """A genuine source blocked by v19 and v20 but exact-L1 dominated.

    C1'=s and C2'=1-s, so their derivative envelopes have L1 sum exactly 1.
    The small exact phase envelopes add less than 1/10 over [0,1].  Thus
    |P'|=6/5 strictly dominates the exact L1 envelope.  v19 nevertheless sees
    separate derivative suprema 1+1, and v20's N=4 Cauchy bound already fails
    at s=0 because 4*sum(f_i^2) >= 4 > (6/5)^2.
    """
    sign = Fraction(-1) if negate_oscillation else Fraction(1)
    if anchor is None:
        anchor = [Fraction(-3, 5), Fraction(6, 5)]
    c1 = [0, 0, Fraction(1, 2)]
    c2 = [0, 1, Fraction(-1, 2)]
    return _spec(
        {
            0: anchor,
            1: [sign * value for value in c1],
            2: [sign * value for value in c2],
        },
        rate="1/100",
    )


def _v21_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span.get("route_kind") == "PB00701_V21_EXACT_SIGN_ORTHANT_L1_DERIVATIVE_ENVELOPE"
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
    source = _l1_fixture()

    old19 = v19.classify_required_analytic_event(source)
    assert old19["status"] == "BLOCKED", old19
    assert any(
        span.get("route", {}).get("reason") == "MONOTONE_ANCHOR_DERIVATIVE_DOMINANCE_NOT_CERTIFIED"
        for span in old19.get("spans", [])
    ), old19

    old20 = v20.classify_required_analytic_event(source)
    assert old20["status"] == "BLOCKED", old20
    assert any(
        span.get("route", {}).get("reason") == "POINTWISE_ENVELOPE_STRICT_DOMINANCE_NOT_CERTIFIED"
        for span in old20.get("spans", [])
    ), old20

    route = _v21_route(model.classify_required_analytic_event(source))
    assert route["relation"] == model.V21_ROUTE
    certificate = route["derivative_certificate"]
    assert certificate["relation"] == "EXACT_FINITE_SIGN_ORTHANT_L1_DERIVATIVE_DOMINANCE"
    assert certificate["direction"] == "INCREASING"
    assert certificate["active_positive_harmonics"] == [1, 2]
    assert certificate["term_count"] == 4
    assert certificate["orthant_count"] == 16
    assert len(certificate["orthant_certificates"]) == 16
    assert all(item["certificate"]["status"] == "CERTIFIED" for item in certificate["orthant_certificates"])
    assert "max_" not in certificate["pointwise_identity"]  # guard against accidental numeric max metadata
    assert "max_{sigma" in certificate["pointwise_identity"]
    assert certificate["approximate_root_ordering_used"] is False
    assert certificate["sampling_used"] is False
    assert certificate["arbitrary_subdivision_cap_used"] is False
    assert route["left_event"]["relation"] == "NEGATIVE"
    assert route["right_event"]["relation"] == "POSITIVE"
    assert route["distinct_roots_open"] == 1
    assert route["all_roots_simple"] is True

    decreasing_source = _l1_fixture(
        [Fraction(3, 5), Fraction(-6, 5)], negate_oscillation=True
    )
    decreasing = _v21_route(model.classify_required_analytic_event(decreasing_source))
    assert decreasing["derivative_certificate"]["direction"] == "DECREASING"
    assert decreasing["left_event"]["relation"] == "POSITIVE"
    assert decreasing["right_event"]["relation"] == "NEGATIVE"
    assert decreasing["distinct_roots_open"] == 1

    no_root = _v21_route(model.classify_required_analytic_event(
        _l1_fixture([Fraction(2), Fraction(6, 5)])
    ))
    assert no_root["left_event"]["relation"] == "POSITIVE"
    assert no_root["right_event"]["relation"] == "POSITIVE"
    assert no_root["total_distinct_roots_closed"] == 0

    left_root = _v21_route(model.classify_required_analytic_event(
        _l1_fixture([Fraction(0), Fraction(6, 5)])
    ))
    assert left_root["left_event"]["relation"] == "ZERO"
    assert left_root["left_endpoint_root"] is True
    assert left_root["endpoint_root_multiplicity"] == {"left": 1}
    assert left_root["distinct_roots_open"] == 0

    # Exact L1 boundary: phase envelopes are exactly 1 and 2, so |P'|=3 is
    # equality.  v21 must reject equality and the lower neighbour, while the
    # exact +1/1000000 neighbour is certified.  v20 remains blocked even there.
    eps = Fraction(1, 1000000)
    equality = model._l1_sign_orthant_derivative_certificate(
        {0: [0, 3], 1: [1], 2: [1]}, {}, Fraction(7, 44)
    )
    below = model._l1_sign_orthant_derivative_certificate(
        {0: [0, Fraction(3) - eps], 1: [1], 2: [1]}, {}, Fraction(7, 44)
    )
    above = model._l1_sign_orthant_derivative_certificate(
        {0: [0, Fraction(3) + eps], 1: [1], 2: [1]}, {}, Fraction(7, 44)
    )
    assert equality["status"] == "BLOCKED"
    assert equality["reason"] == "L1_ENVELOPE_STRICT_DOMINANCE_NOT_CERTIFIED"
    assert below["status"] == "BLOCKED"
    assert above["status"] == "CERTIFIED"
    assert above["direction"] == "INCREASING"
    v20_above = v20._pointwise_derivative_envelope_certificate(
        {0: [0, Fraction(3) + eps], 1: [1], 2: [1]}, {}, Fraction(7, 44)
    )
    assert v20_above["status"] == "BLOCKED"

    # Rational and algebraic-irrational sign changes need no approximate root
    # ordering.  Every possible sign cell is covered by exact orthant margins.
    rational_change = model._l1_sign_orthant_derivative_certificate(
        {0: [0, 4], 1: [0, Fraction(-1, 2), Fraction(1, 2)], 2: [Fraction(1, 100)]},
        {}, Fraction(1, 1000)
    )
    assert rational_change["status"] == "CERTIFIED"
    assert rational_change["approximate_root_ordering_used"] is False

    algebraic_change = model._l1_sign_orthant_derivative_certificate(
        {0: [0, 4], 1: [0, Fraction(-1, 2), 0, Fraction(1, 3)], 2: [Fraction(1, 100)]},
        {}, Fraction(1, 1000)
    )
    assert algebraic_change["status"] == "CERTIFIED"
    assert algebraic_change["approximate_root_ordering_used"] is False

    repeated_root = model._l1_sign_orthant_derivative_certificate(
        {0: [0, 4], 1: [0, Fraction(1, 4), Fraction(-1, 2), Fraction(1, 3)], 2: [Fraction(1, 100)]},
        {}, Fraction(1, 1000)
    )
    assert repeated_root["status"] == "CERTIFIED"

    changing_anchor = model._l1_sign_orthant_derivative_certificate(
        {0: [0, 1, -1], 1: [1], 2: [1]}, {}, Fraction(1, 100)
    )
    assert changing_anchor["status"] == "BLOCKED"
    assert changing_anchor["reason"] == "L1_ENVELOPE_ANCHOR_SIGN_NOT_CERTIFIED"

    # Historical precedence: v20-owned coverage stays v20-owned.
    prior_spec = v20test._separated_sup_fixture()
    prior = model.classify_required_analytic_event(prior_spec)
    assert prior["status"] == "CERTIFIED"
    assert not prior.get("v21_l1_sign_orthant_extension", False)
    assert any(
        span.get("route_kind") == "PB00701_V20_EXACT_POINTWISE_DERIVATIVE_ENVELOPE"
        for span in prior.get("spans", [])
    )

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "different-source-coordinate"
    mismatch_result = model.classify_required_analytic_event(mismatch)
    assert mismatch_result["status"] == "SEMANTIC_BLOCKER"

    forged = copy.deepcopy(source)
    forged.update({
        "l1_envelope": {"status": "CERTIFIED"},
        "sign_cells": [{"status": "CERTIFIED"}],
        "orthants": [{"margin": "999"}],
        "orthant_certificates": [{"status": "CERTIFIED"}],
        "margin_polynomials": [["999"]],
        "sturm_certificate": {"roots": 0},
        "sturm_root_count": 0,
        "anchor_sign": "NEGATIVE",
        "root_count": 99,
    })
    forged_route = _v21_route(model.classify_required_analytic_event(forged))
    assert forged_route["derivative_certificate"] == route["derivative_certificate"]
    assert forged_route["distinct_roots_open"] == route["distinct_roots_open"]
    assert forged_route["caller_certificate_trusted"] is False

    floating = copy.deepcopy(source)
    floating["cos_splines"]["0"]["controls"][0] = -0.6
    assert _rejected(floating)

    original_roots = model.EE.distinct_roots_open
    try:
        def refuse(*_args, **_kwargs):
            raise ArithmeticError("adversarial exact Sturm refusal")
        model.EE.distinct_roots_open = refuse
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL", refused
    finally:
        model.EE.distinct_roots_open = original_roots

    assert model.resource_refusal()["is_truth_value"] is False
    print("PB-007-01 v21 finite sign-orthant L1 derivative-envelope adversarial controls: PASS")


if __name__ == "__main__":
    run()
