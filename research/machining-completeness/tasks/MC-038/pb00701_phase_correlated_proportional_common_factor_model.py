#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_phase_correlated_common_factor_model as v34  # noqa: E402
import pb00701_source_adaptive_separator_model as v30  # noqa: E402

q = v30.q
v24 = v30.v24
v22 = v30.v22
v20 = v30.v20
v19 = v30.v19

V35_ROUTE = "EXACT_PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR_HARMONIC_DERIVATIVE_ANCHOR"
SQRT2_COS_LOWER = v34.SQRT2_COS_LOWER
SQRT2_SIN_UPPER = v34.SQRT2_SIN_UPPER
SQRT2_UPPER = Fraction(99, 70)


def _trim(poly):
    return v34._trim(poly)


def _pderiv(poly):
    return v34._pderiv(poly)


def _poly_coeff(poly, index):
    poly = _trim(poly)
    return poly[index] if index < len(poly) else Fraction(0)


def _derive_proportional_common_factor(cos_poly, sin_poly):
    """Derive C=lambda*G, S=G from source coefficients only."""
    c = _trim(cos_poly)
    g = _trim(sin_poly)
    if c == [0] or g == [0]:
        return {
            "status": "BLOCKED",
            "reason": "SELECTED_HARMONIC_REQUIRES_TWO_NONZERO_QUADRATURES",
            "blocker": "PB-007-01",
        }

    pivot = next((i for i, value in enumerate(g) if value != 0), None)
    if pivot is None:
        return {
            "status": "BLOCKED",
            "reason": "PROPORTIONAL_COMMON_FACTOR_PIVOT_NOT_FOUND",
            "blocker": "PB-007-01",
        }
    lam = _poly_coeff(c, pivot) / _poly_coeff(g, pivot)
    if lam == 0:
        return {
            "status": "BLOCKED",
            "reason": "PROPORTIONALITY_SCALAR_ZERO_DISALLOWED",
            "blocker": "PB-007-01",
        }

    width = max(len(c), len(g))
    identities = []
    for index in range(width):
        lhs = _poly_coeff(c, index)
        rhs = lam * _poly_coeff(g, index)
        identities.append({
            "coefficient": index,
            "C": str(lhs),
            "lambda_times_G": str(rhs),
            "equal": lhs == rhs,
        })
        if lhs != rhs:
            return {
                "status": "BLOCKED",
                "reason": "SELECTED_HARMONIC_NOT_EXACT_RATIONAL_PROPORTIONAL_COMMON_FACTOR",
                "blocker": "PB-007-01",
                "derived_lambda": str(lam),
                "failed_coefficient": index,
                "coefficient_identities": identities,
            }

    a = (lam + 1) / 2
    b = (lam - 1) / 2
    if a <= 0:
        return {
            "status": "BLOCKED",
            "reason": "PROPORTIONAL_FAMILY_REQUIRES_A_POSITIVE",
            "blocker": "PB-007-01",
            "derived_lambda": str(lam),
            "A": str(a),
            "B": str(b),
        }

    p = a * SQRT2_COS_LOWER - abs(b) * SQRT2_SIN_UPPER
    q_upper = abs(a) * SQRT2_SIN_UPPER + abs(b) * SQRT2_UPPER
    if p <= 0:
        return {
            "status": "BLOCKED",
            "reason": "PROPORTIONAL_PHASE_CORRELATION_GAP_NOT_STRICT",
            "blocker": "PB-007-01",
            "derived_lambda": str(lam),
            "A": str(a),
            "B": str(b),
            "phase_gap_P": str(p),
            "joint_amplitude_upper_Q": str(q_upper),
        }

    return {
        "status": "CERTIFIED",
        "relation": "EXACT_SOURCE_DERIVED_RATIONAL_PROPORTIONAL_COMMON_FACTOR",
        "common_factor_polynomial": [str(x) for x in g],
        "derived_lambda": str(lam),
        "pivot_coefficient": pivot,
        "coefficient_identities": identities,
        "A": str(a),
        "B": str(b),
        "phase_gap_P": str(p),
        "joint_amplitude_upper_Q": str(q_upper),
        "joint_phase_lower_L": str(SQRT2_COS_LOWER),
        "joint_transverse_upper_U": str(SQRT2_SIN_UPPER),
        "joint_Y_upper_W": str(SQRT2_UPPER),
        "caller_lambda_trusted": False,
        "caller_common_factor_trusted": False,
        "binary_float_used": False,
    }


