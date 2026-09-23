# PB-007-01 v32 — exact algebraic critical-value / rational-separator foundation

Issue: #227  
Parent integration gate: MC-038 / #100  
Source baseline: `bee133512e8e95096c38356ca086b9a0ae53fe10`

## Decision

The missing v31 algebraic primitive is now qualified as a finite exact **foundation**. This does not itself promote a new PB-007-01 event-classification route: PB-007-01 remains **OPEN**, MC-B and MC-1 remain `NOT_ESTABLISHED`, and the machining-domain denominator remains frozen at **26 operations**.

The foundation accepts exact rational source polynomials only. Binary float, sampled/numerical minimization, epsilon/tolerance, caller-supplied critical roots/values/orderings/separators, arbitrary denominator caps, arbitrary subdivision depth and timeout/resource-budget truth authority remain forbidden.

## Exact construction

Let `A(s)=sign(D)D(s)>0` be independently certified on closed `[0,1]`, and let `T(s)` be the transverse source polynomial. Any exact polynomial gcd common to `A` and `T` is cancelled first; because `A` is zero-free on the span, that cancellation cannot remove a source-domain pole or zero.

The rational projective ratio `A/|T|` can have a finite minimum only at a closed-span endpoint with `T != 0` or at a stationary point of

`H(s)=A'(s)T(s)-A(s)T'(s)`

inside a nonzero transverse sign cell. V32 reuses MC-032 exact rational polynomial arithmetic and Sturm counting to isolate all transverse roots and all distinct stationary roots. Repeated stationary roots retain their exact multiplicity through the polynomial gcd chain. Rational isolating intervals are source-derived and independently checkable. Bisection termination is not an arbitrary cap: a conservative rational corollary of the Mignotte root-separation theorem supplies a finite source-derived depth bound.

At an isolated stationary root `r` with exact transverse sign `sigma`, comparison with `alpha=tan(pi/8)=sqrt(2)-1` does not numerically evaluate `r` or `sqrt(2)`. Because `A/|T| >= 0` and `alpha` is the positive root of `y^2+2y-1`, the exact rational source polynomial

`A(s)^2 + 2*sigma*A(s)T(s) - T(s)^2`

has the same sign at `r` as `A(r)/|T(r)|-alpha`. Its sign at the algebraic root is decided exactly: common roots are detected by polynomial gcd, otherwise Sturm isolation is refined only until the test polynomial is root-free on the isolating interval, with a Mignotte-derived finite depth bound.

## Critical-value elimination and rational-between-algebraics synthesis

For separator construction, v32 forms the exact critical-value polynomial in `y`. The stationary contribution is the Sylvester/Bareiss resultant

`Res_s(square_free(H), A(s)^2-y^2*T(s)^2)`

and each finite endpoint contributes `A(e)^2-y^2*T(e)^2`. All arithmetic is exact rational polynomial arithmetic. Real roots are isolated by Sturm authority and ordered against `sqrt(2)-1` using the minimal polynomial `y^2+2y-1`; exact equality fails closed.

Once the least over-approximating critical-value root above the algebraic phase boundary has a rational lower enclosure `beta>sqrt(2)-1`, v32 constructs

`f(beta)=beta^2+2beta-1`

and

`m = beta - f(beta)/(4(beta+1))`.

Exactly as in v30, `beta-alpha = f(beta)/(beta+alpha+2) > f(beta)/(2(beta+1))`, so the source-derived rational `m` satisfies

`sqrt(2)-1 < m < beta`.

No convergent rational search is part of this step. As an independent final guard, v32 then requires both complete-span rational polynomial margins `A-m*T` and `A+m*T` to be strictly positive under MC-032 endpoint/Sturm authority. This final check directly proves `m < A(s)/|T(s)|` everywhere, even if the resultant contains conservative extraneous roots from stationary points outside the source span.

## Adversarial boundary

The v31 diagnostic `D=1+2s`, `T=2+3s` is now certified with a separator synthesized from the canonical source itself, despite v30's separate global Bernstein ratio being only `1/5`; the old diagnostic `m=5/12` is never trusted. Coverage also includes an irrational interior stationary minimum, endpoint minima, an algebraic transverse zero with both sign cells, a repeated transverse zero coincident with a stationary-polynomial root, a repeated stationary root, positive and negative source orientations, and a sign-changing transverse polynomial.

The exact boundary fixture chooses rational `T(s)` so that its interior stationary maximum has value `sqrt(2)+1`; with `A=1`, the projective minimum is exactly `sqrt(2)-1` and fails closed. Changing only the rational constant coefficient by signed `1/1000000` produces independently checked strict neighbours. The rational controls `70/169 < sqrt(2)-1 < 169/408` are also retained.

Caller separator/root/value/ordering/margin/multiplicity metadata is rejected, source-parameter mismatch is a semantic blocker, binary float is rejected, and exact resource refusal remains refusal rather than a mathematical truth value. Historical v31 evidence and the MC-032 event engine are blob-pinned.

## Programme effect and next repair

V32 resolves the precise algebraic foundation blocker recorded by v31. It does **not** close PB-007-01 because it has not yet wired the synthesized separator into the complete phase-cell derivative route with all retained residual terms. The next dependency-ready repair is therefore PB-007-01 v33: integrate this source-owned separator foundation into the v31 pointwise projective certificate, preserve complete v8-v30 precedence, retain both selected-harmonic amplitude derivatives plus harmonic-0 and every non-anchor derivative residual, and prove the final derivative margins through the existing finite orthant / MC-032 machinery.

PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/05/08 remain OPEN. Protected source/audio/provenance, canonical journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics are unchanged. No native, paid, production or expensive campaign is authorized.
