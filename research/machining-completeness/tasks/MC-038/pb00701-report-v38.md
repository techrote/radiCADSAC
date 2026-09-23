# MC-038 / PB-007-01 v38 report

## Decision

`EXACT_DIRECT_ROTATED_COORDINATE_ROUTE_ESTABLISHED_PB00701_OPEN`.

PB-007-01 remains open. MC-B and MC-1 remain `NOT_ESTABLISHED`. The domain denominator remains frozen at 26 operations. No protected source/audio/provenance or downstream semantics are changed.

## Exact repair

V38 removes v37's nonconstant-common-factor prerequisite for one selected positive harmonic. From exact source polynomials it regenerates `A=(C+S)/2`, `B=(C-S)/2`, `A'=(C'+S')/2`, `B'=(C'-S')/2` and retains the complete derivative

`A'*X+B'*Y+2*pi*h*r*(A*Y-B*X)`

with `X=cos(theta)+sin(theta)` and `Y=cos(theta)-sin(theta)`. On `-3/16+k/2 <= h*phi <= -1/16+k/2`, only the established rational bounds `|X|<99/182`, fixed-sign `|Y|>2856/2197`, `|Y|<99/70`, and `2*pi>6` are used. MC-032 exact endpoint/Sturm strict positivity discharges `A>0`, both `sigma_B` phase gaps, and every complete residual sign orthant. Equality and resource refusal fail closed.

## Genuine extension beyond v37

The acceptance source `C_1=1+6s/5`, `S_1=11/10+6s/5` is coprime over `Q[s]`: its canonical monic GCD is `1`. The test suite requires complete v37 executable authority to return `BLOCKED` specifically through the constant-GCD boundary before v38 may certify it. V38 derives `A=21/20+6s/5`, `B=-1/20`, `A'=6/5`, `B'=0`. Both original amplitude derivatives are nonzero and consumed jointly. A second coprime fixture with `S_1=11/10+7s/6` makes both rotated derivative channels `A'` and `B'` nonzero.

## Boundary and preservation controls

Adversarial tests cover positive/negative phase rates, opposite diagonal cells, exact phase-cell/A/phase-gap/complete-margin equality and signed `1/1000000` neighbours, zero/open/left-endpoint/right-endpoint outcomes under preserved exact multiplicity authority, malformed or forged rotated-coordinate/derivative/cell/bound/margin/root metadata, zero quadratures, source-coordinate mismatch, binary floats, and exact resource refusal. Historical v30, v34, v35, v36 and v37 successes retain exact precedence; v33 blocker evidence remains pinned; false MC-B promotion and denominator drift are rejected.

The repair uses no sampling, numerical trigonometry, epsilon/tolerance, approximate root ordering, arbitrary refinement cap, native campaign, paid campaign, production execution, or expensive execution.
