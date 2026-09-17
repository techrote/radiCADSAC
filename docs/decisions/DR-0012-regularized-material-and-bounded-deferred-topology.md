# DR-0012 — Regularized material semantics with bounded deferred topology

Status: accepted  
Date: 2026-09-17  
Decision scope: OpenSimachinist internal material/topology semantics

## Context

The programme treats coincidence, tangency, retracing, slivers and large operation counts as normal manufacturing input. Immediate conventional B-rep reconstruction after every canonical event can create topology churn even when an event changes no material, while a fully permissive/deferred representation can postpone failures until an unacceptable export or body-connectivity boundary.

RCS-007 established that a broad global fuzzy tolerance can erase real material changes and that ambiguous local contact is safer to defer than to classify incorrectly. RCS-008 established that durable manufacturing identity cannot depend on OCCT face/edge identity and that provenance can prove some exact retraces redundant for geometry recomputation while preserving their journal events.

RCS-009 tested whether these findings support a precise volumetric regularization rule plus bounded topology deferral.

## Decision

The programme adopts the following architecture input:

1. **Physical subtractive material uses regularized volumetric set semantics.** For material set `A` and removal envelope `B`, the intended solid is `cl(int(A \ B))`, subject to explicit body-retention/process policy. Lower-dimensional point/edge/face-only remnants are not separate physical material volume.
2. **Lower-dimensional facts are not erased.** Contact, tangency, lineage and process evidence may remain semantic/provenance records even when they do not create material topology.
3. **Positive-volume removal is preserved regardless of broad numerical-tolerance convenience.** RCS-007 tolerance/uncertainty channels remain separate from the regularization rule.
4. **Bounded deferred topology is allowed as backend-private derived state.** A provider may retain pending removal envelopes/contact classifications instead of immediately constructing new B-rep boundaries when no hard reconciliation boundary is crossed.
5. **The canonical operation journal remains durable authority for manufacturing intent.** A pending ledger/cache is replaceable and rebuildable.
6. **Geometry recomputation may be elided only with RCS-008 semantic/provenance proof.** Transient topology identity, enumeration order, proximity or one global epsilon cannot prove a retrace equivalent.
7. **Connectivity/query/version/export boundaries can force reconciliation.** Possible material-body separation must be resolved before body-retention/scrap/clamping decisions, and primary STEP export must consume conventional validated reconciled solids.
8. **RCS-005 remains the export gate.** If pending state cannot reconcile to the required body set and accuracy/validity contract, export is refused. Mesh/STL or silent body loss is not a success fallback.
9. **OCCT General Fuse/`BOPAlgo_CellsBuilder` is a candidate reconciliation mechanism, not the durable material representation.** Its split parts/history remain backend-private evidence and its failures/warnings remain measurable research outcomes.

The exact production data structures, pending-state resource limits, reconciliation scheduler and process-specific policies remain RCS-010/RCS-011/RCS-012/RCS-013 work.

## Alternatives considered

### Immediate B-rep after every canonical operation

Retained as a valid implementation strategy where reliable and inexpensive, but rejected as a universal programme rule. It needlessly materializes topology for proven zero-volume contacts and exact provenance-equivalent retraces, and it prevents specialized/process-domain solvers from choosing better reconciliation boundaries.

### One enlarged global tolerance to suppress fragile topology

Rejected by RCS-007 measured evidence: global fuzzy tolerance produced valid-looking B-reps while erasing genuine positive-volume material changes and could become order-dependent across an operation chain.

### Fully defer all topology until save/export

Rejected. It makes body-connectivity decisions and exact engineering queries stale, risks unbounded pending state and moves too much failure risk to the export boundary.

### Treat General Fuse/CellsBuilder as the programme material ontology

Not selected. Pinned OCCT documentation shows CellsBuilder builds on General Fuse split parts over valid B-rep arguments. This can be useful for reconciliation/cell selection but does not itself establish a backend-independent deferred representation.

### Durable identity based on B-rep faces/edges

Rejected by RCS-008. Engineering-equivalent replay and reconciliation can regenerate/split/merge topology while material semantics remain stable.

## Evidence

