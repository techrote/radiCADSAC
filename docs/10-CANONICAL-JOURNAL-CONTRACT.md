# Canonical manufacturing journal and normalization contract

Status: accepted RCS-002 programme contract  
Date: 2026-09-16  
Issue: RCS-002 / GitHub #2  
Logical schema version: `msac-journal/1.0`

## Purpose

This document defines the durable manufacturing language between future MSAC machine modules and OpenSimachinist geometry providers.

It is a **logical contract**, not a commitment to JSON, Protocol Buffers, FlatBuffers, a database, or any other persistence technology. The machine-readable examples under `research/rcs-002/fixtures/` use JSON only because it is easy to inspect and validate during genesis research.

The contract preserves the programme invariant established by RCS-001:

- the canonical operation journal is authoritative for manufacturing intent/history;
- committed engineering state is a replaceable backend realization of a journal revision;
- preview geometry, B-rep snapshots, meshes and caches are derived artifacts.

This document should be read with `docs/01-MSAC-GEOMETRY-CONTRACT.md`, `docs/08-TERMINOLOGY.md`, `docs/09-FOUNDATION-AUDIT.md`, and `docs/decisions/DR-0002-journal-is-durable-intent.md`.

## Research question and falsification criteria

### Question

Can natural high-frequency simulated machining be normalized into a durable manufacturing journal that is independent of render frame rate, controller deadzones, Godot objects, and a particular geometry kernel while retaining enough process meaning for deterministic replay and later specialized solvers?

### Hypothesis

**PROPOSAL at issue start; accepted by this issue:** yes, if the durable boundary records physical/process state rather than raw device samples, uses explicit immutable definition references and coordinate frames, preserves engagement and repeated motion semantics, and permits only deterministic bounded path normalization.

### Falsification criteria

The design would be inadequate if any of the following were required for correct replay:

- historical render-frame timing;
- a particular gamepad deadzone or input-mapping implementation;
- Godot scene/node identity;
- OCCT/private backend objects;
- undocumented metric/imperial assumptions;
- undocumented axis handedness or transform order;
- silently discarded repeated/retraced manufacturing motion;
- silently discarded disconnected material bodies;
- path fitting without a declared and checkable error bound.

The accepted contract below is constructed so none of those dependencies are required.

## Evidence classification

Most of RCS-002 is a programme contract rather than an empirical geometry result.

- **SOURCE:** RCS-001 foundation documents establish journal authority, backend replaceability, explicit units/frames, and disconnected-body requirements.
- **INFERENCE:** a durable journal must therefore encode physical machine/process meaning rather than raw controller representation or kernel-private state.
- **PROPOSAL → ACCEPTED:** the concrete logical schema, numeric conventions, normalization pipeline, history model, and compatibility rules defined here.
- **OPEN:** detailed provenance/topological naming, tolerance algebra, STEP mapping, and backend body-matching algorithms remain owned by later issues.

SI unit meaning follows the BIPM SI Brochure: https://www.bipm.org/en/publications/si-brochure

## Design principles

The journal contract follows these rules.

1. **Manufacturing actions, not CAD features.** Operations describe machining actions and context. A backend may recognize a turning pass or drilling action, but the journal is not a conventional feature tree.
2. **Physical state before device state.** Gamepad axes, deadzones and frame callbacks are upstream implementation details. The durable journal records physical trajectory and process semantics.
3. **No one-sample/one-operation requirement.** Many raw samples may become one canonical trajectory section; one user action may also become several operations at real semantic discontinuities.
4. **No hidden units or axes.** Every spatial quantity is interpreted through the fixed canonical numeric/unit contract and explicit coordinate frames.
5. **Bounded normalization only.** Fitting, simplification, resampling and quantization are allowed only under versioned explicit bounds.
6. **No silent semantic deletion.** Geometrically redundant passes may be optimized by a backend, but the journal preserves the manufacturing action unless an explicit canonical compaction rule proves semantic equivalence.
7. **Immutable referenced definitions.** Tool geometry, setup transforms and normalization policies are versioned immutable definitions once referenced by a committed operation.
8. **History is immutable; navigation is mutable.** Undo/redo and branching select existing/new revision nodes rather than rewriting past operations.
9. **Derived acceleration remains disposable.** Snapshots/caches are keyed to a journal revision and backend identity and can always be discarded.

