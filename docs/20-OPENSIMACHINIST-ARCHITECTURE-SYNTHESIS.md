# OpenSimachinist architecture synthesis and Gate-2 decision

Status: RCS-013 accepted architecture synthesis  
Date: 2026-09-17  
Machine-readable contract: `research/rcs-013/architecture-v1.json`  
Unresolved register: `research/rcs-013/unresolved-v1.json`

## Purpose and scope

RCS-013 converts the accepted RCS-005 and RCS-007–RCS-012 research into an initial OpenSimachinist architecture. It deliberately does **not** implement the production kernel. Its purpose is to select a productive starting architecture that preserves tested escape routes where the research remains incomplete.

The decision is evidence-driven rather than an extrapolation from one geometry library. The canonical manufacturing journal, material-body semantics, semantic lineage and STEP success contract remain programme-owned. Geometry implementations are replaceable derived machinery.

## Executive decision

Gate 2 selects a **semantic-provider hybrid architecture**:

- MSAC sends versioned manufacturing semantics, not OCCT or Godot objects.
- The canonical journal and immutable revision/body history remain the durable source of intent.
- A backend-independent semantic lineage graph owns durable material-body, operation, tool-envelope and split/merge ancestry.
- A policy/dispatch layer chooses process-specific geometry providers according to explicit capabilities.
- The qualified fixed-axis lathe subset uses the RCS-010 axisymmetric axial/radial material provider as a first-class solver.
- Milling uses a hierarchy: recognized analytic operations, strictly proven canonical batches, exact per-segment cutter envelopes, then bounded local fallback/reconciliation. No universal freehand n-ary batch is accepted.
- OCCT 8.0.1 remains the initial exact/parametric B-rep, validation, reconciliation and STEP baseline behind programme-owned adapters. A wholesale OCCT fork is not selected.
- Regularized volumetric semantics and bounded deferred topology may postpone unnecessary B-rep materialization, but connectivity, topology-dependent queries, provider handoff and export can force reconciliation.
- Local cell/mesh/voxel/SDF/exact fallbacks are permitted only with explicit scope and error metadata. They are not whole-workpiece engineering truth and must reconcile to conventional B-rep before successful STEP export.
- Geometry execution defaults to process-isolated workers with timeouts until RCS-017 measures whether specific OCCT Boolean/STEP paths can safely share a process.

This is an **isolated OCCT backend with programme-owned semantic/provenance/policy subsystems, process-specialized providers and bounded hybrid escape routes**. It is neither a deep fork nor a monolithic B-rep-only design.

## Gate-2 evidence assessment

The roadmap's Gate-2 conditions are met:

| Gate-2 requirement | Accepted evidence | Result |
|---|---|---|
| Baseline OCCT behavior on core fixtures | RCS-006 plus RCS-004 audit | Measured, pinned OCCT 8.0.1 baseline and reproducible harness exist. |
| Tolerance/provenance model evaluated | RCS-007 and RCS-008 | Global fuzzy tolerance produced valid-but-wrong material results; local uncertainty plus semantic lineage is the accepted direction. |
| Lathe specialization evaluated | RCS-010 | Nine qualified cases passed; axisymmetric reconstruction preserved analytic geometry and all enabled STEP round trips. |
| Mill strategy evaluated | RCS-011 | 88 attempts measured; strict canonical batching can be effective, while unproven freehand batching and dense sampled-pose B-rep fallback produced decisive negative evidence. |
| Alternative/hybrid representation evaluated | RCS-012 | Exact bounded cell/deferred representation succeeded in its narrow subset; coarse voxel occupancy demonstrated explicit sub-cell semantic loss. |
| STEP criteria drafted and exercised | RCS-005 plus later campaigns | Four-layer conformance contract exists; geometry/read-back gates were exercised in RCS-006/009/010/011. |

Gate 2 explicitly does not require every pathological case to be solved. The remaining work is ranked under `research/rcs-013/unresolved-v1.json` rather than hidden.

## Architecture options matrix

