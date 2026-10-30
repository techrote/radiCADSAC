#!/usr/bin/env python3
"""Source-bound adversarial tests for degree <=8 real multiquadratic embedding."""
import argparse
from fractions import Fraction as Q
from itertools import product
import json
import unittest
from pathlib import Path
import pb00701_multiquadratic_embedding as m
import pb00701_v44_biquadratic_independent_check as challenger

TASK=Path(__file__).resolve().parent
CHALLENGER_BLOB="5e4148b608038fe11b7ed02ac0e45cd0e3421e51"
SOURCE_SHA256="d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2"


def source_contract():
    # Pin prior independent fixed-field checker as well as its original-source
    # original-harmonics, historical-v54 and authority checks.
    actual=challenger.owner.parent.bridge.previous.git_blob(TASK / "pb00701_v44_biquadratic_independent_check.py")
    if actual != CHALLENGER_BLOB:
        raise m.Refusal("PINNED_INDEPENDENT_CHECKER_DRIFT")
    previous=challenger.challenge()
    if previous["original_source_sha256"] != SOURCE_SHA256 or previous["checked_vectors"] != 625 or previous["mc_b_established"] is not False:
        raise m.Refusal("FROZEN_SOURCE_CHECK_NOT_REPLAYED")
    return previous


def scenario():
    previous=source_contract()
    f=m.Field((2,3))
    # Fully check all 625 small coefficient vectors against the *separate*
    # inherited K sign primitive, using our arbitrary-rank interval machinery.
    checked=0
    for coeffs in product(range(-2,3), repeat=4):
        c=tuple(Q(x) for x in coeffs)
        s=f.element(c).sign_certificate()["sign"]
        if s != challenger.owner.K(c).sign():
            raise m.Refusal("FIXED_FIELD_SIGN_DISAGREEMENT")
        checked += 1
    g=m.Field((2,3,5))
    # Degree-eight native arithmetic: eight basis elements, identities,
    # mixed signs and nontrivial inverses, no floating-point arithmetic.
    for i in range(8):
        for j in range(8):
            if g.basis(i)*g.basis(j) != g.scalar(g.radicand(i&j))*g.basis(i^j):
                raise m.Refusal("DEGREE_EIGHT_BASIS_TABLE_MISMATCH")
    checked_inverses=0
    for k in range(1, 26):
        coeffs=tuple(Q((((k*17 + i*11) % 13) - 6), (i+1)) for i in range(8))
        a=g.element(coeffs)
        if not any(coeffs):
            continue
        if a*a.inverse() != g.scalar(1):
            raise m.Refusal("DEGREE_EIGHT_INVERSE_MISMATCH")
        s=a.sign_certificate()
        if s["sign"] not in (-1,1):
            raise m.Refusal("DEGREE_EIGHT_SIGN_NOT_DECIDED")
        if a.sign_certificate() != s:
            raise m.Refusal("NONDETERMINISTIC_SIGN_RECORD")
        checked_inverses += 1
    return {"schema": m.SCHEMA, "status": "BOUNDED_MULTIRADICAL_EXACT_ARITHMETIC_PASSED",
            "evidence_class": "DETERMINISTIC_MODEL", "source_sha256": SOURCE_SHA256,
            "prior_checker_sha1": CHALLENGER_BLOB, "rank2_vectors": checked,
            "rank3_basis_products": 64, "rank3_inverses": checked_inverses,
            "highest_rank": 3, "highest_degree": 8,
            "arbitrary_number_fields": False, "irrational_phase_zero_decider": False,
            "nonmonotone_physical_root_theorem": False,
            "historical_v54_admitted": False, "mc_b_established": False,
            "mc1_established": False, "production_authorized": False}

