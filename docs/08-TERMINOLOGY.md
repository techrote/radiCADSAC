# Programme terminology

Status: accepted Gate-1 vocabulary  
Date: 2026-09-16  
Issue: RCS-001

## Purpose

This document defines the stable-enough vocabulary used by the radiCADSAC research programme. Later research may refine implementation details, but it must not silently change these meanings. Material changes require an explicit decision record and reconciliation of dependent documents.

The terms deliberately separate **manufacturing intent**, **derived engineering geometry**, and **visual simulation**. That separation is necessary because MSAC must preserve a user's machining actions even when the geometry kernel, preview representation, or reconstruction algorithm changes.

## SAC — Simulation Aided Creation

**Simulation Aided Creation (SAC)** is the broader interaction paradigm in which a user creates engineering geometry by operating simulated physical creation processes rather than primarily by manipulating conventional CAD sketches, feature trees, extrusion dialogs, or abstract Boolean commands.

SAC describes the class of workflow, not one application or geometry kernel.

## MSAC — Machinist Simulation Aided Creator

**MSAC** is the planned user-facing Godot application implementing SAC through simulated machining.

Initial MSAC scope is deliberately limited to:

- lathe;
- mill.

MSAC owns the interactive workshop experience, control feel, camera/view systems, machine simulation, user-facing project workflow, and production of canonical manufacturing intent for the geometry backend.

MSAC is not itself defined by Godot scene geometry, render meshes, or one geometry kernel.

## OpenSimachinist

**OpenSimachinist** is the planned manufacturing-native geometry and STEP backend consumed by MSAC.

OpenSimachinist is a programme role, not yet a selected implementation architecture. OCCT is the pinned baseline and likely source substrate for research, but a deep OCCT fork, a wrapped OCCT backend, a hybrid kernel, or another architecture remain research outcomes.

OpenSimachinist ultimately owns exact/reconciled engineering geometry generation, validation, backend status reporting, and STEP production. It may expose specialized manufacturing solvers behind a stable programme-level interface.

## Workpiece

A **workpiece** is the persistent logical manufactured item being created by the user.

A workpiece identity survives:

- machining operations;
- setup changes;
- backend regeneration;
- undo/redo history;
- replacement of intermediate geometry representations.

A workpiece is not synonymous with a single transient B-rep object.

A workpiece may temporarily contain more than one disconnected **material body** after a cut separates material. The policy for body selection, retention, parting, falling scrap, and export is an explicit research requirement for RCS-002/RCS-003/RCS-005; it is not silently defined here.

## Material body

A **material body** is a connected volumetric component of the material state associated with a workpiece revision.

This term exists so the programme can discuss parting/cut-through events without overloading `workpiece` or assuming every manufacturing state is one connected solid.

Whether multiple bodies are retained, classified as workpiece/scrap, or exported is process and product policy to be researched.

## Stock

**Stock** is the initial material definition from which a workpiece begins.

A stock definition must eventually identify enough information to reconstruct the initial engineering state, including at least:

- geometry or imported geometry reference;
- dimensional units;
- stable coordinate frame;
- initial material-body identity;
- versioned source/provenance information where imported.

Material properties may be attached as metadata, but the founding geometry contract does not require high-fidelity material physics.

## Setup

A **setup** is a versioned description of how a workpiece is positioned and held for a manufacturing period.

A setup includes or references the transforms needed to relate:

- workpiece coordinates;
- machine coordinates;
- workholding/fixture coordinates where relevant.

A setup change does not change the intrinsic geometry merely because the workpiece is moved, flipped, re-chucked, or re-clamped.

## Coordinate frame

A **coordinate frame** is a named, versioned spatial reference with explicit handedness, axes, origin, units, and transform semantics.

The programme requires coordinate conventions to be explicit. RCS-002 must define the canonical journal representation and RCS-005 must reconcile dimensional units with STEP export. No consumer may assume an unstated Godot, OCCT, machine-controller, metric, or imperial convention.

## Machine module

A **machine module** is the MSAC-side modular implementation of a simulated machine/process interface.

It may own or contribute:

- controls and interaction;
- machine kinematics;
- workholding interaction;
- tool selection/definitions;
- engagement semantics;
- raw motion sampling;
- process-semantic metadata;
- canonicalization rules or hints;
- preview-specific behaviour;
- collision/spectacle behaviour.

A machine module does **not** expose OCCT/private backend objects as programme state and does not directly own the authoritative exact geometry kernel.

## Geometry process provider

A **geometry process provider** is an OpenSimachinist-side solver component specialized for a manufacturing process or machine semantic class.

Examples may eventually include:

- axisymmetric turning material-domain solver;
- drilling analytic-removal provider;
- fixed-orientation milling sweep provider;
- general/hybrid fallback provider.

A machine module and geometry process provider may be designed as a compatible pair, but they remain separated by the stable programme contract. This preserves backend replaceability and prevents Godot/frontend modules from becoming kernel-private plugins.

## Process

A **process** is a manufacturing method with semantics relevant to how material changes.

Examples include:

- OD turning;
- facing;
- boring;
- milling;
- drilling.

Future additive processes may include welding or arc spray, but they are outside the initial lathe/mill research scope.

Process semantics may inform geometry without requiring the user to express conventional CAD features.

## Operation

An **operation** is a canonical, versioned manufacturing action in the operation journal.

An operation describes what the simulated manufacturing process did in physical/process terms. It is not required to correspond one-to-one with:

- controller samples;
- render frames;
- B-rep Boolean calls;
- conventional CAD features.

An operation may contain or reference tool identity, setup, engagement state, trajectory, machine/process state, tolerance policy, and provenance.

## Raw interaction telemetry

**Raw interaction telemetry** is high-frequency device/simulation data captured before canonicalization, such as controller samples or machine-axis samples.

Raw telemetry may be retained for diagnostics, research, or re-canonicalization, but it is not by itself the durable manufacturing language. The canonical journal must not depend on a historical render frame rate, deadzone implementation, or transient input code.

## Canonical manufacturing operation

A **canonical manufacturing operation** is an operation normalized into a stable, versioned representation whose meaning is independent of the original frame/sample timing implementation within declared error bounds.

The exact schema and normalization algorithms are RCS-002 deliverables.

## Canonical trajectory

A **canonical trajectory** is the normalized geometric motion description used by one or more canonical operations.

It must have explicit:

- coordinate frame(s);
- units;
- orientation semantics where relevant;
- engagement segmentation;
- ordering/parameterization;
- approximation/error bounds if raw motion is fitted or simplified.

A canonical trajectory may contain lines, arcs, splines, sampled segments, or another representation selected by RCS-002. The term does not preselect one curve type.

## Operation journal

The **operation journal** is the versioned durable record of canonical manufacturing intent for a workpiece/project.

The journal is the programme's durable source of manufacturing intent. It must be sufficient, subject to versioned compatibility rules, to regenerate engineering geometry using a later or alternate backend.

Backend snapshots, B-reps, meshes, caches, and previews may accelerate loading/replay but are derived artifacts and cannot be the only record required to understand the workpiece.

The journal may be a linear history, revision graph, or another versioned structure; RCS-002 decides the detailed model.

## Workpiece revision

A **workpiece revision** identifies a durable manufacturing state boundary in the operation/history model.

It is conceptually defined by stock/setup/history state, not by an OCCT object address or a render mesh instance.

A revision may have zero or more derived backend realizations produced by different solver versions.

## Preview geometry

**Preview geometry** is a disposable representation used for responsive visualization, interaction, or approximate inspection.

Examples could include:

- tessellated B-rep;
- incremental mesh;
- implicit/SDF field;
- voxel/cell field;
- process-specific material/height field.

Preview geometry may be approximate and may update ahead of exact reconciliation. It must never silently become the sole source used to reconstruct primary STEP output.

## Committed engineering state

A **committed engineering state** is a backend-produced engineering realization of a specific workpiece revision that has passed the validity/quality level required for that state.

It is derived from canonical manufacturing intent. Depending on future architecture it may be represented by B-rep, a reconciled hybrid, or another model.

The phrase **authoritative geometry** should be used carefully. The programme's durable authority is split:

- the operation journal is authoritative for **manufacturing intent/history**;
- a validated committed engineering state is authoritative for **the backend's engineering realization of a particular revision**;
- preview geometry is never authoritative.