| Option | Benefits | Evidence against / cost | Gate-2 decision |
|---|---|---|---|
| Deep OCCT fork | Maximum source-level control over Boolean/intersection internals. | RCS-004 found plausible narrow fork seams but no evidence requiring wholesale divergence; upstream remains active; fork does not solve journal, semantic identity or process-domain architecture. | **Reject initially.** Retain narrow source modification as an evidence-triggered escape route. |
| Monolithic isolated OCCT B-rep core | Mature analytic B-rep, validation, Boolean and STEP stack; straightforward baseline. | RCS-007 measured valid-but-wrong fuzzy results; RCS-009 showed useful deferral; RCS-010/RCS-011 showed process-specific benefits and path-dependent strategy behavior. | **Retain as provider/reconciliation baseline, reject as universal architecture.** |
| Whole-model mesh/voxel/implicit core | Potential robustness against topology degeneracy; useful local operations. | RCS-012's 0.5 mm occupancy missed a real 0.001 mm plunge and erased a 0.001 mm cusp/body; analytic STEP recovery remains mandatory. | **Reject as founding authoritative whole-model state.** |
| Exact arithmetic / Nef-style core everywhere | Strong exact set-operation prior art. | Does not itself solve manufacturing semantics, operation scaling, analytic STEP reconstruction or provenance; Nef_3 package licensing is GPL-3+ in the reviewed CGAL version. | **Defer; use targeted exact components only where measurements justify them.** |
| Semantic-provider hybrid | Preserves stable manufacturing intent while allowing specialized lathe/mill solvers, deferred material state, OCCT reconciliation and bounded alternatives. | More orchestration and contract design than a monolith; reconciliation boundaries must be explicit. | **Selected.** Best fit to the combined evidence and replaceability invariant. |

## Programme-owned versus implementation-private state

### Durable programme authority

The following survive backend replacement, replay and project persistence:

- canonical manufacturing journal and canonicalization profile;
- programme-owned pending-intent transactions anchored to a committed revision while `accepted_pending`;
- immutable workpiece revisions and material-body split/merge transitions;
- setup, machine and tool revisions;
- explicit coordinate frames/transforms/units;
- semantic lineage graph;
- tolerance/uncertainty policy versions;
- provider capability/dispatch profile versions used for replay diagnostics;
- STEP exporter/conformance profile records.

### Replaceable derived state

The following can be invalidated and rebuilt:

- OCCT `TopoDS_*` topology and operation-local history attachments;
- the lathe provider's axial/radial material representation;
- pending/deferred removal ledgers;
- preview meshes;
- local fallback cells/triangles/voxels/SDF state;
- reconciled B-rep caches;
- backend acceleration structures.

This separation is the principal escape route against premature kernel lock-in.

## Component architecture and data flow

The initial logical flow is:

`MSAC machine module` → `versioned programme API` → `journal ingress / revision validation` → `semantic lineage + policy/dispatch` → `lathe | mill | generic B-rep | bounded fallback provider` → `regularized/deferred material coordinator` → `B-rep reconciliation/validation` → `STEP conformance adapter`.

Preview branches from provider/material state and is explicitly derived. It never becomes engineering authority.

The principal components are:

- **Journal ingress** validates canonical operations, revision ancestry, units/frames and setup/tool revisions.
- **Semantic lineage** owns durable material/body/operation/envelope ancestry, including explicit split, merge, replacement and ambiguity.
- **Policy/dispatch** owns tolerance-channel selection, provider capability predicates, fallback authorization and reconciliation policy.
- **Axisymmetric lathe provider** owns the qualified fixed-axis turning representation and reconstruction.
- **Mill provider** owns the strategy hierarchy and strict recognition/canonicalization rules.
- **Generic B-rep provider** uses isolated OCCT operations for qualified general exact work.
- **Deferred-material coordinator** owns bounded pending material/contact work and hard reconciliation boundaries.
- **Bounded fallback adapter** hosts optional local alternative representations with explicit error/scope contracts.
- **B-rep reconciler** reconstructs conventional engineering topology, recovering provenance-known analytic boundaries first and then validating the result.
- **STEP conformance adapter** applies RCS-005 body-selection, units, analytic-fidelity, read-back and interoperability rules.
- **Worker supervisor** contains crashes/hangs/global state and records backend/version/build evidence.

## Stable programme-facing API proposal

The API is semantic and versioned before transport technology is selected. RCS-013 deliberately does not choose RPC, shared-library ABI, IPC encoding or Godot GDExtension deployment.

Required request families are:

- capability discovery;
- apply canonical operations;
- commit a workpiece revision;
- deterministic replay/rebuild;
- material-state/body query;
- preview request;
- explicit reconciliation request;
- reconciled geometry/inspection query;
- STEP export.

Every engineering request carries enough identity to be replayable: contract version, project/workpiece revision, journal schema version, operation IDs, setup revision, tool revision, coordinate frame, tolerance-policy version and relevant material-body selection.

