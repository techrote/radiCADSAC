#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_phase_sector_partition_model as model  # noqa: E402
import pb00701_pointwise_component_cone_model as v26  # noqa: E402
import test_pb00701_pointwise_component_cone_adversarial as v26test  # noqa: E402
import test_pb00701_l1_sign_orthant_envelope_adversarial as v21test  # noqa: E402


C_CROSSING = [
    Fraction(-79, 40),
    Fraction(-3, 4),
    Fraction(13, 8),
    Fraction(-3, 2),
    Fraction(1, 2),
]


def _spec(cos_polys, sin_polys=None, *, offset="1/12", rate="1/6", **extra):
    return v21test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(*, offset="1/12", rate="1/6"):
    # C1 = -(2 + (1/10)*(1-5*(s-1/2)^2*(s-1)^2)).
    # Whole-span C-dominant v26 fails at s=0 because |C1|/2 < S1.
    # On the left child [0,1/2], v24's aligned mixed-quadrature anchor dominates.
    # On the right child [1/2,1], v25's C-dominant cone has a strict margin.
    # The single exact phase-sector cut is h=1 phase turn 1/6 at s=1/2.
    return _spec(
        {1: C_CROSSING, 2: [Fraction(1, 10000)]},
        {1: [1]},
        offset=offset,
        rate=rate,
    )


def _v27_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"]
        for span in result["spans"]
        if span.get("route_kind") == "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION"
    ]
    assert routes, result
    assert routes[0]["status"] == "CERTIFIED", routes[0]
    return routes[0]


def _rejected(spec):
    try:
        return model.classify_required_analytic_event(spec).get("status") != "CERTIFIED"
    except (AssertionError, ValueError, KeyError, TypeError, ZeroDivisionError):
        return True


def _synthetic_route(left, right, *, open_roots=0, left_mult=None, right_mult=None):
    multiplicity = {}
    if left_mult is not None:
        multiplicity["left"] = left_mult
    if right_mult is not None:
        multiplicity["right"] = right_mult
    return {
        "status": "CERTIFIED",
        "left_event": {"status": "CERTIFIED", "relation": left},
        "right_event": {"status": "CERTIFIED", "relation": right},
        "distinct_roots_open": open_roots,
        "total_distinct_roots_closed": (
            open_roots + int(left == "ZERO") + int(right == "ZERO")
        ),
        "all_roots_simple": True,
        "endpoint_root_multiplicity": multiplicity,
    }


