#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_source_laurent_factor_model as model  # noqa: E402
import pb00701_even_trig_multiplier_model as v17  # noqa: E402
import test_pb00701_even_trig_multiplier_adversarial as v17test  # noqa: E402


def _trim(poly):
    out = [Fraction(value) for value in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [Fraction(0)]


def _add(left, right):
    left = _trim(left)
    right = _trim(right)
    out = [Fraction(0)] * max(len(left), len(right))
    for i, value in enumerate(left):
        out[i] += value
    for i, value in enumerate(right):
        out[i] += value
    return _trim(out)


def _scale(poly, scalar):
    scalar = Fraction(scalar)
    return _trim([scalar * value for value in _trim(poly)])


def _mul(left, right):
    left = _trim(left)
    right = _trim(right)
    out = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return _trim(out)


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
        "cos_splines": {str(h): _power_spline(poly) for h, poly in sorted(cos_polys.items()) if _trim(poly) != [0]},
        "sin_splines": {str(h): _power_spline(poly) for h, poly in sorted(sin_polys.items()) if _trim(poly) != [0]},
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": offset,
        "phase_turn_rate": rate,
        "source_parameter_id": "source-time-t",
    }
    value.update(extra)
    return value


def _source_factor_fixture(factor):
    # This residual is the same coprime single-harmonic carrier class exercised
    # by v17 through v12. Multiplying by a nonconstant source factor blocks all
    # historical routes unless that factor is removed soundly.
    a = [Fraction(-1, 3), Fraction(1)]
    b = [Fraction(2, 3), Fraction(-1)]
    return _spec({1: _mul(factor, a)}, {1: _mul(factor, b)})


def _v18_source_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span.get("route_kind") == "PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR"
    ]
    assert routes, result
    assert routes[0]["status"] == "CERTIFIED"
    return routes[0]


def _laurent_multiharmonic_fixture():
    # Residual carrier: genuine {h,3h} source with independent s-slices.
    c1, s1 = [1, 1], [1, 0]
    c3, s3 = [2, 0], [0, 1]
    # Multiply independently by M(alpha)=2+sin(2*alpha), using exact
    # product-to-sum identities. The resulting source uses {h,3h,5h}.
    cos_polys = {
        1: _add(_scale(c1, 2), _add(_scale(s1, Fraction(1, 2)), _scale(s3, Fraction(1, 2)))),
        3: _add(_scale(c3, 2), _scale(s1, Fraction(-1, 2))),
        5: _scale(s3, Fraction(-1, 2)),
    }
    sin_polys = {
        1: _add(_scale(s1, 2), _add(_scale(c1, Fraction(1, 2)), _scale(c3, Fraction(-1, 2)))),
        3: _add(_scale(s3, 2), _scale(c1, Fraction(1, 2))),
        5: _scale(c3, Fraction(1, 2)),
    }
    return cos_polys, sin_polys


def _rejected(spec):
    try:
        return model.classify_required_analytic_event(spec).get("status") != "CERTIFIED"
    except (AssertionError, ValueError, KeyError, TypeError, ZeroDivisionError):
        return True


