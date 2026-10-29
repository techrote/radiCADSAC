#!/usr/bin/env python3
"""MC-038 research: exact rational-parameter events for polynomial-modulated trig.

This is a POINT-LOCAL jet proof, never a complete open-root or V27/V41
child-certificate decision. Cyclotomic field arithmetic proves exact zero
derivatives; rational pi/trig enclosures separately prove the first sign.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from functools import lru_cache
from math import comb, lcm

import pb00701_transverse_trig_interval as interval

SCHEMA = "radicadsac-mc038-rational-phase-point/1.0"
MAX_CYCLOTOMIC_ORDER = 48
MAX_JET_ORDER = 10
MAX_BITS = 16384


class Refusal(ValueError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def need(condition, reason):
    if not condition:
        raise Refusal(reason)


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def poly_mul(a, b):
    out = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return trim(out)


def poly_div(a, b):
    a, b = trim(a), trim(b)
    need(b != [0], "ZERO_POLYNOMIAL_DIVISOR")
    quotient = [Q(0)] * max(1, len(a)-len(b)+1)
    while a != [0] and len(a) >= len(b):
        degree = len(a)-len(b)
        factor = a[-1]/b[-1]
        quotient[degree] = factor
        for j, v in enumerate(b):
            a[degree+j] -= factor*v
        a = trim(a)
    return trim(quotient), a


@lru_cache(maxsize=MAX_CYCLOTOMIC_ORDER)
def cyclotomic(n):
    """Exact Phi_n: (x^n-1) / product of Phi_d over proper divisors."""
    need(type(n) is int and 1 <= n <= MAX_CYCLOTOMIC_ORDER,
         "CYCLOTOMIC_ORDER_RESOURCE_LIMIT")
    numerator = [Q(-1)] + [Q(0)]*(n-1) + [Q(1)]
    for divisor in range(1, n):
        if n % divisor == 0:
            quotient, remainder = poly_div(numerator, cyclotomic(divisor))
            need(remainder == [0], "CYCLOTOMIC_EXACT_DIVISION_FAILED")
            numerator = quotient
    need(numerator[-1] == 1, "NONMONIC_CYCLOTOMIC")
    return tuple(numerator)


def ring_reduce(p, modulus):
    _, remainder = poly_div(p, modulus)
    need(len(remainder) < len(modulus), "INVALID_QUOTIENT_FIELD_REDUCTION")
    vector = tuple(remainder + [Q(0)]*(len(modulus)-1-len(remainder)))
    need(all(max(v.numerator.bit_length(), v.denominator.bit_length()) <= MAX_BITS
             for v in vector), "CYCLOTOMIC_COEFFICIENT_RESOURCE_LIMIT")
    return vector


def ring_add(a, b):
    return tuple(x+y for x,y in zip(a,b))


def ring_scale(a, scalar):
    return tuple(scalar*x for x in a)


def ring_mul(a, b, modulus):
    return ring_reduce(poly_mul(a,b), modulus)


def ring_power(exponent, n, modulus):
    exponent %= n
    return ring_reduce([Q(0)]*exponent + [Q(1)], modulus)


def ring_trig(turn, n, modulus):
    """Exact real cos/sin in Q[zeta_n], using i=zeta_n^(n/4)."""
    turn = turn % 1
    need((turn*n).denominator == 1 and n % 4 == 0,
         "ROOT_OF_UNITY_PHASE_MISMATCH")
    exponent = int(turn*n)
    positive = ring_power(exponent, n, modulus)
    negative = ring_power(-exponent, n, modulus)
    cosine = ring_scale(ring_add(positive,negative), Q(1,2))
    difference = ring_add(positive,ring_scale(negative,-1))
    sine = ring_scale(
        ring_mul(ring_power(n//4,n,modulus),difference,modulus),
        Q(-1,2))
    return cosine, sine


def point_derivative(poly, x, order):
    return sum((coef * (comb(i,order) if i>=order else 0)
                * (1 if order == 0 else 1)
                * product_range(i-order+1,i) * x**(i-order))
               for i,coef in enumerate(poly) if i>=order)


def product_range(start, end):
    total = 1
    for k in range(start,end+1):
        total *= k
    return total


def shift_pair(cos, sin, order):
    return ((cos, sin), (ring_scale(sin,-1),cos),
            (ring_scale(cos,-1),ring_scale(sin,-1)),
            (sin,ring_scale(cos,-1)))[order%4]


def interval_shift(cos, sin, order):
    return ((cos,sin), (interval.scale(sin,-1),cos),
            (interval.scale(cos,-1),interval.scale(sin,-1)),
            (sin,interval.scale(cos,-1)))[order%4]


def validate(span,x,max_order):
    need(type(span) is interval.Span, "UNSUPPORTED_SOURCE_SPAN")
    x = interval.formal_rational(x)
    need(span.left <= x <= span.right, "POINT_OUTSIDE_ORIGINAL_SOURCE_SPAN")
    need(type(max_order) is int and 0 <= max_order <= MAX_JET_ORDER,
         "JET_ORDER_RESOURCE_LIMIT")
    phase = span.offset + span.rate*x
    n = 4
    for h in span.terms:
        n = lcm(n,(h*phase).denominator)
    need(n <= MAX_CYCLOTOMIC_ORDER, "CYCLOTOMIC_ORDER_RESOURCE_LIMIT")
    return x,phase,n,cyclotomic(n)


def jet(span,x,order,n,modulus):
    """Pi^k coefficients in Q[zeta_n] for exact derivative order."""
    degree = len(modulus)-1
    zero = (Q(0),)*degree
    accum = {}
    for h,(cos_poly,sin_poly) in span.terms.items():
        cosine,sine = ring_trig(h*(span.offset+span.rate*x),n,modulus)
        for j in range(order+1):
            k = order-j
            p = point_derivative(cos_poly,x,j)
            q = point_derivative(sin_poly,x,j)
            if p==0 and q==0:
                continue
            shifted_cos,shifted_sin = shift_pair(cosine,sine,k)
            coeff = ring_add(ring_scale(shifted_cos,p),
                             ring_scale(shifted_sin,q))
            coeff = ring_scale(coeff,Q(comb(order,j))*(2*h*span.rate)**k)
            accum[k] = ring_add(accum.get(k,zero),coeff)
    return {k:v for k,v in accum.items() if any(v)}


def derivative_interval(span,x,order):
    plo,phi = interval.pi_bounds()
    answer = interval.exact(Q(0))
    for h,(cp,sp) in span.terms.items():
        cosine,sine = interval.trig(h*(span.offset+span.rate*x))
        for j in range(order+1):
            k = order-j
            a,b = interval_shift(cosine,sine,k)
            p,q = point_derivative(cp,x,j),point_derivative(sp,x,j)
            coeff = Q(comb(order,j))*(2*h*span.rate)**k
            contribution = interval.add(interval.scale(a,p),
                                        interval.scale(b,q))
            contribution = interval.mul(interval.scale(contribution,coeff),
                                        (plo**k,phi**k))
            answer = interval.add(answer,contribution)
    return answer


def span_binding(span):
    source = {
        "interval":[str(span.left),str(span.right)],
        "phase":[str(span.offset),str(span.rate)],
        "terms":{str(h):[list(map(str,p)),list(map(str,q))]
                 for h,(p,q) in sorted(span.terms.items())},
    }
    return hashlib.sha256(json.dumps(source,sort_keys=True,
                          separators=(",",":")).encode("ascii")).hexdigest()


def point(span,x,max_order=MAX_JET_ORDER):
    x,phase,n,modulus = validate(span,x,max_order)
    for order in range(max_order+1):
        coefficients = jet(span,x,order,n,modulus)
        if not coefficients:
            continue
        # Pi is transcendental over the algebraic numbers. A nonzero
        # polynomial in Pi with algebraic coefficients is nonzero exactly.
        enclosure = derivative_interval(span,x,order)
        sign = interval.strict_sign(enclosure)
        need(sign != 0, "FIRST_NONZERO_DERIVATIVE_SIGN_UNRESOLVED")
        if order == 0:
            status = "EXACT_NONZERO_RATIONAL_POINT"
            result = {"value_sign":sign}
        else:
            status = "EXACT_RATIONAL_POINT_EVENT"
            result = {
                "one_sided_order":order,
                "left_sign":sign*(-1)**order,
                "right_sign":sign,
                "event_kind":"CROSSING" if order%2 else "TANGENCY",
                "left_in_source":x>span.left,
                "right_in_source":x<span.right,
            }
        return {"schema":SCHEMA,"status":status,
                "evidence_class":"DETERMINISTIC_MODEL",
                "source_binding_sha256":span_binding(span),
                "coordinate":str(x),"phase_turn":str(phase),
                "cyclotomic_order":n,
                "exact_vanishing_derivatives":list(range(order)),
                "first_nonzero_derivative_order":order,
                "first_nonzero_derivative_sign":sign,
                "strict_derivative_enclosure":list(map(str,enclosure)),
                "exact_zero_decision":"ROOT_OF_UNITY_AND_PI_TRANSCENDENCE",
                "original_v27_v41_route_certified":False,
                "historical_v54_admitted":False,
                "complete_open_roots_claimed":False,
                "mc_b_established":False,"mc1_established":False,
                "production_authorized":False,**result}
    raise Refusal("JET_ORDER_RESOURCE_LIMIT_UNRESOLVED")


def compose_knot(left,right,x,max_order=MAX_JET_ORDER):
    need(type(left) is interval.Span and type(right) is interval.Span,
         "UNSUPPORTED_KNOT_OWNER")
    x = interval.formal_rational(x)
    need(left.right == x == right.left and
         (left.offset,left.rate)==(right.offset,right.rate),
         "SOURCE_KNOT_PHASE_OR_COORDINATE_MISMATCH")
    _,_,n,modulus = validate(left,x,max_order)
    _,_,n2,_ = validate(right,x,max_order)
    need(n==n2, "SOURCE_KNOT_CYCLOTOMIC_MISMATCH")
    # Do not confuse equal point signs with actual continuity. Exact F_L=F_R
    # is required in the same cyclotomic number field.
    need(jet(left,x,0,n,modulus)==jet(right,x,0,n,modulus),
         "DISCONTINUOUS_SOURCE_KNOT")
    l,r = point(left,x,max_order),point(right,x,max_order)
    need(l["status"]==r["status"],"SOURCE_KNOT_ZERO_STATUS_MISMATCH")
    if l["status"]=="EXACT_NONZERO_RATIONAL_POINT":
        need(l["value_sign"]==r["value_sign"],"SOURCE_KNOT_SIGN_MISMATCH")
        return {"schema":SCHEMA,"status":"EXACT_NONZERO_SOURCE_KNOT",
                "coordinate":str(x),"sign":l["value_sign"],
                "source_bindings":[l["source_binding_sha256"],r["source_binding_sha256"]],
                "physical_zero_events":0,"production_authorized":False}
    return {"schema":SCHEMA,"status":"EXACT_SINGLE_SOURCE_KNOT_ZERO",
            "coordinate":str(x),"physical_zero_events":1,
            "left_one_sided_order":l["one_sided_order"],
            "right_one_sided_order":r["one_sided_order"],
            "left_sign":l["left_sign"],"right_sign":r["right_sign"],
            "event_kind":"CROSSING" if l["left_sign"]!=r["right_sign"] else "TOUCHING",
            "global_smooth_multiplicity_claimed":False,
            "source_bindings":[l["source_binding_sha256"],r["source_binding_sha256"]],
            "historical_v54_admitted":False,"production_authorized":False}


def attempt(fn,*args,**kwargs):
    try:
        return fn(*args,**kwargs)
    except (Refusal,interval.Refusal) as exc:
        return {"schema":SCHEMA,"status":"RESOURCE_REFUSAL" if
                "RESOURCE" in str(exc) or "UNRESOLVED" in str(exc) else "BLOCKED",
                "reason":str(exc),"is_truth_value":False,
                "production_authorized":False}
    except (MemoryError,OverflowError,RecursionError) as exc:
        return {"schema":SCHEMA,"status":"RESOURCE_REFUSAL",
                "reason":type(exc).__name__,"is_truth_value":False,
                "production_authorized":False}


def validate_submitted(span,x,submitted):
    need(type(submitted) is dict, "UNTRUSTED_REPORT_TYPE")
    expected=attempt(point,span,x)
    need(expected==submitted,"FORGED_OR_UNCHECKED_POINT_WITNESS")
    return expected
