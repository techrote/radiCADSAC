#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_phase_correlated_proportional_common_factor_model as v35  # noqa: E402

q = v35.q
v34 = v35.v34
v30 = v35.v30
v24 = v35.v24
v22 = v35.v22
v20 = v35.v20
v19 = v35.v19

V36_ROUTE = "EXACT_PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR_HARMONIC_DERIVATIVE_ANCHOR"
JOINT_Y_LOWER = v35.SQRT2_COS_LOWER
JOINT_X_UPPER = v35.SQRT2_SIN_UPPER
JOINT_Y_UPPER = v35.SQRT2_UPPER


def _trim(poly):
    values = [q(value) for value in poly]
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return values or [Fraction(0)]


def _pderiv(poly):
    poly = _trim(poly)
    if len(poly) <= 1:
        return [Fraction(0)]
    return _trim([Fraction(i) * poly[i] for i in range(1, len(poly))])


def _pmul(a, b):
    a, b = _trim(a), _trim(b)
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, av in enumerate(a):
        for j, bv in enumerate(b):
            out[i + j] += av * bv
    return _trim(out)


def _poly_coeff(poly, index):
    poly = _trim(poly)
    return poly[index] if index < len(poly) else Fraction(0)


def _poly_divmod_exact(numerator, denominator):
    """Exact rational-polynomial long division in ascending coefficient order."""
    numerator = _trim(numerator)
    denominator = _trim(denominator)
    if denominator == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    if numerator == [0]:
        return [Fraction(0)], [Fraction(0)]
    remainder = list(numerator)
    if len(remainder) < len(denominator):
        return [Fraction(0)], remainder
    quotient = [Fraction(0)] * (len(remainder) - len(denominator) + 1)
    den_degree = len(denominator) - 1
    den_lead = denominator[-1]
    while remainder != [0] and len(remainder) - 1 >= den_degree:
        shift = (len(remainder) - 1) - den_degree
        coeff = remainder[-1] / den_lead
        quotient[shift] += coeff
        for i, value in enumerate(denominator):
            remainder[i + shift] -= coeff * value
        remainder = _trim(remainder)
    return _trim(quotient), _trim(remainder)


def _strict_positive(poly, label):
    cert = v20._strict_positive_certificate(_trim(poly), label)
    if cert.get("status") == "RESOURCE_REFUSAL":
        return {**cert, "reason": f"{label}_RESOURCE_REFUSAL", "is_truth_value": False}
    return cert


def _a_positive_certificate(lambda_poly):
    a = v22._pscale(v22._padd(_trim(lambda_poly), [1]), Fraction(1, 2))
    return _strict_positive(a, "PB00701_V36_A_POSITIVE")


def _phase_gap_certificates(a, b):
    certs = []
    for sigma_b in (-1, 1):
        p_sigma = v22._padd(
            v22._pscale(a, JOINT_Y_LOWER),
            v22._pscale(b, -Fraction(sigma_b) * JOINT_X_UPPER),
        )
        p_sigma = _trim(p_sigma)
        cert = _strict_positive(
            p_sigma,
            f"PB00701_V36_PHASE_GAP_SIGMA_B_{'P' if sigma_b > 0 else 'M'}",
        )
        certs.append({
            "sigma_B": sigma_b,
            "phase_gap_polynomial": [str(x) for x in p_sigma],
            "certificate": cert,
        })
        if cert.get("status") != "CERTIFIED":
            return {
                "status": cert.get("status", "BLOCKED"),
                "reason": cert.get("reason") if cert.get("status") == "RESOURCE_REFUSAL" else "VARYING_RATIO_PHASE_GAP_NOT_STRICT",
                "blocker": "PB-007-01",
                "failed_sigma_B": sigma_b,
                "phase_gap_polynomial": [str(x) for x in p_sigma],
                "phase_gap_certificate": cert,
                "phase_gap_certificates": certs,
            }
    return {
        "status": "CERTIFIED",
        "relation": "FINITE_EXACT_VARYING_RATIO_PHASE_GAP_SIGN_FAMILY",
        "phase_gap_certificates": certs,
    }


