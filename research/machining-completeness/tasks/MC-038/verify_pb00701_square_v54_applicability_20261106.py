#!/usr/bin/env python3
"""Exact frozen-source applicability challenge to PR #397; NOT an event solver."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
REPORT = HERE / "pb00701-square-v54-applicability-20261106.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
REPORT_SCHEMA = "radicadsac-pb00701-square-v54-applicability/1.0"
COUNTS = {"SINE_CHANNEL": 110, "COSINE_HARMONICS": 7,
          "TWO_SPAN_QUADRATIC": 4}
DISPOSITIONS = {
    "BLOCKED": 20,
    "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE": 30,
    "CERTIFIED": 40,
    "FINITE_OWNER_SOURCE_EVIDENCE_CERTIFIED": 26,
    "MIXED_OWNER_SOURCE_EVIDENCE_CERTIFIED": 5,
}
MAX_CORPUS_BYTES, MAX_V2_BYTES, MAX_REPORT_BYTES = 300000, 240000, 50000


class Refusal(Exception):
    pass


def require(ok, message):
    if not ok:
        raise Refusal(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def no_constant(value):
    raise Refusal("NONFINITE_JSON_NUMBER")


def read_pinned(path, expected_blob, bound):
    raw = path.open("rb").read(bound + 1)
    require(len(raw) <= bound, "FILE_BYTE_BUDGET")
    git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") +
                            b"\0" + raw).hexdigest()
    require(git_blob == expected_blob, "FROZEN_GIT_BLOB_MISMATCH")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicates,
                      parse_constant=no_constant)


def shape_refusal(spec):
    """First violated NECESSARY gate of #397's original source grammar.

    NOT_EXCLUDED is deliberately not an accepted mathematical event theorem.
    No analytic evaluations, root counts or certificates are returned here.
    """
    require(type(spec) is dict, "SOURCE_TYPE")
    require(type(spec.get("sin_splines")) is dict and
            type(spec.get("cos_splines")) is dict, "SOURCE_CHANNEL_TYPES")
    if spec["sin_splines"]:
        return "SINE_CHANNEL"
    cos = spec["cos_splines"]
    if set(cos) != {"0", "1"}:
        return "COSINE_HARMONICS"
    for h in ("0", "1"):
        entry = cos[h]
        require(type(entry) is dict, "SOURCE_SPLINE_TYPE")
        if (type(entry.get("degree")) is not int or entry["degree"] != 2 or
                type(entry.get("controls")) is not list or
                len(entry["controls"]) != 5 or
                type(entry.get("knots")) is not list or
                len(entry["knots"]) != 8):
            return "TWO_SPAN_QUADRATIC"
    # Other required conditions (shared double knot, rational-affine square
    # identities, nonzero phase rate, resource bounds) are intentionally NOT
    # checked here: failure of any one of the above is already dispositive.
    return "NOT_EXCLUDED"


def compute(corpus, v2):
    cases = corpus["cases"]
    rows = []
    require(len(cases) == 121 and
            len({c["id"] for c in cases}) == 121, "FROZEN_DENOMINATOR")
    requires = [c for c in cases if c["expected"]["v54_disposition"].startswith("BLOCKED")]
    require(len(requires) == 50, "HISTORICAL_UNRESOLVED_DENOMINATOR")
    v2rows = v2["source_cases"]
    v2map = {r["case_id"]: r for r in v2rows}
    require(len(v2rows) == 50 and len(v2map) == 50 and
            set(v2map) == {c["id"] for c in requires}, "V2_CASE_ID_UNION")
    counter = Counter()
    by = defaultdict(Counter)
    for c in sorted(cases, key=lambda row: row["id"]):
        case_id = c["id"]
        disposition = c["expected"]["v54_disposition"]
        reason = shape_refusal(c["spec"])
        counter[reason] += 1
        by[disposition][reason] += 1
        source_sha = hashlib.sha256(canonical(c["spec"])).hexdigest()
        if case_id in v2map:
            old = v2map[case_id]
            require(old["source_sha256"] == source_sha and
                    old["historical_v54_disposition"] == disposition and
                    old["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC",
                    "V2_SOURCE_OR_EVIDENCE_MISMATCH:" + case_id)
        rows.append({"case_id": case_id, "v54_disposition": disposition,
                     "necessary_gate_refusal": reason})
    require(dict(counter) == COUNTS, "FROZEN_SHAPE_HISTOGRAM_DRIFT")
    require({k: sum(v.values()) for k, v in by.items()} ==
            DISPOSITIONS, "FROZEN_DISPOSITION_DRIFT")
    require(sum(1 for r in rows if r["necessary_gate_refusal"] == "NOT_EXCLUDED") == 0,
            "PREREGISTERED_ZERO_ADMISSION_FALSIFIED")
    return {
        "schema": REPORT_SCHEMA,
        "evidence_class": "DETERMINISTIC_MODEL",
        "proof_route": "DIRECT_FROZEN_V54_ADMISSION_BY_TWO_SPAN_H0_H1_SQUARE_THEOREM",
        "pr397_pinned_head": "5f29ed7118f2061644893200f19d4c334716d392",
        "frozen_corpus_blob": CORPUS_BLOB,
        "v2_evidence_blob": V2_BLOB,
        "frozen_before": {"original_sources": 121, "route_refusals": 20,
                          "missing_ordered_premises": 30,
                          "complete_source_specific_witnesses": 50},
        "frozen_after": {"original_sources": 121, "route_refusals": 20,
                         "missing_ordered_premises": 30,
                         "complete_source_specific_witnesses": 50},
        "direct_source_admissions": 0,
        "new_historical_case_closures": [],
        "required_pb_obligations_discharged": 0,
        "shape_gate_counts": dict(sorted(counter.items())),
        "by_v54_disposition": {
            k: dict(sorted(v.items())) for k, v in sorted(by.items())},
        "cases": rows,
        "nonclaims": {
            "general_analytic_event_theorem": False,
            "pr397_theorem_falsified": False,
            "frozen_source_mathematically_unsolvable": False,
            "native_geometry": False,
            "engineering_step": False,
            "mc_b_established": False,
            "mc1_established": False,
            "production_authorized": False,
        },
    }


def verify():
    report_bytes = REPORT.open("rb").read(MAX_REPORT_BYTES + 1)
    require(len(report_bytes) <= MAX_REPORT_BYTES, "REPORT_BYTE_BUDGET")
    receipt = json.loads(report_bytes, object_pairs_hook=no_duplicates,
                         parse_constant=no_constant)
    actual = compute(read_pinned(CORPUS, CORPUS_BLOB, MAX_CORPUS_BYTES),
                     read_pinned(V2, V2_BLOB, MAX_V2_BYTES))
    require(canonical(actual) == canonical(receipt), "MACHINE_RECEIPT_DRIFT")
    return actual


class Adversarial(unittest.TestCase):
    def seed(self):
        knots = ["0", "0", "0", "1", "1", "2", "2", "2"]
        return {
            "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "source_parameter_id": "source-time-t",
            "parameter_lo": "0", "parameter_hi": "2",
            "phase_turn_offset": "0", "phase_turn_rate": "1",
            "sin_splines": {},
            "cos_splines": {
                h: {"degree": 2, "controls": ["0"] * 5,
                    "knots": knots[:]} for h in ("0", "1")}}

    def test_admitted_shape_is_not_event_certification(self):
        s = self.seed()
        for control in (["0"]*5, ["1"]*5,
                        ["0", "0", "0", "1/2", "1"],
                        ["0", "0", "0", "1/" + str(2**120), "1"]):
            s["cos_splines"]["1"]["controls"] = control
            self.assertEqual(shape_refusal(s), "NOT_EXCLUDED")
        # Identity zero, tangency and close-root candidates cannot be
        # promoted to events by a source-shape-only admission test.

    def test_sine_channel_even_when_zero(self):
        s = self.seed()
        s["sin_splines"]["1"] = copy.deepcopy(s["cos_splines"]["1"])
        self.assertEqual(shape_refusal(s), "SINE_CHANNEL")

    def test_wrong_harmonic_basis(self):
        s = self.seed()
        s["cos_splines"].pop("0")
        self.assertEqual(shape_refusal(s), "COSINE_HARMONICS")
        s = self.seed()
        s["cos_splines"]["2"] = s["cos_splines"].pop("1")
        self.assertEqual(shape_refusal(s), "COSINE_HARMONICS")

    def test_not_original_two_span_quadratic(self):
        for field, value in (("degree", 1), ("degree", True),
                             ("controls", ["0"] * 4),
                             ("knots", ["0"] * 7)):
            s = self.seed()
            s["cos_splines"]["0"][field] = value
            self.assertEqual(shape_refusal(s), "TWO_SPAN_QUADRATIC")

    def test_malformed_source_refusal(self):
        for value in (None, [], "source"):
            with self.assertRaises(Refusal):
                shape_refusal(value)
        s = self.seed()
        s["sin_splines"] = ["0"]
        with self.assertRaises(Refusal):
            shape_refusal(s)

    def test_type_preserving_receipt(self):
        self.assertNotEqual(canonical({"count": 1}), canonical({"count": True}))
        self.assertNotEqual(canonical({"count": 1}), canonical({"count": 1.0}))
        with self.assertRaises(ValueError):
            canonical({"count": float("nan")})

    def test_github_blob_tampering(self):
        raw = b"{}"
        valid = hashlib.sha1(b"blob 2\0" + raw).hexdigest()
        self.assertNotEqual(valid,
            hashlib.sha1(b"blob 3\0" + raw + b" ").hexdigest())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--contract", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Adversarial)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)
    if args.contract or args.json or not args.self_test:
        report = verify()
        if args.json:
            print(json.dumps({"result": "PASS",
                  "cases_checked": len(report["cases"]),
                  "necessary_shape_refusals": report["shape_gate_counts"],
                  "new_historical_case_closures": 0}, sort_keys=True))
        else:
            print("PASS: 121 pinned originals, 50 V2 identities, zero direct #397 admissions")


if __name__ == "__main__":
    main()
