# OpenSimachinist v2 clean bootstrap issue graph

Every issue below is an autonomous implementation prompt. For each: read this v2 handoff package and the referenced accepted evidence; inspect current `main`; create a dedicated branch; implement deterministic tests including adversarial/boundary cases; reconcile docs/contracts; open a PR; repair CI; merge only after required automated checks pass; verify the merge landed on `main`; close the issue only when its acceptance criteria are genuinely satisfied. Never weaken journal/body/source/audio/provenance/error/STEP semantics to make a test pass.

## OSM-001 — Repository skeleton and stable contract types
References: `00-FOUNDING-SPEC.md`, RCS-018, RCS-019. Create build/CI on pinned Windows/Linux profiles and programme-owned journal/revision/body/lineage/status types. No OCCT types in public API. Acceptance: serialization and negative private-ID tests pass.

## OSM-002 — Canonical journal ingestion and replay
Depends on OSM-001. References: RCS-019 and `msac-journal/1.0`. Implement validation, immutable revisions, replay/undo navigation, stable-source-order handling and policy-version checks. Acceptance: canonical vectors and cache-destruction replay invariants pass.

## OSM-003 — Propagated error-budget trace
Depends on OSM-002. References: RCS-023/DR-0020. Implement typed contributions, conservative composition, one-sided contact classification, positive-intent ambiguity and fail-closed exact/export decisions. Acceptance: correlation/max-only/order/breach adversarial controls pass.

## OSM-004 — Process-isolated OCCT 8.0.1 worker
Depends on OSM-001. References: RCS-024/DR-0021 and RCS-027 Windows evidence. Build exact pinned Windows/Linux worker packages, explicit per-job configuration and supervision. Acceptance: cross-talk reproducer is contained across processes; crash/timeout/kill cannot mutate durable authority.

## OSM-005 — Lathe provider capability
Depends on OSM-002/003. References: RCS-020/DR-0017. Implement the bounded realistic circular-nose turning/boring/facing/shoulder/taper/groove/parting subset, reachability gate and provider handoff/refusal. Acceptance: independent material oracle and two-body parting controls pass.

## OSM-006 — Fixed-axis mill truth and bounded fallback
Depends on OSM-002/003. References: RCS-021/DR-0018. Implement exact-strategy dispatch, independent material oracle and bounded directional state. Acceptance: retrace-jitter rejects valid-but-wrong batch, positive 1 µm intent survives, cut-through body semantics persist, unqualified orientations refuse/pending.

## OSM-007 — Reconciliation coordinator
Depends on OSM-003/005/006. References: RCS-025/DR-0022. Implement hard semantic/query boundaries, finite observable pending-resource guard, provenance-backed replacement and ambiguous-lineage refusal. Acceptance: mixed-provider replay and split/merge/body-selection stress pass without error reset.

## OSM-008 — STEP AP242DIS exporter and qualification state
Depends on OSM-004/007. References: RCS-022, RCS-026, RCS-027. Implement exact profile, all-body default, Layer A-C validation, independent parser/import probes and explicit `interoperability_unqualified`. Acceptance: metric/inch/analytic/two-body/adversarial cases pass without claiming Layer-D qualification.

## OSM-009 — Production persistence/transport and recovery
Depends on OSM-002/007. Persist only programme authority plus versioned derived-cache metadata. Add cancellation, idempotency, cache discard and restart. Acceptance: provider/kernel replacement and cache corruption reproduce the same programme invariant.

## OSM-010 — Production scale and release gate
Depends on OSM-004..009. Repeat RCS-026 style Windows/Linux 100k+ soak using production components, define measured capacity/resource SLAs, verify no orphan workers/handle growth, and publish explicit capability matrix. Do not widen correctness budgets to hit throughput.