This resolves the apparent conflict between “authoritative geometry” and journal-driven replay.

## Exact state

**Exact state** means a geometry state satisfying the backend's declared engineering representation/accuracy contract for its current stage. It does not necessarily mean mathematical exact arithmetic.

Because some algorithms may defer reconciliation, documents should prefer `committed engineering state`, `reconciled state`, or a named conformance level when precision matters.

## Regularized material solid

A **regularized material solid** is the intended volumetric material set after removing lower-dimensional artifacts that have no physical material volume, according to an explicitly defined regularization policy.

The term does not yet choose a particular topological representation or algorithm. RCS-009 must define when point/edge/face-only contacts are physically irrelevant versus semantically meaningful.

## Valid solid

A **valid solid** is an engineering solid/body satisfying the topology and geometry checks required by the relevant backend/conformance level.

For primary STEP export, `valid` must ultimately be defined by RCS-005 and cannot mean only:

- visually plausible;
- watertight triangle mesh;
- successful Boolean return code;
- successful STEP writer return code.

## Tolerance classes

**Tolerance classes** are distinct policy domains that must not be silently collapsed into one epsilon before research.

The founding set is:

1. input sampling resolution;
2. machine/control resolution;
3. intended manufacturing tolerance;
4. numerical uncertainty;
5. topological equivalence tolerance/policy;
6. contact/tangency classification tolerance/policy;
7. preview tessellation tolerance;
8. export geometric tolerance;
9. validation/acceptance tolerance.

RCS-007 determines whether these remain numeric tolerances, semantic/equivalence policies, uncertainty bounds, or another formal model.

## Reconciliation

**Reconciliation** is the process of converting a permissive, deferred, specialized, or hybrid internal material state into a more conventional engineering representation with explicit validity and error guarantees.

Reconciliation may occur at boundaries such as:

- end of an engaged pass;
- tool withdrawal;
- explicit checkpoint;
- setup change;
- save/export;
- backend policy boundary.

The exact boundaries are research outcomes.

## STEP conformance

**STEP conformance** is the programme-defined evidence that a primary export is a conventional, usable engineering STEP result within declared tolerances.

It includes more than file serialization. RCS-005 must define at least:

- selected STEP application protocol/profile/entity expectations;
- pre-export solid validity;
- dimensional/geometric acceptance;
- topology acceptance;
- tolerance representation;
- analytic-surface policy;
- write/read round trip;
- independent downstream interoperability strategy;
- explicit refusal/failure conditions.

## Replay

**Replay** is regeneration of workpiece engineering state from versioned stock/setup/tool definitions plus the canonical operation journal.

Replay may target:

- the same backend/version;
- a newer backend;
- an alternate solver;
- a research backend.

Determinism may mean bitwise equality or a weaker geometric/topological equivalence; the required level must be explicitly versioned and measured.

## Provenance

**Provenance** is structured ancestry that relates derived geometry/material state to its manufacturing causes.

Potential provenance sources include:

- initial stock;
- material body;
- setup;
- tool/tool envelope;
- operation;
- solver/reconciliation event;
- split/merge relationships.

Programme provenance must not depend on transient B-rep object identity. RCS-008 researches the detailed ancestry model.

## Backend snapshot/cache

A **backend snapshot** or **cache** is a derived acceleration artifact associated with a workpiece revision and backend version.

It may be discarded and regenerated. It must not be required to preserve the durable meaning of the project.

## Geometry failure versus invalid manufacturing intent

A **geometry algorithm failure** means the selected backend/solver could not realize a manufacturing operation under its current algorithms or policies.

**Invalid/unsupported manufacturing intent** means the canonical operation is genuinely undefined or outside the declared supported process contract.

These are different statuses. A kernel failure must not be reported as if the user performed an invalid action merely because a conventional CAD algorithm found the geometry difficult.

## Terminology-change rule

If later research needs to change a term's programme meaning:

1. create or update a decision record;
2. identify affected contracts/issues/fixtures;
3. update this document and dependent current documents in the same PR where practical;
4. preserve old research results with their historical terminology rather than rewriting evidence retroactively.