def run():
    # New coverage: v17 is blocked by a nonconstant common source factor whose
    # quotients are themselves nonconstant. v18 proves g=s+2 never vanishes,
    # divides exactly, regenerates exactly, then delegates the residual to v17.
    source = _source_factor_fixture([2, 1])
    old = v17.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    route = _v18_source_route(model.classify_required_analytic_event(source))
    assert route["relation"] == model.V18_SOURCE_ROUTE
    assert route["source_factor"] == ["2", "1"]
    assert route["source_factor_nonvanishing"]["status"] == "CERTIFIED"
    assert route["source_factor_nonvanishing"]["distinct_roots_open"] == 0
    assert route["residual"]["status"] == "CERTIFIED"
    assert all(item["remainder"] == ["0"] for item in route["division_proof"])

    # Exact closed-interval source-factor boundaries, including algebraic roots.
    endpoint = model.certify_source_factor_nonvanishing([0, 1])
    assert endpoint["status"] == "BLOCKED" and endpoint["reason"] == "SOURCE_FACTOR_ENDPOINT_ROOT"
    rational = model.certify_source_factor_nonvanishing([Fraction(-1, 2), 1])
    assert rational["status"] == "BLOCKED" and rational["reason"] == "SOURCE_FACTOR_INTERIOR_REAL_ROOT"
    algebraic = model.certify_source_factor_nonvanishing([Fraction(-2, 9), 0, 1])
    assert algebraic["status"] == "BLOCKED" and algebraic["reason"] == "SOURCE_FACTOR_INTERIOR_REAL_ROOT"
    eps = Fraction(1, 1000000)
    above = model.certify_source_factor_nonvanishing([eps, 1])
    at = model.certify_source_factor_nonvanishing([0, 1])
    below = model.certify_source_factor_nonvanishing([-eps, 1])
    assert above["status"] == "CERTIFIED" and above["factor_sign"] == "POSITIVE"
    assert at["reason"] == "SOURCE_FACTOR_ENDPOINT_ROOT"
    assert below["reason"] == "SOURCE_FACTOR_INTERIOR_REAL_ROOT"

    # Genuine Laurent/source-module extraction with a multi-harmonic residual.
    lcos, lsin = _laurent_multiharmonic_fixture()
    detected = model.detect_laurent_module_factor(lcos, lsin)
    assert detected["status"] == "SOURCE_LAURENT_FACTORIZATION_CERTIFIED", detected
    assert detected["multiplier_degree"] == 1
    assert detected["residual_harmonics"] == [1, 3]
    assert detected["source_regeneration_verified_exactly"] is True
    assert detected["factor"]["projective_nonvanishing"]["status"] == "CERTIFIED"
    # The residual itself is intentionally outside existing exact authority;
    # factor extraction must not launder that into success.
    residual_block = model._laurent_factor_route(lcos, lsin, 0, Fraction(1, 4), "source-time-t")
    assert residual_block["status"] != "CERTIFIED", residual_block
    assert residual_block["blocker"] == "PB-007-01"

    odd = model._canonical_even_multiplier([v17._g(1), v17._g(1)])
    assert odd["status"] == "BLOCKED" and odd["reason"] == "LAURENT_COMMON_FACTOR_HAS_ODD_DEGREE"
    nonreciprocal = model._canonical_even_multiplier([v17._g(1), v17._g(1), v17._g(2)])
    assert nonreciprocal["status"] == "BLOCKED"
    rooted = model._canonical_even_multiplier([v17._g(1), v17._g(2), v17._g(1)])
    assert rooted["status"] == "BLOCKED"
    assert rooted["reason"] in {"PROJECTIVE_MULTIPLIER_ROOT_AT_INFINITY", "PROJECTIVE_MULTIPLIER_FINITE_REAL_ROOT"}

    # A one-coefficient source perturbation destroys exact module divisibility
    # rather than being repaired by tolerance.
    malformed_cos = copy.deepcopy(lcos)
    malformed_cos[3][0] += eps
    malformed = model.detect_laurent_module_factor(malformed_cos, lsin)
    assert malformed is None or malformed.get("status") != "SOURCE_LAURENT_FACTORIZATION_CERTIFIED"

    # Historical precedence: an already-v17-certified source stays v17-owned.
    prior_spec = v17test.factor_spec(2, [2, 0], [0, 1])
    prior = model.classify_required_analytic_event(prior_spec)
    assert prior["status"] == "CERTIFIED"
    assert not prior.get("v18_source_laurent_module_extension", False)

    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "different-source-coordinate"
    mismatch_result = model.classify_required_analytic_event(mismatch)
    assert mismatch_result["status"] == "SEMANTIC_BLOCKER"

    forged = copy.deepcopy(source)
    forged.update({
        "source_factor": ["1"],
        "source_factor_certificate": {"status": "CERTIFIED"},
        "laurent_factorization": {"status": "CERTIFIED"},
        "laurent_gcd": [{"re": "1", "im": "0"}],
        "sturm_root_count": 0,
        "multiplier_sign": "NEGATIVE",
        "root_free": True,
    })
    forged_route = _v18_source_route(model.classify_required_analytic_event(forged))
    assert forged_route["source_factor"] == ["2", "1"]
    assert forged_route["source_factor_nonvanishing"]["caller_certificate_trusted"] is False

    floating = copy.deepcopy(source)
    floating["cos_splines"]["1"]["controls"][0] = 0.5
    assert _rejected(floating)

    original = model.EE.distinct_roots_open
    try:
        def refuse(*_args, **_kwargs):
            raise ArithmeticError("adversarial exact Sturm budget refusal")
        model.EE.distinct_roots_open = refuse
        refused = model.certify_source_factor_nonvanishing([2, 1])
        assert refused["status"] == "RESOURCE_REFUSAL"
        assert refused["is_truth_value"] is False
    finally:
        model.EE.distinct_roots_open = original

    assert model.resource_refusal()["is_truth_value"] is False
    print("PB-007-01 v18 source/Laurent module adversarial controls: PASS")


if __name__ == "__main__":
    run()
