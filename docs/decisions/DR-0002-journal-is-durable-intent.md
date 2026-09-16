# DR-0002 — Canonical manufacturing journal is the durable source of manufacturing intent

Status: accepted  
Date: 2026-09-16  
Decision scope: programme-wide

## Context

MSAC must support undo/redo, replay, alternate solver research, regeneration under future geometry kernels, and recovery from backend failures. Intermediate B-rep objects, preview meshes, kernel caches, and frontend scene nodes are implementation-specific and may change over time.

Raw gamepad/controller samples are also too coupled to historical sampling rates, deadzones, frame timing, and input code to be the only durable manufacturing language.

## Decision

Saved project meaning is anchored in a **versioned canonical manufacturing operation journal** plus the stock/setup/tool/policy definitions required to interpret it.

The journal is authoritative for manufacturing intent/history.

Derived artifacts may include:

- committed engineering states;
- B-rep snapshots;
- meshes;
- preview fields;
- caches;
- acceleration indices.

These may be stored for performance but cannot be the only information required to understand or regenerate the workpiece.

Raw interaction telemetry may be preserved for diagnostics/research, but RCS-002 must define deterministic/bounded canonicalization rather than treating telemetry as the stable journal by default.

## Alternatives considered

### Persist the latest B-rep as the project source of truth

Rejected because it couples project meaning to one kernel/version and weakens replay/provenance/research.

### Persist only raw controller/machine samples

Rejected as the sole durable model because future replay could depend on transient frontend implementation details.

### Conventional CAD feature tree

Rejected as the primary model because the product interaction is manufacturing action, not feature-tree editing. The journal may be structured/revisioned internally without exposing conventional CAD semantics to the user.

## Evidence

The founding brief and geometry contract require replayability, backend replaceability, and manufacturing semantics across the MSAC/backend boundary.

The plan review identifies raw-input normalization as a hidden core problem.

## Consequences

- RCS-002 becomes a foundational compatibility design task.
- Backend snapshots require explicit backend/version identity.
- Undo/redo may be implemented by journal revisions/replay/snapshots rather than inverse CAD operations only.
- Regression fixtures can be derived from real manufacturing journals.
- New backends can attempt old projects without decoding private historical kernel objects.

## Reversibility

Low at programme level. The exact journal schema and history data structure are highly reversible during research, but abandoning journal-driven durable intent would invalidate replay/backend-replacement goals.

## Reconsideration trigger

This record may be refined if RCS-002 proves a different durable representation better expresses manufacturing intent, provided it remains implementation-independent, versionable, replayable, and not dependent on private kernel/frontend state.
