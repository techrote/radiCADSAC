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
import test_pb00701_multiharmonic_monotone_anchor_adversarial as v19test  # noqa: E402
import test_pb00701_pointwise_component_cone_adversarial as v26test  # noqa: E402


def _spec(cos_polys, sin_polys=None, *, offset="-1/6", rate="2/3", **extra):
    return v19test._spec(
        cos_polys,
        {} if sin_polys is None else sin_polys,
        offset=offset,
        rate=rate,
        **extra,
    )


def _fixture(*, reverse=False):
    # Whole-span historical authority is blocked: h=1's pure-S phase anchor crosses
    # the COS half-magnitude boundary at local source s=1/2, while global exact
    # amplitude dominance also fails.  Exact sector children before that transition
    # are decided by preserved phase-anchor authority; later children are decided by
    # preserved rational amplitude dominance.  h=2 is deliberately tiny but active,
    # forcing multiple finite certificate cuts and exercising cut deduplication.
    if not reverse:
        return _spec(
            {0: [5], 2: [Fraction(1, 100)]},
            {1: [6, -4]},
            offset="-1/6",
            rate="2/3",
        )
    return _spec(
        {0: [5], 2: [Fraction(1, 100)]},
        {1: [2, 4]},
        offset="1/2",
        rate="-2/3",
    )


def _v27_route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"] for span in result.get("spans", [])
        if span.get("route_kind") == "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION"
    ]
    assert routes, result
    assert routes[0]["status"] == "CERTIFIED", routes[0]
    return routes[0]


