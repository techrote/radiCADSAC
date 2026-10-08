#!/usr/bin/env python3
"""V53 bounded mixed-owner contract plus actual-source adversarial execution."""
import argparse
import ast
import copy
import json
from pathlib import Path
import subprocess
import sys

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
BASE = '7126dabf013ef95b0965b74008466e12f0650ef8'
PINS = {
    'pb00701_piecewise_product_model.py': '6ca7a321bd027f3ed2a22059e9aa856c76485f8a',
    'pb00701_piecewise_product_certificate.py': 'e5546f2d408505e8b07d1ebb20253d075d0ada19',
    'test_pb00701_piecewise_product.py': 'c847b27a8981aa3743291a60e267ee8d91d5b5d5',
    'test_pb00701_piecewise_product_integration.py': '46ed0adba3e752be1fbd91f6469ac378fe9af61c',
    'verify_pb00701_v52.py': 'd3372ed41a1218dbc4906cfb3a7eae4d37d830a6',
    'pb00701-piecewise-product-v52.json': '95fd5b3e34e41bd9fc2d6a6df09295789ec67c3d',
    'pb00701-report-v52.md': '27ad74be7104c267a206d29037069c4c262043a7',
    'pb00701_multiharmonic_monotone_anchor_model.py': '38db0b5f1f4549f7ea632db27a5347b3aadd7b1a',
    'pb00701_vanishing_source_factor_model.py': 'dfd554bf9ee41c96f9009f8ed8ceae485e134a5d',
}
FLAGS = {
    'full_original_source_checker': True, 'global_root_union_claimed': True,
    'physical_continuity_at_every_source_knot_required': True,
    'distinct_strict_and_product_provenance': True,
    'normalized_view_alone_is_authority': False, 'strict_owners_relabelled_as_product': False,
    'unit_factor_fabricates_v50_authority': False, 'implicit_root_arithmetic_claimed': False,
    'global_analytic_multiplicity_at_source_knots_claimed': False,
    'discontinuous_source_point_policy_claimed': False, 'general_nonmonotone_solver_claimed': False,
    'native_topology_claimed': False, 'material_body_transition_claimed': False,
    'caller_lowering_trusted': False, 'historical_span_evidence_changed': False,
    'resource_refusal_is_truth': False,
}
CONTROLS = [
    'actual_original_bspline_missing_view_novelty', 'all_product_v52_byte_preservation',
    'all_four_actual_strict_owner_witnesses', 'every_closed_child_direction_checked',
    'gcd_one_is_not_product_authority', 'strict_open_free_and_both_exterior_roots',
    'both_derivative_directions_and_rational_but_implicit_root',
    'all_strict_three_piece_zigzag', 'four_piece_two_product_two_strict_distinct_fields',
    'same_knot_simple_repeated_orders_crossing_tangency', 'full_expression_continuity_not_equal_amplitudes',
    'same_sign_exact_tiny_jump_refusal', 'repeated_knots_channel_degrees_and_partitions',
    'nonconstant_live_harmonic_amplitudes', 'crop_nonunit_global_maps_reversal_negation',
    'old_amplitude_dominance_owner_not_relabelled', 'implicit_roots_namespaced_by_source_span',
    'nonzero_bridge_point_and_maximal_cell_coverage', 'no_missing_duplicate_reordered_span_or_event',
    'owner_route_derivative_endpoint_and_view_forgery', 'original_source_and_digest_substitution',
    'boolean_float_unknown_and_ignored_annotation_dispositions',
    'finite_checker_with_classifier_derivative_selector_sign_search_disabled',
    'stage_resource_nontruth_retains_predecessor', 'unrelated_errors_propagate',
    'historical_pins_full_v52_once', 'frozen_26_no_false_solver_material_native_gate_promotion',
]
UNSUPPORTED = [
    'SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE', 'PRODUCT_SPAN_WITHOUT_CHECKED_V51_VIEW',
    'DISCONTINUOUS_PHYSICAL_SOURCE_KNOT', 'GLOBAL_ANALYTIC_MULTIPLICITY_AT_NONANALYTIC_KNOT',
    'GENERAL_NONMONOTONE_OR_NONCOMMON_FACTOR_SOLVER', 'IMPLICIT_ROOT_ARITHMETIC_BEYOND_ORDER_BRACKET',
    'NATIVE_MATERIAL_TOPOLOGY_AND_STEP_QUALIFICATION',
]


