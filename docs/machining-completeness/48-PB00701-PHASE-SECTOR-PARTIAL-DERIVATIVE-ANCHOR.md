# PB-007-01 v22 — exact phase-sector partial derivative anchor

## Contract

This bounded extension follows PB-007-01 v21 and preserves all v8–v21 authority. Historical classification runs first. v22 is considered only for an exact residual multi-harmonic span that remains blocked after v21.

The source still has the exact local form

`F(s)=P(s)+sum_{h>=1}(C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s)))`,

with `s in [0,1]`, exact rational polynomial source channels and exact-rational affine `phi(s)=a+r*s`, `r != 0`. No source factor, harmonic, phase relation, source/audio/provenance identity, or operation is discarded.

Unlike v19–v21, v22 does **not** require `P'` to have a fixed sign. `P'` may be zero or sign-changing and is then retained as part of the exact residual derivative envelope.

## Source-owned phase-dependent anchor

v22 searches only source-derived positive harmonics. A candidate anchor must have one exactly constant, nonzero quadrature and an exactly zero complementary quadrature. Thus the admitted partial event is either

`G(s)=B sin(2*pi*h*phi(s))`

or

`G(s)=C cos(2*pi*h*phi(s))`,

with exact rational constant `B` or `C`. Nonconstant amplitude and a nonzero complementary quadrature fail closed.

The harmonic phase `t=h*phi(s)` is affine and has exact rational endpoints. For a SIN anchor, v22 accepts only closed rational sectors on which `|cos(2*pi*t)| >= 1/2` with fixed sign. For a COS anchor it accepts only sectors on which `|sin(2*pi*t)| >= 1/2` with fixed sign. The sector endpoints are rational turns such as `n±1/6`, `n+1/3`, `n+2/3`, `n+1/12`, `n+5/12`, `n+7/12`, and `n+11/12`.

No numerical trigonometry is used. The exact sector theorem and `pi > 3` give

`|G'(s)| >= pi*|amplitude*h*r| > 3*|amplitude*h*r|`.

The strict rational lower bound

`L_anchor = 3*|amplitude*h*r|`

is therefore source-derived and valid on the complete closed span. The lower-complexity constant-amplitude single-harmonic partial event is already inside the established v10/v11/v12-or-later exact event family, but those historical event certificates are **not** treated as if they supplied a uniform derivative magnitude. v22 derives that lower bound independently and explicitly.

## Residual exact L1 dominance

Every derivative contribution except the certified anchor phase derivative remains residual. This includes `P'(s)` even if it changes sign, every non-anchor `C'_h` and `S'_h`, and every non-anchor phase derivative bounded with the rigorous rational upper inequality `2*pi < 44/7`.

As in v21, the nonzero exact residual envelope polynomials are `f_1,...,f_N` and

`sum_i |f_i(s)| = max_{sigma in {-1,+1}^N} sum_i sigma_i f_i(s)`.

v22 constructs all finite residual margin polynomials

`M_sigma(s)=L_anchor-sum_i sigma_i f_i(s)`

and requires every one to be strictly positive on closed `[0,1]` using existing MC-032 exact rational endpoint and Sturm authority. Exact equality, an endpoint zero, or an interior zero fails closed. This proves

`sum_i |f_i(s)| < L_anchor < |G'(s)|`

throughout the span, so the complete derivative has the anchor sign everywhere.

## Endpoint and multiplicity authority

After strict derivative sign is established, v22 reuses v19–v21 endpoint and root semantics unchanged. Exact rational-turn endpoint values are decided through the established v6 algebraic tangent-half authority. A tangent-half coordinate pole is handled by exact half-turn shifting and `(-1)^h` parity, never by epsilon displacement.

Exact endpoint signs plus strict monotonicity yield zero or one open root and exact endpoint-root decisions. Because the complete derivative is nonzero over the complete closed span, every admitted root has multiplicity one.

## Termination and refusal

For a finite source there are finitely many constant-amplitude pure-quadrature anchor candidates. Each candidate requires only a finite rational phase-sector check and, if admitted, `2^N` exact rational-polynomial residual margin decisions. There is no recursive refinement or convergence criterion.

Timeout, memory exhaustion, arithmetic refusal, or another exact-resource failure is a non-truth `RESOURCE_REFUSAL`; it is never certification or rejection authority.

## Adversarial boundary

The acceptance source is genuinely multi-harmonic and remains blocked by v21 because its harmonic-0 derivative changes sign. v22 certifies it with a source-owned SIN anchor while retaining the sign-changing `P'` as residual.

Tests cover positive and negative derivative sectors, SIN and COS anchor quadratures, exact phase-sector boundary equality and signed `±1/1000000` neighbours, exact residual-L1 equality and signed neighbours, zero/open/endpoint-root outcomes, nonconstant anchor amplitude, nonzero complementary quadrature, v21 precedence, source-parameter mismatch, forged anchor/sector/lower-bound/L1/Sturm/root metadata, binary floats, resource refusal, historical-v21 drift, frozen-denominator shrinkage, and false MC-B promotion.

## Programme state

PB-007-01 **remains OPEN** outside the admitted phase-sector partial-anchor family. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/PO-05/PO-08 remain OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`.

The frozen 26-operation denominator and all protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged. No native, paid, production, or expensive campaign is authorized by this result.
