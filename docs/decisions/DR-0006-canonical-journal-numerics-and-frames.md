# DR-0006 — Canonical journal uses explicit fixed physical quantities and right-handed frames

Status: accepted  
Date: 2026-09-16  
Decision scope: canonical journal boundary

## Context

RCS-001 requires units, handedness, axis conventions, transform composition and numeric expectations to be explicit at the durable MSAC↔OpenSimachinist boundary.

Persisting binary floating-point values with unstated engine/controller conventions would make old journals vulnerable to unit/display assumptions and implementation-specific rounding. Conversely, selecting a storage quantum must not be confused with selecting a manufacturing or topology tolerance.

## Decision

`msac-journal/1.0` uses:

- signed 64-bit integer nanometres for lengths/translations;
- signed 64-bit integer nanoradians for angles;
- signed 64-bit integer nanoseconds for durations/time offsets;
- signed integer nanometres/second and nanoradians/second for rates;
- fixed-rational quaternion components scaled by `10^15` for durable orientation tokens;
- right-handed Cartesian frames with explicit immutable frame revisions;
- column-vector transforms defined as `p_parent = R(q) * p_child + t`;
- explicit child→parent composition order.

Metric/imperial UI is presentation only and cannot alter committed physical meaning.

The storage quantum is **not** the programme manufacturing, equivalence, export or validation tolerance.

## Alternatives considered

### Store user-selected units and binary floating-point values

Rejected for the canonical boundary because physical equivalence would depend unnecessarily on display-unit choices and implementation-specific numeric details.

### Canonical metres as IEEE-754 doubles

Not selected for the durable token because binary encoding/rounding would become part of persistence meaning without providing a useful programme benefit.

### Exact arbitrary-precision rationals everywhere

Rejected for the baseline journal because complexity is disproportionate to the physical machining domain. Exact arithmetic remains an internal research option for geometry algorithms.

## Evidence

RCS-001 foundation documents require explicit units/frames and backend-independent saved meaning. The BIPM SI system provides stable physical unit semantics; the journal converts those physical quantities into fixed programme storage scales.

## Consequences

- RCS-003 fixtures can use one explicit physical convention.
- RCS-005 must convert canonical quantities to/from selected STEP units without treating the nanometre storage scale as export tolerance.
- Machine modules must translate controller-specific axes, diameter programming and display units before journal commit.
- Readers can reject overflow or malformed transforms deterministically.

## Reversibility

Medium. A future journal major version can change numeric encoding through explicit migration. Existing `msac-journal/1.x` meaning remains stable.

## Reconsideration trigger

Reconsider for a new journal major version if real manufacturing requirements exceed signed 64-bit range/resolution, orientation fixed-rational encoding proves impractical, or an alternative encoding demonstrably improves interoperability without weakening deterministic physical meaning.
