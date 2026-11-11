"""B1-E6 strict receipt boundary; run from the B1 core directory."""
from __future__ import annotations

import copy
from fractions import Fraction as Q
import unittest

from certificate_algebra import Piece, Refusal, base_record
from closed_nonzero import verify_closed_base
from refined_product import derive as product_derive, verify as product_verify
from rational_quotient import derive as quotient_derive, verify as quotient_verify
from quotient_sided_germ import (derive as germ_derive, verify as germ_verify,
                                  project_signed_affine)
from receipt_integrity import admit


class AlwaysEqual(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


class ReceiptIntegrityTests(unittest.TestCase):
    def fixtures(self):
        left = base_record((Piece(Q(0), Q(1), (Q(1), Q(1))),))
        right = base_record((Piece(Q(0), Q(1), (Q(2),)),))
        return left, right

    def test_infinite_structural_family_representatives(self):
        count = 0
        for n in range(1, 129):
            v = {'schema': 'b1-test', 'n': n, 'leaves': [
                {'coeff': [str(i), str(i + n)], 'active': i % 2 == 0}
                for i in range(n)]}
            admit(v, copy.deepcopy(v))
            changed = copy.deepcopy(v)
            changed['leaves'][-1]['coeff'][0] = 'altered'
            with self.assertRaises(Refusal):
                admit(v, changed)
            count += 1
        self.assertEqual(count, 128)

    def test_builtin_equality_is_not_receipt_equality(self):
        authentic = {'schema': 'RATIONAL_C0', 'claim': 'VERIFIED'}
        hostile = {'schema': 'RATIONAL_C0', 'claim': AlwaysEqual('FORGED')}
        self.assertTrue(authentic == hostile)  # old code's precise failure mode
        with self.assertRaises(Refusal):
            admit(authentic, hostile)
        self.assertTrue({'flag': True} == {'flag': 1})
        with self.assertRaises(Refusal):
            admit({'flag': True}, {'flag': 1})

    def test_e2_closed_receipt_forgery(self):
        _, d = self.fixtures()
        _, actual, _ = verify_closed_base(d, source_pin=d['hash'])
        bad = copy.deepcopy(actual)
        bad['closed_sign'] = AlwaysEqual('NEG')
        self.assertTrue(actual == bad)
        with self.assertRaises(Refusal):
            verify_closed_base(d, source_pin=d['hash'], proposed=bad)

    def test_e3_product_receipt_forgery(self):
        a, b = self.fixtures()
        _, expected, _ = product_derive(a, b, left_pin=a['hash'], right_pin=b['hash'])
        bad = copy.deepcopy(expected)
        bad['schema'] = AlwaysEqual('BYPASS')
        self.assertTrue(expected == bad)
        with self.assertRaises(Refusal):
            product_verify(a, b, bad, left_pin=a['hash'], right_pin=b['hash'])
        product_verify(a, b, expected, left_pin=a['hash'], right_pin=b['hash'])

    def test_e4_quotient_receipt_forgery(self):
        a, b = self.fixtures()
        expected, _ = quotient_derive(a, b, numerator_pin=a['hash'], denominator_pin=b['hash'])
        bad = copy.deepcopy(expected)
        bad['representation'] = AlwaysEqual('B_SPLINE_PHYSICAL_AUTHORITY')
        self.assertTrue(expected == bad)
        with self.assertRaises(Refusal):
            quotient_verify(a, b, bad, numerator_pin=a['hash'], denominator_pin=b['hash'])
        quotient_verify(a, b, expected, numerator_pin=a['hash'], denominator_pin=b['hash'])

    def test_e5_germ_receipt_and_unbound_prediction_forgery(self):
        a, b = self.fixtures()
        quotient, _ = quotient_derive(a, b, numerator_pin=a['hash'], denominator_pin=b['hash'])
        original, _ = germ_derive(a, b, quotient, numerator_pin=a['hash'],
                                  denominator_pin=b['hash'], time='1/2')
        bad = copy.deepcopy(original)
        bad['genuine_structural_knot'] = AlwaysEqual('AUTHENTICATED')
        self.assertTrue(original == bad)
        with self.assertRaises(Refusal):
            germ_verify(a, b, quotient, bad, numerator_pin=a['hash'],
                        denominator_pin=b['hash'], time='1/2')
        germ_verify(a, b, quotient, original, numerator_pin=a['hash'],
                    denominator_pin=b['hash'], time='1/2')
        projected = copy.deepcopy(original)
        projected['source_custody'] = AlwaysEqual('EXTERNALLY_PINNED_CONTENT_ONLY')
        # The subclass serializes as identical text, hence the original hash
        # still matches; bounded primitive type admission must nevertheless refuse.
        with self.assertRaises(Refusal):
            project_signed_affine(projected, offset='0', rate='-1')
        self.assertEqual(project_signed_affine(original, offset='0', rate='-1')
                         ['status'], 'UNBOUND_PREDICTION_REVERIFY_TRANSFORMED_SOURCE')

    def test_budget_depth_nonstring_keys_and_extra_fields(self):
        with self.assertRaises(Refusal):
            admit({'a': 1}, {1: 1})
        nested = []
        for _ in range(40):
            nested = [nested]
        with self.assertRaises(Refusal):
            admit({'a': 1}, {'a': nested})
        with self.assertRaises(Refusal):
            admit({'a': 1}, {'a': 'x' * 4097})
        with self.assertRaises(Refusal):
            admit({'a': 1}, {'a': 1, 'unexpected': 2})
        with self.assertRaises(Refusal):
            admit({'a': 1}, {'a': 1 << 4097})


if __name__ == '__main__':
    unittest.main()
