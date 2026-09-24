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
import pb00701_orientation_transition_bridge_model as v42  # noqa: E402
import pb00701_signed_b_anti_diagonal_model as v40  # noqa: E402
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


def _acceptance_candidates():
    # Focused exact candidate while establishing the v42-aware composition witness.
    # phi=-1/8+s/4: diagonal v42 authority owns [0,1/4] in source s;
    # both orientation roots lie strictly inside that cell.
    meta = {
        "A_root": Fraction(1, 8),
        "B_root": Fraction(1, 6),
        "A_scale": Fraction(1),
        "B_scale": Fraction(1),
        "offset": Fraction(-1, 8),
        "rate": Fraction(1, 4),
    }
    yield meta, _linear_spec(
        meta["A_root"], meta["B_root"],
        meta["A_scale"], meta["B_scale"],
        offset=meta["offset"], rate=meta["rate"],
    )


def _child_owners(route):
    owners = []
    for index, child in enumerate(route["children"]):
        for span in child["child_result"].get("spans", []):
            child_route = span.get("route", {})
            if child_route.get("status") == "CERTIFIED":
                owners.append(
                    (
                        index,
                        span.get("route_kind"),
                        child_route.get("harmonic"),
                        tuple(child["parent_local_interval"]),
                    )
                )
    return owners


def _failure_digest(result):
    out = []
    for span in result.get("spans", []):
        route = span.get("route", {})
        item = {
            "source_interval": span.get("source_interval"),
            "route_kind": span.get("route_kind"),
            "route_status": route.get("status"),
            "route_reason": route.get("reason"),
            "failed_child_interval": route.get("failed_child_interval"),
        }
        blocker = route.get("child_blocker", {})
        if blocker:
            item["child_blocker_status"] = blocker.get("status")
            item["child_blocker_reason"] = blocker.get("reason")
            item["child_blocker_relation"] = blocker.get("relation")
        child_digests = []
        for child in route.get("children", []):
            cd = {
                "interval": child.get("parent_local_interval"),
                "summary_status": child.get("summary", {}).get("status"),
                "summary_reason": child.get("summary", {}).get("reason"),
                "child_status": child.get("child_result", {}).get("status"),
                "child_relation": child.get("child_result", {}).get("relation"),
                "routes": [],
            }
            for cspan in child.get("child_result", {}).get("spans", []):
                cr = cspan.get("route", {})
                cd["routes"].append({
                    "kind": cspan.get("route_kind"),
                    "status": cr.get("status"),
                    "reason": cr.get("reason"),
                    "harmonic": cr.get("harmonic"),
                })
            child_digests.append(cd)
        if child_digests:
            item["children"] = child_digests
        out.append(item)
    return out


def _find_acceptance():
    diagnostics = []
    for meta, spec in _acceptance_candidates():
        predecessor = v42.classify_required_analytic_event(spec)
        if predecessor.get("status") == "CERTIFIED":
            continue
        new = model.classify_required_analytic_event(spec)
        if new.get("status") != "CERTIFIED":
            if len(diagnostics) < 16:
                diagnostics.append(
                    (
                        {k: str(v) for k, v in meta.items()},
                        new.get("status"),
                        _failure_digest(new),
                    )
                )
            continue
        route = _route(new)
        owners = _child_owners(route)
        if not any(kind == "PB00701_V42_EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_BRIDGE" for _, kind, _, _ in owners):
            continue
        distinct_owners = {(kind, harmonic) for _, kind, harmonic, _ in owners}
        if len(distinct_owners) < 2:
            continue

        return meta, spec, predecessor, new, owners

    raise AssertionError(
        "no exact v42-residual composition fixture found in bounded two-harmonic family: "
        + repr(diagnostics)
    )


def run_roots():
    simple = model.exact_rational_orientation_roots(
        [Fraction(1, 6), Fraction(-5, 6), 1], "SIMPLE"
    )
    assert simple["status"] == "CERTIFIED", simple
    assert [x["source"] for x in simple["roots"]] == ["1/3", "1/2"]
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

    # Both A and B share s=1/2; the canonical cut must occur once with both causes.
    c = [Fraction(-3, 2), Fraction(3)]
    s = [Fraction(1, 2), Fraction(-1)]
    cert = model._orientation_cut_certificate({1: c}, {1: s}, Fraction(1, 16), Fraction(1, 8))
    assert cert["status"] == "CERTIFIED", cert
    records = [r for r in cert["cut_records"] if r["source_cut"] == "1/2"]
    assert len(records) == 1
    coordinates = {
        cause.get("coordinate")
        for cause in records[0]["causes"]
        if cause.get("kind") == "orientation_root"
    }
    assert coordinates == {"A", "B"}, records
    assert cert["coincident_cuts_deduplicated"] is True
    assert cert["caller_cuts_trusted"] is False


