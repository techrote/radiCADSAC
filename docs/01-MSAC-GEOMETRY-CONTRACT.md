# MSAC ↔ geometry backend founding contract

Status: Gate-1 contract v0.1; accepted programme boundary, with detailed schemas/algorithms delegated to research  
Date: 2026-09-16  
Issue: RCS-001 reconciliation

## Purpose

This document defines the minimum programme-level contract between the future **MSAC** application and whatever geometry system becomes **OpenSimachinist**.

It is intentionally implementation-independent. OCCT-specific classes, handles and topology objects must not become part of this stable boundary.

Terminology in `08-TERMINOLOGY.md` is normative for current research vocabulary.

## Core principle

> The simulated manufacturing action is authoritative intent; the geometric implementation used to realize that action is replaceable.

MSAC and its machine modules capture what the user physically did in explicit machine/process coordinate semantics. A versioned canonical manufacturing journal preserves that intent. The backend is responsible for constructing, validating, reconciling and exporting engineering geometry from it.

Authority is separated deliberately:

- the **canonical operation journal** is durable authority for manufacturing intent/history;
- a **committed engineering state** is authoritative for the backend's engineering realization of a specific workpiece revision;
- **preview geometry** is disposable and non-authoritative.

This avoids making an intermediate B-rep the only durable meaning of a project while still allowing the backend to expose a trustworthy committed engineering state.

## Stable inputs to the geometry backend

The backend must be capable of consuming canonical manufacturing operations carrying enough semantics to avoid reducing every action to an anonymous Boolean.

At minimum an operation may need:

- operation identifier;
- workpiece identifier;
- parent workpiece revision;
- material-body identity where relevant;
- setup/workholding identifier;
- machine type and instance;
- process type;
- stock/body identity;
- tool identifier and geometric definition/version;
- tool coordinate frame;
- tool orientation history where relevant;
- machine/workpiece/setup transforms;
- explicit dimensional units and coordinate-frame semantics;
- timestamped or parameterized canonical trajectory;
- spindle/rotary state where relevant;
- cut/add/neutral engagement state;
- process-specific metadata;
- tolerance/policy references;
- deterministic input-normalization metadata;
- provenance links to previous operations/body split-merge events where relevant.

The precise serialized schema is an RCS-002 research deliverable, not fixed here.

## Coordinate and units requirement

No stable consumer may depend on an unstated Godot, OCCT, machine-controller, metric, or imperial convention.

RCS-002 must define the canonical journal representation for:

- dimensional units;
- handedness and axis conventions;
- transform composition/order;
- coordinate-frame versioning;
- numeric representation/precision expectations.

User-facing metric/imperial display choices must not alter the stored physical meaning of a canonical operation.

RCS-005 must define how canonical units and dimensional tolerances map to STEP and how conversion/round-trip behaviour is tested.

## Geometry backend responsibilities

The backend must ultimately support:

1. Creating engineering stock/material states from canonical primitive or imported definitions.
2. Applying manufacturing operations to workpiece state.
3. Exploiting process semantics where useful.
4. Maintaining enough provenance to explain/replay geometry evolution.
5. Returning preview/query geometry suitable for MSAC visualization and inspection.
6. Supporting undo/redo through immutable revisions, replay, snapshots, inverse bookkeeping, or another validated mechanism.
7. Detecting and reporting unresolved/invalid geometry rather than silently corrupting state.
8. Producing a conventional valid STEP engineering result at export boundaries.
9. Producing derived tessellations such as STL from committed/reconciled geometry.
10. Supporting deterministic or explicitly characterized replay.
11. Representing or reporting material-body split/merge events without silently losing disconnected volumetric material.

## MSAC responsibilities

MSAC is expected to own:

- user input devices and control feel;
- camera systems;
- machine visual simulation;
- non-authoritative chips/sparks/chatter/etc.;
- user interaction and tool selection;
- machine module orchestration;
- sampling raw controller/machine motion;
- producing process semantics and the information required for canonical manufacturing operations according to the accepted RCS-002 contract;
- presentation of geometry/backend warnings and validation state;
- save/project packaging around the canonical operation history and versioned referenced definitions.

The exact placement of every canonicalization step remains a RCS-002 design question. Raw Godot scene objects and render meshes must never become the authoritative engineering model.

## Machine module extension point

A **machine module** is the MSAC-side process/interaction module. It may provide or contribute:

- kinematic model;
- tool definitions;
- engagement semantics;
- raw sampling and specialized trajectory-canonicalization rules/hints;
- process-specific semantic metadata;
- preview strategy;
- process-specific validation hints;
- workholding/setup interaction.

A machine module does not directly expose backend-private topology objects or own the stable exact geometry implementation.

## Geometry process provider extension point

A **geometry process provider** is the OpenSimachinist-side specialized solver component. It may provide:

- process-specific exact/reconciled material-state algorithms;
- analytic/specialized removal constructions;
- backend-side batching/reconciliation strategy;
- backend validation specific to a process domain;
- fallback/escalation rules to other providers.

Machine modules and geometry process providers may be paired through versioned semantic contracts, but the stable boundary remains implementation-independent.

The backend must permit specialized solvers without making one solver mandatory for every operation.

## Initial process families

### Lathe

The backend must account for process semantics including:

- known spindle axis;
- rotating workpiece;
- fixed or controlled tool orientation;
- common axisymmetric material-removal behaviour;
- facing, OD/ID turning, boring and related initial operations;
- repeated/retraced finishing passes;
- approach, tangency and withdrawal from already-created surfaces;
- eventual body separation/cut-through semantics where turning operations disconnect material.

Research should test whether a 2D radius/axial material-domain solver can robustly reconstruct many lathe results without repeated general 3D Booleans.

