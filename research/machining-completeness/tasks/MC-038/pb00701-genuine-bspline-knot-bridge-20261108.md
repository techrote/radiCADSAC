# MC-038 / PB-007-01 — genuine rational B-spline knot → complete physical events

**8 November 2026 · Research only · DETERMINISTIC_MODEL · Draft / NO MAIN MERGE.**
Stacked on [#457](https://github.com/techrote/radiCADSAC/pull/457) → [#455](https://github.com/techrote/radiCADSAC/pull/455) → [#453](https://github.com/techrote/radiCADSAC/pull/453). Main integration remains exclusively with [#397](https://github.com/techrote/radiCADSAC/pull/397). This is an exact-source conversion and local proof-custody result; **not** general spline/phase certification or programme capability.

## Problem and falsifiable claim

#453/#455/#457 accept rational polynomial spans and prove complete physical zero/sign partitions for a bounded moving H0/H1/H2 source. But a *declared polynomial interface* is not an authenticated knot of an originating B-spline. A forged interface can otherwise acquire attractive-looking "knot" event labels without a supplied B-spline control/knot vector.

This bridge accepts **actual bounded rational clamped B-spline coefficient data** for all five coefficients H0/C1/S1/C2/S2, reconstructs each coefficient polynomial *exactly* on the union of its real, positive-width knot spans, and passes only the reconstructed source into the inherited complete event certifier. It records a canonical input-source SHA-256, a distinct exact reconstructed polynomial-source SHA-256, and internal-knot multiplicity witnesses derived directly from the original vectors. A verifier redoes conversion and all downstream physical-certificate checks. Changing a control, falsely adding a knot, changing a sided physical order, or promoting MC/PB/production must refuse.

The decisive falsifier is an input whose reported knot does **not** appear as a positive-multiplicity interior member of a validated supplied knot vector, or whose physical events differ from an independently evaluated spline law. Such an input must never return a COMPLETE receipt.

## Admitted grammar and exactness

The self-bound input schema is:

\`\`\`json
{
  "grammar": "RATIONAL_BSPLINE_H0H1H2_AFFINE_PHASE/1",
  "phase_offset_pi": "0",
  "phase_slope_pi": "1",
  "splines": {
    "H0": {"degree": 2, "knots": ["0","0","0","1","1","2","2","2"], "controls": ["9/8","7/8","7/8","7/8","11/8"]},
    "C1": {"degree": 0, "knots": ["0","2"], "controls": ["1"]},
    "S1": {"degree": 0, "knots": ["0","2"], "controls": ["0"]},
    "C2": {"degree": 0, "knots": ["0","2"], "controls": ["1/8"]},
    "S2": {"degree": 0, "knots": ["0","2"], "controls": ["0"]}
  }
}
\`\`\`

Every coefficient has its own knot vector and polynomial degree, including constant degree-zero terms. Degrees are 0–3, at most 24 controls per coefficient, canonical bounded rational knot/control values, a common clamped domain in \([-8,8]\), and at most four positive-width spans in the union of all five knot vectors. End knots have the open-clamped multiplicity degree+1. Interior knot multiplicity may not exceed degree (or one for degree zero), and discontinuous resulting coefficient interfaces fail the inherited strong C0 source test. These are **strict sufficiency restrictions**, not a claim that a legitimate machining source outside them is physically invalid.

At each positive-width source span, the Cox–de Boor recursion defines each coefficient as a rational polynomial of degree at most the source spline degree. Evaluating at \(p+1\) distinct *interior rational nodes*, and Newton-interpolating with exact \`fractions.Fraction\` arithmetic, recovers the **unique full polynomial**, not a sampled approximation. This is justified by the polynomial-per-knot-span theorem; it is not an inference from finitely sampled signs. Four additional rational interior probes recompute the original basis and check the reconstruction, catching implementation mistakes but not replacing the mathematical theorem.

The converter canonicalizes **global source-time powers** for each of the five coefficients. The inherited #453 parser verifies rational degrees, shared endpoints, exact continuity, resource bounds, and source SHA-256. #457 then proves every accepted interior crossing or first-/second-order boundary event with exact rational interval arithmetic. It refuses unresolved flat contacts, nonquarterturn exact boundary values, insufficient arithmetic precision or incomplete partitions. It counts true-knot zeros once, and does not silently treat a knot that is merely present in a vector as a physical zero.

## Genuine internal double-knot example with two harmonics

At \(t\in[0,2]\), phase \(\theta(t)=\pi t\), C1=1 and C2=1/8, with nonzero moving H1 and H2. The H0 control vector \([9/8,7/8,7/8,7/8,11/8]\) and degree-two open knot vector \([0,0,0,1,1,2,2,2]\) yield

\[
H_0(t)=\begin{cases}
7/8+(t-1)^2/4,&0\leq t\leq1,\\
7/8+(t-1)^2/2,&1\leq t\leq2.
\end{cases}
\]

The supplied vector has a **genuine internal double knot** at t=1, not a fabricated subdivision. Both coefficient laws are C0 at that knot but have distinct quadratic curvature. The physical law is

\[
F(t)=H_0(t)+\cos(\pi t)+\tfrac18\cos(2\pi t).
\]

At t=1, F=0 and F'=0 separately on both sides, whereas

\[
F''(1^-)=1/2+3\pi^2/4,\qquad
F''(1^+)=1+3\pi^2/4,
\]

both strictly positive. The inherited #457 strict rational sided-F'' guards prove an **isolated second-order touch** from both sides. This source has one physical root, at the genuine knot, with positive signs on both sides.

A separate degree-two true-double-knot source with controls \([7/8,7/8,7/8,1,9/8]\) has a flat left H0 and right H0 \(=7/8+(t-1)/4\): the same physical knot is **order 2 on the left and order 1 on the right**. The parent certificate carries those sided orders distinctly, without inventing a globally smooth multiplicity.

## Original-source custody boundary

#453 already authenticates the frozen genuine V44 source from the pinned immutable V54/V2 blobs and validates its full moving H1+tiny-H2 coefficient law. This bridge independently reconstructs the equivalent V44 coefficient polynomials from explicit clamped degree-two C1/S1 controls plus exact degree-zero H0/C2/S2 terms, and compares the resulting entire source document to #453's authenticated frozen V44 shape. It calls #453's original frozen-source authentication rather than importing a user-provided original ID.

**Important limitation:** SHA-256 of a user-provided spline document binds the exact *supplied* data, but is not itself proof that those data were taken from a historical original. An original-source claim needs a separate pinned original specimen/row identity and source-contract verifier. The prospective double-knot tests are genuine structural splines but **not among the 121 frozen originals**. No new original witness is admitted.

## Receipt and adversarial safety

The receipt binds complete supplied-source and derived-piece hashes, canonical derived polynomial spans, the exact genuine-knot multiplicity witness list, the inherited physical-event certificate, zero newly closed historical sources, zero required PB/PO discharges, and explicit false PB/MC-B/MC-1/production flags. The verifier checks canonical JSON type identity, so bool/int aliasing cannot accidentally pass. The inherited event checker checks source/child identity, guard proofs, exhaustive intervals and exact total root counts.

Tests cover changed actual source controls, a forged knot witness, substituted source SHA, false capability promotion, false boolean zero discharge, mutated physical event order, unsupported degrees, reversed or excessive multiplicities, disallowed discontinuities, over-budget union, malformed source grammar, noncanonical rational values, nonuniform cubic reconstruction and V44 frozen-shape agreement.

Source construction and verification run with finite bounds. An input that cannot be established exactly raises typed \`Nontruth\` rather than emitting a probable result. The executable is invoked with:

\`\`\`bash
python3 research/machining-completeness/tasks/MC-038/pb00701_genuine_bspline_knot_bridge_20261108.py --contract --self-test
\`\`\`

The literal-head workflow additionally executes inherited #457/#455/#453 contracts, **full producing** original V54/V2 reconciliation, and repository-wide MC-1 static validation. Separate exact-head independent mathematical/source-critical review is necessary before Ready; main integration by #397 is independent of research admission.

## Outcome and nonclaims

This proves **bounded provenance of actual supplied rational B-spline internal knots**, not general B-spline source matching, broad arbitrary degree/multiplicity, C-1 discontinuities, general transcendental phase, algebraic coefficients or the full PB-007 constructive theorem. It is \`DETERMINISTIC_MODEL\`, not native geometry, STEP export, independent oracle qualification or production authorization.

Frozen **121 original cases / 20 historical route refusals / 30 missing ordered premises / 50 existing complete V2 witnesses** remain unchanged. New original-case closures: **0**. Required PB/PO discharges: **0**. PB-007-01/02/03/04 and PO-02/04/05/07/08 remain open; MC-B and MC-1 remain \`NOT_ESTABLISHED\`. All 26 supported operations remain in scope. Only a later separately authorized #397 integration and gate review can alter shared decision authority.

## Next engineering frontier

Source-native ingestion of arbitrary pinned V54 B-spline component specs (not only a manually compared V44 shape), rigorous handling of discontinuous coefficient splines with piece-sided physical values, and a terminating certified path for higher-order or non-quarterturn boundary zeros. Do not relabel a prospective proof as newly closed historical coverage.
