#!/usr/bin/env python3
"""Research: one synthetic second quadratic cut on frozen V44 original source.

A strictly scoped Q(sqrt(2),sqrt(3)) construction. The sqrt(3)/3 cut is NOT
an historical V41 orientation owner; this does not admit V54 or pass MC-B.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as Q
import pb00701_v44_mixed_cut_child_interface as parent

SCHEMA="radicadsac-pb00701-v44-two-quadratic-restriction/1.0"
SUCCESS="FROZEN_V44_SYNTHETIC_TWO_QUADRATIC_DETERMINISTIC_MODEL"
PARENT_BLOB="4de3a6d8eeb34bfc8debb418e169a1b6d743ff5f"
CAP=65536

class Refusal(ValueError): pass
class ResourceRefusal(RuntimeError): pass

def require(v,reason):
    if not v: raise Refusal(reason)

def psign(x):
    a,b=x
    if a==0:return (b>0)-(b<0)
    if b==0 or (a>0)==(b>0):return (a>0)-(a<0)
    delta=a*a-2*b*b
    require(delta!=0,"QUADRATIC_FIELD_INDEPENDENCE")
    return ((a>0)-(a<0))*((delta>0)-(delta<0))

def pmul(x,y):
    a,b=x;c,d=y
    return a*c+2*b*d,a*d+b*c

def psub(x,y):return x[0]-y[0],x[1]-y[1]

@dataclass(frozen=True)
class K:
    """Exact coefficients (a,b,c,d) for a+b√2+c√3+d√6."""
    v:tuple
    def __post_init__(self):
        require(type(self.v) is tuple and len(self.v)==4
                and all(type(x) is Q for x in self.v),"NONEXACT_FIELD_COEFFICIENT")
    @staticmethod
    def of(x):
        if type(x) is K:return x
        require(type(x) in (int,Q),"NONEXACT_FIELD_OPERAND")
        return K((Q(x),Q(0),Q(0),Q(0)))
    def __add__(self,x):
        x=K.of(x)
        return K(tuple(a+b for a,b in zip(self.v,x.v)))
    __radd__=__add__
    def __neg__(self):return K(tuple(-a for a in self.v))
    def __sub__(self,x):return self+-K.of(x)
    def __rsub__(self,x):return K.of(x)-self
    def __mul__(self,x):
        x=K.of(x);a,b,c,d=self.v;e,f,g,h=x.v
        p=pmul((a,b),(e,f));q=pmul((c,d),(g,h))
        z=pmul((a,b),(g,h));w=pmul((c,d),(e,f))
        return K((p[0]+3*q[0],p[1]+3*q[1],z[0]+w[0],z[1]+w[1]))
    __rmul__=__mul__
    def zero(self):return all(x==0 for x in self.v)
    def sign(self):
        a,b,c,d=self.v
        sa,sb=psign((a,b)),psign((c,d))
        if sa==0:return sb
        if sb==0 or sa==sb:return sa
        t=psub(pmul((a,b),(a,b)),tuple(3*v for v in pmul((c,d),(c,d))))
        st=psign(t)
        require(st!=0,"BIQUADRATIC_FIELD_INDEPENDENCE")
        return sa*st
    def inverse(self):
        require(not self.zero(),"ZERO_INVERSE")
        a,b,c,d=self.v
        den=psub(pmul((a,b),(a,b)),tuple(3*v for v in pmul((c,d),(c,d))))
        require(psign(den)!=0,"BIQUADRATIC_NORM_ZERO")
        n=den[0]*den[0]-2*den[1]*den[1]
        require(n!=0,"QUADRATIC_NORM_ZERO")
        inv=(den[0]/n,-den[1]/n)
        u=pmul((a,b),inv);v=pmul((-c,-d),inv)
        answer=K(u+v)
        require(self*answer==K.of(1),"INVERSE_REPLAY_MISMATCH")
        return answer
    def record(self):return [str(x) for x in self.v]
    @staticmethod
    def parse(value):
        require(type(value) is list and len(value)==4
                and all(type(x) is str for x in value),"INVALID_FIELD_RECORD")
        out=K(tuple(Q(x) for x in value))
        require(out.record()==value,"NONCANONICAL_FIELD_RECORD")
        return out

def affine(poly,a,w):
    require(type(poly) in (list,tuple) and 1<=len(poly)<=32
            and type(a) is K and type(w) is K,"INVALID_AFFINE_POLYNOMIAL")
    result=[K.of(0)]
    for p in reversed(poly):
        nxt=[K.of(0) for _ in range(len(result)+1)]
        for i,c in enumerate(result):
            nxt[i]=nxt[i]+c*a;nxt[i+1]=nxt[i+1]+c*w
        nxt[0]=nxt[0]+K.of(p)
        while len(nxt)>1 and nxt[-1].zero():nxt.pop()
        result=nxt
    return result

def pins():
    p=parent.bridge.previous
    require(p.git_blob(p.TASK/"pb00701_v44_mixed_cut_child_interface.py")
            ==PARENT_BLOB,"PINNED_PARENT_SOURCE_DRIFT")
    parent.pins()

def prove():
    pins()
    upstream=parent.prove()
    require(upstream["status"]==parent.SUCCESS
            and upstream["historical_v54_admitted"] is False,
            "PARENT_SOURCE_NOT_CERTIFIED")
    atlas,span,_,_=parent.derivative._source_snapshot(None)
    require(span.left==0 and span.right==1
            and span.offset==Q(-1,8) and span.rate==Q(1,16),
            "SOURCE_PHASE_DRIFT")
    # Field identity: sqrt(3) not in Q(sqrt(2)); K basis has degree four.
    alpha=K((Q(0),Q(1,2),Q(0),Q(0)))
    beta=K((Q(0),Q(0),Q(1,3),Q(0)))
    zero,one=K.of(0),K.of(1)
    require((2*alpha*alpha-one).zero()
            and (3*beta*beta-one).zero()
            and beta.sign()==1 and (alpha-beta).sign()==1
            and (one-alpha).sign()==1,"SYNTHETIC_CUT_ORDER_INVALID")
    # New beta value sign is independently transported from rational-source
    # trig enclosures with exact Sturm isolation and a global Lipschitz bound.
    v45=parent.v45
    poly=(-1,0,3)
    beta_field=v45.RealField(poly,v45._canonical_interval(poly,0),0)
    beta_sign=parent.source_sign.certify_strict_sign(span,beta_field)
    require(beta_sign["strict_nonzero_sign"]==1,"BETA_SOURCE_SIGN_NOT_POSITIVE")
    inherited=upstream["independently_recomputed_boundary_signs"]
    irr=[x for x in inherited if x["method"]==
        "EXACT_STURM_RATIONAL_MIDPOINT_OUTWARD_TRIG_LIPSCHITZ"]
    require(len(irr)==1 and irr[0]["strict_nonzero_sign"]==1
            and inherited[0]["strict_nonzero_sign"]==-1
            and inherited[-1]["strict_nonzero_sign"]==1,
            "ORIGINAL_SOURCE_SIGNS_NOT_REPLAYED")
    m=Q(upstream["global_strict_source_derivative_lower"])
    require(m>0,"MISSING_STRICT_GLOBAL_DERIVATIVE")
    endpoints=[zero,beta,alpha,one];signs=[-1,1,1,1]
    children=[];counts=[]
    for i in range(3):
        a,b=endpoints[i:i+2];w=b-a
        require(w.sign()==1 and (w*m).sign()==1,"CHILD_WIDTH_OR_DERIVATIVE_NOT_POSITIVE")
        inv=w.inverse();channels={}
        for h,pair in sorted(span.terms.items()):
            out=[]
            for p in pair:
                restricted=affine(p,a,w)
                require(affine(restricted,-a*inv,inv)==[K.of(x) for x in p],
                        "SOURCE_POLYNOMIAL_INVERSE_ROUNDTRIP_FAILED")
                out.append([c.record() for c in restricted])
            channels[str(h)]=out
        count=int(signs[i]==-1 and signs[i+1]==1)
        counts.append(count)
        children.append(dict(index=i,offset=a.record(),width=w.record(),
            right=b.record(),phase_offset=(K.of(span.offset)+a*span.rate).record(),
            phase_rate=(w*span.rate).record(),
            derivative_lower=(w*m).record(),channels=channels,root_count=count))
    require(counts==[1,0,0] and sum(counts)==1
            and upstream["complete_open_simple_physical_root_counts"]==[0,1,0,0],
            "FROZEN_ROOT_CONSERVATION_FAILED")
    pins()
    return dict(schema=SCHEMA,status=SUCCESS,evidence_class="DETERMINISTIC_MODEL",
        source_sha256=upstream["source_sha256"],source_parameter_id=atlas["source_parameter_id"],
        source_phase=[str(span.offset),str(span.rate)],
        exact_field_basis=["1","sqrt(2)","sqrt(3)","sqrt(6)"],
        cut_order=["0","sqrt(3)/3","sqrt(2)/2","1"],
        beta_minimal_polynomial=[-1,0,3],
        beta_isolation=[str(v) for v in beta_field.interval],
        beta_source_sign=beta_sign["strict_nonzero_sign"],
        beta_sign_method=beta_sign["strict_sign_certification_method"],
        beta_refinements=beta_sign["certificate"]["refinements_used"],
        boundary_signs=signs,source_derivative_lower=str(m),
        synthetic_closed_children=children,synthetic_open_root_counts=counts,
        synthetic_cut_is_historical_orientation_owner=False,
        general_multifield_compositum_constructed=False,
        general_irrational_trig_zero_decider_constructed=False,
        historical_v54_admitted=False,pb00701_certified=False,
        mc_b_established=False,mc1_established=False,
        native_geometry_or_step_qualified=False,production_authorized=False)

def nontruth(why,status="BLOCKED"):
    return dict(schema=SCHEMA,status=status,reason=str(why),
        is_truth_value=False,historical_v54_admitted=False,
        mc_b_established=False,mc1_established=False,production_authorized=False)

def attempt():
    try:return prove()
    except (ResourceRefusal,parent.ResourceRefusal,parent.source_sign.ResourceRefusal,
            parent.bridge.ResourceRefusal,MemoryError,OverflowError,
            RecursionError) as e:return nontruth(e,"RESOURCE_REFUSAL")
    except (Refusal,parent.Refusal,parent.source_sign.Refusal,
            parent.bridge.Refusal,ValueError,TypeError,KeyError,
            IndexError,AssertionError,AttributeError,ZeroDivisionError) as e:
        return nontruth(e)

def validate_report(submitted):
    try:
        parent.bridge.predecessor._bound_untrusted_report_structure(submitted)
        claimed=parent.bridge.previous.canonical(submitted)
        if len(claimed)>CAP:raise ResourceRefusal("SUBMITTED_REPORT_OVER_64K")
        expected=attempt()
        require(expected["status"]==SUCCESS,"SOURCE_PROOF_NOT_AVAILABLE")
        require(claimed==parent.bridge.previous.canonical(expected),"FORGED_REPORT")
        return expected
    except (ResourceRefusal,parent.bridge.predecessor.ResourceRefusal,
            MemoryError,OverflowError,RecursionError) as e:
        return nontruth(e,"RESOURCE_REFUSAL")
    except (Refusal,parent.bridge.previous.ResearchRefusal,ValueError,
            TypeError,KeyError) as e:return nontruth(e)
