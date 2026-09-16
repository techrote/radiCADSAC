# Foundation audit and Gate-1 reconciliation

Status: accepted RCS-001 foundation audit  
Date: 2026-09-16  
Issue: RCS-001

## Purpose

This document audits the complete founding corpus created before RCS-001, reconciles ambiguities, separates fixed programme invariants from research hypotheses, and defines an executable Gate-1 boundary.

The audit covers:

- `README.md`;
- `AGENTS.md`;
- `docs/00-FOUNDING-BRIEF.md`;
- `docs/01-MSAC-GEOMETRY-CONTRACT.md`;
- `docs/02-INITIAL-RESEARCH-PLAN.md`;
- `docs/03-PLAN-REVIEW.md`;
- `docs/04-REVISED-RESEARCH-ROADMAP.md`;
- `docs/05-SOURCE-BASELINE.md`;
- `docs/06-RESEARCH-METHOD.md`;
- `docs/07-RESEARCH-ISSUE-GRAPH.md`;
- GitHub issue #1 / RCS-001.

The historical initial plan remains intentionally preserved. Where it differs from current planning, `04-REVISED-RESEARCH-ROADMAP.md` is authoritative.

## Executive result

The founding corpus is directionally consistent, but RCS-001 found four material ambiguities/contradictions that had to be resolved before parallel research begins:

1. **Gate-1 depended on outputs from issues that were themselves scheduled after Gate-1.**
2. **`authoritative geometry` could be misread as contradicting journal-driven replay.**
3. **`machine module` mixed frontend/process responsibilities with backend exact-solver ownership.**
4. **units/coordinate conventions and disconnected-body semantics were not explicit enough for RCS-002/RCS-003/RCS-005.**

The first three are resolved by this issue and accompanying document changes. The fourth is made an explicit required question in the existing downstream issues rather than hidden as an assumption.

No contradiction was found with the core product proposition: MSAC remains a simulation-aided engineering creation tool whose initial manufacturing interfaces are a lathe and mill and whose primary engineering output is usable STEP.

## Fixed programme invariants

The following are **accepted programme invariants**, not hypotheses to be re-proven by every issue.

### Product purpose

- The primary product is useful engineering geometry, not a machining game.
- Simulated manufacturing action is the user-facing modelling interface.
- The project must not collapse into conventional sketch/extrude/feature-tree CAD merely because that would be easier to implement.
- A later game/publication layer is subordinate to proving a productive engineering core loop.

### Initial user and process scope

- The initial hypothetical external tester is an experienced machinist with substantial console-game fluency.
- Initial machine/process families are **lathe and mill only**.
- Later machine/additive processes must remain architecturally possible but are not founding implementation obligations.

### Interaction/realism doctrine

- Machine simulation should improve intuition, control, feedback, or spectacle rather than impose busywork.
- Geometry-critical state must be trustworthy enough for engineering output.
- Chatter, dirt, wear, sparks, crashes, and similar phenomena may be cosmetic/approximate unless later engineering value justifies more fidelity.
- Undo/redo and recoverability are first-class; dramatic failure is not a justification for permanently destroying user work.

### Output doctrine

- **STEP is the mandatory primary engineering output.**
- STL/tessellations are derived convenience outputs and not an architectural fallback.
- A triangulated surrogate inside a STEP container does not satisfy the programme by default.
- Export failure must be explicit; the system may not silently claim successful engineering output when conformance is not met.

### Workload doctrine

The following are normal manufacturing input and may not simply be prohibited to protect a geometry kernel:

- coincidence/near coincidence;
- tangency;
- zero-thickness contact events;
- repeated/retraced passes;
- sub-tolerance movement;
- sliver formation;
- self-crossing and jittery trajectories;
- overlapping cutter envelopes;
- very large operation counts.

### Durable-state doctrine

- Canonical manufacturing intent/history must survive replacement of a geometry backend.
- Saved project meaning may not depend on OCCT/private kernel objects.
- Raw render meshes and preview geometry are not authoritative engineering sources.
- Backend snapshots/caches may accelerate work but are disposable derived artifacts.
- The canonical operation journal is the durable source of manufacturing intent, subject to versioned replay compatibility.

### Backend-boundary doctrine

- MSAC and OpenSimachinist communicate through implementation-independent manufacturing/geometry contracts.
- OCCT-specific types are prohibited from the stable programme-level boundary.
- Manufacturing/process semantics must cross the boundary; operations must not be prematurely reduced to anonymous `A - B` operands.
- Exact solver implementations belong behind the backend boundary even when specialized by process.

### Research doctrine

- OCCT 8.0.1 is the pinned baseline for current research, not a predetermined final architecture.
- Competing representations/algorithms must be evaluated with shared fixtures and measurable conformance criteria.
- Negative results are programme assets.
- The genesis repo preserves research archaeology; clean production repositories are created later from fresh handoffs.

## Research hypotheses — not fixed architecture

The following remain **proposals/hypotheses** and must not be treated as settled because they appear repeatedly in planning documents.

### H1 — multidimensional / virtual tolerance model

