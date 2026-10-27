#!/usr/bin/env python3
"""Direct V54 owner-adapter controls using actual historical owner witnesses.

Every category-2 owner is exercised on frozen admitted spans whose route is
produced by the owner's own unchanged recipe. Forgery, cross-owner substitution,
mutation and replacement-search controls must fail closed.
"""
from contextlib import ExitStack, contextmanager
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import copy
import json
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_finite_owner_span_model as m
import pb00701_finite_owner_span_certificate as checker
import pb00701_finite_owner_inventory as inventory

a, b = m.a, m.b
BAD = (ValueError, TypeError, KeyError, AssertionError, AttributeError, IndexError)
SLOW_RECIPES = {'PB00701_V21_EXACT_SIGN_ORTHANT_L1_DERIVATIVE_ENVELOPE'}


@lru_cache(maxsize=1)
def corpus():
    return inventory.load_corpus()


def args_of(record):
    return ({int(h): [Q(x) for x in p] for h, p in record['cos'].items()},
            {int(h): [Q(x) for x in p] for h, p in record['sin'].items()},
            record['id'], tuple(record['interval']), record['offset'], record['rate'])


def fixtures(owner):
    return [(row['shape'], args_of(row)) for row in corpus()['fixtures'][owner]]


def kind_of(owner):
    return 'SIGN_SPAN' if owner in m.SIGN_ADAPTERS else 'OWNER_STRICT_SPAN'


@lru_cache(maxsize=None)
def _view(owner, index):
    shape, args = fixtures(owner)[index]
    route = m.regenerate_owner_route(owner, a._material(*args))
    assert route is not None and route['status'] == 'CERTIFIED', owner
    view = m.build_ordered_span_view(kind_of(owner), owner, route, *args)
    assert view['status'] == 'ORDERED_SPAN_VIEW_CERTIFIED', (owner, view.get('reason'))
    return json.dumps(view), args


def view(owner, index=0):
    text, args = _view(owner, index)
    return json.loads(text), args


def dominance_args(constant=Q(1), slope=Q(1, 10), osc=Q(1, 10), ident='v54-dominance', interval=('0', '1'),
                   offset='1/3', rate='1/4'):
    return ({0: [Q(constant), Q(slope)], 1: [Q(osc)]}, {2: [Q(osc)]}, ident, interval, offset, rate)


@contextmanager
def no_search():
    """Disable every classifier/builder/selector; finite checking must not need them."""
    # Each test is independently runnable: do not rely on prior fixtures having
    # imported every historical owner module before their selectors are guarded.
    for entry in m.STRICT_ADAPTERS.values():
        __import__(entry['module'])
    with ExitStack() as stack:
        for name, module in list(sys.modules.items()):
            if not name.startswith('pb00701_') or module is None:
                continue
            for attr in ('classify_required_analytic_event', 'analyze_coupled_bspline_event',
                         'build_mixed_source_evidence', 'build_mixed_certificate', 'build_ordered_span_view',
                         'build_piecewise_source_evidence', 'build_piecewise_certificate',
                         'build_ordered_source_evidence', 'build_ordered_product_event', 'carrier_proof',
                         'build_finite_owner_source_evidence', 'build_finite_owner_certificate',
                         'certify_derivative', '_decide_factor_sign', '_delegate_carrier', '_delegate_residual'):
                if hasattr(module, attr):
                    stack.enter_context(patch.object(module, attr,
                                                     side_effect=AssertionError('replacement search: ' + attr)))
        # Crucially disable each historical route's *internal* candidate loop.
        # Checking must use the selected leaf from the supplied certificate.
        for owner, entry in m.STRICT_ADAPTERS.items():
            module = sys.modules[entry['module']]
            stack.enter_context(patch.object(
                module, entry['recipe'],
                side_effect=AssertionError('historical anchor selection: ' + entry['recipe'])))
        yield


