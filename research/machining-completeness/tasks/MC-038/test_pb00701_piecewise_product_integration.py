#!/usr/bin/env python3
"""Actual-source V51/V52 composition; local summaries are never substitute truth."""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import copy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pb00701_piecewise_product_model as m
import pb00701_piecewise_product_certificate as checker
import pb00701_ordered_product_model as prior
import pb00701_ordered_product_certificate as spancheck
import pb00701_coupled_bspline_model as v7
import pb00701_mixed_multicut_model as v49
import pb00701_algebraic_monotone_cut_model as v47
import test_pb00701_piecewise_product as core

a,b=m.a,m.b


@lru_cache(maxsize=1)
def acceptance():
    spec=core.fixture()
    previous=prior.build_ordered_source_evidence(spec)
    result=m.build_piecewise_source_evidence(spec)
    assert previous['status']=='ORDERED_SOURCE_EVIDENCE_CERTIFIED',previous.get('reason')
    assert result['status']=='PIECEWISE_SOURCE_EVIDENCE_CERTIFIED',result.get('reason')
    return spec,previous,result


def scale_right(spec,scale):
    spec=copy.deepcopy(spec)
    for name in ('cos_splines','sin_splines'):
        for spline in spec[name].values():
            n=spline['degree']+1
            spline['controls'][n:]=[str(Q(c)*Q(scale)) for c in spline['controls'][n:]]
    return spec


