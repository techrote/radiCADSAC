# MC-038 / PB-007-01 — exact source-tail contrast and root noncoincidence

**Status:** bounded deterministic exact-source research candidate, 29 October 2026. **Owner:** [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Preselected hypothesis/falsifiers:** [#6508665183](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6508665183). **Selection main:** `5828d44fb02561e4eb34f7afd21be2bf40507f4f` after reviewed/merged #301. No implementation or capability promotion is implied by this memo.

## Question and mathematical result

The two original frozen V27 composite source records `tail0` and `tail100` share the first restriction but differ on their second source span, `1 <= t <= 2`. Prior #300 established second-root ordering by **disjoint strict rational isolation brackets**; #301 proved the first roots mathematically identical from the exactly shared first source restriction and independent unique-root witnesses.

This research supplies a second and logically different sufficient theorem for the **different** second roots: if two exact physical functions `F_L` and `F_R` on one exact source parameter interval each have independently checked **exactly one simple negative-to-positive root**, and an exact source-derived witness proves `F_R(t)-F_L(t)>0` at every interior point, then their roots cannot coincide and `root(F_R)<root(F_L)`. At `root(F_L)`, `F_R>0`, while `F_R` is negative before its sole crossing; its root must precede `root(F_L)`. This does **not** require the two strict root brackets to be disjoint and does **not** imply they are the same physical machining event or part of a common manufacturing clock.

## Original-source evidence, not inferred ownership

The executable model re-lowers all original rational B-spline cosine and sine harmonic channels from **both** frozen full source rows, using the pinned original-source proof/lowering dependencies, rather than hand-writing a desired function. Both use the original parameter `source-time-t`, affine phase turns `1/2 - 2t/3`, the same [1,2] second restriction, and complete harmonic indices 0, 1, 2.

Crucially, the **original second span owners differ**: `tail0` has `PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION`, and `tail100` has `PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR`. The model checks these distinct historical owner labels; it never relabels the two source records as one common owner.

Exact source subtraction checks **every** harmonic and every cosine/sine polynomial. Every nonzero-harmonic difference and every sine difference is identically zero, leaving only harmonic-zero cosine polynomial

```text
F_tail100(t) - F_tail0(t) = -100 + 100 t = 100(t-1).
u := t-1,  0 <= u <= 1.
D(1+u) = 100u,  knot order = 1.
D(1+u) / u = 100;  Bernstein coefficient on [0,1] = [100] > 0.
```

The positivity checker is a general bounded **sufficient** rational-polynomial witness: translate `t=1+u`, remove exact `u`-adic vanishing order, convert the remaining polynomial to the Bernstein basis on [0,1] with exact rational binomial coefficients, and require every Bernstein coefficient strictly positive. Since Bernstein basis functions are nonnegative and sum to one, this proves strict positivity on `0<u<=1`. A missing or undecidable Bernstein witness refuses; it never asserts sign change or equality.

Both original second-span checked interval proofs are recomputed and require **one and only one** simple negative-to-positive open root, with nonzero negative left endpoint and positive right endpoint. Existing source-bound #299 dual-proof records are replayed as an independent-root-method corroboration; **their disjoint interval separation is not used in the contrast-order argument**. The right source crosses first, then the left, without sharing a zero. The two functions agree at the source knot `t=1`, which is **not** a physical zero in these pinned inputs.

## Precise boundary and falsification

This theorem is a conditional **shared-coordinate mathematical contrast** on two pinned original source histories. It does not prove equality/inequality or order of arbitrary coincident implicit/algebraic roots, nontransverse open tangencies, general nested-child composition, physical event chronology, finite-history material, geometry or STEP. It is not a generic decision algorithm for trigonometric functional equality or polynomial positivity. A failing Bernstein witness is `BLOCKED`, not evidence the function changes sign. Source owner differences remain explicit.

Negative controls require rejection of changes to the original source phase, parameter, span, nonconstant-harmonic coefficients or historical second-span owner, as well as a sign-reversed contrast, a polynomial with interior sign change, identity-zero contrast, nonzero knot contrast, forged root order or source hash, wrong isolation/positivity witness, shared physical event/clock or journal, false capability promotion, noncanonical/nonfinite claims and resource excess. Mutation controls never edit the frozen corpus or historical evidence.

## Exact custody and verification

- Frozen v54 121-case corpus Git blob: `5841c331579489b25caef38cd412bdbf286f9134`; all historical dispositions remain untouched.
- Required 26-operation MC-002 domain Git blob: `23de82f5240a72509f7afe4acd5948b65bc4ff13`.
- Current no-production authority Git blob: `fa0233323a0804d8a5d3eb7cd892a274a6173fab`.
- Pinned original-source transverse producer: `992ad17ddbdf34687bcb59acba46f672b2d4a1c4`; pinned same-source dual-root verifier: `9a7aee7f784e9aa37b4348b2bd78f047ba885fd4`. Each producer verifies its own transitive historical source/proof dependencies.
- Deterministic test entry point:

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v27_tail_contrast.py --contract --self-test
```

**Landing gate:** exact-head focused and `mc1-static` success, distinct current-head technical proof review, reviewed/synthetic/landed tree identity, expected-head-protected merge and merged-main checks, then an issue #100 custody checkpoint. A COMMENT review by the owner account may document AI-assisted technical review, but is not a separate human approval.

**Explicit nonclaims:** PB-007-01 and issue #100 stay **OPEN**; MC-B/MC-1 remain `NOT_ESTABLISHED`; `production_authorized=false`. No native/paid campaign or production repo. The full 26-operation lathe/mill domain, source/provenance/phase, canonical journal, material/body/lineage, typed refusal and `UNCERTIFIED`, and conventional usable engineering B-rep/STEP obligations remain in force. Further general nontransverse/coincident-event work belongs under existing #100 and must retain these unknowns.
