"""A1: exact algebraic-point zero decisions for rational-turn Fourier sources.

Research-only: NOT a complete trigonometric root isolator or an accepted
machining event certificate. Exact rational arithmetic, Python stdlib only.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from math import gcd, isqrt
import json


class Refusal(ValueError):
    """Unsupported grammar or explicit resource limit; never means no zero."""


def rational(value: int | Q) -> Q:
    if type(value) is int or isinstance(value, Q):
        q = Q(value)
        if max(q.numerator.bit_length(), q.denominator.bit_length()) > 256:
            raise Refusal("rational component exceeds 256 bits")
        return q
    raise Refusal("only exact int/Fraction input is admitted")


def trim(coeffs: tuple[Q, ...] | list[Q]) -> tuple[Q, ...]:
    c = list(coeffs)
    while c and not c[-1]:
        c.pop()
    return tuple(c)


def polynomial(seq) -> tuple[Q, ...]:
    values = tuple(rational(c) for c in seq)
    if len(values) > 17:
        raise Refusal("polynomial degree exceeds 16")
    return trim(values)


@dataclass(frozen=True)
class Source:
    c0: tuple[Q, ...]
    cos: tuple[tuple[Q, ...], ...]
    sin: tuple[tuple[Q, ...], ...]
    phase_offset: Q
    phase_rate: Q

    def __post_init__(self) -> None:
        validate_source(self)

    def channels(self) -> tuple[tuple[Q, ...], ...]:
        return (self.c0,) + self.cos + self.sin


def validate_source(s: Source) -> None:
    """Validate even after construction, so forged frozen Source mutations refuse."""
    if type(s) is not Source:
        raise Refusal("expected an exact Source object")
    if any(type(x) is not tuple for x in (s.c0, s.cos, s.sin)):
        raise Refusal("source channels must be immutable tuples")
    if len(s.cos) != len(s.sin) or len(s.cos) > 2:
        raise Refusal("matched H0/H1/H2 channels required")
    if type(s.phase_offset) is not Q or type(s.phase_rate) is not Q:
        raise Refusal("phase fields must be exact canonical Fraction values")
    rational(s.phase_offset)
    rational(s.phase_rate)
    for p in s.channels():
        if type(p) is not tuple or len(p) > 17:
            raise Refusal("polynomial must be a canonical degree<=16 tuple")
        if any(type(v) is not Q for v in p):
            raise Refusal("polynomial contains noncanonical/nonrational coefficient")
        if p and not p[-1]:
            raise Refusal("polynomial trailing zero is not canonical")
        for v in p:
            rational(v)


def source(c0, cos=(), sin=(), *, phase_offset=0, phase_rate=1) -> Source:
    if len(cos) != len(sin) or len(cos) > 2:
        raise Refusal("matched H0/H1/H2 cosine and sine channels required")
    return Source(polynomial(c0), tuple(polynomial(x) for x in cos),
                  tuple(polynomial(x) for x in sin),
                  rational(phase_offset), rational(phase_rate))


def source_sha(s: Source) -> str:
    validate_source(s)
    obj = {"c0": list(map(str, s.c0)),
           "cos": [[str(y) for y in x] for x in s.cos],
           "sin": [[str(y) for y in x] for x in s.sin],
           "phase_offset": str(s.phase_offset), "phase_rate": str(s.phase_rate)}
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def evaluate(p: tuple[Q, ...], t: Q) -> Q:
    acc = Q(0)
    for c in reversed(p):
        acc = acc * t + c
    return acc


def divmod_poly(p: tuple[Q, ...], q: tuple[Q, ...]):
    p, q = trim(p), trim(q)
    if not q:
        raise Refusal("polynomial division by zero")
    rem = list(p)
    quotient = [Q(0)] * max(0, len(p) - len(q) + 1)
    while rem and len(rem) >= len(q):
        i = len(rem) - len(q)
        v = rem[-1] / q[-1]
        quotient[i] = v
        for j, c in enumerate(q):
            rem[i + j] -= v * c
        rem = list(trim(rem))
    return trim(quotient), trim(rem)


def _proper_divisors(n: int):
    return [d for d in range(1, n) if n % d == 0]


@lru_cache(maxsize=128)
def cyclotomic(n: int) -> tuple[Q, ...]:
    """Phi_n from exact factorisation of x**n-1 (bounded n <= 128)."""
    if type(n) is not int or not 1 <= n <= 128:
        raise Refusal("cyclotomic degree budget (4*denominator <= 128)")
    f = tuple([Q(-1)] + [Q(0)] * (n - 1) + [Q(1)])
    for divisor in _proper_divisors(n):
        factor = cyclotomic(divisor)
        f, rem = divmod_poly(f, factor)
        assert not rem, "invalid cyclotomic factorization"
    return f


def constant_phase_identity(s: Source) -> bool:
    """Decide F(t) identically zero at rational, constant phase.

    For every amplitude degree j, form its exact cyclotomic Fourier
    coefficient; all coefficients must vanish in Q[zeta_{4d}].
    This is an infinite-family result (bounded computational grammar).
    """
    validate_source(s)
    if s.phase_rate:
        raise Refusal("constant-phase identity requires zero phase rate")
    d, p = s.phase_offset.denominator, s.phase_offset.numerator
    n = 4 * d
    if n > 128:
        raise Refusal("constant phase denominator exceeds cyclotomic budget")
    phi = cyclotomic(n)
    channels = s.channels()
    for j in range(max((len(poly) for poly in channels), default=0)):
        coeff = lambda poly: poly[j] if j < len(poly) else Q(0)
        total = [Q(0)] * n
        total[0] += 2 * coeff(s.c0)
        for k, (cc, ss) in enumerate(zip(s.cos, s.sin), 1):
            c, sine = coeff(cc), coeff(ss)
            total[(2 * k * p) % n] += c
            total[(-2 * k * p) % n] += c
            total[(d - 2 * k * p) % n] += sine
            total[(d + 2 * k * p) % n] -= sine
        _, remainder = divmod_poly(trim(total), phi)
        if remainder:
            return False
    return True


def rational_event(s: Source, t: int | Q) -> dict:
    """Decide F(t)==0 exactly for a rational time; sign is NOT claimed.

    For beta=p/d turns, let zeta=exp(2*pi*i/(4*d)), so i=zeta**d.
    The Laurent Fourier sum is converted to an integer-power polynomial
    modulo Phi_(4*d). It vanishes iff its exact remainder is zero.
    """
    validate_source(s)
    t = rational(t)
    beta = s.phase_offset + s.phase_rate * t
    d, p = beta.denominator, beta.numerator
    n = 4 * d
    if n > 128:
        raise Refusal("phase denominator exceeds exact cyclotomic budget")
    total = [Q(0)] * n
    total[0] += 2 * evaluate(s.c0, t)
    for k, (cc, ss) in enumerate(zip(s.cos, s.sin), 1):
        c, sine = evaluate(cc, t), evaluate(ss, t)
        total[(2*k*p) % n] += c
        total[(-2*k*p) % n] += c
        total[(d - 2*k*p) % n] += sine
        total[(d + 2*k*p) % n] -= sine
    numerator = trim(total)
    phi = cyclotomic(n)
    _, rem = divmod_poly(numerator, phi)
    identity = (not any(s.channels()) if s.phase_rate else
                constant_phase_identity(s))
    return {"schema": "a1-rational-event/1", "source_sha256": source_sha(s),
            "time": str(t), "phase_turns": str(beta), "cyclotomic_order": n,
            "numerator_2F": [str(x) for x in numerator],
            "phi": [str(x) for x in phi], "remainder": [str(x) for x in rem],
            "result": ("IDENTICAL_ZERO_PIECE" if identity else
                       "EXACT_ZERO" if not rem else "EXACT_NONZERO"),
            "sign": "UNDETERMINED"}


def verify_rational_event(s: Source, receipt: dict) -> bool:
    if type(receipt) is not dict:
        return False
    try:
        return rational_event(s, Q(receipt["time"])) == receipt
    except (KeyError, ValueError, TypeError, ZeroDivisionError, Refusal):
        return False


def _quadratic(a: int, b: int, c: int) -> tuple[tuple[Q,...], int]:
    if any(type(x) is not int for x in (a, b, c)):
        raise Refusal("quadratic must have integer coefficients")
    if a <= 0 or any(abs(x).bit_length() > 128 for x in (a, b, c)):
        raise Refusal("quadratic leading coefficient/bit budget invalid")
    if gcd(gcd(a, abs(b)), abs(c)) != 1:
        raise Refusal("quadratic must be primitive")
    disc = b*b - 4*a*c
    if disc <= 0 or isqrt(disc)**2 == disc:
        raise Refusal("quadratic must have distinct irrational real roots")
    return (Q(c), Q(b), Q(a)), disc


def quadratic_event(s: Source, a: int, b: int, c: int) -> dict:
    """Both real irrational roots of primitive a*t^2+b*t+c, a>0.

    By Gelfond-Schneider, exp(i*pi*(offset+rate*root)) is transcendental
    when rate != 0. The polynomial Fourier Laurent sum therefore vanishes
    iff every channel vanishes. The common quadratic valuation determines
    the exact zero order (simple quadratic roots).
    """
    validate_source(s)
    if not s.phase_rate:
        raise Refusal("zero phase rate outside the irrational-phase theorem")
    m, disc = _quadratic(a, b, c)
    values = [p for p in s.channels() if p]
    if not values:
        result, order, crossing = "IDENTICAL_ZERO_PIECE", None, None
    else:
        vals = []
        for p in values:
            v = 0
            while len(p) >= len(m):
                quotient, rem = divmod_poly(p, m)
                if rem:
                    break
                p, v = quotient, v + 1
            vals.append(v)
        order = min(vals)
        result = "EXACT_ZERO" if order else "EXACT_NONZERO"
        crossing = bool(order % 2) if order else None
    floor_sqrt = isqrt(disc)
    left = (Q(-b - floor_sqrt - 1, 2*a), Q(-b - floor_sqrt, 2*a))
    right = (Q(-b + floor_sqrt, 2*a), Q(-b + floor_sqrt + 1, 2*a))
    return {"schema": "a1-quadratic-event/1", "source_sha256": source_sha(s),
            "minimal_polynomial": [c,b,a], "discriminant": disc,
            "root_intervals": [[str(v) for v in z] for z in (left, right)],
            "result_at_both_roots": result, "multiplicity_at_both": order,
            "crosses_at_each": crossing, "sign": "UNDETERMINED"}


def verify_quadratic_event(s: Source, receipt: dict) -> bool:
    if type(receipt) is not dict:
        return False
    try:
        c, b, a = receipt["minimal_polynomial"]
        return quadratic_event(s, a, b, c) == receipt
    except (KeyError, ValueError, TypeError, ZeroDivisionError, Refusal):
        return False
