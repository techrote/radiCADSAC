"""Pinned frozen original-source and parametric mathematical threshold receipt."""
import argparse
import copy
import json
import subprocess
from fractions import Fraction as Q
from pathlib import Path
from pb00701_v12_affine_threshold import (CASE,SOURCE_SHA,ROW_SHA,CORPUS_BLOB,EVIDENCE_BLOB,
    Refusal,source_spec,canonical_sha,classify,strict_near_case,self_test)

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT/'pb00701-finite-owner-corpus-v54.json'
RECON = ROOT/'pb00701-post-v54-evidence-reconciliation-v2.json'
RECEIPT = ROOT/'pb00701-v12-affine-threshold.json'
EXPECTED_SPANS=[['PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC','CERTIFIED',None],
                ['PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF','BLOCKED',
                 'CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED']]

def blob_sha(path):
    try:
        return subprocess.check_output(['git','hash-object',str(path)],text=True).strip()
    except (OSError,subprocess.CalledProcessError) as e:
        raise Refusal('cannot establish frozen Git blob identity') from e

def canonical_data(path):
    raw=path.read_bytes()
    if len(raw)>1000000: raise Refusal('source data byte budget exceeded')
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out: raise Refusal('duplicate JSON key')
            out[k]=v
        return out
    try: return json.loads(raw,object_pairs_hook=unique)
    except (ValueError,UnicodeDecodeError) as e: raise Refusal('invalid source JSON') from e

def check_original(row,evidence):
    if row.get('id')!=CASE or row.get('origin')!='v19' or row.get('kind')!='COMPOSITE_TAIL':
        raise Refusal('historical original ID/origin drift')
    if canonical_sha(row.get('spec'))!=SOURCE_SHA or row['spec']!=source_spec(Q(1,3)):
        raise Refusal('original B-spline controls/phase/knot/hash mismatch')
    if canonical_sha(row)!=ROW_SHA:
        raise Refusal('original full case row hash mismatch')
    expected=row.get('expected')
    if expected!={'id':CASE,'observed':{'status':'BLOCKED','spans':EXPECTED_SPANS},'v54_disposition':'BLOCKED'}:
        raise Refusal('old V12/V43 refusal or whole-case disposition drift')
    if not isinstance(evidence,dict) or evidence.get('case_id')!=CASE or evidence.get('source_sha256')!=SOURCE_SHA or evidence.get('original_row_sha256')!=ROW_SHA:
        raise Refusal('v2 source evidence identity mismatch')
    if evidence.get('registered_evidence_level')!='COMPLETE_SOURCE_SPECIFIC' or evidence.get('prior_v1_registered_evidence_level')!='PARTIAL_REFUSED_TAIL_ONLY' or evidence.get('historical_disposition_changed') is not False:
        raise Refusal('historical source evidence promoted or drifted')
    return True

