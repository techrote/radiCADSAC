# PB-007-01 v25 — exact mixed-projection component-cone phase anchor

Issue: #212  
Parent integration gate: MC-038 / #100  
Source baseline: `130d8ce5ee9c3d816dc908df4d1eb044f0396a88`

## Result

A bounded exact PB-007-01 route is established for residual multi-harmonic sources that remain blocked after v24 and contain both source-owned cosine and sine modulation at one positive harmonic. The new route materially broadens v24: it does not require both amplitude components to have fixed sign, and it does not require a dual-half-magnitude phase sector. One component may change sign, while the harmonic phase may traverse an exact single-quadrature half-magnitude sector up to `1/3` turn wide.

This is a constructive extension, not a general coupled-analytic theorem. PB-007-01 remains OPEN, PB-007-02 remains dependent, PB-007-03 remains OPEN, PB-007-04 remains `OPEN_PROPAGATED`, PO-04/05/08 remain OPEN, MC-B remains `NOT_ESTABLISHED`, and MC-1 remains `NOT_ESTABLISHED`.

## Source-owned component cone

For one candidate harmonic `h`, the source contribution is

`C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s))`,

with exact rational source polynomials and exact affine phase `phi(s)=a+r*s`, `r!=0`.

The phase derivative is

`G_phase' = 2*pi*h*r*(-C_h(s) sin(2*pi*h*phi) + S_h(s) cos(2*pi*h*phi))`.

v25 tries two symmetric exact component-cone certificates.

For an **S-dominant** certificate, `S_h` must have one exact fixed sign and a strict rational floor `S_floor>0`, derived either from a nonzero constant or from exact Bernstein convex-hull authority. The complete transverse `C_h` polynomial is converted exactly to Bernstein form, and `C_ceiling=max_i |b_i|` supplies a rigorous absolute upper bound on closed `[0,1]`; `C_h` may change sign and may cross zero. The harmonic phase must lie wholly in a rational sector where cosine has fixed sign and `|cos|>=1/2`. Sine is used only through the exact universal bound `|sin|<=1`. The strict source-derived cone separation is

`S_floor/2 > C_ceiling`.

For a **C-dominant** certificate the construction is symmetric: `C_floor>0`, exact `S_ceiling`, a fixed-sign `|sin|>=1/2` sector, and strict `C_floor/2 > S_ceiling`.

The half-magnitude sectors are exact rational-turn families. Cosine uses integer translates of `[-1/6,1/6]` for positive sign and `[1/3,2/3]` for negative sign. Sine uses integer translates of `[1/12,5/12]` for positive sign and `[7/12,11/12]` for negative sign. Endpoint equality is exact. Numerical trigonometry is never authority.

## Exact mixed-projection lower bound

Let

`gap = dominant_floor/2 - transverse_ceiling > 0`.

On the certified sector, the dominant projection term has the proved source/phase sign and magnitude at least `dominant_floor/2`; the transverse term has magnitude at most `transverse_ceiling`. Therefore the complete mixed projection cannot cross the phase-orthogonal zero-projection direction and has magnitude strictly greater than `gap` with an exact sign.

Using exact `pi > 3`,

`|G_phase'| > 2*pi*|h*r|*gap > 6*|h*r|*gap = L_anchor`.

The certificate derives the component signs, Bernstein floor/ceiling, phase sector, cone gap, projection sign and `L_anchor` from source data. Caller-supplied component-cone, floor, ceiling, Bernstein, sector, sign, derivative-bound, L1, Sturm or root metadata is discarded as non-authoritative.

## Residual derivative and exact decision

The anchor consumes only the two phase-derivative terms at the selected harmonic. Both amplitude derivatives `C'_h cos(...)` and `S'_h sin(...)` remain residual, along with `P'` and every other harmonic derivative channel. Remaining phase terms use only the established exact rational theorem `2*pi < 44/7`.

Residual dominance reuses the v21-v24 finite sign-orthant identity

`sum_i |f_i(s)| = max_{sigma in {-1,+1}^N} sum_i sigma_i f_i(s)`.

Every directed margin `L_anchor - sum_i sigma_i f_i(s)` must be strictly positive on closed `[0,1]` under MC-032 exact rational endpoint/Sturm authority. Equality is not accepted. Resource refusal is not a truth value.

Once complete derivative nonvanishing is established, the existing exact rational-turn endpoint authority decides zero/open/endpoint root outcomes and the unchanged root-summary contract proves every admitted root simple. v8-v24 routes run first and retain precedence; v25 consumes only their residual blocked spans.

## Adversarial boundary coverage

The v25 suite includes a genuine multi-harmonic source blocked by v24 whose transverse component changes sign and whose phase interval crosses v24's dual-quadrature sectors; v25 certifies it through an S-dominant cone. A symmetric C-dominant wider-sector case is also covered. Controls include positive and negative derivative directions, constant/nonconstant dominant amplitudes, exact Bernstein absolute ceilings for sign-changing transverse amplitudes, exact phase-sector endpoints and signed `1/1000000` neighbours, exact cone-separation equality and signed neighbours, dominant-floor failure, residual-L1 equality and signed neighbours, zero/open/left-endpoint/right-endpoint root outcomes, v24 prior-route ownership, source-parameter mismatch, forged certificate metadata, binary-float rejection and exact resource refusal propagation.

Historical v24 artifacts are SHA-pinned. The frozen 26-operation denominator is unchanged. The verifier rejects false MC-B promotion and any mutation of protected source/audio/provenance semantics.

## Authority boundaries

The following are forbidden as correctness authority: caller component-cone assertions, binary float, epsilon/tolerance, finite sampling, numerical trigonometry, approximate minimization, approximate algebraic-root ordering, arbitrary subdivision/refinement depth, timeout, or resource exhaustion/refusal. Exact resource refusal propagates as refusal/`UNCERTIFIED`, never as a mathematical result.

This package does not authorize native, paid, production or expensive execution. Canonical journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder access, durable body/lineage and conventional STEP semantics are unchanged.

## Residual frontier

PB-007-01 remains OPEN beyond v8-v25. The remaining branch includes source amplitude cones that cannot be kept uniformly separated from the phase-orthogonal zero-projection direction by either single-quadrature half-magnitude sector, phase intervals crossing every such sector, and broader irreducible coupled analytic events. The next repair should seek a terminating exact residual-event construction materially beyond a single dominant component cone. If that requires a genuinely new transcendental zero/minimization theorem, record the theorem boundary precisely rather than substituting approximation or retrying MC-B prematurely.
