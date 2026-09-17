# OpenSimachinist founding specification

Status: implementation-ready founding specification  
Handoff: `opensimachinist-handoff/1.0`  
Architecture: `semantic-provider-hybrid-v1`  
Genesis source state: radiCADSAC main `23519b5989b14f1b0947dca77588729585150115`

## Product and kernel brief

**OpenSimachinist** is the manufacturing-native geometry, reconciliation, validation and engineering-export backend for the MSAC programme. It is not a conventional sketch/feature-tree CAD application and it is not the visual machine simulator. Its job is to consume versioned manufacturing intent, maintain trustworthy workpiece/material semantics, exploit process-specific geometry strategies, expose engineering state and diagnostics, and produce conventional usable STEP output.

The founding interaction model is direct simulated machining. MSAC machine modules decide what physical manufacturing action occurred; OpenSimachinist decides how to realize that action as robust engineering geometry. The manufacturing language and durable project meaning therefore live above any one geometry kernel.

Initial process scope is **lathe and mill only**. The architecture must permit later process providers without weakening the stable programme boundary.

Genesis evidence: `docs/00-FOUNDING-BRIEF.md`, `docs/01-MSAC-GEOMETRY-CONTRACT.md`, `docs/decisions/DR-0003-initial-scope-lathe-mill.md`, `docs/decisions/DR-0015-gate-2-semantic-provider-hybrid-architecture.md`.

## Non-negotiable invariants

The production implementation must preserve these invariants unless a later programme decision explicitly supersedes them with evidence.

- **Manufacturing intent is durable authority.** The canonical operation journal, immutable workpiece revisions, material-body transitions, semantic lineage and versioned definitions/policies survive backend replacement. See DR-0002, DR-0006, DR-0007 and DR-0008.
- **Geometry implementation is replaceable.** OCCT objects, provider-private material domains, pending/deferred ledgers, meshes, cells/voxels/SDFs, acceleration structures and reconciled B-rep caches are derived state. See DR-0004 and DR-0015.
- **STEP is mandatory primary engineering output.** STL/mesh may be derived output, never the success fallback for an unreconciled or invalid engineering state. See DR-0001 and DR-0009.
- **Pathological geometry is normal workload.** Coincidence, tangency, zero-volume contact, sub-tolerance removal, slivers, retraces, self-crossing paths, overlaps, disconnected bodies and very large operation counts are not rejected merely because a kernel finds them inconvenient. See DR-0005 and the RCS-003 corpus.
- **Disconnected material is explicit.** Parting/cut-through may yield multiple bodies. No implicit largest/first/primary body rule may silently delete or merge them. See DR-0008 and DR-0009.
- **No private-kernel types cross the stable API.** `TopoDS_*`, OCCT handles, Godot objects, triangle-index identity and voxel/cell IDs are private implementation details. See DR-0004 and DR-0015.
- **Units, frames, transforms and policies are explicit and versioned.** Saved meaning may not depend on hidden metric/imperial, handedness, axis-order or tolerance assumptions. See DR-0006.
- **One fuzzy epsilon is not programme truth.** Manufacturing tolerance, numerical uncertainty, topological equivalence, contact classification, preview, export and validation are separate policy channels. See DR-0010 and RCS-007 evidence.
- **Persistent identity is semantic, not topological.** Durable identity belongs to workpiece/material bodies, operations, tool/removal envelopes, setup/tool revisions, semantic boundary roles and lineage events. See DR-0011 and RCS-008 evidence.
- **Internal permissiveness ends at engineering/export boundaries.** Deferred/hybrid state is legal only under explicit capability/error/reconciliation rules. A successful STEP result must be conventional validated engineering geometry. See DR-0012, DR-0014 and DR-0009.
- **Algorithm failure is not invalid user intent.** Provider/kernel failures, unsupported semantics, ambiguity, geometry errors and conformance failures remain distinguishable.

## Stable programme-facing API contract

The founding API is a **semantic contract**, not a transport decision. Do not select RPC, shared-library ABI, IPC framing, Protocol Buffers, FlatBuffers, JSON or a Godot integration mechanism merely because this document needs field names. Transport remains replaceable.

### Request families

The implementation must support versioned equivalents of:

- `capabilities` — provider/process/profile discovery;
- `apply_canonical_operations` — apply one or more journal operations against an immutable parent revision;
- `commit_revision` — establish the durable engineering/material result and lineage transitions of accepted intent;
- `replay_revision` — reconstruct derived state from programme-owned semantic history;
- `query_material_state` — bodies, connectivity/status and representation/reconciliation state;
- `request_preview` — explicitly non-authoritative visualization geometry;
- `request_reconciliation` — force conventional engineering state when required;
- `inspect_reconciled_geometry` — exact/topology-dependent inspection against reconciled state;
- `export_step` — export selected committed bodies under a named qualified conformance profile.

