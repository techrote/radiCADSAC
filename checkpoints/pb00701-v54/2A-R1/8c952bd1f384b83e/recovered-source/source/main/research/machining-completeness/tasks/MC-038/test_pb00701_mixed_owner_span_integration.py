#!/usr/bin/env python3
"""V53 original B-spline acceptance, continuous mixed partitions and falsification."""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import copy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_pb00701_mixed_owner_span as core
import pb00701_mixed_owner_span_model as m
import pb00701_mixed_owner_span_certificate as checker

source, a, b = core.source, m.a, m.b


def candidate():
    return source.encode([source.physical_piece(source.power([-1, 0, 2], 2)), core.anchor(Q(1, 2))],
                         ident='v53-issue271-original-source')


@lru_cache(maxsize=1)
def acceptance():
    spec = candidate()
    prior = m.v52.build_piecewise_source_evidence(spec)
    result = m.build_mixed_source_evidence(spec)
    assert result['status'] == 'MIXED_OWNER_SOURCE_EVIDENCE_CERTIFIED', result.get('reason')
    return spec, prior, result


def tail_for(piece, slope=100):
    # Match EVERY physical amplitude limit, then use a large rational h=0
    # derivative on the next real source piece; no endpoint-value fake owner.
    tail = tuple({h: [sum(map(Q, poly))] for h, poly in mapping.items()} for mapping in piece)
    tail[0][0] = [tail[0].get(0, [Q(0)])[0], Q(slope)]
    return tail


def owner_source(version):
    args = core.strict_args(version)
    return source.encode([args[:2], tail_for(args[:2])], offset=args[4], rate=args[5], ident=args[2])


def zero_join(sign=1):
    left = source.physical_piece(a.pmul(source.power([-1, 1], 2), source.power([-1, 0, 2], 2)))
    right = core.scale_piece(core.anchor(0), sign)
    return source.encode([left, right], ident='v53-simple-repeated-join')


def four_piece():
    # g=(1-k*t*(1-t))^2 has both exterior values 1; k=8 and k=6
    # give distinct selected quadratic fields and two double roots per product.
    pieces = []
    for i, k in enumerate((8, None, 6, None)):
        piece = core.anchor(-Q(1, 2) if i % 2 == 0 else Q(1, 2), 1 if i % 2 == 0 else -1)
        if k:
            factor = source.power([1, -k, k], 2)
            piece = tuple({h: a.pmul(factor, p) for h, p in axis.items()} for axis in piece)
        pieces.append(piece)
    return source.encode(pieces, ident='v53-four-original-pieces')