## Logical document model

A project contains five logical collections.

### Project header

The header records:

- `journal_schema`: schema identifier and major/minor version;
- `project_id`;
- `workpiece_id`;
- canonical numeric convention identifier;
- required extension identifiers;
- the initial/root workpiece revision;
- the currently selected UI branch/head as mutable project metadata.

The selected UI head is not part of immutable manufacturing history. It is analogous to a branch reference pointing at a revision.

### Definition registry

Operations reference immutable definitions instead of embedding mutable frontend/backend objects.

The registry can contain:

- stock definitions;
- coordinate-frame definitions;
- setup definitions;
- tool definitions;
- machine/process semantic definitions;
- normalization policy definitions;
- tolerance-policy references;
- optional material metadata definitions.

Every referenced definition has at least:

- stable definition ID;
- definition type;
- definition schema/version;
- immutable revision/version identifier.

A persistence format may additionally use content hashes, but the logical contract does not require one specific hashing or serialization scheme.

### Canonical operation records

Version 1 defines three required operation families:

- `setup_change` — establishes a new versioned setup/frame relationship without pretending the workpiece geometry changed merely because it was moved or re-clamped;
- `process_motion` — describes one manufacturing action containing ordered trajectory sections, engagement state and process context;
- `material_body_transition` — records durable body identities after a committed split/merge/classification transition.

Future additive operation families are possible through versioned extensions. Initial programme scope remains lathe and mill.

### Workpiece revisions

A workpiece revision is an immutable node that records:

- `revision_id`;
- one parent revision in `msac-journal/1.0`;
- the operation record or transaction that produced it;
- the resulting set of durable material-body IDs expected at that revision;
- optional labels/annotations that do not affect manufacturing meaning.

Version 1 deliberately supports branching but not automatic merging of two manufacturing-history branches. Multi-parent history merge is not assumed to be semantically safe and requires a future explicit contract.

### Derived artifacts

Derived artifacts are outside authoritative journal meaning. An artifact key contains at least:

- `revision_id`;
- backend/solver identifier and version;
- relevant policy versions;
- artifact kind;
- optional platform/build identity where reproducibility needs it.

Examples include committed B-rep snapshots, preview meshes, spatial indices, tessellations and benchmark caches.

## Canonical numeric and dimensional representation

### Fixed logical quantities

`msac-journal/1.0` uses signed integer physical quantities for durable dimensional values:

| Quantity | Canonical token | Scale |
|---|---|---:|
| length/translation | `length_nm` | 1 nanometre |
| angle | `angle_nrad` | 1 nanoradian |
| duration/time offset | `time_ns` | 1 nanosecond |
| linear rate | `rate_nm_s` | 1 nanometre/second |
| angular rate | `angular_rate_nrad_s` | 1 nanoradian/second |
| dimensionless rotation component | `q15` | integer / 10^15 |

The logical integer range is signed 64-bit. A writer must reject overflow; wraparound is invalid.

The choice is not a claim that machine or geometry accuracy is one nanometre. It is a storage quantization fine enough to avoid conflating ordinary manufacturing tolerances with serialization precision. Manufacturing, uncertainty, topology, export and validation tolerances remain separate policy concepts under RCS-007/RCS-005.

### Display-unit independence

User-facing metric/imperial display never changes canonical physical meaning.

For example:

- `25.4 mm` and `1.000 in` both normalize to `25_400_000 length_nm`;
- changing the UI display from millimetres to inches does not rewrite journal operations;
- importers must perform explicit unit conversion before emitting canonical physical quantities.

### Source precision and quantization evidence

A canonicalizer records the policy version that selected numeric quantization. When source physical values are not already exact canonical integers, conversion uses round-to-nearest, ties-to-even.