### Common request identity

Engineering requests carry enough identity for deterministic interpretation and diagnostics, including at least:

- programme contract version;
- project/workpiece revision;
- journal schema and canonicalization profile;
- canonical operation IDs;
- setup revision;
- tool revision;
- explicit coordinate-frame reference;
- tolerance/uncertainty policy version;
- requested material-body IDs where selection matters.

### Common response identity

Engineering responses carry at least:

- contract version;
- programme-facing engineering status;
- resulting/inspected revision ID;
- material-body IDs;
- lineage events;
- provider/dispatch profile;
- reconciliation state;
- structured diagnostics with backend/version/build evidence.

The stable API may reference opaque derived-artifact handles for cache efficiency, but such handles are never durable project meaning and must be invalidatable/rebuildable.

Genesis evidence: `docs/01-MSAC-GEOMETRY-CONTRACT.md`, `research/rcs-013/architecture-v1.json`, DR-0004 and DR-0015.

## Canonical journal expectations at backend ingress

The founding journal contract is `msac-journal/1.0`. OpenSimachinist consumes **canonical physical/process state**, not raw gamepad values or render-frame samples.

Required backend assumptions include:

- dimensional translation is stored canonically as signed 64-bit `length_nm` quantities;
- angle uses `angle_nrad`, time `time_ns`, rates use fixed physical-unit integer tokens, and durable rotation components use the journal's fixed-rational convention;
- canonical frames are explicit right-handed Cartesian frames with versioned parent relations and explicit transform composition;
- tool, setup, machine/process and normalization/tolerance definitions referenced by committed operations are immutable revisions;
- canonicalization never fits/simplifies across semantic boundaries such as setup, tool revision, process, target body or engagement changes;
- path simplification/fitting is allowed only under recorded deterministic error bounds;
- repeated/retraced actions remain journal events even where geometry recomputation can later be proven redundant;
- workpiece revisions are immutable nodes; undo/redo/branching selects history rather than rewriting it;
- derived backend snapshots are disposable accelerators keyed to semantic revision plus implementation/policy identity.

The backend may reject malformed or unsupported canonical records, but it may not reinterpret a historical journal under a new policy silently. Migration creates an explicit new semantic version/revision.

Genesis evidence: `docs/10-CANONICAL-JOURNAL-CONTRACT.md`, DR-0002, DR-0006, DR-0007 and DR-0008.

## Selected component architecture

The accepted logical flow is:

`MSAC machine module` → `versioned programme API` → `journal ingress/revision validation` → `semantic lineage + policy/dispatch` → `lathe | mill | generic B-rep | bounded fallback provider` → `deferred-material coordination` → `B-rep reconciliation/validation` → `STEP conformance adapter`.

Preview branches from derived provider/material state and never becomes engineering authority.

### Programme-owned components

- **Journal ingress** — validates schemas, revision ancestry, definition references, units/frames and operation semantics.
- **Revision store** — owns immutable workpiece revisions and body-set transitions.
- **Semantic lineage** — owns body/operation/envelope ancestry, split/merge/replacement and explicit ambiguity.
- **Policy/dispatch** — owns provider capability predicates, tolerance channels, fallback authorization and reconciliation policy.
- **STEP conformance policy** — owns programme-level export success/refusal independently of writer return codes.

### Provider/backend components

- **Axisymmetric lathe provider** — first-class fixed-axis turning provider for the qualified subset.
- **Mill provider** — process hierarchy; never one universal arbitrary-freehand batch.
- **Generic B-rep provider** — isolated OCCT operations where qualified.
- **Deferred-material coordinator** — bounded regularized/pending state with hard reconciliation boundaries.
- **Bounded fallback adapter** — optional local alternative representations with declared domain/error metadata.
- **B-rep reconciler/validator** — materializes conventional bodies, recovers provenance-known analytic boundaries first, validates topology/geometry and records reconciliation deltas.
- **Worker supervisor** — contains crashes/hangs/global-state risk using process isolation and timeouts by default.

Genesis evidence: DR-0015 and `research/rcs-013/architecture-v1.json`.

## Representation and reconciliation strategy

The authoritative meaning is a regularized volumetric material state plus semantic history, not continuous persistence of every transient face/edge.

