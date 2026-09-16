# STEP conformance and downstream-usability contract

Status: RCS-005 research output  
Contract: `msac-step-conformance/1.0`  
Date: 2026-09-16

## Purpose

This contract defines when MSAC/OpenSimachinist may claim that a STEP engineering export succeeded. A writer return code, syntactically valid Part 21 text, visually plausible geometry, or a watertight mesh is not sufficient.

The contract is backend-independent. OCCT 8.0.1 is the pinned baseline implementation used by later RCS-006 measurements, not the definition of correctness.

## Source basis and version pinning

Primary sources consulted for this version are:

- ISO 10303-242:2025, Edition 4, *Managed model-based 3D engineering*, published 2025-08: https://www.iso.org/standard/84300.html
- OCCT 8.0.1 pinned commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`.
- OCCT `STEPControl_StepModelType.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/DataExchange/TKDESTEP/STEPControl/STEPControl_StepModelType.hxx
- OCCT `DESTEP_Parameters.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/DataExchange/TKDESTEP/DESTEP/DESTEP_Parameters.hxx
- OCCT `STEPControl_Writer.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/DataExchange/TKDESTEP/STEPControl/STEPControl_Writer.hxx
- OCCT `STEPCAFControl_Writer.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/DataExchange/TKDESTEP/STEPCAFControl/STEPCAFControl_Writer.hxx
- OCCT `BRepCheck_Analyzer.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKTopAlgo/BRepCheck/BRepCheck_Analyzer.hxx
- STEPcode `p21read`, an implementation-independent Part 21 / EXPRESS-schema reader: https://stepcode.github.io/docs/p21read/

### Important AP242 distinction

**SOURCE:** ISO 10303-242:2025 Edition 4 is the current published AP242 application protocol as of this research date.

**SOURCE:** OCCT 8.0.1 exposes `DESTEP_Parameters::WriteMode_StepSchema_AP242DIS`. That symbol is an OCCT implementation mode; it is not evidence that a produced file is conformant to ISO 10303-242:2025 Edition 4.

**DECISION:** the programme target is **AP242-family engineering exchange semantics**. Each concrete exporter profile records the exact schema identifier and implementation/version it emits. The RCS-006 OCCT baseline profile is named `occt-8.0.1-ap242dis` and must qualify through this contract before it may be described as programme-conformant. No code may relabel the OCCT `AP242DIS` mode as Edition-4 certification.

## Definitions

### Export candidate

A committed engineering revision plus:

- the exact material-body set requested for export;
- the export unit;
- a versioned conformance/export profile;
- declared geometric accuracy budgets;
- any explicit healing/reconciliation policy;
- provenance linking the export to the journal/revision.

Preview geometry is never an export candidate.

### Export profile

A versioned set of STEP protocol/schema, solid representation, unit, healing, read-back and interoperability rules. A profile is separately **qualified** against the conformance fixture matrix.

### Conformant export

A STEP file for which all mandatory per-export gates pass under a currently qualified export profile.

### Interoperability-qualified profile

An export profile whose representative fixtures have passed the required independent parser and downstream-consumer qualification for the exact relevant exporter version/configuration.

## Initial application protocol and solid representation

### Protocol target

The programme uses AP242-family managed model-based 3D engineering as its initial STEP target because the current published AP242 scope includes mechanical parts, assemblies, boundary geometry, compound shape geometry, dimensional/tolerance data and manufacturing-related product information.

The programme does not require every AP242 capability. The founding profile is deliberately narrow: conventional exact/parametric engineering solids with explicit units and optional lightweight product/provenance metadata.

### Primary geometric representation

For each exported material body, the preferred STEP geometric representation is conventional manifold B-rep:

- `MANIFOLD_SOLID_BREP`; or
- `BREP_WITH_VOIDS` when a closed body contains enclosed void shells.

OCCT's `STEPControl_ManifoldSolidBrep` explicitly targets these forms.

The following do **not** satisfy the founding primary-output contract by themselves:

- `FACETED_BREP`;
- `SHELL_BASED_SURFACE_MODEL`;
- tessellated-only geometry;
- polygon mesh/STL-equivalent payloads;
- wireframe/curve-set output.

Such representations may be auxiliary preview or metadata, but a successful engineering export must contain the conforming B-rep body set.

## Four-layer validation model

A successful export crosses four distinct layers. Later layers never retroactively excuse an earlier failure.

### Layer A — pre-export committed state

Before serialization:

1. The source is a committed engineering revision, not preview state.
2. Every requested material body ID resolves in that revision.
3. The requested body selection is explicit and deterministic.
4. Every selected body intended as a volumetric workpiece result is a closed, orientable, finite solid with positive volume.
5. Topological and geometric validity checks pass under the exact validation configuration recorded by the export profile.
6. Body count and connectivity match the committed material state.
7. No unresolved reconciliation state exceeds the declared export accuracy.
8. Any healing/same-domain operation is explicit, measured and bounded as described below.

