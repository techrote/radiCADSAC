#!/usr/bin/env python3
"""V50 exact product contract, physical-source attacks and repository acceptance."""
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
BASE = 'eb76a34405244f842e3b10ae6d45acb22ffef973'
PINS = {'research/machining-completeness/tasks/MC-032/event_engine.py': '789a709c5141479a343035d1b7055dd4e53534e1', 'research/machining-completeness/tasks/MC-038/pb00701_common_factor_model.py': 'eb96654d96717b34d05fd46f875abf0581c492d3', 'research/machining-completeness/tasks/MC-038/pb00701_source_laurent_factor_model.py': '4e656c95a13858ee8ed496149d200a0a321a61a0', 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_child_map_model.py': 'c055e7f392a921b386a1a99cc70b5004121ae7f6', 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_endpoint_model.py': '77c18cb5c8c0700072c65969c973e8f3c4c12a99', 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_endpoint_certificate.py': '92258bbad7fa4cfa1be5413a7253369e73abc318', 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_monotone_cut_model.py': '07b092f9c7df8b3325c2b15d17ca7abe9781cb10', 'research/machining-completeness/tasks/MC-038/pb00701_algebraic_monotone_cut_certificate.py': 'f98e0e4f506f9b4c5eb247eca4f5a142caa3c4b6', 'research/machining-completeness/tasks/MC-038/pb00701_mixed_orientation_roots_model.py': '22ddac25d318082178ba28bee77b5b8021c80734', 'research/machining-completeness/tasks/MC-038/pb00701_mixed_orientation_consumer.py': 'ad14933591ec6caea1ee28431252381015a7edd7', 'research/machining-completeness/tasks/MC-038/pb00701_mixed_boundary_model.py': '4c4c9697b2237790d2e7ac8b96ec1dcdf2398303', 'research/machining-completeness/tasks/MC-038/pb00701_mixed_multicut_model.py': 'd7a0c35dee39514c4d49b91739c01f57866a0bf5', 'research/machining-completeness/tasks/MC-038/pb00701_mixed_multicut_certificate.py': '0d6acd3259346be863e9c40a039f694b1b750c71', 'research/machining-completeness/tasks/MC-038/pb00701_multiharmonic_monotone_anchor_model.py': '38db0b5f1f4549f7ea632db27a5347b3aadd7b1a'}
CONTROLS = {'finite_checker_no_replacement_search', 'historical_pins_precedence', 'actual_predecessor_residual', 'nearby_distinct_roots', 'checked_modulated_simple_carrier', 'rational_coincidence_additive_multiplicity', 'exact_resource_nontruth', 'uncertified_carrier_blocked', 'irrational_disjointness_scoped_laurent', 'maximal_monic_all_amplitudes', 'endpoint_union', 'boolean_float_rejection', 'frozen_26_operations', 'physical_jet_multiplicity', 'source_factor_not_forged_orientation', 'source_and_carrier_corruption', 'exact_source_reconstruction', 'root_free_factor', 'unknown_source_rejection', 'no_false_capability_promotion', 'odd_crossing_even_tangency', 'phase_reversal_global_scaling'}
PROTECTED = {'source_audio_provenance', 'cutter_holder_access', 'refusal_uncertified', 'positive_volume_material', 'exact_time_path_phase', 'durable_body_lineage', 'canonical_journal', 'source_uncertainty', 'conventional_step'}
EFFECT = {'PB-007-01': 'OPEN', 'PB-007-02': 'OPEN_DEPENDENT_ON_PB-007-01', 'PB-007-03': 'OPEN', 'PB-007-04': 'OPEN_PROPAGATED', 'PO-04': 'OPEN', 'PO-05': 'OPEN', 'PO-08': 'OPEN', 'MC-B': 'NOT_ESTABLISHED', 'MC-1': 'NOT_ESTABLISHED', 'domain_operation_count': 26, 'domain_narrowed': False}
RESOURCES = {'native_campaign_run': False, 'paid_campaign_run': False, 'production_authorized': False, 'expensive_execution_authorized': False}
UNSUPPORTED = ['NON_SIMPLE_OR_UNSUPPORTED_CARRIER_CHECKER_OWNER', 'GENERAL_NONCOMMON_FACTOR_NONMONOTONE_COUPLED_EVENTS', 'ORDERED_FULL_ANALYTIC_ROOT_UNION', 'NONCOMMENSURATE_OR_INDEPENDENT_PHASE_LAWS']


def load(path):
    return json.loads(path.read_text())


def blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()


