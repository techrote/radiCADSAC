#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_finite_multiplier_model as v15  # noqa: E402

EE = v15.EE
q = v15.q
V16_ROUTE = "EXACT_CHEBYSHEV_STURM_FINITE_EVEN_COSINE_MULTIPLIER_TO_SINGLE_HARMONIC"


class ChebyshevSturmRefusal(RuntimeError):
    """Bounded exact-resource refusal. Never a truth value."""


def _trim(poly):
    return v15._trim([q(value) for value in poly])


def _padd(left, right):
    left = _trim(left)
    right = _trim(right)
    out = [Fraction(0)] * max(len(left), len(right))
    for i, value in enumerate(left):
        out[i] += value
    for i, value in enumerate(right):
        out[i] += value
    return _trim(out)


def _psub(left, right):
    return _padd(left, [-q(value) for value in right])


def _pscale(poly, scalar):
    scalar = q(scalar)
    return _trim([q(value) * scalar for value in poly])


def _xmul(poly):
    return _trim([Fraction(0), *[q(value) for value in poly]])


def chebyshev_basis(degree):
    """Return exact ascending-power T_0..T_degree over Q[x]."""
    degree = int(degree)
    if degree < 0:
        raise ValueError("negative Chebyshev degree")
    basis = [[Fraction(1)]]
    if degree == 0:
        return basis
    basis.append([Fraction(0), Fraction(1)])
    for _ in range(1, degree):
        basis.append(_trim(_psub(_pscale(_xmul(basis[-1]), 2), basis[-2])))
    return basis


def chebyshev_polynomial(lambda_vector):
    """Convert sum lambda_k*T_k(x) to an exact Q[x] polynomial."""
    lambdas = [q(value) for value in lambda_vector]
    if not lambdas:
        raise ValueError("empty multiplier")
    basis = chebyshev_basis(len(lambdas) - 1)
    poly = [Fraction(0)]
    for value, term in zip(lambdas, basis):
        poly = _padd(poly, _pscale(term, value))
    return _trim(poly)


