# PB-007-01 v20 — exact pointwise polynomial derivative envelope

Issue: #202  
Parent integration gate: MC-038 / #100  
Source baseline: `ac3d034633f9f50d216b0afdec4958a8ed005d40`  
Disposition: **bounded exact derivative-envelope route added; PB-007-01 remains OPEN**  
Native/paid execution: **none**

## Result

v20 attacks a specific conservatism left by v19. v19 independently takes a whole-span Bernstein absolute supremum for each oscillatory derivative term and sums those suprema. That is sound but can fail when different terms attain their maxima at different source locations. v20 preserves v8–v19 precedence and is considered only when v19 reaches `MONOTONE_ANCHOR_DERIVATIVE_DOMINANCE_NOT_CERTIFIED` on an otherwise eligible exact residual span.

For

`F(s)=P(s)+sum_h(C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s)))`,

with exact rational source polynomials, exact-rational affine phase rate `r != 0`, and at least two active positive harmonics, v20 derives the exact pointwise envelope terms

`C'_h`, `S'_h`, `(44/7)|h*r| C_h`, `(44/7)|h*r| S_h`.

Only exact-zero terms are omitted. The theorem `pi < 22/7` is the sole transcendental inequality used on the derivative bound.

## Exact pointwise dominance certificate

Let the nonzero envelope polynomials be `f_1,...,f_N`. The complete oscillatory derivative magnitude is bounded pointwise by

`sum_i |f_i(s)|`.

Cauchy–Schwarz gives the exact algebraic inequality

`sum_i |f_i(s)| <= sqrt(N * sum_i f_i(s)^2)`.

v20 constructs the rational polynomial

`Q(s)=P'(s)^2 - N * sum_i f_i(s)^2`.

It then proves, using existing MC-032 exact rational polynomial/Sturm authority, both that `P'` has one fixed strict sign on the complete closed source span and that `Q>0` on the complete closed source span. Each proof uses exact endpoint relations plus a zero count on the open interval. An endpoint zero, an interior root, or equality `Q=0` fails closed.

Those two certificates imply

`sum_i |f_i(s)| < |P'(s)|`

for every source point. Therefore the complete event derivative has the sign of `P'` and never vanishes. This is a finite terminating route: it requires a fixed finite number of rational-polynomial constructions and exact Sturm decisions, not recursive subdivision. No arbitrary subdivision depth, timeout, sampling, epsilon, or resource exhaustion is correctness authority.

## New constructive coverage

The acceptance fixture uses three positive-harmonic polynomial modulations whose source derivatives are proportional to `8(1-s)^2`, `16s(1-s)`, and `8s^2`. Their independent whole-span derivative suprema already sum to `20`, so v19 cannot establish dominance over the anchor derivative `199/10` even before adding phase terms. The v20 pointwise `Q` polynomial is nevertheless strictly positive over `[0,1]`, which MC-032 Sturm authority proves exactly. The same source is then decided directly, without factor removal or numerical zero search.

Both increasing and decreasing directions are covered, together with zero-root, one-open-root and exact endpoint-root outcomes. The exact `Q=0` threshold is rejected, and exact `±1/1000000` rational neighbours discriminate the strict boundary.

## Endpoint and multiplicity authority

Once strict derivative sign is established, v20 reuses v19's exact endpoint machinery unchanged. Rational turns are classified through the v6 algebraic tangent-half route. A tangent-coordinate half-turn pole is handled by the exact identity-preserving half-turn shift and `(-1)^h` parity, never by epsilon displacement.

Strict monotonicity plus exact endpoint relations yields zero or one open root and any endpoint event. Since `Q>0` and the anchor derivative has fixed strict sign, the complete derivative is nonzero everywhere on the closed span; every admitted open or endpoint root is therefore simple.

## Adversarial boundary

The suite rejects anchor-derivative sign changes and zeros, endpoint/interior failures of `Q>0`, missing anchors, single-positive-harmonic inputs, zero phase rate, source-parameter mismatch, binary-float source authority, forged envelope/Q/Sturm/sign/root metadata, resource-refusal laundering, historical-v19 mutation, frozen-denominator shrinkage and false MC-B promotion. A prior v19-certified source remains v19-owned.

Neither binary floating point, numerical trigonometry, epsilon, sampling, approximate minimization, arbitrary subdivision limits, timeout nor resource exhaustion is a truth source. Resource refusal remains a non-truth terminal status.

## Programme effect

**PB-007-01 remains OPEN.** v20 is a materially broader terminating exact subroute, not a universal decision procedure for all residual coupled exponential-polynomial event predicates. Sources without a fixed-sign anchor derivative, or for which the exact pointwise envelope polynomial is not strictly positive, remain explicit blockers.

PB-007-02 remains dependent on PB-007-01; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04, PO-05 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`. No MC-B retry is justified solely by v20.

The frozen 26-operation denominator is unchanged. Protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain binding.

## Next repair boundary

The surviving PB-007-01 frontier is the irreducible coupled multi-harmonic branch beyond v8–v20, especially sources lacking a fixed-sign phase-independent anchor derivative or failing the exact pointwise polynomial envelope. Further work must provide another genuinely broader exact terminating construction or record the precise theorem boundary. Sampling, tolerance, timeout and domain narrowing remain forbidden substitutes.
