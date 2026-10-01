#!/usr/bin/env python3
"""Independent coefficient identities plus adversarial real-field boundaries."""
from fractions import Fraction as F
from pathlib import Path
import copy
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_child_map_model as m


def certificate(poly=(-1, 0, 2), interval=(F(1, 2), F(3, 4)), multiplicity=1):
    """A checkable witness input, not an assumed authority: factory rederives it."""
    return {
        "root_type": "REAL_ALGEBRAIC_IRRATIONAL",
        "source_polynomial_primitive": list(m.primitive(poly)),
        "defining_square_free_polynomial": list(m.primitive(m.engine.square_free(poly))),
        "isolating_interval": [str(x) for x in interval],
        "multiplicity": multiplicity,
        "unique_root_proof": {"method": "EXACT_STURM_OPEN_INTERVAL_COUNT", "sturm_open_root_count": 1, "rational_endpoints_are_not_roots": True},
        "binary_float_used": False, "epsilon_used": False,
        "sampling_used": False, "approximate_root_used": False,
    }


def fixture_material(poly=(-1, 0, 2), *, interval=('0', '1'), rate='1/8'):
    # A=p, B=2p, so both coordinates have the same exact cut.
    return m._material({0: ['2/3'], 1: m.pscale(poly, 3), 2: [1, 2, 3, 4, 5]},
                       {0: [0], 1: m.pscale(poly, -1), 2: ['1/10']},
                       'source-s', interval, '-3/16', rate)


def fixture_cut(poly=(-1, 0, 2), interval=(F(1, 2), F(3, 4)), multiplicity=1):
    return {'certificate': certificate(poly, interval, multiplicity),
            'ownership': [{'harmonic': 1, 'coordinate': 'A', 'multiplicity': multiplicity},
                          {'harmonic': 1, 'coordinate': 'B', 'multiplicity': multiplicity}]}


