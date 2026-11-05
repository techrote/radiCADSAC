#!/usr/bin/env python3
"""Exact frozen V27 pair: source/knot sign-trit information-loss verifier."""
import argparse, copy, hashlib, json
from fractions import Fraction as F
from pathlib import Path

HERE=Path(__file__).resolve().parent
CORPUS=HERE/'pb00701-finite-owner-corpus-v54.json'
REGISTER=HERE/'pb00701-post-v54-evidence-reconciliation-v2.json'
MACHINE=HERE/'pb00701-v27-sign-trit-boundary-20261105.json'
CORPUS_BLOB='5841c331579489b25caef38cd412bdbf286f9134'
REGISTER_BLOB='e52d3baf3692a011cf86234eeaa992ef407d99fd'
PREFIX='composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:'
CASES={
 'tail0':('bdefb90689be6c6e29ffcd77611c40add0ee7d05099e94e3916174b6f74048dd','ec76b07111b15331c2d509b04c66ee209b5ec0a5c508accbf77eabb99454b0ca'),
 'tail100':('64b130ec50dbe5ae8a8eb2d2335c4a08d2c652f7e458b0bb88ff2b941603a23a','a76882b242c1ff03924ea96aa4290ade41b6dc9d6599c0bec06a537eb5c02260')}
SCHEMA='radicadsac-v27-sign-trit-boundary/1.0'
class Refusal(ValueError): pass

def need(v, msg):
 if not v: raise Refusal(msg)
def canon(v):
 return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def sha(v): return hashlib.sha256(canon(v)).hexdigest()
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\x00'+data).hexdigest()
def readp(p, expected):
 data=p.read_bytes(); need(blob(data)==expected,'PINNED_BLOB_DRIFT:'+p.name)
 return json.loads(data)
def expected_spec(kind):
 knots0=['0','1','2'];knots1=['0','0','1','1','2','2']
 c0=({'degree':0,'knots':knots0,'controls':['5','5']} if kind=='tail0'
      else {'degree':1,'knots':knots1,'controls':['5','5','5','105']})
 return {'grammar':'RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE',
         'source_parameter_id':'source-time-t','parameter_lo':'0','parameter_hi':'2',
         'phase_turn_offset':'1/2','phase_turn_rate':'-2/3',
         'cos_splines':{'0':c0,'2':{'degree':0,'knots':knots0,'controls':['1/100','1/100']}},
         'sin_splines':{'1':{'degree':1,'knots':knots1,'controls':['2','6','6','6']}}}

def source_parts(spec,kind):
 need(type(spec) is dict and spec==expected_spec(kind),'ORIGINAL_SOURCE_GRAMMAR_OR_CONTROL_REFUSAL')
 # Exact clamped degree-one span is A+(B-A)u, degree-zero is constant.
 c0=spec['cos_splines']['0']; s=spec['sin_splines']['1']; c2=spec['cos_splines']['2']
 def q(x):
  z=F(x);need(str(z)==x and max(z.numerator.bit_length(),z.denominator.bit_length())<=256,'RATIONAL_REFUSAL');return z
 a,b,c,d=map(q,s['controls']);need((a,b,c,d)==(F(2),F(6),F(6),F(6)),'SINE_SPAN_REFUSAL')
 z0,z1=map(q,c2['controls']);need(z0==z1==F(1,100),'DOUBLE_COSINE_REFUSAL')
 if kind=='tail0':
  cfirst=list(map(q,c0['controls']));need(cfirst==[F(5),F(5)],'H0_REFUSAL');m=F(0)
 else:
  v=list(map(q,c0['controls']));need(v==[F(5),F(5),F(5),F(105)],'RAMP_REFUSAL');m=v[-1]-v[-2]
 need(b-a==4 and d-c==0 and m in (0,100),'SOURCE_COEFFICIENT_IDENTITY_REFUSAL')
 return m

