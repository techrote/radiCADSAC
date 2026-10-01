#!/usr/bin/env python3
"""V49 scope/pin contract and full-repository acceptance entrypoint.

--self-test executes the actual historical source stack, never substitutes.
Initial repository evidence is a pinned past checkpoint, not a claim that an
untested future head or merge passes. Final landing evidence lives on #263.
"""
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
BASE = 'd13d1e24d13f087a999a68228c200136d9aedf79'
PREFIX = 'research/machining-completeness/tasks/'
PINS = {
 PREFIX+'MC-032/event_engine.py': '789a709c5141479a343035d1b7055dd4e53534e1',
 PREFIX+'MC-038/pb00701_algebraic_child_map_model.py': 'c055e7f392a921b386a1a99cc70b5004121ae7f6',
 PREFIX+'MC-038/pb00701_algebraic_endpoint_model.py': '77c18cb5c8c0700072c65969c973e8f3c4c12a99',
 PREFIX+'MC-038/pb00701_algebraic_endpoint_certificate.py': '92258bbad7fa4cfa1be5413a7253369e73abc318',
 PREFIX+'MC-038/pb00701_algebraic_orientation_cut_model.py': 'a56d6487963d269405ab82f3db4cce58a0165520',
 PREFIX+'MC-038/pb00701_orientation_root_partition_model.py': '2f96622b5c69655279d66fe2b36f8f3e03414660',
 PREFIX+'MC-038/pb00701_phase_sector_partition_model.py': '6211e658621af7100c2509dcafdaeaf348e48d46',
 PREFIX+'MC-038/pb00701_algebraic_interval_model.py': '859cb6ee600486198f53bfcc9660e2b482bb54d0',
 PREFIX+'MC-038/pb00701_algebraic_monotone_cut_model.py': '07b092f9c7df8b3325c2b15d17ca7abe9781cb10',
 PREFIX+'MC-038/pb00701_algebraic_monotone_cut_certificate.py': 'f98e0e4f506f9b4c5eb247eca4f5a142caa3c4b6',
 PREFIX+'MC-038/pb00701_mixed_orientation_roots_model.py': '22ddac25d318082178ba28bee77b5b8021c80734',
 PREFIX+'MC-038/pb00701_mixed_orientation_consumer.py': 'ad14933591ec6caea1ee28431252381015a7edd7',
}
IMPLEMENTATION_PINS = {
 'pb00701_mixed_boundary_model.py': '4c4c9697b2237790d2e7ac8b96ec1dcdf2398303',
 'pb00701_mixed_multicut_model.py': 'd7a0c35dee39514c4d49b91739c01f57866a0bf5',
 'pb00701_mixed_multicut_certificate.py': '0d6acd3259346be863e9c40a039f694b1b750c71',
}
INITIAL_EVIDENCE = {
 'checked_head': 'acabfbce7edb63864ae32b19ab849f67d0a7cb43',
 'checked_tree': '9454e1f271427dbb6f63996b749abf8bfc4031e9',
 'focused_run': 36938994942, 'static_run': 36938994888, 'conclusion': 'SUCCESS',
 'core_test_methods': 14, 'integration_test_methods': 11,
 'complete_predecessor_residual_executed': True, 'implementation_repair_required': False,
}
CONTROLS = {'rational_phase_cut_coincidence', 'distinct_conjugates_and_minimal_polynomials', 'multiple_root_strict_derivative_contradiction', 'unknown_source_and_nonexact_rejection', 'source_field_partition_derivative_endpoint_corruption', 'zero_open_external_endpoint_outcomes', 'historical_success_precedence', 'internal_physical_root_once', 'genuine_complete_v48_residual', 'uniform_phase_containment_and_exact_floor', 'both_phase_directions', 'overlap_is_not_root_equality', 'exact_mixed_source_partition', 'strict_margin_equality_and_neighbors', 'all_physical_derivative_channels', 'finite_checker_no_route_or_endpoint_sign_search', 'exact_resource_refusal', 'boundary_local_sturm_one_sided_jets', 'original_parent_coordinate_chain_rule', 'full_source_counts_and_multiplicities', 'no_false_capability_promotion', 'frozen_26_operations'}
EFFECT = {'PB-007-01': 'OPEN', 'PB-007-02': 'OPEN_DEPENDENT_ON_PB-007-01', 'PB-007-03': 'OPEN', 'PB-007-04': 'OPEN_PROPAGATED', 'PO-04': 'OPEN', 'PO-05': 'OPEN', 'PO-08': 'OPEN', 'MC-B': 'NOT_ESTABLISHED', 'MC-1': 'NOT_ESTABLISHED', 'domain_operation_count': 26, 'domain_narrowed': False}
PROTECTED = {'durable_body_lineage', 'canonical_journal', 'exact_time_path_phase', 'source_uncertainty', 'cutter_holder_access', 'source_audio_provenance', 'conventional_step', 'positive_volume_material', 'refusal_uncertified'}
AUTHORITY = {'root_producer': 'PRESERVED_V48_FULL_SOURCE_MIXED_ROOT_ACCOUNTING', 'representation': 'UNCHANGED_PARENT_COORDINATE_INDEPENDENT_BOUNDARY_PAIR', 'polynomial': 'RATIONAL_STURM_WITH_BOUNDARY_LOCAL_ONE_SIDED_JETS', 'derivative': 'PRESERVED_V42_V43_COMPLETE_STRICT_ORTHANT_INEQUALITIES', 'external_and_rational_endpoint': 'PRESERVED_V19_V6_RATIONAL_TURN', 'irrational_endpoint': 'PRESERVED_V46_SOURCE_BOUND_ENDPOINT_CHECKER', 'composition': 'SOURCE_VALIDATION_THEN_PRESERVED_V27_COMPOSER'}
FALSE_FLAGS = ('compositum_claimed', 'normalized_mixed_field_maps_claimed',
               'general_nonmonotone_solver_claimed', 'caller_metadata_trusted',
               'resource_refusal_is_truth', 'unknown_source_fields_stripped',
               'historical_source_mutated', 'native_geometry_claimed')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()


