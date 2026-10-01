#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_orientation_root_partition_model as model  # noqa: E402
import pb00701_correlated_closed_handoff_model as v43  # noqa: E402
import pb00701_orientation_transition_bridge_model as v42  # noqa: E402
import pb00701_signed_b_anti_diagonal_model as v40  # noqa: E402
import test_pb00701_correlated_closed_handoff_adversarial as v43test  # noqa: E402
import test_pb00701_orientation_transition_bridge_adversarial as v42test  # noqa: E402
import test_pb00701_signed_b_anti_diagonal_adversarial as v40test  # noqa: E402
import test_pb00701_phase_sector_partition_adversarial as v27test  # noqa: E402

TINY = Fraction(1, 100000000)


def _spec(a, b, *, offset, rate):
    c = model._trim(model.v22._padd(a, b))
    s = model._trim(model.v22._padd(a, model.v22._pscale(b, -1)))
    return v40test._spec({1: c, 2: [-TINY]}, {1: s}, offset=str(offset), rate=str(rate))


def _linear_spec(ra, rb, sa, sb, *, offset, rate):
    a = [-sa * ra, sa]
    b = [-sb * rb, sb]
    c = model._trim(model.v22._padd(a, b))
    sin = model._trim(model.v22._padd(a, model.v22._pscale(b, -1)))
    return v40test._spec({1: c}, {1: sin}, offset=str(offset), rate=str(rate))


def _route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [
        span["route"]
        for span in result.get("spans", [])
        if span.get("route_kind")
        == "PB00701_V41_EXACT_ROTATED_COORDINATE_ORIENTATION_ROOT_PARTITION_COMPOSITION"
    ]
    assert routes, result
    return routes[0]


def _child_owners(route):
    owners = []
    for index, child in enumerate(route["children"]):
        for span in child["child_result"].get("spans", []):
            cr = span.get("route", {})
            if cr.get("status") == "CERTIFIED":
                owners.append(
                    (
                        index,
                        span.get("route_kind"),
                        cr.get("harmonic"),
                        tuple(child["parent_local_interval"]),
                    )
                )
    return owners


def _acceptance():
    source = v43test._spec()
    predecessor = v43.classify_required_analytic_event(source)
    assert predecessor["status"] != "CERTIFIED", predecessor

    result = model.classify_required_analytic_event(source)
    route = _route(result)
    owners = _child_owners(route)
    assert owners, route
    return source, predecessor, result, route, owners


def run_roots():
    simple = model.exact_rational_orientation_roots(
        [Fraction(1, 6), Fraction(-5, 6), 1], "SIMPLE"
    )
    assert simple["status"] == "CERTIFIED", simple
    assert [x["source"] for x in simple["roots"]] == ["1/3", "1/2"]

    nearby = model.exact_rational_orientation_roots(
        [Fraction(101, 400), Fraction(-201, 200), 1], "NEARBY"
    )
    assert nearby["status"] == "CERTIFIED", nearby
    assert [x["source"] for x in nearby["roots"]] == ["1/2", "101/200"]

    repeated = model.exact_rational_orientation_roots([Fraction(1, 4), -1, 1], "REPEATED")
    assert repeated["status"] == "CERTIFIED", repeated
    assert repeated["roots"] == [{"source": "1/2", "multiplicity": 2}]

    endpoint = model.exact_rational_orientation_roots([0, -1, 1], "ENDPOINT")
    assert endpoint["status"] == "CERTIFIED", endpoint
    assert endpoint["roots"] == []
    assert endpoint["endpoint_roots"] == [
        {"source": "0", "multiplicity": 1},
        {"source": "1", "multiplicity": 1},
    ]

    irrational = model.exact_rational_orientation_roots([-2, 0, 4], "IRRATIONAL")
    assert irrational["status"] == "BLOCKED", irrational
    assert irrational["missing_exact_root_count"] == 1
    assert "IRRATIONAL_ALGEBRAIC" in irrational["reason"]

    # A and B share s=1/2. The canonical cut appears once with both causes.
    c_same = [Fraction(-3, 2), Fraction(3)]
    s_same = [Fraction(1, 2), Fraction(-1)]
    cert_same = model._orientation_cut_certificate(
        {1: c_same}, {1: s_same}, Fraction(1, 16), Fraction(1, 8)
    )
    assert cert_same["status"] == "CERTIFIED", cert_same
    records = [r for r in cert_same["cut_records"] if r["source_cut"] == "1/2"]
    assert len(records) == 1
    coordinates = {
        cause.get("coordinate")
        for cause in records[0]["causes"]
        if cause.get("kind") == "orientation_root"
    }
    assert coordinates == {"A", "B"}, records

    # An A orientation root coincident with a historical exact phase-sector
    # cut is still one canonical proof cut and never creates a zero-width child.
    a = [Fraction(-1, 2), 1]
    b = [Fraction(-1, 3), 1]
    c_prior = model._trim(model.v22._padd(a, b))
    s_prior = model._trim(model.v22._padd(a, model.v22._pscale(b, -1)))
    cert_prior = model._orientation_cut_certificate(
        {1: c_prior}, {1: s_prior}, Fraction(0), Fraction(1, 3)
    )
    prior_record = [r for r in cert_prior["cut_records"] if r["source_cut"] == "1/2"]
    assert len(prior_record) == 1, cert_prior
    kinds = {cause.get("kind") for cause in prior_record[0]["causes"]}
    assert "orientation_root" in kinds and "historical_phase_sector_cut" in kinds
    assert cert_prior["coincident_cuts_deduplicated"] is True
    assert cert_prior["caller_cuts_trusted"] is False

    # Root-isolation resource refusal remains non-truth.
    saved = model._distinct_open_root_count
    try:
        def refuse(_poly):
            raise MemoryError("test")
        model._distinct_open_root_count = refuse
        refused = model.exact_rational_orientation_roots([Fraction(-1, 2), 1], "REFUSE")
        assert refused["status"] == "RESOURCE_REFUSAL"
        assert refused["is_truth_value"] is False
    finally:
        model._distinct_open_root_count = saved

    # Certificate-cut construction is sign/rate symmetric and exact.
    cos_polys, sin_polys = v43test._maps()
    reverse = model._orientation_cut_certificate(
        cos_polys, sin_polys,
        v43test.OFFSET + v43test.RATE,
        -v43test.RATE,
    )
    assert reverse["status"] == "CERTIFIED", reverse


