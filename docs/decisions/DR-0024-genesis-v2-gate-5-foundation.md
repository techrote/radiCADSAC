# DR-0024 — Genesis v2 Gate-5 foundation

Status: proposed by RCS-027; acceptance is conditional on the frozen exact Windows/MSVC OCCT 8.0.1 STEP closure evidence.

## Context

Genesis v2 was created to qualify architecture-driving choices that Genesis v1 supported only with narrower experiments. RCS-018 through RCS-026 now cover contract composition, deterministic canonicalization, realistic lathe tool envelopes, independent manual-mill material truth and bounded fallback, independent STEP parsing/import, propagated uncertainty, current-OCCT differential behavior, repeated provider handoff/reconciliation, and Windows/Linux scale/fault recovery.

RCS-026 deliberately left one Gate-5 blocker: it did not execute the exact pinned OCCT 8.0.1 STEP worker under Windows/MSVC. RCS-027 owns that bounded closure test and the final synthesis.

## Decision

When and only when the RCS-027 Windows closure record is accepted, declare Genesis v2 **Gate-5 foundation-qualified** with these boundaries:

1. retain `msac-journal/1.0` and the programme-owned immutable revision/material-body/semantic-lineage/source/audio/provenance model;
2. retain semantic-provider hybrid architecture;
3. retain the RCS-020 bounded realistic axisymmetric lathe predicate and explicit provider-handoff/refusal for unsupported tool/process classes;
4. retain the RCS-021 independent fixed-axis mill material oracle and directional fallback only where declared material/spatial/error budgets close;
5. require hard semantic/query reconciliation boundaries plus a finite observable deferred-state resource guard;
6. propagate RCS-023 error channels conservatively through all provider/reconciliation boundaries;
7. retain OCCT 8.0.1 at commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42` inside process-isolated workers;
8. retain `rcs-022-occt-ap242dis-layer-d/1.0` as the exact production-candidate STEP profile while reporting its current Layer-D status as `interoperability_unqualified`;
9. treat Windows/Linux 100k research qualification as semantic/recovery evidence, not a product SLA;
10. move remaining safely bounded capability expansion and performance tuning into clean production repositories.

No production repository is created by this decision.

## Alternatives considered

**Delay Gate 5 until Layer D becomes positive.** Rejected. The Gate-5 roadmap explicitly permits an exact profile to remain independently unqualified when the blocker is recorded and product/API semantics expose it truthfully. This is safer than replacing the consumer, widening its metric gate or misrepresenting another OCCT wrapper as independent evidence.

**Infer Windows STEP support from Linux STEP plus portable Windows semantic tests.** Rejected by DR-0023. RCS-027 must execute the pinned Windows kernel/export path.

**Upgrade to OCCT 8.1.0.dev1 before production.** Rejected by RCS-024 because every decisive defect reproduced and no measured safety/correctness benefit justified leaving the stable 8.0.1 baseline.

**Promote directional/mesh state directly to engineering output.** Rejected. It remains bounded deferred material state and must reconcile to conventional B-rep before STEP.

## Evidence

The complete predecessor matrix is `research/rcs-027/evidence-matrix-v1.json`; the decision audit is `research/rcs-027/decision-delta-v1.json`; the synthesis is `docs/35-GENESIS-V2-SYNTHESIS-AND-GATE5.md`.

The final acceptance evidence must additionally bind the exact successful RCS-027 Windows workflow head/run/artifact digest in `research/rcs-027/windows-step-qualification-v1.json`. Until that record exists, this decision remains proposed.

## Consequences

OpenSimachinist can begin from a stable programme-level journal/body/lineage/status/error contract while providers remain replaceable. MSAC can treat direct machining interaction and preview as user experience while the canonical journal and backend engineering status remain authoritative.

Unsupported or unresolved operations remain explicit `accepted_pending`, `refused_unsupported`, ambiguity or budget-breach states. STEP remains mandatory primary output, but UI/API must not equate a successful file write or clean independent B-rep import with Layer-D qualification.

Genesis-v1 package identity remains unchanged. Fresh Genesis-v2 packages are new artefacts with their own manifest and tag plan.

## Reversibility

Individual backend/provider/profile choices may be superseded by later measured decisions. Any change must preserve old journal/source/audio/provenance meaning and rerun the corresponding capability/error/export/platform gates. Gate-5 history itself is not rewritten; future work records a new decision.