For each normalized trajectory, the declared normalization error budget includes quantization. A canonicalizer must not claim a geometric fitting bound that excludes its own numeric quantization error.

### Dimensionless values

Rigid-rotation quaternions use four signed `q15` integer components representing exact rational components divided by `10^15`.

The semantic rotation is the mathematical normalization of that exact rational quaternion. Writers must:

1. reject a zero quaternion;
2. canonicalize sign so the first non-zero component in `(w, x, y, z)` is positive;
3. ensure the unnormalized rational norm lies within the policy's admissible encoding deviation from unit length.

Backends may use floating point internally, but the durable token itself has fixed meaning independent of IEEE-754 bit patterns.

## Coordinate frames and transforms

### Handedness and basis

All canonical geometric frames are right-handed Cartesian frames.

A frame definition states:

- `frame_id`;
- immutable frame revision;
- semantic role such as `workpiece`, `machine`, `tool`, `fixture` or process-specific role;
- optional parent frame;
- rigid transform from child coordinates to parent coordinates.

A machine's native controller convention may be different. The machine module must convert it into explicit canonical frames before committing manufacturing operations.

### Transform convention

Canonical points are column vectors.

A transform `T_parent_from_child` is defined by translation `t` and quaternion rotation `R(q)`:

`p_parent = R(q) * p_child + t`

Composition is explicit:

`T_A_from_C = T_A_from_B ∘ T_B_from_C`

which means a point in frame C is first transformed C→B, then B→A.

No reader may reverse this order based on local engine conventions.

### Frame graph rules

- Frame parentage must be acyclic.
- A committed operation references immutable frame revisions.
- Re-chucking/re-clamping creates a new setup/frame definition instead of mutating a historical transform.
- A setup change does not itself alter intrinsic workpiece geometry.
- Tool trajectories identify the frame in which coordinates are expressed.

### Lathe controller conventions

A lathe machine module may expose diameter programming or machine-specific X/Z sign conventions to the user. The canonical trajectory nevertheless stores true Cartesian physical positions.

If a UI/controller uses diameter values, the machine module converts them to geometric position before canonicalization. The durable path therefore does not require a future backend to know whether a historical control displayed radius or diameter.

## Immutable tool, setup and policy identity

Every `process_motion` operation references immutable versions of the definitions needed to interpret it.

### Tool reference

A tool reference identifies:

- `tool_id`;
- immutable `tool_revision`;
- geometry-definition revision;
- tool-frame revision;
- process-relevant geometry parameters or an immutable external-definition reference.

Changing insert nose radius, cutter diameter, stickout, orientation convention, or another geometry-critical property produces a new tool revision.

### Setup reference

A setup identifies the workpiece↔machine/workholding frame relation and any geometry-critical clamped/retained-body reference.

### Policy reference

Normalization and tolerance policies are versioned definitions. A historical operation always retains the policy version under which it became canonical.

A newer implementation may migrate/re-canonicalize into a **new** journal revision, but it must not reinterpret an old operation silently under a different policy.

## Raw telemetry versus canonical manufacturing state

### Raw interaction telemetry

Raw telemetry is optional forensic material. It may include:

- raw controller samples;
- input-device timestamps;
- deadzone/mapping version;
- render/simulation frame timing;
- raw machine-axis samples;
- diagnostic sensor state.

Raw telemetry is not required to replay a committed journal.

If retained, it is stored separately and linked to canonical operations by opaque trace references. The project remains valid if those traces are removed.

### Normalized machine-state trace

Canonicalization operates on a physical machine-state trace, not directly on controller values.

A normalized trace contains time-ordered physical/process samples such as:

- tool pose in an explicit machine/setup frame;
- machine-axis physical positions where process semantics require them;
- tool orientation;
- engagement/contact command state;
- spindle/rotary state;
- tool/setup/process references;
- target workpiece/body reference.

Input mapping, deadzones and control acceleration have already been resolved into physical state by this boundary.