class PiecewiseIntegrationTests(unittest.TestCase):
    def checked(self,spec):
        result=m.build_piecewise_source_evidence(spec)
        self.assertEqual(result['status'],'PIECEWISE_SOURCE_EVIDENCE_CERTIFIED',result.get('reason'))
        proof=result['certificate']
        self.assertIs(checker.validate_piecewise_certificate(proof,spec),True)
        return proof

    def test_actual_two_span_source_five_roots_knot_once(self):
        spec,previous,result=acceptance();proof=result['certificate']
        self.assertEqual(a._json(previous),a._json(result['predecessor_result']))
        self.assertFalse(previous['global_cross_span_root_union_claimed'])
        self.assertTrue(proof['global_root_union_claimed'])
        self.assertIs(checker.validate_piecewise_certificate(proof,spec),True)
        self.assertEqual(len(proof['span_proofs']),2)
        for i,span in enumerate(proof['span_proofs']):
            self.assertEqual(a._json(span),a._json(previous['ordered_spans'][i]['ordered_evidence']))
            self.assertEqual(span['physical_event_result']['carrier_evidence']['owner'],
                             'PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR')
            self.assertEqual(span['physical_root_summary']['total_distinct_roots_closed'],3)
        summary=proof['global_root_summary']
        self.assertEqual((summary['distinct_roots_open'],summary['total_distinct_roots_closed']),(5,5))
        self.assertEqual((summary['crossings_open'],summary['tangencies_open']),(3,2))
        self.assertEqual(summary['source_knot_roots'],1)
        self.assertEqual(summary['analytic_multiple_roots_strictly_inside_spans'],2)
        self.assertEqual(summary['knot_roots_without_global_analytic_multiplicity'],1)
        roots=proof['ordered_physical_events']
        self.assertEqual([p['kind'] for p in roots],['SPAN_ROOT','SPAN_ROOT','SOURCE_KNOT','SPAN_ROOT','SPAN_ROOT'])
        knot=roots[2]
        self.assertEqual(knot['global_position'],{'kind':'RATIONAL','value':'1'})
        self.assertEqual(knot['one_sided_orders'],[2,3])
        self.assertEqual(knot['neighborhood_signs'],[1,-1])
        self.assertEqual(knot['event_kind'],'CROSSING')
        self.assertIsNone(knot['analytic_multiplicity'])
        self.assertEqual([c['physical_sign'] for c in proof['maximal_open_sign_cells']],[-1,1,1,-1,1,1])
        self.assertEqual(len({p['id'] for p in proof['ordered_boundaries']}),len(proof['ordered_boundaries']))
        print('v52 ACTUAL SOURCE: two checked v51 spans -> five globally ordered roots; shared knot counted once, one-sided orders (2,3), crossing; no invented analytic multiplicity')

    def test_same_one_sided_orders_can_instead_be_a_tangency(self):
        proof=self.checked(core.fixture('touch'))
        knot=next(p for p in proof['ordered_physical_events'] if p['kind']=='SOURCE_KNOT')
        self.assertEqual(knot['one_sided_orders'],[2,3])
        self.assertEqual(knot['event_kind'],'TANGENCY')
        self.assertEqual(knot['neighborhood_signs'],[1,1])
        self.assertIsNone(knot['analytic_multiplicity'])
        self.assertEqual((proof['global_root_summary']['crossings_open'],proof['global_root_summary']['tangencies_open']),(2,3))
        self.assertEqual([c['physical_sign'] for c in proof['maximal_open_sign_cells']],[-1,1,1,1,-1,-1])
        # Opposite carrier directions across a REAL source knot are legitimate.
        self.assertEqual([p['carrier_ordering']['direction']['delta'] for p in proof['span_proofs']],[1,-1])

    def test_nonzero_physical_continuity_by_harmonic_cancellation_coalesces(self):
        proof=self.checked(core.fixture('nonzero'))
        join=proof['knot_evidence'][0]
        self.assertEqual(join['physical_relation'],'POSITIVE')
        self.assertEqual(join['physical_difference_evidence']['relation'],'ZERO')
        self.assertNotEqual(join['one_sided_amplitude_values'][0],join['one_sided_amplitude_values'][1])
        self.assertEqual(join['one_sided_orders'],[0,0])
        self.assertEqual(len(proof['ordered_physical_events']),4)
        self.assertEqual(len(proof['elementary_open_cells']),6)
        self.assertEqual(len(proof['maximal_open_sign_cells']),5)
        bridges=[c for c in proof['maximal_open_sign_cells'] if c['included_nonzero_source_knots']]
        self.assertEqual(len(bridges),1)
        self.assertEqual(bridges[0]['included_nonzero_source_knots'],['knot:0'])
        self.assertEqual(len(bridges[0]['elementary_cell_indices']),2)
        self.assertEqual(bridges[0]['physical_sign'],1)
        self.assertFalse(any(p['kind']=='SOURCE_KNOT' for p in proof['ordered_physical_events']))

    def test_same_sign_unequal_values_and_tiny_jumps_block_new_scope(self):
        base=core.fixture('nonzero')
        for scale in (Q(2),1+Q(1,10**12)):
            spec=scale_right(base,scale)
            previous=prior.build_ordered_source_evidence(spec)
            self.assertEqual(previous['status'],'ORDERED_SOURCE_EVIDENCE_CERTIFIED')
            result=m.build_piecewise_source_evidence(spec)
            self.assertEqual(result['status'],'BLOCKED')
            self.assertEqual(result['reason'],'PHYSICAL_SOURCE_KNOT_DISCONTINUITY')
            self.assertEqual(result['physical_difference_evidence']['relation'],'POSITIVE')
            self.assertEqual(a._json(result['predecessor_result']),a._json(previous))
            self.assertFalse(result['piecewise_evidence_complete'])
            self.assertFalse(result['valid_manufacturing_source_rejected_as_invalid'])
            lp,rp=[x['ordered_evidence'] for x in previous['ordered_spans']]
            self.assertEqual(lp['ordered_boundaries'][-1]['physical_relation'],'POSITIVE')
            self.assertEqual(rp['ordered_boundaries'][0]['physical_relation'],'POSITIVE')

    def test_both_external_roots_preserve_orders_and_open_closed_counts(self):
        proof=self.checked(core.fixture(exterior=True))
        summary=proof['global_root_summary']
        self.assertEqual(summary['exterior_root_orders'],{'left':2,'right':3})
        self.assertEqual((summary['distinct_roots_open'],summary['total_distinct_roots_closed']),(5,7))
        self.assertEqual(proof['ordered_boundaries'][0]['physical_relation'],'ZERO')
        self.assertEqual(proof['ordered_boundaries'][-1]['physical_relation'],'ZERO')
        self.assertEqual(sum(p['kind']=='SOURCE_KNOT' for p in proof['ordered_physical_events']),1)

    def test_reversal_global_scale_and_cropped_original_source(self):
        spec,_,result=acceptance();before=result['certificate']
        expected=[c['physical_sign'] for c in before['maximal_open_sign_cells']]
        reverse=self.checked(core.reverse_source(spec))
        self.assertEqual([c['physical_sign'] for c in reverse['maximal_open_sign_cells']],list(reversed(expected)))
        self.assertEqual(reverse['knot_evidence'][0]['one_sided_orders'],[3,2])
        transformed=self.checked(core.affine_source(spec))
        self.assertEqual(transformed['source_lowering']['source_boundaries'],['2','5','8'])
        self.assertEqual(transformed['knot_evidence'][0]['global_derivative_scales'],['1/9','1/27'])
        self.assertEqual([c['physical_sign'] for c in transformed['maximal_open_sign_cells']],expected)
        cropped=copy.deepcopy(spec);cropped['parameter_lo']='1/4';cropped['parameter_hi']='7/4'
        proof=self.checked(cropped)
        self.assertEqual(proof['global_root_summary']['distinct_roots_open'],5)
        self.assertEqual(proof['source_lowering']['source_boundaries'],['1/4','1','7/4'])
        self.assertEqual(proof['knot_evidence'][0]['one_sided_orders'],[2,3])

    def test_whole_source_negation_flips_cells_not_root_ownership(self):
        spec,_,result=acceptance();changed=copy.deepcopy(spec)
        for key in ('cos_splines','sin_splines'):
            for spline in changed[key].values():
                spline['controls']=[str(-3*Q(x)) for x in spline['controls']]
        proof=self.checked(changed)
        self.assertEqual(proof['global_root_summary'],result['certificate']['global_root_summary'])
        self.assertEqual([c['physical_sign'] for c in proof['maximal_open_sign_cells']],
                         [-c['physical_sign'] for c in result['certificate']['maximal_open_sign_cells']])
        self.assertEqual(proof['knot_evidence'][0]['one_sided_signs'],[-1,1])

    def test_finite_full_source_checker_cannot_search_or_relower_from_claims(self):
        spec,_,result=acceptance();proof=result['certificate']
        with patch.object(prior,'build_ordered_source_evidence',side_effect=AssertionError('no classifier envelope')),
             patch.object(prior.v50,'classify_required_analytic_event',side_effect=AssertionError('no v50 classifier')),
             patch.object(v49,'classify_required_analytic_event',side_effect=AssertionError('no v49 classifier')),
             patch.object(v7,'classify_required_analytic_event',side_effect=AssertionError('no v7 classifier')),
             patch.object(prior.v50,'carrier_proof',side_effect=AssertionError('no carrier selector')),
             patch.object(v49.b,'certify_derivative',side_effect=AssertionError('no multicut selector')),
             patch.object(v47,'certify_derivative',side_effect=AssertionError('no singlecut selector')),
             patch.object(prior,'_decide_factor_sign',side_effect=AssertionError('no factor sign search')),
             patch.object(prior.e,'_decide_endpoint',side_effect=AssertionError('no endpoint sign search')):
            self.assertIs(checker.validate_piecewise_certificate(proof,spec),True)

    def test_forged_lowering_join_orders_union_and_sign_coverage_rejected(self):
        spec,_,result=acceptance();proof=result['certificate']
        changes=[
            (['source_lowering','source_boundaries'],['0','2']),
            (['source_lowering','spans',0,'material','cos_polynomials','0'],['0']),
            (['span_proofs'],list(reversed(proof['span_proofs']))),
            (['span_proofs'],proof['span_proofs'][:1]),
            (['span_proofs'],proof['span_proofs']+proof['span_proofs'][:1]),
            (['span_proofs',0,'physical_root_summary','distinct_roots_open'],0),
            (['knot_evidence',0,'physical_difference_evidence','relation'],'POSITIVE'),
            (['knot_evidence',0,'one_sided_orders'],[5,5]),
            (['knot_evidence',0,'analytic_multiplicity'],5),
            (['knot_evidence',0,'global_derivative_scales'],['0','0']),
            (['ordered_physical_events'],list(reversed(proof['ordered_physical_events']))),
            (['ordered_physical_events'],proof['ordered_physical_events'][:-1]),
            (['ordered_physical_events'],proof['ordered_physical_events']+proof['ordered_physical_events'][2:3]),
            (['ordered_boundaries',3,'analytic_multiplicity'],5),
            (['elementary_open_cells',0,'source_span_index'],1),
            (['elementary_open_cells',0,'boundary_ids'],['exterior:left','exterior:right']),
            (['maximal_open_sign_cells',0,'physical_sign'],1),
            (['maximal_open_sign_cells',0,'included_nonzero_source_knots'],['knot:0']),
            (['maximal_open_sign_cells'],proof['maximal_open_sign_cells'][:-1]),
            (['global_root_summary','total_distinct_roots_closed'],6),
            (['global_root_summary','source_knot_roots'],True),
            (['global_analytic_multiplicity_at_source_knots_claimed'],True),
            (['general_nonmonotone_solver_claimed'],True),(['material_body_transition_claimed'],True),
            (['native_topology_claimed'],True)]
        for path,value in changes:
            with self.subTest(path=path),self.assertRaises((ValueError,TypeError,KeyError,AssertionError)):
                checker.validate_piecewise_certificate(core.mutate(proof,path,value),spec)
        bad=copy.deepcopy(proof);bad['MC-B']='ESTABLISHED'
        with self.assertRaises(ValueError):checker.validate_piecewise_certificate(bad,spec)

    def test_actual_source_mutations_not_just_digest_changes_reject(self):
        spec,_,result=acceptance();proof=result['certificate']
        variants=[core.mutate(spec,['source_parameter_id'],'another'),
                  core.mutate(spec,['phase_turn_rate'],'-1/4'),
                  core.mutate(spec,['parameter_lo'],'1/10')]
        for key in ('cos_splines','sin_splines'):
            for h in spec[key]:
                variants.append(core.mutate(spec,[key,h,'controls',0],str(Q(spec[key][h]['controls'][0])+Q(1,10**12))))
        for changed in variants:
            with self.assertRaises((ValueError,TypeError,KeyError)):
                checker.validate_piecewise_certificate(proof,changed)
            # Updating the visible source and digest still cannot launder stale
            # per-span analytic evidence into a proof for different controls.
            forged=copy.deepcopy(proof);forged['source_lowering']=m.lower_source(changed)
            forged['source_binding_sha256']=forged['source_lowering']['source_binding_sha256']
            with self.assertRaises((ValueError,TypeError,KeyError)):
                checker.validate_piecewise_certificate(forged,changed)
        knot_changed=copy.deepcopy(spec)
        for key in ('cos_splines','sin_splines'):
            for spline in knot_changed[key].values():
                spline['knots']=['9/10' if k=='1' else k for k in spline['knots']]
        with self.assertRaises(ValueError):checker.validate_piecewise_certificate(proof,knot_changed)

    def test_missing_owner_single_span_and_unknown_source_keep_predecessors(self):
        left=core.physical_piece(core.power([-1,0,2],2))
        right=({0:[-Q(1,2),1],1:[Q(1,100)]},{2:[Q(1,200)]})
        spec=core.encode([left,right])
        previous=prior.build_ordered_source_evidence(spec)
        self.assertEqual(previous['status'],'ORDERED_SOURCE_EVIDENCE_CERTIFIED')
        self.assertFalse(previous['all_source_spans_have_ordered_evidence'])
        result=m.build_piecewise_source_evidence(spec)
        self.assertEqual(result['reason'],'NOT_ALL_SOURCE_SPANS_HAVE_V51_PRODUCT_WITNESSES')
        self.assertEqual(result['predecessor_result'],previous)
        for source in (core.encode([left]),core.encode([right])):
            previous=prior.build_ordered_source_evidence(source)
            self.assertEqual(m.build_piecewise_source_evidence(source),previous)
        source=core.fixture()
        for key,value in (('epsilon','1/100'),('v52_certificate',{}),('second_phase_law',{})):
            bad=copy.deepcopy(source);bad[key]=value
            previous=prior.build_ordered_source_evidence(bad)
            self.assertNotEqual(previous['status'],'ORDERED_SOURCE_EVIDENCE_CERTIFIED')
            self.assertEqual(m.build_piecewise_source_evidence(bad),previous)
        with patch.object(prior,'build_ordered_source_evidence',side_effect=RuntimeError('unrelated defect')):
            with self.assertRaisesRegex(RuntimeError,'unrelated defect'):m.build_piecewise_source_evidence(source)

    def test_resource_nontruth_at_lowering_join_composition_and_checking(self):
        spec,previous,result=acceptance();proof=result['certificate']
        for module,name in ((v7,'_piece_from_normal'),(m,'check_spans'),(m,'knot_continuity'),(m,'assemble')):
            with patch.object(module,name,side_effect=MemoryError('exact resources')):
                for failed in (m.build_piecewise_certificate(spec,proof['span_proofs']),
                               checker.validate_piecewise_certificate(proof,spec)):
                    self.assertEqual(failed['status'],'RESOURCE_REFUSAL')
                    self.assertIs(failed['is_truth_value'],False)
        with patch.object(m,'knot_continuity',return_value=m.refusal('injected-join')):
            failed=checker.validate_piecewise_certificate(proof,spec)
            self.assertEqual(failed['status'],'RESOURCE_REFUSAL')
        with patch.object(m,'build_piecewise_certificate',return_value=m.refusal('new-global-stage')):
            failed=m.build_piecewise_source_evidence(spec)
            self.assertEqual(failed['status'],'RESOURCE_REFUSAL')
            self.assertFalse(failed['piecewise_evidence_complete'])
            self.assertEqual(failed['predecessor_result'],previous)
        self.assertIs(checker.validate_piecewise_certificate(proof,spec),True)
        with patch.object(m,'knot_continuity',side_effect=RuntimeError('unexpected join bug')):
            with self.assertRaisesRegex(RuntimeError,'unexpected join bug'):
                checker.validate_piecewise_certificate(proof,spec)


def run():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PiecewiseIntegrationTests))
    if not result.wasSuccessful():
        raise AssertionError('v52 actual-source piecewise composition suite failed')


if __name__=='__main__':run()
