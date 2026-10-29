#!/usr/bin/env python3
"""MC-038: bounded exact-rational transverse-root verifier for affine-turn trig spans.

Every successful span has a complete finite rational partition. Each cell is
strictly nonzero or strictly monotone with proved endpoint signs, hence contains
zero or exactly one *simple* root. Inconclusive/tangent/endpoint cases refuse;
these are NOT certificates for historical child routes or MC-B.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
from math import factorial

SCHEMA = "radicadsac-pb00701-transverse-trig-interval/1.0"

class Refusal(ValueError):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def need(condition, code):
    if not condition:
        raise Refusal(code)


def arctan_bounds(x, terms=14):
    series = sum((-1)**j * x**(2*j + 1) / (2*j + 1)
                 for j in range(terms))
    next_term = x**(2*terms + 1) / (2*terms + 1)
    return ((series, series + next_term) if terms % 2 == 0
            else (series - next_term, series))


@lru_cache(maxsize=1)
def pi_bounds():
    a, b = arctan_bounds(Q(1, 5))
    c, d = arctan_bounds(Q(1, 239))
    lo, hi = 16*a - 4*d, 16*b - 4*c
    need(Q(3) < lo < hi < Q(22, 7), "PI_BOUND_INVALID")
    return lo, hi


def add(a, b): return (a[0] + b[0], a[1] + b[1])
def mul(a, b):
    p = [a[i]*b[j] for i in (0, 1) for j in (0, 1)]
    return (min(p), max(p))
def scale(a, k): return (a[0]*k, a[1]*k) if k >= 0 else (a[1]*k, a[0]*k)
def exact(x): return (x, x)
def widen(a, error): return (a[0] - error, a[1] + error)
def strict_sign(a): return 1 if a[0] > 0 else -1 if a[1] < 0 else 0


@lru_cache(maxsize=32768)
def trig(turns):
    """Exact rational enclosures of cos/sin(2*pi*turns), no float sampling."""
    r = turns + Q(1, 2)
    q = turns - r.numerator // r.denominator
    if q == 0: return exact(Q(1)), exact(Q(0))
    if q == -Q(1, 2): return exact(Q(-1)), exact(Q(0))
    if q == Q(1, 4): return exact(Q(0)), exact(Q(1))
    if q == -Q(1, 4): return exact(Q(0)), exact(Q(-1))
    plo, phi = pi_bounds()
    x = q*(plo + phi)
    argument_error = abs(q)*(phi - plo)
    n = 13
    cos_poly = sum((-1)**j*x**(2*j)/factorial(2*j) for j in range(n + 1))
    sin_poly = sum((-1)**j*x**(2*j + 1)/factorial(2*j + 1)
                   for j in range(n + 1))
    # Taylor-Lagrange remainder and the globally 1-Lipschitz sin/cos bound.
    e_cos = abs(x)**(2*n + 1)/factorial(2*n + 1) + argument_error
    e_sin = abs(x)**(2*n + 2)/factorial(2*n + 2) + argument_error
    return widen(exact(cos_poly), e_cos), widen(exact(sin_poly), e_sin)


def polynomial(coefficients, x):
    y = Q(0)
    for c in reversed(coefficients):
        y = y*x + c
    return y


def derivative(coefficients):
    return tuple(i*c for i, c in enumerate(coefficients) if i > 0)


def norm_bound(coefficients, radius):
    return sum(abs(c)*radius**i for i, c in enumerate(coefficients))


def formal_rational(x):
    need(type(x) in (str, int, Q), "NONEXACT_COEFFICIENT_TYPE")
    if isinstance(x, str):
        need(0 < len(x) <= 128, "OVERSIZED_RATIONAL_LITERAL")
    try:
        y = Q(x)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("INVALID_RATIONAL") from exc
    need(y.numerator.bit_length() <= 128 and y.denominator.bit_length() <= 128,
         "RATIONAL_RESOURCE_LIMIT")
    return y


class Span:
    """Formal F(s)=sum_h [P_h(s)cos(2*pi*h*(offset+rate*s))
                                   +Q_h(s)sin(2*pi*h*(offset+rate*s))]."""
    def __init__(self, left, right, offset, rate, terms):
        self.left, self.right, self.offset, self.rate = map(
            formal_rational, (left, right, offset, rate))
        need(-4 <= self.left < self.right <= 4 and abs(self.rate) <= 4,
             "UNSUPPORTED_SOURCE_DOMAIN")
        need(type(terms) is dict and 1 <= len(terms) <= 8,
             "UNSUPPORTED_HARMONIC_COUNT")
        self.terms = {}
        for key, pair in terms.items():
            need(type(key) is int and 0 <= key <= 8 and
                 type(pair) in (list, tuple) and len(pair) == 2,
                 "UNSUPPORTED_HARMONIC_GRAMMAR")
            p, q = pair
            need(type(p) in (list, tuple) and type(q) in (list, tuple) and
                 1 <= len(p) <= 4 and 1 <= len(q) <= 4,
                 "UNSUPPORTED_POLYNOMIAL_DEGREE")
            self.terms[key] = (tuple(map(formal_rational, p)),
                               tuple(map(formal_rational, q)))
        self.derivatives = {h: (derivative(p), derivative(q))
                            for h, (p, q) in self.terms.items()}
        radius = max(Q(1), abs(self.left), abs(self.right))
        self.m1 = self.m2 = Q(0)
        for h, (p, q) in self.terms.items():
            dp, dq = self.derivatives[h]
            k = Q(44, 7)*abs(h*self.rate)
            amplitude = norm_bound(p, radius) + norm_bound(q, radius)
            d_amplitude = norm_bound(dp, radius) + norm_bound(dq, radius)
            dd_amplitude = (norm_bound(derivative(dp), radius) +
                            norm_bound(derivative(dq), radius))
            self.m1 += d_amplitude + k*amplitude
            self.m2 += dd_amplitude + 2*k*d_amplitude + k*k*amplitude

    @lru_cache(maxsize=32768)
    def evaluate(self, x, first_derivative=False):
        result = exact(Q(0))
        plo, phi = pi_bounds()
        for h, (p, q) in self.terms.items():
            cos, sin = trig(h*(self.offset + self.rate*x))
            if not first_derivative:
                part = add(scale(cos, polynomial(p, x)),
                           scale(sin, polynomial(q, x)))
            else:
                dp, dq = self.derivatives[h]
                k = scale((2*plo, 2*phi), h*self.rate)
                part = add(scale(cos, polynomial(dp, x)),
                           scale(sin, polynomial(dq, x)))
                part = add(part, mul(k, add(
                    scale(cos, polynomial(q, x)),
                    scale(sin, -polynomial(p, x)))))
            result = add(result, part)
        return result

    def prove(self, max_depth=14, max_nodes=20000, bracket_width=Q(1, 64)):
        need(type(max_depth) is int and 0 <= max_depth <= 18 and
             type(max_nodes) is int and 1 <= max_nodes <= 20000 and
             formal_rational(bracket_width) in (Q(1, 16), Q(1, 32), Q(1, 64)),
             "INVALID_RESOURCE_BUDGET")
        bracket_width = Q(bracket_width)
        partition, nodes = [], 0

        def visit(a, b, depth):
            nonlocal nodes
            nodes += 1
            if nodes > max_nodes:
                raise Refusal("NODE_RESOURCE_LIMIT")
            mid, radius = (a + b)/2, (b - a)/2
            possible_f = widen(self.evaluate(mid), self.m1*radius)
            s = strict_sign(possible_f)
            if s:
                partition.append({"kind": "NO_ROOT", "interval": [str(a), str(b)],
                                  "sign": s})
                return
            possible_df = widen(self.evaluate(mid, True), self.m2*radius)
            derivative_sign = strict_sign(possible_df)
            if derivative_sign:
                sign_a, sign_b = (strict_sign(self.evaluate(a)),
                                  strict_sign(self.evaluate(b)))
                if sign_a and sign_b:
                    if sign_a == sign_b:
                        partition.append({"kind": "NO_ROOT", "interval": [str(a), str(b)],
                                          "sign": sign_a})
                        return
                    need((sign_b - sign_a)*derivative_sign > 0,
                         "INCONSISTENT_DERIVATIVE_SIGN")
                    lo, hi = a, b
                    while hi - lo > bracket_width:
                        cut = (lo + hi)/2
                        sign_cut = strict_sign(self.evaluate(cut))
                        if not sign_cut:
                            raise Refusal("UNDECIDED_ISOLATION_CUT")
                        if sign_cut == sign_a:
                            lo = cut
                        else:
                            hi = cut
                    partition.append({
                        "kind": "ONE_SIMPLE_ROOT", "interval": [str(a), str(b)],
                        "strict_isolation": [str(lo), str(hi)],
                        "derivative_sign": derivative_sign,
                        "left_sign": sign_a, "right_sign": sign_b,
                        "smooth_multiplicity": 1,
                    })
                    return
            if depth >= max_depth:
                raise Refusal("UNDECIDED_EVENT_OR_TANGENCY")
            visit(a, mid, depth+1)
            visit(mid, b, depth+1)

        visit(self.left, self.right, 0)
        endpoints = [strict_sign(self.evaluate(self.left)),
                     strict_sign(self.evaluate(self.right))]
        if not all(endpoints):
            raise Refusal("ENDPOINT_ZERO_OR_UNDECIDED")
        # The complete dyadic cover must have one consistent physical sign chain.
        sign_state = endpoints[0]
        for cell in partition:
            if cell["kind"] == "NO_ROOT":
                need(cell["sign"] == sign_state, "SIGN_PARTITION_INCONSISTENT")
            else:
                need(cell["left_sign"] == sign_state,
                     "ROOT_PARTITION_INCONSISTENT")
                sign_state = cell["right_sign"]
        need(sign_state == endpoints[1], "ENDPOINT_SIGN_INCONSISTENT")
        return {"schema": SCHEMA, "status": "RESEARCH_ONLY_CHECKED",
                "evidence_class": "DETERMINISTIC_MODEL", "is_truth_value": True,
                "source_interval": [str(self.left), str(self.right)],
                "source_phase_turns": [str(self.offset), str(self.rate)],
                "partition": partition, "endpoint_signs": endpoints,
                "complete_simple_root_count": sum(
                    c["kind"] == "ONE_SIMPLE_ROOT" for c in partition),
                "nodes": nodes, "historical_child_certified": False,
                "production_authorized": False}


def attempt(span, **budget):
    try:
        return span.prove(**budget)
    except Refusal as exc:
        return {"schema": SCHEMA,
                "status": "RESOURCE_REFUSAL" if exc.reason in (
                    "NODE_RESOURCE_LIMIT", "UNDECIDED_EVENT_OR_TANGENCY",
                    "UNDECIDED_ISOLATION_CUT", "ENDPOINT_ZERO_OR_UNDECIDED")
                else "BLOCKED",
                "reason": exc.reason, "is_truth_value": False,
                "historical_child_certified": False,
                "production_authorized": False}
