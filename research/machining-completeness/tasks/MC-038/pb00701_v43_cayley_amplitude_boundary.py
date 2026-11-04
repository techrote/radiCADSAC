#!/usr/bin/env python3
"""Original V43 affine-H1 Cayley polynomialization obstruction (model-only C)."""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import unittest

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
CORPUS = TASK / "pb00701-finite-owner-corpus-v54.json"
REGISTER = TASK / "pb00701-post-v54-evidence-reconciliation-v2.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
REGISTER_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
CASE = "harvested:verify_pb00701_v9:4e7b85fa122a"
SOURCE_SHA = "a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10"
ROW_SHA = "62346bbddca22c4271a14c10aa130327013ac7cf8daa0b0ae515257e8f28cfad"
ROUTE = "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"
REFUSAL = "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"
EVIDENCE_CLASS = "DETERMINISTIC_MODEL"
TARGET_SPEC = {
    "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
    "source_parameter_id": "source-time-t",
    "parameter_lo": "0", "parameter_hi": "1",
    "phase_turn_offset": "0", "phase_turn_rate": "1/8",
    "cos_splines": {"1": {"degree": 1, "knots": ["0","0","1","1"],
                          "controls": ["1","1"]}},
    "sin_splines": {"1": {"degree": 1, "knots": ["0","0","1","1"],
                          "controls": ["-1/2","1/2"]}},
}


class Refused(ValueError):
    """An unqualified source, evidence or proof claim must not be admitted."""


def need(condition: bool, code: str) -> None:
    if not condition:
        raise Refused(code)


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii")
                        + b"\0" + data).hexdigest()


def canonical_sha(value: dict) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def load_inputs():
    raw_corpus, raw_register = CORPUS.read_bytes(), REGISTER.read_bytes()
    need(git_blob(raw_corpus) == CORPUS_BLOB, "FROZEN_CORPUS_IDENTITY_CHANGED")
    need(git_blob(raw_register) == REGISTER_BLOB, "FROZEN_REGISTER_IDENTITY_CHANGED")
    return json.loads(raw_corpus), json.loads(raw_register)


def exact_bernstein_coefficients(spec: dict):
    """Reject any source change; lower the actual clamped degree-one splines."""
    need(spec == TARGET_SPEC, "UNSUPPORTED_OR_MUTATED_ORIGINAL_SOURCE")
    need(canonical_sha(spec) == SOURCE_SHA, "CANONICAL_SOURCE_HASH_MISMATCH")
    def lower(channel: dict):
        spline = channel["1"]
        need(spline["degree"] == 1 and spline["knots"] == ["0","0","1","1"],
             "NOT_ONE_CLAMPED_DEGREE_ONE_SPAN")
        c0, c1 = map(Fraction, spline["controls"])
        # (1-t)*c0+t*c1, with the ORIGINAL global source-time t.
        return (c0, c1-c0)
    return lower(spec["cos_splines"]), lower(spec["sin_splines"])


def residue_obstruction():
    """Exact symbolic lemma; not a floating root search.

    The derivative of a rational function has residue 0 at each finite pole.
    1/(1+z^2) has residues -i/2 and +i/2 at z=+i and z=-i:
    both nonzero. Therefore arctan(z) is not a rational function.
    """
    # Store residues as ordered exact (real, imaginary) Fraction pairs.
    at_i = (Fraction(0), Fraction(-1,2))
    at_negative_i = (Fraction(0), Fraction(1,2))
    need(at_i != (0,0) and at_negative_i != (0,0),
         "ERRONEOUS_ZERO_RESIDUE")
    need(at_i[1] + at_negative_i[1] == 0, "INCORRECT_SIMPLE_POLE_PAIR")
    return {
        "poles": ["+i","-i"],
        "residues_re_im": [["0","-1/2"],["0","1/2"]],
        "lemma": "DERIVATIVE_OF_RATIONAL_HAS_ZERO_FINITE_POLE_RESIDUES",
        "consequence": "ARCTAN_Z_NONRATIONAL_OVER_COMPLEX_RATIONAL_FUNCTIONS",
    }


