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
import pb00701_signed_b_anti_diagonal_model as v40  # noqa: E402
import test_pb00701_signed_b_anti_diagonal_adversarial as v40test  # noqa: E402
import test_pb00701_phase_sector_partition_adversarial as v27test  # noqa: E402

TINY = Fraction(1, 100000000)


def _spec(a, b, *, offset, rate):
    c = model._trim(model.v22._padd(a, b))
    s = model._trim(model.v22._padd(a, model.v22._pscale(b, -1)))
    return v40test._spec({1: c, 2: [-TINY]}, {1: s}, offset=str(offset), rate=str(rate))


def _route(result):
    assert result["status"] == "CERTIFIED", result
    routes = [span["route"] for span in result.get("spans", []) if span.get("route_kind") == "PB00701_V41_EXACT_ROTATED_COORDINATE_ORIENTATION_ROOT_PARTITION_COMPOSITION"]
    assert routes, result
    return routes[0]


def _acceptance_candidates():
    roots = [Fraction(1, 4), Fraction(1, 3), Fraction(2, 5), Fraction(3, 5), Fraction(2, 3), Fraction(3, 4)]
    phases = [
        (Fraction(-3, 16), Fraction(1, 8)),
        (Fraction(1, 16), Fraction(1, 8)),
        (Fraction(-1, 4), Fraction(1, 4)),
        (Fraction(0), Fraction(1, 4)),
        (Fraction(-1, 8), Fraction(1, 4)),
        (Fraction(1, 8), Fraction(1, 4)),
        (Fraction(-1, 6), Fraction(1, 3)),
        (Fraction(0), Fraction(1, 3)),
    ]
    for ra in roots:
        for rb in roots:
            if ra == rb:
                continue
            a = [-ra, Fraction(1)]
            b = [-rb, Fraction(1)]
            for offset, rate in phases:
                yield ra, rb, offset, rate, _spec(a, b, offset=offset, rate=rate)


def _find_acceptance():
    diagnostics = []
    for ra, rb, offset, rate, spec in _acceptance_candidates():
        old = v40.classify_required_analytic_event(spec)
        if old.get("status") == "CERTIFIED":
            continue
        new = model.classify_required_analytic_event(spec)
        if new.get("status") == "CERTIFIED":
            return (ra, rb, offset, rate, spec, old, new)
        if len(diagnostics) < 12:
            diagnostics.append((str(ra), str(rb), str(offset), str(rate), new.get("status"), json.dumps(new, sort_keys=True)[-600:]))
    raise AssertionError("no exact residual acceptance fixture found in targeted rational candidate family: " + repr(diagnostics))


