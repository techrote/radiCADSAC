# DR-0021 — Retain OCCT 8.0.1 pending a release-qualified upgrade; permit selective backend-private BRepGraph use

Status: **proposed by RCS-024; becomes accepted only with the successful measured differential merged to `main`.**

Date: 2026-09-18

## Context

The founding backend research is pinned to OCCT 8.0.1 commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`. RCS-024 was created because newer upstream development contains BRepGraph/history work and because RCS-017 found same-process STEP tolerance cross-talk plus process-global Boolean parallel configuration. A newer version must not be presumed safer without replaying decisive manufacturing controls.

At RCS-024 execution, 8.0.1 remained the latest stable upstream release. The distinct comparison is therefore the exact current development snapshot 8.1.0.dev1 commit `3d097a0328e71b826377d4814ab05ec3c3d23871` rather than an unpinned branch.

## Decision

1. **Retain OCCT 8.0.1 as the founding production-baseline candidate.** A development snapshot is not promoted merely because it is current.
2. **Retain process-isolated OCCT workers as the scheduler-level concurrency boundary.** RCS-024 may show that particular current APIs are cleaner, but that narrow result is not broad qualification of all process-global/static/cache surfaces.
3. **Permit selective backend-private use of BRepGraph history, UID and freshness facilities** when they improve topology reconciliation, cache invalidation or diagnostic lineage.
4. **Do not use any OCCT/BRepGraph identifier as durable programme identity.** Canonical operation IDs, body transitions, source identity and provenance remain kernel-independent.
5. **Require the RCS-007/RCS-011 material oracles and RCS-023 propagated error budgets for kernel upgrades.** Valid topology alone is insufficient.
6. **Revisit baseline upgrade only against an exact released candidate** (or a deliberately accepted fork, which is outside this decision) with the same or stronger differential campaign and migration evidence.

## Evidence required before acceptance

The PR that accepts this record must contain machine-readable results from both exact pins covering minimized STEP configuration interference, per-instance/global parallel ownership, the RCS-007 positive-skim and order controls, the RCS-011 retrace-jitter and bounded sampled control, plus BRepGraph split/merge/rebuild freshness probes. Existing pull-request checks must pass on the exact final head.

## Alternatives considered

### Upgrade immediately to the development snapshot

Rejected as a founding decision. There is no released newer stable candidate, and recency does not establish manufacturing correctness or deployment maturity.

### Freeze all use of newer BRepGraph facilities

Rejected. Backend-private history and freshness facilities can be useful without becoming stable programme identity or forcing an OCCT version upgrade.

### Remove process isolation if minimized STEP cross-talk is fixed

Rejected. The worker boundary protects against a broader family of process-global/static/cache interactions than one reproducer covers. Removing it requires separate broad qualification.

### Fork OCCT now

Rejected for RCS-024. The issue explicitly asks for upstream differential evidence, not a maintenance fork.

## Consequences

OpenSimachinist handoff material may describe BRepGraph as an implementation aid behind an adapter, but must retain kernel-independent journal/body/provenance contracts. The RCS-006 worker-only toolkit footprint remains the baseline build shape. Upgrade research can reuse the RCS-024 probes as regression controls.

## Reversibility

High. A future stable OCCT release can supersede this decision after exact-pin qualification. The programme contracts intentionally make a kernel swap possible without rewriting durable manufacturing history.