def certify(corpus: dict, register: dict):
    cases = corpus.get("cases")
    need(isinstance(cases, list) and len(cases) == 121,
         "HISTORICAL_DENOMINATOR_CHANGED")
    ids = [c.get("id") for c in cases]
    need(len(set(ids)) == 121, "DUPLICATE_ORIGINAL_CASE_ID")
    route = [c for c in cases if c["id"] == CASE]
    need(len(route) == 1, "TARGET_NOT_UNIQUE")
    row = route[0]
    need(row["kind"] == "HARVESTED" and row["origin"] == "verify_pb00701_v9",
         "TARGET_ORIGINAL_PROVENANCE_CHANGED")
    need(row["expected"]["v54_disposition"] == "BLOCKED" and
         row["expected"]["observed"]["status"] == "BLOCKED" and
         row["expected"]["observed"]["spans"] == [[ROUTE,"BLOCKED",REFUSAL]],
         "HISTORICAL_V43_REFUSAL_CHANGED")

    a, b = exact_bernstein_coefficients(row["spec"])
    need(a == (Fraction(1), Fraction(0)), "COSINE_POLYNOMIAL_CHANGED")
    need(b == (Fraction(-1,2), Fraction(1)), "AFFINE_SINE_POLYNOMIAL_CHANGED")
    # F(t) = cos(pi*t/4) + (t-1/2)*sin(pi*t/4).
    # z = tan(pi*t/8),  t=(8/pi)*arctan(z) on original t in (0,1).
    # (1+z^2)F = 1-z^2-z + (16/pi)*z*arctan(z).
    need(Fraction(2)*b[0] == -1 and Fraction(2)*b[1] == 2,
         "INCORRECT_CAYLEY_NUMERATOR_LOWERING")
    pole_certificate = residue_obstruction()

    dispositions = [c["expected"]["v54_disposition"] for c in cases]
    refusal_count = dispositions.count("BLOCKED")
    missing_count = dispositions.count(
        "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE")
    need((refusal_count,missing_count) == (20,30),
         "FROZEN_OUTCOME_COUNTS_CHANGED")
    unresolved = {c["id"] for c in cases
                  if c["expected"]["v54_disposition"].startswith("BLOCKED")}
    registered = register.get("source_cases")
    need(isinstance(registered,list) and len(registered) == 50,
         "HISTORICAL_REGISTER_DENOMINATOR_CHANGED")
    levels = {x["case_id"]:x["registered_evidence_level"] for x in registered}
    need(len(levels) == 50 and set(levels) == unresolved and
         set(levels.values()) == {"COMPLETE_SOURCE_SPECIFIC"},
         "REGISTRY_NOT_EXACT_50_COMPLETE_SOURCE_SET")
    reg = next(x for x in registered if x["case_id"] == CASE)
    need(reg["source_sha256"] == SOURCE_SHA and
         reg["original_row_sha256"] == ROW_SHA and
         reg["historical_v54_disposition"] == "BLOCKED" and
         reg["historical_spans"] == [[ROUTE,"BLOCKED",REFUSAL]],
         "TARGET_V2_PROVENANCE_CHANGED")

    return {
        "schema": "radicadsac-mc038-v43-cayley-affine-boundary/1.0",
        "evidence_class": EVIDENCE_CLASS,
        "outcome": "C_BOUNDED_DIRECT_RATIONAL_POLYNOMIALIZATION_FALSIFIED",
        "case_id": CASE, "source_sha256": SOURCE_SHA, "row_sha256": ROW_SHA,
        "source_parameter": "source-time-t", "domain": ["0","1"],
        "phase_turn_law": ["0","1/8"],
        "original_harmonic_polynomials": {"C1":["1","0"],"S1":["-1/2","1"]},
        "cayley": {
            "z": "tan(pi*t/8)", "inverse": "t=(8/pi)*arctan(z)",
            "range": "0<z<tan(pi/8)",
            "numerator": "1-z^2-z+(16/pi)*z*arctan(z)",
            "denominator": "1+z^2",
            "nonrational_term_coefficient": "(16/pi)*z",
            "direct_polynomialization_possible": False,
        },
        "exact_nonrationality_certificate": pole_certificate,
        "frozen_git_blobs": {"corpus": CORPUS_BLOB, "v2": REGISTER_BLOB},
        "before": {"sources":121,"route_refusals":20,
                   "missing_ordered_premises":30,"complete_witnesses":50},
        "after": {"sources":121,"route_refusals":20,
                  "missing_ordered_premises":30,"complete_witnesses":50},
        "delta": {"sources":0,"route_refusals":0,
                  "missing_ordered_premises":0,"complete_witnesses":0},
        "newly_resolved_historical_ids": [],
        "required_pb007_obligation_discharged": False,
        "general_analytic_event_theorem": "NOT_PROVED",
        "mc_b": "NOT_ESTABLISHED", "mc_1": "NOT_ESTABLISHED",
        "production_authorized": False,
    }



