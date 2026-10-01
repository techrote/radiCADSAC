#!/usr/bin/env python3
"""V48 mixed-root regression, source integration and historical contract checks."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
sys.path.insert(0, str(TASK))
import verify_pb00701_v47 as old

PINS = {
    'pb00701_algebraic_orientation_cut_model.py': 'a56d6487963d269405ab82f3db4cce58a0165520',
    'pb00701_algebraic_child_map_model.py': 'c055e7f392a921b386a1a99cc70b5004121ae7f6',
    'pb00701_algebraic_endpoint_model.py': '77c18cb5c8c0700072c65969c973e8f3c4c12a99',
    'pb00701_algebraic_monotone_cut_model.py': '07b092f9c7df8b3325c2b15d17ca7abe9781cb10',
    'pb00701_algebraic_monotone_cut_certificate.py': 'f98e0e4f506f9b4c5eb247eca4f5a142caa3c4b6',
    'pb00701_algebraic_interval_model.py': '859cb6ee600486198f53bfcc9660e2b482bb54d0',
    'verify_pb00701_v47.py': 'b77e2c2255cfc00fe1bf4d9c3f9efa09ce913725',
}
CONTROLS = {
    'legacy_endpoint_and_mixed_isolation_failures', 'endpoint_rational_irrational_multiplicities',
    'full_source_unique_intervals_and_exact_neighbors', 'rational_only_constant_identity',
    'AB_deduplication_and_algebraic_order', 'enforced_accounting_and_certificate_corruption',
    'actual_source_restored_with_unchanged_derivative_proofs', 'phase_directions_global_coordinates_precedence',
    'finite_checker_without_route_or_sign_search', 'unknown_source_and_unrelated_exception_preservation',
    'resource_refusal',
}
REPAIR = {
    'endpoint_factor_removal': 'ISOLATION_WORKSPACE_ONLY',
    'irrational_interval_uniqueness': 'FULL_ORIGINAL_SQUARE_FREE_SOURCE',
    'multiplicity': 'FULL_ORIGINAL_SOURCE',
    'root_accounting': 'EXACT_OPEN_STURM_COUNT_PLUS_ENDPOINT_RECORDS_ENFORCED',
    'termination': 'FINITE_DISTINCT_ROOT_SEPARATION_NO_CAP',
    'consumer': 'UNCHANGED_V45_V46_V47_THEOREMS_WITH_NEW_SOURCE_REGENERATING_ADAPTER',
    'physical_source_deflated': False, 'global_monkeypatch': False,
    'exception_text_is_source_authority': False, 'full_multi_cut_partition': False,
    'resource_refusal_is_truth': False,
}


def equal(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def contract(data, check_repo=True):
    assert data['schema'] == 'radicadsac-mc038-pb00701-mixed-orientation-roots/48.0'
    assert data['task'] == 'MC-038' and type(data['corrective_issue']) is int and data['corrective_issue'] == 261
    assert data['source_baseline'] == '8033c8102acc0cf1db77b259a56cee5cb85998ea'
    assert data['evidence_class'] == 'DETERMINISTIC_MODEL'
    assert data['decision'] == 'MIXED_ROOT_ISOLATION_AND_PRESERVED_SINGLE_CUT_CONSUMPTION_REPAIRED'
    assert equal(data['repair'], REPAIR) and data['historical_git_blob_pins'] == PINS
    assert set(data['boundary_controls']) == CONTROLS and len(data['boundary_controls']) == len(CONTROLS)
    assert equal(data['programme_effect'], old.EFFECT)
    assert set(data['protected_semantics']) == old.PROTECTED
    assert all(x is True for x in data['protected_semantics'].values())
    assert equal(data['resources'], {'native_campaign_run': False, 'paid_campaign_run': False,
                                    'production_authorized': False, 'expensive_execution_authorized': False})
    if not check_repo:
        return
    for path, digest in PINS.items():
        raw = (TASK / path).read_bytes()
        assert hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == digest, path
    old.contract(old.load(TASK / 'pb00701-algebraic-single-cut-v47.json'))
    for name in ('pb00701_mixed_orientation_roots_model.py', 'pb00701_mixed_orientation_consumer.py'):
        tree = ast.parse((TASK / name).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                assert not isinstance(node.value, float), 'floating authority constant'
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [node.module or ''] if isinstance(node, ast.ImportFrom) else [n.name for n in node.names]
                assert all(not n.startswith(('sympy', 'numpy', 'mpmath', 'unittest.mock')) for n in names)
    for path in (TASK / 'pb00701-report-v48.md', ROOT / 'docs/machining-completeness/72-PB00701-MIXED-ROOT-REPAIR.md'):
        text = path.read_text().lower()
        for word in ('source', 'isolation', 'not_established', '26 operations'):
            assert word in text, (path, word)
    workflow = (ROOT / '.github/workflows/mc1-pb00701-v48.yml').read_text()
    assert 'verify_pb00701_v48.py --contract --self-test' in workflow


def self_test():
    import test_pb00701_mixed_orientation_roots as tests
    tests.run()
    data = old.load(TASK / 'pb00701-mixed-orientation-roots-v48.json')
    for section, key, value in (('programme_effect', 'MC-B', 'ESTABLISHED'),
                                ('programme_effect', 'domain_operation_count', 25),
                                ('repair', 'resource_refusal_is_truth', True),
                                ('repair', 'physical_source_deflated', True),
                                ('repair', 'exception_text_is_source_authority', True)):
        bad = copy.deepcopy(data); bad[section][key] = value
        old.rejected(lambda: contract(bad, False))
    print('PB-007-01 v48 mixed-root repair self-test: PASS')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if not (args.contract or args.self_test): parser.error('select --contract and/or --self-test')
    if args.contract:
        contract(old.load(TASK / 'pb00701-mixed-orientation-roots-v48.json'))
        print('PB-007-01 v48 contract: PASS')
    if args.self_test: self_test()

if __name__ == '__main__': main()
