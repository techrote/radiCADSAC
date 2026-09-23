#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_phase_correlated_varying_ratio_shared_factor_model as v36  # noqa: E402

q = v36.q
v35 = v36.v35
v34 = v36.v34
v30 = v36.v30
v24 = v36.v24
v22 = v36.v22
v20 = v36.v20
v19 = v36.v19

V37_ROUTE = "EXACT_PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR_HARMONIC_DERIVATIVE_ANCHOR"
JOINT_Y_LOWER = v36.JOINT_Y_LOWER
JOINT_X_UPPER = v36.JOINT_X_UPPER
JOINT_Y_UPPER = v36.JOINT_Y_UPPER

_trim = v36._trim
_pderiv = v36._pderiv
_pmul = v36._pmul
_poly_coeff = v36._poly_coeff
_poly_divmod_exact = v36._poly_divmod_exact
_strict_positive = v36._strict_positive


def _monic(poly):
    poly = _trim(poly)
    if poly == [0]:
        return [Fraction(0)]
    return _trim([value / poly[-1] for value in poly])


def _poly_gcd_monic(a, b):
    """Canonical Euclidean GCD over Q[s], normalized to monic form."""
    a, b = _trim(a), _trim(b)
    if a == [0] and b == [0]:
        return [Fraction(0)]
    try:
        while b != [0]:
            _, remainder = _poly_divmod_exact(a, b)
            a, b = b, remainder
        return _monic(a)
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V37_POLYNOMIAL_GCD_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _a_positive_certificate(a):
    return _strict_positive(_trim(a), "PB00701_V37_A_POSITIVE")


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
            f"PB00701_V37_PHASE_GAP_SIGMA_B_{'P' if sigma_b > 0 else 'M'}",
        )
        certs.append({
            "sigma_B": sigma_b,
            "phase_gap_polynomial": [str(x) for x in p_sigma],
            "certificate": cert,
        })
        if cert.get("status") != "CERTIFIED":
            return {
                "status": cert.get("status", "BLOCKED"),
                "reason": cert.get("reason") if cert.get("status") == "RESOURCE_REFUSAL" else "TWO_POLYNOMIAL_PHASE_GAP_NOT_STRICT",
                "blocker": "PB-007-01",
                "failed_sigma_B": sigma_b,
                "phase_gap_polynomial": [str(x) for x in p_sigma],
                "phase_gap_certificate": cert,
                "phase_gap_certificates": certs,
            }
    return {
        "status": "CERTIFIED",
        "relation": "FINITE_EXACT_TWO_POLYNOMIAL_PHASE_GAP_SIGN_FAMILY",
        "phase_gap_certificates": certs,
    }


def _coefficient_identities(source, factor, quotient, label):
    regenerated = _pmul(quotient, factor)
    width = max(len(_trim(source)), len(regenerated))
    identities = []
    for index in range(width):
        lhs = _poly_coeff(source, index)
        rhs = _poly_coeff(regenerated, index)
        item = {
            "coefficient": index,
            label: str(lhs),
            f"quotient_times_G_{label}": str(rhs),
            "equal": lhs == rhs,
        }
        identities.append(item)
        if lhs != rhs:
            return None, identities
    return regenerated, identities