Separating numerical uncertainty, manufacturing tolerance, topological equivalence, contact classification, export tolerance, and other policy channels may be more robust than one propagated epsilon.

Open questions include the algebraic properties, locality, conflict rules, accumulation, and export-collapse semantics.

Research owner: RCS-007.

### H2 — semantic provenance improves robustness

Manufacturing ancestry may help distinguish intentional retracing/coincidence from accidental numerical proximity and may improve stable topological identity.

Research owner: RCS-008.

### H3 — regularized/deferred topology

Operating on volumetric material semantics and delaying fragile lower-dimensional topology may reduce failure under tangency/coincidence.

Research owner: RCS-009.

### H4 — process-specific lathe reduction

Common fixed-axis turning may be better represented in a 2D radius/axial material domain followed by exact reconstruction/revolution than by repeated 3D cutter subtraction.

Research owner: RCS-010.

### H5 — milling should use a strategy hierarchy

Milling may benefit from analytic operations where semantics are explicit, then bounded sweeps/batches, then general/hybrid fallbacks rather than one universal cutter-sweep algorithm.

Research owner: RCS-011.

### H6 — hybrid/non-B-rep intermediate representations

Implicit, cell, mesh, exact-predicate, CSG, or other representations may provide robust local or general escape routes if they can reconcile to valid STEP without unacceptable geometric loss.

Research owner: RCS-012.

### H7 — deep OCCT fork

A radical OCCT-derived kernel may prove to be the best OpenSimachinist architecture.

This remains only one candidate. RCS-004 audits forkability and RCS-012 compares alternatives; RCS-013 selects the initial architecture from evidence.

## Reconciliation finding A — Gate-1 circular dependency

### Previous state

`04-REVISED-RESEARCH-ROADMAP.md` originally required Gate 1 to contain:

- an initial journal schema direction;
- an initial adversarial fixture format.

However:

- RCS-002, which defines the journal/schema direction, depends on RCS-001;
- RCS-003, which defines the fixture format, depends on RCS-001;
- the issue graph says RCS-002 through RCS-005 start **after RCS-001**.

That made Gate 1 circular: Gate 1 required outputs from work intended to begin only after Gate 1.

### Resolution

Gate 1 is now the **research-foundation-ready gate** completed by RCS-001.

It requires:

- stable-enough programme vocabulary;
- reconciled/versioned founding geometry contract;
- fixed-invariant versus hypothesis separation;
- research/evidence method;
- research issue/dependency graph;
- pinned OCCT baseline version/commit;
- explicit downstream ownership of unresolved foundation questions.

After Gate 1:

- RCS-002 / Track A can define the journal;
- RCS-003 / Track C can define the fixture format;
- RCS-004 / Track B can audit OCCT;
- RCS-005 / Track G can define STEP conformance.

RCS-006 then creates the shared baseline harness. The deeper RCS-007 through RCS-012 campaigns start only when their declared issue dependencies are met.

This preserves parallelism without pretending downstream deliverables already exist.

## Reconciliation finding B — authority model

### Ambiguity

The corpus used both:

- `authoritative geometry`;
- the claim that the operation journal is more durable than any intermediate B-rep and can regenerate geometry under another backend.

Read literally, these could imply two competing sources of truth.

### Resolution

Authority is separated by concern:

- **manufacturing intent/history:** the canonical operation journal is durable authority;
- **engineering realization at a revision:** a validated committed engineering state is authoritative for the backend result it represents;
- **visual interaction:** preview geometry is disposable and non-authoritative.

A workpiece revision may therefore have multiple derived engineering realizations across backend versions without changing the recorded manufacturing intent.

The term `authoritative geometry` remains acceptable only when this scope is clear. New documents should prefer `committed engineering state` or another explicit conformance level.

## Reconciliation finding C — machine-module/backend ownership

### Ambiguity

`01-MSAC-GEOMETRY-CONTRACT.md` placed `specialized exact solver implementation` inside the machine-module extension list while also stating that OpenSimachinist owns backend geometry.

That could lead to Godot-facing machine modules directly containing or exposing kernel-private solver code and data.

### Resolution

The programme now distinguishes:

- **machine module** — MSAC-side controls, kinematics, process semantics, tool/workholding interaction, raw sampling, canonicalization contributions, preview/experience behaviour;
- **geometry process provider** — OpenSimachinist-side specialized exact/reconciled solver component.

They may be paired by a versioned semantic contract, but exact solver/private kernel ownership remains behind OpenSimachinist.

The exact placement of trajectory canonicalization remains a RCS-002 research question. The fixed rule is that the stable journal/backend boundary is implementation-independent.

## Reconciliation finding D — raw telemetry versus canonical journal

### Finding

The founding brief correctly values replay, but raw controller/frame samples are too implementation-dependent to be the only durable manufacturing history.

### Resolution

The programme distinguishes:

- optional raw telemetry for diagnostics/research;
- canonical versioned operations as durable manufacturing intent.

RCS-002 must define bounded normalization, coordinate/units semantics, replay compatibility, and the relationship between raw traces and canonical operations.

## Reconciliation finding E — exactness language

### Ambiguity

`exact state` can be mistaken for exact arithmetic or mathematically exact constructions.

