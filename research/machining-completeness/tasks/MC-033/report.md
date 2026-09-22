# MC-033 — Regularized material bodies, durable lineage and finite-history state

Status: **COMPLETED_RESEARCH** as a bounded programme-owned body/lineage state implementation; no capability gate is promoted.  
Issue: #95.  
Source baseline: `46b84622bccc2ae68f4a68042480b3d2d5d6de9b`.  
Native/paid execution: **none**.

## Hypothesis and falsification criterion

MC-033 tests a narrow implementation hypothesis from the MC-026 `MC033-A/B` blueprints: once material and critical connectivity facts are independently certified and bound to the canonical source/revision, a finite pure-removal machining history can commit durable body and lineage transitions without leaking kernel/private identity into product semantics.

The implementation is falsified by any control that can merge touching bodies, drop a positive-volume component, round a positive residual to empty, create a body from a zero-volume artifact, revive/reuse an exhausted identity, select continuity from provider topology/order/size/proximity, accept stale or mutated certificate bindings, or mutate canonical state after a non-success terminal.

This is intentionally not a claim that MC-033 can generate all required connectivity evidence. `PB-007-04` remains the universal topology/connectivity proof boundary.

## Authority and inputs

The formal task dependencies remain unchanged: accepted MC-005/MC-A capability plus the reviewed MC-026 and MC-015 artifacts. MC-031 and MC-032 are auxiliary producing-owner inputs established by the recorded MC-038 repair path: MC-031 emits source/body/revision-bound material certificates and marks body-transition commitment as owned by MC-033; MC-032 emits event certificates and similarly defers durable transition commitment.

`body_state.py` accepts only cryptographically bound JSON-compatible certificate objects. Durable identity authority is `canonical_journal`; backend topology IDs, kernel handles, tessellation components, enumeration order, largest-component selection and geometric-nearest/proximity matching are not identity sources. Authority-path volume quantities are exact rationals; binary floating point, epsilon, tolerance, timeout and resource exhaustion are not correctness predicates.

## Regularized pure-removal state semantics

The state machine implements the material semantics already frozen by MC-A: regularization removes lower-dimensional artifacts, not positive-volume material. A durable body record is not a provider component. Historical records remain present after a body stops carrying active material.

Four transitions are executable:

- `CONTINUE` — one explicit continuation retains the same `body_id` and `lineage_id` while advancing the material/revision certificate. This is the ordinary remachining path.
- `SPLIT` — requires positive new removal, at least two certified positive-volume remainder components, a complete pairwise-interior-disjoint partition certificate and explicit identity assignments. At most one output may be an explicit continuation of the parent; every other output receives fresh body and lineage IDs plus a programme-owned parent→child lineage edge. No heuristic chooses the continuation.
- `DISAPPEAR` — requires exact empty material, zero certified residual positive volume and no positive output body. The body becomes `EXHAUSTED`; its durable ID and lineage remain recorded. No epsilon residual or placeholder solid is invented.
- `TOUCH_ONLY` — requires exact zero new removal and an MC-032-compatible touching decision. It records a contact relation between two existing durable bodies without merging or reinterpreting either identity.

Pure-removal `MERGE` is not a transition: machining cannot fuse two previously distinct durable bodies or add material. An exhausted body cannot later be revived by a removal operation. Durable IDs and lineage node IDs are globally unique and never recycled, including after exhaustion/supersession.

## Certificate chain and finite history

A committed transition binds input/output revision, target body and lineage, source/canonical identity, material certificate, event certificate when relevant, independent connectivity certificate, configuration and challenge identity. Nested MC-031/MC-032-style bindings are rechecked before commit. Missing or mutated evidence fails closed.

The independent connectivity certificate must state `PROVED`, bind the same target/revision/material/event evidence, and use canonical-journal identity. Split evidence additionally binds exact component count, complete remainder coverage, pairwise interior disjointness and the exact component-certificate ID set. A missing proof returns a typed `BLOCKED` result rather than assigning provider topology as truth.

`finite_history` processes certificates strictly in journal/revision order. The first `BLOCKED`, `UNCERTIFIED`, `RESOURCE_REFUSAL` or semantic rejection stops the history, and the rejected step leaves the prior immutable state unchanged.

## Boundary and adversarial controls

The deterministic verifier exercises an exact `1/1000000` positive split, explicit descendant remachining, exact-zero contact, exact disappearance and durable exhausted-state retention. It attacks positive residual `1/1000000` rounded to empty, zero-volume split children, binary-float volume authority, backend identity, a forbidden merge, stale revisions, nested certificate mutation, identifier reuse, missing/unknown connectivity proof and non-success terminal mutation.

The split controls verify both explicit parent continuation plus fresh descendant lineage and the rule that all output components are independently accounted. Touching preserves both bodies even where their boundaries coincide. Disappearance proves that `EMPTY_MATERIAL` means no active positive-volume body while historical durable identity remains queryable.

No native geometry or paid campaign is required to test these programme-owned state/certificate invariants; none was run.

## What this does not close

`PB-007-04` remains **OPEN_PROPAGATED**. MC-033 is a consumer/committer of independently certified connectivity facts; it is not a universal topology decision procedure. Consequently global PO-07 remains **OPEN** under MC-032 integration ownership.

The nominal state machine also does not qualify engineering output. `RB-016-02` remains open for native/disconnected multi-solid body mapping through independent consumption, `RB-016-04` remains open for exact-zero/touching/singular engineering-output evidence, and `RB-016-05` remains open for downstream empty-output evidence. MC-054's profile decisions remain intact; they are not substituted by this nominal state result.

`PB-007-01`, `PB-007-02` and `PB-007-03` remain unchanged under their existing owners. MC-A remains accepted; **MC-B through MC-F and MC-1 remain `NOT_ESTABLISHED`**. Production and expensive execution remain unauthorized.

## Protected semantics

No historical source/audio/provenance or Genesis evidence is rewritten. Canonical-journal meaning, source-to-revision binding, positive-volume material semantics, immutable chronology, durable body/lineage ownership and conventional STEP requirements are preserved. Provider/private identifiers remain derived observations only.

## Verification

```text
python3 research/machining-completeness/tasks/MC-033/verify.py --self-test
python3 research/machining-completeness/tasks/MC-033/verify.py --contract
python3 tools/mc_workflow.py verify MC-033
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The exact PR head must pass `mc1-static` before merge. The exact merged `main` SHA must pass the same workflow before issue #95 may be closed.
