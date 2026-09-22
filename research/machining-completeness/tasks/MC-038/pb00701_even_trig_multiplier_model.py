#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_chebyshev_multiplier_model as v16  # noqa: E402

v15 = v16.v15
EE = v16.EE
q = v16.q
V17_ROUTE = "EXACT_PROJECTIVE_STURM_FINITE_EVEN_TRIG_MULTIPLIER_TO_SINGLE_HARMONIC"


class EvenTrigMultiplierRefusal(RuntimeError):
    """Bounded exact-resource refusal. Never a truth value."""


def _trim(poly):
    return v15._trim([q(value) for value in poly])


def _padd(left, right):
    left = _trim(left)
    right = _trim(right)
    out = [Fraction(0)] * max(len(left), len(right))
    for i, value in enumerate(left):
        out[i] += value
    for i, value in enumerate(right):
        out[i] += value
    return _trim(out)


def _pscale(poly, scalar):
    scalar = q(scalar)
    return _trim([q(value) * scalar for value in poly])


def _pmul(left, right):
    left = _trim(left)
    right = _trim(right)
    out = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return _trim(out)


def _g(re=0, im=0):
    return (q(re), q(im))


def _gadd(left, right):
    return (left[0] + right[0], left[1] + right[1])


def _gsub(left, right):
    return (left[0] - right[0], left[1] - right[1])


