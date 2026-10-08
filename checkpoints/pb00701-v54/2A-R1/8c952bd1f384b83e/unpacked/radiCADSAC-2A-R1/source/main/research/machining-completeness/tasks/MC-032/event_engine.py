#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json

TERMINAL = {
    "DECIDED", "CERTIFIED", "BLOCKED", "UNCERTIFIED",
    "RESOURCE_REFUSAL", "SEMANTIC_BLOCKER"
}

def q(value):
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("correctness-authority rationals must not be bool/float")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    raise TypeError(f"unsupported rational type: {type(value).__name__}")

def _trim(p):
    p = [q(x) for x in p]
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p or [Fraction(0)]

def degree(p):
    p = _trim(p)
    return -1 if p == [0] else len(p) - 1

def peval(p, x):
    x=q(x); acc=Fraction(0)
    for c in reversed(_trim(p)):
        acc=acc*x+c
    return acc

def deriv(p):
    p=_trim(p)
    if len(p)<=1:
        return [Fraction(0)]
    return _trim([Fraction(i)*p[i] for i in range(1,len(p))])

def pdivmod(a,b):
    a=_trim(a); b=_trim(b)
    if b == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    if degree(a)<degree(b):
        return [Fraction(0)], a
    quotient=[Fraction(0)]*(degree(a)-degree(b)+1)
    rem=a[:]
    while rem != [0] and degree(rem)>=degree(b):
        k=degree(rem)-degree(b)
        c=rem[-1]/b[-1]
        quotient[k]+=c
        for i,bc in enumerate(b):
            rem[i+k]-=c*bc
        rem=_trim(rem)
    return _trim(quotient), _trim(rem)

def monic(p):
    p=_trim(p)
    if p==[0]: return p
    lead=p[-1]
    return _trim([c/lead for c in p])

def pgcd(a,b):
    a=_trim(a); b=_trim(b)
    while b != [0]:
        _,r=pdivmod(a,b)
        a,b=b,r
    return monic(a)

def square_free(p):
    p=_trim(p)
    if degree(p)<=0: return p
    g=pgcd(p,deriv(p))
    out,rem=pdivmod(p,g)
    if rem != [0]:
        raise ArithmeticError("non-exact polynomial gcd division")
    return monic(out)

def sign(v):
    v=q(v)
    return 1 if v>0 else -1 if v<0 else 0

def multiplicity_at(p,x):
    p=_trim(p); x=q(x)
    if p == [0]:
        return None
    if peval(p,x)!=0:
        return 0
    m=0
    cur=p
    while cur != [0] and peval(cur,x)==0:
        m+=1
        cur=deriv(cur)
    return m

def exact_event(p,x):
    p=_trim(p); x=q(x)
    if p == [0]:
        return {
            "status":"BLOCKED", "reason":"DEGENERATE_IDENTITY_ZERO",
            "blocker":"ALGEBRAIC_IDENTITY_BLOCKER"
        }
    value=peval(p,x)
    if value:
        return {"status":"DECIDED","relation":"POSITIVE" if value>0 else "NEGATIVE","value":str(value),"multiplicity":0}
    m=multiplicity_at(p,x)
    return {
        "status":"DECIDED",
        "relation":"ZERO",
        "multiplicity":m,
        "singular":m>1,
        "event_kind":(
            "SIMPLE_CROSSING" if m==1
            else "MULTIPLE_CROSSING" if m%2
            else "MULTIPLE_TANGENCY"
        ),
        "sign_change":bool(m%2)
    }

def _one_sided_sign(p,x,side):
    """Sign immediately to one side of x, exact for a nonzero polynomial."""
    p=_trim(p); x=q(x)
    if p == [0]:
        return 0
    cur=p
    order=0
    while cur != [0]:
        v=peval(cur,x)
        if v:
            s=sign(v)
            return s if side=="right" or order%2==0 else -s
        cur=deriv(cur); order+=1
    return 0

def sturm_sequence(p):
    p=square_free(p)
    if degree(p)<=0:
        return [p]
    seq=[p,deriv(p)]
    while seq[-1] != [0]:
        _,r=pdivmod(seq[-2],seq[-1])
        if r == [0]:
            break
        seq.append(_trim([-c for c in r]))
    return seq

def _variations(signs):
    nz=[s for s in signs if s]
    return sum(a!=b for a,b in zip(nz,nz[1:]))

def distinct_roots_open(p,a,b):
    a=q(a); b=q(b)
    if not a<b:
        raise ValueError("require a < b")
    seq=sturm_sequence(p)
    va=_variations([_one_sided_sign(s,a,"right") for s in seq])
    vb=_variations([_one_sided_sign(s,b,"left") for s in seq])
    return va-vb

def classify_open_interval(p,a,b):
    """MC032-A: classify only when exact root evidence excludes the boundary."""
    a=q(a); b=q(b)
    if not a<b:
        raise ValueError("require a < b")
    ea=exact_event(p,a); eb=exact_event(p,b)
    if ea.get("relation")=="ZERO" or eb.get("relation")=="ZERO":
        return {"status":"BLOCKED","reason":"CRITICAL_EVENT_AT_INTERVAL_ENDPOINT","next_owner":"MC032-B"}
    n=distinct_roots_open(p,a,b)
    if n:
        return {"status":"BLOCKED","reason":"CRITICAL_EVENT_IN_INTERVAL","distinct_root_count":n,"next_owner":"MC032-B"}
    mid=(a+b)/2
    v=peval(p,mid)
    if v==0:
        raise AssertionError("Sturm exclusion inconsistent with midpoint")
    return {"status":"DECIDED","relation":"POSITIVE" if v>0 else "NEGATIVE","root_free":True}