def same(x, y):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False) == json.dumps(y, sort_keys=True, separators=(',', ':'), allow_nan=False)


def contract(data, check_repo=True):
    assert data['schema'] == 'radicadsac-mc038-pb00701-mixed-boundary-multicut/49.1'
    assert data['task'] == 'MC-038' and type(data['corrective_issue']) is int and data['corrective_issue'] == 263
    assert data['source_baseline'] == BASE and data['evidence_class'] == 'DETERMINISTIC_MODEL'
    assert data['decision'] == 'BOUNDED_MIXED_BOUNDARY_MULTICUT_MONOTONE_COMPOSITION_ESTABLISHED'
    assert same(data['authority'], AUTHORITY) and same(data['historical_git_blob_pins'], PINS)
    assert same(data['implementation_git_blob_pins'], IMPLEMENTATION_PINS)
    assert same(data['initial_repository_evidence'], INITIAL_EVIDENCE)
    assert data['landing_policy'] == 'EXACT_FINAL_HEAD_AND_INDEPENDENT_MERGED_MAIN_REQUIRED'
    assert data['landing_evidence_owner'] == 'MC-038_ISSUE_263_ACCEPTANCE_LEDGER'
    assert set(data['boundary_controls']) == CONTROLS and len(data['boundary_controls']) == len(CONTROLS)
    assert data['phase_cut_family'] == 'V34_DIAGONAL_BOUNDARIES_MINUS_3_16_MINUS_1_16_PLUS_K_OVER_2'
    assert data['partition_scope'] == 'FINITE_SOURCE_ORIENTATION_ROOTS_PLUS_EXPLICIT_PHASE_BOUNDARIES'
    for key in FALSE_FLAGS:
        assert data[key] is False, key
    assert set(data['protected_semantics']) == PROTECTED
    assert all(x is True for x in data['protected_semantics'].values())
    assert same(data['programme_effect'], EFFECT)
    assert same(data['resources'], {'native_campaign_run':False, 'paid_campaign_run':False,
                                    'production_authorized':False, 'expensive_execution_authorized':False})
    assert data['unsupported'] == ['GENERAL_NONMONOTONE_COUPLED_ZERO_ISOLATION',
                                   'NONCOMMENSURATE_OR_INDEPENDENT_PHASE_LAWS',
                                   'HEURISTIC_OR_UNBOUNDED_PARTITION_SEARCH',
                                   'NORMALIZED_MAPS_OVER_MULTIPLE_ALGEBRAIC_GENERATORS']
    if not check_repo:
        return
    for path, sha in PINS.items():
        assert blob(ROOT / path) == sha, 'historical source changed: ' + path
    for path, sha in IMPLEMENTATION_PINS.items():
        assert blob(TASK / path) == sha, 'checked implementation changed: ' + path
    domain = load(MC / 'tasks/MC-002/domain-contract-v1.json')
    assert len(domain['coverage_rule']['required_operation_ids']) == 26
    programme = load(MC / 'programme-v1.json')
    assert programme['capability_status'] == 'NOT_ESTABLISHED'
    assert programme['production_authorized'] is False and programme['expensive_execution_authorized'] is False
    assert {g['id']:g for g in programme['gates']}['MC-B']['state'] == 'NOT_ESTABLISHED'
    pos = {x['id']:x for x in load(MC / 'proof-obligations-v1.json')['obligations']}
    for po in ('PO-04', 'PO-05', 'PO-08'):
        assert pos[po]['state'] == 'OPEN'
    for path in (ROOT / 'docs/machining-completeness/73-PB00701-MIXED-MULTICUT.md', TASK / 'pb00701-report-v49.md'):
        text = path.read_text(encoding='utf-8').lower()
        for token in ('sturm', 'multi-cut', 'not_established', '26 operations'):
            assert token in text, (str(path), token)
    for filename in IMPLEMENTATION_PINS:
        for node in ast.walk(ast.parse((TASK / filename).read_text(encoding='utf-8'))):
            if isinstance(node, ast.Constant):
                assert not isinstance(node.value, float), 'floating proof constant'
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [node.module or ''] if isinstance(node, ast.ImportFrom) else [n.name for n in node.names]
                assert not any(n.split('.')[0] in ('numpy', 'mpmath', 'sympy', 'decimal', 'math') for n in names)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in ('setattr', 'exec', 'eval'), 'dynamic dependency mutation'
    workflow = (ROOT / '.github/workflows/mc1-pb00701-v49.yml').read_text(encoding='utf-8')
    assert 'verify_pb00701_v49.py --contract --self-test' in workflow
    assert 'github.event.pull_request.head.sha || github.sha' in workflow
    import pb00701_mixed_boundary_model as b
    import pb00701_algebraic_monotone_cut_model as v47
    assert (b.L, b.U, b.W, b.K) == (v47.L, v47.U, v47.W, v47.K)


