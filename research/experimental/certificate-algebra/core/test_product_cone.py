"""Exact deterministic adversarial oracle for B1-E1. Python 3.11+ stdlib."""
import copy
import unittest
from fractions import Fraction as Q

from certificate_algebra import (EvidenceMeter, Piece, Refusal, base_record,
                                 bernstein, check_seam, events, prove, verify_base)
from product_cone import product, verify_product
from closed_nonzero import verify_closed_product


def P(a, b, *coeff):
    return Piece(Q(a), Q(b), tuple(Q(x) for x in coeff))


def base(*ps):
    return base_record(tuple(ps))


class ProductClosureTests(unittest.TestCase):
    def product_check(self, a, b):
        x, w, opt = product(a, b, left_pin=a["hash"], right_pin=b["hash"])
        x2, replay = verify_product(a, b, w, left_pin=a["hash"], right_pin=b["hash"])
        self.assertEqual(x, x2)
        self.assertEqual(replay.full_leaf_checks, len(x.pieces) * 2)
        fresh = EvidenceMeter()
        for p, c in zip(x.pieces, x.certs):
            self.assertEqual(prove(p, fresh), c)  # independent exact Bernstein conversion
        for p, q in zip(x.pieces, x.pieces[1:]):
            check_seam(p, q, fresh)
        return x, w, opt, fresh

    def test_infinite_family_finite_adversarial_samples(self):
        # Infinite proof: each 1+c*u*(1-u), c>=0 has all-positive Bernstein b.
        count = 0
        for i in range(8):
            for j in range(1, 8):
                c, d = Q(i, j), Q(j, i+1)
                a = P(0, 1, 1, c, -c) if c else P(0, 1, 1)
                b = P(0, 1, -1, -d, d)
                out, _, _, _ = self.product_check(base(a), base(b))
                self.assertEqual(out.certs[0].sign, "NEG")
                for u in (Q(0), Q(1, 7), Q(1, 2), Q(6, 7), Q(1)):
                    self.assertEqual(out.pieces[0].at(u), a.at(u) * b.at(u))
                count += 1
        self.assertEqual(count, 56)

    def test_piecewise_endpoint_zeros_and_signed_contact(self):
        a = base(P(0, 1, 0, 1), P(1, 2, 1), P(2, 3, 1, -1))
        b = base(P(0, 1, 0, -1), P(1, 2, -1), P(2, 3, -1, 1))
        out, _, _, _ = self.product_check(a, b)
        self.assertEqual([c.sign for c in out.certs], ["NEG"] * 3)
        self.assertEqual([x["time"] for x in events(out)["isolated_points"]], ["0", "3"])
        cross = base(P(0, 1, 1, -1), P(1, 2, 0, -1))
        positive = base(P(0, 1, 1), P(1, 2, 1))
        signed, _, _, _ = self.product_check(cross, positive)
        self.assertEqual(events(signed)["isolated_points"],
                         [{"time": "1", "kind": "CROSS", "left": "POS", "right": "NEG"}])

    def test_identity_zero_continuum(self):
        a = base(P(0, 1, 0), P(1, 2, 0, 1))
        b = base(P(0, 1, 0, 1), P(1, 2, 1))
        out, _, _, _ = self.product_check(a, b)
        self.assertEqual(events(out)["identity_intervals"], [["0", "1"]])
        self.assertEqual(out.certs[0].sign, "ZERO")
        self.assertEqual(out.certs[1].sign, "POS")

    def test_mismatched_partitions_and_pins_refuse(self):
        a, b = base(P(0, 1, 1)), base(P(0, 2, 1))
        with self.assertRaises(Refusal):
            product(a, b, left_pin=a["hash"], right_pin=b["hash"])
        b = base(P(0, 1, -1))
        with self.assertRaises(Refusal):
            product(a, b, left_pin="0" * 64, right_pin=b["hash"])
        tampered = copy.deepcopy(a)
        tampered["pieces"][0]["coeff"] = ["2"]
        with self.assertRaises(Refusal):
            product(tampered, b, left_pin=a["hash"], right_pin=b["hash"])
        tampered = copy.deepcopy(a)
        tampered["receipts"][0]["sign"] = "NEG"
        with self.assertRaises(Refusal):
            product(tampered, b, left_pin=a["hash"], right_pin=b["hash"])

    def test_witness_and_degree_forgery_refuse(self):
        a, b = base(P(0, 1, 1, 1)), base(P(0, 1, -1))
        _, w, _, _ = self.product_check(a, b)
        for key, replacement in (("product", "0" * 64), ("signs", ["POS"]),
                                 ("leaf_hashes", ["f" * 64])):
            forged = copy.deepcopy(w)
            forged[key] = replacement
            with self.assertRaises(Refusal):
                verify_product(a, b, forged, left_pin=a["hash"], right_pin=b["hash"])
        degree13 = P(0, 1, *([Q(1)] * 14))
        with self.assertRaises(Refusal):
            product(base(degree13), base(degree13),
                    left_pin=base(degree13)["hash"], right_pin=base(degree13)["hash"])

    def test_work_counter_and_limits(self):
        ps = tuple(P(i, i + 1, 1) for i in range(32))
        a = base(*ps)
        b = base(*ps)
        out, _, meter, fresh = self.product_check(a, b)
        self.assertEqual(meter.full_leaf_checks, 64)
        self.assertEqual(fresh.full_leaf_checks, 32)
        self.assertEqual(meter.transform_checks, 32)
        self.assertEqual(meter.seam_checks, 62)
        self.assertEqual(fresh.seam_checks, 31)
        self.assertEqual(len(out.pieces), 32)


