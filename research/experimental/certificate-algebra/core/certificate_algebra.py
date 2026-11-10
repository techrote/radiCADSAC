"""B1-C1/C2: rational Bernstein sign certificates and incremental source reuse.

Research-only, no accepted MC-038, physics, topology, or STEP guarantees.
Run: python3 -m unittest -v test_certificate_algebra.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
import json
import re

MAX_DEGREE = 24
MAX_BITS = 1024
_CANON = re.compile(r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")


class Refusal(ValueError):
    """Unverified or unadmitted statement; never mathematical truth."""


def frac(s: str) -> Q:
    if not isinstance(s, str) or len(s) > 640 or not _CANON.fullmatch(s):
        raise Refusal("noncanonical or oversized rational")
    q = Q(s)
    if enc(q) != s:
        raise Refusal("noncanonical rational representation")
    if q.numerator.bit_length() > MAX_BITS or q.denominator.bit_length() > MAX_BITS:
        raise Refusal("rational resource budget")
    return q


def enc(x: Q) -> str:
    return str(x)


def digest(obj: object) -> str:
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


@dataclass(frozen=True)
class Piece:
    left: Q
    right: Q
    coeff: tuple[Q, ...]  # power basis in u=(t-left)/(right-left)

    def __post_init__(self) -> None:
        if not isinstance(self.left, Q) or not isinstance(self.right, Q) or not self.left < self.right:
            raise Refusal("invalid exact interval")
        if not isinstance(self.coeff, tuple) or not (1 <= len(self.coeff) <= MAX_DEGREE + 1):
            raise Refusal("invalid polynomial degree")
        for q in (self.left, self.right, *self.coeff):
            if not isinstance(q, Q) or q.numerator.bit_length() > MAX_BITS or q.denominator.bit_length() > MAX_BITS:
                raise Refusal("non-rational or oversized input")
        if len(self.coeff) > 1 and self.coeff[-1] == 0:
            raise Refusal("noncanonical trailing-zero coefficient")

    def source(self) -> dict:
        return {"left": enc(self.left), "right": enc(self.right), "coeff": [enc(x) for x in self.coeff]}

    @property
    def hash(self) -> str:
        return digest({"schema": "b1-piece-v1", **self.source()})

    def endpoint(self, right: bool) -> Q:
        return sum(self.coeff) if right else self.coeff[0]

    def at(self, t: Q) -> Q:
        u = (t - self.left) / (self.right - self.left)
        return sum(c * u**k for k, c in enumerate(self.coeff))


def piece(data: dict) -> Piece:
    from receipt_integrity import validate
    validate(data)
    if type(data) is not dict or set(data) != {"left", "right", "coeff"}:
        raise Refusal("source fields mismatch")
    if not isinstance(data["coeff"], list):
        raise Refusal("coefficients must be a list")
    return Piece(frac(data["left"]), frac(data["right"]), tuple(frac(c) for c in data["coeff"]))


def bernstein(p: Piece) -> tuple[Q, ...]:
    """Exact conversion from power-basis coefficients to Bernstein coefficients."""
    n = len(p.coeff) - 1
    return tuple(sum(p.coeff[k] * Q(comb(i, k), comb(n, k)) for k in range(i+1)) for i in range(n+1))


def kind(b: tuple[Q, ...]) -> str:
    if all(x == 0 for x in b):
        return "ZERO"
    if all(x >= 0 for x in b):
        return "POS"
    if all(x <= 0 for x in b):
        return "NEG"
    raise Refusal("UNKNOWN: Bernstein coefficients do not prove a zero-free interior")


@dataclass(frozen=True)
class Certificate:
    source_hash: str
    sign: str
    b: tuple[Q, ...]

    def record(self) -> dict:
        return {"source_hash": self.source_hash, "sign": self.sign, "bernstein": [enc(x) for x in self.b]}


def receipt(data: dict) -> Certificate:
    from receipt_integrity import validate
    validate(data)
    if type(data) is not dict or set(data) != {"source_hash", "sign", "bernstein"}:
        raise Refusal("receipt fields mismatch")
    if not isinstance(data["source_hash"], str) or not re.fullmatch(r"[0-9a-f]{64}", data["source_hash"]):
        raise Refusal("invalid source digest")
    if data["sign"] not in ("ZERO", "POS", "NEG") or not isinstance(data["bernstein"], list) or len(data["bernstein"]) > MAX_DEGREE+1:
        raise Refusal("invalid receipt kind or coefficients")
    return Certificate(data["source_hash"], data["sign"], tuple(frac(x) for x in data["bernstein"]))


class EvidenceMeter:
    def __init__(self) -> None:
        self.full_leaf_checks = 0
        self.transform_checks = 0
        self.seam_checks = 0


def prove(p: Piece, meter: EvidenceMeter) -> Certificate:
    meter.full_leaf_checks += 1
    b = bernstein(p)
    return Certificate(p.hash, kind(b), b)


def check_leaf(p: Piece, c: Certificate, meter: EvidenceMeter) -> None:
    meter.full_leaf_checks += 1
    # Certificate is an ordinary Python dataclass, not an opaque signed token.
    # Refuse hostile subclass fields even on a direct (non-JSON) call site.
    if (type(c) is not Certificate or type(c.source_hash) is not str
            or type(c.sign) is not str or type(c.b) is not tuple
            or any(type(x) is not Q for x in c.b)):
        raise Refusal("noncanonical in-process leaf certificate")
    if p.hash != c.source_hash or bernstein(p) != c.b or kind(c.b) != c.sign:
        raise Refusal("forged leaf certificate / source substitution")


def check_seam(left: Piece, right: Piece, meter: EvidenceMeter) -> None:
    meter.seam_checks += 1
    if left.right != right.left or left.endpoint(True) != right.endpoint(False):
        raise Refusal("noncontiguous or discontinuous seam")


# In-process transition closures are entitled to reuse earlier proof work
# ONLY for objects minted by a checked importer or a trusted closure. A public
# dataclass constructor is not a proof: raw callers could otherwise assert any
# Bernstein coefficients and make split/affine emit false zero-set claims.
_VERIFIED_MINT = object()


@dataclass(frozen=True)
class Verified:
    pieces: tuple[Piece, ...]
    certs: tuple[Certificate, ...]
    generation: int
    hash: str
    _mint: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._mint is not _VERIFIED_MINT:
            raise Refusal("Verified requires checked source import or trusted closure")


def snapshot_hash(pieces: tuple[Piece, ...], generation: int) -> str:
    return digest({"schema": "b1-snapshot-v1", "generation": generation, "ordered": [p.hash for p in pieces]})


def _state(ps: tuple[Piece, ...], cs: tuple[Certificate, ...], gen: int) -> Verified:
    if not ps or len(ps) != len(cs) or gen < 0:
        raise Refusal("invalid snapshot")
    for p, c in zip(ps, cs):
        if p.hash != c.source_hash or len(p.coeff) != len(c.b) or c.sign not in ("ZERO", "POS", "NEG"):
            raise Refusal("certificate attachment mismatch")
    return Verified(ps, cs, gen, snapshot_hash(ps, gen), _VERIFIED_MINT)


def verify_base(raw_pieces: list[dict], raw_receipts: list[dict], meter: EvidenceMeter) -> Verified:
    from receipt_integrity import validate
    # Inspect the complete input before performing comparisons or iteration.
    validate(raw_pieces)
    validate(raw_receipts)
    if type(raw_pieces) is not list or type(raw_receipts) is not list:
        raise Refusal("base source/receipt arrays must be primitive lists")
    if len(raw_pieces) != len(raw_receipts) or not (1 <= len(raw_pieces) <= 512):
        raise Refusal("invalid base cardinality")
    ps, cs = tuple(piece(x) for x in raw_pieces), tuple(receipt(x) for x in raw_receipts)
    for p, c in zip(ps, cs):
        check_leaf(p, c, meter)
    for a, b in zip(ps, ps[1:]):
        check_seam(a, b, meter)
    return _state(ps, cs, 0)


def _restrict(p: Piece, lo: Q, hi: Q) -> Piece:
    if not (p.left <= lo < hi <= p.right):
        raise Refusal("restriction not inside source")
    x = (lo - p.left) / (p.right - p.left)
    h = (hi - lo) / (p.right - p.left)
    a = tuple(h**j * sum(p.coeff[k] * comb(k, j) * x**(k-j) for k in range(j, len(p.coeff))) for j in range(len(p.coeff)))
    while len(a) > 1 and a[-1] == 0:
        a = a[:-1]
    return Piece(lo, hi, a)


def _casteljau(b: tuple[Q, ...], u: Q) -> tuple[tuple[Q, ...], tuple[Q, ...]]:
    levels = [b]
    while len(levels[-1]) > 1:
        prev = levels[-1]
        levels.append(tuple((1-u)*prev[j] + u*prev[j+1] for j in range(len(prev)-1)))
    n = len(b)-1
    return tuple(levels[j][0] for j in range(n+1)), tuple(levels[n-j][j] for j in range(n+1))


def split(s: Verified, i: int, cut: Q, meter: EvidenceMeter) -> Verified:
    if not isinstance(i, int) or not (0 <= i < len(s.pieces)) or not isinstance(cut, Q):
        raise Refusal("invalid split index/cut")
    p, c = s.pieces[i], s.certs[i]
    if not p.left < cut < p.right:
        raise Refusal("split must be strictly interior")
    q = (cut-p.left)/(p.right-p.left)
    l, r = _restrict(p, p.left, cut), _restrict(p, cut, p.right)
    bl, br = _casteljau(c.b, q)
    # The split must preserve the mathematical degree in this version.
    # Degenerate restrictions may remove highest terms; rebuild the proof then.
    if len(l.coeff) != len(bl) or len(r.coeff) != len(br):
        raise Refusal("non-degree-preserving restriction requires leaf re-verification")
    if kind(bl) != c.sign or kind(br) != c.sign:
        raise Refusal("invalid inherited sign cone")
    lc, rc = Certificate(l.hash, c.sign, bl), Certificate(r.hash, c.sign, br)
    meter.transform_checks += 1
    check_seam(l, r, meter)
    return _state(s.pieces[:i]+(l,r)+s.pieces[i+1:],s.certs[:i]+(lc,rc)+s.certs[i+1:],s.generation)


def affine(s: Verified, offset: Q, rate: Q, meter: EvidenceMeter) -> Verified:
    """Reparameterize f(t) as g(x)=f(offset+rate*x), rate!=0."""
    if not isinstance(offset, Q) or not isinstance(rate, Q) or rate == 0:
        raise Refusal("affine rate must be nonzero exact rational")
    ps, cs = [], []
    for p, c in zip(s.pieces, s.certs):
        left, right = (p.left-offset)/rate, (p.right-offset)/rate
        if rate < 0:
            left, right = right, left
            a = tuple(sum(p.coeff[k]*comb(k,j)*(-1)**j for k in range(j,len(p.coeff))) for j in range(len(p.coeff)))
            b = tuple(reversed(c.b))
        else:
            a, b = p.coeff, c.b
        pp = Piece(left, right, a)
        cc = Certificate(pp.hash, c.sign, b)
        if kind(b) != c.sign:
            raise Refusal("invalid transformed sign")
        ps.append(pp)
        cs.append(cc)
        meter.transform_checks += 1
    if rate < 0:
        ps.reverse()
        cs.reverse()
    for p, q in zip(ps, ps[1:]):
        check_seam(p, q, meter)
    return _state(tuple(ps), tuple(cs), s.generation)


def replace(s: Verified, i: int, new_coeff: tuple[Q, ...], meter: EvidenceMeter) -> Verified:
    """Single-owned local mutation; no claim about distant physical influence."""
    if not isinstance(i, int) or not (0 <= i < len(s.pieces)):
        raise Refusal("invalid update index")
    old = s.pieces[i]
    p = Piece(old.left, old.right, new_coeff)
    c = prove(p, meter)
    if i:
        check_seam(s.pieces[i-1], p, meter)
    if i+1 < len(s.pieces):
        check_seam(p, s.pieces[i+1], meter)
    return _state(s.pieces[:i]+(p,)+s.pieces[i+1:], s.certs[:i]+(c,)+s.certs[i+1:],s.generation+1)


def concatenate(a: Verified, b: Verified, meter: EvidenceMeter) -> Verified:
    check_seam(a.pieces[-1], b.pieces[0], meter)
    meter.transform_checks += 1
    return _state(a.pieces+b.pieces,a.certs+b.certs,max(a.generation,b.generation)+1)


def events(s: Verified) -> dict:
    """Exact entire zero set: identity-zero closed pieces and isolated zero-valued knots."""
    zero_intervals = []
    for p,c in zip(s.pieces,s.certs):
        if c.sign == "ZERO":
            if zero_intervals and zero_intervals[-1][1] == enc(p.left):
                zero_intervals[-1][1] = enc(p.right)
            else:
                zero_intervals.append([enc(p.left),enc(p.right)])
    points = []
    for j in range(len(s.pieces)+1):
        p = s.pieces[j-1] if j else s.pieces[0]
        t = p.right if j else p.left
        if p.at(t) != 0:
            continue
        left = s.certs[j-1].sign if j else None
        right = s.certs[j].sign if j<len(s.certs) else None
        if left=="ZERO" or right=="ZERO":
            continue  # already included in a closed zero interval
        mode = "BOUNDARY" if left is None or right is None else ("CROSS" if left!=right else "TOUCH")
        points.append({"time":enc(t),"kind":mode,"left":left,"right":right})
    return {"identity_intervals":zero_intervals,"isolated_points":points}


def replay(log: dict, meter: EvidenceMeter | None = None) -> tuple[Verified, EvidenceMeter]:
    """Untrusted JSON journal: independently verify all base claims and every transition.

    Initial certificates are supplied, not trusted. Transformation closure follows
    already verified parents; new mutations each receive a new exact leaf check.
    """
    from receipt_integrity import validate
    validate(log)
    meter = meter if meter is not None else EvidenceMeter()
    if type(log) is not dict or set(log)!={"schema","base","steps"} or log["schema"]!="b1-journal-v1":
        raise Refusal("journal schema mismatch")
    base = log["base"]
    if not isinstance(base,dict) or set(base)!={"pieces","receipts","hash"}:
        raise Refusal("base fields mismatch")
    s = verify_base(base["pieces"],base["receipts"],meter)
    if s.hash != base["hash"]:
        raise Refusal("base snapshot hash mismatch")
    if not isinstance(log["steps"],list) or len(log["steps"])>1024:
        raise Refusal("invalid journal length")
    for op in log["steps"]:
        if not isinstance(op,dict) or op.get("before") != s.hash or "after" not in op:
            raise Refusal("stale epoch, substitution, or incomplete operation")
        tag = op.get("op")
        if tag=="split" and set(op)=={"before","after","op","index","cut"}:
            s = split(s,op["index"],frac(op["cut"]),meter)
        elif tag=="affine" and set(op)=={"before","after","op","offset","rate"}:
            s = affine(s,frac(op["offset"]),frac(op["rate"]),meter)
        elif tag=="replace" and set(op)=={"before","after","op","index","coeff"}:
            if not isinstance(op["coeff"],list):
                raise Refusal("invalid replacement coefficients")
            s = replace(s,op["index"],tuple(frac(x) for x in op["coeff"]),meter)
        else:
            raise Refusal("unknown operation or extra fields")
        if s.hash != op["after"]:
            raise Refusal("transformed snapshot hash mismatch")
    return s,meter


def base_record(ps: tuple[Piece,...]) -> dict:
    m = EvidenceMeter()
    cs = tuple(prove(p,m) for p in ps)
    s = verify_base([p.source() for p in ps],[c.record() for c in cs],EvidenceMeter())
    return {"pieces":[p.source() for p in ps],"receipts":[c.record() for c in cs],"hash":s.hash}
