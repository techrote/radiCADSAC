#!/usr/bin/env python3
"""Exact source-factor endpoint controls; no substituted carrier or root oracle."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import copy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_ordered_product_model as m
import pb00701_ordered_product_certificate as checker

a, b, E = m.a, m.b, m.E


def power(p, n):
    out = [Q(1)]
    for _ in range(n):
        out = a.pmul(out, p)
    return out


def carrier_args():
    A, B = [Q(469, 2500), -1, 1], [Q(-1, 4), Q(1, 2)]
    return ({1: a.padd(A, B), 2: [Q(1, 10**8)]},
            {1: a.padd(A, a.pscale(B, -1))}, 'v51-physical-source', ('0', '1'), '-1/8', '1/16')


def product_args(factor=None, carrier=None):
    factor = power([-1, 0, 2], 2) if factor is None else factor
    c, s, *tail = carrier_args() if carrier is None else carrier
    return ({h: a.pmul(factor, p) for h, p in c.items()},
            {h: a.pmul(factor, p) for h, p in s.items()}, *tail)


def reverse_poly(poly):
    out = [Q(0)] * len(poly)
    for k, value in enumerate(poly):
        for j in range(k + 1):
            out[j] += Q(value) * comb(k, j) * (-1) ** j
    return a.trim(out)


def certificate(factor, index=0):
    # These test factors have one irreducible square-free factor. The source
    # checker still validates exact source multiplicity and the selected root.
    defining = a.primitive(E.square_free(factor))
    lo, hi = a._canonical_interval(defining, index)
    return {'root_type': 'REAL_ALGEBRAIC_IRRATIONAL',
            'source_polynomial_primitive': list(a.primitive(factor)),
            'defining_square_free_polynomial': list(defining),
            'isolating_interval': [str(lo), str(hi)],
            'multiplicity': a._multiplicity(a.trim(factor), lo, hi),
            'unique_root_proof': {'method': 'EXACT_STURM_OPEN_INTERVAL_COUNT',
                                  'sturm_open_root_count': 1, 'rational_endpoints_are_not_roots': True},
            'binary_float_used': False, 'epsilon_used': False,
            'sampling_used': False, 'approximate_root_used': False}


def mutate(value, path, replacement):
    out = copy.deepcopy(value)
    node = out
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = replacement
    return out


class FactorSignTests(unittest.TestCase):
    def test_actual_factor_owned_carrier_sign_not_orientation_owned(self):
        args = product_args(); cert = certificate(power([-1, 0, 2], 2))
        proof = m.build_factor_carrier_sign(cert, *args)
        self.assertEqual(proof['status'], 'FACTOR_CARRIER_SIGN_CERTIFIED')
        self.assertEqual(proof['relation'], 'POSITIVE')
        self.assertTrue(checker.validate_factor_carrier_sign(proof, cert, *args))
        endpoint = proof['factor_endpoint_evidence']
        self.assertEqual(endpoint['physical_multiplicity'], 2)
        self.assertFalse(endpoint['carrier_orientation_ownership_invented'])
        self.assertFalse(proof['whole_span_certified'])
        self.assertGreater(Q(proof['sign_certificate']['total_interval'][0]), 0)
        fac = m.v50.factor_source(*args)
        field = a.RealField.from_source_certificate(fac['monic_factor'], cert)
        for coordinate in ('A', 'B'):
            self.assertFalse(field.element(a._orientation(fac['carrier_material'], 1, coordinate)).is_zero())

    def test_both_conjugate_signs_are_source_bound(self):
        factor = power([Q(469, 2500), -1, 1], 2)
        args = product_args(factor)
        proofs = [m.build_factor_carrier_sign(certificate(factor, index), *args) for index in (0, 1)]
        self.assertEqual([p['relation'] for p in proofs], ['NEGATIVE', 'POSITIVE'])
        for index, proof in enumerate(proofs):
            self.assertTrue(checker.validate_factor_carrier_sign(proof, certificate(factor, index), *args))
            with self.assertRaises(ValueError):
                checker.validate_factor_carrier_sign(proof, certificate(factor, 1-index), *args)

    def test_negative_phase_global_interval_and_physical_scaling(self):
        base = product_args(); factor = power([-1, 0, 2], 2)
        for operation in ('reverse', 'negate', 'global'):
            c, s, ident, span, off, rate = base
            off, rate = Q(off), Q(rate)
            f = factor
            if operation == 'reverse':
                c, s = ({h: reverse_poly(p) for h, p in x.items()} for x in (c, s))
                off, rate, f = off + rate, -rate, reverse_poly(factor)
            elif operation == 'negate':
                c, s = ({h: a.pscale(p, -3) for h, p in x.items()} for x in (c, s))
            else:
                span, off, rate = ('2', '5'), off - rate * Q(2, 3), rate/3
            args = (c, s, ident, span, str(off), str(rate)); cert = certificate(f)
            proof = m.build_factor_carrier_sign(cert, *args)
            self.assertEqual(proof['relation'], 'NEGATIVE' if operation == 'negate' else 'POSITIVE')
            self.assertTrue(checker.validate_factor_carrier_sign(proof, cert, *args))
            if operation == 'global':
                self.assertEqual(proof['factor_endpoint_evidence']['global_source_cut'], ['2', '3'])
                self.assertEqual(proof['factor_endpoint_evidence']['global_jet_scale'], '1/9')

    def test_close_irrational_neighbors_have_opposite_exact_signs(self):
        carrier = list(carrier_args()); carrier[4] = '-5/32'  # exact H(1/2)=0
        for denominator in (100, 10**6):
            for direction in (-1, 1):
                factor = [-Q(1, 4) - Q(direction, denominator), 0, 1]
                args, cert = product_args(factor, tuple(carrier)), certificate(factor)
                proof = m.build_factor_carrier_sign(cert, *args)
                self.assertEqual(m.SIGNS[proof['relation']], direction)
                self.assertTrue(checker.validate_factor_carrier_sign(proof, cert, *args))
                field = a.RealField.from_source_certificate(factor, cert)
                self.assertEqual((field.element([0, 1]) - Q(1, 2)).sign(), direction)

    def test_finite_checker_does_not_repeat_sign_or_carrier_search(self):
        args = product_args(); cert = certificate(power([-1, 0, 2], 2))
        proof = m.build_factor_carrier_sign(cert, *args)
        with patch.object(m, '_decide_factor_sign', side_effect=AssertionError('no sign search')), \
             patch.object(m.e, '_decide_endpoint', side_effect=AssertionError('no orientation endpoint search')), \
             patch.object(m.v50, 'carrier_proof', side_effect=AssertionError('no carrier selection')), \
             patch.object(m.v50, 'classify_required_analytic_event', side_effect=AssertionError('no source classifier')):
            self.assertTrue(checker.validate_factor_carrier_sign(proof, cert, *args))

    def test_corrupt_finite_sign_source_field_and_remainder_rejected(self):
        args = product_args(); cert = certificate(power([-1, 0, 2], 2))
        proof = m.build_factor_carrier_sign(cert, *args)
        changes = [(['relation'], 'NEGATIVE'), (['whole_span_certified'], True),
                   (['carrier_orientation_ownership_invented'], True), (['nonzero_proved_before_refinement'], False),
                   (['carrier_binding_sha256'], 'another'),
                   (['factor_endpoint_evidence', 'field', 'root_index_in_open_unit_interval'], 1),
                   (['factor_endpoint_evidence', 'carrier_jets', 'endpoint_laurent'], []),
                   (['factor_endpoint_evidence', 'phase_turn'], ['0']),
                   (['sign_certificate', 'precision'], True), (['sign_certificate', 'precision'], 8.0),
                   (['sign_certificate', 'total_interval'], ['1', '2']),
                   (['sign_certificate', 'alpha_interval'], ['1/4', '1/3']),
                   (['sign_certificate', 'pi', 'atan_1_5', 'signed_next_term'], '0'),
                   (['sign_certificate', 'components'], []),
                   (['sign_certificate', 'components', 0, 'trig', 'lagrange_remainder'], '0'),
                   (['sign_certificate', 'components', 0, 'trig', 'lipschitz_constant'], '0')]
        for path, replacement in changes:
            with self.subTest(path=path), self.assertRaises((ValueError, TypeError, KeyError)):
                checker.validate_factor_carrier_sign(mutate(proof, path, replacement), cert, *args)
        for index, value in ((2, 'other-source'), (3, ('0', '2')), (4, '0'), (5, '-1/16')):
            changed = list(args); changed[index] = value
            with self.assertRaises(ValueError):
                checker.validate_factor_carrier_sign(proof, cert, *changed)
        bad = copy.deepcopy(proof); bad['unreviewed_authority'] = True
        with self.assertRaises(ValueError):
            checker.validate_factor_carrier_sign(bad, cert, *args)

    def test_exact_input_premises_and_resource_nontruth(self):
        args = product_args(); cert = certificate(power([-1, 0, 2], 2))
        proof = m.build_factor_carrier_sign(cert, *args)
        for index, value in ((4, True), (5, 0.0625), (5, '0')):
            changed = list(args); changed[index] = value
            with self.assertRaises((ValueError, TypeError)):
                m.build_factor_carrier_sign(cert, *changed)
        for module, name in ((m.v50, 'factor_source'), (m.v50, 'irrational_factor_event'), (m.e, 'sign_enclosure')):
            with patch.object(module, name, side_effect=MemoryError('exact resource')):
                for result in (m.build_factor_carrier_sign(cert, *args),
                               checker.validate_factor_carrier_sign(proof, cert, *args)):
                    self.assertEqual(result['status'], 'RESOURCE_REFUSAL')
                    self.assertIs(result['is_truth_value'], False)
        with patch.object(m.epcheck, '_audit_series', side_effect=OverflowError('exact series resource')):
            self.assertEqual(checker.validate_factor_carrier_sign(proof, cert, *args)['status'], 'RESOURCE_REFUSAL')
        with patch.object(m.e, 'sign_enclosure', side_effect=RuntimeError('unrelated defect')):
            with self.assertRaisesRegex(RuntimeError, 'unrelated defect'):
                m.build_factor_carrier_sign(cert, *args)


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FactorSignTests))
    if not result.wasSuccessful():
        raise AssertionError('v51 exact factor-sign controls failed')


if __name__ == '__main__':
    run()
