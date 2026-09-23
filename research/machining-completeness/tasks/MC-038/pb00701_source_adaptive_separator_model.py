#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_pythagorean_phase_cell_model as v29  # noqa: E402

v28 = v29.v28
v27 = v29.v27
v26 = v29.v26
v25 = v29.v25
v24 = v29.v24
v23 = v29.v23
v22 = v29.v22
v21 = v29.v21
v20 = v29.v20
v19 = v29.v19
EE = v29.EE
q = v29.q

V30_ROUTE = "EXACT_SOURCE_ADAPTIVE_PROJECTIVE_RATIONAL_SEPARATOR_DERIVATIVE_DOMINANCE"
DOMINANT_QUADRATURE_LOWER = Fraction(12, 13)


class SourceAdaptiveSeparatorRefusal(RuntimeError):
    """Exact-resource refusal. Refusal is never a truth value."""


def _trim(poly):
    return v29._trim([q(value) for value in poly])


def _sign(value):
    return v29._sign(value)


def _tan_pi_8_comparison(candidate):
    """Exact rational comparison against tan(pi/8)=sqrt(2)-1.

    For m >= 0, m > sqrt(2)-1 iff (m+1)^2 > 2.  No numerical
    approximation of sqrt(2) or trigonometry participates.
    """
    m = q(candidate)
    if m < 0:
        return {
            "status": "CERTIFIED",
            "candidate": str(m),
            "relation": "BELOW_TAN_PI_8",
            "above_boundary": False,
            "integer_rational_test": "negative candidate",
            "binary_float_used": False,
        }
    lhs = (m + 1) * (m + 1)
    rhs = Fraction(2)
    above = lhs > rhs
    return {
        "status": "CERTIFIED",
        "candidate": str(m),
        "relation": "ABOVE_TAN_PI_8" if above else "BELOW_TAN_PI_8",
        "above_boundary": above,
        "exact_polynomial_value": str(m * m + 2 * m - 1),
        "integer_rational_test": f"({m}+1)^2 {'>' if above else '<'} 2",
        "algebraic_boundary": "tan(pi/8)=sqrt(2)-1",
        "binary_float_used": False,
        "numerical_trigonometry_used": False,
        "epsilon_used": False,
    }


