#!/usr/bin/env python3
"""Independent adversarial contract tests for exact moving square-source proof."""
import copy
import hashlib
import json
import tempfile
import unittest
from fractions import Fraction as R
from pathlib import Path

import pb00701_two_span_moving_square_components as m

HERE=Path(__file__).resolve().parent
FROZEN=HERE/"pb00701-finite-owner-corpus-v54.json"
V2=HERE/"pb00701-post-v54-evidence-reconciliation-v2.json"
CORPUS_BLOB="5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB="e52d3baf3692a011cf86234eeaa992ef407d99fd"
ANCHOR_ID="composite:DELEGATED_V6_CONSTANT_MODULATION:tail0"
ANCHOR_SHA="9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1"


def make_quadratic_controls(p,q):
    # Affine P(u),Q(u) defined on the physical Bernstein span u in [0,1].
    p0,p1=p
    q0,q1=q
    c0=[(p0*p0+q0*q0)/2, p0*p1+q0*q1, (p1*p1+q1*q1)/2]
    c1=[(p0*p0-q0*q0)/2, p0*p1-q0*q1, (p1*p1-q1*q1)/2]
    return [[a,a+b/2,a+b+c] for a,b,c in (c0,c1)]


def source(left,right,rate=R(1),offset=R(0),interval=(R(0),R(2)),knot=R(1)):
    first=make_quadratic_controls(*left)
    second=make_quadratic_controls(*right)
    assert all(first[j][-1]==second[j][0] for j in range(2)), "noncontinuous proposed source"
    lo,hi=interval
    knots=list(map(str,[lo]*3+[knot]*2+[hi]*3))
    channels={}
    for h in range(2):
        controls=first[h]+second[h][1:]
        channels[str(h)]={"degree":2,"knots":knots,
                          "controls":list(map(str,controls))}
    return {"grammar":m.GRAMMAR,"source_parameter_id":"source-time-t",
            "parameter_lo":str(lo),"parameter_hi":str(hi),
            "phase_turn_offset":str(offset),"phase_turn_rate":str(rate),
            "cos_splines":channels,"sin_splines":{}}


Z=(R(0),R(0))
ONE=(R(1),R(0))
U=(R(0),R(1))
UM1=(R(-1),R(1))
ONE_MINUS_U=(R(1),R(-1))