def _phase_correlated_proportional_orthant_certificate(
    cos_polys, sin_polys, phase_rate, harmonic
):
    """Prove the complete derivative for C=lambda*G, S=G.

    The selected harmonic is consumed exactly as
      G'*(A*X+B*Y) + 2*pi*h*r*G*(A*Y-B*X),
    with X=cos+sin and Y=cos-sin. Exact diagonal-cell bounds give
      |A*Y-B*X| > P = A*L-|B|*U,
      |A*X+B*Y| < Q = |A|*U+|B|*W.
    Every non-anchor derivative contribution remains explicit and all absolute
    values are discharged by finite exact rational-polynomial sign orthants.
    """
    try:
        rate = q(phase_rate)
        harmonic = int(harmonic)
        if rate == 0 or harmonic <= 0:
            return None
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        proportional = _derive_proportional_common_factor(c, s)
        if proportional.get("status") != "CERTIFIED":
            return proportional

        g = s
        sign_cert = v34._strict_common_factor_sign(g)
        if sign_cert.get("status") != "CERTIFIED":
            return sign_cert
        g_sign = int(sign_cert["amplitude_sign_number"])
        g_prime = _pderiv(g)
        p = q(proportional["phase_gap_P"])
        q_upper = q(proportional["joint_amplitude_upper_Q"])

        positive_harmonics, terms, residual_polynomials = v24._mixed_residual_envelope_terms(
            cos_polys, sin_polys, rate, harmonic
        )
        retained_terms = []
        retained_polynomials = []
        consumed = []
        for term, poly in zip(terms, residual_polynomials):
            if term.get("harmonic") == harmonic and term.get("kind") in ("C_prime", "S_prime"):
                consumed.append(term)
                continue
            retained_terms.append(term)
            retained_polynomials.append(_trim(poly))

        phase_base = v22._pscale(
            g,
            6 * abs(Fraction(harmonic) * rate) * p * Fraction(g_sign),
        )
        joint_amplitude = v22._pscale(g_prime, q_upper)

        orthant_certificates = []
        signed_term_count = 1 + len(retained_polynomials)
        orthant_count = 1 << signed_term_count
        for mask in range(orthant_count):
            amp_sign = 1 if (mask & 1) else -1
            margin = v22._padd(phase_base, v22._pscale(joint_amplitude, -amp_sign))
            residual_signs = []
            for index, poly in enumerate(retained_polynomials):
                sign = 1 if (mask >> (index + 1)) & 1 else -1
                residual_signs.append(sign)
                margin = v22._padd(margin, v22._pscale(poly, -sign))
            margin = _trim(margin)
            cert = v20._strict_positive_certificate(
                margin, f"PB00701_V35_PHASE_CORRELATED_PROPORTIONAL_ORTHANT_{mask}"
            )
            if cert.get("status") == "RESOURCE_REFUSAL":
                return {
                    **cert,
                    "reason": f"PB00701_V35_ORTHANT_{mask}_RESOURCE_REFUSAL",
                    "is_truth_value": False,
                }
            if cert.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "PHASE_CORRELATED_PROPORTIONAL_STRICT_MARGIN_NOT_CERTIFIED",
                    "blocker": "PB-007-01",
                    "failed_orthant": mask,
                    "failed_joint_amplitude_sign": amp_sign,
                    "failed_residual_signs": residual_signs,
                    "failed_margin_polynomial": [str(x) for x in margin],
                    "failed_margin_certificate": cert,
                    "proportional_common_factor_certificate": proportional,
                    "common_factor_sign_certificate": sign_cert,
                    "retained_residual_terms": retained_terms,
                    "consumed_selected_amplitude_terms": consumed,
                }
            orthant_certificates.append({
                "orthant": mask,
                "joint_amplitude_sign": amp_sign,
                "residual_signs": residual_signs,
                "margin_polynomial": [str(x) for x in margin],
                "certificate": cert,
            })

        return {
            "status": "CERTIFIED",
            "relation": "EXACT_PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR_PLUS_NONANCHOR_RESIDUAL_ORTHANT_DOMINANCE",
            "harmonic": harmonic,
            "active_positive_harmonics": positive_harmonics,
            "proportional_common_factor_certificate": proportional,
            "common_factor_polynomial": [str(x) for x in g],
            "common_factor_derivative": [str(x) for x in g_prime],
            "common_factor_sign_certificate": sign_cert,
            "selected_harmonic_identity": "G'*(A*X+B*Y)+2*pi*h*r*G*(A*Y-B*X)",
            "consumed_selected_amplitude_terms": consumed,
            "selected_amplitude_derivatives_consumed_jointly": True,
            "selected_phase_terms_consumed_jointly": True,
            "retained_residual_terms": retained_terms,
            "residual_term_count": len(retained_polynomials),
            "orthant_count": orthant_count,
            "orthant_certificates": orthant_certificates,
            "strict_relation": "6*|h*r|*P*|G(s)|-Q*|G'(s)|-sum_i|R_i(s)|>0",
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
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V35_PHASE_CORRELATED_PROPORTIONAL_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _phase_correlated_proportional_derivative_certificate(
    cos_polys, sin_polys, offset, rate, harmonic
):
    rate, offset, harmonic = q(rate), q(offset), int(harmonic)
    if rate == 0 or harmonic <= 0:
        return None
    c = _trim(cos_polys.get(harmonic, [0]))
    s = _trim(sin_polys.get(harmonic, [0]))
    proportional = _derive_proportional_common_factor(c, s)
    if proportional.get("status") != "CERTIFIED":
        return proportional

    t0 = Fraction(harmonic) * offset
    t1 = Fraction(harmonic) * (offset + rate)
    cell = v34._diagonal_phase_cell_certificate(min(t0, t1), max(t0, t1))
    if cell.get("status") != "CERTIFIED":
        return cell

    combined = _phase_correlated_proportional_orthant_certificate(
        cos_polys, sin_polys, rate, harmonic
    )
    if combined is None or combined.get("status") != "CERTIFIED":
        return combined

    g_sign = int(combined["common_factor_sign_certificate"]["amplitude_sign_number"])
    diagonal_sign = int(cell["diagonal_projection_sign_number"])
    derivative_sign = v30._sign(Fraction(harmonic) * rate) * g_sign * diagonal_sign
    if derivative_sign == 0:
        raise AssertionError("certified v35 route lost complete derivative sign")

    return {
        "status": "CERTIFIED",
        "relation": "EXACT_PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR_DERIVATIVE_AUTHORITY",
        "harmonic": harmonic,
        "phase_turn_law_local": {"offset": str(offset), "rate": str(rate)},
        "harmonic_phase_turn_law": {
            "offset": str(Fraction(harmonic) * offset),
            "rate": str(Fraction(harmonic) * rate),
        },
        "phase_cell_certificate": cell,
        "phase_correlated_proportional_residual_certificate": combined,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "derivative_sign_number": derivative_sign,
        "selected_harmonic_full_derivative_identity": "G'*(A*X+B*Y)+2*pi*h*r*G*(A*Y-B*X)",
        "selected_harmonic_amplitude_derivatives_independently_bounded": False,
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
    }


def _phase_correlated_proportional_route(
    cos_polys, sin_polys, offset, rate, source_parameter_id
):
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
        proportional = _derive_proportional_common_factor(c, s)
        if proportional.get("status") != "CERTIFIED":
            attempts.append(proportional)
            continue
        anchor = _phase_correlated_proportional_derivative_certificate(
            cos_polys, sin_polys, offset, rate, harmonic
        )
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
            "relation": V35_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "phase_correlated_proportional_common_factor_certificate": anchor,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": (
                "source-owned C_h=lambda*G and S_h=G are regenerated coefficientwise with exact rational "
                "lambda; an exact rational diagonal phase cell rewrites the selected harmonic derivative "
                "as G'*(A*X+B*Y)+2*pi*h*r*G*(A*Y-B*X); source-derived P>0 and Q bounds plus finite "
                "MC-032 sign orthants dominate every retained non-anchor residual"
            ),
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
            "reason": "PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR_EVENT_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "attempts": attempts,
        }
    return None


