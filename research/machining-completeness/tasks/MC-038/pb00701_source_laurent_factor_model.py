#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from math import comb, gcd as int_gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_even_trig_multiplier_model as v17  # noqa: E402

v16 = v17.v16
v15 = v17.v15
EE = v17.EE
q = v17.q

V18_SOURCE_ROUTE = "EXACT_NONVANISHING_SOURCE_MODULE_FACTOR_REDUCTION"
V18_LAURENT_ROUTE = "EXACT_LAURENT_MODULE_NONVANISHING_FACTOR_REDUCTION"


class SourceLaurentFactorRefusal(RuntimeError):
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
    return _trim([scalar * value for value in _trim(poly)])


def _pmul(left, right):
    left = _trim(left)
    right = _trim(right)
    out = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return _trim(out)


def _pdiv_exact(numerator, denominator):
    numerator = _trim(numerator)
    denominator = _trim(denominator)
    if denominator == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    if len(numerator) < len(denominator):
        return [Fraction(0)], numerator
    remainder = list(numerator)
    quotient = [Fraction(0)] * (len(numerator) - len(denominator) + 1)
    while remainder != [0] and len(remainder) >= len(denominator):
        shift = len(remainder) - len(denominator)
        coefficient = remainder[-1] / denominator[-1]
        quotient[shift] += coefficient
        for index, value in enumerate(denominator):
            remainder[index + shift] -= coefficient * value
        remainder = _trim(remainder)
    return _trim(quotient), _trim(remainder)


def _monic(poly):
    poly = _trim(poly)
    if poly == [0]:
        return poly
    return _pscale(poly, Fraction(1, 1) / poly[-1])


def _common_source_factor(cos_polys, sin_polys):
    polynomials = []
    for mapping in (cos_polys, sin_polys):
        for poly in mapping.values():
            value = _trim(poly)
            if value != [0]:
                polynomials.append(value)
    if not polynomials:
        return None
    common = polynomials[0]
    for poly in polynomials[1:]:
        common = EE.pgcd(common, poly)
    common = _monic(common)
    return common if EE.degree(common) > 0 else None


def certify_source_factor_nonvanishing(poly):
    """Prove an exact rational source factor has no zero on closed [0,1]."""
    try:
        poly = _trim(poly)
        if EE.degree(poly) <= 0:
            return {
                "status": "BLOCKED",
                "reason": "SOURCE_FACTOR_NOT_NONCONSTANT",
                "blocker": "PB-007-01",
            }
        left = EE.exact_event(poly, Fraction(0))
        right = EE.exact_event(poly, Fraction(1))
        if left.get("relation") == "ZERO" or right.get("relation") == "ZERO":
            return {
                "status": "BLOCKED",
                "reason": "SOURCE_FACTOR_ENDPOINT_ROOT",
                "blocker": "PB-007-01",
                "left_event": left,
                "right_event": right,
                "factor": [str(value) for value in poly],
            }
        roots = EE.distinct_roots_open(poly, Fraction(0), Fraction(1))
        if roots:
            return {
                "status": "BLOCKED",
                "reason": "SOURCE_FACTOR_INTERIOR_REAL_ROOT",
                "blocker": "PB-007-01",
                "distinct_roots_open": int(roots),
                "left_event": left,
                "right_event": right,
                "factor": [str(value) for value in poly],
            }
        left_relation = left.get("relation")
        right_relation = right.get("relation")
        if left_relation not in {"POSITIVE", "NEGATIVE"} or right_relation != left_relation:
            raise ArithmeticError("exact source-factor sign unavailable")
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_RATIONAL_CLOSED_INTERVAL_STURM_NONVANISHING",
            "factor": [str(value) for value in poly],
            "source_interval": ["0", "1"],
            "left_event": left,
            "right_event": right,
            "distinct_roots_open": 0,
            "factor_sign": left_relation,
            "source": "MC-032_EXACT_RATIONAL_STURM_AUTHORITY",
            "caller_certificate_trusted": False,
            "binary_float_used": False,
            "epsilon_used": False,
            "sampling_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V18_SOURCE_FACTOR_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _power_to_clamped_spline(poly):
    """Convert exact power coefficients on [0,1] to one clamped Bezier span."""
    poly = _trim(poly)
    degree = EE.degree(poly)
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