### Resolution

`Exact` is not a founding requirement for arithmetic representation. The programme requires engineering correctness within explicit conformance/tolerance contracts.

Documents should name the intended state precisely: preview, committed, reconciled, export-conformant, etc. Exact predicates/constructions remain candidate techniques under RCS-012.

## Missing cross-cutting requirement 1 — units, coordinate conventions, and transform semantics

### Finding

The founding corpus refers to dimensions and machine/workpiece transforms but does not yet define a canonical units/handedness/axis serialization contract.

This is material because:

- RCS-002 must serialize trajectories/setups deterministically;
- RCS-003 fixtures must be comparable across implementations;
- RCS-005 must define dimensional STEP conformance and unit transfer.

### Disposition

This is not a new standalone research campaign; it belongs in the already-planned contract work.

RCS-002 must explicitly define:

- canonical dimensional unit representation;
- display-unit independence (metric/imperial UI must not alter stored physical meaning);
- handedness and axis conventions;
- transform composition/order;
- coordinate frame versioning;
- numeric representation/precision expectations at the journal boundary.

RCS-005 must explicitly define how canonical units/tolerances map to STEP and how unit-conversion round trips are tested.

RCS-003 must encode units/frames in fixture metadata.

The relevant issue prompts should be amended by this RCS-001 PR.

## Missing cross-cutting requirement 2 — disconnected bodies, parting, cut-through, and scrap

### Finding

A machining operation can split stock into multiple disconnected volumetric bodies. This can happen intentionally (parting/cutoff) or accidentally (cut-through) even within initial lathe/mill scope.

The founding corpus often says `the workpiece` or `a valid solid` in the singular, leaving unresolved:

- whether all separated bodies remain part of the workpiece state;
- how the clamped/retained body is identified;
- how falling/free scrap is classified;
- how undo/replay preserves body identity;
- whether primary STEP exports one selected part, multiple bodies, or another product structure.

### Disposition

This is a required question across existing research rather than grounds to block Gate 1.

- RCS-002 must provide body identity and split/merge history hooks in the journal model.
- RCS-003 must include at least representative separation/parting fixtures and expected physical intent.
- RCS-005 must define allowed primary export body/product structure and refusal/selection rules.
- RCS-008 later researches durable ancestry through split/merge events.
- RCS-009 later researches regularized connectivity semantics.

The relevant early issue prompts should be amended by this RCS-001 PR.

## Deferred non-blocking foundation questions

The following are real but do not need to block RCS-002 through RCS-005.

### Imported stock scope

The backend contract permits imported stock definitions but no initial import-format requirement is fixed. RCS-005 may research STEP read-back for conformance; production import UX can remain a later product decision unless a research fixture needs it.

### Material-physics metadata

Material identity may matter later for visual/physical simulation, feeds/speeds, additive compatibility, or machining feedback. The initial geometry kernel does not require a high-fidelity constitutive material model to prove geometric creation.

### Fixture collision geometry

Workholding/fixture transforms are geometry-critical context, while collision spectacle and machine damage are MSAC concerns. Exact fixture-subtraction/collision consequences are not required to define the foundational workpiece geometry contract.

### Gamepad mapping

Gamepads are a strong product hypothesis and likely primary control device, but the stable backend contract consumes canonical machine/process actions rather than controller-specific axes. Exact mappings remain MSAC design work.

## Gate 1 — research-foundation ready

Gate 1 is satisfied when all of the following are true on `main`:

1. `docs/08-TERMINOLOGY.md` defines the programme vocabulary required by RCS-002 through RCS-005.
2. `docs/09-FOUNDATION-AUDIT.md` reconciles the founding corpus and identifies downstream open questions.
3. `docs/01-MSAC-GEOMETRY-CONTRACT.md` is marked as the Gate-1 contract version and reflects the authority/module clarifications.
4. `docs/06-RESEARCH-METHOD.md` remains the accepted evidence/decision method.
5. `docs/07-RESEARCH-ISSUE-GRAPH.md` remains consistent with the roadmap and actual GitHub issues.
6. OCCT baseline is pinned to upstream tag `V8.0.1` and commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42` for the start of RCS-004/RCS-006 research. RCS-004 may deliberately select additional comparison commits but must record them.
7. Accepted programme decisions are recorded under `docs/decisions/`.
8. Downstream issue prompts explicitly carry the units/coordinate and disconnected-body requirements rather than relying on chat context.
9. Repository validation and GitHub Actions are green.
10. The RCS-001 PR is merged and merge is verified on `main`.

Gate 1 does **not** claim that the following are already solved:

- final operation-journal schema;
- fixture format;
- STEP conformance profile;
- virtual tolerance model;
- provenance model;
- deferred topology;
- lathe/mill solver algorithms;
- OpenSimachinist architecture.

Those are deliberately downstream research outputs.

## RCS-001 conclusion

The programme can proceed after the above changes without relying on inaccessible founding conversation context.

The foundation is intentionally strong on invariants and deliberately weak on unproven kernel architecture. This is the correct state for parallel research: later issues know what must remain true while retaining freedom to discover how to achieve it.
