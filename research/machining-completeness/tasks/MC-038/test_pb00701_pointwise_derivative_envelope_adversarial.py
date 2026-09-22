#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_pointwise_derivative_envelope_model as model  # noqa: E402
import pb00701_multiharmonic_monotone_anchor_model as v19  # noqa: E402
import test_pb00701_multiharmonic_monotone_anchor_adversarial as v19test  # noqa: E402


def _spec(cos_polys, sin_polys=None, *, offset="0", rate="1/50", **extra):
    return v19test._spec(cos_polys, {} if sin_polys is None else sin_polys, offset=offset, rate=rate, **extra)


def _separated_sup_fixture(anchor=None, *, negate_oscillation=False):
    """A source v19 cannot certify but the exact pointwise envelope can.

    The three derivative shapes have separated maxima:
      8(1-s)^2, 16s(1-s), 8s^2.
    Their individual suprema sum to 20 before v19 even adds phase terms, so
    P'=199/10 is insufficient for v19. Pointwise their joint L2 envelope is
    substantially smaller and v20 proves the exact Q polynomial positive.
    """
    sign = Fraction(-1) if negate_oscillation else Fraction(1)
    if anchor is None:
        anchor = [Fraction(-10), Fraction(199, 10)]
    c1 = [0, 8, -8, Fraction(8, 3)]
    c2 = [0, 0, 8, Fraction(-16, 3)]
    c3 = [0, 0, 0, Fraction(8, 3)]
    return _spec(
        {
            0: anchor,
            1: [sign * value for value in c1],
            2: [sign * value for value in c2],
            3: [sign * value for value in c3],
        },
        rate="1/50",
    )


