#!/usr/bin/env python3
"""Exact adversarial qualification for finite endpoint/knot jet blindness."""
from __future__ import annotations
import argparse
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import unittest

import pb00701_finite_jet_blindspot as m

HERE = Path(__file__).resolve().parent
CORPUS = HERE / 'pb00701-finite-owner-corpus-v54.json'
V2 = HERE / 'pb00701-post-v54-evidence-reconciliation-v2.json'
REPORT = HERE / 'pb00701-finite-jet-blindspot.json'
CORPUS_BLOB = '5841c331579489b25caef38cd412bdbf286f9134'
V2_BLOB = 'e52d3baf3692a011cf86234eeaa992ef407d99fd'
ANCHOR = 'composite:DELEGATED_V6_CONSTANT_MODULATION:tail0'
ANCHOR_SHA = '9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1'
M = 9
EPSILON = '1/1073741824'


def blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def census(corpus=None, v2=None):
    if blob(CORPUS) != CORPUS_BLOB or blob(V2) != V2_BLOB:
        raise ValueError('FROZEN_OR_V2_INPUT_GIT_BLOB_DRIFT')
    historical = json.loads(CORPUS.read_text()) if corpus is None else corpus
    registry = json.loads(V2.read_text()) if v2 is None else v2
    cases = historical['cases']
    if len(cases) != 121 or len({r['id'] for r in cases}) != 121:
        raise ValueError('FROZEN_121_CASE_ID_DRIFT')
    source_shas = {r['id']: m.source_sha(r['spec']) for r in cases}
    if len(set(source_shas.values())) != 121:
        raise ValueError('FROZEN_121_SOURCE_IDENTITY_DRIFT')
    ix = {r['id']: r for r in cases}
    if ANCHOR not in ix or source_shas[ANCHOR] != ANCHOR_SHA:
        raise ValueError('HISTORICAL_V27_ANCHOR_SOURCE_DRIFT')
    anchor = ix[ANCHOR]['spec']
    if (anchor['parameter_lo'] != '0' or anchor['parameter_hi'] != '2' or
            anchor['phase_turn_rate'] != '1/4' or
            anchor['cos_splines']['1'] !=
            {'degree': 0, 'knots': ['0','1','2'], 'controls':['1','1']}):
        raise ValueError('HISTORICAL_ANCHOR_PIECE_KNOT_PHASE_DRIFT')
    refused = {r['id'] for r in cases if r['expected']['v54_disposition'] == 'BLOCKED'}
    missing = {r['id'] for r in cases if r['expected']['v54_disposition'] ==
               'BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE'}
    if len(refused) != 20 or len(missing) != 30 or refused & missing:
        raise ValueError('FROZEN_20_30_HISTORICAL_CENSUS_DRIFT')
    rows = registry['source_cases']
    if len(rows) != 50 or {r['case_id'] for r in rows} != refused | missing:
        raise ValueError('FIFTY_CASE_REGISTRY_ID_DRIFT')
    if len({r['case_id'] for r in rows}) != 50:
        raise ValueError('DUPLICATED_REGISTERED_SOURCE_ID')
    for row in rows:
        old = ix[row['case_id']]
        if not (row['source_sha256'] == source_shas[row['case_id']] ==
                row['evidence']['source_sha256'] and
                row['origin'] == old['origin'] and row['provenance_kind'] == old['kind'] and
                row['historical_v54_disposition'] == old['expected']['v54_disposition'] and
                row['registered_evidence_level'] == 'COMPLETE_SOURCE_SPECIFIC' and
                row['evidence']['level'] == 'COMPLETE_SOURCE_SPECIFIC' and
                row['evidence']['complete_original_source_zero_set'] is True and
                row['evidence']['covered_original_source_interval'] ==
                [old['spec']['parameter_lo'], old['spec']['parameter_hi']] and
                row['historical_disposition_changed'] is False):
            raise ValueError('FIFTY_SOURCE_CERTIFICATE_BINDING_DRIFT:' + row['case_id'])
    summary = registry['summary']
    if not (registry['frozen_corpus_git_blob'] == CORPUS_BLOB and
            summary['by_registered_evidence_level'] == {'COMPLETE_SOURCE_SPECIFIC': 50,
              'PARTIAL_REFUSED_TAIL_ONLY': 0, 'PARTIAL_ORDERED_CHILD': 0,
              'NO_REGISTERED_SOURCE_EVENT_OR_ORDER_WITNESS': 0} and
            summary['complete_finite_sources'] == 49 and
            summary['complete_continuum_sources'] == 1):
        raise ValueError('FIFTY_CENSUS_EVIDENCE_CLASS_DRIFT')
    result = m.proof(M, EPSILON)
    if (result['baseline_sha256'] in source_shas.values() or
            result['adversary_sha256'] in source_shas.values()):
        raise ValueError('NEW_SOURCE_COLLIDES_WITH_FROZEN_ORIGINAL')
    return {
        'frozen_source_count_before_after': [121,121],
        'historical_route_refusals_before_after': [20,20],
        'historical_missing_order_premises_before_after': [30,30],
        'complete_source_specific_witnesses_before_after': [50,50],
        'complete_finite_witnesses': 49,
        'complete_continuum_witnesses': 1,
        'new_frozen_case_ids_resolved': [],
        'historical_v54_dispositions_changed': False,
        'all_121_original_source_hashes_recomputed': True,
        'all_50_evidence_case_ids_and_source_hashes_rechecked': True,
    }


