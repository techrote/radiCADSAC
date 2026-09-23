#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_mixed_quadrature_phase_anchor_model as v24  # noqa: E402

v23 = v24.v23
v22 = v24.v22
v21 = v24.v21
v20 = v24.v20
v19 = v24.v19
EE = v24.EE
q = v24.q
TWO_PI_UPPER = v24.TWO_PI_UPPER

V25_ROUTE = "EXACT_MIXED_PROJECTION_COMPONENT_CONE_PHASE_ANCHOR_WITH_RESIDUAL_L1_DOMINANCE"


class ComponentConeAnchorRefusal(RuntimeError):
    """Bounded exact-resource refusal. Never a truth value."""


def _trim(poly):
    return v24._trim([q(value) for value in poly])


def _sign(value):
    value = q(value)
    return 1 if value > 0 else -1 if value < 0 else 0


def _floor(value):
    value = q(value)
    return value.numerator // value.denominator


def _component_abs_upper_certificate(poly, component):
    """Exact Bernstein convex-hull absolute upper bound for one source component."""
    try:
        poly = _trim(poly)
        if poly == [0]:
            return {
                "status": "CERTIFIED",
                "relation": "EXACT_ZERO_COMPONENT_ABSOLUTE_CEILING",
                "component": component,
                "amplitude_polynomial": ["0"],
                "bernstein_coefficients": ["0"],
                "exact_rational_absolute_ceiling": "0",
                "caller_certificate_trusted": False,
                "binary_float_used": False,
                "epsilon_used": False,
                "sampling_used": False,
            }
        if len(poly) == 1:
            ceiling = abs(poly[0])
            return {
                "status": "CERTIFIED",
                "relation": "EXACT_CONSTANT_COMPONENT_ABSOLUTE_CEILING",
                "component": component,
                "amplitude_polynomial": [str(poly[0])],
                "bernstein_coefficients": [str(poly[0])],
                "exact_rational_absolute_ceiling": str(ceiling),
                "caller_certificate_trusted": False,
                "binary_float_used": False,
                "epsilon_used": False,
                "sampling_used": False,
            }
        bernstein = v19._bernstein_coefficients(poly)
        ceiling = max(abs(value) for value in bernstein)
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_BERNSTEIN_CONVEX_HULL_COMPONENT_ABSOLUTE_CEILING",
            "component": component,
            "amplitude_polynomial": [str(value) for value in poly],
            "bernstein_coefficients": [str(value) for value in bernstein],
            "exact_rational_absolute_ceiling": str(ceiling),
            "sign_change_allowed": True,
            "proof": (
                "the exact Bernstein basis is nonnegative and partitions unity on closed [0,1], "
                "so |A(s)| is at most max_i |b_i| without sampling or numerical minimization"
            ),
            "caller_certificate_trusted": False,
            "binary_float_used": False,
            "epsilon_used": False,
            "sampling_used": False,
            "approximate_minimization_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V25_{component}_ABS_CEILING_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _half_magnitude_sector_certificate(component, low, high):
    """Exact rational-turn sector where one quadrature has fixed sign and magnitude >=1/2."""
    low = q(low)
    high = q(high)
    if high < low:
        low, high = high, low
    if component == "COS":
        families = (
            (Fraction(-1, 6), Fraction(1, 6), 1, "cos(2*pi*t)>=1/2"),
            (Fraction(1, 3), Fraction(2, 3), -1, "cos(2*pi*t)<=-1/2"),
        )
    elif component == "SIN":
        families = (
            (Fraction(1, 12), Fraction(5, 12), 1, "sin(2*pi*t)>=1/2"),
            (Fraction(7, 12), Fraction(11, 12), -1, "sin(2*pi*t)<=-1/2"),
        )
    else:
        raise ValueError("component must be COS or SIN")

    start = _floor(low) - 1
    stop = _floor(high) + 1
    for integer in range(start, stop + 1):
        for left_offset, right_offset, sign, theorem in families:
            left = Fraction(integer) + left_offset
            right = Fraction(integer) + right_offset
            if low >= left and high <= right:
                return {
                    "status": "CERTIFIED",
                    "component": component,
                    "phase_interval": [str(low), str(high)],
                    "sector_interval": [str(left), str(right)],
                    "quadrature_sign": "POSITIVE" if sign > 0 else "NEGATIVE",
                    "quadrature_sign_number": sign,
                    "quadrature_magnitude_lower_bound": "1/2",
                    "transverse_quadrature_absolute_upper_bound": "1",
                    "sector_theorem": theorem,
                    "sector_endpoints_exact_rational_turns": True,
                    "numerical_trigonometry_used": False,
                    "epsilon_used": False,
                    "sampling_used": False,
                }
    return None


