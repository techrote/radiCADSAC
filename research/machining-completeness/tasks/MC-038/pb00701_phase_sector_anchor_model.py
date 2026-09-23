#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_l1_sign_orthant_envelope_model as v21  # noqa: E402

v20 = v21.v20
v19 = v21.v19
EE = v21.EE
q = v21.q
TWO_PI_UPPER = v21.TWO_PI_UPPER
V22_ROUTE = "EXACT_PHASE_SECTOR_PARTIAL_DERIVATIVE_ANCHOR_WITH_RESIDUAL_L1_DOMINANCE"


class PhaseSectorAnchorRefusal(RuntimeError):
    """Bounded exact-resource refusal. Never a truth value."""


def _trim(poly):
    return v21._trim([q(value) for value in poly])


def _padd(left, right):
    return v21._padd(left, right)


def _pscale(poly, scalar):
    return v21._pscale(poly, scalar)


def _sign(value):
    value = q(value)
    return 1 if value > 0 else -1 if value < 0 else 0


def _floor(value):
    value = q(value)
    return value.numerator // value.denominator


def _sector_certificate(component, low, high):
    """Exact closed phase sector where the derivative quadrature has |q|>=1/2.

    `component` names the source anchor quadrature. A SIN anchor differentiates
    through cos(2*pi*t); a COS anchor differentiates through -sin(2*pi*t).
    All sector endpoints are exact rational turns. No trigonometric numerical
    evaluation participates in the certificate.
    """
    low = q(low)
    high = q(high)
    if high < low:
        low, high = high, low
    if high - low > Fraction(1, 3):
        return None

    start = _floor(low) - 1
    stop = _floor(high) + 2
    if component == "SIN":
        families = (
            (Fraction(-1, 6), Fraction(1, 6), 1, "cos(2*pi*t) >= 1/2"),
            (Fraction(1, 3), Fraction(2, 3), -1, "cos(2*pi*t) <= -1/2"),
        )
        derivative_quadrature = "COSINE"
    elif component == "COS":
        families = (
            (Fraction(1, 12), Fraction(5, 12), 1, "sin(2*pi*t) >= 1/2"),
            (Fraction(7, 12), Fraction(11, 12), -1, "sin(2*pi*t) <= -1/2"),
        )
        derivative_quadrature = "SINE"
    else:
        raise ValueError("component must be SIN or COS")

    for integer in range(start, stop + 1):
        for left_offset, right_offset, quadrature_sign, theorem in families:
            left = Fraction(integer) + left_offset
            right = Fraction(integer) + right_offset
            if low >= left and high <= right:
                return {
                    "status": "CERTIFIED",
                    "component": component,
                    "derivative_quadrature": derivative_quadrature,
                    "phase_interval": [str(low), str(high)],
                    "sector_interval": [str(left), str(right)],
                    "quadrature_sign": "POSITIVE" if quadrature_sign > 0 else "NEGATIVE",
                    "quadrature_sign_number": quadrature_sign,
                    "quadrature_magnitude_lower_bound": "1/2",
                    "sector_theorem": theorem,
                    "sector_endpoints_exact_rational_turns": True,
                    "numerical_trigonometry_used": False,
                    "epsilon_used": False,
                    "sampling_used": False,
                }
    return None


def _phase_anchor_derivative_certificate(
    cos_polys, sin_polys, offset, rate, harmonic, component
):
    """Derive a strict rational lower bound for one source-owned phase anchor."""
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

    if complement != [0] or len(anchor) != 1 or anchor[0] == 0:
        return None

    t0 = Fraction(harmonic) * offset
    t1 = Fraction(harmonic) * (offset + rate)
    sector = _sector_certificate(component, min(t0, t1), max(t0, t1))
    if sector is None:
        return {
            "status": "BLOCKED",
            "reason": "PHASE_ANCHOR_EXACT_HALF_MAGNITUDE_SECTOR_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "harmonic": harmonic,
            "component": component,
            "harmonic_phase_interval": [str(min(t0, t1)), str(max(t0, t1))],
        }

    amplitude = anchor[0]
    base_sign = _sign(amplitude * Fraction(harmonic) * rate)
    quadrature_sign = sector["quadrature_sign_number"]
    if component == "SIN":
        derivative_sign = base_sign * quadrature_sign
        identity = "G'=2*pi*h*r*B*cos(2*pi*h*phi)"
    else:
        derivative_sign = -base_sign * quadrature_sign
        identity = "G'=-2*pi*h*r*C*sin(2*pi*h*phi)"
    if derivative_sign == 0:
        raise AssertionError("certified nonzero phase anchor lost derivative sign")

    lower = 3 * abs(amplitude * Fraction(harmonic) * rate)
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_RATIONAL_PHASE_SECTOR_PARTIAL_DERIVATIVE_LOWER_BOUND",
        "harmonic": harmonic,
        "component": component,
        "amplitude": str(amplitude),
        "phase_turn_law_local": {"offset": str(offset), "rate": str(rate)},
        "harmonic_phase_turn_law": {
            "offset": str(Fraction(harmonic) * offset),
            "rate": str(Fraction(harmonic) * rate),
        },
        "sector_certificate": sector,
        "derivative_identity": identity,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "strict_rational_lower_bound": str(lower),
        "lower_bound_proof": (
            "sector gives derivative-quadrature magnitude >=1/2, so |G'| >= "
            "pi*|amplitude*h*r| > 3*|amplitude*h*r| using exact pi>3"
        ),
        "pi_lower_theorem": "pi > 3",
        "historical_event_authority": (
            "the source-owned constant-amplitude single-harmonic partial event is within the established "
            "v10/v11/v12-or-later exact event family; v22 independently derives the uniform derivative lower bound"
        ),
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "epsilon_used": False,
        "sampling_used": False,
        "numerical_trigonometry_used": False,
    }