def expected_machine():
    p = m.proof(M, EPSILON)
    return {
        'schema': m.SCHEMA,
        'claim': p['claim'],
        'evidence_class': 'DETERMINISTIC_MODEL',
        'historical_frozen_case_anchor': ANCHOR,
        'historical_anchor_source_sha256': ANCHOR_SHA,
        'frozen_v54_git_blob': CORPUS_BLOB,
        'complete_v2_registry_git_blob': V2_BLOB,
        'selected_prospective_construction': p,
        'census': census(),
        'general_no_solver_impossibility_claim': True,
        'fixed_endpoint_or_knot_jet_budget_route_falsified': True,
        'full_pb00701_coverage_established': False,
        'mc_b_established': False,
        'mc1_established': False,
        'production_authorized': False,
    }


def validate_claim(submitted):
    try:
        actual = expected_machine()
        if m.canonical(submitted) != m.canonical(actual):
            raise ValueError('FORGED_OR_DRIFTED_COUNTEREXAMPLE_REPORT')
        return actual
    except (ValueError, TypeError, OverflowError, MemoryError) as exc:
        return {'status': 'BLOCKED', 'reason': str(exc), 'is_truth_value': False,
                'pb00701_certified': False, 'production_authorized': False}


def deboor_value(spec, t):
    """Independent Cox-de Boor basis evaluation at exact rational interior t."""
    channel = spec['cos_splines']['1']
    p = channel['degree']
    k = [Q(x) for x in channel['knots']]
    c = [Q(x) for x in channel['controls']]
    t = Q(t)
    if t == k[-1]:
        return c[-1]
    if not (k[0] <= t < k[-1]):
        raise ValueError('OUT_OF_DOMAIN')
    previous = [Q(1) if k[i] <= t < k[i+1] else Q(0) for i in range(len(k)-1)]
    for degree in range(1, p+1):
        current = []
        for i in range(len(previous)-1):
            left_den = k[i+degree]-k[i]
            right_den = k[i+degree+1]-k[i+1]
            left = (t-k[i])*previous[i]/left_den if left_den else Q(0)
            right = (k[i+degree+1]-t)*previous[i+1]/right_den if right_den else Q(0)
            current.append(left+right)
        previous = current
    return sum(ci*ni for ci,ni in zip(c,previous))


class FiniteJetFalsifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = m.proof(M, EPSILON)
        cls.baseline = m.construction(M, EPSILON, adversarial=False)
        cls.adversary = m.construction(M, EPSILON, adversarial=True)

    def test_selected_machine_report_and_hashes(self):
        self.assertEqual(self.report['m'], 9)
        self.assertEqual(self.report['first_unmatched_jet_order'], 9)
        self.assertEqual(self.report['baseline_sha256'],
                         'e49198f9f123c1a15f0ad3747f58c20bb917d843dede8f4a18a1fdc8708cb723')
        self.assertEqual(self.report['adversary_sha256'],
                         '52af293fcb0df5a3749ff0f311b06995f35dac88367648ef17b2c79020bcfc34')
        self.assertEqual([Q(x) for x in self.report['adversary_complete_zero_set']],
                         [Q(1,2)-Q(EPSILON), Q(1,2)+Q(EPSILON)])
        self.assertEqual([r['sign'] for r in self.report['adversary_exact_open_sign_cells']],
                         [1,-1,1])

    def test_independent_deboor_original_source_reduction(self):
        for t in [Q(0),Q(1,8), Q(1,4), Q(1,2),Q(3,4),Q(7,8),Q(1),Q(5,4),Q(2)]:
            e = Q(EPSILON)
            value = 1 - (t*(1-t))**M / ((Q(1,2)-e)*(Q(1,2)+e))**M if t < 1 else Q(1)
            self.assertEqual(deboor_value(self.adversary,t),value)
            self.assertEqual(deboor_value(self.baseline,t),Q(1))

    def test_bernstein_global_control_count_and_true_knot(self):
        spline = self.adversary['cos_splines']['1']
        d = 2*M
        self.assertEqual(len(spline['knots']),3*d+2)
        self.assertEqual(len(spline['controls']),2*d+1)
        self.assertEqual(spline['knots'].count('1'), d)
        self.assertEqual(spline['controls'][d], '1')

    def test_exact_arbitrary_order_proof_family(self):
        for n,epsilon in [(0,'1/4'), (1,'1/16'), (3,'1/1024'),
                          (8,EPSILON), (15,'1/281474976710656')]:
            p = m.proof(n+1,epsilon)
            self.assertEqual(p['first_unmatched_jet_order'],n+1)
            self.assertEqual(p['endpoint_and_true_knot_jet_equality_through_order'],n)
            self.assertEqual(p['adversary_root_orders'],[1,1])
            self.assertTrue(p['both_true_knot_point_values_equal_and_positive'])
            self.assertNotEqual(p['baseline_sha256'],p['adversary_sha256'])
            self.assertEqual(Q(p['adversary_complete_zero_set'][1])-
                             Q(p['adversary_complete_zero_set'][0]),2*Q(epsilon))

    def test_two_extremely_close_exact_roots_and_both_signs(self):
        a,b = [Q(x) for x in self.report['adversary_complete_zero_set']]
        self.assertEqual(b-a,Q(1,536870912))
        self.assertEqual(deboor_value(self.adversary,a),Q(0))
        self.assertEqual(deboor_value(self.adversary,b),Q(0))
        self.assertGreater(deboor_value(self.adversary,(a+Q(0))/2),0)
        self.assertLess(deboor_value(self.adversary,Q(1,2)),0)
        self.assertGreater(deboor_value(self.adversary,(b+Q(1))/2),0)
        self.assertGreater(deboor_value(self.baseline,Q(1,2)),0)

    def test_mth_derivative_first_disagreement(self):
        ea = ((Q(1,2)-Q(EPSILON))*(Q(1,2)+Q(EPSILON)))**M
        self.assertEqual(Q(self.report['left_span_difference_order_m_coefficient_at_zero']),-1/ea)
        self.assertEqual(Q(self.report['left_span_difference_order_m_coefficient_at_knot_without_cos_factor']),
                         Q((-1)**(M+1),1)/ea)

    def test_unbounded_jet_order_is_not_constant(self):
        controls = self.adversary['cos_splines']['1']['controls']
        self.assertEqual(sum(Q(x) != 1 for x in controls),1)
        self.assertNotEqual(Q(controls[M]),Q(1))
        self.assertEqual(m.expected_power(M,EPSILON),
                         m.bernstein_to_power([Q(x) for x in controls[:2*M+1]]))

    def test_mutated_control_fails_closed(self):
        altered=copy.deepcopy(self.adversary)
        altered['cos_splines']['1']['controls'][M]='1'
        self.assertEqual(m.validate_source_pair(M,EPSILON,self.baseline,altered)['status'],'BLOCKED')

    def test_mutated_phase_fails_closed(self):
        altered=copy.deepcopy(self.adversary)
        altered['phase_turn_rate']='1/4'
        self.assertEqual(m.validate_source_pair(M,EPSILON,self.baseline,altered)['status'],'BLOCKED')

    def test_mutated_knot_fails_closed(self):
        altered=copy.deepcopy(self.adversary)
        altered['cos_splines']['1']['knots'][2*M+1]='3/2'
        self.assertEqual(m.validate_source_pair(M,EPSILON,self.baseline,altered)['status'],'BLOCKED')

    def test_mutated_original_source_parameter_fails_closed(self):
        altered=copy.deepcopy(self.baseline)
        altered['source_parameter_id']='faked-caller-coordinate'
        self.assertEqual(m.validate_source_pair(M,EPSILON,altered,self.adversary)['status'],'BLOCKED')

    def test_rejects_float_and_noncanonical_rationals(self):
        for e in [0.125, '2/4', True, '-1/4','0','1/2','2','oops']:
            with self.subTest(e=e), self.assertRaises(m.Refusal):
                m.construction(3,e)

    def test_rejects_inadmissible_degrees_and_resource_bounds(self):
        for n in [False, -1,0,21,10**9]:
            with self.subTest(n=n), self.assertRaises(m.Refusal):
                m.proof(n,'1/4')
        with self.assertRaisesRegex(m.Refusal,'RESOURCE_REFUSAL'):
            m.proof(1,'1/'+str(2**300))

    def test_resource_refusal_never_becomes_truth(self):
        result=m.validate_source_pair(21,'1/4',{}, {})
        self.assertEqual(result['status'],'RESOURCE_REFUSAL')
        self.assertIs(result['is_truth_value'],False)

    def test_frozen_historical_source_and_fifty_registry(self):
        c=census()
        self.assertEqual(c['historical_route_refusals_before_after'],[20,20])
        self.assertEqual(c['historical_missing_order_premises_before_after'],[30,30])
        self.assertEqual(c['complete_source_specific_witnesses_before_after'],[50,50])
        self.assertEqual(c['new_frozen_case_ids_resolved'],[])

    def test_registry_source_swap_cannot_preserve_claim(self):
        reg=json.loads(V2.read_text())
        reg['source_cases'][0]['source_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'BINDING_DRIFT'):
            census(v2=reg)

    def test_frozen_disposition_mutation_rejected(self):
        corpus=json.loads(CORPUS.read_text())
        row=next(r for r in corpus['cases'] if r['expected']['v54_disposition'] not in
                 ('BLOCKED','BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE'))
        row['expected']['v54_disposition']='BLOCKED'
        with self.assertRaisesRegex(ValueError,'HISTORICAL_CENSUS_DRIFT'):
            census(corpus=corpus)

    def test_machine_report_digest_and_fake_root_rejection(self):
        actual=expected_machine()
        stored=json.loads(REPORT.read_text())
        self.assertEqual(actual,stored)
        self.assertEqual(validate_claim(stored),actual)
        forged=copy.deepcopy(actual)
        forged['selected_prospective_construction']['adversary_complete_zero_set']=['1/2']
        refused=validate_claim(forged)
        self.assertEqual(refused['status'],'BLOCKED')
        self.assertIs(refused['is_truth_value'],False)

    def test_forged_promotion_rejected(self):
        altered=expected_machine()
        altered['mc_b_established']=True
        self.assertEqual(validate_claim(altered)['status'],'BLOCKED')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--contract',action='store_true')
    ap.add_argument('--self-test',action='store_true')
    args=ap.parse_args()
    if not (args.contract or args.self_test):
        ap.error('specify --contract and/or --self-test')
    if args.contract:
        print(m.canonical(expected_machine()))
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(FiniteJetFalsifierTests)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__=='__main__':
    main()
