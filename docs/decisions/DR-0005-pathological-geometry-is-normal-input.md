# DR-0005 — Pathological CAD geometry is normal manufacturing input

Status: accepted  
Date: 2026-09-16  
Decision scope: geometry research and product behaviour

## Context

Natural manual machining routinely creates geometry that conventional CAD kernels often treat as numerically difficult or degenerate: coincident finishing passes, tangency, zero-depth contact, retracing, tiny cusps/slivers, sub-tolerance moves, and large overlapping path histories.

For MSAC these conditions will frequently arise from ordinary competent use rather than malformed input.

## Decision

The programme treats the following as **normal supported research workload**, not invalid user behaviour merely because a geometry algorithm struggles:

- exact/near coincidence;
- tangency and lower-dimensional contact;
- zero-depth/redundant passes;
- sub-tolerance movement;
- tiny/sliver remnants;
- retraced/self-crossing/jittery trajectories;
- overlapping cutter envelopes;
- extremely large operation/segment counts.

A backend may normalize, regularize, batch, defer, or classify such events according to explicit policy, but it must distinguish algorithm failure from genuinely undefined/unsupported manufacturing intent.

## Alternatives considered

### Prohibit or snap away difficult motion before it reaches the kernel

Rejected as a general policy because it would make geometry-kernel limitations constrain the SAC interaction model and could silently change intended dimensions.

### Require continuous valid B-rep after every controller sample

Rejected as a founding requirement because it encourages pathological operation counts and makes render/input cadence dictate topology updates.

### Treat every tiny motion as geometrically meaningful regardless of policy

Not accepted as a fixed rule. Explicit manufacturing/control/export policies may classify some motion as redundant or below meaningful resolution, but those policies must be versioned and measurable rather than hidden kernel heuristics.

## Evidence

The founding brief explicitly identifies these conditions as routine and often simultaneous. The user-facing premise requires natural manual machining rather than CAD-safe constrained gestures.

## Consequences

- RCS-003 must create adversarial fixtures from these workloads.
- RCS-006 must measure them rather than filter them out.
- RCS-007–RCS-012 must compare approaches using the same workload.
- MSAC error/status presentation must not blame the user for a backend algorithm failure.

## Reversibility

Low. Removing this requirement would materially change MSAC into a constrained CAD-safe interaction system rather than the intended simulation-aided machining creator.

## Reconsideration trigger

Individual operations may be explicitly outside an implemented process domain, but broad rejection of coincidence/tangency/retracing/etc. requires a product-level decision and evidence that the SAC workflow remains useful without them.