class SignSpanTests(unittest.TestCase):
    def rejected(self, candidate, args):
        with self.assertRaises(BAD):
            outcome = checker.validate_ordered_span_view(candidate, *args)
            self.assertIs(outcome, True)

    def test_positive_and_negative_dominance_are_root_free_sign_spans_not_derivatives(self):
        for sign in (1, -1):
            args = dominance_args(constant=sign)
            material = a._material(*args)
            route = m.regenerate_owner_route(m.SIGN_OWNER, material)
            self.assertEqual(route['sign'], 'POSITIVE' if sign > 0 else 'NEGATIVE')
            self.assertEqual(route['margin'], '7/10')
            view = m.build_ordered_span_view('SIGN_SPAN', m.SIGN_OWNER, route, *args)
            self.assertIs(checker.validate_ordered_span_view(view, *args), True)
            self.assertEqual(view['owner'], 'EXACT_RATIONAL_AMPLITUDE_DOMINANCE')
            self.assertEqual(view['owner_version'], 7)
            self.assertEqual([c['physical_sign'] for c in view['sign_cells']], [sign])
            self.assertEqual([p['physical_relation'] for p in view['ordered_boundaries']],
                             ['POSITIVE' if sign > 0 else 'NEGATIVE'] * 2)
            self.assertEqual([p['inward_sign'] for p in view['ordered_boundaries']], [sign, sign])
            self.assertEqual(view['physical_root_summary']['total_distinct_roots_closed'], 0)
            evidence = view['sign_evidence']
            self.assertFalse(evidence['derivative_certificate_claimed'])
            self.assertFalse(evidence['monotonicity_claimed'])
            self.assertFalse(evidence['endpoint_roots_possible'])
            self.assertNotIn('strict_evidence', view)
            self.assertNotIn('direction', json.dumps(view))
            self.assertFalse(view['historical_owner_changed'])

    def test_boundary_root_is_impossible_and_nondominated_span_is_refused(self):
        args = dominance_args()
        view = m.build_ordered_span_view('SIGN_SPAN', m.SIGN_OWNER,
                                         m.regenerate_owner_route(m.SIGN_OWNER, a._material(*args)), *args)
        for side in (0, -1):
            bad = copy.deepcopy(view)
            bad['ordered_boundaries'][side]['physical_relation'] = 'ZERO'
            bad['ordered_boundaries'][side]['physical_multiplicity'] = 1
            self.rejected(bad, args)
        # margin exactly zero / negative: the historical recipe itself refuses.
        for constant in (Q(3, 10), Q(1, 5)):
            tight = dominance_args(constant=constant)
            self.assertIsNone(m.regenerate_owner_route(m.SIGN_OWNER, a._material(*tight)))
            with self.assertRaises(BAD):
                m.build_ordered_span_view('SIGN_SPAN', m.SIGN_OWNER, view['underlying_witness'], *tight)

    def test_forged_route_owner_kind_derivative_and_field_types_are_rejected(self):
        args = dominance_args()
        good = m.regenerate_owner_route(m.SIGN_OWNER, a._material(*args))
        forged = []
        for key, value in (('sign', 'NEGATIVE'), ('margin', '1'), ('margin', 0.7), ('sign', True),
                           ('distinct_roots_open', 1), ('distinct_roots_open', False),
                           ('direction', 'INCREASING'), ('monotonicity', 'STRICT'), ('unknown', 1)):
            bad = dict(good); bad[key] = value; forged.append(bad)
        bad = dict(good); del bad['margin']; forged.append(bad)
        for route in forged:
            with self.assertRaises(BAD):
                m.build_ordered_span_view('SIGN_SPAN', m.SIGN_OWNER, route, *args)
        for kind, owner in (('OWNER_STRICT_SPAN', m.SIGN_OWNER), ('STRICT_SPAN', m.SIGN_OWNER),
                            ('SIGN_SPAN', 'PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR'),
                            ('SIGN_SPAN', 'PB00701_V20_EXACT_POINTWISE_DERIVATIVE_ENVELOPE'),
                            ('V51_PRODUCT', m.SIGN_OWNER), ('UNKNOWN', m.SIGN_OWNER)):
            with self.assertRaises(BAD):
                m.regenerate_view(kind, owner, good, *args) if kind not in m.V53_KINDS else \
                    m.v53.regenerate_view(kind, owner, good, *args)
        view = m.build_ordered_span_view('SIGN_SPAN', m.SIGN_OWNER, good, *args)
        for path, value in ((['owner'], 'PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR'),
                            (['kind'], 'OWNER_STRICT_SPAN'), (['kind'], 'STRICT_SPAN'), (['adapter'], 'X'),
                            (['owner_version'], 19), (['owner_version'], 7.0),
                            (['historical_owner_changed'], True), (['normalized_view_alone_is_authority'], True),
                            (['sign_evidence', 'monotonicity_claimed'], True),
                            (['sign_evidence', 'derivative_certificate_claimed'], 1),
                            (['sign_cells', 0, 'physical_sign'], -1), (['parent_map', 'positive_scale'], '2'),
                            (['ordered_boundaries', 0, 'inward_sign'], True),
                            (['physical_root_summary', 'distinct_roots_open'], 1), (['unknown_authority'], True)):
            bad = copy.deepcopy(view)
            target = bad
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            self.rejected(bad, args)

    def test_source_phase_harmonic_identity_and_interval_mutation_are_rejected(self):
        args = dominance_args()
        good = m.build_ordered_span_view('SIGN_SPAN', m.SIGN_OWNER,
                                         m.regenerate_owner_route(m.SIGN_OWNER, a._material(*args)), *args)
        mutated = [dominance_args(constant=Q(2)), dominance_args(osc=Q(1, 20)),
                   dominance_args(ident='other-source'), dominance_args(interval=('0', '2')),
                   dominance_args(offset='1/5'), dominance_args(rate='1/3'),
                   ({0: [Q(1), Q(1, 10)], 3: [Q(1, 10)]}, {2: [Q(1, 10)]}, 'v54-dominance', ('0', '1'), '1/3', '1/4')]
        for other in mutated:
            self.rejected(good, other)