Physical subtraction follows the accepted regularized interpretation `cl(int(A \ B))`. Proven zero-volume contacts can remain semantic facts without requiring separate material volume. Proven exact retraces can preserve the journal/lineage event while eliding redundant geometry recomputation.

The implementation may use provider-private axisymmetric domains, pending removal ledgers and bounded local cell/mesh/voxel/SDF/exact islands. Every non-B-rep representation must have:

- a declared supported domain;
- an explicit construction/spatial error budget;
- provenance anchors to the manufacturing operations/material bodies that created it;
- a reconciliation status;
- refusal criteria when it cannot recover conventional engineering geometry safely.

Reconciliation is forced before at least:

- material-body connectivity/retention decisions;
- topology-dependent exact inspection;
- provider handoff when representation assumptions change;
- an engineering checkpoint that cannot safely rely on replayable private state;
- explicit API reconciliation requests;
- STEP export.

Reconciliation should recover known analytic planes/cylinders/cones/circles/etc. from semantic/provenance knowledge before generic fitting. Generic fitting is bounded, diagnostic and never allowed to silently widen project/export tolerances.

Genesis evidence: DR-0012, DR-0014, RCS-009, RCS-012 and DR-0015.

## Axisymmetric lathe provider — initial scope

A first-class axial/radial material-domain provider is accepted for the **qualified fixed-axis rotationally symmetric subset**:

- cylindrical OD turning;
- facing;
- shoulders;
- linear taper/chamfer-class boundaries;
- cylindrical through/blind boring;
- exact and repeated finishing/retrace operations;
- bounded canonicalized analogue-controlled variants whose resulting removal envelope remains rotationally symmetric.

The provider reconstructs conventional validated B-rep when reconciliation is required and should retain exact analytic planes/cylinders/cones where mathematically present.

Do **not** claim the following solved at founding time:

- arbitrary insert nose-radius/orientation envelopes;
- production grooving/parting/undercut semantics beyond separately qualified cases;
- eccentric work;
- live tooling;
- general non-axisymmetric turning.

Unsupported semantics reconcile/handoff to another qualified provider or return `refused_unsupported`; they are not approximated inside the axisymmetric domain merely to avoid a refusal.

Genesis evidence: `docs/18-LATHE-MATERIAL-DOMAIN-RESEARCH.md`, DR-0013 and `research/rcs-010/measured-summary-v1.json`.

## Mill provider — initial scope and hierarchy

Milling uses a hierarchy rather than one universal swept-solid algorithm:

1. use an explicit recognized analytic/process operation when semantics justify it;
2. apply strict canonical simplification/batching only when equivalence is proven;
3. use exact per-segment cutter-envelope material removal as the fixed-orientation correctness baseline;
4. use a bounded local hybrid/deferred fallback only when its domain and error contract are explicit;
5. reconcile to conventional B-rep or refuse authoritative completion when no qualified route preserves the requested operation.

The implementation must preserve the negative RCS-011 evidence: a valid B-rep is not a sufficient physical oracle; unproven near-coincident/freehand n-ary batching can be materially wrong; dense sampled-pose B-rep subtraction is not accepted as the universal fallback.

The initial production vertical slice should target fixed-orientation simple paths and recognized operations first, while arbitrary/self-crossing/retraced freehand fallback remains a tracked high-priority research item.

Genesis evidence: `docs/19-MILL-CUTTER-SWEEP-RESEARCH.md`, `research/rcs-011/measured-summary-v1.json`, DR-0014 and DR-0015.

## Tolerance, uncertainty, provenance and topology policies

### Separate policy channels

At minimum keep these independently named/versioned:

- input sampling resolution;
- machine/control resolution;
- manufacturing tolerance;
- numerical uncertainty;
- topological equivalence policy;
- contact/tangency classification policy;
- preview tolerance;
- export tolerance;
- validation tolerance.

A provider can translate these into local algorithm parameters, but that translation must be explicit and diagnostic. It may not promote a convenient fuzzy Boolean epsilon into manufacturing truth.

### Ambiguity and positive material intent

Operation-local uncertainty may yield an ambiguous/contact classification. The safe meaning is **defer/reconcile while retaining signed manufacturing intent**. A positive-volume removal request is never silently converted into a no-op solely because it is smaller than a convenience epsilon.

### Retrace and semantic equivalence

Geometry recomputation for an exact/redundant retrace may be elided only when semantic lineage proves equivalent material-body ancestry, setup/tool revisions and removal envelope with no intervening conflicting material mutation. The journal event and lineage evidence remain.

### Topology identity