def _residual_envelope_terms(cos_polys, sin_polys, phase_rate, anchor_harmonic, anchor_component):
    """All derivative channels except the certified phase derivative anchor."""
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
            ("phase_C", _pscale(c, scale)),
            ("phase_S", _pscale(s, scale)),
        )
        for kind, poly in candidates:
            if harmonic == int(anchor_harmonic) and (
                (anchor_component == "COS" and kind == "phase_C")
                or (anchor_component == "SIN" and kind == "phase_S")
            ):
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


def _residual_l1_certificate(cos_polys, sin_polys, phase_rate, anchor_certificate):
    """Require exact L1 residual derivative to stay below the phase-anchor lower bound."""
    try:
        lower = q(anchor_certificate["strict_rational_lower_bound"])
        harmonic = int(anchor_certificate["harmonic"])
        component = anchor_certificate["component"]
        positive_harmonics, terms, polynomials = _residual_envelope_terms(
            cos_polys, sin_polys, phase_rate, harmonic, component
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
                margin = _padd(margin, _pscale(poly, -sign))
            margin = _trim(margin)
            certificate = v20._strict_positive_certificate(
                margin, f"PHASE_ANCHOR_RESIDUAL_ORTHANT_{mask}"
            )
            if certificate.get("status") == "RESOURCE_REFUSAL":
                return {
                    **certificate,
                    "reason": f"PB00701_V22_RESIDUAL_ORTHANT_{mask}_RESOURCE_REFUSAL",
                    "is_truth_value": False,
                }
            if certificate.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "PHASE_ANCHOR_RESIDUAL_L1_STRICT_DOMINANCE_NOT_CERTIFIED",
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
            "relation": "EXACT_FINITE_SIGN_ORTHANT_RESIDUAL_L1_BELOW_PHASE_ANCHOR",
            "anchor_lower_bound": str(lower),
            "active_positive_harmonics": positive_harmonics,
            "term_count": len(polynomials),
            "orthant_count": orthant_count,
            "terms": terms,
            "orthant_certificates": orthant_certificates,
            "pointwise_identity": "sum_i |f_i(s)| = max_{sigma in {-1,+1}^N} sum_i sigma_i f_i(s)",
            "strict_relation": "sum_i |f_i(s)| < L_anchor < |G_anchor'(s)|",
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
            "reason": f"PB00701_V22_RESIDUAL_L1_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _candidate_anchors(cos_polys, sin_polys):
    candidates = []
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
        if c == [0] and len(s) == 1 and s[0] != 0:
            candidates.append((harmonic, "SIN"))
        if s == [0] and len(c) == 1 and c[0] != 0:
            candidates.append((harmonic, "COS"))
    return positive_harmonics, candidates


def _phase_partial_anchor_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    if rate == 0:
        return None
    positive_harmonics, candidates = _candidate_anchors(cos_polys, sin_polys)
    if len(positive_harmonics) < 2 or not candidates:
        return None

    attempts = []
    for harmonic, component in candidates:
        anchor = _phase_anchor_derivative_certificate(
            cos_polys, sin_polys, offset, rate, harmonic, component
        )
        if anchor is None:
            continue
        if anchor.get("status") != "CERTIFIED":
            attempts.append(anchor)
            continue
        residual = _residual_l1_certificate(cos_polys, sin_polys, rate, anchor)
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
            "relation": V22_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": positive_harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "phase_anchor_certificate": anchor,
            "residual_l1_certificate": residual,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": (
                "the exact phase sector gives |G_anchor'|>L_anchor while every exact residual L1 orthant "
                "proves sum|R_i'|<L_anchor; therefore the complete source derivative has the anchor sign everywhere"
            ),
            "multiplicity_proof": (
                "strict phase-anchor/residual derivative separation holds on the complete closed span, so the "
                "complete derivative is nonzero and every admitted root, including an endpoint root, is simple"
            ),
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
            "reason": "PHASE_DEPENDENT_PARTIAL_DERIVATIVE_ANCHOR_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "attempts": attempts,
        }
    return None


def analyze_phase_sector_anchor_event(spec):
    baseline = v21.classify_required_analytic_event(spec)
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
            replacement = _phase_partial_anchor_route(
                cos_polys,
                sin_polys,
                local_offset,
                local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V22_EXACT_PHASE_SECTOR_PARTIAL_DERIVATIVE_ANCHOR"
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
        "FINITE_EXACT_PIECEWISE_PHASE_SECTOR_PARTIAL_ANCHOR_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v22_phase_sector_partial_anchor_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "phase_anchor", "phase_anchor_certificate", "phase_sector", "sector_certificate",
            "derivative_lower_bound", "partial_event", "partial_event_certificate",
            "residual_l1", "residual_l1_certificate", "orthants", "orthant_certificates",
            "margin_polynomials", "sturm_certificate", "sturm_root_count", "root_count",
            "root_certificate", "derivative_certificate",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_phase_sector_anchor_event(source_spec)
        return v21.classify_required_analytic_event(source_spec)
    return v21.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V22_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
