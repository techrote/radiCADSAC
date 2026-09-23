#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_nonconstant_phase_anchor_model as v23  # noqa: E402

v22 = v23.v22
v21 = v23.v21
v20 = v23.v20
v19 = v23.v19
EE = v23.EE
q = v23.q
TWO_PI_UPPER = v23.TWO_PI_UPPER

V24_ROUTE = "EXACT_MIXED_QUADRATURE_PHASE_ANCHOR_WITH_RESIDUAL_L1_DOMINANCE"


class MixedQuadratureAnchorRefusal(RuntimeError):
    """Bounded exact-resource refusal. Never a truth value."""


def _trim(poly):
    return v23._trim([q(value) for value in poly])


def _sign(value):
    value = q(value)
    return 1 if value > 0 else -1 if value < 0 else 0


def _floor(value):
    value = q(value)
    return value.numerator // value.denominator


def _component_floor_certificate(poly, component):
    """Exact fixed-sign nonzero floor for one source-owned amplitude component."""
    try:
        poly = _trim(poly)
        if poly == [0]:
            return {
                "status": "BLOCKED",
                "reason": f"MIXED_{component}_COMPONENT_IS_ZERO",
                "blocker": "PB-007-01",
            }
        if len(poly) == 1:
            value = poly[0]
            return {
                "status": "CERTIFIED",
                "relation": "EXACT_CONSTANT_NONZERO_COMPONENT_FLOOR",
                "component": component,
                "amplitude_polynomial": [str(value)],
                "amplitude_sign": "POSITIVE" if value > 0 else "NEGATIVE",
                "amplitude_sign_number": _sign(value),
                "strict_rational_amplitude_floor": str(abs(value)),
                "caller_certificate_trusted": False,
                "binary_float_used": False,
                "epsilon_used": False,
                "sampling_used": False,
            }
        cert = v23._amplitude_floor_certificate(poly)
        if cert is None:
            return {
                "status": "BLOCKED",
                "reason": f"MIXED_{component}_COMPONENT_FLOOR_NOT_CERTIFIED",
                "blocker": "PB-007-01",
            }
        cert = dict(cert)
        cert["component"] = component
        return cert
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V24_{component}_FLOOR_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _mixed_sector_certificate(low, high):
    """Exact rational-turn sector where both sin and cos have fixed sign and |.|>=1/2."""
    low = q(low)
    high = q(high)
    if high < low:
        low, high = high, low
    if high - low > Fraction(1, 12):
        return None

    families = (
        (Fraction(1, 12), Fraction(1, 6), 1, 1,
         "sin(2*pi*t)>=1/2 and cos(2*pi*t)>=1/2"),
        (Fraction(1, 3), Fraction(5, 12), 1, -1,
         "sin(2*pi*t)>=1/2 and cos(2*pi*t)<=-1/2"),
        (Fraction(7, 12), Fraction(2, 3), -1, -1,
         "sin(2*pi*t)<=-1/2 and cos(2*pi*t)<=-1/2"),
        (Fraction(5, 6), Fraction(11, 12), -1, 1,
         "sin(2*pi*t)<=-1/2 and cos(2*pi*t)>=1/2"),
    )
    start = _floor(low) - 1
    stop = _floor(high) + 1
    for integer in range(start, stop + 1):
        for left_offset, right_offset, sin_sign, cos_sign, theorem in families:
            left = Fraction(integer) + left_offset
            right = Fraction(integer) + right_offset
            if low >= left and high <= right:
                return {
                    "status": "CERTIFIED",
                    "phase_interval": [str(low), str(high)],
                    "sector_interval": [str(left), str(right)],
                    "sin_sign": "POSITIVE" if sin_sign > 0 else "NEGATIVE",
                    "sin_sign_number": sin_sign,
                    "cos_sign": "POSITIVE" if cos_sign > 0 else "NEGATIVE",
                    "cos_sign_number": cos_sign,
                    "sin_magnitude_lower_bound": "1/2",
                    "cos_magnitude_lower_bound": "1/2",
                    "sector_theorem": theorem,
                    "sector_endpoints_exact_rational_turns": True,
                    "numerical_trigonometry_used": False,
                    "epsilon_used": False,
                    "sampling_used": False,
                }
    return None


