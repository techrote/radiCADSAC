#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_source_adaptive_separator_model as v30  # noqa: E402

q = v30.q
v24 = v30.v24
v22 = v30.v22
v20 = v30.v20
v19 = v30.v19

V34_ROUTE = "EXACT_PHASE_CORRELATED_COMMON_FACTOR_HARMONIC_DERIVATIVE_ANCHOR"
SQRT2_COS_LOWER = Fraction(2856, 2197)  # (238/169)*(12/13)
SQRT2_SIN_UPPER = Fraction(99, 182)      # (99/70)*(5/13)


def _trim(poly):
    return v30._trim([q(value) for value in poly])


def _pderiv(poly):
    poly = _trim(poly)
    if len(poly) <= 1:
        return [Fraction(0)]
    return _trim([Fraction(i) * poly[i] for i in range(1, len(poly))])


def _floor_fraction(value):
    value = q(value)
    return value.numerator // value.denominator


def _diagonal_phase_cell_certificate(lo, hi):
    """Recognise one exact diagonal cell using rational turn arithmetic only."""
    lo, hi = q(lo), q(hi)
    if hi < lo:
        lo, hi = hi, lo
    # left(k)=-3/16+k/2 <= lo implies k <= 2*(lo+3/16).
    k0 = _floor_fraction(2 * (lo + Fraction(3, 16)))
    for k in (k0 - 1, k0, k0 + 1):
        left = Fraction(-3, 16) + Fraction(k, 2)
        right = Fraction(-1, 16) + Fraction(k, 2)
        if left <= lo and hi <= right:
            return {
                "status": "CERTIFIED",
                "relation": "EXACT_RATIONAL_TURN_DIAGONAL_COMMON_FACTOR_PHASE_CELL",
                "k": k,
                "cell": [str(left), str(right)],
                "contained_interval": [str(lo), str(hi)],
                "diagonal_projection_sign_number": 1 if k % 2 == 0 else -1,
                "rotated_phase_variable": "u=2*pi*(t+1/8-k/2) in [-pi/8,pi/8]",
                "joint_amplitude_identity": "cos(theta)+sin(theta)=(-1)^k*sqrt(2)*sin(u)",
                "joint_phase_identity": "cos(theta)-sin(theta)=(-1)^k*sqrt(2)*cos(u)",
                "sqrt2_cos_lower": str(SQRT2_COS_LOWER),
                "sqrt2_sin_abs_upper": str(SQRT2_SIN_UPPER),
                "lower_bound_derivation": "sqrt(2)>238/169 and cos(u)>12/13",
                "upper_bound_derivation": "sqrt(2)<99/70 and |sin(u)|<5/13",
                "binary_float_used": False,
                "numerical_trigonometry_used": False,
                "epsilon_used": False,
            }
    return {
        "status": "BLOCKED",
        "reason": "EXACT_DIAGONAL_PHASE_CELL_CONTAINMENT_NOT_CERTIFIED",
        "blocker": "PB-007-01",
        "interval": [str(lo), str(hi)],
    }


def _strict_common_factor_sign(poly):
    """Derive the sign of G from exact source coefficients, never caller metadata."""
    g = _trim(poly)
    if g == [0]:
        return {
            "status": "BLOCKED",
            "reason": "COMMON_FACTOR_ZERO_OR_SIGN_NOT_STRICT",
            "blocker": "PB-007-01",
        }
    pos = v20._strict_positive_certificate(g, "PB00701_V34_COMMON_FACTOR_POSITIVE")
    if pos.get("status") == "RESOURCE_REFUSAL":
        return {**pos, "is_truth_value": False}
    if pos.get("status") == "CERTIFIED":
        return {
            "status": "CERTIFIED",
            "amplitude_sign_number": 1,
            "common_factor_polynomial": [str(x) for x in g],
            "strict_sign_certificate": pos,
        }
    neg_poly = v22._pscale(g, Fraction(-1))
    neg = v20._strict_positive_certificate(neg_poly, "PB00701_V34_COMMON_FACTOR_NEGATIVE")
    if neg.get("status") == "RESOURCE_REFUSAL":
        return {**neg, "is_truth_value": False}
    if neg.get("status") == "CERTIFIED":
        return {
            "status": "CERTIFIED",
            "amplitude_sign_number": -1,
            "common_factor_polynomial": [str(x) for x in g],
            "strict_sign_certificate": neg,
        }
    return {
        "status": "BLOCKED",
        "reason": "COMMON_FACTOR_ZERO_OR_SIGN_NOT_STRICT",
        "blocker": "PB-007-01",
        "positive_attempt": pos,
        "negative_attempt": neg,
    }


