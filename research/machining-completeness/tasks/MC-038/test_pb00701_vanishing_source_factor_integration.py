#!/usr/bin/env python3
"""Actual complete-source predecessors and checked physical factor/carrier unions."""
from fractions import Fraction as Q
from functools import lru_cache
from math import comb
from pathlib import Path
import copy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_vanishing_source_factor_model as m
import pb00701_vanishing_source_factor_certificate as checker
import pb00701_mixed_multicut_model as prior
import pb00701_mixed_orientation_roots_model as roots
import test_pb00701_vanishing_source_factor as core
import test_pb00701_mixed_boundary as old

a = m.a


def power(p, n):
    result = [Q(1)]
    for _ in range(n):
        result = a.pmul(result, p)
    return result


def source(args):
    return m.source_spec(a._material(*args))


def route(result):
    assert result['status'] == 'CERTIFIED', result
    rows = [s['route'] for s in result['spans'] if s.get('route_kind') == 'PB00701_V50_VANISHING_SOURCE_FACTOR']
    assert len(rows) == 1, result
    return rows[0]


@lru_cache(maxsize=1)
def acceptance():
    # Only cache this already executed immutable test fixture; never replace
    # actual predecessor novelty or source integration with a mock oracle.
    args = core.product_args()
    spec = source(args)
    predecessor = prior.classify_required_analytic_event(spec)
    result = m.classify_required_analytic_event(spec)
    return args, predecessor, result


def coincident_carrier():
    args = list(old.candidate_args())
    args[4] = '-5/32'  # at t=1/2: theta=-pi/4, X=B=C2*cos(2theta)=0
    return tuple(args)


def reverse_poly(poly):
    out = [Q(0)] * len(poly)
    for k, value in enumerate(poly):
        for j in range(k + 1):
            out[j] += Q(value) * comb(k, j) * (-1) ** j
    return a.trim(out)


