#!/usr/bin/env python3
"""Actual repository source/product/owner integration, never a substitute oracle."""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import copy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_ordered_product_model as m
import pb00701_ordered_product_certificate as checker
import pb00701_vanishing_source_factor_certificate as v50check
import pb00701_mixed_multicut_model as v49
import pb00701_algebraic_monotone_cut_model as v47
import test_pb00701_ordered_product as core

a, b = m.a, m.b


def source(args):
    return m.v50.source_spec(a._material(*args))


@lru_cache(maxsize=1)
def acceptance():
    args = core.product_args(); spec = source(args)
    previous = m.v50.classify_required_analytic_event(spec)
    current = m.build_ordered_source_evidence(spec)
    assert previous['status'] == 'CERTIFIED', previous.get('reason')
    assert current['status'] == 'ORDERED_SOURCE_EVIDENCE_CERTIFIED', current.get('reason')
    return args, spec, previous, current


def ordered_source(result):
    assert result['status'] == 'ORDERED_SOURCE_EVIDENCE_CERTIFIED', result.get('reason')
    assert len(result['ordered_spans']) == 1
    return result['ordered_spans'][0]['ordered_evidence']


def runtime_point(record):
    if record['kind'] == 'RATIONAL':
        return b.Boundary.at(record['value'])
    f = record['field']
    return b.Boundary(field=a.RealField(tuple(f['minimal_polynomial']),
                                      tuple(map(Q, f['isolating_interval'])), f['root_index_in_open_unit_interval']))


def coincident_carrier():
    args = list(core.carrier_args()); args[4] = '-5/32'
    return tuple(args)