def _derive_varying_ratio_shared_factor(cos_poly, sin_poly):
    """Derive C=lambda(s)G, S=G from source coefficients only."""
    c = _trim(cos_poly)
    g = _trim(sin_poly)
    if c == [0] or g == [0]:
        return {"status": "BLOCKED", "reason": "SELECTED_HARMONIC_REQUIRES_TWO_NONZERO_QUADRATURES", "blocker": "PB-007-01"}
    try:
        lam, remainder = _poly_divmod_exact(c, g)
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": f"PB00701_V36_POLYNOMIAL_DIVISION_RESOURCE_REFUSAL:{type(exc).__name__}", "is_truth_value": False}
    if remainder != [0]:
        return {
            "status": "BLOCKED",
            "reason": "SELECTED_HARMONIC_POLYNOMIAL_DIVISION_REMAINDER_NONZERO",
            "blocker": "PB-007-01",
            "derived_quotient": [str(x) for x in lam],
            "division_remainder": [str(x) for x in remainder],
        }
    if len(lam) <= 1:
        return {
            "status": "BLOCKED",
            "reason": "VARYING_RATIO_REQUIRES_NONCONSTANT_EXACT_POLYNOMIAL_QUOTIENT",
            "blocker": "PB-007-01",
            "derived_quotient": [str(x) for x in lam],
            "division_remainder": ["0"],
        }
    regenerated = _pmul(lam, g)
    width = max(len(c), len(regenerated))
    identities = []
    for index in range(width):
        lhs = _poly_coeff(c, index)
        rhs = _poly_coeff(regenerated, index)
        identities.append({"coefficient": index, "C": str(lhs), "lambda_times_G": str(rhs), "equal": lhs == rhs})
        if lhs != rhs:
            raise AssertionError("exact division product failed source regeneration")
    a = _trim(v22._pscale(v22._padd(lam, [1]), Fraction(1, 2)))
    b = _trim(v22._pscale(v22._padd(lam, [-1]), Fraction(1, 2)))
    a_cert = _a_positive_certificate(lam)
    if a_cert.get("status") != "CERTIFIED":
        return {
            "status": a_cert.get("status", "BLOCKED"),
            "reason": a_cert.get("reason") if a_cert.get("status") == "RESOURCE_REFUSAL" else "VARYING_RATIO_A_NOT_STRICTLY_POSITIVE",
            "blocker": "PB-007-01",
            "derived_lambda_polynomial": [str(x) for x in lam],
            "A_polynomial": [str(x) for x in a],
            "A_positive_certificate": a_cert,
        }
    gap = _phase_gap_certificates(a, b)
    if gap.get("status") != "CERTIFIED":
        return {
            **gap,
            "derived_lambda_polynomial": [str(x) for x in lam],
            "A_polynomial": [str(x) for x in a],
            "B_polynomial": [str(x) for x in b],
            "A_positive_certificate": a_cert,
            "coefficient_identities": identities,
        }
    lam_prime = _pderiv(lam)
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_SOURCE_DERIVED_NONCONSTANT_POLYNOMIAL_VARYING_RATIO_SHARED_FACTOR",
        "common_factor_polynomial": [str(x) for x in g],
        "derived_lambda_polynomial": [str(x) for x in lam],
        "derived_lambda_derivative": [str(x) for x in lam_prime],
        "division_remainder": ["0"],
        "coefficient_identities": identities,
        "A_polynomial": [str(x) for x in a],
        "B_polynomial": [str(x) for x in b],
        "A_positive_certificate": a_cert,
        "phase_gap_sign_family": gap,
        "joint_phase_lower_L": str(JOINT_Y_LOWER),
        "joint_transverse_upper_U": str(JOINT_X_UPPER),
        "joint_Y_upper_W": str(JOINT_Y_UPPER),
        "caller_lambda_trusted": False,
        "caller_division_trusted": False,
        "caller_common_factor_trusted": False,
        "binary_float_used": False,
    }


