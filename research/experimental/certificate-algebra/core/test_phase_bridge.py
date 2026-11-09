"""B1-D1 deterministic positive and adversarial tests; no numerical root sampling."""
import copy
from fractions import Fraction as Q
import unittest

from phase_bridge import (PRODUCERS, SCHEMA, Refusal, canonical,
                          digest, prove_equivalent, verify)


def make(producer, *, offset="0", rate="1", terms=None, original="a"*64):
    return {"schema": SCHEMA, "producer": producer,
            "producer_head": PRODUCERS[producer][0], "origin_source_sha": original,
            "interval": ["-2", "2"], "offset": offset, "rate": rate,
            "terms": terms or {"0": [["-1"], ["0"]], "1": [["0"], ["1"]]}}


class BridgeTests(unittest.TestCase):
    def test_A3_exact_counterexample_and_repair(self):
        # At t=1/2, -1+sin(pi*t) == 0, but -1+sin(2*pi*t) == -1.
        a1 = make("A1-470")
        mc_same_fields = make("MC038-main")
        with self.assertRaises(Refusal):
            prove_equivalent(a1, mc_same_fields)
        mc = make("MC038-main", rate="1/2")
        receipt = prove_equivalent(a1, mc)
        self.assertTrue(verify(a1, mc, receipt, pinned_source_hash=digest(a1),
                               pinned_target_hash=digest(mc)))
        self.assertEqual(canonical(a1), canonical(mc))
        mc_at_rate_one = make("MC038-main")
        a1_doubled = make("A1-470", rate="2")
        self.assertEqual(canonical(mc_at_rate_one), canonical(a1_doubled))
        self.assertEqual(prove_equivalent(mc_at_rate_one,a1_doubled)["semantic_hash"],
                         digest(canonical(mc_at_rate_one)))
        # Independently exact quarter-turn table; not an approximate trig check.
        sin_pi_half, sin_pi = Q(1), Q(0)
        self.assertEqual(-1+sin_pi_half, 0)
        self.assertEqual(-1+sin_pi, -1)

    def test_infinite_family_rational_phase_identity_controls(self):
        # General proof is algebraic phase substitution. Finite suite challenges it.
        n = 0
        for p in range(-6,7):
            for q in (1,2,3,5):
                for r in (-3,-1,0,1,4):
                    native_offset, native_rate = Q(p,q), Q(r,q)
                    a1 = make("A1-470", offset=str(2*native_offset),
                              rate=str(2*native_rate), terms={
                              "0":[["2","-1"],["0"]],
                              "1":[["0","3/2","-1/4"],["-1","0","1"]],
                              "2":[["-2"],["1/3"]]})
                    origin = "A2-471" if native_rate else "MC038-main"
                    typed = make(origin, offset=str(native_offset),
                                 rate=str(native_rate), terms=copy.deepcopy(a1["terms"]))
                    c = prove_equivalent(typed, a1)
                    self.assertTrue(verify(typed,a1,c,pinned_source_hash=digest(typed),
                                           pinned_target_hash=digest(a1)))
                    n += 1
        self.assertEqual(n,260)

    def test_tampering_source_identity_pins_and_semantics(self):
        a = make("A2-471", original="b"*64)
        b = make("A1-470", rate="2", original="c"*64)
        claim = prove_equivalent(a,b)
        pins = {"pinned_source_hash":digest(a),"pinned_target_hash":digest(b)}
        for field,changed in [("rate","1"),("origin_source_sha","d"*64),
                              ("producer_head","e"*40)]:
            forged = copy.deepcopy(b)
            forged[field]=changed
            with self.assertRaises(Refusal):
                verify(a,forged,claim,**pins)
        forged = copy.deepcopy(b)
        forged["terms"]["1"][1][0]="2"
        with self.assertRaises(Refusal):
            prove_equivalent(a,forged)
        bad_claim = dict(claim, semantic_hash="0"*64)
        with self.assertRaises(Refusal):
            verify(a,b,bad_claim,**pins)

    def test_fail_closed_grammar_and_resource_limits(self):
        a = make("A1-470")
        for edit in [lambda s: s.update(offset="-0"),
                     lambda s: s.update(rate="1/1"),
                     lambda s: s.update(rate="1"*200),
                     lambda s: s.update(producer="unknown"),
                     lambda s: s.update(producer_head="a"*40),
                     lambda s: s.update(interval=["2","-2"]),
                     lambda s: s["terms"].update({"0":[["0"],["1"]]}),
                     lambda s: s["terms"].update({"9":[["1"],["0"]]}),
                     lambda s: s["terms"].update({"1":[["0","0"],["1"]]}),
                     lambda s: s.update(extra=1),
                     lambda s: s.update(terms={"1":[["1"]*100000,["0"]]}),
                     lambda s: s["terms"].update({"3":[["1"],["0"]]})]:
            bad = copy.deepcopy(a)
            edit(bad)
            with self.assertRaises(Refusal):
                canonical(bad)

    def test_producer_admission_restrictions(self):
        a2 = make("A2-471", rate="0")
        with self.assertRaises(Refusal):
            canonical(a2)
        a2 = make("A2-471")
        a2["terms"]["1"][0] = ["1", "2", "3", "4", "5"]
        with self.assertRaises(Refusal):
            canonical(a2)

    def test_phase_period_alias_is_conservatively_not_proven(self):
        # pi*(beta+2) is semantically periodic, but this restricted contract
        # intentionally does not derive periodic-alias equivalence.
        a = make("A1-470",offset="0")
        b = make("A1-470",offset="2")
        with self.assertRaises(Refusal):
            prove_equivalent(a,b)

if __name__ == "__main__":
    unittest.main(verbosity=2)
