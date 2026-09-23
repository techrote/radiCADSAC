#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_phase_sector_anchor_model as v22  # noqa: E402

v21 = v22.v21
v20 = v22.v20
v19 = v22.v19
EE = v22.EE
q = v22.q
TWO_PI_UPPER = v22.TWO_PI_UPPER

V23_ROUTE = "EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR_WITH_RESIDUAL_L1_DOMINANCE"


class NonconstantAmplitudeAnchorRefusal(RuntimeError):
    """Bounded exact-resource refusal. Never a truth value."""


def _trim(poly):
    return v22._trim([q(value) for value in poly])


def _sign(value):
    value = q(value)
    return 1 if value > 0 else -1 if value < 0 else 0


def _amplitude_floor_certificate(poly):
    """Exact Bernstein convex-hull lower bound for a nonconstant amplitude."""
    try:
        poly = _trim(poly)
        if len(poly) <= 1:
            return None
        bernstein = v19._bernstein_coefficients(poly)
        if all(value > 0 for value in bernstein):
            sign = 1
        elif all(value < 0 for value in bernstein):
            sign = -1
        else:
            return {
                "status": "BLOCKED",
                "reason": "NONCONSTANT_ANCHOR_BERNSTEIN_STRICT_SIGN_NOT_CERTIFIED",
                "blocker": "PB-007-01",
                "amplitude_polynomial": [str(value) for value in poly],
                "bernstein_coefficients": [str(value) for value in bernstein],
                "zero_bernstein_coefficient": any(value == 0 for value in bernstein),
                "mixed_bernstein_signs": (
                    any(value > 0 for value in bernstein)
                    and any(value < 0 for value in bernstein)
                ),
            }
        floor = min(abs(value) for value in bernstein)
        if floor <= 0:
            raise AssertionError("strict Bernstein sign produced a nonpositive floor")
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_BERNSTEIN_CONVEX_HULL_NONZERO_AMPLITUDE_FLOOR",
            "amplitude_polynomial": [str(value) for value in poly],
            "bernstein_coefficients": [str(value) for value in bernstein],
            "amplitude_sign": "POSITIVE" if sign > 0 else "NEGATIVE",
            "amplitude_sign_number": sign,
            "strict_rational_amplitude_floor": str(floor),
            "proof": (
                "all exact Bernstein coefficients on closed [0,1] have one strict sign; "
                "the Bernstein convex-hull property gives |A(s)| >= min_i |b_i| > 0"
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
            "reason": f"PB00701_V23_AMPLITUDE_FLOOR_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _nonconstant_phase_anchor_derivative_certificate(
    cos_polys, sin_polys, offset, rate, harmonic, component
):
    """Source-derived phase-derivative lower bound for a nonconstant pure quadrature."""
    rate = q(rate)
    offset = q(offset)
    harmonic = int(harmonic)
    if rate == 0 or harmonic <= 0:
        return None

    c = _trim(cos_polys.get(harmonic, [0]))
    s = _trim(sin_polys.get(harmonic, [0]))
    if component == "SIN":
        anchor = s
        complement = c
    elif component == "COS":
        anchor = c
        complement = s
    else:
        raise ValueError("component must be SIN or COS")

    if complement != [0] or anchor == [0] or len(anchor) <= 1:
        return None

    amplitude = _amplitude_floor_certificate(anchor)
    if amplitude is None:
        return None
    if amplitude.get("status") != "CERTIFIED":
        return amplitude

    t0 = Fraction(harmonic) * offset
    t1 = Fraction(harmonic) * (offset + rate)
    sector = v22._sector_certificate(component, min(t0, t1), max(t0, t1))
    if sector is None:
        return {
            "status": "BLOCKED",
            "reason": "NONCONSTANT_ANCHOR_EXACT_HALF_MAGNITUDE_SECTOR_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "harmonic": harmonic,
            "component": component,
            "harmonic_phase_interval": [str(min(t0, t1)), str(max(t0, t1))],
            "amplitude_floor_certificate": amplitude,
        }

    base_sign = amplitude["amplitude_sign_number"] * _sign(Fraction(harmonic) * rate)
    quadrature_sign = sector["quadrature_sign_number"]
    if component == "SIN":
        derivative_sign = base_sign * quadrature_sign
        identity = "G_phase'=2*pi*h*r*A(s)*cos(2*pi*h*phi)"
    else:
        derivative_sign = -base_sign * quadrature_sign
        identity = "G_phase'=-2*pi*h*r*A(s)*sin(2*pi*h*phi)"
    if derivative_sign == 0:
        raise AssertionError("certified nonconstant phase anchor lost derivative sign")

    floor = q(amplitude["strict_rational_amplitude_floor"])
    lower = 3 * abs(Fraction(harmonic) * rate) * floor
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_DERIVATIVE_LOWER_BOUND",
        "harmonic": harmonic,
        "component": component,
        "amplitude_floor_certificate": amplitude,
        "phase_turn_law_local": {"offset": str(offset), "rate": str(rate)},
        "harmonic_phase_turn_law": {
            "offset": str(Fraction(harmonic) * offset),
            "rate": str(Fraction(harmonic) * rate),
        },
        "sector_certificate": sector,
        "phase_derivative_identity": identity,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "strict_rational_lower_bound": str(lower),
        "lower_bound_proof": (
            "Bernstein convex-hull gives |A(s)|>=A_floor>0 and the exact phase sector gives "
            "|Q|>=1/2; hence the phase derivative magnitude is >=pi*|h*r|*A_floor "
            ">3*|h*r|*A_floor using exact pi>3"
        ),
        "amplitude_derivative_is_residual": True,
        "pi_lower_theorem": "pi > 3",
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "epsilon_used": False,
        "sampling_used": False,
        "numerical_trigonometry_used": False,
    }


