# PB-007-01 common-factor reduction boundary

Status: **v8 bounded route established; PB-007-01 remains open**.

## Scope

This document records the v8 constructive extension owned by corrective issue #178. It consumes the accepted PB-007-01 v7 exact B-spline lowering and recognizes only those residual source spans whose nonzero harmonic modulation polynomials share one exact nonconstant rational polynomial factor and leave constant harmonic quotients.

It does not redefine the MC-1 domain, close PB-007-01, or authorize MC-B.

## Accepted v8 predicate

For a v7 local span, let every cosine/sine modulation channel be an exact rational polynomial in the same local source coordinate `s`. The v8 route is admissible only when exact rational polynomial GCD/division proves

`p_k(s) = g(s) c_k` and `q_k(s) = g(s) d_k`

for every nonzero channel, where `degree(g) > 0` and all `c_k,d_k` are exact rationals. Thus

`F(s) = g(s) T(theta(s))`.

The factor is computed; a caller-supplied factor, quotient, tolerance or sampling claim is not authority.

## Exact authorities

`g` uses the MC-032 exact rational polynomial/Sturm machinery. `T` uses the PB-007-01 v6 rational-turn tangent-half/Sturm machinery. v7 B-spline knot boundaries are preserved exactly, and additional exact source boundaries are inserted at affine-phase quarter turns so a cardinal chart shift can avoid tangent-half poles without epsilon.

Rational common-factor roots are enumerated by the rational-root theorem and checked against `T` at the exact rational phase turn. Coincident multiplicities add.

## Algebraic-irrational disjointness

Under all of these conditions:

- `g` has rational coefficients;
- the source/span maps are rational affine maps;
- phase offset and nonzero phase rate are rational;
- `T` is a finite nonzero rational-coefficient trigonometric polynomial;

an algebraic-irrational root of `g` maps to an algebraic-irrational turn. A zero of `T` there would make `exp(2*pi*i*turn)` algebraic after the finite Fourier relation is converted to a polynomial in that exponential. Gel'fond–Schneider, applied to the principal value of `(-1)^(2*turn)`, makes the same number transcendental. Therefore such an intersection is excluded exactly in this narrow grammar.

Reference: Encyclopedia of Mathematics, *Gel'fond–Schneider method*, https://encyclopediaofmath.org/wiki/Gel%27fond%E2%80%93Schneider_method .

The result must not be generalized to an arbitrary exponential-polynomial/Pfaffian grammar, a zero phase rate, nonalgebraic source authority, or any unreviewed coefficient field.

## Failure-closed boundary

A constant GCD, a nonconstant quotient after exact division, malformed exact source data, independent source/phase parameters, identity-zero semantic ambiguity, unsupported theorem preconditions, or bounded-resource exhaustion does not become a geometric truth value. The existing PB-007-01 blocker remains live.

Binary floating point, epsilon signs, finite sampling, adaptive-refinement exhaustion, timeout and resource refusal are not correctness authority.

## Programme state

PB-007-01 remains **OPEN** because the v7 residual grammar still admits nonproportional nonconstant modulation channels. PB-007-02 remains `OPEN_DEPENDENT_ON_PB-007-01`; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04, PO-05 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`.

The operation denominator remains 26. Source/audio/provenance, canonical journal, exact time/path/phase correlation, source uncertainty, positive-volume material, holder/access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain protected and unchanged.