def run():
    # Exact root completeness, order, multiplicity, endpoints, and irrational fail-closed boundary.
    simple = model.exact_rational_orientation_roots([Fraction(1, 6), Fraction(-5, 6), 1], "SIMPLE")
    assert simple["status"] == "CERTIFIED"
    assert [x["source"] for x in simple["roots"]] == ["1/3", "1/2"]
    repeated = model.exact_rational_orientation_roots([Fraction(1, 4), -1, 1], "REPEATED")
    assert repeated["status"] == "CERTIFIED" and repeated["roots"] == [{"source": "1/2", "multiplicity": 2}]
    endpoint = model.exact_rational_orientation_roots([0, -1, 1], "ENDPOINT")
    assert endpoint["status"] == "CERTIFIED"
    assert endpoint["roots"] == [] and endpoint["endpoint_roots"] == [{"source": "0", "multiplicity": 1}, {"source": "1", "multiplicity": 1}]
    irrational = model.exact_rational_orientation_roots([-2, 0, 4], "IRRATIONAL")
    assert irrational["status"] == "BLOCKED"
    assert irrational["missing_exact_root_count"] == 1
    assert "IRRATIONAL_ALGEBRAIC" in irrational["reason"]

    # Coincident A/B roots deduplicate to one source cut while retaining both causes.
    cert = model._orientation_cut_certificate({1: [-1, 2]}, {1: [0]}, Fraction(1, 16), Fraction(1, 8))
    # A source with a zero quadrature is not route-eligible, but exact cut derivation remains source-owned.
    assert cert["status"] == "CERTIFIED"
    assert cert["caller_cuts_trusted"] is False

    ra, rb, offset, rate, source, old, result = _find_acceptance()
    assert old["status"] != "CERTIFIED"
    route = _route(result)
    assert route["relation"] == model.V41_ROUTE
    assert route["all_children_reclassified_by_complete_v40_authority"] is True
    assert route["orientation_roots_are_proof_geometry_only"] is True
    assert route["partition_certificate"]["coincident_cuts_deduplicated"] is True
    assert all(child["summary"]["status"] == "CERTIFIED" for child in route["children"])
    assert all(Fraction(*map(int, x.split('/'))) if '/' in x else Fraction(int(x)) for x in route["partition_certificate"]["cuts"])

    # Exact reverse-rate analogue must remain exact and certifiable where child authority supports it.
    reverse = copy.deepcopy(source)
    reverse["phase_turn_offset"] = str(offset + rate)
    reverse["phase_turn_rate"] = str(-rate)
    reverse_old = v40.classify_required_analytic_event(reverse)
    reverse_new = model.classify_required_analytic_event(reverse)
    assert reverse_old.get("status") != "CERTIFIED"
    assert reverse_new.get("status") == "CERTIFIED", reverse_new

    # Forged caller partition/root/child/multiplicity evidence is ignored.
    forged = copy.deepcopy(source)
    forged.update({
        "orientation_roots": ["1/999"],
        "orientation_partition_certificate": {"status": "CERTIFIED"},
        "cuts": ["1/999"],
        "children": [{"status": "CERTIFIED"}],
        "child_root_counts": [0],
        "multiplicity_certificate": {"status": "CERTIFIED"},
        "root_count": 0,
    })
    assert model.classify_required_analytic_event(forged) == result

    # Historical v40 and v27 successes retain strict byte-for-byte precedence.
    prior40 = v40test._fixture()
    assert model.classify_required_analytic_event(prior40) == v40.classify_required_analytic_event(prior40)
    prior27 = v27test._fixture()
    assert model.classify_required_analytic_event(prior27) == v40.classify_required_analytic_event(prior27)

    # Exact composition: proof cut without physical equality is neutral; equality mismatch fails closed.
    neutral = [
        {"parent_local_interval": ["0", "1/2"], "summary": {"status": "CERTIFIED", "right_event": {"relation": "POSITIVE"}, "left_event": {"relation": "POSITIVE"}, "right_endpoint_multiplicity": None, "left_endpoint_multiplicity": None, "distinct_roots_open": 0, "multiple_roots_open": 0, "all_roots_simple": True}},
        {"parent_local_interval": ["1/2", "1"], "summary": {"status": "CERTIFIED", "left_event": {"relation": "POSITIVE"}, "right_event": {"relation": "POSITIVE"}, "right_endpoint_multiplicity": None, "left_endpoint_multiplicity": None, "distinct_roots_open": 0, "multiple_roots_open": 0, "all_roots_simple": True}},
    ]
    composed = model.v27._compose_child_summaries(neutral)
    assert composed["status"] == "CERTIFIED" and composed["internal_cut_roots"] == []
    bad = copy.deepcopy(neutral)
    bad[1]["summary"]["left_event"] = {"relation": "NEGATIVE"}
    assert model.v27._compose_child_summaries(bad)["status"] == "SEMANTIC_BLOCKER"

    # Resource refusal remains non-truth.
    refusal = model.resource_refusal()
    assert refusal["status"] == "RESOURCE_REFUSAL" and refusal["is_truth_value"] is False

    print("v41 acceptance", ra, rb, offset, rate, route["child_count"])


if __name__ == "__main__":
    run()
