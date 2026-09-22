#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_pointwise_derivative_envelope_model as v20  # noqa: E402

v19 = v20.v19
EE = v20.EE
q = v20.q
TWO_PI_UPPER = v20.TWO_PI_UPPER
V21_ROUTE = "EXACT_MULTI_HARMONIC_FINITE_SIGN_ORTHANT_L1_DERIVATIVE_ENVELOPE"


class L1SignOrthantRefusal(RuntimeError):
    """Bounded exact-resource refusal. Never a truth value."""


def _trim(poly):
    return v20._trim([q(value) for value in poly])


def _padd(left, right):
    return v20._padd(left, right)


def _pscale(poly, scalar):
    return v20._pscale(poly, scalar)


def _source_envelope_terms(cos_polys, sin_polys, phase_rate):
    """Derive the exact v20 source envelope terms, with zero terms omitted."""
    rate = q(phase_rate)
    positive_harmonics = sorted(
        int(h) for h in (set(cos_polys) | set(sin_polys))
        if int(h) > 0 and (
            _trim(cos_polys.get(h, [0])) != [0]
            or _trim(sin_polys.get(h, [0])) != [0]
        )
    )
    terms = []
    polynomials = []
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


def _l1_sign_orthant_derivative_certificate(cos_polys, sin_polys, phase_rate):
    """Prove |P'| > sum_i |f_i| by finite exact sign-orthant enumeration.

    Pointwise, sum_i |f_i| equals max over sigma_i in {-1,+1} of
    sum_i sigma_i f_i.  Once P' has a fixed strict sign, exact positivity of
    every directed margin polynomial is therefore equivalent to the desired
    strict L1 dominance.  Each margin is a rational polynomial and is decided
    on closed [0,1] by the existing MC-032 endpoint/Sturm authority.
    """
    try:
        rate = q(phase_rate)
        anchor = _trim(cos_polys.get(0, [0]))
        anchor_derivative = v19._deriv(anchor)
        if anchor == [0] or anchor_derivative == [0] or rate == 0:
            return None

        positive_harmonics, terms, term_polynomials = _source_envelope_terms(
            cos_polys, sin_polys, rate
        )
        if len(positive_harmonics) < 2 or not term_polynomials:
            return None

        anchor_sign = v20._strict_sign_certificate(anchor_derivative, "ANCHOR_DERIVATIVE")
        if anchor_sign.get("status") == "RESOURCE_REFUSAL":
            return anchor_sign
        if anchor_sign.get("status") != "CERTIFIED":
            return {
                "status": "BLOCKED",
                "reason": "L1_ENVELOPE_ANCHOR_SIGN_NOT_CERTIFIED",
                "blocker": "PB-007-01",
                "anchor_sign_certificate": anchor_sign,
            }

        direction = "INCREASING" if anchor_sign["sign"] == "POSITIVE" else "DECREASING"
        directed_anchor = (
            anchor_derivative if direction == "INCREASING"
            else _pscale(anchor_derivative, -1)
        )

        orthant_certificates = []
        orthant_count = 1 << len(term_polynomials)
        for mask in range(orthant_count):
            margin = list(directed_anchor)
            signs = []
            for index, poly in enumerate(term_polynomials):
                sign = 1 if (mask >> index) & 1 else -1
                signs.append(sign)
                margin = _padd(margin, _pscale(poly, -sign))
            margin = _trim(margin)
            certificate = v20._strict_positive_certificate(
                margin, f"L1_ORTHANT_{mask}"
            )
            if certificate.get("status") == "RESOURCE_REFUSAL":
                return {
                    **certificate,
                    "reason": f"PB00701_V21_L1_ORTHANT_{mask}_RESOURCE_REFUSAL",
                    "is_truth_value": False,
                }
            if certificate.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "L1_ENVELOPE_STRICT_DOMINANCE_NOT_CERTIFIED",
                    "blocker": "PB-007-01",
                    "direction": direction,
                    "anchor_sign_certificate": anchor_sign,
                    "failed_orthant": mask,
                    "failed_signs": signs,
                    "failed_margin_polynomial": [str(value) for value in margin],
                    "failed_margin_certificate": certificate,
                    "term_count": len(term_polynomials),
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
            "relation": "EXACT_FINITE_SIGN_ORTHANT_L1_DERIVATIVE_DOMINANCE",
            "direction": direction,
            "anchor_polynomial": [str(value) for value in anchor],
            "anchor_derivative": [str(value) for value in anchor_derivative],
            "active_positive_harmonics": positive_harmonics,
            "term_count": len(term_polynomials),
            "orthant_count": orthant_count,
            "terms": terms,
            "orthant_certificates": orthant_certificates,
            "pointwise_identity": "sum_i |f_i(s)| = max_{sigma in {-1,+1}^N} sum_i sigma_i f_i(s)",
            "pointwise_inequality": "sum_i |f_i(s)| < |P'(s)|",
            "sign_cell_interpretation": (
                "every possible envelope-polynomial sign cell is covered by its exact sign orthant; "
                "global positivity of every orthant margin removes any need to order algebraic sign-change roots"
            ),
            "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "pi_upper_theorem": "pi < 22/7",
            "two_pi_rational_upper_bound": "44/7",
            "finite_termination": "finite 2^N exact rational-polynomial orthant margin decisions",
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
            "reason": f"PB00701_V21_L1_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _l1_envelope_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    anchor = _trim(cos_polys.get(0, [0]))
    positive_harmonics = sorted(
        int(h) for h in (set(cos_polys) | set(sin_polys))
        if int(h) > 0 and (
            _trim(cos_polys.get(h, [0])) != [0]
            or _trim(sin_polys.get(h, [0])) != [0]
        )
    )
    if rate == 0 or anchor == [0] or EE.degree(anchor) <= 0 or len(positive_harmonics) < 2:
        return None

    derivative = _l1_sign_orthant_derivative_certificate(cos_polys, sin_polys, rate)
    if derivative is None:
        return None
    if derivative.get("status") != "CERTIFIED":
        return derivative

    left_event = v19._endpoint_relation(cos_polys, sin_polys, Fraction(0), q(offset))
    if left_event.get("status") == "RESOURCE_REFUSAL":
        return left_event
    right_event = v19._endpoint_relation(cos_polys, sin_polys, Fraction(1), q(offset) + rate)
    if right_event.get("status") == "RESOURCE_REFUSAL":
        return right_event
    root_summary = v19._root_summary(derivative["direction"], left_event, right_event)
    if root_summary.get("status") != "CERTIFIED":
        return {
            **root_summary,
            "blocker": "PB-007-01",
            "derivative_certificate": derivative,
            "left_event": left_event,
            "right_event": right_event,
        }

    return {
        "status": "CERTIFIED",
        "relation": V21_ROUTE,
        "source_parameter_id": source_parameter_id,
        "active_positive_harmonics": positive_harmonics,
        "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
        "derivative_certificate": derivative,
        "left_event": left_event,
        "right_event": right_event,
        **root_summary,
        "multiplicity_proof": (
            "exact finite sign-orthant positivity proves |P'|>sum_i|f_i| throughout the closed span; "
            "the complete source derivative is therefore strictly nonzero and every admitted root is simple"
        ),
        "caller_certificate_trusted": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
        "approximate_root_ordering_used": False,
        "arbitrary_subdivision_cap_used": False,
    }


def analyze_l1_sign_orthant_event(spec):
    baseline = v20.classify_required_analytic_event(spec)
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
            and old_route.get("reason") == "POINTWISE_ENVELOPE_STRICT_DOMINANCE_NOT_CERTIFIED"
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
            replacement = _l1_envelope_route(
                cos_polys,
                sin_polys,
                local_offset,
                local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V21_EXACT_SIGN_ORTHANT_L1_DERIVATIVE_ENVELOPE"
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
        "FINITE_EXACT_PIECEWISE_MULTI_HARMONIC_SIGN_ORTHANT_L1_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v21_l1_sign_orthant_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "l1_envelope", "l1_envelope_certificate", "sign_cells", "sign_cell_partition",
            "orthants", "orthant_certificates", "margin_polynomial", "margin_polynomials",
            "pointwise_identity", "envelope_terms", "sturm_certificate", "sturm_root_count",
            "anchor_sign", "derivative_certificate", "root_count", "root_certificate",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_l1_sign_orthant_event(source_spec)
        return v20.classify_required_analytic_event(source_spec)
    return v20.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V21_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
