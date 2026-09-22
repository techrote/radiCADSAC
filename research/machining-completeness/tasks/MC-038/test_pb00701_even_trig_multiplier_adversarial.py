#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_even_trig_multiplier_model as model  # noqa: E402


def _trim(poly):
    out = [Fraction(value) for value in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [Fraction(0)]


def _scale(poly, scalar):
    scalar = Fraction(scalar)
    return _trim([scalar * value for value in poly])


def _add(left, right):
    left = _trim(left)
    right = _trim(right)
    out = [Fraction(0)] * max(len(left), len(right))
    for i, value in enumerate(left):
        out[i] += value
    for i, value in enumerate(right):
        out[i] += value
    return _trim(out)


def _linear_spline(poly):
    poly = _trim(poly)
    if len(poly) > 2:
        raise ValueError("test source helper is deliberately linear")
    a0 = poly[0]
    a1 = poly[1] if len(poly) > 1 else Fraction(0)
    return {
        "degree": 1,
        "knots": ["0", "0", "1", "1"],
        "controls": [str(a0), str(a0 + a1)],
    }


def factor_polys(lambda_0, cosine, sine, *, harmonic=1, a=None, b=None):
    """Independent product-to-sum source construction for the v17 family."""
    cosine = [Fraction(value) for value in cosine]
    sine = [Fraction(value) for value in sine]
    assert len(cosine) == len(sine) and len(cosine) >= 2
    m = len(cosine) - 1
    assert cosine[0] == Fraction(lambda_0) and sine[0] == 0
    a = [Fraction(-1, 3), Fraction(1)] if a is None else [Fraction(x) for x in a]
    b = [Fraction(2, 3), Fraction(-1)] if b is None else [Fraction(x) for x in b]
    cos_polys = {}
    sin_polys = {}
    for r in range(m + 1):
        if r == 0:
            c = _add(_scale(a, cosine[0] + cosine[1] / 2), _scale(b, sine[1] / 2))
            s = _add(_scale(a, sine[1] / 2), _scale(b, cosine[0] - cosine[1] / 2))
        elif r < m:
            c = _add(_scale(a, (cosine[r] + cosine[r + 1]) / 2), _scale(b, (-sine[r] + sine[r + 1]) / 2))
            s = _add(_scale(a, (sine[r] + sine[r + 1]) / 2), _scale(b, (cosine[r] - cosine[r + 1]) / 2))
        else:
            c = _add(_scale(a, cosine[r] / 2), _scale(b, -sine[r] / 2))
            s = _add(_scale(a, sine[r] / 2), _scale(b, cosine[r] / 2))
        h = (2 * r + 1) * harmonic
        cos_polys[h] = c
        sin_polys[h] = s
    return cos_polys, sin_polys


def factor_spec(lambda_0, cosine, sine, *, harmonic=1, offset="0", rate="1/4", **extra):
    cos_polys, sin_polys = factor_polys(lambda_0, cosine, sine, harmonic=harmonic)
    value = {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": {str(h): _linear_spline(poly) for h, poly in cos_polys.items()},
        "sin_splines": {str(h): _linear_spline(poly) for h, poly in sin_polys.items()},
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": offset,
        "phase_turn_rate": rate,
        "source_parameter_id": "source-time-t",
    }
    value.update(extra)
    return value


def _v17_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result["spans"]
        if span.get("route_kind") == "PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER"
    ]
    assert routes, result
    assert routes[0]["status"] == "CERTIFIED"
    return routes[0]


def _rejected(spec):
    try:
        return model.classify_required_analytic_event(spec).get("status") != "CERTIFIED"
    except (AssertionError, ValueError, KeyError, TypeError, ZeroDivisionError):
        return True


