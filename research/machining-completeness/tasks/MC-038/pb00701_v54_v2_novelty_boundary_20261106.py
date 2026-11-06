#!/usr/bin/env python3
"""Source-pinned negative admission check for three repeated V54 signed claims.

DETERMINISTIC_MODEL only. This checks novelty of a proposed *counting route*,
not mathematical impossibility, generic event completeness or MC-B acceptance.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
V54 = "pb00701-finite-owner-corpus-v54.json"
V2 = "pb00701-post-v54-evidence-reconciliation-v2.json"
OLD_V23 = "pb00701-exact-zero-child-source-completion-witness.json"
RECEIPT = "pb00701-v54-v2-novelty-boundary-20261106.json"
PINS = {
    V54: ("5841c331579489b25caef38cd412bdbf286f9134", 300000),
    V2: ("e52d3baf3692a011cf86234eeaa992ef407d99fd", 210000),
    OLD_V23: ("ed0a09595a4e73f7fdb9853d9151b8c7b6fea05f", 40000),
}
OLD_STATIONARY_CODE = "d0fbe7e189066fd9398958f1b1814b8147a6a64e"
CASES = {
    "composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0": {
        "sha": "f4c2d33cc4c5a52f355ff4ecc36ad6ee38af0ff0fa8c5159aaac5923a10125ff",
        "row": "9ee0aed1b32cb85389f372e291a1eb80b9666d2c480d1bfbfa9fb62254dc78d8",
        "rate": "0", "producer": "stationary", "old_event": "1/2",
        "candidate": 421, "head": "359784454c4eaeda173458b9f4919b07edbdacd8",
        "candidate_receipt_blob": "d7ee51ed09bc317f29177286dbd9b1e827c8bd10",
    },
    "composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100": {
        "sha": "a49b92bbb74a7e016eed471feb64808eb9109a6a42b3ef874243364981a396fd",
        "row": "a656298a7843e5dfff9bcf4d6262e18331c12f37cb23381d94bd8487f0ab57ca",
        "rate": "0", "producer": "stationary", "old_event": "1/2",
        "candidate": 421, "head": "359784454c4eaeda173458b9f4919b07edbdacd8",
        "candidate_receipt_blob": "d7ee51ed09bc317f29177286dbd9b1e827c8bd10",
    },
    "composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0": {
        "sha": "e8d2451833854ee7eaf73d4fb70b78b86ba72194b2688876f3bb9ee6ab132ffd",
        "row": "e52a27e5c3dcdf984919cdcd7bb925c52d2865550035da357cd87178b9fbfc89",
        "rate": "1/12", "producer": "exact_zero_children", "old_event": "1",
        "candidate": 423, "head": "cb594e7a1fe286e953e62e5d3c01916120b18337",
        "candidate_receipt_blob": "4e8d41aba7c1b90b4fda20e39a9c41a6e93fe4f1",
    },
}


class InvalidEvidence(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise InvalidEvidence(reason)


def blob_digest(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def bounded(path, limit):
    with path.open("rb") as handle:
        raw = handle.read(limit + 1)
    need(len(raw) <= limit, "FROZEN_INPUT_BYTE_LIMIT")
    return raw


def no_duplicates(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def decode(raw):
    return json.loads(raw, object_pairs_hook=no_duplicates,
                      parse_constant=lambda _: (_ for _ in ()).throw(
                          InvalidEvidence("NONFINITE_JSON")))


def pinned(name):
    expected, limit = PINS[name]
    raw = bounded(HERE / name, limit)
    need(blob_digest(raw) == expected, "PINNED_GIT_BLOB_MISMATCH:" + name)
    return decode(raw)


def snapshot_validate(corpus, registry, ident, spec):
    rows = [row for row in corpus["cases"] if row["id"] == ident]
    v2 = [row for row in registry["source_cases"] if row["case_id"] == ident]
    need(len(rows) == len(v2) == 1, "ORIGINAL_ID_CUSTODY")
    row, prior = rows[0], v2[0]
    need(row["expected"]["v54_disposition"] ==
         "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE",
         "NOT_HISTORICAL_ORDERED_GAP")
    need(row["spec"]["source_parameter_id"] == "source-time-t" and
         row["spec"]["parameter_lo"] == "0" and
         row["spec"]["parameter_hi"] == "2" and
         row["spec"]["phase_turn_offset"] == "0" and
         row["spec"]["phase_turn_rate"] == spec["rate"],
         "ORIGINAL_TIME_PHASE")
    need(prior["source_sha256"] == spec["sha"] and
         prior["original_row_sha256"] == spec["row"],
         "SOURCE_AND_ROW_SHA256")
    canonical = json.dumps(row["spec"], sort_keys=True, separators=(",", ":")).encode()
    need(hashlib.sha256(canonical).hexdigest() == spec["sha"],
         "ORIGINAL_SPEC_DIGEST")
    need(prior["source_interval"] == ["0", "2"] and
         prior["original_source_piece_edges"] == ["0", "1", "2"] and
         prior["phase_turn_law"] == {"offset": "0", "rate": spec["rate"]},
         "ORIGINAL_SOURCE_KNOT_BINDING")
    ev = prior["evidence"]
    need(prior["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
         ev["level"] == "COMPLETE_SOURCE_SPECIFIC" and
         ev["complete_original_source_zero_set"] is True and
         ev["source_sha256"] == spec["sha"] and
         ev["original_row_sha256"] == spec["row"] and
         ev["covered_original_source_interval"] == ["0", "2"] and
         ev["producer"] == spec["producer"] and
         prior["historical_disposition_changed"] is False,
         "ALREADY_COMPLETE_SOURCE_SPECIFIC")
    return prior


def check_stationary(prior_map):
    p = HERE / "pb00701_stationary_knot_composition.py"
    need(blob_digest(bounded(p, 30000)) == OLD_STATIONARY_CODE,
         "PRIOR_STATIONARY_PRODUCER_DRIFT")
    sys.path.insert(0, str(HERE))
    import pb00701_stationary_knot_composition as stationary
    old = stationary.replay_frozen_stationary_cases()
    out = {}
    for ident, spec in CASES.items():
        if spec["producer"] != "stationary":
            continue
        earlier = [x for x in old if x["source_case_id"] == ident]
        need(len(earlier) == 1, "PRIOR_STATIONARY_EVENT_MISSING")
        item = earlier[0]
        need(item["original_source_sha256"] == spec["sha"] and
             item["historical_v54_disposition"] ==
             "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE" and
             item["distinct_open_physical_zeros"] == 1,
             "PRIOR_STATIONARY_FULL_SOURCE")
        events = item["ordered_physical_zero_events"]
        print("PRIOR_STATIONARY_EVENT_DIAG", ident, json.dumps(events, sort_keys=True))
        need(len(events) == 1 and events[0]["coordinate"] == spec["old_event"] and
             events[0]["coordinate_kind"] == "EXACT_RATIONAL" and
             events[0]["left_sign"] == -1 and events[0]["right_sign"] == 1 and
             events[0]["multiplicity"] == 1 and
             events[0]["event_kind"] == "CROSSING",
             "PRIOR_STATIONARY_SIGNED_EVENT")
        knots = item["true_source_knots"]
        need(len(knots) == 1 and knots[0]["position"] == "1" and
             knots[0]["kind"] == "NONZERO_KNOT_NOT_ROOT" and
             knots[0]["is_physical_zero"] is False and
             knots[0]["left_inward_sign"] == 1 and
             knots[0]["right_inward_sign"] == 1,
             "PRIOR_STATIONARY_PHYSICAL_KNOT")
        need([x["sign"] for x in item["maximal_open_sign_cells"]] == [-1, 1],
             "PRIOR_STATIONARY_SIGN_CELLS")
        out[ident] = {"producer_git_blob": OLD_STATIONARY_CODE,
                      "prior_event": "SIMPLE_NEGATIVE_TO_POSITIVE_AT_1/2",
                      "true_knot": "NONZERO_POSITIVE",
                      "prior_maximal_sign_cells": [-1, 1]}
    need(len(out) == 2, "PRIOR_STATIONARY_COVERAGE")
    return out


def v23_validate(witness, ident, spec):
    selected = [x for x in witness["source_specific_proofs"]
                if x["case_id"] == ident]
    need(len(selected) == 1, "PRIOR_V23_PROOF_MISSING")
    x = selected[0]
    need(x["source_sha256"] == spec["sha"] and
         x["original_row_sha256"] == spec["row"] and
         x["source_interval"] == ["0", "2"] and
         x["phase_turn_law"] == {"offset": "0", "rate": "1/12"} and
         x["original_source_piece_edges"] == ["0", "1", "2"] and
         x["complete_original_source_zero_set"] is True and
         x["physical_zero_set"] == ["1"] and
         x["complete_finite_physical_event_count"] == 1 and
         x["ordered_nonzero_signs"] == [-1, 1],
         "PRIOR_V23_SIGNED_COVERAGE")
    k = x["source_knot_receipt"]
    need(k["coordinate"] == "1" and
         k["status"] == "EXACT_SINGLE_SOURCE_KNOT_ZERO" and
         k["left_one_sided_order"] == k["right_one_sided_order"] == 1 and
         k["left_sign"] == -1 and k["right_sign"] == 1 and
         k["event_kind"] == "CROSSING" and
         k["global_smooth_multiplicity_claimed"] is False,
         "PRIOR_V23_KNOT_AND_PARITY")
    need([cell["sign"] for cell in x["maximal_nonzero_cells"]] == [-1, 1] and
         len(x["physical_events"]) == 1 and
         x["physical_events"][0]["coordinate"] == "1" and
         x["physical_events"][0]["left_sign"] == -1 and
         x["physical_events"][0]["right_sign"] == 1 and
         x["whole_source_completeness_proof"]["entire_original_closed_interval_covered"] is True,
         "PRIOR_V23_EXHAUSTIVE_SIGN_CELLS")
    return {"producer_git_blob": "668eef22876afdeec0931a6ccb6a48573b053203",
            "prior_event": "SIGNED_SOURCE_KNOT_CROSSING_AT_1",
            "true_knot": "EXACT_ZERO_SIDED_ORDERS_1_1",
            "prior_maximal_sign_cells": [-1, 1]}


def census(corpus, registry):
    cases = corpus["cases"]
    need(len(cases) == 121 and len({x["id"] for x in cases}) == 121,
         "FROZEN_121_SOURCE_DENOMINATOR")
    hist = [x["expected"]["v54_disposition"] for x in cases]
    missing = sum(x == "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
                  for x in hist)
    routes = sum(x == "BLOCKED" for x in hist)
    need(missing == 30 and routes == 20 and len(registry["source_cases"]) == 50,
         "FROZEN_121_20_30_50_CENSUS")
    need(len({x["case_id"] for x in registry["source_cases"]}) == 50,
         "PRIOR_COMPLETE_SOURCE_IDS_NOT_UNIQUE")
    need({x["case_id"] for x in registry["source_cases"]} ==
         {x["id"] for x in cases if x["expected"]["v54_disposition"].startswith("BLOCKED")},
         "PRIOR_V2_CASE_SET_DRIFT")
    disposition_by_id = {x["id"]: x["expected"]["v54_disposition"] for x in cases}
    need(all(x["historical_v54_disposition"] == disposition_by_id[x["case_id"]]
             for x in registry["source_cases"]),
         "CASE_LEVEL_HISTORICAL_DISPOSITION_CHANGED")
    return {"frozen_originals": 121, "route_refusals": 20,
            "missing_ordered": 30, "preexisting_complete_source_witnesses": 50}


def receipt_for(corpus, registry, old_v23, station=None):
    counts = census(corpus, registry)
    prior_map = {ident: snapshot_validate(corpus, registry, ident, spec)
                 for ident, spec in CASES.items()}
    station = station if station is not None else check_stationary(prior_map)
    records = []
    for ident, spec in CASES.items():
        evidence = (station[ident] if spec["producer"] == "stationary" else
                    v23_validate(old_v23, ident, spec))
        records.append({
            "case_id": ident, "original_source_sha256": spec["sha"],
            "original_row_sha256": spec["row"], "source_time": ["0", "2"],
            "source_knot": "1", "phase_rate_turns": spec["rate"],
            "challenged_pr": spec["candidate"], "challenged_pr_head": spec["head"],
            "challenged_receipt_blob": spec["candidate_receipt_blob"],
            "prior_v2_registered_complete": True,
            "prior_full_signed_physical_event": evidence["prior_event"],
            "prior_producer_git_blob": evidence["producer_git_blob"],
            "prior_true_knot": evidence["true_knot"],
            "prior_maximal_sign_cells": evidence["prior_maximal_sign_cells"],
            "unique_new_source_specific_event_or_sign_cells": False,
            "generic_historical_owner_renewed_by_this_comparison": False
        })
    return {
        "schema": "radicadsac-mc038-v54-v2-novelty-boundary/1.0",
        "evidence_class": "DETERMINISTIC_MODEL",
        "claim": "REPEATED_SOURCE_SIGNED_WITNESS_NOT_NEW_V54_OWNER_PREMISE",
        "historical_before": counts, "historical_after": counts.copy(),
        "accepted_delta": {name: 0 for name in counts},
        "previously_unregistered_unique_signed_source_closures": 0,
        "cases": records,
        "requested_candidate_ordered_count_30_to_27_accepted": False,
        "does_not_falsify_new_generic_compositor": True,
        "required_pb_or_po_obligations_discharged": 0,
        "mc_b_established": False, "mc1_established": False,
        "production_authorized": False, "native_or_step_qualified": False,
    }


def typed_equal(a, b):
    return json.dumps(a, sort_keys=True, separators=(",", ":"), ensure_ascii=True) == \
           json.dumps(b, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def verify():
    corpus, registry, old = pinned(V54), pinned(V2), pinned(OLD_V23)
    result = receipt_for(corpus, registry, old)
    actual = decode(bounded(HERE / RECEIPT, 16000))
    need(typed_equal(actual, result), "COMMITTED_NOVELTY_RECEIPT_MISMATCH")
    return result


def tests():
    import unittest

    class Adversarial(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.a, cls.b, cls.c = pinned(V54), pinned(V2), pinned(OLD_V23)
            cls.good = receipt_for(cls.a, cls.b, cls.c)

        def reject(self, action, label):
            with self.assertRaises(InvalidEvidence, msg=label):
                action()

        def test_positive(self):
            self.assertTrue(typed_equal(verify(), self.good))
            self.assertEqual(len(self.good["cases"]), 3)

        def test_original_source_identity(self):
            a = copy.deepcopy(self.a)
            next(x for x in a["cases"] if x["id"] in CASES)["spec"]["phase_turn_rate"] = "1/999"
            self.reject(lambda: receipt_for(a, self.b, self.c, check_stationary({})), "phase altered")

        def test_wrong_source_sha(self):
            b = copy.deepcopy(self.b)
            next(x for x in b["source_cases"] if x["case_id"] in CASES)["source_sha256"] = "0"*64
            self.reject(lambda: receipt_for(self.a, b, self.c, check_stationary({})), "source altered")

        def test_wrong_source_knot(self):
            b = copy.deepcopy(self.b)
            next(x for x in b["source_cases"] if x["case_id"] in CASES)["original_source_piece_edges"] = ["0","3/2","2"]
            self.reject(lambda: receipt_for(self.a, b, self.c, check_stationary({})), "knot altered")

        def test_old_v23_crossing_changed(self):
            c = copy.deepcopy(self.c)
            next(x for x in c["source_specific_proofs"] if x["case_id"] in CASES)["source_knot_receipt"]["left_sign"] = 1
            self.reject(lambda: receipt_for(self.a, self.b, c, check_stationary({})), "sign altered")

        def test_old_v23_order_changed(self):
            c = copy.deepcopy(self.c)
            next(x for x in c["source_specific_proofs"] if x["case_id"] in CASES)["source_knot_receipt"]["left_one_sided_order"] = 2
            self.reject(lambda: receipt_for(self.a, self.b, c, check_stationary({})), "order altered")

        def test_old_v23_source_cells_changed(self):
            c = copy.deepcopy(self.c)
            next(x for x in c["source_specific_proofs"] if x["case_id"] in CASES)["maximal_nonzero_cells"][0]["sign"] = 1
            self.reject(lambda: receipt_for(self.a, self.b, c, check_stationary({})), "cells altered")

        def test_missing_original_row(self):
            a = copy.deepcopy(self.a)
            a["cases"] = [x for x in a["cases"] if x["id"] != next(iter(CASES))]
            self.reject(lambda: receipt_for(a, self.b, self.c, check_stationary({})), "missing row")

        def test_missing_prior_complete(self):
            b = copy.deepcopy(self.b)
            next(x for x in b["source_cases"] if x["case_id"] in CASES)["registered_evidence_level"] = "PARTIAL"
            self.reject(lambda: receipt_for(self.a, b, self.c, check_stationary({})), "partial witness")

        def test_census_unchanged_histogram_is_not_enough(self):
            a = copy.deepcopy(self.a)
            rows = [x for x in a["cases"] if x["expected"]["v54_disposition"].startswith("BLOCKED")]
            rows[0]["expected"]["v54_disposition"], rows[-1]["expected"]["v54_disposition"] = (
                rows[-1]["expected"]["v54_disposition"], rows[0]["expected"]["v54_disposition"])
            self.reject(lambda: receipt_for(a, self.b, self.c, check_stationary({})), "disposition swap")

        def test_bool_int_receipt_alias(self):
            x = copy.deepcopy(self.good)
            x["required_pb_or_po_obligations_discharged"] = False
            self.assertFalse(typed_equal(x, self.good))
            x = copy.deepcopy(self.good)
            x["historical_before"]["missing_ordered"] = 30.0
            self.assertFalse(typed_equal(x, self.good))

        def test_duplicate_and_nonfinite_json(self):
            self.reject(lambda: decode(b'{"x":1,"x":2}'), "duplicate key")
            self.reject(lambda: decode(b'{"x":NaN}'), "nonfinite")

        def test_oversized_raw_ingress(self):
            with tempfile.TemporaryDirectory() as d:
                path = Path(d)/"bad.json"
                path.write_bytes(b"x"*1025)
                self.reject(lambda: bounded(path, 1024), "byte budget")

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Adversarial)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("ADVERSARIAL_CONTROLS", result.testsRun)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--print-receipt", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        tests()
    result = verify()
    print("NOVELTY_BOUNDARY", len(result["cases"]),
          "ACCEPTED_HISTORICAL_DELTA", 0,
          "ALREADY_COMPLETE_V2", result["historical_before"]["preexisting_complete_source_witnesses"])
    if args.print_receipt:
        print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
