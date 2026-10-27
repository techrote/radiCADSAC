#!/usr/bin/env python3
"""V54 finite owner inventory, owner-specific ordered-span adapters and acceptance."""
import argparse
import ast
import copy
import json
from pathlib import Path
import subprocess
import sys

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
sys.path.insert(0, str(TASK))
BASE = '7e82d5a21ad5879a497c91ec2b1ca12863e06e9b'
ISSUE_BASELINE = '9734776b3cef3d7039be9623e8872df2c2a85174'
PINS = {
    'pb00701_mixed_owner_span_model.py': '0d7b334accaec307ef2016a1bec2fa22cb115920',
    'pb00701_mixed_owner_span_certificate.py': '91bfc606539d05f054a86ee381af59926502c167',
    'test_pb00701_mixed_owner_span.py': 'f25e76dab22e47b6573a4c2fd8c1170677c887fb',
    'test_pb00701_mixed_owner_span_integration.py': '050e6b2110d9d706a9cf96006b79e069adb7beac',
    'verify_pb00701_v53.py': '7995627b8ff784c17947b2db746a588b5ed18d7b',
    'pb00701-mixed-owner-spans-v53.json': '006ceb86365616462de3b77689950e9b849d349d',
    'pb00701-report-v53.md': '0ad24327f9839d8ade12a6fa98ab2238438d9a08',
    'pb00701_coupled_bspline_model.py': 'a086b625e1a6dea8bd202699d161167bb69cc9e7',
    'pb00701_pointwise_derivative_envelope_model.py': 'a0bbc30f5a26e2f2991c96640cf4410763ef2eb4',
    'pb00701_l1_sign_orthant_envelope_model.py': 'f97e5c18e27fd8021362f24b62a11c889b5b6ce1',
    'pb00701_phase_sector_anchor_model.py': '923e9d63e3950a705923b9b5e619fee43c2819eb',
    'pb00701_nonconstant_phase_anchor_model.py': '1eb91cd3274256fdff7b1e3d296508bdcf7a87e2',
    'pb00701_mixed_quadrature_phase_anchor_model.py': '925a51b89a477b388e4824eaae2675059ee47c33',
    'pb00701_component_cone_phase_anchor_model.py': 'fc1f940f5b9b2b6fd8570b36a91c4389453e29b2',
    'pb00701_pointwise_component_cone_model.py': 'a303bba600fa83a1b55c8e113ce1ec7d06f68590',
    'pb00701_algebraic_phase_cell_model.py': '117dafa3073dd2a5dc00c288089fd88d41628fae',
    'pb00701_pythagorean_phase_cell_model.py': '3c792284922a481c9c2edad4f61f3f4f1afbe63a',
    'pb00701_source_adaptive_separator_model.py': 'd920a5b670d14ac4a54b0ed879e83532f2114b95',
    'pb00701_phase_correlated_common_factor_model.py': 'dc7110fb46f585e8849b7fd3b0dc43f393fdbd87',
    'pb00701_phase_correlated_proportional_common_factor_model.py': '7cecbbb120cc751f434cf49209e3a70cead85c3f',
    'pb00701_phase_correlated_varying_ratio_shared_factor_model.py': 'e4b9ecefed12a92c3d72da4edf0a12f45ce05e3d',
    'pb00701_phase_correlated_two_polynomial_shared_factor_model.py': '485ad89d9b5ff9847095f48880cc9a9cb3be96ce',
    'pb00701_direct_rotated_coordinate_model.py': 'f943ee9b0c093bb84d559beb403d83e07646c316',
    'pb00701_signed_a_direct_rotated_coordinate_model.py': 'd8cf3c4f3abaf1299bae2e4fd7120b17724a2df1',
    'pb00701_signed_b_anti_diagonal_model.py': '2f642ac0b6f222dd8ec2cf3a54ffa3c07bb27abe',
    'pb00701_orientation_transition_bridge_model.py': 'a0930d7bfddd619bf930a51bbfa14570e2450fe5',
    'pb00701_correlated_closed_handoff_model.py': 'd47b8dd8fe8b4b91fd12c1e76974a5a4e85b03b2',
}
FLAGS = {
    'full_original_source_checker': True, 'global_root_union_claimed': True,
    'physical_continuity_at_every_source_knot_required': True,
    'one_category_per_historical_owner': True, 'owner_specific_finite_recipes_only': True,
    'historical_owners_relabelled': False, 'sign_span_claims_derivative_or_monotonicity': False,
    'counts_or_delegated_zero_sets_promoted_to_order': False,
    'checker_reclassifies_or_selects_replacement_proofs': False,
    'normalized_view_alone_is_authority': False, 'implicit_root_arithmetic_claimed': False,
    'global_analytic_multiplicity_at_source_knots_claimed': False,
    'discontinuous_source_point_policy_claimed': False, 'general_nonmonotone_solver_claimed': False,
    'general_noncommon_factor_solver_claimed': False, 'native_topology_claimed': False,
    'material_body_transition_claimed': False, 'mc_b_retry_claimed': False,
    'caller_lowering_trusted': False, 'historical_span_evidence_changed': False,
    'resource_refusal_is_truth': False, 'automatic_successor_adapter_issue_created': False,
}
CONTROLS = [
    'static_emitter_and_observed_owner_inventory_agree', 'actual_reversed_v53_residual',
    'positive_and_negative_amplitude_dominance', 'sign_span_endpoint_root_impossibility',
    'strict_owner_open_free_and_endpoint_root_shapes', 'owner_witness_and_identity_retained',
    'product_plus_legacy', 'strict_plus_legacy', 'all_legacy', 'four_piece_sign_product_strict_sign',
    'preserved_v52_all_product_and_v53_mixed_results', 'exact_continuity_and_tiny_jump_refusal',
    'reversal_negation_nonunit_maps', 'repeated_and_different_knots_and_degrees',
    'forged_owner_route_endpoint_derivative_monotonicity_fields', 'cross_owner_witness_substitution',
    'missing_duplicate_reordered_views', 'source_phase_harmonic_identity_mutation',
    'boolean_float_unknown_and_annotation_dispositions',
    'finite_checking_with_classifier_and_proof_selection_disabled',
    'resource_nontruth_and_unrelated_exception_propagation', 'category_three_premise_and_four_disposition',
    'frozen_admitted_corpus_rerun', 'full_unchanged_v53_once',
    'frozen_26_no_false_pb_solver_native_material_mcb_promotion',
]
UNSUPPORTED = [
    'SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE', 'SPAN_OWNER_IS_BLOCKER_OR_NON_EVENT',
    'SPAN_OWNER_OUTSIDE_FINITE_V54_INVENTORY', 'PHYSICAL_SOURCE_KNOT_DISCONTINUITY',
    'GLOBAL_ANALYTIC_MULTIPLICITY_AT_NONANALYTIC_KNOT', 'GENERAL_NONMONOTONE_OR_NONCOMMON_FACTOR_SOLVER',
    'IMPLICIT_ROOT_ARITHMETIC_BEYOND_ORDER_BRACKET', 'NATIVE_MATERIAL_TOPOLOGY_AND_STEP_QUALIFICATION',
]
NEXT_THEOREM = {
    'routing': 'THEOREM_TASK_IN_EVIDENCE_AND_CURRENT_STATE_HANDOFF_NOT_AN_ADAPTER_ISSUE',
    'family': 'PB00701_GENERAL_NONCOMMON_FACTOR_NONMONOTONE_ANALYTIC_EVENT_COVERAGE',
    'static_only_boundary_owner': 'PB00701_GENERAL_COUPLED_THEOREM_BOUNDARY',
    'theorem_boundary': 'BOUNDED_POLYNOMIAL_TRIGONOMETRIC_EXPONENTIAL_ZERO_PROBLEM',
    'secondary_frontier': 'ORDERED_ROOT_ISOLATION_FOR_COUNT_ONLY_CATEGORY_THREE_OWNERS',
    'issue_created': False,
}