def _candidate_anchors(cos_polys, sin_polys):
    positive_harmonics = sorted(
        int(h) for h in (set(cos_polys) | set(sin_polys))
        if int(h) > 0 and (
            _trim(cos_polys.get(h, [0])) != [0]
            or _trim(sin_polys.get(h, [0])) != [0]
        )
    )
    candidates = []
    for harmonic in positive_harmonics:
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        if c == [0] and len(s) > 1:
            candidates.append((harmonic, "SIN"))
        if s == [0] and len(c) > 1:
            candidates.append((harmonic, "COS"))
    return positive_harmonics, candidates


def _nonconstant_phase_anchor_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    if rate == 0:
        return None
    positive_harmonics, candidates = _candidate_anchors(cos_polys, sin_polys)
    if len(positive_harmonics) < 2 or not candidates:
        return None

    attempts = []
    for harmonic, component in candidates:
        anchor = _nonconstant_phase_anchor_derivative_certificate(
            cos_polys, sin_polys, offset, rate, harmonic, component
        )
        if anchor is None:
            continue
        if anchor.get("status") == "RESOURCE_REFUSAL":
            return anchor
        if anchor.get("status") != "CERTIFIED":
            attempts.append(anchor)
            continue

        residual = v22._residual_l1_certificate(cos_polys, sin_polys, rate, anchor)
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

        amplitude_kind = "S_prime" if component == "SIN" else "C_prime"
        assert any(
            term["harmonic"] == harmonic and term["kind"] == amplitude_kind
            for term in residual["terms"]
        ), "nonconstant anchor amplitude derivative must remain residual"

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
            "relation": V23_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": positive_harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "nonconstant_phase_anchor_certificate": anchor,
            "residual_l1_certificate": residual,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": (
                "the exact Bernstein amplitude floor plus exact phase sector gives "
                "|G_phase'|>L_anchor while all residual terms, including the anchor amplitude "
                "derivative, satisfy sum|R_i'|<L_anchor; therefore the complete derivative "
                "has the phase-anchor sign everywhere"
            ),
            "multiplicity_proof": (
                "strict phase-anchor/residual derivative separation holds on the complete closed span, "
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
            "reason": "NONCONSTANT_AMPLITUDE_PHASE_DEPENDENT_ANCHOR_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "attempts": attempts,
        }
    return None


def analyze_nonconstant_amplitude_anchor_event(spec):
    baseline = v22.classify_required_analytic_event(spec)
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
            replacement = _nonconstant_phase_anchor_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR"
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
        "FINITE_EXACT_PIECEWISE_NONCONSTANT_AMPLITUDE_PHASE_ANCHOR_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v23_nonconstant_amplitude_phase_anchor_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "phase_anchor", "phase_anchor_certificate", "phase_sector", "sector_certificate",
            "amplitude_floor", "amplitude_floor_certificate", "bernstein_coefficients",
            "derivative_lower_bound", "partial_event", "partial_event_certificate",
            "residual_l1", "residual_l1_certificate", "orthants", "orthant_certificates",
            "margin_polynomials", "sturm_certificate", "sturm_root_count", "root_count",
            "root_certificate", "derivative_certificate",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_nonconstant_amplitude_anchor_event(source_spec)
        return v22.classify_required_analytic_event(source_spec)
    return v22.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V23_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