def _mixed_phase_anchor_derivative_certificate(
    cos_polys, sin_polys, offset, rate, harmonic
):
    """Source-derived strict lower bound for a mixed C/S phase derivative."""
    rate = q(rate)
    offset = q(offset)
    harmonic = int(harmonic)
    if rate == 0 or harmonic <= 0:
        return None

    c = _trim(cos_polys.get(harmonic, [0]))
    s = _trim(sin_polys.get(harmonic, [0]))
    if c == [0] or s == [0]:
        return None

    c_floor = _component_floor_certificate(c, "COS")
    s_floor = _component_floor_certificate(s, "SIN")
    for cert in (c_floor, s_floor):
        if cert.get("status") == "RESOURCE_REFUSAL":
            return cert
        if cert.get("status") != "CERTIFIED":
            return {
                "status": "BLOCKED",
                "reason": "MIXED_QUADRATURE_COMPONENT_FLOOR_NOT_CERTIFIED",
                "blocker": "PB-007-01",
                "cos_component_floor_certificate": c_floor,
                "sin_component_floor_certificate": s_floor,
            }

    t0 = Fraction(harmonic) * offset
    t1 = Fraction(harmonic) * (offset + rate)
    sector = _mixed_sector_certificate(min(t0, t1), max(t0, t1))
    if sector is None:
        return {
            "status": "BLOCKED",
            "reason": "MIXED_QUADRATURE_EXACT_DUAL_HALF_MAGNITUDE_SECTOR_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "harmonic": harmonic,
            "harmonic_phase_interval": [str(min(t0, t1)), str(max(t0, t1))],
            "cos_component_floor_certificate": c_floor,
            "sin_component_floor_certificate": s_floor,
        }

    c_sign = int(c_floor["amplitude_sign_number"])
    s_sign = int(s_floor["amplitude_sign_number"])
    sin_sign = int(sector["sin_sign_number"])
    cos_sign = int(sector["cos_sign_number"])
    minus_c_sin_sign = -c_sign * sin_sign
    s_cos_sign = s_sign * cos_sign
    if minus_c_sin_sign != s_cos_sign:
        return {
            "status": "BLOCKED",
            "reason": "MIXED_QUADRATURE_PHASE_PROJECTION_SIGN_ALIGNMENT_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "harmonic": harmonic,
            "cos_component_floor_certificate": c_floor,
            "sin_component_floor_certificate": s_floor,
            "sector_certificate": sector,
            "minus_C_sin_sign": minus_c_sin_sign,
            "S_cos_sign": s_cos_sign,
        }

    hr_sign = _sign(Fraction(harmonic) * rate)
    derivative_sign = hr_sign * minus_c_sin_sign
    if derivative_sign == 0:
        raise AssertionError("certified mixed phase anchor lost derivative sign")

    c_bound = q(c_floor["strict_rational_amplitude_floor"])
    s_bound = q(s_floor["strict_rational_amplitude_floor"])
    lower = 3 * abs(Fraction(harmonic) * rate) * (c_bound + s_bound)
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_MIXED_QUADRATURE_PHASE_PROJECTION_DERIVATIVE_LOWER_BOUND",
        "harmonic": harmonic,
        "cos_component_floor_certificate": c_floor,
        "sin_component_floor_certificate": s_floor,
        "phase_turn_law_local": {"offset": str(offset), "rate": str(rate)},
        "harmonic_phase_turn_law": {
            "offset": str(Fraction(harmonic) * offset),
            "rate": str(Fraction(harmonic) * rate),
        },
        "sector_certificate": sector,
        "phase_derivative_identity": "G_phase'=2*pi*h*r*(-C(s)*sin(2*pi*h*phi)+S(s)*cos(2*pi*h*phi))",
        "projection_terms_aligned": True,
        "projection_sign_number": minus_c_sin_sign,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "strict_rational_lower_bound": str(lower),
        "lower_bound_proof": (
            "the exact mixed phase sector gives |sin|,|cos|>=1/2 with fixed signs; "
            "source-derived C/S signs align -C*sin and S*cos, so the projection magnitude is at least "
            "(C_floor+S_floor)/2; therefore |G_phase'|>=pi*|h*r|*(C_floor+S_floor) "
            ">3*|h*r|*(C_floor+S_floor) using exact pi>3"
        ),
        "both_amplitude_derivatives_are_residual": True,
        "pi_lower_theorem": "pi > 3",
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "epsilon_used": False,
        "sampling_used": False,
        "numerical_trigonometry_used": False,
    }


