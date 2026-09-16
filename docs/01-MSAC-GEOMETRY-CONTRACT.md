# MSAC ↔ geometry backend founding contract

Status: planning baseline; intended to be challenged and refined by research  
Date: 2026-09-16

## Purpose

This document defines the minimum programme-level contract between the future **MSAC** application and whatever geometry system becomes **OpenSimachinist**.

It is intentionally implementation-independent. OCCT-specific classes, handles and topology objects must not become part of this stable boundary.

## Core principle

> The simulated manufacturing action is authoritative; the geometric implementation used to realize that action is replaceable.

MSAC records what the user physically did in a machine/process coordinate system. The backend is responsible for constructing, validating and exporting the resulting engineering solid.

## Stable inputs to the geometry backend

The backend must be capable of consuming canonical manufacturing operations carrying enough semantics to avoid reducing every action to an anonymous Boolean.

At minimum an operation may need:

- operation identifier;
- workpiece identifier;
- parent workpiece revision;
- setup/workholding identifier;
- machine type and instance;
- process type;
- stock/body identity;
- tool identifier and geometric definition;
- tool coordinate frame;
- tool orientation history where relevant;
- machine/workpiece transform;
- timestamped or parameterized trajectory;
- spindle/rotary state where relevant;
- cut/add/neutral engagement state;
- process-specific metadata;
- tolerance/policy references;
- deterministic input-normalization metadata;
- provenance links to previous operations.

The precise serialized schema is a research deliverable, not fixed here.

## Geometry backend responsibilities

The backend must ultimately support:

1. Creating engineering stock solids from canonical primitive or imported definitions.
2. Applying manufacturing operations to workpiece state.
3. Exploiting process semantics where useful.
4. Maintaining enough provenance to explain/replay geometry evolution.
5. Returning preview/query geometry suitable for MSAC visualization and inspection.
6. Supporting undo/redo through immutable revisions, replay, inverse bookkeeping, snapshots, or another validated mechanism.
7. Detecting and reporting unresolved/invalid geometry rather than silently corrupting state.
8. Producing a conventional valid STEP solid at export boundaries.
9. Producing derived tessellations such as STL from authoritative geometry.
10. Supporting deterministic or explicitly characterized replay.

## MSAC responsibilities

MSAC is expected to own:

- user input devices and control feel;
- camera systems;
- machine visual simulation;
- non-authoritative chips/sparks/chatter/etc.;
- user interaction and tool selection;
- machine module orchestration;
- sampling raw controller/machine motion;
- converting raw interaction into canonical manufacturing operations according to a documented normalization policy;
- presentation of geometry/backend warnings and validation state;
- save/project packaging around the canonical operation history.

The exact split between machine module and geometry backend may change after research, but raw Godot scene objects and render meshes must not become the authoritative engineering model.

## Machine module extension point

A machine/process module may provide:

- kinematic model;
- tool definitions;
- engagement semantics;
- specialized trajectory canonicalization;
- process-specific geometry hints;
- specialized exact solver implementation;
- preview strategy;
- validation rules;
- reconciliation strategy.

The backend must permit specialized solvers without making them mandatory for every operation.

## Initial process families

### Lathe

The backend must account for process semantics including:

- known spindle axis;
- rotating workpiece;
- fixed or controlled tool orientation;
- common axisymmetric material-removal behaviour;
- facing, OD/ID turning, boring and related initial operations;
- repeated/retraced finishing passes;
- approach, tangency and withdrawal from already-created surfaces.

Research should test whether a 2D radius/axial material-domain solver can robustly reconstruct many lathe results without repeated general 3D Booleans.

### Mill

The backend must account for:

- cutter solid/envelope;
- XYZ trajectory;
- fixed and eventually variable tool orientation;
- repeated/retraced paths;
- cutter sweeps and overlapping swept volumes;
- drilling/slotting/facing/pocket-like process semantics where detectable or explicitly supplied;
- arbitrary analogue freehand motion as a valid workload.

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

## Tolerance concepts must not be prematurely collapsed

Research must distinguish at least these concepts before selecting a numeric model:

- input sampling resolution;
- machine/control resolution;
- intended manufacturing tolerance;
- numerical uncertainty;
- topological equivalence tolerance;
- contact/tangency classification tolerance;
- preview tessellation tolerance;
- export geometric tolerance;
- validation/acceptance tolerance.

A major research question is whether these should be independent policy channels rather than one propagated epsilon.

## Revision and replay model

A saved MSAC project must not become unreadable merely because an intermediate kernel representation changes.

Therefore the programme should preserve:

- initial stock definition;
- setup transforms;
- canonical operation journal;
- referenced tool definitions and versions;
- normalization/tolerance policy versions;
- optional backend snapshots/caches as accelerators only;
- backend/kernel version used to create a given derived result.

A future backend should be able to replay an old journal, subject to versioned compatibility rules.

## Preview versus exact representation

MSAC may use a fast visual representation independent from the final exact representation.

Examples under investigation include:

- tessellated B-rep;
- incremental mesh;
- signed-distance/implicit field;
- voxel/cell representation;
- process-specific height/material fields.

The preview is disposable and must not become the only source from which STEP is reconstructed.

## Export contract

A successful primary export must result in a conventional engineering STEP solid rather than a triangulated surrogate.

Research must define exact conformance criteria, but likely checks include:

- valid closed solid topology;
- manifold/orientable boundary where expected;
- no unresolved lower-dimensional manufacturing debris in the exported solid;
- dimensions within declared tolerance;
- volume/mass-properties consistency within declared tolerance;
- successful STEP round-trip through the selected writer/reader baseline;
- validation in at least one independent downstream consumer during conformance testing.

Where export cannot satisfy the contract, the system must report failure clearly rather than silently emitting a superficially valid file.

## Error/failure contract

The backend should distinguish:

- operation accepted and exact state committed;
- operation accepted but exact reconciliation deferred;
- operation normalized/regularized with recorded policy;
- operation rejected as genuinely undefined/unsupported;
- backend algorithm failure requiring retry/alternate solver;
- export reconciliation failure;
- validation failure.

Algorithm failure must not be conflated with invalid user intent.

## Performance contract

Gameplay/control feedback should remain responsive even when exact CAD reconciliation is expensive.

The programme may therefore separate:

- immediate visual response;
- operation canonicalization;
- incremental exact reconciliation;
- high-confidence export reconstruction.

No requirement currently says every exact Boolean must complete synchronously inside a render frame.

## Explicit non-contracts

The founding programme does **not** require:

- continuous B-rep validity after every controller sample;
- one Boolean operation per input sample;
- OCCT data structures in saved projects;
- preservation of conventional CAD feature-tree semantics;
- physically exact chatter/tool wear/thermal simulation;
- modelling every cutting tooth;
- punishing irreversible crash/failure behaviour.

These exclusions exist to protect the core SAC interaction model from accidental conventional-CAD or chore-simulation assumptions.