class ExactFieldTests(unittest.TestCase):
    def setUp(self):
        self.k = m.RealField.from_source_certificate([-1, 0, 2], certificate())
        self.a = self.k.element([0, 1])
        self.z, self.o = self.k.element(0), self.k.element(1)

    def test_minimal_reduction_and_inverse(self):
        self.assertEqual(self.a ** 2, self.k.element('1/2'))
        self.assertEqual(self.a ** 4, self.k.element('1/4'))
        self.assertEqual(self.k.element([1, 0, 2]), self.k.element(2))
        self.assertEqual(self.a.inverse(), self.a * 2)
        self.assertEqual((self.o - self.a) * (self.o - self.a).inverse(), self.o)
        with self.assertRaises(ValueError): self.z.inverse()

    def test_reducible_square_free_is_not_minimal(self):
        # f=(2x^2-1)(x^2+1). Using f as modulus incorrectly leaves 2a^2-1 nonzero.
        p = m.pmul([-1, 0, 2], [1, 0, 1])
        field = m.RealField.from_source_certificate(p, certificate(p))
        self.assertEqual(field, self.k)
        self.assertTrue(field.element([-1, 0, 2]).is_zero())
        with self.assertRaises(ValueError): m.RealField(m.primitive(p), field.interval, 0)

    def test_rational_and_endpoint_factors_are_not_silently_fields(self):
        for extra in ([0, 1], [-1, 1], [-F(2, 3), 1], [0, -1, 1]):
            p = m.pmul([-1, 0, 2], extra)
            # Refined interval excludes the extra 2/3 root if present.
            field = m.RealField.from_source_certificate(p, certificate(p, (F(7, 10), F(3, 4))))
            self.assertEqual(field, self.k)
        p = [-1, 2]
        with self.assertRaises(ValueError):
            m.RealField.from_source_certificate(p, certificate(p, (F(1, 4), F(3, 4))))

    def test_repeated_and_even_multiplicity(self):
        for degree in (2, 3, 4):
            p = [1]
            for _ in range(degree): p = m.pmul(p, [-1, 0, 2])
            self.assertEqual(m.RealField.from_source_certificate(p, certificate(p, multiplicity=degree)), self.k)
            with self.assertRaises(ValueError): m.RealField.from_source_certificate(p, certificate(p, multiplicity=degree - 1))

    def test_canonical_embedding_and_conjugates(self):
        refined = certificate(interval=(F(7, 10), F(71, 100)))
        self.assertEqual(self.k, m.RealField.from_source_certificate([-1, 0, 2], refined))
        poly = [1, -8, 8]
        lo = m.RealField.from_source_certificate(poly, certificate(poly, (F(1, 8), F(1, 4))))
        hi = m.RealField.from_source_certificate(poly, certificate(poly, (F(3, 4), F(7, 8))))
        self.assertNotEqual(lo, hi)
        with self.assertRaises(ValueError): lo.element([0, 1]) + hi.element([0, 1])
        self.assertEqual(lo.element([-F(1, 2), 1]).sign(), -1)
        self.assertEqual(hi.element([-F(1, 2), 1]).sign(), 1)

    def test_exact_sign_no_epsilon(self):
        self.assertEqual((self.a - F(7, 10)).sign(), 1)
        self.assertEqual((self.a - F(71, 100)).sign(), -1)
        tiny = self.k.element(F(1, 2**150))
        self.assertEqual(tiny.sign(), 1)
        self.assertEqual((-tiny).sign(), -1)
        self.assertEqual((self.a * 2 - self.a.inverse()).sign(), 0)
        # Near an algebraic value, enclosures refine exactly rather than use epsilon.
        self.assertGreater(665857**2 - 2*470832**2, 0)
        self.assertEqual(self.k.element([F(-470832, 665857), 1]).sign(), 1)
        self.assertEqual(self.k.element([F(-665857, 941664), 1]).sign(), -1)

    def test_complete_finite_factorization_small_degrees(self):
        for factors in (([-1, 0, 2], [1, 0, 1]), ([-2, 0, 0, 1], [1, 1]),
                        ([1, -8, 8], [2, 1]), ([-1, 0, 2], [-1, 0, 3])):
            p = m.pmul(*factors)
            actual = m.irreducible_factors(p)
            self.assertEqual(set(actual), {m.primitive(x) for x in factors})
            rebuilt = [F(1)]
            for x in actual: rebuilt = m.pmul(rebuilt, x)
            self.assertEqual(m.primitive(rebuilt), m.primitive(p))
        # No rational roots is not by itself an irreducibility test for quartics.
        self.assertEqual(m.irreducible_factors([1, 1, 0, 0, 1]), ((1, 1, 0, 0, 1),))

    def test_exact_polynomial_restriction_known_coefficients(self):
        a, o, z, k = self.a, self.o, self.z, self.k
        self.assertEqual(m.compose_affine([0, 1], z, a), [z, a])
        self.assertEqual(m.compose_affine([0, 1], a, o - a), [a, o - a])
        self.assertEqual(m.compose_affine([0, 0, 1], z, a), [z, z, k.element('1/2')])
        self.assertEqual(m.compose_affine([0, 0, 1], a, o - a),
                         [k.element('1/2'), a * 2 - o, k.element('3/2') - a * 2])
        for p in ([0], [7], [1, 2], [1, -3, 2], [3, -2, 5, 0, F(7, 11), 9]):
            for offset, width in ((z, a), (a, o - a)):
                child = m.compose_affine(p, offset, width)
                back = m.compose_affine(child, -offset * width.inverse(), width.inverse())
                self.assertEqual(back, [k.element(x) for x in m.trim(p)])
                # Chain rule checked independently, including both amplitude channels.
                derivative = [x * i for i, x in enumerate(child)][1:] or [z]
                expected = [x * width for x in m.compose_affine(m.engine.deriv(p), offset, width)]
                self.assertEqual(m._etrim(derivative), m._etrim(expected))

    def test_bisection_provenance_phase_and_roundtrip(self):
        for parent in (('0', '1'), ('-2', '3/2')):
            for rate in ('1/8', '-1/8', '0'):
                material = fixture_material(interval=parent, rate=rate)
                record = m._bisection(material, fixture_cut())
                self.assertEqual(record['status'], 'REPRESENTATION_CERTIFIED')
                self.assertFalse(record['analytic_cut_consumed'])
                left, right = record['children']
                self.assertEqual(left['parent_source_interval'][1], right['parent_source_interval'][0])
                self.assertEqual(left['parent_source_interval'][0], [parent[0]])
                self.assertEqual(right['parent_source_interval'][1], [parent[1]])
                for item in record['children']: self.assertTrue(item['exact_polynomial_roundtrip'])
                self.assertEqual(record['internal_phase_kind'], 'RATIONAL' if rate == '0' else 'ALGEBRAIC_IRRATIONAL')
                if rate != '0': self.assertEqual(record['endpoint_event_authority'], m.ENDPOINT_BLOCKER)
        p = m.pmul([-1, 0, 2], [-1, 0, 2])
        record = m._bisection(fixture_material(p), fixture_cut(p, multiplicity=2))
        self.assertEqual([x['multiplicity'] for x in record['orientation_ownership']], [2, 2])
        self.assertFalse(record['physical_event_inferred_from_orientation_root'])

    def test_certificate_corruption_and_nonexact_input(self):
        original = certificate()
        mutations = [
            ('defining_square_free_polynomial', [-1, 0, 3]),
            ('defining_square_free_polynomial', [-1.0, 0, 2]),
            ('source_polynomial_primitive', [-1, 0, 3]),
            ('isolating_interval', ['1/100', '1/50']),
            ('isolating_interval', ['0', '1']),
            ('isolating_interval', ['3/4', '1/2']),
            ('isolating_interval', [0.5, '3/4']),
            ('multiplicity', 2), ('multiplicity', True),
            ('binary_float_used', True), ('epsilon_used', True),
            ('root_type', 'RATIONAL'),
        ]
        for key, value in mutations:
            bad = copy.deepcopy(original); bad[key] = value
            with self.subTest(key=key, value=value), self.assertRaises((ValueError, TypeError)):
                m.RealField.from_source_certificate([-1, 0, 2], bad)
        for value in (True, 0.5, float('nan'), float('inf')):
            with self.assertRaises((TypeError, ValueError)): self.k.element(value)
        with self.assertRaises(ValueError): m.Element(self.k, (F(-1), F(0), F(2)))
        bad = fixture_cut(); bad['ownership'][1]['multiplicity'] = 2
        with self.assertRaises(ValueError): m._bisection(fixture_material(), bad)
        bad_material = fixture_material(); bad_material['sin_polynomials']['1'] = ['1']
        with self.assertRaises(ValueError): m._bisection(bad_material, fixture_cut())


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ExactFieldTests))
    if not result.wasSuccessful(): raise AssertionError('v45 exact-field adversarial suite failed')


if __name__ == '__main__':
    run()
