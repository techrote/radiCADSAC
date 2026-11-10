#!/usr/bin/env python3
"""Exact rational-point local germs for polynomial-modulated rational-phase trig.

Research model; never a global open-root isolator or original-source admission.
Proof: separated-amplitude moment valuation, not a finite jet sample.
Standard-library rational/cyclotomic arithmetic.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from functools import lru_cache
from math import comb, factorial, lcm

SCHEMA = "radicadsac-a2-moment-germ/1.0"
MAX_HARMONICS, MAX_DEGREE, MAX_FIELD_ORDER = 8, 3, 64
# Canonical 160-bit numerator/denominator text fits in 101 characters.
# Reject oversized text BEFORE Fraction parses/normalizes it.
MAX_RATIONAL_LITERAL_CHARS = 128


class Refusal(ValueError):
    pass


def require(test, reason):
    if not test:
        raise Refusal(reason)


def rational(value):
    require(type(value) in (str, int, Q), "NONEXACT_RATIONAL")
    if type(value) is str:
        require(len(value) <= MAX_RATIONAL_LITERAL_CHARS,
                "RATIONAL_LITERAL_RESOURCE_LIMIT")
    try:
        result = Q(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise Refusal("INVALID_RATIONAL") from exc
    require(max(result.numerator.bit_length(), result.denominator.bit_length()) <= 160,
            "RATIONAL_RESOURCE_LIMIT")
    return result


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return tuple(p)


def divmod_poly(a, b):
    a, b = list(trim(a)), trim(b)
    require(b != (0,), "ZERO_POLYNOMIAL_DIVISOR")
    q = [Q(0)] * max(1, len(a) - len(b) + 1)
    while trim(a) != (0,) and len(a) >= len(b):
        i, scale = len(a) - len(b), a[-1] / b[-1]
        q[i] = scale
        for j, value in enumerate(b):
            a[i + j] -= scale * value
        a = list(trim(a))
    return trim(q), trim(a)


@lru_cache(maxsize=MAX_FIELD_ORDER)
def phi(n):
    require(type(n) is int and 1 <= n <= MAX_FIELD_ORDER,
            "CYCLOTOMIC_FIELD_RESOURCE_LIMIT")
    p = tuple([Q(-1)] + [Q(0)] * (n - 1) + [Q(1)])
    for d in range(1, n):
        if n % d == 0:
            p, remainder = divmod_poly(p, phi(d))
            require(remainder == (0,), "CYCLOTOMIC_DIVISION_FAILED")
    return p


class Field:
    def __init__(self, n):
        require(n % 4 == 0, "MISSING_EXACT_I")
        self.n, self.mod = n, phi(n)
        self.dim = len(self.mod) - 1
        self.zero = tuple(Q(0) for _ in range(self.dim))
        self.one = self.reduce((Q(1),))

    def reduce(self, p):
        _, remainder = divmod_poly(p, self.mod)
        require(len(remainder) <= self.dim, "CYCLOTOMIC_REMAINDER_INVALID")
        return tuple(remainder) + tuple(Q(0) for _ in range(self.dim - len(remainder)))

    def add(self, a, b):
        return tuple(x + y for x, y in zip(a, b))

    def scale(self, a, k):
        return tuple(k * x for x in a)

    def mult(self, a, b):
        out = [Q(0)] * (2 * self.dim - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                out[i + j] += x * y
        return self.reduce(out)

    def power(self, k):
        return self.reduce(tuple([Q(0)] * (k % self.n) + [Q(1)]))

    def trig(self, turn):
        turn = turn % 1
        require((turn * self.n).denominator == 1, "INCOMPATIBLE_CYCLOTOMIC_PHASE")
        k = int(turn * self.n)
        plus, minus = self.power(k), self.power(-k)
        cosine = self.scale(self.add(plus, minus), Q(1, 2))
        sine = self.scale(self.mult(self.power(self.n // 4),
                                    self.add(plus, self.scale(minus, -1))), Q(-1, 2))
        return cosine, sine


def norm_terms(raw):
    require(type(raw) is dict and 1 <= len(raw) <= MAX_HARMONICS,
            "HARMONIC_RESOURCE_LIMIT")
    out = {}
    for h, pair in raw.items():
        require(type(h) is int and 0 <= h <= 8 and
                type(pair) in (list, tuple) and len(pair) == 2,
                "INVALID_HARMONIC")
        ps, qs = pair
        require(type(ps) in (list, tuple) and type(qs) in (list, tuple) and
                1 <= len(ps) <= MAX_DEGREE + 1 and
                1 <= len(qs) <= MAX_DEGREE + 1,
                "POLYNOMIAL_DEGREE_RESOURCE_LIMIT")
        p, q = trim(map(rational, ps)), trim(map(rational, qs))
        require(h != 0 or q == (0,), "NONCANONICAL_ZERO_HARMONIC_SINE")
        out[h] = (p, q)
    return dict(sorted(out.items()))


def source(left, right, offset, rate, terms):
    left, right, offset, rate = map(rational, (left, right, offset, rate))
    require(left < right and rate != 0, "INVALID_SOURCE_INTERVAL_OR_PHASE_RATE")
    require(-4 <= left and right <= 4 and abs(rate) <= 4,
            "SOURCE_DOMAIN_RESOURCE_LIMIT")
    return {"left": left, "right": right, "offset": offset,
            "rate": rate, "terms": norm_terms(terms)}


def source_dict(s):
    return {"interval": [str(s["left"]), str(s["right"])],
            "phase": [str(s["offset"]), str(s["rate"])],
            "terms": {str(h): [[str(x) for x in p], [str(x) for x in q]]
                      for h, (p, q) in s["terms"].items()}}


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":"))
                          .encode("ascii")).hexdigest()


def shifted(poly, x):
    # Polynomial at x+s, coefficients by powers of s.
    return tuple(sum(coef * comb(i, j) * x ** (i - j)
                     for i, coef in enumerate(poly) if i >= j)
                 for j in range(len(poly)))


def algebraic_moment(field, s, shifts, x, j, k):
    """Coefficient of (pi*s)^k in the j-th amplitude Taylor slice."""
    acc = field.zero
    for h, (p, q) in shifts.items():
        pj = p[j] if j < len(p) else Q(0)
        qj = q[j] if j < len(q) else Q(0)
        if pj == 0 and qj == 0:
            continue
        if h == 0 and k:
            continue
        c, si = field.trig(h * (s["offset"] + s["rate"] * x))
        cycle_c = (c, field.scale(si, -1), field.scale(c, -1), si)
        cycle_s = (si, c, field.scale(si, -1), field.scale(c, -1))
        coeff = field.add(field.scale(cycle_c[k % 4], pj),
                          field.scale(cycle_s[k % 4], qj))
        acc = field.add(acc, field.scale(coeff, (2 * h * s["rate"]) ** k / factorial(k)))
    return acc


def analytic_moments(s, x):
    s = source(s["left"], s["right"], s["offset"], s["rate"], s["terms"])
    x = rational(x)
    require(s["left"] <= x <= s["right"], "POINT_OUTSIDE_SOURCE")
    n = 4
    for h in s["terms"]:
        n = lcm(n, (h * (s["offset"] + s["rate"] * x)).denominator)
    field = Field(n)
    shifted_terms = {h: (shifted(p, x), shifted(q, x))
                     for h, (p, q) in s["terms"].items()}
    max_degree = max(max(len(p), len(q)) - 1
                     for p, q in shifted_terms.values())
    rows = []
    for j in range(max_degree + 1):
        hs = [h for h, (p, q) in shifted_terms.items()
              if (j < len(p) and p[j] != 0) or (j < len(q) and q[j] != 0)]
        if not hs:
            continue
        M = int(0 in hs) + 2 * sum(h > 0 for h in hs)
        for k in range(M):
            if algebraic_moment(field, s, shifted_terms, x, j, k) != field.zero:
                rows.append((j, k))
                break
        else:
            raise AssertionError("ANNIHILATOR_MOMENT_BOUND_VIOLATED")
    return s, x, field, shifted_terms, rows


def pi_interval(n):
    def atan(x):
        partial = sum((-1) ** k * x ** (2 * k + 1) / (2 * k + 1)
                      for k in range(n))
        error = x ** (2 * n + 1) / (2 * n + 1)
        return (partial, partial + error) if n % 2 == 0 else (partial - error, partial)
    a, b = atan(Q(1, 5)), atan(Q(1, 239))
    return 16 * a[0] - 4 * b[1], 16 * a[1] - 4 * b[0]


def iadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def iscale(a, q):
    return (a[0] * q, a[1] * q) if q >= 0 else (a[1] * q, a[0] * q)


def imul(a, b):
    values = [x * y for x in a for y in b]
    return min(values), max(values)


def trig_interval(turns, precision, piv):
    # Exact periodic reduction; Taylor at rational midpoint of pi enclosure.
    turns = turns % 1
    if turns > Q(1, 2):
        turns -= 1
    if turns == 0:
        return (Q(1), Q(1)), (Q(0), Q(0))
    if turns == Q(1, 2):
        return (Q(-1), Q(-1)), (Q(0), Q(0))
    mid = sum(piv) / 2
    radius = (piv[1] - piv[0]) / 2 * abs(2 * turns)
    arg = 2 * turns * mid
    c = sum((-1) ** k * arg ** (2 * k) / factorial(2 * k)
            for k in range(precision + 1))
    si = sum((-1) ** k * arg ** (2 * k + 1) / factorial(2 * k + 1)
             for k in range(precision + 1))
    ec = abs(arg) ** (2 * precision + 1) / factorial(2 * precision + 1) + radius
    es = abs(arg) ** (2 * precision + 2) / factorial(2 * precision + 2) + radius
    return (c - ec, c + ec), (si - es, si + es)


def leading_interval(s, x, shifts, first_n, precision):
    pi = pi_interval(precision)
    coeff = (Q(0), Q(0))
    trig_cache = {}
    for j in range(first_n + 1):
        k = first_n - j
        pp = (pi[0] ** k, pi[1] ** k)
        for h, (p, q) in shifts.items():
            pj = p[j] if j < len(p) else 0
            qj = q[j] if j < len(q) else 0
            if not pj and not qj:
                continue
            if h == 0 and k:
                continue
            turn = h * (s["offset"] + s["rate"] * x)
            if turn not in trig_cache:
                trig_cache[turn] = trig_interval(turn, precision, pi)
            cosine, sine = trig_cache[turn]
            a = (cosine, iscale(sine, -1), iscale(cosine, -1), sine)[k % 4]
            b = (sine, cosine, iscale(sine, -1), iscale(cosine, -1))[k % 4]
            part = iadd(iscale(a, pj), iscale(b, qj))
            part = imul(iscale(part, (2 * h * s["rate"]) ** k / factorial(k)), pp)
            coeff = iadd(coeff, part)
    return coeff


def point_germ(s, x):
    s, x, field, shifts, rows = analytic_moments(s, x)
    binding = digest(source_dict(s))
    if not rows:
        return {"schema": SCHEMA, "status": "IDENTITY_ZERO_ON_ANALYTIC_SPAN",
                "source_sha256": binding, "coordinate": str(x),
                "zero_interval": True, "original_source_certified": False,
                "mc_b_established": False, "production_authorized": False}
    first_n = min(j + k for j, k in rows)
    sign = None
    for precision in (8, 12, 16, 24, 32, 48, 64, 96):
        lo, hi = leading_interval(s, x, shifts, first_n, precision)
        if lo > 0:
            sign = 1
            break
        if hi < 0:
            sign = -1
            break
    require(sign is not None, "SIGN_INTERVAL_RESOURCE_REFUSAL")
    const_h = any(h == 0 and p != (0,) for h, (p, _) in shifts.items())
    positive_h = sum(h > 0 and (p != (0,) or q != (0,))
                     for h, (p, q) in shifts.items())
    deg = max(max(len(p), len(q)) - 1 for p, q in shifts.values())
    global_bound = deg + int(const_h) + 2 * positive_h - 1
    require(first_n <= global_bound, "MOMENT_GLOBAL_BOUND_VIOLATED")
    return {"schema": SCHEMA,
            "status": "EXACT_POINT_ZERO" if first_n else "EXACT_POINT_NONZERO",
            "source_sha256": binding, "coordinate": str(x),
            "phase_turn": str(s["offset"] + s["rate"] * x),
            "cyclotomic_order": field.n, "order": first_n,
            "right_sign": sign, "left_sign": sign * (-1) ** first_n,
            "event_kind": ("NONZERO" if first_n == 0 else
                           "CROSSING" if first_n % 2 else "TANGENCY"),
            "moment_rows": [{"degree": j, "moment": k}
                            for j, k in rows],
            "first_coefficient_enclosure": [str(lo), str(hi)],
            "sign_series_terms": precision,
            "structural_order_bound": global_bound,
            "evidence_class": "DETERMINISTIC_MODEL",
            "original_source_certified": False,
            "complete_open_root_isolation": False,
            "mc_b_established": False, "production_authorized": False}


def strict_receipt_equal(expected, claimed):
    """Compare canonical research receipts without subclass-controlled equality.

    The expected tree is independently recomputed from an admitted source and
    contains only bounded JSON primitives.  Exact type checks distinguish
    bool/int, prevent hostile `__eq__`, and reject noncanonical dict keys.
    Recursion follows that finite expected tree, not attacker-owned structure.
    This checks receipt integrity, *not* original physical-source custody.
    """
    if type(expected) is not type(claimed):
        return False
    if type(expected) is dict:
        if len(expected) != len(claimed) or any(type(k) is not str for k in claimed):
            return False
        return all(k in claimed and strict_receipt_equal(value, claimed[k])
                   for k, value in expected.items())
    if type(expected) is list:
        return len(expected) == len(claimed) and all(
            strict_receipt_equal(a, b) for a, b in zip(expected, claimed))
    if type(expected) in (str, int, bool, type(None)):
        return expected == claimed
    return False


def verify_receipt(s, x, claimed):
    require(type(claimed) is dict and
            strict_receipt_equal(point_germ(s, x), claimed),
            "FORGED_OR_STALE_GERM_RECEIPT")
    return True


def bezier_polynomial(control, left, right):
    p = len(control) - 1
    scale = right - left
    # Convert exact Bernstein controls to global monomial polynomial.
    u = [sum(Q(comb(p, k) * comb(k, i) * (-1) ** (k - i)) * control[i]
             for i in range(k + 1)) for k in range(p + 1)]
    out = [Q(0)] * (p + 1)
    for k, a in enumerate(u):
        for m in range(k + 1):
            out[m] += a * comb(k, m) * (-left) ** (k - m) / scale ** k
    return trim(out)


def clamped_two_span_bezier(degree, knots, controls, offset, rate):
    """Authenticate a genuine clamped C0 rational B-spline knot.

    Only [L]*(p+1) + [K]*p + [R]*(p+1), p=1..3.
    Shared control at the internal p-multiple knot enforces C0.
    """
    require(type(degree) is int and 1 <= degree <= MAX_DEGREE,
            "UNSUPPORTED_SPLINE_DEGREE")
    # Own the source grammar before processing elements: no unbounded iterator
    # materialisation, and at most 3*p+2 rational conversions for p<=3.
    require(type(knots) in (list, tuple) and len(knots) == 3 * degree + 2,
            "INVALID_BSPLINE_KNOT_COUNT")
    ks = tuple(rational(x) for x in knots)
    L, K, R = ks[0], ks[degree + 1], ks[-1]
    require(L < K < R and ks == ((L,) * (degree + 1) +
                                 (K,) * degree + (R,) * (degree + 1)),
            "UNSUPPORTED_SPLINE_KNOT_PATTERN")
    require(type(controls) is dict and 1 <= len(controls) <= MAX_HARMONICS,
            "INVALID_SPLINE_CHANNELS")
    first, second = {}, {}
    identity_channels = {}
    for h, pair in controls.items():
        require(type(h) is int and 0 <= h <= 8 and
                type(pair) in (tuple, list) and len(pair) == 2,
                "INVALID_SPLINE_HARMONIC")
        cp, cq = pair
        require(type(cp) in (tuple, list) and type(cq) in (tuple, list) and
                len(cp) == 2 * degree + 1 and len(cq) == 2 * degree + 1,
                "INVALID_SPLINE_CONTROL_COUNT")
        cp = tuple(map(rational, cp))
        cq = tuple(map(rational, cq))
        identity_channels[str(h)] = [[str(v) for v in cp], [str(v) for v in cq]]
        first[h] = (bezier_polynomial(cp[:degree + 1], L, K),
                    bezier_polynomial(cq[:degree + 1], L, K))
        second[h] = (bezier_polynomial(cp[degree:], K, R),
                     bezier_polynomial(cq[degree:], K, R))
    a, b = source(L, K, offset, rate, first), source(K, R, offset, rate, second)
    source_binding = digest({"degree": degree, "knots": list(map(str, ks)),
                             "phase": [str(rational(offset)), str(rational(rate))],
                             "controls": identity_channels})
    return a, b, K, source_binding


def knot_germ(degree, knots, controls, offset, rate):
    a, b, x, spline_sha = clamped_two_span_bezier(degree, knots, controls,
                                                   offset, rate)
    lhs, rhs = point_germ(a, x), point_germ(b, x)
    # A C0 spline shares its actual control at the knot, not merely its sign.
    left_zero = lhs["status"] != "EXACT_POINT_NONZERO"
    right_zero = rhs["status"] != "EXACT_POINT_NONZERO"
    require(left_zero == right_zero, "DISCONTINUOUS_KNOT_VALUE")
    if not left_zero:
        require(lhs["right_sign"] == rhs["right_sign"],
                "DISCONTINUOUS_NONZERO_KNOT")
        category = "NONZERO_KNOT"
    elif lhs["status"] == rhs["status"] == "IDENTITY_ZERO_ON_ANALYTIC_SPAN":
        category = "CONTINUUM_BOTH_SIDES"
    elif (lhs["status"] == "IDENTITY_ZERO_ON_ANALYTIC_SPAN" or
          rhs["status"] == "IDENTITY_ZERO_ON_ANALYTIC_SPAN"):
        category = "CONTINUUM_ADJACENT_ZERO_KNOT"
    else:
        category = "SINGLE_PHYSICAL_ZERO_KNOT"
    return {"schema": SCHEMA, "status": category, "spline_sha256": spline_sha,
            "knot": str(x), "left": lhs, "right": rhs,
            "physical_zero_count": 1 if category == "SINGLE_PHYSICAL_ZERO_KNOT" else 0,
            "global_smooth_multiplicity_claimed": False,
            "original_source_certified": False, "mc_b_established": False,
            "production_authorized": False}



def verify_knot_receipt(degree, knots, controls, offset, rate, claimed):
    """Reconstruct from complete knot/control source; never trust a knot report."""
    require(type(claimed) is dict and
            strict_receipt_equal(
                knot_germ(degree, knots, controls, offset, rate), claimed),
            "FORGED_OR_STALE_KNOT_RECEIPT")
    return True


def reversed_spline(degree, knots, controls, offset, rate, A=2):
    """Reparameterise t=A-u; refuse invalid source shape before reversal.

    Source and transformed-source admission are checked independently. A
    syntactically plausible returned array is not itself a germ certificate.
    """
    require(type(degree) is int and 1 <= degree <= MAX_DEGREE,
            "UNSUPPORTED_SPLINE_DEGREE")
    require(type(knots) in (list, tuple) and len(knots) == 3 * degree + 2,
            "INVALID_BSPLINE_KNOT_COUNT")
    # A3 review #5834336109: preflight *all* control shapes before any
    # reversed() call or element conversion, including channels after h=0.
    require(type(controls) is dict and 1 <= len(controls) <= MAX_HARMONICS,
            "INVALID_SPLINE_CHANNELS")
    for h, pair in controls.items():
        require(type(h) is int and 0 <= h <= 8 and
                type(pair) in (tuple, list) and len(pair) == 2,
                "INVALID_SPLINE_HARMONIC")
        cp, cq = pair
        require(type(cp) in (tuple, list) and type(cq) in (tuple, list) and
                len(cp) == 2 * degree + 1 and len(cq) == 2 * degree + 1,
                "INVALID_SPLINE_CONTROL_COUNT")
    # Bound literal parsing and authenticate complete source rather than
    # returning a reversal of noncanonical or discontinuous input.
    clamped_two_span_bezier(degree, knots, controls, offset, rate)
    anchor, phase_offset, phase_rate = rational(A), rational(offset), rational(rate)
    ks = [anchor - rational(x) for x in reversed(knots)]
    cs = {h: [list(reversed(pair[0])), list(reversed(pair[1]))]
          for h, pair in controls.items()}
    new_offset, new_rate = phase_offset + phase_rate * anchor, -phase_rate
    # A may move a valid source outside this model's domain budget.
    # Validate the *output* instead of claiming it is admissible regardless.
    clamped_two_span_bezier(degree, ks, cs, new_offset, new_rate)
    return degree, ks, cs, new_offset, new_rate


def attempt(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except (Refusal, MemoryError, OverflowError, RecursionError) as exc:
        return {"schema": SCHEMA, "status": "RESOURCE_REFUSAL_OR_BLOCKED",
                "reason": str(exc), "is_truth_value": False,
                "mc_b_established": False, "production_authorized": False}
