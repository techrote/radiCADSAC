# OpenSimachinist v2 implementation roadmap

## Phase 0 — repository and contract lock

Create a clean repository with CI, supported Windows/Linux toolchains, license/provenance inventory and machine-readable contract fixtures. Import specifications, not genesis history. Freeze `msac-journal/1.0`, stable statuses and programme-owned identity types before geometry code.

## Phase 1 — journal/revision/body core

Implement immutable journal ingestion, revision DAG, durable material-body transitions, semantic lineage and source/audio/provenance attachment. Make provider-private identifiers impossible to serialize through the stable API. Add replay, undo navigation and derived-cache destruction/regeneration tests.

## Phase 2 — canonicalization and budget trace

Implement or integrate an RCS-019-conforming canonicalizer. Add typed error channels and RCS-023 conservative propagation. Fail closed on unknown/breached exact/export queries. Preserve positive material intent.

## Phase 3 — worker supervisor and OCCT baseline

Build the process-isolated OCCT 8.0.1 worker profile, explicit global configuration per job, crash/timeout/kill containment and restart. Add Windows/Linux exact build provenance. Keep transport replaceable behind the programme request/status boundary.

## Phase 4 — provider core

Implement capability dispatch, the qualified lathe axisymmetric provider/reachability predicate, exact fixed-axis mill strategies and the independent manual-mill material oracle. Add directional deferred state only with explicit bounds.

## Phase 5 — reconciliation coordinator

Implement mandatory semantic/query boundaries, finite observable pending-resource guards, provenance-backed replacement, body/connectivity resolution and replay-stable provider transitions. Add ambiguous-lineage refusal and long-history stress.

## Phase 6 — STEP exporter

Implement exact RCS-022 profile and Layer A-C gates, independent parser/import integration and qualification-state reporting. Preserve all committed material bodies by default. `interoperability_unqualified` is a first-class result, not a warning to hide.

## Phase 7 — production hardening

Repeat Windows/Linux soak with production transport/persistence, native worker resource telemetry, cancellation/backpressure, crash recovery and version migration. Only then set product capacity targets.

Each phase must maintain deterministic/adversarial fixtures from the relevant RCS evidence and must not trade protected semantics for performance.
