"""B1-E7: exact-module tests for untrusted base-sign premise admission.

Run from research/experimental/certificate-algebra/core:
    python3 -m unittest -v test_base_receipt_integrity.py
No native/MC-038 claims; retain the old vulnerable behavior as negative evidence
in BASE-RECEIPT-INTEGRITY.md rather than teaching the corrected module to pass it.
"""
from __future__ import annotations

import copy
from fractions import Fraction as Q
import unittest

from certificate_algebra import (
    Certificate, EvidenceMeter, Piece, Refusal, base_record, check_leaf,
    events, piece, receipt, replay, split, verify_base,
)
from closed_nonzero import verify_closed_base


class AlwaysEqual(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


class BaseReceiptIntegrityTests(unittest.TestCase):
    def source(self, coeff=(Q(1),)):
        p = Piece(Q(0), Q(1), coeff)
        return p, base_record((p,))

    def test_forged_identity_zero_on_strict_positive_base(self):
        p, base = self.source()
        good = verify_base(base["pieces"], base["receipts"], EvidenceMeter())
        self.assertEqual(events(good), {"identity_intervals": [],
                                        "isolated_points": []})
        bad = copy.deepcopy(base)
        bad["receipts"][0]["sign"] = AlwaysEqual("ZERO")
        self.assertTrue("POS" == bad["receipts"][0]["sign"])
        with self.assertRaises(Refusal):
            verify_base(bad["pieces"], bad["receipts"], EvidenceMeter())
        # This is a genuinely valid independent source pin, not a forged pin:
        # the mutated input must fail despite retaining the authentic source.
        with self.assertRaises(Refusal):
            verify_closed_base(bad, source_pin=base["hash"])

    def test_source_hash_subclass_cannot_bypass_replay(self):
        _, base = self.source()
        bad = copy.deepcopy(base)
        bad["receipts"][0]["source_hash"] = AlwaysEqual("0" * 64)
        with self.assertRaises(Refusal):
            verify_base(bad["pieces"], bad["receipts"], EvidenceMeter())

    def test_direct_receipt_and_direct_leaf_check_refuse_hostile_dataclass(self):
        p, base = self.source()
        raw = copy.deepcopy(base["receipts"][0])
        raw["sign"] = AlwaysEqual("ZERO")
        with self.assertRaises(Refusal):
            receipt(raw)
        fake = Certificate(source_hash=p.hash, sign=AlwaysEqual("ZERO"),
                           b=(Q(1),))
        with self.assertRaises(Refusal):
            check_leaf(p, fake, EvidenceMeter())
        good = receipt(base["receipts"][0])
        check_leaf(p, good, EvidenceMeter())

    def test_source_coefficient_and_nonstring_key_subclasses_refuse(self):
        p, base = self.source()
        raw = copy.deepcopy(base["pieces"][0])
        raw["coeff"] = [AlwaysEqual("1")]
        with self.assertRaises(Refusal):
            piece(raw)
        raw = copy.deepcopy(base["pieces"][0])
        raw[1] = "junk"
        with self.assertRaises(Refusal):
            piece(raw)
        self.assertEqual(piece(base["pieces"][0]), p)

    def test_journal_inherits_base_guard(self):
        _, base = self.source()
        good = {"schema": "b1-journal-v1", "base": base, "steps": []}
        s, _ = replay(good)
        self.assertEqual(s.hash, base["hash"])
        bad = copy.deepcopy(good)
        bad["base"]["receipts"][0]["sign"] = AlwaysEqual("ZERO")
        with self.assertRaises(Refusal):
            replay(bad)
        bad = copy.deepcopy(good)
        bad["steps"] = [AlwaysEqual("malformed")]
        with self.assertRaises(Refusal):
            replay(bad)

    def test_valid_split_and_replay_preserve_zero_set(self):
        _, base = self.source()
        s = verify_base(base["pieces"], base["receipts"], EvidenceMeter())
        after = split(s, 0, Q(1, 2), EvidenceMeter())
        step = {"op": "split", "index": 0, "cut": "1/2",
                "before": s.hash, "after": after.hash}
        replayed, m = replay({"schema": "b1-journal-v1",
                               "base": base, "steps": [step]})
        self.assertEqual(replayed.hash, after.hash)
        self.assertEqual(events(replayed)["identity_intervals"], [])
        self.assertGreaterEqual(m.transform_checks, 1)

    def test_real_zero_continuum_preserved(self):
        _, base = self.source((Q(0),))
        verified = verify_base(base["pieces"], base["receipts"], EvidenceMeter())
        self.assertEqual(events(verified)["identity_intervals"], [["0", "1"]])
        self.assertEqual(events(verified)["isolated_points"], [])

    def test_infinite_positive_bernstein_family_sampled(self):
        # All rational c >= 0: 1+c*u*(1-u) has Bernstein (1,1+c/2,1).
        # The theorem is algebraic; this loop only probes 112 representatives.
        for n in range(112):
            c = Q(n, n + 1)
            _, base = self.source((Q(1), c, -c) if n else (Q(1),))
            verified = verify_base(base["pieces"], base["receipts"], EvidenceMeter())
            self.assertEqual(events(verified)["isolated_points"], [])
            self.assertEqual(events(verified)["identity_intervals"], [])
            bad = copy.deepcopy(base)
            bad["receipts"][0]["sign"] = AlwaysEqual("ZERO")
            with self.assertRaises(Refusal):
                verify_base(bad["pieces"], bad["receipts"], EvidenceMeter())

    def test_cyclic_and_oversized_inputs_typed_refusal(self):
        _, base = self.source()
        bad = copy.deepcopy(base)
        cycle = []
        cycle.append(cycle)
        bad["receipts"][0]["bernstein"] = cycle
        with self.assertRaises(Refusal):
            verify_base(bad["pieces"], bad["receipts"], EvidenceMeter())
        bad = copy.deepcopy(base)
        bad["receipts"][0]["sign"] = "x" * 4097
        with self.assertRaises(Refusal):
            verify_base(bad["pieces"], bad["receipts"], EvidenceMeter())


if __name__ == "__main__":
    unittest.main()
