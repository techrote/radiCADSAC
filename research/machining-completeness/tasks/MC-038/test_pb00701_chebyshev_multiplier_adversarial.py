#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import copy
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_chebyshev_multiplier_model as model  # noqa: E402
import verify_pb00701_v15 as verify_v15  # noqa: E402


def _v16_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span.get("route_kind") == "PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER"
    ]
    assert routes, result
    assert routes[0]["status"] == "CERTIFIED"
    return routes[0]


def _rejected(spec):
    try:
        return model.classify_required_analytic_event(spec).get("status") != "CERTIFIED"
    except (AssertionError, ValueError, KeyError, TypeError):
        return True


def _boundary_lambdas(c):
    c = Fraction(c)
    # 4*(x^2-x+1)*(x+c) in Chebyshev coordinates, normalized at T_3.
    return [6 * c - 2, 7 - 4 * c, 2 * c - 2, Fraction(1)]


def run():
    positive = [Fraction(160), Fraction(-200), Fraction(50), Fraction(1)]
    source = verify_v15.factor_spec(positive)
    old = verify_v15.model.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    old_v15 = verify_v15.model.classify_required_analytic_event(source)
    assert any(
        span.get("route_kind") == "PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER"
        and span["route"].get("reason") == "FINITE_MULTIPLIER_STRICT_DOMINANCE_NOT_CERTIFIED"
        for span in old_v15["spans"]
    )

    route = _v16_route(model.classify_required_analytic_event(source))
    cert = route["chebyshev_nonvanishing"]
    assert cert["multiplier_sign"] == "POSITIVE"
    assert cert["open_interval_distinct_root_count"] == 0
    assert cert["source"] == "MC-032_EXACT_RATIONAL_STURM_AUTHORITY"
    assert route["factorization"]["strict_dominance_margin"].startswith("-")
    assert route["carrier_route_kind"] == "PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC"

    negative = [Fraction(-160), Fraction(200), Fraction(-50), Fraction(1)]
    negative_route = _v16_route(model.classify_required_analytic_event(verify_v15.factor_spec(negative)))
    assert negative_route["chebyshev_nonvanishing"]["multiplier_sign"] == "NEGATIVE"

    # v15 keeps precedence when strict L1 dominance already proves nonvanishing.
    prior = model.classify_required_analytic_event(
        verify_v15.factor_spec([Fraction(4), Fraction(1, 2), Fraction(-1, 4), Fraction(1)])
    )
    assert prior["status"] == "CERTIFIED"
    assert any(span.get("route_kind") == "PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER" for span in prior["spans"])
    assert not any(span.get("route_kind") == "PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER" for span in prior["spans"])

    endpoint = model.certify_chebyshev_nonvanishing([4, 3, 0, 1])
    assert endpoint["status"] == "BLOCKED"
    assert endpoint["reason"] == "CHEBYSHEV_MULTIPLIER_ENDPOINT_ROOT"

    interior = model.certify_chebyshev_nonvanishing([0, 7, 0, 1])
    assert interior["status"] == "BLOCKED"
    assert interior["reason"] == "CHEBYSHEV_MULTIPLIER_INTERIOR_ROOT"
    assert interior["open_interval_distinct_root_count"] == 1

    repeated = model.certify_chebyshev_nonvanishing([4, 3, 4, 1])
    assert repeated["status"] == "BLOCKED"
    assert repeated["reason"] == "CHEBYSHEV_MULTIPLIER_INTERIOR_ROOT"
    assert repeated["open_interval_distinct_root_count"] == 1

    algebraic = model.certify_chebyshev_nonvanishing([0, 1, 4, 1])
    assert algebraic["status"] == "BLOCKED"
    assert algebraic["reason"] == "CHEBYSHEV_MULTIPLIER_INTERIOR_ROOT"
    assert algebraic["open_interval_distinct_root_count"] == 2

    eps = Fraction(1, 1000000)
    at = model.certify_chebyshev_nonvanishing(_boundary_lambdas(Fraction(1)))
    above = model.certify_chebyshev_nonvanishing(_boundary_lambdas(Fraction(1) + eps))
    below = model.certify_chebyshev_nonvanishing(_boundary_lambdas(Fraction(1) - eps))
    assert at["reason"] == "CHEBYSHEV_MULTIPLIER_ENDPOINT_ROOT"
    assert above["status"] == "CERTIFIED" and above["multiplier_sign"] == "POSITIVE"
    assert below["reason"] == "CHEBYSHEV_MULTIPLIER_INTERIOR_ROOT"

    below_full = model.classify_required_analytic_event(
        verify_v15.factor_spec(_boundary_lambdas(Fraction(1) - eps))
    )
    assert below_full["status"] == "BLOCKED"
    assert any(
        span.get("route_kind") == "PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER"
        and span["route"].get("reason") == "CHEBYSHEV_MULTIPLIER_INTERIOR_ROOT"
        for span in below_full["spans"]
    )

    forged = copy.deepcopy(source)
    forged.update({
        "lambda_vector": ["4", "0", "0", "1"],
        "factorization": {"status": "CERTIFIED"},
        "chebyshev_polynomial": ["1"],
        "sturm_root_count": 0,
        "multiplier_sign": "NEGATIVE",
        "root_free": True,
        "nonvanishing_certificate": {"status": "CERTIFIED"},
    })
    forged_route = _v16_route(model.classify_required_analytic_event(forged))
    assert forged_route["factorization"]["lambda_vector"] == ["160", "-200", "50", "1"]
    assert forged_route["chebyshev_nonvanishing"]["caller_certificate_trusted"] is False

    floating = copy.deepcopy(source)
    floating["cos_splines"]["1"]["controls"][0] = 0.5
    assert _rejected(floating)

    original = model.EE.distinct_roots_open
    try:
        def refuse(*_args, **_kwargs):
            raise ArithmeticError("adversarial exact Sturm budget refusal")
        model.EE.distinct_roots_open = refuse
        refused = model.certify_chebyshev_nonvanishing(positive)
        assert refused["status"] == "RESOURCE_REFUSAL"
        assert refused["is_truth_value"] is False
    finally:
        model.EE.distinct_roots_open = original

    assert model.resource_refusal()["is_truth_value"] is False
    print("PB-007-01 v16 adversarial Chebyshev/Sturm controls: PASS")


if __name__ == "__main__":
    run()
