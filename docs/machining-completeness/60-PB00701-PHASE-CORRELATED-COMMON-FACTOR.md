# PB-007-01 v34 — exact phase-correlated common-factor authority

## Status

**RAG: GREEN for the bounded V34 family; RED for full PB-007-01.** PB-007-01 remains OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`. The domain remains **26 operations** and all protected source/audio/provenance semantics remain unchanged.

## Why V34 exists

V33 established a precise residual theorem boundary: exact source-owned separator synthesis was available, but independent absolute bounds on the selected harmonic's `C'` and `S'` terms destroyed useful phase correlation. V34 repairs that conservatism for the bounded source-owned family `C_h=S_h=G` without changing any non-anchor residual or event semantics.

## Exact construction

For a source polynomial `G` proved one strict sign and phase turn `t=h*phi` contained in

`-3/16+k/2 <= t <= -1/16+k/2`, 

set `u=2*pi*(t+1/8-k/2)`. Then `u` lies in `[-pi/8,pi/8]` and

- `cos(theta)+sin(theta)=(-1)^k*sqrt(2)*sin(u)`;
- `cos(theta)-sin(theta)=(-1)^k*sqrt(2)*cos(u)`.

Thus the selected harmonic's full derivative is treated jointly as

`G'(cos+sin)+2*pi*h*r*G*(cos-sin)`.

Using the exact rational inequalities `sqrt(2)>238/169`, `sqrt(2)<99/70`, `cos(u)>12/13`, `|sin(u)|<5/13`, and `2*pi>6`, V34 obtains the strict sufficient margin

`6*|h*r|*(2856/2197)*|G|-(99/182)*|G'|-sum_i|R_i|>0`.

Finite sign-orthant enumeration converts every absolute value to exact rational-polynomial margins. MC-032 endpoint/Sturm strict-positivity authority must prove every margin on the complete closed child span. Equality fails closed. No numerical trigonometry, sampling, epsilon, tolerance, binary-float authority, arbitrary refinement, timeout, or resource refusal becomes truth authority.

## Acceptance boundary

The principal witness uses `G=(1+3s/4)^2`, exact phase interval `[-3/16,-1/16]`, and a nonzero tiny non-anchor h=2 harmonic. Its V30 separate global projective ratio is `16/49 < sqrt(2)-1`, so the old global envelope remains blocked, while the V34 joint derivative certificate is strict. Both selected amplitude derivatives are active but consumed only through the exact `G'(cos+sin)` identity.

Adversarial coverage includes both phase-rate directions and opposite cell parity, exact cell boundaries with signed rational neighbours, exact joint-margin equality with neighbours, preserved zero/open/endpoint root outcomes, unequal quadratures, sign-changing/zero common factors, unsupported cells, source-coordinate mismatch, forged proof metadata, binary floats, exact resource refusal, historical V30 precedence, pinned V33 blocker evidence, the frozen 26-operation denominator, and false MC-B promotion.

## Programme consequence

This is a sufficient-family repair, not a claim that PB-007-01 is closed. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/05/08 remain OPEN. Source/audio/provenance, canonical-journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP contracts remain protected.

The next useful repair is an exact phase-correlated proportional/common-factor family beyond equal quadratures. It must remain finitely terminating and retain every non-anchor residual; otherwise the unresolved theorem boundary should be recorded explicitly.