class OwnerStrictTests(unittest.TestCase):
    def test_every_strict_owner_regenerates_from_its_own_recipe_and_retains_identity(self):
        shapes = set()
        for owner, entry in sorted(m.STRICT_ADAPTERS.items()):
            for index, (shape, args) in enumerate(fixtures(owner)):
                v, args = view(owner, index)
                self.assertIs(checker.validate_ordered_span_view(v, *args), True, owner)
                self.assertEqual((v['owner'], v['kind'], v['owner_version'], v['adapter']),
                                 (owner, 'OWNER_STRICT_SPAN', entry['version'], entry['adapter']))
                summary = v['physical_root_summary']
                self.assertEqual(shape, '%d/%d' % (summary['distinct_roots_open'],
                                                  summary['total_distinct_roots_closed']), owner)
                self.assertTrue(summary['all_roots_simple'])
                direction = v['strict_evidence']['complete_derivative']
                certificate = v['underlying_witness'][entry['direction_certificate']]
                self.assertEqual(direction['delta'], 1 if certificate['direction'] == 'INCREASING' else -1)
                if summary['distinct_roots_open']:
                    self.assertEqual(v['ordered_boundaries'][1]['adjacent_cell_signs'],
                                     [-direction['delta'], direction['delta']])
                for side, point in zip(('left', 'right'), (v['ordered_boundaries'][0], v['ordered_boundaries'][-1])):
                    if point['physical_relation'] == 'ZERO':
                        # Justified endpoint root: simple, inward sign from owned direction.
                        self.assertEqual(point['physical_multiplicity'], 1)
                        self.assertEqual(point['inward_sign'], direction['delta'] if side == 'left' else -direction['delta'])
                        self.assertEqual(summary['endpoint_root_multiplicity'], {side: 1})
                shapes.add(shape)
        self.assertEqual(shapes, {'0/0', '0/1', '1/1'})

    def test_forged_direction_events_roots_and_cross_owner_substitution(self):
        owners = sorted(m.STRICT_ADAPTERS)
        for i, owner in enumerate(owners):
            v, args = view(owner)
            route = v['underlying_witness']
            key = m.STRICT_ADAPTERS[owner]['direction_certificate']
            forged = []
            bad = copy.deepcopy(route)
            bad[key]['direction'] = {'INCREASING': 'DECREASING', 'DECREASING': 'INCREASING'}[bad[key]['direction']]
            forged.append(bad)
            for field, value in (('distinct_roots_open', 2), ('all_roots_simple', 1), ('multiple_roots_open', 1),
                                 ('left_event', route['right_event']), ('status', 'BLOCKED'), ('monotone', True)):
                bad = copy.deepcopy(route); bad[field] = value; forged.append(bad)
            if owner in SLOW_RECIPES:
                forged = forged[:2]  # each forgery costs one full owner-recipe regeneration
            for bad in forged:
                with self.assertRaises(BAD):
                    m.build_ordered_span_view('OWNER_STRICT_SPAN', owner, bad, *args)
            other = owners[(i + 1) % len(owners)]
            with self.assertRaises(BAD):
                m.build_ordered_span_view('OWNER_STRICT_SPAN', other, route, *args)
            for kind, own in (('SIGN_SPAN', owner), ('STRICT_SPAN', owner), ('V51_PRODUCT', owner)):
                with self.assertRaises(BAD):
                    m.build_ordered_span_view(kind, own, route, *args)
            paths = ((['owner'], other), (['strict_evidence', 'complete_derivative', 'delta'], 0),
                     (['adapter'], 'V54_V19_WHOLE_SPAN_STRICT_DERIVATIVE'),
                     (['ordered_boundaries', 0, 'physical_relation'], 'ZERO'),
                     (['sign_cells', 0, 'physical_sign'], 0),
                     (['physical_root_summary', 'total_distinct_roots_closed'], 9),
                     (['implicit_root_arithmetic_claimed'], True))
            for path, value in (paths[:2] if owner in SLOW_RECIPES else paths):
                bad = copy.deepcopy(v)
                target = bad
                for k in path[:-1]:
                    target = target[k]
                target[path[-1]] = value
                with self.assertRaises(BAD):
                    self.assertIs(checker.validate_ordered_span_view(bad, *args), True)

    def test_finite_checking_runs_with_classifiers_and_proof_selection_disabled(self):
        prepared = [view(owner) for owner in sorted(m.STRICT_ADAPTERS)]
        args = dominance_args()
        sign_view = m.build_ordered_span_view('SIGN_SPAN', m.SIGN_OWNER,
                                              m.regenerate_owner_route(m.SIGN_OWNER, a._material(*args)), *args)
        with no_search():
            for v, view_args in prepared:
                self.assertIs(checker.validate_ordered_span_view(v, *view_args), True, v['owner'])
            self.assertIs(checker.validate_ordered_span_view(sign_view, *args), True)

    def test_historical_multiharmonic_route_admission_is_checked_without_selection(self):
        import pb00701_finite_owner_witness_check as witness_check
        # Every V20–V30 owner route explicitly requires >=2 active positive
        # harmonics. A selected leaf is not proof that its owner was eligible.
        for owner, entry in sorted(m.STRICT_ADAPTERS.items()):
            if entry['version'] > 30:
                continue
            _, args = fixtures(owner)[0]
            c, s, ident, interval, offset, rate = args
            harmonics = sorted(h for h in set(c) | set(s) if h > 0)
            self.assertGreaterEqual(len(harmonics), 2, owner)
            selected = harmonics[0]
            only_c = {h: p for h, p in c.items() if h in (0, selected)}
            only_s = {h: p for h, p in s.items() if h in (0, selected)}
            source = a._material(only_c, only_s, ident, interval, offset, rate)
            module = __import__(entry['module'])
            # If the leaf runs before admission, this RuntimeError must escape
            # rather than being mistaken for a source eligibility refusal.
            with patch.object(module, witness_check.LEAVES[entry['version']],
                              side_effect=RuntimeError('unchecked owner eligibility')):
                with self.assertRaises(BAD):
                    witness_check.validate_owner_witness(owner, {}, source)

    def test_corrupt_selected_proof_is_not_rescued_by_historical_route_selection(self):
        # Two owners with internal SIN/COS or harmonic searches.
        for version in (25, 43):
            owner = next(k for k, item in m.STRICT_ADAPTERS.items()
                         if item['version'] == version)
            good, args = view(owner)
            with no_search():
                self.assertIs(checker.validate_ordered_span_view(good, *args), True)
                bad = copy.deepcopy(good)
                key = m.STRICT_ADAPTERS[owner]['direction_certificate']
                direction = bad['underlying_witness'][key]['direction']
                bad['underlying_witness'][key]['direction'] = (
                    'DECREASING' if direction == 'INCREASING' else 'INCREASING')
                with self.assertRaises(BAD):
                    checker.validate_ordered_span_view(bad, *args)

    def test_resource_refusal_is_not_truth_and_unrelated_errors_propagate(self):
        owner = 'PB00701_V20_EXACT_POINTWISE_DERIVATIVE_ENVELOPE'
        v, args = view(owner)
        module = sys.modules[m.STRICT_ADAPTERS[owner]['module']]
        recipe = m.STRICT_ADAPTERS[owner]['recipe']
        # The checker must no longer call the old route-level selector.
        selected_leaf = '_pointwise_derivative_envelope_certificate'
        with patch.object(module, selected_leaf, side_effect=MemoryError):
            refused = checker.validate_ordered_span_view(v, *args)
        self.assertEqual(refused['status'], 'RESOURCE_REFUSAL')
        self.assertIs(refused['is_truth_value'], False)
        with patch.object(module, selected_leaf, side_effect=ZeroDivisionError('unrelated')):
            with self.assertRaises(ZeroDivisionError):
                checker.validate_ordered_span_view(v, *args)
        refusal = {'status': 'RESOURCE_REFUSAL', 'reason': 'X', 'is_truth_value': False}
        with patch.object(module, recipe, return_value=refusal):
            self.assertEqual(m.build_ordered_span_view('OWNER_STRICT_SPAN', owner, v['underlying_witness'], *args),
                             refusal)


