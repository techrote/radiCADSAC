"""B1-D20: bounded cross-consumer metamorphic laws, not native evidence.

A deterministic 150-source second shape of testing. Each real B1 parent is
replayed before split/affine/product/quotient; equalities are checked by exact
rational evaluation, not by comparing only B1's self-generated receipt hashes.
"""
import random
import unittest
from fractions import Fraction as Q

from certificate_algebra import (EvidenceMeter, Piece, affine, base_record,
                                 events, split, verify_base)
from product_cone import product
from rational_quotient import derive as quotient


class MetamorphicConsumerProperties(unittest.TestCase):
    def test_150_rational_sources_across_real_consumers(self):
        rng = random.Random(202611110724)
        for index in range(150):
            degree = rng.randrange(4)
            left = Q(rng.randrange(-5, 0), rng.randrange(1, 5))
            right = left + Q(rng.randrange(1, 8), rng.randrange(1, 5))
            coefficients = (Q(1),) + tuple(
                Q(rng.randrange(1, 7), rng.randrange(1, 8))
                for _ in range(degree))
            source = Piece(left, right, coefficients)
            parent = base_record((source,))
            state = verify_base(parent["pieces"], parent["receipts"], EvidenceMeter())
            cut = left + (right - left) * Q(rng.randrange(1, 10), 10)
            divided = split(state, 0, cut, EvidenceMeter())
            for step in range(7):
                x = left + (right - left) * Q(step, 6)
                leaf = divided.pieces[0] if x <= cut else divided.pieces[1]
                with self.subTest(index=index, control="split", step=step):
                    self.assertEqual(leaf.at(x), source.at(x))
            for sign in (1, -1):
                rate = sign * Q(rng.randrange(1, 6), rng.randrange(1, 6))
                offset = Q(rng.randrange(-3, 4), rng.randrange(1, 6))
                transformed = affine(state, offset, rate, EvidenceMeter())
                for step in range(7):
                    x = left + (right - left) * Q(step, 6)
                    y = (x - offset) / rate
                    with self.subTest(index=index, control="affine", sign=sign, step=step):
                        self.assertEqual(transformed.pieces[0].at(y), source.at(x))
            constant = base_record((Piece(left, right, (Q(2),)),))
            multiplied, _, _ = product(parent, constant, left_pin=parent["hash"],
                                       right_pin=constant["hash"])
            for step in range(7):
                x = left + (right - left) * Q(step, 6)
                with self.subTest(index=index, control="product", step=step):
                    self.assertEqual(multiplied.pieces[0].at(x), 2 * source.at(x))
            quotient_receipt, _ = quotient(parent, constant,
                                           numerator_pin=parent["hash"],
                                           denominator_pin=constant["hash"])
            self.assertEqual(quotient_receipt["denominator_closed_sign"], "POS")
            self.assertEqual(quotient_receipt["open_piece_signs"], ["POS"])

    def test_cross_touch_event_orientation_under_negative_affine(self):
        for after, expected in ((Q(1), "CROSS"), (Q(-1), "TOUCH")):
            left = Piece(Q(0), Q(1), (Q(-1), Q(1)))
            right = Piece(Q(1), Q(2), (Q(0), after))
            parent = base_record((left, right))
            state = verify_base(parent["pieces"], parent["receipts"], EvidenceMeter())
            before = events(state)
            self.assertEqual(before["isolated_points"], [
                {"time": "1", "kind": expected, "left": "NEG",
                 "right": "POS" if after > 0 else "NEG"}])
            reversed_state = affine(state, Q(2), Q(-1), EvidenceMeter())
            opposite = events(reversed_state)
            self.assertEqual(opposite["isolated_points"], [
                {"time": "1", "kind": expected,
                 "left": "POS" if after > 0 else "NEG", "right": "NEG"}])


if __name__ == "__main__":
    unittest.main()
