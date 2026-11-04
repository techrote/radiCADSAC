"""Exact rational-parameter V12 affine-H1 whole-source event threshold (model research).

No numeric root search; root coordinates stay implicit. Refusal is NONTRUTH.
"""
import hashlib
import json
from fractions import Fraction as Q

CASE = 'composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0'
SOURCE_SHA = 'ee15e947924b45640dd16634247a476bb230fdc145fef94407d9a7c219928cd5'
ROW_SHA = 'd0acef7c69cb8ac1ba128b988e83817a91feff78509dd18007d0e56a506336c3'
CORPUS_BLOB = '5841c331579489b25caef38cd412bdbf286f9134'
EVIDENCE_BLOB = 'e52d3baf3692a011cf86234eeaa992ef407d99fd'

class Refusal(ValueError):
    pass

def require_a(a):
    if type(a) is not Q or not Q(0) < a < Q(1):
        raise Refusal('admitted rational amplitude a must satisfy 0<a<1')
    if a.numerator.bit_length() > 512 or a.denominator.bit_length() > 512:
        raise Refusal('arithmetic budget; no zero/nonzero claim')
    return a

def source_spec(a):
    a = require_a(a)
    controls_cos = [str(-a), str(1-a), str(1-a), str(1-a)]
    controls_sin = [str(1-a), str(-a), str(-a), str(-a)]
    return {'grammar':'RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE',
            'source_parameter_id':'source-time-t', 'parameter_lo':'0', 'parameter_hi':'2',
            'phase_turn_offset':'0', 'phase_turn_rate':'1/4',
            'cos_splines':{
                '0':{'degree':0,'knots':['0','1','2'],'controls':['0','0']},
                '1':{'degree':1,'knots':['0','0','1','1','2','2'],'controls':controls_cos}},
            'sin_splines':{'1':{'degree':1,'knots':['0','0','1','1','2','2'],'controls':controls_sin}}}

def canonical_sha(spec):
    return hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def classify(a):
    """Consequences of analytically proved unique monotone x*tan(pi*x/2) branch.

    For t in [0,1], x=t-1/2, delta=1/2-a:
      F=sqrt(2)[delta cos(pi*x/2)-x sin(pi*x/2)].
    For t in [1,2], F=(1-a)cos(pi*t/2)-a sin(pi*t/2)<0.
    """
    a=require_a(a)
    delta=Q(1,2)-a
    if delta>0:
        return {'a':str(a), 'event_type':'TWO_SIMPLE_PREFIX_ROOTS',
                'root_count':2,'orders':[1,1], 'sign_cells':[-1,1,-1],
                'intervals':['(0,1/2)','(1/2,1)'], 'knot_zero':False,
                'whole_source_endpoint_signs':[-1,-1]}
    if delta==0:
        return {'a':str(a), 'event_type':'ONE_DOUBLE_PREFIX_TANGENCY',
                'root_count':1,'orders':[2], 'sign_cells':[-1,-1],
                'intervals':['{1/2}'], 'knot_zero':False,
                'whole_source_endpoint_signs':[-1,-1]}
    return {'a':str(a), 'event_type':'NO_ROOTS_NEGATIVE',
            'root_count':0,'orders':[], 'sign_cells':[-1],
            'intervals':[], 'knot_zero':False, 'whole_source_endpoint_signs':[-1,-1]}

def strict_near_case():
    # q=2^-100; delta=q^2. On (0,1), sin((pi/2)q)>q by strict chord inequality,
    # cos((pi/2)q)<1. F(1/2+/-q)<sqrt(2)(delta-q^2)=0 and F(1/2)>0.
    q=Q(1,2**100); delta=q*q; a=Q(1,2)-delta
    assert q*q==delta and 0<a<Q(1,2)
    return {'a':str(a),'delta':'2^-200','two_roots_between':
            [str(Q(1,2)-q),str(Q(1,2)+q)],
            'strict_separation_upper_bound':'2^-99',
            'proof_inequality':'sin((pi/2)*q)>q; cos((pi/2)*q)<1, q=2^-100',
            'result':classify(a)['event_type']}

def self_test():
    if canonical_sha(source_spec(Q(1,3)))!=SOURCE_SHA:
        raise AssertionError('literal original source spec mismatch')
    control=[(Q(1,3),2,[1,1],[-1,1,-1]),
             (Q(1,2),1,[2],[-1,-1]),(Q(2,3),0,[],[-1])]
    for a,count,orders,signs in control:
        x=classify(a)
        assert (x['root_count'],x['orders'],x['sign_cells'])==(count,orders,signs)
        assert source_spec(a)['sin_splines']['1']['controls'][1]==str(-a)
    for n in range(1,257):
        a=Q(n,257)
        x=classify(a)
        assert x['root_count']==(2 if a<Q(1,2) else 0)
        assert x['knot_zero'] is False
        assert source_spec(a)['cos_splines']['1']['controls'][1]==str(1-a)
    for exp in (4,16,100,200,400):
        a=Q(1,2)-Q(1,2**exp)
        assert classify(a)['root_count']==2
        assert classify(Q(1,2)+Q(1,2**exp))['root_count']==0
    z=strict_near_case(); assert z['result']=='TWO_SIMPLE_PREFIX_ROOTS'
    for a in (Q(0),Q(1),Q(-1),Q(2),1/3,False,0.5,'1/3',Q(1,2**1025)):
        try: classify(a); raise AssertionError('invalid parameter accepted')
        except Refusal: pass
    for a in (Q(1,3),Q(1,2),Q(2,3)):
        spec=source_spec(a)
        assert Q(spec['cos_splines']['1']['controls'][0])==-a
        assert Q(spec['sin_splines']['1']['controls'][1])==-a
        assert Q(spec['cos_splines']['1']['controls'][-1])==1-a
    return {'rational_grid':256,'threshold_and_near_controls':14,
            'invalid_parameters':9,'canonical_original_source_sha256':SOURCE_SHA}

if __name__=='__main__':
    print(json.dumps({'controls':self_test(),'examples':[classify(a) for a in (Q(1,3),Q(1,2),Q(2,3))],
                      'near':strict_near_case()},indent=2,sort_keys=True))
