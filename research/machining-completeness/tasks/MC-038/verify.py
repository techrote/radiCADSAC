#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MC = ROOT / 'research' / 'machining-completeness'
TASK = MC / 'tasks' / 'MC-038'
REVIEW = TASK / 'constructive-coverage-review-v1.json'
RETRY = TASK / 'gate-scope-retry-v2.json'
OUTCOME = TASK / 'outcome.json'
REPORT = TASK / 'report.md'
PROGRAMME = MC / 'programme-v1.json'
PROOFS = MC / 'proof-obligations-v1.json'
OUTCOMES = MC / 'outcomes-v1.json'
GRAPH = MC / 'task-graph-v1.json'
DOMAIN = MC / 'tasks' / 'MC-002' / 'domain-contract-v1.json'
WORKFLOW = ROOT / '.github' / 'workflows' / 'mc1-static.yml'
EXPECTED_BASE = 'e82f417b0474a51648928f26d1035d39860777b0'
EXPECTED_RETRY_BASE = '7a480da12e46764ed972c814df3991ebbf0baee5'
EXPECTED_BLOCKERS = {
    'PB-007-01','PB-007-02','PB-007-03','PB-007-04',
    'RB-016-01','RB-016-02','RB-016-03','RB-016-04','RB-016-05'
}
PRE_GATE_BLOCKERS = {'PB-007-01','PB-007-02','PB-007-03','PB-007-04'}
DOWNSTREAM_RB = {'RB-016-01','RB-016-02','RB-016-03','RB-016-04','RB-016-05'}
DECISIVE_OPEN_POS_V1 = {'PO-02','PO-03','PO-04','PO-05','PO-07','PO-08','PO-09'}
PRE_GATE_OPEN_POS = {'PO-02','PO-04','PO-05','PO-07','PO-08'}
DOWNSTREAM_OPEN_POS = {'PO-03':'MC-039','PO-06':'MC-037','PO-09':'MC-037'}
PRE_GATE_REPAIR_TASKS = {'MC-031','MC-032','MC-033'}
POST_GATE_RECON_TASKS = {'MC-034','MC-035','MC-036','MC-037'}


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()


def required_operation_count() -> int:
    d = load(DOMAIN)
    return len(d['coverage_rule']['required_operation_ids'])


def task_map(graph):
    return {t['id']: t for t in graph['tasks']}


def validate_review(review, check_repo=True):
    """Preserve and validate the historical v1 blocked review unchanged."""
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
    assert set(review['required_open_proof_obligations']) == DECISIVE_OPEN_POS_V1
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
    for po in DECISIVE_OPEN_POS_V1:
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
            assert DOWNSTREAM_RB <= ids

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


