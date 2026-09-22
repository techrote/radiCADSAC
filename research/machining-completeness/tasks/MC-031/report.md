# MC-031 — Native sweep-to-material evaluator integration

Status: **COMPLETED_RESEARCH as bounded integration evidence; MC-B remains `NOT_ESTABLISHED`**.  
Issue: #93.  
Source baseline: `8cac00439bec4b8c6032be9709f81ac1bed21a7d`.  
Native/paid execution: **none**.

## Result

MC-031 now integrates the selected `PRIMARY_CERTIFIED_ADAPTIVE_IMPLICIT` material route with the **actual qualified MC-018..023 sweep/setup constructors** rather than duplicating them, replacing them with operation labels, or using mesh/voxel/directional observations as truth. The executable adapter dynamically loads those reviewed modules and the verifier freezes their Git blob identities. The frozen MC-026 denominator remains exactly 26 operation IDs and every ID has an explicit constructor-owner route.

This is a bounded material-evaluator integration result, not a theorem that every admitted request is now universally decidable. The accepted exact/bounded subtypes terminate with typed decisions; unresolved general coupled phase/eccentric membership, universal arbitrary form-source encoding, durable connectivity transitions, resource refusal and enclosure uncertainty remain explicit non-success outcomes.

## Actual constructor integration

Ordinary fixed-axis milling uses MC-018 flat/corner sweep objects and MC-058-certified leaves; ball/round milling uses MC-019; bounded form, accessible-undercut and fixed-axis helical-form requests use MC-020. The evaluator calls each task's existing `swept_path`/`certified_classify` machinery directly. MC-020 accessible-undercut requests additionally require the existing complete cutter-plus-holder access witness. A missing universal form/source codec terminates as `PB-007-03`; it cannot be replaced by an AABB/hull, label, sampling density or guessed tool family.

Conventional axisymmetric lathe requests use MC-021 only when its complete sufficient admission predicate is satisfied: source/body/setup binding, coaxial certified target, phase-independent meridian placement and full spindle orbit remain mandatory. Phase synchronization, eccentricity or another failed axisymmetry premise routes fail-closed as the surviving general coupled-membership obligation rather than being sampled into an axisymmetric answer. Bounded lathe form turning consumes an MC-020 `lathe_form_tool` source object and the MC-021 meridian sweep together.

Synchronized threading consumes MC-022's exact shared time/feed/unwrapped-phase constructor. General unresolved analytic events still propagate `PB-007-01` from the event route. MC-022 eccentric placement is constructed symbolically, but its finite/cardinal controls are not promoted into a universal point-membership solver: general eccentric sweep membership remains `PB-007-02`.

Multi-setup histories use the actual MC-023 `Workpiece`, `Cut`, `Setup`, `apply_cut` and `reclamp` objects. Exact input revision order, common-frame transforms, durable `body_id`/`lineage_id`, unrelated retained bodies and inherited error survive each preview. Backend component enumeration/order/size never becomes identity. Durable connectivity/body-transition commitment remains MC-033 ownership and is reported as propagated `PB-007-04`, not guessed by MC-031.

## Material and boundary semantics

A closed cutter-sweep membership result is not, by itself, authority to delete material. Regularized machining semantics require an independent exact positive-volume witness before an `INSIDE` sweep query commits removal. An exact zero witness is `TOUCHING_ONLY_NO_MATERIAL_TRANSITION`. The controls exercise exact tangent and signed `±1/1000000` neighbours for MC-018 flat milling, MC-019 curved ball/round milling and MC-021 rotational reduction.

The material algebra is monotone subtraction: machining cannot add material; `VOID` cannot become material; touching/no-hit preserves the prior state; and `UNCERTIFIED`, blockers or resource refusal cannot mutate canonical material. This prevents boundary coincidence, closed-set membership, tolerance or timeout from deleting positive-volume features or healing topology.

MC-058/MC-023 uncertainty is also preserved without reset. Every request supplies all terms of

`e_total = e_inherited + e_translation + support_radius * e_rotation + e_tool`.

A missing inherited term, negative term or binary floating-point correctness value is rejected. Re-clamp histories may not decrease inherited uncertainty.

## Adversarial controls

The self-test covers denominator shrinkage, exact tangent and signed-neighbour discrimination, nonlinear enclosure uncertainty, missing form-source authority, complete cutter/holder access, phase-vs-axisymmetry confusion, same-phase/wrong-feed synchronization, unresolved analytic events, symbolic eccentric non-totality, stale revisions, inherited-error reset, durable-connectivity deferral, wrong common frame, unbound source, backend topology identity, missing error terms, binary-float authority, refusal laundering and stale/mutated certificate bindings.

The contract separately rejects any attempt to make binary float, epsilon/global tolerance, sampling pitch/refinement depth, timeout/resource budget, accelerator observations or backend topology identity into truth authority. Directional, mesh/Manifold and sparse-level-set representations remain non-authoritative accelerators/challengers.

## Certificate binding

Material certificates bind input digest, canonical-source digest, actual-sweep digest, durable `body_id`, exact input revision, configuration digest, challenge identity and result under canonical JSON plus SHA-256. Body, revision, configuration or payload mutation invalidates the binding. Agreement with a challenger is evidence only; it does not override an `UNCERTIFIED` primary result.

## Remaining blockers and proof boundary

`PB-007-02` remains **OPEN** for general coupled spindle/feed/eccentric membership outside the bounded MC-022 subtype. `PB-007-03` remains **OPEN_PROPAGATED** for a universal exact finite source codec covering every required arbitrary form/imported cutter instance. `PB-007-04` remains **OPEN_PROPAGATED** for durable connectivity/body-transition certification owned by MC-033. MC-032's `PB-007-01` also remains live wherever its analytic event service cannot certify a required event; MC-031 does not claim ownership of or closure for it.

Consequently PO-02 remains **OPEN**: the bounded integration supplies reviewable evidence to its owner but does not erase the surviving universal sweep-semantic gaps. MC-A remains accepted; **MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`**. Production and expensive execution remain unauthorized.

No historical `research/rcs-*` evidence, source/audio/provenance material, canonical-journal meaning, positive-volume semantics, durable body/lineage identity or conventional STEP requirement was altered.

## Verification

```text
python3 research/machining-completeness/tasks/MC-031/verify.py --self-test
python3 research/machining-completeness/tasks/MC-031/verify.py --contract
python3 tools/mc_workflow.py verify MC-031
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The exact PR head must pass the repository `mc1-static` workflow before merge. After merge, the exact merged `main` SHA must pass that same required workflow before issue #93 may be closed.