def _phase_correlated_varying_ratio_orthant_certificate(cos_polys, sin_polys, phase_rate, harmonic):
    """Prove the complete derivative with lambda'G retained as selected evidence."""
    try:
        rate = q(phase_rate)
        harmonic = int(harmonic)
        if rate == 0 or harmonic <= 0:
            return None
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        derived = _derive_varying_ratio_shared_factor(c, s)
        if derived.get("status") != "CERTIFIED":
            return derived
        g = s
        sign_cert = v34._strict_common_factor_sign(g)
        if sign_cert.get("status") != "CERTIFIED":
            return sign_cert
        g_sign = int(sign_cert["amplitude_sign_number"])
        lam = [q(x) for x in derived["derived_lambda_polynomial"]]
        lam_prime = _pderiv(lam)
        a = [q(x) for x in derived["A_polynomial"]]
        b = [q(x) for x in derived["B_polynomial"]]
        g_prime = _pderiv(g)
        positive_harmonics, terms, residual_polynomials = v24._mixed_residual_envelope_terms(cos_polys, sin_polys, rate, harmonic)
        retained_terms, retained_polynomials, consumed = [], [], []
        for term, poly in zip(terms, residual_polynomials):
            if term.get("harmonic") == harmonic and term.get("kind") in ("C_prime", "S_prime"):
                consumed.append(term)
                continue
            retained_terms.append(term)
            retained_polynomials.append(_trim(poly))
        ag_prime = _pmul(a, g_prime)
        bg_prime = _pmul(b, g_prime)
        lambda_prime_g = _pmul(lam_prime, g)
        orthant_certificates = []
        residual_count = len(retained_polynomials)
        signed_term_count = 3 + residual_count
        orthant_count_per_sigma = 1 << signed_term_count
        for sigma_b in (-1, 1):
            p_sigma = v22._padd(v22._pscale(a, JOINT_Y_LOWER), v22._pscale(b, -Fraction(sigma_b) * JOINT_X_UPPER))
            phase_base = v22._pscale(_pmul(g, p_sigma), 6 * abs(Fraction(harmonic) * rate) * Fraction(g_sign))
            for mask in range(orthant_count_per_sigma):
                sigma_a = 1 if (mask & 1) else -1
                sigma_t = 1 if (mask & 2) else -1
                sigma_lambda = 1 if (mask & 4) else -1
                margin = v22._padd(phase_base, v22._pscale(ag_prime, -Fraction(sigma_a) * JOINT_X_UPPER))
                margin = v22._padd(margin, v22._pscale(bg_prime, -Fraction(sigma_t) * JOINT_Y_UPPER))
                margin = v22._padd(margin, v22._pscale(lambda_prime_g, -Fraction(sigma_lambda)))
                residual_signs = []
                for index, poly in enumerate(retained_polynomials):
                    sign = 1 if (mask >> (index + 3)) & 1 else -1
                    residual_signs.append(sign)
                    margin = v22._padd(margin, v22._pscale(poly, -Fraction(sign)))
                margin = _trim(margin)
                cert = _strict_positive(margin, f"PB00701_V36_SIGMA_B_{sigma_b}_ORTHANT_{mask}")
                if cert.get("status") == "RESOURCE_REFUSAL":
                    return {**cert, "reason": f"PB00701_V36_SIGMA_B_{sigma_b}_ORTHANT_{mask}_RESOURCE_REFUSAL", "is_truth_value": False}
                if cert.get("status") != "CERTIFIED":
                    return {
                        "status": "BLOCKED",
                        "reason": "PHASE_CORRELATED_VARYING_RATIO_STRICT_MARGIN_NOT_CERTIFIED",
                        "blocker": "PB-007-01",
                        "failed_sigma_B": sigma_b,
                        "failed_orthant": mask,
                        "failed_A_G_prime_sign": sigma_a,
                        "failed_B_G_prime_sign": sigma_t,
                        "failed_lambda_prime_G_sign": sigma_lambda,
                        "failed_residual_signs": residual_signs,
                        "failed_margin_polynomial": [str(x) for x in margin],
                        "failed_margin_certificate": cert,
                        "varying_ratio_shared_factor_certificate": derived,
                        "common_factor_sign_certificate": sign_cert,
                        "retained_residual_terms": retained_terms,
                        "consumed_selected_amplitude_terms": consumed,
                    }
                orthant_certificates.append({
                    "sigma_B": sigma_b,
                    "orthant": mask,
                    "A_G_prime_sign": sigma_a,
                    "B_G_prime_sign": sigma_t,
                    "lambda_prime_G_sign": sigma_lambda,
                    "residual_signs": residual_signs,
                    "margin_polynomial": [str(x) for x in margin],
                    "certificate": cert,
                })
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR_PLUS_NONANCHOR_RESIDUAL_ORTHANT_DOMINANCE",
            "harmonic": harmonic,
            "active_positive_harmonics": positive_harmonics,
            "varying_ratio_shared_factor_certificate": derived,
            "common_factor_polynomial": [str(x) for x in g],
            "common_factor_derivative": [str(x) for x in g_prime],
            "lambda_derivative_polynomial": [str(x) for x in lam_prime],
            "lambda_derivative_times_G_polynomial": [str(x) for x in lambda_prime_g],
            "common_factor_sign_certificate": sign_cert,
            "selected_harmonic_identity": "G'*(A*X+B*Y)+lambda'*G*cos(theta)+2*pi*h*r*G*(A*Y-B*X)",
            "consumed_selected_amplitude_terms": consumed,
            "selected_amplitude_derivatives_consumed_jointly": True,
            "selected_lambda_prime_G_term_retained": lambda_prime_g != [0],
            "selected_phase_terms_consumed_jointly": True,
            "retained_residual_terms": retained_terms,
            "residual_term_count": residual_count,
            "phase_gap_sigma_B_count": 2,
            "orthant_count_per_sigma_B": orthant_count_per_sigma,
            "orthant_count": len(orthant_certificates),
            "orthant_certificates": orthant_certificates,
            "strict_relation": "for both sigma_B and all sign orthants: 6*|h*r|*sign(G)*G*(A*L-sigma_B*B*U)-sigma_A*U*(A*G')-sigma_T*W*(B*G')-sigma_lambda*(lambda'*G)-sum_i sigma_i*R_i>0",
            "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "pi_lower_theorem": "2*pi > 6",
            "caller_lambda_trusted": False,
            "caller_common_factor_trusted": False,
            "caller_margin_trusted": False,
            "binary_float_used": False,
            "sampling_used": False,
            "epsilon_used": False,
            "numerical_trigonometry_used": False,
            "arbitrary_subdivision_cap_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": f"PB00701_V36_PHASE_CORRELATED_VARYING_RATIO_RESOURCE_REFUSAL:{type(exc).__name__}", "is_truth_value": False}


