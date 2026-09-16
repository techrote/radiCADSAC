# DR-0004 — Stable MSAC/OpenSimachinist boundary is implementation-independent

Status: accepted  
Date: 2026-09-16  
Decision scope: programme architecture boundary

## Context

The programme needs freedom to replace or radically modify geometry algorithms while keeping saved manufacturing intent and the user-facing MSAC application viable.

The founding contract also contained an ownership ambiguity: machine modules could “provide specialized exact solver implementation”, which could be read as placing kernel-specific solvers inside Godot/frontend modules.

## Decision

The stable programme boundary between MSAC and OpenSimachinist is expressed in manufacturing/geometry semantics rather than private implementation objects.

Fixed rules:

- OCCT/private backend topology types do not cross the stable programme API.
- Godot scene/render objects do not become engineering state.
- MSAC-side **machine modules** own interaction/kinematics/process-semantic contributions.
- OpenSimachinist-side **geometry process providers** own exact/reconciled specialized solver implementations.
- Machine/process semantics cross the boundary in versioned implementation-independent form.
- The precise API/schema remains research work; this record does not select an RPC, ABI, in-process library, serialization technology, or plugin mechanism.

## Alternatives considered

### Directly expose OCCT `TopoDS_*` or equivalent types to MSAC

Rejected because it would make the frontend and saved/project architecture depend on one kernel.

### Put exact solver implementations directly inside machine modules

Rejected as a stable ownership rule because it entangles Godot/process UI modules with backend-private geometry machinery.

### Reduce every operation to anonymous Boolean operands before crossing the boundary

Rejected because it discards manufacturing semantics that may be necessary for robustness and process-specific solvers.

## Evidence

The founding product requires backend replaceability and manufacturing semantics. RCS-001 identified the machine-module ownership ambiguity while auditing `docs/01-MSAC-GEOMETRY-CONTRACT.md`.

## Consequences

- RCS-002 must define canonical semantic data without Godot or OCCT types.
- RCS-010/RCS-011 can propose specialized backend providers without changing the frontend boundary.
- The frontend may provide process hints/canonicalization rules, but solver-private state remains backend-owned.
- A future out-of-process backend, in-process GDExtension bridge, or other deployment model remains possible.

## Reversibility

Moderate. The exact API and process boundary are intentionally open. The prohibition on kernel-private/frontend-private types in the stable contract is low-reversibility because violating it would undermine backend replacement and clean project persistence.

## Reconsideration trigger

A later architecture may revise physical deployment or which side performs canonicalization, but any revision must preserve implementation-independent saved intent and avoid coupling project meaning to private kernel/frontend objects.