def receipt():
    if blob_sha(CORPUS)!=CORPUS_BLOB or blob_sha(RECON)!=EVIDENCE_BLOB:
        raise Refusal('pinned corpus/reconciliation Git blob mismatch')
    c=canonical_data(CORPUS); v=canonical_data(RECON)
    if len(c['cases'])!=121 or len({i['id'] for i in c['cases']})!=121:
        raise Refusal('historical case denominator or identity changed')
    if c['summary']['v54_dispositions'].get('BLOCKED')!=20 or c['summary']['v54_dispositions'].get('BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE')!=30:
        raise Refusal('historical v54 refusal/order census changed')
    s=v['summary']
    if s.get('total_historical_unresolved_source_cases')!=50 or s.get('by_registered_evidence_level',{}).get('COMPLETE_SOURCE_SPECIFIC')!=50:
        raise Refusal('v2 accepted source evidence census changed')
    matches=[q for q in c['cases'] if q['id']==CASE]
    witnesses=[q for q in v['source_cases'] if q['case_id']==CASE]
    if len(matches)!=1 or len(witnesses)!=1: raise Refusal('original frozen case/witness absent')
    check_original(matches[0],witnesses[0])
    variants=[classify(a) for a in (Q(1,3),Q(1,2),Q(2,3))]
    return {
        'schema':'radicadsac-mc038-v12-affine-threshold/1.0',
        'evidence_class':'DETERMINISTIC_MODEL',
        'original_source_case_id':CASE,
        'original_source_sha256':SOURCE_SHA,
        'original_row_sha256':ROW_SHA,
        'historical_v54_raw_refusal_retained':'V43 CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED',
        'historical_complete_source_witness_preexisting':True,
        'frozen_git_blobs':{'corpus':CORPUS_BLOB,'reconciliation':EVIDENCE_BLOB},
        'frozen_census':{'source_denominator':[121,121,0],
                         'historical_route_refusals':[20,20,0],
                         'missing_ordered_premises':[30,30,0],
                         'complete_source_specific_witnesses':[50,50,0]},
        'new_historical_case_ids':[],
        'falsified_candidate':'ENDPOINT_SAME_SIGN_IMPLIES_EMPTY_INTERIOR',
        'admitted_rational_parameter':'0<a<1, degree-1 clamped two-span C1/S1, H0=0, phase t/4',
        'exact_parametric_outcomes':variants,
        'extremely_close_roots':strict_near_case(),
        'required_pb00701_discharged':False,
        'native_geometry_or_engineering_step_qualified':False}

def adversarial():
    core=self_test()
    row={'id':CASE,'origin':'v19','kind':'COMPOSITE_TAIL','spec':source_spec(Q(1,3)),
         'expected':{'id':CASE,'observed':{'status':'BLOCKED','spans':copy.deepcopy(EXPECTED_SPANS)},
                     'v54_disposition':'BLOCKED'}}
    evidence={'case_id':CASE,'source_sha256':SOURCE_SHA,'original_row_sha256':ROW_SHA,
              'registered_evidence_level':'COMPLETE_SOURCE_SPECIFIC',
              'prior_v1_registered_evidence_level':'PARTIAL_REFUSED_TAIL_ONLY',
              'historical_disposition_changed':False}
    assert check_original(row,evidence)
    bad=[]
    for key in ('phase','knot','coscontrol','sincontrol','degree','refusal','status','sourceid','evidence'):
        a=copy.deepcopy(row);b=copy.deepcopy(evidence)
        if key=='phase': a['spec']['phase_turn_rate']='1/8'
        elif key=='knot': a['spec']['sin_splines']['1']['knots'][3]='5/4'
        elif key=='coscontrol': a['spec']['cos_splines']['1']['controls'][0]='0'
        elif key=='sincontrol': a['spec']['sin_splines']['1']['controls'][2]='0'
        elif key=='degree': a['spec']['cos_splines']['1']['degree']=2
        elif key=='refusal': a['expected']['observed']['spans'][1][2]='NO_LONGER_BLOCKED'
        elif key=='status': a['expected']['v54_disposition']='CERTIFIED'
        elif key=='sourceid': a['id']='other'
        elif key=='evidence': b['registered_evidence_level']='PARTIAL_ORDERED_CHILD'
        try:check_original(a,b);raise AssertionError('accepted mutation '+key)
        except Refusal:bad.append(key)
    assert len(bad)==9
    return {'parameter_controls':core,'original_source_mutations_refused':bad}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--contract',action='store_true');ap.add_argument('--self-test',action='store_true');ap.add_argument('--emit',action='store_true');args=ap.parse_args()
    if not (args.contract or args.self_test or args.emit):ap.error('choose mode')
    if args.self_test:print('self-test PASS',json.dumps(adversarial(),sort_keys=True))
    if args.contract or args.emit:
        actual=receipt()
        if args.contract and not args.emit and canonical_data(RECEIPT)!=actual:
            raise AssertionError('machine-readable receipt is not fresh reproduction')
        print(json.dumps(actual,indent=2,sort_keys=True))