def _phase_correlated_varying_ratio_derivative_certificate(cos_polys, sin_polys, offset, rate, harmonic):
    rate, offset, harmonic = q(rate), q(offset), int(harmonic)
    if rate == 0 or harmonic <= 0:
        return None
    c = _trim(cos_polys.get(harmonic, [0]))
    s = _trim(sin_polys.get(harmonic, [0]))
    derived = _derive_varying_ratio_shared_factor(c, s)
    if derived.get("status") != "CERTIFIED":
        return derived
    t0 = Fraction(harmonic) * offset
    t1 = Fraction(harmonic) * (offset + rate)
    cell = v34._diagonal_phase_cell_certificate(min(t0, t1), max(t0, t1))
    if cell.get("status") != "CERTIFIED":
        return cell
    combined = _phase_correlated_varying_ratio_orthant_certificate(cos_polys, sin_polys, rate, harmonic)
    if combined is None or combined.get("status") != "CERTIFIED":
        return combined
    g_sign = int(combined["common_factor_sign_certificate"]["amplitude_sign_number"])
    diagonal_sign = int(cell["diagonal_projection_sign_number"])
    derivative_sign = v30._sign(Fraction(harmonic) * rate) * g_sign * diagonal_sign
    if derivative_sign == 0:
        raise AssertionError("certified v36 route lost complete derivative sign")
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR_DERIVATIVE_AUTHORITY",
        "harmonic": harmonic,
        "phase_turn_law_local": {"offset": str(offset), "rate": str(rate)},
        "harmonic_phase_turn_law": {"offset": str(Fraction(harmonic) * offset), "rate": str(Fraction(harmonic) * rate)},
        "phase_cell_certificate": cell,
        "phase_correlated_varying_ratio_residual_certificate": combined,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "derivative_sign_number": derivative_sign,
        "selected_harmonic_full_derivative_identity": "G'*(A*X+B*Y)+lambda'*G*cos(theta)+2*pi*h*r*G*(A*Y-B*X)",
        "selected_harmonic_amplitude_derivatives_independently_bounded": False,
        "lambda_prime_G_dropped": False,
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
    }


