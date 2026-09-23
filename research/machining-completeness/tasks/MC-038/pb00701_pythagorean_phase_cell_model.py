#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_algebraic_phase_cell_model as v28  # noqa: E402

v27 = v28.v27
v26 = v28.v26
v25 = v28.v25
v24 = v28.v24
v23 = v28.v23
v22 = v28.v22
v21 = v28.v21
v20 = v28.v20
v19 = v28.v19
EE = v28.EE
q = v28.q

V29_ROUTE = "EXACT_5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_PROJECTION_DERIVATIVE_DOMINANCE"
DOMINANT_LOWER = Fraction(12, 13)
TRANSVERSE_UPPER = Fraction(5, 13)

# Exact nested cells with endpoint angle pi/8 from the quadrature maximum.
# At those endpoints:
#   dominant   = cos(pi/8) = sqrt(2 + sqrt(2))/2 > 12/13
#   transverse = sin(pi/8) = sqrt(2 - sqrt(2))/2 < 5/13
# The two comparisons share one exact rational reduction:
#   sqrt(2) > 238/169 because 2 > (238/169)^2,
#   i.e. 57122 > 56644.
_BASE_CELLS = {
    "COS": (
        (Fraction(-1, 16), Fraction(1, 16), 1),
        (Fraction(7, 16), Fraction(9, 16), -1),
    ),
    "SIN": (
        (Fraction(3, 16), Fraction(5, 16), 1),
        (Fraction(11, 16), Fraction(13, 16), -1),
    ),
}


class PythagoreanPhaseCellRefusal(RuntimeError):
    """Exact-resource refusal. Refusal is never a truth value."""


def _trim(poly):
    return v28._trim(poly)


def _sign(value):
    return v28._sign(value)


def _phase_cell_certificate(component, lo, hi):
    """Prove exact containment in one supported 1/16-turn nested cell."""
    component = str(component).upper()
    if component not in _BASE_CELLS:
        raise ValueError("component must be SIN or COS")
    lo, hi = q(lo), q(hi)
    if lo > hi:
        lo, hi = hi, lo
    first = v27._floor(lo) - 2
    last = v27._ceil(hi) + 2
    for a, b, quadrature_sign in _BASE_CELLS[component]:
        for translate in range(first, last + 1):
            left = a + translate
            right = b + translate
            if left <= lo and hi <= right:
                transverse = "SIN" if component == "COS" else "COS"
                return {
                    "status": "CERTIFIED",
                    "relation": "EXACT_5_12_13_RATIONAL_TURN_ALGEBRAIC_PHASE_CELL",
                    "dominant_quadrature": component,
                    "transverse_quadrature": transverse,
                    "harmonic_phase_interval": [str(lo), str(hi)],
                    "cell_interval": [str(left), str(right)],
                    "quadrature_sign": "POSITIVE" if quadrature_sign > 0 else "NEGATIVE",
                    "quadrature_sign_number": quadrature_sign,
                    "dominant_exact_endpoint_magnitude": "sqrt(2+sqrt(2))/2",
                    "transverse_exact_endpoint_magnitude": "sqrt(2-sqrt(2))/2",
                    "dominant_rational_lower_bound": str(DOMINANT_LOWER),
                    "transverse_rational_upper_bound": str(TRANSVERSE_UPPER),
                    "algebraic_comparison": (
                        "sqrt(2)>238/169 because 2>(238/169)^2, i.e. 57122>56644; "
                        "therefore cos(pi/8)>12/13 and sin(pi/8)<5/13"
                    ),
                    "rational_turn_authority": (
                        "exact 1/16-turn endpoint half-angle identities plus fixed sign and "
                        "monotonicity on the selected elementary phase cell"
                    ),
                    "caller_cell_trusted": False,
                    "caller_algebraic_value_trusted": False,
                    "binary_float_used": False,
                    "sampling_used": False,
                    "epsilon_used": False,
                    "numerical_trigonometry_used": False,
                    "approximate_minimization_used": False,
                }
    return None


