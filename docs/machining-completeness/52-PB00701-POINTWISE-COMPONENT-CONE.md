# PB-007-01 v26 — exact pointwise component-cone/residual orthant certificate

## Contract

This bounded extension follows PB-007-01 v25 and preserves all v8–v25 authority. Historical classification runs first. v26 is considered only for exact residual multi-harmonic spans that remain blocked after v25.

The source remains

`F(s)=P(s)+sum_{h>=1}(C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s)))`,

with `s in [0,1]`, exact rational source polynomials and exact-rational affine phase `phi(s)=a+r*s`, `r != 0`.

## Fixed-sign source component

A v26 candidate harmonic has both `C_h(s)` and `S_h(s)` nonzero. One component is selected as dominant. Unlike v25, the dominant component does not need a Bernstein-derived amplitude floor. Its complete exact rational polynomial is proved strictly positive or strictly negative on closed `[0,1]` using MC-032 exact endpoint/Sturm strict-positivity authority.

This sign certificate is source-derived. Caller sign, floor, cone, Sturm or root metadata is not authority.

## Exact half-magnitude sectors

The exact v25 phase-sector theorem is retained unchanged.

For S-dominant authority, cosine must have one fixed sign and `|cos|>=1/2` over the complete harmonic phase interval. For C-dominant authority, sine must have one fixed sign and `|sin|>=1/2`. The transverse quadrature uses only the exact absolute bound `1`.

Exact rational-turn sector containment is required. Numerical trigonometry, sampled extrema and epsilon-expanded sectors are forbidden as correctness authority.

## Pointwise cone and residual orthants

The selected harmonic phase derivative is

`G_phase'=2*pi*h*r*(-C_h(s) sin(2*pi*h*phi)+S_h(s) cos(2*pi*h*phi))`.

For S-dominant authority with `d=sign(S_h)`, v26 constructs every polynomial

`M_sigma(s)=6*|h*r|*(d*S_h(s)/2-sigma_C*C_h(s))-sum_i sigma_i R_i(s)`

for `sigma_C,sigma_i in {-1,+1}`. `R_i` are the complete retained exact derivative-envelope polynomials. C-dominant authority is symmetric.

Every `M_sigma` must be strictly positive on closed `[0,1]` under MC-032 exact rational endpoint/Sturm authority. Since the finite sign choices realize `|T|` and `sum_i |R_i|` exactly, acceptance proves

`6*|h*r|*(|D(s)|/2-|T(s)|) > sum_i |R_i(s)|`

pointwise on the complete source span.

The selected phase sector fixes the dominant projection sign, and exact `pi > 3` gives `2*pi > 6`. Therefore the true mixed phase derivative has that fixed sign and strictly dominates every retained derivative channel. Exact equality in any orthant is fail-closed.

This construction terminates after finite `2^(1+N)` rational-polynomial positivity decisions. It does not use sign-cell root approximation, numerical minimization, sampling, arbitrary subdivision or a refinement cap.

## Residual authority

Only the selected anchor harmonic's two phase terms are consumed. Both anchor amplitude derivatives `C'_h` and `S'_h` remain residual. Harmonic-0 `P'` and all other derivative channels remain residual. Other phase terms use only the established exact rational theorem `2*pi < 44/7`.

Once complete derivative nonvanishing is established, existing rational-turn endpoint/root/multiplicity authority is reused unchanged. Every admitted root is simple. v25 and all earlier routes retain precedence.

Exact resource refusal is non-truth and propagates as refusal/`UNCERTIFIED`; it can never establish a pointwise margin or event result.

## Material broadening

v26 is intentionally broader than v25's separate global cone test. A source may have `dominant_floor/2 <= transverse_ceiling` under the old Bernstein/global sufficient bounds and still satisfy every exact pointwise cone/residual orthant margin. The acceptance suite includes such a genuine multi-harmonic source.

The dominant sign proof is also independent of a strict Bernstein-floor certificate: exact Sturm positivity may prove a source polynomial strictly positive even when a Bernstein coefficient reaches the old sufficient-certificate boundary.

## Caller metadata and protected semantics

Caller-supplied pointwise cones, dominant signs, global floors/ceilings, orthant margins, phase sectors, derivative bounds, Sturm certificates and root counts are discarded before source analysis. Binary floats are not exact source authority.

PB-007-01 remains OPEN. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/05/08 remain OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`. The frozen denominator remains 26 operations.

Protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged. No native, paid, production, or expensive campaign is authorized.

## Remaining theorem boundary

v26 does not solve general coupled analytic zero isolation. It remains blocked when there is no usable fixed-sign component, when the harmonic phase interval lies outside every existing exact single-quadrature half-magnitude sector, when the exact pointwise orthant margins fail, or in broader coupled analytic cases outside the qualified source grammar.

The next PB-007-01 repair should seek a materially broader exact phase-projection/event theorem. If that requires genuinely new transcendental minimization or zero-isolation authority, the theorem boundary must be recorded precisely rather than approximated.
