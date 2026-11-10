#!/usr/bin/env python3
"""A2 experimental, exact signed germs at rational-quadratic irrational time.

Research only. Standalone Fraction/isqrt oracle, not authenticated physical
B-spline source custody, global root isolation or production authority.
"""
from __future__ import annotations

from fractions import Fraction as Q
from hashlib import sha256
from math import comb, factorial, isqrt
import json

SCHEMA = "radicadsac/a2-quadratic-signed-germ/1"
MAX_DEGREE = 12
MAX_HARMONIC = 2
MAX_BITS = 96
PRECISIONS = (6, 10, 16, 24, 36, 52)


class Refusal(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise Refusal(message)


def rational(x):
    require(type(x) in (int, Q), "EXACT_RATIONAL_REQUIRED")
    q = Q(x)
    require(max(q.numerator.bit_length(), q.denominator.bit_length()) <= MAX_BITS,
            "INPUT_RATIONAL_BUDGET")
    return q


def poly(value):
    require(type(value) in (tuple, list) and len(value) <= MAX_DEGREE + 1,
            "POLYNOMIAL_SHAPE_OR_BUDGET")
    out = [rational(x) for x in value]
    while out and out[-1] == 0:
        out.pop()
    return tuple(out)


def source(left, right, offset, rate, terms):
    left, right, offset, rate = map(rational, (left, right, offset, rate))
    require(left < right and rate != 0, "INVALID_INTERVAL_OR_RATE")
    require(type(terms) is dict and 1 <= len(terms) <= MAX_HARMONIC + 1,
            "INVALID_TERMS")
    clean = {}
    for h, pair in terms.items():
        require(type(h) is int and 0 <= h <= MAX_HARMONIC and h not in clean,
                "INVALID_HARMONIC")
        require(type(pair) in (tuple, list) and len(pair) == 2,
                "INVALID_CHANNEL_PAIR")
        p, q = poly(pair[0]), poly(pair[1])
        require(h or not q, "H0_SINE_FORBIDDEN")
        clean[h] = (p, q)
    return {"left": left, "right": right, "offset": offset,
            "rate": rate, "terms": dict(sorted(clean.items()))}


def canonical(s):
    require(type(s) is dict and set(s) == {"left", "right", "offset", "rate", "terms"},
            "INVALID_SOURCE_SHAPE")
    rebuilt = source(s["left"], s["right"], s["offset"], s["rate"], s["terms"])
    require(all(type(k) is str for k in s), "SOURCE_KEY_TYPE")
    require(s == rebuilt, "NONCANONICAL_SOURCE")
    return rebuilt


def source_blob(s):
    return {"bounds": [str(s["left"]), str(s["right"])],
            "phase_turns": [str(s["offset"]), str(s["rate"])],
            "channels": {str(h): [[str(x) for x in a], [str(x) for x in b]]
                         for h, (a,b) in s["terms"].items()}}


def digest(v):
    return sha256(json.dumps(v, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def qadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def qmul(a, b, D):
    return a[0]*b[0] + D*a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def qsign(a, D):
    x,y = a
    if y == 0:
        return (x > 0) - (x < 0)
    if x == 0:
        return (y > 0) - (y < 0)
    if x > 0 and y > 0:
        return 1
    if x < 0 and y < 0:
        return -1
    # Squares are unequal because D is a nonsquare positive integer.
    if x*x > D*y*y:
        return (x > 0) - (x < 0)
    return (y > 0) - (y < 0)


def qeval(p, t, D):
    acc = (Q(0), Q(0))
    for coeff in reversed(p):
        acc = qadd(qmul(acc, t, D), (coeff, Q(0)))
    return acc


def divide(p, m):
    """Rational polynomial long division by a monic quadratic."""
    out, q = list(p), [Q(0)] * max(0, len(p)-2)
    for i in range(len(p)-1, 1, -1):
        c = out[i]
        q[i-2] = c
        for j in range(3):
            out[i-2+j] -= c*m[j]
    while q and q[-1] == 0:
        q.pop()
    return tuple(q), tuple(out[:2])


def valuation(p, m):
    if not p:
        return None
    v, rem = 0, p
    while len(rem) >= 3:
        quot, remainder = divide(rem, m)
        if any(remainder):
            break
        rem, v = quot, v+1
    return v


def idata(x, D, n):
    """Rational enclosure of x=a+b sqrt(D), including signed b."""
    scale = 10**n
    floor = isqrt(D*scale*scale)
    low, high = Q(floor, scale), Q(floor+1, scale)
    a,b = x
    return (a+b*low, a+b*high) if b >= 0 else (a+b*high, a+b*low)


def iadd(a,b):
    return a[0]+b[0], a[1]+b[1]


def imul(a,b):
    v = [x*y for x in a for y in b]
    return min(v), max(v)


def atan_bounds(x, n):
    val = sum((-1)**k*x**(2*k+1)/Q(2*k+1) for k in range(n))
    next_term = (-1)**n*x**(2*n+1)/Q(2*n+1)
    return min(val, val+next_term), max(val, val+next_term)


def pi_bounds(n):
    lo5,hi5 = atan_bounds(Q(1,5),n)
    lo239,hi239 = atan_bounds(Q(1,239),n)
    return 16*lo5-4*hi239, 16*hi5-4*lo239


def trig_bounds(phase, D, n, pi):
    """Rigorous sin/cos of 2*pi*phase with rational Taylor/Lipschitz bounds."""
    plo, phi = idata(phase, D, n)
    k = (plo + phi + 1)//2  # floor(mid + 1/2), integer turn reduction
    reduced = (plo-k,phi-k)
    require(reduced[0] > -Q(1,2) and reduced[1] < Q(1,2),
            "PHASE_REDUCTION_PRECISION")
    xlo,xhi = imul((2*pi[0],2*pi[1]), reduced)
    x, eps = (xlo+xhi)/2, (xhi-xlo)/2
    sine = sum((-1)**j*x**(2*j+1)/factorial(2*j+1) for j in range(n+1))
    cosine = sum((-1)**j*x**(2*j)/factorial(2*j) for j in range(n+1))
    es = eps+abs(x)**(2*n+2)/factorial(2*n+2)
    ec = eps+abs(x)**(2*n+1)/factorial(2*n+1)
    return (cosine-ec,cosine+ec), (sine-es,sine+es)


def strict_sign(s, remaining, t, D):
    """Refine mathematically guaranteed nonzero G(t) to rigorous signed enclosure."""
    for n in PRECISIONS:
        pi = pi_bounds(n)
        total = (Q(0),Q(0))
        good = True
        for h,(p,q) in remaining.items():
            if not p and not q:
                continue
            if h == 0:
                total = iadd(total,idata(qeval(p,t,D),D,n))
                continue
            phase = qmul((s["offset"],Q(0)),(Q(1),Q(0)),D)
            phase = qadd(phase,qmul((s["rate"],Q(0)),t,D))
            phase = (h*phase[0],h*phase[1])
            try:
                c,si = trig_bounds(phase,D,n,pi)
            except Refusal:
                good = False
                break
            if p:
                total = iadd(total,imul(idata(qeval(p,t,D),D,n),c))
            if q:
                total = iadd(total,imul(idata(qeval(q,t,D),D,n),si))
        if good and (total[0] > 0 or total[1] < 0):
            return (1 if total[0] > 0 else -1),n,total
    raise Refusal("CERTIFIED_SIGN_BUDGET_EXHAUSTED")


def rounded_witness(enc, n):
    """Compact outward dyadic-decimal witness, retaining the strict sign."""
    power = 4*n + 8
    while power <= 512:
        scale = 10**power
        lo, hi = enc[0]*scale, enc[1]*scale
        lower = lo.numerator//lo.denominator
        upper = -((-hi.numerator)//hi.denominator)
        if lower > 0 or upper < 0:
            return {"lower_integer":str(lower), "upper_integer":str(upper),
                    "denominator_power10": power}
        power *= 2
    raise Refusal("COMPACT_INTERVAL_BUDGET_EXHAUSTED")


def analyze(s, u, v, D):
    s = canonical(s)
    u,v = rational(u),rational(v)
    require(type(D) is int and 2 <= D <= 1024 and isqrt(D)**2 != D,
            "INVALID_QUADRATIC_RADICAND")
    require(v != 0, "RATIONAL_TIME_NOT_ADMITTED")
    t = (u,v)
    require(qsign(qadd(t,(-s["left"],Q(0))),D)>0 and
            qsign(qadd((s["right"],Q(0)),(-u,-v)),D)>0,
            "TIME_OUTSIDE_PHYSICAL_WINDOW")
    m = (u*u-D*v*v,-2*u,Q(1))
    vals = [valuation(p,m) for a,b in s["terms"].values() for p in (a,b) if p]
    binding = digest({"source":source_blob(s),"time":[str(u),str(v),D]})
    common = {"schema":SCHEMA,"source_time_sha256":binding,
              "quadratic_time": [str(u),str(v),D],
              "signed_affine_turn_phase": [str(s["offset"]),str(s["rate"])],
              "physical_b_spline_custody": "UNVERIFIED",
              "global_event_partition":False,"mc_b_established":False,
              "production_authorized":False}
    if not vals:
        return dict(common,status="IDENTITY_ZERO_ANALYTIC_SPAN",order=None,
                    right_sign=None,left_sign=None,event_kind="CONTINUUM",
                    sign_precision=None,leading_G_enclosure=None)
    r = min(vals)
    stripped = {}
    for h,(p,q) in s["terms"].items():
        pq=[]
        for ch in (p,q):
            cur = ch
            for _ in range(r):
                if cur:
                    cur, remainder = divide(cur,m)
                    require(not any(remainder),"NONEXACT_COMMON_FACTOR")
            pq.append(cur)
        stripped[h] = tuple(pq)
    gsign,precision,enc = strict_sign(s,stripped,t,D)
    right = gsign * ((1 if v > 0 else -1)**r)
    return dict(common,status="EXACT_POINT_ZERO" if r else "EXACT_POINT_NONZERO",
                order=r,right_sign=right,left_sign=right*(-1)**r,
                event_kind="NONZERO" if r==0 else "CROSSING" if r%2 else "TANGENCY",
                sign_precision=precision,leading_G_enclosure=rounded_witness(enc,precision))


def _primitive_tree(x, budget):
    require(budget[0] > 0,"RECEIPT_NODE_BUDGET")
    budget[0]-=1
    require(type(x) in (dict,list,str,int,bool,type(None)),"RECEIPT_NONPRIMITIVE")
    if type(x) is str:
        require(len(x) <= 2048,"RECEIPT_STRING_BUDGET")
    if type(x) is int:
        require(x.bit_length() <= 256,"RECEIPT_INT_BUDGET")
    if type(x) is dict:
        require(len(x)<=32,"RECEIPT_SHAPE")
        for k,v in x.items():
            require(type(k) is str,"RECEIPT_KEY_TYPE")
            _primitive_tree(v,budget)
    if type(x) is list:
        require(len(x)<=32,"RECEIPT_LENGTH")
        for v in x:
            _primitive_tree(v,budget)


def _strict_eq(a,b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return set(a)==set(b) and all(_strict_eq(a[k],b[k]) for k in a)
    if type(a) is list:
        return len(a)==len(b) and all(_strict_eq(x,y) for x,y in zip(a,b))
    return a==b


def verify(s,u,v,D,claimed):
    _primitive_tree(claimed,[128])
    require(_strict_eq(claimed,analyze(s,u,v,D)),"FORGED_OR_STALE_GERM")
    return True
