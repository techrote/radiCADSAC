#!/usr/bin/env python3
"""Compose exact constant-H0/H1 octant cells with supplied two-root pivot witnesses.

MC-038/PB-007-01. Research-only deterministic model. The two admitted parent
proof implementations are imported unchanged. No original-source, PB/PO, MC-B,
MC-1, native, STEP or production qualification is implied.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import pb00701_constant_h0_h1_octant_20261106 as octant
import pb00701_octant_two_root_witness_20261109 as witness

HERE = Path(__file__).resolve().parent
SCHEMA = "radicadsac-pb00701-octant-pivot-composition/1.0"
FIELDS = {"source_parameter_id", "parameter_lo", "parameter_hi",
          "h0", "h1_cos", "h1_sin", "phase_turn_offset", "phase_turn_rate"}


class RefusedNontruth(ValueError):
    """A source, pivot, nested certificate or claim is not admitted."""


def require(ok, reason):
    if not ok:
        raise RefusedNontruth(reason)


def name(sign):
    require(sign in (-1, 1), "NONSTRICT_PHYSICAL_SIGN")
    return "POSITIVE" if sign > 0 else "NEGATIVE"


def source(h="199/200", c="-3/5", s="-4/5", off="1/8",
           rate="1/8", lo="0", hi="1"):
    return {"source_parameter_id": "source-time-t",
            "parameter_lo": lo, "parameter_hi": hi,
            "h0": h, "h1_cos": c, "h1_sin": s,
            "phase_turn_offset": off, "phase_turn_rate": rate}


def parse_source(spec):
    require(type(spec) is dict and set(spec) == FIELDS, "SOURCE_FIELDS")
    require(spec["source_parameter_id"] == "source-time-t", "SOURCE_PARAMETER")
    lo, hi = octant.rat(spec["parameter_lo"]), octant.rat(spec["parameter_hi"])
    h, c, s = [octant.rat(spec[k]) for k in ("h0", "h1_cos", "h1_sin")]
    off, rate = [octant.rat(spec[k]) for k in
                 ("phase_turn_offset", "phase_turn_rate")]
    require(Q(0) <= lo < hi <= Q(2) and rate != 0 and abs(rate) <= 4,
            "DOMAIN_OR_NONSTATIONARY_PHASE")
    q = c*c + s*s
    octant.budget(q)
    require(q > 0, "ZERO_H1_VECTOR")
    start, end = 8*(off + rate*lo), 8*(off + rate*hi)
    require(start.denominator == end.denominator == 1,
            "NONOCTANT_EXTERIOR")
    n = abs(int(end-start))
    require(0 < n <= 128, "OCTANT_CELL_BUDGET")
    step = octant.sgn(rate)
    indices = [int(start)+step*i for i in range(n+1)]
    nodes = [(Q(k, 8)-off)/rate for k in indices]
    require(nodes[0] == lo and nodes[-1] == hi and
            all(nodes[i] < nodes[i+1] for i in range(n)),
            "SOURCE_NODE_ORDER")
    return h, c, s, off, rate, indices, nodes


def certify(spec, pivots):
    """Compose complete ordered open physical regions with *no* guessed zeros.

    For each one-octant cell, replay the #445 theorem unmodified. Fallback is
    permitted *only* for its exact TWO_ROOTS_SAME_OCTANT_UNBRACKETED refusal,
    and then only after #464 independently supplies two strict rational root
    brackets. Any other refusal propagates. Every proof remains in the receipt.
    """
    h, c, s, off, rate, indices, nodes = parse_source(spec)
    require(type(pivots) is dict and len(pivots) <= 128, "PIVOT_FIELDS")
    for key, val in pivots.items():
        require(type(key) is str and type(val) is str, "PIVOT_TOKEN_TYPE")
        octant.rat(key)
        octant.rat(val)

    cells, events, regions, consumed = [], [], [], set()
    for i in range(len(nodes)-1):
        left, right = nodes[i], nodes[i+1]
        key = str(left)
        child_spec = {**spec, "parameter_lo": key,
                      "parameter_hi": str(right)}
        try:
            proof = octant.certify(child_spec)
        except octant.Refusal as exc:
            # Preserve the parent's exact failure *before* inspecting node
            # signs: an actual node zero is its own typed refusal.
            require(str(exc) == "TWO_ROOTS_SAME_OCTANT_UNBRACKETED",
                    "PARENT_REFUSAL:" + str(exc))
            left_sign = name(octant.endpoint_signs(h,c,s,rate,indices[i])[0])
            right_sign = name(octant.endpoint_signs(h,c,s,rate,indices[i+1])[0])
            require(key in pivots, "MISSING_RATIONAL_TWO_ROOT_PIVOT")
            middle = octant.rat(pivots[key])
            require(left < middle < right, "PIVOT_OUTSIDE_CELL")
            proof = witness.certify(h,c,s,off,rate,left,middle,right)
            require(witness.verify_receipt(proof), "INVALID_PIVOT_PROOF")
            require(proof["root_count"] == 2 and
                    proof["root_orders"] == [1,1], "PIVOT_ROOT_CLAIM")
            part_events = [
                {"strict_rational_bracket": interval, "multiplicity": 1,
                 "event_kind": "SIMPLE_CROSSING"}
                for interval in proof["strict_rational_root_brackets"]]
            part_regions = proof["ordered_signed_regions"]
            require(part_regions == [left_sign,
                                    "NEGATIVE" if left_sign == "POSITIVE"
                                    else "POSITIVE", right_sign] and
                    left_sign == right_sign, "PIVOT_SIGN_TRANSFER")
            require(proof["point_interval_proofs"]["left"]["sign"] == left_sign and
                    proof["point_interval_proofs"]["right"]["sign"] == right_sign,
                    "PIVOT_ENDPOINT_PROOF_MISMATCH")
            kind = "TWO_SIMPLE_ROOTS_WITH_EXACT_PIVOT"
            consumed.add(key)
        else:
            left_sign = name(octant.endpoint_signs(h,c,s,rate,indices[i])[0])
            right_sign = name(octant.endpoint_signs(h,c,s,rate,indices[i+1])[0])
            require(key not in pivots, "UNNEEDED_PIVOT_FOR_ADMITTED_CELL")
            require(proof["root_count"] == len(proof["ordered_events"]) and
                    proof["node_signs"] == [left_sign,right_sign] and
                    len(proof["cell_certificates"]) == 1,
                    "PARENT_CELL_CUSTODY")
            part_events = proof["ordered_events"]
            part_regions = proof["ordered_signed_regions"]
            kind = "EXACT_PARENT_OCTANT"
        require(len(part_regions) == len(part_events)+1 and
                part_regions[0] == left_sign and part_regions[-1] == right_sign,
                "CHILD_EVENT_REGION_INCONSISTENT")
        for event in part_events:
            low, high = (octant.rat(v) for v in
                         event["strict_rational_bracket"])
            require(left <= low < high <= right, "CHILD_BRACKET_ESCAPED")
            require(event["event_kind"] ==
                    ("TANGENCY" if event["multiplicity"] == 2 else
                     "SIMPLE_CROSSING"), "CHILD_EVENT_KIND")
            require(event["multiplicity"] in (1,2), "CHILD_MULTIPLICITY")
            if events:
                previous_hi = octant.rat(
                    events[-1]["strict_rational_bracket"][1])
                require(previous_hi <= low, "EVENT_BRACKET_ORDER")
            events.append(event)
        if regions:
            require(regions[-1] == part_regions[0],
                    "OCTANT_SOURCE_SIGN_MISMATCH")
            regions.extend(part_regions[1:])
        else:
            regions.extend(part_regions)
        cells.append({"source_cell": [str(left),str(right)],
                      "kind": kind, "certificate": proof})
    require(consumed == set(pivots), "UNUSED_RATIONAL_PIVOT")
    require(len(regions) == len(events)+1, "EVENT_PARTITION_LENGTH")
    return {
        "schema": SCHEMA,
        "status": "COMPLETE_RESTRICTED_CONSTANT_H0_H1_PIVOT_COMPOSED_SPAN",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_spec": spec,
        "source_spec_sha256": hashlib.sha256(octant.canonical(spec)).hexdigest(),
        "supplied_rational_pivots": pivots,
        "octant_nodes": [str(t) for t in nodes],
        "certified_cells": cells,
        "ordered_events": events,
        "ordered_signed_regions": regions,
        "root_count": len(events),
        "new_historical_closures": [],
        "required_pb_po_discharges": 0,
        "pb00701_established": False,
        "mc_b_established": False,
        "mc1_established": False,
        "production_authorized": False,
    }


def verify_receipt(receipt):
    """Source-replay all child proofs and reject any substituted outer claim.

    This is proof-integrity replay using the parent implementations; it is NOT
    an independent mathematical oracle.
    """
    require(type(receipt) is dict and type(receipt.get("source_spec")) is dict
            and type(receipt.get("supplied_rational_pivots")) is dict,
            "RECEIPT_SHAPE")
    try:
        expected = certify(receipt["source_spec"],
                           receipt["supplied_rational_pivots"])
    except (RefusedNontruth, octant.Refusal, witness.RefusedNontruth,
            ValueError, TypeError, KeyError, IndexError, OverflowError,
            RecursionError, ZeroDivisionError, MemoryError) as exc:
        raise RefusedNontruth("RECEIPT_REPLAY_REFUSED:" + str(exc)) from exc
    try:
        actual_json = json.dumps(receipt, sort_keys=True,
                                 separators=(",", ":"), allow_nan=False)
        expected_json = json.dumps(expected, sort_keys=True,
                                   separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise RefusedNontruth("RECEIPT_NOT_CANONICAL_JSON") from exc
    require(actual_json == expected_json, "RECEIPT_CLAIM_SUBSTITUTION")
    return True


def attempt(spec, pivots):
    try:
        return certify(spec, pivots)
    except (RefusedNontruth, octant.Refusal, witness.RefusedNontruth,
            ValueError, TypeError, IndexError, KeyError, OverflowError,
            ZeroDivisionError, RecursionError, MemoryError) as exc:
        return {"status": "REFUSED_NONTRUTH", "reason": str(exc),
                "pb00701_established": False,
                "mc1_established": False}


class Tests(unittest.TestCase):
    def test_single_same_octant_two_simple_roots(self):
        out = certify(source(), {"0":"1/4"})
        self.assertEqual((out["root_count"], out["ordered_signed_regions"]),
                         (2, ["POSITIVE","NEGATIVE","POSITIVE"]))
        self.assertEqual([x["strict_rational_bracket"] for x in
                          out["ordered_events"]],
                         [["0","1/4"],["1/4","1"]])
        self.assertEqual(out["certified_cells"][0]["kind"],
                         "TWO_SIMPLE_ROOTS_WITH_EXACT_PIVOT")
        self.assertTrue(verify_receipt(out))

    def test_two_octants_share_only_nonzero_boundary(self):
        out = certify(source(hi="2"), {"0":"1/4"})
        self.assertEqual(out["root_count"], 2)
        self.assertEqual(out["ordered_signed_regions"],
                         ["POSITIVE","NEGATIVE","POSITIVE"])
        self.assertEqual(len(out["certified_cells"]), 2)
        self.assertEqual(out["certified_cells"][1]["kind"],
                         "EXACT_PARENT_OCTANT")
        self.assertEqual(len(out["ordered_signed_regions"]),
                         out["root_count"] + 1)

    def test_two_repeated_cycles_and_two_independent_pivots(self):
        # One physical source with 16 consecutive octants, including two
        # disjoint hidden-root cells one exact whole phase turn apart.
        out = certify(source(rate="1", hi="2"),
                      {"0":"1/32", "1":"33/32"})
        self.assertEqual(len(out["certified_cells"]), 16)
        self.assertEqual(out["root_count"], 4)
        self.assertEqual([x["strict_rational_bracket"] for x in
                          out["ordered_events"]],
                         [["0","1/32"],["1/32","1/8"],
                          ["1","33/32"],["33/32","9/8"]])
        self.assertEqual(out["ordered_signed_regions"],
                         ["POSITIVE","NEGATIVE","POSITIVE",
                          "NEGATIVE","POSITIVE"])
        self.assertEqual(sum(c["kind"] ==
                             "TWO_SIMPLE_ROOTS_WITH_EXACT_PIVOT"
                             for c in out["certified_cells"]), 2)
        self.assertTrue(verify_receipt(out))

    def test_negative_phase_reversal(self):
        out = certify(source(off="1/4",rate="-1/8"), {"0":"3/4"})
        self.assertEqual([x["strict_rational_bracket"] for x in
                          out["ordered_events"]],
                         [["0","3/4"],["3/4","1"]])
        self.assertEqual(out["ordered_signed_regions"],
                         ["POSITIVE","NEGATIVE","POSITIVE"])

    def test_mirrored_maximum(self):
        out = certify(source(h="-199/200",c="3/5",s="4/5"),
                      {"0":"1/4"})
        self.assertEqual(out["ordered_signed_regions"],
                         ["NEGATIVE","POSITIVE","NEGATIVE"])

    def test_exact_tangency_and_root_free_not_split(self):
        tangency = certify(source(h="1",hi="2"), {})
        self.assertEqual((tangency["root_count"],
                          tangency["ordered_events"][0]["multiplicity"]), (1,2))
        self.assertEqual(tangency["ordered_signed_regions"],
                         ["POSITIVE","POSITIVE"])
        empty = certify(source(h="201/200",hi="2"), {})
        self.assertEqual(empty["ordered_signed_regions"], ["POSITIVE"])
        self.assertEqual(empty["root_count"], 0)

    def test_original_v12_tail_event_partition_without_pivots(self):
        historical = source(h="0", c="2/3", s="-1/3", off="0",
                            rate="1/4", lo="1", hi="2")
        out = certify(historical, {})
        self.assertEqual(out["ordered_signed_regions"], ["NEGATIVE"])
        self.assertEqual(out["root_count"], 0)
        original = octant.certify(historical)
        self.assertEqual((out["ordered_events"], out["ordered_signed_regions"]),
                         (original["ordered_events"],
                          original["ordered_signed_regions"]))

    def test_missing_unneeded_or_incorrect_pivot_refused(self):
        self.assertEqual(attempt(source(), {})["reason"],
                         "MISSING_RATIONAL_TWO_ROOT_PIVOT")
        self.assertEqual(attempt(source(), {"0":"1/2"})["status"],
                         "REFUSED_NONTRUTH")
        self.assertEqual(attempt(source(h="1"), {"0":"1/4"})["reason"],
                         "UNNEEDED_PIVOT_FOR_ADMITTED_CELL")
        self.assertEqual(attempt(source(), {"1":"1/4"})["status"],
                         "REFUSED_NONTRUTH")
        self.assertEqual(attempt(source(), {"0":"0"})["reason"],
                         "PIVOT_OUTSIDE_CELL")

    def test_near_coalescence_remains_nontruth_not_zero(self):
        h = str(Q(1)-Q(1,2**300))
        self.assertEqual(attempt(source(h=h), {"0":"1/4"})["status"],
                         "REFUSED_NONTRUTH")

    def test_actual_v6_node_zero_remains_refused(self):
        actual = source(h="0",c="1",s="0",off="0",
                        rate="1/4",lo="0",hi="2")
        self.assertEqual(attempt(actual, {})["reason"],
                         "PARENT_REFUSAL:PHYSICAL_OCTANT_NODE_ZERO")
        self.assertEqual(attempt(actual, {"0":"1/2"})["status"],
                         "REFUSED_NONTRUTH")

    def test_adversarial_receipt_substitution(self):
        actual = certify(source(), {"0":"1/4"})
        for field, replacement in (
            ("root_count", True),
            ("ordered_events", []),
            ("ordered_signed_regions", ["POSITIVE"]*3),
            ("source_spec_sha256", "0"*64),
            ("pb00701_established", True),
            ("production_authorized", True),
            ("schema", "wrong")):
            forged = copy.deepcopy(actual)
            forged[field] = replacement
            with self.subTest(field=field), self.assertRaises(RefusedNontruth):
                verify_receipt(forged)
        nested = copy.deepcopy(actual)
        nested["certified_cells"][0]["certificate"]["root_orders"] = [2,1]
        with self.assertRaises(RefusedNontruth):
            verify_receipt(nested)
        swapped = copy.deepcopy(actual)
        swapped["supplied_rational_pivots"]["0"] = "3/4"
        with self.assertRaises(RefusedNontruth):
            verify_receipt(swapped)

    def test_strict_input_grammar_and_historical_custody(self):
        self.assertEqual(attempt({**source(), "h0":"0.995"},
                                 {"0":"1/4"})["status"], "REFUSED_NONTRUTH")
        self.assertEqual(attempt(source(), {"0":Q(1,4)})["status"],
                         "REFUSED_NONTRUTH")
        self.assertEqual(attempt(source(), {"0":"1/4","4":"2"})["status"],
                         "REFUSED_NONTRUTH")
        contract = octant.historical_contract()
        self.assertEqual(contract["historical_deltas"],
                         {"originals":0,"refused":0,
                          "missing_ordered":0,"prior_complete":0})
        self.assertEqual(contract["newly_closed_originals"], [])
        self.assertTrue(witness.verify_receipt(
            witness.read_receipt()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--source", type=Path)
    ap.add_argument("--pivots", type=Path)
    ap.add_argument("--receipt", type=Path)
    args = ap.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        if not result.wasSuccessful():
            raise SystemExit(1)
    if args.contract:
        out = certify(source(hi="2"), {"0":"1/4"})
        require(verify_receipt(out), "COMPOSITE_RECEIPT_REPLAY")
        print(json.dumps({"status":out["status"],
                          "root_count":out["root_count"],
                          "ordered_signed_regions":out["ordered_signed_regions"],
                          "source_spec_sha256":out["source_spec_sha256"],
                          "parent_historical_census":
                              octant.historical_contract()["historical_before_after"],
                          "required_pb_po_discharges":0,
                          "mc_b":"NOT_ESTABLISHED",
                          "mc_1":"NOT_ESTABLISHED"},
                         sort_keys=True, indent=2))
    if args.receipt:
        print(json.dumps({"receipt_valid":verify_receipt(
            octant.checked_json(args.receipt))}, sort_keys=True))
    if args.source or args.pivots:
        require(args.source and args.pivots, "SOURCE_AND_PIVOTS_REQUIRED")
        print(json.dumps(attempt(octant.checked_json(args.source),
                                 octant.checked_json(args.pivots)),
                         sort_keys=True, indent=2))
    if not (args.self_test or args.contract or args.receipt or args.source):
        ap.print_help()


if __name__ == "__main__":
    main()
