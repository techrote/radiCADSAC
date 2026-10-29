#!/usr/bin/env python3
"""Deterministic source-bound subset tests and explicit rejection controls for MC-038."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unittest
from pathlib import Path

import pb00701_checked_child_composition_core as core

ROOT = Path(__file__).resolve().parents[4]
CORPUS = ROOT / 'research/machining-completeness/tasks/MC-038/pb00701-finite-owner-corpus-v54.json'
DOMAIN = ROOT / 'research/machining-completeness/tasks/MC-002/domain-contract-v1.json'
AUTHORITY = ROOT / 'handoffs/current-authority.json'
FROZEN_CORPUS_BLOB = '5841c331579489b25caef38cd412bdbf286f9134'
DOMAIN_BLOB = '23de82f5240a72509f7afe4acd5948b65bc4ff13'
AUTHORITY_BLOB = 'fa0233323a0804d8a5d3eb7cd892a274a6173fab'


def blob_sha(path):
    contents = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(contents)).encode() + b'\0' + contents).hexdigest()


def authoritative_contract():
    if blob_sha(CORPUS) != FROZEN_CORPUS_BLOB:
        raise RuntimeError('original frozen 121-case v54 evidence changed')
    if blob_sha(DOMAIN) != DOMAIN_BLOB:
        raise RuntimeError('original domain contract changed')
    if blob_sha(AUTHORITY) != AUTHORITY_BLOB:
        raise RuntimeError('current MC-1 programme authority changed')
    authority = json.loads(AUTHORITY.read_text())
    domain = json.loads(DOMAIN.read_text())
    if authority['production_authorized'] is not False or authority['capability_status'] != 'NOT_ESTABLISHED':
        raise RuntimeError('MC-1 programme gate unexpectedly changed')
    operations = [op['id'] for op in domain['operation_map']]
    required = domain['coverage_rule']['required_operation_ids']
    if len(operations) != 26 or len(set(operations)) != 26 or operations != required:
        raise RuntimeError('26-operation domain denominator changed')
    return True


def span(left, right, coefficients, scale, factors):
    return {'interval': [left, right], 'coefficients': coefficients,
            'factor_witness': {'scale': scale, 'linear_factors': [
                {'root': root, 'multiplicity': multiplicity} for root, multiplicity in factors]}}


def source(spans, cuts=()):
    return {'schema': core.SCHEMA, 'source_kind': core.SOURCE_KIND,
            'source_parameter_id': 'source-time-t', 'source_spans': spans,
            'cuts': list(cuts)}


def benchmark():
    # p0=(s-1/2)(s-1), p1=-(s-1)(s-3/2)^2.
    a = span('0', '1', ['1/2', '-3/2', '1'], '1', [('1/2', 1), ('1', 1)])
    b = span('1', '2', ['9/4', '-21/4', '4', '-1'], '-1', [('1', 1), ('3/2', 2)])
    return source([a, b], ('3/2', '1/4', '1', '1/4'))


class CompositionCoreTests(unittest.TestCase):
    def test_exact_source_both_sides_knot_and_proof_cuts(self):
        cert = core.compose(benchmark())
        self.assertEqual(cert['status'], 'CONDITIONAL_EXACT_RATIONAL_SUBSET_COMPOSED')
        self.assertEqual(cert['proof_cuts'], ['1/4', '1', '3/2'])
        self.assertEqual(cert['source_knots'], ['1'])
        self.assertEqual([x['position'] for x in cert['events']], ['1/2', '1', '3/2'])
        self.assertEqual([x['kind'] for x in cert['events']],
                         ['CROSSING', 'SOURCE_KNOT_TOUCH', 'TANGENCY'])
        self.assertEqual(cert['events'][1]['left_order'], 1)
        self.assertEqual(cert['events'][1]['right_order'], 1)
        self.assertIsNone(cert['events'][1]['smooth_physical_multiplicity'])
        self.assertEqual(cert['events'][2]['smooth_physical_multiplicity'], 2)
        self.assertTrue(cert['events'][2]['on_proof_cut'])
        self.assertEqual(cert['summary']['distinct_roots_open'], 3)
        self.assertEqual(cert['summary']['smooth_crossings_open'], 1)
        self.assertEqual(cert['summary']['smooth_tangencies_open'], 1)
        self.assertEqual(cert['summary']['source_knot_zeros_open'], 1)
        self.assertEqual([x['sign'] for x in cert['maximal_open_sign_cells']],
                         ['POSITIVE', 'NEGATIVE', 'NEGATIVE', 'NEGATIVE'])
        self.assertFalse(cert['pb00701_certified'])
        self.assertFalse(cert['v27_v41_trigonometric_children_certified'])
        self.assertFalse(cert['production_authorized'])

    def test_source_knot_sign_change_not_global_multiplicity(self):
        obj = benchmark()
        obj['source_spans'][1] = span('1', '2', ['-9/4', '21/4', '-4', '1'], '1',
                                      [('1', 1), ('3/2', 2)])
        result = core.compose(obj)
        self.assertEqual(result['events'][1]['kind'], 'SOURCE_KNOT_SIGN_CHANGE')
        self.assertEqual((result['events'][1]['left_sign'], result['events'][1]['right_sign']),
                         (-1, 1))
        self.assertIsNone(result['events'][1]['smooth_physical_multiplicity'])

    def test_endpoint_zero_and_double_open_tangency(self):
        # s*(s-1)*(s-1/2)^2 = s^4 -2s^3 + 5/4s^2 - 1/4s.
        obj = source([span('0', '1', ['0', '-1/4', '5/4', '-2', '1'], '1',
                           [('0', 1), ('1/2', 2), ('1', 1)])], ['1/2'])
        result = core.compose(obj)
        self.assertEqual([x['kind'] for x in result['events']],
                         ['SOURCE_ENDPOINT_ZERO', 'TANGENCY', 'SOURCE_ENDPOINT_ZERO'])
        self.assertEqual(result['summary']['distinct_roots_open'], 1)
        self.assertEqual(result['summary']['distinct_roots_closed'], 3)
        self.assertEqual(result['events'][0]['left_sign'], None)
        self.assertEqual(result['events'][-1]['right_sign'], None)

    def test_constant_nonzero_and_arbitrary_certificate_cuts(self):
        obj = source([span('0', '1', ['-2'], '-2', []),
                      span('1', '2', ['-2'], '-2', [])],
                     ['1/4', '1/4', '1', '3/2'])
        result = core.compose(obj)
        self.assertEqual(result['events'], [])
        self.assertEqual(result['summary']['distinct_roots_open'], 0)
        self.assertEqual(result['maximal_open_sign_cells'],
                         [{'left': '0', 'right': '2', 'sign': 'NEGATIVE', 'open': True}])
        self.assertEqual(len(result['split_proof_cells']), 4)

    def test_source_order_independent_of_unsorted_factor_witness(self):
        obj = benchmark()
        before = core.compose(obj)
        for row in obj['source_spans']:
            row['factor_witness']['linear_factors'].reverse()
        self.assertEqual(before, core.compose(obj))

    def test_gap_or_overlap_rejected(self):
        for x in ['3/4', '5/4']:
            obj = benchmark()
            obj['source_spans'][1]['interval'][0] = x
            with self.assertRaises(core.InvalidWitness):
                core.compose(obj)

    def test_discontinuous_source_knot_rejected(self):
        obj = source([span('0', '1', ['1'], '1', []),
                      span('1', '2', ['2'], '2', [])])
        with self.assertRaises(core.InvalidWitness):
            core.compose(obj)

    def test_missing_or_forged_multiplicity_rejected(self):
        for m in [1, 3, 0, -2, True]:
            obj = benchmark()
            obj['source_spans'][1]['factor_witness']['linear_factors'][1]['multiplicity'] = m
            with self.assertRaises(core.InvalidWitness):
                core.compose(obj)

    def test_incomplete_factors_and_forged_coefficient_rejected(self):
        for mutation in ('omit', 'move', 'coef', 'scale'):
            obj = benchmark()
            factors = obj['source_spans'][0]['factor_witness']['linear_factors']
            if mutation == 'omit':
                factors.pop()
            elif mutation == 'move':
                factors[0]['root'] = '3/4'
            elif mutation == 'coef':
                obj['source_spans'][0]['coefficients'][1] = '-1'
            else:
                obj['source_spans'][0]['factor_witness']['scale'] = '2'
            with self.assertRaises(core.InvalidWitness):
                core.compose(obj)

    def test_count_only_or_forged_historical_owner_rejected(self):
        for extra_key, extra_val in [('distinct_roots_open', 3),
                                     ('route_kind', 'PB00701_V41_EXACT_ROTATED_COORDINATE_ORIENTATION_ROOT_PARTITION_COMPOSITION'),
                                     ('status', 'CERTIFIED'),
                                     ('phase_turn_law', {'rate': '1/2'})]:
            obj = benchmark()
            obj[extra_key] = extra_val
            with self.assertRaises(core.InvalidWitness):
                core.compose(obj)

    def test_unknown_source_kind_trigonometric_not_admitted(self):
        obj = benchmark()
        obj['source_kind'] = 'AFFINE_PHASE_MODULATED_TRIGONOMETRIC'
        with self.assertRaises(core.InvalidWitness):
            core.compose(obj)

    def test_missing_factor_premise_rejected(self):
        obj = source([span('0', '1', ['1', '0', '1'], '1', [])])
        with self.assertRaises(core.InvalidWitness):
            core.compose(obj)  # x^2+1 not pretend root-free via empty factor list

    def test_identity_zero_is_not_zero_distinct_roots(self):
        obj = source([span('0', '1', ['0'], '1', [])])
        result = core.compose(obj)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertFalse(result['is_truth_value'])

    def test_resource_refusal_is_nontruth(self):
        obj = source([span('0', '1', ['1'] + ['0']*24 + ['1'], '1', [])])
        result = core.compose(obj)
        self.assertEqual(result['status'], 'RESOURCE_REFUSAL')
        self.assertFalse(result['is_truth_value'])
        self.assertFalse(result['certification_authorized'])
        obj = benchmark()
        obj['cuts'] = ['1/2'] * (core.MAX_CUTS+1)
        self.assertEqual(core.compose(obj)['status'], 'RESOURCE_REFUSAL')

    def test_invalid_cut_and_noncanonical_numeric_rejected(self):
        for cut in ['0', '2', '-1/4', '5/2', '1.0', '2/4', True, 0.5]:
            obj = benchmark()
            obj['cuts'] = [cut]
            with self.assertRaises(core.InvalidWitness):
                core.compose(obj)

    def test_invalid_source_parameter_or_phony_certificate_key(self):
        for key in ('source_parameter_id', 'schema'):
            obj = benchmark()
            obj[key] = ''
            with self.assertRaises(core.InvalidWitness):
                core.compose(obj)
        obj = benchmark()
        obj['source_spans'][0]['factor_witness']['claimed_count'] = 999
        with self.assertRaises(core.InvalidWitness):
            core.compose(obj)

    def test_nonroot_cut_never_produces_event(self):
        obj = benchmark()
        obj['cuts'] = ['1/4', '7/4']
        result = core.compose(obj)
        self.assertEqual([e['position'] for e in result['events']], ['1/2','1','3/2'])
        self.assertTrue(all(not e['on_proof_cut'] for e in result['events']))

    def test_single_span_negative_slope_root_parity(self):
        obj = source([span('0', '2', ['2', '-1'], '-1', [('2', 1)])])
        result = core.compose(obj)
        self.assertEqual(result['events'][0]['kind'], 'SOURCE_ENDPOINT_ZERO')
        self.assertEqual(result['events'][0]['left_sign'], 1)
        self.assertEqual(result['maximal_open_sign_cells'][0]['sign'], 'POSITIVE')

    def test_source_digests_bind_parameter_and_coefficients(self):
        a = core.compose(benchmark())
        obj = benchmark()
        obj['source_parameter_id'] = 'other-source'
        b = core.compose(obj)
        self.assertNotEqual(a['source_binding_sha256'], b['source_binding_sha256'])
        # Proof cuts are non-physical and cannot change the physical source digest.
        obj = benchmark()
        obj['cuts'] = []
        self.assertEqual(a['source_binding_sha256'], core.compose(obj)['source_binding_sha256'])

    def test_original_authority_and_frozen_evidence_pins(self):
        self.assertTrue(authoritative_contract())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    opts = parser.parse_args()
    if not opts.contract and not opts.self_test:
        parser.error('use --contract --self-test')
    if opts.contract:
        authoritative_contract()
        print('MC-1 authority and frozen v54 corpus pins: checked')
    if opts.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(CompositionCoreTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
