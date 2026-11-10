"""Research A1: sound conditional signed local algebraic-time event cells.

Works with sibling algebraic_degree's exact source/irreducibility/Sturm oracle.
Pure Fraction interval bounds; no floating point, finite caps, no MC-B claim.
"""
from fractions import Fraction as Q
from math import factorial
from hashlib import sha256
import json


class Refusal(ValueError):
    """Unknown/unsupported is not a root-free finding."""


def require(ok, code):
    if not ok:
        raise Refusal(code)


def fmt(x):
    return f"{x.numerator}/{x.denominator}"


def trim(p):
    p = list(p)
    while p and not p[-1]:
        p.pop()
    return tuple(p)


def divrem(a,b):
    a,b=trim(a),trim(b)
    require(bool(b),'ZERO_DIVISOR')
    r=list(a); q=[Q(0)]*max(0,len(a)-len(b)+1)
    while len(r)>=len(b):
        j=len(r)-len(b); c=r[-1]/b[-1];q[j]=c
        for i,v in enumerate(b):r[j+i]-=c*v
        r=list(trim(r))
    return tuple(q),tuple(r)


def evalp(p,x):
    v=Q(0)
    for c in reversed(p):v=v*x+c
    return v


def atan_interval(x, n):
    """Alternating arctan series with signed remainder, 0 < x < 1."""
    require(Q(0)<x<Q(1) and 1<=n<=32,'ATAN_INPUT')
    s=sum(((-1)**j*x**(2*j+1)/Q(2*j+1) for j in range(n)),Q(0))
    err=x**(2*n+1)/Q(2*n+1)
    return (s,s+err) if n%2==0 else (s-err,s)


def pi_interval(n):
    a,b=atan_interval(Q(1,5),n),atan_interval(Q(1,239),n)
    lo,hi=16*a[0]-4*b[1],16*a[1]-4*b[0]
    require(Q(3)<lo<hi<Q(22,7),'PI_ENCLOSURE')
    return lo,hi


def trig_interval(phase, harmonic, n, pi_bounds):
    """Closed enclosures of sin/cos(h*pi*phase), full rational phase."""
    require(type(phase) is Q and harmonic in (1,2) and 4<=n<=32,'TRIG_INPUT')
    beta=phase*harmonic
    beta-=2*((beta+1)//2) # exact 2-period reduction to [-1,1)
    pl,ph=pi_bounds
    mid=(pl+ph)/2
    x=beta*mid
    shift=abs(beta)*(ph-pl)/2
    s=sum(((-1)**j*x**(2*j+1)/Q(factorial(2*j+1)) for j in range(n)),Q(0))
    c=sum(((-1)**j*x**(2*j)/Q(factorial(2*j)) for j in range(n)),Q(0))
    es=abs(x)**(2*n+1)/Q(factorial(2*n+1))+shift
    ec=abs(x)**(2*n)/Q(factorial(2*n))+shift
    return (c-ec,c+ec),(s-es,s+es)


def magnitude(p,T):
    return sum((abs(c)*T**i for i,c in enumerate(p)),Q(0))


def derivative_magnitude(p,T):
    return sum((i*abs(c)*T**(i-1) for i,c in enumerate(p) if i),Q(0))


def add_scaled(bounds, amplitude, interval):
    lo,hi=bounds
    x,y=amplitude*interval[0],amplitude*interval[1]
    return lo+min(x,y),hi+max(x,y)


def cofactor_closed_sign(qchannels,a,b,lo,hi,n=16):
    """Exact proof that Fourier cofactor has one strict sign on [lo,hi]."""
    require(len(qchannels)==5 and all(type(p) is tuple for p in qchannels),'CHANNELS')
    require(type(a) is Q and type(b) is Q and b!=0,'PHASE')
    require(type(lo) is Q and type(hi) is Q and lo<hi,'BRACKET')
    require(type(n) is int and 4<=n<=32,'TERM_BUDGET')
    q=(lo+hi)/2
    phase=a+b*q
    pb=pi_interval(n)
    result=(evalp(qchannels[0],q),)*2
    for h in (1,2):
        cosi,sini=trig_interval(phase,h,n,pb)
        result=add_scaled(result,evalp(qchannels[2*h-1],q),cosi)
        result=add_scaled(result,evalp(qchannels[2*h],q),sini)
    T=max(Q(1),abs(lo),abs(hi))
    L=derivative_magnitude(qchannels[0],T)
    for h in (1,2):
        for p in (qchannels[2*h-1],qchannels[2*h]):
            L+=derivative_magnitude(p,T)+Q(22,7)*h*abs(b)*magnitude(p,T)
    radius=(hi-lo)/2
    closed=(result[0]-L*radius,result[1]+L*radius)
    if closed[0]>0: sign=1
    elif closed[1]<0: sign=-1
    else: raise Refusal('COFACTOR_SIGN_UNKNOWN')
    return {"midpoint":fmt(q),"pi_bounds":list(map(fmt,pb)),
            "value_bounds":list(map(fmt,result)),"lipschitz_bound":fmt(L),
            "closed_bounds":list(map(fmt,closed)),"cofactor_sign":sign}


def signed_from_verified_germ(doc, minimal, bracket, germ, terms=16):
    """Consumed only after independent replay of A1 germ and unique-root proof."""
    require(germ.get('result')=='EXACT_ZERO' and type(germ.get('multiplicity')) is int
            and germ['multiplicity']>=1,'NOT_ISOLATED_ALGEBRAIC_ZERO')
    r=germ['multiplicity'];m=tuple(Q(x) for x in minimal)
    lo,hi=(Q(v) for v in bracket)
    qchannels=[]
    for key in ('H0','C1','S1','C2','S2'):
        p=trim(tuple(Q(x) for x in doc[key]))
        for _ in range(r):
            p,rem=divrem(p,m)
            require(not rem,'VALUATION_MISMATCH')
        qchannels.append(p)
    qchannels=tuple(qchannels)
    require(any(qchannels),'COFACTOR_IDENTITY')
    ma,mb=evalp(m,lo),evalp(m,hi)
    require(ma*mb<0,'BRACKET_NOT_SIMPLE_CROSSING')
    sign=cofactor_closed_sign(qchannels,Q(doc['a']),Q(doc['b']),lo,hi,terms)
    sg=sign['cofactor_sign']
    left=sg*(1 if ma>0 or r%2==0 else -1)
    right=sg*(1 if mb>0 or r%2==0 else -1)
    return {"schema":"a1-signed-algebraic-cell/1","source_sha256":germ['source_sha256'],
            "germ":germ,"minimal_polynomial":list(minimal),"root_bracket":list(bracket),
            "pi_turns":True,"series_terms":terms,"local_root_count":1,"multiplicity":r,
            "left_sign":left,"right_sign":right,"zero_kind":"CROSS" if r%2 else "TOUCH",
            "strict_cofactor_witness":sign,"physical_source_authentication":"UNVERIFIED"}


def certify(doc,minimal,prime,bracket,terms=16):
    from algebraic_degree import certify as germ_certify
    germ=germ_certify(doc,minimal,prime,bracket)
    return signed_from_verified_germ(doc,minimal,bracket,germ,terms)


def verify(doc,receipt):
    from algebraic_degree import verify as verify_germ
    try:
        if type(receipt) is not dict or not verify_germ(doc,receipt['germ']):
            return False
        germ=receipt['germ']
        return certify(doc,receipt['minimal_polynomial'],germ['irreducibility_prime'],
                       receipt['root_bracket'],receipt['series_terms'])==receipt
    except (KeyError,ValueError,TypeError,ZeroDivisionError,OverflowError):
        return False
