#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_multiharmonic_multiplier_model as v13  # noqa: E402

v12 = v13.v12
v11 = v13.v11
v10 = v13.v10
v9 = v13.v9
v8 = v13.v8
v7 = v13.v7
EE = v13.EE
q = v13.q


class MultiTermMultiplierRefusal(RuntimeError):
    """Bounded resource refusal. Never a truth value."""


def _trim(poly):
    return v13._trim(poly)


def _pscale(poly, scalar):
    return v13._pscale(poly, scalar)


def _poly_equal(left, right):
    return _trim(left) == _trim(right)


def _scalar_ratio(numerator, denominator):
    return v13._scalar_ratio(numerator, denominator)


def detect_strict_dominance_multiterm_multiplier(cos_polys, sin_polys):
    """Detect the exact normalized {h,3h,5h} source factorization.

    The admitted family is

      (lambda + mu*cos(2*alpha) + cos(4*alpha))
        * (A*cos(alpha) + B*sin(alpha)),
      alpha = 2*pi*h*theta_turn.

    Product-to-sum requires exactly
      C_h  = (lambda + mu/2) A,
      S_h  = (lambda - mu/2) B,
      C_3h = ((mu + 1)/2) A,
      S_3h = ((mu - 1)/2) B,
      C_5h = A/2,
      S_5h = B/2.

    The coefficient of cos(4*alpha) is normalized to one, removing the
    irrelevant scale ambiguity between multiplier and carrier.
    """
    cos_nonzero = {
        int(h): _trim(poly) for h, poly in cos_polys.items() if _trim(poly) != [0]
    }
    sin_nonzero = {
        int(h): _trim(poly) for h, poly in sin_polys.items() if _trim(poly) != [0]
    }
    harmonics = set(cos_nonzero) | set(sin_nonzero)
    if len(harmonics) != 3:
        return None
    harmonic = min(harmonics)
    if harmonic <= 0 or harmonics != {harmonic, 3 * harmonic, 5 * harmonic}:
        return None
    third = 3 * harmonic
    fifth = 5 * harmonic
    if any(h not in cos_nonzero or h not in sin_nonzero for h in (harmonic, third, fifth)):
        return None

    carrier_a = _pscale(cos_nonzero[fifth], 2)
    carrier_b = _pscale(sin_nonzero[fifth], 2)
    if carrier_a == [0] or carrier_b == [0]:
        return None

    ratio_c3 = _scalar_ratio(cos_nonzero[third], carrier_a)
    ratio_s3 = _scalar_ratio(sin_nonzero[third], carrier_b)
    if ratio_c3 is None or ratio_s3 is None:
        return None
    mu_from_cos = 2 * ratio_c3 - 1
    mu_from_sin = 2 * ratio_s3 + 1
    if mu_from_cos != mu_from_sin:
        return None
    multiplier_mu = mu_from_cos

    ratio_ch = _scalar_ratio(cos_nonzero[harmonic], carrier_a)
    ratio_sh = _scalar_ratio(sin_nonzero[harmonic], carrier_b)
    if ratio_ch is None or ratio_sh is None:
        return None
    lambda_from_cos = ratio_ch - multiplier_mu / 2
    lambda_from_sin = ratio_sh + multiplier_mu / 2
    if lambda_from_cos != lambda_from_sin:
        return None
    multiplier_lambda = lambda_from_cos

    expected = {
        "C_h": _pscale(carrier_a, multiplier_lambda + multiplier_mu / 2),
        "S_h": _pscale(carrier_b, multiplier_lambda - multiplier_mu / 2),
        "C_3h": _pscale(carrier_a, (multiplier_mu + 1) / 2),
        "S_3h": _pscale(carrier_b, (multiplier_mu - 1) / 2),
        "C_5h": _pscale(carrier_a, Fraction(1, 2)),
        "S_5h": _pscale(carrier_b, Fraction(1, 2)),
    }
    actual = {
        "C_h": cos_nonzero[harmonic],
        "S_h": sin_nonzero[harmonic],
        "C_3h": cos_nonzero[third],
        "S_3h": sin_nonzero[third],
        "C_5h": cos_nonzero[fifth],
        "S_5h": sin_nonzero[fifth],
    }
    if any(not _poly_equal(actual[key], expected[key]) for key in expected):
        return None

    margin = abs(multiplier_lambda) - abs(multiplier_mu) - 1
    certified = margin > 0
    factorization = {
        "status": "CERTIFIED" if certified else "BLOCKED",
        "relation": "EXACT_STRICT_DOMINANCE_MULTITERM_EVEN_MULTIPLIER_FACTORIZATION",
        "harmonic": harmonic,
        "third_harmonic": third,
        "fifth_harmonic": fifth,
        "lambda": str(multiplier_lambda),
        "mu": str(multiplier_mu),
        "carrier_cos_polynomial": [str(value) for value in carrier_a],
        "carrier_sin_polynomial": [str(value) for value in carrier_b],
        "source_cos_polynomials": {
            str(k): [str(value) for value in poly] for k, poly in sorted(cos_nonzero.items())
        },
        "source_sin_polynomials": {
            str(k): [str(value) for value in poly] for k, poly in sorted(sin_nonzero.items())
        },
        "identity": {
            "C_h": "(lambda+mu/2)*A",
            "S_h": "(lambda-mu/2)*B",
            "C_3h": "((mu+1)/2)*A",
            "S_3h": "((mu-1)/2)*B",
            "C_5h": "A/2",
            "S_5h": "B/2",
        },
        "multiplier": "lambda + mu*cos(2*alpha) + cos(4*alpha)",
        "strict_dominance_condition": "|lambda|>|mu|+1",
        "strict_dominance_margin": str(margin),
        "multiplier_sign": (
            "POSITIVE" if certified and multiplier_lambda > 0 else
            "NEGATIVE" if certified and multiplier_lambda < 0 else
            "NOT_CERTIFIED"
        ),
        "product_to_sum_verified_exactly": True,
        "caller_factorization_trusted": False,
        "binary_float_used": False,
        "epsilon_used": False,
        "sampling_used": False,
        "numeric_trigonometry_used": False,
    }
    if not certified:
        factorization.update({
            "reason": "MULTITERM_MULTIPLIER_STRICT_DOMINANCE_NOT_CERTIFIED",
            "blocker": "PB-007-01",
        })
    return factorization


