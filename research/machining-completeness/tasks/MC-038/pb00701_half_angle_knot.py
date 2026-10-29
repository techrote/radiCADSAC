#!/usr/bin/env python3
"""Research-only exact half-angle Sturm proof for TWO constant-harmonic source spans.

F(s)=sum_{h=0..H} a_h*cos(h*pi*s)+b_h*sin(h*pi*s), with distinct
rational coefficient dictionaries on [0,1] and [1,2].  It is deliberately
NOT an adapter for polynomial-modulated V27/V41 owners or historical v54.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from math import comb

SCHEMA = 'radicadsac-mc038-half-angle-trig-knot-research/1.0'
MAX_HARMONIC = 8
MAX_ROOTS = 32
MAX_DEPTH = 128
MAX_SPLITS = 4096
MAX_BITS = 8192

class Refusal(ValueError):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason

def need(ok, reason):
    if not ok:
        raise Refusal(reason)

def rat(x):
    need(type(x) is str and 0 < len(x) <= 128, 'NONCANONICAL_RATIONAL')
    try: q = Q(x)
    except (ValueError, ZeroDivisionError, OverflowError) as ex:
        raise Refusal('INVALID_RATIONAL') from ex
    need(str(q) == x and max(q.numerator.bit_length(), q.denominator.bit_length()) <= 128,
         'NONCANONICAL_OR_OVERSIZED_RATIONAL')
    return q

def trim(p):
    p = list(p)
    while len(p)>1 and p[-1]==0: p.pop()
    return p

def bounded(p):
    need(len(p) <= 2*MAX_HARMONIC+2, 'POLYNOMIAL_DEGREE_RESOURCE_LIMIT')
    need(all(max(x.numerator.bit_length(),x.denominator.bit_length()) <= MAX_BITS for x in p),
         'POLYNOMIAL_COEFFICIENT_RESOURCE_LIMIT')
    return p

def add(a,b):
    c=[Q(0)]*max(len(a),len(b))
    for i,x in enumerate(a): c[i]+=x
    for i,x in enumerate(b): c[i]+=x
    return bounded(trim(c))

def scale(a,x): return bounded(trim([v*x for v in a]))

def mul(a,b):
    c=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j]+=x*y
    return bounded(trim(c))

def power(a,n):
    p=[Q(1)]
    for _ in range(n): p=mul(p,a)
    return p

def at(a,x):
    y=Q(0)
    for c in reversed(a): y=y*x+c
    return y

def derivative(a): return trim([i*a[i] for i in range(1,len(a))] or [Q(0)])

def divmodp(a,b):
    a,b=trim(a),trim(b)
    need(b!=[0], 'POLYNOMIAL_DIVISION_BY_ZERO')
    q=[Q(0)]*max(1,len(a)-len(b)+1)
    while a != [0] and len(a)>=len(b):
        i=len(a)-len(b); c=a[-1]/b[-1]; q[i]=c
        for j,v in enumerate(b): a[i+j]-=c*v
        a=bounded(trim(a))
    return bounded(trim(q)),a

def exact_div(a,b):
    q,r=divmodp(a,b)
    need(r==[0], 'NONEXACT_POLYNOMIAL_DIVISION')
    return q

def monic(a):
    a=trim(a)
    return a if a==[0] else scale(a,1/a[-1])

def gcd(a,b):
    a,b=trim(a),trim(b)
    while b != [0]:
        _,r=divmodp(a,b); a,b=b,r
    return monic(a)

def sturm(f):
    f=monic(f)
    need(len(f)>1, 'CONSTANT_STURM_POLYNOMIAL')
    sequence=[f,derivative(f)]
    while sequence[-1] != [0]:
        _,r=divmodp(sequence[-2],sequence[-1])
        if r==[0]: break
        sequence.append(scale(r,-1))
    return sequence

def variations(seq,x):
    s=[(1 if v>0 else -1) for p in seq if (v:=at(p,x))!=0]
    return sum(a!=b for a,b in zip(s,s[1:]))

def count(seq,a,b):
    need(a<b, 'INVALID_ROOT_INTERVAL')
    return variations(seq,a)-variations(seq,b)

def squarefree_factors(f):
    f=monic(f)
    if len(f)==1: return []
    c=gcd(f,derivative(f)); w=exact_div(f,c); i=1; result=[]
    while w != [1]:
        y=gcd(w,c); z=exact_div(w,y)
        if z != [1]: result.append((monic(z),i))
        w=y; c=exact_div(c,y); i+=1
        need(i<=2*MAX_HARMONIC+2, 'FACTORIZATION_RESOURCE_LIMIT')
    need(c==[1], 'INCOMPLETE_SQUAREFREE_FACTORIZATION')
    check=[Q(1)]
    for factor,m in result: check=mul(check,power(factor,m))
    need(monic(check)==f, 'FACTORIZATION_IDENTITY_MISMATCH')
    return result

def coef_pair_terms(src):
    need(type(src) is dict and 1<=len(src)<=MAX_HARMONIC+1, 'UNSUPPORTED_HARMONIC_COUNT')
    result={}
    for key,value in src.items():
        need(type(key) is str and key.isdecimal() and str(int(key))==key,
             'NONCANONICAL_HARMONIC_INDEX')
        h=int(key)
        need(0<=h<=MAX_HARMONIC and type(value) is dict and set(value)=={'cos','sin'},
             'UNSUPPORTED_HARMONIC_GRAMMAR')
        a,b=rat(value['cos']),rat(value['sin'])
        need(h!=0 or b==0,'SINE_ZERO_HARMONIC_FORBIDDEN')
        need(a!=0 or b!=0,'REDUNDANT_ZERO_HARMONIC')
        result[h]=(a,b)
    return result

def half_angle(src):
    """F(theta)=P(t)/(1+t^2)^H, t=tan(theta/2), exact over real t."""
    H=max(src)
    # (1+i*t)^(2*h) = C_h(t)+i*S_h(t).
    out=[Q(0)]
    for h,(a,b) in src.items():
        cos_poly=[Q(((-1)**(j//2))*comb(2*h,j)) if j%2==0 else Q(0)
                  for j in range(2*h+1)]
        sin_poly=[Q(((-1)**((j-1)//2))*comb(2*h,j)) if j%2 else Q(0)
                  for j in range(2*h+1)]
        out=add(out,mul(add(scale(cos_poly,a),scale(sin_poly,b)),power([1,0,1],H-h)))
    need(out!=[0],'IDENTITY_ZERO_TRIG_SOURCE')
    need(len(out)-1<=2*H, 'HALF_ANGLE_DEGREE_INVALID')
    return bounded(out),H

def at_pi(src):
    return sum(a*(-1)**h for h,(a,b) in src.items())

def positive_bound(poly):
    lead=abs(poly[-1]); B=Q(2)+max((abs(c)/lead for c in poly[:-1]),default=Q(0))
    # All complex roots have modulus < 1+max(abs(a_i/a_n)).
    return (B.numerator//B.denominator)+1

def isolate(poly):
    """All real nonzero roots, strict disjoint rational t intervals, multiplicities."""
    k=0
    while k<len(poly)-1 and poly[k]==0: k+=1
    reduced=poly[k:]
    if len(reduced)<=1: return [],k
    factors=squarefree_factors(reduced)
    sf=monic(exact_div(reduced,gcd(reduced,derivative(reduced))))
    seq=sturm(sf); B=Q(positive_bound(reduced)); out=[]; splits=0
    for l,r in ((-B,Q(0)),(Q(0),B)):
        need(at(sf,l)!=0 and at(sf,r)!=0, 'BOUNDARY_ROOT_NOT_EXCLUDED')
        def go(a,b,depth):
            nonlocal splits
            splits+=1
            if splits>MAX_SPLITS or depth>MAX_DEPTH:
                raise Refusal('STURM_ISOLATION_RESOURCE_LIMIT')
            n=count(seq,a,b)
            need(n>=0, 'NEGATIVE_STURM_ROOT_COUNT')
            if n==0: return
            if n==1 and b-a<=Q(1,64):
                matched=[m for factor,m in factors if count(sturm(factor),a,b)==1]
                need(len(matched)==1,'AMBIGUOUS_ROOT_MULTIPLICITY')
                out.append({'t_bracket':[str(a),str(b)],'multiplicity':matched[0]})
                return
            # Rational cut never hits any root of sf; exact rational roots remain
            # strictly inside their isolating interval rather than on a cut.
            mid=None
            for j in range(2,len(sf)+6):
                cut=a+(b-a)/Q(j)
                if at(sf,cut)!=0:
                    mid=cut;break
            need(mid is not None,'RATIONAL_CUT_RESOURCE_LIMIT')
            go(a,mid,depth+1);go(mid,b,depth+1)
        go(l,r,0)
    need(len(out)<=MAX_ROOTS,'ROOT_COUNT_RESOURCE_LIMIT')
    out.sort(key=lambda e:Q(e['t_bracket'][0]))
    for a,b in zip(out,out[1:]):
        need(Q(a['t_bracket'][1])<Q(b['t_bracket'][0]),
             'OVERLAPPING_ISOLATION_BRACKETS')
    return out,k

def sgn(v):
    need(v!=0,'ZERO_SIGN_WITNESS')
    return 1 if v>0 else -1

def classify_span(poly,H,left_half):
    roots,k=isolate(poly)
    roots=[r for r in roots if (Q(r['t_bracket'][0])>0 if left_half else Q(r['t_bracket'][1])<0)]
    # Positive t runs from 0+ to +inf. Negative t runs from -inf to 0-.
    start_sign=(sgn(poly[k]) if left_half else sgn(poly[-1])*(-1)**(len(poly)-1))
    end_sign=(sgn(poly[-1]) if left_half else sgn(poly[k])*(-1)**k)
    state=start_sign
    for event in roots:
        a,b=map(Q,event['t_bracket'])
        need(a<b and at(poly,a)*at(poly,b) !=0, 'ROOT_BRACKET_BOUNDARY_ZERO')
        need(sgn(at(poly,a))==state, 'ROOT_LEFT_SIGN_INCONSISTENT')
        event['left_sign']=state
        state*=(-1)**event['multiplicity']
        event['right_sign']=state
        need(sgn(at(poly,b))==state,'ROOT_RIGHT_SIGN_INCONSISTENT')
        event['kind']='CROSSING' if event['multiplicity']%2 else 'TANGENCY'
        event['phase_half']='0_TO_PI' if left_half else 'PI_TO_2PI'
        event['source_coordinate']='2*atan(t)/pi' if left_half else '2+2*atan(t)/pi'
    need(state==end_sign, 'SPAN_SIGN_CHAIN_INCONSISTENT')
    return roots,start_sign,end_sign,k,2*H-(len(poly)-1)

def contract(spec):
    need(type(spec) is dict and set(spec)=={'schema','source_parameter_id','spans'},
         'SOURCE_SCHEMA_FIELDS_INVALID')
    need(spec['schema']==SCHEMA and type(spec['source_parameter_id']) is str and
         0<len(spec['source_parameter_id'])<=128, 'SOURCE_SCHEMA_ID_INVALID')
    spans=spec['spans'];need(type(spans) is list and len(spans)==2,'REQUIRE_TWO_SOURCE_SPANS')
    rows=[]
    for i,row in enumerate(spans):
        need(type(row) is dict and set(row)=={'interval','harmonics'},'SPAN_FIELDS_INVALID')
        need(row['interval']==(['0','1'] if i==0 else ['1','2']),
             'UNSUPPORTED_SOURCE_PARAMETER_OR_PHASE')
        terms=coef_pair_terms(row['harmonics']); p,H=half_angle(terms)
        roots,start,end,endpoint_order,knot_order=classify_span(p,H,i==0)
        rows.append({'terms':terms,'poly':p,'H':H,'roots':roots,
                     'start':start,'end':end,'endpoint_order':endpoint_order,
                     'knot_order':knot_order})
    need(at_pi(rows[0]['terms'])==at_pi(rows[1]['terms']),
         'DISCONTINUOUS_ORIGINAL_SOURCE_KNOT')
    knot_value=at_pi(rows[0]['terms'])
    need((knot_value==0)==(rows[0]['knot_order']>0), 'LEFT_KNOT_ZERO_MISMATCH')
    need((knot_value==0)==(rows[1]['knot_order']>0), 'RIGHT_KNOT_ZERO_MISMATCH')
    if knot_value:
        need(rows[0]['end']==rows[1]['start']==sgn(knot_value),
             'NONZERO_KNOT_SIGN_MISMATCH')
    events=[]
    for event in rows[0]['roots']:
        events.append({'kind':'OPEN_TRIG_ZERO',**event})
    if knot_value==0:
        events.append({'kind':'SOURCE_KNOT_ZERO','coordinate':'1',
                       'left_one_sided_order':rows[0]['knot_order'],
                       'right_one_sided_order':rows[1]['knot_order'],
                       'left_sign':rows[0]['end'],'right_sign':rows[1]['start'],
                       'event_kind':'CROSSING' if rows[0]['end']!=rows[1]['start'] else 'TOUCHING',
                       'global_smooth_multiplicity_claimed':False})
    for event in rows[1]['roots']:
        events.append({'kind':'OPEN_TRIG_ZERO',**event})
    signs=[rows[0]['start']]
    for ev in events:
        need(signs[-1]==ev['left_sign'],'PHYSICAL_SIGN_CHAIN_INCONSISTENT')
        signs.append(ev['right_sign'])
    need(signs[-1]==rows[1]['end'],'FINAL_SIGN_MISMATCH')
    endpoint_zeros=[]
    if rows[0]['endpoint_order']>0:
        endpoint_zeros.append({'position':'0','one_sided_order':rows[0]['endpoint_order']})
    if rows[1]['endpoint_order']>0:
        endpoint_zeros.append({'position':'2','one_sided_order':rows[1]['endpoint_order']})
    source={k:v for k,v in spec.items()}
    binding=hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'schema':SCHEMA,'status':'CONDITIONAL_EXACT_HALF_ANGLE_TRIG_COMPOSED',
            'evidence_class':'DETERMINISTIC_MODEL', 'source_binding_sha256':binding,
            'root_count_open':len(events),'ordered_physical_events':events,
            'maximal_open_signs':signs,'source_knot_value':str(knot_value),
            'endpoint_zeros':endpoint_zeros,
            'all_roots_recomputed_from_source':True,
            'original_v27_v41_admitted':False,'historical_v54_admitted':False,
            'pb00701_certified':False,'mc_b_established':False,
            'mc1_established':False,'production_authorized':False}

def attempt(spec):
    try: return contract(spec)
    except (MemoryError, RecursionError, OverflowError) as e:
        return {'schema':SCHEMA,'status':'RESOURCE_REFUSAL','reason':type(e).__name__,
                'is_truth_value':False,'production_authorized':False,
                'pb00701_certified':False,'mc_b_established':False}
    except Refusal as e:
        return {'schema':SCHEMA,'status':'RESOURCE_REFUSAL' if 'RESOURCE' in e.reason else 'BLOCKED',
                'reason':e.reason,'is_truth_value':False,'production_authorized':False,
                'pb00701_certified':False,'mc_b_established':False}
