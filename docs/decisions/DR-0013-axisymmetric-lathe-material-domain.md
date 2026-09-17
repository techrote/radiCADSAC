# DR-0013 — Axisymmetric material domain as a first-class lathe provider

Status: accepted  
Date: 2026-09-17  
Decision scope: fixed-axis turning solver architecture

## Context

The initial programme scope includes a lathe and must tolerate exact retraces, repeated finishing, very small removals and gamepad/analogue-control trajectories without requiring one fragile 3D Boolean per journal sample. RCS-009 accepted regularized volumetric material semantics and bounded deferred topology, while leaving process-specific domains to RCS-010/RCS-011.

Fixed-axis turning has unusually strong rotational symmetry. RCS-010 compared an axial/radial material representation with both repeated and batched conventional 3D subtraction on the exact pinned OCCT baseline and through the accepted STEP gates.

## Decision

1. OpenSimachinist should treat a verified axisymmetric axial/radial material domain as a **first-class process provider** for the supported fixed-axis lathe subset.
2. The provider is not the programme's universal geometry kernel. It must expose explicit support/refusal criteria and reconcile/handoff when symmetry or supported tool-envelope semantics cease to hold.
3. The canonical manufacturing journal remains durable authority. The 2D material state is derived/rebuildable backend state.
4. Exact retrace/repeated-pass journal events remain preserved. Geometry recomputation may be elided only when operation semantics plus RCS-008 lineage prove the removal envelope/material effect equivalent.
5. Positive-volume removal is never suppressed by a broad fuzzy tolerance. RCS-007 tolerance/uncertainty channels remain separate.
6. Conventional validated B-rep reconciliation is mandatory for primary STEP export and general/non-axisymmetric provider handoff.
7. Reconciled faces/edges are regenerated implementation details; semantic lineage and material-body identity cross provider boundaries instead of `TopoDS_*` identity.
8. Batched 3D removal remains a fallback/comparison strategy where an operation is axisymmetric in intent but the specialized envelope implementation is not yet qualified.
9. Tool-envelope generation for real insert/nose-radius/orientation semantics is a required production subsystem and is not considered solved by the founding profile prototype.

The accepted founding subset is cylindrical OD turning, facing, shoulders, linear taper/chamfer-class boundaries, cylindrical through/blind boring, exact/repeated finishing, and bounded canonicalized analogue-controlled variants whose material/removal envelope remains rotationally symmetric about one declared spindle axis.

## Alternatives considered

### One 3D Boolean per canonical event

Retained as a baseline/general fallback but rejected as the preferred architecture for the verified axisymmetric domain. The 100-event retrace remained physically identical while requiring 100 repeated material Booleans in the comparison path.

### Batched 3D cutter-envelope subtraction only

Retained as a serious fallback. In the hosted campaign it was correct and far cheaper than repeated 3D replay, but the axisymmetric provider also supplied a compact process-native material state, direct provenance/no-op semantics, analytic reconstruction and lower measured reconstruction cost for the founding set.

### Axisymmetric domain as the entire kernel

Rejected. Milling, live tooling, eccentric features and general freehand motion are outside the representation's natural closure. The provider must hand off rather than approximate them.

### Tessellated/mesh revolution as the lathe result

Rejected for the primary engineering path. The programme requires conventional usable STEP and preservation of analytic cylinders/cones/planes where intended geometry is analytic.

## Evidence

Accepted prior evidence:

- RCS-002 defines canonical manufacturing intent independently of geometry backend.
- RCS-003 classifies repeated finishing, facing, ID/OD retrace, shoulder/tangency, analogue noise and long histories as normal lathe inputs.
- RCS-006 supplies pinned OCCT geometry/STEP measurement infrastructure.
- RCS-007 rejects one broad global fuzzy tolerance as material semantics.
- RCS-008 permits topology regeneration while preserving semantic lineage and provides the proof model for exact-retrace geometry elision.
- RCS-009 accepts regularized volumetric semantics and bounded deferred topology with reconciliation at export/provider boundaries.

**Measured RCS-010 evidence:** workflow run `35214872300`, job `105180888767`, artifact `10493944652`, digest `sha256:7a2511d30fbcdf4dc04b9e8a969b2a3387a84d90226d1f2784249899ca81096c`, exact OCCT commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`.

Nine founding cases completed with zero acceptance failures. All three strategies produced valid one-body material results agreeing within the geometry budgets. All 21 enabled STEP strategy round-trips passed. Axisymmetric reconstruction preserved expected planes/cylinders plus a true conical taper and introduced no B-spline surfaces.

The campaign represented 135 journal events, including nine raw analogue samples, while measuring 127 repeated-3D material Booleans, 9 batched-3D Booleans and 0 material Booleans for the direct axisymmetric path prior to reconciliation. The 100-event exact retrace preserved all journal events and identified 99 material no-ops. Aggregate conceptual runtimes on the hosted run were approximately 858.86 ms repeated, 63.74 ms batched and 10.20 ms axisymmetric. These timing numbers are comparative research evidence, not production guarantees.

The blind-bore reconstruction used six faces while conventional 3D results used five despite equivalent valid material and STEP, reinforcing that RCS-008 semantic identity must survive topology regeneration rather than relying on face-count/topology identity.

Durable measurements are pinned in `research/rcs-010/measured-summary-v1.json`.

## Consequences

- RCS-013 should architect solver dispatch around manufacturing/process domains rather than one universal Boolean engine.
- Initial lathe implementation can prioritize OD/facing/shoulder/taper/boring vertical slices while explicitly delegating non-axisymmetric operations.
- The stable MSAC boundary does not change; machine/process semantics cross the boundary, not 2D profile internals.
- Export and lathe→mill handoff are explicit reconciliation checkpoints.
- Preview/inspection APIs need to distinguish material-domain queries from topology-dependent queries that force reconciliation.
- Tool-envelope qualification becomes a concrete implementation/research item rather than being buried inside general Boolean replay.
- Parting/grooving/undercut connectivity remains outside this accepted subset until separately qualified.

## Reversibility

High before production persistence commits to provider-private state. Because the journal and programme-facing identities remain implementation-independent, the axisymmetric provider can be narrowed, replaced or bypassed without changing saved manufacturing intent.

## Reconsideration triggers

Reconsider or narrow this decision if later evidence shows that:

- common lathe insert/nose-radius envelopes cannot be represented robustly in the 2D domain;
- provider handoff/reconciliation dominates interactive use or causes unacceptable identity churn;
- realistic turning commonly violates the assumed axisymmetric material domain in the initial product scope;
- production-scale histories eliminate the measured practical advantage;
- new STEP/downstream constraints cannot be met by the reconciled analytic result.
