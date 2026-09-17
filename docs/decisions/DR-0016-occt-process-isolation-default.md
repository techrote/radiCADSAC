# DR-0016 — OCCT process isolation is the founding concurrency default

Status: accepted  
Date: 2026-09-17  
Decision owner: radiCADSAC research programme

## Context

RCS-004 identified both explicit per-operation controls and process-global state in OCCT 8.0.1. RCS-013 therefore kept process isolation as the conservative founding boundary pending direct concurrency evidence. RCS-017 adds that evidence using the exact RCS-006 OCCT build and compares sequential, one-process threaded and process-isolated execution.

## Decision

OpenSimachinist shall treat **process-isolated OCCT workers as the default scheduler-level concurrency boundary** for exact geometry, reconciliation and STEP work in the founding architecture.

Within a worker:

- use explicit `DESTEP_Parameters` and distinct writer/session ownership for STEP configuration where supported;
- set Boolean execution policy per instance with `SetRunParallel` where applicable;
- do not multiplex conflicting `Interface_Static` or other process-global policies concurrently;
- establish any unavoidable process-global defaults in controlled worker initialization rather than per job;
- share topology only as immutable/read-only input unless a later qualification explicitly demonstrates safe mutation semantics;
- keep mutable algorithms, work sessions, writers and transient result state job-local.

Thread-level parallelism is permitted inside an isolated worker for measured/qualified APIs. This decision is not a blanket statement that OCCT is thread-safe or unsafe.

## Alternatives considered

### One multi-tenant OCCT process with unrestricted job threads

Rejected for the founding architecture. OCCT 8.0.1 exposes known process-global configuration such as `Interface_Static` and `BOPAlgo_Options::SetParallelMode`, and a narrow set of successful threaded calls cannot establish isolation for the entire geometry/STEP stack.

### Serialize all OCCT work in one process

Safe with respect to conflicting global configuration but unnecessarily constrains throughput and gives weaker fault containment. Process workers allow scheduler-level parallelism without sharing one address space.

### Deep OCCT source modification to remove globals before production

Not justified. Public explicit configuration APIs already reduce much of the ambient-state dependence, and process isolation is a reversible containment mechanism that avoids maintaining a premature fork.

## Evidence

- RCS-004 source audit: `docs/12-OCCT-8.0.1-AUDIT.md`.
- RCS-005 STEP conformance contract: `docs/13-STEP-CONFORMANCE-CONTRACT.md`.
- RCS-006 pinned OCCT harness/build: `docs/14-BASELINE-BENCHMARK-HARNESS.md` and `research/rcs-006/`.
- RCS-017 experiment definition and harness: `research/rcs-017/`.
- RCS-017 synthesis: `docs/21-OCCT-CONCURRENCY-ISOLATION.md`.

The runtime campaign intentionally preserves negative outcomes rather than making successful file creation the criterion. STEP policy is checked through serialized configuration markers, read-back validity and geometry metrics; global Boolean state is probed separately from per-instance controls.

## Consequences

- The production scheduler may scale by worker processes without exposing OCCT process count through the stable programme API.
- Worker pools should amortize process startup while allowing workers to be recycled after faults, leaks or incompatible global-policy use.
- Explicit per-call configuration remains mandatory even with process isolation; isolation is a containment layer, not permission to rely on ambient defaults.
- A worker crash does not require the host/MSAC process to share OCCT's failure domain.
- Later evidence may allow more thread multiplexing inside a worker without changing the semantic-provider-hybrid architecture.

## Remaining unknowns

- Full ThreadSanitizer qualification of the used OCCT subset.
- Platform-specific behaviour on Windows/MSVC and macOS.
- Concurrent mutation of shared topology.
- Every legacy `Interface_Static` consumer and other lazy/static caches outside the measured surfaces.
- Long-duration soak, cancellation and malformed STEP inputs.
- Final production worker-pool overhead under realistic mixed lathe/mill workloads.

## Reversibility

High. Worker topology is an implementation/deployment boundary behind programme-owned contracts. If broader evidence later proves all used subsystems safely job-local, multiple independent jobs may share a worker process without changing durable journals, provider semantics, STEP contracts or MSAC integration.