def expected_boundary():
    import verify_pb00701_v51 as inherited
    return {
        'schema': 'radicadsac-mc038-pb00701-mixed-owner-spans/53.0', 'task': 'MC-038',
        'corrective_issue': 271, 'source_baseline': BASE, 'evidence_class': 'DETERMINISTIC_MODEL',
        'decision': 'BOUNDED_CONTINUOUS_MIXED_OWNER_SOURCE_CERTIFICATE',
        'acceptance_authority': 'EXECUTED_REPOSITORY_SELF_TEST_AND_VERIFIED_ISSUE_LEDGER',
        'source_interface': 'ORIGINAL_RATIONAL_BSPLINE_CONTROLS_KNOTS_ID_INTERVAL_AND_AFFINE_PHASE',
        'inherited_contract': 'verify_pb00701_v52.py', 'historical_additional_git_blob_pins': PINS,
        'ordered_evidence_kinds': ['V51_PRODUCT', 'STRICT_SPAN'],
        'strict_owner_versions': [19, 47, 48, 49],
        'finite_checking_policy': 'SUPPLIED_OWNER_RECIPE_AND_EXACT_RATIONAL_TURN_REGENERATION_NO_REPLACEMENT_SEARCH',
        **FLAGS, 'boundary_controls': CONTROLS, 'unsupported': UNSUPPORTED,
        'primary_acceptance': {'source': 'test_pb00701_mixed_owner_span_integration.candidate',
                               'original_source_pieces': 2, 'physical_owners': [50, 19],
                               'open_roots': 2, 'open_crossings': 1, 'open_tangencies': 1,
                               'shared_knot_relation': 'POSITIVE', 'maximal_signs': [-1, 1, 1]},
        'programme_effect': inherited.EFFECT, 'other_open_obligations': ['PO-02', 'PO-07'],
        'protected_semantics': inherited.PROTECTED, 'resources': inherited.RESOURCES,
    }


def contract(data, check_repo=True):
    import verify_pb00701_v52 as parent
    assert parent.same(data, expected_boundary()), 'V53 contract or capability promotion mismatch'
    assert len(CONTROLS) == len(set(CONTROLS))
    if not check_repo:
        return
    for name, sha in PINS.items():
        assert parent.blob(TASK / name) == sha, name
    parent.contract(parent.load(TASK / 'pb00701-piecewise-product-v52.json'), check_repo=True)
    for path in (TASK / 'pb00701-report-v53.md', ROOT / 'docs/machining-completeness/78-PB00701-MIXED-OWNER-SPANS.md'):
        text = path.read_text().lower()
        for token in ('original source', 'strict_span', 'continuity', 'one-sided', 'multiplicity', 'not_established', '26 operations'):
            assert token in text, (str(path), token)
    forbidden = {'classify_required_analytic_event', 'build_mixed_source_evidence', 'build_mixed_certificate',
                 'build_ordered_span_view', 'build_piecewise_source_evidence', 'build_ordered_source_evidence',
                 'carrier_proof', 'certify_derivative', '_decide_factor_sign', '_decide_endpoint'}
    for suffix in ('model', 'certificate'):
        path = TASK / ('pb00701_mixed_owner_span_' + suffix + '.py')
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                assert not isinstance(node.value, float)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [node.module or ''] if isinstance(node, ast.ImportFrom) else [x.name for x in node.names]
                assert all(not n.startswith(('numpy', 'sympy', 'mpmath', 'decimal')) for n in names)
            if suffix == 'certificate' and isinstance(node, ast.Call):
                called = node.func.attr if isinstance(node.func, ast.Attribute) else ''
                assert called not in forbidden, called
    workflow = (ROOT / '.github/workflows/mc1-pb00701-v53.yml').read_text()
    assert workflow.count('verify_pb00701_v53.py --contract --self-test') == 1
    assert 'github.event.pull_request.head.sha || github.sha' in workflow
    assert 'verify_pb00701_v52.py' not in workflow  # inherited once, no parallel clone


def rejected(fn):
    try:
        fn()
    except (ValueError, TypeError, KeyError, AssertionError):
        return
    raise AssertionError('corrupt V53 contract accepted')


def self_test():
    import test_pb00701_mixed_owner_span as core
    import test_pb00701_mixed_owner_span_integration as integration
    core.run()
    integration.run()
    data = expected_boundary()
    for key, value in FLAGS.items():
        bad = copy.deepcopy(data); bad[key] = not value
        rejected(lambda: contract(bad, False))
    for key, value in (('MC-B', 'ESTABLISHED'), ('MC-1', 'ESTABLISHED'),
                       ('domain_operation_count', 25), ('domain_operation_count', True)):
        bad = copy.deepcopy(data); bad['programme_effect'][key] = value
        rejected(lambda: contract(bad, False))
    for key in data['protected_semantics']:
        bad = copy.deepcopy(data); bad['protected_semantics'][key] = False
        rejected(lambda: contract(bad, False))
    bad = copy.deepcopy(data); bad['strict_owner_versions'].append(8)
    rejected(lambda: contract(bad, False))
    bad = copy.deepcopy(data); bad['unknown_authority'] = True
    rejected(lambda: contract(bad, False))
    # Full preserved V52 already executes its complete predecessor chain.
    subprocess.run([sys.executable, str(TASK / 'verify_pb00701_v52.py'), '--contract', '--self-test'], check=True)
    print('PB-007-01 v53 mixed-owner original-source contract and self-test: PASS')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    opts = parser.parse_args()
    if not (opts.contract or opts.self_test):
        parser.error('choose --contract and/or --self-test')
    if opts.contract:
        data = json.loads((TASK / 'pb00701-mixed-owner-spans-v53.json').read_text())
        contract(data)
        print('PB-007-01 v53 contract: PASS')
    if opts.self_test:
        self_test()


if __name__ == '__main__':
    main()