Failure at this layer is an **export refusal**, not permission to fall back to STL or silently drop geometry.

### Layer B — serialized STEP file

The emitted file must:

1. be parseable as a STEP Part 21 exchange file;
2. identify the exact schema/profile actually written;
3. use an export-profile-approved AP242-family schema identifier;
4. encode the requested dimensional unit explicitly;
5. contain the full selected material-body set as conventional B-rep solids;
6. contain no unexpected top-level open shell/surface/mesh substitute for a requested material solid;
7. preserve body/product structure according to the multi-body policy;
8. record the writer/export-profile/version metadata needed for reproducibility.

A successful `STEPControl_Writer::Write()` or equivalent is evidence only that serialization was attempted successfully; it does not satisfy Layer B by itself.

### Layer C — independent read-back comparison

The file is read into a fresh geometry session/process using the pinned read-back configuration. The read-back state is compared with the pre-export candidate using the metrics below.

Mandatory checks are:

- valid B-rep after read-back;
- selected material-body count preserved exactly;
- connectivity/void semantics preserved where fixture expectations specify them;
- units and physical scale preserved;
- representative dimensions within their declared budget;
- volume within its declared absolute/relative budget;
- surface/geometric deviation within its declared budget where a reference comparison is available;
- required analytic surface classes preserved;
- no extra material body introduced and no selected body omitted.

OCCT read-back is the founding automated geometry baseline, but because the writer and reader share much implementation, this layer is not independent interoperability evidence.

### Layer D — independent interoperability qualification

Interoperability is qualification of an **export profile**, not a claim inferred from one writer/reader pair.

The founding strategy has two complementary parts:

1. **Independent schema/Part-21 parser:** representative files are accepted by STEPcode `p21read` built for the matching AP242 schema, with no definite parse/schema errors. This catches a class of writer/self-reader agreement failures but does not prove geometric usability.
2. **Independent downstream CAD/CAM consumer qualification:** the representative fixture set is imported into at least one available CAD/CAM system whose STEP import path is independent of the exporter implementation where practical. The exact application, version, platform, import settings and whether its geometry kernel is known to be OCCT-based must be recorded. A second consumer is strongly preferred for release qualification.

Consumer qualification checks solid/body count, physical dimensions, accessible/editable B-rep or solid status, voids/connectivity and gross analytic-surface recognition where the consumer exposes it. A screenshot-only visual check is insufficient.

No specific proprietary vendor defines correctness. If a consumer disagrees with the programme oracle, the discrepancy is recorded and investigated rather than automatically treating either side as authoritative.

Hosted CI is not required to install proprietary CAD systems. CI must run the open automated layers; consumer qualification records are versioned artifacts rerun when the writer, schema, healing policy, or other material export behaviour changes.

## Geometric and topological acceptance metrics

There is deliberately no universal magic epsilon. Every export profile/request records declared accuracy budgets derived from the manufacturing/export requirement.

### Required declared budgets

At minimum:

- `max_dimension_error_nm`;
- `max_surface_deviation_nm` when a geometric comparison oracle exists;
- `max_angular_error_nrad` for angular/normal-sensitive fixtures;
- `max_volume_error_abs_mm3`;
- `max_volume_error_rel`.

A project/manufacturing tolerance may be tighter than the exporter's capability. In that case the exporter must refuse or require an explicit less-accurate export profile; it may not silently widen the project tolerance.

### Pass rules

- Representative dimensions: absolute deviation must be `<= max_dimension_error_nm`.
- Surface comparison: symmetric sampled/Hausdorff-equivalent deviation must be `<= max_surface_deviation_nm` using a documented sampling/metric algorithm.
- Angular comparison: deviation must be `<= max_angular_error_nrad` where applicable.
- Volume: both the absolute and relative criteria declared for the fixture/profile are evaluated; the machine-readable fixture states whether both or either threshold is mandatory. Founding conformance fixtures require both.
- Body count: exact equality.
- Void count where specified: exact equality.
- Topology validity: pass/fail; no tolerance can excuse invalid B-rep.
- Face/edge counts are diagnostic unless a fixture explicitly makes them semantic. STEP readers may legitimately split or unify topological entities without changing the engineering solid.

## Units and scale

### Canonical versus export units

The durable journal remains canonical in integer nanometres under RCS-002. STEP output is a unit-bearing engineering exchange representation and does not inherit an implicit unit from the journal.

The founding conformance profile must support at least:

- millimetres;
- inches.

OCCT 8.0.1 `UnitsMethods_LengthUnit` explicitly includes millimetres, inches, metres and additional units. This capability is useful, but the conformance oracle is physical-size preservation rather than enum selection.

### Required unit tests