class ProductIntegrationTests(unittest.TestCase):
    def test_genuine_complete_predecessor_residual_with_tangency(self):
        args, predecessor, result = acceptance()
        self.assertEqual(predecessor['status'], 'BLOCKED')
        proof = route(result)
        self.assertTrue(checker.validate_product_event(proof, *args))
        self.assertEqual(proof['carrier_evidence']['owner'], 'PB00701_V49_MIXED_BOUNDARY_MULTICUT')
        self.assertEqual(proof['factorization']['monic_factor'], ['1/4', '0', '-1', '0', '1'])
        self.assertEqual((proof['distinct_roots_open'], proof['multiple_roots_open']), (2, 1))
        self.assertEqual((proof['crossings_open'], proof['tangencies_open']), (1, 1))
        self.assertEqual(proof['endpoint_root_multiplicity'], {})
        self.assertFalse(proof['physical_product_strict_monotonicity_claimed'])
        self.assertFalse(proof['general_nonmonotone_solver_claimed'])
        event = proof['factor_root_evidence']['factor_events'][0]
        self.assertEqual(event['physical_multiplicity'], 2)
        self.assertEqual(event['algebraic_disjointness_evidence']['carrier_relation'], 'NONZERO')
        self.assertEqual(proof['carrier_root_correspondence']['carrier_only_open_roots'], 1)
        print('v50 actual source: complete v49 BLOCKED -> irrational double factor root + disjoint simple modulated-carrier root')

    def test_rational_and_irrational_simple_odd_even_factor_roots(self):
        for factor in ([-Q(1, 2), 1], [-1, 0, 2]):
            for n in (1, 2, 3):
                args = core.product_args(power(factor, n))
                proof = m.build_product_event(*args)
                self.assertEqual(proof['status'], 'CERTIFIED', proof)
                self.assertTrue(checker.validate_product_event(proof, *args))
                event = proof['factor_root_evidence']['factor_events'][0]
                self.assertEqual(event['factor_multiplicity'], n)
                self.assertEqual(event['carrier_multiplicity'], 0)
                self.assertEqual(event['event_kind'], 'CROSSING' if n % 2 else 'TANGENCY')
                self.assertEqual(proof['distinct_roots_open'], 2)
                self.assertEqual(proof['multiple_roots_open'], int(n > 1))

    def test_rational_carrier_coincidence_is_one_root_with_additive_multiplicity(self):
        for n in (1, 2, 3):
            args = core.product_args(power([-Q(1, 2), 1], n), coincident_carrier())
            proof = m.build_product_event(*args)
            self.assertEqual(proof['status'], 'CERTIFIED', proof)
            self.assertTrue(checker.validate_product_event(proof, *args))
            event = proof['factor_root_evidence']['factor_events'][0]
            self.assertEqual(event['carrier_endpoint_evidence']['relation'], 'ZERO')
            self.assertEqual(event['physical_multiplicity'], n + 1)
            self.assertTrue(event['coincidence_counted_once'])
            self.assertEqual(proof['distinct_roots_open'], 1)
            self.assertEqual(proof['multiple_roots_open'], 1)
            self.assertEqual(proof['carrier_root_correspondence']['carrier_only_open_roots'], 0)
            # The rational factor root is also the carrier's orientation proof
            # boundary. Neither the proof cut nor the second factor counts twice.
            self.assertEqual(proof['total_distinct_roots_closed'], 1)

    def test_endpoint_factor_roots_and_carrier_coincidence(self):
        for factor, side, n in (([0, 1], 'left', 2), ([-1, 1], 'right', 3)):
            args = core.product_args(power(factor, n))
            proof = m.build_product_event(*args)
            self.assertEqual(proof['status'], 'CERTIFIED', proof)
            self.assertEqual(proof['endpoint_root_multiplicity'], {side: n})
            self.assertEqual(proof['distinct_roots_open'], 1)
            self.assertEqual(proof['total_distinct_roots_closed'], 2)
            self.assertTrue(checker.validate_product_event(proof, *args))
        for c0, factor, side in (([-Q(1, 100), 1], [0, 1], 'left'), ([-1, 1], [-1, 1], 'right')):
            carrier = ({0: c0, 1: [Q(1, 100)]}, {2: [Q(1, 200)]}, 'old-strict-carrier', ('0', '1'), '0', '1/4')
            args = core.product_args(power(factor, 2), carrier)
            proof = m.build_product_event(*args)
            self.assertEqual(proof['status'], 'CERTIFIED', proof)
            self.assertEqual(proof['carrier_evidence']['owner'], 'PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR')
            self.assertEqual(proof['endpoint_root_multiplicity'], {side: 3})
            self.assertEqual(proof['distinct_roots_open'], 0)
            self.assertEqual(proof['total_distinct_roots_closed'], 1)
            self.assertTrue(checker.validate_product_event(proof, *args))

    def test_nearby_factor_and_carrier_roots_are_not_coincident(self):
        for direction in (-1, 1):
            factor = [-Q(1, 4) - Q(direction, 10**6), 0, 1]
            args = core.product_args(factor, coincident_carrier())
            proof = m.build_product_event(*args)
            self.assertEqual(proof['status'], 'CERTIFIED', proof)
            self.assertEqual(proof['distinct_roots_open'], 2)
            self.assertEqual(proof['carrier_root_correspondence']['rational_open_coincidences'], 0)
            cert = proof['factor_root_evidence']['root_certificate']['irrational_open_roots'][0]
            cut = m.b.Boundary.from_source(factor, cert)
            self.assertEqual(m.b.order_certificate(cut, m.b.Boundary.at(Q(1, 2)))['comparison'], direction)
            self.assertTrue(checker.validate_product_event(proof, *args))

    def test_root_free_factor_and_uncertified_carrier_do_not_change_scope(self):
        args = core.product_args([1, 0, 1])
        proof = m.build_product_event(*args)
        self.assertEqual(proof['status'], 'CERTIFIED', proof)
        self.assertEqual(proof['factor_root_evidence']['factor_events'], [])
        self.assertEqual(proof['distinct_roots_open'], 1)
        self.assertTrue(checker.validate_product_event(proof, *args))
        carrier = list(old.candidate_args()); carrier[0] = dict(carrier[0]); carrier[0][0] = [1]
        args = core.product_args([1, 0, 1], tuple(carrier))
        proof = m.build_product_event(*args)
        self.assertEqual(proof['status'], 'CERTIFIED', proof)
        self.assertEqual(proof['total_distinct_roots_closed'], 0)
        unresolved = ({1: [1], 2: [1]}, {1: [0, 1]}, 'unresolved-carrier', ('0', '1'), '0', '1')
        previous = prior.classify_required_analytic_event(source(unresolved))
        self.assertEqual(previous['status'], 'BLOCKED', previous)
        result = m.build_product_event(*core.product_args([0, 1], unresolved))
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result['reason'], 'CARRIER_NOT_CERTIFIED')

    def test_reverse_global_negative_source_and_phase_invariance(self):
        original = core.product_args()
        for reversal, negative, global_span in ((True, False, False), (False, True, False), (False, False, True)):
            c, s, ident, span, off, rate = original
            off, rate = Q(off), Q(rate)
            if reversal:
                c = {h: reverse_poly(p) for h, p in c.items()}
                s = {h: reverse_poly(p) for h, p in s.items()}
                off, rate = off + rate, -rate
            if negative:
                c = {h: a.pscale(p, -3) for h, p in c.items()}
                s = {h: a.pscale(p, -3) for h, p in s.items()}
            if global_span:
                span = ('2', '5'); off, rate = off - rate * Q(2, 3), rate / 3
            args = (c, s, 'transformed-product', span, str(off), str(rate))
            proof = m.build_product_event(*args)
            self.assertEqual(proof['status'], 'CERTIFIED', proof)
            self.assertEqual((proof['distinct_roots_open'], proof['multiple_roots_open']), (2, 1))
            self.assertTrue(checker.validate_product_event(proof, *args))
            if global_span:
                event = proof['factor_root_evidence']['factor_events'][0]['algebraic_disjointness_evidence']
                self.assertEqual(event['global_jet_scale'], '1/9')
            if negative:
                events = proof['physical_exterior_evidence']['endpoints']
                self.assertEqual([x['physical_event']['relation'] for x in events], ['POSITIVE', 'NEGATIVE'])

    def test_source_and_all_product_certificate_mutations_are_rejected(self):
        args, _, result = acceptance(); proof = route(result)
        changes = [
            (['factorization', 'monic_factor'], ['1']),
            (['factorization', 'channel_identities', 0, 'quotient'], ['0']),
            (['factorization', 'source_material', 'phase_turn_law', 'rate'], '-1/16'),
            (['carrier_evidence', 'owner'], 'FORGED'),
            (['carrier_evidence', 'route', 'distinct_roots_open'], 0),
            (['carrier_evidence', 'route', 'multiple_roots_open'], 1),
            (['carrier_evidence', 'route', 'children', 0, 'derivative_certificate', 'orthants'], []),
            (['factor_root_evidence', 'root_certificate', 'distinct_roots_open'], True),
            (['factor_root_evidence', 'root_certificate', 'all_roots_accounted_exactly'], False),
            (['factor_root_evidence', 'factor_events', 0, 'physical_multiplicity'], 1),
            (['factor_root_evidence', 'factor_events', 0, 'algebraic_disjointness_evidence', 'field', 'root_index_in_open_unit_interval'], 1),
            (['factor_root_evidence', 'factor_events', 0, 'algebraic_disjointness_evidence', 'carrier_jets', 'endpoint_laurent'], []),
            (['factor_root_evidence', 'factor_events', 0, 'algebraic_disjointness_evidence', 'carrier_orientation_ownership_invented'], True),
            (['physical_exterior_evidence', 'endpoints', 0, 'physical_event', 'relation'], 'ZERO'),
            (['carrier_root_correspondence', 'carrier_only_open_roots'], 0),
            (['distinct_roots_open'], 1), (['multiple_roots_open'], False),
            (['physical_product_strict_monotonicity_claimed'], True),
            (['general_nonmonotone_solver_claimed'], True),
            (['source_parameter_id'], 'another-source'),
        ]
        for path, value in changes:
            bad = copy.deepcopy(proof); node = bad
            for key in path[:-1]: node = node[key]
            node[path[-1]] = value
            with self.subTest(path=path), self.assertRaises((ValueError, TypeError, KeyError, AssertionError)):
                checker.validate_product_event(bad, *args)
        for index, value in ((2, 'other-id'), (3, ('2', '5')), (4, '0'), (5, '-1/16')):
            changed = list(args); changed[index] = value
            with self.assertRaises((ValueError, TypeError, KeyError, AssertionError)):
                checker.validate_product_event(proof, *changed)
        with patch.object(m, 'carrier_proof', side_effect=AssertionError('no carrier selection in checker')), \
             patch.object(prior, 'classify_required_analytic_event', side_effect=AssertionError('no predecessor search')), \
             patch.object(prior, 'certify_derivative', side_effect=AssertionError('no replacement derivative route')), \
             patch.object(m.v46, '_decide_endpoint', side_effect=AssertionError('no endpoint sign search')):
            self.assertTrue(checker.validate_product_event(proof, *args))

    def test_predecessor_success_source_rejection_and_unrelated_errors_preserved(self):
        spec = source(old.candidate_args()); previous = prior.classify_required_analytic_event(spec)
        self.assertEqual(previous['status'], 'CERTIFIED')
        with patch.object(m, 'build_product_event', side_effect=AssertionError('older success must keep owner')):
            self.assertEqual(m.classify_required_analytic_event(spec), previous)
        spec = source(core.product_args())
        for key, value in (('v50_certificate', {}), ('epsilon', '1/100'), ('second_phase_law', {})):
            bad = copy.deepcopy(spec); bad[key] = value
            previous = prior.classify_required_analytic_event(bad)
            self.assertNotEqual(previous['status'], 'CERTIFIED')
            self.assertEqual(m.classify_required_analytic_event(bad), previous)
        for key, value in (('phase_turn_rate', 0.0625), ('source_parameter_id', False)):
            bad = copy.deepcopy(spec); bad[key] = value
            try:
                result = m.classify_required_analytic_event(bad)
            except (ValueError, TypeError, AssertionError):
                continue
            self.assertNotEqual(result['status'], 'CERTIFIED')
        with patch.object(prior, 'classify_required_analytic_event', side_effect=ValueError('unrelated failure')):
            with self.assertRaisesRegex(ValueError, 'unrelated failure'):
                m.classify_required_analytic_event(spec)

    def test_exact_resource_refusal_at_builder_checker_and_source_stages(self):
        args, _, result = acceptance(); proof = route(result)
        for owner, name in ((m, 'factor_source'), (m, 'carrier_proof'), (roots, 'exact_orientation_roots'),
                            (m, 'irrational_factor_event'), (m, 'physical_exteriors'), (m, 'assemble_product')):
            with self.subTest(stage=name), patch.object(owner, name, side_effect=MemoryError('injected')):
                refused = m.build_product_event(*args)
                self.assertEqual(refused['status'], 'RESOURCE_REFUSAL')
                self.assertFalse(refused['is_truth_value'])
        for name in ('factor_source', 'validate_carrier', 'factor_root_events', 'physical_exteriors', 'assemble_product'):
            with self.subTest(checker_stage=name), patch.object(m, name, side_effect=MemoryError('injected')):
                refused = checker.validate_product_event(proof, *args)
                self.assertEqual(refused['status'], 'RESOURCE_REFUSAL')
                self.assertFalse(refused['is_truth_value'])
        refusal = m.refusal('typed')
        for name in ('factor_source', 'carrier_proof', 'factor_root_events', 'physical_exteriors'):
            with patch.object(m, name, return_value=refusal):
                self.assertEqual(m.build_product_event(*args), refusal)
        with patch.object(m, 'irrational_factor_event', return_value=refusal):
            self.assertEqual(m.build_product_event(*args), refusal)
        with patch.object(m, 'validate_carrier', return_value=refusal):
            self.assertEqual(checker.validate_product_event(proof, *args), refusal)
        with patch.object(prior, 'classify_required_analytic_event', return_value=refusal):
            self.assertEqual(m.classify_required_analytic_event(source(args)), refusal)


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProductIntegrationTests))
    if not result.wasSuccessful():
        raise AssertionError('v50 actual-source product suite failed')


if __name__ == '__main__':
    run()