def _source_adaptive_separator_certificate(
    dominant_poly, transverse_poly, dominant_component, transverse_component
):
    """Synthesize one rational separator directly from canonical source data.

    Let beta = D_floor/T_ceiling, using exact source-owned Bernstein bounds.
    If beta > alpha=sqrt(2)-1, then f(beta)=beta^2+2 beta-1 > 0 and

        beta-alpha = f(beta)/(beta+alpha+2)
                   > f(beta)/(2(beta+1)).

    Therefore

        m = beta - f(beta)/(4(beta+1))

    is rational and satisfies alpha < m < beta.  This is a closed-form,
    finitely terminating synthesis; there is no convergent search, depth cap,
    timeout, sampling, or approximate algebraic comparison.
    """
    try:
        dominant_poly = _trim(dominant_poly)
        transverse_poly = _trim(transverse_poly)
        floor_cert = v24._component_floor_certificate(dominant_poly, dominant_component)
        if floor_cert.get("status") == "RESOURCE_REFUSAL":
            return floor_cert
        if floor_cert.get("status") != "CERTIFIED":
            return {
                "status": "BLOCKED",
                "reason": "SOURCE_ADAPTIVE_DOMINANT_FLOOR_NOT_CERTIFIED",
                "blocker": "PB-007-01",
                "dominant_component": dominant_component,
                "dominant_floor_certificate": floor_cert,
            }

        upper_cert = v25._component_abs_upper_certificate(transverse_poly, transverse_component)
        if upper_cert.get("status") == "RESOURCE_REFUSAL":
            return upper_cert
        if upper_cert.get("status") != "CERTIFIED":
            return {
                "status": "BLOCKED",
                "reason": "SOURCE_ADAPTIVE_TRANSVERSE_CEILING_NOT_CERTIFIED",
                "blocker": "PB-007-01",
                "transverse_component": transverse_component,
                "transverse_ceiling_certificate": upper_cert,
            }

        floor_value = q(floor_cert["strict_rational_amplitude_floor"])
        ceiling_value = q(upper_cert["exact_rational_absolute_ceiling"])
        if floor_value <= 0 or ceiling_value <= 0:
            return {
                "status": "BLOCKED",
                "reason": "SOURCE_ADAPTIVE_PROJECTIVE_RATIO_UNAVAILABLE",
                "blocker": "PB-007-01",
                "dominant_floor": str(floor_value),
                "transverse_ceiling": str(ceiling_value),
                "dominant_floor_certificate": floor_cert,
                "transverse_ceiling_certificate": upper_cert,
            }

        beta = floor_value / ceiling_value
        beta_cmp = _tan_pi_8_comparison(beta)
        if not beta_cmp["above_boundary"]:
            return {
                "status": "BLOCKED",
                "reason": "SOURCE_PROJECTIVE_CEILING_NOT_ABOVE_TAN_PI_8",
                "blocker": "PB-007-01",
                "source_projective_ceiling": str(beta),
                "algebraic_comparison": beta_cmp,
                "dominant_floor_certificate": floor_cert,
                "transverse_ceiling_certificate": upper_cert,
            }

        f_beta = beta * beta + 2 * beta - 1
        if f_beta <= 0:
            raise AssertionError("exact algebraic comparison disagrees with polynomial sign")
        shrink = f_beta / (4 * (beta + 1))
        separator = beta - shrink
        sep_cmp = _tan_pi_8_comparison(separator)
        if not (sep_cmp["above_boundary"] and Fraction(0) < separator < beta):
            raise AssertionError("closed-form rational separator proof failed")

        return {
            "status": "CERTIFIED",
            "relation": "EXACT_SOURCE_DERIVED_CLOSED_FORM_RATIONAL_SEPARATOR_ABOVE_TAN_PI_8",
            "dominant_component": dominant_component,
            "transverse_component": transverse_component,
            "dominant_floor_certificate": floor_cert,
            "transverse_ceiling_certificate": upper_cert,
            "source_projective_ceiling": str(beta),
            "source_projective_ceiling_comparison": beta_cmp,
            "source_polynomial_f_beta": str(f_beta),
            "closed_form_shrink": str(shrink),
            "rational_separator": str(separator),
            "separator_algebraic_comparison": sep_cmp,
            "strict_relation": "tan(pi/8)=sqrt(2)-1 < m < beta=D_floor/T_ceiling",
            "proof": (
                "for f(x)=x^2+2x-1 and alpha=sqrt(2)-1, beta-alpha="
                "f(beta)/(beta+alpha+2)>f(beta)/(2(beta+1)); subtracting only "
                "f(beta)/(4(beta+1)) leaves the rational m strictly above alpha"
            ),
            "finite_termination": "one exact rational source ratio, one exact square comparison, and one closed-form rational expression",
            "caller_separator_trusted": False,
            "caller_algebraic_value_trusted": False,
            "binary_float_used": False,
            "sampling_used": False,
            "epsilon_used": False,
            "numerical_trigonometry_used": False,
            "approximate_algebraic_comparison_used": False,
            "iterative_separator_search_used": False,
            "arbitrary_refinement_cap_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V30_SEPARATOR_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _projective_orthant_certificate(
    cos_polys, sin_polys, phase_rate, harmonic, dominant, dominant_sign, separator
):
    """Prove source-adaptive projective separation plus every retained residual."""
    try:
        rate = q(phase_rate)
        harmonic = int(harmonic)
        dominant_sign = int(dominant_sign)
        m = q(separator)
        if rate == 0 or harmonic <= 0 or dominant_sign not in (-1, 1):
            return None
        cmp_m = _tan_pi_8_comparison(m)
        if not cmp_m["above_boundary"]:
            return {
                "status": "BLOCKED",
                "reason": "RATIONAL_SEPARATOR_NOT_STRICTLY_ABOVE_TAN_PI_8",
                "blocker": "PB-007-01",
                "separator": str(m),
                "algebraic_comparison": cmp_m,
            }

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
        phase_scale = 6 * abs(Fraction(harmonic) * rate) * DOMINANT_QUADRATURE_LOWER
        dominant_base = v22._pscale(
            dominant_poly, phase_scale * Fraction(dominant_sign)
        )
        transverse_scaled = v22._pscale(transverse_poly, phase_scale * m)

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
                margin, f"PB00701_V30_SOURCE_ADAPTIVE_ORTHANT_{mask}"
            )
            if cert.get("status") == "RESOURCE_REFUSAL":
                return {
                    **cert,
                    "reason": f"PB00701_V30_SOURCE_ADAPTIVE_ORTHANT_{mask}_RESOURCE_REFUSAL",
                    "is_truth_value": False,
                }
            if cert.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "SOURCE_ADAPTIVE_PROJECTIVE_RESIDUAL_STRICT_DOMINANCE_NOT_CERTIFIED",
                    "blocker": "PB-007-01",
                    "harmonic": harmonic,
                    "dominant_component": dominant_component,
                    "transverse_component": transverse_component,
                    "rational_separator": str(m),
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
            "relation": "EXACT_SOURCE_ADAPTIVE_PROJECTIVE_SEPARATOR_PLUS_RESIDUAL_ORTHANT_DOMINANCE",
            "harmonic": harmonic,
            "dominant_component": dominant_component,
            "transverse_component": transverse_component,
            "dominant_sign_number": dominant_sign,
            "dominant_quadrature_rational_lower_bound": str(DOMINANT_QUADRATURE_LOWER),
            "rational_separator": str(m),
            "separator_algebraic_comparison": cmp_m,
            "phase_scale": str(phase_scale),
            "active_positive_harmonics": positive_harmonics,
            "residual_terms": terms,
            "residual_term_count": len(residual_polynomials),
            "orthant_count": orthant_count,
            "orthant_certificates": orthant_certificates,
            "strict_relation": (
                "6*|h*r|*(12/13)*(|D(s)|-m*|T(s)|) > sum_i |R_i(s)| "
                "on the complete closed source span, with tan(pi/8)<m"
            ),
            "derivative_implication": (
                "the exact v29 cell gives |dominant quadrature|>12/13 and "
                "|transverse/dominant quadrature|<=tan(pi/8)<m; because 2*pi>6, "
                "the selected mixed phase projection dominates every retained residual pointwise"
            ),
            "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "pi_lower_theorem": "pi > 3",
            "two_pi_rational_upper_bound_for_other_phase_terms": "44/7",
            "finite_termination": "finite 2^(1+N) exact rational-polynomial orthant decisions after closed-form separator synthesis",
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
            "reason": f"PB00701_V30_PROJECTIVE_ORTHANT_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _dominance_attempt(cos_polys, sin_polys, offset, rate, harmonic, dominant):
    c = _trim(cos_polys.get(harmonic, [0]))
    s = _trim(sin_polys.get(harmonic, [0]))
    if c == [0] or s == [0]:
        return None

    if dominant == "SIN":
        dominant_poly, transverse_poly = s, c
        dominant_component, transverse_component = "SIN", "COS"
        phase_component = "COS"
        projection_term = "S*cos"
        projection_sign_factor = 1
    elif dominant == "COS":
        dominant_poly, transverse_poly = c, s
        dominant_component, transverse_component = "COS", "SIN"
        phase_component = "SIN"
        projection_term = "-C*sin"
        projection_sign_factor = -1
    else:
        raise ValueError("dominant must be SIN or COS")

    separator_cert = _source_adaptive_separator_certificate(
        dominant_poly, transverse_poly, dominant_component, transverse_component
    )
    if separator_cert.get("status") == "RESOURCE_REFUSAL":
        return separator_cert
    if separator_cert.get("status") != "CERTIFIED":
        return {
            "status": "BLOCKED",
            "reason": separator_cert.get("reason", "SOURCE_ADAPTIVE_SEPARATOR_NOT_CERTIFIED"),
            "blocker": "PB-007-01",
            "dominant_component": dominant_component,
            "source_adaptive_separator_certificate": separator_cert,
        }

    sign_cert = separator_cert["dominant_floor_certificate"]
    t0 = Fraction(harmonic) * q(offset)
    t1 = Fraction(harmonic) * (q(offset) + q(rate))
    cell = v29._phase_cell_certificate(phase_component, min(t0, t1), max(t0, t1))
    if cell is None:
        return {
            "status": "BLOCKED",
            "reason": f"SOURCE_ADAPTIVE_{phase_component}_PHASE_CELL_CONTAINMENT_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "harmonic": harmonic,
            "harmonic_phase_interval": [str(min(t0, t1)), str(max(t0, t1))],
            "source_adaptive_separator_certificate": separator_cert,
        }

    combined = _projective_orthant_certificate(
        cos_polys, sin_polys, rate, harmonic, dominant,
        sign_cert["amplitude_sign_number"], separator_cert["rational_separator"],
    )
    if combined is None:
        return None
    if combined.get("status") != "CERTIFIED":
        return {
            "status": combined.get("status", "BLOCKED"),
            "reason": combined.get("reason", "SOURCE_ADAPTIVE_PROJECTIVE_RESIDUAL_NOT_CERTIFIED"),
            "blocker": "PB-007-01" if combined.get("status") != "RESOURCE_REFUSAL" else None,
            "dominant_component": dominant_component,
            "source_adaptive_separator_certificate": separator_cert,
            "phase_cell_certificate": cell,
            "combined_certificate": combined,
            **({"is_truth_value": False} if combined.get("status") == "RESOURCE_REFUSAL" else {}),
        }

    dominant_sign = int(sign_cert["amplitude_sign_number"])
    quadrature_sign = int(cell["quadrature_sign_number"])
    projection_sign = projection_sign_factor * dominant_sign * quadrature_sign
    derivative_sign = _sign(Fraction(harmonic) * q(rate)) * projection_sign
    if derivative_sign == 0:
        raise AssertionError("certified v30 source-adaptive route lost derivative sign")

    return {
        "status": "CERTIFIED",
        "relation": "EXACT_SOURCE_DERIVED_PROJECTIVE_RATIONAL_SEPARATOR_DERIVATIVE_AUTHORITY",
        "harmonic": int(harmonic),
        "dominant_component": dominant_component,
        "transverse_component": transverse_component,
        "projection_term": projection_term,
        "source_adaptive_separator_certificate": separator_cert,
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


def _source_adaptive_derivative_certificate(cos_polys, sin_polys, offset, rate, harmonic):
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
        "reason": "SOURCE_ADAPTIVE_PROJECTIVE_RATIONAL_SEPARATOR_ANCHOR_NOT_CERTIFIED",
        "blocker": "PB-007-01",
        "harmonic": harmonic,
        "attempts": attempts,
    }


