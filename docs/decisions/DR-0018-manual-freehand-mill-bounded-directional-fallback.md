# DR-0018 — Manual/freehand milling requires independent material truth and bounded directional fallback

Status: **proposed pending RCS-021 measured evidence**  
Date: 2026-09-17  
Decision scope: Genesis-v1 fixed-axis manual/freehand milling

## Context

RCS-011 showed that conventional kernel success is not a sufficient manufacturing oracle. Its near-coincident `retrace-jitter` one-shot batch returned a valid one-solid B-rep while leaving essentially the full stock volume instead of the material removed by the exact sequential reference. The same campaign's dense sampled-pose B-rep fallback reached its containment timeout in all ten tested attempts.

RCS-012 then demonstrated a different failure mode: coarse volumetric occupancy can be robust and deterministic while erasing real positive material smaller than its resolution. DR-0014 consequently permits bounded local hybrid representations but requires explicit representation error, programme-owned lineage, analytic preservation and conventional B-rep reconciliation before STEP.

RCS-021 adds the missing independent material oracle and measures a machining-native directional material representation plus a maintained external comparator against the same physical fixtures.

## Decision

Pending successful RCS-021 measurement, the programme adopts the following fixed rules for manual/freehand milling:

- **Material truth is independent of OCCT success.** Valid B-rep, `IsDone`, watertight mesh or visual plausibility never substitutes for an independent physical/material oracle on pathological freehand cases.
- **The canonical journal remains durable intent.** A fallback may reduce derived geometric work but may not compact away journal history, provenance or control uncertainty.
- **Directional/deferred material state is eligible only as a bounded fallback.** Its supported tool/path domain, material-volume interval, spatial support/error, deterministic behavior and body/connectivity semantics must be explicit.
- **Resolution cannot erase physical truth.** Positive sub-tolerance material removal is retained analytically or the representation refuses authoritative use; it is never snapped to zero for convenience.
- **Disconnected material remains valid.** A cut-through that physically separates stock must preserve every remaining material body.
- **Backend-local identities are non-durable.** Octree cells, dexels, ray intervals, mesh vertices/triangles and regenerated B-rep topology do not become project identity.
- **Known analytic/process boundaries survive fallback through programme provenance.** Reconciliation recovers these known boundaries before generic fitting of genuinely unknown residual surfaces.
- **STEP remains a reconciliation boundary.** Directional or mesh fallback state is not STEP-authoritative. It must reconcile to conventional B-rep and pass RCS-005 before the result can be called successful engineering output.
- **Capability narrows before error budgets do.** If the independent oracle and candidate bounds do not close inside the accepted domain, the outcome is refinement, `accepted_pending`, `refused_unsupported` or `refused_unresolved_ambiguity`, not an inflated tolerance disguised as success.
- **External engines remain replaceable comparators/providers.** Manifold 3.5.3 is measured as an external candidate, not promoted into durable semantics by this decision.

The final status of this record depends on hosted RCS-021 evidence. If the campaign falsifies the bounded directional candidate, this decision will be narrowed rather than relabeling failed evidence as success.

## Alternatives considered

### Trust exact per-segment OCCT subtraction as the oracle

Rejected as the sole oracle. It remains valuable comparison evidence, but issue #40 specifically exists because kernel execution cannot independently validate itself and the general freehand path needs a truth source with different failure modes.

### Accept one-shot freehand B-rep batching when topology is valid

Rejected. RCS-011 supplied a direct counterexample: valid topology can coexist with materially wrong geometry.

### Increase the timeout for dense sampled B-rep poses

Rejected as a founding answer. A longer timeout does not create a scaling contract, independent material truth or bounded representation error. The old fallback is retained as a live negative/control comparison.

### Whole-model mesh authority

Rejected. A watertight/manifold mesh may be an excellent local robustness representation, but it does not intrinsically preserve the programme's analytic engineering semantics or satisfy conventional STEP obligations.

### Whole-model coarse voxel/SDF authority

Rejected. RCS-012 directly demonstrated semantic loss below cell size. Any discretized material field requires an explicit error/resolution policy and reconstruction boundary.

### Refuse all manual/freehand milling

Retained as the safe fallback if RCS-021 cannot qualify a bounded representation. Product capability may narrow; manufacturing truth may not.

## Evidence

### Accepted prior evidence

RCS-011 measured the decisive `retrace-jitter` counterexample and contained ten dense sampled-pose timeouts. RCS-012 measured sub-resolution material loss in a coarse occupancy representation. DR-0014 already established the representation-neutral lineage and B-rep reconciliation rules consumed here.

### RCS-021 evidence required for acceptance

Before this record becomes accepted, hosted evidence must show:

- closed-form material/connectivity truth lies within the independent oracle bounds;
- the directional material candidate is deterministic on the complete pathological profile;
- candidate material bounds agree with the independent oracle on its claimed domain;
- positive 1 µm removal is not erased;
- the through-cut retains two material bodies;
- refinement/scaling metrics are recorded for decisive fixtures;
- Manifold 3.5.3 executes as a maintained external comparator or a concrete blocker is recorded;
- the RCS-011 valid-but-wrong retrace is independently rejected while the exact sequential reference is accepted;
- the old sampled fallback is rerun under bounded containment;
- all reconciliation/error channels remain explicit.

Run IDs, artifact digest and measured aggregates will be frozen in `research/rcs-021/measured-summary-v1.json` after the required CI gates pass.

## Consequences

- The production handoff can implement manual/freehand material tracking without making OCCT per-segment topology the only source of truth.
- A directional representation may answer local material/collision/preview queries before conventional topology is reconstructed, but only inside the domain qualified by the measured campaign.
- RCS-011 exact per-segment execution remains a valuable high-fidelity comparator and possible fallback path; it is no longer privileged as the independent truth source.
- STEP export still pays a reconciliation cost. The architecture is intentionally allowed to defer that cost rather than forcing topology construction at every controller sample.
- Sub-resolution machining features require retained analytic witnesses or explicit refusal. This may make some fallback paths less permissive, but prevents silent geometry loss.
- Future five-axis/tool-reorientation work requires separate cutter-field and material-representation evidence; this record does not infer it from fixed-axis results.

## Reversibility

High at the research stage. The independent oracle, directional candidate and Manifold comparator are all behind programme-owned material semantics. No saved-project meaning depends on their cell/ray/triangle IDs.

Reversibility becomes lower only after a production implementation chooses a specific representation for cached/reconstructable state. Durable journal/provenance contracts are designed so that representation can still be replaced without changing document meaning.

## Reconsideration trigger

Reconsider the chosen bounded fallback when later measurements show another representation provides materially tighter certified error, better scaling or simpler analytic STEP reconciliation over the same manual/freehand corpus without weakening provenance or physical truth. Also reconsider if the RCS-021 hosted campaign falsifies the proposed directional candidate on any required fixture; in that event the capability must be narrowed immediately.