def _projection_orthant_certificate(
    cos_polys, sin_polys, phase_rate, harmonic, dominant, dominant_sign
):
    """Prove the sharper 5-12-13 projection and every retained residual."""
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
            dominant_poly, transverse_poly = s, c
            dominant_component, transverse_component = "SIN", "COS"
        elif dominant == "COS":
            dominant_poly, transverse_poly = c, s
            dominant_component, transverse_component = "COS", "SIN"
        else:
            raise ValueError("dominant must be SIN or COS")

        positive_harmonics, terms, residual_polynomials = v24._mixed_residual_envelope_terms(
            cos_polys, sin_polys, rate, harmonic
        )
        phase_scale = 6 * abs(Fraction(harmonic) * rate)
        dominant_base = v22._pscale(
            dominant_poly,
            phase_scale * DOMINANT_LOWER * Fraction(dominant_sign),
        )
        transverse_scaled = v22._pscale(
            transverse_poly, phase_scale * TRANSVERSE_UPPER
        )

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
                margin, f"PB00701_V29_5_12_13_ORTHANT_{mask}"
            )
            if cert.get("status") == "RESOURCE_REFUSAL":
                return {
                    **cert,
                    "reason": f"PB00701_V29_5_12_13_ORTHANT_{mask}_RESOURCE_REFUSAL",
                    "is_truth_value": False,
                }
            if cert.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "5_12_13_PHASE_CELL_PROJECTION_RESIDUAL_STRICT_DOMINANCE_NOT_CERTIFIED",
                    "blocker": "PB-007-01",
                    "harmonic": harmonic,
                    "dominant_component": dominant_component,
                    "transverse_component": transverse_component,
                    "failed_orthant": mask,
                    "failed_transverse_sign": transverse_sign,
                    "failed_residual_signs": residual_signs,
                    "failed_margin_polynomial": [str(value) for value in margin],
                    "failed_margin_certificate": cert,
                    "orthant_count": orthant_count,
                    "residual_terms": terms,
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
            "relation": "EXACT_5_12_13_PHASE_CELL_PROJECTION_PLUS_RESIDUAL_ORTHANT_DOMINANCE",
            "harmonic": harmonic,
            "dominant_component": dominant_component,
            "transverse_component": transverse_component,
            "dominant_sign_number": dominant_sign,
            "dominant_rational_lower_bound": str(DOMINANT_LOWER),
            "transverse_rational_upper_bound": str(TRANSVERSE_UPPER),
            "phase_scale": str(phase_scale),
            "active_positive_harmonics": positive_harmonics,
            "residual_terms": terms,
            "residual_term_count": len(residual_polynomials),
            "orthant_count": orthant_count,
            "orthant_certificates": orthant_certificates,
            "strict_relation": (
                "6*|h*r|*((12/13)*|D(s)|-(5/13)*|T(s)|) > sum_i |R_i(s)| "
                "on the complete closed source span"
            ),
            "derivative_implication": (
                "the exact nested cell gives |dominant quadrature| >= cos(pi/8) > 12/13 "
                "and |transverse quadrature| <= sin(pi/8) < 5/13; because 2*pi>6, "
                "the selected mixed phase projection dominates every retained residual pointwise"
            ),
            "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "pi_lower_theorem": "pi > 3",
            "two_pi_rational_upper_bound_for_other_phase_terms": "44/7",
            "finite_termination": "finite 2^(1+N) exact rational-polynomial orthant decisions",
            "caller_certificate_trusted": False,
            "binary_float_used": False,
            "sampling_used": False,
            "epsilon_used": False,
            "numerical_trigonometry_used": False,
            "approximate_minimization_used": False,
            "arbitrary_subdivision_cap_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V29_5_12_13_ORTHANT_RESOURCE_REFUSAL:{type(exc).__name__}",
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
        phase_component = "COS"
        projection_term = "S*cos"
        projection_sign_factor = 1
    elif dominant == "COS":
        dominant_poly = c
        dominant_component = "COS"
        phase_component = "SIN"
        projection_term = "-C*sin"
        projection_sign_factor = -1
    else:
        raise ValueError("dominant must be SIN or COS")

    sign_cert = v26._fixed_sign_sturm_certificate(dominant_poly, dominant_component)
    if sign_cert.get("status") == "RESOURCE_REFUSAL":
        return sign_cert
    if sign_cert.get("status") != "CERTIFIED":
        return {
            "status": "BLOCKED",
            "reason": f"5_12_13_PHASE_CELL_{dominant_component}_SIGN_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "dominant_sign_certificate": sign_cert,
        }

    t0 = Fraction(harmonic) * q(offset)
    t1 = Fraction(harmonic) * (q(offset) + q(rate))
    cell = _phase_cell_certificate(phase_component, min(t0, t1), max(t0, t1))
    if cell is None:
        return {
            "status": "BLOCKED",
            "reason": f"5_12_13_PHASE_CELL_{phase_component}_CONTAINMENT_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "harmonic": harmonic,
            "harmonic_phase_interval": [str(min(t0, t1)), str(max(t0, t1))],
            "dominant_sign_certificate": sign_cert,
        }

    combined = _projection_orthant_certificate(
        cos_polys, sin_polys, rate, harmonic, dominant,
        sign_cert["amplitude_sign_number"],
    )
    if combined is None:
        return None
    if combined.get("status") != "CERTIFIED":
        return {
            "status": combined.get("status", "BLOCKED"),
            "reason": combined.get("reason", "5_12_13_PHASE_CELL_RESIDUAL_NOT_CERTIFIED"),
            "blocker": "PB-007-01" if combined.get("status") != "RESOURCE_REFUSAL" else None,
            "dominant_component": dominant_component,
            "dominant_sign_certificate": sign_cert,
            "phase_cell_certificate": cell,
            "combined_certificate": combined,
            **({"is_truth_value": False} if combined.get("status") == "RESOURCE_REFUSAL" else {}),
        }

    dominant_sign = int(sign_cert["amplitude_sign_number"])
    quadrature_sign = int(cell["quadrature_sign_number"])
    projection_sign = projection_sign_factor * dominant_sign * quadrature_sign
    derivative_sign = _sign(Fraction(harmonic) * q(rate)) * projection_sign
    if derivative_sign == 0:
        raise AssertionError("certified v29 nested phase-cell route lost derivative sign")

    return {
        "status": "CERTIFIED",
        "relation": "EXACT_SOURCE_DERIVED_5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_DERIVATIVE_AUTHORITY",
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
        "phase_cell_certificate": cell,
        "projection_residual_certificate": combined,
        "projection_sign_number": projection_sign,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "phase_derivative_identity": "G_phase'=2*pi*h*r*(-C(s)*sin(2*pi*h*phi)+S(s)*cos(2*pi*h*phi))",
        "both_amplitude_derivatives_are_residual": True,
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
    }


