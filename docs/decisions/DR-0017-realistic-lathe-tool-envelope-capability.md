# DR-0017 — realistic lathe tool-envelope capability

Status: **proposed pending RCS-020 measured evidence**  
Date: 2026-09-17  
Issue: RCS-020 / #39

## Context

DR-0013 accepted an axisymmetric axial/radial material domain as a first-class provider for a bounded fixed-axis lathe subset. Its decisive limitation was upstream: the RCS-010 experiment began from an oracle-derived completed material-removal profile rather than deriving that profile from realistic insert/tool geometry, orientation, canonical tool trajectory and reachability.

RCS-020 exists to determine whether that missing seam can be qualified without weakening programme ownership of tool/process semantics.

## Decision

**PROPOSED, not yet accepted:** retain the RCS-010 axisymmetric provider as the preferred fixed-axis lathe material solver only when a versioned capability predicate can demonstrate all of the following:

1. the immutable tool geometry and canonical tool trajectory generate the removal/material envelope within a declared construction error;
2. the derived envelope agrees with an independent material oracle within its research/production policy budget;
3. tool/holder reachability does not invalidate the commanded motion under the qualified reachability model;
4. material-body connectivity is preserved explicitly, including complete parting;
5. reconciliation to conventional B-rep satisfies the applicable RCS-005 automated geometry/STEP gates;
6. any unqualified analytic reconstruction property remains explicitly unqualified rather than inferred from a successful file.

Operations that fail the capability/reachability predicate must hand off to another qualified provider or return a stable refusal. They may not be converted into target-profile CAD features silently.

This decision remains **proposed** until RCS-020's hosted campaign is measured and accepted. The final issue pass must either accept, narrow, replace or reject it from evidence.

## Alternatives considered

### Keep DR-0013 unchanged and defer real tool envelopes to implementation

Rejected as a Genesis-v2 stopping point. Tool-envelope derivation determines what the supposedly first-class lathe provider actually supports, so postponing it risks founding implementation around an unrealistically broad capability.

### Store target radii/profiles in the journal

Rejected. This would move backend-derived geometry into durable manufacturing intent and undermine the accepted direct-machining/journal boundary. The journal should preserve tool/process motion; the provider derives material consequences.

### Treat circular nose radius as a cosmetic rendering property

Rejected. Nose radius changes the physical swept envelope and must belong to the immutable tool revision when geometry-critical.

### Ignore holder/reachability and model only the final rotational material set

Rejected. A rotationally representable result does not prove that the specified tool can create it. This would let the process-specific provider falsify manufacturing semantics.

### Require exact analytic insert-nose STEP surfaces before accepting any lathe specialization

Not selected as the RCS-020 material criterion. Material-set correctness, body semantics and conventional B-rep/STEP fidelity can be qualified independently from exact analytic reconstruction of every nose-generated surface. The latter remains visible as a separate reconstruction capability rather than becoming a hidden blocker or hidden success.

## Evidence

Current evidence before RCS-020 measurement:

- RCS-010 showed zero acceptance failures in its bounded oracle-profile set and successful automated STEP round trips, supporting the downstream axisymmetric material representation.
- RCS-008 requires durable identity to remain semantic rather than tied to regenerated topology.
- RCS-007/DR-0010 prohibit using a global tolerance to erase real positive material or ambiguity.
- RCS-009/DR-0012 permits bounded deferred/reconciliation behavior while preserving signed manufacturing intent.
- Primary manufacturer training/handbook/catalogue sources recorded in `research/rcs-020/experiment-plan-v1.json` establish that insert nose radius, approach/entering angle, and grooving/parting width/corner radii are physically meaningful tool parameters.

Evidence still required before acceptance:

- the complete RCS-020 independent-oracle campaign;
- OCCT repeated/batched/axisymmetric comparison on tool-derived profiles;
- applicable STEP Layer A-C evidence;
- explicit two-body parting evidence;
- a demonstrated reachability refusal/handoff boundary.

## Consequences

If accepted, the lathe provider's production entry predicate becomes more concrete: an operation is not accepted merely because its desired final material is rotationally symmetric. The provider must know the tool revision, path/frame semantics, and qualified envelope/reachability class.

The provider remains implementation-private. MSAC does not receive or persist RCS-020 polygons, OCCT objects or target B-rep topology.

A future exact/provenance-assisted reconstruction implementation may improve analytic STEP fidelity without changing durable journal meaning, provided it preserves the same material/error contract.

## Reversibility

Highly reversible before Genesis-v2 Gate 5. RCS-020 can narrow or reject tool classes without changing the canonical journal's ownership model.

After production handoff, widening the provider capability remains additive when new tool/envelope classes are qualified. Changing the meaning of an already accepted tool/process operation is not an implementation tweak: it requires a versioned capability/policy change and replay/regression evidence.