def run_acceptance():
    source, predecessor, result, route, owners = _acceptance()
    assert predecessor["status"] != "CERTIFIED"
    assert route["relation"] == model.V41_ROUTE
    assert route["all_children_reclassified_by_complete_v43_authority"] is True
    assert route["zero_adjacent_children_require_v43_or_other_independent_current_authority"] is True
    assert route["orientation_roots_are_proof_geometry_only"] is True
    assert route["partition_certificate"]["coincident_cuts_deduplicated"] is True
    assert all(child["summary"]["status"] == "CERTIFIED" for child in route["children"])

    kinds = {kind for _, kind, _, _ in owners if kind}
    assert "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF" in kinds, owners
    assert len(kinds) >= 2, owners

    roots = route["partition_certificate"]["orientation_roots"]
    a_roots = {
        item["source"] for item in roots
        if item["harmonic"] == 1 and item["coordinate"] == "A"
    }
    b_roots = {
        item["source"] for item in roots
        if item["harmonic"] == 1 and item["coordinate"] == "B"
    }
    assert str(v43test.HANDOFF) in a_roots, roots
    assert "1/2" in b_roots, roots

    # The v43 handoff root itself is proof geometry, not a physical event.
    cos_polys, sin_polys = v43test._maps()
    event = model.v27.v19._endpoint_relation(
        cos_polys,
        sin_polys,
        v43test.HANDOFF,
        v43test.OFFSET + v43test.RATE * v43test.HANDOFF,
    )
    assert event["relation"] != "ZERO", event

    # Caller-supplied partition/root/reparameterization evidence is ignored.
    forged = copy.deepcopy(source)
    forged.update(
        {
            "orientation_roots": ["1/999"],
            "orientation_partition_certificate": {"status": "CERTIFIED"},
            "cuts": ["1/999"],
            "children": [{"status": "CERTIFIED"}],
            "child_root_counts": [0],
            "multiplicity_certificate": {"status": "CERTIFIED"},
            "root_count": 0,
            "reparameterization": {"status": "CERTIFIED"},
        }
    )
    assert model.classify_required_analytic_event(forged) == result

    float_forged = copy.deepcopy(source)
    float_forged["phase_turn_rate"] = 0.125
    try:
        float_result = model.classify_required_analytic_event(float_forged)
    except (AssertionError, ValueError, TypeError):
        float_result = {"status": "REJECTED"}
    assert float_result.get("status") != "CERTIFIED"

    print(
        "v41 v43-aware exact orientation-root composition",
        "children",
        route["child_count"],
        "owners",
        owners,
        "orientation roots",
        [(x["coordinate"], x["source"]) for x in roots],
    )
    return source, result


def run_precedence():
    # A child already owned by v43 must remain byte-for-byte v43-owned.
    right_spec, _, _ = v43test._right_child_material()
    prior43 = v43.classify_required_analytic_event(right_spec)
    assert prior43["status"] == "CERTIFIED", prior43
    assert model.classify_required_analytic_event(right_spec) == prior43

    prior42 = v42test._fixture()
    assert model.classify_required_analytic_event(prior42) == v43.classify_required_analytic_event(prior42)
    prior40 = v40test._fixture()
    assert model.classify_required_analytic_event(prior40) == v43.classify_required_analytic_event(prior40)
    prior27 = v27test._fixture()
    assert model.classify_required_analytic_event(prior27) == v43.classify_required_analytic_event(prior27)

    # Existing negative-rate v43 authority remains intact.
    v43test.run_reverse_direction()


