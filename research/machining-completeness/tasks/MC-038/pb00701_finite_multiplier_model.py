#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_multiterm_multiplier_model as v14  # noqa: E402

v13 = v14.v13
v12 = v14.v12
v11 = v14.v11
v10 = v14.v10
v9 = v14.v9
v8 = v14.v8
v7 = v14.v7
EE = v14.EE
q = v14.q


class FiniteMultiplierRefusal(RuntimeError):
    """Bounded resource refusal. Never a truth value."""


def _trim(poly):
    return v14._trim(poly)


def _pscale(poly, scalar):
    return v14._pscale(poly, scalar)


def _poly_equal(left, right):
    return _trim(left) == _trim(right)


def _scalar_ratio(numerator, denominator):
    numerator = _trim(numerator)
    denominator = _trim(denominator)
    if numerator == [0]:
        return Fraction(0)
    return v14._scalar_ratio(numerator, denominator)


def detect_finite_strict_dominance_multiplier(cos_polys, sin_polys):
    """Detect a source-derived finite normalized even-cosine multiplier.

    The admitted family is

      (lambda_0 + sum_{k=1}^m lambda_k*cos(2*k*alpha))
        * (A*cos(alpha) + B*sin(alpha)),

    for finite m >= 3.  The highest coefficient is normalized to lambda_m=1
    by absorbing the original nonzero scale into A and B.  This removes only
    product scale ambiguity; every coefficient is reconstructed from the
    unfactored source harmonic maps and then checked exactly.
    """
    cos_nonzero = {
        int(h): _trim(poly) for h, poly in cos_polys.items() if _trim(poly) != [0]
    }
    sin_nonzero = {
        int(h): _trim(poly) for h, poly in sin_polys.items() if _trim(poly) != [0]
    }
    harmonics = sorted(set(cos_nonzero) | set(sin_nonzero))
    if not harmonics:
        return None
    harmonic = harmonics[0]
    if harmonic <= 0:
        return None
    if any(h <= 0 or h % harmonic != 0 or (h // harmonic) % 2 != 1 for h in harmonics):
        return None
    top_harmonic = harmonics[-1]
    top_ratio = top_harmonic // harmonic
    multiplier_degree = (top_ratio - 1) // 2
    if top_ratio != 2 * multiplier_degree + 1 or multiplier_degree < 3:
        return None

    if top_harmonic not in cos_nonzero or top_harmonic not in sin_nonzero:
        return None
    carrier_a = _pscale(cos_nonzero[top_harmonic], 2)
    carrier_b = _pscale(sin_nonzero[top_harmonic], 2)
    if carrier_a == [0] or carrier_b == [0]:
        return None

    ratios = []
    for r in range(multiplier_degree + 1):
        h = (2 * r + 1) * harmonic
        c_poly = cos_nonzero.get(h, [0])
        s_poly = sin_nonzero.get(h, [0])
        c_ratio = _scalar_ratio(c_poly, carrier_a)
        s_ratio = _scalar_ratio(s_poly, carrier_b)
        if c_ratio is None or s_ratio is None:
            return None
        ratios.append((c_ratio, s_ratio))

    # The normalized top harmonic must be exactly A/2 and B/2.
    if ratios[-1] != (Fraction(1, 2), Fraction(1, 2)):
        return None

    candidates = {k: [] for k in range(multiplier_degree + 1)}
    c0, s0 = ratios[0]
    candidates[0].append((c0 + s0) / 2)
    candidates[1].append(c0 - s0)
    for r in range(1, multiplier_degree):
        c_r, s_r = ratios[r]
        candidates[r].append(c_r + s_r)
        candidates[r + 1].append(c_r - s_r)
    candidates[multiplier_degree].append(Fraction(1))

    lambdas = []
    for k in range(multiplier_degree + 1):
        values = candidates[k]
        if not values or any(value != values[0] for value in values[1:]):
            return None
        lambdas.append(values[0])
    if lambdas[-1] != 1:
        return None

    expected_cos = {}
    expected_sin = {}
    for r in range(multiplier_degree + 1):
        h = (2 * r + 1) * harmonic
        if r == 0:
            c_scalar = lambdas[0] + lambdas[1] / 2
            s_scalar = lambdas[0] - lambdas[1] / 2
        elif r < multiplier_degree:
            c_scalar = (lambdas[r] + lambdas[r + 1]) / 2
            s_scalar = (lambdas[r] - lambdas[r + 1]) / 2
        else:
            c_scalar = s_scalar = Fraction(1, 2)
        expected_cos[h] = _pscale(carrier_a, c_scalar)
        expected_sin[h] = _pscale(carrier_b, s_scalar)
        if not _poly_equal(cos_nonzero.get(h, [0]), expected_cos[h]):
            return None
        if not _poly_equal(sin_nonzero.get(h, [0]), expected_sin[h]):
            return None

    tail_sum = sum((abs(value) for value in lambdas[1:]), Fraction(0))
    margin = abs(lambdas[0]) - tail_sum
    certified = margin > 0
    source_cos = {
        str(k): [str(value) for value in poly] for k, poly in sorted(cos_nonzero.items())
    }
    source_sin = {
        str(k): [str(value) for value in poly] for k, poly in sorted(sin_nonzero.items())
    }
    certificate = {
        "status": "CERTIFIED" if certified else "BLOCKED",
        "relation": "EXACT_FINITE_STRICT_DOMINANCE_EVEN_COSINE_MULTIPLIER_FACTORIZATION",
        "harmonic": harmonic,
        "top_harmonic": top_harmonic,
        "multiplier_degree": multiplier_degree,
        "lambda_vector": [str(value) for value in lambdas],
        "normalized_highest_coefficient": "1",
        "normalization": (
            "the original nonzero highest multiplier coefficient is absorbed into the carrier; "
            "the normalized carrier is reconstructed as A=2*C_top and B=2*S_top"
        ),
        "carrier_cos_polynomial": [str(value) for value in carrier_a],
        "carrier_sin_polynomial": [str(value) for value in carrier_b],
        "source_cos_polynomials": source_cos,
        "source_sin_polynomials": source_sin,
        "source_coefficient_identities_verified_exactly": True,
        "inversion": (
            "lambda_0=(c_0+s_0)/2; lambda_1=c_0-s_0; "
            "for 1<=r<m, lambda_r=c_r+s_r and lambda_{r+1}=c_r-s_r; "
            "all overlapping inferences agree exactly"
        ),
        "multiplier": "lambda_0 + sum_{k=1}^m lambda_k*cos(2*k*alpha)",
        "strict_dominance_condition": "|lambda_0|>sum_{k>=1}|lambda_k|",
        "strict_dominance_tail_sum": str(tail_sum),
        "strict_dominance_margin": str(margin),
        "multiplier_sign": (
            "POSITIVE" if certified and lambdas[0] > 0 else
            "NEGATIVE" if certified and lambdas[0] < 0 else
            "NOT_CERTIFIED"
        ),
        "caller_factorization_trusted": False,
        "binary_float_used": False,
        "epsilon_used": False,
        "sampling_used": False,
        "numeric_trigonometry_used": False,
    }
    if not certified:
        certificate.update({
            "reason": "FINITE_MULTIPLIER_STRICT_DOMINANCE_NOT_CERTIFIED",
            "blocker": "PB-007-01",
        })
    return certificate


def _delegate_carrier(a_poly, b_poly, harmonic, offset, rate, source_parameter_id):
    return v14._delegate_carrier(a_poly, b_poly, harmonic, offset, rate, source_parameter_id)


def _finite_multiplier_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    if q(rate) == 0:
        return None
    factorization = detect_finite_strict_dominance_multiplier(cos_polys, sin_polys)
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
        "relation": "EXACT_FINITE_STRICT_DOMINANCE_MULTIHARMONIC_EVENT_REDUCTION",
        "source_parameter_id": source_parameter_id,
        "factorization": factorization,
        "carrier_route_kind": route_kind,
        "carrier": carrier,
        "zero_set_equivalence": (
            "the exact finite even-cosine multiplier is globally nonzero by strict rational dominance; "
            "therefore the original odd-harmonic event is zero exactly where the carrier is zero"
        ),
        "multiplicity_preservation": (
            "multiplication by a smooth globally nonzero factor preserves every finite event-root multiplicity"
        ),
        "new_transcendental_zero_oracle_used": False,
        "numeric_trigonometry_used": False,
        "sampling_used": False,
    }


def _is_upgradeable_finite_span(span):
    return v14._is_upgradeable_multiterm_span(span)


def analyze_finite_multiplier_event(spec):
    baseline = v14.classify_required_analytic_event(spec)
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
        if _is_upgradeable_finite_span(span):
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
            replacement = _finite_multiplier_route(
                cos_polys, sin_polys, local_offset, local_rate, baseline["source_parameter_id"]
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER"
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
        "FINITE_EXACT_PIECEWISE_FINITE_STRICT_DOMINANCE_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v15_finite_strict_dominance_multiplier_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict) and spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
        return analyze_finite_multiplier_event(spec)
    return v14.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V15_FINITE_MULTIPLIER_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