def _source_adaptive_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    if rate == 0:
        return None
    positive_harmonics, candidates = v25._candidate_anchors(cos_polys, sin_polys)
    if len(positive_harmonics) < 2 or not candidates:
        return None

    attempts = []
    for harmonic in candidates:
        anchor = _source_adaptive_derivative_certificate(
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
            "relation": V30_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": positive_harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "source_adaptive_projective_separator_certificate": anchor,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": (
                "canonical source Bernstein bounds derive beta=D_floor/T_ceiling; one closed-form exact "
                "rational m satisfies tan(pi/8)<m<beta; the v29 exact phase cell supplies dominant "
                "quadrature >12/13, and finite rational-polynomial sign orthants plus MC-032 Sturm "
                "authority prove strict complete-derivative dominance"
            ),
            "multiplicity_proof": (
                "every v30 projective/residual orthant margin is strictly positive on the complete "
                "closed span, so the derivative never vanishes and every admitted root is simple"
            ),
            "caller_certificate_trusted": False,
            "sampling_used": False,
            "epsilon_used": False,
            "numerical_trigonometry_used": False,
            "approximate_algebraic_comparison_used": False,
            "approximate_root_ordering_used": False,
            "iterative_separator_search_used": False,
            "arbitrary_subdivision_cap_used": False,
        }

    if attempts:
        return {
            "status": "BLOCKED",
            "reason": "SOURCE_ADAPTIVE_PROJECTIVE_SEPARATOR_RESIDUAL_EVENT_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "attempts": attempts,
        }
    return None


def analyze_source_adaptive_separator_event(spec):
    baseline = v29.classify_required_analytic_event(spec)
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
            replacement = _source_adaptive_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V30_EXACT_SOURCE_ADAPTIVE_PROJECTIVE_RATIONAL_SEPARATOR"
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
        "FINITE_EXACT_PIECEWISE_SOURCE_ADAPTIVE_PROJECTIVE_SEPARATOR_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v30_source_adaptive_projective_separator_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "source_adaptive_separator", "source_adaptive_separator_certificate",
            "rational_separator", "separator", "separator_certificate",
            "source_projective_ceiling", "projective_ceiling", "tan_pi_8",
            "tan_pi_8_value", "algebraic_boundary", "algebraic_comparison",
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
            return analyze_source_adaptive_separator_event(source_spec)
        return v29.classify_required_analytic_event(source_spec)
    return v29.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V30_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