def _gmul(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def _gconj(value):
    return (value[0], -value[1])


def _gdiv(left, right):
    den = right[0] * right[0] + right[1] * right[1]
    if den == 0:
        raise ZeroDivisionError("Gaussian-rational division by zero")
    return (
        (left[0] * right[0] + left[1] * right[1]) / den,
        (left[1] * right[0] - left[0] * right[1]) / den,
    )


def _gzero(value):
    return value[0] == 0 and value[1] == 0


def _gstr(value):
    return {"re": str(value[0]), "im": str(value[1])}


def _gpoly_trim(poly):
    out = [(_g(value[0], value[1])) for value in poly]
    while len(out) > 1 and _gzero(out[-1]):
        out.pop()
    return out or [_g()]


def _gpoly_conj(poly):
    return _gpoly_trim([_gconj(value) for value in poly])


def _gpoly_scale(poly, scalar):
    return _gpoly_trim([_gmul(value, scalar) for value in poly])


def _gpoly_add(left, right):
    left = _gpoly_trim(left)
    right = _gpoly_trim(right)
    out = [_g()] * max(len(left), len(right))
    for i in range(len(out)):
        a = left[i] if i < len(left) else _g()
        b = right[i] if i < len(right) else _g()
        out[i] = _gadd(a, b)
    return _gpoly_trim(out)


def _gpoly_sub(left, right):
    return _gpoly_add(left, _gpoly_scale(right, _g(-1)))


def _gpoly_equal(left, right):
    return _gpoly_trim(left) == _gpoly_trim(right)


def _gpoly_scalar_ratio(numerator, denominator):
    numerator = _gpoly_trim(numerator)
    denominator = _gpoly_trim(denominator)
    if len(denominator) == 1 and _gzero(denominator[0]):
        return None
    pivot = next((i for i, value in enumerate(denominator) if not _gzero(value)), None)
    if pivot is None:
        return None
    if pivot >= len(numerator):
        return None
    ratio = _gdiv(numerator[pivot], denominator[pivot])
    if not _gpoly_equal(numerator, _gpoly_scale(denominator, ratio)):
        return None
    return ratio


def _complex_source_poly(cos_poly, sin_poly):
    """Return p=C-iS, the positive-frequency complex source coefficient."""
    cosine = _trim(cos_poly)
    sine = _trim(sin_poly)
    size = max(len(cosine), len(sine))
    return _gpoly_trim([
        _g(cosine[i] if i < len(cosine) else 0, -(sine[i] if i < len(sine) else 0))
        for i in range(size)
    ])


def _solve_top_phase(top, previous):
    """Solve previous=a*top+rho*conj(top) over exact Gaussian rationals."""
    u = _gpoly_trim(top)
    v = _gpoly_conj(u)
    w = _gpoly_trim(previous)
    size = max(len(u), len(v), len(w))
    u = u + [_g()] * (size - len(u))
    v = v + [_g()] * (size - len(v))
    w = w + [_g()] * (size - len(w))
    for i in range(size):
        for j in range(i + 1, size):
            det = _gsub(_gmul(u[i], v[j]), _gmul(u[j], v[i]))
            if _gzero(det):
                continue
            a = _gdiv(_gsub(_gmul(w[i], v[j]), _gmul(w[j], v[i])), det)
            rho = _gdiv(_gsub(_gmul(u[i], w[j]), _gmul(u[j], w[i])), det)
            rebuilt = _gpoly_add(_gpoly_scale(top, a), _gpoly_scale(_gpoly_conj(top), rho))
            if _gpoly_equal(rebuilt, previous):
                return a, rho
    return None


def detect_even_trig_multiplier(cos_polys, sin_polys):
    """Recover a normalized finite real even-trigonometric multiplier from source maps.

    Writing q=A-iB and m_k=(c_k-i*s_k)/2 for k>0, m_0=lambda_0,
    the positive-frequency source coefficient at (2r+1)h is

      p_r = q*m_r + conj(q)*m_{r+1},   0<=r<m,
      p_m = q*m_m.

    The phase/scale of the highest multiplier coefficient is derived from
    p_{m-1}=a*p_m+rho*conj(p_m). If p_m and its conjugate are not independent
    as polynomial vectors, the normalized source inversion is deliberately
    left blocked rather than guessed.
    """
    cos_nonzero = {int(h): _trim(poly) for h, poly in cos_polys.items() if _trim(poly) != [0]}
    sin_nonzero = {int(h): _trim(poly) for h, poly in sin_polys.items() if _trim(poly) != [0]}
    harmonics = sorted(set(cos_nonzero) | set(sin_nonzero))
    if not harmonics:
        return None
    harmonic = harmonics[0]
    if harmonic <= 0:
        return None
    if any(h <= 0 or h % harmonic != 0 or (h // harmonic) % 2 != 1 for h in harmonics):
        return None
    top_harmonic = harmonics[-1]
    top_ratio = top_harmonic // harmonic
    degree = (top_ratio - 1) // 2
    if degree < 1 or top_ratio != 2 * degree + 1:
        return None

    source = []
    for r in range(degree + 1):
        h = (2 * r + 1) * harmonic
        source.append(_complex_source_poly(cos_nonzero.get(h, [0]), sin_nonzero.get(h, [0])))
    if len(source[-1]) == 1 and _gzero(source[-1][0]):
        return None

    solved = _solve_top_phase(source[-1], source[-2])
    if solved is None:
        return {
            "status": "BLOCKED",
            "relation": "EXACT_SOURCE_DERIVED_EVEN_TRIG_MULTIPLIER_FACTORIZATION",
            "reason": "EVEN_TRIG_TOP_PHASE_UNDERDETERMINED",
            "blocker": "PB-007-01",
            "harmonic": harmonic,
            "top_harmonic": top_harmonic,
            "multiplier_degree": degree,
            "caller_factorization_trusted": False,
        }
    _, rho = solved
    if _gmul(rho, _gconj(rho)) != _g(1):
        return None

    if rho == _g(-1):
        top_c = Fraction(0)
        top_s = Fraction(1)
    else:
        den = Fraction(1) + rho[0]
        if den == 0:
            return None
        top_c = Fraction(1)
        top_s = -rho[1] / den
    top_m = _g(top_c / 2, -top_s / 2)
    if _gdiv(top_m, _gconj(top_m)) != rho:
        return None

    qpoly = _gpoly_scale(source[-1], _gdiv(_g(1), top_m))
    qbar = _gpoly_conj(qpoly)
    multipliers = [None] * (degree + 1)
    multipliers[-1] = top_m
    for r in range(degree - 1, -1, -1):
        residual = _gpoly_sub(source[r], _gpoly_scale(qbar, multipliers[r + 1]))
        scalar = _gpoly_scalar_ratio(residual, qpoly)
        if scalar is None:
            return None
        multipliers[r] = scalar

    if multipliers[0][1] != 0:
        return None
    lambda_0 = multipliers[0][0]
    cosine = [Fraction(0)] * (degree + 1)
    sine = [Fraction(0)] * (degree + 1)
    cosine[0] = lambda_0
    for k in range(1, degree + 1):
        cosine[k] = 2 * multipliers[k][0]
        sine[k] = -2 * multipliers[k][1]
    if not any(value != 0 for value in sine[1:]):
        # Even-cosine sources remain owned by v15/v16.
        return None

    for r in range(degree + 1):
        next_m = multipliers[r + 1] if r < degree else _g()
        rebuilt = _gpoly_add(_gpoly_scale(qpoly, multipliers[r]), _gpoly_scale(qbar, next_m))
        if not _gpoly_equal(rebuilt, source[r]):
            return None

    carrier_a = _trim([value[0] for value in qpoly])
    carrier_b = _trim([-value[1] for value in qpoly])
    return {
        "status": "SOURCE_FACTORIZATION_CERTIFIED",
        "relation": "EXACT_SOURCE_DERIVED_EVEN_TRIG_MULTIPLIER_FACTORIZATION",
        "harmonic": harmonic,
        "top_harmonic": top_harmonic,
        "multiplier_degree": degree,
        "normalization": (
            "highest (c_m,s_m) is normalized to c_m=1 when c_m!=0, otherwise s_m=1; "
            "the exact nonzero real scale is absorbed into the carrier"
        ),
        "lambda_0": str(lambda_0),
        "cosine_coefficients": [str(value) for value in cosine],
        "sine_coefficients": [str(value) for value in sine],
        "highest_phase_ratio": _gstr(rho),
        "carrier_cos_polynomial": [str(value) for value in carrier_a],
        "carrier_sin_polynomial": [str(value) for value in carrier_b],
        "source_cos_polynomials": {
            str(k): [str(value) for value in poly] for k, poly in sorted(cos_nonzero.items())
        },
        "source_sin_polynomials": {
            str(k): [str(value) for value in poly] for k, poly in sorted(sin_nonzero.items())
        },
        "source_coefficient_identities_verified_exactly": True,
        "caller_factorization_trusted": False,
        "binary_float_used": False,
        "epsilon_used": False,
        "sampling_used": False,
        "numeric_trigonometry_used": False,
    }


def _one_plus_t2_power(power):
    out = [Fraction(0)] * (2 * power + 1)
    for j in range(power + 1):
        out[2 * j] = Fraction(comb(power, j))
    return _trim(out)


def _complex_binomial_2k(k):
    """Real/imag parts of (1+i*t)^(2k), ascending exact powers."""
    real = [Fraction(0)] * (2 * k + 1)
    imag = [Fraction(0)] * (2 * k + 1)
    for j in range(2 * k + 1):
        coefficient = Fraction(comb(2 * k, j))
        residue = j % 4
        if residue == 0:
            real[j] = coefficient
        elif residue == 1:
            imag[j] = coefficient
        elif residue == 2:
            real[j] = -coefficient
        else:
            imag[j] = -coefficient
    return _trim(real), _trim(imag)


def projective_numerator(cosine_coefficients, sine_coefficients):
    cosine = [q(value) for value in cosine_coefficients]
    sine = [q(value) for value in sine_coefficients]
    if len(cosine) != len(sine) or len(cosine) < 2:
        raise ValueError("even-trigonometric multiplier coefficient vectors must have equal finite degree")
    degree = len(cosine) - 1
    if sine[0] != 0:
        raise ValueError("sine coefficient at k=0 must be exactly zero")
    numerator = _pscale(_one_plus_t2_power(degree), cosine[0])
    for k in range(1, degree + 1):
        real, imag = _complex_binomial_2k(k)
        lift = _one_plus_t2_power(degree - k)
        numerator = _padd(numerator, _pscale(_pmul(real, lift), cosine[k]))
        numerator = _padd(numerator, _pscale(_pmul(imag, lift), sine[k]))
    return _trim(numerator)


def certify_projective_nonvanishing(cosine_coefficients, sine_coefficients):
    """Prove exact nonvanishing on RP^1 after t=tan(alpha) rationalization."""
    try:
        cosine = [q(value) for value in cosine_coefficients]
        sine = [q(value) for value in sine_coefficients]
        if len(cosine) != len(sine) or len(cosine) < 2 or sine[0] != 0:
            raise ValueError("invalid multiplier vectors")
        degree = len(cosine) - 1
        numerator = projective_numerator(cosine, sine)
        expected_degree = 2 * degree
        infinity_value = cosine[0] + sum(((-1) ** k) * cosine[k] for k in range(1, degree + 1))
        if infinity_value == 0 or EE.degree(numerator) != expected_degree:
            return {
                "status": "BLOCKED",
                "reason": "PROJECTIVE_MULTIPLIER_ROOT_AT_INFINITY",
                "blocker": "PB-007-01",
                "projective_degree": expected_degree,
                "infinity_value": str(infinity_value),
                "projective_numerator": [str(value) for value in numerator],
                "caller_certificate_trusted": False,
            }

        lead = numerator[-1]
        bound = Fraction(2)
        if len(numerator) > 1:
            bound += max((abs(value / lead) for value in numerator[:-1]), default=Fraction(0))
        root_count = EE.distinct_roots_open(numerator, -bound, bound)
        if root_count != 0:
            return {
                "status": "BLOCKED",
                "reason": "PROJECTIVE_MULTIPLIER_FINITE_REAL_ROOT",
                "blocker": "PB-007-01",
                "projective_degree": expected_degree,
                "cauchy_sturm_bound": str(bound),
                "finite_distinct_root_count": int(root_count),
                "infinity_value": str(infinity_value),
                "projective_numerator": [str(value) for value in numerator],
                "caller_certificate_trusted": False,
            }
        at_zero = EE.exact_event(numerator, Fraction(0))
        relation = at_zero.get("relation")
        if relation not in {"POSITIVE", "NEGATIVE"}:
            raise ArithmeticError("exact projective sign unavailable")
        lead_relation = "POSITIVE" if lead > 0 else "NEGATIVE"
        if lead_relation != relation:
            raise AssertionError("root-free even-degree projective polynomial changed sign")
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_RATIONAL_TANGENT_PROJECTIVE_STURM_NONVANISHING",
            "projective_degree": expected_degree,
            "projective_numerator": [str(value) for value in numerator],
            "known_positive_denominator": f"(1+t^2)^{degree}",
            "cauchy_sturm_bound": str(bound),
            "finite_distinct_root_count": 0,
            "infinity_value": str(infinity_value),
            "multiplier_sign": relation,
            "source": "MC-032_EXACT_RATIONAL_STURM_AUTHORITY",
            "caller_certificate_trusted": False,
            "binary_float_used": False,
            "epsilon_used": False,
            "sampling_used": False,
            "numeric_trigonometry_used": False,
            "approximate_minimization_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V17_EXACT_PROJECTIVE_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _even_trig_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    if q(rate) == 0:
        return None
    factorization = detect_even_trig_multiplier(cos_polys, sin_polys)
    if factorization is None:
        return None
    if factorization.get("status") != "SOURCE_FACTORIZATION_CERTIFIED":
        return factorization

    certificate = certify_projective_nonvanishing(
        factorization["cosine_coefficients"], factorization["sine_coefficients"]
    )
    if certificate.get("status") != "CERTIFIED":
        result = {
            "status": certificate.get("status", "BLOCKED"),
            "reason": certificate.get("reason", "PROJECTIVE_NONVANISHING_NOT_CERTIFIED"),
            "blocker": "PB-007-01",
            "factorization": factorization,
            "projective_nonvanishing": certificate,
        }
        if certificate.get("status") == "RESOURCE_REFUSAL":
            result["is_truth_value"] = False
        return result

    carrier_a = [q(value) for value in factorization["carrier_cos_polynomial"]]
    carrier_b = [q(value) for value in factorization["carrier_sin_polynomial"]]
    if EE.degree(EE.pgcd(carrier_a, carrier_b)) > 0:
        return {
            "status": "BLOCKED",
            "reason": "CARRIER_COMMON_FACTOR_REMAINS_OWNED_BY_PB00701_V8",
            "blocker": "PB-007-01",
            "factorization": factorization,
            "projective_nonvanishing": certificate,
        }

    carrier, route_kind = v15._delegate_carrier(
        carrier_a, carrier_b, int(factorization["harmonic"]), q(offset), q(rate), source_parameter_id
    )
    if carrier.get("status") != "CERTIFIED":
        return {
            "status": carrier.get("status", "BLOCKED"),
            "reason": carrier.get("reason", "CARRIER_EXACT_EVENT_ROUTE_NOT_CERTIFIED"),
            "blocker": "PB-007-01",
            "factorization": factorization,
            "projective_nonvanishing": certificate,
            "carrier_route_kind": route_kind,
            "carrier": carrier,
        }
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_PROJECTIVE_STURM_EVEN_TRIG_MULTIHARMONIC_EVENT_REDUCTION",
        "source_parameter_id": source_parameter_id,
        "factorization": factorization,
        "projective_nonvanishing": certificate,
        "carrier_route_kind": route_kind,
        "carrier": carrier,
        "zero_set_equivalence": (
            "the exact source-derived even-trigonometric multiplier has no root on the real projective line; "
            "therefore original event zeros are exactly carrier zeros"
        ),
        "multiplicity_preservation": "the exact smooth globally nonzero multiplier preserves finite carrier root multiplicities",
        "new_transcendental_zero_oracle_used": False,
        "numeric_trigonometry_used": False,
        "sampling_used": False,
    }


def analyze_even_trig_multiplier_event(spec):
    baseline = v16.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict) or baseline.get("status") == "CERTIFIED":
        return baseline
    if baseline.get("relation") != "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER":
        return baseline

    phase = baseline.get("phase_turn_law", {})
    rate = q(phase.get("rate", "0"))
    offset_global = q(phase.get("offset", "0"))
    upgraded = []
    unresolved = False
    for original_span in baseline.get("spans", []):
        span = dict(original_span)
        replacement = None
        if span.get("route", {}).get("status") != "CERTIFIED" and "cos_polynomials" in span and "sin_polynomials" in span:
            left = q(span["source_interval"][0])
            right = q(span["source_interval"][1])
            width = right - left
            cos_polys = {int(h): [q(value) for value in poly] for h, poly in span["cos_polynomials"].items()}
            sin_polys = {int(h): [q(value) for value in poly] for h, poly in span["sin_polynomials"].items()}
            replacement = _even_trig_route(
                cos_polys,
                sin_polys,
                offset_global + rate * left,
                rate * width,
                baseline["source_parameter_id"],
            )
        if replacement is not None:
            span["route_kind"] = "PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER"
            span["route"] = replacement
            span["local_phase_turn_law"] = {
                "offset": str(offset_global + rate * q(span["source_interval"][0])),
                "rate": str(rate * (q(span["source_interval"][1]) - q(span["source_interval"][0]))),
                "local_parameter": "s=(u-lo)/(hi-lo)",
                "shared_parameter": baseline["source_parameter_id"],
            }
        if span.get("route", {}).get("status") != "CERTIFIED":
            unresolved = True
        upgraded.append(span)

    statuses = [span.get("route", {}).get("status") for span in upgraded]
    if "RESOURCE_REFUSAL" in statuses:
        status = "RESOURCE_REFUSAL"
    elif "SEMANTIC_BLOCKER" in statuses:
        status = "SEMANTIC_BLOCKER"
    elif unresolved:
        status = "BLOCKED"
    else:
        status = "CERTIFIED"
    result = dict(baseline)
    result["status"] = status
    result["spans"] = upgraded
    result["relation"] = (
        "FINITE_EXACT_PIECEWISE_PROJECTIVE_EVEN_TRIG_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v17_even_trig_projective_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "factorization", "lambda_vector", "cosine_coefficients", "sine_coefficients",
            "projective_numerator", "projective_certificate", "sturm_certificate",
            "sturm_root_count", "multiplier_sign", "root_free", "infinity_value",
            "nonvanishing_certificate",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_even_trig_multiplier_event(source_spec)
        return v16.classify_required_analytic_event(source_spec)
    return v16.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V17_PROJECTIVE_STURM_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