def _mixed_residual_envelope_terms(cos_polys, sin_polys, phase_rate, anchor_harmonic):
    """All derivative channels except both phase terms consumed by the mixed anchor."""
    rate = q(phase_rate)
    terms = []
    polynomials = []

    anchor0 = _trim(cos_polys.get(0, [0]))
    p_prime = _trim(v19._deriv(anchor0))
    if p_prime != [0]:
        polynomials.append(p_prime)
        terms.append({
            "harmonic": 0,
            "kind": "P_prime",
            "polynomial": [str(value) for value in p_prime],
            "role": "residual even if its sign changes",
        })

    positive_harmonics = sorted(
        int(h) for h in (set(cos_polys) | set(sin_polys))
        if int(h) > 0 and (
            _trim(cos_polys.get(h, [0])) != [0]
            or _trim(sin_polys.get(h, [0])) != [0]
        )
    )
    for harmonic in positive_harmonics:
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        scale = TWO_PI_UPPER * abs(Fraction(harmonic) * rate)
        candidates = (
            ("C_prime", v19._deriv(c)),
            ("S_prime", v19._deriv(s)),
            ("phase_C", v22._pscale(c, scale)),
            ("phase_S", v22._pscale(s, scale)),
        )
        for kind, poly in candidates:
            if harmonic == int(anchor_harmonic) and kind in ("phase_C", "phase_S"):
                continue
            poly = _trim(poly)
            if poly == [0]:
                continue
            polynomials.append(poly)
            terms.append({
                "harmonic": harmonic,
                "kind": kind,
                "polynomial": [str(value) for value in poly],
            })
    return positive_harmonics, terms, polynomials


