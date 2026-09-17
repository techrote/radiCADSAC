# RCS-018 — integrated semantic contract vertical-slice report

Status: accepted on `main`; implementation merged via PR #48  
Date: 2026-09-17  
Issue: RCS-018 / GitHub #37  
Experiment contract: `rcs-018-experiment-plan/1.0`  
Evidence contract: `rcs-018-integration-evidence/1.0`

## Purpose and scope

RCS-018 tests whether the accepted Genesis-v1 contracts can be composed as one research transaction path before production repositories harden them into implementation structure. The executable slice covers canonical journal ingress, immutable revisions, durable material-body IDs, semantic lineage, provider dispatch, bounded pending/reconciliation state, process isolation, replay, fault mapping and STEP handoff.

This is deliberately not production OpenSimachinist. It selects no RPC/ABI, database, scheduler, UI, Godot integration or new geometry kernel. Provider adapters point to accepted RCS-010/RCS-011 evidence so this issue tests semantic seams rather than duplicating those geometry campaigns.

## Baseline and protected semantics

The baseline is `semantic-provider-hybrid-v1`. The durable authority remains:

- canonical `msac-journal/1.0` manufacturing intent;
- immutable revision history;
- durable material-body identity and explicit split/merge transitions;
- semantic lineage independent of topology IDs;
- versioned tool/setup/policy references.

The slice preserves the RCS-005 default that STEP body selection is all material bodies unless the caller explicitly asks for a subset. Genesis-v1 handoff trees and their freeze identities are not modified.

## Hypotheses and falsification

**H1 — contract composition.** Programme-owned journal/revision/body/lineage semantics can execute without OCCT, Godot or provider-private object identity entering durable state. Any requirement for such identity falsifies H1.

**H2 — pending-state seam.** `accepted_pending` can remain a transaction/reconciliation status while the committed journal stays unchanged until reconciliation/acceptance. A failed derived attempt changing committed history falsifies H2.

**H3 — replay.** Derived provider state can be discarded and reconstructed from programme authority while preserving the J2 engineering invariant: statuses, material-body mapping and semantic lineage. Replay divergence falsifies H3.

**H4 — process containment.** Success, provider error, crash and timeout can cross a process-isolated worker boundary as stable programme statuses without worker identity becoming project meaning. Durable mutation on a failed attempt falsifies H4.

## Executable scenarios

### Lathe trace

The slice consumes `research/rcs-002/fixtures/lathe-finishing-pass-v1.json`. Setup and both turning operations retain immutable setup/tool/normalization references and `body:stock`. Turning dispatch uses the accepted `lathe-axisymmetric-provider@rcs-010` research profile.

The repeated finishing pass remains a distinct journal operation even though a provider may prove it removes no new material. This preserves RCS-002 and RCS-008 provenance semantics.

### Mill pending → reconciled trace

The slice consumes `research/rcs-002/fixtures/mill-cut-through-v1.json`. `milling.general` first returns `accepted_pending`; the durable authority is still the parent revision. A successful process-isolated provider adapter then permits a `reconciled` transition and only then is the operation committed.

This is the concrete integration interpretation of RCS-002 plus DR-0012: pending/deferred geometry is replaceable derived state, while the journal remains durable authority. No new journal schema meaning is introduced.

### Body split

The cut-through commit consumes the fixture's explicit `material_body_transition`. The final revision contains exactly `body:left` and `body:right`; lineage records a `split` relation from `body:stock`. No first/largest/primary-body shortcut exists.

### Undo/replay and derived-state destruction

The harness reconstructs the selected revision from committed operation/revision/lineage data, hashes the programme engineering invariant, discards that derived result, and reconstructs it again. The two derived hashes must match.

Navigation to an earlier immutable revision does not rewrite history. Rebuilding later derived state is therefore independent of provider cache lifetime.

### Worker supervision and fault injection

Every process-motion scenario routes through a child process. Before the successful provider-adapter attempt, deterministic injected provider error, hard process exit and timeout cases are executed.

They map respectively to `kernel_error`, `crash` and `timeout`. The durable-authority SHA-256 is compared before and after every failed attempt and must be unchanged. Diagnostics may contain return codes; durable journal/revision/lineage state may not contain worker/process identity.

### STEP handoff

The slice evaluates RCS-005 Layer A semantic preconditions from the committed/reconciled state and body selection. It does not falsely claim to generate new serialized geometry.

