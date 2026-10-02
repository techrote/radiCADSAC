#!/usr/bin/env python3
"""Direct finite owner/view controls, using actual historical route producers."""
from contextlib import ExitStack, contextmanager
from fractions import Fraction as Q
from pathlib import Path
import copy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_mixed_owner_span_model as m
import pb00701_mixed_owner_span_certificate as checker
import test_pb00701_piecewise_product as source

a, b = m.a, m.b
OWNERS = {version: owner for owner, version in m.v50.OWNERS.items()}


def anchor(constant=-Q(1, 2), slope=1):
    return ({0: [Q(constant), Q(slope)], 1: [Q(1, 100)]}, {2: [Q(1, 200)]})


def scale_piece(piece, scale):
    return tuple({h: a.pscale(poly, scale) for h, poly in mapping.items()} for mapping in piece)


def strict_args(version=19, constant=-Q(1, 2)):
    if version == 19:
        return (*anchor(constant), 'v53-strict-19', ('0', '1'), '0', '1/4')
    if version == 49:
        from test_pb00701_mixed_boundary import candidate_args
        return candidate_args()
    assert version in (47, 48)
    A, B = [Q(-1, 8), Q(1, 2), Q(1, 10000)], [Q(-7, 40), Q(7, 20)]
    rotated = A if version == 47 else a.pmul(A, [0, 1])
    return ({1: a.padd(rotated, B), 2: [Q(1, 10**8)]},
            {1: a.padd(rotated, a.pscale(B, -1))},
            'v53-strict-' + str(version), ('0', '1'), '-1/8', '1/16')


def strict_view(args, expected_owner=None):
    material = a._material(*args)
    actual = m.v50.carrier_proof(material)
    assert actual['status'] == 'CARRIER_CERTIFIED', actual.get('reason')
    if expected_owner is not None:
        assert actual['owner'] == expected_owner, actual['owner']
    view = m.build_ordered_span_view('STRICT_SPAN', actual['owner'], actual['route'], *args)
    assert view['status'] == 'ORDERED_SPAN_VIEW_CERTIFIED', view.get('reason')
    assert checker.validate_ordered_span_view(view, *args) is True
    assert b.same(view['underlying_witness'], actual['route'])
    return view


@contextmanager
def no_search():
    import pb00701_mixed_multicut_model as v49
    import pb00701_mixed_orientation_consumer as v48
    import pb00701_algebraic_monotone_cut_model as v47
    import pb00701_coupled_bspline_model as v7
    import pb00701_multiharmonic_monotone_anchor_model as v19
    guarded = [(m, 'build_mixed_source_evidence'), (m, 'build_mixed_certificate'),
               (m, 'build_ordered_span_view'), (m.v52, 'build_piecewise_source_evidence'),
               (m.v52, 'build_piecewise_certificate'), (m.v51, 'build_ordered_source_evidence'),
               (m.v51, 'build_ordered_product_event'), (m.v50, 'classify_required_analytic_event'),
               (m.v50, 'carrier_proof'), (v49, 'classify_required_analytic_event'),
               (v48, 'classify_required_analytic_event'), (v47, 'classify_required_analytic_event'),
               (v19, 'classify_required_analytic_event'), (v7, 'classify_required_analytic_event'),
               (v49.b, 'certify_derivative'), (v47, 'certify_derivative'),
               (m.v51, '_decide_factor_sign'), (m.v51.e, '_decide_endpoint')]
    with ExitStack() as stack:
        for module, name in guarded:
            stack.enter_context(patch.object(module, name, side_effect=AssertionError('replacement search: ' + name)))
        yield