def _derive_two_polynomial_shared_factor(cos_poly, sin_poly):
    """Derive canonical C=N*G and S=D*G solely from exact source polynomials."""
    c, s = _trim(cos_poly), _trim(sin_poly)
    if c == [0] or s == [0]:
        return {
            "status": "BLOCKED",
            "reason": "SELECTED_HARMONIC_REQUIRES_TWO_NONZERO_QUADRATURES",
            "blocker": "PB-007-01",
        }
    gcd = _poly_gcd_monic(c, s)
    if isinstance(gcd, dict):
        return gcd
    if gcd == [0] or len(gcd) <= 1:
        return {
            "status": "BLOCKED",
            "reason": "TWO_POLYNOMIAL_SHARED_FACTOR_REQUIRES_NONCONSTANT_CANONICAL_GCD",
            "blocker": "PB-007-01",
            "canonical_gcd_polynomial": [str(x) for x in gcd],
        }
    try:
        n, c_remainder = _poly_divmod_exact(c, gcd)
        d, s_remainder = _poly_divmod_exact(s, gcd)
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V37_GCD_DIVISION_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }
    if c_remainder != [0] or s_remainder != [0]:
        return {
            "status": "BLOCKED",
            "reason": "CANONICAL_GCD_DIVISION_REMAINDER_NONZERO",
            "blocker": "PB-007-01",
            "canonical_gcd_polynomial": [str(x) for x in gcd],
            "C_division_remainder": [str(x) for x in c_remainder],
            "S_division_remainder": [str(x) for x in s_remainder],
        }
    _, c_identities = _coefficient_identities(c, gcd, n, "C")
    _, s_identities = _coefficient_identities(s, gcd, d, "S")
    if not all(item["equal"] for item in c_identities + s_identities):
        return {
            "status": "BLOCKED",
            "reason": "CANONICAL_GCD_SOURCE_REGENERATION_FAILED",
            "blocker": "PB-007-01",
            "C_coefficient_identities": c_identities,
            "S_coefficient_identities": s_identities,
        }
    a = _trim(v22._pscale(v22._padd(n, d), Fraction(1, 2)))
    b = _trim(v22._pscale(v22._padd(n, v22._pscale(d, -1)), Fraction(1, 2)))
    a_prime, b_prime = _pderiv(a), _pderiv(b)
    a_cert = _a_positive_certificate(a)
    if a_cert.get("status") != "CERTIFIED":
        return {
            "status": a_cert.get("status", "BLOCKED"),
            "reason": a_cert.get("reason") if a_cert.get("status") == "RESOURCE_REFUSAL" else "TWO_POLYNOMIAL_A_NOT_STRICTLY_POSITIVE",
            "blocker": "PB-007-01",
            "canonical_gcd_polynomial": [str(x) for x in gcd],
            "N_polynomial": [str(x) for x in n],
            "D_polynomial": [str(x) for x in d],
            "A_polynomial": [str(x) for x in a],
            "A_positive_certificate": a_cert,
        }
    gap = _phase_gap_certificates(a, b)
    if gap.get("status") != "CERTIFIED":
        return {
            **gap,
            "canonical_gcd_polynomial": [str(x) for x in gcd],
            "N_polynomial": [str(x) for x in n],
            "D_polynomial": [str(x) for x in d],
            "A_polynomial": [str(x) for x in a],
            "B_polynomial": [str(x) for x in b],
            "A_positive_certificate": a_cert,
            "C_coefficient_identities": c_identities,
            "S_coefficient_identities": s_identities,
        }
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_SOURCE_DERIVED_CANONICAL_TWO_POLYNOMIAL_SHARED_FACTOR",
        "canonical_gcd_normalization": "MONIC_OVER_Q",
        "canonical_gcd_polynomial": [str(x) for x in gcd],
        "N_polynomial": [str(x) for x in n],
        "D_polynomial": [str(x) for x in d],
        "N_derivative_polynomial": [str(x) for x in _pderiv(n)],
        "D_derivative_polynomial": [str(x) for x in _pderiv(d)],
        "C_division_remainder": ["0"],
        "S_division_remainder": ["0"],
        "C_coefficient_identities": c_identities,
        "S_coefficient_identities": s_identities,
        "A_polynomial": [str(x) for x in a],
        "B_polynomial": [str(x) for x in b],
        "A_derivative_polynomial": [str(x) for x in a_prime],
        "B_derivative_polynomial": [str(x) for x in b_prime],
        "A_positive_certificate": a_cert,
        "phase_gap_sign_family": gap,
        "joint_phase_lower_L": str(JOINT_Y_LOWER),
        "joint_transverse_upper_U": str(JOINT_X_UPPER),
        "joint_Y_upper_W": str(JOINT_Y_UPPER),
        "caller_gcd_trusted": False,
        "caller_quotients_trusted": False,
        "caller_common_factor_trusted": False,
        "binary_float_used": False,
    }


