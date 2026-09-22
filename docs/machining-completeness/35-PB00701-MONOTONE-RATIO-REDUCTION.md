# PB-007-01 v9 — monotone single-harmonic ratio reduction

This document records corrective issue #180. It is an additive bounded repair on top of immutable PB-007-01 v3/v6/v7/v8 evidence. PB-007-01 remains open, MC-B remains `NOT_ESTABLISHED`, and the 26-operation machining denominator is unchanged.

## Qualified non-common subgrammar

After v7 lowers rational B-spline modulation to exact local power-basis polynomials, and after v8 has had the opportunity to consume common-factor products, v9 considers a remaining span only when exactly one positive harmonic is active with both cosine and sine modulation:

`F(s)=A(s) cos(h theta(s)) + B(s) sin(h theta(s))`.

Exact rational-polynomial GCD must prove `gcd(A,B)` constant. Thus this route is genuinely non-common and cannot steal a case from v8. Exact MC-032 Sturm/equality authority must prove `B` nonzero on the closed local span.

## Ratio theorem used by the implementation

Define

`u(s)=2*h*theta_turn(s)` and `r(s)=-A(s)/B(s)`.

Away from tangent poles, `F(s)=0` is equivalent to

`H(s)=tan(pi*u(s))-r(s)=0`.

Since

`r'(s)=(A B' - A' B)/B^2`,

its sign is exactly the sign of the rational polynomial numerator once `B` is proved nonzero. For increasing `u`, v9 requires that numerator to be identically zero or strictly negative on the open span; for decreasing `u`, identically zero or strictly positive. Exact Sturm root exclusion plus an exact rational sample proves the strict case. Then

`H'(s)=pi*u'(s)*sec^2(pi*u(s))-r'(s)`

has the fixed strict sign of `u'`. Only the facts `pi>0` and `sec^2>0` are used; no numeric approximation to pi participates in correctness.

## Exact poles, signs and root counts

The route splits at every exact rational source point where `u=n+1/2`. At those tangent poles, one-sided `H` signs are symbolic infinities. The original event remains finite and nonzero because `cos(h theta)=0`, `sin(h theta)=+/-1`, and `B` is certified nonzero.

At finite rational source boundaries, v6 represents `tan(pi*u)` as an exact rational or isolated algebraic root. Comparing it with the exact rational value `r(s)` uses polynomial GCD/sign refinement. Because `H` is strictly monotone on each pole-free chart, exact boundary signs establish zero or one open root. Every certified open root is simple. External source endpoint equalities remain blocked in v9 unless a separate coupled endpoint-multiplicity route is established; they are not silently counted as simple.

## Fail-closed boundary

The following do not qualify: multiple active harmonics; harmonic zero in place of the positive-harmonic route; a nonconstant `gcd(A,B)` owned by v8; any source zero of `B`; a ratio-derivative numerator whose required sign is not exactly established; zero phase rate already owned by stationary-phase authority; independent source-parameter projection; binary-float or epsilon authority; caller-supplied monotonicity/factor evidence; and resource refusal interpreted as truth.

PB-007-01 remains open for the residual non-common multi-harmonic/nonmonotone coupled analytic grammar. PB-007-02 remains dependent, PB-007-03 remains OPEN, PB-007-04 remains `OPEN_PROPAGATED`, PO-04/PO-05/PO-08 remain OPEN, and MC-B / MC-1 remain `NOT_ESTABLISHED`.

The frozen source/audio/provenance record and canonical-journal, exact time/path/phase, source-uncertainty, positive-volume, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics are preserved. This repair authorizes no native, paid, production or expensive campaign.
