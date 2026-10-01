#!/usr/bin/env python3
"""V45 contract checks and executable falsification suite (no native campaign)."""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MC = ROOT / 'research' / 'machining-completeness'
PREFIX = 'research/machining-completeness/tasks/MC-038/'
BASE = '8b215136ea9d30bc018618525d73d9b97c09b4bc'
PINS = {
    'research/machining-completeness/tasks/MC-032/event_engine.py': '789a709c5141479a343035d1b7055dd4e53534e1',
    PREFIX + 'pb00701_algebraic_orientation_cut_model.py': 'a56d6487963d269405ab82f3db4cce58a0165520',
    PREFIX + 'test_pb00701_algebraic_orientation_cut_adversarial.py': '376e4f376471f0a796b2cd2663a5b17393344a33',
    PREFIX + 'pb00701-algebraic-orientation-cut-v44.json': 'db8aae272996950d0e3c006ec1872c59afb40bc5',
    PREFIX + 'pb00701_orientation_root_partition_model.py': '2f96622b5c69655279d66fe2b36f8f3e03414660',
}
PROTECTED = ('source_audio_provenance', 'canonical_journal', 'exact_time_path_phase',
             'source_uncertainty', 'positive_volume_material', 'cutter_holder_access',
             'durable_body_lineage', 'refusal_uncertified', 'conventional_step')
CONTROLS = ('minimal_factor_not_square_free_quotient', 'canonical_real_embedding',
            'field_zero_equality_inverse_sign', 'both_affine_maps', 'coefficient_roundtrip',
            'amplitude_chain_rule', 'simple_and_even_multiplicity', 'common_AB_identity',
            'nearby_algebraic_order', 'phase_rate_both_directions', 'source_binding_mutations',
            'forged_field_and_child_metadata', 'nonexact_rejection', 'resource_refusal',
            'historical_precedence', 'no_event_promotion', 'frozen_domain')


