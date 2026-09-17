# Programme terminology

Status: accepted Gate-1 vocabulary, reconciled through RCS-009  
Date: 2026-09-17  
Issue: RCS-001; terminology refinement: DR-0012 / RCS-009

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

A workpiece may contain more than one disconnected **material body** after a cut separates material. Body selection, retention, parting, scrap classification and export are explicit semantic decisions and must not be inferred by silently taking the largest or first backend solid.

## Material body

A **material body** is a connected volumetric component of the regularized material state associated with a workpiece revision.

This term exists so the programme can discuss parting/cut-through events without overloading `workpiece` or assuming every manufacturing state is one connected solid. Point-, edge-, or face-only contact does not by itself create a volumetric bridge between material bodies.

Whether multiple bodies are retained, classified as workpiece/scrap, or selected for export is process and product policy. RCS-005 requires preserve-all or explicit recorded selection at the export boundary.

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

The programme requires coordinate conventions to be explicit. RCS-002 defines the canonical journal representation and RCS-005 reconciles dimensional units with STEP export. No consumer may assume an unstated Godot, OCCT, machine-controller, metric, or imperial convention.

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

The accepted RCS-002 contract defines the founding schema and normalization rules.

## Canonical trajectory

A **canonical trajectory** is the normalized geometric motion description used by one or more canonical operations.

It must have explicit:

- coordinate frame(s);
- units;
- orientation semantics where relevant;
- engagement segmentation;
- ordering/parameterization;
- approximation/error bounds if raw motion is fitted or simplified.

A canonical trajectory may contain lines, arcs, splines, sampled segments, or another versioned representation. The term does not preselect one curve type.

## Operation journal

The **operation journal** is the versioned durable record of canonical manufacturing intent for a workpiece/project.

The journal is the programme's durable source of manufacturing intent. It must be sufficient, subject to versioned compatibility rules, to regenerate engineering geometry using a later or alternate backend.

Backend snapshots, B-reps, meshes, pending-topology ledgers, caches, and previews may accelerate loading/replay but are derived artifacts and cannot be the only record required to understand the workpiece.

The accepted founding model uses immutable workpiece revisions connected by canonical operations; future versioned extensions may add graph structure without changing the journal's authority.

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

A **regularized material solid** is the volumetric material set `M` satisfying `M = cl(int(M))` after the operation's set semantics are applied. For subtractive material set `A` and removal envelope `B`, the founding physical interpretation is the regularized difference `cl(int(A \ B))`, subject to explicit process/body-retention policy.

A point-, edge-, or face-only contact has no material volume and does not by itself remove material or join two material bodies. Such contact may nevertheless remain semantically meaningful as contact, tangency, uncertainty or provenance evidence. Conversely, any known positive-volume removal remains a material change regardless of whether it is numerically small.

This term defines physical material semantics, not a particular kernel data structure. DR-0012 / RCS-009 records the accepted founding rule.

## Deferred topology

**Deferred topology** is backend-private derived engineering state in which some canonical manufacturing events have not yet been converted into newly materialized B-rep faces/edges, while enough semantic/provenance information is retained to reconstruct the intended regularized volumetric material at a required reconciliation boundary.

A deferred state may retain the last reconciled material bodies plus pending immutable removal envelopes and contact/uncertainty classifications. It never replaces the operation journal. Geometry recomputation may be elided only when RCS-008 semantic lineage proves equivalence; transient topology identity or a broad epsilon is insufficient proof.

Deferral is bounded. Material-body connectivity decisions, exact topology-dependent queries, incompatible setup/tool-definition transitions, explicit conventional checkpoints, downstream B-rep contracts, and primary STEP export can force reconciliation.

## Valid solid

A **valid solid** is an engineering solid/body satisfying the topology and geometry checks required by the relevant backend/conformance level.

For primary STEP export, `valid` is governed by the accepted RCS-005 contract and cannot mean only:

- visually plausible;
- watertight triangle mesh;
- successful Boolean return code;
- successful STEP writer return code.

## Tolerance classes

**Tolerance classes** are distinct policy domains that must not be silently collapsed into one epsilon.

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

RCS-007 retained these as separate channels and established that ambiguity may require a semantic/uncertainty state rather than an enlarged global numeric epsilon.

## Reconciliation

**Reconciliation** is the process of converting a permissive, deferred, specialized, or hybrid internal material state into a conventional engineering representation with explicit validity and error guarantees.

Under DR-0012, hard reconciliation boundaries include:

- primary STEP export;
- body-retention/scrap/clamping decisions after a possible volumetric connectivity change;
- exact engineering queries that require current boundary topology or body count;
- setup/frame/tool-definition transitions that cannot preserve pending-envelope semantics explicitly;
- explicit committed/checkpoint requests requiring conventional valid solids;
- transfer to a downstream component whose contract requires reconciled B-rep.

End of an engaged pass and tool withdrawal remain useful **soft** checkpoint candidates rather than universal hard boundaries. Process-specific RCS-010/RCS-011 research may choose stronger boundaries.

## STEP conformance

**STEP conformance** is the programme-defined evidence that a primary export is a conventional, usable engineering STEP result within declared tolerances.

The accepted RCS-005 contract includes more than file serialization. It separates:

- selected STEP application protocol/profile/entity expectations;
- pre-export solid validity and material-body selection;
- dimensional/geometric acceptance;
- topology acceptance;
- tolerance representation;
- analytic-surface policy;
- write/read round trip;
- independent downstream interoperability strategy;
- explicit refusal/failure conditions.

A deferred or permissive state must reconcile before it can satisfy this contract.

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

Accepted provenance sources include or may reference:

- initial stock;
- material body;
- setup;
- tool/tool envelope;
- operation;
- solver/reconciliation event;
- split/merge/replacement relationships.

Programme provenance does not depend on transient B-rep object identity. RCS-008 established semantic lineage as the durable basis and DR-0012 uses that lineage as the prerequisite for safe geometry-recomputation elision.

## Backend snapshot/cache

A **backend snapshot** or **cache** is a derived acceleration artifact associated with a workpiece revision and backend version.

It may be discarded and regenerated. It must not be required to preserve the durable meaning of the project. An RCS-009 pending/deferred ledger is one such replaceable backend-derived artifact.

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