def validate_saved_receipt(receipt: dict, report: dict) -> None:
    """Bind the committed machine receipt to freshly checked source and census."""
    need(receipt.get("schema") == report["schema"] and
         receipt.get("evidence_class") == report["evidence_class"],
         "MACHINE_RECEIPT_SCHEMA_OR_EVIDENCE_CHANGED")
    need(receipt.get("case_id") == report["case_id"] and
         receipt.get("original_spec_sha256") == report["source_sha256"] and
         receipt.get("original_row_sha256") == report["row_sha256"],
         "MACHINE_RECEIPT_SOURCE_IDENTITY_CHANGED")
    need(receipt.get("source_interval") == report["domain"] and
         receipt.get("source_piece_edges") == ["0","1"] and
         receipt.get("interior_source_knots") == [] and
         receipt.get("phase_turns") == {"offset":"0","rate":"1/8"},
         "MACHINE_RECEIPT_KNOT_PHASE_OR_INTERVAL_CHANGED")
    need(receipt.get("frozen",{}).get("corpus_git_blob") == CORPUS_BLOB and
         receipt.get("frozen",{}).get("v2_git_blob") == REGISTER_BLOB and
         receipt.get("frozen",{}).get("historical_v43_refusal") == REFUSAL and
         receipt.get("frozen",{}).get("prior_complete_source_specific") is True,
         "MACHINE_RECEIPT_FROZEN_EVIDENCE_CHANGED")
    need(receipt.get("cayley_chart",{}).get("numerator") ==
         "1-z^2-z+(16/pi)*z*arctan(z)" and
         receipt["cayley_chart"].get("direct_rational_polynomialization_possible") is False,
         "MACHINE_RECEIPT_PROOF_CONCLUSION_CHANGED")
    keys = {"original_sources":"sources", "route_refusals":"route_refusals",
            "missing_ordered_premises":"missing_ordered_premises",
            "complete_source_specific":"complete_witnesses"}
    for side in ("before","after"):
        need(all(receipt.get(side,{}).get(key) == report[side][mapped]
                 for key,mapped in keys.items()), "MACHINE_RECEIPT_CENSUS_CHANGED")
    need(receipt.get("delta") == dict.fromkeys(keys,0) and
         receipt.get("newly_resolved_original_case_ids") == [] and
         receipt.get("pb007_01_discharged") is False and
         receipt.get("mc_b") == "NOT_ESTABLISHED" and
         receipt.get("mc_1") == "NOT_ESTABLISHED" and
         receipt.get("production_authorized") is False,
         "MACHINE_RECEIPT_UNQUALIFIED_GATE_PROMOTION")


class AdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus, cls.register = load_inputs()

    def test_actual_original_source_admitted(self):
        r = certify(self.corpus, self.register)
        self.assertFalse(r["cayley"]["direct_polynomialization_possible"])
        self.assertEqual(r["newly_resolved_historical_ids"], [])
        self.assertEqual(r["delta"]["route_refusals"],0)

    def test_original_harmonics_and_inverse_chart(self):
        self.assertEqual(exact_bernstein_coefficients(TARGET_SPEC),
                         ((Fraction(1),Fraction(0)),
                          (Fraction(-1,2),Fraction(1))))
        self.assertEqual(residue_obstruction()["residues_re_im"],
                         [["0","-1/2"],["0","1/2"]])

    def test_affine_amplitude_not_a_constant_cayley_polynomial(self):
        self.assertNotEqual(exact_bernstein_coefficients(TARGET_SPEC)[1][1],0)
        # If the S1 slope were zero, clearing Cayley denominators
        # WOULD give an exact quadratic: do not mislabel that case.
        constant = copy.deepcopy(TARGET_SPEC)
        constant["sin_splines"]["1"]["controls"] = ["-1/2","-1/2"]
        with self.assertRaises(Refused):
            exact_bernstein_coefficients(constant)

    def test_unsupported_source_mutations_fail_closed(self):
        for path, replacement in [
            (("phase_turn_rate",), "0"),
            (("phase_turn_rate",), "1/4"),
            (("source_parameter_id",), "local-u"),
            (("parameter_hi",), "2"),
            (("cos_splines","1","controls"), ["0","0"]),
            (("sin_splines","1","controls"), ["0","0"]), # identity zero
            (("sin_splines","1","controls"), ["-1/2","-1/2"]),
            (("sin_splines","1","controls"), ["-1/2","0"]), # tangential alternative
            (("sin_splines","1","knots"), ["0","0","1/2","1"]),
            (("cos_splines","2"), {"degree":0,"knots":["0","1"],"controls":["1"]}),
        ]:
            change = copy.deepcopy(TARGET_SPEC)
            dst = change
            for key in path[:-1]:
                dst = dst[key]
            dst[path[-1]] = replacement
            with self.subTest(path=path), self.assertRaises(Refused):
                exact_bernstein_coefficients(change)

    def test_cross_source_and_historical_custody_refusals(self):
        for mutation in ["wrong-case", "wrong-v43", "duplicate", "missing"]:
            corpus = copy.deepcopy(self.corpus)
            if mutation=="wrong-case":
                next(x for x in corpus["cases"] if x["id"]==CASE)["spec"]["phase_turn_rate"]="1/4"
            elif mutation=="wrong-v43":
                next(x for x in corpus["cases"] if x["id"]==CASE)["expected"]["observed"]["spans"][0][2]=None
            elif mutation=="duplicate":
                corpus["cases"][0]["id"]=corpus["cases"][1]["id"]
            else:
                corpus["cases"].pop()
            with self.subTest(mutation=mutation), self.assertRaises(Refused):
                certify(corpus,self.register)

    def test_machine_evidence_binding_and_adversarial_corruption(self):
        report=certify(self.corpus,self.register)
        receipt=json.loads((TASK/"pb00701-v43-cayley-amplitude-boundary.json").read_text())
        validate_saved_receipt(receipt,report)
        for path,value in [
            (("case_id",),"forged:source"),
            (("source_piece_edges",),["0","1/2","1"]),
            (("phase_turns","rate"),"1/4"),
            (("cayley_chart","numerator"),"1-z^2-z"),
            (("frozen","corpus_git_blob"),"wrong"),
            (("before","route_refusals"),19),
            (("after","complete_source_specific"),51),
            (("delta","route_refusals"),-1),
            (("newly_resolved_original_case_ids",),[CASE]),
            (("pb007_01_discharged",),True),
            (("production_authorized",),True),
        ]:
            change=copy.deepcopy(receipt)
            dest=change
            for key in path[:-1]:
                dest=dest[key]
            dest[path[-1]]=value
            with self.subTest(path=path),self.assertRaises(Refused):
                validate_saved_receipt(change,report)

    def test_register_custody_and_complete_set_refusals(self):
        for mutation in ["source-sha", "row-sha", "evidence-class", "extra-id"]:
            register=copy.deepcopy(self.register)
            if mutation=="extra-id":
                register["source_cases"].append(copy.deepcopy(register["source_cases"][0]))
            else:
                obj=next(x for x in register["source_cases"] if x["case_id"]==CASE)
                obj[{"source-sha":"source_sha256","row-sha":"original_row_sha256",
                     "evidence-class":"registered_evidence_level"}[mutation]]="INVALID"
            with self.subTest(mutation=mutation), self.assertRaises(Refused):
                certify(self.corpus,register)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.contract or not args.self_test:
        report=certify(*load_inputs())
        receipt=json.loads((TASK/"pb00701-v43-cayley-amplitude-boundary.json").read_text())
        validate_saved_receipt(receipt,report)
        print(json.dumps(report,sort_keys=True,indent=2))
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(AdversarialTests)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__=="__main__":
    main()