def _dominance_attempt(cos_polys, sin_polys, offset, rate, harmonic, dominant):
    c = _trim(cos_polys.get(harmonic, [0]))
    s = _trim(sin_polys.get(harmonic, [0]))
    if c == [0] or s == [0]:
        return None

    if dominant == "SIN":
        dominant_poly = s
        transverse_poly = c
        dominant_component = "SIN"
        transverse_component = "COS"
        sector_component = "COS"
        projection_term = "S*cos"
        projection_sign_factor = 1
    elif dominant == "COS":
        dominant_poly = c
        transverse_poly = s
        dominant_component = "COS"
        transverse_component = "SIN"
        sector_component = "SIN"
        projection_term = "-C*sin"
        projection_sign_factor = -1
    else:
        raise ValueError("dominant must be SIN or COS")

    floor_cert = v24._component_floor_certificate(dominant_poly, dominant_component)
    if floor_cert.get("status") == "RESOURCE_REFUSAL":
        return floor_cert
    if floor_cert.get("status") != "CERTIFIED":
        return {
            "status": "BLOCKED",
            "reason": f"COMPONENT_CONE_{dominant_component}_DOMINANT_FLOOR_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "dominant_component": dominant_component,
            "dominant_floor_certificate": floor_cert,
        }

    upper_cert = _component_abs_upper_certificate(transverse_poly, transverse_component)
    if upper_cert.get("status") == "RESOURCE_REFUSAL":
        return upper_cert
    if upper_cert.get("status") != "CERTIFIED":
        return {
            "status": "BLOCKED",
            "reason": f"COMPONENT_CONE_{transverse_component}_TRANSVERSE_CEILING_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "transverse_component": transverse_component,
            "transverse_ceiling_certificate": upper_cert,
        }

    t0 = Fraction(harmonic) * q(offset)
    t1 = Fraction(harmonic) * (q(offset) + q(rate))
    sector = _half_magnitude_sector_certificate(
        sector_component, min(t0, t1), max(t0, t1)
    )
    if sector is None:
        return {
            "status": "BLOCKED",
            "reason": f"COMPONENT_CONE_{sector_component}_HALF_MAGNITUDE_SECTOR_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "dominant_component": dominant_component,
            "harmonic": harmonic,
            "harmonic_phase_interval": [str(min(t0, t1)), str(max(t0, t1))],
            "dominant_floor_certificate": floor_cert,
            "transverse_ceiling_certificate": upper_cert,
        }

    floor_value = q(floor_cert["strict_rational_amplitude_floor"])
    ceiling = q(upper_cert["exact_rational_absolute_ceiling"])
    gap = floor_value / 2 - ceiling
    if gap <= 0:
        return {
            "status": "BLOCKED",
            "reason": "MIXED_PROJECTION_COMPONENT_CONE_STRICT_SEPARATION_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "dominant_component": dominant_component,
            "dominant_floor": str(floor_value),
            "transverse_component": transverse_component,
            "transverse_ceiling": str(ceiling),
            "cone_margin": str(gap),
            "strict_required_relation": "dominant_floor/2 > transverse_ceiling",
            "dominant_floor_certificate": floor_cert,
            "transverse_ceiling_certificate": upper_cert,
            "sector_certificate": sector,
        }

    dominant_sign = int(floor_cert["amplitude_sign_number"])
    quadrature_sign = int(sector["quadrature_sign_number"])
    projection_sign = projection_sign_factor * dominant_sign * quadrature_sign
    hr_sign = _sign(Fraction(harmonic) * q(rate))
    derivative_sign = hr_sign * projection_sign
    if derivative_sign == 0:
        raise AssertionError("certified component-cone anchor lost derivative sign")

    lower = 6 * abs(Fraction(harmonic) * q(rate)) * gap
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_SOURCE_DERIVED_MIXED_PROJECTION_COMPONENT_CONE_DERIVATIVE_LOWER_BOUND",
        "harmonic": int(harmonic),
        "dominant_component": dominant_component,
        "transverse_component": transverse_component,
        "projection_term": projection_term,
        "dominant_floor_certificate": floor_cert,
        "transverse_ceiling_certificate": upper_cert,
        "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(q(rate))},
        "harmonic_phase_turn_law": {
            "offset": str(Fraction(harmonic) * q(offset)),
            "rate": str(Fraction(harmonic) * q(rate)),
        },
        "sector_certificate": sector,
        "strict_cone_separation": "dominant_floor/2 > transverse_ceiling",
        "strict_rational_cone_gap": str(gap),
        "projection_sign_number": projection_sign,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "phase_derivative_identity": "G_phase'=2*pi*h*r*(-C(s)*sin(2*pi*h*phi)+S(s)*cos(2*pi*h*phi))",
        "strict_rational_lower_bound": str(lower),
        "lower_bound_proof": (
            "the dominant source component has exact fixed sign and floor D_floor; the selected exact "
            "quadrature sector gives |Q_dom|>=1/2 with fixed sign, while the transverse quadrature "
            "satisfies |Q_trans|<=1 and the exact Bernstein certificate gives |A_trans|<=T_ceiling; "
            "strict D_floor/2>T_ceiling therefore fixes the mixed projection sign and gives projection "
            "magnitude > gap=D_floor/2-T_ceiling; hence |G_phase'|>2*pi*|h*r|*gap>6*|h*r|*gap "
            "using exact pi>3"
        ),
        "both_amplitude_derivatives_are_residual": True,
        "pi_lower_theorem": "pi > 3",
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "epsilon_used": False,
        "sampling_used": False,
        "numerical_trigonometry_used": False,
        "approximate_minimization_used": False,
    }


