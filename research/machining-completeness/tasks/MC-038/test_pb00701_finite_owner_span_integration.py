#!/usr/bin/env python3
"""V54 original B-spline acceptance, mixed partitions, corpus rerun and falsification."""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import copy
import json
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_pb00701_mixed_owner_span as core
import test_pb00701_mixed_owner_span_integration as v53_tests
import pb00701_finite_owner_span_model as m
import pb00701_finite_owner_span_certificate as checker
import pb00701_finite_owner_inventory as inventory

source, a, b = core.source, m.a, m.b
BAD = (ValueError, TypeError, KeyError, AssertionError, AttributeError, IndexError)
DOMINANCE = m.SIGN_OWNER
V19 = 'PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR'
V50 = 'PB00701_V50_VANISHING_SOURCE_FACTOR'


def constant_piece(h0, h1=Q(1, 100), s2=Q(1, 200)):
    return ({0: [Q(h0)], 1: [Q(h1)]}, {2: [Q(s2)]})


def candidate():
    """Issue #275 principal source: the actual reversed V53 acceptance source."""
    return source.reverse_source(v53_tests.candidate())


def strict_legacy():
    # V19 anchor (one simple crossing) continued by an exactly dominated constant span.
    return source.encode([core.anchor(), constant_piece(Q(1, 2))], ident='v54-strict-legacy')


def four_piece():
    # SIGN(-) | V51 product | V19 strict | SIGN(+), continuous at every knot.
    product = source.physical_piece(source.power([-1, 0, 2], 2))
    return source.encode([constant_piece(-Q(1, 2)), product, core.anchor(Q(1, 2)), constant_piece(Q(3, 2))],
                         ident='v54-four-piece')


@lru_cache(maxsize=None)
def _evidence(text):
    spec = json.loads(text)
    return json.dumps(m.build_finite_owner_source_evidence(spec))


def evidence(spec):
    return json.loads(_evidence(json.dumps(spec, sort_keys=True)))


def certified(spec):
    result = evidence(spec)
    assert result['status'] == 'FINITE_OWNER_SOURCE_EVIDENCE_CERTIFIED', (result.get('reason'), result.get('owner'))
    assert checker.validate_finite_owner_certificate(result['certificate'], spec) is True
    return result['certificate']


def any_certificate(spec):
    result = evidence(spec)
    if result['status'] == 'MIXED_OWNER_SOURCE_EVIDENCE_CERTIFIED':
        assert b.same(result, m.v53.build_mixed_source_evidence(spec))
        return result['certificate']
    return certified(spec)


