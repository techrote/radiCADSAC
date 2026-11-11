"""Deterministic independent A1/A2 canonical-source-serialization challenges.

These are upstream serialization-format fixtures, NOT executions of the
published A1/A2 source modules, and not independently trusted source pins.
"""
import copy
from unittest.mock import patch
import unittest
from fractions import Fraction as Q

from phase_bridge import Refusal, digest
from producer_codec import (a1_envelope, a2_envelope, certified_pair)

A1 = {"c0": ["-1"], "cos": [[]], "sin": [["1"]],
      "phase_offset": "0", "phase_rate": "1"}
A2 = {"interval": ["0", "2"], "phase": ["0", "1/2"],
      "terms": {"0": [["-1"], ["0"]], "1": [["0"], ["1"]]}}
WIN = ["0", "2"]


def prove(x=A1, y=A2, w=WIN, *, pins=None):
    a, b, c = pins or (digest(A1), digest(A2), digest(WIN))
    return certified_pair(x, y, w, a1_pin=a, a2_pin=b, window_pin=c)


class SourceCodecTests(unittest.TestCase):
    def test_producer_serialization_grammar_and_phase(self):
        result = prove()
        self.assertEqual(result["source_pin"], digest(A1))
        self.assertEqual(a1_envelope(A1, WIN, source_pin=digest(A1),
                                     window_pin=digest(WIN))["terms"],
                         a2_envelope(A2, source_pin=digest(A2),
                                     window_pin=digest(WIN))["terms"])

    def test_substituted_amplitude_or_phase_with_old_pin(self):
        for raw, field, val in ((A1, "c0", ["-2"]),
                                (A1, "phase_rate", "2"),
                                (A2, "phase", ["0", "1"]),
                                (A2, "terms", {"0": [["-2"],["0"]],
                                                "1": [["0"],["1"]]})):
            a, b = copy.deepcopy(A1), copy.deepcopy(A2)
            if raw is A1:
                a[field] = val
            else:
                b[field] = val
            with self.assertRaises(Refusal):
                prove(a, b)

    def test_self_authored_equality_does_not_override_source_pins(self):
        # Both claimed sources can be modified into an equivalent new pair.
        a, b = copy.deepcopy(A1), copy.deepcopy(A2)
        a["c0"] = ["-2"]
        b["terms"]["0"][0] = ["-2"]
        with self.assertRaises(Refusal):
            prove(a, b)
        # New pins are only as trustworthy as their external custody.
        self.assertEqual(prove(a, b, pins=(digest(a), digest(b), digest(WIN)))["schema"],
                         "b1-source-serialization-codec-v1")

    def test_external_window_ownership_and_phase_mismatch(self):
        with self.assertRaises(Refusal):
            prove(w=["0", "3"])
        b = copy.deepcopy(A2)
        b["interval"] = ["0", "3"]
        with self.assertRaises(Refusal):
            prove(y=b)
        b = copy.deepcopy(A2)
        b["phase"] = ["0", "1"]
        with self.assertRaises(Refusal):
            prove(y=b, pins=(digest(A1), digest(b), digest(WIN)))

    def test_reject_producer_invalid_and_overbudget(self):
        for invalid in (dict(A1, cos=[["1"], ["1"]]),
                        dict(A1, c0=["1", "0"]),
                        dict(A1, c0=["9"*10000]),
                        dict(A1, phase_rate="-0"),
                        dict(A1, cos="not-a-channel")):
            with self.assertRaises(Refusal):
                prove(x=invalid, pins=(digest(invalid),digest(A2),digest(WIN)))
        for invalid in (dict(A2, phase=["0", "0"]),
                        dict(A2, terms={"0": [["1"], ["1"]]}),
                        dict(A2, terms={"0": [["1", "0"], ["0"]]}),
                        dict(A2, terms={"0": [["0"]*100000,["0"]]})):
            with self.assertRaises(Refusal):
                prove(y=invalid, pins=(digest(A1),digest(invalid),digest(WIN)))

    def test_hostile_serialization_keys_and_nested_budget_refused(self):
        # An actual producer cannot emit a hostile Python str-subclass key.
        # Previously set(raw) == literal_fields called attacker equality and
        # indexing retrieved a value under an alien literal name.
        class Alias(str):
            def __new__(cls, text, impersonates):
                obj = str.__new__(cls, text)
                obj.impersonates = impersonates
                return obj
            def __hash__(self): return hash(self.impersonates)
            def __eq__(self, other): return other == self.impersonates

        a = {Alias("alien-a1-key", "c0"): ["-1"],
             "cos": [[]], "sin": [["1"]],
             "phase_offset": "0", "phase_rate": "1"}
        b = {Alias("alien-a2-key", "interval"): ["0", "2"],
             "phase": ["0", "1/2"],
             "terms": {"0": [["-1"], ["0"]], "1": [["0"], ["1"]]}}
        self.assertEqual(a["c0"], ["-1"])
        self.assertEqual(b["interval"], ["0", "2"])
        self.assertEqual(set(a), set(A1))
        self.assertEqual(set(b), set(A2))
        for x, y in ((a, A2), (A1, b)):
            with self.subTest(hostile_a1=(x is a)):
                with self.assertRaises(Refusal):
                    prove(x, y, pins=(digest(x), digest(y), digest(WIN)))
        for payload in (dict(A1, sin=[["1"]], cos=[["1"]*200000]),
                        dict(A1, c0=["1" * 10000]),
                        dict(A1, cos=[[]], sin=[["1"]], phase_rate="1/1")):
            with self.assertRaises(Refusal):
                a1_envelope(payload, WIN, source_pin=digest(payload),
                            window_pin=digest(WIN))
        deep = copy.deepcopy(A2)
        deep["terms"]["1"][0] = ["1"]
        deep["terms"]["1"][0][0] = [deep]  # intentional cycle
        with self.assertRaises(Refusal):
            a2_envelope(deep, source_pin="f" * 64,
                        window_pin=digest(WIN))

    def test_source_snapshot_refuses_torn_identity_during_digest(self):
        # Real adapter boundary: previously it parsed one source and then
        # hashed a mutated different source using a caller-controlled pin.
        import producer_codec as codec
        for name in ("A1", "A2"):
            with self.subTest(producer=name):
                original = copy.deepcopy(A1 if name == "A1" else A2)
                changed = copy.deepcopy(original)
                if name == "A1":
                    changed["c0"][0] = "-2"
                else:
                    changed["terms"]["0"][0][0] = "-2"
                old_pin, changed_pin = digest(original), digest(changed)
                self.assertNotEqual(old_pin, changed_pin)
                triggered = [False]

                def mutate_then_hash(value):
                    if not triggered[0] and type(value) is dict:
                        triggered[0] = True
                        if name == "A1":
                            original["c0"][0] = "-2"
                        else:
                            original["terms"]["0"][0][0] = "-2"
                    return digest(value)

                with patch.object(codec, "digest", side_effect=mutate_then_hash):
                    with self.assertRaises(Refusal):
                        if name == "A1":
                            a1_envelope(original, WIN, source_pin=changed_pin,
                                        window_pin=digest(WIN))
                        else:
                            a2_envelope(original, source_pin=changed_pin,
                                        window_pin=digest(WIN))
                self.assertTrue(triggered[0])
                # No claim that this verifies who produced either source or pin.
                self.assertEqual(digest(original), changed_pin)

    def test_infinite_rational_family_and_negative_rates(self):
        # General law follows from exact phase substitution, not finite tests.
        for k in range(-6, 7):
            for degree in range(4):
                a, b = copy.deepcopy(A1), copy.deepcopy(A2)
                a["phase_rate"] = str(Q(k, 2))
                b["phase"][1] = str(Q(k, 4))
                a["c0"] = ["-1"] + ["0"]*(degree-1) + (["1"] if degree else [])
                b["terms"]["0"][0] = a["c0"]
                if k:
                    self.assertEqual(prove(a, b, pins=(digest(a),digest(b),digest(WIN)))["schema"],
                                     "b1-source-serialization-codec-v1")
                else:
                    with self.assertRaises(Refusal):
                        prove(a, b, pins=(digest(a),digest(b),digest(WIN)))


if __name__ == "__main__":
    unittest.main()