class MixedSourceTests(unittest.TestCase):
    def checked(self, spec):
        original = copy.deepcopy(spec)
        result = m.build_mixed_source_evidence(spec)
        self.assertEqual(result['status'], 'MIXED_OWNER_SOURCE_EVIDENCE_CERTIFIED', result.get('reason'))
        proof = result['certificate']
        self.assertIs(checker.validate_mixed_certificate(proof, spec), True)
        self.assertEqual(spec, original)
        return proof

    def rejected(self, proof, spec):
        with self.assertRaises((ValueError, TypeError, KeyError, AssertionError)):
            checker.validate_mixed_certificate(proof, spec)

    def test_candidate_actual_predecessor_boundary_owners_and_exact_two_root_union(self):
        spec, prior, result = acceptance(); proof = result['certificate']
        self.assertEqual(prior['reason'], 'NOT_ALL_SOURCE_SPANS_HAVE_V51_PRODUCT_WITNESSES')
        self.assertEqual(a._json(prior), a._json(result['predecessor_result']))
        old = prior['predecessor_result']; physical = old['physical_event_result']
        self.assertEqual(physical['status'], 'CERTIFIED')
        self.assertEqual([s['route_kind'] for s in physical['spans']], [m.v51.V50_OWNER, core.OWNERS[19]])
        self.assertEqual(proof['span_evidence_kinds'], ['V51_PRODUCT', 'STRICT_SPAN'])
        self.assertEqual(a._json(proof['span_proofs'][0]['underlying_witness']),
                         a._json(old['ordered_spans'][0]['ordered_evidence']))
        self.assertEqual(a._json(proof['span_proofs'][1]['underlying_witness']),
                         a._json(physical['spans'][1]['route']))
        self.assertEqual(m.v50.amplitude_gcd(*m.v50.maps(proof['span_proofs'][1]['source_material'])), [1])
        summary = proof['global_root_summary']
        self.assertEqual((summary['distinct_roots_open'], summary['crossings_open'], summary['tangencies_open']), (2, 1, 1))
        self.assertEqual(summary['source_knot_roots'], 0)
        self.assertEqual([c['physical_sign'] for c in proof['maximal_open_sign_cells']], [-1, 1, 1])
        self.assertEqual(proof['maximal_open_sign_cells'][-1]['included_nonzero_source_knots'], ['knot:0'])
        self.assertEqual(proof['maximal_open_sign_cells'][-1]['elementary_cell_indices'], [2, 3])
        join = proof['knot_evidence'][0]
        self.assertEqual(join['physical_relation'], 'POSITIVE')
        self.assertEqual(join['physical_difference_evidence']['relation'], 'ZERO')
        self.assertEqual(join['one_sided_amplitude_values'][0], join['one_sided_amplitude_values'][1])
        self.assertEqual(join['one_sided_amplitude_values'][0]['COS']['0'], '1/2')
        self.assertIs(checker.validate_mixed_certificate(proof, spec), True)
        print('v53 ACTUAL SOURCE: original B-splines, retained V50/V19, two roots, exact nonzero join and maximal bridge: PASS')

    def test_existing_all_product_v52_result_byte_for_byte_and_typed_common_view(self):
        spec = source.fixture()
        prior = m.v52.build_piecewise_source_evidence(spec)
        self.assertEqual(prior['status'], 'PIECEWISE_SOURCE_EVIDENCE_CERTIFIED')
        self.assertEqual(a._json(m.build_mixed_source_evidence(spec)), a._json(prior))
        old = prior['certificate']; lowering = m.v52.lower_source(spec)
        views = [m.build_ordered_span_view('V51_PRODUCT', m.v51.V50_OWNER, p, *m.v52.source_args(row))
                 for row, p in zip(lowering['spans'], old['span_proofs'])]
        proof = m.build_mixed_certificate(spec, views)
        self.assertIs(checker.validate_mixed_certificate(proof, spec), True)
        self.assertEqual(proof['global_root_summary'], old['global_root_summary'])
        self.assertEqual(proof['span_evidence_kinds'], ['V51_PRODUCT'] * 2)

    def test_all_strict_three_real_pieces_multiple_implicit_roots_and_opposite_directions(self):
        pieces = [core.anchor(), core.anchor(Q(1, 2), -1), core.anchor()]
        spec = source.encode(pieces, ident='v53-three-strict-zigzag')
        prior = m.v52.build_piecewise_source_evidence(spec)
        self.assertEqual(prior['status'], 'CERTIFIED')
        proof = self.checked(spec)
        self.assertEqual(proof['span_evidence_kinds'], ['STRICT_SPAN'] * 3)
        self.assertEqual(proof['global_root_summary']['distinct_roots_open'], 3)
        self.assertEqual([p['strict_evidence']['complete_derivative']['delta'] for p in proof['span_proofs']], [1, -1, 1])
        roots = proof['ordered_physical_events']
        self.assertEqual([p['id'] for p in roots], ['span:0/strict:open', 'span:1/strict:open', 'span:2/strict:open'])
        self.assertEqual(len({p['global_position']['local_root_binding_sha256'] for p in roots}), 3)
        self.assertEqual([p['physical_sign'] for p in proof['maximal_open_sign_cells']], [-1, 1, -1, 1])
        self.assertEqual(sum(len(p['included_nonzero_source_knots']) for p in proof['maximal_open_sign_cells']), 2)

    def test_four_original_pieces_two_products_two_stricts_and_distinct_algebraic_fields(self):
        proof = self.checked(four_piece())
        self.assertEqual(proof['span_evidence_kinds'], ['V51_PRODUCT', 'STRICT_SPAN'] * 2)
        self.assertEqual(proof['global_root_summary']['distinct_roots_open'], 8)
        self.assertEqual(proof['global_root_summary']['analytic_multiple_roots_strictly_inside_spans'], 4)
        fields = []
        for i in (0, 2):
            product = proof['span_proofs'][i]['underlying_witness']
            events = product['physical_event_result']['factor_root_evidence']['factor_events']
            fields.append([x['source_cut'] for x in events])
        self.assertNotEqual(fields[0], fields[1])
        self.assertEqual(len(proof['source_lowering']['spans']), 4)
        self.assertEqual(sum(len(c['included_nonzero_source_knots']) for c in proof['maximal_open_sign_cells']), 3)
        with core.no_search():
            self.assertIs(checker.validate_mixed_certificate(proof, four_piece()), True)

    def test_each_strict_owner_in_an_actual_continuous_full_source_without_search(self):
        for version in (19, 47, 48, 49):
            with self.subTest(version=version):
                spec = owner_source(version)
                prior = m.v52.build_piecewise_source_evidence(spec)
                self.assertEqual(prior['status'], 'CERTIFIED')
                proof = self.checked(spec)
                self.assertEqual(proof['span_original_owners'], [core.OWNERS[version], core.OWNERS[19]])
                self.assertEqual(a._json(proof['span_proofs'][0]['underlying_witness']), a._json(prior['spans'][0]['route']))
                with core.no_search():
                    self.assertIs(checker.validate_mixed_certificate(proof, spec), True)

    def test_simple_repeated_source_knot_zero_crossing_tangency_and_global_scales(self):
        for sign, kind in ((1, 'TANGENCY'), (-1, 'CROSSING')):
            with self.subTest(sign=sign):
                spec = zero_join(sign)
                proof = self.checked(spec)
                knot = next(p for p in proof['ordered_physical_events'] if p['kind'] == 'SOURCE_KNOT')
                self.assertEqual(knot['one_sided_orders'], [2, 1])
                self.assertEqual(knot['event_kind'], kind)
                self.assertEqual(knot['neighborhood_signs'], [1, sign])
                self.assertIsNone(knot['analytic_multiplicity'])
                self.assertEqual(proof['global_root_summary']['source_knot_roots'], 1)
                self.assertEqual(proof['global_root_summary']['distinct_roots_open'], 3)
                mapped = self.checked(source.affine_source(spec))
                self.assertEqual(mapped['knot_evidence'][0]['global_derivative_scales'], ['1/9', '1/3'])
                reversed_proof = self.checked(source.reverse_source(spec))
                self.assertEqual(reversed_proof['knot_evidence'][0]['one_sided_orders'], [1, 2])

    def test_strict_external_roots_and_both_directions_from_original_source(self):
        # Both ORIGINAL exteriors are zero; the positive internal join is not a
        # root. Neither span can be certified by the older nonzero owner.
        spec = source.encode([core.anchor(-Q(1, 100)), core.anchor(Q(99, 100), -Q(98, 100))])
        for original in (spec, source.reverse_source(spec), source.affine_source(spec)):
            proof = self.checked(original)
            self.assertEqual(proof['global_root_summary']['exterior_root_orders'], {'left': 1, 'right': 1})
            self.assertEqual(proof['global_root_summary']['total_distinct_roots_closed'], 2)
            self.assertEqual(proof['global_root_summary']['distinct_roots_open'], 0)
            self.assertEqual(proof['span_evidence_kinds'], ['STRICT_SPAN'] * 2)

    def test_physical_not_amplitude_continuity_and_same_sign_tiny_jump_refusal(self):
        left = source.physical_piece(source.power([-1, 0, 2], 2))
        right = core.anchor(Q(1, 2)); right[0][1] = [-Q(1, 100)]; right[1][2] = [-Q(1, 200)]
        spec = source.encode([left, right]); proof = self.checked(spec)
        join = proof['knot_evidence'][0]
        self.assertNotEqual(join['one_sided_amplitude_values'][0], join['one_sided_amplitude_values'][1])
        self.assertEqual(join['physical_difference_evidence']['relation'], 'ZERO')
        for jump in (Q(1, 10), Q(1, 10**80)):
            changed = copy.deepcopy(right); changed[0][0][0] += jump
            bad = source.encode([left, changed])
            prior = m.v52.build_piecewise_source_evidence(bad)
            result = m.build_mixed_source_evidence(bad)
            self.assertEqual(result['reason'], 'PHYSICAL_SOURCE_KNOT_DISCONTINUITY')
            self.assertEqual(result['physical_difference_evidence']['relation'], 'POSITIVE')
            self.assertEqual(result['predecessor_result'], prior)
            self.assertFalse(result['mixed_owner_evidence_complete'])

    def test_original_channel_partitions_repeated_knots_and_nonconstant_harmonic_amplitudes(self):
        # A constant channel spans the whole source while the other channels have
        # repeated knots. A real extra knot at 3/2 produces three original pieces.
        pieces = [core.anchor(), core.anchor(Q(1, 2), -1)]
        spec = source.encode(pieces)
        spec['cos_splines']['1'] = {'degree': 0, 'knots': ['0', '2'], 'controls': ['1/100']}
        spec['sin_splines']['2'] = {'degree': 0, 'knots': ['0', '3/2', '2'], 'controls': ['1/200', '1/200']}
        proof = self.checked(spec)
        self.assertEqual(proof['source_lowering']['source_boundaries'], ['0', '1', '3/2', '2'])
        self.assertEqual(len(proof['span_proofs']), 3)
        # Live nonconstant oscillatory amplitudes, continuous at the true knot.
        first = core.anchor(); first[0][1] = [Q(1, 100), Q(1, 10000)]; first[1][2] = [Q(1, 200), -Q(1, 10000)]
        live = self.checked(source.encode([first, tail_for(first)]))
        self.assertEqual(live['span_evidence_kinds'], ['STRICT_SPAN'] * 2)

    def test_cropped_global_maps_reversal_and_source_negation_preserve_physical_counts(self):
        spec, _, result = acceptance(); proof = result['certificate']
        signs = [c['physical_sign'] for c in proof['maximal_open_sign_cells']]
        transformed = self.checked(source.affine_source(spec))
        self.assertEqual(transformed['source_lowering']['source_boundaries'], ['2', '5', '8'])
        self.assertEqual(transformed['global_root_summary'], proof['global_root_summary'])
        # The reversed primary fixture changes fixed predecessor selection:
        # the root-free span is owned by older amplitude dominance, NOT v19.
        reversed_spec = source.reverse_source(spec)
        prior_reverse = m.v52.build_piecewise_source_evidence(reversed_spec)
        reverse = m.build_mixed_source_evidence(reversed_spec)
        self.assertEqual(reverse['reason'], 'SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE')
        self.assertEqual(reverse['owner'], 'EXACT_RATIONAL_AMPLITUDE_DOMINANCE')
        self.assertEqual(reverse['predecessor_result'], prior_reverse)
        # Reversal is positively established on a genuinely admitted mixed
        # source (not by relabelling that old owner).
        admitted = zero_join()
        before_reverse = self.checked(admitted)
        after_reverse = self.checked(source.reverse_source(admitted))
        self.assertEqual([c['physical_sign'] for c in after_reverse['maximal_open_sign_cells']],
                         list(reversed([c['physical_sign'] for c in before_reverse['maximal_open_sign_cells']])))
        cropped = copy.deepcopy(spec); cropped['parameter_lo'] = '1/4'; cropped['parameter_hi'] = '7/4'
        cropped_proof = self.checked(cropped)
        self.assertEqual(cropped_proof['source_lowering']['source_boundaries'], ['1/4', '1', '7/4'])
        self.assertEqual(cropped_proof['global_root_summary'], proof['global_root_summary'])
        negative = copy.deepcopy(spec)
        for key in ('cos_splines', 'sin_splines'):
            for spline in negative[key].values():
                spline['controls'] = [str(-3 * Q(x)) for x in spline['controls']]
        negated = self.checked(negative)
        self.assertEqual(negated['span_original_owners'], proof['span_original_owners'])
        self.assertEqual(negated['global_root_summary'], proof['global_root_summary'])
        self.assertEqual([c['physical_sign'] for c in negated['maximal_open_sign_cells']], [-s for s in signs])

    def test_full_source_checker_rejects_corruption_without_replacement_search(self):
        spec, _, result = acceptance(); proof = result['certificate']
        changes = [(['source_lowering', 'source_boundaries'], ['0', '2']),
                   (['span_proofs'], list(reversed(proof['span_proofs']))),
                   (['span_proofs'], proof['span_proofs'][:1]),
                   (['span_proofs'], proof['span_proofs'] + proof['span_proofs'][:1]),
                   (['span_proofs', 1, 'owner'], core.OWNERS[47]),
                   (['span_proofs', 1, 'strict_evidence', 'complete_derivative', 'delta'], -1),
                   (['span_proofs', 1, 'underlying_witness', 'all_roots_simple'], False),
                   (['span_proofs', 0, 'underlying_witness', 'physical_event_result', 'factorization', 'monic_factor'], ['1']),
                   (['knot_evidence', 0, 'physical_difference_evidence', 'relation'], 'POSITIVE'),
                   (['knot_evidence', 0, 'one_sided_orders'], [1, 1]),
                   (['knot_evidence', 0, 'analytic_multiplicity'], 2),
                   (['ordered_physical_events'], list(reversed(proof['ordered_physical_events']))),
                   (['ordered_physical_events'], proof['ordered_physical_events'][:-1]),
                   (['ordered_physical_events'], proof['ordered_physical_events'] * 2),
                   (['ordered_boundaries', 1, 'global_position', 'positive_scale'], '2'),
                   (['elementary_open_cells', 0, 'source_span_index'], 1),
                   (['elementary_open_cells', 0, 'boundary_ids'], ['exterior:left', 'exterior:right']),
                   (['maximal_open_sign_cells', 2, 'included_nonzero_source_knots'], []),
                   (['maximal_open_sign_cells', 2, 'elementary_cell_indices'], [2]),
                   (['maximal_open_sign_cells'], proof['maximal_open_sign_cells'][:-1]),
                   (['global_root_summary', 'total_distinct_roots_closed'], 3),
                   (['global_root_summary', 'source_knot_roots'], False),
                   (['strict_owners_relabelled_as_product'], True),
                   (['global_analytic_multiplicity_at_source_knots_claimed'], True),
                   (['general_nonmonotone_solver_claimed'], True),
                   (['native_topology_claimed'], True), (['material_body_transition_claimed'], True)]
        with core.no_search():
            self.assertIs(checker.validate_mixed_certificate(proof, spec), True)
            for path, value in changes:
                with self.subTest(path=path):
                    self.rejected(source.mutate(proof, path, value), spec)
            forged = copy.deepcopy(proof); forged['MC-B'] = 'ESTABLISHED'
            self.rejected(forged, spec)

    def test_original_source_controls_harmonics_phase_id_degree_knots_cannot_be_rescued_by_digest(self):
        spec, _, result = acceptance(); proof = result['certificate']
        variants = [source.mutate(spec, ['source_parameter_id'], 'substituted'),
                    source.mutate(spec, ['phase_turn_offset'], '1/8'),
                    source.mutate(spec, ['phase_turn_rate'], '-1/4'),
                    source.mutate(spec, ['parameter_lo'], '1/10')]
        for key in ('cos_splines', 'sin_splines'):
            for h, spline in spec[key].items():
                for i in (0, len(spline['controls']) - 1):
                    variants.append(source.mutate(spec, [key, h, 'controls', i], str(Q(spline['controls'][i]) + Q(1, 10**12))))
        knot = copy.deepcopy(spec)
        for key in ('cos_splines', 'sin_splines'):
            for spline in knot[key].values():
                spline['knots'] = ['9/10' if x == '1' else x for x in spline['knots']]
        variants.append(knot)
        for changed in variants:
            self.rejected(proof, changed)
            forged = copy.deepcopy(proof); forged['source_lowering'] = m.v52.lower_source(changed)
            forged['source_binding_sha256'] = forged['source_lowering']['source_binding_sha256']
            self.rejected(forged, changed)
        degree = source.mutate(spec, ['cos_splines', '0', 'degree'], True)
        self.rejected(proof, degree)
        renamed = copy.deepcopy(spec); renamed['sin_splines']['3'] = renamed['sin_splines'].pop('2')
        self.rejected(proof, renamed)

    def test_typed_invalid_unknown_ignored_and_single_span_predecessor_dispositions(self):
        spec = candidate()
        variants = [source.mutate(spec, ['phase_turn_rate'], True),
                    source.mutate(spec, ['phase_turn_rate'], 0.25),
                    source.mutate(spec, ['cos_splines', '0', 'degree'], True)]
        for key, value in (('epsilon', '1/100'), ('second_phase_law', {}),
                           ('derivative_certificate', {}), ('root_count', 0), ('v53_certificate', {})):
            bad = copy.deepcopy(spec); bad[key] = value; variants.append(bad)
        for bad in variants:
            try:
                prior = m.v52.build_piecewise_source_evidence(bad)
            except (ValueError, TypeError, KeyError) as exc:
                with self.assertRaises(type(exc)):
                    m.build_mixed_source_evidence(bad)
            else:
                self.assertEqual(a._json(m.build_mixed_source_evidence(bad)), a._json(prior))
        for piece in (core.anchor(), source.physical_piece(source.power([-1, 0, 2], 2)), ({0: [0]}, {})):
            single = source.encode([piece])
            self.assertEqual(a._json(m.build_mixed_source_evidence(single)), a._json(m.v52.build_piecewise_source_evidence(single)))
        unsupported = source.encode([({0: [1]}, {}), ({0: [1]}, {})])
        prior = m.v52.build_piecewise_source_evidence(unsupported)
        result = m.build_mixed_source_evidence(unsupported)
        self.assertEqual(result['reason'], 'SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE')
        self.assertEqual(result['predecessor_result'], prior)

    def test_exact_resources_at_each_new_stage_keep_predecessor_and_errors_propagate(self):
        spec, prior, result = acceptance(); proof = result['certificate']
        for module, name in ((m.v52, 'lower_source'), (m, 'check_views'), (m.v52, 'knot_continuity'), (m, 'assemble')):
            for error in (MemoryError, OverflowError, RecursionError):
                with self.subTest(name=name, error=error), patch.object(module, name, side_effect=error):
                    for failed in (m.build_mixed_certificate(spec, proof['span_proofs']),
                                   checker.validate_mixed_certificate(proof, spec)):
                        self.assertEqual(failed['status'], 'RESOURCE_REFUSAL')
                        self.assertIs(failed['is_truth_value'], False)
            with patch.object(module, name, side_effect=RuntimeError('unrelated bug')):
                with self.assertRaises(RuntimeError):
                    checker.validate_mixed_certificate(proof, spec)
        for module, name in ((m.v52, 'lower_source'), (m, 'build_ordered_span_view'),
                             (m.v52, 'knot_continuity'), (m, 'assemble')):
            with patch.object(m.v52, 'build_piecewise_source_evidence', return_value=prior), \
                 patch.object(module, name, side_effect=MemoryError):
                failed = m.build_mixed_source_evidence(spec)
                self.assertEqual(failed['status'], 'RESOURCE_REFUSAL')
                self.assertIs(failed['is_truth_value'], False)
                self.assertEqual(failed['predecessor_result'], prior)
        with patch.object(m.v52, 'build_joins', return_value=m.refusal('finite-equality-budget')):
            self.assertEqual(checker.validate_mixed_certificate(proof, spec)['status'], 'RESOURCE_REFUSAL')
        with patch.object(m.v52, 'build_piecewise_source_evidence', side_effect=RuntimeError('unrelated')):
            with self.assertRaises(RuntimeError):
                m.build_mixed_source_evidence(spec)


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MixedSourceTests))
    if not result.wasSuccessful():
        raise AssertionError('v53 original-source integration controls failed')


if __name__ == '__main__':
    run()
