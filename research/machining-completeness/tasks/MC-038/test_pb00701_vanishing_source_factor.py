#!/usr/bin/env python3
"""Exact local algebra and theorem premises, using actual MC032/v45/v46 code."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import copy
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_vanishing_source_factor_model as m
import test_pb00701_mixed_boundary as old

a, E = m.a, m.E


def product_args(g=None, carrier=None):
    if g is None:
        g = a.pmul([-1, 0, 2], [-1, 0, 2])
    c, s, ident, span, off, rate = old.candidate_args() if carrier is None else carrier
    return ({h: a.pmul(g, p) for h, p in c.items()},
            {h: a.pmul(g, p) for h, p in s.items()}, ident, span, off, rate)


def certificate(g, lo='1/2', hi='3/4'):
    # A candidate certificate only: the real source/field constructor checks
    # the interval, primitive polynomial, multiplicity and irrationality.
    lo, hi = Q(lo), Q(hi)
    return {'root_type': 'REAL_ALGEBRAIC_IRRATIONAL',
            'source_polynomial_primitive': list(a.primitive(g)),
            'defining_square_free_polynomial': list(a.primitive(E.square_free(g))),
            'isolating_interval': [str(lo), str(hi)], 'multiplicity': a._multiplicity(g, lo, hi),
            'unique_root_proof': {'method': 'EXACT_STURM_OPEN_INTERVAL_COUNT',
                                 'sturm_open_root_count': 1, 'rational_endpoints_are_not_roots': True},
            'binary_float_used': False, 'epsilon_used': False,
            'sampling_used': False, 'approximate_root_used': False}


class FactorAlgebraTests(unittest.TestCase):
    def test_maximal_monic_all_channels_and_original_scaling(self):
        original = product_args()
        proof = m.factor_source(*original)
        self.assertEqual(proof['monic_factor'], ['1/4', '0', '-1', '0', '1'])
        self.assertEqual(proof['quotient_amplitude_gcd'], ['1'])
        self.assertFalse(proof['physical_source_replaced_by_carrier'])
        for original_map, key in zip(original[:2], ('cos_polynomials', 'sin_polynomials')):
            for h, p in original_map.items():
                self.assertEqual(a.pmul(proof['monic_factor'], proof['carrier_material'][key][str(h)]), p)
        negative = list(original)
        negative[0] = {h:a.pscale(p, -3) for h,p in original[0].items()}
        negative[1] = {h:a.pscale(p, -3) for h,p in original[1].items()}
        changed = m.factor_source(*negative)
        self.assertEqual(changed['monic_factor'], proof['monic_factor'])
        self.assertEqual(changed['carrier_material']['cos_polynomials']['2'], ['-3/25000000'])
        # A single non-anchor or harmonic-zero channel without g destroys the
        # alleged common factor; neither may be silently ignored.
        for h in (0, 3):
            missing = list(original);missing[0] = dict(original[0]);missing[0][h] = [1]
            self.assertEqual(m.factor_source(*missing)['status'], 'NOT_APPLICABLE')

    def test_power_spline_conversion_reconstructs_exactly(self):
        original = product_args()
        material = a._material(*original)
        spec = m.source_spec(material)
        for key, src in (('cos_splines', original[0]), ('sin_splines', original[1])):
            for h, spline in spec[key].items():
                n = spline['degree'];out = [Q(0)] * (n + 1)
                # Independent expansion of sum b_j binom(n,j)t^j(1-t)^(n-j).
                for j, bj in enumerate(spline['controls']):
                    for k in range(n - j + 1):
                        out[j+k] += Q(bj) * comb(n,j) * comb(n-j,k) * (-1)**k
                self.assertEqual(a.trim(out), a.trim(src[int(h)]))
        global_args = (*original[:3], ('2','5'), '-1/6', '1/48')
        glob = m.source_spec(a._material(*global_args))
        self.assertEqual(glob['parameter_lo'], '2')
        self.assertTrue(all(set(x['knots']) == {'2','5'} for x in glob['cos_splines'].values()))

    def test_irrational_disjointness_and_physical_even_odd_jets(self):
        p = [-1,0,2]
        for power in (1, 2, 3, 4):
            g = [Q(1)]
            for _ in range(power):g = a.pmul(g, p)
            fac = m.factor_source(*product_args(g))
            cert = certificate(fac['monic_factor'])
            event = m.irrational_factor_event(fac, cert)
            self.assertEqual(event['carrier_relation'], 'NONZERO')
            self.assertEqual(event['physical_relation'], 'ZERO')
            self.assertEqual(event['physical_multiplicity'], power)
            self.assertEqual(event['carrier_jets']['physical_multiplicity'], 0)
            self.assertEqual(event['physical_jets']['physical_multiplicity'], power)
            self.assertTrue(event['carrier_jets']['endpoint_laurent'])
            self.assertFalse(event['carrier_orientation_ownership_invented'])
            self.assertFalse(event['trigonometric_sign_search_used'])
        changed = copy.deepcopy(fac)
        changed['source_material']['phase_turn_law']['rate'] = '0'
        with self.assertRaises(ValueError):m.irrational_factor_event(changed, cert)

    def test_algebraic_factor_need_not_be_a_carrier_orientation_root(self):
        fac = m.factor_source(*product_args())
        event = m.irrational_factor_event(fac, certificate(fac['monic_factor']))
        field = a.RealField((-1,0,2), (Q(1,2),Q(3,4)), 0)
        carrier = fac['carrier_material']
        for coordinate in ('A','B'):
            self.assertFalse(field.element(a._orientation(carrier, 1, coordinate)).is_zero())
        self.assertEqual(event['source_binding_sha256'], m.b.digest(fac['source_material']))
        self.assertNotEqual(event['source_binding_sha256'], m.b.digest(carrier))

    def test_factor_certificate_and_theorem_premise_corruption(self):
        fac = m.factor_source(*product_args());cert = certificate(fac['monic_factor'])
        for key, value in (('multiplicity', True), ('multiplicity', 1),
                           ('isolating_interval', ['1/8','1/4']),
                           ('source_polynomial_primitive', [-1,0,2]),
                           ('defining_square_free_polynomial', [-2,0,3]),
                           ('binary_float_used', True)):
            bad = copy.deepcopy(cert);bad[key] = value
            with self.subTest(key=key),self.assertRaises((ValueError,TypeError)):
                m.irrational_factor_event(fac,bad)
        bad = copy.deepcopy(fac)
        for key in ('cos_polynomials','sin_polynomials'):
            bad['carrier_material'][key] = {h:[str(x) for x in a.pmul(p,[-1,0,2])]
                                            for h,p in bad['carrier_material'][key].items()}
        with self.assertRaisesRegex(ValueError, 'coprime'):m.irrational_factor_event(bad, cert)

    def test_global_phase_and_multiplicity_scale(self):
        original = list(product_args())
        original[3:] = [('2','5'), '-1/6', '1/48']
        fac = m.factor_source(*original)
        event = m.irrational_factor_event(fac, certificate(fac['monic_factor']))
        self.assertEqual(event['global_source_cut'], ['2','3'])
        self.assertEqual(event['phase_turn'], ['-1/8','1/16'])
        self.assertEqual(event['global_jet_scale'], '1/9')

    def test_identity_constant_and_exact_input_rejections(self):
        self.assertEqual(m.factor_source({}, {}, 'zero', ('0','1'), 0, 1)['status'], 'BLOCKED')
        self.assertEqual(m.factor_source(*old.candidate_args())['status'], 'NOT_APPLICABLE')
        for index, value in ((2,False), (3,('0',True)), (4,0.0), (5,True)):
            bad = list(product_args());bad[index] = value
            with self.assertRaises((ValueError,TypeError)):m.factor_source(*bad)
        for c in ({True:[1]}, {1:[False]}, {1:[0.1]}):
            with self.assertRaises((ValueError,TypeError)):m.factor_source(c,{},'bad',('0','1'),0,1)


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FactorAlgebraTests))
    if not result.wasSuccessful():raise AssertionError('v50 exact factor algebra failed')

if __name__ == '__main__':run()
