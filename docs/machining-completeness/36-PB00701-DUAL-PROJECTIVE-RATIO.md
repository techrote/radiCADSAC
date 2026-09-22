# PB-007-01 v10 — dual-projective single-harmonic ratio route

This document records corrective issue #182. It is an additive bounded repair on top of immutable PB-007-01 v3/v6/v7/v8/v9 evidence. PB-007-01 remains open, MC-B remains `NOT_ESTABLISHED`, and the frozen 26-operation machining denominator is unchanged.

## Dual projective construction

For the existing exact single-harmonic non-common family

`F(s)=A(s) cos(h theta(s)) + B(s) sin(h theta(s))`,

v10 keeps the v9 premises: exact rational modulation polynomials, exact constant `gcd(A,B)`, one positive harmonic, one shared source parameter, and nonzero exact-rational affine phase. Define `u=2*h*theta_turn` and `D=A*B'-A'*B`.

When exact Sturm authority proves `B` zero-free, the existing v9 tangent route remains authoritative:

`tan(pi*u)=-A/B`, with `(-A/B)'=D/B^2`.

When `B` is not zero-free but exact Sturm authority proves `A` zero-free, v10 uses the dual chart

`cot(pi*u)=-B/A`, with `(-B/A)'=-D/A^2`.

The same exact opposed-sign condition on `D` used by v9 makes the selected projective event function strictly monotone. For increasing `u`, the tangent function is strictly increasing while the cotangent function is strictly decreasing; for decreasing `u` the directions reverse. Root counts therefore follow from exact endpoint signs rather than sampling.

## Exact cotangent poles and finite comparisons

Cotangent poles are the exact values `u=n`. Rational affine phase makes every induced source cut rational. One-sided pole signs are symbolic infinities. At a cotangent pole the original event equals `A*cos(pi*n)`, so the independently certified zero-free `A` proves the original event is nonzero.

At a finite source boundary, v10 does not numerically evaluate cotangent. It uses

`cot(pi*u)=tan(pi*(1/2-u))`

and delegates the shifted exact rational turn to the established v6 algebraic endpoint representation, polynomial GCD equality test and exact sign refinement.

## Exact endpoint-zero multiplicity

For a finite tangent-chart endpoint root,

`F'/cos(phi)=(-D+pi*u'*(A^2+B^2))/B`, `phi=pi*u`.

For a finite cotangent-chart endpoint root,

`F'/sin(phi)=(D-pi*u'*(A^2+B^2))/A`.

In either chart the denominator is exact nonzero, `u'` is nonzero rational, and `A^2+B^2` is positive rational. A multiple root would force

`pi=D/(u'*(A^2+B^2))`,

which is rational, contradicting the irrationality of `pi`. v10 therefore certifies admitted finite endpoint zeros as exact multiplicity one. The proof is symbolic; no numeric approximation or bound for `pi` is used.

## Fail-closed boundary

The route remains unavailable when neither modulation component is zero-free, when the exact derivative-sign condition changes or cannot be established, or when multiple harmonics are active. Common-factor inputs remain v8-owned and ordinary zero-free-`B` cases remain v9-owned. Binary floating point, epsilon, caller-supplied chart/multiplicity certificates and resource refusal are never correctness authority.

PB-007-01 remains open for the residual non-common multi-harmonic, nonmonotone and neither-component-zero-free coupled analytic grammar. PB-007-02 remains dependent, PB-007-03 remains OPEN, PB-007-04 remains `OPEN_PROPAGATED`, PO-04/PO-05/PO-08 remain OPEN, and MC-B / MC-1 remain `NOT_ESTABLISHED`.

The protected source/audio/provenance record and canonical-journal, exact time/path/phase, source-uncertainty, positive-volume, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics are preserved. This repair authorizes no native, paid, production or expensive campaign.
