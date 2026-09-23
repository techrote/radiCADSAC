#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_direct_rotated_coordinate_model as v38  # noqa: E402

q = v38.q
v37 = v38.v37
v34 = v38.v34
v30 = v38.v30
v24 = v38.v24
v22 = v38.v22
v19 = v38.v19

V39_ROUTE = "EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE_HARMONIC_DERIVATIVE_ANCHOR"
JOINT_Y_LOWER = v38.JOINT_Y_LOWER
JOINT_X_UPPER = v38.JOINT_X_UPPER
JOINT_Y_UPPER = v38.JOINT_Y_UPPER

_trim = v38._trim
_pderiv = v38._pderiv
_strict_positive = v38._strict_positive


def _derive_signed_a_orientation(a_poly):
    """Derive sigma_A solely from exact strict sign of source-derived A."""
    a = _trim(a_poly)
    try:
        positive = _strict_positive(a, "PB00701_V39_A_POSITIVE")
        if positive.get("status") == "CERTIFIED":
            return {
                "status": "CERTIFIED", "relation": "EXACT_SOURCE_DERIVED_STRICT_SIGNED_A_ORIENTATION",
                "sigma_A": 1, "A_polynomial": [str(x) for x in a], "Abar_polynomial": [str(x) for x in a],
                "strict_sign_certificate": positive, "caller_orientation_trusted": False,
            }
        if positive.get("status") == "RESOURCE_REFUSAL":
            return {**positive, "reason": "PB00701_V39_A_POSITIVE_RESOURCE_REFUSAL", "is_truth_value": False}
        neg_a = _trim(v22._pscale(a, -1))
        negative = _strict_positive(neg_a, "PB00701_V39_A_NEGATIVE")
        if negative.get("status") == "CERTIFIED":
            return {
                "status": "CERTIFIED", "relation": "EXACT_SOURCE_DERIVED_STRICT_SIGNED_A_ORIENTATION",
                "sigma_A": -1, "A_polynomial": [str(x) for x in a], "Abar_polynomial": [str(x) for x in neg_a],
                "strict_sign_certificate": negative, "positive_attempt": positive, "caller_orientation_trusted": False,
            }
        if negative.get("status") == "RESOURCE_REFUSAL":
            return {**negative, "reason": "PB00701_V39_A_NEGATIVE_RESOURCE_REFUSAL", "is_truth_value": False}
        return {
            "status": "BLOCKED", "reason": "SIGNED_DIRECT_ROTATED_A_NOT_STRICTLY_NONZERO", "blocker": "PB-007-01",
            "A_polynomial": [str(x) for x in a], "positive_certificate": positive, "negative_certificate": negative,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": f"PB00701_V39_A_SIGN_RESOURCE_REFUSAL:{type(exc).__name__}", "is_truth_value": False}


def _derive_signed_direct_rotated_coordinates(cos_poly, sin_poly):
    """Regenerate A/B and orient them by exact source-owned strict sign of A."""
    c, s = _trim(cos_poly), _trim(sin_poly)
    if c == [0] or s == [0]:
        return {"status": "BLOCKED", "reason": "SIGNED_DIRECT_TWO_QUADRATURE_ROUTE_REQUIRES_TWO_NONZERO_SOURCE_QUADRATURES", "blocker": "PB-007-01"}
    try:
        a = _trim(v22._pscale(v22._padd(c, s), Fraction(1, 2)))
        b = _trim(v22._pscale(v22._padd(c, v22._pscale(s, -1)), Fraction(1, 2)))
        a_prime, b_prime = _pderiv(a), _pderiv(b)
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": f"PB00701_V39_ROTATED_COORDINATE_RESOURCE_REFUSAL:{type(exc).__name__}", "is_truth_value": False}
    orientation = _derive_signed_a_orientation(a)
    if orientation.get("status") != "CERTIFIED":
        return {**orientation, "C_polynomial": [str(x) for x in c], "S_polynomial": [str(x) for x in s], "B_polynomial": [str(x) for x in b]}
    sigma_a = int(orientation["sigma_A"])
    abar, bbar = _trim(v22._pscale(a, sigma_a)), _trim(v22._pscale(b, sigma_a))
    abar_prime, bbar_prime = _trim(v22._pscale(a_prime, sigma_a)), _trim(v22._pscale(b_prime, sigma_a))
    gap_certs = []
    for sigma_b in (-1, 1):
        p_sigma = _trim(v22._padd(v22._pscale(abar, JOINT_Y_LOWER), v22._pscale(bbar, -Fraction(sigma_b) * JOINT_X_UPPER)))
        cert = _strict_positive(p_sigma, f"PB00701_V39_PHASE_GAP_SIGMA_A_{sigma_a}_SIGMA_B_{'P' if sigma_b > 0 else 'M'}")
        gap_certs.append({"sigma_B": sigma_b, "phase_gap_polynomial": [str(x) for x in p_sigma], "certificate": cert})
        if cert.get("status") != "CERTIFIED":
            return {
                "status": cert.get("status", "BLOCKED"),
                "reason": cert.get("reason") if cert.get("status") == "RESOURCE_REFUSAL" else "SIGNED_DIRECT_ROTATED_PHASE_GAP_NOT_STRICT",
                "blocker": "PB-007-01", "failed_sigma_B": sigma_b, "phase_gap_polynomial": [str(x) for x in p_sigma],
                "phase_gap_certificate": cert, "phase_gap_certificates": gap_certs,
                "C_polynomial": [str(x) for x in c], "S_polynomial": [str(x) for x in s],
                "A_polynomial": [str(x) for x in a], "B_polynomial": [str(x) for x in b],
                "signed_A_orientation_certificate": orientation,
            }
    return {
        "status": "CERTIFIED", "relation": "EXACT_SOURCE_DERIVED_SIGNED_A_DIRECT_ROTATED_COORDINATES",
        "C_polynomial": [str(x) for x in c], "S_polynomial": [str(x) for x in s],
        "A_polynomial": [str(x) for x in a], "B_polynomial": [str(x) for x in b],
        "A_derivative_polynomial": [str(x) for x in a_prime], "B_derivative_polynomial": [str(x) for x in b_prime],
        "sigma_A": sigma_a, "Abar_polynomial": [str(x) for x in abar], "Bbar_polynomial": [str(x) for x in bbar],
        "Abar_derivative_polynomial": [str(x) for x in abar_prime], "Bbar_derivative_polynomial": [str(x) for x in bbar_prime],
        "signed_A_orientation_certificate": orientation,
        "phase_gap_sign_family": {"status": "CERTIFIED", "relation": "FINITE_EXACT_SIGNED_A_DIRECT_ROTATED_PHASE_GAP_SIGN_FAMILY", "phase_gap_certificates": gap_certs},
        "joint_phase_lower_L": str(JOINT_Y_LOWER), "joint_transverse_upper_U": str(JOINT_X_UPPER), "joint_Y_upper_W": str(JOINT_Y_UPPER),
        "source_coordinates_regenerated": True, "caller_orientation_trusted": False,
        "caller_rotated_coordinates_trusted": False, "caller_derivatives_trusted": False, "binary_float_used": False,
    }


def _phase_correlated_signed_direct_orthant_certificate(cos_polys, sin_polys, phase_rate, harmonic):
    """Prove sigma_A times the complete selected derivative plus all residuals."""
    try:
        rate, harmonic = q(phase_rate), int(harmonic)
        if rate == 0 or harmonic <= 0:
            return None
        c, s = _trim(cos_polys.get(harmonic, [0])), _trim(sin_polys.get(harmonic, [0]))
        derived = _derive_signed_direct_rotated_coordinates(c, s)
        if derived.get("status") != "CERTIFIED":
            return derived
        sigma_a = int(derived["sigma_A"])
        abar, bbar = [q(x) for x in derived["Abar_polynomial"]], [q(x) for x in derived["Bbar_polynomial"]]
        abar_prime, bbar_prime = _pderiv(abar), _pderiv(bbar)
        positive_harmonics, terms, residual_polynomials = v24._mixed_residual_envelope_terms(cos_polys, sin_polys, rate, harmonic)
        retained_terms, retained_polynomials, consumed = [], [], []
        for term, poly in zip(terms, residual_polynomials):
            if term.get("harmonic") == harmonic and term.get("kind") in ("C_prime", "S_prime"):
                consumed.append(term)
                continue
            retained_terms.append(term)
            retained_polynomials.append(_trim(poly))
        residual_count = len(retained_polynomials)
        orthant_count_per_sigma = 1 << (2 + residual_count)
        orthant_certificates = []
        for sigma_b in (-1, 1):
            p_sigma = _trim(v22._padd(v22._pscale(abar, JOINT_Y_LOWER), v22._pscale(bbar, -Fraction(sigma_b) * JOINT_X_UPPER)))
            phase_base = v22._pscale(p_sigma, 6 * abs(Fraction(harmonic) * rate))
            for mask in range(orthant_count_per_sigma):
                sigma_ap, sigma_bp = (1 if (mask & 1) else -1), (1 if (mask & 2) else -1)
                margin = v22._padd(phase_base, v22._pscale(abar_prime, -Fraction(sigma_ap) * JOINT_X_UPPER))
                margin = v22._padd(margin, v22._pscale(bbar_prime, -Fraction(sigma_bp) * JOINT_Y_UPPER))
                residual_signs = []
                for index, poly in enumerate(retained_polynomials):
                    sign = 1 if (mask >> (index + 2)) & 1 else -1
                    residual_signs.append(sign)
                    margin = v22._padd(margin, v22._pscale(poly, -Fraction(sign)))
                margin = _trim(margin)
                cert = _strict_positive(margin, f"PB00701_V39_SIGMA_A_{sigma_a}_SIGMA_B_{sigma_b}_ORTHANT_{mask}")
                if cert.get("status") == "RESOURCE_REFUSAL":
                    return {**cert, "reason": f"PB00701_V39_SIGMA_A_{sigma_a}_SIGMA_B_{sigma_b}_ORTHANT_{mask}_RESOURCE_REFUSAL", "is_truth_value": False}
                if cert.get("status") != "CERTIFIED":
                    return {
                        "status": "BLOCKED", "reason": "SIGNED_A_DIRECT_ROTATED_COORDINATE_STRICT_MARGIN_NOT_CERTIFIED", "blocker": "PB-007-01",
                        "sigma_A": sigma_a, "failed_sigma_B": sigma_b, "failed_orthant": mask,
                        "failed_Abar_prime_sign": sigma_ap, "failed_Bbar_prime_sign": sigma_bp, "failed_residual_signs": residual_signs,
                        "failed_margin_polynomial": [str(x) for x in margin], "failed_margin_certificate": cert,
                        "signed_direct_rotated_coordinate_certificate": derived, "retained_residual_terms": retained_terms,
                        "consumed_selected_amplitude_terms": consumed,
                    }
                orthant_certificates.append({
                    "sigma_A": sigma_a, "sigma_B": sigma_b, "orthant": mask,
                    "Abar_prime_sign": sigma_ap, "Bbar_prime_sign": sigma_bp, "residual_signs": residual_signs,
                    "margin_polynomial": [str(x) for x in margin], "certificate": cert,
                })
        return {
            "status": "CERTIFIED", "relation": "EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE_PLUS_NONANCHOR_RESIDUAL_ORTHANT_DOMINANCE",
            "harmonic": harmonic, "sigma_A": sigma_a, "active_positive_harmonics": positive_harmonics,
            "signed_direct_rotated_coordinate_certificate": derived,
            "oriented_selected_harmonic_identity": "sigma_A*D=Abar'(s)*X+Bbar'(s)*Y+2*pi*h*r*(Abar(s)*Y-Bbar(s)*X)",
            "physical_selected_harmonic_identity": "D=A'(s)*X+B'(s)*Y+2*pi*h*r*(A(s)*Y-B(s)*X)",
            "equivalent_source_derivative_identity": "C'(s)*cos(theta)+S'(s)*sin(theta)+2*pi*h*r*(-C(s)*sin(theta)+S(s)*cos(theta))",
            "consumed_selected_amplitude_terms": consumed, "selected_amplitude_derivatives_consumed_jointly": True,
            "selected_Abar_prime_term_retained": abar_prime != [0], "selected_Bbar_prime_term_retained": bbar_prime != [0],
            "selected_phase_terms_consumed_jointly": True, "retained_residual_terms": retained_terms,
            "residual_term_count": residual_count, "phase_gap_sigma_B_count": 2,
            "orthant_count_per_sigma_B": orthant_count_per_sigma, "orthant_count": len(orthant_certificates),
            "orthant_certificates": orthant_certificates,
            "strict_relation": "for both sigma_B and all sign orthants: 6*|h*r|*(Abar*L-sigma_B*Bbar*U)-sigma_Ap*U*Abar'-sigma_Bp*W*Bbar'-sum_i sigma_i*R_i>0",
            "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity", "pi_lower_theorem": "2*pi > 6",
            "caller_orientation_trusted": False, "caller_rotated_coordinates_trusted": False,
            "caller_derivatives_trusted": False, "caller_margin_trusted": False,
            "binary_float_used": False, "sampling_used": False, "epsilon_used": False,
            "numerical_trigonometry_used": False, "arbitrary_subdivision_cap_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": f"PB00701_V39_SIGNED_DIRECT_ROTATED_RESOURCE_REFUSAL:{type(exc).__name__}", "is_truth_value": False}


def _phase_correlated_signed_direct_derivative_certificate(cos_polys, sin_polys, offset, rate, harmonic):
    rate, offset, harmonic = q(rate), q(offset), int(harmonic)
    if rate == 0 or harmonic <= 0:
        return None
    c, s = _trim(cos_polys.get(harmonic, [0])), _trim(sin_polys.get(harmonic, [0]))
    derived = _derive_signed_direct_rotated_coordinates(c, s)
    if derived.get("status") != "CERTIFIED":
        return derived
    t0, t1 = Fraction(harmonic) * offset, Fraction(harmonic) * (offset + rate)
    cell = v34._diagonal_phase_cell_certificate(min(t0, t1), max(t0, t1))
    if cell.get("status") != "CERTIFIED":
        return cell
    combined = _phase_correlated_signed_direct_orthant_certificate(cos_polys, sin_polys, rate, harmonic)
    if combined is None or combined.get("status") != "CERTIFIED":
        return combined
    sigma_a = int(combined["sigma_A"])
    diagonal_sign = int(cell["diagonal_projection_sign_number"])
    oriented_derivative_sign = v30._sign(Fraction(harmonic) * rate) * diagonal_sign
    derivative_sign = sigma_a * oriented_derivative_sign
    if derivative_sign == 0:
        raise AssertionError("certified v39 route lost complete derivative sign")
    return {
        "status": "CERTIFIED", "relation": "EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE_DERIVATIVE_AUTHORITY",
        "harmonic": harmonic, "sigma_A": sigma_a, "phase_turn_law_local": {"offset": str(offset), "rate": str(rate)},
        "harmonic_phase_turn_law": {"offset": str(Fraction(harmonic) * offset), "rate": str(Fraction(harmonic) * rate)},
        "phase_cell_certificate": cell, "phase_correlated_signed_direct_residual_certificate": combined,
        "oriented_derivative_sign_number": oriented_derivative_sign,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING", "derivative_sign_number": derivative_sign,
        "sign_identity": "sign(D)=sigma_A*sign(h*r)*diagonal_projection_sign", "orientation_is_proof_bookkeeping_only": True,
        "selected_harmonic_full_derivative_identity": "D=A'*X+B'*Y+2*pi*h*r*(A*Y-B*X)",
        "selected_harmonic_amplitude_derivatives_independently_bounded": False,
        "A_prime_dropped": False, "B_prime_dropped": False, "caller_certificate_trusted": False,
        "caller_orientation_trusted": False, "binary_float_used": False, "sampling_used": False,
        "epsilon_used": False, "numerical_trigonometry_used": False,
    }


def _phase_correlated_signed_direct_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    if rate == 0:
        return None
    harmonics = sorted(h for h in set(cos_polys) | set(sin_polys) if int(h) > 0 and (_trim(cos_polys.get(h, [0])) != [0] or _trim(sin_polys.get(h, [0])) != [0]))
    attempts = []
    for harmonic in harmonics:
        c, s = _trim(cos_polys.get(harmonic, [0])), _trim(sin_polys.get(harmonic, [0]))
        if c == [0] or s == [0]:
            continue
        derived = _derive_signed_direct_rotated_coordinates(c, s)
        if derived.get("status") != "CERTIFIED":
            attempts.append(derived)
            continue
        if int(derived["sigma_A"]) != -1:
            attempts.append({"status": "BLOCKED", "reason": "SIGNED_A_ROUTE_POSITIVE_ORIENTATION_REMAINS_V38_OWNED", "blocker": "PB-007-01"})
            continue
        anchor = _phase_correlated_signed_direct_derivative_certificate(cos_polys, sin_polys, offset, rate, harmonic)
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
            return {**root_summary, "blocker": "PB-007-01", "anchor_certificate": anchor, "left_event": left_event, "right_event": right_event}
        return {
            "status": "CERTIFIED", "relation": V39_ROUTE, "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": harmonics, "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "phase_correlated_signed_direct_rotated_coordinate_certificate": anchor,
            "left_event": left_event, "right_event": right_event, **root_summary,
            "complete_derivative_proof": "source-owned C_h and S_h regenerate A,B and exact derivatives; MC-032 proves strict sign of A and derives sigma_A; both sigma_B oriented phase-gap cases, both selected amplitude-derivative rotated channels, and every non-anchor residual sign orthant prove sigma_A times the complete derivative without changing physical semantics",
            "multiplicity_proof": "the complete derivative never vanishes, so every admitted root is simple",
            "caller_certificate_trusted": False, "caller_orientation_trusted": False,
            "sampling_used": False, "epsilon_used": False, "numerical_trigonometry_used": False,
            "approximate_root_ordering_used": False, "arbitrary_subdivision_cap_used": False,
        }
    if attempts:
        return {"status": "BLOCKED", "reason": "SIGNED_A_DIRECT_ROTATED_COORDINATE_EVENT_NOT_CERTIFIED", "blocker": "PB-007-01", "attempts": attempts}
    return None


def analyze_signed_direct_rotated_coordinate_event(spec):
    baseline = v38.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict) or baseline.get("status") == "CERTIFIED":
        return baseline
    if baseline.get("relation") != "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER":
        return baseline
    phase = baseline.get("phase_turn_law", {})
    rate, offset_global = q(phase.get("rate", "0")), q(phase.get("offset", "0"))
    upgraded, unresolved = [], False
    for original_span in baseline.get("spans", []):
        span = dict(original_span)
        old_route = span.get("route", {})
        eligible = old_route.get("status") == "BLOCKED" and "cos_polynomials" in span and "sin_polynomials" in span
        if eligible:
            left, right = q(span["source_interval"][0]), q(span["source_interval"][1])
            width = right - left
            local_offset, local_rate = offset_global + rate * left, rate * width
            cos_polys = {int(h): [q(x) for x in poly] for h, poly in span["cos_polynomials"].items()}
            sin_polys = {int(h): [q(x) for x in poly] for h, poly in span["sin_polynomials"].items()}
            replacement = _phase_correlated_signed_direct_route(cos_polys, sin_polys, local_offset, local_rate, baseline["source_parameter_id"])
            if replacement is not None:
                span["route_kind"] = "PB00701_V39_EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE"
                span["route"] = replacement
                span["local_phase_turn_law"] = {"offset": str(local_offset), "rate": str(local_rate), "local_parameter": "s=(u-lo)/(hi-lo)", "shared_parameter": baseline["source_parameter_id"]}
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
    result["relation"] = "FINITE_EXACT_PIECEWISE_SIGNED_A_DIRECT_ROTATED_COORDINATE_EVENT_DECISION" if status == "CERTIFIED" else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v39_signed_A_direct_rotated_coordinate_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "A", "B", "Abar", "Bbar", "A_polynomial", "B_polynomial", "Abar_polynomial", "Bbar_polynomial",
            "A_prime", "B_prime", "A_derivative_polynomial", "B_derivative_polynomial", "Abar_derivative_polynomial", "Bbar_derivative_polynomial",
            "sigma_A", "A_sign", "orientation", "orientation_certificate", "signed_A_orientation_certificate",
            "rotated_coordinates", "rotated_coordinate_certificate", "derivative_certificate", "A_positive_certificate", "A_negative_certificate",
            "phase_gap_P", "phase_gap_polynomial", "phase_gap_sign_family", "diagonal_phase_cell", "diagonal_phase_cell_certificate", "cell_k",
            "sqrt2_cos_lower", "sqrt2_sin_upper", "sqrt2_upper", "joint_phase_bound", "joint_amplitude_bound", "joint_margin",
            "joint_margin_certificate", "phase_correlated_certificate", "phase_correlated_direct_residual_certificate", "phase_correlated_signed_direct_residual_certificate",
            "root_count", "root_certificate", "multiplicity", "multiplicity_certificate", "sturm_certificate", "sturm_root_count",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_signed_direct_rotated_coordinate_event(source_spec)
        return v38.classify_required_analytic_event(source_spec)
    return v38.classify_required_analytic_event(spec)


def resource_refusal():
    return {"status": "RESOURCE_REFUSAL", "reason": "PB00701_V39_EXACT_RESOURCE_REFUSAL", "is_truth_value": False}