- RCS-003 adversarial corpus defines point/edge/face contact, tangency, sliver, repeated/retraced operations, overlapping removal and connected/disconnected transitions as normal workloads.
- RCS-006 supplies the pinned immediate-B-rep benchmark and shared geometry/STEP metrics.
- RCS-007 measured semantic loss from global fuzzy tolerance and successful local deferral of ambiguous contact without decisive oracle mismatches.
- RCS-008 measured topology identity churn and demonstrated the semantic-lineage proof needed for safe exact-retrace geometry elision.
- **SOURCE:** CGAL Nef documentation defines regular sets via closure of interior and regularized set operations, providing established prior art for the solid-set definition: https://doc.cgal.org/latest/Nef_3/index.html
- **SOURCE:** pinned OCCT 8.0.1 CellsBuilder documentation states that it is based on General Fuse split parts and can select cells/remove same-material internal boundaries: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKBO/BOPAlgo/BOPAlgo_CellsBuilder.hxx
- **MEASURED (RCS-009):** CI run `35212264059`, job `105172585743`, artifact `10491869655` (`sha256:3b1c761b3cbf60dd6451ba6f6b25fc0970acc5ba5b484ce6f7f0133f1bdf9def`) measured eight candidate cases against pinned OCCT 8.0.1. All 8/8 satisfied the physical/body oracle and matched the immediate baseline's final volume and bounds within the campaign tolerance. Immediate materializations totalled 227 versus 6 for the bounded candidate; two zero-volume contacts were deferred and 218 provenance-equivalent repeated-event recomputations were elided. Both 2/2 CellsBuilder probes reproduced the candidate material/body result. The cut-through case reconciled to two solids and passed the automated AP242DIS STEP write/read-back with zero volume delta and approximately `5.0e-8 mm` maximum bounding-box delta. Durable evidence: `research/rcs-009/measured-summary-v1.json`.
- **MEASURED (RCS-009):** the candidate preserved the `0.0001 mm` positive-volume skim and `0.001 mm` tangent overlap as real material changes. Deferral therefore did not become a hidden small-feature tolerance.
- **MEASURED (RCS-009):** timing was workload-dependent. Repeated retraces benefited substantially from avoiding redundant recomputation, while the one-off `0.0001 mm` skim candidate was slower than immediate baseline. No universal performance conclusion is adopted.

## Consequences

- OpenSimachinist architecture synthesis may separate material semantics from the timing of B-rep topology construction.
- A material-body split is a volumetric connectivity event and does not depend on incidental lower-dimensional bridges/debris.
- Preview and incremental providers may retain more permissive private state, but exact/topology-dependent APIs must expose whether reconciliation is required.
- Replay/undo remains journal-driven; derived pending state can be invalidated rather than migrated as durable truth.
- RCS-010 and RCS-011 can define process-specific material domains/reconciliation boundaries without violating one universal immediate-B-rep rule.
- RCS-012 can compare cell/implicit/voxel/CSG hybrids against the same regularized physical semantics.
- The backend status model will need to distinguish `pending/deferred`, `reconciled`, `ambiguous classification`, `reconciliation failed` and export refusal rather than flattening them to success/failure.
- General Fuse/CellsBuilder remains available for measured reconciliation experiments without gaining programme-level identity status.

## Reversibility

Moderate to high before Gate 2. The regularized-volumetric semantic rule is intended as a stable physical interpretation but can be reconsidered if later process evidence demonstrates a lower-dimensional object must itself count as material. The particular pending-ledger/batched-Boolean prototype is highly reversible and is not selected as production architecture.

## Reconsideration triggers

Reconsider or narrow this decision if later measured work shows any of the following:

- process-specific machining semantics require a lower-dimensional remnant to act as physical material rather than metadata/contact;
- deferred state cannot answer required interactive engineering queries without reconciliation so frequent that no robustness/performance value remains;
- batching changes physical results or deterministic replay beyond declared bounds on realistic RCS-010/RCS-011 paths;
- body connectivity cannot be determined safely at the proposed hard boundaries;
- reconciliation fails RCS-005 STEP requirements at an unacceptable rate;
- RCS-012 finds an alternative representation that provides stronger regularized semantics with simpler reconciliation.