class OriginalSourceTests(unittest.TestCase):
    def test_actual_reversed_v53_residual_closes_with_retained_amplitude_owner(self):
        spec = candidate()
        prior = m.v53.build_mixed_source_evidence(spec)
        self.assertEqual((prior['reason'], prior['owner']), ('SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE', DOMINANCE))
        result = evidence(spec)
        self.assertEqual(result['status'], 'FINITE_OWNER_SOURCE_EVIDENCE_CERTIFIED')
        self.assertTrue(b.same(result['predecessor_result'], prior))
        proof = result['certificate']
        self.assertEqual(proof['span_evidence_kinds'], ['SIGN_SPAN', 'V51_PRODUCT'])
        self.assertEqual(proof['span_original_owners'], [DOMINANCE, V50])
        self.assertEqual(proof['span_owner_categories'], [2, 1])
        sign_view = proof['span_proofs'][0]
        physical = prior['predecessor_result']['predecessor_result']['physical_event_result']
        self.assertTrue(b.same(sign_view['underlying_witness'], physical['spans'][0]['route']))
        self.assertEqual(sign_view['underlying_witness']['margin'], '97/200')
        self.assertFalse(sign_view['sign_evidence']['monotonicity_claimed'])
        forward = m.v53.build_mixed_source_evidence(v53_tests.candidate())['certificate']
        self.assertEqual(proof['global_root_summary'], forward['global_root_summary'])
        self.assertEqual(proof['global_root_summary']['crossings_open'], 1)
        self.assertEqual(proof['global_root_summary']['tangencies_open'], 1)
        self.assertEqual([c['physical_sign'] for c in proof['maximal_open_sign_cells']],
                         list(reversed([c['physical_sign'] for c in forward['maximal_open_sign_cells']])))
        self.assertEqual(proof['knot_evidence'][0]['physical_relation'], 'POSITIVE')
        self.assertEqual(proof['maximal_open_sign_cells'][0]['included_nonzero_source_knots'], ['knot:0'])

    def test_preserved_v52_all_product_and_v53_mixed_results_are_returned_unchanged(self):
        for spec in (source.fixture('cross'), v53_tests.candidate(), v53_tests.zero_join()):
            prior = m.v53.build_mixed_source_evidence(spec)
            self.assertIn(prior['status'], ('PIECEWISE_SOURCE_EVIDENCE_CERTIFIED', 'MIXED_OWNER_SOURCE_EVIDENCE_CERTIFIED'))
            self.assertTrue(b.same(evidence(spec), prior))

    def test_product_strict_legacy_and_all_legacy_partitions(self):
        sl = certified(strict_legacy())
        self.assertEqual(sl['span_evidence_kinds'], ['STRICT_SPAN', 'SIGN_SPAN'])
        self.assertEqual(sl['span_original_owners'], [V19, DOMINANCE])
        self.assertEqual(sl['global_root_summary']['distinct_roots_open'], 1)
        self.assertEqual([c['physical_sign'] for c in sl['maximal_open_sign_cells']], [-1, 1])
        legacy = certified(source.encode([constant_piece(1), constant_piece(1)], ident='v54-all-legacy'))
        self.assertEqual(legacy['span_evidence_kinds'], ['SIGN_SPAN', 'SIGN_SPAN'])
        self.assertEqual(legacy['global_root_summary']['total_distinct_roots_closed'], 0)
        self.assertEqual(len(legacy['maximal_open_sign_cells']), 1)
        four = certified(four_piece())
        self.assertEqual(four['span_evidence_kinds'], ['SIGN_SPAN', 'V51_PRODUCT', 'STRICT_SPAN', 'SIGN_SPAN'])
        self.assertEqual(four['span_owner_categories'], [2, 1, 1, 2])
        self.assertEqual([k['physical_relation'] for k in four['knot_evidence']], ['NEGATIVE', 'POSITIVE', 'POSITIVE'])
        self.assertEqual([c['physical_sign'] for c in four['maximal_open_sign_cells']], [-1, 1, 1])
        self.assertEqual(four['global_root_summary']['distinct_roots_open'], 2)

    def test_owner_strict_adapters_compose_on_original_sources_from_frozen_corpus(self):
        seen = set()
        for case in inventory.load_corpus()['cases']:
            expected = case['expected']
            if expected['v54_disposition'] != 'FINITE_OWNER_SOURCE_EVIDENCE_CERTIFIED':
                continue
            if 'OWNER_STRICT_SPAN' not in expected['view_kinds'] or len(seen) >= 4:
                continue
            proof = certified(case['spec'])
            self.assertEqual(proof['span_evidence_kinds'], expected['view_kinds'])
            seen.update(o for o in proof['span_original_owners'] if o in m.STRICT_ADAPTERS)
        self.assertGreaterEqual(len(seen), 2)

    def test_repeated_knots_different_degrees_and_extra_channels(self):
        spec = strict_legacy()
        spec['sin_splines']['3'] = {'degree': 0, 'knots': ['0', '3/2', '2'], 'controls': ['1/400', '1/400']}
        spec['cos_splines']['2'] = {'degree': 2, 'knots': ['0', '0', '0', '1', '1', '1', '2', '2', '2'],
                                    'controls': ['1/500', '1/500', '1/500', '1/500', '1/500', '1/500']}
        proof = certified(spec)
        self.assertEqual(proof['source_lowering']['source_boundaries'], ['0', '1', '3/2', '2'])
        self.assertEqual(proof['span_evidence_kinds'], ['STRICT_SPAN', 'SIGN_SPAN', 'SIGN_SPAN'])
        self.assertEqual(proof['global_root_summary']['distinct_roots_open'], 1)

    def test_continuity_is_exact_and_tiny_jump_is_refused(self):
        exact = certified(source.encode([constant_piece(1), constant_piece(1)], ident='v54-jump'))
        self.assertEqual(exact['knot_evidence'][0]['physical_relation'], 'POSITIVE')
        jump = source.encode([constant_piece(1), constant_piece(1 + Q(1, 10**30))], ident='v54-jump')
        prior = m.v53.build_mixed_source_evidence(jump)
        result = evidence(jump)
        self.assertEqual(result['reason'], 'PHYSICAL_SOURCE_KNOT_DISCONTINUITY')
        self.assertEqual(result['physical_difference_evidence']['relation'], 'POSITIVE')
        self.assertTrue(b.same(result['predecessor_result'], prior))
        self.assertFalse(result['finite_owner_evidence_complete'])

    def test_reversal_negation_and_nonunit_global_maps(self):
        for spec in (candidate(), strict_legacy(), four_piece()):
            proof = certified(spec)
            signs = [c['physical_sign'] for c in proof['maximal_open_sign_cells']]
            moved = certified(source.affine_source(spec))
            self.assertEqual(moved['global_root_summary'], proof['global_root_summary'])
            self.assertEqual(moved['span_original_owners'], proof['span_original_owners'])
            # Reversing the principal source returns the V53-admitted original: preserved, not regrown.
            reverse = any_certificate(source.reverse_source(spec))
            self.assertEqual(reverse['global_root_summary']['distinct_roots_open'],
                             proof['global_root_summary']['distinct_roots_open'])
            self.assertEqual([c['physical_sign'] for c in reverse['maximal_open_sign_cells']], list(reversed(signs)))
            negative = copy.deepcopy(spec)
            for key in ('cos_splines', 'sin_splines'):
                for spline in negative[key].values():
                    spline['controls'] = [str(-3 * Q(x)) for x in spline['controls']]
            negated = certified(negative)
            self.assertEqual(negated['span_original_owners'], proof['span_original_owners'])
            self.assertEqual(negated['global_root_summary'], proof['global_root_summary'])
            self.assertEqual([c['physical_sign'] for c in negated['maximal_open_sign_cells']], [-s for s in signs])

    def test_category_three_and_four_owners_are_reported_not_adapted(self):
        # Rate zero: the second span is an exact stationary polynomial with counts only.
        spec = source.encode([constant_piece(1), ({0: [Q(1), Q(-2)], 1: [Q(1, 100)]}, {2: [Q(1, 200)]})],
                             rate='0', ident='v54-stationary')
        prior = m.v53.build_mixed_source_evidence(spec)
        result = evidence(spec)
        self.assertEqual(result['reason'], 'SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE')
        self.assertEqual((result['owner'], result['owner_category']), ('EXACT_STATIONARY_PHASE_POLYNOMIAL', 3))
        self.assertEqual(result['missing_premise'], m.LACKING_PREMISE['EXACT_STATIONARY_PHASE_POLYNOMIAL'][1])
        self.assertTrue(b.same(result['predecessor_result'], prior))
        for case in inventory.load_corpus()['cases']:
            owners = [o for o, *_ in case["expected"]["observed"]["spans"]]
            if any(m.category(o) == 4 for o in owners):
                prior = m.v53.build_mixed_source_evidence(case['spec'])
                self.assertTrue(b.same(evidence(case['spec']), prior))
                break
        else:
            self.fail('frozen corpus lacks a category-4 owner')