Every engineering response carries programme status, resulting revision/body IDs, lineage events, provider profile, reconciliation state and diagnostics. `TopoDS_*`, OCCT handles, Godot objects, triangle indices and voxel/cell IDs are forbidden from the stable contract.

The production handoff may refine field names and serialization, but may not change the semantic ownership boundary without a new decision record.

## Tolerance, uncertainty and equivalence

RCS-007 rules become architecture policy, not merely research advice. The initial design keeps separate channels for input/sampling resolution, machine/control resolution, manufacturing tolerance, numerical uncertainty, topology equivalence, contact classification, preview tolerance, export tolerance and validation tolerance.

A single enlarged global fuzzy epsilon is prohibited as programme truth. In the measured RCS-007 campaign, OCCT fuzzy `0.0001 mm` erased four real material changes while returning valid one-solid B-reps, and a 100-step chain became order-dependent by approximately `7.5396 mm³`.

Operation-local uncertainty may produce an ambiguous/contact state. That state means **defer/reconcile while retaining signed manufacturing intent**, not `no material change`. Positive-volume removal remains positive intent even below a convenient numerical threshold.

Exact retrace geometry work may be elided only with the RCS-008 semantic-lineage proof. The journal event remains present.

## Provenance and semantic identity

RCS-008 makes durable identity semantic rather than topological. This is required because independent engineering-equivalent reconstruction preserved zero tested OCCT face identities, while split and same-domain cases produced genuine one-to-many and many-to-one topology ancestry.

The programme lineage model therefore anchors:

- material bodies;
- canonical operations;
- tool/removal envelopes;
- setup/tool revisions;
- semantic boundary roles where meaningful;
- reconciliation events.

Backend histories such as `BRepTools_History` and `TNaming` are diagnostic/evidence attachments. They may populate lineage evidence but do not define persistent project identity.

Ambiguous ancestry remains explicit. Enumeration order, object address/hash, nearest-neighbor matching or tolerance transitive closure cannot silently resolve it.

## Regularized material and deferred topology

Physical subtractive material follows the accepted regularized volumetric interpretation `cl(int(A \ B))`. Lower-dimensional contact facts remain useful semantic/provenance records without becoming separate material volume.

Providers may postpone B-rep construction for:

- proven zero-volume contact;
- provenance-proven exact retraces;
- bounded groups of removal envelopes whose material semantics remain explicit;
- local fallback regions whose representation/error budget is known.

Deferral is bounded rather than `wait until export`. Reconciliation is forced before material connectivity/body-retention decisions, topology-dependent exact queries, provider handoff when assumptions change, explicit reconciled-geometry requests and STEP export. Production must additionally establish resource/time/query thresholds for pending state.

## Lathe provider policy

The RCS-010 axisymmetric provider is first-class for the qualified fixed-axis subset:

- cylindrical OD turning;
- facing;
- shoulders;
- linear taper/chamfer-class boundaries;
- cylindrical through/blind boring;
- exact/repeated finishing and retraces;
- bounded canonicalized analogue-controlled variants whose removal envelope stays rotationally symmetric.

The provider's axial/radial representation is private derived state. It reconciles to validated conventional B-rep at export or provider handoff.

Nine RCS-010 cases had zero acceptance failures; all 21 enabled STEP strategy/file combinations passed the automated round-trip gates. The direct axisymmetric path also retained true planes/cylinders/cones in the measured set.

This does **not** claim real insert nose-radius/orientation, grooving/parting connectivity, undercuts, eccentric/live-tool operations or arbitrary non-axisymmetric turning are solved. Unsupported semantics trigger handoff or refusal, not hidden approximation.

## Mill strategy hierarchy

Milling is not assigned one universal swept-solid algorithm. The initial hierarchy is:

1. explicit recognized analytic/process operation where semantics provide it;
2. strict canonical simplification/batching only with an equivalence proof;
3. exact per-segment cutter-envelope removal as the fixed-orientation correctness baseline;
4. bounded local hybrid/deferred fallback for pathological regions under an explicit error contract;
5. reconcile to conventional B-rep or refuse authoritative completion if no qualified route preserves the operation.

This hierarchy reconciles RCS-011's positive and negative results. A 50-segment collinear path was safely reduced to one batch and from 1137 to 16 faces while preserving measured volume. In contrast, a one-shot near-coincident freehand retrace batch returned a valid but materially wrong B-rep, and all ten dense sampled-pose fallback attempts timed out at 30 seconds.

Therefore `valid B-rep` is not a sufficient strategy oracle and arbitrary freehand batching is not the universal fallback.

## Bounded hybrid fallbacks