The normalized trace itself can remain transient because the durable result is the canonical operation journal.

## Deterministic normalization pipeline

`msac-journal/1.0` defines the following conceptual stages.

### Stage 1 — validate and order physical samples

- timestamps are monotonic physical time, never frame indices;
- samples identify the same immutable setup/tool/process context until a semantic boundary;
- malformed/non-finite/unrepresentable values are rejected rather than guessed;
- duplicated timestamps are resolved by the versioned normalization policy using a deterministic stable ordering.

### Stage 2 — identify semantic boundaries

A canonicalizer may not fit or simplify across:

- setup change;
- tool-definition revision change;
- process semantic change;
- target workpiece/body change;
- discontinuous pose jump not explicitly represented as a setup/context transition;
- engagement-state boundary;
- policy-defined rotary/spindle discontinuity.

This prevents a curve fitter from erasing the event that actually changes manufacturing meaning.

### Stage 3 — reconstruct time-parameterized physical motion

Within each continuous sample interval, interpolation is determined by the normalization-policy version.

The baseline policy uses piecewise-linear interpolation in translation and shortest-arc quaternion interpolation in orientation before any optional fitting.

The meaning therefore depends on physical timestamps and positions, not the render frequency that happened to produce the samples.

### Stage 4 — fit or simplify under explicit bounds

A policy can emit:

- line;
- circular arc;
- polyline;
- cubic B-spline.

The canonicalizer must preserve ordering and endpoints and declare the bound it guarantees.

Required bound fields are:

- `max_translation_error_nm`;
- `max_orientation_error_nrad` where orientation matters;
- `max_event_time_shift_ns`;
- optional `max_rate_error_nm_s` when feed-rate history has process meaning.

A fitter may use a tighter internal bound, but never a looser one than recorded.

If the fitter cannot certify the requested bound, it must fall back to a less compressed representation such as a polyline. Cosmetic smoothing is not an allowed reason to exceed the declared error.

A future fitter can add curve families without changing the manufacturing meaning so long as it satisfies the same versioned bounded-normalization contract.

### Stage 5 — canonical quantization

Fitted values are converted to the canonical integer/fixed-rational tokens. Quantization contribution is included in the recorded bound.

### Stage 6 — assemble operations

Adjacent trajectory sections may be grouped into one `process_motion` operation when they share immutable process context and represent one manufacturing action.

There is no requirement that each engagement transition become an entirely separate operation. Instead, engagement is explicit per ordered trajectory section.

### Stage 7 — validate logical invariants

Before commit, validate at least:

- all definition refs resolve;
- frame graph is acyclic;
- trajectory time is monotonic within each section;
- canonical integers are in range;
- curve definitions are structurally valid;
- required normalization bounds are non-negative;
- engagement/process combinations are supported or explicitly extension-defined;
- parent revision and target material-body refs exist.

## Sampling-rate and deadzone independence

Two distinct guarantees are required.

### Identical-input canonical determinism

Given the same normalized physical sample trace, same definition registry, and same normalization-policy version, conforming canonicalizers must emit the same logical canonical values and segmentation.

The reference policy uses integer/fixed-rational decisions wherever thresholds affect durable output. Any implementation-specific optimization must produce the same logical result.

### Equivalent-motion invariance

Two traces sampled at different rates but representing the same physical time-parameterized motion may not have identical source sample sets. Their canonical trajectories must nevertheless remain within the declared normalization bounds of that same physical motion.

The contract does **not** require byte-identical curves for arbitrary differently sampled traces; it requires bounded physical equivalence.

### Controller mapping independence

A change to gamepad deadzone, response curve or render loop may change future physical machine motion, but it does not change the meaning of an already committed journal because the journal stores the resulting physical path.

Re-running old raw controller telemetry under a new controller mapping is a new canonicalization experiment, not ordinary journal replay.

## Canonical trajectory representation

A trajectory contains ordered sections. Every section records:

- trajectory frame reference;
- process-relative start time or monotonically increasing parameter domain;
- engagement state;
- one or more curve segments;
- orientation representation if geometry-critical;
- spindle/rotary state or reference if geometry-critical;
- normalization bounds actually guaranteed.