def _phase_correlated_orthant_certificate(cos_polys, sin_polys, phase_rate, harmonic):
    """Prove the complete derivative for C_h=S_h=G without splitting G' twice.

    The selected harmonic is consumed exactly as
      G'(cos+sin) + 2*pi*h*r*G*(cos-sin).
    On one diagonal cell, exact rational bounds give
      |phase part| > 6|hr| L |G|,
      |joint amplitude part| < U |G'|.
    Every non-anchor derivative contribution remains in the historical exact
    envelope and all absolute values are discharged by finite sign orthants.
    """
    try:
        rate = q(phase_rate)
        harmonic = int(harmonic)
        if rate == 0 or harmonic <= 0:
            return None
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        if c == [0] or s == [0] or c != s:
            return {
                "status": "BLOCKED",
                "reason": "SELECTED_HARMONIC_NOT_SOURCE_OWNED_EQUAL_QUADRATURE_COMMON_FACTOR",
                "blocker": "PB-007-01",
            }
        g = c
        sign_cert = _strict_common_factor_sign(g)
        if sign_cert.get("status") != "CERTIFIED":
            return sign_cert
        g_sign = int(sign_cert["amplitude_sign_number"])
        g_prime = _pderiv(g)

        positive_harmonics, terms, residual_polynomials = v24._mixed_residual_envelope_terms(
            cos_polys, sin_polys, rate, harmonic
        )
        retained_terms = []
        retained_polynomials = []
        consumed = []
        for term, poly in zip(terms, residual_polynomials):
            if term.get("harmonic") == harmonic and term.get("kind") in ("C_prime", "S_prime"):
                consumed.append(term)
                continue
            retained_terms.append(term)
            retained_polynomials.append(_trim(poly))

        phase_base = v22._pscale(
            g,
            6 * abs(Fraction(harmonic) * rate) * SQRT2_COS_LOWER * Fraction(g_sign),
        )
        joint_amplitude = v22._pscale(g_prime, SQRT2_SIN_UPPER)

        orthant_certificates = []
        signed_term_count = 1 + len(retained_polynomials)
        orthant_count = 1 << signed_term_count
        for mask in range(orthant_count):
            amp_sign = 1 if (mask & 1) else -1
            margin = v22._padd(phase_base, v22._pscale(joint_amplitude, -amp_sign))
            residual_signs = []
            for index, poly in enumerate(retained_polynomials):
                sign = 1 if (mask >> (index + 1)) & 1 else -1
                residual_signs.append(sign)
                margin = v22._padd(margin, v22._pscale(poly, -sign))
            margin = _trim(margin)
            cert = v20._strict_positive_certificate(
                margin, f"PB00701_V34_PHASE_CORRELATED_ORTHANT_{mask}"
            )
            if cert.get("status") == "RESOURCE_REFUSAL":
                return {
                    **cert,
                    "reason": f"PB00701_V34_ORTHANT_{mask}_RESOURCE_REFUSAL",
                    "is_truth_value": False,
                }
            if cert.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "PHASE_CORRELATED_COMMON_FACTOR_STRICT_MARGIN_NOT_CERTIFIED",
                    "blocker": "PB-007-01",
                    "failed_orthant": mask,
                    "failed_joint_amplitude_sign": amp_sign,
                    "failed_residual_signs": residual_signs,
                    "failed_margin_polynomial": [str(x) for x in margin],
                    "failed_margin_certificate": cert,
                    "common_factor_sign_certificate": sign_cert,
                    "retained_residual_terms": retained_terms,
                    "consumed_selected_amplitude_terms": consumed,
                }
            orthant_certificates.append({
                "orthant": mask,
                "joint_amplitude_sign": amp_sign,
                "residual_signs": residual_signs,
                "margin_polynomial": [str(x) for x in margin],
                "certificate": cert,
            })

        return {
            "status": "CERTIFIED",
            "relation": "EXACT_PHASE_CORRELATED_COMMON_FACTOR_PLUS_NONANCHOR_RESIDUAL_ORTHANT_DOMINANCE",
            "harmonic": harmonic,
            "active_positive_harmonics": positive_harmonics,
            "common_factor_polynomial": [str(x) for x in g],
            "common_factor_derivative": [str(x) for x in g_prime],
            "common_factor_sign_certificate": sign_cert,
            "joint_phase_lower_coefficient": str(SQRT2_COS_LOWER),
            "joint_amplitude_upper_coefficient": str(SQRT2_SIN_UPPER),
            "phase_lower_scale": str(6 * abs(Fraction(harmonic) * rate) * SQRT2_COS_LOWER),
            "selected_harmonic_identity": "G'(cos+sin)+2*pi*h*r*G*(cos-sin)",
            "consumed_selected_amplitude_terms": consumed,
            "selected_amplitude_derivatives_consumed_jointly": True,
            "selected_phase_terms_consumed_jointly": True,
            "retained_residual_terms": retained_terms,
            "residual_term_count": len(retained_polynomials),
            "orthant_count": orthant_count,
            "orthant_certificates": orthant_certificates,
            "strict_relation": "6*|h*r|*(2856/2197)*|G(s)|-(99/182)*|G'(s)|-sum_i|R_i(s)|>0",
            "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "pi_lower_theorem": "2*pi > 6",
            "caller_common_factor_trusted": False,
            "caller_margin_trusted": False,
            "binary_float_used": False,
            "sampling_used": False,
            "epsilon_used": False,
            "numerical_trigonometry_used": False,
            "arbitrary_subdivision_cap_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V34_PHASE_CORRELATED_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _phase_correlated_derivative_certificate(cos_polys, sin_polys, offset, rate, harmonic):
    rate, offset, harmonic = q(rate), q(offset), int(harmonic)
    if rate == 0 or harmonic <= 0:
        return None
    c = _trim(cos_polys.get(harmonic, [0]))
    s = _trim(sin_polys.get(harmonic, [0]))
    if c == [0] or s == [0] or c != s:
        return {
            "status": "BLOCKED",
            "reason": "SELECTED_HARMONIC_NOT_SOURCE_OWNED_EQUAL_QUADRATURE_COMMON_FACTOR",
            "blocker": "PB-007-01",
        }

    t0 = Fraction(harmonic) * offset
    t1 = Fraction(harmonic) * (offset + rate)
    cell = _diagonal_phase_cell_certificate(min(t0, t1), max(t0, t1))
    if cell.get("status") != "CERTIFIED":
        return cell

    combined = _phase_correlated_orthant_certificate(
        cos_polys, sin_polys, rate, harmonic
    )
    if combined is None or combined.get("status") != "CERTIFIED":
        return combined

    g_sign = int(combined["common_factor_sign_certificate"]["amplitude_sign_number"])
    diagonal_sign = int(cell["diagonal_projection_sign_number"])
    derivative_sign = v30._sign(Fraction(harmonic) * rate) * g_sign * diagonal_sign
    if derivative_sign == 0:
        raise AssertionError("certified v34 route lost complete derivative sign")

    return {
        "status": "CERTIFIED",
        "relation": "EXACT_PHASE_CORRELATED_COMMON_FACTOR_DERIVATIVE_AUTHORITY",
        "harmonic": harmonic,
        "phase_turn_law_local": {"offset": str(offset), "rate": str(rate)},
        "harmonic_phase_turn_law": {
            "offset": str(Fraction(harmonic) * offset),
            "rate": str(Fraction(harmonic) * rate),
        },
        "phase_cell_certificate": cell,
        "phase_correlated_residual_certificate": combined,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "derivative_sign_number": derivative_sign,
        "selected_harmonic_full_derivative_identity": "G'(cos+sin)+2*pi*h*r*G*(cos-sin)",
        "selected_harmonic_amplitude_derivatives_independently_bounded": False,
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
    }


def _phase_correlated_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    if rate == 0:
        return None
    harmonics = sorted(
        h for h in set(cos_polys) | set(sin_polys)
        if int(h) > 0 and (_trim(cos_polys.get(h, [0])) != [0] or _trim(sin_polys.get(h, [0])) != [0])
    )
    attempts = []
    for harmonic in harmonics:
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        if c == [0] or c != s:
            continue
        anchor = _phase_correlated_derivative_certificate(
            cos_polys, sin_polys, offset, rate, harmonic
        )
        if anchor is None:
            continue
        if anchor.get("status") == "RESOURCE_REFUSAL":
            return anchor
        if anchor.get("status") != "CERTIFIED":
            attempts.append(anchor)
            continue

        left_event = v19._endpoint_relation(cos_polys, sin_polys, Fraction(0), q(offset))
        if left_event.get("status") == "RESOURCE_REFUSAL":
            return left_event
        right_event = v19._endpoint_relation(cos_polys, sin_polys, Fraction(1), q(offset) + rate)
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
            "active_positive_harmonics": harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "phase_correlated_common_factor_certificate": anchor,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": (
                "source-owned C_h=S_h=G is proved strict-sign; an exact rational diagonal phase cell "
                "turns the two selected amplitude derivatives into one G'(cos+sin) term and the two "
                "selected phase terms into one 2*pi*h*r*G*(cos-sin) term; exact rational rotated-" 
                "quadrature bounds plus finite MC-032 sign orthants dominate every non-anchor residual"
            ),
            "multiplicity_proof": "the complete derivative never vanishes, so every admitted root is simple",
            "caller_certificate_trusted": False,
            "sampling_used": False,
            "epsilon_used": False,
            "numerical_trigonometry_used": False,
            "approximate_root_ordering_used": False,
            "arbitrary_subdivision_cap_used": False,
        }
    if attempts:
        return {
            "status": "BLOCKED",
            "reason": "PHASE_CORRELATED_COMMON_FACTOR_EVENT_NOT_CERTIFIED",
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
        eligible = (
            old_route.get("status") == "BLOCKED"
            and "cos_polynomials" in span
            and "sin_polynomials" in span
        )
        if eligible:
            left = q(span["source_interval"][0])
            right = q(span["source_interval"][1])
            width = right - left
            local_offset = offset_global + rate * left
            local_rate = rate * width
            cos_polys = {int(h): [q(x) for x in poly] for h, poly in span["cos_polynomials"].items()}
            sin_polys = {int(h): [q(x) for x in poly] for h, poly in span["sin_polynomials"].items()}
            replacement = _phase_correlated_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
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
            "common_factor", "common_factor_certificate", "common_factor_sign",
            "diagonal_phase_cell", "diagonal_phase_cell_certificate", "cell_k",
            "sqrt2_cos_lower", "sqrt2_sin_upper", "joint_phase_bound",
            "joint_amplitude_bound", "joint_margin", "joint_margin_certificate",
            "phase_correlated_certificate", "phase_correlated_residual_certificate",
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
