# OpenSimachinist unresolved research register

Status: founding production register derived from accepted RCS-013 unknowns. These are **not** implementation facts. Each item has a safe current policy so useful implementation can proceed without pretending the question is solved.

## Priority 1 — pathological freehand mill fallback

**Question:** Which bounded local representation/algorithm can robustly preserve arbitrary, self-crossing and retraced freehand mill removal without the valid-but-wrong n-ary batching result or sampled-pose B-rep timeout behavior observed in RCS-011?

**Safe current policy:** use qualified recognized/canonical/per-segment strategies where their predicates hold. Otherwise keep the operation pending, contain the pathological region, attempt only explicitly qualified fallback adapters, or return `refused_unsupported`/`refused_unresolved_ambiguity`. Never declare success because a B-rep is merely valid.

**Production owner:** OSM-013.  
**Genesis evidence:** `research/rcs-011/measured-summary-v1.json`, `docs/19-MILL-CUTTER-SWEEP-RESEARCH.md`, DR-0014.

## Priority 2 — real lathe tool envelopes

**Question:** How should insert nose radius, tool orientation, representative grooving/parting and undercut envelopes be constructed and qualified in the axisymmetric provider?

**Safe current policy:** keep the first provider limited to the RCS-010-qualified rotationally symmetric subset. Unsupported envelope semantics hand off/reconcile/refuse rather than being approximated silently.

**Production owner:** OSM-014.  
**Genesis evidence:** `research/rcs-010/measured-summary-v1.json`, `docs/18-LATHE-MATERIAL-DOMAIN-RESEARCH.md`, DR-0013.

## Priority 3 — production STEP interoperability profile

**Question:** Which exact exporter build/profile and independent CAD/CAM consumer matrix will be qualified before production claims fully successful STEP interoperability?

**Safe current policy:** Layers A-C remain mandatory automated gates, but a profile is `interoperability_unqualified` until current independent parser and downstream-consumer evidence exists for that exact material exporter/profile/version.

**Production owner:** OSM-015.  
**Genesis evidence:** `docs/13-STEP-CONFORMANCE-CONTRACT.md`, DR-0009.

## Priority 4 — curved/non-orthogonal fallback reconciliation

**Question:** How should a local fallback island containing curved or non-orthogonal geometry reconstruct exact/analytic boundaries and bound residual fitting error before engineering export?

**Safe current policy:** recover provenance-known analytic geometry first; allow bounded fallbacks only where reconciliation can demonstrate the STEP/validation budgets. Otherwise refuse exact topology/export for that state.

**Production owner:** fallback/reconciliation subsystem after OSM-011; create a dedicated issue when a concrete workload requires it.  
**Genesis evidence:** `research/rcs-012/measured-summary-v1.json`, DR-0014.

## Priority 5 — OCCT concurrency and process-global state

**Question:** Which Boolean/STEP paths in the selected OCCT baseline are safely instance-local under conflicting concurrent jobs, and where may process isolation be relaxed?

**Safe current policy:** run geometry/STEP work in supervised processes with timeouts and explicit per-call configuration. Do not infer thread safety from single-job or process-isolated success.

**Production owner:** dedicated concurrency benchmark equivalent to genesis RCS-017.  
**Genesis evidence:** `docs/12-OCCT-8.0.1-AUDIT.md`, `research/rcs-013/unresolved-v1.json`.

## Priority 6 — provider handoff/reconciliation frequency

**Question:** Under realistic interactive workloads, how often do lathe/mill/generic/fallback transitions force expensive reconciliation, and can that erase the specialization benefit?

**Safe current policy:** keep capability predicates explicit, cache replayable reconciled checkpoints, record provider changes and measure handoff cost in vertical slices. Do not weaken semantic boundaries pre-emptively for performance.

**Production owner:** OSM-012 integration benchmark plus later performance work.  
**Genesis evidence:** DR-0012, DR-0013, DR-0015.

## Priority 7 — semantic-lineage persistence encoding

**Question:** What concrete ID/graph/index/migration encoding best implements the accepted semantic-lineage model?

**Safe current policy:** implementation may choose a practical serialization/indexing scheme, but durable identities/relations remain backend-independent and explicit. No face/edge/object identity may become persistent meaning.

**Production owner:** OSM-004.  
**Genesis evidence:** DR-0011 and RCS-008.

## Priority 8 — bounded deferred-state resource policy

**Question:** Which pending-state size/time/query thresholds should force reconciliation before deferred work becomes unbounded or stale?

**Safe current policy:** connectivity/body decisions, exact topology queries, provider handoff and export are unconditional hard boundaries. OSM-010 must add measured resource thresholds and explicit failure behavior.

**Production owner:** OSM-010.  
**Genesis evidence:** DR-0012 and RCS-009.

## Priority 9 — targeted exact-arithmetic seams

**Question:** Which reproduced intersection/classification failures justify exact predicates/constructions and which library/license choice is acceptable?

**Safe current policy:** do not blanket-rewrite the core around exact arithmetic. Introduce an exact component only at a minimized measured seam, behind a replaceable adapter, and re-run physical/STEP oracles.

**Production owner:** future robustness issue created from a concrete regression.  
**Genesis evidence:** `docs/12-OCCT-8.0.1-AUDIT.md`, `docs/19-ALTERNATIVE-HYBRID-GEOMETRY-REPRESENTATIONS.md`.

## Priority 10 — distribution/license compliance

**Question:** What exact source, notice, relinking and packaging material is required for the actual distributed OCCT configuration and optional fallback dependencies?

**Safe current policy:** keep dependencies pinned, distinguishable and adapter-isolated; retain upstream source/license/build/patch provenance; conduct a release-specific compliance audit before distribution. Genesis licensing notes are technical constraints, not a substitute for that audit.

**Production owner:** release engineering.  
**Genesis evidence:** `docs/12-OCCT-8.0.1-AUDIT.md`, `docs/19-ALTERNATIVE-HYBRID-GEOMETRY-REPRESENTATIONS.md`.

## Priority 11 — live-tool and non-axisymmetric lathe work

**Question:** How should eccentric, live-tool and other non-axisymmetric lathe operations dispatch without contaminating the fixed-axis provider?

**Safe current policy:** reconcile and hand off to mill/general providers where qualified, otherwise refuse. Do not approximate these operations inside the axisymmetric domain.

**Production owner:** later process expansion after the productive core.  
**Genesis evidence:** DR-0013 and DR-0015.

## Escape-route doctrine

An unresolved item is allowed to produce one of four safe outcomes:

1. **defer** — preserve manufacturing intent and mark engineering state `accepted_pending` while a bounded safe reconciliation path still exists;
2. **handoff** — reconcile as needed and dispatch to another provider whose capability predicate is actually satisfied;
3. **bounded fallback** — use a local alternate representation only under an explicit support/error/provenance contract and reconcile before engineering/export success;
4. **refuse** — return a stable unsupported/ambiguity/conformance status rather than corrupting material, widening tolerance, dropping bodies or substituting mesh output.

A new measurement may promote an unresolved item into an accepted capability only through a versioned decision plus regression/qualification evidence. Negative results remain part of the production regression record.