def run():
    source = _fixture()
    old = v26.classify_required_analytic_event(source)
    assert old["status"] == "BLOCKED", old
    assert any(span.get("route", {}).get("status") == "BLOCKED" for span in old.get("spans", []))

    result = model.classify_required_analytic_event(source)
    route = _v27_route(result)
    assert route["relation"] == model.V27_ROUTE
    assert route["child_count"] > 1
    assert route["all_children_reclassified_by_complete_v8_v26_classifier"] is True
    assert all(child["child_result"]["status"] == "CERTIFIED" for child in route["children"])
    assert all(child["summary"]["status"] == "CERTIFIED" for child in route["children"])
    assert route["sector_cut_certificate"]["relation"] == "FINITE_EXACT_RATIONAL_HALF_MAGNITUDE_SECTOR_CROSSINGS"
    assert "1/2" in route["sector_cut_certificate"]["cuts"]
    assert route["distinct_roots_open"] >= 1
    assert route["composition"]["internal_cut_root_counted_once"] is True
    assert route["sampling_used"] is False
    assert route["epsilon_used"] is False
    assert route["adaptive_refinement_used"] is False
    assert route["arbitrary_subdivision_cap_used"] is False

    # Exact negative-rate reversal has the same finite cut set in reverse traversal.
    reverse = _v27_route(model.classify_required_analytic_event(_fixture(reverse=True)))
    assert reverse["status"] == "CERTIFIED"
    assert reverse["phase_turn_law_local"]["rate"].startswith("-")
    assert reverse["sector_cut_certificate"]["cuts"] == route["sector_cut_certificate"]["cuts"]

    # Exact cuts on external source endpoints are excluded; no zero-width child exists.
    endpoints = model.exact_sector_cuts(Fraction(1, 6), Fraction(1, 6), [1])
    assert endpoints["status"] == "CERTIFIED"
    assert endpoints["cuts"] == []

    # Multiple harmonics/families produce several cuts, sorted exactly, while coincident
    # crossings are represented once with all exact causes retained.
    many = model.exact_sector_cuts(Fraction(0), Fraction(1), [1, 2])
    cuts = [Fraction(value) for value in many["cuts"]]
    assert len(cuts) > 4
    assert cuts == sorted(set(cuts))
    assert any(len(item["causes"]) > 1 for item in many["crossings"])

    # Exact polynomial reparameterization is source preserving at both child endpoints.
    poly = [Fraction(3, 7), Fraction(-5, 3), Fraction(11, 5), Fraction(2, 9)]
    left, right = Fraction(2, 11), Fraction(7, 13)
    child = model._reparameterize_polynomial(poly, left, right)
    eval_poly = lambda p, x: sum(value * x ** i for i, value in enumerate(p))
    assert eval_poly(child, Fraction(0)) == eval_poly(poly, left)
    assert eval_poly(child, Fraction(1)) == eval_poly(poly, right)

    # Internal certificate-cut root composition must deduplicate the two child endpoint
    # views and require exact matching multiplicity rather than inventing it.
    negative = {"status": "DECIDED", "relation": "NEGATIVE"}
    positive = {"status": "DECIDED", "relation": "POSITIVE"}
    zero = {"status": "DECIDED", "relation": "ZERO"}
    synthetic = [
        {
            "parent_local_interval": ["0", "1/2"],
            "summary": {
                "status": "CERTIFIED", "left_event": negative, "right_event": zero,
                "left_endpoint_multiplicity": None, "right_endpoint_multiplicity": 1,
                "distinct_roots_open": 0, "multiple_roots_open": 0, "all_roots_simple": True,
            },
        },
        {
            "parent_local_interval": ["1/2", "1"],
            "summary": {
                "status": "CERTIFIED", "left_event": zero, "right_event": positive,
                "left_endpoint_multiplicity": 1, "right_endpoint_multiplicity": None,
                "distinct_roots_open": 0, "multiple_roots_open": 0, "all_roots_simple": True,
            },
        },
    ]
    composed = model._compose_child_summaries(synthetic)
    assert composed["status"] == "CERTIFIED", composed
    assert composed["distinct_roots_open"] == 1
    assert len(composed["internal_cut_roots"]) == 1
    assert composed["internal_cut_roots"][0]["multiplicity"] == 1
    bad_mult = copy.deepcopy(synthetic)
    bad_mult[1]["summary"]["left_endpoint_multiplicity"] = 2
    assert model._compose_child_summaries(bad_mult)["status"] == "BLOCKED"
    bad_relation = copy.deepcopy(synthetic)
    bad_relation[1]["summary"]["left_event"] = positive
    assert model._compose_child_summaries(bad_relation)["status"] == "SEMANTIC_BLOCKER"

    # One unresolved child and an exact resource refusal both propagate fail-closed.
    blocked = copy.deepcopy(synthetic)
    blocked[1]["summary"] = {"status": "BLOCKED", "reason": "TEST_CHILD_BLOCKED"}
    assert model._compose_child_summaries(blocked)["status"] == "BLOCKED"
    refused = copy.deepcopy(synthetic)
    refused[1]["summary"] = model.resource_refusal()
    refused_result = model._compose_child_summaries(refused)
    assert refused_result["status"] == "RESOURCE_REFUSAL"
    assert refused_result["is_truth_value"] is False

    # Caller-provided cuts/certificates/root metadata are stripped and cannot become authority.
    forged = copy.deepcopy(source)
    forged.update({
        "phase_sector_partition": ["0", "1"],
        "sector_cuts": ["1/999999"],
        "child_certificates": [{"status": "CERTIFIED"}],
        "root_count": 0,
        "endpoint_events": {"left": "FORGED", "right": "FORGED"},
        "deduplication_assertion": True,
        "multiplicity_certificate": 99,
    })
    forged_result = model.classify_required_analytic_event(forged)
    assert forged_result["status"] == result["status"]
    assert _v27_route(forged_result)["sector_cut_certificate"]["cuts"] == route["sector_cut_certificate"]["cuts"]

    # Binary floating point and an independent source coordinate never become exact authority.
    float_spec = copy.deepcopy(source)
    float_spec["phase_turn_rate"] = 2.0 / 3.0
    assert model.classify_required_analytic_event(float_spec)["status"] != "CERTIFIED"
    mismatch = copy.deepcopy(source)
    mismatch["parameter_projection"] = "independent-u"
    assert model.classify_required_analytic_event(mismatch)["status"] != "CERTIFIED"

    # Historical v26 success has strict precedence and is returned unchanged by v27.
    historical = v26test._fixture()
    historical_v26 = v26.classify_required_analytic_event(historical)
    assert historical_v26["status"] == "CERTIFIED"
    assert model.classify_required_analytic_event(historical) == historical_v26

    # v27 is a PB-007-01 extension only; it never promotes MC-B/MC-1 itself.
    assert model.V27_ROUTE.startswith("EXACT_")
    assert model.resource_refusal()["is_truth_value"] is False

    print("PB-007-01 v27 phase-sector partition adversarial tests passed")


if __name__ == "__main__":
    run()
