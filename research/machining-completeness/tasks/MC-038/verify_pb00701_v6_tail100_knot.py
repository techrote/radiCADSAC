#!/usr/bin/env python3
"""PB-007-01: exact frozen V6 tail100 touching-knot source proof and census.

Research-only deterministic mathematical case evidence, NOT a general V27 repair,
a changed historical v54 decision, a PB-007-01 gate closure or native geometry.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

CASE_ID = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail100"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
AUDITOR_BLOB = "12c6efeb667a954ffc5a7e27849ae815d466580a"
DOMAIN_BLOB = "23de82f5240a72509f7afe4acd5948b65bc4ff13"
AUTH_BLOB = "fa0233323a0804d8a5d3eb7cd892a274a6173fab"
SOURCE_SHA256 = "f6a0eb06c66af415fbb8abdfe62f9b36a2a2bf154e535d83307a80228e044ad5"
MACHINE = HERE / "pb00701-v6-tail100-knot-post-v54-witness.json"
SCHEMA = "radicadsac-mc038-v6-tail100-knot-source-witness/1.0"
BLOCKED = "BLOCKED"
OWNER0 = "DELEGATED_V6_CONSTANT_MODULATION"
OWNER1 = "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def pin(path, sha):
    require(path.is_file() and git_blob(path) == sha,
            "pinned file changed: " + str(path))
    return path


def exact(raw):
    require(type(raw) is str, "non-string / binary coefficient")
    result = Fraction(raw)
    require(str(result) == raw, "noncanonical rational coefficient")
    return result


def lower_clamped_two_piece(bs, expected_degree):
    """Independent degree-0/1 Bernstein endpoint replay from original knots."""
    require(type(bs) is dict and set(bs) == {"degree", "knots", "controls"},
            "unsupported original B-spline record")
    degree = bs["degree"]
    require(type(degree) is int and degree == expected_degree, "changed spline degree")
    expected_knots = (["0"] * (degree + 1) + ["1"] * (degree + 1) +
                      ["2"] * (degree + 1))
    require(bs["knots"] == expected_knots, "changed clamped original source knots")
    controls = [exact(v) for v in bs["controls"]]
    require(len(controls) == 2 * (degree + 1), "changed B-spline controls")
    if degree == 0:
        return ((controls[0], controls[0]), (controls[1], controls[1]))
    return ((controls[0], controls[1]), (controls[2], controls[3]))


def piecewise_source(row):
    """Reject every original source or historical-owner change before the theorem."""
    require(type(row) is dict and
            set(row) == {"id", "origin", "kind", "spec", "expected"},
            "unexpected historical source record")
    require(row["id"] == CASE_ID and row["kind"] == "COMPOSITE_TAIL" and
            row["origin"] == "verify_pb00701_v7", "source identity/provenance changed")
    exp = row["expected"]
    require(exp == {
        "id": CASE_ID,
        "observed": {
            "status": "BLOCKED",
            "spans": [[OWNER0, "CERTIFIED", None],
                      [OWNER1, "BLOCKED", "V27_CHILD_NOT_CERTIFIED"]]
        },
        "v54_disposition": BLOCKED
    }, "historical v54 route/refusal changed")
    spec = row["spec"]
    require(type(spec) is dict and set(spec) == {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"
    }, "original source grammar/fields changed")
    require(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
            spec["source_parameter_id"] == "source-time-t",
            "original source provenance changed")
    require(tuple(exact(spec[k]) for k in
                  ("parameter_lo", "parameter_hi", "phase_turn_offset",
                   "phase_turn_rate")) ==
            (Fraction(0), Fraction(2), Fraction(0), Fraction(1, 4)),
            "source interval or true global phase law changed")
    require(spec["sin_splines"] == {} and
            type(spec["cos_splines"]) is dict and
            set(spec["cos_splines"]) == {"0", "1"},
            "harmonic inventory/source phase changed")
    c0 = lower_clamped_two_piece(spec["cos_splines"]["0"], 1)
    c1 = lower_clamped_two_piece(spec["cos_splines"]["1"], 0)
    require(c0 == ((Fraction(0), Fraction(0)),
                   (Fraction(0), Fraction(100))) and
            c1 == ((Fraction(1), Fraction(1)),
                   (Fraction(1), Fraction(1))),
            "original two-span physical coefficients changed")
    raw = json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256,
            "canonical original source SHA-256 mismatch")
    # Degree-1 fully clamped Bernstein interpolation makes the two C0 pieces
    # 0 and 100*(t-1); degree-0 C1 is exactly 1 in both pieces.
    return {"first_c0": c0[0], "tail_c0": c0[1],
            "first_c1": c1[0], "tail_c1": c1[1],
            "tail_slope": c0[1][1] - c0[1][0]}


def strict_tail_lower_bound(slope):
    """Sufficient condition from sin(x) <= x and 0 < pi < 4.

    For t = 1 + x, x in (0,1], F = slope*x - sin(pi*x/2)
    >= (slope - pi/2)*x > (slope-2)*x > 0.
    Refuse weak slopes; refusal does not assert a negative physical function.
    """
    require(type(slope) is Fraction, "nonexact tail slope")
    require(slope > 2, "RESOURCE_REFUSAL: insufficient positive tail slope")
    return slope - 2


def load_frozen():
    pin(HERE / "pb00701-finite-owner-corpus-v54.json", CORPUS_BLOB)
    pin(HERE / "verify_pb00701_post_v54_frontier.py", AUDITOR_BLOB)
    pin(ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json",
        DOMAIN_BLOB)
    pin(ROOT / "handoffs/current-authority.json", AUTH_BLOB)
    import verify_pb00701_post_v54_frontier as audit
    corpus, inventory, boundary = audit.inputs()
    census = audit.audit(corpus, inventory, boundary)
    require(census["cases"] == 121 and
            census["v54_dispositions"]["BLOCKED"] == 20 and
            census["v54_dispositions"][
                "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
            "frozen historical census drifted")
    domain = json.loads((ROOT / "research/machining-completeness/tasks/MC-002/"
                         "domain-contract-v1.json").read_text())
    authority = json.loads((ROOT / "handoffs/current-authority.json").read_text())
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "26-operation denominator changed")
    require(authority["production_authorized"] is False and
            authority["capability_status"] == "NOT_ESTABLISHED",
            "programme authority illegally promoted")
    rows = [r for r in corpus["cases"] if r["id"] == CASE_ID]
    require(len(rows) == 1, "missing or duplicate historical source")
    return census, rows[0]


def source_proof(row):
    data = piecewise_source(row)
    slope = data["tail_slope"]
    margin = strict_tail_lower_bound(slope)
    require(slope == 100 and margin == 98, "unexpected physical slope bound")
    # F_0(t) = cos(pi*t/2), 0<=t<=1: strictly positive before t=1.
    # At t=1, cos(pi/2)=0 and left derivative = -pi/2 != 0.
    # F_1(1+x) = slope*x - sin(pi*x/2), 0<=x<=1:
    # F_1 > margin*x for x>0; right derivative slope-pi/2 > margin>0.
    # Thus the two actual one-sided first-order zeros share precisely
    # one original-source knot; their signs are both positive.
    return {
        "status": "EXACT_FROZEN_SOURCE_KNOT_TOUCHING_RESEARCH",
        "original_source_sha256": SOURCE_SHA256,
        "original_source_parameter": "source-time-t",
        "original_source_interval": ["0", "2"],
        "phase_turn_offset": "0",
        "phase_turn_rate": "1/4",
        "piecewise_physical_formula": [
            "cos(pi*t/2) on 0<=t<=1",
            "100*(t-1)+cos(pi*t/2) on 1<=t<=2"
        ],
        "lemma": "0<pi<4; for 0<x<=1, sin(pi*x/2)<=pi*x/2<2*x",
        "strict_second_span_lower_slope": str(margin),
        "exact_exterior_values": {"at_0": "1", "at_2": "99"},
        "physical_root_count_closed": 1,
        "physical_root_count_strict_source_interior": 1,
        "span_open_root_counts": [0, 0],
        "source_knot": {
            "coordinate": "1", "exact_zero": True,
            "distinct_physical_event_count": 1,
            "left_one_sided_vanishing_order": 1,
            "right_one_sided_vanishing_order": 1,
            "left_inward_sign": "POSITIVE",
            "right_inward_sign": "POSITIVE",
            "event": "TOUCHING",
            "global_smooth_multiplicity_claimed": False
        },
        "maximal_open_physical_signs": ["POSITIVE", "POSITIVE"],
        "historical_v54_route_repaired": False,
        "general_v27_child_route_proved": False
    }


def expected_machine_record():
    census, row = load_frozen()
    return {
        "schema": SCHEMA,
        "task": "MC-038",
        "claim": "PB-007-01 bounded source-specific analytic knot/event proof only",
        "evidence_class": "DETERMINISTIC_MODEL",
        "original_corpus_git_blob": CORPUS_BLOB,
        "original_source_case_id": CASE_ID,
        "preregistered_issue_comment": 6523853415,
        "historical_v54_baseline": {
            "source_count": census["cases"],
            "uncertified_route_cases": 20,
            "missing_ordered_span_premise_cases": 30
        },
        "supplemental_exact_source_research": {
            "newly_proved_source_cases": [CASE_ID],
            "independently_unsupported_uncertified_route_cases_if_admitted": 19,
            "unresolved_missing_ordered_span_premise_cases": 30,
            "total_original_source_cases": 121,
            "historical_v54_dispositions_mutated": False,
            "historical_v54_route_pass_claimed": False
        },
        "proof": source_proof(row),
        "global_claims": {
            "pb00701_closed": False, "pb00702_closed": False,
            "pb00703_closed": False, "pb00704_closed": False,
            "mc_b_established": False, "mc1_established": False,
            "native_material_or_step_qualified": False,
            "production_authorized": False
        }
    }


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = expected_machine_record()
        cls.frozen = load_frozen()[1]

    def test_exact_original_source_and_historical_refusal(self):
        self.assertEqual(self.record["proof"]["original_source_sha256"], SOURCE_SHA256)
        self.assertEqual(self.frozen["expected"]["v54_disposition"], "BLOCKED")
        self.assertEqual(self.frozen["expected"]["observed"]["spans"][1][2],
                         "V27_CHILD_NOT_CERTIFIED")

    def test_unique_source_knot_touching_and_side_orders(self):
        p = self.record["proof"]
        self.assertEqual(p["span_open_root_counts"], [0, 0])
        self.assertEqual(p["physical_root_count_strict_source_interior"], 1)
        self.assertEqual(p["source_knot"]["coordinate"], "1")
        self.assertEqual([p["source_knot"]["left_one_sided_vanishing_order"],
                          p["source_knot"]["right_one_sided_vanishing_order"]], [1, 1])
        self.assertEqual(p["maximal_open_physical_signs"],
                         ["POSITIVE", "POSITIVE"])
        self.assertEqual(p["source_knot"]["event"], "TOUCHING")
        self.assertFalse(p["source_knot"]["global_smooth_multiplicity_claimed"])

    def test_exact_bounds_and_endpoint_values(self):
        self.assertEqual(strict_tail_lower_bound(Fraction(100)), 98)
        self.assertEqual(strict_tail_lower_bound(Fraction(3)), 1)
        self.assertEqual(strict_tail_lower_bound(Fraction(2000001, 1000000)),
                         Fraction(1, 1000000))
        self.assertEqual(self.record["proof"]["exact_exterior_values"],
                         {"at_0": "1", "at_2": "99"})

    def test_insufficient_slope_does_not_imply_positive_tail(self):
        for slope in [Fraction(0), Fraction(1, 2), Fraction(1), Fraction(2)]:
            with self.subTest(slope=slope), self.assertRaisesRegex(
                    ValueError, "RESOURCE_REFUSAL"):
                strict_tail_lower_bound(slope)
        # Actual counterexample to extending the method to ANY positive ramp:
        # slope=1/2 has F(1)=0 and F(2)=-1/2; cannot be positive on (1,2].
        self.assertEqual(Fraction(1, 2) - 1, Fraction(-1, 2))

    def test_mutated_source_phase_knots_harmonics_and_slope_rejected(self):
        changes = [
            lambda r: r["spec"].__setitem__("phase_turn_rate", "0"),
            lambda r: r["spec"].__setitem__("phase_turn_offset", "1/4"),
            lambda r: r["spec"].__setitem__("parameter_hi", "3"),
            lambda r: r["spec"].__setitem__("source_parameter_id", "other"),
            lambda r: r["spec"]["cos_splines"]["0"]["controls"].__setitem__(3, "1/2"),
            lambda r: r["spec"]["cos_splines"]["0"]["knots"].__setitem__(3, "3/2"),
            lambda r: r["spec"]["cos_splines"]["1"]["controls"].__setitem__(0, "2"),
            lambda r: r["spec"]["cos_splines"]["1"].__setitem__("degree", 1),
            lambda r: r["spec"]["sin_splines"].__setitem__(
                "1", {"degree": 0, "knots": ["0", "1", "2"], "controls": ["1", "1"]}),
            lambda r: r["spec"].__setitem__("parameter_projection", "source-time-t"),
            lambda r: r["spec"]["cos_splines"]["0"]["controls"].__setitem__(0, 0),
        ]
        for change in changes:
            r = copy.deepcopy(self.frozen)
            change(r)
            with self.subTest(change=str(change)), self.assertRaises(ValueError):
                source_proof(r)

    def test_forged_case_owner_and_disposition_rejected(self):
        for mutate in [
            lambda r: r.__setitem__("id", "OTHER"),
            lambda r: r.__setitem__("kind", "HARVESTED"),
            lambda r: r.__setitem__("origin", "other"),
            lambda r: r["expected"].__setitem__("v54_disposition", "CERTIFIED"),
            lambda r: r["expected"]["observed"]["spans"][1].__setitem__(1, "CERTIFIED"),
            lambda r: r["expected"]["observed"]["spans"][1].__setitem__(2, None),
            lambda r: r["expected"]["observed"]["spans"].pop(),
        ]:
            r = copy.deepcopy(self.frozen)
            mutate(r)
            with self.assertRaises(ValueError):
                source_proof(r)

    def test_machine_report_and_histogram_are_exact(self):
        actual = json.loads(MACHINE.read_text(encoding="utf-8"))
        self.assertEqual(actual, self.record)
        self.assertEqual(self.record["historical_v54_baseline"],
                         {"source_count":121, "uncertified_route_cases":20,
                          "missing_ordered_span_premise_cases":30})
        self.assertEqual(self.record["supplemental_exact_source_research"][
            "independently_unsupported_uncertified_route_cases_if_admitted"], 19)

    def test_forged_machine_field_rejected(self):
        canonical = self.record
        for field, key, value in [
            ("proof", "physical_root_count_closed", 2),
            ("proof", "maximal_open_physical_signs", ["POSITIVE", "NEGATIVE"]),
            ("historical_v54_baseline", "uncertified_route_cases", 19),
            ("supplemental_exact_source_research",
             "historical_v54_dispositions_mutated", True),
            ("global_claims", "pb00701_closed", True),
            ("global_claims", "production_authorized", True),
        ]:
            mutated = copy.deepcopy(canonical)
            mutated[field][key] = value
            with self.subTest(field=field, key=key):
                self.assertNotEqual(mutated, expected_machine_record())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        data = expected_machine_record()
        require(json.loads(MACHINE.read_text(encoding="utf-8")) == data,
                "machine-readable source evidence mismatch")
        print(json.dumps(data, sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
