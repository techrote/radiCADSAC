#!/usr/bin/env python3
"""MC-038: source-specific full physical root proof for one frozen V9/V43 case.

DETERMINISTIC_MODEL only; historical V54 refusals and PB-007/MC-B gates unchanged.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
CASE_ID = "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100"
FIRST_OWNER = "PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO"
TAIL_OWNER = "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"
TAIL_REASON = "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"
CORPUS_SHA = "5841c331579489b25caef38cd412bdbf286f9134"
AUDIT_SHA = "12c6efeb667a954ffc5a7e27849ae815d466580a"
DOMAIN_SHA = "23de82f5240a72509f7afe4acd5948b65bc4ff13"
AUTH_SHA = "fa0233323a0804d8a5d3eb7cd892a274a6173fab"
SOURCE_SHA256 = "cc13a39582060e763c573f2665b3ea3b6dfe8b76a6cb0fb77a7b0ec90cf6253a"
SCHEMA = "radicadsac-mc038-pb00701-v9-v43-full-original-source/1.0"
REPORT = HERE / "pb00701-v9-v43-full-source-witness.json"
MAX_REPORT_BYTES = 65536


def require(ok, why):
    if not ok:
        raise ValueError(why)


def blob(path):
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


def pinned(path, digest):
    require(path.is_file() and blob(path) == digest, "pinned source drift: " + str(path))
    return path


def exact(value):
    require(type(value) is str, "binary/typed rational refused")
    result = Q(value)
    require(str(result) == value, "noncanonical rational refused")
    return result


def original_two_pieces(spec, degree):
    """Independent degree-0/1 clamped Bernstein lowering, original t coordinate."""
    require(type(spec) is dict and set(spec) == {"degree", "knots", "controls"},
            "unexpected source spline field")
    require(type(spec["degree"]) is int and spec["degree"] == degree,
            "wrong source spline degree")
    require(spec["knots"] == (["0"] * (degree+1) +
                             ["1"] * (degree+1) + ["2"] * (degree+1)),
            "wrong source knots")
    controls = [exact(v) for v in spec["controls"]]
    require(len(controls) == 2*(degree+1), "wrong source control count")
    if degree == 0:
        return ((controls[0], controls[0]), (controls[1], controls[1]))
    return ((controls[0], controls[1]), (controls[2], controls[3]))


def check_original(row):
    require(type(row) is dict and set(row) ==
            {"id", "origin", "kind", "spec", "expected"},
            "unreviewed original case fields")
    require(row["id"] == CASE_ID and row["origin"] == "verify_pb00701_v10" and
            row["kind"] == "COMPOSITE_TAIL", "frozen source identity changed")
    require(row["expected"] == {
        "id": CASE_ID, "observed": {"status": "BLOCKED", "spans": [
            [FIRST_OWNER, "CERTIFIED", None],
            [TAIL_OWNER, "BLOCKED", TAIL_REASON]]},
        "v54_disposition": "BLOCKED"
    }, "historical V9/V43 producer/refusal changed")
    s = row["spec"]
    require(type(s) is dict and set(s) ==
            {"grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
             "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"},
            "unreviewed original-source field")
    require(s["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
            s["source_parameter_id"] == "source-time-t", "source grammar/ID drift")
    require(tuple(exact(s[k]) for k in
                  ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate"))
            == (Q(0), Q(2), Q(0), Q(1,8)), "wrong source interval/affine phase")
    require(type(s["cos_splines"]) is dict and
            set(s["cos_splines"]) == {"0", "1"} and
            type(s["sin_splines"]) is dict and
            set(s["sin_splines"]) == {"1"}, "original harmonics changed")
    c0 = original_two_pieces(s["cos_splines"]["0"], 1)
    c1 = original_two_pieces(s["cos_splines"]["1"], 1)
    s1 = original_two_pieces(s["sin_splines"]["1"], 0)
    require(c0 == ((Q(0),Q(0)),(Q(0),Q(100))) and
            c1 == ((Q(-1,2),Q(1,2)),(Q(1,2),Q(1,2))) and
            s1 == ((Q(1),Q(1)),(Q(1),Q(1))),
            "original physical coefficients changed")
    require(all(p[0][1] == p[1][0] for p in (c0,c1,s1)),
            "source-knot continuity not proven")
    raw = json.dumps(s, sort_keys=True, separators=(",",":")).encode()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256,
            "original source SHA-256 changed")
    return (c0,c1,s1)


def exact_analytic_bounds():
    """Exact rational parts of the original-function analytic proof.

    For t=1/4, z=pi/16<11/56. Classical sin(z)<z and cos(z)>1-z*z/2
    imply tan(z)<1232/6151<1/4, hence F(1/4)<0.
    For t=1/3, tan(pi/12)>pi/12>1/4>1/6, hence F(1/3)>0.
    On [0,1], cos(theta)>=sin(theta)>=0 (theta=pi*t/4), so
      F'=cos(theta)+(pi/4)*(cos(theta)-(t-1/2)*sin(theta))
        >=(1+pi/8)*cos(theta)>0.
    On [1,2], theta in [pi/4,pi/2], sin(theta)>=sqrt2/2>1/2,
    cos(theta)>=0, C0=100*(t-1)>=0, so F>1/2 everywhere.
    """
    r = Q(22,7)/16
    ub = r/(1-r*r/2)
    require(r == Q(11,56) and ub == Q(1232,6151) and
            ub < Q(1,4), "t=1/4 strict sign bound failed")
    require(Q(3)/12 == Q(1,4) and Q(1,4)>Q(1,6) and
            Q(1)-Q(1,2)>0, "t=1/3 / derivative bound failed")
    return {"pi_lower":"3","pi_upper":"22/7",
            "quarter_angle_tan_upper":"1232/6151",
            "first_strict_negative_source_witness":"1/4",
            "first_strict_positive_source_witness":"1/3",
            "first_span_derivative":"STRICTLY_POSITIVE",
            "V43_tail_physical_sign":"STRICTLY_POSITIVE"}


def frozen_case():
    pinned(HERE/"pb00701-finite-owner-corpus-v54.json",CORPUS_SHA)
    pinned(HERE/"verify_pb00701_post_v54_frontier.py",AUDIT_SHA)
    pinned(ROOT/"research/machining-completeness/tasks/MC-002/domain-contract-v1.json",
           DOMAIN_SHA)
    pinned(ROOT/"handoffs/current-authority.json",AUTH_SHA)
    import verify_pb00701_post_v54_frontier as auditor
    corpus, inventory, boundary = auditor.inputs()
    census = auditor.audit(corpus, inventory, boundary)
    require(census["cases"]==121 and
            census["v54_dispositions"]["BLOCKED"]==20 and
            census["v54_dispositions"][
                "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"]==30,
            "frozen historical v54 census drift")
    require(sum(any(span == [TAIL_OWNER,"BLOCKED",TAIL_REASON]
                    for span in c["expected"]["observed"]["spans"])
                for c in corpus["cases"]) == 11, "V43 historical refusal count drift")
    rows=[c for c in corpus["cases"] if c["id"]==CASE_ID]
    require(len(rows)==1,"missing/duplicate frozen source")
    domain=json.loads((ROOT/"research/machining-completeness/tasks/MC-002/"
                       "domain-contract-v1.json").read_text())
    auth=json.loads((ROOT/"handoffs/current-authority.json").read_text())
    require(len(domain["coverage_rule"]["required_operation_ids"])==26,
            "26-operation domain weakened")
    require(auth["capability_status"]=="NOT_ESTABLISHED" and
            auth["production_authorized"] is False, "authority promoted")
    return rows[0]


def source_proof(row):
    check_original(row)
    bounds=exact_analytic_bounds()
    # First span strictly increasing with exact opposite signs in (1/4,1/3),
    # hence exactly one simple root. Knot t=1 nonzero. Second closed span
    # strictly positive, including both exteriors and source knot.
    return {
        "source_case_id":CASE_ID,"source_sha256":SOURCE_SHA256,
        "status":"COMPLETE_FROZEN_ORIGINAL_SOURCE_SIMPLE_CROSSING_RESEARCH",
        "original_source_parameter":"source-time-t","interval":["0","2"],
        "phase_turn_law":{"offset":"0","rate":"1/8"},
        "exact_piecewise_functions":[
            "(t-1/2)*cos(pi*t/4)+sin(pi*t/4)",
            "100*(t-1)+(1/2)*cos(pi*t/4)+sin(pi*t/4)"],
        "analytic_bounds":bounds,
        "true_source_knot":{"at":"1","is_physical_zero":False,
                            "is_exactly_continuous":True,
                            "source_sign":"POSITIVE"},
        "span_open_root_counts":[1,0],
        "whole_source_open_root_count":1,
        "whole_source_exterior_values":{"at_0":"-1/2","at_2":"101"},
        "only_physical_event":{"kind":"IMPLICIT_UNIQUE_SOURCE_ROOT",
                               "strict_bracket":["1/4","1/3"],
                               "multiplicity":1,"event":"CROSSING",
                               "left_sign":"NEGATIVE","right_sign":"POSITIVE",
                               "algebraic_or_rational_root_claimed":False},
        "maximal_source_sign_cells":["NEGATIVE","POSITIVE"],
        "historical_v54_admitted":False,"general_V43_route_proved":False}


def expected_report():
    p=source_proof(frozen_case())
    return {
        "schema":SCHEMA,"task":"MC-038","evidence_class":"DETERMINISTIC_MODEL",
        "preregistration_issue_324_comment":6531114353,
        "frozen_corpus_git_blob":CORPUS_SHA,"case_id":CASE_ID,
        "historical_v54_census":{"total":121,"blocked_routes":20,
                                  "missing_ordered_premises":30},
        "single_source_overlay":{"source_specific_witnesses_added":[CASE_ID],
                                 "historical_route_cases_without_this_one_new_witness":19,
                                 "missing_ordered_premises":30,
                                 "total_frozen_sources":121,
                                 "historical_v54_changed":False,
                                 "exhaustive_combined_post_v54_tally_claimed":False},
        "proof":p,
        "gates":{"PB-007-01":"OPEN","PB-007-02":"OPEN",
                 "PB-007-03":"OPEN_PROPAGATED","PB-007-04":"OPEN_PROPAGATED",
                 "MC-B":"NOT_ESTABLISHED","MC-1":"NOT_ESTABLISHED",
                 "native_material_or_STEP_qualified":False,
                 "production_authorized":False}}


def validate_report(report):
    require(type(report) is dict,"untrusted report not object")
    raw=json.dumps(report, sort_keys=True, separators=(",",":"), allow_nan=False)
    require(len(raw.encode())<=MAX_REPORT_BYTES,
            "RESOURCE_REFUSAL: untrusted report exceeds 64KiB")
    require(report==expected_report(),"forged/missing report evidence or false gate")
    return True


class TestOriginalSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row=frozen_case()
        cls.report=expected_report()

    def test_original_source_and_refusal_identity(self):
        self.assertEqual(self.row["expected"]["v54_disposition"],"BLOCKED")
        self.assertEqual(self.row["expected"]["observed"]["spans"][1],
                         [TAIL_OWNER,"BLOCKED",TAIL_REASON])
        self.assertEqual(check_original(self.row)[1][0],(Q(-1,2),Q(1,2)))

    def test_exact_root_bracket_and_no_false_algebraic_coordinate(self):
        self.assertEqual(exact_analytic_bounds()["quarter_angle_tan_upper"],
                         "1232/6151")
        p=self.report["proof"]
        self.assertEqual(p["span_open_root_counts"],[1,0])
        self.assertEqual(p["whole_source_open_root_count"],1)
        self.assertEqual(p["only_physical_event"]["strict_bracket"],["1/4","1/3"])
        self.assertEqual(p["only_physical_event"]["multiplicity"],1)
        self.assertFalse(p["only_physical_event"]["algebraic_or_rational_root_claimed"])

    def test_physical_source_knot_exteriors_and_signs(self):
        p=self.report["proof"]
        self.assertTrue(p["true_source_knot"]["is_exactly_continuous"])
        self.assertFalse(p["true_source_knot"]["is_physical_zero"])
        self.assertEqual(p["whole_source_exterior_values"],
                         {"at_0":"-1/2","at_2":"101"})
        self.assertEqual(p["maximal_source_sign_cells"],
                         ["NEGATIVE","POSITIVE"])

    def test_mutated_source_controls_phases_and_identity_zero_refuse(self):
        changes=[
            lambda r:r["spec"].__setitem__("phase_turn_offset","1/4"),
            lambda r:r["spec"].__setitem__("phase_turn_rate","-1/8"),
            lambda r:r["spec"].__setitem__("parameter_hi","3"),
            lambda r:r["spec"].__setitem__("source_parameter_id","forged"),
            lambda r:r["spec"]["cos_splines"]["0"]["controls"].__setitem__(3,"99"),
            lambda r:r["spec"]["cos_splines"]["1"]["controls"].__setitem__(0,"0"),
            lambda r:r["spec"]["sin_splines"]["1"]["controls"].__setitem__(0,"0"),
            lambda r:r["spec"]["cos_splines"]["1"]["knots"].__setitem__(3,"3/2"),
            lambda r:r["spec"]["cos_splines"]["1"].__setitem__("degree",0),
            lambda r:r["spec"]["sin_splines"]["1"]["controls"].__setitem__(0,1.0),
            lambda r:r["spec"].__setitem__("parameter_projection","source-time-t"),
        ]
        for mutate in changes:
            c=copy.deepcopy(self.row);mutate(c)
            with self.subTest(mutate=str(mutate)),self.assertRaises(ValueError):
                source_proof(c)
        identity=copy.deepcopy(self.row)
        for group in ("cos_splines","sin_splines"):
            for piece in identity["spec"][group].values():
                piece["controls"]=["0"]*len(piece["controls"])
        with self.assertRaises(ValueError):
            source_proof(identity)

    def test_owner_case_and_historical_disposition_mutations_refuse(self):
        changes=[
            lambda r:r.__setitem__("id","another-id"),
            lambda r:r.__setitem__("origin","another-origin"),
            lambda r:r.__setitem__("kind","HARVESTED"),
            lambda r:r["expected"].__setitem__("v54_disposition","CERTIFIED"),
            lambda r:r["expected"]["observed"]["spans"][1].__setitem__(2,None),
            lambda r:r["expected"]["observed"]["spans"].pop(),
        ]
        for mutate in changes:
            c=copy.deepcopy(self.row);mutate(c)
            with self.assertRaises(ValueError):
                source_proof(c)

    def test_census_denominator_and_protected_gates(self):
        x=self.report
        self.assertEqual(x["historical_v54_census"],
                         {"total":121,"blocked_routes":20,"missing_ordered_premises":30})
        self.assertEqual(x["single_source_overlay"][
            "historical_route_cases_without_this_one_new_witness"],19)
        self.assertFalse(x["single_source_overlay"][
            "exhaustive_combined_post_v54_tally_claimed"])
        self.assertEqual(x["gates"]["MC-B"],"NOT_ESTABLISHED")
        self.assertFalse(x["gates"]["production_authorized"])

    def test_machine_report_and_forged_claims_fail_closed(self):
        canonical=json.loads(REPORT.read_text())
        self.assertTrue(validate_report(canonical))
        for section,key,forgery in [
            ("proof","whole_source_open_root_count",2),
            ("proof","maximal_source_sign_cells",["POSITIVE"]),
            ("historical_v54_census","blocked_routes",19),
            ("single_source_overlay","exhaustive_combined_post_v54_tally_claimed",True),
            ("gates","MC-B","ESTABLISHED"),
            ("gates","production_authorized",True),
        ]:
            altered=copy.deepcopy(canonical)
            altered[section][key]=forgery
            with self.subTest(section=section,key=key),self.assertRaises(ValueError):
                validate_report(altered)
        altered=copy.deepcopy(canonical)
        altered["large_blob"]="x"*(MAX_REPORT_BYTES+1)
        with self.assertRaisesRegex(ValueError,"RESOURCE_REFUSAL"):
            validate_report(altered)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--contract",action="store_true")
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if not args.contract and not args.self_test:
        p.error("specify --contract and/or --self-test")
    if args.contract:
        actual=json.loads(REPORT.read_text())
        validate_report(actual)
        print(json.dumps(actual,sort_keys=True))
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(TestOriginalSource)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__=="__main__":
    main()
