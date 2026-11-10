"""A1-F6 research-only H0/H1/H2 constant-amplitude projective root atlas.

All positive claims are exact rational polynomial/Sturm statements.  Source-time
phase uses pi turns, never radians or the sibling 2*pi convention.  Physical
B-spline provenance is intentionally UNVERIFIED.  See PROJECTIVE-H2-ATLAS.md.
"""
from __future__ import annotations
from receipt_integrity import strict_equal

from fractions import Fraction as Q
from hashlib import sha256
from math import floor
import json

KEYS = ('a', 'b', 'phase_lo', 'phase_hi', 'H0', 'C1', 'S1', 'C2', 'S2')
MAX_BITS = 128
MAX_PHASE = 4096
MAX_WIDTH = 32
MAX_NODES = 8192


class Refusal(ValueError):
    """Unsupported input or proof budget: never a root-absence verdict."""


def require(test, why):
    if not test:
        raise Refusal(why)


def fmt(q):
    return f'{q.numerator}/{q.denominator}'


def token(value):
    require(type(value) is str and '/' in value, 'NONCANONICAL_RATIONAL')
    a, b, *extra = value.split('/')
    require(not extra and a.lstrip('-').isdigit() and b.isdigit(), 'RATIONAL_FORMAT')
    require(len(a) <= 45 and len(b) <= 45, 'RATIONAL_SIZE')
    try:
        q = Q(int(a), int(b))
    except ZeroDivisionError as e:
        raise Refusal('RATIONAL_DENOMINATOR') from e
    require(fmt(q) == value, 'NONCANONICAL_RATIONAL')
    require(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= MAX_BITS, 'RATIONAL_BITS')
    return q


def trim(p):
    p = list(p)
    while p and not p[-1]:
        p.pop()
    return tuple(p)


def val(p, x):
    v = Q(0)
    for c in reversed(p):
        v = v * x + c
    return v


def derivative(p):
    return trim(tuple(j * p[j] for j in range(1, len(p))))


def divide(p, q):
    p, q = trim(p), trim(q)
    require(bool(q), 'ZERO_DIVISOR')
    rem = list(p)
    quot = [Q(0)] * max(0, len(p) - len(q) + 1)
    while len(rem) >= len(q):
        i = len(rem) - len(q)
        c = rem[-1] / q[-1]
        quot[i] = c
        for j, coeff in enumerate(q):
            rem[i + j] -= c * coeff
        rem = list(trim(rem))
    return trim(quot), trim(rem)


def monic(p):
    p = trim(p)
    return tuple(v / p[-1] for v in p) if p else ()


def gcd(p, q):
    p, q = trim(p), trim(q)
    while q:
        _, remainder = divide(p, q)
        p, q = q, remainder
    return monic(p)


def squarefree(p):
    require(bool(p), 'SQUAREFREE_IDENTITY')
    if len(p) == 1:
        return (Q(1),)
    q, r = divide(p, gcd(p, derivative(p)))
    require(not r, 'SQUAREFREE_DIVISION')
    return monic(q)


def sturm(p):
    p = trim(p)
    require(bool(p), 'STURM_IDENTITY')
    if len(p) == 1:
        return (p,)
    seq = [p, derivative(p)]
    while seq[-1]:
        _, r = divide(seq[-2], seq[-1])
        if not r:
            break
        seq.append(tuple(-v for v in r))
    return tuple(seq)


def variation(seq, x):
    signs = [1 if y > 0 else -1 for p in seq if (y := val(p, x)) != 0]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def count(seq, p, lo, hi):
    require(lo < hi and val(p, lo) != 0 and val(p, hi) != 0, 'STURM_BOUNDARY')
    n = variation(seq, lo) - variation(seq, hi)
    require(n >= 0, 'STURM_NEGATIVE_COUNT')
    return n


def split_avoiding(p, lo, hi):
    # At most deg(p) rational roots exclude choices in this list.
    for k in range(2, len(p) + 4):
        x = lo + (hi - lo) / k
        if val(p, x):
            return x
    raise Refusal('STURM_SPLIT_EXHAUSTED')


def bound(p, *finite_endpoints):
    # Every finite complex root has |x| < 1 + max(|a_i/a_d|).
    require(bool(p), 'ROOT_BOUND_IDENTITY')
    m = max((abs(c / p[-1]) for c in p[:-1]), default=Q(0))
    B = max((Q(2) + m, *(Q(2) + abs(x) for x in finite_endpoints)))
    require(max(abs(B.numerator).bit_length(), B.denominator.bit_length()) <= 640, 'ROOT_BOUND_BUDGET')
    return B


