#!/usr/bin/env python3
"""Bounded, exact, variable-rank *real multiquadratic* embedding experiment.

Every positive squarefree generator must have an independent square class.
This is not an arbitrary algebraic number field constructor, trigonometric
zero decider, physical-root algorithm, or MC-B/MC-1 admission.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as Q
from math import isqrt
from typing import Sequence

SCHEMA = "radicadsac-pb00701-multiquadratic-embedding/1.0"
BITS = (8, 16, 32, 64, 128, 256, 512)
MAX_GENERATORS = 3
MAX_RADICAND = 10000
MAX_COEFF_BITS = 1024
MAX_WORK_BITS = 8192
MAX_CERT_BYTES = 65536

class Refusal(ValueError):
    pass
class ResourceRefusal(RuntimeError):
    pass

def require(ok, why):
    if not ok:
        raise Refusal(why)

def bound(x: Q, limit=MAX_WORK_BITS):
    if max(x.numerator.bit_length(), x.denominator.bit_length()) > limit:
        raise ResourceRefusal("RATIONAL_ARITHMETIC_BIT_BUDGET")
    return x

def prime_factor_parity(n: int) -> frozenset[int]:
    """Trial division is bounded by MAX_RADICAND, not general factorisation."""
    require(type(n) is int and 1 < n <= MAX_RADICAND, "RADICAND_OUTSIDE_BOUNDED_GRAMMAR")
    original = n
    factors = set()
    d = 2
    while d*d <= n:
        if n % d == 0:
            power = 0
            while n % d == 0:
                n //= d
                power += 1
            if power > 1:
                raise Refusal("NON_SQUAREFREE_GENERATOR")
            factors.add(d)
        d += 1 if d == 2 else 2
    if n > 1:
        factors.add(n)
    require(factors and original > 1, "TRIVIAL_GENERATOR")
    return frozenset(factors)

@dataclass(frozen=True)
class Field:
    generators: tuple[int, ...]

    def __post_init__(self):
        require(type(self.generators) is tuple and 1 <= len(self.generators) <= MAX_GENERATORS,
                "FIELD_RANK_BUDGET")
        parities = [prime_factor_parity(d) for d in self.generators]
        # Independence over F_2 of square classes. Equivalent to every
        # nonempty subset product being a nonsquare rational integer.
        for mask in range(1, 1 << len(parities)):
            parity = set()
            for i, fs in enumerate(parities):
                if mask & (1 << i):
                    parity.symmetric_difference_update(fs)
            require(bool(parity), "DEPENDENT_SQUARE_CLASSES")

    @property
    def degree(self):
        return 1 << len(self.generators)

    def radicand(self, mask: int) -> int:
        require(type(mask) is int and 0 <= mask < self.degree, "INVALID_BASIS_INDEX")
        value = 1
        for i, r in enumerate(self.generators):
            if mask & (1 << i):
                value *= r
        return value

    def element(self, values: Sequence[Q]):
        require(type(values) in (list, tuple) and len(values) == self.degree,
                "WRONG_FIELD_DIMENSION")
        require(all(type(x) is Q for x in values), "INEXACT_COEFFICIENT")
        for x in values:
            bound(x, MAX_COEFF_BITS)
        return Element(self, tuple(values))

    def scalar(self, x: Q | int):
        require(type(x) in (Q, int), "INEXACT_SCALAR")
        return self.element((Q(x),) + (Q(0),) * (self.degree - 1))

    def basis(self, mask: int):
        require(type(mask) is int and 0 <= mask < self.degree, "INVALID_BASIS_INDEX")
        return self.element(tuple(Q(int(i == mask)) for i in range(self.degree)))

@dataclass(frozen=True)
class Element:
    field: Field
    coeffs: tuple[Q, ...]

    def __post_init__(self):
        require(type(self.field) is Field and type(self.coeffs) is tuple
                and len(self.coeffs) == self.field.degree
                and all(type(c) is Q for c in self.coeffs), "INVALID_FIELD_ELEMENT")
        for c in self.coeffs:
            bound(c)

    def _other(self, other):
        if type(other) in (Q, int):
            return self.field.scalar(other)
        require(type(other) is Element and other.field == self.field, "FIELD_IDENTITY_MISMATCH")
        return other

    def __add__(self, other):
        o = self._other(other)
        return Element(self.field, tuple(bound(a + b) for a, b in zip(self.coeffs, o.coeffs)))
    __radd__ = __add__
    def __neg__(self):
        return Element(self.field, tuple(-c for c in self.coeffs))
    def __sub__(self, other):
        return self + (-self._other(other))
    def __rsub__(self, other):
        return self._other(other) - self

    def __mul__(self, other):
        o = self._other(other)
        out = [Q(0)] * self.field.degree
        for i, ai in enumerate(self.coeffs):
            if ai == 0:
                continue
            for j, bj in enumerate(o.coeffs):
                if bj:
                    out[i ^ j] = bound(out[i ^ j] + ai * bj * self.field.radicand(i & j))
        return Element(self.field, tuple(out))
    __rmul__ = __mul__

    def inverse(self):
        require(any(self.coeffs), "ZERO_INVERSE")
        n = self.field.degree
        columns = [(self * self.field.basis(j)).coeffs for j in range(n)]
        rows = [[columns[j][i] for j in range(n)] + [Q(int(i == 0))]
                for i in range(n)]
        for col in range(n):
            pivot = next((i for i in range(col, n) if rows[i][col]), None)
            require(pivot is not None, "NONFIELD_MULTIPLICATION_MATRIX")
            rows[col], rows[pivot] = rows[pivot], rows[col]
            divisor = rows[col][col]
            rows[col] = [bound(v / divisor) for v in rows[col]]
            for i in range(n):
                if i != col:
                    multiple = rows[i][col]
                    if multiple:
                        rows[i] = [bound(a - multiple*b) for a, b in zip(rows[i], rows[col])]
        result = Element(self.field, tuple(row[-1] for row in rows))
        require(self * result == self.field.scalar(1), "INVERSE_ROUNDTRIP_MISMATCH")
        return result

    def sign_certificate(self, refinements=BITS):
        """Finite, exact dyadic interval proof at the all-positive embedding.

        F_2 independence means a nonzero coefficient tuple is not zero as an
        algebraic number; interval refinement therefore *eventually* decides
        its sign, but finite computational budgets can refuse.
        """
        if not any(self.coeffs):
            return {"status": "EXACT_ZERO", "sign": 0, "bits": 0,
                    "lower": "0", "upper": "0"}
        for bits in refinements:
            if type(bits) is not int or bits < 1 or bits > 1024:
                raise ResourceRefusal("REFINEMENT_BUDGET_INVALID")
            scale = 1 << bits
            lo = hi = self.coeffs[0]
            for mask in range(1, self.field.degree):
                coeff = self.coeffs[mask]
                if coeff == 0:
                    continue
                f = isqrt(self.field.radicand(mask) * scale * scale)
                low = Q(f, scale)
                high = Q(f + 1, scale)
                if coeff > 0:
                    lo = bound(lo + coeff * low)
                    hi = bound(hi + coeff * high)
                else:
                    lo = bound(lo + coeff * high)
                    hi = bound(hi + coeff * low)
            if lo > 0 or hi < 0:
                return {"status": "STRICT_SIGN", "sign": 1 if lo > 0 else -1,
                        "bits": bits, "lower": str(lo), "upper": str(hi)}
        raise ResourceRefusal("STRICT_EMBEDDING_SIGN_UNRESOLVED")

    def record(self):
        return {"generators": list(self.field.generators),
                "coefficients": [str(x) for x in self.coeffs]}


def parse_record(raw):
    require(type(raw) is dict and set(raw) == {"generators", "coefficients"},
            "INVALID_RECORD_SHAPE")
    require(type(raw["generators"]) is list and type(raw["coefficients"]) is list,
            "INVALID_RECORD_TYPES")
    f = Field(tuple(raw["generators"]))
    require(len(raw["coefficients"]) == f.degree
            and all(type(s) is str and len(s) <= 512 for s in raw["coefficients"]),
            "INVALID_COEFFICIENT_RECORD")
    try:
        el = f.element([Q(s) for s in raw["coefficients"]])
    except (ValueError, ZeroDivisionError) as e:
        raise Refusal("UNPARSEABLE_COEFFICIENT") from e
    require(el.record() == raw, "NONCANONICAL_COEFFICIENT_RECORD")
    return el


def verify_sign_certificate(record, submitted):
    """Replay pinned field and strict interval witness, not client assertion."""
    import json
    try:
        require(type(submitted) is dict, "INVALID_CERTIFICATE")
        size = len(json.dumps(submitted, sort_keys=True, separators=(",", ":")))
        if size > MAX_CERT_BYTES:
            raise ResourceRefusal("CERTIFICATE_SIZE_BUDGET")
        e = parse_record(record)
        require(set(submitted) == {"status", "sign", "bits", "lower", "upper"},
                "CERTIFICATE_SHAPE")
        bits = submitted["bits"]
        require(type(bits) is int and bits in (0,) + BITS, "CERTIFICATE_BITS_UNSUPPORTED")
        expected = e.sign_certificate((bits,))
        require(submitted == expected, "FORGED_SIGN_CERTIFICATE")
        return {"status": "CERTIFIED", "sign": expected["sign"]}
    except ResourceRefusal as ex:
        return {"status": "RESOURCE_REFUSAL", "reason": str(ex), "is_truth_value": False}
    except (Refusal, ValueError, TypeError, KeyError, OverflowError, RecursionError) as ex:
        return {"status": "BLOCKED", "reason": str(ex), "is_truth_value": False}