Persistent identifiers do not attach meaning to transient B-rep face/edge identity. Backend history (`BRepTools_History`, TNaming or equivalent) may be useful evidence during one reconstruction but cannot define durable project identity. Split, merge, replacement and ambiguous ancestry are first-class lineage events.

Genesis evidence: DR-0010, DR-0011, RCS-007 and RCS-008.

## STEP conformance contract

The founding STEP contract is `msac-step-conformance/1.0`, targeting **AP242-family engineering exchange semantics**. OCCT's `AP242DIS` mode is an implementation mode and must not be advertised as ISO 10303-242:2025 Edition-4 certification.

A successful export is an explicit export candidate consisting of committed revision, selected body set, unit, export/conformance profile and declared accuracy budgets. Preview state is never exportable.

### Four mandatory validation layers

- **Layer A — pre-export committed state:** explicit valid body selection; finite positive-volume closed/orientable solids; connectivity/body count consistent with committed state; unresolved reconciliation within budget.
- **Layer B — serialized STEP:** parseable Part 21; exact schema/profile and unit; every selected body represented as conventional solid B-rep; reproducibility metadata recorded.
- **Layer C — fresh read-back:** valid B-rep; exact selected body count; physical units/scale; dimension/volume/surface/angular budgets; analytic-class retention where required; no extra or missing bodies.
- **Layer D — interoperability qualification:** representative files pass an independent parser plus at least one independent downstream CAD/CAM consumer qualification for the exact exporter/profile/version. A second consumer is preferred before release claims.

Primary solid representation is `MANIFOLD_SOLID_BREP` or `BREP_WITH_VOIDS` as applicable. Faceted/surface/tessellated-only output cannot satisfy the primary engineering contract.

Default export selection is **all material bodies** in the committed revision. Subset export is explicit and records selected and omitted durable body IDs. There is no implicit largest/first body policy.

The founding profile supports at least millimetres and inches and checks physical scale explicitly. Required analytic primitives are retained where source/reconciliation semantics prove them exact and the profile supports them.

If any mandatory gate fails, export is refused or remains `interoperability_unqualified`; emitting STL or a visually plausible STEP file does not convert failure into success.

Genesis evidence: `docs/13-STEP-CONFORMANCE-CONTRACT.md`, DR-0009, RCS-005 and RCS-006.

## Programme-facing error and status model

The API must preserve at least these status classes:

- `accepted_pending` — intent durably accepted, bounded material/topology work remains deferred;
- `reconciled` — conventional validated engineering B-rep exists for the relevant state;
- `success` — requested qualified operation/query/export completed;
- `refused_unsupported` — no qualified provider supports the requested semantics;
- `refused_unresolved_ambiguity` — current policy cannot safely resolve material meaning;
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

Backend-specific status/warnings are nested diagnostics. A file, mesh or valid-looking B-rep may not overwrite a higher-level physical/conformance failure.

Where needed, transport-level errors (authentication, framing, unavailable worker, version mismatch) should remain distinct from these engineering statuses.

Genesis evidence: DR-0015 and `research/rcs-013/architecture-v1.json`.

## Benchmark and corpus strategy

The production repository should import **specifications/fixtures deliberately**, not copy the genesis research tree or its experimental binaries.

Founding regression coverage must retain representative families from the RCS-003 corpus:

- coincidence/coplanarity;
- tangency and lower-dimensional contact;
- sub-tolerance/sliver material removal;
- exact repeated/retraced operations;
- high operation/segment count;
- lathe OD/facing/boring and eventually qualified parting;
- mill edge-following, overlapping paths, cut-through and freehand pathologies;
- disconnected-body transitions;
- STEP millimetre/inch and multi-body round trips.

Every engineering-result record should retain fixture identity, canonical input/profile versions, backend/provider version/build, status classification, validity/body count, geometry/volume metrics, runtime/resource metrics where relevant, reconciliation/STEP observations and repeatability signature.

A kernel/provider defect is a measured test result; a test harness failure is different. Process isolation and timeouts should prevent one crash/hang from destroying a campaign.

Production CI should run a tractable deterministic smoke subset. Broader stress and interoperability campaigns can be scheduled/release gates, but their commands, inputs and result schemas must remain reproducible.

Genesis evidence: `docs/11-ADVERSARIAL-MANUFACTURING-CORPUS.md`, `docs/14-BASELINE-BENCHMARK-HARNESS.md`, `research/rcs-006/` and RCS-007–RCS-012 measured summaries.

## Dependency, license and upstream provenance plan

### OCCT baseline