def _v20_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span.get("route_kind") == "PB00701_V20_EXACT_POINTWISE_DERIVATIVE_ENVELOPE"
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
    source = _separated_sup_fixture()
    old = v19.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    old_routes = [span.get("route", {}) for span in old.get("spans", [])]
    assert any(
        route.get("reason") == "MONOTONE_ANCHOR_DERIVATIVE_DOMINANCE_NOT_CERTIFIED"
        for route in old_routes
    ), old

    route = _v20_route(model.classify_required_analytic_event(source))
    assert route["relation"] == model.V20_ROUTE
    certificate = route["derivative_certificate"]
    assert certificate["relation"] == "EXACT_POINTWISE_POLYNOMIAL_L2_DERIVATIVE_DOMINANCE"
    assert certificate["direction"] == "INCREASING"
    assert certificate["term_count"] == 6
    assert certificate["active_positive_harmonics"] == [1, 2, 3]
    assert certificate["anchor_sign_certificate"]["status"] == "CERTIFIED"
    assert certificate["q_positivity_certificate"]["status"] == "CERTIFIED"
    assert certificate["q_positivity_certificate"]["distinct_roots_open"] == 0
    assert certificate["pi_upper_theorem"] == "pi < 22/7"
    assert certificate["sampling_used"] is False
    assert certificate["arbitrary_subdivision_cap_used"] is False
    assert route["left_event"]["relation"] == "NEGATIVE"
    assert route["right_event"]["relation"] == "POSITIVE"
    assert route["distinct_roots_open"] == 1
    assert route["all_roots_simple"] is True

    decreasing_source = _separated_sup_fixture(
        [Fraction(10), Fraction(-199, 10)], negate_oscillation=True
    )
    decreasing = _v20_route(model.classify_required_analytic_event(decreasing_source))
    assert decreasing["derivative_certificate"]["direction"] == "DECREASING"
    assert decreasing["left_event"]["relation"] == "POSITIVE"
    assert decreasing["right_event"]["relation"] == "NEGATIVE"
    assert decreasing["distinct_roots_open"] == 1

    no_root = _v20_route(model.classify_required_analytic_event(
        _separated_sup_fixture([Fraction(1), Fraction(199, 10)])
    ))
    assert no_root["left_event"]["relation"] == "POSITIVE"
    assert no_root["right_event"]["relation"] == "POSITIVE"
    assert no_root["total_distinct_roots_closed"] == 0

    left_root = _v20_route(model.classify_required_analytic_event(
        _separated_sup_fixture([Fraction(0), Fraction(199, 10)])
    ))
    assert left_root["left_event"]["relation"] == "ZERO"
    assert left_root["left_endpoint_root"] is True
    assert left_root["endpoint_root_multiplicity"] == {"left": 1}
    assert left_root["distinct_roots_open"] == 0

    # Exact Q=0 threshold. With constant harmonics h=1 and h=7, rate=7/44
    # makes the two nonzero phase-envelope terms exactly 1 and 7. N=2, so
    # N*sum(f_i^2)=100. P'=10 is exact equality and must fail closed.
    eps = Fraction(1, 1000000)
    equality = model._pointwise_derivative_envelope_certificate(
        {0: [0, 10], 1: [1], 7: [1]}, {}, Fraction(7, 44)
    )
    below = model._pointwise_derivative_envelope_certificate(
        {0: [0, Fraction(10) - eps], 1: [1], 7: [1]}, {}, Fraction(7, 44)
    )
    above = model._pointwise_derivative_envelope_certificate(
        {0: [0, Fraction(10) + eps], 1: [1], 7: [1]}, {}, Fraction(7, 44)
    )
    assert equality["status"] == "BLOCKED"
    assert equality["reason"] == "POINTWISE_ENVELOPE_STRICT_DOMINANCE_NOT_CERTIFIED"
    assert equality["q_polynomial"] == ["0"]
    assert below["status"] == "BLOCKED"
    assert above["status"] == "CERTIFIED"
    assert above["direction"] == "INCREASING"

    # A changing/zero anchor derivative is not converted into monotonicity.
    changing_anchor = model._pointwise_derivative_envelope_certificate(
        {0: [0, 1, -1], 1: [1], 2: [1]}, {}, Fraction(1, 100)
    )
    assert changing_anchor["status"] == "BLOCKED"
    assert changing_anchor["reason"] == "POINTWISE_ENVELOPE_ANCHOR_SIGN_NOT_CERTIFIED"

    # Q can have interior roots even while both endpoints are positive. Exact
    # Sturm authority must detect them rather than relying on endpoint signs.
    peaked = [0, 0, 10, -20, 10]
    q_root = model._pointwise_derivative_envelope_certificate(
        {0: [0, 1], 1: peaked, 2: peaked}, {}, Fraction(1, 1000000)
    )
    assert q_root["status"] == "BLOCKED"
    assert q_root["reason"] == "POINTWISE_ENVELOPE_STRICT_DOMINANCE_NOT_CERTIFIED"
    q_cert = q_root["q_positivity_certificate"]
    assert q_cert["reason"] in {"POINTWISE_ENVELOPE_Q_INTERIOR_ROOT", "POINTWISE_ENVELOPE_Q_ENDPOINT_NOT_POSITIVE"}

    # Structural boundaries remain fail-closed.
    assert model._pointwise_envelope_route({1: [1], 2: [1]}, {}, 0, Fraction(1, 50), "s") is None
    assert model._pointwise_envelope_route({0: [0, 1], 1: [1]}, {}, 0, Fraction(1, 50), "s") is None
    assert model._pointwise_envelope_route({0: [0, 1], 1: [1], 2: [1]}, {}, 0, 0, "s") is None

    # Historical precedence: a v19-owned case remains v19-owned.
    prior_spec = v19test._fixture([Fraction(-1, 2), 1])
    prior = model.classify_required_analytic_event(prior_spec)
    assert prior["status"] == "CERTIFIED"
    assert not prior.get("v20_pointwise_derivative_envelope_extension", False)
    assert any(
        span.get("route_kind") == "PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR"
        for span in prior.get("spans", [])
    )

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "different-source-coordinate"
    mismatch_result = model.classify_required_analytic_event(mismatch)
    assert mismatch_result["status"] == "SEMANTIC_BLOCKER"

    forged = copy.deepcopy(source)
    forged.update({
        "pointwise_envelope": {"status": "CERTIFIED"},
        "sum_squares_polynomial": ["0"],
        "q_polynomial": ["999"],
        "sturm_certificate": {"roots": 0},
        "sturm_root_count": 0,
        "anchor_sign": "NEGATIVE",
        "term_count": 1,
        "root_count": 99,
    })
    forged_route = _v20_route(model.classify_required_analytic_event(forged))
    assert forged_route["derivative_certificate"] == route["derivative_certificate"]
    assert forged_route["distinct_roots_open"] == route["distinct_roots_open"]
    assert forged_route["caller_certificate_trusted"] is False

    floating = copy.deepcopy(source)
    floating["cos_splines"]["0"]["controls"][0] = -10.0
    assert _rejected(floating)

    # Exact Sturm refusal is non-truth and cannot be converted into success.
    original_roots = model.EE.distinct_roots_open
    try:
        def refuse(*_args, **_kwargs):
            raise ArithmeticError("adversarial exact Sturm refusal")
        model.EE.distinct_roots_open = refuse
        refused = model.classify_required_analytic_event(source)
        assert refused["status"] == "RESOURCE_REFUSAL", refused
        assert any(
            span.get("route", {}).get("is_truth_value") is False
            for span in refused.get("spans", [])
        )
    finally:
        model.EE.distinct_roots_open = original_roots

    assert model.resource_refusal()["is_truth_value"] is False
    print("PB-007-01 v20 pointwise derivative-envelope adversarial controls: PASS")


if __name__ == "__main__":
    run()
