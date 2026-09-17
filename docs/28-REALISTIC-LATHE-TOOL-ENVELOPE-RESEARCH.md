# Realistic lathe tool-envelope derivation research

Status: RCS-020 candidate report pending hosted measured evidence  
Date: 2026-09-17  
Issue: RCS-020 / #39

## Purpose

RCS-020 closes the most important qualification gap left by RCS-010. The accepted axisymmetric lathe material-domain experiment showed that a completed 2D `(z,r)` material boundary can outperform repeated general 3D cutter subtraction and reconcile to conventional B-rep/STEP. It did **not** show how a realistic insert/tool and canonical machine motion become that boundary.

This campaign therefore begins with explicit tool geometry and pose/path semantics rather than target radii or finished profiles.

## Hypotheses

### H1 — real radiused-tool motion can feed the specialized provider

For a bounded fixed-axis subset, the swept material envelope of a circular insert nose plus explicit canonical tool-centre motion can be reduced into the RCS-010 axial/radial material domain within a declared construction budget.

Falsification: the independently calculated material oracle disagrees beyond budget, or the resulting conventional B-rep/STEP comparison violates the accepted geometry/body gates.

### H2 — tool approach and holder reachability belong in the capability predicate

A rotationally symmetric target shape is not sufficient proof that the specialized provider may execute an operation. Tool/holder approach geometry may make a nominal undercut unreachable without collision.

Falsification: no tested reachability condition changes the safe supported/refused boundary, or the proposed collision test cannot distinguish an intentionally unreachable case.

### H3 — grooving/parting can preserve explicit connectivity semantics

A bounded groove/parting tool model with cutting width and rounded corners can represent a partial groove and a complete parting event without losing the second disconnected body.

Falsification: complete cut-through is collapsed back to one body, one body is dropped in STEP control, or corner-radius material differs from its independent oracle outside budget.

## Tool-model source basis

The research values are representative rather than catalogue-locked.

Primary manufacturer material recorded in `research/rcs-020/experiment-plan-v1.json` supplies evidence that:

- external turning practice uses geometry-critical entering/approach angle and insert nose radius;
- a representative Sandvik training setup uses 95° entering angle with a CNMG-class insert and 0.8 mm nose radius;
- current parting/grooving products specify cutting width and left/right corner radii.

The experiment uses these values to define immutable abstract tools. Product identity is not part of programme semantics.

## Experiment design

### Circular-nose generator

For OD, shoulder, taper, retrace and boring cases, the candidate generator forms the Minkowski sum of each canonical tool-centre segment with a circular nose. Circular caps are polygonized under an explicit chord-error limit; vertical intersections of that candidate envelope then produce the derived radial material boundary.

### Independent oracle

The oracle does not reuse the polygon generator. It independently solves exact vertical intersections of the segment-plus-disc capsule from endpoint-circle and parallel-offset-line geometry, then integrates the resulting material state at a substantially finer step with a coarse/fine convergence check.

The candidate therefore cannot pass simply because it compares with itself.

### Facing

Facing is explicitly represented rather than inferred from an OD fixture. A radial sweep of the radiused nose must cover from spindle axis through the stock OD. The new front plane is derived from the minimum axial support of that nose sweep. Its conventional B-rep reconstruction is then compared through RCS-010.

### Grooving and parting

The groove model uses explicit cutting width plus left/right corner radius. The candidate constructs rounded groove corners; a separately coded analytic radius function provides the material-volume oracle.

Complete parting has a finite zero-material axial interval and therefore two disconnected material bodies. Because the single-profile RCS-010 worker is a one-body reconstruction comparator, RCS-020 uses the already qualified RCS-006 parting case solely as a conventional multi-solid/STEP connectivity control. That control is not misrepresented as proof that a rectangular slot is geometrically equivalent to the rounded groove envelope.

### Reachability

A deliberately stepped undercut case evaluates a conservative holder ray after a defined insert-to-holder setback. Collision with material causes `refused_unsupported`; the experiment does not alter the target profile or widen tolerance to make the operation executable.

## Required cases

The machine-readable plan covers:

- OD turning with R0.8 nose at 95° approach;
- facing from the same radiused external tool;
- shoulder creation;
- a taper path under a second 45° approach configuration;
- 20-event exact retrace/finishing history;
- R0.4 through boring;
- R0.4 blind boring;
- partial R0.2-corner groove;
- full parting producing two bodies;
- holder-collision undercut refusal.

## Measurements

The hosted campaign records:

- tool and canonical trajectory used to derive each envelope;
- candidate profile point count and construction tolerance;
- independently integrated material volume and convergence delta;
- candidate/oracle material-volume error;
- holder reachability result where applicable;
- OCCT 8.0.1 repeated-3D, batched-3D and axisymmetric reconstruction metrics;
- B-rep validity, body count, volume and bounds;
- STEP Layer A-C fresh-readback results for qualified one-body cases;
- multi-body STEP connectivity for complete parting;
- material Boolean counts for exact retrace.

## Capability interpretation

RCS-020 distinguishes four outcomes:

1. **qualified exact/bounded material semantics** — tool-derived envelope and independent oracle agree, provider reconstruction is valid, and applicable STEP automated gates pass;
2. **bounded material capability with analytic-surface qualification still open** — material is demonstrated but the research adapter discretizes a boundary whose exact analytic reconstruction has not been proven;
3. **provider handoff required** — the manufacturing semantics remain valid but fall outside this specialized provider's demonstrated representation/reachability domain;
4. **refused unsupported** — no safe specialized-provider execution exists under the tested tool/setup semantics.

The expected holder-collision undercut belongs to category 4 and is a positive safety result, not an experiment failure.

## STEP boundary

The RCS-010 comparator revolves a polygonized radial profile. A successful read-back therefore demonstrates material/body/engineering geometry fidelity within RCS-005 automated budgets, but it does not automatically demonstrate that a circular insert nose has been reconstructed into an exact toroidal/other analytic surface class.

RCS-020 explicitly records `analytic_nose_surface_exactly_qualified = false` for that adapter. Gate 5 may retain this as a bounded reconstruction question or later evidence may qualify a provenance-assisted exact reconstruction path. The campaign will not obscure that distinction.

## Implications for MSAC

MSAC may continue to emit physical tool geometry revisions, frames/orientation and canonical trajectories rather than target CAD profiles. A tool change or orientation change remains semantic input, even when two motions happen to produce similar final material.

Unsafe tool reachability must surface as an explicit backend capability/refusal status rather than being converted into a hidden geometry approximation.

## Implications for OpenSimachinist

If measured evidence passes, the RCS-010 provider remains first-class but with a refined entry predicate: fixed-axis rotational material semantics plus a qualified tool-envelope/reachability model. The private 2D material representation remains replaceable; neither commercial insert IDs nor OCCT topology become programme identity.

## Unresolved questions

Before measured evidence is frozen, the following remain OPEN:

- exact quantitative material/oracle deviations for the hosted campaign;
- whether every polygonized profile remains robust through repeated/batched OCCT comparison;
- exact nose-radius analytic surface reconstruction in conventional STEP;
- broader holder/fixture interference beyond the deliberately bounded reachability model;
- general undercut tooling and complex form tools;
- live-tool/eccentric/non-axisymmetric operations, which remain outside this provider by design.

The final RCS-020 report must replace candidate language with measured evidence and narrow the capability matrix if any required case falsifies the hypotheses.
