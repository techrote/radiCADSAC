# MSAC v2 clean bootstrap issue graph

Every issue below is an autonomous implementation prompt. For each: read this v2 handoff package, resolve imported fixtures/results through `handoffs/evidence-dependencies-v2.1.json` (exact source commit + blob SHA), and then read referenced accepted evidence; inspect current `main`; create a dedicated branch; implement deterministic/adversarial tests; reconcile docs/contracts; open a PR; repair CI; merge only after required automated checks pass; verify the merge landed on `main`; close only when acceptance is genuinely satisfied. Never erase source/audio/provenance, body lineage, uncertainty or backend qualification state to simplify UI.

## MSAC-001 — Repository/project schema and contract types
Create clean app/Godot project, Windows-first CI, versioned save skeleton and backend-neutral journal/revision/body/status models. Acceptance: no OCCT/provider-private type can enter saved/public state.

## MSAC-002 — Lathe/mill machine input and canonicalizer
Depends on MSAC-001. Implement explicit frame/tool/setup/engagement input and RCS-019-conforming canonicalization. Acceptance: deterministic vectors, sampling-rate equivalence, overflow/refusal and semantic-boundary tests pass.

## MSAC-003 — Revision/undo/replay and project persistence
Depends on MSAC-001/002. Save canonical journal, immutable revisions, bodies/lineage, source/audio identity and provenance. Acceptance: cache/provider state deletion does not change replay invariant; split bodies persist; pending-intent transactions survive save/restart without falsely advancing the committed revision.

## MSAC-004 — Async backend client and failure recovery
Depends on MSAC-001/003. Implement capability/apply/reconcile/query/export request families, status lifecycle, cancellation/reconnect/replay. Acceptance: crash/timeout cannot advance committed revision; `accepted_pending` is visible and non-blocking, is durably recoverable without provider-private state, and remains distinct from committed revision success.

## MSAC-005 — Revision-keyed preview and inspection
Depends on MSAC-004. Implement derived preview with stale/pending labels, DRO/frame display, exact-query reconciliation trigger and body selection guard. Acceptance: preview cannot authorize unresolved connectivity or STEP.

## MSAC-006 — Lathe capability and reachability UX
Depends on MSAC-002/004. Represent RCS-020 qualified subset, provider handoff and explicit holder-collision/unsupported outcomes. Acceptance: no target-profile fabrication and complete parting exposes both material bodies.

## MSAC-007 — Manual mill pending/fallback UX
Depends on MSAC-002/004/005. Represent exact, bounded directional, refinement/reconciliation and refusal states from RCS-021. Acceptance: unqualified five-axis/tool-reorientation remains refused/pending; positive sub-resolution intent is not displayed as no-op.

## MSAC-008 — STEP engineering workflow
Depends on MSAC-004/005. Implement all committed material bodies as default, reconciliation/error gating, exact profile/version and `interoperability_unqualified` Layer-D messaging. Acceptance: generated-file success cannot be presented as full interoperability qualification.

## MSAC-009 — Autosave/migration and source/audio provenance
Depends on MSAC-003. Implement atomic saves, schema migration, recovery and immutable source/audio/provenance references. Acceptance: old project meaning survives backend/provider changes; unknown semantic migration fails closed/read-only; cancellation/refusal of recovered pending transactions cannot mutate the committed parent.

## MSAC-010 — Windows product soak and responsiveness
Depends on MSAC-004..009. Run long-session replay/backend restart/export workflows on target Windows hardware, define UI responsiveness budgets and recovery acceptance. Engineering correctness/status gates remain unchanged when performance is poor.