def census():
    def git_blob(p):
        raw=p.read_bytes()
        return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
    assert git_blob(FROZEN)==CORPUS_BLOB
    assert git_blob(V2)==V2_BLOB
    corpus=json.loads(FROZEN.read_text(encoding="utf-8"))
    registry=json.loads(V2.read_text(encoding="utf-8"))
    rows=corpus["cases"]
    original={x["id"]:x for x in rows}
    assert len(rows)==121 and len(original)==121
    blocked={i for i,c in original.items()
             if c["expected"]["v54_disposition"]=="BLOCKED"}
    missing={i for i,c in original.items()
             if c["expected"]["v54_disposition"]==
             "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
    assert len(blocked)==20 and len(missing)==30
    assert len(registry["source_cases"])==50
    evidence={r["case_id"]:r for r in registry["source_cases"]}
    assert len(evidence)==50 and set(evidence)==blocked|missing
    for case_id,row in evidence.items():
        orig=original[case_id]
        assert row["source_sha256"]==hashlib.sha256(m.encode(orig["spec"])).hexdigest()
        assert row["historical_v54_disposition"]==orig["expected"]["v54_disposition"]
        assert row["origin"]==orig["origin"]
        assert row["source_parameter_id"]==orig["spec"]["source_parameter_id"]
        assert row["source_interval"]==[
            orig["spec"]["parameter_lo"],orig["spec"]["parameter_hi"]]
        assert row["phase_turn_law"]=={
            "offset":orig["spec"]["phase_turn_offset"],
            "rate":orig["spec"]["phase_turn_rate"]}
        assert row["registered_evidence_level"]=="COMPLETE_SOURCE_SPECIFIC"
        assert row["evidence"]["source_sha256"]==row["source_sha256"]
    assert evidence[ANCHOR_ID]["source_sha256"]==ANCHOR_SHA
    return {"frozen_original_sources":len(rows),
            "historical_route_refusals":len(blocked),
            "historical_missing_ordered_premises":len(missing),
            "complete_source_specific_witnesses":len(evidence)}


class ExactOriginalTwoSpanMovingSquareTests(unittest.TestCase):
    def checked(self,s):
        r=m.attempt(s)
        self.assertEqual(r["status"],m.STATUS,r)
        self.assertEqual(m.validate_report(s,copy.deepcopy(r)),r)
        self.assertFalse(r["pb00701_certified"])
        self.assertFalse(r["mc_b_established"])
        self.assertFalse(r["mc1_established"])
        self.assertFalse(r["production_authorized"])
        return r

    def refused(self,s,expected_status="BLOCKED"):
        r=m.attempt(s)
        self.assertEqual(r["status"],expected_status,r)
        self.assertFalse(r["is_truth_value"])
        self.assertFalse(r["pb00701_certified"])
        self.assertFalse(r["production_authorized"])
        return r

    def test_01_moving_left_continuum_plus_isolated_right_exterior(self):
        s=source((Z,Z),(Z,U))
        r=self.checked(s)
        self.assertEqual(r["source_sha256"],
                         "f832ada1c7da5c155626857b4b02b252d721275ca56d29a45e5f310e8d96957d")
        self.assertEqual([x["interval"] for x in r["maximal_closed_zero_intervals"]],
                         [["0","1"]])
        self.assertEqual([(x["coordinate"],x["left_order"],x["right_order"])
                          for x in r["isolated_zero_points"]],[("2",2,None)])
        self.assertEqual(r["maximal_closed_zero_intervals"][0][
                         "right_boundary_outward_order"],4)
        self.assertEqual(r["nonzero_sign_cells"],[{
            "left":"1","right":"2","left_included":False,
            "right_included":False,"sign":"POSITIVE"}])
        self.assertFalse(r["finite_total_root_cardinality"])

    def test_02_right_continuum_left_exterior_isolated(self):
        r=self.checked(source((Z,UM1),(Z,Z)))
        self.assertEqual([x["interval"] for x in r["maximal_closed_zero_intervals"]],
                         [["1","2"]])
        self.assertEqual([x["coordinate"] for x in r["isolated_zero_points"]],["0"])
        self.assertEqual(r["maximal_closed_zero_intervals"][0][
                         "left_boundary_outward_order"],4)

    def test_03_whole_source_identity(self):
        r=self.checked(source((Z,Z),(Z,Z)))
        self.assertEqual([x["interval"] for x in r["maximal_closed_zero_intervals"]],
                         [["0","2"]])
        self.assertEqual(r["isolated_zero_points"],[])
        self.assertEqual(r["nonzero_sign_cells"],[])

    def test_04_true_source_knot_distinct_sided_2_and_4(self):
        r=self.checked(source((UM1,UM1),(Z,U)))
        self.assertEqual([x["coordinate"] for x in r["isolated_zero_points"]],
                         ["1","2"])
        e=r["isolated_zero_points"][0]
        self.assertTrue(e["true_source_knot"])
        self.assertEqual([e["left_order"],e["right_order"]],[2,4])
        self.assertFalse(e["global_smooth_knot_multiplicity_claimed"])
        self.assertEqual(len(r["maximal_closed_zero_intervals"]),0)

    def test_05_nonzero_knot_bridges_positive_cells(self):
        r=self.checked(source((U,U),(ONE_MINUS_U,ONE_MINUS_U)))
        self.assertEqual([x["coordinate"] for x in r["isolated_zero_points"]],
                         ["0","2"])
        self.assertEqual(r["nonzero_sign_cells"],[{
            "left":"0","right":"2","left_included":False,
            "right_included":False,"sign":"POSITIVE"}])
        self.assertTrue(r["finite_total_root_cardinality"])

    def test_06_exact_arbitrarily_close_rational_roots(self):
        eps=R(1,2**70)
        a=R(1)-eps
        r=self.checked(source((Z,(-a,R(0))),(Z,(-a,R(1)))))
        self.assertEqual([x["coordinate"] for x in r["isolated_zero_points"]],
                         ["0","1",str(R(2)-eps),"2"])
        self.assertEqual(R(2)-R(r["isolated_zero_points"][-2]["coordinate"]),eps)
        self.assertEqual([e["right_order"] for e in r["isolated_zero_points"][:2]],
                         [2,2])

    def test_07_submicroscopic_tangency_not_collapsed_into_endpoint(self):
        eps=R(1,2**80)
        a=R(1)-eps
        p=(R(-1)*a,R(1))
        left=(R(-1)*a,R(0))
        r=self.checked(source((left,left),(p,p)))
        self.assertEqual([x["coordinate"] for x in r["isolated_zero_points"]],
                         [str(R(2)-eps)])
        self.assertEqual(r["isolated_zero_points"][0]["right_order"],2)
        self.assertEqual(r["nonzero_sign_cells"][-1]["right"],"2")
        self.assertTrue(r["nonzero_sign_cells"][-1]["right_included"])

    def test_08_negative_phase_direction(self):
        r=self.checked(source((Z,Z),(Z,U),rate=R(-1),offset=R(1)))
        self.assertEqual([x["interval"] for x in r["maximal_closed_zero_intervals"]],
                         [["0","1"]])
        self.assertEqual([x["coordinate"] for x in r["isolated_zero_points"]],["2"])

    def test_09_nonunit_negative_source_interval(self):
        lo,k,hi=R(-2),R(-1),R(2)
        s=source((Z,Z),(Z,U),rate=R(1),interval=(lo,hi),knot=k)
        r=self.checked(s)
        self.assertEqual(r["true_original_source_knot"],"-1")
        self.assertEqual([x["interval"] for x in r["maximal_closed_zero_intervals"]],
                         [["-2","-1"]])

    def test_10_reject_stationary_phase(self):
        self.refused(source((Z,Z),(Z,U),rate=R(0)))

    def test_11_reject_incompatible_source_knot(self):
        s=source((Z,Z),(Z,U))
        s["cos_splines"]["1"]["knots"][3]="1/2"
        self.refused(s)

    def test_12_reject_sine_and_wrong_harmonic(self):
        s=source((Z,Z),(Z,U))
        s["sin_splines"]["1"]={"degree":2,"knots":s["cos_splines"]["0"]["knots"],
                               "controls":["0"]*5}
        self.refused(s)
        s=source((Z,Z),(Z,U))
        s["cos_splines"]["2"]=s["cos_splines"].pop("1")
        self.refused(s)

    def test_13_reject_nonsquare_source_no_float(self):
        s=source((ONE,ONE),(ONE,ONE))
        # Original H0 controls changed so C0+C1 no longer an affine square.
        s["cos_splines"]["0"]["controls"][0]="2"
        self.refused(s)
        s=source((Z,Z),(Z,U))
        s["cos_splines"]["0"]["controls"][0]=0.0
        self.refused(s)

    def test_14_refuse_too_many_phase_turns_as_nontruth(self):
        s=source((Z,Z),(Z,U),rate=R(1000))
        self.refused(s,expected_status="RESOURCE_REFUSAL")

    def test_15_source_parameter_and_corruption(self):
        s=source((Z,Z),(Z,U))
        s["source_parameter_id"]="carrier-u"
        self.refused(s)
        s=source((Z,Z),(Z,U))
        s["cos_splines"]["0"]["degree"]=1
        self.refused(s)

    def test_16_refuse_forged_report_and_promotion(self):
        s=source((Z,Z),(Z,U))
        r=self.checked(s)
        for key,value in [("source_sha256","f"*64),
                          ("pb00701_certified",True),
                          ("historical_case_ids_newly_closed",[ANCHOR_ID]),
                          ("maximal_closed_zero_intervals",[]),
                          ("nonzero_sign_cells",[])]:
            fake=copy.deepcopy(r)
            fake[key]=value
            self.assertEqual(m.validate_report(s,fake)["status"],"BLOCKED",key)

    def test_17_exact_corpus_and_fifty_witness_custody(self):
        expected={"frozen_original_sources":121,
                  "historical_route_refusals":20,
                  "historical_missing_ordered_premises":30,
                  "complete_source_specific_witnesses":50}
        self.assertEqual(census(),expected)
        frozen=json.loads(FROZEN.read_text())
        evidence=json.loads(V2.read_text())
        self.assertEqual(len({r["id"] for r in frozen["cases"]}),121)
        self.assertEqual(len({r["case_id"] for r in evidence["source_cases"]}),50)
        receipt=json.loads((HERE/"pb00701-two-span-moving-square-components.json")
                           .read_text(encoding="utf-8"))
        self.assertEqual(receipt["frozen_inputs"]["corpus_git_blob"],CORPUS_BLOB)
        self.assertEqual(receipt["frozen_inputs"]["complete_witness_git_blob"],V2_BLOB)
        self.assertEqual(receipt["historical_anchor"]["id"],ANCHOR_ID)
        self.assertEqual(receipt["historical_anchor"]["original_source_sha256"],ANCHOR_SHA)
        self.assertTrue(receipt["historical_anchor"]["existing_complete_witness"])
        for column,value in [("original_sources",121),("route_refusals",20),
                             ("missing_ordered_premises",30),
                             ("complete_source_specific_witnesses",50)]:
            self.assertEqual(receipt["population"]["before"][column],value)
            self.assertEqual(receipt["population"]["after"][column],value)
            self.assertEqual(receipt["population"]["delta"][column],0)
        self.assertEqual(receipt["population"]["newly_resolved_historical_case_ids"],[])
        self.assertEqual(receipt["bounded_proof"]["bounded_input_rational_bits"],m.MAX_BITS)
        self.assertEqual(receipt["bounded_proof"]["bounded_absolute_phase_turns"],
                         m.MAX_ABS_PHASE_TURNS)
        self.assertEqual(receipt["prospective_examples"][0]["source_sha256"],
                         self.checked(source((Z,Z),(Z,U)))["source_sha256"])
        self.assertEqual(receipt["evidence_class"],"DETERMINISTIC_MODEL")
        self.assertEqual(receipt["claim_kind"],
                         "BOUNDED_PROSPECTIVE_SOURCE_METHOD_NOT_A_B_OR_C")
        for key in ("mc_b","mc1"):
            self.assertEqual(receipt["gates"][key],"NOT_ESTABLISHED")
        self.assertFalse(receipt["gates"]["production_authorized"])
        self.assertFalse(receipt["gates"]["native_geometry_qualified"])
        self.assertFalse(receipt["gates"]["engineering_step_qualified"])
        self.assertEqual(receipt["gates"]["supported_operations"],26)

    def test_18_all_admitted_nonidentity_components_positive(self):
        examples=[((ONE,ONE),(ONE,ONE)),
                  ((Z,Z),(Z,U)),
                  ((UM1,UM1),(Z,U)),
                  ((U,U),(ONE_MINUS_U,ONE_MINUS_U))]
        for left,right in examples:
            r=self.checked(source(left,right))
            self.assertTrue(all(c["sign"]=="POSITIVE"
                                for c in r["nonzero_sign_cells"]))

    def test_19_exact_square_recognition_adversarial(self):
        for q in [(R(2),R(0),R(0)),
                  (R(1),R(1),R(1)),
                  (R(0),R(1),R(0)),
                  (R(-1),R(0),R(0))]:
            with self.assertRaises(m.Refusal):
                m.square_affine(q)
        self.assertEqual(m.square_affine((R(1),R(-2),R(1))),
                         (R(-1),R(1)))

    def test_20_full_phase_lattice_equalities(self):
        self.assertEqual(m.phase_lattice(R(0),R(2),R(0),R(1)),
                         [R(0),R(1,2),R(1),R(3,2),R(2)])
        self.assertEqual(m.phase_lattice(R(0),R(2),R(1),R(-1)),
                         [R(2),R(3,2),R(1),R(1,2),R(0)])

    def test_21_file_ingress_exact_raw_size_and_oversized_valid_json(self):
        valid=m.encode(source((Z,Z),(Z,U)))
        self.assertLess(len(valid),m.MAX_SOURCE_BYTES)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"prospective-source.json"
            path.write_bytes(valid)
            good=m.attempt_file(path)
            self.assertEqual(good["status"],m.STATUS,good)
            # The raw file budget is inclusive, even when padded JSON parses
            # to precisely the same canonical source specification.
            path.write_bytes(valid+b" "*(m.MAX_SOURCE_BYTES-len(valid)))
            good=m.attempt_file(path)
            self.assertEqual(good["status"],m.STATUS,good)
            path.write_bytes(valid+b" "*(m.MAX_SOURCE_BYTES+1-len(valid)))
            bad=m.attempt_file(path)
            self.assertEqual(bad["status"],"RESOURCE_REFUSAL",bad)
            self.assertEqual(bad["reason"],"SOURCE_FILE_BYTE_BUDGET")
            self.assertFalse(bad["is_truth_value"])
            self.assertFalse(bad["pb00701_certified"])

    def test_22_file_ingress_duplicate_malformed_nonfinite_and_nesting(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"source.json"
            bad_cases=[
                (b'{"grammar":"A","grammar":"B"}',
                 "BLOCKED","DUPLICATE_SOURCE_JSON_KEY"),
                (b'{"value":NaN}',"BLOCKED","NONFINITE_SOURCE_JSON"),
                (b'{"value":Infinity}',"BLOCKED","NONFINITE_SOURCE_JSON"),
                (b'{"', "BLOCKED",None),
                (bytes([0xff]), "BLOCKED",None),
                (b"["*1500+b"0"+b"]"*1500,"RESOURCE_REFUSAL","RecursionError"),
            ]
            for raw,kind,reason in bad_cases:
                with self.subTest(expected=reason or raw[:20]):
                    path.write_bytes(raw)
                    answer=m.attempt_file(path)
                    self.assertEqual(answer["status"],kind,answer)
                    if reason is not None:
                        self.assertEqual(answer["reason"],reason)
                    self.assertFalse(answer["is_truth_value"])
                    self.assertFalse(answer["mc_b_established"])
                    self.assertFalse(answer["production_authorized"])


if __name__=="__main__":
    unittest.main()
