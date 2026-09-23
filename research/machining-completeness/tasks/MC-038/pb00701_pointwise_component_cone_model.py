#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_component_cone_phase_anchor_model as v25  # noqa: E402

v24 = v25.v24
v23 = v25.v23
v22 = v25.v22
v21 = v25.v21
v20 = v25.v20
v19 = v25.v19
EE = v25.EE
q = v25.q
TWO_PI_UPPER = v25.TWO_PI_UPPER

V26_ROUTE = "EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANT_DERIVATIVE_DOMINANCE"


class PointwiseComponentConeRefusal(RuntimeError):
    """Bounded exact-resource refusal. Never a truth value."""


def _trim(poly):
    return v25._trim([q(value) for value in poly])


def _sign(value):
    return v25._sign(q(value))


def _fixed_sign_sturm_certificate(poly, component):
    """Prove one strict source-polynomial sign on closed [0,1] exactly."""
    try:
        poly = _trim(poly)
        if poly == [0]:
            return {
                "status": "BLOCKED",
                "reason": f"POINTWISE_CONE_{component}_DOMINANT_COMPONENT_ZERO",
                "blocker": "PB-007-01",
            }

        positive = v20._strict_positive_certificate(
            poly, f"PB00701_V26_{component}_DOMINANT_POSITIVE"
        )
        if positive.get("status") == "RESOURCE_REFUSAL":
            return {
                **positive,
                "reason": f"PB00701_V26_{component}_DOMINANT_SIGN_RESOURCE_REFUSAL",
                "is_truth_value": False,
            }
        if positive.get("status") == "CERTIFIED":
            return {
                "status": "CERTIFIED",
                "relation": "EXACT_CLOSED_INTERVAL_STURM_FIXED_COMPONENT_SIGN",
                "component": component,
                "amplitude_polynomial": [str(value) for value in poly],
                "amplitude_sign": "POSITIVE",
                "amplitude_sign_number": 1,
                "strict_sign_certificate": positive,
                "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
                "caller_certificate_trusted": False,
                "sampling_used": False,
                "epsilon_used": False,
                "approximate_root_ordering_used": False,
            }

        negative_poly = v22._pscale(poly, Fraction(-1))
        negative = v20._strict_positive_certificate(
            negative_poly, f"PB00701_V26_{component}_DOMINANT_NEGATIVE"
        )
        if negative.get("status") == "RESOURCE_REFUSAL":
            return {
                **negative,
                "reason": f"PB00701_V26_{component}_DOMINANT_SIGN_RESOURCE_REFUSAL",
                "is_truth_value": False,
            }
        if negative.get("status") == "CERTIFIED":
            return {
                "status": "CERTIFIED",
                "relation": "EXACT_CLOSED_INTERVAL_STURM_FIXED_COMPONENT_SIGN",
                "component": component,
                "amplitude_polynomial": [str(value) for value in poly],
                "amplitude_sign": "NEGATIVE",
                "amplitude_sign_number": -1,
                "strict_sign_certificate": negative,
                "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
                "caller_certificate_trusted": False,
                "sampling_used": False,
                "epsilon_used": False,
                "approximate_root_ordering_used": False,
            }

        return {
            "status": "BLOCKED",
            "reason": f"POINTWISE_CONE_{component}_DOMINANT_FIXED_SIGN_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "amplitude_polynomial": [str(value) for value in poly],
            "positive_attempt": positive,
            "negative_attempt": negative,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V26_{component}_DOMINANT_SIGN_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _pointwise_combined_orthant_certificate(
    cos_polys, sin_polys, phase_rate, harmonic, dominant, dominant_sign
):
    """Certify pointwise cone separation and every retained derivative residual together."""
    try:
        rate = q(phase_rate)
        harmonic = int(harmonic)
        dominant_sign = int(dominant_sign)
        if rate == 0 or harmonic <= 0 or dominant_sign not in (-1, 1):
            return None

        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        if c == [0] or s == [0]:
            return None
        if dominant == "SIN":
            dominant_poly = s
            transverse_poly = c
            dominant_component = "SIN"
            transverse_component = "COS"
        elif dominant == "COS":
            dominant_poly = c
            transverse_poly = s
            dominant_component = "COS"
            transverse_component = "SIN"
        else:
            raise ValueError("dominant must be SIN or COS")

        positive_harmonics, terms, residual_polynomials = v24._mixed_residual_envelope_terms(
            cos_polys, sin_polys, rate, harmonic
        )
        phase_scale = 6 * abs(Fraction(harmonic) * rate)
        if phase_scale <= 0:
            return None

        dominant_base = v22._pscale(
            dominant_poly, phase_scale * Fraction(dominant_sign, 2)
        )
        transverse_scaled = v22._pscale(transverse_poly, phase_scale)

        orthant_certificates = []
        total_signed_terms = 1 + len(residual_polynomials)
        orthant_count = 1 << total_signed_terms
        for mask in range(orthant_count):
            transverse_sign = 1 if (mask & 1) else -1
            margin = v22._padd(
                dominant_base, v22._pscale(transverse_scaled, -transverse_sign)
            )
            residual_signs = []
            for index, poly in enumerate(residual_polynomials):
                sign = 1 if (mask >> (index + 1)) & 1 else -1
                residual_signs.append(sign)
                margin = v22._padd(margin, v22._pscale(poly, -sign))
            margin = _trim(margin)
            cert = v20._strict_positive_certificate(
                margin, f"PB00701_V26_POINTWISE_ORTHANT_{mask}"
            )
            if cert.get("status") == "RESOURCE_REFUSAL":
                return {
                    **cert,
                    "reason": f"PB00701_V26_POINTWISE_ORTHANT_{mask}_RESOURCE_REFUSAL",
                    "is_truth_value": False,
                }
            if cert.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "POINTWISE_COMPONENT_CONE_RESIDUAL_STRICT_DOMINANCE_NOT_CERTIFIED",
                    "blocker": "PB-007-01",
                    "harmonic": harmonic,
                    "dominant_component": dominant_component,
                    "transverse_component": transverse_component,
                    "dominant_sign_number": dominant_sign,
                    "phase_scale": str(phase_scale),
                    "failed_orthant": mask,
                    "failed_transverse_sign": transverse_sign,
                    "failed_residual_signs": residual_signs,
                    "failed_margin_polynomial": [str(value) for value in margin],
                    "failed_margin_certificate": cert,
                    "residual_terms": terms,
                    "orthant_count": orthant_count,
                }
            orthant_certificates.append({
                "orthant": mask,
                "transverse_sign": transverse_sign,
                "residual_signs": residual_signs,
                "margin_polynomial": [str(value) for value in margin],
                "certificate": cert,
            })

        return {
            "status": "CERTIFIED",
            "relation": "EXACT_POINTWISE_COMPONENT_CONE_PLUS_RESIDUAL_SIGN_ORTHANT_DOMINANCE",
            "harmonic": harmonic,
            "dominant_component": dominant_component,
            "transverse_component": transverse_component,
            "dominant_sign_number": dominant_sign,
            "phase_scale": str(phase_scale),
            "active_positive_harmonics": positive_harmonics,
            "residual_terms": terms,
            "residual_term_count": len(residual_polynomials),
            "orthant_count": orthant_count,
            "orthant_certificates": orthant_certificates,
            "pointwise_identity": (
                "6*|h*r|*(|D(s)|/2-|T(s)|)-sum_i|R_i(s)| = "
                "min over sigma_T,sigma_i of [6*|h*r|*(sign(D)*D(s)/2-sigma_T*T(s)) "
                "- sum_i sigma_i R_i(s)]"
            ),
            "strict_relation": (
                "6*|h*r|*(|D(s)|/2-|T(s)|) > sum_i |R_i(s)| on closed [0,1]"
            ),
            "derivative_implication": (
                "because 2*pi>6 and the selected half-magnitude quadrature fixes the dominant projection sign, "
                "the exact mixed phase derivative dominates every retained residual pointwise"
            ),
            "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "pi_lower_theorem": "pi > 3",
            "pi_upper_theorem": "pi < 22/7",
            "two_pi_rational_upper_bound_for_other_phase_terms": "44/7",
            "finite_termination": "finite 2^(1+N) exact rational-polynomial orthant decisions",
            "caller_certificate_trusted": False,
            "binary_float_used": False,
            "epsilon_used": False,
            "sampling_used": False,
            "numerical_trigonometry_used": False,
            "approximate_minimization_used": False,
            "approximate_root_ordering_used": False,
            "arbitrary_subdivision_cap_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V26_POINTWISE_ORTHANT_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _dominance_attempt(cos_polys, sin_polys, offset, rate, harmonic, dominant):
    c = _trim(cos_polys.get(harmonic, [0]))
    s = _trim(sin_polys.get(harmonic, [0]))
    if c == [0] or s == [0]:
        return None

    if dominant == "SIN":
        dominant_poly = s
        dominant_component = "SIN"
        sector_component = "COS"
        projection_term = "S*cos"
        projection_sign_factor = 1
    elif dominant == "COS":
        dominant_poly = c
        dominant_component = "COS"
        sector_component = "SIN"
        projection_term = "-C*sin"
        projection_sign_factor = -1
    else:
        raise ValueError("dominant must be SIN or COS")

    sign_cert = _fixed_sign_sturm_certificate(dominant_poly, dominant_component)
    if sign_cert.get("status") == "RESOURCE_REFUSAL":
        return sign_cert
    if sign_cert.get("status") != "CERTIFIED":
        return {
            "status": "BLOCKED",
            "reason": f"POINTWISE_COMPONENT_CONE_{dominant_component}_SIGN_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "dominant_component": dominant_component,
            "dominant_sign_certificate": sign_cert,
        }

    t0 = Fraction(harmonic) * q(offset)
    t1 = Fraction(harmonic) * (q(offset) + q(rate))
    sector = v25._half_magnitude_sector_certificate(
        sector_component, min(t0, t1), max(t0, t1)
    )
    if sector is None:
        return {
            "status": "BLOCKED",
            "reason": f"POINTWISE_COMPONENT_CONE_{sector_component}_HALF_MAGNITUDE_SECTOR_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "harmonic": harmonic,
            "harmonic_phase_interval": [str(min(t0, t1)), str(max(t0, t1))],
            "dominant_sign_certificate": sign_cert,
        }

    combined = _pointwise_combined_orthant_certificate(
        cos_polys, sin_polys, rate, harmonic, dominant,
        sign_cert["amplitude_sign_number"],
    )
    if combined is None:
        return None
    if combined.get("status") != "CERTIFIED":
        return {
            "status": combined.get("status", "BLOCKED"),
            "reason": combined.get("reason", "POINTWISE_COMPONENT_CONE_RESIDUAL_NOT_CERTIFIED"),
            "blocker": "PB-007-01" if combined.get("status") != "RESOURCE_REFUSAL" else None,
            "dominant_component": dominant_component,
            "dominant_sign_certificate": sign_cert,
            "sector_certificate": sector,
            "combined_certificate": combined,
            **({"is_truth_value": False} if combined.get("status") == "RESOURCE_REFUSAL" else {}),
        }

    dominant_sign = int(sign_cert["amplitude_sign_number"])
    quadrature_sign = int(sector["quadrature_sign_number"])
    projection_sign = projection_sign_factor * dominant_sign * quadrature_sign
    derivative_sign = _sign(Fraction(harmonic) * q(rate)) * projection_sign
    if derivative_sign == 0:
        raise AssertionError("certified pointwise component-cone route lost derivative sign")

    return {
        "status": "CERTIFIED",
        "relation": "EXACT_SOURCE_DERIVED_POINTWISE_COMPONENT_CONE_DERIVATIVE_AUTHORITY",
        "harmonic": int(harmonic),
        "dominant_component": dominant_component,
        "transverse_component": "COS" if dominant == "SIN" else "SIN",
        "projection_term": projection_term,
        "dominant_sign_certificate": sign_cert,
        "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(q(rate))},
        "harmonic_phase_turn_law": {
            "offset": str(Fraction(harmonic) * q(offset)),
            "rate": str(Fraction(harmonic) * q(rate)),
        },
        "sector_certificate": sector,
        "pointwise_cone_residual_certificate": combined,
        "projection_sign_number": projection_sign,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "phase_derivative_identity": "G_phase'=2*pi*h*r*(-C(s)*sin(2*pi*h*phi)+S(s)*cos(2*pi*h*phi))",
        "both_amplitude_derivatives_are_residual": True,
        "pi_lower_theorem": "pi > 3",
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "epsilon_used": False,
        "sampling_used": False,
        "numerical_trigonometry_used": False,
        "approximate_minimization_used": False,
    }


def _pointwise_component_cone_derivative_certificate(
    cos_polys, sin_polys, offset, rate, harmonic
):
    rate = q(rate)
    offset = q(offset)
    harmonic = int(harmonic)
    if rate == 0 or harmonic <= 0:
        return None
    c = _trim(cos_polys.get(harmonic, [0]))
    s = _trim(sin_polys.get(harmonic, [0]))
    if c == [0] or s == [0]:
        return None

    attempts = []
    for dominant in ("SIN", "COS"):
        attempt = _dominance_attempt(cos_polys, sin_polys, offset, rate, harmonic, dominant)
        if attempt is None:
            continue
        if attempt.get("status") == "RESOURCE_REFUSAL":
            return attempt
        if attempt.get("status") == "CERTIFIED":
            attempt["alternate_dominance_attempts_before_success"] = attempts
            return attempt
        attempts.append(attempt)
    return {
        "status": "BLOCKED",
        "reason": "POINTWISE_COMPONENT_CONE_DERIVATIVE_ANCHOR_NOT_CERTIFIED",
        "blocker": "PB-007-01",
        "harmonic": harmonic,
        "attempts": attempts,
    }


def _pointwise_component_cone_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    if rate == 0:
        return None
    positive_harmonics, candidates = v25._candidate_anchors(cos_polys, sin_polys)
    if len(positive_harmonics) < 2 or not candidates:
        return None

    attempts = []
    for harmonic in candidates:
        anchor = _pointwise_component_cone_derivative_certificate(
            cos_polys, sin_polys, offset, rate, harmonic
        )
        if anchor is None:
            continue
        if anchor.get("status") == "RESOURCE_REFUSAL":
            return anchor
        if anchor.get("status") != "CERTIFIED":
            attempts.append(anchor)
            continue

        combined = anchor["pointwise_cone_residual_certificate"]
        assert any(
            term["harmonic"] == harmonic and term["kind"] == "C_prime"
            for term in combined["residual_terms"]
        ) or len(_trim(cos_polys[harmonic])) == 1
        assert any(
            term["harmonic"] == harmonic and term["kind"] == "S_prime"
            for term in combined["residual_terms"]
        ) or len(_trim(sin_polys[harmonic])) == 1
        assert not any(
            term["harmonic"] == harmonic and term["kind"] in ("phase_C", "phase_S")
            for term in combined["residual_terms"]
        )

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
            "relation": V26_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": positive_harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "pointwise_component_cone_certificate": anchor,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": (
                "the selected exact half-magnitude quadrature and exact fixed sign of the dominant source "
                "component reduce the mixed phase projection to a pointwise algebraic cone inequality; "
                "finite exact sign-orthant margins prove that cone and every retained derivative residual "
                "simultaneously, so 2*pi>6 fixes the complete derivative sign everywhere"
            ),
            "multiplicity_proof": (
                "every combined pointwise cone/residual orthant margin is strictly positive on the complete "
                "closed span, so the complete derivative is nonzero and every admitted root is simple"
            ),
            "caller_certificate_trusted": False,
            "sampling_used": False,
            "epsilon_used": False,
            "numerical_trigonometry_used": False,
            "approximate_minimization_used": False,
            "approximate_root_ordering_used": False,
            "arbitrary_subdivision_cap_used": False,
        }

    if attempts:
        return {
            "status": "BLOCKED",
            "reason": "POINTWISE_COMPONENT_CONE_RESIDUAL_EVENT_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "attempts": attempts,
        }
    return None


