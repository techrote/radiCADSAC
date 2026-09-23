# PB-007-01 v25 — exact mixed-projection component-cone phase anchor

## Contract

This bounded extension follows PB-007-01 v24 and preserves all v8–v24 authority. Historical classification runs first. v25 is considered only for exact residual multi-harmonic spans that remain blocked after v24.

The source remains

`F(s)=P(s)+sum_{h>=1}(C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s)))`,

with `s in [0,1]`, exact rational source polynomials and exact-rational affine phase `phi(s)=a+r*s`, `r != 0`.

## Source-owned projective component cone

A v25 candidate harmonic has both `C_h(s)` and `S_h(s)` nonzero. Unlike v24, both components need not have a fixed sign. One **dominant** component must have a source-derived fixed sign and strict rational floor; the transverse component needs only an exact source-derived absolute ceiling.

A nonzero constant dominant component supplies its exact absolute value. A nonconstant dominant component is converted exactly to Bernstein form on closed `[0,1]`; all Bernstein coefficients must have one strict sign, and the floor is their minimum absolute value. For the transverse component, exact Bernstein conversion gives `ceiling=max_i |b_i|`. Since Bernstein basis functions are nonnegative and sum to one, this bounds the complete absolute value even if the transverse component changes sign or crosses zero. No sampled extremum or numerical minimization is used.

## Exact wider half-magnitude sectors

v25 requires only one quadrature to have fixed sign and magnitude at least `1/2`; the other quadrature uses its exact universal absolute bound `1`.

For an S-dominant anchor, cosine supplies the half-magnitude sector. Exact rational-turn sector families are integer translates of `[-1/6,1/6]` with positive cosine and `[1/3,2/3]` with negative cosine.

For a C-dominant anchor, sine supplies the half-magnitude sector. Exact rational-turn sector families are integer translates of `[1/12,5/12]` with positive sine and `[7/12,11/12]` with negative sine.

These sectors can be as wide as `1/3` turn and therefore materially exceed v24's dual-half-magnitude sectors. Exact endpoint equality is admitted. Any positive rational excursion outside a qualifying sector is not. Numerical trigonometry is forbidden as authority.

## Exact mixed-projection separation

The phase derivative at the candidate harmonic is

`G_phase'=2*pi*h*r*(-C_h(s) sin(2*pi*h*phi)+S_h(s) cos(2*pi*h*phi))`.

For S-dominant authority require

`S_floor/2 > C_ceiling`.

For C-dominant authority require

`C_floor/2 > S_ceiling`.

In either case define

`gap = dominant_floor/2 - transverse_ceiling > 0`.

The dominant projection term has exact sign and magnitude at least `dominant_floor/2`; the transverse projection term has magnitude at most `transverse_ceiling`. Hence the source amplitude cone stays uniformly separated from the phase-orthogonal zero-projection direction, the projection sign is exact, and its magnitude is strictly greater than `gap`.

Using exact `pi > 3`,

`|G_phase'| > 2*pi*|h*r|*gap > 6*|h*r|*gap = L_anchor`.

Equality in the cone separation is fail-closed.

## Residual authority

Only the two phase terms at the selected anchor harmonic are consumed by the component-cone proof. Both amplitude derivatives `C'_h cos(...)` and `S'_h sin(...)` remain residual. Harmonic-0 `P'` and all other derivative channels remain residual. Other phase terms use the exact rational upper theorem `2*pi < 44/7`.

The residual must satisfy the unchanged finite sign-orthant L1 identity

`sum_i |f_i(s)| = max_{sigma in {-1,+1}^N} sum_i sigma_i f_i(s)`.

Every exact margin against `L_anchor` must be strictly positive on closed `[0,1]` under MC-032 exact endpoint/Sturm authority. Resource refusal is non-truth. No epsilon, sampling, approximate root ordering or arbitrary subdivision depth is permitted.

With complete derivative nonvanishing established, existing rational-turn endpoint/root/multiplicity authority is reused unchanged. Admitted roots are simple. v24 and all earlier routes retain precedence.

## Caller metadata and protected semantics

Caller-supplied component cones, dominant/transverse labels, Bernstein floors or ceilings, phase sectors, projection signs, derivative lower bounds, residual L1 certificates, Sturm certificates and root counts are non-authoritative and are discarded before source analysis. Binary floats are not exact source authority.

PB-007-01 remains OPEN. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/05/08 remain OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`. The frozen denominator remains 26 operations.

Protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged. No native, paid, production, or expensive campaign is authorized.

## Remaining theorem boundary

v25 does not solve general coupled analytic zero isolation. It remains blocked when neither component yields a strict projective cone margin on a qualifying half-magnitude sector, when the phase interval crosses all exact sectors, or when residual dominance is not exact. The next PB-007-01 repair should seek a terminating exact residual-event authority beyond a single dominant component cone. If that needs a new transcendental zero or minimization theorem, the theorem boundary must be recorded rather than approximated.
