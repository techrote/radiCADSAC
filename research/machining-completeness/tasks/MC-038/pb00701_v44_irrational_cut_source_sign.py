#!/usr/bin/env python3
"""Source-rational Lipschitz enclosure for the frozen V44 irrational proof cut.

Research only. Exact rational point enclosures and a rational global |F'|
bound transfer a *strict nonzero* physical sign to the exact real algebraic
cut without evaluating sin/cos at the irrational point. Exhaustion and exact
zeros remain nontruth; this is not a general algebraic child event solver.
"""
from __future__ import annotations

from fractions import Fraction as Q

import pb00701_v44_v45_monotone_child_bridge as bridge

derivative = bridge.derivative
trig = derivative.trig
v45 = bridge.v45

SCHEMA = "radicadsac-pb00701-v44-irrational-cut-source-sign/1.0"
SUCCESS = "EXACT_FROZEN_V44_IRRATIONAL_CUT_NONZERO_SOURCE_SIGN_RESEARCH"
BRIDGE_BLOB = "850fc287a92bc57420c51848f21e51b7571a07a9"
MAX_REFINEMENTS = 32
MAX_REPORT_BYTES = 65536


class Refusal(ValueError):
    pass


class ResourceRefusal(RuntimeError):
    pass


def require(ok, reason):
    if not ok:
        raise Refusal(reason)


def pins():
    require(bridge.previous.git_blob(
        bridge.previous.TASK / "pb00701_v44_v45_monotone_child_bridge.py"
    ) == BRIDGE_BLOB, "PINNED_V45_MONOTONE_BRIDGE_SOURCE_DRIFT")
    bridge.pins()


def independent_lipschitz_bound(span):
    """Rebuild M1 from the original rational source, not a report assertion.

    F' = sum_h ((P'_h+k_h Q_h)cos(theta_h)
                 +(Q'_h-k_h P_h)sin(theta_h)).
    With |2*pi|<44/7, |sin|<=1, |cos|<=1 and |t|<=radius:
    |F'| <= sum_h (||P'||_1+||Q'||_1
                    +(44/7)|h*r| (||P||_1+||Q||_1)).
    """
    require(span.left <= Q(0) and span.right >= Q(1)
            and span.left < span.right, "SOURCE_INTERVAL_NOT_COVERED")
    radius = max(Q(1), abs(span.left), abs(span.right))
    out = Q(0)
    for h, (p, s) in span.terms.items():
        require(type(h) is int and 0 <= h <= 8,
                "INVALID_ORIGINAL_SOURCE_HARMONIC")
        k = Q(44, 7) * abs(h * span.rate)
        out += (
            trig.norm_bound(trig.derivative(p), radius)
            + trig.norm_bound(trig.derivative(s), radius)
            + k * (trig.norm_bound(p, radius)
                   + trig.norm_bound(s, radius))
        )
    require(out >= 0 and type(span.m1) is Q and span.m1 == out,
            "ORIGINAL_SOURCE_DERIVATIVE_LIPSCHITZ_DRIFT")
    return out


def _polynomial_sign_at(p, x):
    value = v45.engine.peval(p, x)
    require(type(value) is Q, "ALGEBRAIC_POLYNOMIAL_NOT_EXACT_RATIONAL")
    return (value > 0) - (value < 0)


