# PB-007-01 v22 — exact phase-sector partial derivative anchor

Issue: #206  
Parent integration gate: MC-038 / #100  
Source baseline: `d98bce801e4ba1e95ec6d4fe8b709eb05a1c8c87`  
Disposition: **bounded exact phase-dependent derivative-anchor route added; PB-007-01 remains OPEN**  
Native/paid execution: **none**

## Result

v22 implements the recorded post-v21 frontier without pretending that an exact event-uniqueness certificate is automatically a derivative-magnitude certificate. Historical v8–v21 classification retains precedence. The new route is considered only on residual exact multi-harmonic spans still blocked after v21.

The admitted source-owned anchor is one pure constant-amplitude positive harmonic, either `B sin(2*pi*h*phi)` or `C cos(2*pi*h*phi)`, with the complementary quadrature exactly zero. The exact affine harmonic phase must stay inside a closed rational sector where the derivative quadrature has fixed sign and magnitude at least `1/2`.

For SIN anchors those sectors certify `|cos(2*pi*t)| >= 1/2`; for COS anchors they certify `|sin(2*pi*t)| >= 1/2`. With exact `pi > 3`, v22 derives the strict rational lower bound

`L_anchor = 3*|amplitude*h*r| < |G'(s)|`.

This is a new explicit derivative theorem layered on top of the already-qualified lower-complexity single-harmonic event family. No caller certificate and no numerical trigonometry is trusted.

## Residual construction

The harmonic-0 derivative is no longer required to be an anchor. It may be zero or sign-changing and remains an exact residual polynomial. All other non-anchor amplitude derivatives and phase derivatives are also residual; phase terms use only the rigorous `2*pi < 44/7` bound already established in v19–v21.

For the exact residual envelope polynomials `f_i`, v22 reuses the v21 finite identity

`sum_i |f_i(s)| = max_{sigma in {-1,+1}^N} sum_i sigma_i f_i(s)`.

Every residual orthant margin

`L_anchor - sum_i sigma_i f_i(s)`

must be strictly positive on closed `[0,1]` under MC-032 exact endpoint/Sturm authority. Equality fails closed. Hence the complete derivative has the anchor sign everywhere, so endpoint signs decide zero or one open root and every admitted root is simple.

## New constructive coverage

The acceptance fixture has a sign-changing harmonic-0 derivative, a constant-amplitude `h=1` SIN anchor, and a nonconstant `h=2` source channel. v21 remains blocked because no fixed-sign harmonic-0 derivative exists. The `h=1` harmonic phase stays in the exact `[−1/6,1/6]` cosine sector, giving `L_anchor=1/4`, while all residual orthant margins remain strictly positive. v22 therefore certifies a genuine multi-harmonic source that the previous fixed-anchor family could not admit.

The exact sector boundary is tested at `1/6` together with signed `±1/1000000` neighbours. The boundary itself is valid because the derivative quadrature magnitude is exactly `1/2`; the outside neighbour is rejected. Exact residual-L1 equality is rejected, the `−1/1000000` neighbour is certified, and the `+1/1000000` neighbour is rejected.

## Endpoint and refusal semantics

Endpoint evaluation is unchanged: v19/v21 rational-turn tangent-half authority, including exact half-turn parity shifting, decides the complete original source value. No event boundary is replaced by an approximate certificate boundary.

Resource refusal remains non-truth. The route terminates mathematically because source anchor candidates and residual sign orthants are finite; a runtime budget is not part of the theorem.

## Programme effect

**PB-007-01 remains OPEN.** v22 does not decide sources with nonconstant anchor amplitude, mixed anchor quadratures, phase trajectories leaving a certified half-magnitude sector, residual derivatives that are not strictly dominated, or the broader unresolved coupled exponential-polynomial grammar.

PB-007-02 remains dependent on PB-007-01; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04, PO-05 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`; no MC-B retry is justified solely by v22.

The frozen 26-operation denominator and protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain binding.

## Next repair boundary

The remaining PB-007-01 frontier is beyond constant-amplitude rational phase-sector anchors. A further constructive step would need an exact lower bound for a broader source-owned partial derivative—such as nonconstant-amplitude or mixed-quadrature partial events—without converting event uniqueness, numerical trigonometry, sampling, tolerance, subdivision depth, timeout, or resource exhaustion into correctness authority. If no such bound follows from existing exact authority, that limitation should be recorded as the theorem blocker and the campaign should move to the next independent repair.