def analyze_phase_correlated_proportional_common_factor_event(spec):
    baseline = v34.classify_required_analytic_event(spec)
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
                int(h): [q(x) for x in poly]
                for h, poly in span["cos_polynomials"].items()
            }
            sin_polys = {
                int(h): [q(x) for x in poly]
                for h, poly in span["sin_polynomials"].items()
            }
            replacement = _phase_correlated_proportional_route(
                cos_polys,
                sin_polys,
                local_offset,
                local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V35_EXACT_PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR"
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
        "FINITE_EXACT_PIECEWISE_PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v35_phase_correlated_proportional_common_factor_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "lambda", "proportionality", "proportionality_scalar",
            "common_factor", "common_factor_certificate", "common_factor_sign",
            "proportional_common_factor_certificate", "coefficient_identities",
            "A", "B", "phase_gap_P", "joint_amplitude_upper_Q",
            "diagonal_phase_cell", "diagonal_phase_cell_certificate", "cell_k",
            "sqrt2_cos_lower", "sqrt2_sin_upper", "sqrt2_upper",
            "joint_phase_bound", "joint_amplitude_bound", "joint_margin",
            "joint_margin_certificate", "phase_correlated_certificate",
            "phase_correlated_proportional_residual_certificate",
            "root_count", "root_certificate", "multiplicity",
            "multiplicity_certificate", "sturm_certificate", "sturm_root_count",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_phase_correlated_proportional_common_factor_event(source_spec)
        return v34.classify_required_analytic_event(source_spec)
    return v34.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V35_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
