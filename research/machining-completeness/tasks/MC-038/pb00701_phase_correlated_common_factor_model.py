#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_source_adaptive_separator_model as v30  # noqa: E402

q = v30.q
v29 = v30.v29
v24 = v30.v24
v22 = v30.v22
v20 = v30.v20
v19 = v30.v19

V34_ROUTE = "EXACT_PHASE_CORRELATED_EQUAL_QUADRATURE_COMMON_FACTOR_DERIVATIVE_AUTHORITY"
SQRT2_LOWER = Fraction(238, 169)
SQRT2_UPPER = Fraction(99, 70)
ROTATED_PHASE_LOWER = SQRT2_LOWER * Fraction(12, 13)  # 2856/2197
ROTATED_AMPLITUDE_UPPER = SQRT2_UPPER * Fraction(5, 13)  # 99/182


class CorrelatedCommonFactorRefusal(RuntimeError):
    """Exact-resource refusal. Refusal is never a truth value."""


def _trim(poly):
    return v30._trim([q(x) for x in poly])


def _floor(x):
    x = q(x)
    return x.numerator // x.denominator


def _ceil(x):
    x = q(x)
    return -((-x.numerator) // x.denominator)


def _sign(x):
    x = q(x)
    return 1 if x > 0 else -1 if x < 0 else 0


def _diagonal_phase_cell_certificate(lo, hi):
    """Exact cell around theta=-pi/4+k*pi, expressed in turns.

    The accepted family is [-3/16+k/2,-1/16+k/2].  After the exact shift
    u_turn=t+1/8-k/2, the interval lies in [-1/16,1/16], so v29's qualified
    5-12-13 COS cell applies to cos(u), while sin(u) is the transverse term.
    """
    lo, hi = q(lo), q(hi)
    if lo > hi:
        lo, hi = hi, lo
    if hi - lo > Fraction(1, 8):
        return None

    first = _floor(2 * (lo + Fraction(3, 16))) - 2
    last = _ceil(2 * (hi + Fraction(1, 16))) + 2
    nested = v29._phase_cell_certificate("COS", Fraction(-1, 16), Fraction(1, 16))
    if nested is None:
        raise AssertionError("qualified v29 centered COS cell unavailable")

    for k in range(first, last + 1):
        shift = Fraction(k, 2)
        left = Fraction(-3, 16) + shift
        right = Fraction(-1, 16) + shift
        if left <= lo and hi <= right:
            projection_sign = 1 if k % 2 == 0 else -1
            return {
                "status": "CERTIFIED",
                "relation": "EXACT_DIAGONAL_RATIONAL_TURN_PHASE_CORRELATION_CELL",
                "harmonic_phase_interval": [str(lo), str(hi)],
                "cell_interval": [str(left), str(right)],
                "half_turn_index": k,
                "projection_sign_number": projection_sign,
                "projection_sign": "POSITIVE" if projection_sign > 0 else "NEGATIVE",
                "rotation_identity": (
                    "with u=2*pi*(t+1/8-k/2): cos(theta)+sin(theta)=(-1)^k*sqrt(2)*sin(u), "
                    "cos(theta)-sin(theta)=(-1)^k*sqrt(2)*cos(u)"
                ),
                "rotated_u_turn_interval": [str(lo + Fraction(1, 8) - shift), str(hi + Fraction(1, 8) - shift)],
                "v29_nested_cell_certificate": nested,
                "sqrt2_lower": str(SQRT2_LOWER),
                "sqrt2_lower_integer_proof": "57122 > 56644, so sqrt(2)>238/169",
                "sqrt2_upper": str(SQRT2_UPPER),
                "sqrt2_upper_integer_proof": "9801 > 9800, so sqrt(2)<99/70",
                "rotated_phase_rational_lower_bound": str(ROTATED_PHASE_LOWER),
                "rotated_amplitude_rational_upper_bound": str(ROTATED_AMPLITUDE_UPPER),
                "caller_cell_trusted": False,
                "binary_float_used": False,
                "sampling_used": False,
                "epsilon_used": False,
                "numerical_trigonometry_used": False,
            }
    return None


def _common_factor_sign_certificate(g):
    cert = v30.v26._fixed_sign_sturm_certificate(_trim(g), "COMMON_FACTOR")
    if cert.get("status") == "RESOURCE_REFUSAL":
        return cert
    if cert.get("status") != "CERTIFIED":
        return {
            "status": "BLOCKED",
            "reason": "V34_COMMON_FACTOR_STRICT_SIGN_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "underlying_certificate": cert,
        }
    return cert


def _remaining_residual_terms(cos_polys, sin_polys, phase_rate, harmonic):
    positive, terms, polynomials = v24._mixed_residual_envelope_terms(
        cos_polys, sin_polys, phase_rate, harmonic
    )
    kept_terms = []
    kept_polys = []
    for term, poly in zip(terms, polynomials):
        if int(term["harmonic"]) == int(harmonic) and term["kind"] in ("C_prime", "S_prime"):
            continue
        kept_terms.append(term)
        kept_polys.append(_trim(poly))
    return positive, kept_terms, kept_polys


def _joint_derivative_certificate(cos_polys, sin_polys, phase_rate, harmonic, g, sign_number):
    """Jointly bound G'(cos+sin)+2*pi*h*r*G(cos-sin)."""
    try:
        rate = q(phase_rate)
        harmonic = int(harmonic)
        sign_number = int(sign_number)
        g = _trim(g)
        if rate == 0 or harmonic <= 0 or sign_number not in (-1, 1):
            return None

        positive, terms, residuals = _remaining_residual_terms(
            cos_polys, sin_polys, rate, harmonic
        )
        gp = _trim(v19._deriv(g))
        phase_scale = 6 * abs(Fraction(harmonic) * rate) * ROTATED_PHASE_LOWER
        phase_base = v22._pscale(g, phase_scale * Fraction(sign_number))
        amplitude_scaled = v22._pscale(gp, ROTATED_AMPLITUDE_UPPER)

        total_signed_terms = (0 if gp == [0] else 1) + len(residuals)
        orthant_count = 1 << total_signed_terms
        certificates = []
        for mask in range(orthant_count):
            margin = list(phase_base)
            bit = 0
            gp_sign = None
            if gp != [0]:
                gp_sign = 1 if (mask & 1) else -1
                margin = v22._padd(margin, v22._pscale(amplitude_scaled, -gp_sign))
                bit = 1
            residual_signs = []
            for index, poly in enumerate(residuals):
                sgn = 1 if (mask >> (index + bit)) & 1 else -1
                residual_signs.append(sgn)
                margin = v22._padd(margin, v22._pscale(poly, -sgn))
            margin = _trim(margin)
            cert = v20._strict_positive_certificate(
                margin, f"PB00701_V34_CORRELATED_ORTHANT_{mask}"
            )
            if cert.get("status") == "RESOURCE_REFUSAL":
                return {
                    **cert,
                    "reason": f"PB00701_V34_CORRELATED_ORTHANT_{mask}_RESOURCE_REFUSAL",
                    "is_truth_value": False,
                }
            if cert.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "V34_PHASE_CORRELATED_JOINT_DERIVATIVE_STRICT_DOMINANCE_NOT_CERTIFIED",
                    "blocker": "PB-007-01",
                    "failed_orthant": mask,
                    "failed_common_factor_derivative_sign": gp_sign,
                    "failed_residual_signs": residual_signs,
                    "failed_margin_polynomial": [str(x) for x in margin],
                    "failed_margin_certificate": cert,
                    "common_factor_derivative_polynomial": [str(x) for x in gp],
                    "remaining_residual_terms": terms,
                    "orthant_count": orthant_count,
                }
            certificates.append({
                "orthant": mask,
                "common_factor_derivative_sign": gp_sign,
                "residual_signs": residual_signs,
                "margin_polynomial": [str(x) for x in margin],
                "certificate": cert,
            })

        return {
            "status": "CERTIFIED",
            "relation": "EXACT_PHASE_CORRELATED_COMMON_FACTOR_PLUS_NONANCHOR_RESIDUAL_ORTHANT_DOMINANCE",
            "harmonic": harmonic,
            "common_factor_polynomial": [str(x) for x in g],
            "common_factor_sign_number": sign_number,
            "common_factor_derivative_polynomial": [str(x) for x in gp],
            "selected_amplitude_derivative_identity": "C'=S'=G'; selected amplitude contribution is G'(cos(theta)+sin(theta))",
            "selected_phase_derivative_identity": "selected phase contribution is 2*pi*h*r*G*(cos(theta)-sin(theta))",
            "rotated_phase_lower_bound": str(ROTATED_PHASE_LOWER),
            "rotated_amplitude_upper_bound": str(ROTATED_AMPLITUDE_UPPER),
            "phase_scale": str(phase_scale),
            "active_positive_harmonics": positive,
            "remaining_residual_terms": terms,
            "remaining_residual_term_count": len(residuals),
            "orthant_count": orthant_count,
            "orthant_certificates": certificates,
            "strict_relation": (
                "6*|h*r|*(2856/2197)*|G(s)| - (99/182)*|G'(s)| "
                "- sum_i |R_i(s)| > 0 on the complete closed source span"
            ),
            "selected_C_prime_and_S_prime_independently_counted": False,
            "selected_phase_C_and_phase_S_independently_counted": False,
            "nonanchor_residuals_preserved": True,
            "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "finite_termination": "finite exact rational sign-orthant enumeration after one exact diagonal-cell decision",
            "caller_certificate_trusted": False,
            "binary_float_used": False,
            "sampling_used": False,
            "epsilon_used": False,
            "numerical_trigonometry_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V34_CORRELATED_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _correlated_anchor(cos_polys, sin_polys, offset, rate, harmonic):
    c = _trim(cos_polys.get(harmonic, [0]))
    s = _trim(sin_polys.get(harmonic, [0]))
    if c == [0] or s == [0] or c != s:
        return {
            "status": "BLOCKED",
            "reason": "V34_EQUAL_QUADRATURE_COMMON_FACTOR_NOT_PRESENT",
            "blocker": "PB-007-01",
        }

    sign_cert = _common_factor_sign_certificate(c)
    if sign_cert.get("status") != "CERTIFIED":
        return sign_cert
    sign_number = int(sign_cert["amplitude_sign_number"])

    t0 = Fraction(int(harmonic)) * q(offset)
    t1 = Fraction(int(harmonic)) * (q(offset) + q(rate))
    cell = _diagonal_phase_cell_certificate(min(t0, t1), max(t0, t1))
    if cell is None:
        return {
            "status": "BLOCKED",
            "reason": "V34_EXACT_DIAGONAL_PHASE_CELL_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "harmonic_phase_interval": [str(min(t0, t1)), str(max(t0, t1))],
        }

    joint = _joint_derivative_certificate(
        cos_polys, sin_polys, rate, harmonic, c, sign_number
    )
    if joint is None or joint.get("status") != "CERTIFIED":
        if joint is None:
            return {"status": "BLOCKED", "reason": "V34_JOINT_DERIVATIVE_UNAVAILABLE", "blocker": "PB-007-01"}
        return {
            "status": joint.get("status", "BLOCKED"),
            "reason": joint.get("reason", "V34_JOINT_DERIVATIVE_NOT_CERTIFIED"),
            "blocker": None if joint.get("status") == "RESOURCE_REFUSAL" else "PB-007-01",
            "common_factor_sign_certificate": sign_cert,
            "diagonal_phase_cell_certificate": cell,
            "joint_derivative_certificate": joint,
            **({"is_truth_value": False} if joint.get("status") == "RESOURCE_REFUSAL" else {}),
        }

    projection_sign = int(cell["projection_sign_number"])
    derivative_sign = _sign(Fraction(int(harmonic)) * q(rate)) * sign_number * projection_sign
    if derivative_sign == 0:
        raise AssertionError("certified v34 anchor lost derivative direction")
    return {
        "status": "CERTIFIED",
        "relation": V34_ROUTE,
        "harmonic": int(harmonic),
        "common_factor_sign_certificate": sign_cert,
        "diagonal_phase_cell_certificate": cell,
        "joint_derivative_certificate": joint,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "derivative_sign_number": derivative_sign,
        "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(q(rate))},
        "both_selected_amplitude_derivatives_consumed_jointly": True,
        "both_selected_phase_terms_consumed_jointly": True,
        "nonanchor_residuals_preserved": True,
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
    }


def _correlated_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    if source_parameter_id != "s":
        return {
            "status": "SEMANTIC_BLOCKER",
            "reason": "SOURCE_PARAMETER_MISMATCH",
            "blocker": "PB-007-01",
        }
    candidates = sorted(
        int(h) for h in (set(cos_polys) | set(sin_polys))
        if int(h) > 0 and _trim(cos_polys.get(h, [0])) == _trim(sin_polys.get(h, [0]))
        and _trim(cos_polys.get(h, [0])) != [0]
    )
    attempts = []
    for harmonic in candidates:
        anchor = _correlated_anchor(cos_polys, sin_polys, offset, rate, harmonic)
        if anchor.get("status") == "RESOURCE_REFUSAL":
            return anchor
        if anchor.get("status") != "CERTIFIED":
            attempts.append(anchor)
            continue

        left_event = v19._endpoint_relation(cos_polys, sin_polys, Fraction(0), q(offset))
        if left_event.get("status") == "RESOURCE_REFUSAL":
            return left_event
        right_event = v19._endpoint_relation(cos_polys, sin_polys, Fraction(1), q(offset) + q(rate))
        if right_event.get("status") == "RESOURCE_REFUSAL":
            return right_event
        root_summary = v19._root_summary(anchor["direction"], left_event, right_event)
        if root_summary.get("status") != "CERTIFIED":
            return {
                **root_summary,
                "blocker": "PB-007-01",
                "anchor_certificate": anchor,
                "left_event": left_event,
                "right_event": right_event,
            }
        return {
            "status": "CERTIFIED",
            "relation": V34_ROUTE,
            "source_parameter_id": source_parameter_id,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(q(rate))},
            "phase_correlated_common_factor_certificate": anchor,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": (
                "the exact diagonal phase rotation keeps the selected C'=S'=G' amplitude contribution correlated as "
                "G'(cos+sin), while the selected phase contribution is 2*pi*h*r*G*(cos-sin); exact rational "
                "rotated bounds and finite MC-032 orthants prove their joint sign dominates every non-anchor residual"
            ),
            "multiplicity_proof": "the complete derivative has one strict sign on the closed child span, so every admitted root is simple",
            "caller_certificate_trusted": False,
            "sampling_used": False,
            "epsilon_used": False,
            "numerical_trigonometry_used": False,
        }
    if attempts:
        return {
            "status": "BLOCKED",
            "reason": "V34_PHASE_CORRELATED_COMMON_FACTOR_EVENT_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "attempts": attempts,
        }
    return None


