# PB-007-01 v42: exact orientation-transition derivative bridge authority

V42 is a bounded exact extension of PB-007-01. It repairs the closed-orientation-transition blocker found in #245 / PR #246; it does **not** establish PB-007-01, MC-B or MC-1.

## Authority boundary

Complete v40 authority runs first. V42 is eligible only for a residual exact lowered span with two nonzero source-owned rational-polynomial quadratures on a supported diagonal phase cell. Caller orientation, derivative, margin, root or multiplicity metadata is never proof authority.

Regenerate `A=(C+S)/2`, `B=(C-S)/2`, `A'` and `B'` exactly. Unlike v39/v40, V42 does not require strict whole-span sign of `A` or `B`. Instead MC-032 closed-interval endpoint/Sturm authority must prove strict sign of the source-derived polynomial `B'` and derive `sigma_B_prime`.

## Exact closed-span theorem

For `X=cos(theta)+sin(theta)` and `Y=cos(theta)-sin(theta)`, supported diagonal cells are

`-3/16+k/2 <= h*phi <= -1/16+k/2`.

Existing exact authority supplies fixed sign of `Y`, `|Y|>2856/2197`, `|X|<99/182`, and `|Y|<99/70`. The previously recorded exact rational theorem `2*pi<44/7` is used only as an adverse upper bound for the selected phase contribution.

With `Bprime_bar=sigma_B_prime B'>0`, V42 proves every exact sign orthant of

`(2856/2197)Bprime_bar -(99/182)sigma_Ap A' -(44/7)|h r|(99/70)sigma_A A -(44/7)|h r|(99/182)sigma_B B - sum sigma_i R_i > 0`.

This lower-bounds the oriented complete physical derivative

`D=A'X+B'Y+2*pi*h*r*(AY-BX)+retained residuals`.

Thus `sign(D)=sigma_B_prime*diagonal_projection_sign`. Selected `C'` and `S'` are consumed only through the exact rotated identity; the selected phase channels remain joint; every non-anchor derivative residual remains explicit. Equality and exact resource refusal fail closed.

## Why this is not v41 partitioning

The bridge certifies the complete **closed** transition span directly. It does not cut at `A=0`/`B=0`, reinterpret a child as open or half-open, or add an epsilon neighborhood. Proof orientation zeros are event-neutral and do not alter physical endpoint/root/multiplicity semantics. Once this independent bridge is merged and verified, #245 may resume composition using it as the missing handoff authority.

## Fail-closed boundary

Zero or sign-changing `B'`, unsupported phase cells, failed complete margin, malformed source structure, binary-float authority, source-coordinate mismatch, exact resource refusal, or forged proof metadata is non-certification. Numerical trigonometry, sampling, tolerance, approximate roots, adaptive refinement, arbitrary subdivision depth, timeout and denominator caps are not correctness authority.

## Programme preservation

The frozen machining denominator remains 26 operations. PB-007-01 remains OPEN; PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04, PO-05 and PO-08 remain OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`.

Protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder, durable-body/lineage, refusal/`UNCERTIFIED`, conventional STEP and downstream semantics are unchanged.