def _residual_spec(cos_polys, sin_polys, offset, rate, source_parameter_id):
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": {
            str(h): _power_to_clamped_spline(poly)
            for h, poly in sorted(cos_polys.items()) if _trim(poly) != [0]
        },
        "sin_splines": {
            str(h): _power_to_clamped_spline(poly)
            for h, poly in sorted(sin_polys.items()) if _trim(poly) != [0]
        },
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": str(q(offset)),
        "phase_turn_rate": str(q(rate)),
        "source_parameter_id": source_parameter_id,
        "parameter_projection": source_parameter_id,
    }


def _delegate_residual(cos_polys, sin_polys, offset, rate, source_parameter_id):
    return v17.classify_required_analytic_event(
        _residual_spec(cos_polys, sin_polys, offset, rate, source_parameter_id)
    )


def _source_factor_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    factor = _common_source_factor(cos_polys, sin_polys)
    if factor is None:
        return None
    certificate = certify_source_factor_nonvanishing(factor)
    if certificate.get("status") != "CERTIFIED":
        return {
            "status": certificate.get("status", "BLOCKED"),
            "reason": certificate.get("reason", "SOURCE_FACTOR_NONVANISHING_NOT_CERTIFIED"),
            "blocker": "PB-007-01",
            "source_factor": [str(value) for value in factor],
            "source_factor_nonvanishing": certificate,
            **({"is_truth_value": False} if certificate.get("status") == "RESOURCE_REFUSAL" else {}),
        }

    residual_cos = {}
    residual_sin = {}
    division_proof = []
    for kind, mapping, output in (
        ("cos", cos_polys, residual_cos), ("sin", sin_polys, residual_sin)
    ):
        for harmonic, original in sorted(mapping.items()):
            original = _trim(original)
            if original == [0]:
                continue
            quotient, remainder = _pdiv_exact(original, factor)
            if remainder != [0]:
                return {
                    "status": "BLOCKED",
                    "reason": "SOURCE_FACTOR_EXACT_DIVISION_FAILED",
                    "blocker": "PB-007-01",
                }
            if _pmul(factor, quotient) != original:
                return {
                    "status": "BLOCKED",
                    "reason": "SOURCE_FACTOR_REGENERATION_FAILED",
                    "blocker": "PB-007-01",
                }
            output[int(harmonic)] = quotient
            division_proof.append({
                "channel": kind,
                "harmonic": int(harmonic),
                "source": [str(value) for value in original],
                "quotient": [str(value) for value in quotient],
                "remainder": [str(value) for value in remainder],
            })

    residual = _delegate_residual(
        residual_cos, residual_sin, q(offset), q(rate), source_parameter_id
    )
    if residual.get("status") != "CERTIFIED":
        return {
            "status": residual.get("status", "BLOCKED"),
            "reason": residual.get("reason", "RESIDUAL_CARRIER_EXACT_EVENT_ROUTE_NOT_CERTIFIED"),
            "blocker": "PB-007-01",
            "source_factor": [str(value) for value in factor],
            "source_factor_nonvanishing": certificate,
            "division_proof": division_proof,
            "residual": residual,
            **({"is_truth_value": False} if residual.get("status") == "RESOURCE_REFUSAL" else {}),
        }
    return {
        "status": "CERTIFIED",
        "relation": V18_SOURCE_ROUTE,
        "source_parameter_id": source_parameter_id,
        "source_factor": [str(value) for value in factor],
        "source_factor_nonvanishing": certificate,
        "division_proof": division_proof,
        "residual": residual,
        "zero_set_equivalence": (
            "the exact maximal common source-polynomial factor is nonzero on the closed local source span; "
            "therefore source-event zeros are exactly residual zeros"
        ),
        "multiplicity_preservation": (
            "multiplication by an exact smooth source factor that is nowhere zero on the closed span "
            "preserves every finite residual event-root multiplicity"
        ),
        "caller_factorization_trusted": False,
        "sampling_used": False,
        "epsilon_used": False,
    }


# --- Exact Gaussian-rational polynomial / Laurent-module authority ---

