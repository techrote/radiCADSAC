# PB-007-01 v21 — exact finite sign-orthant L1 derivative envelope

Issue: #204  
Parent integration gate: MC-038 / #100  
Source baseline: `b9444116b4856c606bdcb0040d439ba893f47c85`  
Disposition: **bounded exact L1 derivative-envelope route added; PB-007-01 remains OPEN**  
Native/paid execution: **none**

## Result

v21 attacks the remaining conservatism in v20's Cauchy–Schwarz pointwise certificate. Historical v8–v20 classification retains precedence. v21 is considered only when v20 reaches `POINTWISE_ENVELOPE_STRICT_DOMINANCE_NOT_CERTIFIED` on an otherwise eligible exact residual span with a fixed-sign phase-independent anchor derivative.

For the unchanged source form

`F(s)=P(s)+sum_h(C_h(s) cos(2*pi*h*phi(s)) + S_h(s) sin(2*pi*h*phi(s)))`,

v21 reuses exactly the source-derived v20 envelope polynomials `C'_h`, `S'_h`, `(44/7)|h*r|C_h`, and `(44/7)|h*r|S_h`. The theorem `pi < 22/7` remains the only transcendental inequality used by this derivative bound.

## Exact L1 sign-orthant certificate

Let the nonzero envelope polynomials be `f_1,...,f_N`. Pointwise,

`|F'(s)-P'(s)| <= sum_i |f_i(s)|`.

The recorded next path proposed partitioning the interval into exact sign cells. v21 uses an equivalent but simpler exact formulation that avoids algebraic root ordering entirely:

`sum_i |f_i(s)| = max_{sigma in {-1,+1}^N} sum_i sigma_i f_i(s)`.

After MC-032 exact endpoint/Sturm authority proves that `P'` has one fixed strict sign, v21 forms every one of the finite `2^N` directed margin polynomials. For an increasing anchor these are

`M_sigma(s)=P'(s)-sum_i sigma_i f_i(s)`,

and for a decreasing anchor the directed anchor is `-P'`. Every `M_sigma` must be strictly positive on the complete closed source interval. Each claim is decided with exact rational endpoint relations and exact Sturm distinct-root counting. Endpoint equality, any interior root, or the wrong endpoint sign fails closed.

Because every possible sign cell corresponds to one of those orthants, positivity of every margin is exactly the strict condition

`|P'(s)| > sum_i |f_i(s)|`

for every source point. No approximate sign-change root, root ordering, epsilon, sampling, subdivision, numerical trigonometry, timeout, or caller certificate participates in correctness.

## New constructive coverage

The acceptance source uses two positive harmonics with derivative envelopes `s` and `1-s`, plus small exact phase-envelope terms. Their exact L1 total stays below the anchor magnitude `6/5`. v19 is blocked because separate whole-span derivative suprema already total `2`; v20 is blocked because its `N=4` Cauchy bound fails at an endpoint. v21 certifies all 16 exact orthant margins and therefore proves strict monotonicity.

The exact L1 equality boundary is tested independently with phase-envelope constants `1` and `2`: anchor magnitude `3` is rejected, `3-1/1000000` is rejected, and `3+1/1000000` is certified even though the v20 Cauchy certificate remains blocked. Rational, algebraic-irrational, and repeated sign-change roots in envelope polynomials are covered without computing or ordering approximate roots.

## Endpoint and multiplicity authority

Once strict derivative sign is established, v21 reuses v19/v20 endpoint semantics unchanged. Rational turns are classified by the established exact tangent-half authority; tangent-coordinate half-turn poles use exact half-turn shifting with `(-1)^h` parity. Exact endpoint signs plus strict monotonicity yield zero or one open root and exact endpoint events. Since the derivative is strictly nonzero on the full closed span, every admitted root is simple.

## Adversarial boundary

The suite covers increasing/decreasing directions, no-root/open-root/endpoint-root outcomes, exact equality and `±1/1000000` neighbours, rational/algebraic/repeated envelope sign changes, anchor-derivative sign failure, v20 precedence, source-parameter mismatch, binary-float source authority, forged L1/sign-cell/orthant/margin/Sturm/sign/root metadata, resource-refusal laundering, historical-v20 mutation, frozen-denominator shrinkage, and false MC-B promotion.

Resource refusal remains a non-truth terminal status. Finite orthant enumeration is a mathematical termination argument for finite `N`; inability to complete it under a particular resource budget cannot be converted into certification or rejection.

## Programme effect

**PB-007-01 remains OPEN.** v21 is a materially sharper terminating exact subroute, not a universal decision procedure for residual coupled exponential-polynomial event predicates. In particular, sources without a fixed-sign phase-independent anchor derivative, and sources whose exact L1 envelope is not dominated, remain blockers.

PB-007-02 remains dependent on PB-007-01; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04, PO-05 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`. No MC-B retry is justified solely by v21.

The frozen 26-operation denominator and protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain binding.

## Next repair boundary

The surviving frontier is beyond fixed-sign anchor L1 dominance. The next corrective package should target a materially broader exact coupled multi-harmonic subclass, especially sources where the phase-independent anchor derivative itself changes sign or vanishes, while preserving exact finite termination and refusing rather than laundering genuinely unresolved transcendental zero structure.
