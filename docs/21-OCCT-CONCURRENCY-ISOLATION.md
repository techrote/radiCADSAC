# OCCT 8.0.1 concurrency and isolation synthesis

Status: RCS-017 architecture input  
Date: 2026-09-17

## Purpose

This document converts RCS-017's concurrency experiment into an OpenSimachinist architecture boundary. It is intentionally narrower than a claim that OCCT is globally thread-safe or globally unsafe.

## Qualified surface

The measured campaign covers independent `STEPControl_Writer` instances with conflicting AP203/inch and AP242/mm policies, serialized uncertainty/tolerance and writer-local shape-fix settings; deterministic BRep cuts with per-instance `SetRunParallel`; direct observation of process-global `BOPAlgo_Options::SetParallelMode`; read-only sharing of copied `TopoDS_Shape` handles backed by one immutable `TopoDS_TShape`; and sequential, one-process threaded and concurrently process-isolated execution.

The exact dependency is OCCT 8.0.1 at commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42` using the RCS-006 `release-shared-cxx17-worker-only-headless-v4` profile. The accepted numeric evidence is frozen in `research/rcs-017/measured-summary-v1.json`.

## Measured result

The stress campaign executed 160 sequential jobs, 160 same-process threaded jobs and 160 jobs across eight worker processes. All 480 geometry/STEP jobs completed without timeout or invalid read-back B-rep.

Sequential execution produced zero configuration mismatches. Same-process threads produced **10/160 configuration mismatches**. Process-isolated workers produced **0/160 mismatches**. The observed threaded contamination was STEP serialized uncertainty/tolerance: schema/unit selection and the tested writer-local shape-fix parameter remained correct. A prior smoke run captured a concrete AP242/mm job requesting `1e-5 mm` but serializing `0.001 mm`, while its schema, unit, shape-fix setting, B-rep and volume were otherwise correct.

The dedicated static-global probe produced **6,505 mismatches in 16,000** conflicting `BOPAlgo_Options::SetParallelMode` set/yield/read attempts, directly demonstrating that this control is visible across independent threads.

The immutable shared stock retained its measured volume (`7999.999999999998 mm³` versus analytic `8000 mm³`) in the tested non-destructive threaded workload. This supports the intended read-only ownership pattern only; concurrent mutation remains unqualified.

For the equal 160-attempt workload, same-process threads completed in `1279.04 ms` and eight process-isolated workers in `1319.76 ms`: approximately `40.7 ms` or **3.18%** additional campaign wall time for process isolation on this CI runner. Sequential execution took `2762.58 ms`. These are comparative harness measurements, not production SLAs.

## Per-call/session configuration versus global configuration

`DESTEP_Parameters` is the preferred production path for STEP settings that the API exposes explicitly. In the measured campaign, explicit schema and unit policy remained correct under concurrency. Separate writer/session objects and explicit transfer parameters therefore reduce ambient-state dependence, but they are **not sufficient evidence of complete job isolation**: the tested writer tolerance/serialized uncertainty crossed jobs under one-process threads.

Legacy data-exchange configuration still exposes process-global `Interface_Static` named parameters. RCS-017 did not attempt to enumerate or race every such consumer. Any required code path whose meaning depends on ambient global configuration must be serialized inside the worker or moved behind a process boundary.

## Boolean parallel controls

`BOPAlgo_Options::SetRunParallel` is instance-local. `BOPAlgo_Options::SetParallelMode` is static process-global state. They are different policy surfaces and must not be treated as synonyms. The stress probe's 6,505/16,000 mismatches establish that conflicting per-job use of the static control is not a valid same-process scheduling model.

OpenSimachinist should set per-instance controls explicitly for production operations. It should not allow independent jobs to change `SetParallelMode` concurrently. A worker may establish a process-global default during controlled initialization, after which job execution should avoid mutating it.

## Ownership boundary

Atomic OCCT handle lifetime management and copied `TopoDS_Shape` values make read-only ownership practical, but do not establish concurrent mutation safety. The founding contract is therefore:

- immutable input revisions may be shared read-only within one worker when the specific operation is qualified;
- result shapes are owned by the producing job until published as immutable revisions;
- mutable OCCT sessions, writers, algorithms, maps and topology-editing state are job-local;
- no programme-level API exposes raw OCCT handles as durable identity.

## Process-isolation decision

The founding production topology remains one or more **process-isolated OCCT workers** behind the programme-owned geometry contract. RCS-017 now supplies positive measured justification rather than relying only on source-audit caution: process isolation eliminated the observed STEP tolerance cross-talk at about 3.18% additional campaign wall time relative to same-process threads in the stress workload.

Other reasons remain: OCCT 8.0.1 exposes known process-global configuration surfaces; a bounded successful threaded subset cannot prove absence of unrelated lazy/static/global state; process boundaries contain crashes/leaks/global-policy contamination; and worker pooling can amortize startup while preserving address-space separation.

## Allowed concurrency inside one worker

The decision does **not** ban threads. Thread-level parallelism may be used inside an isolated worker when relevant objects are job-local or immutable shared inputs, required configuration is explicit/per-instance or fixed before jobs begin, deterministic correctness checks exist, no concurrent caller mutates process-global settings, and failures remain contained by the outer worker process.

This permits internal OCCT parallel algorithms where qualified, while preventing the production scheduler from treating one OCCT address space as an unconstrained multi-tenant configuration domain.

## RCS-013 architecture update

RCS-013's `semantic-provider-hybrid-v1` selection remains unchanged. RCS-017 resolves its concurrency uncertainty by making process isolation the default execution boundary for OCCT-backed exact geometry, reconciliation and STEP work. Provider semantics, provenance, material-body revisions and the canonical manufacturing journal remain outside that process-specific implementation detail.

The production handoff should therefore interpret OCCT worker concurrency as follows:

- scheduler-level parallel jobs: separate worker processes by default;
- intra-job OCCT parallelism: permitted when explicitly configured and qualified;
- conflicting `Interface_Static` or static/global policies: never multiplexed concurrently in one process;
- STEP: use explicit `DESTEP_Parameters`/session ownership wherever supported, but keep the worker process as the isolation boundary because writer tolerance cross-talk was measured;
- topology sharing: immutable/read-only only unless a later dedicated qualification expands the boundary.

## Remaining unknowns

RCS-017 does not qualify every OCCT subsystem, Windows/macOS behaviour, concurrent mutable topology, cancellation, long-duration allocator pressure, malformed-file attacks, or ThreadSanitizer-clean execution. It also does not establish production worker-pool overhead under realistic mixed workloads. These remain reasons not to remove the process boundary merely because selected threaded geometry operations passed.

## Reversibility

The decision is deliberately reversible. A future release may consolidate jobs into fewer processes if broader platform/TSAN/soak evidence demonstrates that every used subsystem and configuration path is safely job-local. No stable MSAC/OpenSimachinist contract should depend on worker process count, so such a change should remain an implementation deployment choice.
