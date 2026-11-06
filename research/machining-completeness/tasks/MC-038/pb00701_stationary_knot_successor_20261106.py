#!/usr/bin/env python3
"""PB-007-01: bounded, original-source stationary polynomial knot/sign compositor.

Research successor only; frozen V54 and all historical failures stay unchanged.
The child Sturm/order certificate is independently rechecked by the existing
pinned stationary polynomial verifier. Nontruth refusals never reduce blockers.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
CHILD = HERE / "verify_pb00701_stationary_polynomial_order.py"
RECEIPT = HERE / "pb00701-stationary-knot-successor-20261106.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
CHILD_BLOB = "0954c5e1ad63ec1c8dd2acb3202882650b02c516"
SOURCE_SHA256 = {
    "composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0":
        "f4c2d33cc4c5a52f355ff4ecc36ad6ee38af0ff0fa8c5159aaac5923a10125ff",
    "composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100":
        "a49b92bbb74a7e016eed471feb64808eb9109a6a42b3ef874243364981a396fd",
}
SCHEMA = "radicadsac-pb00701-stationary-knot-successor/1.0"
EVIDENCE_CLASS = "DETERMINISTIC_MODEL"
MAX_BYTES = 300000
MAX_CHILD_BISECTIONS = 512


class Refused(ValueError):
    """A deliberately nontruth admission or composition refusal."""


def require(test, reason):
    if not test:
        raise Refused(reason)


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def read_pinned(path, blob, size):
    with path.open("rb") as handle:
        raw = handle.read(size + 1)
    require(len(raw) <= size, "PINNED_FILE_BYTE_BUDGET_REFUSAL")
    require(git_blob(raw) == blob, "PINNED_GIT_BLOB_DRIFT")
    return raw


def load_child():
    require(git_blob(read_pinned(CHILD, CHILD_BLOB, 60000)) == CHILD_BLOB,
            "STATIONARY_CHILD_DRIFT")
    spec = importlib.util.spec_from_file_location("pb00701_stationary_knot_child", CHILD)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    require(git_blob(read_pinned(CHILD, CHILD_BLOB, 60000)) == CHILD_BLOB,
            "STATIONARY_CHILD_IMPORT_DRIFT")
    return mod


P = load_child()


def as_sign(name):
    require(name in ("POSITIVE", "NEGATIVE"), "INVALID_PHYSICAL_SIGN")
    return 1 if name == "POSITIVE" else -1


def source_hash(spec):
    return P.IDENTITY.hash_exact_source_record(spec)


def boundary_key(span, boundary):
    kind = boundary["kind"]
    if kind == "ROOT":
        return "span" + str(span) + ":root" + str(boundary["root_index"])
    if kind == "LEFT_ENDPOINT":
        return "source:left" if span == 0 else "knot:1"
    if kind == "RIGHT_ENDPOINT":
        return "source:right" if span == 1 else "knot:1"
    raise Refused("UNKNOWN_CHILD_CELL_BOUNDARY")


def compose_checked_child(child, spec):
    """Compose *validated* complete child sign cells and rational knot germs.

    Correctness premise: each child contains every root (Sturm), its exact
    order/multiplicity and all root-free sign cells, checked independently by
    the pinned child validator. Adjacent original pieces meet at one rational
    knot. Nonzero continuous knots glue cells; zero knots remain a separate
    event with two explicitly sided orders. There is no numerical search.
    """
    require(child.get("status") == "STATIONARY_POLYNOMIAL_ORDERED_VIEWS_CERTIFIED",
            "NOT_A_CERTIFIED_STATIONARY_CHILD")
    P.validate_source_candidate(child, spec)
    spans = P.source_stationary_spans(spec)
    require(len(spans) == 2 and child.get("historical_span_count") == 2,
            "EXACT_TWO_SPAN_GRAMMAR_REQUIRED")
    require(all(x.get("owner") == P.OWNER for x in spans),
            "EVERY_SPAN_MUST_HAVE_STATIONARY_POLYNOMIAL_OWNER")
    require(child.get("all_historical_spans_stationary") is True,
            "UNSUPPORTED_HISTORICAL_OWNER")
    views = sorted(child["views"], key=lambda x: x["span_index"])
    require([x["span_index"] for x in views] == [0, 1],
            "ORDERED_COMPLETE_TWO_CHILD_COVER_REQUIRED")
    (a, knot1), (knot2, b) = [x["source_interval"] for x in spans]
    require(a < knot1 == knot2 < b, "NONCONSECUTIVE_OR_EMPTY_SOURCE_PIECES")
    p0, p1 = [x["polynomial"] for x in spans]
    knot_left = P.EE.peval(p0, Q(1))
    knot_right = P.EE.peval(p1, Q(0))
    require(knot_left == knot_right, "PHYSICAL_KNOT_DISCONTINUITY")
    knot_value = knot_left

    records = []
    cells = []
    for i, item in enumerate(views):
        v = item["ordered_view"]
        for root in v["ordered_open_roots"]:
            record = {
                "id": "span" + str(i) + ":root" + str(root["index"]),
                "span_index": i,
                "root_kind": root["kind"],
                "multiplicity": root["multiplicity"],
                "event_kind": root["event_kind"],
                "left_sign": root["left_sign"],
                "right_sign": root["right_sign"],
            }
            if root["kind"] == "RATIONAL_ROOT":
                record["source_value"] = root["source_value"]
            else:
                record["source_isolating_interval"] = root["source_isolating_interval"]
                record["defining_polynomial"] = root["defining_polynomial"]
            records.append(record)
        for cell in v["sign_cells"]:
            cells.append({
                "left_boundary": boundary_key(i, cell["left_boundary"]),
                "right_boundary": boundary_key(i, cell["right_boundary"]),
                "sign": cell["sign"],
                "children": [{"span_index": i, "cell_index": cell["index"]}],
            })

    first_cell_count = len(views[0]["ordered_view"]["sign_cells"])
    require(first_cell_count > 0 and len(cells) > first_cell_count,
            "MISSING_NONZERO_CHILD_CELLS")
    left_knot_cell = cells[first_cell_count - 1]
    right_knot_cell = cells[first_cell_count]
    require(left_knot_cell["right_boundary"] == "knot:1" and
            right_knot_cell["left_boundary"] == "knot:1",
            "CHILD_CELL_KNOT_BOUNDARY_LOST")
    knot = {
        "source_value": str(knot1),
        "relation": "ZERO" if knot_value == 0 else P.sign_name(knot_value),
        "left_inward_sign": left_knot_cell["sign"],
        "right_inward_sign": right_knot_cell["sign"],
    }
    if knot_value:
        require(left_knot_cell["sign"] == right_knot_cell["sign"] ==
                P.sign_name(knot_value), "NONZERO_KNOT_SIGN_TRANSFER_CONTRADICTION")
        left_knot_cell["right_boundary"] = right_knot_cell["right_boundary"]
        left_knot_cell["children"].extend(right_knot_cell["children"])
        del cells[first_cell_count]
        knot["source_root"] = False
    else:
        lm = P.EE.multiplicity_at(p0, Q(1))
        rm = P.EE.multiplicity_at(p1, Q(0))
        require(lm > 0 and rm > 0, "ZERO_KNOT_WITHOUT_SIDED_MULTIPLICITY")
        knot.update({
            "source_root": True, "left_order": lm, "right_order": rm,
            "event_kind": (
                "CROSSING" if left_knot_cell["sign"] != right_knot_cell["sign"]
                else "TANGENCY_OR_SIDED_TOUCH"
            ),
            "global_analytic_multiplicity_claimed": False,
        })
        records.insert(len(views[0]["ordered_view"]["ordered_open_roots"]), {
            "id": "knot:1", "root_kind": "SIDED_SOURCE_KNOT",
            "source_value": str(knot1),
            "left_order": lm, "right_order": rm,
            "event_kind": knot["event_kind"],
            "left_sign": as_sign(left_knot_cell["sign"]),
            "right_sign": as_sign(right_knot_cell["sign"]),
        })

    require(cells[0]["left_boundary"] == "source:left" and
            cells[-1]["right_boundary"] == "source:right",
            "SOURCE_EXTERIOR_BOUNDARY_LOST")
    # A signed open cell is bounded precisely by the complete ordered event
    # sequence, even if its rational witness only occupies a strict subinterval.
    require(len(cells) == len(records) + 1,
            "MAXIMAL_NONZERO_CELL_CARDINALITY_MISMATCH")
    for i, cell in enumerate(cells):
        require(as_sign(cell["sign"]) in (-1, 1), "CELL_HAS_NONTRUTH_SIGN")
        if i:
            require(cells[i-1]["right_boundary"] == cell["left_boundary"],
                    "SOURCE_ORDERED_CELL_GAP_OR_OVERLAP")
    left_endpoint = views[0]["ordered_view"]["left_endpoint"]
    right_endpoint = views[1]["ordered_view"]["right_endpoint"]
    endpoints = {
        "left": {
            "source_value": str(a), "relation": left_endpoint["relation"],
            "one_sided_order": left_endpoint["multiplicity"],
            "inward_sign": left_endpoint["inward_sign"],
        },
        "right": {
            "source_value": str(b), "relation": right_endpoint["relation"],
            "one_sided_order": right_endpoint["multiplicity"],
            "inward_sign": right_endpoint["inward_sign"],
        },
    }
    require(as_sign(cells[0]["sign"]) == endpoints["left"]["inward_sign"],
            "LEFT_SOURCE_GERM_SIGN_MISMATCH")
    require(as_sign(cells[-1]["sign"]) == endpoints["right"]["inward_sign"],
            "RIGHT_SOURCE_GERM_SIGN_MISMATCH")
    return {
        "source_interval": [str(a), str(b)],
        "source_knot": knot,
        "ordered_source_events": records,
        "maximal_nonzero_cells": cells,
        "exterior_germs": endpoints,
        "interior_source_events": len(records),
        "nonzero_cell_count": len(cells),
        "closed_source_zero_occurrences": (
            len(records) + int(endpoints["left"]["relation"] == "ZERO") +
            int(endpoints["right"]["relation"] == "ZERO")
        ),
        "general_analytic_event_theorem_claimed": False,
    }


def build(spec, *, budget=MAX_CHILD_BISECTIONS):
    """Produces a candidate; validation does NOT trust the builder's verdict."""
    child = P.build_source_candidate(spec, max_bisections=budget)
    if child.get("status") == "RESOURCE_REFUSAL":
        raise Refused("RESOURCE_REFUSAL_NONTRUTH")
    view = compose_checked_child(child, spec)
    return {
        "schema": SCHEMA,
        "status": "BOUNDED_SOURCE_ORDERED_SIGN_TRANSFER_CANDIDATE",
        "source_sha256": source_hash(spec),
        "evidence_class": EVIDENCE_CLASS,
        "child_certificate": child,
        "physical_source": view,
        "pb00701_or_mc_b_discharge_claimed": False,
    }


