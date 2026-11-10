"""A1-F7: exact zero-capacity (not zero-isolation) research checker.

All arithmetic on source data is rational. The proof uses pi analytically;
no numerical approximation to pi or trigonometric evaluation occurs here.
"""
from fractions import Fraction as Q
from hashlib import sha256
import json
import re

FIELDS = ('H0', 'C1', 'S1', 'C2', 'S2')
LIMIT_BITS = 128
LIMIT_DEGREE = 16
LIMIT_WINDOWS = 256


class Refusal(ValueError):
    pass


def rat(value):
    if type(value) is not str or not re.fullmatch(r'-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?', value):
        raise Refusal('noncanonical rational syntax')
    try:
        q = Q(value)
    except (ValueError, ZeroDivisionError):
        raise Refusal('invalid rational') from None
    if str(q) != value or max(abs(q.numerator).bit_length(), q.denominator.bit_length()) > LIMIT_BITS:
        raise Refusal('noncanonical or over-budget rational')
    return q


def poly(values):
    if type(values) is not list or not 1 <= len(values) <= LIMIT_DEGREE + 1:
        raise Refusal('polynomial degree/shape')
    p = tuple(rat(v) for v in values)
    if len(p) > 1 and p[-1] == 0:
        raise Refusal('untrimmed polynomial')
    return p


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def degree(p):
    return -1 if len(p) == 1 and p[0] == 0 else len(p) - 1


def encode(q):
    return str(q)


def canonical_digest(source):
    raw = json.dumps(source, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    return sha256(raw.encode('ascii')).hexdigest()


def _admit_piece(piece):
    if type(piece) is not dict or set(piece) != {'lo', 'hi', 'a', 'b', *FIELDS}:
        raise Refusal('piece field shape')
    lo, hi, a, b = (rat(piece[k]) for k in ('lo', 'hi', 'a', 'b'))
    if not lo < hi or b == 0:
        raise Refusal('invalid interval or stationary phase')
    ps = {f: poly(piece[f]) for f in FIELDS}
    return lo, hi, a, b, ps


def piece_capacity(piece):
    lo, hi, _, b, ps = _admit_piece(piece)
    m0 = degree(ps['H0']) + 1
    ms = {h: max(degree(ps[f'C{h}']), degree(ps[f'S{h}'])) + 1 for h in (1, 2)}
    n = m0 + 2 * sum(ms.values())
    if n == 0:
        return {'type': 'IDENTITY_ZERO_CONTINUUM', 'interval': [encode(lo), encode(hi)],
                'source_authentication': 'SUPPLIED_ONLY'}
    hmax = max((h for h in (1, 2) if ms[h]), default=0)
    # Every window is strictly shorter than 1/(hmax*abs(b)).
    windows = (int((hi - lo) * hmax * abs(b)) + 1) if hmax else 1
    if windows > LIMIT_WINDOWS or n > 128:
        raise Refusal('finite partition resource cap')
    # Explicit exact rational endpoints: no arbitrary epsilon or pi approximation.
    cuts = [encode(lo + (hi - lo) * i / windows) for i in range(windows + 1)]
    return {'type': 'FINITE_MULTIPLICITY_UPPER_BOUND', 'interval': [encode(lo), encode(hi)],
            'dimension': n, 'max_harmonic': hmax, 'windows': windows,
            'cuts': cuts, 'max_zeros_counted_with_multiplicity': windows * (n - 1),
            'source_authentication': 'SUPPLIED_ONLY'}


def _bernstein_piece(controls, l, r):
    # Quadratic clamped Bezier: P0(1-u)^2+2P1*u*(1-u)+P2*u^2.
    p0, p1, p2 = controls
    u0, u1 = -l / (r - l), Q(1) / (r - l)
    c0 = p0 + (-2*p0 + 2*p1)*u0 + (p0 - 2*p1 + p2)*u0*u0
    c1 = (-2*p0 + 2*p1)*u1 + 2*(p0 - 2*p1 + p2)*u0*u1
    c2 = (p0 - 2*p1 + p2)*u1*u1
    return [encode(v) for v in trim([c0, c1, c2])]


def spline_pieces(source):
    if type(source) is not dict or set(source) != {'schema', 'L', 'K', 'R', 'a', 'b', 'controls'}:
        raise Refusal('spline source shape')
    if type(source['schema']) is not str or source['schema'] != 'a1-c0-quadratic-bspline/1':
        raise Refusal('spline source version')
    l, k, r, a, b = (rat(source[f]) for f in ('L', 'K', 'R', 'a', 'b'))
    if not l < k < r or b == 0 or type(source['controls']) is not dict or set(source['controls']) != set(FIELDS):
        raise Refusal('spline knots, phase or controls')
    cs = {}
    for f in FIELDS:
        values = source['controls'][f]
        if type(values) is not list or len(values) != 5:
            raise Refusal('C0 quadratic requires five controls')
        cs[f] = tuple(rat(v) for v in values)
    pieces = []
    for u, v, start in ((l, k, 0), (k, r, 2)):
        piece = {'lo': encode(u), 'hi': encode(v), 'a': encode(a), 'b': encode(b)}
        for f in FIELDS:
            piece[f] = _bernstein_piece(cs[f][start:start+3], u, v)
        pieces.append(piece)
    # Endpoints at K coincide coefficientwise by the shared control no. 2.
    return pieces


def certify(source):
    pieces = spline_pieces(source)
    parts = [piece_capacity(p) for p in pieces]
    continua = []
    for part in parts:
        if part['type'] != 'IDENTITY_ZERO_CONTINUUM':
            continue
        if continua and continua[-1][1] == part['interval'][0]:
            continua[-1][1] = part['interval'][1]
        else:
            continua.append(part['interval'][:])
    return {'schema': 'a1-zero-capacity/1', 'source_sha256': canonical_digest(source),
            'source_type': 'CONSTRUCTED_C0_QUADRATIC_BSPLINE',
            'actual_source_ancestry': 'UNVERIFIED', 'knot': source['K'],
            'knot_topology': 'SIDED_GERMS_REQUIRED', 'pieces': parts,
            'maximal_identity_zero_continua': continua,
            'claim': 'UPPER_BOUND_ONLY_NOT_COMPLETE_EVENT_PARTITION'}


def _plain(a, nodes=None, depth=0):
    # Reject hostile __eq__ objects and bool/int coercions, prior A1/A2/B1 lessons.
    if nodes is None:
        nodes = [0]
    nodes[0] += 1
    if nodes[0] > 3000 or depth > 24:
        return False
    if type(a) in (str, int, bool) or a is None:
        return type(a) is not str or len(a) <= 4096
    if type(a) is list:
        return len(a) <= 1024 and all(_plain(x, nodes, depth+1) for x in a)
    if type(a) is dict:
        return len(a) <= 128 and all(type(k) is str and len(k) <= 128 and _plain(v, nodes, depth+1) for k,v in a.items())
    return False


def verify(source, claimed):
    if not _plain(source) or not _plain(claimed):
        return False
    try:
        return certify(source) == claimed
    except (Refusal, ValueError, TypeError, OverflowError):
        return False
