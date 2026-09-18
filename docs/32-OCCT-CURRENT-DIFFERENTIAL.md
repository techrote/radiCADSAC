# OCCT current differential and backend-private history contract

Status: **RCS-024 candidate contract; measured values are frozen from the successful PR evidence before merge.**

## Question

Does current pinned OCCT evidence justify changing the founding 8.0.1 baseline, the process-isolated worker boundary, or the programme's independent manufacturing identity/provenance model?

## Compared builds

| Role | OCCT version | Exact commit | Release status |
|---|---|---|---|
| founding control | 8.0.1 | `b8f597c677811d1f9f4d8a97f5ae2825c0353a42` | latest stable at 2026-09-18 |
| differential candidate | 8.1.0.dev1 | `3d097a0328e71b826377d4814ab05ec3c3d23871` | pinned development snapshot |

The current snapshot is included only because there is no newer stable release distinct from 8.0.1. It is not called stable and is not evidence by recency alone.

## Evidence families

RCS-024 carries forward only the decisive controls needed to test the recorded repair path:

- minimized RCS-017 STEP tolerance cross-talk with distinct writers and sequential controls;
- job-local `SetRunParallel` versus process-global `BOPAlgo_Options` state;
- RCS-007 positive sub-tolerance material removal and order-sensitive repeated finish;
- RCS-011 retrace-jitter one-shot batching and a bounded sampled-fallback pathology;
- BRepGraph one-to-many/many-to-one history, graph-generation freshness, and rebuild identity observations.

This is a differential investigation, not a new broad defect search.

## BRepGraph interpretation

Upstream documents `BRepGraph_ItemId` as a transient structural address and `BRepGraph_ItemUID` as identity that persists across graph compaction/reordering. `BRepGraph_LayerHistory` supports modified/generated/deleted/replaced mappings, including ItemUID-keyed records, and `BRepGraph_VersionStamp` combines identity with mutation/graph-generation freshness.

Those facilities are useful *inside a derived OCCT state*. They do not satisfy the programme-level identity contract by themselves:

- canonical operation IDs describe durable manufacturing intent independently of the kernel;
- body IDs and body transitions survive kernel replacement/rebuild;
- source/provenance identity is not inferred from topology coincidence;
- graph-local UID equality across rebuilds is not semantic equivalence;
- algorithm history is evidence for reconciliation, not the journal itself.

Accordingly, OpenSimachinist may wrap BRepGraph history/UID/freshness behind a backend-private adapter when useful. No BRepGraph type may cross the stable programme API merely to obtain convenient identity.

## Concurrency contract

RCS-017 already established process-isolated OCCT workers as the founding scheduler boundary after same-process STEP configuration cross-talk and process-global parallel-state interference. RCS-024 is allowed to minimize and re-test those mechanisms. A single current snapshot showing an improvement is insufficient to remove the isolation boundary because the programme uses more OCCT surfaces than this compact reproducer.

Per-operation parallelism may be enabled inside an isolated worker only for explicitly qualified operations. Process-global configuration must not be multiplexed between logical jobs in one address space.

## Robustness contract

A valid B-rep remains a structural result, not a material oracle. Positive removal intent, operation-local uncertainty, exact body count, source/provenance and the RCS-023 propagated error budget retain authority over a kernel result. A newer kernel that changes a pathological outcome must be compared against those independent oracles rather than accepted because it is newer.

## Build/migration contract

The differential build deliberately keeps the founding worker-only toolkit list and C++17/headless profile. BRepGraph is supplied by `TKBRep`, already in the RCS-006 worker footprint. CI measures installed bytes rather than assuming equal footprint. Any future baseline move must separately account for compiler/CMake requirements, source/API changes, Windows/Linux packaging, dependency availability, license/provenance and regression evidence.

## Decision rule

RCS-024 may recommend an upgrade only if the exact candidate provides material benefit across the decisive controls without weakening the journal, body, STEP, tolerance/error-budget or process-isolation contracts, and only if release maturity/migration cost is acceptable. Otherwise the correct result is to retain 8.0.1 while preserving useful current-upstream findings for selective backend-private adaptation.

## Measured result

The exact measured classification is generated as `research/rcs-024` CI evidence in `.results/rcs024/differential.json` and is copied into this section before merge. Until that evidence exists on the final PR head, **no upgrade claim is accepted**.
