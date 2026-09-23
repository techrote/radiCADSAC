#!/usr/bin/env python3
from __future__ import annotations
from pb00701_algebraic_separator_exact import *  # exact v32 foundation primitives

def _partition_refine_roots(poly, roots, a=Fraction(0), b=Fraction(1)):
    """Refine only as needed to expose rational gaps between exact root enclosures.

    The maximum number of bisections is source-derived from a root-separation
    bound for p(s)*s*(1-s); the early-stop condition is representational only.
    """
    p=ee.square_free(_trim(poly));a=q(a);b=q(b)
    work=[dict(r) for r in roots]
    if not work:return work
    boundary_poly=ee.square_free(_mul(p,[0,1,-1]))
    sep=_root_separation_lower(boundary_poly)
    max_steps=_depth_for_width(b-a,sep/4)*max(1,len(work))*2
    def step(r):
        if r['kind']=='point':return r
        lo,hi=r['lo'],r['hi'];mid=(lo+hi)/2
        if ee.peval(p,mid)==0:
            return {'kind':'point','value':mid,'multiplicity':r.get('multiplicity',1)}
        if ee.distinct_roots_open(p,lo,mid)==1:
            return {'kind':'interval','lo':lo,'hi':mid,'multiplicity':r.get('multiplicity',1)}
        if ee.distinct_roots_open(p,mid,hi)==1:
            return {'kind':'interval','lo':mid,'hi':hi,'multiplicity':r.get('multiplicity',1)}
        raise ArithmeticError('partition refinement lost isolated root')
    for _ in range(max_steps+1):
        changed=False
        for i,r in enumerate(work):
            lo=r['value'] if r['kind']=='point' else r['lo'];hi=r['value'] if r['kind']=='point' else r['hi']
            left_bad=(i==0 and lo<=a) or (i>0 and lo <= (work[i-1]['value'] if work[i-1]['kind']=='point' else work[i-1]['hi']))
            right_bad=(i==len(work)-1 and hi>=b) or (i<len(work)-1 and hi >= (work[i+1]['value'] if work[i+1]['kind']=='point' else work[i+1]['lo']))
            if (left_bad or right_bad) and r['kind']!='point':
                work[i]=step(r);changed=True
        if not changed:return work
    raise ExactAlgebraRefusal('derived transverse sign-cell partition depth exhausted')

def _source_binding(d,t,sgn,source_parameter_id):
    payload={'dominant':[str(x) for x in _trim(d)],'transverse':[str(x) for x in _trim(t)],'dominant_sign':int(sgn),'source_parameter_id':source_parameter_id}
    raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
    return payload,sha256(raw).hexdigest()

def verify_binding(result):
    if not isinstance(result,dict) or result.get('status')!='CERTIFIED':return False
    payload=result.get('canonical_source')
    if not isinstance(payload,dict):return False
    raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
    return sha256(raw).hexdigest()==result.get('canonical_source_sha256')

def _transverse_sign_cells(t,roots):
    # root representations are ordered and exact; samples in rational gaps certify cell signs.
    cells=[]
    prev=Fraction(0);prev_boundary='s=0'
    for idx,r in enumerate(roots):
        if r['kind']=='point':lo=hi=r['value']
        else:lo,hi=r['lo'],r['hi']
        if lo>prev:
            sample=(prev+lo)/2;cells.append({'left_boundary':prev_boundary,'right_boundary':f'T_root_{idx}','sample':str(sample),'transverse_sign':ee.sign(ee.peval(t,sample))})
        prev=max(prev,hi);prev_boundary=f'T_root_{idx}'
    if prev<Fraction(1):
        sample=(prev+1)/2;cells.append({'left_boundary':prev_boundary,'right_boundary':'s=1','sample':str(sample),'transverse_sign':ee.sign(ee.peval(t,sample))})
    return cells