def require(ok, message):
    if not ok: raise ValueError(message)


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate_artifact(artifact, check_repo=True):
    require(artifact['schema'] == 'radicadsac-mc038-pb00701-algebraic-child-map/45.0', 'schema')
    require(artifact['corrective_issue'] == 255 and artifact['source_baseline'] == BASE, 'owner/base')
    require(artifact['evidence_class'] == 'DETERMINISTIC_MODEL', 'evidence class')
    require(artifact['decision'] == 'EXACT_SINGLE_GENERATOR_CHILD_REPRESENTATION_ESTABLISHED', 'decision')
    require(artifact['historical_git_blob_pins'] == PINS, 'pins')
    require(artifact['boundary_controls'] == list(CONTROLS), 'boundary controls')
    require(artifact['arithmetic']['modulus'] == 'SOURCE_DERIVED_IRREDUCIBLE_MINIMAL_FACTOR', 'not a square-free quotient')
    require(artifact['arithmetic']['factorization'] == 'FINITE_EXACT_KRONECKER_WITH_QUADRATIC_DISCRIMINANT', 'finite factorization')
    require(artifact['arithmetic']['canonical_embedding'] == 'MINIMAL_POLYNOMIAL_REAL_ROOT_INDEX_AND_DYADIC_ISOLATION', 'embedding')
    require(artifact['unsupported'] == ['ALGEBRAIC_IRRATIONAL_PHASE_EVENT_CONSUMPTION', 'MULTI_GENERATOR_COMPOSITUM_AND_FULL_MULTI_CUT_PARTITION'], 'unsupported scope')
    require(artifact['analytic_cut_consumed'] is False, 'must not consume analytic cuts')
    require(artifact['caller_metadata_trusted'] is False, 'must regenerate metadata')
    require(artifact['resource_refusal_is_truth'] is False, 'resource refusal')
    require(artifact['protected_semantics'] == dict.fromkeys(PROTECTED, True), 'protected semantics')
    expected = {'PB-007-01':'OPEN', 'PB-007-02':'OPEN_DEPENDENT_ON_PB-007-01',
                'PB-007-03':'OPEN', 'PB-007-04':'OPEN_PROPAGATED',
                'PO-04':'OPEN', 'PO-05':'OPEN', 'PO-08':'OPEN',
                'MC-B':'NOT_ESTABLISHED', 'MC-1':'NOT_ESTABLISHED',
                'domain_operation_count':26, 'domain_narrowed':False}
    require(artifact['programme_effect'] == expected, 'programme must not be promoted/narrowed')
    require(artifact['resources'] == {'native_campaign_run':False, 'paid_campaign_run':False,
                                    'production_authorized':False, 'expensive_execution_authorized':False}, 'execution permits')
    if not check_repo: return
    for path, digest in PINS.items():
        raw = (ROOT / path).read_bytes()
        actual = hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
        require(actual == digest, 'historical evidence mutated: ' + path)
    domain = load(MC / 'tasks/MC-002/domain-contract-v1.json')
    require(len(domain['coverage_rule']['required_operation_ids']) == 26, 'denominator drift')
    programme = load(MC / 'programme-v1.json')
    require(programme['capability_status'] == 'NOT_ESTABLISHED', 'MC-1 promotion')
    require({x['id']: x['state'] for x in programme['gates']}['MC-B'] == 'NOT_ESTABLISHED', 'MC-B promotion')
    require(programme['production_authorized'] is False and programme['expensive_execution_authorized'] is False, 'permit drift')
    pos = {p['id']:p['state'] for p in load(MC / 'proof-obligations-v1.json')['obligations']}
    require(all(pos[p] == 'OPEN' for p in ('PO-04','PO-05','PO-08')), 'proof promotion')
    for filename in ('pb00701_algebraic_child_map_model.py','test_pb00701_algebraic_child_map.py','test_pb00701_algebraic_child_map_integration.py'):
        compile((HERE / filename).read_text(), filename, 'exec')
    require((ROOT / 'docs/machining-completeness/69-PB00701-ALGEBRAIC-CHILD-MAP.md').is_file(), 'RAG document missing')
    require((HERE / 'pb00701-report-v45.md').is_file(), 'report missing')
    workflow = (ROOT / '.github/workflows/mc1-pb00701-v45.yml').read_text()
    require('verify_pb00701_v45.py --contract --self-test' in workflow, 'missing focused executable gate')
    # Each preserved verifier also checks its own predecessor evidence pins.
    importlib.import_module('verify_pb00701_v44').validate_artifact(load(HERE / 'pb00701-algebraic-orientation-cut-v44.json'))


def self_test():
    import test_pb00701_algebraic_child_map as unit
    import test_pb00701_algebraic_child_map_integration as integration
    unit.run()
    integration.run()
    artifact = load(HERE / 'pb00701-algebraic-child-map-v45.json')
    for path, replacement in ((['analytic_cut_consumed'],True),
                              (['programme_effect','MC-B'],'ESTABLISHED'),
                              (['programme_effect','domain_operation_count'],25),
                              (['arithmetic','modulus'],'ANY_SQUARE_FREE_POLYNOMIAL'),
                              (['caller_metadata_trusted'],True),
                              (['protected_semantics'],{})):
        bad = copy.deepcopy(artifact); target = bad
        for key in path[:-1]: target = target[key]
        target[path[-1]] = replacement
        try: validate_artifact(bad, False)
        except (ValueError, KeyError, TypeError): pass
        else: raise AssertionError('artifact mutation accepted: ' + str(path))
    print('PB-007-01 v45 exact child representation: PASS; analytic event consumption remains BLOCKED')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if not (args.contract or args.self_test): parser.error('choose --contract and/or --self-test')
    if args.contract:
        validate_artifact(load(HERE / 'pb00701-algebraic-child-map-v45.json'))
        print('PB-007-01 v45 contract: PASS')
    if args.self_test: self_test()


if __name__ == '__main__': main()
