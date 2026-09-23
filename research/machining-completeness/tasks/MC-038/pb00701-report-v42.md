# PB-007-01 v42 — exact orientation-transition derivative bridge certificate

Status: **bounded executable authority added; PB-007-01 remains OPEN; MC-B / MC-1 remain NOT_ESTABLISHED**.

## Why v42 exists

Issue #245 / PR #246 established a real closed-interval theorem blocker: cutting exactly at an `A=0` or `B=0` orientation root does not make either adjacent **closed** child admissible to complete v39/v40 strict-orientation authority. The exact v41 root machinery was not the problem. V42 adds the missing local closed-span theorem and does not weaken v39/v40, reinterpret endpoints, or introduce epsilon neighborhoods.

## Exact bridge

For a residual exact lowered span, regenerate source-owned

`A=(C+S)/2`, `B=(C-S)/2`, `A'=(C'+S')/2`, `B'=(C'-S')/2`.

On an exact diagonal phase cell `-3/16+k/2 <= h*phi <= -1/16+k/2`, the established v34/v39 authority gives fixed sign of `Y=cos(theta)-sin(theta)` and exact rational bounds

- `|Y| > 2856/2197`;
- `|X| < 99/182` for `X=cos(theta)+sin(theta)`;
- `|Y| < 99/70`.

MC-032 exact endpoint/Sturm authority must prove either `B'>0` or `-B'>0` over the complete closed span, deriving `sigma_B_prime` and `Bprime_bar=sigma_B_prime B'>0` from source. The historical exact rational theorem `2*pi < 44/7` bounds the selected phase terms adversely.

For every finite sign orthant over `A'`, `A`, `B` and every retained non-anchor residual, MC-032 proves

`(2856/2197)Bprime_bar -(99/182)sigma_Ap A' -(44/7)|h r|(99/70)sigma_A A -(44/7)|h r|(99/182)sigma_B B - sum sigma_i R_i > 0`.

Therefore the favorable `B'Y` channel dominates the complete physical derivative

`D=A'X+B'Y+2*pi*h*r*(AY-BX)+retained residuals`

without requiring `A` or `B` itself to have a strict whole-span sign. The certified physical sign is

`sign(D)=sigma_B_prime*diagonal_projection_sign`.

Strict equality fails closed. No numerical trigonometry, sampling, tolerance, epsilon neighborhood, approximate root ordering, subdivision cap, timeout or denominator cap is proof authority.

## Genuine residual acceptance

The acceptance source is

- `C_1=-5/6+2s`;
- `S_1=-1/6`;
- hence `A=s-1/2` and `B=s-1/3` both have simple interior zeros;
- `A'=B'=1`;
- exact harmonic-1 phase interval `[-1/8,-1/16]` with rate `1/16` lies inside the supported diagonal cell.

Complete v40 blocks because neither whole-span signed-A nor signed-B orientation is strict. V42 derives `sigma_B_prime=+1` and certifies the full closed span. This directly repairs the obstruction recorded for #245 rather than attempting another orientation-root cut.

## Adversarial boundary

A separate adversarial certificate keeps a tiny non-anchor harmonic live to prove residual retention without repeating the expensive complete-v40 residual traversal. The executable suite covers the exact interior A zero and rational neighbors, B' sign equality and both signs, exact complete-margin equality and rational neighbors, diagonal-cell endpoints and just-outside rational points, positive/negative phase rates and the opposite diagonal projection sign, exact resource refusal, forged caller orientation/derivative/margin/root metadata, binary-float and source-coordinate mismatch rejection, historical v39/v40 precedence, and proof-zero event neutrality. Selected `C'`/`S'` and selected phase channels are consumed only through the exact rotated identity; every non-anchor derivative residual remains explicit.

## Programme and protected semantics

V42 is only a bounded sufficient theorem. PB-007-01 remains OPEN; PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04, PO-05 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`; the machining denominator remains frozen at 26 operations. Do not retry MC-B solely because v42 lands.

Protected source/audio/provenance, canonical journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder, durable-body/lineage, refusal/`UNCERTIFIED`, conventional STEP, endpoint/root/multiplicity and downstream semantics are unchanged. An orientation zero used only by the proof is not a physical event and cannot alter multiplicity.