def _component_cone_phase_anchor_derivative_certificate(
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
        "reason": "MIXED_PROJECTION_COMPONENT_CONE_ANCHOR_NOT_CERTIFIED",
        "blocker": "PB-007-01",
        "harmonic": harmonic,
        "attempts": attempts,
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


def _component_cone_phase_anchor_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    if rate == 0:
        return None
    positive_harmonics, candidates = _candidate_anchors(cos_polys, sin_polys)
    if len(positive_harmonics) < 2 or not candidates:
        return None

    attempts = []
    for harmonic in candidates:
        anchor = _component_cone_phase_anchor_derivative_certificate(
            cos_polys, sin_polys, offset, rate, harmonic
        )
        if anchor is None:
            continue
        if anchor.get("status") == "RESOURCE_REFUSAL":
            return anchor
        if anchor.get("status") != "CERTIFIED":
            attempts.append(anchor)
            continue

        residual = v24._mixed_residual_l1_certificate(cos_polys, sin_polys, rate, anchor)
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
            "relation": V25_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": positive_harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "component_cone_phase_anchor_certificate": anchor,
            "residual_l1_certificate": residual,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": (
                "the exact source-derived component cone stays strictly separated from the phase-orthogonal "
                "zero-projection direction on the complete rational half-magnitude sector, yielding a fixed "
                "mixed phase-derivative sign and rational lower bound; all retained amplitude and other "
                "derivative channels satisfy the existing exact residual L1/Sturm dominance certificate"
            ),
            "multiplicity_proof": (
                "strict component-cone anchor/residual derivative separation holds on the complete closed "
                "span, so the complete derivative is nonzero and every admitted root is simple"
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
            "reason": "MIXED_PROJECTION_COMPONENT_CONE_PHASE_ANCHOR_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "attempts": attempts,
        }
    return None


def analyze_component_cone_phase_anchor_event(spec):
    baseline = v24.classify_required_analytic_event(spec)
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
            replacement = _component_cone_phase_anchor_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR"
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
        "FINITE_EXACT_PIECEWISE_COMPONENT_CONE_MIXED_PROJECTION_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v25_component_cone_phase_anchor_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
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
            return analyze_component_cone_phase_anchor_event(source_spec)
        return v24.classify_required_analytic_event(source_spec)
    return v24.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V25_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
