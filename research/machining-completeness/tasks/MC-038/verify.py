#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / 'research' / 'machining-completeness'
TASK = MC / 'tasks' / 'MC-038'
REVIEW = TASK / 'constructive-coverage-review-v1.json'
OUTCOME = TASK / 'outcome.json'
REPORT = TASK / 'report.md'
PROGRAMME = MC / 'programme-v1.json'
PROOFS = MC / 'proof-obligations-v1.json'
OUTCOMES = MC / 'outcomes-v1.json'
GRAPH = MC / 'task-graph-v1.json'
DOMAIN = MC / 'tasks' / 'MC-002' / 'domain-contract-v1.json'
WORKFLOW = ROOT / '.github' / 'workflows' / 'mc1-static.yml'
EXPECTED_BASE = 'e82f417b0474a51648928f26d1035d39860777b0'
EXPECTED_BLOCKERS = {
    'PB-007-01','PB-007-02','PB-007-03','PB-007-04',
    'RB-016-01','RB-016-02','RB-016-03','RB-016-04','RB-016-05'
}
DECISIVE_OPEN_POS = {'PO-02','PO-03','PO-04','PO-05','PO-07','PO-08','PO-09'}
PRE_GATE_REPAIR_TASKS = {'MC-031','MC-032','MC-033'}


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def required_operation_count() -> int:
    d = load(DOMAIN)
    return len(d['coverage_rule']['required_operation_ids'])


def task_map(graph):
    return {t['id']: t for t in graph['tasks']}


def validate_review(review, check_repo=True):
    assert review['schema'] == 'radicadsac-mc038-constructive-coverage-review/1.0'
    assert review['task'] == 'MC-038' and review['issue'] == 100
    assert review['source_baseline'] == EXPECTED_BASE
    assert review['decision'] == 'BLOCKED_DO_NOT_PROMOTE'
    assert review['gate'] == 'MC-B' and review['gate_state'] == 'NOT_ESTABLISHED'
    assert review['dependency_review']['domain_operation_count'] == 26
    assert review['dependency_review']['capability_dependencies_consumed'] == ['MC-005']
    assert set(review['dependency_review']['artifact_dependencies_consumed']) == {
        'MC-006','MC-007','MC-008','MC-016','MC-018','MC-019','MC-020','MC-021','MC-022','MC-023','MC-026','MC-054','MC-058'
    }
    blockers = {b['id']: b for b in review['blocking_lemmas']}
    assert set(blockers) == EXPECTED_BLOCKERS
    assert all(b['status'].startswith('OPEN') for b in blockers.values())
    assert set(review['required_open_proof_obligations']) == DECISIVE_OPEN_POS
    inv = review['dependency_inversion']
    assert inv['present'] is False
    assert inv['resolved_by_issue'] == 156
    assert set(inv['affected_tasks']) == PRE_GATE_REPAIR_TASKS
    assert len(review['repair_path']) == 5
    assert review['repair_path'][0].startswith('Correct the MC-038 -> MC-031/MC-032/MC-033')
    protected = review['protected_semantics']
    assert protected and all(protected.values())
    resources = review['resource_policy']
    assert resources['native_campaign_run'] is False
    assert resources['paid_campaign_run'] is False
    assert resources['production_authorized'] is False
    assert resources['expensive_execution_authorized'] is False
    if not check_repo:
        return

    assert required_operation_count() == 26, 'frozen domain denominator drift'
    programme = load(PROGRAMME)
    gates = {g['id']: g for g in programme['gates']}
    assert gates['MC-A']['state'] == 'ACCEPTED'
    assert gates['MC-B']['owner'] == 'MC-038' and gates['MC-B']['state'] == 'NOT_ESTABLISHED'
    assert programme['capability_status'] == 'NOT_ESTABLISHED'
    assert programme['production_authorized'] is False
    assert programme['expensive_execution_authorized'] is False

    proofs = {p['id']: p for p in load(PROOFS)['obligations']}
    for po in DECISIVE_OPEN_POS:
        assert proofs[po]['state'] == 'OPEN', f'{po} unexpectedly not open'
    assert proofs['PO-05']['integration_owner'] == 'MC-038'
    po5 = proofs['PO-05']['quantified_statement'].lower()
    assert 'proof blocker keeps po-05 open' in po5
    assert 'timeout' in po5 and 'provider cycling' in po5

    registry = load(OUTCOMES)['tasks']
    assert registry['MC-038']['state'] == 'NOT_STARTED', 'blocked gate review must remain retryable, not accepted'
    for source in ('MC-007','MC-008','MC-016','MC-020','MC-022','MC-026','MC-054','MC-058'):
        ids = {b['id'] for b in registry[source].get('blockers', [])}
        if source in {'MC-007','MC-008'}:
            assert {'PB-007-01','PB-007-02','PB-007-03','PB-007-04'} <= ids
        if source in {'MC-016','MC-054'}:
            assert {'RB-016-01','RB-016-02','RB-016-03','RB-016-04','RB-016-05'} <= ids

    graph = load(GRAPH)
    tm = task_map(graph)
    packages = {p['id']: p for p in graph['packages']}
    assert PRE_GATE_REPAIR_TASKS <= set(packages['MG-07']['tasks'])
    assert 'MC-038' in packages['MG-08']['tasks']
    assert graph['package_order'].index('MG-07') < graph['package_order'].index('MG-08')
    for tid in PRE_GATE_REPAIR_TASKS:
        deps = {(d['task'], d['type']) for d in tm[tid]['dependencies']}
        assert ('MC-038','capability') not in deps, f'{tid} circular MC-038 dependency reintroduced'
        assert ('MC-005','capability') in deps, f'{tid} missing accepted MC-A pre-gate authority'
    assert tm['MC-038']['gate'] == 'MC-B'
    assert 'no required lemma is OPEN' in ' '.join(tm['MC-038']['acceptance'])

    outcome = load(OUTCOME)
    assert outcome['task'] == 'MC-038' and outcome['issue'] == 100
    assert outcome['result_kind'] == 'BLOCKED' and outcome['source_baseline'] == EXPECTED_BASE
    assert outcome['native_execution'] is False
    assert outcome['resources']['native_or_paid_campaign_run'] is False
    assert outcome['resources']['required_domain_operation_count'] == 26
    assert outcome['review']['gate_changed'] is False
    assert outcome['review']['gate_state'] == 'NOT_ESTABLISHED'
    assert outcome['review']['issue_must_remain_open'] is True
    out_ids = {b['id'] for b in outcome['blockers']}
    assert EXPECTED_BLOCKERS <= out_ids and 'ORCH-038-01' in out_ids

    text = REPORT.read_text(encoding='utf-8').lower()
    for token in ('blocked', 'mc-b remains `not_established`', 'pb-007-01', 'pb-007-02', 'pb-007-03', 'pb-007-04',
                  'rb-016-01', 'rb-016-05', 'dependency inversion', '26-operation', 'source/audio/provenance'):
        assert token in text

    workflow = WORKFLOW.read_text(encoding='utf-8')
    assert 'tasks/MC-038/verify.py' in workflow
    assert 'mc_workflow.py verify MC-038' in workflow


