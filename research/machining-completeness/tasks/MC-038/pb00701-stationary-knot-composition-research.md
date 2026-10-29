# MC-038 / PB-007-01 — exact stationary polynomial source-knot composition (research only)

**Date:** 29 October 2026. **Owner:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Base:** `2050cb80fe6dee79c5a9baafbf7dbe27a170d7b2` (reviewed PR #294). **Evidence class:** deterministic-model mathematics, NOT native material or engineering geometry.

## Question and result boundary

[PR #281](https://github.com/techrote/radiCADSAC/pull/281) produced exact Sturm-isolated ordered roots, rational/implicit algebraic descriptors, derivative/GCD multiplicities, endpoint inward signs and complete sign cells for three frozen original stationary-cardinal B-spline sources. Two are multiple-span `BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE` cases in the immutable v54 corpus. Those per-span views alone do not constitute a source-knot composition witness.

This research consumes that **specific pinned exact polynomial owner** and implements the mathematically separate conditional source-knot join. It independently regenerates/validates each complete ordered view, proves continuity by exact equality of the two local original physical polynomials at their true shared source parameter, orders interior rational or implicit algebraic zeros by strict source-span/isolating bounds, and counts a physical zero at a source knot exactly once. It keeps left and right one-sided vanishing orders separate and derives crossing versus touching from verified inward signs—not from a fabricated whole-source smooth multiplicity.

The integrated replay processes **three** frozen source records; **two** retain their historical v54 multi-span `BLOCKED` dispositions despite having a separate research-only checked composed view. It does not change the historical interpreter, emit V55, or let historical owner counts certify new evidence.

## Exact mathematical contract

For a finite contiguous sequence of original-source polynomial pieces (p_i(u)) with local (u\in[0,1]), each piece supplies a **complete independently checked Sturm ordered view**. At a true original source knot (k) between adjacent pieces require (p_i(1)=p_{i+1}(0)) as exact rationals.

If the common value is nonzero, both one-sided signs are equal and the knot is not a root or a sign-cell boundary. If zero, the knot contributes **one** physical root, with separate positive integer left/right vanishing orders (m_L,m_R) and separately checked inward signs (\sigma_L,\sigma_R). The physical event crosses iff (\sigma_L\ne\sigma_R); otherwise it touches. No global multiplicity or differentiability order is asserted at the knot. Each strict interior root retains either its exact rational source coordinate or its defining squarefree polynomial and strict rational source-isolation interval; the latter is **not** silently rewritten as a numerical or rational coordinate. Endpoint zero events are explicitly distinguished from open physical roots. An identically-zero interval is not a discrete-root list.

Proof cuts and nonzero knots never become physical roots. Maximal open physical sign cells extend across nonzero knots; zero knots and exact interior roots bound the cells. Source-span intervals must be exactly contiguous; gaps, overlaps, discontinuity and contradicted side signs fail closed.

## Proof and provenance custody

- Source-bound #281 prover: `verify_pb00701_stationary_polynomial_order.py` Git blob `0954c5e1ad63ec1c8dd2acb3202882650b02c516`. Its own dependency pins include the original B-spline lowerer and affine identity helper.
- Frozen v54 121-case original source corpus Git blob `5841c331579489b25caef38cd412bdbf286f9134`.
- MC-002 complete 26-operation domain blob `23de82f5240a72509f7afe4acd5948b65bc4ff13`.
- Current authority blob `fa0233323a0804d8a5d3eb7cd892a274a6173fab`, MC-B/MC-1 `NOT_ESTABLISHED`, production authorization false.
- Full original-source candidate is regenerated through #281 `build_source_candidate`, `validate_source_candidate` and `source_stationary_spans`. The entire source-ordered view is regenerated again inside the join, rather than accepting an unverified count, status or self-declared owner.
- Synthetic, exactly evaluated polynomial controls test a nonzero knot, two zero-knot crossings with equal or differing left/right order, a touching zero-knot, repeated interior tangency, an irrational algebraic root, physical endpoint zero, source gap/overlap/discontinuity and forged/missing root or sign. Those controls prove the *join logic*, not independent original-source provenance.

**Reproduce:**

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_stationary_knot_composition.py --contract --self-test
```

## Falsification, resource and nonpromotion

Incorrect original source, phase, lowerer/prover/corpus/domain/authority pin or historical owner/disposition; omitted, reordered or forged root; changed polynomial coefficients, multiplicity, sign, source map or knot; invented cross-knot smooth order; zero interval; and incompatible closed-source continuity must not certify. The composition has bounded spans/root count and explicit typed `RESOURCE_REFUSAL` as nontruth. Malformed or contradicted witnesses raise a deterministic invalid-evidence error, never `CERTIFIED`.

This restricted stationary polynomial source-knot result is **not** a generic V27/V41 analytic/trigonometric nested-child verifier, a universal event proof, a historical v54 route acceptance, or a complete PB-007-01 claim. The three fixed V27/V41 trigonometric child cases from [PR #294](https://github.com/techrote/radiCADSAC/pull/294) remain separate. No MC-B/MC-1, native material/topology, B-rep, conventional usable engineering STEP, or production authority is promoted. The 26 machining operations and canonical journal/source/phase/provenance/material/body/lineage/refusal/`UNCERTIFIED` semantics are unchanged.

## Next necessary proof

An independently checkable complete ordered witness for the **actual general trigonometric child source grammar**, including arbitrary implicit/algebraic root comparison and completeness, is still missing. Replaying fixed cases or joining stationary polynomials does not supply that premise. Any such generalization must retain source-bound proof authority and typed refusal rather than inheriting historical child root counts.
