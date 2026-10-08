#!/usr/bin/env python3
"""Persist already-read GitHub JSON, checking immutable Git blob identities.
Does not call repository code, the network, or any verifier.
"""
from pathlib import Path
import ast
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
BASE='9734776b3cef3d7039be9623e8872df2c2a85174'
TASK='research/machining-completeness/tasks/MC-038/'

def retain(path, obj, expected):
    raw=(json.dumps(obj,indent=2)+'\n').encode()
    actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if actual != expected:
        raise ValueError(f'Git blob mismatch for {path}: {actual}, expected {expected}')
    target=ROOT/'source/main'/path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(raw)
    manifest=ROOT/'records/exported-blobs.json'
    rows=json.loads(manifest.read_text())
    rows=[r for r in rows if r['local_path']!='source/main/'+path]
    rows.append(dict(local_path='source/main/'+path,repository_path=path,commit=BASE,
                     git_blob=expected,method='Read full immutable JSON via GitHub.fetch_file; persisted byte-identically with Git blob hash assertion'))
    manifest.write_text(json.dumps(rows,indent=2)+'\n')

retain('handoffs/current-authority.json', {
  'schema':'radicadsac-current-authority/1.0','programme':'MC-1',
  'decision':'docs/decisions/DR-0026-machining-completeness-programme.md',
  'entrypoint':'docs/machining-completeness/00-PROGRAMME.md',
  'production_authorized':False,'capability_status':'NOT_ESTABLISHED',
  'historical_foundation':{'gate5_status':'accepted','consistency_revision':'2.1',
   'release_manifest':'handoffs/genesis-release-v2.json','evidence_manifest':'handoffs/evidence-dependencies-v2.1.json',
   'baseline_commit':'e86c15ca0479240a0045ebc80c83973137b58c60'},
  'requirements_before_production_consideration':['MC-1 accepted against all required gates and proof obligations',
    'Separate explicit authorization to create or populate production repositories']},
  'fa0233323a0804d8a5d3eb7cd892a274a6173fab')

# Reuse literal arrays from the already byte-verified v53 verifier, not its
# expected_boundary() function, which would import an unrecovered predecessor.
tree=ast.parse((ROOT/'source/main'/TASK/'verify_pb00701_v53.py').read_text())
const={}
for node in tree.body:
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
        try: const[node.targets[0].id]=ast.literal_eval(node.value)
        except (ValueError,TypeError): pass
boundary={
 'schema':'radicadsac-mc038-pb00701-mixed-owner-spans/53.0',
 'task':'MC-038','corrective_issue':271,'source_baseline':const['BASE'],
 'evidence_class':'DETERMINISTIC_MODEL','decision':'BOUNDED_CONTINUOUS_MIXED_OWNER_SOURCE_CERTIFICATE',
 'acceptance_authority':'EXECUTED_REPOSITORY_SELF_TEST_AND_VERIFIED_ISSUE_LEDGER',
 'source_interface':'ORIGINAL_RATIONAL_BSPLINE_CONTROLS_KNOTS_ID_INTERVAL_AND_AFFINE_PHASE',
 'inherited_contract':'verify_pb00701_v52.py','historical_additional_git_blob_pins':const['PINS'],
 'ordered_evidence_kinds':['V51_PRODUCT','STRICT_SPAN'],'strict_owner_versions':[19,47,48,49],
 'finite_checking_policy':'SUPPLIED_OWNER_RECIPE_AND_EXACT_RATIONAL_TURN_REGENERATION_NO_REPLACEMENT_SEARCH',
 **const['FLAGS'],'boundary_controls':const['CONTROLS'],'unsupported':const['UNSUPPORTED'],
 'primary_acceptance':{'source':'test_pb00701_mixed_owner_span_integration.candidate',
  'original_source_pieces':2,'physical_owners':[50,19],'open_roots':2,'open_crossings':1,
  'open_tangencies':1,'shared_knot_relation':'POSITIVE','maximal_signs':[-1,1,1]},
 'programme_effect':{'PB-007-01':'OPEN','PB-007-02':'OPEN_DEPENDENT_ON_PB-007-01','PB-007-03':'OPEN',
  'PB-007-04':'OPEN_PROPAGATED','PO-04':'OPEN','PO-05':'OPEN','PO-08':'OPEN','MC-B':'NOT_ESTABLISHED',
  'MC-1':'NOT_ESTABLISHED','domain_operation_count':26,'domain_narrowed':False},
 'other_open_obligations':['PO-02','PO-07'],
 'protected_semantics':{key:True for key in ('source_audio_provenance','canonical_journal','exact_time_path_phase',
  'source_uncertainty','positive_volume_material','cutter_holder_access','durable_body_lineage','refusal_uncertified','conventional_step')},
 'resources':{'native_campaign_run':False,'paid_campaign_run':False,'production_authorized':False,'expensive_execution_authorized':False}}
retain(TASK+'pb00701-mixed-owner-spans-v53.json',boundary,'006ceb86365616462de3b77689950e9b849d349d')
print('Retained current authority and v53 boundary: both exact Git blob identities match.')
