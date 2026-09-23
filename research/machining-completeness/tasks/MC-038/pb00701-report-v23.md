# PB-007-01 v23 — exact nonconstant-amplitude phase-sector anchor

Issue: #208  
Parent integration gate: MC-038 / #100  
Source baseline: `5a2d500a4c2956254fa17c89be884ca08ded0324`

## Result

A bounded new PB-007-01 route is established for residual multi-harmonic sources that remain blocked after v22 and contain a **nonconstant source-owned pure SIN/COS anchor**. The route does not establish the general coupled analytic grammar; PB-007-01 remains OPEN and MC-B remains `NOT_ESTABLISHED`.

For a pure anchor amplitude `A(s)`, v23 converts the exact rational power polynomial to exact Bernstein coefficients on closed `[0,1]`. It accepts only when every Bernstein coefficient has one strict sign. Then `A_floor=min_i|b_i|>0` is a source-derived rational lower bound by the Bernstein convex-hull property.

The existing v22 exact rational phase-sector theorem supplies derivative-quadrature magnitude at least `1/2`. Together with exact `pi > 3`, v23 derives

`L_anchor = 3*|h*r|*A_floor < |G_phase'(s)|`.

The anchor amplitude derivative is explicitly retained in the residual. For a SIN anchor, `A'(s) sin(...)` remains residual; for a COS anchor, `A'(s) cos(...)` remains residual. `P'` and all other derivative contributions remain residual as well, with only the established rational upper bound `2*pi < 44/7` used for phase terms.

The residual is discharged by the finite v21/v22 sign-orthant L1 construction. Every exact polynomial margin `L_anchor-sum sigma_i f_i(s)` must be strictly positive on closed `[0,1]` under MC-032 exact endpoint/Sturm authority. Exact equality fails closed. This proves the complete source derivative has a fixed nonzero sign; exact rational-turn endpoint authority then gives zero/one open-root and endpoint-root decisions, and all admitted roots are simple. Tangent-half poles retain the established exact half-turn/parity handling.

## Adversarial boundary

The deterministic suite covers: a genuine nonconstant-amplitude multi-harmonic source blocked by v22 but certified by v23; increasing/decreasing directions; SIN/COS anchors; exact phase-sector equality and signed `±1/1000000` neighbours; exact amplitude-floor zero and signed neighbours; a pointwise-positive amplitude whose mixed Bernstein coefficients deliberately fail this sufficient certificate; exact residual-L1 equality and signed neighbours; zero/open/left-endpoint/right-endpoint root outcomes; constant-amplitude v22 precedence; non-pure quadrature rejection; source-parameter mismatch; forged amplitude/Bernstein/sector/L1/Sturm/root metadata; binary-float authority; resource refusal laundering; historical-v22 preservation; frozen 26-operation coverage; and false MC-B promotion.

## Contract preservation

The frozen 26-operation denominator is unchanged. Historical v22 evidence is hash-pinned and preserved. Source/audio/provenance, canonical journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics are unchanged. No native, paid, production or expensive campaign is authorized. Any exact resource refusal remains a non-truth result and cannot certify or reject an event.

## Residual blocker

PB-007-01 **remains OPEN** beyond the v8–v23 qualified families. In particular, v23 does not solve mixed-quadrature anchors, non-sector phase intervals, amplitudes whose nonvanishing is real but not certified by one-sign Bernstein coefficients, or the broader irreducible coupled analytic grammar. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/PO-05/PO-08 remain OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`.

The next dependency-ready direction is a materially broader exact mixed-quadrature or wider phase-dependent partial derivative anchor if it can derive a uniform rational lower bound from existing algebraic/transcendental authority. Otherwise the exact theorem boundary should be recorded and the campaign should route to the next independent corrective obligation rather than introducing sampling, tolerance, refinement, timeout or resource limits as correctness authority.
