"""Direct negative controls for the published A1 producer/verifier modules.

The H2 mathematical result and physical B-spline provenance are not asserted.
The trace hook deterministically exercises a mutable-input interleaving.
"""
import copy
import sys
import unittest
from fractions import Fraction as Q

from receipt_integrity import strict_equal
import algebraic_zero
import projective_h2_atlas
import zero_capacity


class HostileString(str):
    def __eq__(self, other):
        return True
    def __ne__(self, other):
        return False
    __hash__ = str.__hash__


class IntegrityTests(unittest.TestCase):
    def test_strict_primitive_type_and_resource_contract(self):
        self.assertTrue(strict_equal({'value': [0, 'a', True, None]},
                                     {'value': [0, 'a', True, None]}))
        self.assertFalse(strict_equal({'v': 1}, {'v': True}))
        self.assertFalse(strict_equal({'v': False}, {'v': 0}))
        self.assertFalse(strict_equal({'v': 'TRUE'}, {'v': HostileString('FALSE')}))
        self.assertFalse(strict_equal({'v': [1]}, {'v': (1,)}))
        deep = 0
        for _ in range(40):
            deep = [deep]
        self.assertFalse(strict_equal(deep, deep))
        cyclic = []
        cyclic.append(cyclic)
        self.assertFalse(strict_equal(cyclic, cyclic))

    def test_f1_rational_quadratic_receipt_forgery(self):
        s = algebraic_zero.source((-1,), cos=((),), sin=((1,),), phase_rate=1)
        good = algebraic_zero.rational_event(s, Q(1, 2))
        self.assertTrue(algebraic_zero.verify_rational_event(s, good))
        self.assertEqual(good['result'], 'EXACT_ZERO')
        bad = copy.deepcopy(good)
        bad['result'] = HostileString('EXACT_NONZERO')
        self.assertFalse(algebraic_zero.verify_rational_event(s, bad))
        # Separate actual quadratic event, not a reimplementation of its verifier.
        sq = algebraic_zero.source([1], cos=([-1],), sin=([],))
        qgood = algebraic_zero.quadratic_event(sq, 1, 0, -2)
        self.assertTrue(algebraic_zero.verify_quadratic_event(sq, qgood))
        for key in ('source_sha256', 'result_at_both_roots'):
            if key in qgood:
                forged = copy.deepcopy(qgood)
                forged[key] = HostileString('FABRICATED')
                self.assertFalse(algebraic_zero.verify_quadratic_event(sq, forged))

    def test_f6_negative_phase_order_pole_and_forgery(self):
        s = {'a':'0/1', 'b':'-2/1', 'phase_lo':'-1/2', 'phase_hi':'1/1',
             'H0':'0/1', 'C1':'0/1', 'S1':'0/1', 'C2':'0/1', 'S2':'-1/4'}
        good = projective_h2_atlas.certify(s, bits=12)
        self.assertTrue(projective_h2_atlas.verify(s, good))
        self.assertEqual([e.get('physical_time') for e in good['events']],
                         ['-1/2', None, None, '1/4'])
        self.assertEqual([(e['order'], e['left_sign'], e['right_sign'])
                          for e in good['events']],
                         [(1,-1,1),(1,1,-1),(1,-1,1),(1,1,-1)])
        self.assertEqual(len([e for e in good['events']
                              if e.get('locator') == 'PROJECTIVE_POLE']), 1)
        for path in (('source_sha256',), ('physical_source_authentication',),
                     ('events', 0, 'locator'), ('events', 0, 'kind')):
            bad = copy.deepcopy(good)
            item = bad
            for key in path[:-1]:
                item = item[key]
            item[path[-1]] = HostileString('FABRICATED')
            self.assertFalse(projective_h2_atlas.verify(s, bad), path)

    @staticmethod
    def specimen():
        s={'schema':'a1-c0-quadratic-bspline/1','L':'0','K':'1','R':'2',
           'a':'0','b':'1','controls':{f:['0']*5 for f in zero_capacity.FIELDS}}
        s['controls']['H0'][4]='1'
        return s

    def test_f7_boolean_receipt_aliases(self):
        s = self.specimen()
        good = zero_capacity.certify(s)
        self.assertTrue(zero_capacity.verify(s, good))
        for key, value in (('windows', True), ('max_harmonic', False)):
            bad = copy.deepcopy(good)
            bad['pieces'][1][key] = value
            self.assertFalse(zero_capacity.verify(s, bad), (key, value))

    def test_f7_analysis_digest_same_snapshot_under_interleaving(self):
        s = self.specimen()
        good = zero_capacity.certify(s)
        forged = copy.deepcopy(good)
        zero = copy.deepcopy(s)
        zero['controls']['H0'][4] = '0'
        forged['source_sha256'] = zero_capacity.canonical_digest(zero)
        self.assertFalse(zero_capacity.verify(s, forged))

        def during_digest(call):
            changed=[False]
            def trace(frame, event, arg):
                if event == 'call' and frame.f_code is zero_capacity.canonical_digest.__code__:
                    s['controls']['H0'][4] = '0'
                    changed[0] = True
                return trace
            sys.settrace(trace)
            try:
                answer = call()
            finally:
                sys.settrace(None)
            self.assertTrue(changed[0], 'actual author digest was not reached')
            return answer
        self.assertFalse(during_digest(lambda: zero_capacity.verify(s, forged)))
        # A source snapshot captured before the same mutation must hash the
        # analyzed positive right span, not the post-mutation zero source.
        s['controls']['H0'][4] = '1'
        candidate = during_digest(lambda: zero_capacity.certify(s))
        self.assertEqual(candidate['source_sha256'], good['source_sha256'])
        self.assertEqual(candidate['pieces'], good['pieces'])
        self.assertFalse(zero_capacity.verify(s, candidate)) # source is now all-zero


if __name__ == '__main__':
    unittest.main(verbosity=2)