def isolate(p, lo, hi, bits):
    # PRECONDITION: p has no roots at finite lo,hi.  Both may be Cauchy bounds.
    if len(p) <= 1:
        return []
    sf = squarefree(p)
    seq = sturm(sf)
    pending = [(lo, hi, count(seq, sf, lo, hi))]
    output = []
    nodes = 0
    while pending:
        l, r, n = pending.pop()
        nodes += 1
        require(nodes <= MAX_NODES, 'STURM_NODE_BUDGET')
        if n == 0:
            continue
        if n == 1 and r - l <= Q(1, 2**bits):
            output.append((l, r))
            continue
        mid = split_avoiding(sf, l, r)
        nl = count(seq, sf, l, mid)
        nr = count(seq, sf, mid, r)
        require(nl + nr == n, 'STURM_COUNT_CONSERVATION')
        pending.extend(((mid, r, nr), (l, mid, nl)))
    return sorted(output)


def order_at(p, x):
    """If p(x)=0, return (positive multiplicity, nonzero local quotient)."""
    q, k = trim(p), 0
    while len(q) > 1 and val(q, x) == 0:
        q, remainder = divide(q, (-x, Q(1)))
        require(not remainder, 'ENDPOINT_DIVISION')
        k += 1
    require(bool(q) and val(q, x) != 0, 'ENDPOINT_IDENTITY')
    return k, val(q, x)


def order_inside(p, lo, hi):
    # Repeated-root order from successive square-free gcd layers.
    k = 0
    q = p
    while len(q) > 1:
        sf = squarefree(q)
        if count(sturm(sf), sf, lo, hi) == 0:
            break
        k += 1
        q = gcd(q, derivative(q))
    require(k > 0, 'ROOT_ORDER_MISSING')
    return k


def sign(x):
    require(x != 0, 'UNPROVED_STRICT_SIGN')
    return 1 if x > 0 else -1


def projective_numerator(c):
    """F(phase) = N(tan(pi*phase/2))/(1+tan²(pi*phase/2))²."""
    h, c1, s1, c2, s2 = c
    return trim((h + c1 + c2, 2*s1 + 4*s2,
                 2*h - 6*c2, 2*s1 - 4*s2, h - c1 + c2))