def _phase_cell_derivative_certificate(cos_polys, sin_polys, offset, rate, harmonic):
    rate, offset, harmonic = q(rate), q(offset), int(harmonic)
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
        "reason": "5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_DERIVATIVE_ANCHOR_NOT_CERTIFIED",
        "blocker": "PB-007-01",
        "harmonic": harmonic,
        "attempts": attempts,
    }


def _phase_cell_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    if rate == 0:
        return None
    positive_harmonics, candidates = v25._candidate_anchors(cos_polys, sin_polys)
    if len(positive_harmonics) < 2 or not candidates:
        return None

    attempts = []
    for harmonic in candidates:
        anchor = _phase_cell_derivative_certificate(
            cos_polys, sin_polys, offset, rate, harmonic
        )
        if anchor is None:
            continue
        if anchor.get("status") == "RESOURCE_REFUSAL":
            return anchor
        if anchor.get("status") != "CERTIFIED":
            attempts.append(anchor)
            continue

        combined = anchor["projection_residual_certificate"]
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
        right_event = v19._endpoint_relation(
            cos_polys, sin_polys, Fraction(1), q(offset) + rate
        )
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
            "relation": V29_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": positive_harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "pythagorean_phase_cell_certificate": anchor,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": (
                "an exact 1/16-turn nested algebraic phase cell supplies the exact rational "
                "5-12-13 bounds dominant>12/13 and transverse<5/13; finite rational-polynomial "
                "sign orthants plus MC-032 Sturm authority prove strict complete-derivative dominance"
            ),
            "multiplicity_proof": (
                "every v29 projection/residual orthant margin is strictly positive on the complete "
                "closed span, so the derivative never vanishes and every admitted root is simple"
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
            "reason": "5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_RESIDUAL_EVENT_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "attempts": attempts,
        }
    return None


def analyze_pythagorean_phase_cell_event(spec):
    baseline = v28.classify_required_analytic_event(spec)
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
            replacement = _phase_cell_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V29_EXACT_5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_PROJECTION"
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
        "FINITE_EXACT_PIECEWISE_5_12_13_ALGEBRAIC_PHASE_CELL_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v29_5_12_13_phase_cell_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "pythagorean_phase_cell", "pythagorean_phase_cell_certificate",
            "nested_phase_cell", "nested_phase_cell_certificate",
            "algebraic_phase_cell", "algebraic_phase_cell_certificate",
            "phase_cell", "phase_cell_certificate", "algebraic_endpoint_values",
            "algebraic_value", "algebraic_values", "projection_bound",
            "projection_lower_bound", "transverse_upper_bound", "separation_bound",
            "projection_certificate", "projection_residual_certificate",
            "phase_sector_partition", "phase_sector_partition_certificate",
            "sector_cuts", "sector_cut_certificate", "certificate_cuts",
            "children", "child_certificates", "root_count", "root_certificate",
            "multiplicity", "multiplicity_certificate", "sturm_certificate",
            "sturm_root_count",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_pythagorean_phase_cell_event(source_spec)
        return v28.classify_required_analytic_event(source_spec)
    return v28.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V29_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
