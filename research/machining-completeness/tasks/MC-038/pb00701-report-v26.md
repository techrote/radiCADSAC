# PB-007-01 v26 — exact pointwise component-cone/residual orthant certificate

Issue: #214  
Parent integration gate: MC-038 / #100  
Source baseline: `f668790f648eb9a6815d30fbacf982765cd3bed3`

## Result

A bounded exact PB-007-01 route is established for residual multi-harmonic sources that remain blocked after v25 because v25's separately computed dominant-component floor and transverse-component Bernstein ceiling overlap, even though the source-derived mixed projection remains pointwise separated from zero and dominates every retained derivative channel.

v26 removes that separate-global-bound conservatism. It does not solve general coupled analytic zero isolation. PB-007-01 remains OPEN; PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/05/08 remain OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`.

## Exact dominant sign and phase sector

The source remains

`F(s)=P(s)+sum_{h>=1}(C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s)))`,

on closed `s in [0,1]`, with exact rational source polynomials and affine exact-rational phase `phi(s)=a+r*s`, `r!=0`.

After v8-v25 authority remains blocked, v26 considers a mixed positive harmonic with both `C_h` and `S_h` active. For an S-dominant attempt, the complete source polynomial `S_h(s)` must have one strict sign on closed `[0,1]`. Unlike v25, v26 does not require a Bernstein-derived nonzero floor. It proves `S_h>0` or `-S_h>0` directly using MC-032 exact rational endpoint/Sturm strict-positivity authority. The C-dominant route is symmetric.

The phase-sector theorem is intentionally unchanged from v25. S-dominant authority requires an exact rational-turn cosine sector with fixed sign and `|cos|>=1/2`; C-dominant authority uses the corresponding sine sector. The transverse quadrature uses only the exact universal bound `1`. The accepted sectors are exact rational containment statements, not sampled trigonometry.

## Pointwise cone plus residual certificate

For the selected harmonic,

`G_phase' = 2*pi*h*r*(-C_h(s) sin(2*pi*h*phi) + S_h(s) cos(2*pi*h*phi))`.

Suppose S is dominant and has proved sign `d=sign(S)`. On the exact cosine half-magnitude sector, the dominant projection has fixed sign and magnitude at least `|S|/2`, while the transverse projection has magnitude at most `|C|`.

v26 does **not** replace these functions by a global `S_floor` and `C_ceiling`. Instead it retains them as exact rational polynomials and combines the cone inequality with the complete derivative residual. Let `R_i(s)` be the same exact residual envelope polynomials used by v24-v25: both anchor amplitude derivatives `C'_h`, `S'_h`, harmonic-0 `P'`, and all other derivative channels, with remaining phase terms bounded only by exact `2*pi<44/7`.

For every finite sign choice `sigma_C,sigma_i in {-1,+1}`, v26 constructs

`M_sigma(s)=6*|h*r|*(d*S_h(s)/2 - sigma_C*C_h(s)) - sum_i sigma_i R_i(s)`

and requires `M_sigma(s)>0` on the complete closed span under MC-032 exact rational endpoint/Sturm authority. C-dominant authority uses the symmetric polynomial family.

Finite sign enumeration is exact because

`max_{sigma_C} sigma_C*C = |C|`

and

`max_{sigma_i} sum_i sigma_i R_i = sum_i |R_i|`.

Therefore every accepted source satisfies pointwise

`6*|h*r|*(|D(s)|/2-|T(s)|) > sum_i |R_i(s)|`.

The selected half-magnitude sector fixes the dominant projection sign. Exact `pi > 3` gives `2*pi > 6`, so the true mixed phase derivative is strictly larger in that direction than the complete retained residual at every source point. The full derivative is therefore nonzero with exact fixed sign. Equality in any orthant is rejected.

## Material broadening beyond v25

The acceptance source is a genuine multi-harmonic example whose exact degree-4 dominant/transverse Bernstein controls make v25 fail its separate global cone test: `dominant_floor/2=5.38` while `transverse_ceiling=5.42`. Those global sufficient bounds overlap. The actual source polynomials are correlated, however, and v26 proves all combined pointwise cone/residual margins strictly positive. The source is therefore certified without weakening any phase, residual, endpoint or multiplicity condition.

The suite also checks a positive source polynomial whose old strict Bernstein-floor sufficient test fails at a zero Bernstein coefficient while exact Sturm authority proves the polynomial strictly positive. This verifies that v26's fixed-sign authority is genuinely source-polynomial/Sturm based rather than another restatement of the old floor certificate.

## Residual and event semantics

Only the two phase terms of the selected mixed anchor are consumed. Both anchor amplitude derivatives remain residual. Harmonic-0 and every other derivative channel remain residual. Other phase terms retain the established rational upper theorem `2*pi<44/7`.

After exact derivative nonvanishing is proved, existing rational-turn endpoint/root/multiplicity authority is reused unchanged. Admitted open and endpoint roots are simple. Historical v8-v25 routes run first and retain precedence; v26 upgrades only residual blocked spans.

The adversarial suite covers S-dominant and C-dominant directions, increasing/decreasing derivatives, sign-changing transverse components, exact phase-sector endpoints and `1/1000000` neighbours, exact pointwise cone equality and neighbours, combined residual equality and neighbours, dominant sign failure, retained anchor amplitude derivatives, open/no-root/endpoint outcomes through preserved route ownership, source-parameter mismatch, forged caller certificates, binary-float rejection and exact resource refusal propagation.

## Protected contracts

Historical v25 artifacts are SHA-pinned. The frozen 26-operation denominator is unchanged. Caller pointwise-cone, dominant-sign, orthant, floor/ceiling, sector, Sturm or root metadata is discarded before source analysis. Binary float, epsilon/tolerance, finite sampling, numerical trigonometry, approximate minimization/root ordering, arbitrary subdivision/refinement depth, timeout and resource limits are forbidden as correctness authority. Resource refusal propagates as refusal/`UNCERTIFIED`, never as mathematical success.

Protected source/audio/provenance, canonical journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics are unchanged. No native, paid, production or expensive campaign is authorized.

## Residual frontier

PB-007-01 remains OPEN beyond v8-v26. The remaining frontier includes phase intervals that do not fit any existing exact half-magnitude sector, sources with no usable fixed-sign component, and broader irreducible coupled analytic zero-isolation problems. The next repair should seek a materially broader exact projection/event theorem rather than another global-envelope variant. If widening the phase authority requires genuinely new transcendental minimization or zero-isolation machinery, that theorem boundary must be recorded explicitly instead of introducing sampling, tolerances, refinement caps or a premature MC-B retry.
