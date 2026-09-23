# PB-007-01 v24 — exact mixed-quadrature phase anchor

## Contract

This bounded extension follows PB-007-01 v23 and preserves all v8–v23 authority. Historical classification runs first. v24 is considered only for exact residual multi-harmonic spans that remain blocked after v23.

The source remains

`F(s)=P(s)+sum_{h>=1}(C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s)))`,

with `s in [0,1]`, exact rational source polynomials and exact-rational affine phase `phi(s)=a+r*s`, `r != 0`.

## Source-owned mixed anchor

A v24 candidate harmonic has both `C_h(s)` and `S_h(s)` nonzero. Pure SIN/COS anchors remain owned by v22/v23. Each mixed component must have a source-derived fixed sign and strict rational amplitude floor. A nonzero constant component supplies its exact absolute value. A nonconstant component is converted exactly to Bernstein form on closed `[0,1]`; all Bernstein coefficients must have one strict sign, and the floor is their minimum absolute value. Zero or sign ambiguity fails closed.

The harmonic phase must lie wholly in one rational **dual-half-magnitude sector** where both `sin(2*pi*h*phi)` and `cos(2*pi*h*phi)` have fixed signs and magnitude at least `1/2`. The exact sector families per turn are `[1/12,1/6]`, `[1/3,5/12]`, `[7/12,2/3]`, and `[5/6,11/12]`, plus integer translates. Sector equality is admitted exactly; leaving the sector by any positive rational amount is not.

## Exact projection lower bound

The phase-only derivative contribution is

`G_phase'=2*pi*h*r*(-C_h sin(2*pi*h*phi)+S_h cos(2*pi*h*phi))`.

The component signs and sector quadrature signs must prove that `-C_h sin(...)` and `S_h cos(...)` have the same sign everywhere. Under that alignment,

`|-C_h sin + S_h cos| >= (C_floor+S_floor)/2`.

The exact theorem `pi > 3` therefore gives

`L_anchor=3*|h*r|*(C_floor+S_floor) < |G_phase'|`.

No numerical trigonometry, approximate angle, caller vector normalization, sampling, epsilon, tolerance, or minimization participates.

## Residual L1 / Sturm authority

Both anchor amplitude derivatives remain residual: `C'_h cos(...)` and `S'_h sin(...)`. `P'` and all other derivative channels remain residual. Remaining phase terms use only the established exact rational `2*pi < 44/7` envelope.

For residual envelope polynomials `f_i`, v24 reuses the exact finite identity

`sum_i |f_i(s)| = max_{sigma in {-1,+1}^N} sum_i sigma_i f_i(s)`.

Every polynomial margin `L_anchor-sum_i sigma_i f_i(s)` must be strictly positive on closed `[0,1]` under MC-032 exact rational endpoint/Sturm authority. Exact equality blocks certification. Finite `2^N` orthant enumeration is a proof construction, not an arbitrary refinement cap.

Once the complete derivative is proved strictly nonzero, established exact rational-turn/tangent-half endpoint authority decides the root count and endpoint relations. Every admitted root is simple.

## Fail-closed boundary

v24 fails closed for a zero or sign-ambiguous component, a phase interval not wholly inside one dual-half-magnitude sector, misaligned mixed projection terms, a non-strict residual margin, malformed or mismatched source coordinates, exact-resource refusal, or any case that requires new transcendental zero/minimization authority.

Caller-supplied mixed-anchor, component-floor, Bernstein, sector, residual-L1, Sturm, derivative, root, or event certificates are discarded. Binary float, epsilon, sampling, numerical trigonometry, approximate minimization/root ordering, arbitrary subdivision, timeout, and resource refusal are forbidden as truth authority.

## Programme state

PB-007-01 remains OPEN beyond the bounded v8–v24 families. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/PO-05/PO-08 remain OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`.

The frozen 26-operation denominator and all protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume, cutter/holder, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged. No native, paid, production, or expensive execution is authorized.
