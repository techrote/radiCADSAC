#!/usr/bin/env python3
"""Adversarial verifier for the frozen 20-source identity-topology audit."""
from __future__ import annotations

import argparse
import copy
from collections import Counter
import json
from pathlib import Path
import sys
import unittest

import pb00701_route_refusal_identity_topology_audit as core

MACHINE = core.HERE / "pb00701-route-refusal-identity-topology-audit.json"
MAX_BYTES = 65536
IDENTITY_CASE = "harvested:verify_pb00701_v53:cb01c327d5f1"


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def bounded_json(value):
    stack = [(value, 0, False)]
    live = set()
    nodes = 0
    while stack:
        obj, depth, leaving = stack.pop()
        if leaving:
            live.remove(id(obj))
            continue
        nodes += 1
        need(nodes <= 8192 and depth <= 18,
             "RESOURCE_REFUSAL: report node/depth budget")
        if type(obj) in (dict, list):
            need(id(obj) not in live and len(obj) <= 256,
                 "RESOURCE_REFUSAL: report cycle/container")
            live.add(id(obj))
            stack.append((obj, depth, True))
            if type(obj) is dict:
                for key, val in obj.items():
                    need(type(key) is str and len(key) <= 256,
                         "RESOURCE_REFUSAL: report key")
                    stack.append((val, depth + 1, False))
            else:
                stack.extend((v, depth + 1, False) for v in obj)
        elif type(obj) is str:
            need(len(obj) <= 4096, "RESOURCE_REFUSAL: report string")
        elif type(obj) is int:
            need(abs(obj) < 10**50, "RESOURCE_REFUSAL: report integer")
        else:
            need(obj is None or type(obj) is bool,
                 "invalid report scalar including binary float")
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     allow_nan=False).encode("utf-8")
    need(len(raw) <= MAX_BYTES, "RESOURCE_REFUSAL: report byte budget")
    return raw


def expected_machine():
    report = core.audit()
    report["observed_first_head"] = {
        "git_sha": "6b7351b83afec03b4c58b7b21dab09d695ce5c27",
        "focused_run_id": 41123308401,
        "observation_status":
            "FIRST_HEAD_DESCRIPTIVE_RESULT_REQUIRES_PINNED_REPLAY",
    }
    return report