RCS-012 permits local alternative representations while rejecting silent lossy promotion to engineering truth. The exact orthogonal-cell/deferred prototype matched all 16 volume/body attempts in its deliberately narrow subset; the 0.5 mm sparse occupancy prototype missed a 0.001 mm plunge and erased a 0.001 mm cusp/body.

Each fallback island must record:

- supported geometric/material domain;
- spatial or construction error budget;
- source manufacturing/provenance anchors;
- current reconciliation state;
- conditions requiring refusal.

Known analytic boundaries are recovered from semantics/provenance before generic fitting. A fallback-derived state can become successful engineering output only after conventional B-rep reconciliation and the RCS-005 STEP gates.

No concrete fallback library is mandatory at Gate 2. Manifold/OpenVDB-style techniques and targeted exact arithmetic remain replaceable candidates after workload-specific measurement.

## Reconciliation and STEP boundary

RCS-005 remains authoritative. STEP success is not `writer returned OK`; it requires committed pre-export state, serialized-file checks, geometry-aware fresh read-back and a currently qualified interoperability profile.

The default export selection is all material bodies in the committed revision. There is no implicit largest/first/primary-body inference. Explicit subset export records requested and omitted body identities.

Internal deferred/hybrid states end at the export boundary. The reconciler must produce conventional manifold B-rep solids, preserve intended analytic classes within policy, preserve body connectivity/count and remain within declared geometric budgets. If it cannot, export is refused or remains unqualified; mesh/STL is never the engineering success fallback.

## Preview, incremental engineering state and replay

Preview geometry exists for responsiveness and visualization and may be tessellated/approximate. It is never the committed authority.

An operation can produce `accepted_pending` after its canonical intent is durably stored in a **programme-owned pending-intent transaction** anchored to the last committed revision. That status does not itself create a new committed workpiece revision or body transition. Provider/deferred state remains disposable and can be regenerated after save/crash/restart from the committed parent plus the ordered pending transaction chain. Exact material/body/connectivity queries report whether reconciliation is required. Only successful reconciliation/commit creates the next immutable revision/body transition; a `reconciled` revision has conventional validated B-rep available for exact topology queries/export.

Replay starts from programme-owned journal/revision/lineage state. Provider-private caches may be discarded after backend upgrades. Diagnostic provenance records the implementation, version, build profile and dispatch policy used to materialize derived geometry, allowing regression comparison without making the backend part of project meaning.

## Error and status model

The stable engineering status vocabulary must distinguish at least:

- `accepted_pending` — intent accepted; bounded material/topology work remains deferred;
- `reconciled` — conventional validated engineering geometry exists;
- `success` — the requested operation, query or qualified export completed;
- `refused_unsupported` — no qualified provider supports the requested semantics;
- `refused_unresolved_ambiguity` — material meaning cannot be resolved safely within current policy;
- `invalid_topology`;
- `wrong_geometry`;
- `tolerance_breach`;
- `kernel_error`;
- `crash`;
- `timeout`;
- `nondeterministic_result`;
- `step_writer_failure`;
- `step_roundtrip_failure`;
- `interoperability_unqualified`.

These are programme-facing classes; backend warnings/statuses remain nested diagnostics. A produced file or valid B-rep cannot overwrite a higher-level physical/conformance failure.

## Versioning and replay strategy

Version independently:

- programme API contract;
- journal and canonicalization schema/profile;
- machine/tool/setup definitions;
- semantic lineage schema;
- tolerance/uncertainty policy;
- provider capability/dispatch profile;
- STEP exporter/conformance profile.

Saved project meaning is defined by programme semantics. A backend upgrade may invalidate cached B-rep/provider state and replay it. Schema migrations transform programme-owned semantic data explicitly; they never reinterpret stale backend topology identities.

Cross-version replay should report whether the new derived engineering state is equivalent within the accepted validation policy. A divergence is a measurable migration/replay result, not something hidden by overwriting the old cache.

## Concurrency and process-isolation boundary

RCS-004 found both explicit per-instance configuration and remaining process-global/static surfaces in OCCT. RCS-017 is dependency-ready but not a Gate-2 blocker under the issue graph.

Until RCS-017 provides measured evidence, the architecture adopts process-isolated geometry workers with per-attempt/job timeouts as the safe default for exact geometry and STEP work. Explicit `DESTEP_Parameters`/operation-local settings are preferred, but the production scheduler must not infer global thread safety from them.

Process isolation is intentionally reversible. If RCS-017 proves a narrower set of operations/configuration can safely share a process, deployment can optimize without changing the stable semantic API or persisted projects.

