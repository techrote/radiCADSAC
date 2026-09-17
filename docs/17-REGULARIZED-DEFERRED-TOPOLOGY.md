# Regularized material solids and bounded deferred topology

Status: RCS-009 research report; experimental recommendation pending measured campaign  
Date: 2026-09-17  
Issue: RCS-009

## Purpose and scope

RCS-009 tests whether manufacturing state should be understood primarily as **volumetric material** and whether selected fragile topology construction can be delayed until a meaningful reconciliation boundary.

This report deliberately separates three questions:

1. what physical material set an operation means;
2. when that material state must be represented as conventional B-rep topology;
3. which manufacturing facts must survive even when no B-rep entity is created for them.

The research does not replace the canonical operation journal, RCS-008 semantic lineage, or the RCS-005 STEP contract. It also does not claim that an unevaluated CSG tree or one batched Boolean is a universal manufacturing kernel.

## Evidence labels

Claims use the programme research labels:

- **SOURCE** — primary-source statement;
- **MEASURED** — reproducible RCS-009/RCS-006/RCS-007/RCS-008 experiment;
- **INFERENCE** — conclusion supported by source/measured evidence;
- **PROPOSAL** — candidate architecture rule still subject to later synthesis;
- **OPEN** — unresolved question.

## Hypotheses and falsification criteria

### H1 — volumetric regularization matches physical material semantics

**PROPOSAL:** for subtractive machining, the physical material result should normally be the regularized set difference

`A ⊖ B = cl(int(A \ B))`,

where `int` is interior and `cl` is closure. Point-, edge-, or face-only remnants that carry no volume therefore do not themselves constitute material.

This hypothesis is falsified for the programme if representative machining semantics require a lower-dimensional remnant to act as material rather than as metadata/contact/provenance, or if regularization destroys a volumetric connectivity distinction needed by the operation journal.

### H2 — bounded deferral can reduce needless topology churn

**PROPOSAL:** exact B-rep edges/faces need not be materialized for every canonical operation if the backend retains the operation/provenance facts, preserves every positive-volume material change, and reconciles before a query or boundary that requires conventional exact topology.

This hypothesis is falsified if the deferred candidate changes the physical result beyond declared bounds, loses body connectivity, makes replay/undo ambiguous, or cannot reconcile to an RCS-005-compatible STEP B-rep.

### H3 — General Fuse/cells may help reconciliation but are not deferred topology by themselves

**PROPOSAL:** OCCT General Fuse/`BOPAlgo_CellsBuilder` may be useful at reconciliation because it exposes split parts, cell selection, material labels, and internal-boundary removal. It is not sufficient evidence for a durable deferred representation because it still performs a General Fuse over valid B-rep arguments and creates split parts.

A measured CellsBuilder failure is therefore a valid negative result rather than a failure of the RCS-009 campaign.

## Precise programme definition — regularized material solid

A **regularized material solid** is the volumetric material set `M` satisfying `M = cl(int(M))` after the operation's set semantics are applied.

For subtraction, the programme-level physical interpretation is the regularized difference `cl(int(A \ B))`, subject to explicit process/body-retention policy.

**SOURCE:** CGAL's Nef-polyhedra documentation describes regular sets using closure of interior and defines regularized set operations by applying the ordinary operation followed by regularization. This is prior art for separating physical solid semantics from lower-dimensional set artifacts: https://doc.cgal.org/latest/Nef_3/index.html

The definition has four consequences for this programme:

- a point-only, edge-only, or face-only intersection has zero material volume and does not by itself remove or join material;
- a positive-volume skim remains a material change even when its dimension is numerically small;
- connected **material bodies** are connected components of the regularized volumetric material, not groups joined only by a zero-volume boundary contact;
- a lower-dimensional contact may still be semantically important as a contact/classification/provenance fact even though it is not material.

Regularization is therefore not synonymous with `ignore anything small`. Size/tolerance policies remain the separate RCS-007 channels.

## Precise programme definition — deferred topology

**Deferred topology** is a backend-private engineering state in which some canonical manufacturing events have not yet been converted into newly materialized B-rep faces/edges, while enough information is retained to reconstruct the intended regularized volumetric material at a required reconciliation boundary.

The RCS-009 candidate state is specifically:

- the last reconciled material solid/body set;
- an ordered set of immutable pending removal-envelope events tied to canonical operations and RCS-008 lineage;
- explicit contact/uncertainty classifications;
- setup/tool/envelope definition revisions;
- explicit hard-boundary requirements indicating when reconciliation can no longer be postponed.

The pending ledger is **derived backend state**. It does not replace the canonical operation journal and is safe to discard/rebuild from journal/provenance data.

