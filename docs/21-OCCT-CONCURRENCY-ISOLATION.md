# OCCT 8.0.1 concurrency and isolation synthesis

Status: RCS-017 architecture input  
Date: 2026-09-17

## Purpose

This document converts RCS-017's concurrency experiment into an OpenSimachinist architecture boundary. It is intentionally narrower than a claim that OCCT is globally thread-safe or globally unsafe.

## Qualified surface

The measured campaign covers:

- independent `STEPControl_Writer` instances using explicit `DESTEP_Parameters` with conflicting AP203/inch and AP242/mm policies;
- deterministic BRep Boolean cuts with per-instance `SetRunParallel` controls;
- direct observation of process-global `BOPAlgo_Options::SetParallelMode` state under conflicting threaded callers;
- read-only sharing of copied `TopoDS_Shape` handles backed by one immutable `TopoDS_TShape` input;
- sequential, one-process threaded, and concurrently process-isolated execution topologies;
- STEP read-back validity/configuration markers and geometry-volume checks derived from the RCS-005 conformance approach.

The exact dependency is OCCT 8.0.1 at commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42` using the RCS-006 `release-shared-cxx17-worker-only-headless-v4` profile.

## Per-call/session configuration versus global configuration

`DESTEP_Parameters` is the preferred production path for STEP settings that the API exposes explicitly. Separate writer/session objects and explicit transfer parameters make configuration ownership visible at the call boundary and avoid depending on ambient `Interface_Static` values for those settings.

This does not remove legacy/global data-exchange state from the OCCT process. `Interface_Static` remains a named process-global registry and therefore cannot represent two conflicting job policies safely by construction. Any required code path whose meaning depends on ambient global configuration must be serialized inside the worker or moved behind a process boundary.

## Boolean parallel controls

`BOPAlgo_Options::SetRunParallel` is instance-local. `BOPAlgo_Options::SetParallelMode` is static process-global state. They are different policy surfaces and must not be treated as synonyms.

OpenSimachinist should set per-instance controls explicitly for production operations. It should not allow independent jobs to change `SetParallelMode` concurrently. A worker may establish a process-global default during controlled initialization, after which job execution should avoid mutating it.

## Ownership boundary

Atomic OCCT handle lifetime management and copied `TopoDS_Shape` values make read-only ownership practical, but do not establish concurrent mutation safety. The founding contract is therefore:

- immutable input revisions may be shared read-only within one worker when the specific operation is qualified;
- result shapes are owned by the producing job until published as immutable revisions;
- mutable OCCT sessions, writers, algorithms, maps and topology-editing state are job-local;
- no programme-level API exposes raw OCCT handles as durable identity.

## Process-isolation decision

The founding production topology remains one or more **process-isolated OCCT workers** behind the programme-owned geometry contract.

Reasons:

1. OCCT 8.0.1 contains known process-global configuration surfaces (`Interface_Static`, global Boolean parallel mode) even where newer explicit APIs exist.
2. A narrow success in selected threaded APIs cannot prove absence of unrelated lazy/static/global state across the full exact-geometry and STEP stack.
3. Process boundaries contain crashes, leaks and accidental global-policy contamination in addition to configuration cross-talk.
4. The architecture already treats geometry implementation as replaceable/versioned, so process isolation is compatible with the accepted semantic-provider-hybrid design rather than an invasive workaround.
5. Worker pooling can amortize startup cost while preserving address-space separation between independently configured jobs.

## Allowed concurrency inside one worker

The decision does **not** ban threads. Thread-level parallelism may be used inside an isolated worker when all of the following hold:

- relevant objects are job-local or immutable shared inputs;
- required configuration is explicit/per-instance or fixed once before jobs begin;
- the measured API has deterministic correctness checks;
- no concurrent caller mutates process-global settings;
- failures remain contained by the outer worker process.

This permits internal OCCT parallel algorithms where qualified, while preventing the production scheduler from treating one OCCT address space as an unconstrained multi-tenant configuration domain.

## RCS-013 architecture update

RCS-013's `semantic-provider-hybrid-v1` selection remains unchanged. RCS-017 resolves its concurrency uncertainty by making process isolation the default execution boundary for OCCT-backed exact geometry, reconciliation and STEP work. Provider semantics, provenance, material-body revisions and the canonical manufacturing journal remain outside that process-specific implementation detail.

The production handoff should therefore interpret OCCT worker concurrency as follows:

- scheduler-level parallel jobs: separate worker processes by default;
- intra-job OCCT parallelism: permitted when explicitly configured and qualified;
- conflicting `Interface_Static` or static/global policies: never multiplexed concurrently in one process;
- STEP: use explicit `DESTEP_Parameters`/session ownership wherever supported;
- topology sharing: immutable/read-only only unless a later dedicated qualification expands the boundary.

## Remaining unknowns

RCS-017 does not qualify every OCCT subsystem, Windows/macOS behaviour, concurrent mutable topology, cancellation, long-duration allocator pressure, malformed-file attacks, or ThreadSanitizer-clean execution. These remain reasons not to remove the process boundary merely because selected threaded tests pass.

## Reversibility

The decision is deliberately reversible. A future release may consolidate jobs into fewer processes if broader platform/TSAN/soak evidence demonstrates that every used subsystem and configuration path is safely job-local. No stable MSAC/OpenSimachinist contract should depend on worker process count, so such a change should remain an implementation deployment choice.