def _composition_children():
    return [
        {
            "parent_local_interval": ["0", "1/2"],
            "parent_source_interval": ["0", "1/2"],
            "exact_parent_to_child_coefficients": ["0", "1/2"],
            "source_parameter_id": "s",
            "summary": {
                "status": "CERTIFIED",
                "right_event": {"relation": "POSITIVE"},
                "left_event": {"relation": "POSITIVE"},
                "right_endpoint_multiplicity": None,
                "left_endpoint_multiplicity": None,
                "distinct_roots_open": 0,
                "multiple_roots_open": 0,
                "all_roots_simple": True,
            },
        },
        {
            "parent_local_interval": ["1/2", "1"],
            "parent_source_interval": ["1/2", "1"],
            "exact_parent_to_child_coefficients": ["1/2", "1/2"],
            "source_parameter_id": "s",
            "summary": {
                "status": "CERTIFIED",
                "left_event": {"relation": "POSITIVE"},
                "right_event": {"relation": "POSITIVE"},
                "right_endpoint_multiplicity": None,
                "left_endpoint_multiplicity": None,
                "distinct_roots_open": 0,
                "multiple_roots_open": 0,
                "all_roots_simple": True,
            },
        },
    ]


def run_composition():
    neutral = _composition_children()
    composed = model._compose_v41_children(neutral, "s")
    assert composed["status"] == "CERTIFIED" and composed["internal_cut_roots"] == []

    physical = copy.deepcopy(neutral)
    physical[0]["summary"]["right_event"] = {"relation": "ZERO"}
    physical[1]["summary"]["left_event"] = {"relation": "ZERO"}
    physical[0]["summary"]["right_endpoint_multiplicity"] = 1
    physical[1]["summary"]["left_endpoint_multiplicity"] = 1
    one = model._compose_v41_children(physical, "s")
    assert one["status"] == "CERTIFIED"
    assert len(one["internal_cut_roots"]) == 1
    assert one["distinct_roots_open"] == 1

    bad = copy.deepcopy(physical)
    bad[1]["summary"]["left_endpoint_multiplicity"] = 2
    blocked = model._compose_v41_children(bad, "s")
    assert blocked["status"] == "BLOCKED"
    assert "MULTIPLICITY" in blocked["reason"]

    mismatch = copy.deepcopy(neutral)
    mismatch[1]["summary"]["left_event"] = {"relation": "NEGATIVE"}
    assert model._compose_v41_children(mismatch, "s")["status"] == "SEMANTIC_BLOCKER"

    wrong_source = copy.deepcopy(neutral)
    wrong_source[1]["source_parameter_id"] = "forged"
    result = model._compose_v41_children(wrong_source, "s")
    assert result["status"] == "SEMANTIC_BLOCKER"
    assert "SOURCE_PARAMETER_ID" in result["reason"]

    wrong_map = copy.deepcopy(neutral)
    wrong_map[1]["exact_parent_to_child_coefficients"] = ["1/2", "1/3"]
    result = model._compose_v41_children(wrong_map, "s")
    assert result["status"] == "SEMANTIC_BLOCKER"
    assert "REPARAMETERIZATION" in result["reason"]

    wrong_interval = copy.deepcopy(neutral)
    wrong_interval[1]["parent_source_interval"] = ["2/3", "1"]
    result = model._compose_v41_children(wrong_interval, "s")
    assert result["status"] == "SEMANTIC_BLOCKER"
    assert "SOURCE_INTERVAL" in result["reason"]

    # Reparameterization resource refusal cannot become truth.
    cos_polys, sin_polys = v43test._maps()
    saved = model.v27._child_spec
    try:
        def refuse(*_args, **_kwargs):
            raise MemoryError("test")
        model.v27._child_spec = refuse
        refusal = model._partition_route(
            cos_polys,
            sin_polys,
            v43test.OFFSET,
            v43test.RATE,
            "pb00701-v43-correlated-handoff",
            (Fraction(0), Fraction(1)),
        )
        assert refusal["status"] == "RESOURCE_REFUSAL"
        assert refusal["is_truth_value"] is False
    finally:
        model.v27._child_spec = saved

    refusal = model.resource_refusal()
    assert refusal["status"] == "RESOURCE_REFUSAL" and refusal["is_truth_value"] is False


def run():
    run_roots()
    run_acceptance()
    run_precedence()
    run_composition()


if __name__ == "__main__":
    run()