def expected_boundary():
    import verify_pb00701_v51 as inherited
    import pb00701_finite_owner_span_model as m
    return {
        'schema': 'radicadsac-mc038-pb00701-finite-owner-coverage/54.0', 'task': 'MC-038',
        'corrective_issue': 275, 'source_baseline': BASE, 'issue_reviewed_baseline': ISSUE_BASELINE,
        'evidence_class': 'DETERMINISTIC_MODEL',
        'decision': 'BOUNDED_FINITE_HISTORICAL_OWNER_INVENTORY_AND_ORDERED_SPAN_ADAPTERS',
        'acceptance_authority': 'EXECUTED_REPOSITORY_SELF_TEST_AND_VERIFIED_ISSUE_LEDGER',
        'source_interface': 'ORIGINAL_RATIONAL_BSPLINE_CONTROLS_KNOTS_ID_INTERVAL_AND_AFFINE_PHASE',
        'inherited_contract': 'verify_pb00701_v53.py', 'historical_additional_git_blob_pins': PINS,
        'inventory_artifact': 'pb00701-finite-owner-inventory-v54.json',
        'corpus_artifact': 'pb00701-finite-owner-corpus-v54.json',
        'ordered_evidence_kinds': ['V51_PRODUCT', 'STRICT_SPAN', 'SIGN_SPAN', 'OWNER_STRICT_SPAN'],
        'owner_category_counts': {'1': 5, '2': 20, '3': 16, '4': 2},
        'sign_span_owner': {'owner': m.SIGN_OWNER, 'version': 7,
                            'premise': 'CLOSED_SPAN_EXACT_RATIONAL_AMPLITUDE_DOMINANCE_ROOT_FREE_SIGN'},
        'strict_adapter_owner_versions': sorted(e['version'] for e in m.STRICT_ADAPTERS.values()),
        'lacking_premise_owner_versions': sorted({v for v, _ in m.LACKING_PREMISE.values()}),
        'blocked_owner_versions': sorted(v for v, _ in m.BLOCKED_OWNERS.values()),
        'finite_checking_policy': 'SOURCE_BOUND_SELECTED_WITNESS_LEAVES_ENDPOINTS_AND_ROUTE_METADATA_NO_PROOF_RESELECTION',
        **FLAGS, 'boundary_controls': CONTROLS, 'unsupported': UNSUPPORTED,
        'primary_acceptance': {'source': 'test_pb00701_finite_owner_span_integration.candidate',
                               'description': 'reverse_source(v53 principal original B-spline source)',
                               'original_source_pieces': 2, 'physical_owners': [7, 50],
                               'span_evidence_kinds': ['SIGN_SPAN', 'V51_PRODUCT'],
                               'dominance_margin': '97/200', 'open_roots': 2, 'open_crossings': 1,
                               'open_tangencies': 1, 'shared_knot_relation': 'POSITIVE',
                               'maximal_signs': [1, 1, -1]},
        'next_theorem_task': NEXT_THEOREM,
        'programme_effect': inherited.EFFECT, 'other_open_obligations': ['PO-02', 'PO-07'],
        'protected_semantics': inherited.PROTECTED, 'resources': inherited.RESOURCES,
    }


