#!/usr/bin/env python3
"""Actual v44 source-lowering/precedence and forged child-record controls."""
from fractions import Fraction as F
from pathlib import Path
import copy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_child_map_model as m
import pb00701_algebraic_orientation_cut_model as v44
import test_pb00701_algebraic_orientation_cut_adversarial as v44test
import test_pb00701_correlated_closed_handoff_adversarial as v43test


def args(poly=(-1, 0, 2), *, rate='1/8'):
    return ({1: m.pscale(poly, 3)}, {1: m.pscale(poly, -1)}, 'source-s', ('0', '1'), '-3/16', rate)


class SourceIntegrationTests(unittest.TestCase):
    def test_genuine_residual_representation_not_event_promotion(self):
        source = v44test._source()
        baseline = v44.classify_required_analytic_event(source)
        self.assertEqual(baseline['status'], 'BLOCKED')
        result = m.represent_required_event_children(source)
        self.assertEqual(result['status'], 'REPRESENTATION_CERTIFIED')
        self.assertEqual(result['predecessor_event_result'], baseline)
        self.assertFalse(result['analytic_cut_consumed'])
        for item in result['span_representations']:
            rep = item['representation']
            self.assertEqual(rep['status'], 'REPRESENTATION_CERTIFIED')
            for split in rep['independent_single_cut_bisections']:
                self.assertEqual(split['field']['minimal_polynomial'], [-1, 0, 2])
                self.assertEqual(split['endpoint_event_authority'], m.ENDPOINT_BLOCKER)
                for child in split['children']:
                    self.assertIn('2', child['restricted_polynomials']['cos_polynomials'])
                    self.assertTrue(child['exact_polynomial_roundtrip'])
        forged = copy.deepcopy(source)
        forged.update({'algebraic_child_maps': {'status': 'CERTIFIED'},
                       'algebraic_endpoint_signs': ['ZERO'], 'algebraic_roots': ['1/2']})
        self.assertEqual(m.represent_required_event_children(forged), result)
        # Unknown v45 claim fields are rejected by the historical source grammar,
        # not stripped to manufacture a clean source. Preserve that exact refusal.
        forged['v45_child_representation'] = {'root_count': 0}
        rejected = v44.classify_required_analytic_event(forged)
        self.assertNotEqual(rejected['status'], 'CERTIFIED')
        rejection = m.represent_required_event_children(forged)
        self.assertEqual(rejection['predecessor_event_result'], rejected)
        self.assertEqual(rejection['status'], rejected['status'])
        self.assertEqual(rejection['span_representations'], [])
        self.assertFalse(rejection['analytic_cut_consumed'])

    def test_actual_common_root_even_multiplicity_and_phase_rates(self):
        for poly in ([-1, 0, 2], [1, 0, -4, 0, 4]):
            for rate in ('1/8', '-1/8', '0'):
                inputs = args(poly, rate=rate)
                result = m.build_orientation_child_maps(*inputs)
                self.assertEqual(result['status'], 'REPRESENTATION_CERTIFIED')
                self.assertTrue(m.validate_child_maps(result, *inputs))
                splits = result['independent_single_cut_bisections']
                self.assertEqual(len(splits), 1)
                self.assertEqual({x['coordinate'] for x in splits[0]['orientation_ownership']}, {'A', 'B'})
                self.assertFalse(splits[0]['physical_event_inferred_from_orientation_root'])
                self.assertFalse(splits[0]['analytic_cut_consumed'])

    def test_nearby_roots_independent_exact_bisections(self):
        a, b = [-4999, 0, 10000], [-5001, 0, 10000]
        inputs = ( {1: m.padd(a,b)}, {1: m.padd(a, m.pscale(b, -1))},
                   'nearby-s', ('0','1'), '1/16', '-1/8')
        result = m.build_orientation_child_maps(*inputs)
        self.assertEqual(result['status'], 'REPRESENTATION_CERTIFIED')
        self.assertEqual(len(result['independent_single_cut_bisections']), 2)
        self.assertEqual(result['pairwise_exact_cut_order'][0]['relation'], 'STRICTLY_LESS')
        for split in result['independent_single_cut_bisections']:
            self.assertEqual(len(split['children']), 2)
            self.assertEqual(split['coverage'], 'EXACT_SINGLE_CUT_BISECTION_OF_PARENT_NO_GAP_OR_OVERLAP')

    def test_unsafe_and_forged_child_records_fail_closed(self):
        inputs = args()
        original = m.build_orientation_child_maps(*inputs)
        mutations = [
            (['independent_single_cut_bisections',0,'field','minimal_polynomial'], [-1,0,3]),
            (['independent_single_cut_bisections',0,'field','isolating_interval'], ['1/100','1/50']),
            (['independent_single_cut_bisections',0,'field','root_index_in_open_unit_interval'], True),
            (['independent_single_cut_bisections',0,'children',0,'parent_local_map','width'], ['1/2']),
            (['independent_single_cut_bisections',0,'children',1,'parent_source_map','offset'], ['0']),
            (['independent_single_cut_bisections',0,'children',1,'phase_turn_law','offset'], ['0']),
            (['independent_single_cut_bisections',0,'children',0,'restricted_polynomials','cos_polynomials','1'], [['0']]),
            (['independent_single_cut_bisections',0,'source_binding_sha256'], '0'*64),
            (['independent_single_cut_bisections',0,'source_parameter_id'], 'different-s'),
            (['analytic_cut_consumed'], True),
        ]
        for path, replacement in mutations:
            forged = copy.deepcopy(original); target = forged
            for key in path[:-1]: target = target[key]
            target[path[-1]] = replacement
            with self.subTest(path=path), self.assertRaises(ValueError): m.validate_child_maps(forged, *inputs)
        for i, value in ((2,'changed-s'), (3,('-1','2')), (4,'1/8'), (5,'-1/8')):
            changed = list(inputs); changed[i] = value
            with self.assertRaises(ValueError): m.validate_child_maps(original, *changed)
        # Scaling preserves orientation roots, but must not erase source amplitude/provenance.
        changed = list(inputs); changed[0] = {1: m.pscale(inputs[0][1], 2)}; changed[1] = {1: m.pscale(inputs[1][1],2)}
        with self.assertRaises(ValueError): m.validate_child_maps(original, *changed)
        for i, value in ((0,{1:[-3.0,0,6]}), (3,('0',1.0)), (4,False), (5,0.125)):
            changed = list(inputs); changed[i] = value
            with self.assertRaises((ValueError, TypeError)): m.build_orientation_child_maps(*changed)

    def test_resource_refusal_at_each_new_stage(self):
        for target, error in (('irreducible_factors',MemoryError), ('compose_affine',OverflowError), ('_bisection',RecursionError)):
            with patch.object(m, target, side_effect=error('injected')):
                refusal = m.build_orientation_child_maps(*args())
                self.assertEqual(refusal['status'], 'RESOURCE_REFUSAL')
                self.assertFalse(refusal['is_truth_value'])
                with self.assertRaises(ValueError): m.validate_child_maps({'status':'CERTIFIED'}, *args())
        refusal = v44.resource_refusal()
        with patch.object(v44, 'exact_algebraic_orientation_cut_certificate', return_value=refusal):
            self.assertEqual(m.build_orientation_child_maps(*args()), refusal)

    def test_historical_precedence_and_no_algebraic_event_dispatch(self):
        source = v43test._spec()
        baseline = v44.classify_required_analytic_event(source)
        self.assertEqual(baseline['status'], 'CERTIFIED')
        self.assertEqual(m.classify_required_analytic_event(source), baseline)
        with patch.object(m, 'build_orientation_child_maps', side_effect=AssertionError('no work for certified source')):
            result = m.represent_required_event_children(source)
        self.assertEqual(result['status'], 'NOT_APPLICABLE')
        self.assertEqual(result['predecessor_event_result'], baseline)


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceIntegrationTests))
    if not result.wasSuccessful(): raise AssertionError('v45 source-integration suite failed')


if __name__ == '__main__':
    run()