Founding baseline: Open CASCADE Technology **8.0.1**, tag/revision `V8_0_1` / commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`.

Use OCCT behind an adapter and worker boundary. Keep exact source revision, build options/toolchain and runtime version observable in diagnostics. Prefer an isolated shared-library dependency over a deep source fork initially. Introduce a narrow source modification/fork only when a reproduced failure demonstrates that programme/provider layers cannot correct the relevant seam safely.

### Optional fallback dependencies

No Manifold/OpenVDB/CGAL-style fallback is mandatory at repository creation. Add optional alternatives only behind replaceable adapters after workload-specific qualification. Do not accidentally make a GPL-constrained package such as the reviewed CGAL Nef package a hidden mandatory dependency for a distribution model that cannot satisfy its obligations.

### Compliance records

For every shipped dependency retain:

- exact upstream project/version/commit and source URL;
- license text and required notices;
- build configuration/toolchain profile;
- patches with provenance and rationale;
- whether binaries are dynamic/shared/static and resulting obligations;
- source/relinking or other distribution material required by the dependency license;
- release-time compliance audit evidence.

Licensing observations in genesis are engineering constraints, not legal advice; production release engineering must validate actual obligations for the shipped configuration.

Genesis evidence: `docs/12-OCCT-8.0.1-AUDIT.md`, `docs/19-ALTERNATIVE-HYBRID-GEOMETRY-REPRESENTATIONS.md`, DR-0014 and DR-0015.

## Build and platform assumptions

Founding implementation assumptions are deliberately conservative:

- a C++17-capable native toolchain is acceptable for the OCCT/provider worker layer because the accepted research baseline is already proven there;
- CMake/Ninja-style reproducible builds are a reasonable initial build path, but the product contract is not tied to a generator;
- Linux hosted CI is a required reproducible baseline because the genesis benchmark suite is proven there;
- production must preserve Windows as a first-class target for the intended MSAC desktop workflow rather than treating Linux-only CI success as product portability proof;
- geometry work executes out-of-process by default with per-job/attempt timeouts until measured concurrency evidence supports a narrower boundary;
- deployment transport/IPC is intentionally deferred; keep semantic API schemas separate from transport glue;
- deterministic unit/contract tests must not require proprietary CAD applications; independent STEP consumer qualification can be a release/qualification workflow outside ordinary hosted CI;
- optional heavy fallback libraries must not contaminate the minimal core build when their provider is disabled.

The production bootstrap should create explicit supported-toolchain documentation and a CI matrix early rather than carrying unspoken genesis-machine assumptions forward.

## Evidence map for inherited decisions

| Production rule | Accepted genesis evidence |
|---|---|
| STEP is mandatory primary output | DR-0001; DR-0009; `docs/13-STEP-CONFORMANCE-CONTRACT.md` |
| Journal is durable manufacturing authority | DR-0002; `docs/10-CANONICAL-JOURNAL-CONTRACT.md` |
| Initial scope is lathe + mill | DR-0003 |
| Stable boundary excludes kernel/frontend private types | DR-0004; `docs/01-MSAC-GEOMETRY-CONTRACT.md` |
| Pathological geometry is normal workload | DR-0005; RCS-003 corpus |
| Units/frames/numerics explicit | DR-0006 |
| Canonicalization is deterministic and bounded | DR-0007 |
| Revisions/body transitions are immutable/explicit | DR-0008 |
| Tolerance channels remain separate | DR-0010; RCS-007 measured summary |
| Identity is semantic lineage, not face ID | DR-0011; RCS-008 measured summary |
| Regularized material + bounded topology deferral | DR-0012; RCS-009 measured summary |
| Axisymmetric lathe provider is first-class for qualified subset | DR-0013; RCS-010 measured summary |
| Milling uses a qualified strategy hierarchy | RCS-011 measured summary; DR-0015 |
| Local hybrid fallbacks are bounded/replaceable | DR-0014; RCS-012 measured summary |
| Founding architecture is semantic-provider hybrid | DR-0015; `research/rcs-013/architecture-v1.json` |

## Explicit founding non-goals

Do not begin by attempting a universal CAD-kernel rewrite. Do not wait for every research unknown before building useful vertical slices. Do not make real-time render-frame synchronization a requirement for exact geometry. Do not require every controller sample to produce B-rep topology. Do not model every cutter tooth, chatter or thermal effect as a geometry prerequisite. Do not embed the entire journal into STEP as a validity requirement. Do not import the radiCADSAC Git history into the production repository.

The staged roadmap and issue graph define the productive starting path; unresolved research has explicit safe policies and refusal routes rather than hidden assumptions.