def validate_retry(retry, check_repo=True):
    assert retry['schema'] == 'radicadsac-mc038-gate-scope-retry/2.0'
    assert retry['task'] == 'MC-038' and retry['issue'] == 100
    assert retry['corrective_issue'] == 162
    assert retry['source_baseline'] == EXPECTED_RETRY_BASE
    assert retry['decision'] == 'BLOCKED_DO_NOT_PROMOTE'
    assert retry['gate'] == 'MC-B' and retry['gate_state'] == 'NOT_ESTABLISHED'

    hist = retry['historical_review']
    assert hist['path'] == 'research/machining-completeness/tasks/MC-038/constructive-coverage-review-v1.json'
    assert hist['blob_sha'] == '9042bec1a77d36cfe64de8a13c579a460c926176'
    assert hist['preserved_as_historical_negative_evidence'] is True

    producers = {p['task']: p for p in retry['producing_owner_evidence']}
    assert set(producers) == PRE_GATE_REPAIR_TASKS
    expected_blobs = {
        'MC-031': ('4aa539cd6cc37212e258dd2ba0d984a2e0d8346c','dffac14b7e1381f966641485827b2df968d92144'),
        'MC-032': ('b713bb17199d1973e13815c84e6b84c72e980f1c','bc42e0f824621af10354534dc83aa03765a893ed'),
        'MC-033': ('ff7f49eb8c7c4f6439d0baf5741d4b3e8b04cef2','5bd663c1aa098224f5909d8781009c13f50e40e4'),
    }
    for tid, (report_sha, outcome_sha) in expected_blobs.items():
        assert producers[tid]['report_blob_sha'] == report_sha
        assert producers[tid]['outcome_blob_sha'] == outcome_sha
        assert producers[tid]['surviving_claims']

    scope = retry['gate_scope']
    assert 'before full native implementation claims' in scope['canonical_mc_b_requirement']
    pre = {b['id']: b for b in scope['pre_gate_blockers']}
    assert set(pre) == PRE_GATE_BLOCKERS
    assert all(b['status'].startswith('OPEN') for b in pre.values())
    assert set(scope['required_pre_gate_open_proof_obligations']) == PRE_GATE_OPEN_POS
    downstream = scope['downstream_open_not_mc_b_prerequisites']
    rbs = {b['id']: b for b in downstream['representation_blockers']}
    assert set(rbs) == DOWNSTREAM_RB
    assert all(b['status'] == 'OPEN' for b in rbs.values())
    dpos = {p['id']: p for p in downstream['proof_obligations']}
    assert set(dpos) == set(DOWNSTREAM_OPEN_POS)
    for po, owner in DOWNSTREAM_OPEN_POS.items():
        assert dpos[po]['state'] == 'OPEN' and dpos[po]['owner'] == owner
    assert scope['no_status_changes'] is True

    graph_contract = retry['graph_contract']
    assert set(graph_contract['pre_gate_producers']) == PRE_GATE_REPAIR_TASKS
    assert set(graph_contract['post_gate_reconstruction_tasks']) == POST_GATE_RECON_TASKS
    assert graph_contract['post_gate_integration_task'] == 'MC-039'
    assert graph_contract['post_gate_reconstruction_tasks_retain_mc038_capability'] is True
    assert graph_contract['mc039_consumes_reconstruction_artifacts'] is True
    assert graph_contract['move_native_work_before_gate'] is False

    resources = retry['resources']
    assert resources['domain_operation_count'] == 26
    assert resources['native_campaign_run'] is False
    assert resources['paid_campaign_run'] is False
    assert resources['production_authorized'] is False
    assert resources['expensive_execution_authorized'] is False
    assert all(retry['protected_semantics'].values())
    assert retry['next_repair']['priority'][0] == 'PB-007-01'
    assert retry['next_repair']['mc_b_retry_allowed_only_after_required_pre_gate_claims_close'] is True

    if not check_repo:
        return

    assert git_blob_sha(REVIEW) == hist['blob_sha'], 'historical MC-038 v1 review mutated'
    for tid, p in producers.items():
        assert git_blob_sha(ROOT / p['report_path']) == p['report_blob_sha'], f'{tid} report evidence drift'
        assert git_blob_sha(ROOT / p['outcome_path']) == p['outcome_blob_sha'], f'{tid} outcome evidence drift'

    assert required_operation_count() == 26
    programme = load(PROGRAMME)
    gates = {g['id']: g for g in programme['gates']}
    assert gates['MC-B']['state'] == 'NOT_ESTABLISHED'
    assert programme['capability_status'] == 'NOT_ESTABLISHED'
    assert programme['production_authorized'] is False and programme['expensive_execution_authorized'] is False

    proofs = {p['id']: p for p in load(PROOFS)['obligations']}
    for po in PRE_GATE_OPEN_POS:
        assert proofs[po]['state'] == 'OPEN', f'{po} must remain an explicit pre-gate blocker'
    for po, owner in DOWNSTREAM_OPEN_POS.items():
        assert proofs[po]['state'] == 'OPEN', f'{po} falsely closed by gate-scope repair'
        assert proofs[po]['integration_owner'] == owner, f'{po} owner drift'

    registry = load(OUTCOMES)['tasks']
    assert registry['MC-038']['state'] == 'NOT_STARTED'
    for source in ('MC-016','MC-054'):
        ids = {b['id'] for b in registry[source].get('blockers', [])}
        assert DOWNSTREAM_RB <= ids, f'{source} representation blockers erased'

    graph = load(GRAPH)
    tm = task_map(graph)
    for tid in PRE_GATE_REPAIR_TASKS:
        deps = {(d['task'], d['type']) for d in tm[tid]['dependencies']}
        assert ('MC-038','capability') not in deps
        assert ('MC-005','capability') in deps
    for tid in POST_GATE_RECON_TASKS:
        deps = {(d['task'], d['type']) for d in tm[tid]['dependencies']}
        assert ('MC-038','capability') in deps, f'{tid} lost legitimate post-gate MC-038 dependency'
    mc039_deps = {(d['task'], d['type']) for d in tm['MC-039']['dependencies']}
    for tid in ('MC-031','MC-032','MC-033','MC-034','MC-035','MC-036','MC-037'):
        assert (tid,'artifact') in mc039_deps, f'MC-039 lost {tid} implementation artifact dependency'

    text = REPORT.read_text(encoding='utf-8').lower()
    for token in ('orch-038-02', 'gate-scope', 'post-gate', 'pb-007-01', 'rb-016-01', 'po-03', 'po-09'):
        assert token in text, f'report missing retry reconciliation token {token}'