For Layers B and C, the handoff identifies the accepted automated profile evidence from RCS-006 and the provider campaigns. Layer D remains `interoperability_unqualified` because RCS-022 has not yet qualified the exact exporter profile with an independent parser/downstream consumer.

A pending request fails closed with `RECONCILIATION_UNRESOLVED`. Unknown or duplicate body selections fail with `BODY_SELECTION_INVALID`. Default selection preserves all bodies, including both `body:left` and `body:right`.

## Adversarial and boundary validation

`tools/validate_rcs018.py` adds checks beyond the happy path:

- two clean executions must produce identical evidence;
- injecting a `TopoDS_*`-style ID into durable evidence must be rejected;
- duplicate durable material-body IDs must be rejected;
- a pending STEP request must not advance to serialization;
- unknown or duplicate STEP body selections must be refused;
- error/crash/timeout attempts must preserve the exact durable-authority digest;
- Layer D must remain explicitly `interoperability_unqualified`;
- the mill trace must contain `accepted_pending` → `reconciled` → `success` in order.

These are contract-boundary tests rather than visual or “writer returned success” tests.

## Findings

**MEASURED by this harness:** the two accepted RCS-002 fixtures compose through the research semantic path deterministically. The mill path reaches explicit `accepted_pending` and then `reconciled` before commit. The cut-through replay preserves both durable bodies and split lineage.

**MEASURED by this harness:** provider error, crash and timeout are contained without changing durable authority.

**MEASURED by this harness:** derived replay can be discarded and rebuilt with the same programme-level invariant for the exercised fixtures.

**INFERENCE:** there is **no foundational contradiction** among the exercised Genesis-v1 journal, lineage, deferred-state, provider, worker and STEP status contracts. The integration seam can be implemented without private kernel identity in saved meaning.

**INFERENCE:** `accepted_pending` should remain a programme transaction/status concept backed by replaceable pending provider state. It must not be interpreted as permission to serialize a partially reconciled state or as a hidden mutation of the immutable committed revision graph.

## What this does not prove

This result does not prove:

- realistic lathe tool-envelope coverage; RCS-020 owns that;
- arbitrary freehand mill fallback correctness; RCS-021 owns that;
- independent STEP Layer-D interoperability; RCS-022 owns that;
- complete propagated error budgets; RCS-023 owns that;
- provider-handoff/repeated-defer resource behavior; RCS-025 owns that;
- Windows/Linux scale, soak or recovery qualification; RCS-026 owns that.

The worker probe validates semantic containment and status mapping. It is not evidence that a new geometry algorithm is correct. Geometry evidence remains owned by the accepted predecessor campaigns.

## Contract reconciliation

No accepted Genesis-v1 contract needs to be superseded by this result.

The integration clarification is:

1. `accepted_pending` is observable before durable commit for a transaction that still requires reconciliation;
2. pending provider/deferred topology remains replaceable derived state;
3. a successful reconciliation may then produce the immutable committed revision/body transition;
4. failure before commit leaves journal authority unchanged;
5. STEP remains a hard reconciliation boundary.

This is consistent with RCS-002 transaction semantics, DR-0012 and RCS-013's engineering-status model. It should be carried into RCS-025 and RCS-026 as a testable coordinator invariant.

## Implications for RCS-025

RCS-025 can reuse `rcs-018-integration-evidence/1.0` and the same authority/status separation while adding real provider transitions, repeated defer/reconcile cycles, error-budget propagation and resource measurements. It must not promote provider-private pending IDs into durable lineage.

## Implications for RCS-026

RCS-026 can use the worker failure modes and replay invariant as the minimal cross-platform fault-recovery subset. Windows/Linux qualification must preserve programme statuses and body mapping even when process return codes, topology decomposition or implementation diagnostics differ.

## Reproduction

From repository root:

```bash
python3 research/rcs-018/vertical_slice.py --output /tmp/rcs018-evidence.json
python3 tools/validate_rcs018.py
```

Both commands require only the Python standard library. CI runs the validator and uploads the generated evidence as a research artifact.

## Decision impact

Gate-5 item 1 receives positive integration evidence for the bounded Genesis-v1 semantic slice. This does not declare Gate 5 complete.

The selected semantic-provider hybrid remains coherent for the exercised seams. No production transport/persistence/scheduler choice is made, no Genesis-v1 handoff identity is rewritten, and unresolved capability/qualification items remain assigned to RCS-019 through RCS-027.
