# PB-007-01 v24 — exact mixed-quadrature phase anchor

Issue: #210  
Parent integration gate: MC-038 / #100  
Source baseline: `2fedcc3ac66a08b82df41a3a68ad2425bf77f8a5`

## Result

A bounded new PB-007-01 route is established for residual multi-harmonic sources that remain blocked after v23 and have **both source-owned cosine and sine modulation active at one positive harmonic**. This is a constructive extension, not a general coupled-analytic theorem: PB-007-01 remains OPEN, MC-B remains `NOT_ESTABLISHED`, and MC-1 remains `NOT_ESTABLISHED`.

For one candidate harmonic `h`, the source contribution is

`C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s))`,

with exact rational source polynomials and exact affine phase `phi(s)=a+r*s`, `r!=0`. v24 independently derives fixed sign and strict rational nonzero floors for `C_h` and `S_h`. Nonconstant components use exact power-to-Bernstein conversion on closed `[0,1]`; every Bernstein coefficient must have one strict sign, giving `C_floor` or `S_floor` by the Bernstein convex-hull property. A nonzero constant component uses its exact rational absolute value directly. Component zeros or sign ambiguity fail closed.

## Exact mixed phase sector and projection

The harmonic phase must lie wholly in one exact rational closed sector where **both** `sin(2*pi*h*phi)` and `cos(2*pi*h*phi)` have fixed signs and magnitude at least `1/2`. The four sector families per turn are `[1/12,1/6]`, `[1/3,5/12]`, `[7/12,2/3]`, and `[5/6,11/12]`, translated by integers. No numerical trigonometry is used.

The phase derivative of the mixed anchor is

`G_phase' = 2*pi*h*r*(-C_h(s) sin(2*pi*h*phi) + S_h(s) cos(2*pi*h*phi))`.

v24 accepts only when the exact source-component signs and exact sector quadrature signs make `-C_h sin(...)` and `S_h cos(...)` point in the same direction everywhere. Then

`|-C_h sin + S_h cos| >= (C_floor + S_floor)/2`,

so exact `pi > 3` yields the strict rational lower bound

`L_anchor = 3*|h*r|*(C_floor+S_floor) < |G_phase'|`.

This lower bound is source-derived. A caller-supplied phase anchor, component floor, Bernstein certificate, sector, derivative lower bound, root count, Sturm certificate, or event decision is never truth authority.

## Residual derivative authority

Both amplitude derivatives remain explicit residual terms: `C'_h cos(...)` and `S'_h sin(...)` are not hidden inside the anchor certificate. Harmonic-0 `P'`, every other amplitude derivative, and every other harmonic phase derivative also remain residual. The only trigonometric upper theorem used for residual phase envelopes is the established exact rational `2*pi < 44/7`.

The residual is discharged through the existing finite L1 sign-orthant identity

`sum_i |f_i(s)| = max_{sigma in {-1,+1}^N} sum_i sigma_i f_i(s)`.

Every exact polynomial margin `L_anchor - sum_i sigma_i f_i(s)` must be strictly positive on closed `[0,1]` under MC-032 exact endpoint/Sturm authority. Equality fails closed. This proves the complete source derivative has one strict nonzero sign. Established exact rational-turn/tangent-half endpoint authority then gives zero/one open-root and endpoint-root decisions, with every admitted root simple.

## Adversarial boundary

The v24 suite includes a genuinely v23-blocked mixed-quadrature source; increasing and decreasing complete derivatives; multiple quadrant/component sign patterns; nonconstant/nonconstant and constant/nonconstant component pairs; exact dual-half-magnitude sector boundaries and signed `1/1000000` neighbours; zero Bernstein floors and signed neighbours for each component; deliberately misaligned projection signs; exact residual L1 equality and signed neighbours; zero/open/left-endpoint/right-endpoint roots; v23 prior-route precedence; source-parameter mismatch; forged caller certificates; binary-float authority; and exact resource refusal propagation.

Historical v23 evidence is hash-pinned. The frozen 26-operation denominator is unchanged. Protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics are unchanged. No native, paid, production, or expensive campaign is authorized or run.

## Remaining blocker

PB-007-01 remains open beyond v8-v24. v24 still requires a fixed dual-half-magnitude phase sector and independently fixed-sign nonzero `C_h`/`S_h` components whose mixed projection terms align. Sources whose mixed projection crosses a quadrature boundary, whose component vector crosses an axis, or whose projection remains nonzero only by subtler cancellation/geometry still lack a terminating exact decision route here. PB-007-02 remains dependent on PB-007-01; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/PO-05/PO-08 remain OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`.

The next pre-gate priority is a materially broader exact mixed-projection certificate—such as a source-derived projective/component-cone construction over a wider phase interval—or another terminating exact residual event route. If existing rational/algebraic authority cannot prove the needed nonzero uniform projection without a new transcendental minimization/zero theorem, that theorem boundary must be recorded rather than replaced with sampling, epsilon, tolerance, arbitrary subdivision, timeout, or resource limits.
