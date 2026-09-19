# Genesis-v2 bootstrap consistency correction

Status: accepted bounded consistency repair  
Date: 2026-09-19  
Issue: #60  
Decision: DR-0025

## Purpose

This record is the current routing/consistency bridge between the accepted RCS-027 Gate-5 freeze and autonomous production bootstrap. It adds **no new geometry qualification** and does not reopen RCS-001–RCS-027 research.

## Historical identities preserved

The RCS-027 historical freeze remains identifiable by:

- merge commit: `a68fa92d1128a163b232e2be69d6f731bd56caa5`;
- original `handoffs/genesis-release-v2.json` blob: `c47beb993a3cd64f28fd35c1d47f1a3630cef92c`;
- original OpenSimachinist v2 package tree: `b93e6e7ca28d26753e735f8ffe4acc56c5821676`;
- original MSAC v2 package tree: `a38d265aae2fda8e35dcf58e7d127d459e74055a`.

Consistency revision 2.1 changes the **current bootstrap package content** and records those old identities rather than silently reinterpreting them.

## Current bootstrap route

New production work reads, in order:

1. this document and DR-0025;
2. `handoffs/genesis-release-v2.json` with `consistency_revision: "2.1"`;
3. the project package under `handoffs/v2/opensimachinist/` or `handoffs/v2/msac/`;
4. `handoffs/evidence-dependencies-v2.1.json` for exact immutable fixture/evidence imports;
5. accepted RCS documents only when the package or exact-dependency manifest references them.

Genesis-v1 launch material remains historical.

## Corrected seams

### Handoff status

Gate 5 remains accepted. Current package manifests say `gate5_foundation_qualified_bootstrap_consistent`, while original pre-correction package status/tree identities remain recorded as correction provenance.

### Exact evidence dependencies

Research names such as "RCS-019" are not sufficient autonomous import instructions. The dependency manifest pins each required evidence file to source commit `a68fa92d1128a163b232e2be69d6f731bd56caa5` plus its Git blob SHA and claim class. Production changes to those fixtures are deliberate supersessions, not transparent upgrades.

### Pending-intent durability

`accepted_pending` is durable user/manufacturing intent without a committed engineering revision. Persist a programme-owned pending-intent transaction before acknowledging the state. Keep the last committed revision authoritative; never serialize provider-private state as the only recovery source. Save/crash/restart discards derived state and resumes from the parent revision plus pending transaction chain.

### Connectivity terminology

For one regularized material set, candidate geometric bodies are closures of connected components of its interior. Point/edge-only contacts do not bridge the material interior. Distinct durable body IDs do not auto-merge because backend geometry touches/coincides; split/merge identity changes require explicit validated body transitions.

### Claim classification

Use `MEASURED_NATIVE_GEOMETRY`, `MEASURED_INDEPENDENT_ORACLE`, `MEASURED_DETERMINISTIC_MODEL`, and `MEASURED_PLATFORM_PROCESS` when the distinction matters. In particular, RCS-025 is coordinator/reconciliation model evidence, RCS-026's 100k histories are coordinator/journal scale evidence rather than 100k native geometry-changing operations, and RCS-022/RCS-027 native STEP evidence remains `interoperability_unqualified` at Layer D.

## What remains unchanged

`msac-journal/1.0` committed physical meaning; durable revision/body/lineage/source/audio/provenance authority; positive-removal intent; propagated error budgets; OCCT 8.0.1 process isolation; all-body STEP default; Layer-D `interoperability_unqualified`; and existing qualified/refused lathe/mill capability boundaries.

## Bootstrap implication

Autonomous production bootstrap proceeds only from the consistency-corrected current route. Production must still turn modelled policies into real implementation evidence; no model result in this correction is permission to claim unmeasured geometry capability.