### Required curve kinds

#### Line

A line is represented by exact canonical start/end positions.

#### Polyline

A polyline is an ordered list of canonical positions and optional corresponding relative times.

It is the mandatory loss-limiting fallback when a more compact fit cannot be certified.

#### Circular arc

An arc records frame, start/end, center or equivalent canonical construction, plane normal, and sweep direction/angle. Ambiguous near-zero/near-full-circle cases must be represented using a non-ambiguous parameterization or fall back to polyline.

#### Cubic B-spline

A cubic B-spline records degree, canonical control points, knot sequence in fixed dimensionless tokens, and parameter interval. Any source-motion approximation still carries the same explicit spatial/orientation/time error bound.

Spline fitting is optional; a journal reader must not infer a conventional CAD feature from the presence of a spline.

## Engagement and process state

Every trajectory section has an explicit engagement state.

The core values are:

- `neutral` — motion that does not intentionally alter material;
- `remove` — subtractive machining engagement;
- `add` — reserved for future additive extensions;
- `probe` — measurement/contact semantics, no material change by default;
- namespaced process-specific state when declared as a required extension.

Initial RCS-002 fixtures use `neutral` and `remove` only.

A backend may decide that a nominally engaged section removes zero material because it exactly retraces an existing surface. That geometric no-op does **not** allow the journal operation to disappear.

### Spindle and rotary state

Process sections can carry geometry-relevant rotary state including:

- semantic axis/frame reference;
- signed angular position where phase matters;
- signed angular rate;
- rotational mode/state;
- process-specific synchronization metadata through a versioned extension.

For axisymmetric turning a backend may be able to ignore absolute spindle phase, but the journal records enough state to distinguish a rotating turning process from a stationary tool/workpiece configuration.

## Lathe and mill semantic envelope

The common operation structure is shared; process metadata remains explicit.

### Lathe

A turning `process_motion` can state:

- process family such as `turning.od`, `turning.facing`, or `turning.boring`;
- workpiece spindle axis/frame;
- rotating-workpiece state;
- immutable tool/nose geometry;
- tool trajectory in setup/workpiece coordinates;
- engagement sections;
- target body.

A backend may dispatch this to an axisymmetric material-domain solver without requiring the journal to contain OCCT booleans or CAD revolved features.

### Mill

A milling `process_motion` can state:

- process family such as `milling.general`, `milling.slot`, or `drilling` when explicitly known;
- immutable cutter envelope/tool definition;
- tool-center or defined tool-frame trajectory;
- fixed or varying tool orientation;
- spindle state;
- engagement sections;
- target body.

Freehand motion remains valid as `milling.general`; a process recognizer is not required to reinterpret it as a pocket/slot feature.

## Redundant and retraced motion

Geometric redundancy and semantic redundancy are different.

The journal therefore follows these rules.

- Repeated finishing passes remain separate operations or explicit repeated sections unless the canonicalization policy proves they are semantically identical and records a lossless repetition construct.
- A backend may report `accepted_no_material_change` while preserving the operation and revision history.
- Neutral duplicate samples may be collapsed within a trajectory when doing so cannot alter the bounded physical path or a semantic event.
- Engaged motion is never discarded merely because the current backend predicts zero removal.
- Sub-quantization displacement carrying an engagement or state transition is preserved as a zero-displacement semantic section rather than silently deleting the event.

This preserves later provenance, diagnostics, alternate-solver experiments and potential process semantics even when current geometry does not change.

## Material-body identity and split/merge history

RCS-002 must provide durable hooks without solving the full topological naming problem owned by RCS-008.

### Durable logical body IDs

Every connected material body known at a committed workpiece revision has a journal-level `body_id`.

A `body_id` is not a B-rep solid handle, face ID, object address or transient solver object.

### Material-body transition record

When a committed operation changes body connectivity, the same commit transaction records a `material_body_transition` containing:

- `transition_id`;
- `caused_by_operation_id`;
- input durable `body_id` set;
- output durable `body_id` set;
- transition kind: `split`, `merge`, `replace`, `classification_only` or versioned extension;
- optional user/process classification such as retained/clamped/detached/scrap/unspecified;
- the revision at which the transition became committed.

New output body IDs are assigned as durable journal identities at commit time. A future backend replay is required to map its realized connected bodies to those expected durable identities or report an explicit body-mapping ambiguity/divergence.

This deliberately avoids pretending RCS-002 has solved geometric/topological ancestry. RCS-008 will research how robustly to perform that mapping and preserve finer face/edge provenance.

### No silent scrap deletion

A separated body is not removed from journal state merely because a backend or UI considers it inconvenient.

If a later policy/user action classifies or removes a detached body from the active workpiece set, that change is explicit in journal state. RCS-005 decides what body/product selection is acceptable for STEP export.

## Undo, redo, branching and checkpoints

### Immutable revision graph

`msac-journal/1.0` uses an immutable single-parent revision graph.

- A new operation creates a new child revision.
- Undo selects an ancestor revision as the current UI head; it does not delete operations.
- Redo follows an existing child on the selected branch.
- Performing new work from an older revision creates a new branch.
- Branch names/bookmarks are mutable UI metadata, not manufacturing operations.

This is a history graph of manufacturing actions, not a conventional editable CAD feature tree.

### Checkpoints

A checkpoint is a named reference to a revision plus optional derived artifact references.

A checkpoint does not create new manufacturing meaning by itself.

### Backend snapshots

A snapshot can accelerate replay only when its artifact key matches the requested revision, backend identity/version and relevant policy identity.

On mismatch or corruption, the backend discards the snapshot and replays from authoritative journal data.

## Replay contract

The programme distinguishes three replay guarantees.

### Level J1 — journal interpretation determinism

Every supported reader must assign the same physical/process meaning to canonical numeric tokens, frame transforms, operation ordering, engagement state and immutable definition refs.

Unsupported required extensions or unsupported journal major versions fail explicitly.

### Level J2 — same-backend replay repeatability

The same journal revision replayed by the same backend build/configuration must produce the backend's declared repeatability invariant.

The minimum required invariant is:

- same accepted/rejected/deferred statuses;
- same material-body count/mapping outcome;
- geometry within backend-declared validation tolerance;
- no unexplained order-dependent divergence.

Bitwise-identical B-rep serialization is **not** a programme requirement unless a backend specifically promises it.

### Level J3 — cross-version/cross-backend replay compatibility

A newer/alternate backend must be able to interpret the manufacturing intent. It may produce a different internal representation or topology decomposition.

It must either:

- satisfy the journal/body/conformance expectations within declared tolerances; or
- report a structured incompatibility, unsupported semantic extension, body-mapping divergence, or geometry failure.

It may not silently reinterpret the journal to make replay succeed.

## Schema and compatibility rules

### Version identifiers

A journal schema version is `major.minor` under the stable identifier `msac-journal`.

- **major** changes when an existing canonical record could acquire different physical/process meaning;
- **minor** changes are backward-compatible additive fields/record kinds under the rules below.

### Required versus optional extensions

A project header lists `required_extensions`.

- A reader that does not understand a required extension must fail closed before replay.
- Optional annotation/diagnostic data may be ignored only when the base schema explicitly marks it non-semantic.
- An unknown field inside a semantic record is not assumed ignorable unless its enclosing schema version says so.

### Migration

A migration that changes canonical meaning creates a new journal/schema revision while preserving the original project history or an immutable source reference.

Migration tooling must be deterministic, versioned and auditable. Opening an old project does not silently overwrite it with a new interpretation.

### Definition compatibility

Referenced immutable definitions retain their original schema versions. A journal migration may materialize equivalent newer definitions, but must record that transformation.

## Transaction and commit semantics

A manufacturing action is committed atomically at the logical level.

A commit transaction can contain:

1. one canonical operation;
2. zero or one material-body transition describing its committed connectivity result;
3. the new immutable revision node.

A geometry backend can first return a provisional result. The journal records the transition/revision only when the application accepts the operation under the applicable engineering-state policy.

If geometry realization fails, the failed attempt can remain diagnostic telemetry/log data but does not create a committed workpiece revision unless a later contract explicitly defines a deferred state.

## Error and refusal semantics

Canonicalization must distinguish:

- malformed raw/normalized sample trace;
- unsupported machine/process semantics;
- numeric overflow/unrepresentable value;
- invalid/cyclic frame graph;
- fitting bound not achievable;
- unsupported required extension;
- incompatible schema major version.

Where possible, failure to achieve a compact fit should degrade to a denser loss-bounded trajectory rather than reject valid manufacturing intent.

Backend geometry failure remains separate from journal invalidity as required by the founding geometry contract.

## Example: lathe finishing pass

The RCS-002 lathe fixture demonstrates:

- right-handed workpiece/setup frames;
- a rotating workpiece around +Z;
- immutable turning tool definition;
- neutral approach → engaged OD pass → neutral withdrawal;
- physical coordinates in nanometres;
- explicit normalization bounds;
- a repeated finishing pass preserved as a second manufacturing operation even when a backend may remove no additional material.

See `research/rcs-002/fixtures/lathe-finishing-pass-v1.json`.

## Example: mill slot and cut-through body transition

The mill fixture demonstrates:

- fixed-orientation end-mill trajectory;
- neutral approach and engaged slot path;
- explicit cutter/process references;
- a second cut-through operation that produces two durable material bodies;
- an explicit `material_body_transition` instead of silently selecting one connected body.

See `research/rcs-002/fixtures/mill-cut-through-v1.json`.

## Explicit limits of RCS-002

This contract intentionally does **not** settle:

- topology/face/edge naming and detailed provenance — RCS-008;
- the algebra and policy selection of tolerance/equivalence channels — RCS-007;
- regularized/deferred topology semantics — RCS-009;
- STEP application protocol, multi-body export policy and export tolerances — RCS-005;
- exact lathe or milling solver algorithms — RCS-010/RCS-011;
- persistence/transport encoding technology for production repositories;
- automatic branch merging of divergent manufacturing histories.

Those are not blockers for RCS-010/RCS-011 because the journal now supplies stable physical trajectories, process semantics, tool/setup refs, bounds and body-identity hooks.

## Acceptance-criteria trace

RCS-002 acceptance criteria are satisfied as follows.

- **Independent generation/replay:** this document defines the logical records, quantities, frame semantics, operation families and replay rules without relying on chat context.
- **Lathe and mill examples:** machine-readable fixtures cover both process families.
- **Units/handedness/transforms/versioning:** fixed explicitly above.
- **Normalization bounds/determinism:** staged canonicalization and J1/J2/J3 guarantees are explicit.
- **Material-body split/merge:** durable `material_body_transition` records are defined.
- **Compatibility:** major/minor, extension and migration rules are defined.
- **RCS-010/RCS-011 blockers:** no unresolved journal question prevents those issues once their other dependencies are met.
- **Automated validation:** `tools/validate_repo.py` validates the RCS-002 fixture structure and numeric/frame invariants.

## Recommended downstream use

### RCS-003

Use the same canonical numeric/frame conventions in adversarial fixture metadata, but keep expected physical intent separate from one backend's result.

### RCS-005

Define explicit conversion from these canonical physical quantities to STEP units and conformance tolerances. Do not reinterpret journal nanometre storage scale as export/manufacturing tolerance.

### RCS-006

Use the RCS-002 fixture parser/validator logic as a source of canonical operation inputs, while keeping benchmark result schema independent.

### RCS-008

Treat durable material-body IDs and transition records as the journal-level identity hooks. Research how backend topology and ancestry map robustly onto them.

### RCS-010 and RCS-011

Consume process semantics and canonical trajectories directly. Solver-specific B-rep/sweep/material-domain constructs remain backend-private.