def certify_chebyshev_nonvanishing(lambda_vector):
    """Prove exact nonvanishing of M(alpha) through P(x), x in [-1,1]."""
    try:
        lambdas = [q(value) for value in lambda_vector]
        poly = chebyshev_polynomial(lambdas)
        left = EE.exact_event(poly, Fraction(-1))
        right = EE.exact_event(poly, Fraction(1))
        left_relation = left.get("relation")
        right_relation = right.get("relation")
        if left_relation == "ZERO" or right_relation == "ZERO":
            return {
                "status": "BLOCKED",
                "reason": "CHEBYSHEV_MULTIPLIER_ENDPOINT_ROOT",
                "blocker": "PB-007-01",
                "lambda_vector": [str(value) for value in lambdas],
                "chebyshev_polynomial": [str(value) for value in poly],
                "closed_interval": ["-1", "1"],
                "endpoint_signs": {"-1": left_relation, "1": right_relation},
                "caller_certificate_trusted": False,
            }
        root_count = EE.distinct_roots_open(poly, Fraction(-1), Fraction(1))
        if root_count != 0:
            return {
                "status": "BLOCKED",
                "reason": "CHEBYSHEV_MULTIPLIER_INTERIOR_ROOT",
                "blocker": "PB-007-01",
                "lambda_vector": [str(value) for value in lambdas],
                "chebyshev_polynomial": [str(value) for value in poly],
                "closed_interval": ["-1", "1"],
                "endpoint_signs": {"-1": left_relation, "1": right_relation},
                "open_interval_distinct_root_count": int(root_count),
                "caller_certificate_trusted": False,
            }
        midpoint = EE.exact_event(poly, Fraction(0))
        midpoint_relation = midpoint.get("relation")
        if midpoint_relation == "ZERO":
            raise AssertionError("zero midpoint with zero Sturm root count")
        if midpoint_relation not in {"POSITIVE", "NEGATIVE"}:
            raise ArithmeticError("exact midpoint sign unavailable")
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_RATIONAL_CHEBYSHEV_STURM_CLOSED_INTERVAL_NONVANISHING",
            "lambda_vector": [str(value) for value in lambdas],
            "chebyshev_polynomial": [str(value) for value in poly],
            "closed_interval": ["-1", "1"],
            "endpoint_signs": {"-1": left_relation, "1": right_relation},
            "open_interval_distinct_root_count": 0,
            "multiplier_sign": midpoint_relation,
            "source": "MC-032_EXACT_RATIONAL_STURM_AUTHORITY",
            "caller_certificate_trusted": False,
            "binary_float_used": False,
            "epsilon_used": False,
            "sampling_used": False,
            "numeric_trigonometry_used": False,
            "approximate_minimization_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V16_EXACT_STURM_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _upgrade_span(route, local_offset, local_rate, source_parameter_id):
    factorization = None
    if isinstance(route, dict):
        if route.get("relation") == "EXACT_FINITE_STRICT_DOMINANCE_EVEN_COSINE_MULTIPLIER_FACTORIZATION":
            factorization = route
        elif isinstance(route.get("factorization"), dict):
            factorization = route["factorization"]
    if not isinstance(factorization, dict):
        return None
    if factorization.get("relation") != "EXACT_FINITE_STRICT_DOMINANCE_EVEN_COSINE_MULTIPLIER_FACTORIZATION":
        return None
    if factorization.get("reason") != "FINITE_MULTIPLIER_STRICT_DOMINANCE_NOT_CERTIFIED":
        return None

    certificate = certify_chebyshev_nonvanishing(factorization["lambda_vector"])
    if certificate.get("status") != "CERTIFIED":
        result = {
            "status": certificate.get("status", "BLOCKED"),
            "reason": certificate.get("reason", "CHEBYSHEV_NONVANISHING_NOT_CERTIFIED"),
            "blocker": "PB-007-01",
            "factorization": factorization,
            "chebyshev_nonvanishing": certificate,
        }
        if certificate.get("status") == "RESOURCE_REFUSAL":
            result["is_truth_value"] = False
        return result

    carrier_a = [q(value) for value in factorization["carrier_cos_polynomial"]]
    carrier_b = [q(value) for value in factorization["carrier_sin_polynomial"]]
    if EE.degree(EE.pgcd(carrier_a, carrier_b)) > 0:
        return {
            "status": "BLOCKED",
            "reason": "CARRIER_COMMON_FACTOR_REMAINS_OWNED_BY_PB00701_V8",
            "blocker": "PB-007-01",
            "factorization": factorization,
            "chebyshev_nonvanishing": certificate,
        }

    carrier, route_kind = v15._delegate_carrier(
        carrier_a, carrier_b, int(factorization["harmonic"]), q(local_offset), q(local_rate), source_parameter_id
    )
    if carrier.get("status") != "CERTIFIED":
        return {
            "status": carrier.get("status", "BLOCKED"),
            "reason": carrier.get("reason", "CARRIER_EXACT_EVENT_ROUTE_NOT_CERTIFIED"),
            "blocker": "PB-007-01",
            "factorization": factorization,
            "chebyshev_nonvanishing": certificate,
            "carrier_route_kind": route_kind,
            "carrier": carrier,
        }
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_CHEBYSHEV_STURM_MULTIHARMONIC_EVENT_REDUCTION",
        "source_parameter_id": source_parameter_id,
        "factorization": factorization,
        "chebyshev_nonvanishing": certificate,
        "carrier_route_kind": route_kind,
        "carrier": carrier,
        "zero_set_equivalence": "P(cos(2*alpha)) is exactly nonzero for x in [-1,1], so original event zeros are exactly carrier zeros",
        "multiplicity_preservation": "the exact smooth globally nonzero multiplier preserves finite carrier root multiplicities",
        "new_transcendental_zero_oracle_used": False,
        "numeric_trigonometry_used": False,
        "sampling_used": False,
    }


def analyze_chebyshev_multiplier_event(spec):
    baseline = v15.classify_required_analytic_event(spec)
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
        replacement = None
        if span.get("route_kind") == "PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER":
            left = q(span["source_interval"][0])
            right = q(span["source_interval"][1])
            width = right - left
            replacement = _upgrade_span(
                span.get("route", {}),
                offset_global + rate * left,
                rate * width,
                baseline["source_parameter_id"],
            )
        if replacement is not None:
            span["route_kind"] = "PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER"
            span["route"] = replacement
            span["local_phase_turn_law"] = {
                "offset": str(offset_global + rate * q(span["source_interval"][0])),
                "rate": str(rate * (q(span["source_interval"][1]) - q(span["source_interval"][0]))),
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
        "FINITE_EXACT_PIECEWISE_CHEBYSHEV_STURM_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v16_chebyshev_sturm_multiplier_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "lambda_vector", "factorization", "chebyshev_polynomial", "chebyshev_coefficients",
            "sturm_certificate", "sturm_root_count", "multiplier_sign", "root_free",
            "nonvanishing_certificate",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_chebyshev_multiplier_event(source_spec)
        return v15.classify_required_analytic_event(source_spec)
    return v15.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V16_CHEBYSHEV_STURM_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
