#!/usr/bin/env python3
"""Read-only exact-source identity-topology audit of frozen V54 route refusals.

This is a corpus falsification experiment, not a proof-owner rewrite or MC-B
verdict. It classifies each of the exact 20 historical whole-source route
refusals by the identity topology of its ORIGINAL B-spline source pieces:
ALL_IDENTITY, ALL_NONIDENTITY, MIXED_IDENTITY_NONIDENTITY or INCONCLUSIVE.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
AUDITOR_BLOB = "12c6efeb667a954ffc5a7e27849ae815d466580a"
IDENTITY_BLOB = "9fd150e97bce84fdb3c4bad075c9938f4df9136c"
DOMAIN_BLOB = "23de82f5240a72509f7afe4acd5948b65bc4ff13"
AUTH_BLOB = "fa0233323a0804d8a5d3eb7cd892a274a6173fab"
SCHEMA = "radicadsac-mc038-route-refusal-identity-topology-audit/1.0"

ALL_IDENTITY = "ALL_IDENTITY"
ALL_NONIDENTITY = "ALL_NONIDENTITY"
MIXED = "MIXED_IDENTITY_NONIDENTITY"
INCONCLUSIVE = "INCONCLUSIVE"
BLOCKED = "BLOCKED"


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def pin(path, expected):
    need(path.is_file() and git_blob(path) == expected,
         "PINNED_INPUT_GIT_BLOB_DRIFT: " + str(path))
    return path


def canonical_json_sha256(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_inputs():
    pin(HERE / "pb00701-finite-owner-corpus-v54.json", CORPUS_BLOB)
    pin(HERE / "verify_pb00701_post_v54_frontier.py", AUDITOR_BLOB)
    pin(HERE / "verify_pb00701_affine_identity_frontier.py", IDENTITY_BLOB)
    pin(ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json",
        DOMAIN_BLOB)
    pin(ROOT / "handoffs/current-authority.json", AUTH_BLOB)

    import verify_pb00701_post_v54_frontier as auditor
    import verify_pb00701_affine_identity_frontier as identity

    corpus, inventory, boundary = auditor.inputs()
    census = auditor.audit(corpus, inventory, boundary)
    need(census["cases"] == 121 and
         census["v54_dispositions"]["BLOCKED"] == 20 and
         census["v54_dispositions"][
             "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
         "FROZEN_121_20_30_CENSUS_DRIFT")

    authority = json.loads((ROOT / "handoffs/current-authority.json").read_text())
    domain = json.loads((ROOT / "research/machining-completeness/tasks/MC-002/"
                         "domain-contract-v1.json").read_text())
    need(authority["production_authorized"] is False and
         authority["capability_status"] == "NOT_ESTABLISHED",
         "PRODUCTION_OR_MC1_AUTHORITY_PROMOTED")
    need(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
         "MACHINING_DOMAIN_DENOMINATOR_CHANGED")

    rows = [row for row in corpus["cases"]
            if row["expected"]["v54_disposition"] == BLOCKED]
    need(len(rows) == 20 and len({row["id"] for row in rows}) == 20,
         "ROUTE_REFUSAL_CASE_SET_NOT_EXACTLY_20_DISTINCT_IDS")
    return rows, identity


def topology_from_identity(result):
    need(type(result) is dict and "status" in result,
         "IDENTITY_CHECKER_RETURNED_INVALID_RECORD")
    spans = result.get("spans")
    if result["status"] in ("RESOURCE_REFUSAL", "SEMANTIC_BLOCKER") or not spans:
        return INCONCLUSIVE
    statuses = [piece["identity_status"] for piece in spans]
    if any(s == "RESOURCE_REFUSAL" for s in statuses):
        return INCONCLUSIVE
    need(all(s in ("IDENTITY_ZERO", "NOT_IDENTITY") for s in statuses),
         "UNREVIEWED_IDENTITY_PIECE_STATUS")
    if all(s == "IDENTITY_ZERO" for s in statuses):
        return ALL_IDENTITY
    if all(s == "NOT_IDENTITY" for s in statuses):
        return ALL_NONIDENTITY
    return MIXED


def blocked_reasons(row):
    need(row["expected"]["observed"]["status"] == BLOCKED,
         "ROUTE_REFUSAL_CASE_HAS_NONBLOCKED_OBSERVED_STATUS")
    blocked = []
    for span in row["expected"]["observed"]["spans"]:
        need(type(span) is list and len(span) == 3,
             "HISTORICAL_OWNER_SPAN_RECORD_SHAPE_DRIFT")
        if span[1] == BLOCKED:
            blocked.append({"owner": span[0], "reason": span[2]})
    need(blocked, "WHOLE_SOURCE_BLOCKED_WITHOUT_BLOCKED_OWNER_SPAN")
    return blocked


def audit():
    rows, identity = load_inputs()
    lowerer = identity.original_lowerer()
    results = []
    for row in sorted(rows, key=lambda x: x["id"]):
        spec = row["spec"]
        source_sha = canonical_json_sha256(spec)
        observed = identity.inspect_original_source(
            spec, max_order=identity.MAX_STATIONARY_CYCLOTOMIC_ORDER,
            lowerer=lowerer)
        need(observed.get("source_sha256") == source_sha,
             "ORIGINAL_SOURCE_SHA_NOT_BOUND_TO_IDENTITY_RESULT: " + row["id"])
        need(observed.get("source_parameter_id") == spec["source_parameter_id"],
             "ORIGINAL_SOURCE_PARAMETER_NOT_BOUND: " + row["id"])
        topology = topology_from_identity(observed)
        pieces = [
            {
                "source_interval": p["source_interval"],
                "phase_turn_offset": p["phase_turn_offset"],
                "phase_turn_rate": p["phase_turn_rate"],
                "identity_status": p["identity_status"],
                "cyclotomic_order": p["cyclotomic_order"],
            }
            for p in observed.get("spans", [])
        ]
        results.append({
            "case_id": row["id"],
            "origin": row["origin"],
            "kind": row["kind"],
            "original_source_sha256": source_sha,
            "source_parameter_id": spec["source_parameter_id"],
            "source_interval": [spec["parameter_lo"], spec["parameter_hi"]],
            "global_phase_turn_law": {
                "offset": spec["phase_turn_offset"],
                "rate": spec["phase_turn_rate"],
            },
            "historical_blocked_owner_reasons": blocked_reasons(row),
            "identity_checker_status": observed["status"],
            "identity_topology": topology,
            "original_open_piece_count": len(pieces),
            "open_piece_identity_records": pieces,
            "historical_v54_disposition": BLOCKED,
            "historical_status_modified": False,
        })
    counts = {key: sum(row["identity_topology"] == key for row in results)
              for key in (ALL_IDENTITY, ALL_NONIDENTITY, MIXED, INCONCLUSIVE)}
    return {
        "schema": SCHEMA,
        "task": "MC-038",
        "evidence_class": "DETERMINISTIC_MODEL_DESCRIPTIVE_AUDIT",
        "frozen_original_corpus_git_blob": CORPUS_BLOB,
        "route_refused_original_source_denominator": 20,
        "missing_ordered_premise_denominator_separate": 30,
        "full_frozen_source_denominator": 121,
        "topology_counts": counts,
        "route_refused_sources": results,
        "claims": {
            "historical_v54_dispositions_modified": False,
            "mixed_segmentation_historical_delta_claimed": False,
            "PB00701_closed": False,
            "MC_B_established": False,
            "MC1_established": False,
            "production_authorized": False,
        },
    }


def synthetic_fixture(identity, controls, *, rate="0", hi="2"):
    return identity.fixture(
        cos={"0": identity.spline(*controls, degree=0,
                                  knots=[0, 1, 2] if hi == "2" else [0, 1])},
        offset="0", rate=rate, lo="0", hi=hi)


class TopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.identity = load_inputs()
        cls.lowerer = cls.identity.original_lowerer()

    def classify(self, spec):
        return topology_from_identity(self.identity.inspect_original_source(
            spec, max_order=self.identity.MAX_STATIONARY_CYCLOTOMIC_ORDER,
            lowerer=self.lowerer))

    def test_synthetic_classifier_distinguishes_all_three_topologies(self):
        self.assertEqual(self.classify(
            synthetic_fixture(self.identity, ("0", "0"))), ALL_IDENTITY)
        self.assertEqual(self.classify(
            synthetic_fixture(self.identity, ("1", "1"))), ALL_NONIDENTITY)
        self.assertEqual(self.classify(
            synthetic_fixture(self.identity, ("0", "1"))), MIXED)

    def test_nonstationary_zero_and_nonzero_are_distinguished(self):
        zero = self.identity.fixture(
            cos={"1": self.identity.spline("0", "0")}, rate="1/7")
        nonzero = self.identity.fixture(
            cos={"1": self.identity.spline("0", "1")}, rate="1/7")
        self.assertEqual(self.classify(zero), ALL_IDENTITY)
        self.assertEqual(self.classify(nonzero), ALL_NONIDENTITY)

    def test_stationary_resource_limit_remains_inconclusive(self):
        spec = self.identity.fixture(
            cos={"0": self.identity.spline("1")},
            offset="1/257", rate="0")
        result = self.identity.inspect_original_source(
            spec, max_order=self.identity.MAX_STATIONARY_CYCLOTOMIC_ORDER,
            lowerer=self.lowerer)
        self.assertEqual(result["status"], "RESOURCE_REFUSAL")
        self.assertEqual(topology_from_identity(result), INCONCLUSIVE)
        self.assertFalse(result["is_truth_value"])

    def test_original_source_mutation_changes_binding_not_historical_truth(self):
        row = copy.deepcopy(self.rows[0])
        before = canonical_json_sha256(row["spec"])
        row["spec"]["phase_turn_rate"] = "0"
        after = canonical_json_sha256(row["spec"])
        self.assertNotEqual(before, after)
        # The audit's original row is immutable; a mutation is a new source,
        # not a permissible reclassification of the frozen case.
        self.assertEqual(self.rows[0]["expected"]["v54_disposition"], BLOCKED)

    def test_actual_census_rows_are_exactly_twenty_route_refusals(self):
        self.assertEqual(len(self.rows), 20)
        self.assertEqual(len({row["id"] for row in self.rows}), 20)
        self.assertTrue(all(row["expected"]["v54_disposition"] == BLOCKED
                            for row in self.rows))
        self.assertTrue(all(blocked_reasons(row) for row in self.rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        print(json.dumps(audit(), sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TopologyTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