class HostileProductWitnessTests(unittest.TestCase):
    """Real E1 and E2 imported consumer boundary, not a standalone oracle."""

    class AlwaysEqual(str):
        def __eq__(self, other):
            return True
        __hash__ = str.__hash__

    class DangerousKey(str):
        def __eq__(self, other):
            raise AssertionError("caller-defined key comparator must not run")
        __hash__ = str.__hash__

    def fixture(self):
        a = base(P(0, 1, 1))
        s, witness, _ = product(a, a, left_pin=a['hash'], right_pin=a['hash'])
        return a, s, witness

    def test_str_subclass_false_sign_schema_and_hash_refused(self):
        a, s, witness = self.fixture()
        self.assertEqual(verify_product(a, a, witness,
                         left_pin=a['hash'], right_pin=a['hash'])[0].hash, s.hash)
        for name, value in (("schema", self.AlwaysEqual("FORGED")),
                            ("left", self.AlwaysEqual("0" * 64)),
                            ("product", self.AlwaysEqual("f" * 64)),
                            ("signs", [self.AlwaysEqual("NEG")]),
                            ("leaf_hashes", [self.AlwaysEqual("0" * 64)])):
            fake = copy.deepcopy(witness)
            fake[name] = value
            with self.subTest(field=name), self.assertRaises(Refusal):
                verify_product(a, a, fake, left_pin=a['hash'], right_pin=a['hash'])

    def test_E2_downstream_must_refuse_forged_E1_sign(self):
        a, s, witness = self.fixture()
        forged = copy.deepcopy(witness)
        forged['signs'][0] = self.AlwaysEqual('NEG')
        with self.assertRaises(Refusal):
            verify_closed_product(a, a, forged, left_pin=a['hash'],
                                  right_pin=a['hash'], product_pin=s.hash)

    def test_hostile_witness_key_is_refused_before_key_comparison(self):
        a, _, witness = self.fixture()
        forged = dict(witness)
        forged[self.DangerousKey('intruder')] = 'x'
        with self.assertRaises(Refusal):
            verify_product(a, a, forged, left_pin=a['hash'], right_pin=a['hash'])

    class ForgeEquality(str):
        def __eq__(self, other):
            return True
        def __ne__(self, other):
            return False
        __hash__ = str.__hash__

    def test_parent_source_hash_and_external_pin_must_be_builtin_and_exact(self):
        a, _, _ = self.fixture()
        forged = copy.deepcopy(a)
        forged['hash'] = self.ForgeEquality('0' * 64)
        with self.assertRaises(Refusal):
            product(forged, a, left_pin=a['hash'], right_pin=a['hash'])
        with self.assertRaises(Refusal):
            product(a, a, left_pin=self.ForgeEquality('f' * 64), right_pin=a['hash'])
        with self.assertRaises(Refusal):
            product(a, a, left_pin='f' * 64, right_pin=a['hash'])

    def test_E2_closed_base_source_and_product_pin_spoof_refused(self):
        from closed_nonzero import verify_closed_base
        a, s, witness = self.fixture()
        for fake in (self.ForgeEquality('0' * 64), '0' * 64):
            with self.subTest(pin=type(fake).__name__), self.assertRaises(Refusal):
                verify_closed_base(a, source_pin=fake)
            with self.assertRaises(Refusal):
                verify_closed_product(a, a, witness, left_pin=a['hash'],
                                      right_pin=a['hash'], product_pin=fake)
        forged = copy.deepcopy(a)
        forged['hash'] = self.ForgeEquality('0' * 64)
        with self.assertRaises(Refusal):
            verify_closed_base(forged, source_pin=a['hash'])

    def test_nonprimitive_nested_oversized_and_cyclic_witness_refused(self):
        a, _, witness = self.fixture()
        candidates = []
        forged = copy.deepcopy(witness); forged['signs'] = [True]
        candidates.append(forged)
        forged = copy.deepcopy(witness); forged['schema'] = 'x' * 4097
        candidates.append(forged)
        forged = copy.deepcopy(witness); forged['signs'] = [{'too': {'deep': set()}}]
        candidates.append(forged)
        nested = []
        for _ in range(40):
            nested = [nested]
        forged = copy.deepcopy(witness); forged['signs'] = nested
        candidates.append(forged)
        cycle = []; cycle.append(cycle)
        forged = copy.deepcopy(witness); forged['signs'] = cycle
        candidates.append(forged)
        for i, forged in enumerate(candidates):
            with self.subTest(forgery=i), self.assertRaises(Refusal):
                verify_product(a, a, forged, left_pin=a['hash'], right_pin=a['hash'])


if __name__ == "__main__":
    unittest.main()