def _mixed_residual_l1_certificate(cos_polys, sin_polys, phase_rate, anchor_certificate):
    try:
        lower = q(anchor_certificate["strict_rational_lower_bound"])
        harmonic = int(anchor_certificate["harmonic"])
        positive_harmonics, terms, polynomials = _mixed_residual_envelope_terms(
            cos_polys, sin_polys, phase_rate, harmonic
        )
        if not polynomials:
            return None

        orthant_certificates = []
        orthant_count = 1 << len(polynomials)
        for mask in range(orthant_count):
            margin = [lower]
            signs = []
            for index, poly in enumerate(polynomials):
                sign = 1 if (mask >> index) & 1 else -1
                signs.append(sign)
                margin = v22._padd(margin, v22._pscale(poly, -sign))
            margin = _trim(margin)
            certificate = v20._strict_positive_certificate(
                margin, f"MIXED_PHASE_ANCHOR_RESIDUAL_ORTHANT_{mask}"
            )
            if certificate.get("status") == "RESOURCE_REFUSAL":
                return {
                    **certificate,
                    "reason": f"PB00701_V24_RESIDUAL_ORTHANT_{mask}_RESOURCE_REFUSAL",
                    "is_truth_value": False,
                }
            if certificate.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "MIXED_PHASE_ANCHOR_RESIDUAL_L1_STRICT_DOMINANCE_NOT_CERTIFIED",
                    "blocker": "PB-007-01",
                    "anchor_lower_bound": str(lower),
                    "failed_orthant": mask,
                    "failed_signs": signs,
                    "failed_margin_polynomial": [str(value) for value in margin],
                    "failed_margin_certificate": certificate,
                    "term_count": len(polynomials),
                    "orthant_count": orthant_count,
                    "terms": terms,
                }
            orthant_certificates.append({
                "orthant": mask,
                "signs": signs,
                "margin_polynomial": [str(value) for value in margin],
                "certificate": certificate,
            })

        return {
            "status": "CERTIFIED",
            "relation": "EXACT_FINITE_SIGN_ORTHANT_RESIDUAL_L1_BELOW_MIXED_PHASE_ANCHOR",
            "anchor_lower_bound": str(lower),
            "active_positive_harmonics": positive_harmonics,
            "term_count": len(polynomials),
            "orthant_count": orthant_count,
            "terms": terms,
            "orthant_certificates": orthant_certificates,
            "pointwise_identity": "sum_i |f_i(s)| = max_{sigma in {-1,+1}^N} sum_i sigma_i f_i(s)",
            "strict_relation": "sum_i |f_i(s)| < L_anchor < |G_mixed_phase'(s)|",
            "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "pi_upper_theorem": "pi < 22/7",
            "two_pi_rational_upper_bound": "44/7",
            "finite_termination": "finite 2^N exact rational-polynomial residual orthant decisions",
            "caller_certificate_trusted": False,
            "binary_float_used": False,
            "epsilon_used": False,
            "sampling_used": False,
            "approximate_root_ordering_used": False,
            "arbitrary_subdivision_cap_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V24_RESIDUAL_L1_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _candidate_anchors(cos_polys, sin_polys):
    positive_harmonics = sorted(
        int(h) for h in (set(cos_polys) | set(sin_polys))
        if int(h) > 0 and (
            _trim(cos_polys.get(h, [0])) != [0]
            or _trim(sin_polys.get(h, [0])) != [0]
        )
    )
    mixed = [
        harmonic for harmonic in positive_harmonics
        if _trim(cos_polys.get(harmonic, [0])) != [0]
        and _trim(sin_polys.get(harmonic, [0])) != [0]
    ]
    return positive_harmonics, mixed


def _mixed_phase_anchor_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    if rate == 0:
        return None
    positive_harmonics, candidates = _candidate_anchors(cos_polys, sin_polys)
    if len(positive_harmonics) < 2 or not candidates:
        return None

    attempts = []
    for harmonic in candidates:
        anchor = _mixed_phase_anchor_derivative_certificate(
            cos_polys, sin_polys, offset, rate, harmonic
        )
        if anchor is None:
            continue
        if anchor.get("status") == "RESOURCE_REFUSAL":
            return anchor
        if anchor.get("status") != "CERTIFIED":
            attempts.append(anchor)
            continue

        residual = _mixed_residual_l1_certificate(cos_polys, sin_polys, rate, anchor)
        if residual is None:
            continue
        if residual.get("status") == "RESOURCE_REFUSAL":
            return residual
        if residual.get("status") != "CERTIFIED":
            attempts.append({
                "anchor_certificate": anchor,
                "residual_certificate": residual,
            })
            continue

        assert any(
            term["harmonic"] == harmonic and term["kind"] == "C_prime"
            for term in residual["terms"]
        ) or len(_trim(cos_polys[harmonic])) == 1
        assert any(
            term["harmonic"] == harmonic and term["kind"] == "S_prime"
            for term in residual["terms"]
        ) or len(_trim(sin_polys[harmonic])) == 1
        assert not any(
            term["harmonic"] == harmonic and term["kind"] in ("phase_C", "phase_S")
            for term in residual["terms"]
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
                "residual_certificate": residual,
                "left_event": left_event,
                "right_event": right_event,
            }

        return {
            "status": "CERTIFIED",
            "relation": V24_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": positive_harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "mixed_phase_anchor_certificate": anchor,
            "residual_l1_certificate": residual,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": (
                "the exact source-derived C/S component floors and exact dual-quadrature phase sector align "
                "both mixed phase-derivative terms and prove |G_mixed_phase'|>L_anchor while all retained "
                "amplitude and other derivative channels satisfy sum|R_i'|<L_anchor; therefore the complete "
                "derivative has the mixed phase-anchor sign everywhere"
            ),
            "multiplicity_proof": (
                "strict mixed-phase-anchor/residual derivative separation holds on the complete closed span, "
                "so the complete derivative is nonzero and every admitted root is simple"
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
            "reason": "MIXED_QUADRATURE_PHASE_DEPENDENT_ANCHOR_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "attempts": attempts,
        }
    return None


def analyze_mixed_quadrature_anchor_event(spec):
    baseline = v23.classify_required_analytic_event(spec)
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
            replacement = _mixed_phase_anchor_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR"
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
        "FINITE_EXACT_PIECEWISE_MIXED_QUADRATURE_PHASE_ANCHOR_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v24_mixed_quadrature_phase_anchor_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "phase_anchor", "phase_anchor_certificate", "mixed_phase_anchor",
            "mixed_phase_anchor_certificate", "phase_sector", "sector_certificate",
            "amplitude_floor", "amplitude_floor_certificate", "cos_component_floor_certificate",
            "sin_component_floor_certificate", "bernstein_coefficients", "derivative_lower_bound",
            "partial_event", "partial_event_certificate", "residual_l1", "residual_l1_certificate",
            "orthants", "orthant_certificates", "margin_polynomials", "sturm_certificate",
            "sturm_root_count", "root_count", "root_certificate", "derivative_certificate",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_mixed_quadrature_anchor_event(source_spec)
        return v23.classify_required_analytic_event(source_spec)
    return v23.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V24_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
