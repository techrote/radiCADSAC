"""A1 research prototype: finite signed certificates for simple-root promised H0/H1/H2.

Finite-budget prototype for a conditional promise-termination theorem. A refusal is NONTRUTH.
All certificate arithmetic is fractions; no binary floating-point decisions.
"""
from __future__ import annotations
from receipt_integrity import strict_equal
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from math import factorial
import hashlib, json

POLYS = ("H0", "C1", "S1", "C2", "S2")
MAX_PIECES = 3
MAX_DEGREE = 3
MAX_BITS = 96

class Refusal(ValueError):
    pass

def require(ok, code):
    if not ok: raise Refusal(code)

def canon(q): return f"{q.numerator}/{q.denominator}"

def parse_rat(s):
    require(type(s) is str and 0<len(s)<=100, "TOKEN")
    try: q=Q(s)
    except (ValueError, ZeroDivisionError) as e: raise Refusal("RATIONAL") from e
    require(s == canon(q), "NONCANONICAL")
    require(max(abs(q.numerator).bit_length(), q.denominator.bit_length())<=MAX_BITS,"BITS")
    return q

@dataclass(frozen=True)
class Piece:
    lo: Q
    hi: Q
    p: tuple

@dataclass(frozen=True)
class Source:
    a: Q
    b: Q
    pieces: tuple
    sha256: str


