#!/usr/bin/env python3
"""A2-JOIN-001: source-bound finite-jet regularity at a genuine C0 spline knot.

Research-only. This wraps the exact A2 source adapter and local germ verifier;
it does not claim global physical root isolation or historical source admission.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "a2_cyclotomic_for_join", Path(__file__).with_name("cyclotomic_moments.py"))
a2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a2)

SCHEMA = "radicadsac/a2-analytic-join-research/1"


def _subtract_polynomial(left, right):
    """Exact rational coefficient vector of right minus left."""
    return [((right[i] if i < len(right) else 0) -
             (left[i] if i < len(left) else 0))
            for i in range(max(len(left), len(right)))]


def analytic_join(degree, knots, controls, offset, rate):
    """Decide equality of analytic continuations, or first derivative mismatch.

    Only actual degree-1..3, two-span clamped rational-control C0 B-splines
    admitted by A2. Both sides use the same rational affine phase. Construct
    the *analytic difference* across the true knot, not a source restricted
    to either half-interval. A2's local annihilator proves a finite decision.
    """
    left, right, knot, source_sha = a2.clamped_two_span_bezier(
        degree, knots, controls, offset, rate)
    a2.require(left["offset"] == right["offset"] and
               left["rate"] == right["rate"],
               "JOIN_PHASE_MISMATCH")
    terms = {}
    for harmonic in sorted(set(left["terms"]) | set(right["terms"])):
        lp, lq = left["terms"].get(harmonic, ((0,), (0,)))
        rp, rq = right["terms"].get(harmonic, ((0,), (0,)))
        terms[harmonic] = (_subtract_polynomial(lp, rp),
                           _subtract_polynomial(lq, rq))
    difference = a2.source(left["left"], right["right"],
                           left["offset"], left["rate"], terms)
    germ = a2.point_germ(difference, knot)
    a2.require(germ["status"] != "EXACT_POINT_NONZERO",
               "JOIN_NOT_C0")
    if germ["status"] == "IDENTITY_ZERO_ON_ANALYTIC_SPAN":
        status = "ANALYTICALLY_REMOVABLE_KNOT"
        mismatch_order = None
        continuous_derivatives_through = None
    else:
        a2.require(germ["status"] == "EXACT_POINT_ZERO" and germ["order"] > 0,
                   "JOIN_GERM_UNSUPPORTED")
        status = "FINITE_DERIVATIVE_MISMATCH"
        mismatch_order = germ["order"]
        continuous_derivatives_through = mismatch_order - 1
    return {
        "schema": SCHEMA,
        "status": status,
        "structural_knot": "TRUE_CLAMPED_C0_BSPLINE_KNOT",
        "spline_sha256": source_sha,
        "knot": str(knot),
        "difference_source_sha256": a2.digest(a2.source_dict(difference)),
        "difference_germ": germ,
        "first_mismatched_derivative": mismatch_order,
        "continuous_derivatives_through": continuous_derivatives_through,
        "all_derivatives_match": mismatch_order is None,
        "complete_zero_set_certified": False,
        "original_source_certified": False,
        "mc_b_established": False,
        "production_authorized": False,
    }


def verify_join(degree, knots, controls, offset, rate, claimed):
    """Reject stale, altered or forged receipts by full source replay."""
    a2.require(type(claimed) is dict and claimed == analytic_join(
        degree, knots, controls, offset, rate), "FORGED_OR_STALE_JOIN_RECEIPT")
    return True
