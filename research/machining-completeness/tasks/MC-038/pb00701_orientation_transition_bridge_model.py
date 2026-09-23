#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_signed_b_anti_diagonal_model as v40  # noqa: E402

v39 = v40.v39
v34 = v40.v34
v30 = v40.v30
v24 = v40.v24
v22 = v40.v22
v19 = v40.v19
q = v40.q
_trim = v40._trim
_pderiv = v40._pderiv
_strict_positive = v40._strict_positive

V42_ROUTE = "EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_DERIVATIVE_BRIDGE"
Y_LOWER = v39.JOINT_Y_LOWER
X_UPPER = v39.JOINT_X_UPPER
Y_UPPER = v39.JOINT_Y_UPPER
TWO_PI_UPPER = Fraction(44, 7)


def _derive_transition_coordinates(cos_poly, sin_poly):
    """Regenerate A/B and derive a strict source-owned sign for B'."""
    c, s = _trim(cos_poly), _trim(sin_poly)
    if c == [0] or s == [0]:
        return {
            "status": "BLOCKED",
            "reason": "ORIENTATION_TRANSITION_ROUTE_REQUIRES_TWO_NONZERO_SOURCE_QUADRATURES",
            "blocker": "PB-007-01",
        }
    try:
        a = _trim(v22._pscale(v22._padd(c, s), Fraction(1, 2)))
        b = _trim(v22._pscale(v22._padd(c, v22._pscale(s, -1)), Fraction(1, 2)))
        a_prime = _pderiv(a)
        b_prime = _pderiv(b)
        pos = _strict_positive(b_prime, "PB00701_V42_B_PRIME_POSITIVE")
        if pos.get("status") == "RESOURCE_REFUSAL":
            return {**pos, "reason": "PB00701_V42_B_PRIME_POSITIVE_RESOURCE_REFUSAL", "is_truth_value": False}
        if pos.get("status") == "CERTIFIED":
            sigma_bp = 1
            sign_cert = pos
        else:
            neg_bp = _trim(v22._pscale(b_prime, -1))
            neg = _strict_positive(neg_bp, "PB00701_V42_B_PRIME_NEGATIVE")
            if neg.get("status") == "RESOURCE_REFUSAL":
                return {**neg, "reason": "PB00701_V42_B_PRIME_NEGATIVE_RESOURCE_REFUSAL", "is_truth_value": False}
            if neg.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "ORIENTATION_TRANSITION_B_PRIME_NOT_STRICTLY_NONZERO",
                    "blocker": "PB-007-01",
                    "B_prime_polynomial": [str(x) for x in b_prime],
                    "positive_certificate": pos,
                    "negative_certificate": neg,
                }
            sigma_bp = -1
            sign_cert = neg
        bp_bar = _trim(v22._pscale(b_prime, sigma_bp))
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_SOURCE_DERIVED_ROTATED_COORDINATES_WITH_STRICT_B_PRIME_ORIENTATION",
            "C_polynomial": [str(x) for x in c],
            "S_polynomial": [str(x) for x in s],
            "A_polynomial": [str(x) for x in a],
            "B_polynomial": [str(x) for x in b],
            "A_derivative_polynomial": [str(x) for x in a_prime],
            "B_derivative_polynomial": [str(x) for x in b_prime],
            "sigma_B_prime": sigma_bp,
            "B_prime_bar_polynomial": [str(x) for x in bp_bar],
            "B_prime_sign_certificate": sign_cert,
            "source_coordinates_regenerated": True,
            "caller_orientation_trusted": False,
            "caller_rotated_coordinates_trusted": False,
            "caller_derivatives_trusted": False,
            "binary_float_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V42_ROTATED_COORDINATE_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _transition_orthant_certificate(cos_polys, sin_polys, phase_rate, harmonic, diagonal_sign):
    """Bound the complete derivative through an A-orientation transition on a closed span."""
    try:
        rate, harmonic, diagonal_sign = q(phase_rate), int(harmonic), int(diagonal_sign)
        if rate == 0 or harmonic <= 0 or diagonal_sign not in (-1, 1):
            return None
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        derived = _derive_transition_coordinates(c, s)
        if derived.get("status") != "CERTIFIED":
            return derived
        a = [q(x) for x in derived["A_polynomial"]]
        b = [q(x) for x in derived["B_polynomial"]]
        a_prime = [q(x) for x in derived["A_derivative_polynomial"]]
        bp_bar = [q(x) for x in derived["B_prime_bar_polynomial"]]
        sigma_bp = int(derived["sigma_B_prime"])
        target_sign = sigma_bp * diagonal_sign

        positive_harmonics, terms, residual_polynomials = v24._mixed_residual_envelope_terms(
            cos_polys, sin_polys, rate, harmonic
        )
        retained_terms, retained_polynomials, consumed = [], [], []
        for term, poly in zip(terms, residual_polynomials):
            if term.get("harmonic") == harmonic and term.get("kind") in ("C_prime", "S_prime"):
                consumed.append(term)
                continue
            retained_terms.append(term)
            retained_polynomials.append(_trim(poly))

        phase_scale = TWO_PI_UPPER * abs(Fraction(harmonic) * rate)
        residual_count = len(retained_polynomials)
        orthant_count = 1 << (3 + residual_count)
        certs = []
        for mask in range(orthant_count):
            sigma_ap = 1 if (mask & 1) else -1
            sigma_a = 1 if (mask & 2) else -1
            sigma_b = 1 if (mask & 4) else -1
            margin = v22._pscale(bp_bar, Y_LOWER)
            margin = v22._padd(margin, v22._pscale(a_prime, -Fraction(sigma_ap) * X_UPPER))
            margin = v22._padd(
                margin,
                v22._pscale(a, -phase_scale * Y_UPPER * Fraction(sigma_a)),
            )
            margin = v22._padd(
                margin,
                v22._pscale(b, -phase_scale * X_UPPER * Fraction(sigma_b)),
            )
            residual_signs = []
            for index, poly in enumerate(retained_polynomials):
                sign = 1 if (mask >> (index + 3)) & 1 else -1
                residual_signs.append(sign)
                margin = v22._padd(margin, v22._pscale(poly, -Fraction(sign)))
            margin = _trim(margin)
            cert = _strict_positive(margin, f"PB00701_V42_TRANSITION_ORTHANT_{mask}")
            if cert.get("status") == "RESOURCE_REFUSAL":
                return {
                    **cert,
                    "reason": f"PB00701_V42_TRANSITION_ORTHANT_{mask}_RESOURCE_REFUSAL",
                    "is_truth_value": False,
                }
            if cert.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "ORIENTATION_TRANSITION_STRICT_MARGIN_NOT_CERTIFIED",
                    "blocker": "PB-007-01",
                    "failed_orthant": mask,
                    "failed_A_prime_sign": sigma_ap,
                    "failed_A_sign": sigma_a,
                    "failed_B_sign": sigma_b,
                    "failed_residual_signs": residual_signs,
                    "failed_margin_polynomial": [str(x) for x in margin],
                    "failed_margin_certificate": cert,
                    "transition_coordinate_certificate": derived,
                    "retained_residual_terms": retained_terms,
                    "consumed_selected_amplitude_terms": consumed,
                }
            certs.append({
                "orthant": mask,
                "A_prime_sign": sigma_ap,
                "A_sign": sigma_a,
                "B_sign": sigma_b,
                "residual_signs": residual_signs,
                "margin_polynomial": [str(x) for x in margin],
                "certificate": cert,
            })

        return {
            "status": "CERTIFIED",
            "relation": "EXACT_B_PRIME_DIAGONAL_TRANSITION_PLUS_NONANCHOR_RESIDUAL_ORTHANT_DOMINANCE",
            "harmonic": harmonic,
            "sigma_B_prime": sigma_bp,
            "diagonal_projection_sign_number": diagonal_sign,
            "derivative_sign_number": target_sign,
            "active_positive_harmonics": positive_harmonics,
            "transition_coordinate_certificate": derived,
            "physical_selected_harmonic_identity": "D=A'(s)*X+B'(s)*Y+2*pi*h*r*(A(s)*Y-B(s)*X)",
            "complete_margin_identity": (
                "|B'|*L-|A'|*U-(44/7)*|h*r|*(|A|*W+|B|*U)-sum_i|R_i|>0"
            ),
            "two_pi_upper_theorem": "2*pi < 44/7 (equivalently pi < 22/7)",
            "joint_Y_lower_L": str(Y_LOWER),
            "joint_X_upper_U": str(X_UPPER),
            "joint_Y_upper_W": str(Y_UPPER),
            "consumed_selected_amplitude_terms": consumed,
            "selected_amplitude_derivatives_consumed_jointly": True,
            "selected_A_prime_term_retained": a_prime != [0],
            "selected_B_prime_term_retained": True,
            "selected_phase_terms_consumed_jointly": True,
            "retained_residual_terms": retained_terms,
            "residual_term_count": residual_count,
            "orthant_count": orthant_count,
            "orthant_certificates": certs,
            "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "finite_termination": "finite 2^(3+N) exact rational-polynomial orthant decisions",
            "caller_orientation_trusted": False,
            "caller_derivatives_trusted": False,
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
            "reason": f"PB00701_V42_TRANSITION_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _transition_derivative_certificate(cos_polys, sin_polys, offset, rate, harmonic):
    rate, offset, harmonic = q(rate), q(offset), int(harmonic)
    if rate == 0 or harmonic <= 0:
        return None
    c = _trim(cos_polys.get(harmonic, [0]))
    s = _trim(sin_polys.get(harmonic, [0]))
    derived = _derive_transition_coordinates(c, s)
    if derived.get("status") != "CERTIFIED":
        return derived
    t0 = Fraction(harmonic) * offset
    t1 = Fraction(harmonic) * (offset + rate)
    cell = v34._diagonal_phase_cell_certificate(min(t0, t1), max(t0, t1))
    if cell.get("status") != "CERTIFIED":
        return cell
    diagonal_sign = int(cell["diagonal_projection_sign_number"])
    combined = _transition_orthant_certificate(
        cos_polys, sin_polys, rate, harmonic, diagonal_sign
    )
    if combined is None or combined.get("status") != "CERTIFIED":
        return combined
    derivative_sign = int(combined["derivative_sign_number"])
    if derivative_sign == 0:
        raise AssertionError("certified v42 bridge lost complete derivative sign")
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_DERIVATIVE_AUTHORITY",
        "harmonic": harmonic,
        "phase_turn_law_local": {"offset": str(offset), "rate": str(rate)},
        "harmonic_phase_turn_law": {
            "offset": str(Fraction(harmonic) * offset),
            "rate": str(Fraction(harmonic) * rate),
        },
        "phase_cell_certificate": cell,
        "orientation_transition_residual_certificate": combined,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "derivative_sign_number": derivative_sign,
        "sign_identity": "sign(D)=sign(B')*diagonal_projection_sign",
        "orientation_transition_is_proof_bookkeeping_only": True,
        "proof_cut_is_physical_event": False,
        "selected_harmonic_full_derivative_identity": "D=A'*X+B'*Y+2*pi*h*r*(A*Y-B*X)",
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
    }