def read(doc):
    require(type(doc) is dict and set(doc) == set(KEYS), 'SOURCE_FIELDS')
    a, b, ql, qr = (token(doc[k]) for k in KEYS[:4])
    coeff = tuple(token(doc[k]) for k in KEYS[4:])
    require(b != 0, 'ZERO_PHASE_RATE')
    require(ql < qr and ql.denominator in (1, 2) and qr.denominator in (1, 2), 'PHASE_ENDPOINT_GRAMMAR')
    require(-MAX_PHASE <= ql < qr <= MAX_PHASE and qr-ql <= MAX_WIDTH, 'PHASE_WIDTH_BUDGET')
    digest = sha256(json.dumps(doc,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
    return a, b, ql, qr, coeff, digest


def pole(q):
    return q.denominator == 1 and q.numerator % 2 != 0


def center(ql, qr):
    k = floor((ql + qr + 2) / 4)  # center 2*k in interval (2*k-1,2*k+1)
    require(2*k-1 <= ql < qr <= 2*k+1, 'PROJECTIVE_CHART')
    return k


def coordinate(q, k, side):
    """Projective x endpoint; None denotes an infinite end of chart."""
    d = q - 2*k
    if d == -1:
        require(side == 'left', 'WRONG_LEFT_POLE')
        return None
    if d == 1:
        require(side == 'right', 'WRONG_RIGHT_POLE')
        return None
    values = {Q(-1,2): Q(-1), Q(0): Q(0), Q(1,2): Q(1)}
    require(d in values, 'PHASE_ENDPOINT_NOT_HALF_TURN')
    return values[d]


def phase_boundary_event(q, p, a, b, role):
    """Return exact point event, or None when this point is strictly nonzero."""
    if pole(q):
        deg = len(p) - 1
        m = 4 - deg
        if m == 0:
            return None
        # In increasing phase, x -> +infinity before pole and -infinity after.
        phase_left = sign(p[-1])
        phase_right = phase_left * ((-1) ** deg)
        location = 'PROJECTIVE_POLE'
    else:
        k = floor((q + 1) / 2)
        x = coordinate(q, k, 'left') if q-2*k != 1 else coordinate(q, k, 'right')
        require(x is not None, 'FINITE_ENDPOINT_EXPECTED')
        m, residual = order_at(p, x)
        if m == 0:
            return None
        phase_right = sign(residual)
        phase_left = phase_right * ((-1) ** m)
        location = 'EXACT_HALF_TURN_PHASE'
    physical_left, physical_right = ((phase_left,phase_right) if b > 0 else (phase_right,phase_left))
    require((physical_left != physical_right) == bool(m % 2), 'POINT_EVENT_PARITY')
    return {'locator': location, 'phase': fmt(q), 'physical_time':fmt((q-a)/b),
            'role':role,'order':m,'kind':'CROSS' if m%2 else 'TOUCH',
            'left_sign':physical_left,'right_sign':physical_right}


def chart_atlas(p, ql, qr, bits, a, b):
    k = center(ql,qr)
    xl = coordinate(ql,k,'left')
    xr = coordinate(qr,k,'right')
    interior = p
    for x in (xl,xr):
        if x is not None:
            order, _ = order_at(interior, x)
            for _ in range(order):
                interior, rem = divide(interior,(-x,Q(1)))
                require(not rem, 'FINITE_ENDPOINT_DEFLATION')
    B = bound(interior, *(x for x in (xl,xr) if x is not None))
    lo = xl if xl is not None else -B
    hi = xr if xr is not None else B
    require(lo < hi, 'CHART_COORDINATE_ORDER')
    roots = isolate(interior,lo,hi,bits)
    events=[]
    for left, right in roots:
        order=order_inside(interior,left,right)
        sl,sr=sign(val(p,left)),sign(val(p,right))
        require((sl!=sr)==bool(order%2),'INTERIOR_EVENT_PARITY')
        el,er=(sl,sr) if b>0 else (sr,sl)
        events.append({'locator':'STURM_PROJECTIVE_ROOT', 'chart_center':2*k,
                       'bracket_x':[fmt(left),fmt(right)],'order':order,
                       'kind':'CROSS' if order%2 else 'TOUCH',
                       'left_sign':el,'right_sign':er})
    # Each cell is the exact connected component between algebraic roots.
    # A rational x sample + complete Sturm root count proves its strict sign.
    endpoints=[(lo,lo)]+roots+[(hi,hi)]
    cells=[]
    for i,((_,left),(right,_)) in enumerate(zip(endpoints,endpoints[1:])):
        require(left<right,'EMPTY_SIGN_CELL')
        x=(left+right)/2
        s=sign(val(p,x))
        cells.append({'index':i,'sample_x':fmt(x),'sign':s})
    # Check continuity of germ signs from the signed cells.
    for j,e in enumerate(events):
        sl, sr = cells[j]['sign'], cells[j+1]['sign']
        physical_left,physical_right=(sl,sr) if b>0 else (sr,sl)
        require(physical_left==e['left_sign'] and physical_right==e['right_sign'],'EVENT_CELL_SIGN')
    return {'phase_interval':[fmt(ql),fmt(qr)], 'center':2*k,
            'x_endpoint':[None if xl is None else fmt(xl),None if xr is None else fmt(xr)],
            'events':events,'signed_cells':cells}


def certify(doc, *, bits=20):
    require(type(bits) is int and 2 <= bits <= 72,'ISOLATION_BITS_BUDGET')
    a,b,ql,qr,c,digest=read(doc)
    p = projective_numerator(c)
    base={'schema':'a1-projective-h2/1','source_sha256':digest,
          'phase_units':'pi','physical_source_authentication':'UNVERIFIED',
          'bounds':{'bits':bits},
          'rational_physical_interval':sorted([fmt((ql-a)/b),fmt((qr-a)/b)], key=lambda v:Q(v))}
    if not p:
        base.update({'kind':'IDENTITY_ZERO_CONTINUUM','zero_continua':[[fmt(min((ql-a)/b,(qr-a)/b)),fmt(max((ql-a)/b,(qr-a)/b))]],
                     'numerator':[], 'charts':[], 'events':[]})
        return base
    boundaries = [ql]
    for integer in range(floor(ql)+1, floor(qr)+1):
        if integer%2 and ql < integer < qr:
            boundaries.append(Q(integer))
    boundaries.append(qr)
    charts=[]
    ordered_phase=[]
    left_event=phase_boundary_event(ql,p,a,b,'EXTERIOR_ENDPOINT')
    if left_event:
        ordered_phase.append(left_event)
    for j,(left,right) in enumerate(zip(boundaries,boundaries[1:])):
        chart=chart_atlas(p,left,right,bits,a,b)
        charts.append(chart)
        ordered_phase.extend(chart['events'])
        right_event=phase_boundary_event(right,p,a,b,'EXTERIOR_ENDPOINT' if j==len(boundaries)-2 else 'INTERNAL_POLE')
        if right_event:
            ordered_phase.append(right_event)
    base.update({'kind':'FINITE_PROJECTIVE_H2', 'zero_continua':[],
                 'numerator':list(map(fmt,p)),'charts':charts,
                 'events':ordered_phase if b>0 else list(reversed(ordered_phase))})
    return base


def verify(doc, receipt):
    try:
        return type(receipt) is dict and strict_equal(certify(doc,**receipt['bounds']),receipt)
    except (Refusal,TypeError,ValueError,KeyError,ZeroDivisionError,OverflowError):
        return False