def _phase_correlated_varying_ratio_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    if rate == 0:
        return None
    harmonics = sorted(h for h in set(cos_polys) | set(sin_polys) if int(h) > 0 and (_trim(cos_polys.get(h, [0])) != [0] or _trim(sin_polys.get(h, [0])) != [0]))
    attempts = []
    for harmonic in harmonics:
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        if c == [0] or s == [0]:
            continue
        derived = _derive_varying_ratio_shared_factor(c, s)
        if derived.get("status") != "CERTIFIED":
            attempts.append(derived)
            continue
        anchor = _phase_correlated_varying_ratio_derivative_certificate(cos_polys, sin_polys, offset, rate, harmonic)
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
            "status": "CERTIFIED",
            "relation": V36_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "phase_correlated_varying_ratio_shared_factor_certificate": anchor,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": "source-owned C_h=lambda(s)*G and S_h=G are regenerated by exact rational-polynomial division with zero remainder; the selected derivative retains lambda'*G and both exact sigma_B phase-gap cases plus every amplitude/non-anchor residual sign orthant are discharged by MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "multiplicity_proof": "the complete derivative never vanishes, so every admitted root is simple",
            "caller_certificate_trusted": False,
            "sampling_used": False,
            "epsilon_used": False,
            "numerical_trigonometry_used": False,
            "approximate_root_ordering_used": False,
            "arbitrary_subdivision_cap_used": False,
        }
    if attempts:
        return {"status": "BLOCKED", "reason": "PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR_EVENT_NOT_CERTIFIED", "blocker": "PB-007-01", "attempts": attempts}
    return None


def analyze_phase_correlated_varying_ratio_shared_factor_event(spec):
    baseline = v35.classify_required_analytic_event(spec)
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
        eligible = old_route.get("status") == "BLOCKED" and "cos_polynomials" in span and "sin_polynomials" in span
        if eligible:
            left = q(span["source_interval"][0])
            right = q(span["source_interval"][1])
            width = right - left
            local_offset = offset_global + rate * left
            local_rate = rate * width
            cos_polys = {int(h): [q(x) for x in poly] for h, poly in span["cos_polynomials"].items()}
            sin_polys = {int(h): [q(x) for x in poly] for h, poly in span["sin_polynomials"].items()}
            replacement = _phase_correlated_varying_ratio_route(cos_polys, sin_polys, local_offset, local_rate, baseline["source_parameter_id"])
            if replacement is not None:
                span["route_kind"] = "PB00701_V36_EXACT_PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR"
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
    result["status"] = status
    result["spans"] = upgraded
    result["relation"] = "FINITE_EXACT_PIECEWISE_PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR_EVENT_DECISION" if status == "CERTIFIED" else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v36_phase_correlated_varying_ratio_shared_factor_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "lambda", "lambda_polynomial", "lambda_derivative", "lambda_prime", "proportionality", "proportionality_scalar",
            "division_quotient", "division_remainder", "polynomial_division_certificate", "common_factor", "common_factor_certificate",
            "common_factor_sign", "varying_ratio_shared_factor_certificate", "coefficient_identities", "A", "B", "A_polynomial",
            "B_polynomial", "A_positive_certificate", "phase_gap_P", "phase_gap_polynomial", "phase_gap_sign_family",
            "diagonal_phase_cell", "diagonal_phase_cell_certificate", "cell_k", "sqrt2_cos_lower", "sqrt2_sin_upper", "sqrt2_upper",
            "joint_phase_bound", "joint_amplitude_bound", "joint_margin", "joint_margin_certificate", "phase_correlated_certificate",
            "phase_correlated_varying_ratio_residual_certificate", "root_count", "root_certificate", "multiplicity",
            "multiplicity_certificate", "sturm_certificate", "sturm_root_count",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_phase_correlated_varying_ratio_shared_factor_event(source_spec)
        return v35.classify_required_analytic_event(source_spec)
    return v35.classify_required_analytic_event(spec)


def resource_refusal():
    return {"status": "RESOURCE_REFUSAL", "reason": "PB00701_V36_EXACT_RESOURCE_REFUSAL", "is_truth_value": False}