def certify_strict_sign(span, field, *, max_refinements=MAX_REFINEMENTS):
    """Bounded semidecision of F(alpha)!=0, with exact witness trace.

    Only field's certified real embedding supplies alpha. Every refinement
    retains precisely that one real polynomial root by Sturm and strict
    endpoint signs. A rational-source point enclosure plus global M1
    yields the full irrational-point enclosure by the mean-value theorem.
    """
    require(type(max_refinements) is int
            and 0 <= max_refinements <= MAX_REFINEMENTS,
            "INVALID_ALGEBRAIC_REFINEMENT_BUDGET")
    require(type(field) is v45.RealField,
            "UNVALIDATED_REAL_ALGEBRAIC_EMBEDDING")
    require(span.left == Q(0) and span.right == Q(1),
            "SOURCE_COORDINATE_DOMAIN_NOT_ORIGINAL_UNIT_INTERVAL")
    m1 = independent_lipschitz_bound(span)
    lo, hi = field.interval
    require(Q(0) < lo < hi < Q(1),
            "IRRATIONAL_CUT_OUTSIDE_ORIGINAL_SOURCE")
    polynomial = field.minimal
    require(len(polynomial) >= 3 and
            v45.engine.distinct_roots_open(polynomial, lo, hi) == 1,
            "ALGEBRAIC_CUT_NOT_UNIQUE_STURM_ISOLATION")
    sign_lo, sign_hi = (
        _polynomial_sign_at(polynomial, lo),
        _polynomial_sign_at(polynomial, hi)
    )
    require(sign_lo * sign_hi == -1,
            "ALGEBRAIC_ROOT_INTERVAL_LACKS_STRICT_SIGN_BRACKET")
    initial = (lo, hi)
    trace = []
    for step in range(max_refinements + 1):
        mid, radius = (lo + hi) / 2, (hi - lo) / 2
        raw = span.evaluate(mid)
        require(type(raw) is tuple and len(raw) == 2
                and all(type(x) is Q for x in raw)
                and raw[0] <= raw[1],
                "ORIGINAL_RATIONAL_SOURCE_TRIG_ENCLOSURE_INVALID")
        # Round exact source enclosures *outward* onto the previously
        # qualified dyadic grid. Large raw Fraction denominators must
        # not inflate the published report or bypass its resource cap.
        value = (
            derivative._outward_dyadic(raw[0], upward=False),
            derivative._outward_dyadic(raw[1], upward=True),
        )
        require(value[0] <= raw[0] <= raw[1] <= value[1],
                "RATIONAL_SOURCE_TRIG_ENCLOSURE_ROUNDED_INWARD")
        enclosed = (value[0] - m1 * radius,
                    value[1] + m1 * radius)
        strict = 1 if enclosed[0] > 0 else (
            -1 if enclosed[1] < 0 else 0
        )
        trace.append({
            "refinements_used": step,
            "algebraic_cut_sturm_isolation": [str(lo), str(hi)],
            "exact_rational_source_midpoint": str(mid),
            "rational_source_trig_enclosure": [str(x) for x in value],
            "global_derivative_lipschitz_radius": str(m1 * radius),
            "transported_irrational_cut_value_enclosure":
                [str(x) for x in enclosed],
            "strict_nonzero_sign": strict,
        })
        if strict:
            return {
                "strict_nonzero_sign": strict,
                "source_lipschitz_derivative_upper_bound": str(m1),
                "outward_dyadic_grid_bits": derivative.DYADIC_ENCLOSURE_BITS,
                "initial_exact_algebraic_isolation":
                    [str(x) for x in initial],
                "certificate": trace[-1],
                "refinement_history": trace,
                "strict_sign_certification_method":
                    "EXACT_STURM_RATIONAL_MIDPOINT_OUTWARD_TRIG_LIPSCHITZ",
                "irrational_trigonometric_evaluation_performed": False,
            }
        if step == max_refinements:
            break
        sign_mid = _polynomial_sign_at(polynomial, mid)
        require(sign_mid != 0, "IRRATIONAL_FIELD_ROOT_AT_RATIONAL_MIDPOINT")
        if sign_lo * sign_mid == -1:
            hi, sign_hi = mid, sign_mid
        else:
            require(sign_mid * sign_hi == -1,
                    "ALGEBRAIC_BISECTION_BRACKET_LOST")
            lo, sign_lo = mid, sign_mid
        require(v45.engine.distinct_roots_open(polynomial, lo, hi) == 1,
                "ALGEBRAIC_BISECTION_STURM_ROOT_IDENTITY_LOST")
    raise ResourceRefusal("IRRATIONAL_CUT_NONZERO_SIGN_UNDECIDED_WITHIN_BUDGET")


