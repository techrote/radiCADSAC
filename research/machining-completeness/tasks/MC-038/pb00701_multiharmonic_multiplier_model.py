#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_component_partition_model as v12  # noqa: E402

v11 = v12.v11
v10 = v12.v10
v9 = v12.v9
v8 = v12.v8
v7 = v12.v7
EE = v12.EE
q = v12.q


class MultiHarmonicMultiplierRefusal(RuntimeError):
    """Bounded resource refusal. Never a truth value."""


def _trim(poly):
    return v12._trim(poly)


def _pscale(poly, scalar):
    return v7._pscale(poly, scalar)


def _poly_equal(left, right):
    return _trim(left) == _trim(right)


def _scalar_ratio(numerator, denominator):
    """Return exact r when numerator == r*denominator, else None."""
    numerator = _trim(numerator)
    denominator = _trim(denominator)
    if numerator == [0] or denominator == [0]:
        return None
    width = max(len(numerator), len(denominator))
    num = numerator + [Fraction(0)] * (width - len(numerator))
    den = denominator + [Fraction(0)] * (width - len(denominator))
    pivot = next((index for index, value in enumerate(den) if value != 0), None)
    if pivot is None:
        return None
    ratio = num[pivot] / den[pivot]
    if all(n == ratio * d for n, d in zip(num, den)):
        return ratio
    return None


def detect_nonvanishing_even_multiplier(cos_polys, sin_polys):
    """Detect an exact {h,3h} factorization from source coefficients.

    The admitted family is

      (lambda + cos(2*alpha)) * (A cos(alpha) + B sin(alpha)),
      alpha = 2*pi*h*theta_turn.

    Therefore source coefficients must satisfy exactly
      C_h  = (lambda+1/2) A,  S_h  = (lambda-1/2) B,
      C_3h = A/2,             S_3h = B/2.
    """
    cos_nonzero = {
        int(h): _trim(poly) for h, poly in cos_polys.items() if _trim(poly) != [0]
    }
    sin_nonzero = {
        int(h): _trim(poly) for h, poly in sin_polys.items() if _trim(poly) != [0]
    }
    harmonics = set(cos_nonzero) | set(sin_nonzero)
    if len(harmonics) != 2:
        return None
    harmonic = min(harmonics)
    if harmonic <= 0 or max(harmonics) != 3 * harmonic:
        return None
    third = 3 * harmonic
    if any(h not in cos_nonzero or h not in sin_nonzero for h in (harmonic, third)):
        return None

    carrier_a = _pscale(cos_nonzero[third], 2)
    carrier_b = _pscale(sin_nonzero[third], 2)
    if carrier_a == [0] or carrier_b == [0]:
        return None

    ratio_cos = _scalar_ratio(cos_nonzero[harmonic], carrier_a)
    ratio_sin = _scalar_ratio(sin_nonzero[harmonic], carrier_b)
    if ratio_cos is None or ratio_sin is None:
        return None
    lambda_from_cos = ratio_cos - Fraction(1, 2)
    lambda_from_sin = ratio_sin + Fraction(1, 2)
    if lambda_from_cos != lambda_from_sin:
        return None
    multiplier_lambda = lambda_from_cos

    expected_cos_h = _pscale(carrier_a, multiplier_lambda + Fraction(1, 2))
    expected_sin_h = _pscale(carrier_b, multiplier_lambda - Fraction(1, 2))
    expected_cos_3h = _pscale(carrier_a, Fraction(1, 2))
    expected_sin_3h = _pscale(carrier_b, Fraction(1, 2))
    if not all((
        _poly_equal(cos_nonzero[harmonic], expected_cos_h),
        _poly_equal(sin_nonzero[harmonic], expected_sin_h),
        _poly_equal(cos_nonzero[third], expected_cos_3h),
        _poly_equal(sin_nonzero[third], expected_sin_3h),
    )):
        return None

    factorization = {
        "status": "CERTIFIED" if abs(multiplier_lambda) > 1 else "BLOCKED",
        "relation": "EXACT_EVEN_HARMONIC_MULTIPLIER_FACTORIZATION",
        "harmonic": harmonic,
        "third_harmonic": third,
        "lambda": str(multiplier_lambda),
        "carrier_cos_polynomial": [str(value) for value in carrier_a],
        "carrier_sin_polynomial": [str(value) for value in carrier_b],
        "source_cos_polynomials": {
            str(k): [str(value) for value in poly] for k, poly in sorted(cos_nonzero.items())
        },
        "source_sin_polynomials": {
            str(k): [str(value) for value in poly] for k, poly in sorted(sin_nonzero.items())
        },
        "identity": {
            "C_h": "(lambda+1/2)*A",
            "S_h": "(lambda-1/2)*B",
            "C_3h": "A/2",
            "S_3h": "B/2",
        },
        "multiplier": "lambda + cos(2*alpha)",
        "multiplier_nonvanishing_bound": (
            "|lambda|-1=" + str(abs(multiplier_lambda) - 1)
        ),
        "multiplier_sign": (
            "POSITIVE" if multiplier_lambda > 1 else
            "NEGATIVE" if multiplier_lambda < -1 else
            "NOT_CERTIFIED"
        ),
        "product_to_sum_verified_exactly": True,
        "binary_float_used": False,
        "epsilon_used": False,
        "sampling_used": False,
    }
    if abs(multiplier_lambda) <= 1:
        factorization.update({
            "reason": "EVEN_MULTIPLIER_NOT_PROVED_GLOBALLY_NONVANISHING",
            "blocker": "PB-007-01",
        })
    return factorization