def expect_v1_rejected(mutator):
    obj = copy.deepcopy(load(REVIEW))
    mutator(obj)
    try:
        validate_review(obj, check_repo=False)
    except Exception:
        return
    raise AssertionError('historical-review adversarial mutation accepted')


def expect_retry_rejected(mutator):
    obj = copy.deepcopy(load(RETRY))
    mutator(obj)
    try:
        validate_retry(obj, check_repo=False)
    except Exception:
        return
    raise AssertionError('gate-scope adversarial mutation accepted')


def self_test():
    validate_review(load(REVIEW), check_repo=False)
    validate_retry(load(RETRY), check_repo=False)

    v1_attacks = [
        lambda r: r.__setitem__('decision','CAPABILITY_ACCEPTED'),
        lambda r: r.__setitem__('gate_state','ACCEPTED'),
        lambda r: r['dependency_review'].__setitem__('domain_operation_count',25),
        lambda r: r['blocking_lemmas'].pop(),
        lambda r: r['blocking_lemmas'][0].__setitem__('status','CLOSED'),
        lambda r: r.__setitem__('required_open_proof_obligations',['PO-05']),
        lambda r: r['dependency_inversion'].__setitem__('present',True),
        lambda r: r['protected_semantics'].__setitem__('positive_volume_material_preserved',False),
        lambda r: r['resource_policy'].__setitem__('production_authorized',True),
    ]
    for attack in v1_attacks:
        expect_v1_rejected(attack)

    retry_attacks = [
        lambda r: r.__setitem__('gate_state','ACCEPTED'),
        lambda r: r['gate_scope']['pre_gate_blockers'].pop(),
        lambda r: r['gate_scope']['pre_gate_blockers'][0].__setitem__('status','CLOSED'),
        lambda r: r['gate_scope'].__setitem__('required_pre_gate_open_proof_obligations',['PO-05']),
        lambda r: r['gate_scope']['pre_gate_blockers'].append({'id':'RB-016-01','status':'OPEN','reason':'wrongly promoted downstream blocker'}),
        lambda r: r['gate_scope']['downstream_open_not_mc_b_prerequisites']['representation_blockers'][0].__setitem__('status','CLOSED'),
        lambda r: r['gate_scope']['downstream_open_not_mc_b_prerequisites']['proof_obligations'][0].__setitem__('state','ACCEPTED'),
        lambda r: r['graph_contract'].__setitem__('post_gate_reconstruction_tasks_retain_mc038_capability',False),
        lambda r: r['graph_contract'].__setitem__('move_native_work_before_gate',True),
        lambda r: r['resources'].__setitem__('domain_operation_count',25),
        lambda r: r['resources'].__setitem__('native_campaign_run',True),
        lambda r: r['protected_semantics'].__setitem__('durable_body_lineage_preserved',False),
        lambda r: r['historical_review'].__setitem__('preserved_as_historical_negative_evidence',False),
        lambda r: r['next_repair'].__setitem__('priority',['PB-007-04']),
    ]
    for attack in retry_attacks:
        expect_retry_rejected(attack)
    print('MC-038 adversarial blocker/gate-scope self-test passed')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if not (args.contract or args.self_test):
        ap.error('choose --contract or --self-test')
    if args.contract:
        validate_review(load(REVIEW), check_repo=True)
        validate_retry(load(RETRY), check_repo=True)
        print('MC-038 blocked gate-review and corrected gate-scope verification passed')
    if args.self_test:
        self_test()


if __name__ == '__main__':
    main()