Deferred topology does not mean `ignore topology until export`. It means topology materialization is permitted to lag manufacturing intent only while queries and semantic boundaries remain answerable without falsifying material state.

## Lower-dimensional debris versus meaningful contact

The founding rules are:

| Situation | Material meaning | Topology policy |
|---|---|---|
| Tool merely touches a face at zero penetration | no material removed | record contact if useful; no new material B-rep required |
| Tool is exactly tangent at one point/curve | no material removed | semantic tangency may remain pending; do not invent removal |
| Positive-volume overlap, however small | material removed | preserve removal intent; reconcile or retain exact pending envelope |
| Cut disconnects volumetric interior | material-body transition | must resolve body connectivity before retention/scrap/export decision |
| Two material regions touch only at point/edge/face | no volumetric bridge | do not merge bodies solely due to lower-dimensional contact |
| Contact is ambiguous inside an RCS-007 uncertainty interval | unresolved | retain pending classification; no global snap-to-same decision |
| Exact retrace is proven equivalent by RCS-008 semantic lineage | journal event remains, geometry may be redundant | geometry recomputation may be elided; provenance cannot be discarded |

The distinction is intentionally physical rather than based on OCCT entity dimension alone. A face can be meaningful as a **boundary** of volumetric material without itself being a separate material object.

## Interaction with RCS-007 tolerance/uncertainty

**MEASURED (RCS-007):** a single `0.0001 mm` global fuzzy tolerance erased genuine positive-volume changes in tested coincidence, tangency and skim cases while returning valid solids. RCS-007's operation-local uncertainty model instead deferred ambiguous contact cases without decisive oracle mismatches.

**INFERENCE:** deferred topology must consume the RCS-007 classification result rather than replace it with a larger tolerance. An uncertain contact can remain unresolved in the pending ledger. A known positive-volume operation cannot be converted to `no change` merely because it is smaller than a broad kernel epsilon.

This is why RCS-009's candidate uses zero fuzzy tolerance in the founding comparison and treats contact deferral as an explicit semantic state, not a fuzzy-Boolean side effect.

## Interaction with RCS-008 provenance and identity

**MEASURED (RCS-008):** independent engineering-equivalent replay preserved zero OCCT face identities; through-cut and overlapping-cut cases produced one-to-many/replacement ancestry; same-domain reconciliation produced many-to-one ancestry; an exact lathe retrace was geometry-equivalent while regenerating every face.

**INFERENCE:** topology identity cannot decide whether a pending event is redundant. Geometry recomputation may be collapsed only when semantic provenance proves equivalent target material-body lineage, setup/tool revisions and material-removal envelope, with no intervening intersecting mutation. The canonical journal event itself remains.

A deferred ledger therefore stores semantic references, not durable `TopoDS_*` identity.

## Reconciliation boundaries

RCS-009 distinguishes **hard** and **soft** reconciliation boundaries.

### Hard boundaries

A pending state must reconcile before:

- primary STEP export or any claim of RCS-005 export success;
- a body-retention/scrap/clamping decision after an operation that may change volumetric connectivity;
- an exact engineering query whose answer depends on materialized boundary topology or current body count;
- a setup/frame/tool-definition transition if pending envelopes cannot be transformed with explicit versioned semantics;
- an explicit committed-state/checkpoint request requiring conventional valid solid geometry;
- handing state to a downstream component whose contract requires reconciled B-rep.

### Soft candidate boundaries

End of an engaged pass or tool withdrawal is a useful default checkpoint, but reconciliation may remain deferrable when:

- no exact/topology-dependent query is requested;
- no body-connectivity decision is pending;
- setup/tool/envelope versions remain frozen and interpretable;
- pending-state growth remains within an explicit resource/policy bound.

RCS-010/RCS-011 may find process-specific boundaries superior to a universal end-of-pass rule.

## RCS-009 prototype

The executable candidate under `research/rcs-009/harness/` reuses RCS-006 fixture geometry and metrics.

It compares:

- **baseline:** immediate sequential OCCT `BRepAlgoAPI_Cut` after every operation;
- **candidate:** retain/deduplicate pending removal envelopes and reconcile the tested set with one multi-tool `BRepAlgoAPI_Cut`;
- **probe:** on selected cases, run `BOPAlgo_CellsBuilder` General Fuse, select stock cells outside the tool arguments, assign common material and remove internal boundaries.

The tested categories are:

- face-only coincidence/contact;
- tangent entry/exit and positive tangent overlap;
- sub-tolerance positive-volume skim;
- repeated exact slot passes;
- overlapping slot removals;
- cut-through/body separation;
- reconciled multi-body STEP write/read-back.

