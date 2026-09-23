# PB-007-01 v23 — exact nonconstant-amplitude phase-sector anchor

## Contract

This bounded extension follows PB-007-01 v22 and preserves all v8–v22 authority. Historical classification runs first. v23 is considered only for exact residual multi-harmonic spans that remain blocked after v22.

The source remains

`F(s)=P(s)+sum_{h>=1}(C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s)))`,

with `s in [0,1]`, exact rational source polynomials and exact-rational affine phase `phi(s)=a+r*s`, `r != 0`.

## Nonconstant source-owned anchor

A v23 anchor is a pure quadrature at one positive harmonic: either `G(s)=A(s) sin(2*pi*h*phi(s))` with exactly zero cosine complement, or `G(s)=A(s) cos(2*pi*h*phi(s))` with exactly zero sine complement. `A(s)` must be genuinely nonconstant. Constant amplitude remains v22-owned; mixed quadrature remains outside this route.

The harmonic phase must lie wholly in the same exact rational half-magnitude sector used by v22, where the derivative quadrature has fixed sign and magnitude at least `1/2`. No numerical trigonometry is used.

## Exact Bernstein amplitude floor

v23 converts `A(s)` exactly from power coefficients to Bernstein coefficients on closed `[0,1]`. It accepts only if every exact Bernstein coefficient has one strict sign. With

`A_floor = min_i |b_i| > 0`,

the Bernstein convex-hull property proves that `A(s)` has that sign and `|A(s)| >= A_floor` everywhere. A zero Bernstein coefficient or mixed Bernstein signs fail closed. This certificate is intentionally sufficient rather than complete; v23 does not replace it with sampling or approximate minimization.

The sector theorem and exact `pi > 3` then give the strict rational phase-derivative lower bound

`L_anchor = 3*|h*r|*A_floor < |G_phase'(s)|`.

## Residual exact L1 dominance

The nonconstant amplitude derivative is not discarded. For a SIN anchor, `A'(s) sin(...)` remains residual; for a COS anchor, `A'(s) cos(...)` remains residual. `P'` and every other source derivative contribution also remain residual. Phase terms are bounded only by the existing exact rational inequality `2*pi < 44/7`.

As in v21/v22, the exact residual envelope polynomials `f_i` satisfy

`sum_i |f_i(s)| = max_{sigma in {-1,+1}^N} sum_i sigma_i f_i(s)`.

Every finite exact margin

`M_sigma(s)=L_anchor-sum_i sigma_i f_i(s)`

must be strictly positive on closed `[0,1]` under existing MC-032 exact endpoint/Sturm authority. Equality fails closed. Therefore `sum|R_i'| < L_anchor < |G_phase'|`, so the complete source derivative has the anchor direction and never vanishes.

## Endpoints, multiplicity and termination

After strict monotonicity is established, v23 reuses the exact rational-turn endpoint authority of v19–v22. Tangent-half poles use exact half-turn shifting and `(-1)^h` parity, never epsilon displacement. Endpoint signs give zero/one open-root and endpoint-root decisions, and every admitted root is simple.

A finite source has finitely many pure nonconstant candidate anchors. Each candidate requires one exact Bernstein conversion, one rational sector check and finitely many `2^N` rational-polynomial Sturm decisions. No recursive refinement, tolerance, timeout or resource cap becomes truth authority. Exact resource failure remains `RESOURCE_REFUSAL`.

## Adversarial boundary

Coverage includes a genuinely multi-harmonic source blocked by v22 but certified by v23; increasing/decreasing directions; SIN/COS anchors; exact phase-sector equality and signed `±1/1000000` neighbours; zero Bernstein coefficient and signed neighbours; a pointwise-positive amplitude whose Bernstein coefficients are mixed and therefore fail closed; exact residual-L1 equality and signed neighbours; zero/open/left-endpoint/right-endpoint roots; constant-amplitude v22 precedence; non-pure quadrature rejection; source-parameter mismatch; forged amplitude/Bernstein/sector/L1/Sturm/root metadata; binary floats; resource refusal; historical-v22 preservation; frozen 26-operation coverage; and false MC-B promotion.

## Programme state

PB-007-01 **remains OPEN** outside the admitted nonconstant-amplitude phase-sector family. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/PO-05/PO-08 remain OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`.

The frozen 26-operation denominator and all protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged. No native, paid, production or expensive campaign is authorized.