def rejected(fn):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, TypeError):
        return
    raise AssertionError('adversarial metadata mutation was accepted')


def self_test():
    import test_pb00701_mixed_boundary as core
    import test_pb00701_mixed_multicut_integration as integration
    core.run()
    integration.run()
    data = load(TASK / 'pb00701-mixed-boundary-multicut-v49.json')
    for key in FALSE_FLAGS:
        bad = copy.deepcopy(data); bad[key] = True
        rejected(lambda: contract(bad, False))
    for key, value in (('MC-B', 'ESTABLISHED'), ('domain_operation_count', 25), ('domain_narrowed', 0)):
        bad = copy.deepcopy(data); bad['programme_effect'][key] = value
        rejected(lambda: contract(bad, False))
    for key in ('historical_git_blob_pins', 'implementation_git_blob_pins'):
        bad = copy.deepcopy(data); bad[key][next(iter(bad[key]))] = '0' * 40
        rejected(lambda: contract(bad, False))
    bad = copy.deepcopy(data); bad['initial_repository_evidence']['integration_test_methods'] = 0
    rejected(lambda: contract(bad, False))
    bad = copy.deepcopy(data); bad['corrective_issue'] = True
    rejected(lambda: contract(bad, False))
    bad = copy.deepcopy(data); bad['boundary_controls'].pop()
    rejected(lambda: contract(bad, False))
    subprocess.run([sys.executable, str(TASK / 'verify_pb00701_v48.py'), '--contract'], check=True)
    subprocess.run([sys.executable, str(TASK / 'verify_pb00701_v47.py'), '--contract'], check=True)
    print('PB-007-01 v49 mixed-boundary actual-repository self-test: PASS')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--contract', action='store_true')
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--core', action='store_true', help='core tests only; NOT full repository acceptance')
    args = p.parse_args()
    if not (args.contract or args.self_test or args.core):
        p.error('choose --contract and/or --self-test; --core is partial evidence only')
    if args.contract:
        contract(load(TASK / 'pb00701-mixed-boundary-multicut-v49.json'))
        print('PB-007-01 v49 contract: PASS')
    if args.self_test:
        self_test()
    elif args.core:
        import test_pb00701_mixed_boundary as core
        core.run()


if __name__ == '__main__':
    main()
