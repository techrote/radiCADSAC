"""Deterministic independent A1/A2 canonical-source-serialization challenges.

These are upstream serialization-format fixtures, NOT executions of the
published A1/A2 source modules, and not independently trusted source pins.
"""
import copy
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