def _transition_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    if rate == 0:
        return None
    harmonics = sorted(
        h for h in set(cos_polys) | set(sin_polys)
        if int(h) > 0 and (
            _trim(cos_polys.get(h, [0])) != [0]
            or _trim(sin_polys.get(h, [0])) != [0]
        )
    )
    attempts = []
    for harmonic in harmonics:
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        if c == [0] or s == [0]:
            continue
        anchor = _transition_derivative_certificate(cos_polys, sin_polys, offset, rate, harmonic)
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
            "relation": V42_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "orientation_transition_bridge_certificate": anchor,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": (
                "source-owned C_h and S_h regenerate A,B,A',B'; MC-032 proves strict sign of B'; "
                "the exact diagonal phase cell supplies fixed Y sign, |Y| lower/upper and |X| upper bounds; "
                "2*pi<44/7 bounds the complete selected phase contribution adversely; every selected "
                "amplitude derivative and every non-anchor residual remains represented in finite exact orthants"
            ),
            "multiplicity_proof": "the complete derivative never vanishes, so every admitted root is simple",
            "caller_certificate_trusted": False,
            "caller_orientation_trusted": False,
            "sampling_used": False,
            "epsilon_used": False,
            "numerical_trigonometry_used": False,
            "approximate_root_ordering_used": False,
            "arbitrary_subdivision_cap_used": False,
        }
    if attempts:
        return {
            "status": "BLOCKED",
            "reason": "ORIENTATION_TRANSITION_EVENT_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "attempts": attempts,
        }
    return None


