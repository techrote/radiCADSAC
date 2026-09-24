#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pb00701_orientation_transition_bridge_model as v42  # noqa: E402

v40 = v42.v40
v39 = v42.v39
v34 = v42.v34
v30 = v42.v30
v27 = v30.v27
v24 = v42.v24
v22 = v42.v22
v19 = v42.v19
EE = v30.EE
q = v42.q
_trim = v42._trim
_pderiv = v42._pderiv
_strict_positive = v42._strict_positive

V43_ROUTE = "EXACT_CORRELATED_CLOSED_HANDOFF_DERIVATIVE_CERTIFICATE"
Y_LOWER = v42.Y_LOWER
X_UPPER = v42.X_UPPER
Y_UPPER = v42.Y_UPPER
TWO_PI_UPPER = v42.TWO_PI_UPPER
TWO_PI_LOWER = Fraction(6)


def _peval(poly, x):
    x = q(x)
    out = Fraction(0)
    for value in reversed(_trim(poly)):
        out = out * x + q(value)
    return out


def _relation_sign(relation):
    return {"NEGATIVE": -1, "ZERO": 0, "POSITIVE": 1}.get(relation)


def _closed_weak_sign(poly, label, *, allow_zero=False):
    """Exact fixed weak sign on closed [0,1], allowing endpoint zeros.

    This intentionally refuses interior roots even when their multiplicity might
    preserve sign. V43 needs only the endpoint-handoff case; broader root
    partitioning remains owned by #245.
    """
    try:
        p = _trim(poly)
        if p == [0]:
            if allow_zero:
                return {
                    "status": "CERTIFIED",
                    "relation": "EXACT_IDENTICALLY_ZERO_WEAK_SIGN",
                    "sign_number": 0,
                    "polynomial": ["0"],
                    "endpoint_zero_allowed": True,
                    "interior_roots_allowed": False,
                }
            return {
                "status": "BLOCKED",
                "reason": f"{label}_IDENTICALLY_ZERO",
                "blocker": "PB-007-01",
            }

        left = EE.exact_event(p, Fraction(0))
        right = EE.exact_event(p, Fraction(1))
        roots = int(EE.distinct_roots_open(p, Fraction(0), Fraction(1)))
        if roots:
            return {
                "status": "BLOCKED",
                "reason": f"{label}_INTERIOR_ROOT",
                "blocker": "PB-007-01",
                "distinct_roots_open": roots,
                "left_event": left,
                "right_event": right,
                "polynomial": [str(x) for x in p],
            }

        midpoint = EE.exact_event(p, Fraction(1, 2))
        signs = [
            _relation_sign(left.get("relation")),
            _relation_sign(midpoint.get("relation")),
            _relation_sign(right.get("relation")),
        ]
        if any(sign is None for sign in signs):
            raise ArithmeticError("exact weak-sign relation unavailable")
        nonzero = [sign for sign in signs if sign]
        if not nonzero:
            return {
                "status": "BLOCKED",
                "reason": f"{label}_SIGN_NOT_DERIVED",
                "blocker": "PB-007-01",
                "left_event": left,
                "midpoint_event": midpoint,
                "right_event": right,
            }
        sigma = nonzero[0]
        if any(sign not in (0, sigma) for sign in signs):
            return {
                "status": "BLOCKED",
                "reason": f"{label}_ENDPOINT_SIGN_MISMATCH",
                "blocker": "PB-007-01",
                "left_event": left,
                "midpoint_event": midpoint,
                "right_event": right,
            }
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_CLOSED_INTERVAL_WEAK_SIGN_WITH_ENDPOINT_ZEROS",
            "sign_number": sigma,
            "polynomial": [str(x) for x in p],
            "left_event": left,
            "midpoint_event": midpoint,
            "right_event": right,
            "distinct_roots_open": 0,
            "endpoint_zero_allowed": True,
            "interior_roots_allowed": False,
            "caller_sign_trusted": False,
            "binary_float_used": False,
            "epsilon_used": False,
            "sampling_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V43_{label}_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _derive_correlated_coordinates(cos_poly, sin_poly):
    c, s = _trim(cos_poly), _trim(sin_poly)
    if c == [0] or s == [0]:
        return {
            "status": "BLOCKED",
            "reason": "CORRELATED_HANDOFF_REQUIRES_TWO_NONZERO_SOURCE_QUADRATURES",
            "blocker": "PB-007-01",
        }
    try:
        a = _trim(v22._pscale(v22._padd(c, s), Fraction(1, 2)))
        b = _trim(v22._pscale(v22._padd(c, v22._pscale(s, -1)), Fraction(1, 2)))
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_SOURCE_DERIVED_CORRELATED_ROTATED_COORDINATES",
            "C_polynomial": [str(x) for x in c],
            "S_polynomial": [str(x) for x in s],
            "A_polynomial": [str(x) for x in a],
            "B_polynomial": [str(x) for x in b],
            "A_derivative_polynomial": [str(x) for x in _pderiv(a)],
            "B_derivative_polynomial": [str(x) for x in _pderiv(b)],
            "source_coordinates_regenerated": True,
            "caller_orientation_trusted": False,
            "caller_derivatives_trusted": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V43_COORDINATE_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _correlated_orthant_certificate(cos_polys, sin_polys, phase_rate, harmonic, diagonal_sign):
    """Certify the complete derivative with a correlated favorable Y channel.

    For Y=d*y, y in [L,W], orient the physical derivative by t=eta*d where
    eta is chosen so eta*h*r*A >= 0 over the complete closed span. Then

      t*D = eta*B'*y + 2*pi*eta*h*r*A*y
            + eta*d*X*A' - 2*pi*eta*d*X*h*r*B + retained residuals.

    Unlike v42, the A*Y phase contribution is kept favorable when its
    source-derived sign aligns with the target orientation.
    """
    try:
        rate = q(phase_rate)
        harmonic = int(harmonic)
        diagonal_sign = int(diagonal_sign)
        if rate == 0 or harmonic <= 0 or diagonal_sign not in (-1, 1):
            return None

        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        derived = _derive_correlated_coordinates(c, s)
        if derived.get("status") != "CERTIFIED":
            return derived

        a = [q(x) for x in derived["A_polynomial"]]
        b = [q(x) for x in derived["B_polynomial"]]
        a_prime = [q(x) for x in derived["A_derivative_polynomial"]]
        b_prime = [q(x) for x in derived["B_derivative_polynomial"]]

        a_sign = _closed_weak_sign(a, "A_HANDOFF_WEAK_SIGN")
        if a_sign.get("status") != "CERTIFIED":
            return a_sign
        sigma_a = int(a_sign["sign_number"])
        hr = Fraction(harmonic) * rate
        eta = sigma_a * (1 if hr > 0 else -1)
        if eta not in (-1, 1):
            raise AssertionError("correlated handoff orientation vanished")

        phase_a_oriented = _trim(v22._pscale(a, Fraction(eta) * hr))
        phase_a_sign = _closed_weak_sign(
            phase_a_oriented, "ORIENTED_PHASE_A_WEAK_SIGN"
        )
        if phase_a_sign.get("status") != "CERTIFIED" or int(phase_a_sign["sign_number"]) != 1:
            return {
                "status": "BLOCKED",
                "reason": "CORRELATED_HANDOFF_PHASE_A_NOT_WEAKLY_FAVORABLE",
                "blocker": "PB-007-01",
                "phase_A_sign_certificate": phase_a_sign,
            }

        b_prime_oriented = _trim(v22._pscale(b_prime, eta))
        bp_sign = _closed_weak_sign(
            b_prime_oriented, "ORIENTED_B_PRIME_WEAK_SIGN", allow_zero=True
        )
        if bp_sign.get("status") != "CERTIFIED":
            return bp_sign
        sigma_bp = int(bp_sign["sign_number"])

        margin_base = [Fraction(0)]
        if sigma_bp > 0:
            margin_base = v22._padd(
                margin_base, v22._pscale(b_prime_oriented, Y_LOWER)
            )
            bprime_y_bound = "L*eta*B' (weakly favorable)"
        elif sigma_bp < 0:
            margin_base = v22._padd(
                margin_base, v22._pscale(b_prime_oriented, Y_UPPER)
            )
            bprime_y_bound = "W*eta*B' (weakly adverse)"
        else:
            bprime_y_bound = "0 (B' identically zero)"

        margin_base = v22._padd(
            margin_base,
            v22._pscale(phase_a_oriented, TWO_PI_LOWER * Y_LOWER),
        )

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

        phase_b = _trim(v22._pscale(b, hr))
        residual_count = len(retained_polynomials)
        orthant_count = 1 << (2 + residual_count)
        certs = []
        for mask in range(orthant_count):
            sigma_ap = 1 if (mask & 1) else -1
            sigma_phase_b = 1 if (mask & 2) else -1
            margin = list(margin_base)
            margin = v22._padd(
                margin,
                v22._pscale(a_prime, -Fraction(sigma_ap) * X_UPPER),
            )
            margin = v22._padd(
                margin,
                v22._pscale(
                    phase_b,
                    -TWO_PI_UPPER * X_UPPER * Fraction(sigma_phase_b),
                ),
            )
            residual_signs = []
            for index, poly in enumerate(retained_polynomials):
                sign = 1 if (mask >> (index + 2)) & 1 else -1
                residual_signs.append(sign)
                margin = v22._padd(margin, v22._pscale(poly, -Fraction(sign)))
            margin = _trim(margin)
            cert = _strict_positive(margin, f"PB00701_V43_CORRELATED_ORTHANT_{mask}")
            if cert.get("status") == "RESOURCE_REFUSAL":
                return {
                    **cert,
                    "reason": f"PB00701_V43_CORRELATED_ORTHANT_{mask}_RESOURCE_REFUSAL",
                    "is_truth_value": False,
                }
            if cert.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "CORRELATED_CLOSED_HANDOFF_STRICT_MARGIN_NOT_CERTIFIED",
                    "blocker": "PB-007-01",
                    "failed_orthant": mask,
                    "failed_A_prime_sign": sigma_ap,
                    "failed_phase_B_sign": sigma_phase_b,
                    "failed_residual_signs": residual_signs,
                    "failed_margin_polynomial": [str(x) for x in margin],
                    "failed_margin_certificate": cert,
                    "correlated_coordinate_certificate": derived,
                    "A_weak_sign_certificate": a_sign,
                    "oriented_B_prime_weak_sign_certificate": bp_sign,
                    "retained_residual_terms": retained_terms,
                    "consumed_selected_amplitude_terms": consumed,
                }
            certs.append({
                "orthant": mask,
                "A_prime_sign": sigma_ap,
                "phase_B_sign": sigma_phase_b,
                "residual_signs": residual_signs,
                "margin_polynomial": [str(x) for x in margin],
                "certificate": cert,
            })

        return {
            "status": "CERTIFIED",
            "relation": "EXACT_CORRELATED_Y_CHANNEL_PLUS_TRANSVERSE_RESIDUAL_ORTHANT_DOMINANCE",
            "harmonic": harmonic,
            "eta": eta,
            "sigma_A_weak": sigma_a,
            "sigma_eta_B_prime_weak": sigma_bp,
            "diagonal_projection_sign_number": diagonal_sign,
            "derivative_sign_number": eta * diagonal_sign,
            "correlated_coordinate_certificate": derived,
            "A_weak_sign_certificate": a_sign,
            "oriented_B_prime_weak_sign_certificate": bp_sign,
            "physical_selected_harmonic_identity": "D=A'*X+B'*Y+2*pi*h*r*(A*Y-B*X)",
            "oriented_correlated_identity": (
                "eta*d*D=eta*B'*|Y|+2*pi*eta*h*r*A*|Y|"
                "+eta*d*X*A'-2*pi*eta*d*X*h*r*B+retained residuals"
            ),
            "B_prime_Y_bound": bprime_y_bound,
            "favorable_phase_A_bound": "2*pi*eta*h*r*A*|Y| >= 6*L*eta*h*r*A",
            "transverse_A_prime_bound": "|X*A'| <= U*|A'|",
            "transverse_phase_B_bound": "|2*pi*h*r*B*X| < (44/7)*U*|h*r*B|",
            "joint_Y_lower_L": str(Y_LOWER),
            "joint_X_upper_U": str(X_UPPER),
            "joint_Y_upper_W": str(Y_UPPER),
            "two_pi_lower": str(TWO_PI_LOWER),
            "two_pi_upper": str(TWO_PI_UPPER),
            "selected_amplitude_derivatives_consumed_jointly": True,
            "selected_phase_terms_consumed_jointly": True,
            "retained_residual_terms": retained_terms,
            "residual_term_count": residual_count,
            "orthant_count": orthant_count,
            "orthant_certificates": certs,
            "sturm_authority": "MC-032 exact rational closed-interval endpoint/Sturm strict positivity",
            "weak_sign_authority": "exact endpoint signs plus zero open roots; endpoint zeros allowed",
            "finite_termination": "finite exact sign decisions plus 2^(2+N) rational-polynomial orthants",
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
            "reason": f"PB00701_V43_CORRELATED_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _correlated_derivative_certificate(cos_polys, sin_polys, offset, rate, harmonic):
    rate, offset, harmonic = q(rate), q(offset), int(harmonic)
    if rate == 0 or harmonic <= 0:
        return None
    t0 = Fraction(harmonic) * offset
    t1 = Fraction(harmonic) * (offset + rate)
    cell = v34._diagonal_phase_cell_certificate(min(t0, t1), max(t0, t1))
    if cell.get("status") != "CERTIFIED":
        return cell
    diagonal_sign = int(cell["diagonal_projection_sign_number"])
    combined = _correlated_orthant_certificate(
        cos_polys, sin_polys, rate, harmonic, diagonal_sign
    )
    if combined is None or combined.get("status") != "CERTIFIED":
        return combined
    derivative_sign = int(combined["derivative_sign_number"])
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_CORRELATED_CLOSED_HANDOFF_DERIVATIVE_AUTHORITY",
        "harmonic": harmonic,
        "phase_turn_law_local": {"offset": str(offset), "rate": str(rate)},
        "harmonic_phase_turn_law": {
            "offset": str(Fraction(harmonic) * offset),
            "rate": str(Fraction(harmonic) * rate),
        },
        "phase_cell_certificate": cell,
        "correlated_handoff_residual_certificate": combined,
        "direction": "INCREASING" if derivative_sign > 0 else "DECREASING",
        "derivative_sign_number": derivative_sign,
        "sign_identity": "sign(D)=eta*diagonal_projection_sign",
        "orientation_handoff_is_proof_bookkeeping_only": True,
        "proof_cut_is_physical_event": False,
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
    }