def _gpoly_zero(poly):
    value = v17._gpoly_trim(poly)
    return len(value) == 1 and v17._gzero(value[0])


def _gpoly_divmod(numerator, denominator):
    numerator = v17._gpoly_trim(numerator)
    denominator = v17._gpoly_trim(denominator)
    if _gpoly_zero(denominator):
        raise ZeroDivisionError("Gaussian polynomial division by zero")
    if len(numerator) < len(denominator):
        return [v17._g()], numerator
    remainder = list(numerator)
    quotient = [v17._g()] * (len(numerator) - len(denominator) + 1)
    while not _gpoly_zero(remainder) and len(remainder) >= len(denominator):
        shift = len(remainder) - len(denominator)
        coefficient = v17._gdiv(remainder[-1], denominator[-1])
        quotient[shift] = v17._gadd(quotient[shift], coefficient)
        for index, value in enumerate(denominator):
            at = index + shift
            remainder[at] = v17._gsub(remainder[at], v17._gmul(coefficient, value))
        remainder = v17._gpoly_trim(remainder)
    return v17._gpoly_trim(quotient), v17._gpoly_trim(remainder)


def _gpoly_monic(poly):
    poly = v17._gpoly_trim(poly)
    if _gpoly_zero(poly):
        return poly
    return v17._gpoly_scale(poly, v17._gdiv(v17._g(1), poly[-1]))


def _gpoly_gcd(left, right):
    left = v17._gpoly_trim(left)
    right = v17._gpoly_trim(right)
    while not _gpoly_zero(right):
        _, remainder = _gpoly_divmod(left, right)
        left, right = right, remainder
    return _gpoly_monic(left)


def _serialize_gpoly(poly):
    return [v17._gstr(value) for value in v17._gpoly_trim(poly)]


