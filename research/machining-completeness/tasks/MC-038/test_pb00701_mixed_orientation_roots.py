#!/usr/bin/env python3
"""Regression tests run against actual pinned v44-v47 repository modules."""
from fractions import Fraction as Q
from pathlib import Path
import copy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_mixed_orientation_roots_model as r
import pb00701_mixed_orientation_consumer as m
import test_pb00701_algebraic_monotone_cut as oldcore
import test_pb00701_algebraic_monotone_cut_integration as oldtest

a, E = r.a, r.E


def mul(*polys):
    p = [Q(1)]
    for factor in polys:
        p = a.pmul(p, factor)
    return p


def candidate():
    c, s, ident, span, off, rate = oldcore.candidate_args()
    A = a.pscale(a.padd(c[1], s[1]), Q(1, 2))
    B = a.pscale(a.padd(c[1], a.pscale(s[1], -1)), Q(1, 2))
    A = mul([0, 1], A)
    return ({**c, 1: a.padd(A, B)}, {**s, 1: a.padd(A, a.pscale(B, -1))},
            'v48-endpoint-factor-source', span, off, rate)


class MixedRootTests(unittest.TestCase):
    def test_both_legacy_failures_are_executed(self):
        cases = ((mul([0, 1], [-1, 0, 2]), 'Sturm open interval endpoint is an exact root'),
                 (mul([Q(-3, 5), 1], [-1, 0, 2]), 'multiplicity interval is not source-root unique'))
        for p, reason in cases:
            with self.subTest(reason=reason), self.assertRaises(ValueError) as failure:
                r.old.exact_algebraic_orientation_roots(p, 'legacy')
            self.assertEqual(str(failure.exception), reason)
            fixed = r.exact_orientation_roots(p, 'legacy')
            self.assertEqual(fixed['status'], 'CERTIFIED')
            self.assertEqual(len(fixed['irrational_open_roots']), 1)
            self.assertIs(r.validate_orientation_roots(fixed, p, 'legacy'), True)
            self.assertEqual(fixed['source_polynomial'], [str(x) for x in p])

    def test_endpoint_multiplicities_and_full_counts(self):
        for factors, endpoint_counts, irrational_m in (
            (([0, 1], [-1, 0, 2]), {'0': 1}, 1),
            (([-1, 1], [-1, 0, 2]), {'1': 1}, 1),
            (([0, 1], [-1, 1], [-1, 0, 2]), {'0': 1, '1': 1}, 1),
            (([0, 0, 1], [-1, 1], [-1, 1], [-1, 1], [-1, 0, 2], [-1, 0, 2]), {'0': 2, '1': 3}, 2),
        ):
            p = mul(*factors)
            out = r.exact_orientation_roots(p, 'endpoints')
            self.assertEqual(out['status'], 'CERTIFIED')
            self.assertEqual({x['source']: x['multiplicity'] for x in out['endpoint_roots']}, endpoint_counts)
            self.assertEqual(out['distinct_roots_open'], 1)
            self.assertEqual(out['distinct_roots_closed'], 1 + len(endpoint_counts))
            cert = out['irrational_open_roots'][0]
            self.assertEqual(cert['multiplicity'], irrational_m)
            self.assertEqual(a.RealField.from_source_certificate(p, cert).minimal, (-1, 0, 2))

    def test_rational_removed_root_inside_or_on_isolation_boundary(self):
        for rational in (Q(1, 2), Q(3, 4), Q(3, 5), Q(707106, 1000000), Q(707107, 1000000)):
            p = mul([-rational, 1], [-rational, 1], [-1, 0, 2])
            out = r.exact_orientation_roots(p, 'mixed')
            self.assertEqual(out['rational_open_roots'], [{'source': str(rational), 'multiplicity': 2}])
            self.assertEqual(out['distinct_roots_open'], 2)
            cert = out['irrational_open_roots'][0]
            lo, hi = map(Q, cert['isolating_interval'])
            self.assertFalse(lo <= rational <= hi)
            self.assertNotEqual(E.peval(p, lo), 0)
            self.assertNotEqual(E.peval(p, hi), 0)
            self.assertEqual(E.distinct_roots_open(p, lo, hi), 1)

    def test_rational_only_constant_and_identity(self):
        for p, count in (([4], 0), (mul([0, 1], [-1, 1]), 0), (mul([0, 1], [-Q(1, 2), 1], [-1, 1]), 1)):
            out = r.exact_orientation_roots(p, 'rational')
            self.assertEqual(out['status'], 'CERTIFIED')
            self.assertEqual(out['distinct_roots_open'], count)
            self.assertEqual(out['irrational_open_roots'], [])
        self.assertEqual(r.exact_orientation_roots([0], 'zero')['status'], 'BLOCKED')

    def test_AB_deduplication_and_nearby_algebraic_order(self):
        p = mul([0, 1], [-Q(3, 5), 1], [-1, 0, 2])
        cuts = r.exact_orientation_cuts({1: a.pscale(p, 3)}, {1: a.pscale(p, -1)})
        self.assertEqual(len(cuts['canonical_irrational_cuts']), 1)
        self.assertEqual({x['coordinate'] for x in cuts['canonical_irrational_cuts'][0]['ownership']}, {'A', 'B'})
        A, B = mul([0, 1], [-4999, 0, 10000]), mul([-1, 1], [-5001, 0, 10000])
        cuts = r.exact_orientation_cuts({1: a.padd(A, B)}, {1: a.padd(A, a.pscale(B, -1))})
        self.assertEqual(len(cuts['canonical_irrational_cuts']), 2)
        self.assertEqual(cuts['pairwise_exact_order'][0]['relation'], 'STRICTLY_LESS')

    def test_root_metadata_corruption_and_false_accounting(self):
        p = mul([0, 1], [-Q(3, 5), 1], [-1, 0, 2])
        good = r.exact_orientation_roots(p, 'bound')
        mutations = [(['all_roots_accounted_exactly'], False), (['distinct_roots_open'], True),
                     (['endpoint_roots'], []), (['rational_open_roots'], []),
                     (['irrational_open_roots', 0, 'multiplicity'], True),
                     (['irrational_open_roots', 0, 'defining_square_free_polynomial'], [-1, 0, 3]),
                     (['irrational_open_roots', 0, 'isolating_interval'], ['1/2', '3/4']),
                     (['source_polynomial'], ['0']), (['physical_source_deflated'], True)]
        for path, value in mutations:
            bad = copy.deepcopy(good); node = bad
            for key in path[:-1]: node = node[key]
            node[path[-1]] = value
            with self.subTest(path=path), self.assertRaises(ValueError): r.validate_orientation_roots(bad, p, 'bound')
        for bad in ([0.0, -1, 0, 2], [True, 1]):
            with self.assertRaises((ValueError, TypeError)): r.exact_orientation_roots(bad, 'nonexact')
        with patch.object(r.old, '_isolate_irrational_roots', return_value=[]):
            with self.assertRaisesRegex(ValueError, 'accounting'): r.exact_orientation_roots([-1, 0, 2], 'omitted')

    def test_actual_source_restored_without_changing_derivative_theorems(self):
        args = candidate(); spec = oldtest.source(args)
        with self.assertRaises(ValueError) as exc: m.prior.classify_required_analytic_event(spec)
        self.assertIn(str(exc.exception), m.LEGACY_ROOT_ERRORS)
        result = m.classify_required_analytic_event(spec)
        self.assertEqual(result['status'], 'CERTIFIED', result)
        proof = next(x['route'] for x in result['spans'] if x.get('route_kind') == 'PB00701_V48_MIXED_ROOT_SINGLE_CUT')
        self.assertEqual([c['derivative_certificate']['mode'] for c in proof['children']], ['V42', 'V43'])
        self.assertEqual(proof['distinct_roots_open'], 1)
        self.assertEqual(proof['internal_cut_roots'], [])
        self.assertEqual(proof['source_material']['cos_polynomials']['2'], [str(x) for x in args[0][2]])
        self.assertIs(m.validate_single_cut_event(proof, *args), True)
        print('v48: legacy endpoint-factor exception -> checked V42-left/V43-right single-cut event')

    def test_rates_global_source_and_previous_success_precedence(self):
        args = candidate()
        for reverse, global_span in ((True, False), (False, True)):
            c, s, ident, span, off, rate = args; off, rate = Q(off), Q(rate)
            if reverse:
                c = {h: oldtest.reverse_poly(p) for h, p in c.items()}
                s = {h: oldtest.reverse_poly(p) for h, p in s.items()}
                off, rate = off + rate, -rate
            if global_span:
                span, off, rate = ('2', '5'), off - rate * Q(2, 3), rate / 3
            values = (c, s, ident, span, str(off), str(rate))
            proof = m.build_single_cut_event(*values)
            self.assertEqual(proof['status'], 'CERTIFIED', proof)
            self.assertIs(m.validate_single_cut_event(proof, *values), True)
            self.assertEqual(proof['children'][0]['summary']['derivative_sign'], -1 if reverse else 1)
        oldspec = oldtest.source(oldcore.candidate_args())
        baseline = m.prior.classify_required_analytic_event(oldspec)
        self.assertEqual(baseline['status'], 'CERTIFIED')
        with patch.object(m, 'build_single_cut_event', side_effect=AssertionError('do not relabel')):
            self.assertEqual(m.classify_required_analytic_event(oldspec), baseline)

    def test_consumer_corruption_and_checker_does_not_search(self):
        args = candidate(); proof = m.build_single_cut_event(*args)
        for path, value in ((['source_parameter_id'], 'forged'),
                            (['mixed_root_certificate', 'source_root_records'], []),
                            (['bisection', 'children', 0, 'parent_local_map', 'width'], ['1/4']),
                            (['children', 0, 'derivative_certificate', 'orthants'], []),
                            (['endpoint_evidence', 1, 'relation'], 'ZERO'),
                            (['distinct_roots_open'], 0)):
            bad = copy.deepcopy(proof); node = bad
            for key in path[:-1]: node = node[key]
            node[path[-1]] = value
            with self.subTest(path=path), self.assertRaises((ValueError, KeyError)): m.validate_single_cut_event(bad, *args)
        altered = list(args); altered[2] = 'other-source'
        with self.assertRaises(ValueError): m.validate_single_cut_event(proof, *altered)
        with patch.object(m.prior, 'certify_derivative', side_effect=AssertionError('no route search')), patch.object(m.endpoint, '_decide_endpoint', side_effect=AssertionError('no sign search')):
            self.assertIs(m.validate_single_cut_event(proof, *args), True)
        badargs = list(args); badargs[0] = {**args[0], 0: [0, 10]}
        self.assertNotEqual(m.build_single_cut_event(*badargs)['status'], 'CERTIFIED')

    def test_fail_closed_input_and_exception_routing(self):
        spec = oldtest.source(candidate())
        for key, value in (('v48_certificate', {}), ('epsilon', '1/10'), ('second_phase_law', {})):
            forged = {**spec, key: value}
            before = m.prior.classify_required_analytic_event(forged)
            self.assertNotEqual(before['status'], 'CERTIFIED')
            self.assertEqual(m.classify_required_analytic_event(forged), before)
        with patch.object(m.prior, 'classify_required_analytic_event', side_effect=ValueError('unrelated defect')):
            with self.assertRaisesRegex(ValueError, 'unrelated'): m.classify_required_analytic_event(spec)
        reject = {'status': 'SEMANTIC_BLOCKER', 'reason': 'source mismatch'}
        with patch.object(m.prior, 'classify_required_analytic_event', side_effect=ValueError(next(iter(m.LEGACY_ROOT_ERRORS)))), patch.object(r.old.v41, 'classify_required_analytic_event', return_value=reject):
            self.assertEqual(m.classify_required_analytic_event(spec), reject)
        for key, value in (('phase_turn_rate', 0.0625), ('source_parameter_id', False)):
            try: out = m.classify_required_analytic_event({**spec, key: value})
            except (ValueError, TypeError, AssertionError): continue
            self.assertNotEqual(out['status'], 'CERTIFIED')

    def test_resources_are_not_truth(self):
        for owner, name in ((r.old, '_isolate_irrational_roots'), (r, 'full_source_interval'),
                            (a.RealField, 'from_source_certificate')):
            with patch.object(owner, name, side_effect=MemoryError('injected')):
                out = r.exact_orientation_roots(mul([0, 1], [-1, 0, 2]), 'refused')
                self.assertEqual(out['status'], 'RESOURCE_REFUSAL'); self.assertFalse(out['is_truth_value'])
        for owner, name in ((a, '_bisection'), (m.prior, 'certify_derivative'),
                            (m.endpoint, '_decide_endpoint'), (m, '_finish')):
            with patch.object(owner, name, side_effect=MemoryError('injected')):
                out = m.build_single_cut_event(*candidate())
                self.assertEqual(out['status'], 'RESOURCE_REFUSAL'); self.assertFalse(out['is_truth_value'])
        refused = r.refusal('typed')
        with patch.object(r, 'build_child_maps', return_value=refused):
            self.assertEqual(m.build_single_cut_event(*candidate()), refused)
            self.assertEqual(m.validate_single_cut_event({}, *candidate()), refused)
        with patch.object(m.prior, 'classify_required_analytic_event', return_value=refused):
            self.assertEqual(m.classify_required_analytic_event(oldtest.source(candidate())), refused)


def run():
    out = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MixedRootTests))
    if not out.wasSuccessful(): raise AssertionError('v48 mixed-root repair tests failed')

if __name__ == '__main__': run()