def expect_rejected(mutator):
    obj = copy.deepcopy(load(REVIEW))
    mutator(obj)
    try:
        validate_review(obj, check_repo=False)
    except Exception:
        return
    raise AssertionError('adversarial mutation accepted')


def self_test():
    validate_review(load(REVIEW), check_repo=False)
    attacks = [
        lambda r: r.__setitem__('decision','CAPABILITY_ACCEPTED'),
        lambda r: r.__setitem__('gate_state','ACCEPTED'),
        lambda r: r['dependency_review'].__setitem__('domain_operation_count',25),
        lambda r: r['blocking_lemmas'].pop(),
        lambda r: r['blocking_lemmas'][0].__setitem__('status','CLOSED'),
        lambda r: r.__setitem__('required_open_proof_obligations',['PO-05']),
        lambda r: r['dependency_inversion'].__setitem__('present',True),
        lambda r: r['dependency_inversion'].__setitem__('affected_tasks',['MC-031']),
        lambda r: r['protected_semantics'].__setitem__('positive_volume_material_preserved',False),
        lambda r: r['resource_policy'].__setitem__('production_authorized',True),
        lambda r: r['resource_policy'].__setitem__('expensive_execution_authorized',True),
        lambda r: r.__setitem__('repair_path',r['repair_path'][:2]),
    ]
    for attack in attacks:
        expect_rejected(attack)
    print('MC-038 adversarial blocker-review self-test passed')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if not (args.contract or args.self_test):
        ap.error('choose --contract or --self-test')
    if args.contract:
        validate_review(load(REVIEW), check_repo=True)
        print('MC-038 blocked gate-review verification passed')
    if args.self_test:
        self_test()


if __name__ == '__main__':
    main()
