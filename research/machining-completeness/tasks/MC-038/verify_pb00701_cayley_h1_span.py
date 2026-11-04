"""Frozen original-source admission and adversarial qualification of Cayley H1 span atlas."""
import argparse
import hashlib
import itertools
import json
import subprocess
from fractions import Fraction as Q
from pathlib import Path
from pb00701_cayley_h1_span import Refusal, certify_span, self_test

HERE = Path(__file__).resolve().parent
FROZEN = HERE/'pb00701-finite-owner-corpus-v54.json'
RECON = HERE/'pb00701-post-v54-evidence-reconciliation-v2.json'
RECEIPT = HERE/'pb00701-cayley-h1-span.json'
BLOBS = {FROZEN:'5841c331579489b25caef38cd412bdbf286f9134', RECON:'e52d3baf3692a011cf86234eeaa992ef407d99fd'}
ANCHORS={
 'composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0':('57d3c14096ccedfb7faea5023f5a09bada2ca274748f2207c36d77bbc790927c',(Q(0),Q(1),Q(-1,2)),[-1,1,-1,1,-1]),
 'composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail0':('1535f364cd4d3c1a3bf34f57f394ad70a17ad1327880a0a47f25f3ecff5c7560',(Q(0),Q(1,8),Q(1)),[1,-1,1,-1,1])
}
def blob(path):
    try: return subprocess.check_output(['git','hash-object',str(path)],text=True).strip()
    except (OSError,subprocess.CalledProcessError) as exc: raise Refusal('blob identity unavailable') from exc

