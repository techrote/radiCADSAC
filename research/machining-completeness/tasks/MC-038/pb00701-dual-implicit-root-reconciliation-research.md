# MC-038 / PB-007-01 — dual-producer same-source implicit-root reconciliation

**Status:** 29 October 2026, isolated deterministic research candidate. **Parent:** [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Preselection and falsifiers:** [issue checkpoint #6507006755](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6507006755). **Original base:** 95d26ecdf7b0e0e915f7bfab4d810408421f7300.

## Objective and theorem

The existing [pinned V27/V41 source-view checker](https://github.com/techrote/radiCADSAC/pull/294) and [complete transverse rational-interval verifier](https://github.com/techrote/radiCADSAC/pull/296) provide different **root proof methods** for the same three frozen original-source records. Each reconstructs one exact physical function and proves a complete increasing list of exactly two simple open zeros on its whole original source interval.

For one fixed function F, the k-th zero in two *complete*, independently proved increasing zero sequences must be the **same physical zero**. Hence the intersection of its two strict rational isolating intervals is another valid strict rational isolating interval. This is the exact root-rank uniqueness argument. Mere bracket intersection, by itself, is NOT proof of root equality: different roots can inhabit the nonoverlapping tails of overlapping brackets. A conflicting or disjoint same-rank bracket must refuse, not pick an approximation.

This step verifies both original producers afresh; reconstructs the bound source, source-parameter ID, rational affine phase and physical owner; reconciles counts, order, multiplicity, crossing direction and maximal sign cells; verifies V27's nonzero physical knot; and returns narrower strict rational brackets without assigning a closed-form coordinate or inventing authority for the original historical child.

## Source custody and honest independence

The read-only frozen v54 corpus is pinned at Git blob **5841c331579489b25caef38cd412bdbf286f9134**, current authority at **fa0233323a0804d8a5d3eb7cd892a274a6173fab**, 26-operation domain at **23de82f5240a72509f7afe4acd5948b65bc4ff13**.

Pinned proof producers: pinned_trig_child_views blob **c4a4d865226d01858d93685aa770987b14460e0b**; transverse_original_source blob **992ad17ddbdf34687bcb59acba46f672b2d4a1c4**; transverse_trig_interval blob **2320f92efe4316d865a89f6d848737e2c000ca4d**. Their own source/proof dependency checks remain active.

The two producers serialize their independent source-binding hashes differently: one labels the source key **case_id**, the other **id**. These unequal hash values are not misrepresented as equal. Each is separately checked against its canonical reconstruction of the **same pinned source record**. The methods share historical source-lowering and custody routines; the research is a dual-method root cross-check, not an independently developed geometry kernel, independent physical experiment or independent human review.

## Scope and negative results

Admits only the pinned V27 tail0, V27 tail100 and V41/V13 harvested original-source cases. The exact comparison of root ranks applies only **within one unchanged physical source**, not across unrelated sources even if source-coordinate numbers overlap.

This is NOT a general V27/V41 nested-child composition theorem. Non-simple/tangential/identity-zero roots, discontinuous or zero-valued source knots, nonrational phase samples without certified global event completeness, unknown owners, unsupported grammars, overlap-only claims, source hash/phase mutations and resource limits must fail closed. Historical v54 count-only certificates are never promoted to root-order evidence. Original 121 frozen cases, 43-owner inventory and all earlier dispositions remain unchanged.

All 26 machining operations, manufacturing source/provenance/phase, canonical journal, material/body/lineage, refusal and UNCERTIFIED rules and conventional STEP engineering-output obligations remain unchanged. PB-007-01, MC-B/MC-1, native topology/B-rep and usable STEP remain unqualified. Production authorization false. No native or paid campaign.

## Execution and landing gates

The deterministic verifier includes mutated root lists/ranks, false ownership/phase/source, wrong signs/intervals, gate promotion, noncanonical values, unsupported comparison and resource refusals.

Run:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_dual_implicit_roots.py --contract --self-test

Required: literal-PR-head focused CI and MC-1 static, distinct source/proof technical review of final head, exact tree reconciliation, expected-head-protected merge, merged-main focused/static CI, and durable issue #100 checkpoint. No gate advancement is implied by research acceptance.