### Mill

The backend must account for:

- cutter solid/envelope;
- XYZ trajectory;
- fixed and eventually variable tool orientation;
- repeated/retraced paths;
- cutter sweeps and overlapping swept volumes;
- drilling/slotting/facing/pocket-like process semantics where detectable or explicitly supplied;
- arbitrary analogue freehand motion as a valid workload;
- cut-through operations that can disconnect material bodies.

Research should compare direct repeated B-rep subtraction, batched swept volumes, process-specialized operations and hybrid representations.

## Pathological conditions are valid workload

The following must not be rejected merely because a conventional CAD kernel finds them inconvenient:

- near-coincident faces/edges;
- exactly coincident intended finishing passes;
- tangent entry/exit;
- zero-volume contact events;
- sub-export-tolerance or sub-model-tolerance movement;
- lower-dimensional debris generated by an intermediate algorithm;
- very short path segments;
- trajectory jitter;
- self-crossing trajectory;
- overlapping removal volumes;
- huge operation counts.

The backend may normalize, regularize, batch or semantically ignore geometrically redundant events if the resulting workpiece remains faithful to the declared manufacturing/tolerance policy.

Algorithm failure must remain distinguishable from invalid manufacturing intent.

## Disconnected material bodies are a required research case

A manufacturing operation can split a workpiece's material state into multiple disconnected volumetric bodies.

The programme does not yet prescribe whether every separated body remains part of the user-visible workpiece, becomes scrap, remains clamped, falls free, or is selected for export. However, implementations/research may not silently delete or merge such material merely because singular-solid assumptions are convenient.

Required downstream work:

- RCS-002: body identity and split/merge history hooks;
- RCS-003: representative parting/cut-through fixtures and expected physical intent;
- RCS-005: primary STEP body/product/export-selection semantics;
- RCS-008: stable split/merge provenance;
- RCS-009: regularized connectivity semantics.

## Tolerance concepts must not be prematurely collapsed

Research must distinguish at least these concepts before selecting a numeric model:

- input sampling resolution;
- machine/control resolution;
- intended manufacturing tolerance;
- numerical uncertainty;
- topological equivalence tolerance/policy;
- contact/tangency classification tolerance/policy;
- preview tessellation tolerance;
- export geometric tolerance;
- validation/acceptance tolerance.

A major research question is whether these should be independent policy channels, semantic/equivalence constructs, uncertainty bounds, or another formal model rather than one propagated epsilon.

## Revision and replay model

A saved MSAC project must not become unreadable merely because an intermediate kernel representation changes.

Therefore the programme preserves enough versioned information to interpret:

- initial stock definition;
- material-body identities where relevant;
- setup transforms;
- canonical operation journal;
- referenced tool definitions and versions;
- normalization/tolerance policy versions;
- optional raw telemetry for forensic/research use when retained;
- optional backend snapshots/caches as accelerators only;
- backend/kernel version used to create a given derived result.

A future backend should be able to replay an old journal subject to explicit versioned compatibility rules.

## Preview versus committed engineering representation

MSAC may use a fast visual representation independent from the committed/reconciled engineering representation.

Examples under investigation include:

- tessellated B-rep;
- incremental mesh;
- signed-distance/implicit field;
- voxel/cell representation;
- process-specific height/material fields.

The preview is disposable and must not become the only source from which STEP is reconstructed.

Internal OpenSimachinist state may itself be deferred/hybrid/approximate at some stages if its declared status is explicit and it can later reconcile within the engineering/export contract.

## Export contract

A successful primary export must result in a conventional engineering STEP result rather than a triangulated surrogate.

RCS-005 must define exact conformance criteria, including:

- selected STEP protocol/profile/entity/product expectations;
- valid closed solid/body topology;
- allowed multi-body/product structure and body-selection rules;
- manifold/orientable boundary where expected;
- no unresolved lower-dimensional manufacturing debris in exported bodies;
- dimensions within declared tolerance;
- explicit dimensional units and conversion correctness;
- volume/mass-properties consistency within declared tolerance;
- analytic-surface preservation/approximation policy;
- successful STEP round-trip through the selected writer/reader baseline;
- validation in at least one independent downstream consumer during conformance testing.

Where export cannot satisfy the contract, the system must report failure clearly rather than silently emitting a superficially valid file.

## Error/failure contract

The backend should distinguish at least:

- operation accepted and committed engineering state produced;
- operation accepted but reconciliation deferred;
- operation normalized/regularized with recorded policy;
- material body split/merge event requiring policy/user handling;
- operation rejected as genuinely undefined/unsupported;
- backend algorithm failure requiring retry/alternate solver;
- export reconciliation failure;
- validation/conformance failure.

Algorithm failure must not be conflated with invalid user intent.

## Performance contract

Gameplay/control feedback should remain responsive even when engineering reconciliation is expensive.

The programme may therefore separate:

- immediate visual response;
- operation canonicalization;
- incremental engineering update;
- deferred reconciliation;
- high-confidence export reconstruction.

No requirement currently says every exact Boolean must complete synchronously inside a render frame.

## Explicit non-contracts

The founding programme does **not** require:

- continuous B-rep validity after every controller sample;
- one Boolean operation per input sample;
- OCCT data structures in saved projects;
- preservation of conventional CAD feature-tree semantics;
- mathematically exact arithmetic for every geometry operation;
- physically exact chatter/tool wear/thermal simulation;
- modelling every cutting tooth;
- punishing irreversible crash/failure behaviour;
- one permanently connected material body throughout every operation.

These exclusions protect the SAC interaction model from accidental conventional-CAD, kernel-coupling, or chore-simulation assumptions.