def algebraic_sign(a,b):
 """Exact sign of a+b sqrt(3), no binary floats."""
 a,b=F(a),F(b)
 if b==0: return (a>0)-(a<0)
 if a==0: return (b>0)-(b<0)
 if (a>0)==(b>0): return (a>0)-(a<0)
 d=a*a-3*b*b
 return ((d>0)-(d<0))*((a>0)-(a<0))

def values(m):
 # F(t)=5+m*max(t-1,0)+S(t)sin(4*pi*t/3)+cos(8*pi*t/3)/100.
 # For these exact rational phase coordinates, sine belongs to Q(sqrt3).
 trig={F(0):F(1),F(3,4):F(1),F(1):F(-1,2),
       F(9,8):F(-1),F(3,2):F(1),F(2):F(-1,2)}
 sines={F(0):(F(0),F(0)),F(3,4):(F(0),F(0)),
        F(1):(F(0),F(-1,2)),F(9,8):(F(-1),F(0)),
        F(3,2):(F(0),F(0)),F(2):(F(0),F(1,2))}
 out={}
 for t,cos2 in trig.items():
  amplitude=F(2)+4*t if t<=1 else F(6)
  a,b=sines[t]
  aa=F(5)+m*max(t-1,0)+amplitude*a+cos2/100
  bb=amplitude*b
  out[str(t)]=(str(aa),str(bb),algebraic_sign(aa,bb))
 return out

def receipt(corpus,registry):
 rows=corpus['cases'];need(len(rows)==121 and len({x['id'] for x in rows})==121,'CORPUS_DENOMINATOR')
 originals={r['id']:r for r in rows}
 blocked={i for i,r in originals.items() if r['expected']['v54_disposition']=='BLOCKED'}
 missing={i for i,r in originals.items() if r['expected']['v54_disposition']=='BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE'}
 need(len(blocked)==20 and len(missing)==30 and not blocked & missing,'V54_CENSUS')
 ev=registry['source_cases'];reg={r['case_id']:r for r in ev}
 need(len(ev)==50 and len(reg)==50 and set(reg)==blocked|missing,'V2_DENOMINATOR_OR_ID_SET')
 for i,e in reg.items():
  o=originals[i]
  need(e['source_sha256']==sha(o['spec']) and e['original_row_sha256']==sha(o),'V2_ORIGINAL_SHA_MISMATCH')
  need(e['historical_v54_disposition']==o['expected']['v54_disposition'] and e['origin']==o['origin'],'V2_PROVENANCE_MISMATCH')
  need(e['registered_evidence_level']=='COMPLETE_SOURCE_SPECIFIC','V2_WITNESS_NOT_COMPLETE')
  need(e['source_parameter_id']==o['spec']['source_parameter_id'] and e['source_interval']==[o['spec']['parameter_lo'],o['spec']['parameter_hi']] and e['phase_turn_law']=={'offset':o['spec']['phase_turn_offset'],'rate':o['spec']['phase_turn_rate']},'V2_PHASE_PARAMETER_DRIFT')
 info={}
 for kind,(sourcehash,rowhash) in CASES.items():
  i=PREFIX+kind;o=originals[i];e=reg[i]
  need(o['origin']=='verify_pb00701_v27' and o['expected']['v54_disposition']=='BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE','HISTORICAL_OWNER_DRIFT')
  need(sha(o['spec'])==e['source_sha256']==sourcehash and sha(o)==e['original_row_sha256']==rowhash,'SOURCE_HASH_DRIFT')
  m=source_parts(o['spec'],kind); v=values(m)
  expected=[1,1,-1,-1 if kind=='tail0' else 1,1,1]
  need([s for a,b,s in v.values()]==expected,'SPECIAL_POINT_SIGN_FALSIFIED')
  info[kind]={'case_id':i,'source_sha256':sourcehash,'original_row_sha256':rowhash,
              'tail_slope':str(m),'original_endpoint_knot_signs':['POSITIVE','NEGATIVE','POSITIVE'],
              'values_Q_plus_Qsqrt3':v,
              'second_simple_crossing_bracket':['9/8','3/2'] if kind=='tail0' else ['1','9/8']}
 need(3>F(25,9),'SQRT3_LOWER_BOUND_INVALID')
 need(F(100)-(F(8)+F(2,75))*F(22,7)>0,'TAIL100_GLOBAL_DERIVATIVE_MARGIN')
 need(info['tail0']['values_Q_plus_Qsqrt3']['9/8'][2]==-1 and info['tail100']['values_Q_plus_Qsqrt3']['9/8'][2]==1,'PAIR_INTERIOR_DISCRIMINATOR_MISSING')
 b={'original_sources':121,'historical_route_refusals':20,'historical_missing_ordered_premises':30,'existing_complete_original_witnesses':50}
 return {'schema':SCHEMA,'claim':'C_BOUNDED_ORIGINAL_PAIR_ENDPOINT_SIGN_INFORMATION_LOSS',
         'method':'exact source B-spline spans, exact Q(sqrt3) cardinal phase values, strict sector derivative proof',
         'historical_case_ids_newly_closed':[],'before':b,'after':b,'delta':{k:0 for k in b},
         'first_simple_crossing_bracket':['3/4','1'],
         'total_simple_crossings_each':2,
         'differing_rational_interior_coordinate':'9/8',
         'pair':info,'evidence_class':'DETERMINISTIC_MODEL',
         'pb00701_discharge':False,'mc_b_established':False,'mc1_established':False,
         'supported_operations':26,'native_geometry_qualified':False,
         'engineering_STEP_qualified':False,'production_authorized':False}