def _delegate_carrier(a_poly, b_poly, harmonic, offset, rate, source_parameter_id):
    return v13._delegate_carrier(
        a_poly, b_poly, harmonic, offset, rate, source_parameter_id
    )


def _multiterm_factor_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    if q(rate) == 0:
        return None
    factorization = detect_strict_dominance_multiterm_multiplier(cos_polys, sin_polys)
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
        "relation": "EXACT_STRICT_DOMINANCE_MULTITERM_MULTIHARMONIC_EVENT_REDUCTION",
        "source_parameter_id": source_parameter_id,
        "factorization": factorization,
        "carrier_route_kind": route_kind,
        "carrier": carrier,
        "zero_set_equivalence": (
            "the exact multiplier lambda+mu*cos(2*alpha)+cos(4*alpha) is globally nonzero "
            "because |lambda|>|mu|+1; therefore the original {h,3h,5h} event is zero "
            "exactly where the carrier is zero"
        ),
        "multiplicity_preservation": (
            "multiplication by a smooth globally nonzero factor preserves every finite event-root multiplicity"
        ),
        "new_transcendental_zero_oracle_used": False,
        "numeric_trigonometry_used": False,
        "sampling_used": False,
    }


def _is_upgradeable_multiterm_span(span):
    return v13._is_upgradeable_multiharmonic_span(span)


def analyze_multiterm_event(spec):
    baseline = v13.classify_required_analytic_event(spec)
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
        if _is_upgradeable_multiterm_span(span):
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
            replacement = _multiterm_factor_route(
                cos_polys,
                sin_polys,
                local_offset,
                local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER"
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
        "FINITE_EXACT_PIECEWISE_STRICT_DOMINANCE_MULTITERM_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v14_strict_dominance_multiterm_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict) and spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
        return analyze_multiterm_event(spec)
    return v13.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V14_MULTITERM_MULTIPLIER_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