## Dependency, licensing and upstream-sync strategy

OCCT remains pinned, identifiable and isolated behind programme adapters. The initial architecture prefers upstream shared-library use. A deep fork is not created until a reproduced failure demonstrates that a narrow kernel seam is the limiting cause and programme-level policy/provider/reconciliation fixes are insufficient.

Any OCCT modifications remain clearly distinguishable with license notices/source obligations preserved. Release packaging requires a dedicated compliance audit rather than assuming research conclusions are legal advice.

Optional fallback libraries remain adapters, not project ontology. RCS-012's reviewed candidates include Apache-2.0 Manifold/OpenVDB-style approaches and exact-geometry options; CGAL Nef_3's reviewed package is GPL-3+, which is a material dependency decision rather than something to absorb accidentally.

Every benchmark/release records exact dependency version/commit and build profile.

## Contradictory findings reconciled

### Mature OCCT versus non-B-rep architecture

OCCT is strong in analytic B-rep, validation, Booleans and STEP. The research does not reject it. Instead, it rejects making OCCT topology the durable programme model. OCCT is used where it is strong behind replaceable contracts.

### Valid topology versus correct manufacturing result

RCS-007 and RCS-011 produced valid-looking results that violated material intent. The architecture therefore retains physical/material oracles and semantic intent above kernel validity.

### Topology deferral versus small positive cuts

RCS-009 supports deferring zero-volume contacts/retraces, while RCS-007 shows a broad fuzzy tolerance can erase real small cuts. Deferral is semantic and bounded; positive-volume removal is never suppressed just because it is numerically inconvenient.

### Process specialization versus universal STEP output

Lathe/mill providers may use private representations, but the programme has one reconciliation/export contract. Specialized state is an implementation optimization/robustness mechanism, not an alternate engineering file format.

### Mill batching performance versus freehand correctness

Strict canonical batching is admitted only where equivalence is proven. The materially wrong freehand batch prevents the optimization from being generalized by convenience.

### Robust discrete fallbacks versus dimensional fidelity

Discrete/cell approaches are valuable local escape routes, but RCS-012 demonstrates that coarse resolution can erase manufacturing-scale features. Their resolution/error budget is explicit and distinct from manufacturing tolerance.

### Process isolation versus potential concurrency performance

The absence of RCS-017 does not justify assuming shared-process safety. Process isolation is the safe default and a reversible performance cost, so Gate 2 can proceed without pretending concurrency research is complete.

## Unresolved research register

The ranked machine-readable register is `research/rcs-013/unresolved-v1.json`. The highest-priority items are:

- robust bounded handling of pathological arbitrary/freehand mill removal;
- real lathe insert/nose-radius/orientation and parting/grooving envelope qualification;
- production STEP exporter plus independent CAD/CAM interoperability qualification;
- curved/non-orthogonal hybrid reconstruction with bounded analytic/residual error;
- RCS-017 OCCT concurrency/global-state measurement;
- realistic provider-handoff/reconciliation frequency/cost;
- concrete semantic-lineage persistence encoding;
- bounded-deferred resource thresholds;
- targeted exact-arithmetic seams and future process coverage;
- release-time license compliance packaging.

These are implementation/research tasks, not reasons to preserve a false architecture vacuum. The current policy gives each one a safe refusal/isolation/reconciliation boundary.

## Gate-2 conclusion

**Gate 2 — architecture-choice ready — is satisfied.** The programme now has measured evidence for every roadmap category and an architecture that explicitly preserves STEP integrity, backend replaceability, specialized lathe/mill paths and fallback escape routes.

Gate 2 does not claim universal computational-geometry correctness. It authorizes the programme to proceed to RCS-014/RCS-015 handoff generation with unresolved research carried forward.

RCS-017 may still refine the worker deployment boundary. Until then, process isolation remains part of the initial architecture rather than an untested assumption.

## Implications for OpenSimachinist

OpenSimachinist implementation should begin with measurable vertical slices rather than a monolithic kernel rewrite: semantic request/revision/lineage substrate, one qualified lathe path, one qualified mill path, reconciliation/validation, and STEP export against the existing corpus. Provider/fallback capabilities should expand only with regression evidence.

## Implications for MSAC

MSAC can depend on a stable semantic contract without learning any kernel representation. It may present pending/reconciled/refused states, preview derived geometry, preserve undo/replay semantics and request STEP export with explicit body selection. Machine modules provide process semantics; exact geometry providers remain OpenSimachinist-owned.