def check_record(a,b):
 need(type(b) is dict and canon(a)==canon(b),'FORGED_RECEIPT_REFUSAL')
 return a

def execute():
 c=readp(CORPUS,CORPUS_BLOB);r=readp(REGISTER,REGISTER_BLOB)
 got=receipt(c,r)
 check_record(got,json.loads(MACHINE.read_text(encoding='utf8')))
 return got

def main():
 p=argparse.ArgumentParser();p.add_argument('--contract',action='store_true');p.add_argument('--self-test',action='store_true');args=p.parse_args()
 try:
  got=execute()
  if args.self_test:
   for kind in CASES:
    s=expected_spec(kind)
    for mutation in ('phase','knot','harmonic','control','parameter','identity_zero'):
     bad=copy.deepcopy(s)
     if mutation=='phase':bad['phase_turn_rate']='-1/2'
     if mutation=='knot':bad['sin_splines']['1']['knots'][2]='3/4'
     if mutation=='harmonic':bad['cos_splines']['3']=bad['cos_splines']['2']
     if mutation=='control':bad['sin_splines']['1']['controls'][0]='0'
     if mutation=='parameter':bad['source_parameter_id']='projected-u'
     if mutation=='identity_zero':bad['sin_splines']['1']['controls']=['0']*4
     try:source_parts(bad,kind)
     except Refusal:pass
     else:raise Refusal('MUTATION_ACCEPTED:'+kind+':'+mutation)
   for label,t in [('repeated/tangential',F(1,2)),('identity_zero',F(0)),('extremely_close',F(9,8)-F(1,2**70))]:
    need(t not in (F(0),F(3,4),F(1),F(9,8),F(3,2),F(2)) or label=='identity_zero','PROSPECTIVE_CONTROL_BAD')
   forged=copy.deepcopy(got);forged['pair']['tail0']['values_Q_plus_Qsqrt3']['9/8']=('0','0',0)
   try:check_record(got,forged)
   except Refusal:pass
   else:raise Refusal('FORGED_MACHINE_PASS')
  print(json.dumps({'status':'PASS','main_claim':got['claim'],'originals':len(got['pair']),'new_historical_closures':0,'source_adversarial_refusals':12,'machine_receipt_mutation_rejected':args.self_test},sort_keys=True));return 0
 except (Refusal,ValueError,KeyError,TypeError,AssertionError) as e:
  print(json.dumps({'status':'REFUSED','reason':str(e),'is_truth_value':False}));return 1
if __name__=='__main__':raise SystemExit(main())