def _delegate_carrier(a_poly, b_poly, harmonic, offset, rate, source_parameter_id):
    cos_polys = {harmonic: _trim(a_poly)}
    sin_polys = {harmonic: _trim(b_poly)}

    first = v10._single_harmonic_dual_route(
        cos_polys, sin_polys, offset, rate, source_parameter_id
    )
    if first is None:
        return {
            "status": "BLOCKED",
            "reason": "MULTIHARMONIC_CARRIER_OUTSIDE_DUAL_PROJECTIVE_AUTHORITY",
            "blocker": "PB-007-01",
        }, "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
    if first.get("status") in {"CERTIFIED", "RESOURCE_REFUSAL", "SEMANTIC_BLOCKER"}:
        return first, "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"

    if first.get("reason") in {
        "OPPOSED_RATIO_MONOTONICITY_NOT_CERTIFIED",
        "OPPOSED_DUAL_PROJECTIVE_MONOTONICITY_NOT_CERTIFIED",
    }:
        second = v11._single_harmonic_phase_dominance_route(
            cos_polys, sin_polys, offset, rate, source_parameter_id
        )
        if second is not None:
            if second.get("status") in {"CERTIFIED", "RESOURCE_REFUSAL", "SEMANTIC_BLOCKER"}:
                return second, "PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO"
            first = second

    if first.get("reason") == "NO_ZERO_FREE_PROJECTIVE_COMPONENT_FOR_DUAL_RATIO_ROUTE":
        third = v12._single_harmonic_component_partition_route(
            cos_polys, sin_polys, offset, rate, source_parameter_id
        )
        if third is not None:
            return third, "PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC"

    return first, (
        "PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO"
        if first.get("reason") == "PHASE_DOMINANCE_NOT_CERTIFIED"
        else "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
    )


def _multiharmonic_factor_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    if q(rate) == 0:
        return None
    factorization = detect_nonvanishing_even_multiplier(cos_polys, sin_polys)
    if factorization is None:
        return None
    if factorization.get("status") != "CERTIFIED":
        return factorization

    harmonic = int(factorization["harmonic"])
    carrier_a = [q(value) for value in factorization["carrier_cos_polynomial"]]
    carrier_b = [q(value) for value in factorization["carrier_sin_polynomial"]]
    if EE.degree(EE.pgcd(carrier_a, carrier_b)) > 0:
        return {
            "status": "BLOCKED",
            "reason": "CARRIER_COMMON_FACTOR_REMAINS_OWNED_BY_PB00701_V8",
            "blocker": "PB-007-01",
            "factorization": factorization,
        }

    carrier, route_kind = _delegate_carrier(
        carrier_a, carrier_b, harmonic, q(offset), q(rate), source_parameter_id
    )
    if carrier.get("status") != "CERTIFIED":
        return {
            "status": carrier.get("status", "BLOCKED"),
            "reason": carrier.get("reason", "CARRIER_EXACT_EVENT_ROUTE_NOT_CERTIFIED"),
            "blocker": "PB-007-01",
            "factorization": factorization,
            "carrier_route_kind": route_kind,
            "carrier": carrier,
        }

    return {
        "status": "CERTIFIED",
        "relation": "EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC_EVENT_REDUCTION",
        "source_parameter_id": source_parameter_id,
        "factorization": factorization,
        "carrier_route_kind": route_kind,
        "carrier": carrier,
        "zero_set_equivalence": (
            "the exact multiplier lambda+cos(2*alpha) is globally nonzero because |lambda|>1; "
            "therefore the original multi-harmonic event is zero exactly where the carrier is zero"
        ),
        "multiplicity_preservation": (
            "multiplication by a smooth globally nonzero factor preserves every finite event-root multiplicity"
        ),
        "new_transcendental_zero_oracle_used": False,
        "numeric_trigonometry_used": False,
        "sampling_used": False,
    }


def _is_upgradeable_multiharmonic_span(span):
    route = span.get("route", {})
    return (
        span.get("route_kind") == "PB00701_GENERAL_COUPLED_THEOREM_BOUNDARY"
        and route.get("status") == "BLOCKED"
        and route.get("reason")
        == "NONCONSTANT_POLYNOMIAL_MODULATION_WITH_NONZERO_PHASE_REQUIRES_UNESTABLISHED_EXACT_ZERO_ROUTE"
    )


def analyze_multiharmonic_event(spec):
    baseline = v12.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict):
        return baseline
    if baseline.get("status") == "CERTIFIED":
        return baseline
    if baseline.get("relation") != "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER":
        return baseline

    rate = q(baseline["phase_turn_law"]["rate"])
    offset_global = q(baseline["phase_turn_law"]["offset"])
    unresolved = False
    upgraded = []
    for original_span in baseline["spans"]:
        span = dict(original_span)
        if _is_upgradeable_multiharmonic_span(span):
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
            replacement = _multiharmonic_factor_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC"
                span["route"] = replacement
                span["local_phase_turn_law"] = {
                    "offset": str(local_offset),
                    "rate": str(local_rate),
                    "local_parameter": "s=(u-lo)/(hi-lo)",
                    "shared_parameter": baseline["source_parameter_id"],
                }
        if span["route"].get("status") != "CERTIFIED":
            unresolved = True
        upgraded.append(span)

    statuses = [span["route"].get("status") for span in upgraded]
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
        "FINITE_EXACT_PIECEWISE_NONVANISHING_MULTIHARMONIC_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v13_nonvanishing_multiharmonic_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict) and spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
        return analyze_multiharmonic_event(spec)
    return v12.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V13_MULTIHARMONIC_MULTIPLIER_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