def _odd_harmonic_layout(cos_polys, sin_polys):
    harmonics = sorted({int(h) for h in cos_polys} | {int(h) for h in sin_polys})
    harmonics = [h for h in harmonics if _trim(cos_polys.get(h, [0])) != [0] or _trim(sin_polys.get(h, [0])) != [0]]
    if not harmonics or any(h <= 0 for h in harmonics):
        return None
    base = 0
    for harmonic in harmonics:
        base = int_gcd(base, harmonic)
    if base <= 0 or any((h // base) % 2 != 1 for h in harmonics):
        return None
    top_ratio = max(harmonics) // base
    if top_ratio % 2 != 1:
        return None
    radius = (top_ratio - 1) // 2
    if radius < 1:
        return None
    return base, radius


def _source_laurent_slices(cos_polys, sin_polys, base, radius):
    qpolys = []
    source_degree = 0
    for r in range(radius + 1):
        harmonic = (2 * r + 1) * base
        qpoly = v17._complex_source_poly(cos_polys.get(harmonic, [0]), sin_polys.get(harmonic, [0]))
        qpolys.append(qpoly)
        source_degree = max(source_degree, len(qpoly) - 1)
    slices = []
    for source_power in range(source_degree + 1):
        row = [v17._g()] * (2 * radius + 2)
        for r, qpoly in enumerate(qpolys):
            value = qpoly[source_power] if source_power < len(qpoly) else v17._g()
            row[radius - r] = v17._gadd(row[radius - r], v17._gconj(value))
            row[radius + r + 1] = v17._gadd(row[radius + r + 1], value)
        slices.append(v17._gpoly_trim(row))
    return qpolys, slices


def _canonical_even_multiplier(gcd_poly):
    gcd_poly = _gpoly_monic(gcd_poly)
    degree = len(gcd_poly) - 1
    if degree <= 0:
        return None
    if degree % 2:
        return {
            "status": "BLOCKED",
            "reason": "LAURENT_COMMON_FACTOR_HAS_ODD_DEGREE",
            "blocker": "PB-007-01",
            "laurent_gcd": _serialize_gpoly(gcd_poly),
        }
    if v17._gzero(gcd_poly[0]):
        return {
            "status": "BLOCKED",
            "reason": "LAURENT_COMMON_FACTOR_HAS_ZERO_EXTREME_COEFFICIENT",
            "blocker": "PB-007-01",
            "laurent_gcd": _serialize_gpoly(gcd_poly),
        }
    rho = v17._gconj(gcd_poly[0])
    if v17._gmul(rho, v17._gconj(rho)) != v17._g(1):
        return {
            "status": "BLOCKED",
            "reason": "LAURENT_COMMON_FACTOR_NOT_CONJUGATE_RECIPROCAL_UP_TO_PHASE",
            "blocker": "PB-007-01",
            "laurent_gcd": _serialize_gpoly(gcd_poly),
        }
    if rho == v17._g(-1):
        scale = v17._g(0, 1)
    else:
        scale = v17._gadd(v17._g(1), rho)
        if v17._gzero(scale):
            return {
                "status": "BLOCKED",
                "reason": "LAURENT_COMMON_FACTOR_PHASE_NORMALIZATION_FAILED",
                "blocker": "PB-007-01",
            }
    if v17._gdiv(scale, v17._gconj(scale)) != rho:
        raise AssertionError("exact conjugate-reciprocal phase normalization failed")
    factor = v17._gpoly_scale(gcd_poly, scale)
    for index, value in enumerate(factor):
        if value != v17._gconj(factor[degree - index]):
            return {
                "status": "BLOCKED",
                "reason": "LAURENT_COMMON_FACTOR_NOT_CONJUGATE_RECIPROCAL",
                "blocker": "PB-007-01",
                "laurent_gcd": _serialize_gpoly(gcd_poly),
            }
    half = degree // 2
    if factor[half][1] != 0:
        raise AssertionError("real even-trigonometric center coefficient is not real")
    cosine = [Fraction(0)] * (half + 1)
    sine = [Fraction(0)] * (half + 1)
    cosine[0] = factor[half][0]
    for k in range(1, half + 1):
        coefficient = factor[half + k]
        cosine[k] = 2 * coefficient[0]
        sine[k] = -2 * coefficient[1]
    certificate = v17.certify_projective_nonvanishing(cosine, sine)
    if certificate.get("status") != "CERTIFIED":
        return {
            "status": certificate.get("status", "BLOCKED"),
            "reason": certificate.get("reason", "LAURENT_MULTIPLIER_NONVANISHING_NOT_CERTIFIED"),
            "blocker": "PB-007-01",
            "laurent_gcd": _serialize_gpoly(gcd_poly),
            "normalized_factor": _serialize_gpoly(factor),
            "cosine_coefficients": [str(value) for value in cosine],
            "sine_coefficients": [str(value) for value in sine],
            "projective_nonvanishing": certificate,
            **({"is_truth_value": False} if certificate.get("status") == "RESOURCE_REFUSAL" else {}),
        }
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_GAUSSIAN_LAURENT_CONJUGATE_RECIPROCAL_EVEN_TRIG_FACTOR",
        "laurent_gcd": _serialize_gpoly(gcd_poly),
        "normalized_factor": _serialize_gpoly(factor),
        "factor_degree": degree,
        "multiplier_degree": half,
        "cosine_coefficients": [str(value) for value in cosine],
        "sine_coefficients": [str(value) for value in sine],
        "projective_nonvanishing": certificate,
        "caller_factorization_trusted": False,
    }


def detect_laurent_module_factor(cos_polys, sin_polys):
    """Extract a canonical source-independent even-trig Laurent factor, if exact."""
    layout = _odd_harmonic_layout(cos_polys, sin_polys)
    if layout is None:
        return None
    base, radius = layout
    source_q, slices = _source_laurent_slices(cos_polys, sin_polys, base, radius)
    nonzero = [row for row in slices if not _gpoly_zero(row)]
    if len(nonzero) < 2:
        return {
            "status": "BLOCKED",
            "reason": "LAURENT_FACTOR_UNDERDETERMINED_SINGLE_SOURCE_SLICE",
            "blocker": "PB-007-01",
        }
    common = nonzero[0]
    for row in nonzero[1:]:
        common = _gpoly_gcd(common, row)
    common = _gpoly_monic(common)
    if len(common) <= 1:
        return None
    normalized = _canonical_even_multiplier(common)
    if normalized is None or normalized.get("status") != "CERTIFIED":
        return normalized
    factor = [(q(item["re"]), q(item["im"])) for item in normalized["normalized_factor"]]
    factor_degree = len(factor) - 1
    multiplier_degree = factor_degree // 2
    if multiplier_degree > radius:
        return {
            "status": "BLOCKED",
            "reason": "LAURENT_FACTOR_CONSUMES_ODD_CARRIER_STRUCTURE",
            "blocker": "PB-007-01",
        }
    residual_radius = radius - multiplier_degree
    residual_degree = 2 * residual_radius + 1
    quotient_slices = []
    for row in slices:
        if _gpoly_zero(row):
            quotient_slices.append([v17._g()])
            continue
        quotient, remainder = _gpoly_divmod(row, factor)
        if not _gpoly_zero(remainder):
            return {
                "status": "BLOCKED",
                "reason": "LAURENT_FACTOR_EXACT_DIVISION_FAILED",
                "blocker": "PB-007-01",
            }
        if v17._gpoly_trim(_gpoly_mul(factor, quotient)) != v17._gpoly_trim(row):
            return {
                "status": "BLOCKED",
                "reason": "LAURENT_FACTOR_REGENERATION_FAILED",
                "blocker": "PB-007-01",
            }
        if len(quotient) - 1 > residual_degree:
            return {
                "status": "BLOCKED",
                "reason": "LAURENT_RESIDUAL_DEGREE_INCONSISTENT",
                "blocker": "PB-007-01",
            }
        padded = list(quotient) + [v17._g()] * (residual_degree + 1 - len(quotient))
        for index in range(residual_degree + 1):
            if padded[index] != v17._gconj(padded[residual_degree - index]):
                return {
                    "status": "BLOCKED",
                    "reason": "LAURENT_RESIDUAL_NOT_REAL_ODD_HARMONIC_SOURCE",
                    "blocker": "PB-007-01",
                }
        quotient_slices.append(padded)

    residual_cos = {((2 * r + 1) * base): [] for r in range(residual_radius + 1)}
    residual_sin = {((2 * r + 1) * base): [] for r in range(residual_radius + 1)}
    for row in quotient_slices:
        for r in range(residual_radius + 1):
            coefficient = row[residual_radius + r + 1]
            harmonic = (2 * r + 1) * base
            residual_cos[harmonic].append(coefficient[0])
            residual_sin[harmonic].append(-coefficient[1])
    residual_cos = {h: _trim(poly) for h, poly in residual_cos.items() if _trim(poly) != [0]}
    residual_sin = {h: _trim(poly) for h, poly in residual_sin.items() if _trim(poly) != [0]}
    if not residual_cos and not residual_sin:
        return {
            "status": "BLOCKED",
            "reason": "LAURENT_FACTOR_LEFT_EMPTY_RESIDUAL",
            "blocker": "PB-007-01",
        }

    # Rebuild the original positive-frequency source polynomials from the exact
    # quotient slices, then compare them to the source maps channel by channel.
    rebuilt_q = []
    max_source_power = len(quotient_slices) - 1
    for r in range(radius + 1):
        rebuilt_q.append([v17._g()] * (max_source_power + 1))
    regenerated_slices = []
    for row in quotient_slices:
        regenerated_slices.append(v17._gpoly_trim(_gpoly_mul(factor, row)))
    for source_power, row in enumerate(regenerated_slices):
        padded = list(row) + [v17._g()] * (2 * radius + 2 - len(row))
        for r in range(radius + 1):
            rebuilt_q[r][source_power] = padded[radius + r + 1]
    for r in range(radius + 1):
        if v17._gpoly_trim(rebuilt_q[r]) != v17._gpoly_trim(source_q[r]):
            return {
                "status": "BLOCKED",
                "reason": "LAURENT_SOURCE_COEFFICIENT_REGENERATION_FAILED",
                "blocker": "PB-007-01",
            }

    return {
        "status": "SOURCE_LAURENT_FACTORIZATION_CERTIFIED",
        "relation": "EXACT_GAUSSIAN_LAURENT_SOURCE_MODULE_FACTORIZATION",
        "base_harmonic": base,
        "source_radius": radius,
        "multiplier_degree": multiplier_degree,
        "factor": normalized,
        "residual_cos_polynomials": {
            str(h): [str(value) for value in poly] for h, poly in sorted(residual_cos.items())
        },
        "residual_sin_polynomials": {
            str(h): [str(value) for value in poly] for h, poly in sorted(residual_sin.items())
        },
        "residual_harmonics": sorted(set(residual_cos) | set(residual_sin)),
        "source_regeneration_verified_exactly": True,
        "caller_factorization_trusted": False,
    }


def _gpoly_mul(left, right):
    left = v17._gpoly_trim(left)
    right = v17._gpoly_trim(right)
    out = [v17._g()] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = v17._gadd(out[i + j], v17._gmul(a, b))
    return v17._gpoly_trim(out)


def _laurent_factor_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    factorization = detect_laurent_module_factor(cos_polys, sin_polys)
    if factorization is None:
        return None
    if factorization.get("status") != "SOURCE_LAURENT_FACTORIZATION_CERTIFIED":
        return factorization
    residual_cos = {
        int(h): [q(value) for value in poly]
        for h, poly in factorization["residual_cos_polynomials"].items()
    }
    residual_sin = {
        int(h): [q(value) for value in poly]
        for h, poly in factorization["residual_sin_polynomials"].items()
    }
    residual = _delegate_residual(
        residual_cos, residual_sin, q(offset), q(rate), source_parameter_id
    )
    if residual.get("status") != "CERTIFIED":
        return {
            "status": residual.get("status", "BLOCKED"),
            "reason": residual.get("reason", "RESIDUAL_CARRIER_EXACT_EVENT_ROUTE_NOT_CERTIFIED"),
            "blocker": "PB-007-01",
            "laurent_factorization": factorization,
            "residual": residual,
            **({"is_truth_value": False} if residual.get("status") == "RESOURCE_REFUSAL" else {}),
        }
    return {
        "status": "CERTIFIED",
        "relation": V18_LAURENT_ROUTE,
        "source_parameter_id": source_parameter_id,
        "laurent_factorization": factorization,
        "residual": residual,
        "zero_set_equivalence": (
            "the exact source-derived even-trigonometric Laurent factor is globally nonzero by v17 projective Sturm authority; "
            "therefore original event zeros are exactly residual zeros"
        ),
        "multiplicity_preservation": (
            "multiplication by an exact smooth globally nonzero even-trigonometric factor preserves finite residual multiplicities"
        ),
        "caller_factorization_trusted": False,
    }


def analyze_source_laurent_factor_event(spec):
    baseline = v17.classify_required_analytic_event(spec)
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
            local_offset = offset_global + rate * left
            local_rate = rate * width
            cos_polys = {int(h): [q(value) for value in poly] for h, poly in span["cos_polynomials"].items()}
            sin_polys = {int(h): [q(value) for value in poly] for h, poly in span["sin_polynomials"].items()}
            replacement = _source_factor_route(
                cos_polys, sin_polys, local_offset, local_rate, baseline["source_parameter_id"]
            )
            route_kind = "PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR"
            if replacement is None:
                replacement = _laurent_factor_route(
                    cos_polys, sin_polys, local_offset, local_rate, baseline["source_parameter_id"]
                )
                route_kind = "PB00701_V18_EXACT_LAURENT_MODULE_FACTOR"
            if replacement is not None:
                span["route_kind"] = route_kind
                span["route"] = replacement
                span["local_phase_turn_law"] = {
                    "offset": str(local_offset),
                    "rate": str(local_rate),
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
        "FINITE_EXACT_PIECEWISE_SOURCE_LAURENT_MODULE_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v18_source_laurent_module_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "factorization", "source_factor", "source_factor_certificate", "source_factor_nonvanishing",
            "laurent_factor", "laurent_gcd", "laurent_factorization", "residual_source",
            "projective_certificate", "sturm_certificate", "sturm_root_count", "multiplier_sign",
            "root_free", "nonvanishing_certificate",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_source_laurent_factor_event(source_spec)
        return v17.classify_required_analytic_event(source_spec)
    return v17.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V18_SOURCE_LAURENT_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