def same(x, y):
    return json.dumps(x, sort_keys=True, allow_nan=False) == json.dumps(y, sort_keys=True, allow_nan=False)


def contract(data, check_repo=True):
    assert data['schema'] == 'radicadsac-mc038-pb00701-vanishing-source-factor/50.0'
    assert data['task'] == 'MC-038' and type(data['corrective_issue']) is int and data['corrective_issue'] == 265
    assert data['source_baseline'] == BASE and data['evidence_class'] == 'DETERMINISTIC_MODEL'
    assert data['decision'] == 'EXACT_PRODUCT_ROUTE_WITH_EXPLICIT_SIMPLE_CARRIER_SCOPE'
    assert data['acceptance_authority'] == 'EXECUTED_REPOSITORY_SELF_TEST_AND_VERIFIED_ISSUE_LEDGER'
    import pb00701_vanishing_source_factor_model as m
    assert data['allowed_carrier_owners'] == list(m.OWNERS)
    assert set(data['boundary_controls']) == CONTROLS and len(data['boundary_controls']) == len(CONTROLS)
    assert data['historical_git_blob_pins'] == PINS
    for key in ('physical_product_strict_monotonicity_claimed', 'ordered_full_analytic_root_list_claimed',
                'general_nonmonotone_solver_claimed', 'physical_source_replaced_by_carrier',
                'resource_refusal_is_truth', 'caller_certificates_trusted'):
        assert data[key] is False
    assert set(data['protected_semantics']) == PROTECTED and all(x is True for x in data['protected_semantics'].values())
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
    for po in ('PO-04', 'PO-05', 'PO-08'):
        assert obligations[po]['state'] == 'OPEN'
    for path in (TASK / 'pb00701-report-v50.md', ROOT / 'docs/machining-completeness/74-PB00701-VANISHING-FACTOR.md'):
        text = path.read_text().lower()
        for token in ('carrier', 'multiplicity', 'rational', 'disjoint', 'not_established', '26 operations'):
            assert token in text, (path, token)
    for name in ('pb00701_vanishing_source_factor_model.py', 'pb00701_vanishing_source_factor_certificate.py'):
        for node in ast.walk(ast.parse((TASK / name).read_text())):
            if isinstance(node, ast.Constant):
                assert not isinstance(node.value, float), 'floating truth constant'
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = ([node.module or ''] if isinstance(node, ast.ImportFrom) else [x.name for x in node.names])
                assert all(not n.startswith(('numpy', 'mpmath', 'decimal', 'sympy')) for n in names)
                if isinstance(node, ast.ImportFrom) and node.module == 'math':
                    assert {x.name for x in node.names} <= {'comb'}
    assert 'verify_pb00701_v50.py --contract --self-test' in (ROOT / '.github/workflows/mc1-pb00701-v50.yml').read_text()


def rejected(fn):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, TypeError):
        return
    raise AssertionError('adversarial contract mutation accepted')


def self_test():
    import test_pb00701_vanishing_source_factor as core
    import test_pb00701_vanishing_source_factor_integration as integration
    core.run()
    integration.run()
    data = load(TASK / 'pb00701-vanishing-source-factor-v50.json')
    for key in ('physical_product_strict_monotonicity_claimed', 'general_nonmonotone_solver_claimed',
                'caller_certificates_trusted', 'resource_refusal_is_truth'):
        bad = copy.deepcopy(data); bad[key] = True
        rejected(lambda: contract(bad, False))
    for key, value in (('MC-B', 'ESTABLISHED'), ('domain_operation_count', 25)):
        bad = copy.deepcopy(data); bad['programme_effect'][key] = value
        rejected(lambda: contract(bad, False))
    bad = copy.deepcopy(data); bad['historical_git_blob_pins'][next(iter(PINS))] = '0' * 40
    rejected(lambda: contract(bad, False))
    subprocess.run([sys.executable, str(TASK / 'verify_pb00701_v49.py'), '--contract'], check=True)
    subprocess.run([sys.executable, str(TASK / 'verify_pb00701_v48.py'), '--contract'], check=True)
    print('PB-007-01 v50 physical factor-carrier union self-test: PASS')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    opts = parser.parse_args()
    if not (opts.contract or opts.self_test):
        parser.error('choose --contract and/or --self-test')
    if opts.contract:
        contract(load(TASK / 'pb00701-vanishing-source-factor-v50.json'))
        print('PB-007-01 v50 contract: PASS')
    if opts.self_test:
        self_test()


if __name__ == '__main__':
    main()
