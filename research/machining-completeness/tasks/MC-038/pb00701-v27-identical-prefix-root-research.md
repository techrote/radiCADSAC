# MC-038 / PB-007-01 — identical V27 first-span source and unique-root identity

**Status:** 29 October 2026. **Class:** bounded deterministic exact-source model research, not historical V27 certificate promotion. **Owner:** [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Selection / falsifiers:** [checkpoint #6508037183](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6508037183). **Base:** \`8b50e05c6a26e6f34b384b27d4d7b4dc6ef166a2\` after reviewed #300.

## Mathematical question

Prior #299 checked two complete implicit-root proof methods *within* each of three frozen original sources. Prior #300 compared root **parameter numbers** across *different* source records when strict rational isolation brackets are disjoint, refusing overlap.

The frozen V27 \`tail0\` and \`tail100\` records are distinct full two-span histories but their first physical source-span functions are EXACTLY EQUAL on \`0 <= t <= 1\`. This is a special, limited positive root coincidence case that cannot be admitted just from overlapping isolating brackets.

## Exact original-source restriction proof

Re-lower the complete original source B-spline channels for both frozen records using the source-bound exact V27 lowerer; preserve all harmonics and their original cosine/sine coefficients and the rational affine phase. The first-span coefficients after removing trailing zero polynomial coefficients are the same in both records:

| Harmonic h | cos coefficient polynomial | sin coefficient polynomial |
|---|---|---|
| 0 | 5 | 0 |
| 1 | 0 | 2 + 4t |
| 2 | 1/100 | 0 |

Both have phase **turns** \`1/2 - 2t/3\`, source parameter \`source-time-t\`, source interval \`[0,1]\`, and original V27 owner. Thus their exact first-span physical function is

\[
F(t)=5+\frac{1}{100}\cos\bigl(4\pi(1/2-2t/3)\bigr)
+(2+4t)\sin\bigl(2\pi(1/2-2t/3)\bigr).
\]

Coefficient equality under the identical phase map is a sufficient theorem for equality of functions at every point of this restriction. It is not claimed as a necessary test for arbitrary algebraically equal trigonometric representations. Different B-spline degrees/control encodings for the two histories are interpreted exactly, not compared as raw control arrays.

Each original first-span source independently runs the interval derivative/sign partition verifier (#296), proving exactly one simple open positive-to-negative root and nonzero endpoint signs; the independently checked #299 complete root reports also each contain precisely one first-span root. Therefore both first-span roots are the unique zero of the **same exact restricted function** and are mathematically identical. The intersection of their strict rational uniqueness brackets remains a strict rational bracket. Equality does not follow from overlap alone.

## Divergent second spans

On \`1 <= t <= 2\`, \`tail0\` has constant h=0 cosine coefficient 5, but \`tail100\` has \`5 + 100(t-1)\`; their second-span source expressions are not identical. Replaying the source-bound #300 strict separation verifier confirms the \`tail0\` second root has a GREATER original source-parameter number than \`tail100\`'s second root. No equality or physical shared-event claim is made beyond the first restricted mathematical function.

This supports **shared-prefix / divergent-tail root identity**, not shared machining chronology, a common journal, material lineage, actual separate-scenario physical event equality, or global V27/V41 composition.

## Source and proof custody

Historical frozen v54 source corpus Git blob \`5841c331579489b25caef38cd412bdbf286f9134\` remains untouched, including all 121 source dispositions and the 43-owner inventory. The three independently required producer source files are pinned:

- #299 dual-complete root verifier: \`9a7aee7f784e9aa37b4348b2bd78f047ba885fd4\`.
- #300 strict cross-source root order: \`2ed13e8aa5ab3223af147250ecacc4688194c8d8\`.
- #296 original-source transverse interval binding: \`992ad17ddbdf34687bcb59acba46f672b2d4a1c4\`.

These producers pin their own unchanged lowerers, proof helpers, original source corpus, domain and programme authority. Historical input/proof verification is replayed; a supplied count-only certificate is never trusted. Source SHA-256 bindings of the **different full original records** remain distinct, despite their exact matching first-span function.

Required 26-operation domain Git blob \`23de82f5240a72509f7afe4acd5948b65bc4ff13\`, no-production authority Git blob \`fa0233323a0804d8a5d3eb7cd892a274a6173fab\`, and current MC-B/MC-1 NOT_ESTABLISHED state remain unchanged. The proof methods share original-source lowering/custody code, so this is neither an independent human review nor an independent native kernel.

## Negative controls, refusals and reproducibility

Adversarial tests mutate the first-span amplitude harmonic channels, source parameter, affine phase offset/rate, interval bounds, historical owner and source root/proof assertions; reject forged equalities, false shared machining clocks, invented closed-form coordinates, promoted gates, nonfinite/oversized reports, and coincidence claimed from mere bracket overlap.

\`\`\`sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v27_prefix_root_identity.py --contract --self-test
\`\`\`

A failing proof must refuse without supplying a root truth value; resource exhaustion must not count as proof. The required landing sequence is literal-head focused CI and mc1-static, distinct current-head technical source review, matched synthetic merge and reviewed head, expected-head-protected merge, actual merged-main focused/static CI and a durable #100 checkpoint.

**Explicit nonclaims:** No general nontransverse open-root completeness, no arbitrary cross-owner coincident implicit-root equality, no general V27/V41 nested-child composition or PB-007-01 certification. MC-B and MC-1 remain \`NOT_ESTABLISHED\`; production false. The 26-operation domain, original source/provenance/phase, canonical journal, material/body/lineage, refusal/UNCERTIFIED, native B-rep and usable conventional engineering STEP requirements remain intact.