def run_acceptance():
    meta, source, predecessor, result, owners = _find_acceptance()
    assert predecessor["status"] != "CERTIFIED"
    route = _route(result)
    assert route["relation"] == model.V41_ROUTE
    assert route["all_children_reclassified_by_complete_v42_authority"] is True
    assert route["zero_adjacent_children_require_v42_or_other_independent_current_authority"] is True
    assert route["orientation_roots_are_proof_geometry_only"] is True
    assert route["partition_certificate"]["coincident_cuts_deduplicated"] is True
    assert all(child["summary"]["status"] == "CERTIFIED" for child in route["children"])

    # The new authority must be composition beyond v42 alone, with at least
    # one actual v42 handoff child and at least one differently owned child.
    assert any(
        kind == "PB00701_V42_EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_BRIDGE"
        for _, kind, _, _ in owners
    ), owners
    assert len({(kind, harmonic) for _, kind, harmonic, _ in owners}) >= 2, owners

    # Both source-owned A1 roots and the source-owned B2 root participate in
    # exact partitioning; zero-adjacent pieces are never relabelled strict v39/v40.
    roots = route["partition_certificate"]["orientation_roots"]
    assert any(r["coordinate"] == "A" and r["harmonic"] == 1 for r in roots), roots
    assert any(r["coordinate"] == "B" and r["harmonic"] == 2 for r in roots), roots

    # Exact source-parameter reversal exercises the negative phase-rate direction
    # without asking one asymmetric source to satisfy two different phase-cell layouts.
    reverse = _linear_spec(
        1 - meta["A_root"],
        1 - meta["B_root"],
        -meta["A_scale"],
        -meta["B_scale"],
        offset=meta["offset"] + meta["rate"],
        rate=-meta["rate"],
    )
    reverse_predecessor = v42.classify_required_analytic_event(reverse)
    reverse_new = model.classify_required_analytic_event(reverse)
    assert reverse_predecessor.get("status") != "CERTIFIED"
    assert reverse_new.get("status") == "CERTIFIED", reverse_new

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
        "v41 v42-aware acceptance",
        {k: str(v) for k, v in meta.items()},
        "children",
        route["child_count"],
        "owners",
        owners,
    )
    return source, result


def run_precedence():
    prior42 = v42test._fixture()
    assert model.classify_required_analytic_event(prior42) == v42.classify_required_analytic_event(prior42)
    prior40 = v40test._fixture()
    assert model.classify_required_analytic_event(prior40) == v42.classify_required_analytic_event(prior40)
    prior27 = v27test._fixture()
    assert model.classify_required_analytic_event(prior27) == v42.classify_required_analytic_event(prior27)


def run_composition():
    neutral = [
        {
            "parent_local_interval": ["0", "1/2"],
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
    composed = model.v27._compose_child_summaries(neutral)
    assert composed["status"] == "CERTIFIED" and composed["internal_cut_roots"] == []

    physical = copy.deepcopy(neutral)
    physical[0]["summary"]["right_event"] = {"relation": "ZERO"}
    physical[1]["summary"]["left_event"] = {"relation": "ZERO"}
    physical[0]["summary"]["right_endpoint_multiplicity"] = 1
    physical[1]["summary"]["left_endpoint_multiplicity"] = 1
    one = model.v27._compose_child_summaries(physical)
    assert one["status"] == "CERTIFIED"
    assert len(one["internal_cut_roots"]) == 1
    assert one["distinct_roots_open"] == 1

    bad = copy.deepcopy(physical)
    bad[1]["summary"]["left_endpoint_multiplicity"] = 2
    blocked = model.v27._compose_child_summaries(bad)
    assert blocked["status"] == "BLOCKED"
    assert "MULTIPLICITY" in blocked["reason"]

    mismatch = copy.deepcopy(neutral)
    mismatch[1]["summary"]["left_event"] = {"relation": "NEGATIVE"}
    assert model.v27._compose_child_summaries(mismatch)["status"] == "SEMANTIC_BLOCKER"

    refusal = model.resource_refusal()
    assert refusal["status"] == "RESOURCE_REFUSAL" and refusal["is_truth_value"] is False


def run():
    run_roots()
    run_acceptance()
    run_precedence()
    run_composition()


if __name__ == "__main__":
    run()