The comparison records validity, solid/face/edge counts, volume, bounding box, smallest features, analytic classes, Boolean-materialization count, geometry time, memory, contact/dedup semantics, CellsBuilder result and STEP round-trip evidence.

## OCCT General Fuse / CellsBuilder interpretation

**SOURCE:** pinned OCCT 8.0.1 `BOPAlgo_CellsBuilder` is based on General Fuse, whose result is all split parts of its arguments. The API can select cells, assign material values and remove same-material internal boundaries. Its documentation requires valid B-rep arguments and notes limitations/warnings for internal-boundary removal. Pinned source: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKBO/BOPAlgo/BOPAlgo_CellsBuilder.hxx

**INFERENCE:** this is relevant to reconciliation and cell-complex research because it can make material selection explicit after one global split. It is not itself a deferred-topology architecture: the General Fuse still constructs a split B-rep arrangement, and its topology/history remain OCCT-private evidence.

RCS-009 therefore records CellsBuilder behaviour without making successful use a prerequisite for the candidate model.

## STEP reconciliation contract

Internal permissiveness ends before STEP.

For an RCS-009 state to be exportable:

1. all pending material-changing envelopes required by the selected revision are reconciled;
2. unresolved contact classification that could change material/body semantics is resolved or export is refused;
3. every selected material body is materialized as a conventional valid engineering solid;
4. body count/selection obeys the preserve-all/explicit-selection rule from RCS-005;
5. geometric/tolerance/analytic policies are checked under the RCS-005 gates;
6. serialization and fresh read-back must pass the automated STEP checks;
7. independent-consumer qualification remains part of the RCS-005 profile rather than being replaced by OCCT self-readback.

No pending ledger, SDF, mesh or CellsBuilder compound is allowed to masquerade as successful primary STEP output. A reconciliation failure is an explicit export refusal/failure, not permission to silently drop bodies or fall back to STL.

## Failure modes from deferring too much

Deferred topology creates its own risks:

- **stale exact queries:** UI/inspection asks for a boundary that has not been reconciled;
- **connectivity blindness:** a pending cut has already separated material but body policy has not been resolved;
- **unbounded pending state:** a long engagement accumulates too many interacting envelopes and produces a reconciliation cliff;
- **unsafe deduplication:** geometrically similar operations are collapsed without the RCS-008 provenance proof;
- **chronology loss:** batching changes meaning where tool/setup/body policy or an intervening mutation makes operation order semantically relevant;
- **version drift:** a pending envelope is interpreted after setup/tool definitions change;
- **uncertainty leakage:** ambiguous RCS-007 contact is silently treated as either contact or overlap;
- **reconciliation pathology:** a large batched Boolean/General Fuse can still fail, hang or create poor topology;
- **export failure:** permissive internal state cannot be converted within RCS-005 accuracy/body/validity requirements;
- **topology-dependent feature queries:** downstream logic assumes persistent face/edge names that RCS-008 explicitly rejected as durable identity.

These failure modes are why the proposal is **bounded** deferred topology, not defer-everything-until-export.

## Provisional recommendation

**PROPOSAL:** carry regularized volumetric material semantics and bounded deferred topology into RCS-013 architecture synthesis as separate concepts:

- regularized volumetric material semantics should define what subtractive material physically means;
- deferred topology should be an implementation-private optimization/robustness tool available to process providers, not the durable project model;
- local uncertainty and semantic lineage govern whether an event may stay pending or be recomputation-elided;
- body-connectivity, exact-query, setup/version, checkpoint and STEP boundaries can force reconciliation;
- immediate B-rep remains a valid strategy when cheap/reliable, and specialized RCS-010/RCS-011 material domains may defer/reconcile differently;
- General Fuse/CellsBuilder remains a candidate reconciliation facility rather than the programme's material ontology.

This recommendation becomes evidence-backed only after the RCS-009 CI campaign is measured. Its final status and quantitative findings are recorded in the issue's decision record and measured summary.

## Open questions carried forward

- How large may a pending envelope set become before forced reconciliation is economically preferable?
- Which exact/incremental queries can operate directly on a pending material model without a full B-rep?
- Can process-specific lathe/mill solvers provide stronger regularized guarantees than general 3D batching?
- When two pending removal envelopes overlap, which history/order information is necessary for diagnostics even when set difference is geometrically order-independent?
- Can a CellsBuilder/cell-complex representation be retained incrementally without paying full General Fuse topology cost after every event?
- Which alternative representations in RCS-012 provide a better permissive state while preserving analytic reconstruction?
- How should independent STEP interoperability qualification be automated beyond the existing RCS-005 strategy?
