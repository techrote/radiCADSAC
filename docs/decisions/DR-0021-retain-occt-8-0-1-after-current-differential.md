# DR-0021 — Retain OCCT 8.0.1 after current differential; permit selective backend-private BRepGraph use

Status: **accepted by RCS-024 measured evidence**.

Date: 2026-09-18

## Context

The founding backend research is pinned to OCCT 8.0.1 commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`. RCS-024 was created because current upstream contains continuing BRepGraph/history work and because RCS-017 found same-process STEP tolerance cross-talk plus process-global Boolean parallel configuration. A newer version must not be presumed safer without replaying decisive manufacturing controls.

At RCS-024 execution, 8.0.1 remained the latest stable upstream release. The distinct comparison is therefore exact current development snapshot 8.1.0.dev1 commit `3d097a0328e71b826377d4814ab05ec3c3d23871`, not an unpinned branch.

The successful exact-pin differential is normalized in `research/rcs-024/measured-result-v1.json`. Both pins reproduced the same decisive failures: STEP writer tolerance cross-talk (`0.00001 mm` sequential control becoming `0.001 mm` after conflicting writer configuration), cross-thread process-global parallel state, zero material removal for a positive `0.000001 mm` skim despite a valid B-rep, `7.539633873064304 mm³` finish-chain order delta, `509.00986225103406 mm³` retrace-jitter batch/reference disagreement, and the bounded 8-second sampled fallback timeout. BRepGraph split/merge history and stale-after-clear freshness worked on both pins, while fresh graph rebuilds reused the same numerical ItemUID value.

## Decision

1. **Retain OCCT 8.0.1 as the founding production-baseline candidate.** The 8.1.0.dev1 snapshot produced no measured correctness or concurrency improvement across the decisive controls and is not a stable release.
2. **Retain process-isolated OCCT workers as the scheduler-level concurrency boundary.** The minimized current-snapshot probes reproduce both STEP configuration cross-talk and process-global parallel-state interference.
3. **Permit selective backend-private use of BRepGraph history, UID and freshness facilities** when they improve topology reconciliation, cache invalidation or diagnostic lineage.
4. **Do not use any OCCT/BRepGraph identifier as durable programme identity.** The measured numerical UID collision across fresh graph rebuilds reinforces that canonical operation IDs, body transitions, source identity and provenance must remain kernel-independent.
5. **Require the RCS-007/RCS-011 material oracles and RCS-023 propagated error budgets for kernel upgrades.** Valid topology alone is insufficient; the current snapshot reproduced the same valid-but-materially-wrong controls.
6. **Revisit baseline upgrade only against an exact released candidate** (or a deliberately accepted fork under a separate decision) with the same or stronger differential campaign, STEP conformance and migration evidence.

## Evidence

The first successful workflow evidence was run `35400220872` on head `5ee2dda2677ca9f6dc19da8e3210bb19e982819d`, artifact `10569839655`, artifact SHA-256 `65d61055cd637a09aa61ca6ac6bfc3c661adfbd18cceaf17668a794bbd23a3ae`. The durable normalized record is `research/rcs-024/measured-result-v1.json`; final-head CI is required to rerun the same contract before merge.

The BRepGraph harness itself also produced an adversarial lifetime finding: `FindModified()` / `FindOriginals()` return pointers into layer-owned mutable containers, so retaining those pointers across subsequent history mutation or `graph.Clear()` is invalid. The repaired probe snapshots scalar observations before mutation, and validation guards prevent that lifetime bug from being reintroduced. This finding changes the harness discipline, not the upstream comparative classification.

## Alternatives considered

### Upgrade immediately to the development snapshot

Rejected. It reproduces the same decisive STEP, global-state, Boolean/material and bounded-fallback defects as 8.0.1 and is not a stable release.

### Freeze all use of newer BRepGraph facilities

Rejected. Both exact pins demonstrate useful backend-private history and freshness facilities. They can be used without becoming stable programme identity or forcing an OCCT version upgrade.

### Remove process isolation

Rejected. The minimized differential reproduces the same writer cross-talk and process-global parallel-state observation on both pins. The worker boundary remains directly justified by measured evidence.

### Accept valid B-rep results as sufficient

Rejected. Both pins return structurally valid results while violating independent material intent in the positive-skim and retrace-jitter controls.

### Fork OCCT now

Rejected for RCS-024. The issue asks for upstream differential evidence, not a maintenance fork.

## Consequences

OpenSimachinist handoff material may describe BRepGraph as an implementation aid behind an adapter, but must retain kernel-independent journal/body/source/provenance contracts. The RCS-006 worker-only toolkit footprint remains the baseline build shape. Upgrade research can reuse the RCS-024 probes as regression controls.

No manufacturing tolerance, body-count rule, STEP obligation, error-budget rule, source identity, journal meaning or provenance requirement is weakened by this decision.

## Reversibility

High. A future stable OCCT release can supersede this decision after exact-pin qualification. The programme contracts intentionally make a kernel swap possible without rewriting durable manufacturing history.