def _phase_correlated_two_polynomial_orthant_certificate(cos_polys, sin_polys, phase_rate, harmonic):
    """Prove the complete derivative with both quotient-derivative channels retained."""
    try:
        rate = q(phase_rate)
        harmonic = int(harmonic)
        if rate == 0 or harmonic <= 0:
            return None
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        derived = _derive_two_polynomial_shared_factor(c, s)
        if derived.get("status") != "CERTIFIED":
            return derived
        g = [q(x) for x in derived["canonical_gcd_polynomial"]]
        sign_cert = v34._strict_common_factor_sign(g)
        if sign_cert.get("status") != "CERTIFIED":
            return sign_cert
        g_sign = int(sign_cert["amplitude_sign_number"])
        a = [q(x) for x in derived["A_polynomial"]]
        b = [q(x) for x in derived["B_polynomial"]]
        a_prime = _pderiv(a)
        b_prime = _pderiv(b)
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
        a_prime_g = _pmul(a_prime, g)
        b_prime_g = _pmul(b_prime, g)
        residual_count = len(retained_polynomials)
        signed_term_count = 4 + residual_count
        orthant_count_per_sigma = 1 << signed_term_count
        orthant_certificates = []
        for sigma_b in (-1, 1):
            p_sigma = v22._padd(
                v22._pscale(a, JOINT_Y_LOWER),
                v22._pscale(b, -Fraction(sigma_b) * JOINT_X_UPPER),
            )
            phase_base = v22._pscale(
                _pmul(g, p_sigma),
                6 * abs(Fraction(harmonic) * rate) * Fraction(g_sign),
            )
            for mask in range(orthant_count_per_sigma):
                sigma_ag = 1 if (mask & 1) else -1
                sigma_bg = 1 if (mask & 2) else -1
                sigma_ap = 1 if (mask & 4) else -1
                sigma_bp = 1 if (mask & 8) else -1
                margin = v22._padd(phase_base, v22._pscale(ag_prime, -Fraction(sigma_ag) * JOINT_X_UPPER))
                margin = v22._padd(margin, v22._pscale(bg_prime, -Fraction(sigma_bg) * JOINT_Y_UPPER))
                margin = v22._padd(margin, v22._pscale(a_prime_g, -Fraction(sigma_ap) * JOINT_X_UPPER))
                margin = v22._padd(margin, v22._pscale(b_prime_g, -Fraction(sigma_bp) * JOINT_Y_UPPER))
                residual_signs = []
                for index, poly in enumerate(retained_polynomials):
                    sign = 1 if (mask >> (index + 4)) & 1 else -1
                    residual_signs.append(sign)
                    margin = v22._padd(margin, v22._pscale(poly, -Fraction(sign)))
                margin = _trim(margin)
                cert = _strict_positive(margin, f"PB00701_V37_SIGMA_B_{sigma_b}_ORTHANT_{mask}")
                if cert.get("status") == "RESOURCE_REFUSAL":
                    return {
                        **cert,
                        "reason": f"PB00701_V37_SIGMA_B_{sigma_b}_ORTHANT_{mask}_RESOURCE_REFUSAL",
                        "is_truth_value": False,
                    }
                if cert.get("status") != "CERTIFIED":
                    return {
                        "status": "BLOCKED",
                        "reason": "PHASE_CORRELATED_TWO_POLYNOMIAL_STRICT_MARGIN_NOT_CERTIFIED",
                        "blocker": "PB-007-01",
                        "failed_sigma_B": sigma_b,
                        "failed_orthant": mask,
                        "failed_A_G_prime_sign": sigma_ag,
                        "failed_B_G_prime_sign": sigma_bg,
                        "failed_A_prime_G_sign": sigma_ap,
                        "failed_B_prime_G_sign": sigma_bp,
                        "failed_residual_signs": residual_signs,
                        "failed_margin_polynomial": [str(x) for x in margin],
                        "failed_margin_certificate": cert,
                        "two_polynomial_shared_factor_certificate": derived,
                        "common_factor_sign_certificate": sign_cert,
                        "retained_residual_terms": retained_terms,
                        "consumed_selected_amplitude_terms": consumed,
                    }
                orthant_certificates.append({
                    "sigma_B": sigma_b,
                    "orthant": mask,
                    "A_G_prime_sign": sigma_ag,
                    "B_G_prime_sign": sigma_bg,
                    "A_prime_G_sign": sigma_ap,
                    "B_prime_G_sign": sigma_bp,
                    "residual_signs": residual_signs,
                    "margin_polynomial": [str(x) for x in margin],
                    "certificate": cert,
                })
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR_PLUS_NONANCHOR_RESIDUAL_ORTHANT_DOMINANCE",
            "harmonic": harmonic,
            "active_positive_harmonics": positive_harmonics,
            "two_polynomial_shared_factor_certificate": derived,
            "common_factor_polynomial": [str(x) for x in g],
            "common_factor_derivative": [str(x) for x in g_prime],
            "A_prime_times_G_polynomial": [str(x) for x in a_prime_g],
            "B_prime_times_G_polynomial": [str(x) for x in b_prime_g],
            "common_factor_sign_certificate": sign_cert,
            "selected_harmonic_identity": "G'*(A*X+B*Y)+G*(A'*X+B'*Y)+2*pi*h*r*G*(A*Y-B*X)",
            "equivalent_quotient_derivative_identity": "N'*G*cos(theta)+D'*G*sin(theta)",
            "consumed_selected_amplitude_terms": consumed,
            "selected_amplitude_derivatives_consumed_jointly": True,
            "selected_A_prime_G_term_retained": a_prime_g != [0],
            "selected_B_prime_G_term_retained": b_prime_g != [0],
            "selected_phase_terms_consumed_jointly": True,
            "retained_residual_terms": retained_terms,
            "residual_term_count": residual_count,
            "phase_gap_sigma_B_count": 2,
            "orthant_count_per_sigma_B": orthant_count_per_sigma,
            "orthant_count": len(orthant_certificates),
            "orthant_certificates": orthant_certificates,
            "strict_relation": "for both sigma_B and all sign orthants: 6*|h*r|*sign(G)*G*(A*L-sigma_B*B*U)-sigma_AG*U*(A*G')-sigma_BG*W*(B*G')-sigma_Ap*U*(A'*G)-sigma_Bp*W*(B'*G)-sum_i sigma_i*R_i>0",
            "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "pi_lower_theorem": "2*pi > 6",
            "caller_gcd_trusted": False,
            "caller_quotients_trusted": False,
            "caller_common_factor_trusted": False,
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
            "reason": f"PB00701_V37_PHASE_CORRELATED_TWO_POLYNOMIAL_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _phase_correlated_two_polynomial_derivative_certificate(cos_polys, sin_polys, offset, rate, harmonic):
    rate, offset, harmonic = q(rate), q(offset), int(harmonic)
    if rate == 0 or harmonic <= 0:
        return None
    c = _trim(cos_polys.get(harmonic, [0]))
    s = _trim(sin_polys.get(harmonic, [0]))
    derived = _derive_two_polynomial_shared_factor(c, s)
    if derived.get("status") != "CERTIFIED":
        return derived
    t0 = Fraction(harmonic) * offset
    t1 = Fraction(harmonic) * (offset + rate)
    cell = v34._diagonal_phase_cell_certificate(min(t0, t1), max(t0, t1))
    if cell.get("status") != "CERTIFIED":
        return cell
    combined = _phase_correlated_two_polynomial_orthant_certificate(cos_polys, sin_polys, rate, harmonic)
    if combined is None or combined.get("status") != "CERTIFIED":
        return combined
    g_sign = int(combined["common_factor_sign_certificate"]["amplitude_sign_number"])
    diagonal_sign = int(cell["diagonal_projection_sign_number"])
    derivative_sign = v30._sign(Fraction(harmonic) * rate) * g_sign * diagonal_sign
    if derivative_sign == 0:
        raise AssertionError("certified v37 route lost complete derivative sign")
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR_DERIVATIVE_AUTHORITY",
        "harmonic": harmonic,
        "phase_turn_law_local": {"offset": str(offset), "rate": str(rate)},
        "harmonic_phase_turn_law": {"offset": str(Fraction(harmonic) * offset), "rate": str(Fraction(harmonic) * rate)},
        "phase_cell_certificate": cell,
        "phase_correlated_two_polynomial_residual_certificate": combined,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "derivative_sign_number": derivative_sign,
        "selected_harmonic_full_derivative_identity": "G'*(A*X+B*Y)+G*(A'*X+B'*Y)+2*pi*h*r*G*(A*Y-B*X)",
        "selected_harmonic_amplitude_derivatives_independently_bounded": False,
        "A_prime_G_dropped": False,
        "B_prime_G_dropped": False,
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
    }