def run():
    source = _fixture()

    old = v26.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old

    result = model.classify_required_analytic_event(source)
    route = _v27_route(result)
    assert route["relation"] == model.V27_ROUTE
    assert route["partition_certificate"]["cuts"] == ["1/2"]
    assert route["child_count"] == 2
    assert route["children"][0]["local_interval_serialized"] == ["0", "1/2"]
    assert route["children"][1]["local_interval_serialized"] == ["1/2", "1"]
    assert route["children"][0]["route_kind"] == "PB00701_V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR"
    assert route["children"][1]["route_kind"] in {
        "PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR",
        "PB00701_V26_EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANTS",
    }
    assert route["left_event"]["relation"] == "NEGATIVE"
    assert route["right_event"]["relation"] == "POSITIVE"
    assert route["distinct_roots_open"] == 1
    assert route["total_distinct_roots_closed"] == 1
    assert route["all_roots_simple"] is True
    assert route["internal_cut_roots"] == []
    assert route["caller_partition_trusted"] is False
    assert route["sampling_used"] is False
    assert route["arbitrary_subdivision_cap_used"] is False

    # Exact polynomial substitution is source preserving.
    p = [Fraction(3), Fraction(-2), Fraction(5)]
    left = Fraction(1, 5)
    right = Fraction(4, 5)
    child = model._reparameterize_polynomial(p, left, right)
    for u in (Fraction(0), Fraction(1, 7), Fraction(1), Fraction(5, 9)):
        parent_s = left + (right - left) * u
        original = sum(value * parent_s**i for i, value in enumerate(p))
        lowered = sum(value * u**i for i, value in enumerate(child))
        assert original == lowered

    # Positive and negative affine phase laws derive the same exact cut in source order.
    positive = model._exact_sector_partition(Fraction(1, 12), Fraction(1, 6), [1])
    negative = model._exact_sector_partition(Fraction(1, 4), Fraction(-1, 6), [1])
    assert positive["status"] == "CERTIFIED"
    assert negative["status"] == "CERTIFIED"
    assert positive["cuts"] == ["1/2"]
    assert negative["cuts"] == ["1/2"]

    # External endpoint sector equality never creates a zero-width child.
    endpoint_only = model._exact_sector_partition(Fraction(1, 6), Fraction(1, 12), [1])
    assert "0" not in endpoint_only.get("cuts", [])
    assert "1" not in endpoint_only.get("cuts", [])

    eps = Fraction(1, 1000000)
    before = model._exact_sector_partition(
        Fraction(1, 12), Fraction(1, 12) - eps, [1]
    )
    exact = model._exact_sector_partition(Fraction(1, 12), Fraction(1, 12), [1])
    after = model._exact_sector_partition(
        Fraction(1, 12), Fraction(1, 12) + eps, [1]
    )
    assert before["status"] == "BLOCKED"
    assert exact["status"] == "BLOCKED"
    assert after["status"] == "CERTIFIED"
    assert len(after["cuts"]) == 1

    # Coincident cuts from independent harmonic/boundary families deduplicate exactly.
    coincident = model._exact_sector_partition(Fraction(0), Fraction(1, 3), [1, 2])
    half = next(
        item for item in coincident["cut_provenance"]
        if item["source_parameter_cut"] == "1/2"
    )
    assert len(half["crossings"]) >= 2
    assert len(coincident["cuts"]) == len(set(coincident["cuts"]))

    # An exact event on an internal certificate cut is counted once, not twice.
    synthetic_children = [
        {
            "local_interval": [Fraction(0), Fraction(1, 2)],
            "route": _synthetic_route("NEGATIVE", "ZERO", right_mult=1),
        },
        {
            "local_interval": [Fraction(1, 2), Fraction(1)],
            "route": _synthetic_route("ZERO", "POSITIVE", left_mult=1),
        },
    ]
    composed = model._compose_child_summaries(synthetic_children)
    assert composed["status"] == "CERTIFIED"
    assert composed["distinct_roots_open"] == 1
    assert composed["total_distinct_roots_closed"] == 1
    assert composed["internal_cut_root_count"] == 1
    assert composed["internal_cut_roots"][0]["multiplicity"] == 1

    # Relation disagreement and missing exact cut multiplicity fail closed.
    mismatch_children = copy.deepcopy(synthetic_children)
    mismatch_children[1]["route"]["left_event"]["relation"] = "POSITIVE"
    mismatch = model._compose_child_summaries(mismatch_children)
    assert mismatch["status"] == "BLOCKED"
    assert mismatch["reason"] == "PHASE_SECTOR_INTERNAL_CUT_ENDPOINT_RELATION_MISMATCH"

    missing_mult = copy.deepcopy(synthetic_children)
    missing_mult[1]["route"]["endpoint_root_multiplicity"] = {}
    missing = model._compose_child_summaries(missing_mult)
    assert missing["status"] == "BLOCKED"
    assert missing["reason"] == "PHASE_SECTOR_INTERNAL_CUT_MULTIPLICITY_NOT_EXACTLY_COMPOSABLE"

    # One blocked child blocks the parent; sibling success cannot launder it.
    original_classifier = model.v26.classify_required_analytic_event
    try:
        model.v26.classify_required_analytic_event = lambda _spec: {
            "status": "BLOCKED",
            "relation": "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER",
        }
        blocked = model._phase_sector_partition_route(
            {1: C_CROSSING, 2: [Fraction(1, 10000)]},
            {1: [1]},
            Fraction(1, 12),
            Fraction(1, 6),
            "source-time-t",
            (Fraction(0), Fraction(1)),
        )
        assert blocked["status"] == "BLOCKED"
        assert blocked["reason"] == "PHASE_SECTOR_PARTITION_CHILD_REMAINS_UNCERTIFIED"

        model.v26.classify_required_analytic_event = lambda _spec: {
            "status": "RESOURCE_REFUSAL",
            "reason": "adversarial exact child refusal",
            "is_truth_value": False,
        }
        refused = model._phase_sector_partition_route(
            {1: C_CROSSING, 2: [Fraction(1, 10000)]},
            {1: [1]},
            Fraction(1, 12),
            Fraction(1, 6),
            "source-time-t",
            (Fraction(0), Fraction(1)),
        )
        assert refused["status"] == "RESOURCE_REFUSAL"
        assert refused["is_truth_value"] is False
    finally:
        model.v26.classify_required_analytic_event = original_classifier

    # Caller partition/root metadata is stripped and cannot alter the source-derived result.
    forged = copy.deepcopy(source)
    forged.update({
        "phase_sector_partition": {"status": "CERTIFIED", "cuts": ["1/999"]},
        "certificate_cuts": ["1/999"],
        "partition_children": [{"status": "CERTIFIED"}],
        "child_certificates": [{"status": "CERTIFIED"}],
        "composed_root_count": 99,
        "internal_cut_roots": [{"cut": "1/999", "multiplicity": 99}],
    })
    forged_route = _v27_route(model.classify_required_analytic_event(forged))
    assert forged_route["partition_certificate"]["cuts"] == ["1/2"]
    assert forged_route["distinct_roots_open"] == route["distinct_roots_open"]
    assert forged_route["caller_partition_trusted"] is False

    floating = copy.deepcopy(source)
    floating["cos_splines"]["1"]["controls"][0] = -1.975
    assert _rejected(floating)

    mismatch_source = copy.deepcopy(source)
    mismatch_source["parameter_projection"] = "different-source-coordinate"
    assert model.classify_required_analytic_event(mismatch_source)["status"] == "SEMANTIC_BLOCKER"

    # Historical v26 ownership is preserved; v27 never relabels an already-certified span.
    prior = model.classify_required_analytic_event(v26test._fixture())
    assert prior["status"] == "CERTIFIED"
    assert not prior.get("v27_phase_sector_partition_extension", False)
    assert any(
        span.get("route_kind")
        == "PB00701_V26_EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANTS"
        for span in prior.get("spans", [])
    )

    assert model.resource_refusal()["is_truth_value"] is False
    print("PB-007-01 v27 exact rational phase-sector partition adversarial controls: PASS")


if __name__ == "__main__":
    run()
