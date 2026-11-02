#!/usr/bin/env python3
"""Source-replayed 50-case evidence reconciliation and adversarial controls."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
import pb00701_post_v54_evidence_reconciliation as model


class ReconciliationTests(unittest.TestCase):
    expected = None

    @classmethod
    def setUpClass(cls):
        # CLI has already reexecuted every proof once. Direct unittest loading
        # still performs that real replay. Mutations compare against immutable
        # bytes from this replay, never caller-provided expected results.
        if cls.expected is None:
            cls.expected = model.expected_report()
        cls.expected_bytes = model.bounded_bytes(cls.expected)
        cls.original = model.original_corpus()

    def rejects(self, change):
        changed = copy.deepcopy(self.expected)
        change(changed)
        with self.assertRaises(model.Refusal):
            model._compare_with_replayed_bytes(changed, self.expected_bytes)

    def row(self, report, level=None, cid=None):
        return next(r for r in report["source_cases"] if
                    (level is None or r["registered_evidence_level"] == level) and
                    (cid is None or r["case_id"] == cid))

    def test_exact_replay_and_full_denominator(self):
        self.assertTrue(model._compare_with_replayed_bytes(self.expected, self.expected_bytes))
        ids = {r["id"] for r in self.original.values() if
               r["expected"]["v54_disposition"] in ("BLOCKED", model.ORDER_GAP)}
        rows = self.expected["source_cases"]
        self.assertEqual(len(rows), 50)
        self.assertEqual({r["case_id"] for r in rows}, ids)
        self.assertEqual(self.expected["summary"]["by_registered_evidence_level"], {
            model.COMPLETE: 15, model.TAIL: 9, model.CHILD: 18, model.UNREGISTERED: 8})
        self.assertEqual(self.expected["summary"]["historical_route_refusals"][model.COMPLETE], 11)
        self.assertEqual(self.expected["summary"]["historical_missing_ordered_premises"][model.COMPLETE], 4)

    def test_duplicate_and_omitted_sources(self):
        self.rejects(lambda r: r["source_cases"].append(copy.deepcopy(r["source_cases"][0])))
        self.rejects(lambda r: r["source_cases"].pop())
        self.rejects(lambda r: r["source_cases"].__setitem__(1, copy.deepcopy(r["source_cases"][0])))

    def test_count_preserving_partial_complete_swap(self):
        def swap(r):
            a, b = self.row(r, model.COMPLETE), self.row(r, model.TAIL)
            a["registered_evidence_level"], b["registered_evidence_level"] = (
                b["registered_evidence_level"], a["registered_evidence_level"])
            a["evidence"], b["evidence"] = b["evidence"], a["evidence"]
        self.rejects(swap)

    def test_tail_cannot_be_promoted_to_whole_source(self):
        def promote(r):
            v = self.row(r, model.TAIL)
            v["registered_evidence_level"] = model.COMPLETE
            v["evidence"]["complete_original_source_zero_set"] = True
            v["evidence"]["covered_original_source_interval"] = v["source_interval"]
        self.rejects(promote)
        row = self.original[self.row(self.expected, model.TAIL)["case_id"]]
        with self.assertRaisesRegex(model.Refusal, "PARTIAL_INTERVAL"):
            model.evidence_entry("v10_tail_crossing", row["id"], row, {},
                                 model.COMPLETE, ["1", "2"], "forged complete")

    def test_ordered_child_cannot_be_promoted_to_composed_source(self):
        def promote(r):
            v = self.row(r, model.CHILD)
            v["registered_evidence_level"] = model.COMPLETE
            v["evidence"]["complete_original_source_zero_set"] = True
            v["remaining_requirement"] = "Nothing remains."
        self.rejects(promote)
        row = self.original[self.row(self.expected, model.CHILD)["case_id"]]
        with self.assertRaisesRegex(model.Refusal, "ONE_ACTUAL_ORIGINAL_PIECE"):
            model.evidence_entry("v6_ordered", row["id"], row, {},
                                 model.CHILD, ["0", "2"], "forged child interval")

    def test_unknown_proof_and_generic_primitive_not_evidence(self):
        def claim(r):
            v = self.row(r, model.UNREGISTERED)
            v["registered_evidence_level"] = model.COMPLETE
            v["evidence"] = {"producer": "generic_interval_tests", "PASS": True}
        self.rejects(claim)
        self.rejects(lambda r: r["registry_scope"].__setitem__(
            "all_possible_post_v54_proofs_exhaustively_discovered", True))

    def test_continuum_cannot_be_recounted_as_finite_events(self):
        row = self.row(self.expected, cid=model.CONTINUUM_ID)
        self.assertEqual(row["evidence"]["scope"], "COMPLETE_CLOSED_CONTINUUM_ZERO_SET")
        self.assertEqual(self.expected["summary"]["complete_continuum_sources"], 1)
        self.assertNotIn("closed_root_count", row["evidence"])
        self.rejects(lambda r: self.row(r, cid=model.CONTINUUM_ID)["evidence"].__setitem__(
            "scope", "COMPLETE_FINITE_SOURCE_ZERO_SET"))
        self.rejects(lambda r: self.row(r, cid=model.CONTINUUM_ID)["evidence"].__setitem__(
            "closed_root_count", 0))

    def test_five_and_six_source_unions_do_not_double_count(self):
        rows = self.expected["source_cases"]
        self.assertEqual(sum(r["evidence"] is not None and r["evidence"]["producer"] == "five"
                             for r in rows), 5)
        self.assertEqual(sum(r["evidence"] is not None and r["evidence"]["producer"] == "continuum"
                             for r in rows), 1)
        self.rejects(lambda r: r["summary"]["by_registered_evidence_level"].__setitem__(model.COMPLETE, 20))

    def test_stale_v6_handover_is_resolved_by_existing_evidence(self):
        row = self.row(self.expected, cid=model.KNOT_ID)
        self.assertEqual(row["registered_evidence_level"], model.COMPLETE)
        self.assertEqual(row["evidence"]["producer"], "knot")
        self.assertEqual(row["historical_v54_disposition"], "BLOCKED")

    def test_v23_boundary_proof_is_original_source_bound(self):
        row = self.row(self.expected, cid=model.V23_ID)
        self.assertEqual(row["registered_evidence_level"], model.COMPLETE)
        self.assertEqual(row["evidence"]["producer"], "v23_bernstein")
        self.assertEqual(row["source_sha256"],
                         "4a3ee3f47b9347429c13830abef382301c7963b0af518f0977390c2d3ffba040")
        self.assertEqual(row["historical_spans"][0][2],
                         "NONCONSTANT_AMPLITUDE_PHASE_DEPENDENT_ANCHOR_NOT_CERTIFIED")

    def test_source_phase_knot_and_provenance_mutations(self):
        changes = [
            lambda row: row.__setitem__("source_sha256", "0" * 64),
            lambda row: row.__setitem__("source_parameter_id", "forged-source"),
            lambda row: row["phase_turn_law"].__setitem__("rate", "1/100"),
            lambda row: row.__setitem__("original_source_piece_edges", ["0", "3/2", "2"]),
            lambda row: row.__setitem__("origin", "unregistered-producer"),
            lambda row: row.__setitem__("provenance_kind", "HARVESTED"),
        ]
        for change in changes:
            with self.subTest(change=change):
                self.rejects(lambda r, change=change: change(self.row(r, model.TAIL)))
        row = self.original[model.KNOT_ID]
        view = model.source_metadata(row)
        view["phase_turn_law"]["rate"] = "1/8"
        with self.assertRaisesRegex(model.Refusal, "PARAMETER_INTERVAL_OR_PHASE"):
            model.bind_view(view, row)

    def test_frozen_historical_status_never_changes(self):
        self.rejects(lambda r: self.row(r, model.COMPLETE).__setitem__("historical_v54_disposition", "CERTIFIED"))
        self.rejects(lambda r: r["historical_v54"].__setitem__("route_refusals", 9))
        self.rejects(lambda r: r["historical_v54"].__setitem__("missing_ordered_span_premises", 26))
        self.rejects(lambda r: self.row(r, model.TAIL)["historical_spans"][1].__setitem__(2, None))

    def test_custody_and_producer_code_mutation(self):
        self.rejects(lambda r: r["producer_registry"][0].__setitem__("code_git_blob", "0" * 40))
        self.rejects(lambda r: self.row(r, model.COMPLETE)["evidence"].__setitem__("replayed_result_sha256", "0" * 64))
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "proof.py"
            p.write_text("original proof\n")
            sha = model.git_blob(p)
            p.write_text("changed proof\n")
            with self.assertRaisesRegex(model.Refusal, "PRODUCER_DRIFT"):
                model.pin(p, sha)

    def test_no_gate_or_production_promotion(self):
        for key, value in (("PB-007-01", "CLOSED"), ("MC-B", "ACCEPTED"),
                           ("MC-1", "ACCEPTED"), ("production_authorized", True),
                           ("required_machining_operations", 25),
                           ("native_geometry_or_STEP_qualified", True)):
            with self.subTest(key=key):
                self.rejects(lambda r, key=key, value=value: r["gates"].__setitem__(key, value))

    def test_boolean_integer_alias_is_rejected(self):
        # Python dict equality would accept 1 == True and 0 == False.
        self.rejects(lambda r: r["gates"].__setitem__("production_authorized", 0))
        self.rejects(lambda r: r["registry_scope"].__setitem__("all_50_historical_unresolved_ids_enumerated", 1))
        self.rejects(lambda r: r["summary"].__setitem__("complete_continuum_sources", True))

    def test_oversized_cyclic_deep_and_nonexact_report(self):
        cyc = []; cyc.append(cyc)
        deep = None
        for _ in range(40):
            deep = [deep]
        shared = "a" * 8192
        for bad in (cyc, deep, "a" * 8193, 1 << 257, float("nan"), 1.0,
                    [shared] * 200, {"non-json": object()}):
            with self.subTest(kind=type(bad).__name__), self.assertRaises(model.Refusal):
                model.bounded_bytes(bad)

    def test_invalid_report_never_reaches_historical_source_parser(self):
        with mock.patch.object(model, "expected_report", side_effect=AssertionError("must not replay")):
            with self.assertRaises(model.Refusal):
                model.validate_report({"forged": float("inf")})
        # A bounded exponent string is inert report data, not Fraction input.
        changed = copy.deepcopy(self.expected)
        self.row(changed)["phase_turn_law"]["rate"] = "1e9999999999999999999999999999"
        with self.assertRaises(model.Refusal):
            model._compare_with_replayed_bytes(changed, self.expected_bytes)

    def test_json_reader_duplicate_and_file_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "report.json"
            for contents in ('{"schema":1,"schema":2}', '{"value":NaN}', '{"value":1.25}'):
                p.write_text(contents)
                with self.subTest(contents=contents), self.assertRaises(model.Refusal):
                    model.read_json(p)
            p.write_bytes(b" " * (model.MAX_BYTES + 1))
            with self.assertRaises(model.Refusal):
                model.read_json(p)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    options = parser.parse_args()
    if not (options.contract or options.self_test):
        parser.error("choose --contract and/or --self-test")
    expected = model.expected_report()
    if options.contract:
        model._compare_with_replayed_bytes(model.read_json(model.MACHINE), model.bounded_bytes(expected))
        print("PASS: all registered proofs replayed against exact originals; 50 historical cases reconciled")
        print(json.dumps(expected["summary"], sort_keys=True))
    if options.self_test:
        ReconciliationTests.expected = expected
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(ReconciliationTests))
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