def contract(data, check_repo=True):
    import verify_pb00701_v52 as grand
    import verify_pb00701_v53 as parent
    import pb00701_finite_owner_inventory as inventory
    assert grand.same(data, expected_boundary()), 'V54 contract or capability promotion mismatch'
    assert len(CONTROLS) == len(set(CONTROLS))
    if not check_repo:
        return
    for name, sha in PINS.items():
        assert grand.blob(TASK / name) == sha, name
    parent.contract(grand.load(TASK / 'pb00701-mixed-owner-spans-v53.json'), check_repo=True)
    assert grand.same(grand.load(TASK / 'pb00701-finite-owner-inventory-v54.json'), inventory.inventory())
    corpus = inventory.load_corpus()
    assert grand.same(corpus['summary'], inventory.corpus_summary([c['expected'] for c in corpus['cases']]))
    for path in (TASK / 'pb00701-report-v54.md', ROOT / 'docs/machining-completeness/79-PB00701-FINITE-OWNER-COVERAGE.md'):
        text = path.read_text(encoding='utf-8').lower()
        for token in ('original source', 'sign_span', 'owner_strict_span', 'amplitude dominance', 'inventory',
                      'category 3', 'not a derivative', 'one-sided', 'not_established', '26 operations',
                      'general noncommon-factor'):
            assert token in text, (str(path), token)
    forbidden = {'classify_required_analytic_event', 'build_mixed_source_evidence', 'build_mixed_certificate',
                 'build_finite_owner_source_evidence', 'build_finite_owner_certificate', 'build_ordered_span_view',
                 'build_piecewise_source_evidence', 'build_ordered_source_evidence', 'carrier_proof',
                 'certify_derivative', '_decide_factor_sign', '_decide_endpoint', '_delegate_carrier',
                 '_delegate_residual'}
    for name in ('pb00701_finite_owner_span_model.py', 'pb00701_finite_owner_span_certificate.py',
                 'pb00701_finite_owner_inventory.py', 'pb00701_finite_owner_witness_check.py'):
        tree = ast.parse((TASK / name).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                assert not isinstance(node.value, float)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [node.module or ''] if isinstance(node, ast.ImportFrom) else [x.name for x in node.names]
                assert all(not n.startswith(('numpy', 'sympy', 'mpmath', 'decimal')) for n in names)
            if (name.endswith('certificate.py') or name.endswith('witness_check.py')) and isinstance(node, ast.Call):
                called = node.func.attr if isinstance(node.func, ast.Attribute) else ''
                assert called not in forbidden | {'regenerate_owner_route', 'owner_recipe'}, called
    workflow = (ROOT / '.github/workflows/mc1-pb00701-v54.yml').read_text()
    assert workflow.count('verify_pb00701_v54.py --contract --self-test --acceptance') == 1
    assert 'github.event.pull_request.head.sha || github.sha' in workflow
    assert 'verify_pb00701_v53.py' not in workflow  # inherited once inside acceptance
    assert not (ROOT / '.github/workflows/mc1-pb00701-v54-recovery-bootstrap.yml').exists()
    assert not (ROOT / '.v54-bootstrap').exists()


def rejected(fn):
    try:
        fn()
    except (ValueError, TypeError, KeyError, AssertionError):
        return
    raise AssertionError('corrupt V54 contract accepted')


def self_test():
    import test_pb00701_finite_owner_span as core
    import test_pb00701_finite_owner_span_integration as integration
    core.run()
    integration.run()
    data = expected_boundary()
    for key, value in FLAGS.items():
        bad = copy.deepcopy(data); bad[key] = not value
        rejected(lambda: contract(bad, False))
    for key, value in (('MC-B', 'ESTABLISHED'), ('MC-1', 'ESTABLISHED'), ('PB-007-01', 'CLOSED'),
                       ('domain_operation_count', 25), ('domain_operation_count', True)):
        bad = copy.deepcopy(data); bad['programme_effect'][key] = value
        rejected(lambda: contract(bad, False))
    for key in data['protected_semantics']:
        bad = copy.deepcopy(data); bad['protected_semantics'][key] = False
        rejected(lambda: contract(bad, False))
    for key in data['resources']:
        bad = copy.deepcopy(data); bad['resources'][key] = True
        rejected(lambda: contract(bad, False))
    bad = copy.deepcopy(data); bad['strict_adapter_owner_versions'].append(12)
    rejected(lambda: contract(bad, False))
    bad = copy.deepcopy(data); bad['owner_category_counts']['3'] = 15
    rejected(lambda: contract(bad, False))
    bad = copy.deepcopy(data); bad['next_theorem_task']['issue_created'] = True
    rejected(lambda: contract(bad, False))
    # A green verifier must not advertise the superseded route-regeneration
    # policy now that the checker validates exactly the submitted witness.
    bad = copy.deepcopy(data)
    bad['finite_checking_policy'] = 'OWNER_OWN_FIXED_RECIPE_REGENERATION_ON_ORIGINAL_SPAN_NO_CLASSIFIER_NO_REPLACEMENT'
    rejected(lambda: contract(bad, False))
    bad = copy.deepcopy(data); bad['unknown_authority'] = True
    rejected(lambda: contract(bad, False))
    print('PB-007-01 v54 finite owner adapter self-test: PASS')


def acceptance():
    import pb00701_finite_owner_span_model as m
    import pb00701_finite_owner_span_certificate as checker
    import pb00701_finite_owner_inventory as inventory
    import test_pb00701_finite_owner_span_integration as integration
    spec = integration.candidate()
    prior = m.v53.build_mixed_source_evidence(spec)
    assert (prior['reason'], prior['owner']) == ('SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE', m.SIGN_OWNER)
    result = m.build_finite_owner_source_evidence(spec)
    assert result['status'] == 'FINITE_OWNER_SOURCE_EVIDENCE_CERTIFIED', result.get('reason')
    proof = result['certificate']
    assert checker.validate_finite_owner_certificate(proof, spec) is True
    expected = expected_boundary()['primary_acceptance']
    summary = proof['global_root_summary']
    observed = {'original_source_pieces': len(proof['span_proofs']),
                'physical_owners': [m.SIGN_ADAPTERS.get(o, m.ALREADY_ORDERED.get(o, {})).get('version')
                                    for o in proof['span_original_owners']],
                'span_evidence_kinds': proof['span_evidence_kinds'],
                'dominance_margin': proof['span_proofs'][0]['underlying_witness']['margin'],
                'open_roots': summary['distinct_roots_open'], 'open_crossings': summary['crossings_open'],
                'open_tangencies': summary['tangencies_open'],
                'shared_knot_relation': proof['knot_evidence'][0]['physical_relation'],
                'maximal_signs': [c['physical_sign'] for c in proof['maximal_open_sign_cells']]}
    assert all(observed[k] == expected[k] for k in observed), observed
    print('v54 ACTUAL SOURCE: reversed v53 residual keeps EXACT_RATIONAL_AMPLITUDE_DOMINANCE (margin 97/200) '
          'as a root-free SIGN_SPAN beside V51 product; 2 roots, maximal signs +,+,-: PASS')
    corpus = inventory.load_corpus()
    print('v54 INVENTORY:', json.dumps(inventory.inventory()['category_counts']),
          'corpus:', json.dumps(corpus['summary']['v54_dispositions']))
    # Complete unchanged predecessor chain, exactly once.
    subprocess.run([sys.executable, str(TASK / 'verify_pb00701_v53.py'), '--contract', '--self-test'], check=True)
    print('PB-007-01 v54 finite owner inventory and ordered-span acceptance: PASS')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--acceptance', action='store_true')
    opts = parser.parse_args()
    if not (opts.contract or opts.self_test or opts.acceptance):
        parser.error('choose --contract, --self-test and/or --acceptance')
    if opts.contract:
        data = json.loads((TASK / 'pb00701-finite-owner-coverage-v54.json').read_text())
        contract(data)
        print('PB-007-01 v54 contract: PASS')
    if opts.self_test:
        self_test()
    if opts.acceptance:
        acceptance()


if __name__ == '__main__':
    main()