The fixture matrix contains exact binary/decimal-friendly manufacturing dimensions including 25.4 mm, 12.7 mm and 6.35 mm so metric/inch equivalence is unambiguous.

For the same canonical geometry:

1. export in millimetres and confirm serialized units indicate millimetres;
2. export in inches and confirm serialized units indicate inches;
3. read both files back to the same canonical comparison unit;
4. assert physical bounding dimensions and volume are equal within the fixture budgets;
5. reject any 25.4x, 1/25.4x, 1000x or similar scale error even if topology is valid.

## Analytic geometry preservation

Analytic engineering geometry is semantically useful to downstream CAD/CAM and must not be gratuitously converted to splines.

### Required preservation

Where the committed source/reference identifies a surface or curve as an exact supported analytic class and no operation mathematically destroys that class, read-back must retain the corresponding analytic class for:

- planes;
- cylinders;
- cones;
- spheres;
- tori where used;
- lines;
- circles/arcs.

Trimming these entities does not remove the requirement that the underlying geometry remain analytic when the STEP representation and downstream reader support it.

### Allowed approximation

Spline/NURBS representation is allowed when:

- the source is itself spline/freeform;
- the geometry is an intersection or reconstruction that is not exactly one of the required analytic primitives; or
- a versioned export/reconciliation policy explicitly permits approximation for that entity class.

Any permitted approximation must still satisfy the declared geometric and angular budgets and must be reported in export diagnostics. Converting an exact cylinder/plane/cone to a spline merely because a backend path is convenient is a conformance failure for fixtures that require analytic retention.

## Healing and same-domain cleanup

Healing is a controlled transformation, not a magic success button.

For every healing/reconciliation stage used before export, the exporter records:

- algorithm/policy ID and version;
- input validation status;
- output validation status;
- changed body/topology summary;
- dimension, surface-deviation and volume deltas;
- analytic surface classes gained/lost;
- material-body connectivity before/after.

Healing passes only when all geometry deltas remain within the export candidate's budgets and material-body connectivity/selection is unchanged unless the committed engineering state explicitly requires that transition.

Same-domain cleanup may change face/edge counts and still pass; it may not merge distinct material bodies, close an unintended gap, remove a requested feature, or alter dimensions beyond budget.

## One-body and multi-body policy

Disconnected material bodies produced by parting/cut-through are valid committed engineering states.

### Default selection

The default export selection is **all material bodies present in the selected committed revision**. There is no implicit “largest”, “primary”, “first”, or “convenient” body rule.

### Explicit subset export

A caller/user may explicitly request a subset. The export manifest must record:

- all body IDs present in the revision;
- selected body IDs;
- omitted body IDs;
- the explicit selection/request origin.

Subset export does not mutate the underlying revision and must never masquerade as an all-body export.

### Multi-body STEP representation

A conforming profile may use either of these strategies after it is qualified by fixtures:

1. **single-product multi-solid representation** — distinct selected material solids under one workpiece product/shape representation; or
2. **explicit body product structure** — a workpiece container/product structure with one identifiable solid-bearing child/occurrence per selected body.

The preferred strategy is the least semantically artificial representation that preserves every selected body's identity and geometry across qualified consumers. The chosen strategy is recorded in the export profile.

An implementation may not silently fuse disconnected bodies, silently discard presumed scrap, or coerce a multi-body state into one body. If no qualified representation strategy can preserve the requested set, export is refused.

### Parting and scrap semantics

RCS-005 deliberately does not define which side of a parted workpiece is “the part” versus “scrap”. That is manufacturing/product intent outside pure geometry. Until an explicit body-retention classification exists, all bodies remain exportable and the default is preserve-all.

## STEP provenance and metadata

Geometric correctness does not depend on a downstream application preserving MSAC-specific metadata.

The exporter should include standard product/body names and validation properties where supported, and may include stable programme identifiers when mapped through standard mechanisms. However:

- the STEP file must remain geometrically useful if a consumer discards optional metadata;
- the canonical operation journal is not embedded wholesale as a requirement for STEP validity;
- programme provenance that cannot be represented portably is recorded in a deterministic sidecar/export record keyed by file digest, revision ID and selected body IDs.

The export record should include at least journal schema/version, source revision ID, body selection, export profile/version, exporter build/dependency versions, declared accuracy budgets, validation results and file digest.

## Failure and refusal taxonomy

The machine-readable contract uses stable codes. At minimum:

- `PREVIEW_STATE_NOT_EXPORTABLE` — source is preview rather than committed state;
- `BODY_SELECTION_INVALID` — requested body IDs do not resolve or selection is ambiguous;
- `PREEXPORT_INVALID_TOPOLOGY` — selected body fails required B-rep validity;
- `PREEXPORT_NONVOLUMETRIC_BODY` — requested material body is not a valid finite solid;
- `RECONCILIATION_UNRESOLVED` — internal/deferred state cannot be reconciled within budget;
- `HEALING_BUDGET_EXCEEDED` — healing changes geometry/connectivity beyond permitted limits;
- `SERIALIZATION_FAILED` — writer failed to produce the file;
- `SCHEMA_PROFILE_MISMATCH` — file schema/profile is not the requested qualified profile;
- `UNIT_OR_SCALE_MISMATCH` — encoded/read-back units or physical size are wrong;
- `BODY_COUNT_MISMATCH` — selected body set was lost, fused, split unexpectedly or augmented;
- `READBACK_INVALID_TOPOLOGY` — read-back B-rep is invalid;
- `GEOMETRIC_DEVIATION_EXCEEDED` — dimensions/surface/volume/angular metrics exceed budget;
- `ANALYTIC_GEOMETRY_LOST` — required analytic entity class was unnecessarily approximated;
- `VOID_OR_CONNECTIVITY_MISMATCH` — void/connectivity semantics changed;
- `INDEPENDENT_PARSE_FAILED` — qualified independent Part 21/schema parser rejects the file;
- `PROFILE_NOT_INTEROPERABILITY_QUALIFIED` — exporter/profile version lacks current downstream qualification;
- `DOWNSTREAM_CONSUMER_FAILURE` — a qualification consumer cannot import/use a representative fixture as required.

Warnings must be separate from refusal codes. A warning can never convert a mandatory failed metric into success.

## Export result states

The programme-facing exporter reports one of:

- `success` — all mandatory per-file gates passed and the exact export profile is interoperability-qualified;
- `refused` — a known precondition/conformance rule prevented export;
- `failed` — serialization/read-back/validation encountered an implementation or runtime failure;
- `unqualified` — automated per-file gates may pass, but the exact profile/version lacks current independent interoperability qualification.

Only `success` may be presented as a successful engineering STEP export.

## Minimal RCS-006 conformance fixture matrix

Machine-readable details live in `research/rcs-005/fixtures-v1.json`. The minimum suite covers:

| Fixture | Purpose | Required oracle |
|---|---|---|
| metric analytic turned body | AP242 B-rep, mm, cylinder/plane retention | one valid body; exact analytic classes; dimensions/volume in budget |
| imperial equivalence block | inch unit mapping and 25.4 conversion | same physical geometry as metric reference |
| enclosed cavity | `BREP_WITH_VOIDS` / internal void semantics | one body, one void, volume/dimensions preserved |
| lathe parting | disconnected material state | two selected bodies preserved, not fused/dropped |
| mill cut-through separation | second process-specific disconnect | expected body count/connectivity preserved |
| explicit subset of separated bodies | selection semantics | only requested body exported; omission recorded explicitly |
| same-domain/healing candidate | bounded cleanup | valid result, geometric deltas within budget, no silent feature loss |
| exact analytic cone/cylinder | analytic retention | no gratuitous spline conversion |
| freeform/spline body | permitted non-analytic geometry | valid B-rep and geometric deviation within budget |
| near-tolerance feature | refusal versus preservation boundary | deterministic result against declared budget |
| invalid/open-shell candidate | negative export test | export refused before claiming success |
| unit-pair equivalence | mm/inch physical identity | bounding dimensions and volume agree after normalization |

RCS-006 should materialize concrete fixtures from RCS-003 where possible instead of inventing unrelated geometry.

## RCS-006 harness requirements

The baseline harness must record for every export attempt:

- source fixture and revision IDs;
- body selection and expected body/connectivity oracle;
- exporter/profile/dependency versions;
- STEP schema identifier actually emitted;
- requested and detected units;
- writer/transfer status and warnings;
- pre-export and read-back validity;
- body/void/topology counts;
- dimensions, volume and surface-deviation metrics;
- analytic classes before/after;
- healing/reconciliation events;
- independent parser result when enabled;
- external consumer qualification reference for the profile;
- final conformance status and refusal/failure code.

## What this contract does not claim

- It is not an ISO certification programme.
- It does not claim OCCT `AP242DIS` equals ISO 10303-242:2025 Edition 4.
- It does not require all AP242 PMI/PDM capabilities for founding geometry export.
- It does not require Parasolid or another proprietary format.
- It does not solve future body/scrap product-intent classification.
- It does not make one downstream vendor authoritative.
- It does not allow STL/mesh fallback to count as STEP success.

## Reconsideration triggers

Revise `msac-step-conformance/1.x` or create a new major version when any of these materially change:

- selected STEP application protocol/profile;
- required solid/entity representation;
- body/product-structure policy;
- unit/accuracy semantics;
- analytic-preservation requirements;
- success/refusal semantics;
- interoperability qualification strategy.

Exporter implementation upgrades that do not change the contract still require requalification if they can materially change emitted STEP geometry or schema behaviour.
