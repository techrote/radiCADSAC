# MC-038 / PB-007-01 — original V41/V13 blocked-source exact physical root order

**Date:** 29 October 2026. **Owner:** [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Base:** main \`de7caa967ff0176b41e50a6cd8f882313de8d453\` (merged #291). **Evidence class:** deterministic-model exact rational interval proof, **not** a generic V41/V27 ordered-child composition theorem or native/engineering capability.

## Fixed custody and original source

Frozen original 121-case v54 corpus Git blob \`5841c331579489b25caef38cd412bdbf286f9134\`; accepted degree-0/1 B-spline source lowerer Git blob \`2a8079ee2cf012bc2a12794c4c5ff19ebd760007\`. Investigated exactly one harvested row \`harvested:verify_pb00701_v13:c426f65b5c10\`, original producer \`verify_pb00701_v13\`. The historical span owner is \`PB00701_V41_EXACT_ROTATED_COORDINATE_ORIENTATION_ROOT_PARTITION_COMPOSITION\`, with original span status \`BLOCKED:V41_COMPLETE_V43_CHILD_NOT_COMPOSABLE\` and v54 whole-source disposition \`BLOCKED\`. It remains blocked. The other harvested V41 source remains historically certified and is not reclassified.

The exact original source parameter is \`s∈[0,1]\`, \`source_parameter_id=source-time-t\`, with a single clamped degree-1 physical B-spline span in each of four channels, no harmonic-zero offset, and exact phase turns \`s/4\`. Consequently \`θ(s)=πs/2\`. The original channel amplitudes, independently checked through the pinned spline lowerer, are:

\[
C_1(s)=\frac{15s-5}{6},\quad
C_3(s)=\frac{3s-1}{6},\quad
S_1(s)=\frac{2-3s}{2},\quad
S_4(s)=\frac{2-3s}{6}.
\]

With \`A=(3s-1)/6\`, \`B=(2-3s)/2\`, the original full physical expression is

\[
F(s)=A(s)[5\cos\theta+\cos(3\theta)]
+B(s)[\sin\theta+\tfrac13\sin(4\theta)].
\]

No rephasing, replacement coefficients, sampled root coordinates or child-count inference is used.

## Exact root-order statement and falsification

The executable establishes these **source-specific** closed-zone facts:

| Rational physical interval | Exact established property |
|---|---|
| \([0,3/20]\) | \(F<0\) |
| \([3/20,1/5]\) | \(F'>0\) |
| \([1/5,4/5]\) | \(F>0\) |
| \([4/5,17/20]\) | \(F'<0\) |
| \([17/20,1]\) | \(F<0\) |

The first derivative zone therefore contains exactly one simple negative-to-positive physical root in the strict rational bracket \((3/20,1/5)\). The second derivative zone contains exactly one simple positive-to-negative root in \((4/5,17/20)\). All remaining closed regions are strictly nonzero; original source endpoints are nonzero. Thus exactly **two distinct ordered simple open roots**, no endpoint roots, and maximal sign cells **NEGATIVE / POSITIVE / NEGATIVE**. Both root coordinates remain implicit; neither is claimed algebraic or evaluated numerically.

Falsification is explicit: any altered original source control/knot/phase/source ID/producer/owner/refusal, invalid exact π/trig enclosure, failed strict zone bound, changed root bracket/sign cell or promotion of an unsupported programme gate invalidates the proposed research certificate.

## Fully rational trigonometric interval method

The verifier establishes a certified interval \(\pi_{\rm lo}<\pi<\pi_{\rm hi}\) using the exact Machin identity
\[
\pi=16\arctan(1/5)-4\arctan(1/239)
\]
and twelve alternating rational terms per arctangent, with the next term as its signed strict remainder. It constructs a rational \(\pi_0\le\pi_{\rm lo}\) rounded down to \(10^{-12}\), with exact bound \(\pi_{\rm hi}-\pi_0<10^{-11}\). For \(\sin(k\theta)\) and \(\cos(k\theta)\), \(k=1,3,4\), it evaluates exact rational Taylor polynomials through degrees 41 and 40 at \(x_0=k\pi_0 s/2\). Every argument satisfies \(0\le x_0<7\). Each enclosure adds the rigorous Lagrange remainder \(7^{41}/41!\) and the \(|x-x_0|\) bound using the global unit Lipschitz constants of sine/cosine. All arithmetic in the executable uses Python \`Fraction\`, including interval products, π bounds and sign decisions. Neither the proof nor admission uses binary floating point.

Let \(E=5\cos\theta+\cos3\theta\), \(H=\sin\theta+\sin4\theta/3\). Using \(|A|\le1/3\), \(|B|\le1\), \(|E|\le6\), \(|H|\le4/3\), \(|E_\theta|\le8\), \(|H_\theta|\le7/3\), \(|E_{\theta\theta}|\le14\), \(|H_{\theta\theta}|\le19/3\), and \(\pi/2<11/7\), it verifies globally
\[
|F'(s)|<14,\qquad |F''(s)|<60.
\]
Each of the five rational zones is subdivided into 128 rational closed cells. At each midpoint \(m\), an exact Taylor-plus-phase enclosure of \(F(m)\) or \(F'(m)\) must have the required strict sign margin greater than \(14r\) or \(60r\), respectively, where \(r\) is the exact cell half-width. The mean-value theorem then certifies the asserted sign on **every point of that entire closed cell**, not only at sampled points. The union of the verified cells covers the entire original source interval, including all boundaries. The narrowest margin in the long positive zone is strictly positive; an exact-bound failure raises an error instead of using an epsilon or weaker check.

## Source, authority and adversarial verification

Run:

\`\`\`sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v41_v13_fixed_source_order.py --contract --self-test
\`\`\`

The \`--contract\` path requires the exact original corpus Git blob, exact pinned source-lowerer blob, original source/provenance/owner/disposition and 26-operation domain/MC-1 authority. \`--self-test\` exercises independent alterations to phase, spline knot, cosine/sine controls, source parameter, producer, owner, v54 disposition, output root count, root brackets, sign cells, zone strictness, false general theorem and false engineering claims, production authorization, MC-B status and domain denominator. All must be rejected.

The checker is a bounded **source-specific independent analytic bridge** for a previously BLOCKED V41-owner original source. It does not consume the historical V41/V27 \`_compose_child_summaries\` count summary as an ordered witness, does not change the accepted v54 43-owner inventory or its 121 dispositions, and does not add an adapter or checked general nested-child composition route to the production-facing model. V41/V27 child witness validation, exact endpoint one-sided orders, multiplicities, proof cuts, source knots, mixed owners and resource refusals remain open.

## Downstream nonclaims and next evidence

Historical #275 and all previous qualified bounded cases remain unchanged. PB-007-01/02/03/04 and the broader constructive coverage obligation remain open. MC-B, MC-1 are \`NOT_ESTABLISHED\`, production unauthorized. Retain all 26 operation types, source/provenance/phase/canonical-journal/material/body/lineage, refusal and \`UNCERTIFIED\` semantics, and mandatory conventional usable engineering STEP. No paid/native campaign, B-rep/STEP capability, generic analytic event theorem, historical relabelling or new issue is authorized.

**Next:** build a genuine V27/V41 checked nested-child interface that receives complete physically ordered, source-bound leaf witnesses and rechecks them without choosing alternate successful routes. It must fail closed on count-only inputs and mismatched endpoint signs, preserve one-sided analytic orders on cuts and real knots, and propagate typed resource refusal without calling it a truth value. The present one-source proof cannot discharge that gap.
