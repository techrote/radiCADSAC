# MC-038 / PB-007-01 v42 report — orientation-transition derivative bridge

## Decision

A bounded exact rotated-coordinate orientation-transition bridge is established for a diagonal phase cell. PB-007-01 remains open. MC-B and MC-1 remain `NOT_ESTABLISHED`. The frozen denominator remains 26 operations and no protected source/audio/provenance or downstream semantics change.

## Corrective context

Issue #245 attempted exact orientation-root partition composition. That route is blocked because a proof cut at `A=0` or `B=0` is itself a closed endpoint where complete v39/v40 strict orientation and phase-gap predicates fail. Diagnostic run 35910280571 evaluated 1,680 exact complete-v40-blocked candidates and certified none through that composition route. v42 adds the missing closed-neighborhood theorem rather than weakening the child contract.

## Exact theorem

For source-owned quadratures `C_h(s), S_h(s)` regenerate

`A=(C+S)/2`, `B=(C-S)/2`, `X=cos(theta)+sin(theta)`, `Y=cos(theta)-sin(theta)`.

The selected physical derivative remains

`D=A'X+B'Y+2*pi*h*r*(A Y-B X)`.

On the exact diagonal phase cell, inherited algebraic authority gives fixed sign of `Y`, `|Y|>2856/2197`, `|X|<99/182`, and `|Y|<99/70`. The bridge derives strict sign of `B'` from source coefficients, then proves every finite sign orthant of

`|B'|*(2856/2197) - |A'|*(99/182) - (44/7)*|h*r|*(|A|*(99/70)+|B|*(99/182)) - sum_i |R_i| > 0`.

`2*pi<44/7` is the exact rational upper theorem already recorded in v29 for adverse phase terms. Every orthant is discharged with existing MC-032 exact closed-interval endpoint/Sturm strict positivity. Equality is fail-closed; exact resource refusal is not a truth value.

## Genuine residual acceptance source

The source `C_1=-23/6+11s`, `S_1=17/6-9s` gives `A=-1/2+s` and `B=-10/3+10s`. Thus A crosses zero at `1/2`, B crosses zero at `1/3`, and neither complete whole-span signed-A nor signed-B orientation is available to v39/v40. Nevertheless `B'=10` is strictly positive. With exact phase law `phi=-1/8+s/1000`, the complete source span stays in one supported diagonal cell and the full v42 margin is strictly positive.

The selected C' and S' terms are consumed only through the rotated identity; selected phase terms remain jointly represented by `A Y-B X`; every non-anchor residual remains explicit. No proof cut becomes a physical event and root multiplicity remains governed by the complete derivative.

## Controls

Adversarial coverage includes the exact interior A zero, both B' orientations, B'=0/sign-changing refusal, strict-margin equality fail-close controls, exact phase-cell boundaries and just-outside rational neighbors, forward/reverse phase laws, opposite diagonal projection sign, non-anchor residual retention, forged orientation/derivative/margin metadata, inherited binary-float/source-coordinate rejection, resource-refusal propagation, historical v39/v40 precedence, frozen 26-operation coverage, and false MC-B/MC-1 promotion.

## Contract effect

PB-007-01 remains open; PB-007-02 remains dependent, PB-007-03 remains open, PB-007-04 remains propagated open, and PO-04/05/08 remain open. The next dependency path is to use this exact closed transition bridge as an explicit child type when repairing #245 composition; v42 itself does not close #245.

Protected source/audio/provenance, journal, exact time/path/phase, material, cutter/holder, body/lineage, refusal, conventional STEP, and downstream semantics are unchanged. Production and expensive execution remain unauthorized.