def analyze_pointwise_component_cone_event(spec):
    baseline = v25.classify_required_analytic_event(spec)
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
            cos_polys = {
                int(h): [q(value) for value in poly]
                for h, poly in span["cos_polynomials"].items()
            }
            sin_polys = {
                int(h): [q(value) for value in poly]
                for h, poly in span["sin_polynomials"].items()
            }
            replacement = _pointwise_component_cone_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V26_EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANTS"
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
        "FINITE_EXACT_PIECEWISE_POINTWISE_COMPONENT_CONE_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v26_pointwise_component_cone_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "pointwise_component_cone", "pointwise_component_cone_certificate",
            "dominant_sign", "dominant_sign_certificate", "combined_orthants",
            "combined_orthant_certificates", "pointwise_margin", "pointwise_margins",
            "pointwise_cone_residual_certificate", "component_sign_certificate",
            "component_cone", "component_cone_certificate", "dominant_component",
            "transverse_component", "dominant_floor", "dominant_floor_certificate",
            "transverse_ceiling", "transverse_ceiling_certificate", "cone_margin",
            "phase_anchor", "phase_anchor_certificate", "mixed_phase_anchor",
            "mixed_phase_anchor_certificate", "phase_sector", "sector_certificate",
            "bernstein_coefficients", "derivative_lower_bound", "partial_event",
            "partial_event_certificate", "residual_l1", "residual_l1_certificate",
            "orthants", "orthant_certificates", "margin_polynomials", "sturm_certificate",
            "sturm_root_count", "root_count", "root_certificate", "derivative_certificate",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_pointwise_component_cone_event(source_spec)
        return v25.classify_required_analytic_event(source_spec)
    return v25.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V26_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