def analyze_phase_correlated_common_factor_event(spec):
    baseline = v30.classify_required_analytic_event(spec)
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
        old_route = span.get("route", {})
        eligible = old_route.get("status") == "BLOCKED" and "cos_polynomials" in span and "sin_polynomials" in span
        if eligible:
            left = q(span["source_interval"][0])
            right = q(span["source_interval"][1])
            width = right - left
            local_offset = offset_global + rate * left
            local_rate = rate * width
            cos_polys = {int(h): [q(x) for x in poly] for h, poly in span["cos_polynomials"].items()}
            sin_polys = {int(h): [q(x) for x in poly] for h, poly in span["sin_polynomials"].items()}
            replacement = _correlated_route(
                cos_polys, sin_polys, local_offset, local_rate, baseline["source_parameter_id"]
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V34_EXACT_PHASE_CORRELATED_COMMON_FACTOR"
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
        "FINITE_EXACT_PIECEWISE_PHASE_CORRELATED_COMMON_FACTOR_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v34_phase_correlated_common_factor_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "phase_correlated_common_factor", "common_factor_certificate", "diagonal_phase_cell",
            "diagonal_phase_cell_certificate", "rotated_phase_lower_bound", "rotated_amplitude_upper_bound",
            "joint_derivative_certificate", "projection_certificate", "residual_certificate",
            "source_adaptive_separator", "source_adaptive_separator_certificate", "rational_separator",
            "critical_root", "critical_value", "root_ordering", "margin_certificate",
            "root_count", "root_certificate", "multiplicity", "multiplicity_certificate",
            "sturm_certificate", "sturm_root_count",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_phase_correlated_common_factor_event(source_spec)
        return v30.classify_required_analytic_event(source_spec)
    return v30.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V34_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