def analyze_orientation_transition_event(spec):
    baseline = v40.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict) or baseline.get("status") == "CERTIFIED":
        return baseline
    if baseline.get("relation") != "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER":
        return baseline
    phase = baseline.get("phase_turn_law", {})
    rate = q(phase.get("rate", "0"))
    offset_global = q(phase.get("offset", "0"))
    upgraded, unresolved = [], False
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
            replacement = _transition_route(
                cos_polys, sin_polys, local_offset, local_rate, baseline["source_parameter_id"]
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V42_EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_BRIDGE"
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
    result["status"], result["spans"] = status, upgraded
    result["relation"] = (
        "FINITE_EXACT_PIECEWISE_ORIENTATION_TRANSITION_BRIDGE_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v42_orientation_transition_bridge_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "A", "B", "A_prime", "B_prime", "sigma_B_prime", "orientation",
            "orientation_certificate", "rotated_coordinates", "rotated_coordinate_certificate",
            "derivative_certificate", "transition_certificate", "transition_margin",
            "transition_margin_certificate", "diagonal_phase_cell", "diagonal_phase_cell_certificate",
            "root_count", "root_certificate", "multiplicity", "multiplicity_certificate",
            "sturm_certificate", "sturm_root_count",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_orientation_transition_event(source_spec)
        return v40.classify_required_analytic_event(source_spec)
    return v40.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V42_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