def prove(*, max_refinements=MAX_REFINEMENTS, supplied_atlas=None):
    pins()
    view, span, _, _ = derivative._source_snapshot(supplied_atlas)
    # V45 proof binds the exact historical field to the original V41 cut,
    # original rational source/phase, complete physical-root atlas and
    # original source derivative. Its inherited endpoint sign is NOT used
    # to calculate the new enclosure below.
    parent = bridge.prove(supplied_atlas=view)
    require(parent["status"] == bridge.SUCCESS
            and parent["historical_v54_admitted"] is False,
            "PINNED_V45_SOURCE_OR_FIELD_BINDING_NOT_PROVED")
    field = bridge._field(parent["v45_field"])
    source_proof = certify_strict_sign(
        span, field, max_refinements=max_refinements
    )
    sign = ("POSITIVE" if source_proof["strict_nonzero_sign"] == 1
            else "NEGATIVE")
    require(sign == parent["source_algebraic_boundary_nonzero_sign"],
            "INDEPENDENT_IRRATIONAL_CUT_SIGN_CONTRADICTS_V46_ATLAS")
    pins()
    return {
        "schema": SCHEMA,
        "status": SUCCESS,
        "evidence_class": "DETERMINISTIC_MODEL",
        "frozen_case_id": bridge.previous.CASE_ID,
        "source_sha256": bridge.atlas.SOURCE_SHA256,
        "original_source_interval": ["0", "1"],
        "original_phase_turn_law": [
            str(span.offset), str(span.rate)
        ],
        "source_algebraic_proof_boundary_id":
            parent["source_algebraic_proof_boundary_id"],
        "exact_v45_field": field.record(),
        "independently_certified_irrational_cut_sign": sign,
        "agrees_with_preserved_v46_source_atlas": True,
        "source_proof": source_proof,
        "physical_cut_is_nonzero": True,
        "proof_cut_is_physical_event": False,
        "historical_v45_irrational_phase_endpoint_authority": "DEFERRED",
        "general_irrational_phase_endpoint_zero_decider_constructed": False,
        "general_v41_v47_child_event_route_certified": False,
        "historical_v54_disposition": "BLOCKED",
        "historical_v54_admitted": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_geometry_or_step_qualified": False,
        "production_authorized": False,
    }


def nontruth(reason, status="BLOCKED"):
    return {
        "schema": SCHEMA, "status": status, "reason": str(reason),
        "is_truth_value": False, "historical_v54_admitted": False,
        "pb00701_certified": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }


def attempt(*, max_refinements=MAX_REFINEMENTS, supplied_atlas=None):
    try:
        return prove(max_refinements=max_refinements,
                     supplied_atlas=supplied_atlas)
    except (ResourceRefusal, bridge.ResourceRefusal,
            derivative.ResourceRefusal, bridge.predecessor.ResourceRefusal,
            bridge.previous.ResourceRefusal, MemoryError, RecursionError,
            OverflowError) as exc:
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (Refusal, bridge.Refusal, derivative.Refusal,
            bridge.atlas.Refusal, bridge.previous.ResearchRefusal,
            ValueError, TypeError, KeyError, IndexError, AssertionError,
            AttributeError, ZeroDivisionError) as exc:
        return nontruth(str(exc))


def validate_report(submitted, *, max_refinements=MAX_REFINEMENTS,
                    supplied_atlas=None):
    try:
        bridge.predecessor._bound_untrusted_report_structure(submitted)
        claimed = bridge.previous.canonical(submitted)
        if len(claimed) > MAX_REPORT_BYTES:
            raise ResourceRefusal("SUBMITTED_ALGEBRAIC_SOURCE_SIGN_REPORT_SIZE_LIMIT")
        checked = attempt(max_refinements=max_refinements,
                          supplied_atlas=supplied_atlas)
        require(checked.get("status") == SUCCESS,
                "FROZEN_IRRATIONAL_CUT_SOURCE_SIGN_NOT_PROVED")
        require(claimed == bridge.previous.canonical(checked),
                "FORGED_IRRATIONAL_CUT_SOURCE_SIGN_REPORT")
        return checked
    except (ResourceRefusal, bridge.predecessor.ResourceRefusal,
            MemoryError, RecursionError, OverflowError) as exc:
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (Refusal, bridge.previous.ResearchRefusal,
            ValueError, TypeError, KeyError) as exc:
        return nontruth(str(exc))