def _certified_fraction(value, name):
    try:
        return q(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{name} must be an exact rational encoding") from exc

def validate_analytic_evidence(evidence):
    """Consume evidence only; never evaluate transcendental functions using binary float."""
    if not isinstance(evidence,dict) or evidence.get("certified") is not True:
        return {"status":"UNCERTIFIED","reason":"ANALYTIC_EVIDENCE_NOT_CERTIFIED"}
    if not evidence.get("source_parameter_id"):
        return {"status":"SEMANTIC_BLOCKER","reason":"MISSING_SHARED_SOURCE_PARAMETER"}
    if evidence.get("parameter_projection") not in (None, evidence["source_parameter_id"]):
        return {"status":"SEMANTIC_BLOCKER","reason":"INDEPENDENT_PARAMETER_PROJECTION_FORBIDDEN"}
    kind=evidence.get("kind")
    if kind=="SEPARATED_INTERVAL":
        lo=_certified_fraction(evidence.get("lower_bound"),"lower_bound")
        hi=_certified_fraction(evidence.get("upper_bound"),"upper_bound")
        if lo>hi:
            return {"status":"SEMANTIC_BLOCKER","reason":"INVERTED_CERTIFIED_INTERVAL"}
        if lo>0 or hi<0:
            return {"status":"CERTIFIED","relation":"NO_ZERO","certificate_kind":kind}
        return {"status":"BLOCKED","reason":"ZERO_NOT_EXCLUDED","blocker":"PB-007-01"}
    if kind=="TRANSVERSAL_ROOT":
        if evidence.get("unique_root") is not True:
            return {"status":"BLOCKED","reason":"ROOT_UNIQUENESS_NOT_CERTIFIED","blocker":"PB-007-01"}
        dlo=_certified_fraction(evidence.get("derivative_abs_lower"),"derivative_abs_lower")
        if dlo<=0:
            return {"status":"BLOCKED","reason":"TRANSVERSALITY_NOT_CERTIFIED","blocker":"PB-007-01"}
        a=_certified_fraction(evidence.get("parameter_lo"),"parameter_lo")
        b=_certified_fraction(evidence.get("parameter_hi"),"parameter_hi")
        if not a<=b:
            return {"status":"SEMANTIC_BLOCKER","reason":"INVERTED_PARAMETER_INTERVAL"}
        return {
            "status":"CERTIFIED","relation":"SIMPLE_ZERO_ISOLATED",
            "certificate_kind":kind,"parameter_interval":[str(a),str(b)]
        }
    return {
        "status":"BLOCKED",
        "reason":"TANGENTIAL_MULTIPLE_SINGULAR_OR_UNSUPPORTED_ANALYTIC_EVENT",
        "blocker":"PB-007-01"
    }

def resource_refusal(reason="EVENT_BUDGET_EXHAUSTED"):
    return {"status":"RESOURCE_REFUSAL","reason":reason,"is_truth_value":False}

def certify_topology_event(event):
    if not isinstance(event,dict):
        return {"status":"UNCERTIFIED","reason":"MISSING_TOPOLOGY_EVENT_EVIDENCE"}
    if event.get("event_evidence_status") not in {"DECIDED","CERTIFIED"}:
        return {"status":"UNCERTIFIED","reason":"EVENT_NOT_INDEPENDENTLY_CERTIFIED"}
    for key in ("source_parameter_id","common_frame","input_revision","body_id"):
        if not event.get(key):
            return {"status":"SEMANTIC_BLOCKER","reason":f"MISSING_{key.upper()}"}
    if event.get("durable_identity_source")=="backend_topology_id":
        return {"status":"SEMANTIC_BLOCKER","reason":"BACKEND_TOPOLOGY_IS_NOT_DURABLE_IDENTITY"}
    volume=_certified_fraction(event.get("positive_volume_witness","0"),"positive_volume_witness")
    if volume<0:
        return {"status":"SEMANTIC_BLOCKER","reason":"NEGATIVE_VOLUME_WITNESS"}
    if volume==0:
        return {
            "status":"DECIDED","relation":"TOUCHING_ONLY_NO_MATERIAL_TRANSITION",
            "body_transition":False
        }
    if event.get("independent_connectivity_certificate") is not True:
        return {
            "status":"BLOCKED","reason":"CONNECTIVITY_NOT_CERTIFIED",
            "blocker":"PB-007-04"
        }
    return {
        "status":"CERTIFIED",
        "relation":"CRITICAL_TOPOLOGY_EVENT",
        "positive_volume_witness":str(volume),
        "durable_transition_owner":"MC-033",
        "body_transition_committed":False
    }

def bind_event_certificate(*, input_digest, canonical_digest, sweep_digest,
                           challenge_id, configuration_digest, decision):
    payload={
        "schema":"radicadsac-mc032-event-certificate/1.0",
        "input_digest":input_digest,
        "canonical_digest":canonical_digest,
        "sweep_digest":sweep_digest,
        "challenge_id":challenge_id,
        "configuration_digest":configuration_digest,
        "decision":decision,
    }
    raw=json.dumps(payload,sort_keys=True,separators=(",",":")).encode()
    payload["binding_sha256"]=sha256(raw).hexdigest()
    return payload

def verify_event_certificate(cert, **expected):
    if not isinstance(cert,dict):
        return False
    payload={k:v for k,v in cert.items() if k!="binding_sha256"}
    raw=json.dumps(payload,sort_keys=True,separators=(",",":")).encode()
    if sha256(raw).hexdigest()!=cert.get("binding_sha256"):
        return False
    return all(cert.get(k)==v for k,v in expected.items())

def terminal_status(result):
    s=result.get("status") if isinstance(result,dict) else None
    if s not in TERMINAL:
        raise ValueError("non-terminal or unknown result state")
    return s
