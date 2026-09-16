# Founding brief — radiCADSAC

Status: founding baseline  
Date: 2026-09-16

## Purpose

This document preserves the initial programme intent for a new class of engineering creation workflow provisionally called **Simulation Aided Creation (SAC)**.

The first user-facing implementation is **MSAC — Machinist Simulation Aided Creator**. The planned geometry/backend research project is **OpenSimachinist**.

The project began from a simple but non-negotiable proposition:

> A user should be able to create an engineering object by operating simulated machine tools in a game-like 3D environment, and the resulting workpiece must export as a valid, correct, usable STEP solid.

This is not a machining game with an export gimmick and not conventional CAD with a novelty 3D front end. The simulated manufacturing process is the modelling interface.

## Product philosophy

MSAC should feel immediately legible to somebody who understands machining and is comfortable with console games.

Examples:

- Want a turned shoulder? Put the stock in the lathe and turn it.
- Want a pocket? Mill it.
- Want a hole? Drill it with the appropriate machine/tooling path.
- Future additive work should likewise be expressed through a simulated additive process rather than an abstract CAD feature; e.g. welding or arc spray could add material.

The long-term public product may eventually also function as a game, but that is downstream of proving a productive engineering core loop.

## Initial hypothetical user

The first serious external tester is expected to be:

- an experienced machinist;
- comfortable with machining terminology, setups and machine behaviour;
- familiar with console games and gamepad motor control;
- not assumed to enjoy or prefer conventional parametric CAD workflows.

This target user is important because it lets the programme test whether machining knowledge can transfer directly into digital solid creation without first requiring CAD-specific conceptual training.

## Initial machine scope

Only two machine families are in initial scope:

1. **Lathe**
2. **Mill**

Do not broaden the founding research plan to a complete simulated workshop. The modular architecture should leave space for later manufacturing processes, but the initial kernel and MSAC contracts must be justified by lathe and mill requirements.

## Interaction model

MSAC should provide game-like spatial control and presentation.

Candidate perspectives include:

- first-person machinist view;
- a workpiece-follow/free-flight perspective informally described as a “second-person” mode.

Gamepads are considered unusually well suited to manual machining input because dual analogue sticks plus triggers can provide smooth, simultaneous control of several continuous axes or rates. This should be researched as an input advantage, not treated as a requirement of the geometry kernel.

## Anti-chore requirement

Physicality is valuable only when it improves intuition, feedback or creative control.

MSAC must not become a chore simulator. Examples of intentionally non-required busywork include:

- sweeping floors;
- wiping tools;
- filling routine consumables merely to continue;
- arbitrary warm-up waits;
- repetitive maintenance tasks that do not help create geometry.

Tool dirt, wear, chips, coolant and similar phenomena may be visually simulated later, but should not create needless friction in the modelling workflow.

## Realism policy

Realism is deliberately asymmetric.

### Geometry-critical realism

The following must be trustworthy enough to create engineering output:

- stock dimensions and coordinate frames;
- workholding/setup transforms;
- cutter/tool geometry relevant to removed material;
- tool position/orientation and machine kinematics;
- material addition/removal semantics;
- resulting dimensions and topology;
- export tolerance and validation.

### Experiential realism

The following may be approximate or cosmetic unless later research proves engineering value:

- chatter;
- sparks;
- chips;
- noise;
- coolant appearance;
- camera shake;
- spindle/tool crash effects;
- dirt and cosmetic wear.

A dramatic crash is allowed; it must not permanently destroy creative work. Undo/redo is fundamental.

## Geometry/output doctrine

The rendered workpiece mesh is not the authoritative engineering model.

The programme should preserve manufacturing operations/history and maintain an authoritative geometry representation capable of producing a valid engineering solid.

Primary output requirement:

- **STEP solid/B-rep suitable for normal downstream CAD/CAM use.**

Secondary derived output:

- watertight STL or other tessellations for convenience.

The programme must not quietly downgrade to “mesh-only but stored in a STEP container”.

## Normal pathological input

The following conditions are expected to occur routinely and often simultaneously during natural machining workflows:

- almost coincident surfaces;
- exact or near-exact tangencies;
- zero-thickness contacts;
- repeated cuts over existing surfaces;
- tiny sliver faces/remnants;
- cuts smaller than traditional modelling tolerance;
- self-crossing or retraced tool trajectories;
- noisy analogue trajectories;
- extremely large numbers of overlapping tool motions;
- cutter motion entering/exiting material continuously;
- operations that are geometrically redundant but semantically meaningful.

These are **not user errors** and may not simply be prohibited to protect a fragile CAD kernel.

## OpenSimachinist motivation

Conventional boundary-representation kernels are known to be vulnerable around degeneracy, coincidence and tolerance handling. Because the MSAC workload makes those situations routine, the programme may require a manufacturing-native geometry system.

OpenSimachinist should initially investigate Open CASCADE Technology (OCCT) because it already provides industrial B-rep modelling and STEP infrastructure. However, the project is not constrained to remain a conventional OCCT fork. It may radically alter or replace subsystems if evidence supports doing so.

Candidate research directions include:

- provenance-aware geometry;
- virtual/process-aware tolerance systems;
- semantic equivalence distinct from numerical equality;
- deferred topology;
- regularized manufacturing Booleans;
- cutter-sweep batching;
- process-specific solvers;
- symbolic perturbation;
- exact-predicate assistance;
- hybrid B-rep / implicit / volumetric / mesh representations;
- replay-driven reconstruction from operation history.

## Tool/module doctrine

Workshop machines and processes should be modular.

A machine module should be able to contribute more than visual controls. It may provide process semantics and geometry strategies to the backend.

For example, a lathe module can report spindle-axis symmetry and turning semantics rather than forcing the backend to infer them from anonymous cutter solids. A mill module can report cutter geometry, fixed or varying orientation, path semantics and process type.

The programme should preserve this information across the MSAC↔OpenSimachinist boundary.

## Operation history doctrine

Saved work must retain enough manufacturing intent to replay geometry using a different algorithm or backend later.

The operation history should support:

- undo/redo;
- deterministic replay where possible;
- regeneration under a newer kernel;
- alternate solver experiments;
- minimized regression fixtures from real user failures;
- provenance tracing from exported topology back to manufacturing actions.

The operation journal is therefore more durable than any specific intermediate B-rep.

## Genesis-repository doctrine

`radiCADSAC` intentionally preserves the planning and research process.

When the programme is mature enough to start production repositories:

- produce a fresh OpenSimachinist founding specification and implementation plan;
- produce a fresh MSAC founding specification and implementation plan;
- freeze/tag those handoffs here;
- create separate clean repositories from those handoffs;
- allow both projects to evolve independently afterward.

The genesis repository remains historical design archaeology and research reference, not a permanent monorepo governance layer.
