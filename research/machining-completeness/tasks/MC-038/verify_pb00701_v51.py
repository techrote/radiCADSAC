#!/usr/bin/env python3
"""V51 finite ordering contract and actual-source acceptance, never native evidence."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
TASK = Path(__file__).resolve().parent
MC = ROOT / 'research/machining-completeness'
BASE = '5c7dcf48829176c9e74f60221120ef5414e14e8a'
PINS = {'research/machining-completeness/tasks/MC-032/event_engine.py': '789a709c5141479a343035d1b7055dd4e53534e1', 'research/machining-completeness/tasks/MC-038/pb00701_common_factor_model.py': 'eb96654d96717b34d05fd46f875abf0581c492d3', 'research/machining-completeness/tasks/MC-038/pb00701_source_laurent_factor_model.py': '4e656c95a13858ee8ed496149d200a0a321a61a0', 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_orientation_cut_model.py': 'a56d6487963d269405ab82f3db4cce58a0165520', 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_child_map_model.py': 'c055e7f392a921b386a1a99cc70b5004121ae7f6', 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_endpoint_model.py': '77c18cb5c8c0700072c65969c973e8f3c4c12a99', 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_endpoint_certificate.py': '92258bbad7fa4cfa1be5413a7253369e73abc318', 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_monotone_cut_model.py': '07b092f9c7df8b3325c2b15d17ca7abe9781cb10', 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_monotone_cut_certificate.py': 'f98e0e4f506f9b4c5eb247eca4f5a142caa3c4b6', 'research/machining-completeness/tasks/MC-038/pb00701_mixed_orientation_roots_model.py': '22ddac25d318082178ba28bee77b5b8021c80734', 'research/machining-completeness/tasks/MC-038/pb00701_mixed_orientation_consumer.py': 'ad14933591ec6caea1ee28431252381015a7edd7', 'research/machining-completeness/tasks/MC-038/pb00701_mixed_boundary_model.py': '4c4c9697b2237790d2e7ac8b96ec1dcdf2398303', 'research/machining-completeness/tasks/MC-038/pb00701_mixed_multicut_model.py': 'd7a0c35dee39514c4d49b91739c01f57866a0bf5', 'research/machining-completeness/tasks/MC-038/pb00701_mixed_multicut_certificate.py': '0d6acd3259346be863e9c40a039f694b1b750c71', 'research/machining-completeness/tasks/MC-038/pb00701_multiharmonic_monotone_anchor_model.py': '38db0b5f1f4549f7ea632db27a5347b3aadd7b1a', 'research/machining-completeness/tasks/MC-038/pb00701_vanishing_source_factor_model.py': 'dfd554bf9ee41c96f9009f8ed8ceae485e134a5d', 'research/machining-completeness/tasks/MC-038/pb00701_vanishing_source_factor_certificate.py': '87f026f563b7da828a7299c61861ffd815f34461', 'research/machining-completeness/tasks/MC-038/verify_pb00701_v50.py': '0ae5d62024610d1a66c6c4ca3d42d4dcd22a4102'}
CONTROLS = ['actual_v50_source_count_preserved', 'factor_owned_nonzero_before_sign_refinement', 'exact_rational_series_and_independent_remainder_audit', 'both_irrational_carrier_signs', 'exact_conjugates_and_different_factor_fields', 'strict_carrier_direction_from_all_four_owners', 'implicit_root_order_from_carrier_sign', 'rational_coincidence_additive_multiplicity', 'no_transcendental_or_algebraic_root_coordinate_guess', 'overlapping_and_close_exact_neighbors', 'odd_even_multiplicity_sign_cells', 'zero_one_both_exterior_roots_and_inward_jets', 'root_free_factor_and_root_free_carrier', 'rational_irrational_proof_cut_not_extra_root', 'phase_reversal_global_interval_and_source_scaling', 'full_source_field_phase_witness_binding', 'finite_checker_no_replacement_search', 'omitted_duplicate_reordered_roots_reject', 'sign_cell_coverage_and_parity_corruption_reject', 'boolean_float_unknown_source_rejection', 'exact_resource_nontruth_preserves_v50', 'unrelated_errors_propagate', 'historical_pins_precedence', 'frozen_26_operations_and_no_false_capability']
PROTECTED = {'source_audio_provenance': True, 'canonical_journal': True, 'exact_time_path_phase': True, 'source_uncertainty': True, 'positive_volume_material': True, 'cutter_holder_access': True, 'durable_body_lineage': True, 'refusal_uncertified': True, 'conventional_step': True}
EFFECT = {'PB-007-01': 'OPEN', 'PB-007-02': 'OPEN_DEPENDENT_ON_PB-007-01', 'PB-007-03': 'OPEN', 'PB-007-04': 'OPEN_PROPAGATED', 'PO-04': 'OPEN', 'PO-05': 'OPEN', 'PO-08': 'OPEN', 'MC-B': 'NOT_ESTABLISHED', 'MC-1': 'NOT_ESTABLISHED', 'domain_operation_count': 26, 'domain_narrowed': False}
RESOURCES = {'native_campaign_run': False, 'paid_campaign_run': False, 'production_authorized': False, 'expensive_execution_authorized': False}
UNSUPPORTED = ['GENERAL_NONCOMMON_FACTOR_OR_NONMONOTONE_CARRIER_EVENTS', 'NON_SIMPLE_OR_UNSUPPORTED_CARRIER_CHECKER_OWNER', 'GLOBAL_CROSS_SPLINE_SPAN_ROOT_GLUING', 'ARITHMETIC_ON_IMPLICIT_ROOT_COORDINATES_OR_UNRELATED_FIELD_COMPOSITA', 'NONCOMMENSURATE_OR_INDEPENDENT_PHASE_LAWS', 'NATIVE_TOPOLOGY_OR_MATERIAL_BODY_TRANSITION']
FLAGS = {'ordered_full_product_root_list_claimed': True, 'legacy_v50_order_claim_changed': False, 'physical_product_strict_monotonicity_claimed': False, 'general_nonmonotone_solver_claimed': False, 'material_body_transition_claimed': False, 'native_topology_claimed': False, 'cross_spline_span_continuity_claimed': False, 'compositum_claimed': False, 'physical_source_replaced_by_carrier': False, 'resource_refusal_is_truth': False, 'caller_certificates_trusted': False}


def load(path):
    return json.loads(path.read_text())


def same(x, y):
    return json.dumps(x, sort_keys=True, allow_nan=False) == json.dumps(y, sort_keys=True, allow_nan=False)


def blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()


def contract(data, check_repo=True):
    assert data['schema'] == 'radicadsac-mc038-pb00701-ordered-product/51.0'
    assert data['task'] == 'MC-038' and type(data['corrective_issue']) is int and data['corrective_issue'] == 267
    assert data['source_baseline'] == BASE and data['evidence_class'] == 'DETERMINISTIC_MODEL'
    assert data['decision'] == 'EXACT_ORDERED_PRODUCT_EVIDENCE_WITH_RETAINED_V50_AUTHORITY'
    assert data['acceptance_authority'] == 'EXECUTED_REPOSITORY_SELF_TEST_AND_VERIFIED_ISSUE_LEDGER'
    assert data['ordering_claim_scope'] == 'THIS_CHECKED_V50_PRODUCT_ON_ONE_LOWERED_SPAN'
    assert data['finite_checker_source_interface'] == 'ORIGINAL_LOWERED_RATIONAL_CHANNELS_ID_GLOBAL_INTERVAL_AND_PHASE_PLUS_SUPPLIED_PRODUCT'
    assert data['source_wrapper_preserves_complete_v50_result'] is True
    import pb00701_ordered_product_model as m
    assert data['allowed_carrier_owners'] == list(m.v50.OWNERS)
    assert data['boundary_controls'] == CONTROLS and len(set(CONTROLS)) == len(CONTROLS)
    assert data['historical_git_blob_pins'] == PINS
    for key, value in FLAGS.items():
        assert data[key] is value, key
    assert same(data['protected_semantics'], PROTECTED)
    assert same(data['programme_effect'], EFFECT) and same(data['resources'], RESOURCES)
    assert data['unsupported'] == UNSUPPORTED
    if not check_repo:
        return
    for path, sha in PINS.items():
        assert blob(ROOT / path) == sha, path
    programme = load(MC / 'programme-v1.json')
    assert programme['capability_status'] == 'NOT_ESTABLISHED'
    assert programme['production_authorized'] is False and programme['expensive_execution_authorized'] is False
    assert {g['id']: g for g in programme['gates']}['MC-B']['state'] == 'NOT_ESTABLISHED'
    assert len(load(MC / 'tasks/MC-002/domain-contract-v1.json')['coverage_rule']['required_operation_ids']) == 26
    obligations = {p['id']: p for p in load(MC / 'proof-obligations-v1.json')['obligations']}
    assert all(obligations[po]['state'] == 'OPEN' for po in ('PO-04', 'PO-05', 'PO-08'))
    for path in (TASK / 'pb00701-report-v51.md', ROOT / 'docs/machining-completeness/75-PB00701-ORDERED-PRODUCT.md'):
        text = path.read_text().lower()
        for token in ('carrier', 'multiplicity', 'rational', 'sign', 'not_established', '26 operations'):
            assert token in text, (path, token)
    for name in ('pb00701_ordered_product_model.py', 'pb00701_ordered_product_certificate.py'):
        tree = ast.parse((TASK / name).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                assert not isinstance(node.value, float), 'floating truth constant'
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = ([node.module or ''] if isinstance(node, ast.ImportFrom) else [x.name for x in node.names])
                assert all(not n.startswith(('numpy', 'mpmath', 'decimal', 'sympy')) for n in names)
                assert not isinstance(node, ast.ImportFrom) or node.module != 'math'
            if name.endswith('_certificate.py') and isinstance(node, ast.Call):
                called = node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id if isinstance(node.func, ast.Name) else ''
                assert called not in {'_decide_factor_sign', '_decide_endpoint', 'carrier_proof',
                                      'certify_derivative', 'classify_required_analytic_event',
                                      'build_ordered_source_evidence', 'build_product_event'}
    assert 'verify_pb00701_v51.py --contract --self-test' in (ROOT / '.github/workflows/mc1-pb00701-v51.yml').read_text()


def rejected(fn):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, TypeError):
        return
    raise AssertionError('adversarial V51 contract mutation accepted')


def self_test():
    import test_pb00701_ordered_product as core
    import test_pb00701_ordered_product_integration as integration
    core.run()
    integration.run()
    data = load(TASK / 'pb00701-ordered-product-v51.json')
    for key, value in FLAGS.items():
        bad = copy.deepcopy(data); bad[key] = not value
        rejected(lambda: contract(bad, False))
    for key, value in (('MC-B', 'ESTABLISHED'), ('domain_operation_count', 25), ('domain_operation_count', True)):
        bad = copy.deepcopy(data); bad['programme_effect'][key] = value
        rejected(lambda: contract(bad, False))
    for key in PROTECTED:
        bad = copy.deepcopy(data); bad['protected_semantics'][key] = False
        rejected(lambda: contract(bad, False))
    bad = copy.deepcopy(data); bad['historical_git_blob_pins'][next(iter(PINS))] = '0' * 40
    rejected(lambda: contract(bad, False))
    # Full preserved V50 regression, not just a metadata check or stub import.
    subprocess.run([sys.executable, str(TASK / 'verify_pb00701_v50.py'), '--contract', '--self-test'], check=True)
    print('PB-007-01 v51 ordered physical roots and sign cells self-test: PASS')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    opts = parser.parse_args()
    if not (opts.contract or opts.self_test):
        parser.error('choose --contract and/or --self-test')
    if opts.contract:
        contract(load(TASK / 'pb00701-ordered-product-v51.json'))
        print('PB-007-01 v51 contract: PASS')
    if opts.self_test:
        self_test()


if __name__ == '__main__':
    main()