def run():
    # Genuine sine-multiplier case. v16 cannot source-factor this family.
    positive = factor_spec(2, [2, 0], [0, 1])
    old = model.v16.classify_required_analytic_event(positive)
    assert old["status"] == "BLOCKED", old
    route = _v17_route(model.classify_required_analytic_event(positive))
    factor = route["factorization"]
    cert = route["projective_nonvanishing"]
    assert factor["cosine_coefficients"] == ["2", "0"]
    assert factor["sine_coefficients"] == ["0", "1"]
    assert cert["multiplier_sign"] == "POSITIVE"
    assert cert["finite_distinct_root_count"] == 0
    assert cert["infinity_value"] == "2"
    assert cert["source"] == "MC-032_EXACT_RATIONAL_STURM_AUTHORITY"
    assert route["carrier_route_kind"] == "PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC"

    negative = _v17_route(model.classify_required_analytic_event(factor_spec(-2, [-2, 0], [0, 1])))
    assert negative["projective_nonvanishing"]["multiplier_sign"] == "NEGATIVE"

    # Exact projective infinity root: 1+cos(2 alpha).
    infinity = model.certify_projective_nonvanishing([1, 1], [0, 0])
    assert infinity["status"] == "BLOCKED"
    assert infinity["reason"] == "PROJECTIVE_MULTIPLIER_ROOT_AT_INFINITY"

    # Finite repeated boundary root: 1+sin(2 alpha) has t=-1 double.
    repeated = model.certify_projective_nonvanishing([1, 0], [0, 1])
    assert repeated["status"] == "BLOCKED"
    assert repeated["reason"] == "PROJECTIVE_MULTIPLIER_FINITE_REAL_ROOT"
    assert repeated["finite_distinct_root_count"] == 1

    # Algebraic-irrational finite roots: 1/2+sin(2 alpha), t=-2 +/- sqrt(3).
    algebraic = model.certify_projective_nonvanishing([Fraction(1, 2), 0], [0, 1])
    assert algebraic["status"] == "BLOCKED"
    assert algebraic["reason"] == "PROJECTIVE_MULTIPLIER_FINITE_REAL_ROOT"
    assert algebraic["finite_distinct_root_count"] == 2

    eps = Fraction(1, 1000000)
    at = model.certify_projective_nonvanishing([1, 0], [0, 1])
    above = model.certify_projective_nonvanishing([1 + eps, 0], [0, 1])
    below = model.certify_projective_nonvanishing([1 - eps, 0], [0, 1])
    assert at["reason"] == "PROJECTIVE_MULTIPLIER_FINITE_REAL_ROOT"
    assert above["status"] == "CERTIFIED" and above["multiplier_sign"] == "POSITIVE"
    assert below["reason"] == "PROJECTIVE_MULTIPLIER_FINITE_REAL_ROOT"

    # v15/v16 precedence is preserved for already-qualified even-cosine sources.
    prior = model.classify_required_analytic_event(
        __import__("verify_pb00701_v15").factor_spec([Fraction(4), Fraction(1, 2), Fraction(-1, 4), Fraction(1)])
    )
    assert prior["status"] == "CERTIFIED"
    assert not any(span.get("route_kind") == "PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER" for span in prior["spans"])

    # Exact malformed-source perturbation must not be accepted as the requested factorization.
    malformed = copy.deepcopy(positive)
    malformed["cos_splines"]["3"]["controls"][0] = str(Fraction(malformed["cos_splines"]["3"]["controls"][0]) + eps)
    assert _rejected(malformed)

    missing_top = copy.deepcopy(positive)
    del missing_top["sin_splines"]["3"]
    assert _rejected(missing_top)

    wrong_lattice = copy.deepcopy(positive)
    wrong_lattice["cos_splines"]["2"] = _linear_spline([1])
    assert _rejected(wrong_lattice)

    # Deliberately underdetermined top phase: real carrier gives dependent p_m/conj(p_m).
    under_cos, under_sin = factor_polys(2, [2, 0], [0, 1], a=[1, 1], b=[0])
    under = model.detect_even_trig_multiplier(under_cos, under_sin)
    assert under["status"] == "BLOCKED"
    assert under["reason"] == "EVEN_TRIG_TOP_PHASE_UNDERDETERMINED"

    # Carrier common factor remains owned by v8 after v17 source/nonvanishing proof.
    common_a = [2, 3, 1]       # (s+1)(s+2)
    common_b = [3, 5, 2]       # (s+1)(2s+3)
    common_cos, common_sin = factor_polys(2, [2, 0], [0, 1], a=common_a, b=common_b)
    common = model._even_trig_route(common_cos, common_sin, 0, Fraction(1, 4), "source-time-t")
    assert common["status"] == "BLOCKED"
    assert common["reason"] == "CARRIER_COMMON_FACTOR_REMAINS_OWNED_BY_PB00701_V8"

    mismatch = copy.deepcopy(positive)
    mismatch["parameter_projection"] = "different-source-coordinate"
    result = model.classify_required_analytic_event(mismatch)
    assert result["status"] == "SEMANTIC_BLOCKER"

    forged = copy.deepcopy(positive)
    forged.update({
        "factorization": {"status": "CERTIFIED"},
        "cosine_coefficients": ["99", "0"],
        "sine_coefficients": ["0", "0"],
        "projective_numerator": ["1"],
        "projective_certificate": {"status": "CERTIFIED"},
        "sturm_root_count": 0,
        "multiplier_sign": "NEGATIVE",
        "root_free": True,
        "infinity_value": "1",
    })
    forged_route = _v17_route(model.classify_required_analytic_event(forged))
    assert forged_route["factorization"]["cosine_coefficients"] == ["2", "0"]
    assert forged_route["factorization"]["sine_coefficients"] == ["0", "1"]
    assert forged_route["projective_nonvanishing"]["caller_certificate_trusted"] is False

    floating = copy.deepcopy(positive)
    floating["cos_splines"]["1"]["controls"][0] = 0.5
    assert _rejected(floating)

    original = model.EE.distinct_roots_open
    try:
        def refuse(*_args, **_kwargs):
            raise ArithmeticError("adversarial exact Sturm budget refusal")
        model.EE.distinct_roots_open = refuse
        refused = model.certify_projective_nonvanishing([2, 0], [0, 1])
        assert refused["status"] == "RESOURCE_REFUSAL"
        assert refused["is_truth_value"] is False
    finally:
        model.EE.distinct_roots_open = original

    assert model.resource_refusal()["is_truth_value"] is False
    print("PB-007-01 v17 adversarial projective even-trig controls: PASS")


if __name__ == "__main__":
    run()