class Contract(unittest.TestCase):
    def test_field_independence(self):
        for generators in ((2,3,6),(6,10,15),(2,2),(2,8),(4,),(1,),(2,3,5,7),(0,),(-2,),(10001,),()):
            with self.assertRaises((m.Refusal,m.ResourceRefusal)):
                m.Field(generators)
        for generators in ((2,), (2,3), (2,3,5), (6,7,10)):
            self.assertEqual(m.Field(generators).degree, 2**len(generators))
    def test_mixed_field_incompatibility(self):
        a=m.Field((2,3)).basis(1)
        b=m.Field((3,2)).basis(1)
        with self.assertRaises(m.Refusal):
            a+b
        with self.assertRaises(m.Refusal):
            a*b
        with self.assertRaises(m.Refusal):
            m.Field((2,3)).element([1,2,3,4])
        with self.assertRaises(m.Refusal):
            m.Field((2,3)).scalar(1.0)
    def test_sign_proof_and_near_zero(self):
        f=m.Field((2,3,5))
        z=f.scalar(0)
        self.assertEqual(z.sign_certificate()["status"], "EXACT_ZERO")
        a=f.element((Q(-577),Q(408))+(Q(0),)*6)
        self.assertEqual(a.sign_certificate()["sign"], -1)
        self.assertEqual((-a).sign_certificate()["sign"], 1)
        with self.assertRaises(m.ResourceRefusal):
            a.sign_certificate((1,))
        with self.assertRaises(m.ResourceRefusal):
            a.sign_certificate((1025,))
        with self.assertRaises(m.ResourceRefusal):
            a.sign_certificate(iter([8]))
        with self.assertRaises(m.ResourceRefusal):
            a.sign_certificate((8,)*8)
        with self.assertRaises(m.Refusal):
            z.inverse()
        with self.assertRaises(m.ResourceRefusal):
            f.element((Q(1<<1025),)+(Q(0),)*7)
    def test_canonical_replay_and_forgery(self):
        a=m.Field((2,3,5)).basis(1)+m.Field((2,3,5)).scalar(-1)
        record=a.record()
        witness=a.sign_certificate()
        self.assertEqual(m.parse_record(record),a)
        z=m.Field((2,3,5)).scalar(0)
        self.assertEqual(m.verify_sign_certificate(z.record(),z.sign_certificate()),
                         {"status":"CERTIFIED","sign":0})
        self.assertEqual(m.verify_sign_certificate(record,witness),{"status":"CERTIFIED","sign":1})
        forged=dict(witness,sign=-1)
        self.assertEqual(m.verify_sign_certificate(record,forged)["status"],"BLOCKED")
        altered=dict(record,coefficients=list(record["coefficients"]))
        altered["coefficients"][1]="01"
        self.assertEqual(m.verify_sign_certificate(altered,witness)["status"],"BLOCKED")
        self.assertEqual(m.verify_sign_certificate(
            {"generators":[2]*100, "coefficients": []}, witness)["status"], "BLOCKED")
        gigantic={"items": "!"*m.MAX_CERT_BYTES}
        self.assertEqual(m.verify_sign_certificate(record,gigantic)["status"],"RESOURCE_REFUSAL")
    def test_exact_rank3_algebra(self):
        g=m.Field((2,3,5))
        for i in range(g.degree):
            for j in range(g.degree):
                self.assertEqual(g.basis(i)*g.basis(j),g.scalar(g.radicand(i&j))*g.basis(i^j))
        a=g.element((Q(1,3), Q(-2,5),Q(7,11),Q(3,13),Q(2,17),Q(-5,19),Q(7,23),Q(11,29)))
        self.assertEqual(a*a.inverse(),g.scalar(1))
        self.assertEqual(a.inverse()*a,g.scalar(1))
    def test_original_source_bound_challenge(self):
        record=scenario()
        self.assertEqual(record["rank2_vectors"],625)
        self.assertEqual(record["rank3_basis_products"],64)
        self.assertFalse(record["historical_v54_admitted"])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--contract",action="store_true")
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if not (args.contract or args.self_test):
        p.error("Choose --contract and/or --self-test")
    if args.contract:
        print(json.dumps(scenario(),sort_keys=True))
    if args.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contract))
        raise SystemExit(0 if result.wasSuccessful() else 1)

if __name__=="__main__":
    main()
