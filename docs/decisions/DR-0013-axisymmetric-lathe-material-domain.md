# DR-0013 — Axisymmetric material domain as a first-class lathe provider

Status: proposed pending RCS-010 measured evidence  
Date: 2026-09-17  
Decision scope: fixed-axis turning solver architecture

## Context

The initial programme scope includes a lathe and must tolerate exact retraces, repeated finishing, very small removals and gamepad/analogue-control trajectories without requiring one fragile 3D Boolean per journal sample. RCS-009 accepted regularized volumetric material semantics and bounded deferred topology, while leaving process-specific domains to RCS-010/RCS-011.

Fixed-axis turning has unusually strong rotational symmetry. A large useful subset can be described by material radius as a function of spindle-axis position and reconstructed as a solid of revolution. RCS-010 compares that possibility against repeated and batched conventional 3D subtraction before selecting it.

## Proposed decision

Subject to the RCS-010 measured campaign satisfying its acceptance contract:

1. OpenSimachinist should treat a verified axisymmetric axial/radial material domain as a **first-class process provider** for the supported fixed-axis lathe subset.
2. The provider is not the programme's universal geometry kernel. It must expose explicit support/refusal criteria and reconcile/handoff when symmetry or supported tool-envelope semantics cease to hold.
3. The canonical manufacturing journal remains durable authority. The 2D material state is derived/rebuildable backend state.
4. Exact retrace/repeated-pass journal events remain preserved. Geometry recomputation may be elided only when operation semantics plus RCS-008 lineage prove the removal envelope/material effect equivalent.
5. Positive-volume removal is never suppressed by a broad fuzzy tolerance. RCS-007 tolerance/uncertainty channels remain separate.
6. Conventional validated B-rep reconciliation is mandatory for primary STEP export and general/non-axisymmetric provider handoff.
7. Reconciled faces/edges are regenerated implementation details; semantic lineage and material-body identity cross provider boundaries instead of `TopoDS_*` identity.
8. Batched 3D removal remains a supported comparison/fallback strategy where an operation is axisymmetric in intent but the specialized envelope implementation is not yet qualified.
9. Tool-envelope generation for real insert/nose-radius/orientation semantics is a required production subsystem and is not considered solved by the founding profile prototype.

## Alternatives considered

### One 3D Boolean per canonical event

Retained as a baseline/general fallback but not preferred for a domain where repeated/retraced histories can be represented without repeated topology construction. It remains necessary evidence because the specialized provider must reproduce the same material result.

### Batched 3D cutter-envelope subtraction only

A serious alternative. It can remove operation-count pressure without introducing a persistent 2D material representation. RCS-010 measures it separately; if it provides equivalent correctness/robustness with simpler implementation, this decision should be narrowed.

### Axisymmetric domain as the entire kernel

Rejected. Milling, live tooling, eccentric features and general freehand motion are outside the representation's natural closure. The provider must hand off rather than approximate them.

### Tessellated/mesh revolution as the lathe result

Rejected for the primary engineering path. The programme requires conventional usable STEP and preservation of analytic cylinders/cones/planes where the intended geometry is analytic.

## Evidence

Accepted prior evidence:

- RCS-002 defines canonical manufacturing intent independently of any geometry backend.
- RCS-003 classifies repeated finishing, facing, ID/OD retrace, shoulder/tangency, analogue noise and long histories as normal lathe inputs.
- RCS-006 supplies pinned OCCT geometry/STEP measurement infrastructure.
- RCS-007 rejects one broad global fuzzy tolerance as material semantics.
- RCS-008 permits topology regeneration while preserving semantic lineage and provides the proof model for exact-retrace geometry elision.
- RCS-009 accepts regularized volumetric semantics and bounded deferred topology with reconciliation at export/provider boundaries.

RCS-010 measured evidence is intentionally not claimed here until the hosted campaign has completed and its workflow/job/artifact provenance is pinned in `research/rcs-010/measured-summary-v1.json`.

## Consequences if accepted

- RCS-013 may architect solver dispatch around manufacturing/process domains rather than one universal Boolean engine.
- Initial lathe implementation can prioritize OD/facing/shoulder/taper/boring vertical slices while explicitly delegating non-axisymmetric operations.
- The stable MSAC boundary does not change; machine/process semantics cross the boundary, not 2D profile internals.
- Export and lathe→mill handoff become explicit reconciliation checkpoints.
- Preview/inspection APIs will need to distinguish material-domain queries from topology-dependent queries that force reconciliation.
- Tool-envelope qualification becomes a concrete implementation/research item rather than being buried inside general Boolean replay.

## Reversibility

High before production persistence commits to provider-private state. Because the journal and programme-facing identities remain implementation-independent, the axisymmetric provider can be narrowed, replaced or bypassed without changing saved manufacturing intent.

## Reconsideration triggers

Reconsider, narrow or reject this decision if RCS-010 or later production evidence shows that:

- supported cases cannot reconstruct valid analytic STEP B-reps within the RCS-005 budgets;
- common lathe insert/nose-radius envelopes cannot be represented robustly in the 2D domain;
- provider handoff/reconciliation dominates interactive use or causes unacceptable identity churn;
- batched 3D subtraction provides equivalent robustness with substantially lower architectural complexity;
- realistic turning commonly violates the assumed axisymmetric material domain in the initial product scope.