def validate_report(report):
    need(bounded_json(report) == bounded_json(expected_machine()),
         "FORGED_OR_STALE_IDENTITY_TOPOLOGY_AUDIT")
    counts = report["topology_counts"]
    need(counts == {
        core.ALL_IDENTITY: 1,
        core.ALL_NONIDENTITY: 19,
        core.MIXED: 0,
        core.INCONCLUSIVE: 0,
    }, "UNEXPECTED_20_SOURCE_IDENTITY_TOPOLOGY_COUNTS")
    rows = report["route_refused_sources"]
    need(len(rows) == 20 and len({row["case_id"] for row in rows}) == 20,
         "ROUTE_REFUSAL_DENOMINATOR_NOT_20_DISTINCT_IDS")
    identity_ids = [row["case_id"] for row in rows
                    if row["identity_topology"] == core.ALL_IDENTITY]
    need(identity_ids == [IDENTITY_CASE],
         "SOLE_IDENTITY_SOURCE_ID_CHANGED")
    need(not any(row["identity_topology"] == core.MIXED for row in rows),
         "MIXED_IDENTITY_SOURCE_EXISTS_IN_FROZEN_ROUTE_DENOMINATOR")
    need(not any(row["identity_topology"] == core.INCONCLUSIVE for row in rows),
         "IDENTITY_TOPOLOGY_AUDIT_CONTAINS_INCONCLUSIVE_SOURCE")

    reasons = Counter(
        (item["owner"], item["reason"])
        for row in rows for item in row["historical_blocked_owner_reasons"])
    need(sum(reasons.values()) == 20, "EXPECTED_ONE_BLOCKED_ROUTE_OWNER_PER_CASE")
    expected_reasons = Counter({
        ("DELEGATED_V6_CONSTANT_MODULATION",
         "TRIGONOMETRIC_IDENTITY_ZERO_REQUIRES_SEPARATE_SEMANTIC_HANDLING"): 1,
        ("PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR",
         "NONCONSTANT_AMPLITUDE_PHASE_DEPENDENT_ANCHOR_NOT_CERTIFIED"): 1,
        ("PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION",
         "V27_CHILD_LEFT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE"): 1,
        ("PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION",
         "V27_CHILD_NOT_CERTIFIED"): 4,
        ("PB00701_V41_EXACT_ROTATED_COORDINATE_ORIENTATION_ROOT_PARTITION_COMPOSITION",
         "V41_COMPLETE_V43_CHILD_NOT_COMPOSABLE"): 1,
        ("PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF",
         "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"): 11,
        ("PB00701_V44_EXACT_REAL_ALGEBRAIC_ORIENTATION_CUT_BOUNDARY",
         "ALGEBRAIC_ORIENTATION_COORDINATE_CERTIFIED_BUT_EXACT_CONSUMPTION_AUTHORITY_MISSING"): 1,
    })
    need(reasons == expected_reasons,
         "HISTORICAL_ROUTE_REFUSAL_REASON_DENOMINATOR_CHANGED")
    return True


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = json.loads(MACHINE.read_text(encoding="utf-8"))
        cls.expected = expected_machine()
        cls.rows = {x["case_id"]: x for x in cls.actual["route_refused_sources"]}

    def test_01_machine_report_exactly_replays_all_20_sources(self):
        self.assertTrue(validate_report(self.actual))
        self.assertEqual(self.actual, self.expected)
        self.assertEqual(len(self.rows), 20)

    def test_02_only_historical_v6_identity_source_is_all_identity(self):
        identity = self.rows[IDENTITY_CASE]
        self.assertEqual(identity["identity_topology"], core.ALL_IDENTITY)
        self.assertEqual(identity["identity_checker_status"],
                         "IDENTITY_ZERO_ON_ALL_OPEN_SPANS")
        self.assertEqual(identity["original_open_piece_count"], 1)
        self.assertTrue(all(
            p["identity_status"] == "IDENTITY_ZERO"
            for p in identity["open_piece_identity_records"]))

    def test_03_every_other_route_refusal_is_all_nonidentity(self):
        others = [row for cid, row in self.rows.items() if cid != IDENTITY_CASE]
        self.assertEqual(len(others), 19)
        self.assertTrue(all(
            row["identity_topology"] == core.ALL_NONIDENTITY
            for row in others))
        self.assertTrue(all(
            row["identity_checker_status"] == "NOT_IDENTITY_ON_SOME_OPEN_SPAN"
            for row in others))
        self.assertTrue(all(
            all(p["identity_status"] == "NOT_IDENTITY"
                for p in row["open_piece_identity_records"])
            for row in others))

    def test_04_no_mixed_or_inconclusive_historical_route_source(self):
        self.assertEqual(self.actual["topology_counts"][core.MIXED], 0)
        self.assertEqual(self.actual["topology_counts"][core.INCONCLUSIVE], 0)

    def test_05_classifier_is_not_dead_and_detects_synthetic_mixed(self):
        rows, identity = core.load_inputs()
        lowerer = identity.original_lowerer()
        mixed = core.synthetic_fixture(identity, ("0", "1"))
        result = identity.inspect_original_source(
            mixed, max_order=identity.MAX_STATIONARY_CYCLOTOMIC_ORDER,
            lowerer=lowerer)
        self.assertEqual(core.topology_from_identity(result), core.MIXED)
        self.assertEqual(
            [p["identity_status"] for p in result["spans"]],
            ["IDENTITY_ZERO", "NOT_IDENTITY"])

    def test_06_resource_refusal_is_inconclusive_not_nonidentity(self):
        _, identity = core.load_inputs()
        lowerer = identity.original_lowerer()
        fixture = identity.fixture(
            cos={"0": identity.spline("1")}, offset="1/257", rate="0")
        result = identity.inspect_original_source(
            fixture, max_order=identity.MAX_STATIONARY_CYCLOTOMIC_ORDER,
            lowerer=lowerer)
        self.assertEqual(result["status"], "RESOURCE_REFUSAL")
        self.assertEqual(core.topology_from_identity(result), core.INCONCLUSIVE)
        self.assertFalse(result["is_truth_value"])

    def test_07_forged_count_case_source_piece_or_gate_refuse(self):
        mutations = [
            lambda x: x["topology_counts"].update({core.MIXED: 1}),
            lambda x: x["topology_counts"].update({core.ALL_NONIDENTITY: 18}),
            lambda x: x["route_refused_sources"].pop(),
            lambda x: x["route_refused_sources"][0].update(
                original_source_sha256="f" * 64),
            lambda x: x["route_refused_sources"][0].update(
                identity_topology=core.MIXED),
            lambda x: x["route_refused_sources"][0][
                "open_piece_identity_records"][0].update(
                    identity_status="IDENTITY_ZERO"),
            lambda x: x["route_refused_sources"][0][
                "historical_blocked_owner_reasons"][0].update(
                    reason="FORGED"),
            lambda x: x["claims"].update({ "MC_B_established": True }),
            lambda x: x["claims"].update({ "production_authorized": True }),
            lambda x: x["observed_first_head"].update(
                git_sha="0" * 40),
        ]
        for mutate in mutations:
            forged = copy.deepcopy(self.actual)
            mutate(forged)
            with self.subTest(mutate=str(mutate)), self.assertRaises(ValueError):
                validate_report(forged)

    def test_08_untrusted_report_resources_fail_before_comparison(self):
        with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
            bounded_json({"huge": "x" * (MAX_BYTES + 1)})
        cycle = []
        cycle.append(cycle)
        with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
            bounded_json(cycle)
        deep = []
        node = deep
        for _ in range(20):
            item = []
            node.append(item)
            node = item
        with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
            bounded_json(deep)
        with self.assertRaisesRegex(ValueError, "invalid report scalar"):
            bounded_json({"binary_float": 0.25})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        actual = json.loads(MACHINE.read_text(encoding="utf-8"))
        validate_report(actual)
        print("PASS: exact 20 route-refused original sources replayed")
        print("PASS: identity topology ALL_IDENTITY=1 ALL_NONIDENTITY=19 "
              "MIXED=0 INCONCLUSIVE=0")
        print("PASS: sole identity source is historical V6 continuum-zero case")
        print("OUTCOME C: mixed identity segmentation has zero historical "
              "route-refusal delta on frozen V54 corpus")
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(AuditTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            sys.exit(1)


if __name__ == "__main__":
    main()