class OrderedProductIntegrationTests(unittest.TestCase):
    def checked(self, args):
        product = m.v50.build_product_event(*args)
        self.assertEqual(product['status'], 'CERTIFIED', product.get('reason'))
        original = a._json(product)
        proof = m.build_ordered_product_event(product, *args)
        self.assertEqual(proof['status'], 'ORDERED_PRODUCT_CERTIFIED', proof.get('reason'))
        self.assertTrue(checker.validate_ordered_product_event(proof, *args))
        self.assertEqual(a._json(product), original)
        self.assertEqual(a._json(proof['physical_event_result']), original)
        self.assertFalse(product['ordered_full_analytic_root_list_claimed'])
        self.assertTrue(proof['ordered_full_product_root_list_claimed'])
        return proof

    def test_actual_v50_source_gains_ordered_union_without_changing_counts(self):
        args, spec, previous, current = acceptance()
        self.assertEqual(a._json(current['physical_event_result']), a._json(previous))
        self.assertEqual(current['source_spec_binding_sha256'], b.digest(spec))
        proof = ordered_source(current)
        self.assertTrue(checker.validate_ordered_product_event(proof, *args))
        self.assertEqual(proof['physical_event_result'], previous['spans'][0]['route'])
        events = proof['ordered_physical_events']
        self.assertEqual([x['id'] for x in events], ['carrier:open', 'factor:0'])
        self.assertEqual([x['physical_multiplicity'] for x in events], [1, 2])
        self.assertEqual([x['physical_sign'] for x in proof['sign_cells']], [-1, 1, 1])
        self.assertEqual(proof['factor_carrier_signs'][0]['relation'], 'POSITIVE')
        self.assertEqual(proof['carrier_ordering']['factor_comparisons'][0]['comparison_to_carrier_root'], 1)
        implicit = proof['carrier_ordering']['implicit_root_descriptor']
        self.assertIsNone(implicit['algebraic_minimal_polynomial'])
        self.assertEqual(implicit['arithmetic_nature'], 'UNCLAIMED')
        # The old root-bearing carrier child actually contains the factor cut:
        # an overlapping old isolation cannot tell us their relative order.
        carrier = proof['physical_event_result']['carrier_evidence']['route']
        child = next(c for c in carrier['children'] if c['summary']['distinct_roots_open'] == 1)
        alpha = runtime_point(events[1]['position'])
        left, right = map(runtime_point, child['parent_local_interval'])
        self.assertEqual(b.order_certificate(left, alpha)['comparison'], -1)
        self.assertEqual(b.order_certificate(alpha, right)['comparison'], -1)
        self.assertTrue(current['all_source_spans_have_ordered_evidence'])
        self.assertFalse(current['global_cross_span_root_union_claimed'])
        print('v51 ACTUAL SOURCE: unchanged v50 two-root count -> simple carrier crossing before irrational double factor tangency; sign cells NEGATIVE/POSITIVE/POSITIVE')

    def test_factor_roots_on_both_irrational_carrier_proof_cuts(self):
        factor = core.power([Q(469, 2500), -1, 1], 2)
        proof = self.checked(core.product_args(factor))
        self.assertEqual([x['id'] for x in proof['ordered_physical_events']], ['factor:0', 'carrier:open', 'factor:1'])
        self.assertEqual([x['physical_multiplicity'] for x in proof['ordered_physical_events']], [2, 1, 2])
        self.assertEqual([x['physical_sign'] for x in proof['sign_cells']], [-1, -1, 1, 1])
        self.assertEqual([x['relation'] for x in proof['factor_carrier_signs']], ['NEGATIVE', 'POSITIVE'])
        cuts = proof['physical_event_result']['carrier_evidence']['route']['partition']['boundaries']
        for row in proof['factor_carrier_signs']:
            self.assertTrue(any(b.same(row['source_cut'], c['point']) for c in cuts))
        self.assertEqual(proof['physical_root_summary']['distinct_roots_open'], 3)
        self.assertFalse(proof['proof_cuts_counted_as_extra_physical_roots'])

    def test_different_factor_fields_and_rational_proof_boundary(self):
        factor = a.pmul([-1, 0, 2], [-1, 0, 5])
        proof = self.checked(core.product_args(factor))
        self.assertEqual([x['id'] for x in proof['ordered_physical_events']], ['factor:0', 'carrier:open', 'factor:1'])
        fields = [x['source_cut']['field']['minimal_polynomial'] for x in proof['factor_carrier_signs']]
        self.assertEqual(fields, [[-1, 0, 5], [-1, 0, 2]])
        self.assertEqual(len(proof['sign_cells']), 4)
        self.assertTrue(all(x['normalized_mixed_field_map'] is None for x in proof['sign_cells']))
        proof = self.checked(core.product_args(core.power([-Q(1, 2), 1], 3)))
        self.assertEqual([x['physical_multiplicity'] for x in proof['ordered_physical_events']], [3, 1])
        self.assertEqual(proof['factor_carrier_signs'][0]['sign'], -1)
        self.assertFalse(proof['ordered_physical_events'][0]['coincidence_counted_once'])

    def test_exact_rational_coincidence_and_additive_parity(self):
        for exponent in (1, 2, 3):
            proof = self.checked(core.product_args(core.power([-Q(1, 2), 1], exponent), coincident_carrier()))
            self.assertIsNone(proof['carrier_ordering']['implicit_root_descriptor'])
            self.assertEqual(proof['carrier_ordering']['carrier_root_boundary_id'], 'factor:0')
            self.assertEqual(len(proof['ordered_physical_events']), 1)
            event = proof['ordered_physical_events'][0]
            self.assertEqual(event['physical_multiplicity'], exponent + 1)
            self.assertTrue(event['coincidence_counted_once'])
            left, right = event['adjacent_cell_signs']
            self.assertEqual(right, left * (-1) ** (exponent + 1))
            self.assertEqual(len(proof['sign_cells']), 2)

    def test_overlapping_nearby_irrational_factor_and_rational_carrier(self):
        for direction in (-1, 1):
            factor = [-Q(1, 4) - Q(direction, 10**6), 0, 1]
            proof = self.checked(core.product_args(factor, coincident_carrier()))
            expected = ['factor:0', 'carrier:open'] if direction < 0 else ['carrier:open', 'factor:0']
            self.assertEqual([x['id'] for x in proof['ordered_physical_events']], expected)
            comparison = proof['carrier_ordering']['factor_comparisons'][0]
            self.assertEqual(comparison['comparison_to_carrier_root'], direction)
            # Here the carrier zero really is rational. Its implicit descriptor
            # correctly makes NO claim that such a root must be transcendental.
            self.assertEqual(proof['carrier_ordering']['implicit_root_descriptor']['arithmetic_nature'], 'UNCLAIMED')
            self.assertEqual(proof['physical_root_summary']['distinct_roots_open'], 2)

    def test_factor_roots_at_both_exteriors_have_inward_jet_signs(self):
        factor = a.pmul(core.power([0, 1], 2), core.power([-1, 1], 3))
        proof = self.checked(core.product_args(factor))
        self.assertEqual(proof['physical_root_summary']['endpoint_root_multiplicity'], {'left': 2, 'right': 3})
        self.assertEqual([x['physical_multiplicity'] for x in proof['ordered_physical_events']], [2, 1, 3])
        self.assertEqual([x['physical_sign'] for x in proof['sign_cells']], [1, -1])
        self.assertEqual([x['factor_jet']['order'] for x in proof['exterior_inward_evidence']], [2, 3])
        self.assertEqual(proof['ordered_boundaries'][0]['physical_relation'], 'ZERO')
        self.assertEqual(proof['ordered_boundaries'][-1]['physical_relation'], 'ZERO')

    def test_carrier_only_and_coincident_exterior_roots(self):
        for c0, factor, side in (([-Q(1,100), 1], [0,1], 'left'), ([-1,1], [-1,1], 'right')):
            carrier = ({0:c0, 1:[Q(1,100)]}, {2:[Q(1,200)]}, 'v19-exterior', ('0','1'), '0','1/4')
            for common, multiplicity in (([1,0,1],1),(core.power(factor,2),3)):
                proof = self.checked(core.product_args(common, carrier))
                self.assertEqual(proof['physical_root_summary']['endpoint_root_multiplicity'], {side:multiplicity})
                self.assertEqual(proof['physical_root_summary']['distinct_roots_open'],0)
                self.assertEqual(len(proof['sign_cells']),1)
                ext = proof['exterior_inward_evidence'][0 if side == 'left' else 1]
                self.assertEqual(ext['carrier_jet_order'],1)
                self.assertEqual(ext['carrier_sign_method'],'CHECKED_STRICT_DERIVATIVE_AND_INWARD_DIRECTION')
                self.assertEqual(ext['carrier_inward_sign'],1 if side == 'left' else -1)

    def test_root_free_factors_and_no_open_carrier_roots(self):
        proof = self.checked(core.product_args([1,0,1]))
        self.assertEqual([x['id'] for x in proof['ordered_physical_events']],['carrier:open'])
        for offset in (-1, 1):
            carrier = list(core.carrier_args()); carrier[0] = dict(carrier[0]); carrier[0][0] = [offset]
            for factor in ([1,0,1],core.power([-1,0,2],2)):
                proof = self.checked(core.product_args(factor,tuple(carrier)))
                self.assertEqual(proof['carrier_ordering']['carrier_open_roots'],0)
                self.assertIsNone(proof['carrier_ordering']['implicit_root_descriptor'])
                self.assertTrue(all(cell['physical_sign'] == offset for cell in proof['sign_cells']))

    def test_reversal_negation_and_nonunit_global_source(self):
        args, _, _, current = acceptance(); original = ordered_source(current)
        expected_signs = [x['physical_sign'] for x in original['sign_cells']]
        for operation in ('reverse','negate','global'):
            c,s,ident,span,off,rate = args;off,rate=Q(off),Q(rate)
            if operation == 'reverse':
                c,s = ({h:core.reverse_poly(p) for h,p in x.items()} for x in (c,s))
                off,rate = off+rate,-rate
            elif operation == 'negate':
                c,s = ({h:a.pscale(p,-3) for h,p in x.items()} for x in (c,s))
            else:
                span,off,rate = ('2','5'),off-rate*Q(2,3),rate/3
            changed=(c,s,ident,span,str(off),str(rate))
            proof=self.checked(changed)
            expected=list(reversed(expected_signs)) if operation=='reverse' else [-s for s in expected_signs] if operation=='negate' else expected_signs
            self.assertEqual([c['physical_sign'] for c in proof['sign_cells']],expected)
            self.assertEqual([x['physical_multiplicity'] for x in proof['ordered_physical_events']], [2,1] if operation=='reverse' else [1,2])
            if operation=='global':
                self.assertEqual(proof['ordered_boundaries'][0]['global_position'],{'kind':'RATIONAL','value':'2'})
                self.assertEqual(proof['ordered_boundaries'][-1]['global_position'],{'kind':'RATIONAL','value':'5'})
                analytic=next(x for x in proof['ordered_physical_events'] if x['id']=='carrier:open')
                self.assertEqual(analytic['global_position']['positive_scale'],'3')

    def test_all_four_carrier_owners_and_no_replacement_search(self):
        A,B=[Q(-1,8),Q(1,2),Q(1,10000)],[Q(-7,40),Q(7,20)]
        carriers=[(19,({0:[-Q(1,2),1],1:[Q(1,100)]},{2:[Q(1,200)]},'v19-carrier',('0','1'),'0','1/4')),
                  (49,core.carrier_args())]
        for shift,version in ((False,47),(True,48)):
            rotated=a.pmul(A,[0,1]) if shift else A
            carriers.append((version,({1:a.padd(rotated,B),2:[Q(1,10**8)]},
                                     {1:a.padd(rotated,a.pscale(B,-1))},'owner-specific',('0','1'),'-1/8','1/16')))
        for version,carrier in carriers:
            args=core.product_args(carrier=carrier);proof=self.checked(args)
            self.assertEqual(m.v50.OWNERS[proof['carrier_ordering']['direction']['owner']],version)
            with patch.object(m,'_decide_factor_sign',side_effect=AssertionError('no sign search')), \
                 patch.object(m.v50,'carrier_proof',side_effect=AssertionError('no carrier selection')), \
                 patch.object(m.v50,'classify_required_analytic_event',side_effect=AssertionError('no v50 classification')), \
                 patch.object(v49,'classify_required_analytic_event',side_effect=AssertionError('no v49 classification')), \
                 patch.object(v49.b,'certify_derivative',side_effect=AssertionError('no multicut derivative selection')), \
                 patch.object(v47,'certify_derivative',side_effect=AssertionError('no single-cut derivative selection')), \
                 patch.object(m.e,'_decide_endpoint',side_effect=AssertionError('no endpoint sign search')):
                self.assertTrue(checker.validate_ordered_product_event(proof,*args))

    def test_all_order_sign_coverage_and_capability_mutations_reject(self):
        args,_,_,current=acceptance();proof=ordered_source(current)
        changes=[
            (['factor_carrier_signs',0,'sign'],True),(['factor_carrier_signs',0,'relation'],'NEGATIVE'),
            (['factor_carrier_signs',0,'factor_event_index'],1),
            (['factor_carrier_signs',0,'sign_evidence','sign_certificate','components'],[]),
            (['factor_carrier_signs',0,'sign_evidence','sign_certificate','precision'],True),
            (['carrier_ordering','direction','delta'],-1),
            (['carrier_ordering','direction','closed_derivative_witnesses'],[]),
            (['carrier_ordering','factor_comparisons',0,'comparison_to_carrier_root'],-1),
            (['carrier_ordering','implicit_root_descriptor','defining_interval'],list(reversed(proof['carrier_ordering']['implicit_root_descriptor']['defining_interval']))),
            (['carrier_ordering','implicit_root_descriptor','algebraic_minimal_polynomial'],[-1,2]),
            (['carrier_ordering','implicit_root_descriptor','arithmetic_nature'],'TRANSCENDENTAL'),
            (['ordered_physical_events'],proof['ordered_physical_events'][:-1]),
            (['ordered_physical_events'],list(reversed(proof['ordered_physical_events']))),
            (['ordered_physical_events'],proof['ordered_physical_events']+proof['ordered_physical_events'][:1]),
            (['ordered_boundaries',1,'physical_multiplicity'],2),
            (['ordered_boundaries',2,'adjacent_cell_signs'],[1,-1]),
            (['ordered_boundaries',1,'global_position','positive_scale'],'2'),
            (['sign_cells'],proof['sign_cells'][:-1]),
            (['sign_cells',0,'physical_sign'],1),(['sign_cells',1,'boundary_ids'],['source:left','source:right']),
            (['sign_cells',1,'positive_width_proof','comparison'],True),
            (['sign_cells',2,'normalized_mixed_field_map'],{'width':'1/2'}),
            (['exterior_inward_evidence',0,'factor_jet','sign'],-1),
            (['physical_root_summary','distinct_roots_open'],1),
            (['physical_event_result','carrier_evidence','route','children',0,'derivative_certificate','orthants'],[]),
            (['source_material','phase_turn_law','rate'],'-1/16'),
            (['physical_product_strict_monotonicity_claimed'],True),
            (['general_nonmonotone_solver_claimed'],True),(['material_body_transition_claimed'],True),
            (['native_topology_claimed'],True),(['cross_spline_span_continuity_claimed'],True)]
        for path,value in changes:
            with self.subTest(path=path),self.assertRaises((ValueError,TypeError,KeyError,AssertionError)):
                checker.validate_ordered_product_event(core.mutate(proof,path,value),*args)
        for index,value in ((2,'other'),(3,('0','2')),(4,'0'),(5,'-1/16')):
            changed=list(args);changed[index]=value
            with self.assertRaises((ValueError,TypeError,KeyError)):
                checker.validate_ordered_product_event(proof,*changed)
        # Every live physical channel remains source authority, including C2.
        for mapping_index in (0, 1):
            for harmonic in args[mapping_index]:
                changed = list(copy.deepcopy(args))
                changed[mapping_index][harmonic] = a.padd(changed[mapping_index][harmonic], [Q(1, 10**12)])
                with self.subTest(mapping=mapping_index, harmonic=harmonic), self.assertRaises((ValueError, TypeError, KeyError)):
                    checker.validate_ordered_product_event(proof, *changed)
        bad=copy.deepcopy(proof);bad['MC-B']='ESTABLISHED'
        with self.assertRaises(ValueError):checker.validate_ordered_product_event(bad,*args)

    def test_original_source_rejections_precedence_and_unrelated_errors(self):
        for args in (core.carrier_args(),({1:[1]},{},'constant',('0','1'),'0','1/8'),
                     ({1:[0]},{},'zero',('0','1'),'0','1/8')):
            spec=source(args);previous=m.v50.classify_required_analytic_event(spec)
            with patch.object(m,'build_ordered_product_event',side_effect=AssertionError('older owner preserved')):
                self.assertEqual(m.build_ordered_source_evidence(spec),previous)
        args,spec,_,_=acceptance()
        for key,value in (('epsilon','1/100'),('v51_ordered_certificate',{}),('second_phase_law',{})):
            bad=copy.deepcopy(spec);bad[key]=value
            previous=m.v50.classify_required_analytic_event(bad)
            self.assertNotEqual(previous['status'],'CERTIFIED')
            self.assertEqual(m.build_ordered_source_evidence(bad),previous)
        for value in (True,0.0625):
            bad=copy.deepcopy(spec);bad['phase_turn_rate']=value
            previous=m.v50.classify_required_analytic_event(bad)
            self.assertNotEqual(previous['status'],'CERTIFIED')
            self.assertEqual(m.build_ordered_source_evidence(bad),previous)
        with patch.object(m.v50,'classify_required_analytic_event',side_effect=RuntimeError('unrelated bug')):
            with self.assertRaisesRegex(RuntimeError,'unrelated bug'):m.build_ordered_source_evidence(spec)

    def test_resource_refusal_preserves_certified_physical_product(self):
        args,spec,previous,current=acceptance();proof=ordered_source(current);product=proof['physical_event_result']
        for module,name in ((v50check,'validate_product_event'),(m.e,'sign_enclosure'),
                            (m,'_assemble_ordered'),(m,'_inward_exteriors')):
            with patch.object(module,name,side_effect=MemoryError('exact resource')):
                for result in (m.build_ordered_product_event(product,*args),checker.validate_ordered_product_event(proof,*args)):
                    self.assertEqual(result['status'],'RESOURCE_REFUSAL')
                    self.assertIs(result['is_truth_value'],False)
        with patch.object(m,'build_ordered_product_event',return_value=m.refusal('injected-new-order-stage')):
            result=m.build_ordered_source_evidence(spec)
            self.assertEqual(result['status'],'RESOURCE_REFUSAL')
            self.assertFalse(result['is_truth_value'])
            self.assertEqual(result['physical_event_result'],previous)
            self.assertFalse(result['ordered_evidence_complete'])
        self.assertTrue(v50check.validate_product_event(product,*args))
        with patch.object(m,'_assemble_ordered',side_effect=RuntimeError('unrelated composition bug')):
            with self.assertRaisesRegex(RuntimeError,'unrelated composition bug'):
                m.build_ordered_product_event(product,*args)


def run():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OrderedProductIntegrationTests))
    if not result.wasSuccessful():
        raise AssertionError('v51 actual-source ordered-product suite failed')


if __name__=='__main__':run()