class InventoryTests(unittest.TestCase):
    def test_every_static_emitter_has_exactly_one_category_and_precise_premise(self):
        data = inventory.inventory()
        self.assertEqual(data['owner_count'], 43)
        self.assertEqual(data['category_counts'], {'1': 5, '2': 20, '3': 16, '4': 2})
        seen = set()
        for row in data['owners']:
            self.assertNotIn(row['owner'], seen)
            seen.add(row['owner'])
            if row['category'] == 3:
                self.assertTrue(row['missing_premise'].isupper() and 'WITHOUT' in row['missing_premise'])
            if row['category'] == 2:
                self.assertTrue(row['adapter'].startswith('V54_V%d_' % row['version']))
        artifact = json.loads((inventory.TASK / 'pb00701-finite-owner-inventory-v54.json').read_text())
        self.assertTrue(b.same(artifact, data))
        with patch.object(m, 'LACKING_PREMISE', {**m.LACKING_PREMISE, m.SIGN_OWNER: (7, 'X')}):
            with self.assertRaises(BAD):
                inventory.inventory()
        with patch.object(m, 'BLOCKED_OWNERS', {}):
            with self.assertRaises(BAD):
                inventory.inventory()


def run():
    suite = unittest.TestSuite()
    for case in (SignSpanTests, OwnerStrictTests, InventoryTests):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(case))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == '__main__':
    run()
