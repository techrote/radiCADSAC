# DR-0001 — STEP is the mandatory primary engineering output

Status: accepted  
Date: 2026-09-16  
Decision scope: programme-wide

## Context

The central value proposition of MSAC is that direct simulated machining produces normal downstream engineering geometry rather than only a visual or mesh approximation.

A watertight STL can represent shape for printing/rendering but does not satisfy the founding requirement for conventional CAD/CAM interoperability.

## Decision

A successful primary MSAC/OpenSimachinist export must be a conventional usable STEP engineering result within the programme's declared conformance/tolerance policy.

- STEP is mandatory primary output.
- STL/tessellations may be derived convenience outputs.
- A mesh-only architecture is not an acceptable fallback.
- A triangulated surrogate merely serialized inside a STEP container does not satisfy the programme by default.
- Export must fail explicitly when STEP conformance cannot be established.

RCS-005 owns the measurable definition of STEP conformance.

## Alternatives considered

### STL-first with optional STEP reconstruction

Rejected as a founding architecture because it allows the internal representation to lose engineering/analytic information and makes STEP reconstruction an unreliable afterthought.

### Proprietary Parasolid as mandatory output

Not selected. Parasolid interoperability may be explored later, but the founding open-source programme must not require proprietary Parasolid output.

### STEP plus STL as equal outputs

Rejected as a framing choice. STL remains useful, but treating it as an equal fallback weakens the architectural requirement that the authoritative engineering result remain CAD-usable.

## Evidence

This decision comes directly from the founding product requirement recorded in `docs/00-FOUNDING-BRIEF.md`, `README.md`, and `AGENTS.md`.

RCS-001 found no conflicting product requirement.

## Consequences

- Geometry research must include STEP reconciliation cost/fidelity in evaluations.
- Candidate hybrid/mesh/implicit representations are not judged successful solely by watertightness.
- RCS-005 must define conformance before architecture synthesis.
- OpenSimachinist architecture must retain or recover sufficient analytic/topological information to meet the export contract.

## Reversibility

Low before production handoff only by explicit programme-purpose change. Changing this would alter the core value proposition rather than merely an implementation choice.

## Reconsideration trigger

Only an explicit future programme decision that changes the primary engineering interoperability goal should supersede this record.