def _phase_correlated_two_polynomial_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    if rate == 0:
        return None
    harmonics = sorted(
        h for h in set(cos_polys) | set(sin_polys)
        if int(h) > 0 and (_trim(cos_polys.get(h, [0])) != [0] or _trim(sin_polys.get(h, [0])) != [0])
    )
    attempts = []
    for harmonic in harmonics:
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        if c == [0] or s == [0]:
            continue
        derived = _derive_two_polynomial_shared_factor(c, s)
        if derived.get("status") != "CERTIFIED":
            attempts.append(derived)
            continue
        anchor = _phase_correlated_two_polynomial_derivative_certificate(cos_polys, sin_polys, offset, rate, harmonic)
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
            "relation": V37_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "phase_correlated_two_polynomial_shared_factor_certificate": anchor,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": "source-owned C_h=N(s)*G and S_h=D(s)*G are regenerated from the monic exact rational-polynomial GCD with zero remainders; both quotient-derivative channels, both sigma_B phase-gap cases, both common-factor derivative channels, and every non-anchor residual sign orthant are discharged by MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "multiplicity_proof": "the complete derivative never vanishes, so every admitted root is simple",
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
            "reason": "PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR_EVENT_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "attempts": attempts,
        }
    return None


def analyze_phase_correlated_two_polynomial_shared_factor_event(spec):
    baseline = v36.classify_required_analytic_event(spec)
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
            replacement = _phase_correlated_two_polynomial_route(
                cos_polys,
                sin_polys,
                local_offset,
                local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V37_EXACT_PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR"
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
        "FINITE_EXACT_PIECEWISE_PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v37_phase_correlated_two_polynomial_shared_factor_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "gcd", "gcd_polynomial", "gcd_certificate", "canonical_gcd", "canonical_gcd_polynomial",
            "common_factor", "common_factor_certificate", "common_factor_sign", "N", "D", "N_polynomial",
            "D_polynomial", "N_derivative", "D_derivative", "quotient_N", "quotient_D", "quotient_certificate",
            "division_quotient", "division_remainder", "C_division_remainder", "S_division_remainder",
            "coefficient_identities", "A", "B", "A_polynomial", "B_polynomial", "A_prime", "B_prime",
            "A_positive_certificate", "phase_gap_P", "phase_gap_polynomial", "phase_gap_sign_family",
            "diagonal_phase_cell", "diagonal_phase_cell_certificate", "cell_k", "sqrt2_cos_lower",
            "sqrt2_sin_upper", "sqrt2_upper", "joint_phase_bound", "joint_amplitude_bound", "joint_margin",
            "joint_margin_certificate", "phase_correlated_certificate", "phase_correlated_two_polynomial_residual_certificate",
            "root_count", "root_certificate", "multiplicity", "multiplicity_certificate", "sturm_certificate", "sturm_root_count",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_phase_correlated_two_polynomial_shared_factor_event(source_spec)
        return v36.classify_required_analytic_event(source_spec)
    return v36.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V37_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
