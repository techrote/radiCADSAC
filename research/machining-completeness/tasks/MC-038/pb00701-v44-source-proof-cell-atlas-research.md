# MC-038 / PB-007-01 — frozen V44 original-source proof-cell sign atlas

**Status:** 30 October 2026 — bounded deterministic exact-arithmetic research candidate; not a V44 route change or capability acceptance.  
**Parent:** [MC-038 / #100](https://github.com/techrote/radiCADSAC/issues/100).  
**Preselection:** [#6513430426](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6513430426).  
**Base main:** `89c187750081f9555fd3123e1e957830fea49b92`.  
**Parent proof:** [PR #310](https://github.com/techrote/radiCADSAC/pull/310) model Git blob `5d38a42fd8e23dc7930788e2b0c080caf567e851`.

## Purpose and actual gap

The frozen historical case `harvested:verify_pb00701_v44:ffaea08e30c9` is a genuine degree-2 rational B-spline-modulated trigonometric source. Its original source coordinate is `t in [0,1]`, source parameter `pb00701-v44-algebraic-orientation`, affine phase turns `-1/8+t/16`, original source SHA-256 `d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2`.

PR #310 already proves one simple physical root on the **original source** and exactly partitions it across three strict, source-bound rational/algebraic *proof cuts*. The physical root is in the second of four open proof cells, count pattern `[0,1,0,0]`. #310 is **not** a child analytic solver. The question for this candidate is whether a downstream *physical event/sign* consumer can be given a finite, explicit original-source coordinate cell interface **without** pretending to have reparameterized the analytic function over a real-algebraic coordinate.

## Hypothesis, proof argument and falsifier

**Hypothesis:** the already-certified complete root-set partition, plus physical nonzero values at every proof cut, suffices to derive one finite *source-coordinate sign/event atlas*. The only permitted new inference is continuity plus the complete root-set theorem: on each proof cell with count zero the physical sign is constant; on the unique count-one cell a simple root causes one crossing with the proven left/right signs.

Every cell references the original source parameter and its two exact ordered boundary descriptors. An irrational cut remains a square-free polynomial and isolating interval, not an invented rational point. No analytic function is re-expressed in a local algebraic chart; no zero is introduced at a proof cut.

The candidate checks independently of its output:

- the pinned #310 model, its transitive source pins, the exact frozen case source identity, phase, source interval, historical blocker and explicit nonpromotion fields;
- exactly three proof cuts / four proof cells, one distinct simple original-source root and exactly one occupied cell;
- external original-source endpoint signs match the certified root's left and right signs, with the exact simple-crossing derivative orientation;
- each proof-cut sign matches its exact order relative to the physical root, with exactly one algebraic cut whose V46 endpoint relation is nonzero and bound by #306's exact GCD/Sturm identity;
- all three proof cuts are event-neutral, remain strictly inside the original interval and preserve exact source parameter identity;
- every zero-free cell has identical nonzero end signs; the unique root cell has opposite nonzero end signs and retains the original source root witness;
- no chart or derivative theorem, historical v54 admission, PB-007-01/MC-B/MC-1, native engineering/STEP or production status may be claimed.

This atlas is a **logical corollary** of the existing frozen #310 proof. It is not an independent second root oracle and cannot generalize to arbitrary multiple roots, root-on-cut cases, discontinuous source spans or uncertified cut sets. If the existing proof refuses, this atlas refuses.

## Explicit consumer boundary

A consumer needing only a complete **source-coordinate physical root count, proof-cell membership, event-neutral nonzero cut endpoints or sign on a root-free original-source restriction** can potentially use this interface as a bounded research witness. A consumer requiring a bona fide V41/V47 *analytic child chart*, algebraic child-function representation, closed-child derivative certificate, independently qualified topology, or a changed historical route **cannot** use it to discharge that obligation. The output flags this distinction explicitly.

Consequently, an accepted result would **not** prove that the existing V41 child interface consumes the proof: that requires a separate exact adapter theorem and source-bound regression against the actual consuming route. This work only identifies which derivative-free information can be transferred faithfully without that adapter.

## Evidence / custody / negative controls

The only separately pinned new dependency is the landed #310 model Git blob `5d38a42fd8e23dc7930788e2b0c080caf567e851`. Its `pins()` re-verifies the frozen v54 corpus blob `5841c331579489b25caef38cd412bdbf286f9134`, 26-operation domain blob `23de82f5240a72509f7afe4acd5948b65bc4ff13`, no-production authority blob `fa0233323a0804d8a5d3eb7cd892a274a6173fab`, #296, #306, V44–V47, MC-032 and transitive dependencies. The frozen historical v54 disposition stays **BLOCKED**.

Adversarial tests mutate source SHA, affine phase, original-source endpoints, root multiplicity, proof-cut sign, ordering, number, event-neutrality, root-cell count, algebraic cut multiplicity, explicit nonpromotion fields and the proposed atlas itself.

**Source-report trust boundary:** simple local cardinality and sign checks cannot establish that a *supplied* rational/algebraic coordinate is actually a V41 source-owned proof cut. The consumer-visible atlas therefore checks the **entire** provided #310 report against #310's freshly recomputed, pinned `validate_report` before exporting any cut coordinate. A targeted falsifier substitutes a plausible, strictly interior rational coordinate (`1/128`) while retaining otherwise consistent root-side signs and metadata: local shape checks alone accept it, but full exact source replay must refuse. This is an additional provenance check, not another independent physical-root oracle.

**Retained development failure:** the first literal branch-head focused workflow [#40991984258](https://github.com/techrote/radiCADSAC/actions/runs/40991984258) failed a negative test because the proposed *mutation* of proof-cut relation 1 was already that relation's actual value (a no-op), not because the exact atlas theorem was contradicted. The test was corrected to mutate a genuinely later proof cut to a wrong before-root relation; subsequent exact-head CI must prove the correction. Resource refusal is a nontruth result, not a zero or an accepted cell. All earlier #310 failed heads / corrections remain preserved in its memo and issue checkpoint.

## Verification / review / landing

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v44_source_proof_cell_atlas.py --contract --self-test
```

Required before merging: focused literal-head CI, `mc1-static`, technical/source review of the final exact head, expected-head-protected merge, reviewed/synthetic/landed tree identity, and actual merged-main focused/static checks. Any failed experiments remain in a durable attempt ledger. This research adds no native or paid campaign.

The stable 26-operation MC-1 domain, source/provenance/phase/canonical journal/material/body/lineage/refusal/UNCERTIFIED and conventional STEP obligations remain fully in force. MC-B and MC-1 are **NOT_ESTABLISHED** and `production_authorized=false`.