def _correlated_handoff_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
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
        anchor = _correlated_derivative_certificate(
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
            "relation": V43_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": harmonics,
            "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
            "correlated_closed_handoff_certificate": anchor,
            "left_event": left_event,
            "right_event": right_event,
            **root_summary,
            "complete_derivative_proof": (
                "source-owned A/B coordinates are regenerated exactly; A has one weak closed sign "
                "with endpoint zeros allowed; eta orients the A*Y phase channel favorably; eta*B'*Y "
                "uses its exact weak sign and rational Y bounds; A'*X, B*X and every non-anchor "
                "derivative residual are bounded adversely by finite exact rational-polynomial orthants"
            ),
            "multiplicity_proof": "the complete derivative has a strict nonzero sign on the closed span",
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
            "reason": "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "attempts": attempts,
        }
    return None


def analyze_correlated_closed_handoff_event(spec):
    baseline = v42.classify_required_analytic_event(spec)
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
            cos_polys = {
                int(h): [q(x) for x in poly]
                for h, poly in span["cos_polynomials"].items()
            }
            sin_polys = {
                int(h): [q(x) for x in poly]
                for h, poly in span["sin_polynomials"].items()
            }
            replacement = _correlated_handoff_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"]
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"
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
        "FINITE_EXACT_PIECEWISE_CORRELATED_CLOSED_HANDOFF_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v43_correlated_closed_handoff_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source = dict(spec)
        for key in (
            "A", "B", "A_prime", "B_prime", "eta", "orientation",
            "orientation_certificate", "weak_sign_certificate",
            "correlated_handoff_certificate", "correlated_margin",
            "correlated_margin_certificate", "derivative_certificate",
            "root_count", "root_certificate", "multiplicity",
            "multiplicity_certificate", "sturm_certificate", "sturm_root_count",
        ):
            source.pop(key, None)
        if source.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_correlated_closed_handoff_event(source)
        return v42.classify_required_analytic_event(source)
    return v42.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V43_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