def validate(candidate, spec):
    require(isinstance(candidate, dict) and candidate.get("schema") == SCHEMA,
            "SUCCESSOR_SCHEMA_INVALID")
    require(candidate.get("status") == "BOUNDED_SOURCE_ORDERED_SIGN_TRANSFER_CANDIDATE",
            "SUCCESSOR_STATUS_NOT_CANDIDATE")
    require(candidate.get("source_sha256") == source_hash(spec),
            "ORIGINAL_SOURCE_HASH_MISMATCH")
    require(candidate.get("evidence_class") == EVIDENCE_CLASS and
            candidate.get("pb00701_or_mc_b_discharge_claimed") is False,
            "ILLICIT_PROOF_PROMOTION")
    # Independently check submitted child proof, its complete source-origin
    # coverage and every Sturm sign/multiplicity/parity result before transfer.
    child = candidate.get("child_certificate")
    require(isinstance(child, dict), "CHILD_PROOF_MISSING")
    expected = compose_checked_child(child, spec)
    require(candidate.get("physical_source") == expected,
            "PHYSICAL_SOURCE_TRANSFER_MISMATCH")
    return True


def load_baseline():
    corpus = json.loads(read_pinned(CORPUS, CORPUS_BLOB, MAX_BYTES))
    v2 = json.loads(read_pinned(V2, V2_BLOB, 200000))
    cases = corpus["cases"]
    require(len(cases) == 121 and len({x["id"] for x in cases}) == 121,
            "FROZEN_121_SOURCE_POPULATION_CHANGED")
    dispositions = Counter(x["expected"]["v54_disposition"] for x in cases)
    require(dispositions["BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30
            and dispositions["BLOCKED"] == 20, "V54_HISTORICAL_DENOMINATOR_CHANGED")
    require(len(v2["source_cases"]) == 50, "FROZEN_V2_WITNESS_DENOMINATOR_CHANGED")
    require(set(SOURCE_SHA256) <= {x["id"] for x in cases},
            "SELECTED_ORIGINAL_SOURCE_MISSING")
    return cases, v2


def source_case_outputs():
    cases, v2 = load_baseline()
    originals = {x["id"]: x for x in cases}
    outputs = []
    for case_id, pinned_sha in SOURCE_SHA256.items():
        case = originals[case_id]
        require(case["expected"]["v54_disposition"] ==
                "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE",
                "SELECTED_CASE_NOT_HISTORICALLY_ORDER_BLOCKED")
        require(source_hash(case["spec"]) == pinned_sha,
                "SELECTED_ORIGINAL_SOURCE_IDENTITY_DRIFT")
        cert = build(case["spec"])
        validate(cert, case["spec"])
        parent = cert["physical_source"]
        require(parent["source_interval"] == ["0", "2"] and
                parent["source_knot"]["source_value"] == "1" and
                parent["source_knot"]["relation"] == "POSITIVE",
                "HISTORICAL_SOURCE_SPAN_OR_KNOT_MISMATCH")
        require(parent["closed_source_zero_occurrences"] == 1 and
                parent["ordered_source_events"][0].get("source_value") == "1/2" and
                parent["ordered_source_events"][0]["multiplicity"] == 1 and
                parent["ordered_source_events"][0]["event_kind"] == "CROSSING",
                "HISTORICAL_SOURCE_ROOT_OR_MULTIPLICITY_MISMATCH")
        require([x["sign"] for x in parent["maximal_nonzero_cells"]] ==
                ["NEGATIVE", "POSITIVE"], "HISTORICAL_SIGN_CELL_MISMATCH")
        require(cert["child_certificate"]["historical_span_count"] == 2,
                "HISTORICAL_CHILD_COVERAGE_MISSING")
        outputs.append({
            "case_id": case_id, "source_sha256": pinned_sha,
            "historical_v54_disposition": case["expected"]["v54_disposition"],
            "successor_candidate": "BOUNDED_SOURCE_ORDERED_SIGN_TRANSFER_CANDIDATE",
            "physical": parent,
        })
    require(set(x["case_id"] for x in v2["source_cases"]).issuperset(SOURCE_SHA256),
            "EXISTING_SOURCE_SPECIFIC_WITNESSES_NOT_PRESERVED")
    receipt = {
        "schema": SCHEMA,
        "evidence_class": EVIDENCE_CLASS,
        "frozen_v54_corpus_git_blob": CORPUS_BLOB,
        "frozen_v2_registry_git_blob": V2_BLOB,
        "stationary_child_verifier_git_blob": CHILD_BLOB,
        "case_results": outputs,
        "matched_census": {
            "frozen_original_source_count": 121,
            "historical_v54_refusals_before": 20,
            "historical_v54_missing_ordered_before": 30,
            "complete_preexisting_v2_source_witnesses": 50,
            "successor_candidate_newly_ordered_ids": sorted(SOURCE_SHA256),
            "successor_candidate_missing_ordered_after": 28,
            "successor_candidate_route_refusals_after": 20,
            "frozen_v54_dispositions_modified": False,
            "required_pb007_obligations_discharged": 0,
            "mc_b_or_mc1_accepted": False,
        },
    }
    return receipt


def expect_refusal(func):
    try:
        func()
    except (Refused, ValueError):
        return
    raise AssertionError("adversarial candidate was incorrectly admitted")


def synthetic(spec, first, second, *, degree=1):
    """Make a two-piece, source-time-preserving synthetic control mutation."""
    spec = deepcopy(spec)
    if degree == 1:
        spec["cos_splines"]["1"]["controls"] = list(first) + list(second)
    else:
        spec["cos_splines"]["1"] = {
            "degree": 2,
            "knots": ["0", "0", "0", "1", "1", "1", "2", "2", "2"],
            "controls": list(first) + list(second),
        }
    return spec


def self_test():
    cases, _ = load_baseline()
    base = next(x["spec"] for x in cases if x["id"].endswith(
        "EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0"))
    a = build(base)
    assert validate(a, base)
    # Mutation controls challenge parent sign, root, knot, source identity,
    # child proof and inadmissible claimed gate promotion.
    for key, value in [
        ("source_sha256", "0" * 64),
        ("status", "CAPABILITY_ACCEPTED"),
        ("pb00701_or_mc_b_discharge_claimed", True),
    ]:
        bad = deepcopy(a)
        bad[key] = value
        expect_refusal(lambda bad=bad: validate(bad, base))
    for field, value in [
        ("nonzero_cell_count", 0),
        ("closed_source_zero_occurrences", 0),
        ("source_interval", ["0", "1"]),
    ]:
        bad = deepcopy(a)
        bad["physical_source"][field] = value
        expect_refusal(lambda bad=bad: validate(bad, base))
    bad = deepcopy(a)
    bad["physical_source"]["source_knot"]["relation"] = "ZERO"
    expect_refusal(lambda: validate(bad, base))
    bad = deepcopy(a)
    bad["physical_source"]["ordered_source_events"][0]["multiplicity"] = 2
    expect_refusal(lambda: validate(bad, base))
    bad = deepcopy(a)
    bad["physical_source"]["maximal_nonzero_cells"][0]["sign"] = "POSITIVE"
    expect_refusal(lambda: validate(bad, base))
    bad = deepcopy(a)
    bad["child_certificate"]["views"][0]["ordered_view"]["summary"]["distinct_roots_open"] = 0
    expect_refusal(lambda: validate(bad, base))

    # Actual rational near-knot crossing, separated by 2^-120 in controls:
    # Sturm must not use an epsilon, scan or falsely merge into the knot.
    delta = str(Q(1, 2**120))
    near = synthetic(base, ["-1", delta], [delta, delta])
    near_cert = build(near)
    assert validate(near_cert, near)
    event = near_cert["physical_source"]["ordered_source_events"][0]
    expected_root = Q(1) / (Q(1) + Q(delta))
    if event["root_kind"] == "RATIONAL_ROOT":
        assert Q(event["source_value"]) == expected_root
    else:
        # A rational zero may validly be encoded as a unique algebraic
        # isolator when the bisection never lands on that rational point.
        left, right = map(Q, event["source_isolating_interval"])
        assert left < expected_root < right
        assert P.EE.peval(P.source_stationary_spans(near)[0]["polynomial"],
                          expected_root) == 0
    assert near_cert["physical_source"]["source_knot"]["relation"] == "POSITIVE"

    # At the true original knot, both sided orders must be retained;
    # there is deliberately no invented global analytic multiplicity.
    crossing = synthetic(base, ["-1", "0"], ["0", "1"])
    x = build(crossing)
    assert validate(x, crossing)
    assert x["physical_source"]["source_knot"]["event_kind"] == "CROSSING"
    assert x["physical_source"]["source_knot"]["left_order"] == 1
    assert x["physical_source"]["source_knot"]["right_order"] == 1
    assert x["physical_source"]["nonzero_cell_count"] == 2

    touching = synthetic(base, ["1", "0"], ["0", "1"])
    t = build(touching)
    assert validate(t, touching)
    assert t["physical_source"]["source_knot"]["event_kind"] == "TANGENCY_OR_SIDED_TOUCH"
    assert t["physical_source"]["nonzero_cell_count"] == 2

    # Repeated/tangential interior roots on two quadratic original pieces.
    tangency = synthetic(base, ["1/4", "-1/4", "1/4"],
                        ["1/4", "-1/4", "1/4"], degree=2)
    tc = build(tangency)
    assert validate(tc, tangency)
    assert [r["multiplicity"] for r in tc["physical_source"]["ordered_source_events"]] == [2, 2]
    assert [r["event_kind"] for r in tc["physical_source"]["ordered_source_events"]] == [
        "TANGENCY", "TANGENCY"]
    assert tc["physical_source"]["nonzero_cell_count"] == 3

    identity = synthetic(base, ["-1", "0"], ["0", "0"])
    expect_refusal(lambda: build(identity))
    discontinuity = synthetic(base, ["-1", "1/2"], ["3/4", "3/4"])
    expect_refusal(lambda: build(discontinuity))
    invalid_phase = deepcopy(base)
    invalid_phase["phase_turn_rate"] = "1/8"
    expect_refusal(lambda: build(invalid_phase))
    expect_refusal(lambda: build(base, budget=0))
    # No historical failure or source witness is ever rewritten by the test.
    receipt = source_case_outputs()
    assert len(receipt["case_results"]) == 2
    assert receipt["matched_census"]["successor_candidate_missing_ordered_after"] == 28
    print("PASS: two frozen originals, full source/knot/sign order and adversarial controls")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        receipt = source_case_outputs()
        if args.contract:
            expected = json.loads(read_pinned(RECEIPT, RECEIPT_BLOB, 20000))
            require(receipt == expected, "MACHINE_RECEIPT_REPLAY_MISMATCH")
        if args.report:
            print(json.dumps(receipt, indent=2, sort_keys=True))
        elif not args.self_test:
            print("PASS: bounded source order candidate, frozen-v54 population preserved")
    except (Refused, ValueError, OSError, MemoryError, RecursionError, OverflowError) as exc:
        print("REFUSED: " + str(exc), file=sys.stderr)
        raise SystemExit(1)


# The receipt is separately checked by exact content, not permitted to
# establish truth without source replay. Filled at candidate publication.
RECEIPT_BLOB = "d7ee51ed09bc317f29177286dbd9b1e827c8bd10"


if __name__ == "__main__":
    main()