class CheckerFalsificationTests(unittest.TestCase):
    def rejected(self, candidate, spec):
        with self.assertRaises(BAD):
            self.assertIs(checker.validate_finite_owner_certificate(candidate, spec), True)

    def test_full_source_checker_rejects_corruption_without_replacement_search(self):
        spec = four_piece()
        proof = certified(spec)
        views = proof['span_proofs']
        changes = [(['span_proofs'], list(reversed(views))), (['span_proofs'], views[:3]),
                   (['span_proofs'], views + views[:1]), (['span_proofs'], [views[0], views[0], views[2], views[3]]),
                   (['span_original_owners'], [V19] * 4), (['span_owner_categories'], [1, 1, 1, 1]),
                   (['span_evidence_kinds'], ['STRICT_SPAN'] * 4), (['schema'], m.v53.SCHEMA),
                   (['sign_spans_claim_derivative_or_monotonicity'], True), (['historical_owners_relabelled'], True),
                   (['general_nonmonotone_solver_claimed'], True), (['native_topology_claimed'], True),
                   (['material_body_transition_claimed'], True),
                   (['global_analytic_multiplicity_at_source_knots_claimed'], True),
                   (['global_root_summary', 'distinct_roots_open'], 3),
                   (['global_root_summary', 'distinct_roots_open'], 2.0),
                   (['global_root_summary', 'distinct_roots_open'], True),
                   (['maximal_open_sign_cells', 0, 'physical_sign'], 1),
                   (['knot_evidence', 0, 'physical_relation'], 'ZERO'),
                   (['span_proofs', 0, 'kind'], 'OWNER_STRICT_SPAN'),
                   (['span_proofs', 0, 'underlying_witness', 'direction'], 'INCREASING'),
                   (['span_proofs', 0, 'ordered_boundaries', 0, 'physical_relation'], 'ZERO'),
                   (['span_proofs', 2, 'owner'], 'PB00701_V20_EXACT_POINTWISE_DERIVATIVE_ENVELOPE'),
                   (['unknown_authority'], True)]
        for path, value in changes:
            bad = copy.deepcopy(proof)
            target = bad
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            self.rejected(bad, spec)
        with core.no_search():
            self.assertIs(checker.validate_finite_owner_certificate(proof, spec), True)

    def test_source_phase_harmonic_and_identity_mutations_are_rejected(self):
        spec = candidate()
        proof = certified(spec)
        mutated = []
        for key, value in (('source_parameter_id', 'other'), ('phase_turn_offset', '1/3'),
                           ('phase_turn_rate', '-1/5'), ('parameter_hi', '3/2')):
            bad = copy.deepcopy(spec); bad[key] = value; mutated.append(bad)
        bad = copy.deepcopy(spec); bad['cos_splines']['3'] = bad['cos_splines'].pop('1'); mutated.append(bad)
        bad = copy.deepcopy(spec); bad['cos_splines']['0']['controls'][0] = '7/5'; mutated.append(bad)
        for other in mutated:
            self.rejected(proof, other)

    def test_bool_float_unknown_and_annotation_inputs_do_not_grow_scope(self):
        spec = candidate()
        variants = []
        for key, value in (('parameter_lo', 0.0), ('parameter_lo', False), ('phase_turn_rate', -0.25),
                           ('annotation', 'caller says monotone'), ('derivative_certificate', {'direction': 'UP'})):
            bad = copy.deepcopy(spec); bad[key] = value; variants.append(bad)
        bad = copy.deepcopy(spec); bad['cos_splines']['0']['degree'] = True; variants.append(bad)
        for variant in variants:
            try:
                prior = m.v53.build_mixed_source_evidence(variant)
            except BAD as exc:
                with self.assertRaises(type(exc)):
                    m.build_finite_owner_source_evidence(variant)
                continue
            self.assertTrue(b.same(m.build_finite_owner_source_evidence(variant), prior))

    def test_stage_resource_refusal_retains_predecessor_and_unrelated_errors_propagate(self):
        spec = candidate()
        prior = m.v53.build_mixed_source_evidence(spec)
        for target, name in ((m, 'regenerate_owner_route'), (m.v52, 'build_joins'), (m.v52, 'assemble')):
            with patch.object(target, name, side_effect=MemoryError):
                result = m.build_finite_owner_source_evidence(spec)
            self.assertEqual(result['status'], 'RESOURCE_REFUSAL')
            self.assertIs(result['is_truth_value'], False)
            self.assertTrue(b.same(result['predecessor_result'], prior))
            self.assertFalse(result['finite_owner_evidence_complete'])
            with patch.object(target, name, side_effect=RuntimeError('unrelated')):
                with self.assertRaises(RuntimeError):
                    m.build_finite_owner_source_evidence(spec)
        with patch.object(m.v53, 'build_mixed_source_evidence', side_effect=MemoryError):
            refused = m.build_finite_owner_source_evidence(spec)
        self.assertEqual((refused['status'], refused['is_truth_value']), ('RESOURCE_REFUSAL', False))
        self.assertNotIn('predecessor_result', refused)


class CorpusTests(unittest.TestCase):
    def test_frozen_admitted_corpus_reruns_through_complete_predecessor_chain(self):
        data = inventory.load_corpus()
        rows = []
        for case in data['cases']:
            row = inventory.run_case(case)
            self.assertTrue(b.same(row, case['expected']), case['id'])
            rows.append(row)
        summary = inventory.corpus_summary(rows)
        self.assertTrue(b.same(summary, data['summary']))
        observed = {o for owners in summary['observed_by_category'].values() for o in owners}
        for owner in list(m.SIGN_ADAPTERS) + list(m.STRICT_ADAPTERS):
            self.assertIn(owner, observed)
        for owner in data['fixtures']:
            self.assertEqual(m.category(owner), 2)


def run():
    suite = unittest.TestSuite()
    for case in (OriginalSourceTests, CheckerFalsificationTests, CorpusTests):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(case))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == '__main__':
    run()