def synthesize_separator(dominant_poly,transverse_poly,dominant_sign=1,*,source_parameter_id='s',caller_assertions=None,force_resource_refusal=False):
    if caller_assertions:
        raise ValueError('caller-supplied separator/critical-root/ordering certificates are non-authoritative')
    if source_parameter_id!='s':
        return {'status':'SEMANTIC_BLOCKER','reason':'SOURCE_PARAMETER_MISMATCH','blocker':'PB-007-01'}
    if force_resource_refusal:
        return {'status':'RESOURCE_REFUSAL','reason':'PB00701_V32_FORCED_EXACT_RESOURCE_REFUSAL','is_truth_value':False}
    try:
        d=_trim(dominant_poly);t=_trim(transverse_poly);sgn=int(dominant_sign)
        if sgn not in (-1,1):raise ValueError('dominant_sign must be +/-1')
        a=_scale(d,sgn)
        if not _strict_positive(a):
            return {'status':'BLOCKED','reason':'DOMINANT_STRICT_SIGN_NOT_CERTIFIED','blocker':'PB-007-01'}
        if t==[0]:return {'status':'BLOCKED','reason':'TRANSVERSE_ZERO_DEGENERATE_PROJECTIVE_TARGET','blocker':'PB-007-01'}
        common=ee.pgcd(a,t)
        if _degree(common)>0:
            a=_exact_div(a,common);t=_exact_div(t,common)
            # orient reduced dominant positive without changing ratio
            sample=ee.peval(a,0)
            if sample==0:sample=ee.peval(a,Fraction(1,2))
            if sample<0:a=_scale(a,-1);t=_scale(t,-1)
            if not _strict_positive(a):raise ArithmeticError('gcd reduction lost dominant sign')
        h=_sub(_mul(ee.deriv(a),t),_mul(a,ee.deriv(t)))
        t_roots=_partition_refine_roots(t,_isolate_closed_roots(t,0,1),0,1)
        h_roots=_isolate_closed_roots(h,0,1) if h!=[0] else []
        candidate_orders=[]
        for endpoint in (Fraction(0),Fraction(1)):
            tv=ee.peval(t,endpoint)
            if tv==0:continue
            ratio=ee.peval(a,endpoint)/abs(tv);rel=_compare_rational_alpha(ratio)
            candidate_orders.append({'kind':'ENDPOINT','source_parameter':str(endpoint),'relation_to_sqrt2_minus_1':rel,'ratio':str(ratio)})
            if rel<=0:return {'status':'BLOCKED','reason':'PROJECTIVE_MINIMUM_NOT_STRICTLY_ABOVE_TAN_PI_8','blocker':'PB-007-01','candidate_orders':candidate_orders}
        h_sf=ee.square_free(h) if h!=[0] else [0]
        for i,rep in enumerate(h_roots):
            # endpoints already handled
            if rep['kind']=='point' and rep['value'] in (0,1):continue
            tsign=_sign_at_algebraic_root(h_sf,rep,t)
            if tsign==0:
                candidate_orders.append({'kind':'STATIONARY_TRANSVERSE_ZERO','root_index':i,'root':_serial_rep(rep),'excluded_from_finite_minimum':True})
                continue
            # f(y)=y^2+2y-1 at y=A/|T|; multiply by T^2 using certified T sign.
            test=_sub(_add(_mul(a,a),_scale(_mul(a,t),2*tsign)),_mul(t,t))
            rel=_sign_at_algebraic_root(h_sf,rep,test)
            candidate_orders.append({'kind':'STATIONARY','root_index':i,'root':_serial_rep(rep),'transverse_sign':tsign,'relation_to_sqrt2_minus_1':rel,'comparison_polynomial':[str(x) for x in test]})
            if rel<=0:return {'status':'BLOCKED','reason':'PROJECTIVE_MINIMUM_NOT_STRICTLY_ABOVE_TAN_PI_8','blocker':'PB-007-01','candidate_orders':candidate_orders}
        vpoly=_critical_value_polynomial(a,t,h)
        if vpoly==[0]:return {'status':'RESOURCE_REFUSAL','reason':'CRITICAL_VALUE_ELIMINATION_DEGENERATE','is_truth_value':False}
        if _minpoly_divides(vpoly):
            return {'status':'BLOCKED','reason':'ALGEBRAIC_BOUNDARY_IS_CRITICAL_VALUE','blocker':'PB-007-01','critical_value_polynomial':[str(x) for x in vpoly],'candidate_orders':candidate_orders}
        bound=_ceil_fraction(_root_bound(vpoly))+1
        vroots=_isolate_open_roots(vpoly,Fraction(-bound),Fraction(bound))
        above=[]
        for rep in vroots:
            rel,refined=_relation_root_to_alpha(vpoly,rep,return_refined=True)
            if rel>0:above.append(refined)
        if not above:raise ArithmeticError('critical-value polynomial lacks a root above certified finite minimum')
        above.sort(key=lambda r:r['value'] if r['kind']=='point' else r['lo'])
        first_ref=above[0]
        beta=first_ref['value'] if first_ref['kind']=='point' else first_ref['lo']
        if _compare_rational_alpha(beta)<=0:raise ArithmeticError('critical-value lower enclosure is not above alpha')
        m=_closed_form_separator_below(beta)
        minus=_sub(a,_scale(t,m));plus=_add(a,_scale(t,m))
        if not (_strict_positive(minus) and _strict_positive(plus)):
            raise ArithmeticError('synthesized separator failed independent MC-032-style global margins')
        # Bind to the caller's canonical source polynomials rather than only the gcd-reduced pair.
        canonical_source,source_digest=_source_binding(dominant_poly,transverse_poly,sgn,source_parameter_id)
        return {
            'status':'CERTIFIED','route':V32_ROUTE,'source_parameter_id':'s','dominant_sign':sgn,
            'canonical_source':canonical_source,'canonical_source_sha256':source_digest,
            'reduced_dominant_polynomial':[str(x) for x in a],'reduced_transverse_polynomial':[str(x) for x in t],
            'stationary_polynomial':[str(x) for x in h],
            'transverse_roots':[_serial_rep(r) for r in t_roots],
            'transverse_sign_cells':_transverse_sign_cells(t,t_roots),
            'stationary_roots':[_serial_rep(r) for r in h_roots],
            'candidate_orderings':candidate_orders,
            'critical_value_polynomial':[str(x) for x in vpoly],
            'least_overapproximating_critical_value_root':_serial_rep(first_ref),
            'rational_lower_enclosure_above_boundary':str(beta),
            'rational_separator':str(m),
            'separator_relation':'sqrt(2)-1 < m < complete-span pointwise projective minimum',
            'global_margin_minus':[str(x) for x in minus],'global_margin_plus':[str(x) for x in plus],
            'global_margin_authority':'MC-032 exact rational endpoint/Sturm strict positivity',
            'root_isolation_authority':'MC-032 Sturm plus conservative Mignotte-derived rational separation bound',
            'critical_ordering_authority':'exact sign-at-algebraic-root and exact root ordering against x^2+2x-1',
            'separator_synthesis':'closed-form rational-between-algebraics from a certified rational lower enclosure',
            'finite_termination':'derived Cauchy root bound + Mignotte root-separation depth + finite Sturm bisection + one closed-form rational separator',
            'caller_metadata_trusted':False,'binary_float_used':False,'sampling_used':False,'epsilon_used':False,
            'arbitrary_denominator_cap_used':False,'arbitrary_subdivision_depth_used':False,'timeout_truth_authority_used':False,
        }
    except (MemoryError,RecursionError,OverflowError,ExactAlgebraRefusal) as exc:
        return {'status':'RESOURCE_REFUSAL','reason':f'PB00701_V32_EXACT_RESOURCE_REFUSAL:{type(exc).__name__}','is_truth_value':False}
    except (ArithmeticError,ZeroDivisionError) as exc:
        return {'status':'BLOCKED','reason':f'UNSUPPORTED_EXACT_ALGEBRAIC_STRUCTURE:{type(exc).__name__}','blocker':'PB-007-01'}
