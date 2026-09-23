#!/usr/bin/env python3
from __future__ import annotations
from fractions import Fraction as F
import copy
import pb00701_algebraic_separator_foundation_model as model

def must_cert(d,t,sign=1):
    r=model.synthesize_separator(d,t,sign)
    assert r['status']=='CERTIFIED',r
    assert model.verify_binding(r)
    m=F(r['rational_separator'])
    assert model._compare_rational_alpha(m)>0
    assert model._strict_positive([F(x) for x in r['global_margin_minus']])
    assert model._strict_positive([F(x) for x in r['global_margin_plus']])
    assert r['caller_metadata_trusted'] is False
    for k in ('binary_float_used','sampling_used','epsilon_used','arbitrary_denominator_cap_used','arbitrary_subdivision_depth_used','timeout_truth_authority_used'):
        assert r[k] is False
    return r

def run():
    # v31 diagnostic: global floor/ceiling is 1/5, but v32 synthesizes a source-owned separator.
    diag=must_cert([1,2],[2,3])
    assert F(diag['rational_separator']) != F(5,12)
    assert not diag['stationary_roots']

    # Interior irrational stationary minimum; endpoint-only reasoning is insufficient.
    interior=must_cert([2,-1,0,1],[3])
    assert len(interior['stationary_roots'])==1
    assert interior['stationary_roots'][0]['kind']=='RATIONAL_ISOLATING_INTERVAL'
    assert interior['candidate_orderings'][-1]['kind']=='STATIONARY'
    assert interior['candidate_orderings'][-1]['relation_to_sqrt2_minus_1']==1

    # Exact algebraic transverse zero yields two independently signed cells.
    alg_t=must_cert([1],[F(-1,2),0,1])
    assert len(alg_t['transverse_roots'])==1
    assert [c['transverse_sign'] for c in alg_t['transverse_sign_cells']]==[-1,1]

    # A repeated transverse zero can coincide with a stationary-polynomial root; it is excluded from finite minima.
    coincident=must_cert([1],[F(1,4),-1,1])
    assert coincident['transverse_roots'][0]['multiplicity']==2
    assert coincident['stationary_roots'][0]['value']=='1/2'
    assert any(c['kind']=='STATIONARY_TRANSVERSE_ZERO' for c in coincident['candidate_orderings'])

    # Repeated stationary root is retained with exact multiplicity.
    repeated=must_cert([F(9,16),F(-1,2),F(3,2),-2,1],[1])
    assert repeated['stationary_roots']==[{'kind':'POINT','value':'1/2','multiplicity':3,'independently_checkable':True}]

    # Exact sqrt(2)-1 equality at the interior stationary minimum fails closed; signed rational neighbours straddle it.
    base_t=[F(9,4),F(3,4),F(-3,4),F(-1,4)]
    eq=model.synthesize_separator([1],base_t)
    assert eq['status']=='BLOCKED' and eq['reason']=='PROJECTIVE_MINIMUM_NOT_STRICTLY_ABOVE_TAN_PI_8'
    assert any(c.get('relation_to_sqrt2_minus_1')==0 for c in eq['candidate_orders'])
    above_t=base_t[:];above_t[0]-=F(1,1000000) # smaller denominator => ratio above boundary
    must_cert([1],above_t)
    below_t=base_t[:];below_t[0]+=F(1,1000000)
    below=model.synthesize_separator([1],below_t)
    assert below['status']=='BLOCKED'
    assert any(c.get('relation_to_sqrt2_minus_1')==-1 for c in below['candidate_orders'])

    # Independent rational controls around the algebraic boundary.
    assert model._compare_rational_alpha(F(70,169))<0
    assert model._compare_rational_alpha(F(169,408))>0

    # Dominant/transverse orientations, including sign-changing transverse data.
    must_cert([-1,-2],[2,3],-1)
    must_cert([1,2],[-2,-3],1)
    sign_cells=must_cert([1],[F(-1,2),1])
    assert [c['transverse_sign'] for c in sign_cells['transverse_sign_cells']]==[-1,1]

    # Exact common polynomial factor is cancelled source-algebraically, not numerically.
    common=must_cert([2,3,1],[3,4,1]) # (s+1)(s+2) / (s+1)(s+3)
    assert common['reduced_dominant_polynomial'] != ['2','3','1']

    # Caller certificates are non-authoritative; malformed numeric authority is rejected.
    for forged in (
        {'separator':'5/12'}, {'critical_root':'1/2'}, {'critical_value':'0.5'},
        {'root_ordering':'above'}, {'margin_certificate':True}, {'multiplicity':1},
    ):
        try:model.synthesize_separator([1,2],[2,3],caller_assertions=forged)
        except ValueError:pass
        else:raise AssertionError('forged caller algebraic metadata accepted')
    try:model.synthesize_separator([1.0,2],[2,3])
    except TypeError:pass
    else:raise AssertionError('binary float accepted as exact authority')
    mismatch=model.synthesize_separator([1,2],[2,3],source_parameter_id='independent-t')
    assert mismatch['status']=='SEMANTIC_BLOCKER'
    refusal=model.synthesize_separator([1,2],[2,3],force_resource_refusal=True)
    assert refusal=={'status':'RESOURCE_REFUSAL','reason':'PB00701_V32_FORCED_EXACT_RESOURCE_REFUSAL','is_truth_value':False}

    # Binding is source-owned and tamper evident.
    tampered=copy.deepcopy(diag);tampered['canonical_source']['dominant'][0]='999'
    assert not model.verify_binding(tampered)

    print('PB-007-01 v32 exact algebraic separator foundation adversarial tests: PASS')

if __name__=='__main__': run()
