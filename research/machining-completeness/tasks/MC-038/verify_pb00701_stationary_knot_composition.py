#!/usr/bin/env python3
"""Deterministic frozen stationary-source composition and algebraic knot controls."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import unittest
from fractions import Fraction as Q

import pb00701_stationary_knot_composition as core

P = None


def test_spans(*descriptors):
    out = []
    for interval, coefficients in descriptors:
        lo, hi = map(Q, interval)
        view = P.build_polynomial_view(coefficients, source_left=lo, source_right=hi)
        out.append({'interval': list(interval), 'polynomial': coefficients, 'view': view})
    return out


class StationaryCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global P
        P = core.stationary()

    def test_three_frozen_source_cases_and_unaltered_blocked_dispositions(self):
        cases = core.replay_frozen_stationary_cases(P)
        self.assertEqual(len(cases), 3)
        self.assertEqual(sum(c['historical_v54_disposition'].startswith('BLOCKED:')
                             for c in cases), 2)
        for case in cases:
            with self.subTest(case=case['source_case_id']):
                self.assertTrue(case['original_source_sha256'])
                self.assertEqual(len(case['maximal_open_sign_cells']),
                                 len(case['ordered_physical_zero_events']) + 1)
                self.assertFalse(case['pb00701_certified'])
                self.assertFalse(case['general_v27_v41_theorem_claimed'])
                self.assertFalse(case['production_authorized'])

    def test_nonzero_continuous_knot_not_an_event(self):
        spans = test_spans((['0', '1'], [Q(1,4), -1, 1]),
                           (['1', '2'], [Q(1,4)]))
        result = core.compose_polynomial_spans(spans, P)
        self.assertEqual(result['true_source_knots'][0]['kind'], 'NONZERO_KNOT_NOT_ROOT')
        self.assertEqual(len(result['ordered_physical_zero_events']), 1)
        self.assertEqual(result['ordered_physical_zero_events'][0]['multiplicity'], 2)
        self.assertEqual([x['sign'] for x in result['maximal_open_sign_cells']],
                         ['POSITIVE', 'POSITIVE'])

    def test_knot_zero_crosses_once_with_separate_one_sided_orders(self):
        spans = test_spans((['0', '1'], [-1, 1]), (['1', '2'], [0, 1]))
        result = core.compose_polynomial_spans(spans, P)
        self.assertEqual(result['distinct_open_physical_zeros'], 1)
        event = result['ordered_physical_zero_events'][0]
        self.assertEqual(event['kind'], 'SOURCE_KNOT_ZERO')
        self.assertEqual(event['event_kind'], 'CROSSING')
        self.assertEqual([event['left_one_sided_order'], event['right_one_sided_order']], [1,1])
        self.assertFalse(event['global_smooth_multiplicity_claimed'])
        self.assertEqual([x['sign'] for x in result['maximal_open_sign_cells']],
                         ['NEGATIVE', 'POSITIVE'])

    def test_knot_zero_touching_with_different_orders(self):
        spans = test_spans((['0', '1'], [1, -1]), (['1', '2'], [0, 0, 1]))
        result = core.compose_polynomial_spans(spans, P)
        event = result['ordered_physical_zero_events'][0]
        self.assertEqual(event['event_kind'], 'TOUCHING')
        self.assertEqual([event['left_one_sided_order'], event['right_one_sided_order']], [1,2])
        self.assertEqual([x['sign'] for x in result['maximal_open_sign_cells']],
                         ['POSITIVE','POSITIVE'])
        self.assertFalse(event['global_smooth_multiplicity_claimed'])

    def test_knot_zero_crossing_even_left_and_odd_right_orders(self):
        spans = test_spans((['0', '1'], [1, -2, 1]),
                           (['1', '2'], [0, 0, 0, -1]))
        result = core.compose_polynomial_spans(spans, P)
        event = result['ordered_physical_zero_events'][0]
        self.assertEqual(event['event_kind'], 'CROSSING')
        self.assertEqual([event['left_one_sided_order'], event['right_one_sided_order']], [2,3])
        self.assertEqual([x['sign'] for x in result['maximal_open_sign_cells']],
                         ['POSITIVE','NEGATIVE'])

    def test_unique_irrational_root_source_interval_not_invented_coordinate(self):
        spans = test_spans((['0', '1'], [-Q(1,2), 0, 1]),
                           (['1', '2'], [Q(1,2)]))
        result = core.compose_polynomial_spans(spans, P)
        event = result['ordered_physical_zero_events'][0]
        self.assertEqual(event['coordinate_kind'], 'UNIQUE_IMPLICIT_ALGEBRAIC_ZERO')
        self.assertIn('strict_bracket', event)
        self.assertNotIn('coordinate', event)
        self.assertEqual([x['sign'] for x in result['maximal_open_sign_cells']],
                         ['NEGATIVE','POSITIVE'])

    def test_endpoint_zero_is_not_an_interior_event(self):
        spans = test_spans((['0','1'], [0,1]), (['1','2'], [1]))
        result = core.compose_polynomial_spans(spans, P)
        self.assertEqual(result['distinct_open_physical_zeros'], 0)
        self.assertEqual(result['left_physical_endpoint']['relation'], 'ZERO')
        self.assertEqual(len(result['maximal_open_sign_cells']), 1)

    def test_discontinuous_or_overlapping_or_missing_source_spans_refused(self):
        for descriptors in (
            ((['0','1'], [1]), (['1','2'], [-1])),
            ((['0','1'], [1]), (['3/2','2'], [1])),
            ((['0','1'], [1]), (['1/2','2'], [1])),
        ):
            with self.subTest(descriptors=descriptors):
                with self.assertRaises(core.InvalidComposition):
                    core.compose_polynomial_spans(test_spans(*descriptors), P)

    def test_forged_multiplicity_sign_missing_root_and_unreviewed_keys_refused(self):
        base = test_spans((['0','1'], [-Q(1,2), 0, 1]))
        mutations = []
        x=copy.deepcopy(base); x[0]['view']['ordered_open_roots'][0]['multiplicity']=3; mutations.append(x)
        x=copy.deepcopy(base); x[0]['view']['ordered_open_roots'].clear(); mutations.append(x)
        x=copy.deepcopy(base); x[0]['view']['sign_cells'][0]['sign']='POSITIVE'; mutations.append(x)
        x=copy.deepcopy(base); x[0]['view']['owner']='FAKE'; mutations.append(x)
        x=copy.deepcopy(base); x[0]['interval']=['9','10']; mutations.append(x)
        for x in mutations:
            with self.subTest(mutation=x):
                with self.assertRaises((core.InvalidComposition, ValueError)):
                    core.compose_polynomial_spans(x, P)

    def test_identity_zero_and_resource_budget_are_nontruth(self):
        with self.assertRaises(core.InvalidComposition):
            core.compose_polynomial_spans(test_spans((['0','1'], [0])), P)
        with self.assertRaises(core.ResourceRefusal):
            core.compose_polynomial_spans([{}]*(core.MAX_SPANS+1), P)
        resource = core.no_truth('RESOURCE_REFUSAL','bounded')
        self.assertFalse(resource['is_truth_value'])
        self.assertFalse(resource['production_authorized'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    a = parser.parse_args()
    if not (a.contract or a.self_test):
        parser.error('select --contract or --self-test')
    global P
    if a.contract:
        P = core.stationary()
        results = core.run_bounded()
        if not isinstance(results, list):
            raise RuntimeError('stationary source replay gave a nontruth result: '+str(results))
        for r in results:
            print(json.dumps({'case': r['source_case_id'],
                              'source_spans': r['source_span_count'],
                              'physical_zeros': r['distinct_open_physical_zeros'],
                              'historical_disposition':r['historical_v54_disposition'],
                              'knot_events':[k['kind'] for k in r['true_source_knots']],
                              'programme_authorized':r['production_authorized']},sort_keys=True))
    if a.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(StationaryCompositionTests)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful(): sys.exit(1)

if __name__ == '__main__':
    main()