class StrictViewTests(unittest.TestCase):
    def rejected(self, candidate, args):
        with self.assertRaises((ValueError, TypeError, KeyError, AssertionError)):
            checker.validate_ordered_span_view(candidate, *args)

    def test_all_four_actual_owners_and_complete_child_directions_without_search(self):
        for version in (19, 47, 48, 49):
            with self.subTest(version=version):
                args = strict_args(version)
                view = strict_view(args, OWNERS[version])
                self.assertEqual(m.v50.amplitude_gcd(*m.v50.maps(view['source_material'])), [1])
                self.assertEqual(view['kind'], 'STRICT_SPAN')
                self.assertFalse(view['strict_evidence']['nonconstant_factor_claimed'])
                direction = view['strict_evidence']['complete_derivative']
                proofs = direction['closed_derivative_witnesses']
                self.assertEqual(len(proofs), {19: 1, 47: 2, 48: 2, 49: 4}[version])
                self.assertEqual({w['sign'] for w in proofs}, {direction['delta']})
                with no_search():
                    self.assertIs(checker.validate_ordered_span_view(view, *args), True)
                if version != 19:
                    for index in range(len(proofs)):
                        bad = copy.deepcopy(view)
                        child = bad['underlying_witness']['children'][index]
                        child['derivative_certificate']['derivative_sign'] *= -1
                        child['summary']['derivative_sign'] *= -1
                        self.rejected(bad, args)

    def test_open_free_and_both_endpoint_roots_in_both_directions(self):
        for constant, location in ((-Q(1, 2), 'open'), (Q(1, 2), 'none'),
                                   (-Q(1, 100), 'left'), (-Q(1), 'right')):
            for sign in (-1, 1):
                with self.subTest(location=location, sign=sign):
                    args = strict_args(19, constant)
                    args = (*scale_piece(args[:2], sign), *args[2:])
                    view = strict_view(args, OWNERS[19])
                    evidence = view['strict_evidence']
                    self.assertEqual(evidence['complete_derivative']['delta'], sign)
                    summary = view['physical_root_summary']
                    self.assertEqual(summary['distinct_roots_open'], int(location == 'open'))
                    self.assertEqual(summary['endpoint_root_multiplicity'],
                                     {location: 1} if location in ('left', 'right') else {})
                    self.assertEqual(len(view['sign_cells']), 2 if location == 'open' else 1)
                    self.assertEqual([c['physical_sign'] for c in view['sign_cells']],
                                     [-sign, sign] if location == 'open' else
                                     [sign if location in ('left', 'none') else -sign])
                    descriptor = evidence['implicit_root_descriptor']
                    if location == 'open':
                        self.assertEqual(descriptor['arithmetic_nature'], 'UNCLAIMED')
                        self.assertIsNone(descriptor['algebraic_minimal_polynomial'])
                        self.assertEqual(descriptor['endpoint_signs'], [-sign, sign])
                    else:
                        self.assertIsNone(descriptor)

    def test_source_bound_implicit_even_when_the_root_is_exactly_rational(self):
        # At t=1/2 the two equal cosine channels at turns 1/8 and 3/8 cancel.
        args = ({0: [-Q(1, 2), 1], 1: [Q(1, 100)], 3: [Q(1, 100)]}, {},
                'rational-but-implicit', ('0', '1'), '0', '1/4')
        view = strict_view(args, OWNERS[19])
        self.assertEqual(m.v50.rational_event(view['source_material'], Q(1, 2))['relation'], 'ZERO')
        root = view['ordered_physical_events'][0]['position']
        self.assertEqual(root['kind'], 'UNIQUE_ANALYTIC_ROOT')
        self.assertIsNone(root['algebraic_minimal_polynomial'])
        self.assertNotIn('value', root)
        self.assertEqual(root['arithmetic_nature'], 'UNCLAIMED')

    def test_owner_route_derivative_simplicity_and_normalized_view_forgery(self):
        args = strict_args()
        view = strict_view(args)
        changes = [(['owner'], OWNERS[47]), (['kind'], 'V51_PRODUCT'),
                   (['underlying_witness', 'all_roots_simple'], False),
                   (['underlying_witness', 'derivative_certificate', 'direction'], 'DECREASING'),
                   (['strict_evidence', 'complete_derivative', 'delta'], -1),
                   (['strict_evidence', 'implicit_root_descriptor', 'arithmetic_nature'], 'ALGEBRAIC'),
                   (['ordered_boundaries', 1, 'physical_multiplicity'], 2),
                   (['physical_root_summary', 'distinct_roots_open'], True),
                   (['sign_cells', 0, 'physical_sign'], 1),
                   (['ordered_boundaries', 0, 'physical_relation'], 'POSITIVE'),
                   (['parent_map', 'positive_scale'], '2'),
                   (['source_binding_sha256'], '0' * 64)]
        for path, value in changes:
            with self.subTest(path=path):
                self.rejected(source.mutate(view, path, value), args)
        other = strict_view(strict_args(19, Q(1, 2)))
        bad = copy.deepcopy(view); bad['underlying_witness'] = other['underlying_witness']
        self.rejected(bad, args)
        bad = copy.deepcopy(view); del bad['underlying_witness']
        self.rejected(bad, args)
        bad = copy.deepcopy(view); bad['trusted_summary'] = True
        self.rejected(bad, args)

    def test_original_channels_phase_map_and_id_cannot_be_substituted(self):
        args = strict_args()
        view = strict_view(args)
        for index, replacement in ((0, {0: [-Q(1, 3), 1], 1: [Q(1, 100)]}),
                                   (1, {2: [Q(1, 201)]}), (2, 'other'),
                                   (3, ('2', '5')), (4, '1/8'), (5, '1/5')):
            altered = list(args); altered[index] = replacement
            self.rejected(view, altered)
        transformed = (*args[:2], args[2], ('2', '5'), '-1/6', '1/12')
        mapped = strict_view(transformed)
        self.assertEqual(mapped['parent_map'], {'offset': '2', 'positive_scale': '3'})
        self.assertNotEqual(mapped['source_binding_sha256'], view['source_binding_sha256'])
        self.assertEqual(mapped['physical_root_summary'], view['physical_root_summary'])

    def test_no_fake_unit_factor_product_or_unsupported_strict_owner(self):
        args = strict_args()
        view = strict_view(args)
        self.assertEqual(m.v50.factor_source(*args)['reason'], 'CONSTANT_AMPLITUDE_GCD')
        for owner in ('PB00701_V50_VANISHING_SOURCE_FACTOR', 'UNKNOWN', OWNERS[48]):
            self.rejected(source.mutate(view, ['owner'], owner), args)
        bad = copy.deepcopy(view); bad['kind'] = 'V51_PRODUCT'; bad['owner'] = m.v51.V50_OWNER
        bad['underlying_witness'] = {'physical_event_result': {'factorization': {'monic_factor': ['1']}}}
        self.rejected(bad, args)

    def test_owner_and_endpoint_resource_nontruth_and_unrelated_errors(self):
        args = strict_args(); view = strict_view(args)
        for module, name in ((m.v50, 'validate_carrier'), (m.v50, 'rational_event'),
                             (m.v51, 'carrier_direction')):
            for error in (MemoryError, OverflowError, RecursionError):
                with self.subTest(name=name, error=error), patch.object(module, name, side_effect=error):
                    for result in (m.build_ordered_span_view('STRICT_SPAN', view['owner'], view['underlying_witness'], *args),
                                   checker.validate_ordered_span_view(view, *args)):
                        self.assertEqual(result['status'], 'RESOURCE_REFUSAL')
                        self.assertIs(result['is_truth_value'], False)
            with patch.object(module, name, side_effect=RuntimeError('programming error')):
                with self.assertRaises(RuntimeError):
                    checker.validate_ordered_span_view(view, *args)


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(StrictViewTests))
    if not result.wasSuccessful():
        raise AssertionError('v53 strict owner/view controls failed')


if __name__ == '__main__':
    run()