def constant_right(piece):
    if not isinstance(piece,dict) or set(piece)!={'degree','knots','controls'}: raise Refusal('malformed original spline')
    deg=piece['degree']
    patterns={0:(['0','1','2'],2),1:(['0','0','1','1','2','2'],4),2:(['0','0','0','1','1','1','2','2','2'],6)}
    if type(deg) is not int or deg not in patterns: raise Refusal('unsupported original degree')
    knots,n=patterns[deg]
    if piece['knots']!=knots or len(piece['controls'])!=n: raise Refusal('changed actual knots/controls')
    values=[Q(x) for x in piece['controls'][n//2:]]
    if any(x!=values[0] for x in values): raise Refusal('nonconstant actual source piece')
    return values[0]

def validate_case(row,entry):
    id=row['id']; canonical, triple, signs=entry
    spec=row['spec']
    digest=hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if digest!=canonical: raise Refusal('wrong canonical original source identity')
    if set(spec)!={'grammar','source_parameter_id','parameter_lo','parameter_hi','phase_turn_offset','phase_turn_rate','cos_splines','sin_splines'}: raise Refusal('wrong source keys')
    if (spec['grammar'],spec['source_parameter_id'],spec['parameter_lo'],spec['parameter_hi'])!=('RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE','source-time-t','0','2'): raise Refusal('wrong source grammar or domain')
    if set(spec['cos_splines'])!={'0','1'} or set(spec['sin_splines'])!={'1'}: raise Refusal('changed harmonic inventory')
    A=constant_right(spec['cos_splines']['0']); C=constant_right(spec['cos_splines']['1']); S=constant_right(spec['sin_splines']['1'])
    if (A,C,S)!=triple: raise Refusal('changed physical right-span Fourier coefficients')
    sp=row['expected']['observed']['spans']
    if row['expected']['v54_disposition']!='BLOCKED' or row['expected']['observed']['status']!='BLOCKED' or len(sp)!=2 or sp[1]!=['PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF','BLOCKED','CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED'] or sp[0][1]!='CERTIFIED': raise Refusal('changed historical V43 refusal')
    x=certify_span(lo=Q(1),hi=Q(2),offset=Q(spec['phase_turn_offset']),rate=Q(spec['phase_turn_rate']),A=A,C=C,S=S)
    if x['kind']!='FINITE_EVENTS' or len(x['events'])!=4 or [e['order'] for e in x['events']]!=[1]*4 or x['sign_cells']!=signs or any(x['endpoint_zeros']): raise AssertionError('physical span classification differs')
    return {'case_id':id,'original_source_sha256':digest,'historical_span':'V43 BLOCKED','complete_source_specific_preexisting':True,'new_historical_closure':False,'span_event_count':len(x['events']),'span_event_orders':[e['order'] for e in x['events']],'span_sign_cells':x['sign_cells'],'exact_implicit_events':x['events']}

V8_ID='composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0'
V8_SHA='9abbed355812241cdef20f3ce3b3522619bdd682c3a73fb01828d8f95c72f0af'

def validate_v8(row, evidence):
    """Actual original-source V27 refusal falsifies finite-z-only Cayley."""
    spec=row['spec']
    digest=hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if digest!=V8_SHA or evidence['source_sha256']!=V8_SHA or evidence['case_id']!=V8_ID:
        raise Refusal('V8 historical source identity drift')
    if set(spec)!={'grammar','source_parameter_id','parameter_lo','parameter_hi','phase_turn_offset','phase_turn_rate','cos_splines','sin_splines'}:
        raise Refusal('V8 source keys changed')
    if (spec['grammar'],spec['source_parameter_id'],spec['parameter_lo'],spec['parameter_hi'],spec['phase_turn_offset'],spec['phase_turn_rate'])!=('RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE','source-time-t','0','2','-1/4','1/2'):
        raise Refusal('V8 actual phase/parameter changed')
    if set(spec['cos_splines'])!={'0'} or set(spec['sin_splines'])!={'1'}:
        raise Refusal('V8 harmonic inventory changed')
    if spec['cos_splines']['0']!={'degree':0,'knots':['0','1','2'],'controls':['0','0']} or spec['sin_splines']['1']!={'degree':1,'knots':['0','0','1','1','2','2'],'controls':['-1/2','1/2','1/2','1/2']}:
        raise Refusal('V8 exact original spline controls changed')
    observed=row['expected']['observed']
    if row['expected']['v54_disposition']!='BLOCKED' or observed['status']!='BLOCKED' or observed['spans']!=[['PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION','CERTIFIED',None],['PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION','BLOCKED','V27_CHILD_NOT_CERTIFIED']]:
        raise Refusal('V8 original historical refusal changed')
    if evidence['registered_evidence_level']!='COMPLETE_SOURCE_SPECIFIC' or evidence['prior_v1_registered_evidence_level']!='COMPLETE_SOURCE_SPECIFIC' or evidence['prior_complete_result_digest_preserved'] is not True:
        raise Refusal('V8 existing full source witness status changed')
    A=constant_right(spec['cos_splines']['0'])
    C=Q(0)  # literal absent original H1 cosine channel
    S=constant_right(spec['sin_splines']['1'])
    if (A,C,S)!=(Q(0),Q(0),Q(1,2)): raise Refusal('V8 right source not admitted')
    x=certify_span(lo=Q(1),hi=Q(2),offset=Q(spec['phase_turn_offset']),rate=Q(spec['phase_turn_rate']),A=A,C=C,S=S)
    if x['kind']!='FINITE_EVENTS' or len(x['events'])!=1 or x['events'][0]['kind']!='PHASE_POLE_ZERO' or x['events'][0]['phase']!='1/2' or x['events'][0]['order']!=1 or x['sign_cells']!=[1,-1] or any(x['endpoint_zeros']):
        raise AssertionError('V8 actual pole zero/order/sign is not preserved')
    # Pole-blind P(z)=z has a single finite zero z=0 at integer phase,
    # which is OUTSIDE original right child phase [1/4,3/4].
    from pb00701_cayley_h1_span import finite_cayley_roots, phase_cmp_root_to_boundary
    finite=finite_cayley_roots(A,C,S)
    if len(finite)!=1: raise AssertionError('finite-only candidate changed')
    if any(phase_cmp_root_to_boundary(n,root,Q(1,4))>=0 and phase_cmp_root_to_boundary(n,root,Q(3,4))<=0 for n in (0,1) for root in finite):
        raise AssertionError('finite-only candidate unexpectedly sees actual pole root')
    return {'case_id':V8_ID,'original_source_sha256':digest,'historical_span':'V27 BLOCKED',
            'complete_source_specific_preexisting':True,'new_historical_closure':False,
            'span_event_count':1,'span_event_orders':[1],'span_sign_cells':[1,-1],
            'exact_implicit_events':x['events'],'falsified_candidate':'FINITE_Z_CAYLEY_ONLY',
            'candidate_reported_roots':0,'actual_closed_child_roots':1}

def contract():
    for p,h in BLOBS.items():
        if blob(p)!=h: raise Refusal('frozen file git blob drift: '+str(p))
    v54=json.loads(FROZEN.read_text()); v2=json.loads(RECON.read_text())
    rows={x['id']:x for x in v54['cases']}; rr={x['case_id']:x for x in v2['source_cases']}
    if len(rows)!=121 or len(v54['cases'])!=121 or v54['summary']['v54_dispositions'].get('BLOCKED')!=20 or v54['summary']['v54_dispositions'].get('BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE')!=30: raise Refusal('historical population drift')
    if v2['summary'].get('total_historical_unresolved_source_cases')!=50 or v2['summary'].get('by_registered_evidence_level',{}).get('COMPLETE_SOURCE_SPECIFIC')!=50: raise Refusal('post-v54 source registry drift')
    out=[]
    for id,entry in ANCHORS.items():
        if id not in rows or id not in rr or rr[id]['source_sha256']!=entry[0] or rr[id]['registered_evidence_level']!='COMPLETE_SOURCE_SPECIFIC' or rr[id]['prior_v1_registered_evidence_level']!='PARTIAL_REFUSED_TAIL_ONLY': raise Refusal('source/evidence mismatch')
        out.append(validate_case(rows[id],entry))
    if V8_ID not in rows or V8_ID not in rr: raise Refusal('missing historical V8 source')
    out.append(validate_v8(rows[V8_ID],rr[V8_ID]))
    return {'schema':'radicadsac-pb00701-cayley-h1-span/1.0','evidence_class':'DETERMINISTIC_MODEL','historical_v54':{'source_denominator':121,'route_refusals_before':20,'route_refusals_after':20,'missing_ordered_before':30,'missing_ordered_after':30},'source_specific_witnesses_before':50,'source_specific_witnesses_after':50,'newly_closed_ids':[],'required_pb00701_discharge':False,'span_certificates':out}

def tests():
    self_test()
    for a,c,s in itertools.product(range(-3,4),repeat=3):
        for p0,p1 in [(Q(0),Q(1)),(Q(-1,2),Q(1,2)),(Q(0),Q(1,2)),(Q(1,2),Q(1)),(Q(-1,2),Q(0)),(Q(0),Q(2)),(Q(1),Q(3,2))]:
            certify_span(lo=Q(0),hi=Q(1),offset=p0,rate=p1-p0,A=Q(a),C=Q(c),S=Q(s))
    original=next(x for x in json.loads(FROZEN.read_text())['cases'] if x['id']=='composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0')
    from copy import deepcopy
    for mutation in ('phase','control','refusal','degree','harmonic'):
        row=deepcopy(original)
        if mutation=='phase': row['spec']['phase_turn_rate']='3'
        if mutation=='control': row['spec']['cos_splines']['1']['controls'][-1]='9'
        if mutation=='refusal': row['expected']['observed']['spans'][-1][1]='CERTIFIED'
        if mutation=='degree': row['spec']['cos_splines']['1']['degree']=99
        if mutation=='harmonic': row['spec']['cos_splines']['7']={'degree':0,'knots':['0','1','2'],'controls':['1','1']}
        try: validate_case(row,ANCHORS[row['id']]);raise AssertionError('altered original source accepted')
        except Refusal: pass
    actual=next(x for x in json.loads(FROZEN.read_text())['cases'] if x['id']==V8_ID)
    fake_evidence={'source_sha256':V8_SHA,'case_id':V8_ID,'registered_evidence_level':'COMPLETE_SOURCE_SPECIFIC','prior_v1_registered_evidence_level':'COMPLETE_SOURCE_SPECIFIC','prior_complete_result_digest_preserved':True}
    validate_v8(actual,fake_evidence)
    for change in ('phase','amplitude','knot','refusal'):
        from copy import deepcopy
        m=deepcopy(actual)
        if change=='phase': m['spec']['phase_turn_offset']='0'
        if change=='amplitude': m['spec']['sin_splines']['1']['controls'][-1]='1'
        if change=='knot': m['spec']['sin_splines']['1']['knots'][3]='9/8'
        if change=='refusal': m['expected']['observed']['spans'][1][2]='SYNTHETIC_FAKE'
        try: validate_v8(m,fake_evidence); raise AssertionError('modified V8 source accepted')
        except Refusal: pass
    return 2401+5+4

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--contract',action='store_true');ap.add_argument('--self-test',action='store_true');ap.add_argument('--emit',action='store_true');args=ap.parse_args()
    if not (args.contract or args.self_test or args.emit): ap.error('select a mode')
    if args.self_test: print('adversarial self-test PASS',tests())
    if args.contract or args.emit:
        output=contract()
        if args.contract and not args.emit:
            expected={k:v for k,v in output.items() if k!='span_certificates'}
            expected['span_certificates']=[{k:v for k,v in item.items() if k!='exact_implicit_events'} for item in output['span_certificates']]
            if json.loads(RECEIPT.read_text())!=expected: raise AssertionError('exact machine evidence receipt differs')
        print(json.dumps(output,sort_keys=True,indent=2))
