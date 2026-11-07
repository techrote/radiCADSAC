#!/usr/bin/env python3
"""Exact octant-node, exterior and restricted same-law knot event transfer.

Research-only deterministic model. Extends the separately qualified constant-H0/H1
octant span theorem without changing its root-count decisions or production gates.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
import unittest

import pb00701_constant_h0_h1_octant_20261106 as base

V6_ID = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0"
V6_SHA = "9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1"
V6_ROW = "145ac5ce5b533c447c7356e8dc721dbfa5a44562cdc3a37422278fd7bd0199fc"
KEYS = {"source_parameter_id", "parameter_lo", "parameter_hi", "h0",
        "h1_cos", "h1_sin", "phase_turn_offset", "phase_turn_rate"}


def sided_sign(f, derivative, h, direction):
    """Exact sign on the open source-time side of a physical octant node.

    If F=0 and F'=0, F''=(2*pi*rate)^2*h is nonzero because q>0.
    """
    base.require(direction in (-1, 1), "SIDED_DIRECTION")
    if f:
        return f
    if derivative:
        return direction * derivative
    base.require(h != 0, "DEGENERATE_NODE_ZERO")
    return base.sgn(h)


def node_event(time, derivative):
    return {"exact_source_time": str(time),
            "multiplicity": 1 if derivative else 2,
            "event_kind": "SIMPLE_CROSSING" if derivative else "TANGENCY"}


def certify_nodes(spec):
    base.require(type(spec) is dict and set(spec) == KEYS, "SOURCE_FIELDS")
    base.require(spec["source_parameter_id"] == "source-time-t", "SOURCE_PARAMETER")
    lo, hi = base.rat(spec["parameter_lo"]), base.rat(spec["parameter_hi"])
    h, c, s = (base.rat(spec[k]) for k in ("h0", "h1_cos", "h1_sin"))
    off, rate = (base.rat(spec[k]) for k in
                 ("phase_turn_offset", "phase_turn_rate"))
    base.require(Q(0) <= lo < hi <= Q(2) and rate != 0 and abs(rate) <= 4,
                 "DOMAIN_OR_NONSTATIONARY_PHASE")
    q = c*c + s*s
    base.budget(q)
    base.require(q > 0, "ZERO_H1_VECTOR")
    x0, x1 = 8*(off + rate*lo), 8*(off + rate*hi)
    base.require(x0.denominator == x1.denominator == 1,
                 "NONOCTANT_EXTERIOR")
    count = abs(int(x1-x0))
    base.require(0 < count <= 128, "OCTANT_CELL_BUDGET")
    direction = base.sgn(rate)
    ks = [int(x0) + i*direction for i in range(count+1)]
    times = [(Q(k,8)-off)/rate for k in ks]
    base.require(times[0] == lo and times[-1] == hi and
                 all(a < b for a,b in zip(times, times[1:])),
                 "SOURCE_NODE_ORDER")
    values, derivatives = zip(
        *(base.endpoint_signs(h, c, s, rate, k) for k in ks))
    left_boundary = node_event(lo, derivatives[0]) if values[0] == 0 else None
    right_boundary = (node_event(hi, derivatives[-1])
                      if values[-1] == 0 else None)

    current = sided_sign(values[0], derivatives[0], h, 1)
    regions = ["POSITIVE" if current > 0 else "NEGATIVE"]
    events, cell_details = [], []

    for i in range(count):
        before = sided_sign(values[i], derivatives[i], h, 1)
        after = sided_sign(values[i+1], derivatives[i+1], h, -1)
        base.require(current == before, "LEFT_SIDED_SIGN_CONTRADICTION")
        interior_count, order, method = base.cell_count(
            before, after, derivatives[i], derivatives[i+1], h, q)
        if interior_count:
            events.append({
                "strict_open_rational_bracket": [str(times[i]), str(times[i+1])],
                "multiplicity": order,
                "event_kind": "TANGENCY" if order == 2 else "SIMPLE_CROSSING"})
            if order == 1:
                current = -current
            regions.append("POSITIVE" if current > 0 else "NEGATIVE")
        base.require(current == after, "RIGHT_SIDED_SIGN_CONTRADICTION")
        cell_details.append({
            "source_time_cell": [str(times[i]), str(times[i+1])],
            "sided_signs": [before, after],
            "endpoint_values": [values[i], values[i+1]],
            "derivative_signs": [derivatives[i], derivatives[i+1]],
            "interior_root_count": interior_count, "method": method})
        if i+1 < count and values[i+1] == 0:
            # The same zero belongs to *neither* neighboring open cell;
            # emit it once here, after the cell on its physical left.
            events.append(node_event(times[i+1], derivatives[i+1]))
            if derivatives[i+1]:
                current = -current
            base.require(
                current == sided_sign(values[i+1], derivatives[i+1], h, 1),
                "NODE_SIDED_SIGN_CONTRADICTION")
            regions.append("POSITIVE" if current > 0 else "NEGATIVE")

    base.require(len(events) + 1 == len(regions),
                 "EVENT_REGION_CARDINALITY")
    return {
        "status": "COMPLETE_RESTRICTED_H0H1_OCTANT_NODE_SPAN",
        "evidence_class": "DETERMINISTIC_MODEL",
        "span_spec_sha256": hashlib.sha256(base.canonical(spec)).hexdigest(),
        "octant_nodes": [str(t) for t in times],
        "node_value_signs": list(values),
        "node_derivative_signs": list(derivatives),
        "left_boundary_event": left_boundary,
        "right_boundary_event": right_boundary,
        "ordered_interior_events": events,
        "ordered_signed_open_regions": regions,
        "interior_root_count": len(events),
        "cell_certificates": cell_details,
        "new_historical_closures": [],
        "required_pb_po_discharges": 0,
        "pb00701_established": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False}


def certify_identical_law_knot(left, right):
    """Compose ONLY two consecutive spans of literally the same phase/H0/H1 law.

    Different coefficients or phase functions, including continuous piecewise
    functions, need a separate knot-sided continuity and order theorem.
    """
    base.require(type(left) is dict and type(right) is dict and
                 set(left) == set(right) == KEYS, "SPLIT_SOURCE_FIELDS")
    for key in KEYS - {"parameter_lo", "parameter_hi"}:
        base.require(left[key] == right[key], "DIFFERENT_LAW_AT_KNOT")
    base.require(base.rat(left["parameter_hi"]) ==
                 base.rat(right["parameter_lo"]), "NONADJACENT_KNOT")
    a, b = certify_nodes(left), certify_nodes(right)
    base.require(a["right_boundary_event"] == b["left_boundary_event"],
                 "KNOT_EVENT_MISMATCH")
    seam = a["right_boundary_event"]
    if seam is None:
        base.require(a["ordered_signed_open_regions"][-1] ==
                     b["ordered_signed_open_regions"][0],
                     "KNOT_SIGN_DISCONTINUITY")
    else:
        la = a["ordered_signed_open_regions"][-1]
        rb = b["ordered_signed_open_regions"][0]
        base.require((la != rb) == (seam["multiplicity"] == 1),
                     "KNOT_SIDED_SIGN_CONTRADICTION")

    whole = certify_nodes({**left, "parameter_hi": right["parameter_hi"]})
    expected_events = (a["ordered_interior_events"] +
                       ([seam] if seam else []) +
                       b["ordered_interior_events"])
    expected_regions = (a["ordered_signed_open_regions"] +
                        (b["ordered_signed_open_regions"] if seam else
                         b["ordered_signed_open_regions"][1:]))
    base.require(whole["ordered_interior_events"] == expected_events and
                 whole["ordered_signed_open_regions"] == expected_regions,
                 "SOURCE_COMPOSITION_CONTRADICTION")
    # Matching laws and adjacent intervals prove a mathematical join, NOT an
    # original B-spline knot. A caller can fabricate an octant-aligned split.
    # Only a separate hash-pinned source/knot witness may upgrade this label.
    whole["status"] = "COMPLETE_RESTRICTED_SAME_LAW_TWO_SPAN_JOIN"
    whole["unverified_same_law_join"] = left["parameter_hi"]
    whole["constituent_span_sha256"] = [
        a["span_spec_sha256"], b["span_spec_sha256"]]
    return whole


def attempted(fn, *args):
    try:
        return fn(*args)
    except (base.Refusal, ValueError, TypeError, IndexError, KeyError,
            OverflowError, ZeroDivisionError, RecursionError, MemoryError) as e:
        return {"status": "REFUSED_NONTRUTH", "reason": str(e)}


def original_v6_contract():
    rows = base.checked_json(base.CORPUS, base.V54_BLOB)["cases"]
    v2 = base.checked_json(base.V2, base.V2_BLOB)["source_cases"]
    base.require(len(rows) == 121 and len(v2) == 50, "FROZEN_CENSUS")
    r = next(x for x in rows if x["id"] == V6_ID)
    e = next(x for x in v2 if x["case_id"] == V6_ID)
    s = r["spec"]
    base.require(
        hashlib.sha256(base.canonical(s)).hexdigest() == V6_SHA and
        hashlib.sha256(base.canonical(r)).hexdigest() == V6_ROW and
        e["source_sha256"] == V6_SHA and
        e["evidence"]["original_row_sha256"] == V6_ROW and
        e["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC",
        "ORIGINAL_V6_PROVENANCE")
    base.require(s == {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0", "parameter_hi": "2",
        "phase_turn_offset": "0", "phase_turn_rate": "1/4",
        "cos_splines": {
            "0": {"degree": 0, "knots": ["0","1","2"],
                  "controls": ["0","0"]},
            "1": {"degree": 0, "knots": ["0","1","2"],
                  "controls": ["1","1"]}},
        "sin_splines": {}}, "NOT_IDENTICAL_CONSTANT_ORIGINAL_SPANS")
    # Extraction is admissible only after exact original spline custody
    # verifies both adjacent degree-0 spans have identical coefficients.
    a = base.source(h="0", c="1", s="0", off="0", rate="1/4",
                    lo="0", hi="1")
    b = {**a, "parameter_lo": "1", "parameter_hi": "2"}
    result = certify_identical_law_knot(a, b)
    # The exact frozen original spec above proves the true degree-zero
    # B-spline knot is 1. The generic same-law join alone does not.
    base.require(result["unverified_same_law_join"] == "1",
                 "V6_TRUE_KNOT_IDENTITY")
    result["true_source_knot"] = "1"
    result["status"] = "COMPLETE_RESTRICTED_SAME_LAW_TWO_SPAN_KNOT"
    result["verified_original_source_sha256"] = V6_SHA
    result["verified_original_row_sha256"] = V6_ROW
    base.require(
        result["ordered_interior_events"] == [{
            "exact_source_time": "1", "multiplicity": 1,
            "event_kind": "SIMPLE_CROSSING"}] and
        result["ordered_signed_open_regions"] ==
        ["POSITIVE", "NEGATIVE"] and
        result["interior_root_count"] == 1 and
        result["left_boundary_event"] is None and
        result["right_boundary_event"] is None,
        "V6_ORIGINAL_KNOT_EVENT_CONTRADICTION")
    return {"frozen_original": V6_ID, "v54_git_blob": base.V54_BLOB,
            "v2_git_blob": base.V2_BLOB, "original_source_sha256": V6_SHA,
            "original_row_sha256": V6_ROW, "original_v2_prior_art": True,
            "same_law_two_span_certificate": result,
            "historical_before_after": {"originals": 121, "route_refusals": 20,
                                        "missing_ordered": 30, "v2_complete": 50},
            "historical_delta": {"originals": 0, "route_refusals": 0,
                                 "missing_ordered": 0, "v2_complete": 0},
            "new_historical_closures": [], "required_pb_po_discharges": 0,
            "mc_b_established": False, "mc1_established": False}


class Tests(unittest.TestCase):
    def test_full_original_v6_true_knot_simple_crossing(self):
        out = original_v6_contract()["same_law_two_span_certificate"]
        self.assertEqual(out["ordered_interior_events"][0]["exact_source_time"], "1")
        self.assertEqual(out["ordered_signed_open_regions"], ["POSITIVE","NEGATIVE"])

    def test_fabricated_original_v6_law_splits_are_not_true_knots(self):
        # V6 original B-spline knots [0,1,2] are verified in the separate
        # original_v6_contract() custody check. Neither 1/2 nor 3/2 is a
        # genuine knot, although both are valid octant-aligned time cuts.
        original = original_v6_contract()["same_law_two_span_certificate"]
        self.assertEqual(original["true_source_knot"], "1")
        self.assertEqual(original["verified_original_source_sha256"], V6_SHA)
        self.assertEqual(original["verified_original_row_sha256"], V6_ROW)
        self.assertEqual(original["ordered_interior_events"], [{
            "exact_source_time": "1", "multiplicity": 1,
            "event_kind": "SIMPLE_CROSSING"}])
        for fake in ("1/2", "3/2"):
            a = base.source(h="0", c="1", s="0", off="0",
                            rate="1/4", lo="0", hi=fake)
            b = {**a, "parameter_lo": fake, "parameter_hi": "2"}
            unverified = certify_identical_law_knot(a, b)
            self.assertEqual(unverified["status"],
                             "COMPLETE_RESTRICTED_SAME_LAW_TWO_SPAN_JOIN")
            self.assertEqual(unverified["unverified_same_law_join"], fake)
            self.assertNotIn("true_source_knot", unverified)
            self.assertNotIn("verified_original_source_sha256", unverified)
            self.assertEqual(unverified["ordered_interior_events"],
                             original["ordered_interior_events"])
            self.assertEqual(unverified["ordered_signed_open_regions"],
                             ["POSITIVE", "NEGATIVE"])
        rows = base.checked_json(base.CORPUS, base.V54_BLOB)["cases"]
        source_spec = next(r["spec"] for r in rows if r["id"] == V6_ID)
        self.assertTrue(all(fake not in src["knots"]
                            for src in source_spec["cos_splines"].values()
                            for fake in ("1/2", "3/2")))

    def test_simple_zero_at_left_endpoint_has_one_interior_region(self):
        out = certify_nodes(base.source(h="0",c="1",s="0",off="0",
                                         rate="1/4",lo="1",hi="2"))
        self.assertEqual(out["left_boundary_event"]["multiplicity"], 1)
        self.assertIsNone(out["right_boundary_event"])
        self.assertEqual(out["interior_root_count"], 0)
        self.assertEqual(out["ordered_signed_open_regions"], ["NEGATIVE"])

    def test_simple_zero_at_right_endpoint_has_one_interior_region(self):
        out = certify_nodes(base.source(h="0",c="1",s="0",off="0",
                                         rate="1/4",lo="0",hi="1"))
        self.assertEqual(out["right_boundary_event"]["exact_source_time"], "1")
        self.assertEqual(out["ordered_signed_open_regions"], ["POSITIVE"])
        self.assertEqual(out["interior_root_count"], 0)

    def test_both_exteriors_zero_one_negative_region(self):
        out = certify_nodes(base.source(h="0",c="1",s="0",off="1/4",
                                         rate="1/4",lo="0",hi="2"))
        self.assertEqual(out["interior_root_count"], 0)
        self.assertEqual(out["ordered_signed_open_regions"], ["NEGATIVE"])
        self.assertEqual(out["left_boundary_event"]["multiplicity"], 1)
        self.assertEqual(out["right_boundary_event"]["multiplicity"], 1)

    def test_interior_node_order_two_tangency(self):
        out = certify_nodes(base.source(h="1",c="0",s="-1",off="0",
                                         rate="1/4",lo="0",hi="2"))
        self.assertEqual(out["ordered_interior_events"], [{
            "exact_source_time": "1", "multiplicity": 2,
            "event_kind": "TANGENCY"}])
        self.assertEqual(out["ordered_signed_open_regions"],
                         ["POSITIVE","POSITIVE"])

    def test_boundary_order_two_no_interior_split(self):
        left = certify_nodes(base.source(h="1",c="-1",s="0",off="0",
                                          rate="1/4",lo="0",hi="2"))
        right = certify_nodes(base.source(h="1",c="1",s="0",off="0",
                                           rate="1/4",lo="0",hi="2"))
        self.assertEqual(left["left_boundary_event"]["multiplicity"], 2)
        self.assertEqual(right["right_boundary_event"]["multiplicity"], 2)
        self.assertEqual(left["ordered_signed_open_regions"], ["POSITIVE"])
        self.assertEqual(right["ordered_signed_open_regions"], ["POSITIVE"])

    def test_negative_phase_rate_interior_node_crossing(self):
        out = certify_nodes(base.source(h="0",c="1",s="0",off="1/2",
                                         rate="-1/4",lo="0",hi="2"))
        self.assertEqual(out["ordered_interior_events"][0]["exact_source_time"], "1")
        self.assertEqual(out["ordered_signed_open_regions"],
                         ["NEGATIVE","POSITIVE"])

    def test_original_v12_root_free_tail_unchanged(self):
        out = certify_nodes(base.source(h="0",c="2/3",s="-1/3",
                                         off="0",rate="1/4",lo="1",hi="2"))
        self.assertEqual(out["ordered_interior_events"], [])
        self.assertEqual(out["ordered_signed_open_regions"], ["NEGATIVE"])

    def test_unbracketed_same_octant_two_roots_still_refuse(self):
        x = base.source(h="199/200",c="-3/5",s="-4/5",
                        off="1/8",rate="1/8",lo="0",hi="1")
        self.assertEqual(attempted(certify_nodes,x)["reason"],
                         "TWO_ROOTS_SAME_OCTANT_UNBRACKETED")

    def test_split_mismatched_law_refuses(self):
        a = base.source(h="0",c="1",s="0",off="0",rate="1/4",lo="0",hi="1")
        b = {**a, "parameter_lo":"1", "parameter_hi":"2", "h0":"1"}
        self.assertEqual(attempted(certify_identical_law_knot,a,b)["reason"],
                         "DIFFERENT_LAW_AT_KNOT")
        self.assertEqual(attempted(certify_identical_law_knot,a,
                          {**b,"h0":"0","parameter_lo":"3/2"})["reason"],
                         "NONADJACENT_KNOT")

    def test_nonzero_node_derivative_not_mistaken_for_root(self):
        out = certify_nodes(base.source(h="0",c="1",s="0",off="0",
                                         rate="1/8",lo="0",hi="1"))
        self.assertEqual(out["interior_root_count"], 0)
        self.assertEqual(out["ordered_signed_open_regions"], ["POSITIVE"])

    def test_parent_legacy_strict_node_refusal_preserved(self):
        x = base.source(h="0",c="1",s="0",off="0",rate="1/4",lo="0",hi="2")
        self.assertEqual(base.attempt(x)["reason"], "PHYSICAL_OCTANT_NODE_ZERO")
        self.assertEqual(certify_nodes(x)["interior_root_count"], 1)

    def test_exact_near_endpoint_not_rounded_to_node(self):
        e = Q(1, 2**300)
        x = base.source(h=str(-Q(1)+e),c="1",s="0",
                        off="0",rate="1/8",lo="0",hi="1")
        out = certify_nodes(x)
        self.assertEqual(out["node_value_signs"][0], 1)
        self.assertEqual(out["ordered_interior_events"], [{
            "strict_open_rational_bracket": ["0","1"],
            "multiplicity": 1, "event_kind": "SIMPLE_CROSSING"}])
        self.assertEqual(out["ordered_signed_open_regions"],
                         ["POSITIVE","NEGATIVE"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.contract:
        print(json.dumps(original_v6_contract(), indent=2, sort_keys=True))
    if args.self_test:
        run = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        if not run.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
