# PB-007-01 v11 — exact phase-dominance single-harmonic route

## Contract

This document records a bounded constructive extension of the existing PB-007-01 event authority. It applies only after the v7–v10 exact lowering has produced one positive harmonic with exact rational-polynomial modulation, exact `gcd(A,B)=1`, nonzero exact-rational affine phase rate, and an exact-zero-free tangent or cotangent projective denominator.

It does not narrow the supported machining domain and does not close PB-007-01.

## Predicate

For

`F(s)=A(s) cos(pi*u(s)) + B(s) sin(pi*u(s))`

let

`D=A*B' - A'*B`.

The v10 tangent chart has

`H'=pi*u'*sec^2(pi*u)-D/B^2`,

and the v10 cotangent chart has

`K'=-pi*u'*csc^2(pi*u)+D/A^2`.

For the selected exact-zero-free denominator `den`, construct exactly

`P(s)=3*abs(u')*den(s)^2-sign(u')*D(s)`.

The theorem `pi > 3`, together with `sec^2>=1` and `csc^2>=1` on their pole-free charts, proves the required derivative direction whenever `P>0` on the entire closed local source span. `P>0` must itself be proved from exact rational-polynomial authority: exact positive endpoint values and exact Sturm exclusion of every open-span root. Numerical pi, epsilon tests, finite samples and time/resource limits are not correctness authority.

## Dispatch precedence

Existing routes retain ownership. v8 common-factor reduction is attempted before v9/v10. v9/v10 exact opposed-monotone routes remain authoritative when they certify. v11 may replace only an exact single-harmonic residual whose failure is the lack of the opposed monotonicity certificate and whose v10 projective preconditions are otherwise established.

The resulting projective function is strictly increasing/decreasing on every existing v10 pole-free chart, so exact boundary signs imply zero or one open root and every admitted open root is simple.

## Boundary semantics

No boundary rule changes. Tangent poles are exact rational-source cuts induced by `u=n+1/2`; cotangent poles are induced by `u=n`. Their one-sided projective signs are symbolic infinities. Finite chart boundaries use the established v6 exact rational-turn algebraic comparison. External endpoint zeros use the v10 exact multiplicity-one theorem. Internal pole points are original-event nonzeros under the exact-zero-free selected component.

Adversarial qualification includes tangent and cotangent `D` sign changes, decreasing phase, exact `1/1000000` neighbours around the dominance threshold, dominance equality/negativity, pole crossings, endpoint events, neither-component-zero-free spans, multi-harmonic inputs, parameter mismatch, binary-float/epsilon authority, forged certificates, refusal laundering, historical mutation and denominator shrinkage.

## Gate state

PB-007-01 remains **OPEN**. PO-04, PO-05 and PO-08 remain OPEN; PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`. MC-B and MC-1 remain `NOT_ESTABLISHED`. The frozen 26-operation denominator and protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume, cutter/holder, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged.
