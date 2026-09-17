# DR-0016 — OCCT process isolation is the founding concurrency default

Status: accepted  
Date: 2026-09-17  
Decision owner: radiCADSAC research programme

## Context

RCS-004 identified both explicit per-operation controls and process-global state in OCCT 8.0.1. RCS-013 therefore kept process isolation as the conservative founding boundary pending direct concurrency evidence. RCS-017 adds that evidence using the exact RCS-006 OCCT build and compares sequential, one-process threaded and process-isolated execution.

The accepted stress campaign recorded zero configuration mismatches in 160 sequential jobs, **10 mismatches in 160 same-process threaded jobs**, and zero mismatches in 160 jobs across eight isolated worker processes. The observed threaded contamination affected serialized STEP uncertainty/tolerance while the tested schema/unit and writer-local shape-fix settings remained correct. Separately, conflicting `BOPAlgo_Options::SetParallelMode` callers observed **6,505 mismatches in 16,000** set/yield/read attempts. Process isolation added about **3.18%** campaign wall time relative to same-process threads for the equal 160-attempt workload on the CI runner.

## Decision

OpenSimachinist shall treat **process-isolated OCCT workers as the default scheduler-level concurrency boundary** for exact geometry, reconciliation and STEP work in the founding architecture.

Within a worker:

- use explicit `DESTEP_Parameters` and distinct writer/session ownership for STEP configuration where supported, while recognizing that this does not by itself make the entire writer/transfer stack a multi-tenant isolation boundary;
- set Boolean execution policy per instance with `SetRunParallel` where applicable;
- do not multiplex conflicting `Interface_Static` or other process-global policies concurrently;
- establish any unavoidable process-global defaults in controlled worker initialization rather than per job;
- share topology only as immutable/read-only input unless a later qualification explicitly demonstrates safe mutation semantics;
- keep mutable algorithms, work sessions, writers and transient result state job-local.

Thread-level parallelism is permitted inside an isolated worker for measured/qualified APIs. This decision is not a blanket statement that OCCT is thread-safe or unsafe.

## Alternatives considered

### One multi-tenant OCCT process with unrestricted job threads

Rejected for the founding architecture. Beyond the source-level existence of `Interface_Static` and static Boolean policy, RCS-017 directly observed STEP tolerance contamination in 10/160 threaded jobs and process-global Boolean state cross-talk in 6,505/16,000 set/read attempts.

### Serialize all OCCT work in one process

Safe with respect to conflicting global configuration but unnecessarily constrains throughput and gives weaker fault containment. The stress baseline took `2762.58 ms` sequentially versus `1319.76 ms` across eight isolated workers for the equal 160-attempt campaign. These numbers are harness-specific but demonstrate that process isolation need not imply serialization.

### Deep OCCT source modification to remove globals before production

Not justified. Public explicit configuration APIs already reduce much ambient-state dependence, and process isolation is a reversible containment mechanism that avoids maintaining a premature fork.

## Evidence

- RCS-004 source audit: `docs/12-OCCT-8.0.1-AUDIT.md`.
- RCS-005 STEP conformance contract: `docs/13-STEP-CONFORMANCE-CONTRACT.md`.
- RCS-006 pinned OCCT harness/build: `docs/14-BASELINE-BENCHMARK-HARNESS.md` and `research/rcs-006/`.
- RCS-017 experiment definition and harness: `research/rcs-017/`.
- Frozen accepted measurements: `research/rcs-017/measured-summary-v1.json`, sourced from Actions run `35258066758` and artifact `10512917975`.
- RCS-017 synthesis: `docs/21-OCCT-CONCURRENCY-ISOLATION.md`.

All 480 geometry/STEP jobs in the accepted sequential/thread/process comparison completed with valid read-back B-reps, no worker failures and no timeouts. The maximum source/read-back volume delta was approximately `8.71e-9 mm³`. The shared immutable stock retained its measured volume under threaded non-destructive use. Those successful geometry observations coexist with the configuration cross-talk and must not be misrepresented as proof of general thread safety.

## Consequences

- The production scheduler may scale by worker processes without exposing OCCT process count through the stable programme API.
- Worker pools should amortize process startup while allowing workers to be recycled after faults, leaks or incompatible global-policy use.
- Explicit per-call configuration remains mandatory even with process isolation; isolation is a containment layer, not permission to rely on ambient defaults.
- A worker crash does not require the host/MSAC process to share OCCT's failure domain.
- Later evidence may allow more thread multiplexing inside a worker without changing the semantic-provider-hybrid architecture.
- Production conformance must continue validating serialized STEP semantics; a successful writer call or valid B-rep alone would not have detected the measured tolerance contamination.

## Remaining unknowns

- Full ThreadSanitizer qualification of the used OCCT subset.
- Platform-specific behaviour on Windows/MSVC and macOS.
- Concurrent mutation of shared topology.
- Every legacy `Interface_Static` consumer and other lazy/static caches outside the measured surfaces.
- Long-duration soak, cancellation and malformed STEP inputs.
- Final production worker-pool overhead under realistic mixed lathe/mill workloads.

## Reversibility

High. Worker topology is an implementation/deployment boundary behind programme-owned contracts. If broader evidence later proves all used subsystems safely job-local, multiple independent jobs may share a worker process without changing durable journals, provider semantics, STEP contracts or MSAC integration.
