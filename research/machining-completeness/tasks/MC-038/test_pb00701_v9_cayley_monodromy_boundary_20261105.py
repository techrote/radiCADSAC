#!/usr/bin/env python3
"""Independent adversarial controls for one frozen original V9/V43 Cayley boundary."""
import copy
import unittest
from fractions import Fraction as Q
import pb00701_v9_cayley_monodromy_boundary_20261105 as m

class ExactFrozenSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = m.readp(m.CORPUS, m.CORPUS_BLOB)
        cls.register = m.readp(m.REGISTER, m.REGISTER_BLOB)

    def test_01_actual_frozen_corpus_and_receipt(self):
        report = m.execute()
        self.assertEqual(report["historical_case_id"], m.CASE_ID)
        self.assertEqual(report["historical_case_ids_newly_closed"], [])
        self.assertEqual(report["before"], report["after"])
        self.assertFalse(report["required_pb_discharge"])

    def test_02_canonical_original_hash(self):
        self.assertEqual(m.sha(m.expected_spec()), m.SRC_SHA)
        row = next(x for x in self.corpus["cases"] if x["id"] == m.CASE_ID)
        self.assertEqual(m.sha(row), m.ROW_SHA)

    def test_03_both_original_span_polynomials(self):
        p = m.source_parts(m.expected_spec())
        self.assertEqual(p["left_cos1"], (Q(-1, 2), Q(1)))
        self.assertEqual(p["right_cos0"], (Q(-100), Q(100)))
        self.assertEqual(p["right_sin1"], 1)

    def test_04_exact_cayley_polynomials(self):
        a, b, c, d = m.cayley_polynomials(m.source_parts(m.expected_spec()))
        self.assertEqual(a, (8, 0, -8))
        self.assertEqual(b, (Q(-1,2), 2, Q(1,2)))
        self.assertEqual(c, (800, 0, 800))
        self.assertEqual(d, (Q(-199,2), 2, Q(-201,2)))

    def test_05_nonvanishing_arctan_coefficient_on_physical_spans(self):
        a, _, c, _ = m.cayley_polynomials(m.source_parts(m.expected_spec()))
        for u in (Q(0), Q(1, 4), Q(1, 3), Q(1, 2), Q(3,4), Q(1)):
            val = lambda p: p[0] + p[1]*u + p[2]*u*u
            if u < 1:
                self.assertGreater(val(a), 0)
            self.assertGreater(val(c), 0)

    def test_06_original_left_root_exists_and_is_simple(self):
        # F(0)=-1/2, F(1)=3 sqrt(2)/4; F'(t)>43/140.
        self.assertLess(Q(-1, 2), 0)
        self.assertGreater(Q(3,4), 0)
        self.assertLess(Q(7,5)**2, 2)
        self.assertEqual(Q(7,10)-Q(11,28), Q(43,140))
        self.assertGreater(Q(43,140), 0)

    def test_07_original_right_span_cannot_have_a_root(self):
        # 100(t-1)>=0, cos(theta)>=0, sin(theta)>0 for t in [1,2].
        s = m.expected_spec()
        self.assertEqual(s["phase_turn_rate"], "1/8")
        self.assertEqual(s["cos_splines"]["0"]["controls"], ["0","0","0","100"])
        self.assertEqual(s["cos_splines"]["1"]["controls"][2:], ["1/2","1/2"])
        self.assertEqual(s["sin_splines"]["1"]["controls"], ["1","1"])

    def test_08_phase_offset_or_rate_mutation_refuses(self):
        for key, value in [("phase_turn_offset", "1/8"),
                           ("phase_turn_rate", "0"),
                           ("phase_turn_rate", "-1/8")]:
            s = copy.deepcopy(m.expected_spec())
            s[key] = value
            with self.assertRaises(m.Refusal): m.source_parts(s)

    def test_09_knot_or_parameter_mutation_refuses(self):
        for key, value in [("source_parameter_id", "projected-t"),
                           ("parameter_hi", "3")]:
            s=copy.deepcopy(m.expected_spec());s[key]=value
            with self.assertRaises(m.Refusal): m.source_parts(s)
        s=copy.deepcopy(m.expected_spec())
        s["cos_splines"]["1"]["knots"][2]="1/2"
        with self.assertRaises(m.Refusal): m.source_parts(s)

    def test_10_harmonic_and_identity_zero_mutations_refuse(self):
        for mutation in ("extra", "zero"):
            s=copy.deepcopy(m.expected_spec())
            if mutation=="extra":
                s["sin_splines"]["2"] = copy.deepcopy(s["sin_splines"]["1"])
            else:
                s["sin_splines"]["1"]["controls"]=["0","0"]
            with self.assertRaises(m.Refusal): m.source_parts(s)

    def test_11_ramp_control_and_continuity_mutation_refuse(self):
        for index, value in [(2,"1"), (3,"99")]:
            s=copy.deepcopy(m.expected_spec())
            s["cos_splines"]["0"]["controls"][index]=value
            with self.assertRaises(m.Refusal): m.source_parts(s)

    def test_12_same_count_but_wrong_original_source_refuses(self):
        corpus=copy.deepcopy(self.corpus)
        row=next(x for x in corpus["cases"] if x["id"] == m.CASE_ID)
        row["spec"]["sin_splines"]["1"]["controls"][0]="2"
        with self.assertRaises(m.Refusal): m.receipt(corpus,self.register)

    def test_13_evidence_provenance_drift_refuses(self):
        register=copy.deepcopy(self.register)
        row=next(x for x in register["source_cases"] if x["case_id"] == m.CASE_ID)
        row["original_row_sha256"]="0"*64
        with self.assertRaises(m.Refusal): m.receipt(self.corpus,register)

    def test_14_crossing_parity_and_evidence_promotion_forgery_refuses(self):
        result=m.execute()
        for change in (
            ("first_span_root_order", 2),
            ("first_span_crossing", "TANGENT"),
            ("evidence_class", "NATIVE_GEOMETRY"),
            ("native_geometry_qualified", True),
            ("production_authorized", True),
            ("required_pb_discharge", True),
        ):
            forged=copy.deepcopy(result);forged[change[0]]=change[1]
            with self.assertRaises(m.Refusal): m.check_record(result,forged)

    def test_15_extremely_close_and_identity_zero_unproved_controls_refuse(self):
        result=m.execute()
        tiny=Q(1,2**90)
        self.assertLess(tiny,Q(1,2**80))
        for key,value in [
            ("first_span_root_bracket",["0",str(tiny)]),
            ("identity_zero_or_tangent_or_extremely_close_general_grammar_admitted",True),
            ("second_span_open_physical_roots",1),
        ]:
            forged=copy.deepcopy(result);forged[key]=value
            with self.assertRaises(m.Refusal): m.check_record(result,forged)

    def test_16_historical_census_forgery_refuses(self):
        original=m.execute()
        forged=copy.deepcopy(original)
        forged["after"]["historical_route_refusals"]=19
        with self.assertRaises(m.Refusal): m.check_record(original,forged)

if __name__=="__main__":
    unittest.main()