def source(doc):
    require(type(doc) is dict and set(doc)=={"a", "b", "pieces"}, "SOURCE_FIELDS")
    a,b=parse_rat(doc["a"]),parse_rat(doc["b"])
    require(type(doc["pieces"]) is list and 1<=len(doc["pieces"])<=MAX_PIECES,"PIECE_LIMIT")
    out=[]
    for p in doc["pieces"]:
        require(type(p) is dict and set(p)=={"lo","hi",*POLYS},"PIECE_FIELDS")
        lo,hi=parse_rat(p["lo"]),parse_rat(p["hi"])
        require(-16<=lo<hi<=16,"DOMAIN")
        cs=[]
        for name in POLYS:
            data=p[name]
            require(type(data) is list and 1<=len(data)<=MAX_DEGREE+1,"DEGREE")
            cs.append(tuple(parse_rat(x) for x in data))
        out.append(Piece(lo,hi,tuple(cs)))
    for prev,nxt in zip(out,out[1:]):
        require(prev.hi==nxt.lo,"PIECE_GAP")
        # Coefficient-continuity is stronger than physical continuity, but checkable.
        require(all(eval_poly(p,prev.hi)==eval_poly(q,nxt.lo)
                    for p,q in zip(prev.p,nxt.p)),"KNOT_DISCONTINUITY")
    sha=hashlib.sha256(json.dumps(doc,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
    return Source(a,b,tuple(out),sha)

def valid_source(s):
    """Reject forged/mutated Source before consuming a source-bound receipt."""
    try:
        if type(s) is not Source or type(s.a) is not Q or type(s.b) is not Q or type(s.pieces) is not tuple:
            return False
        doc={"a":canon(s.a),"b":canon(s.b),"pieces":[]}
        for p in s.pieces:
            if type(p) is not Piece or type(p.lo) is not Q or type(p.hi) is not Q or type(p.p) is not tuple or len(p.p)!=5:
                return False
            row={"lo":canon(p.lo),"hi":canon(p.hi)}
            for key,coeffs in zip(POLYS,p.p):
                if type(coeffs) is not tuple or not all(type(c) is Q for c in coeffs):return False
                row[key]=[canon(c) for c in coeffs]
            doc["pieces"].append(row)
        renewed=source(doc)
        return renewed == s and renewed.sha256 == s.sha256
    except (TypeError,Refusal,ValueError,AttributeError,OverflowError):return False


def eval_poly(p,x):
    z=Q(0)
    for c in reversed(p): z=z*x+c
    return z

def deriv(p): return tuple(i*p[i] for i in range(1,len(p))) or (Q(0),)
def plus(*xs): return (sum((x[0] for x in xs),Q()),sum((x[1] for x in xs),Q()))
def times(a,b):
    v=(a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1]);return min(v),max(v)
def val(x):return x,x

def horner_range(p,lo,hi):
    r=val(Q())
    for c in reversed(p):r=plus(times(r,(lo,hi)),val(c))
    return r

def polyrange(p,lo,hi):
    direct=horner_range(p,lo,hi)
    if lo==hi or len(p)==1:return direct
    mid=(lo+hi)/2
    derivative=horner_range(deriv(p),lo,hi)
    radius=(hi-lo)/2
    delta=times(derivative,(-radius,radius))
    centered=plus(val(eval_poly(p,mid)),delta)
    # The intersection of two rigorous enclosures is rigorous.
    return max(direct[0],centered[0]),min(direct[1],centered[1])

@lru_cache(maxsize=16)
def pi_bound(n):
    def atan_inv(v):
        x=Q(1,v)
        lo=sum(((-1)**j*x**(2*j+1)/Q(2*j+1) for j in range(2*n)),Q())
        hi=lo+x**(4*n+1)/Q(4*n+1)
        return lo,hi
    a,b=atan_inv(5),atan_inv(239)
    lo,hi=16*a[0]-4*b[1],16*a[1]-4*b[0]
    require(Q(3)<lo<hi<Q(22,7),"PI_BOUND")
    return lo,hi

@lru_cache(maxsize=8192)
def trig_at(q,n):
    q=q%2
    if q>1:q-=2
    pl,pu=pi_bound(n)
    x,y=sorted((q*pl,q*pu))
    z=(x+y)/2; err=(y-x)/2
    sn=sum(((-1)**j*z**(2*j+1)/factorial(2*j+1) for j in range(n+1)),Q())
    cn=sum(((-1)**j*z**(2*j)/factorial(2*j) for j in range(n+1)),Q())
    sr=abs(z)**(2*n+2)/factorial(2*n+2)+err
    cr=abs(z)**(2*n+1)/factorial(2*n+1)+err
    return (sn-sr,sn+sr),(cn-cr,cn+cr)

def trig_cell(s,h,lo,hi,n):
    mid=(lo+hi)/2
    sn,cs=trig_at(h*(s.a+s.b*mid),n)
    radius=abs(h*s.b)*pi_bound(n)[1]*(hi-lo)/2
    return (sn[0]-radius,sn[1]+radius),(cs[0]-radius,cs[1]+radius)

def enclose(s,p,lo,hi,n,derivative=False):
    require(p.lo<=lo<=hi<=p.hi,"PIECE_BOUNDS")
    cs=[polyrange(deriv(x) if derivative else x,lo,hi) for x in p.p]
    res=cs[0]
    for h in (1,2):
        sn,co=trig_cell(s,h,lo,hi,n)
        c,z=2*h-1,2*h
        res=plus(res,times(cs[c],co),times(cs[z],sn))
        if derivative:
            c0=polyrange(p.p[c],lo,hi)
            z0=polyrange(p.p[z],lo,hi)
            w=(h*s.b*pi_bound(n)[0],h*s.b*pi_bound(n)[1])
            if w[0]>w[1]:w=w[::-1]
            res=plus(res,times(w,plus(times(z0,co),times((-c0[1],-c0[0]),sn))))
    return res

def sg(r): return 1 if r[0]>0 else -1 if r[1]<0 else 0

def point_sign(s,p,t,n):return sg(enclose(s,p,t,t,n))

def cell_kind(s,p,lo,hi,n):
    f=enclose(s,p,lo,hi,n)
    if sg(f):return {"kind":"EMPTY","sign":sg(f)}
    l,r=point_sign(s,p,lo,n),point_sign(s,p,hi,n)
    d=sg(enclose(s,p,lo,hi,n,True))
    if d and l and r:
        if l==r:return {"kind":"EMPTY","sign":l}
        if l==-1 and r==1 and d==1:return {"kind":"CROSS","sign":1}
        if l==1 and r==-1 and d==-1:return {"kind":"CROSS","sign":-1}
    return None

def grid(lo,hi,n,j,shifts):
    step=(hi-lo)/n
    delta=Q(j,shifts+1)
    return [lo]+[lo+step*(i+delta) for i in range(n)]+[hi]

def partition(s,limit_level=6,max_shifts=8,precision=(4,6,8,12)):
    require(type(limit_level) is int and type(max_shifts) is int and
            0<=limit_level<=10 and 1<=max_shifts<=32 and
            valid_source(s) and type(precision) is tuple and all(type(k) is int and 3<=k<=16 for k in precision),"BUDGET")
    # Global stage-wise search; each candidate is independently checked.
    for level in range(limit_level+1):
        n=2**level
        for j in range(1,max_shifts+1):
            for k in precision:
                result=[]; good=True
                for pi,p in enumerate(s.pieces):
                    pts=grid(p.lo,p.hi,n,j,max_shifts)
                    for a,b in zip(pts,pts[1:]):
                        kind=cell_kind(s,p,a,b,k)
                        if kind is None:
                            good=False;break
                        result.append({"piece":pi,"lo":canon(a),"hi":canon(b),**kind})
                    if not good: break
                if good:
                    proof={"source_sha256":s.sha256,"level":level,"shift":j,
                           "shifts":max_shifts,"precision":k,"cells":result,
                           "status":"CERTIFIED_SIMPLE_PARTITION"}
                    require(verify(s,proof),"SELF_VERIFICATION")
                    return proof
    raise Refusal("UNRESOLVED_BUDGET_NOT_NO_ROOT")

def verify(s,cert):
    try:
        if not valid_source(s) or type(cert) is not dict or cert.get("status")!="CERTIFIED_SIMPLE_PARTITION" or cert.get("source_sha256")!=s.sha256:return False
        level,j,shifts,k=cert["level"],cert["shift"],cert["shifts"],cert["precision"]
        if not all(type(x) is int for x in (level,j,shifts,k)) or not (0<=level<=10 and 1<=j<=shifts<=32 and 3<=k<=16):return False
        expected=[]
        for i,p in enumerate(s.pieces):
            pts=grid(p.lo,p.hi,2**level,j,shifts)
            for a,b in zip(pts,pts[1:]):
                kind=cell_kind(s,p,a,b,k)
                if kind is None:return False
                expected.append({"piece":i,"lo":canon(a),"hi":canon(b),**kind})
        return strict_equal({"source_sha256":s.sha256,"level":level,"shift":j,"shifts":shifts,
                             "precision":k,"cells":expected,"status":"CERTIFIED_SIMPLE_PARTITION"},cert)
    except (Refusal, KeyError, TypeError, ValueError, ZeroDivisionError):return False

def input_doc(parts,a="0/1",b="1/1"):
    # Test-only constructor: each part = (lo,hi,{channel:[rational strings]})
    items=[]
    for lo,hi,channels in parts:
        row={"lo":lo,"hi":hi}
        row.update({k:channels.get(k,["0/1"]) for k in POLYS});items.append(row)
    return {"a":a,"b":b,"pieces":items}
