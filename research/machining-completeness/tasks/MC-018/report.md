# MC-018 — Actual flat/corner-radius milling sweep construction

Status: **COMPLETED_RESEARCH** for the fixed-axis flat/corner-radius milling slice, with programme-wide proof and realization obligations left open. Issue: #80. Source baseline: `b85b8081dd83ca35f81e6e1a9495bd5f88589ee0`.

## Purpose and disposition

MC-018 replaces a centreline-only or infinitely extruded interpretation of ordinary flat and corner-radius end milling with an executable finite-cutter construction. The task is deliberately source-bound: it consumes the accepted MC-A fixed-axis milling domain, the independent MC-010 exact-control foundation, and the MC-058 curve/transform/sweep-enclosure contract. It does not reinterpret old journal operations, change the admitted denominator, run native geometry, or claim that one task closes the programme-wide sweep/topology/output proof.

The result has two layers. Stationary, line and polyline translations are decided with exact rational arithmetic. Other admitted fixed-axis source curves consume finite MC-058-derived line leaves carrying a certified translation enclosure; the constructor then returns a sound `INSIDE` / `OUTSIDE` / `UNCERTIFIED` sweep sandwich. `UNCERTIFIED` is retained rather than converted into a guessed equality or a pass.

No native or paid geometry campaign was run.

## Cutter constructions

### Flat end mill

The finite effective cutting solid is

```text
x^2 + y^2 <= R^2
0 <= z <= L
```

with exact positive rational radius `R` and finite axial length `L`. For a source line `P(t)=P0+t(P1-P0)`, `t in [0,1]`, point membership in the sweep is reduced exactly to:

1. intersect `[0,1]` with the closed interval where the point lies inside the translated cutter's axial slab; and
2. minimize the exact quadratic XY distance to the translated cutter axis over that closed rational interval.

This handles simultaneous XYZ motion directly. There is no constant-Z assumption and no centreline-only acceptance rule.

### Corner-radius end mill

Let outer radius be `R`, corner radius `c`, finite axial length `L`, and core radius `a=R-c`, with `0<c<R` and `c<=L`. The lower rounded cutting profile is the exact toroidal-profile disk implied by

```text
(rho-a)^2 + (z-c)^2 <= c^2
```

for `rho>=a`, together with the central `rho<=a` region; the upper portion `c<=z<=L` is the full radius-`R` cylinder. Ball/round (`c=R`) remains owned by MC-019 rather than being silently folded into this task.

For rational line motion, the lower fillet existential condition is reduced to an exact univariate semialgebraic predicate. The implementation uses rational polynomial arithmetic, square-free reduction and Sturm isolation; it does not sample, apply a global epsilon, decimalize a tangent, or replace the corner cutter with its enclosing flat cylinder.

## Source-path semantics

`fixed_axis_sweep.py` retains finite ordered leaves rather than canonicalizing the source journal away. Exact stationary, line and polyline paths are supported; reversals and exact retraces remain explicit source pieces even though the swept-set union is idempotent. Consecutive engaged leaves must meet exactly. An engaged teleport is rejected.

Each leaf also carries its exact source interval and an engagement binding. Those fields are part of the evidence route: a derived geometric segment without its source/engagement association is insufficient authority.

Within MC-018 the cutter axis is fixed by the accepted domain, so rotational pose error is exactly zero for one milling operation. This is a property of this slice, not permission to drop `rho*e_rotation` for a later rotating/reoriented cutter. Reorientation remains an explicit setup transition.

## MC-058 bounded nonlinear-leaf route

For circular-arc, helical, spline, piecewise and timed/phase source motion, MC-018 consumes a finite MC-058-derived line leaf with certified Euclidean translation enclosure `e`, bound to the same exact source interval and semantic boundaries. Time/path/phase correlation is therefore inherited rather than factored into unrelated coverage.

For either cutter family, the true sweep is conservatively contained in the union of segment cylinders with radial extent `R+e` and axial range `[-e,L+e]`. A conservative definitely-inside subset is obtained from the cutter's central cylinder, shrunk by `e` radially and axially: radius `core_radius-e`, axial range `[e,L-e]`, when nonempty. For a flat cutter `core_radius=R`; for a corner-radius cutter `core_radius=R-c`.

This gives three truthful outcomes:

- `INSIDE` when an exact leaf hits or a certified inner witness exists;
- `OUTSIDE` when no certified outer envelope can reach the point; and
- `UNCERTIFIED` in the remaining shell.

The shell is not a solver failure to hide. Later refinement or an exact event route may reduce it; until then it cannot establish an exact-zero/topology claim.

## Exact and adversarial controls

The deterministic verifier exercises the task without candidate code or native geometry:

- a flat `R=1`, `L=2` cutter on `(0,0,0)->(2,0,2)` has exact tangent point `(1,1,2)`, with signed radial neighbours `99/100` inside and `101/100` outside;
- a corner-radius `R=2`, `c=1`, `L=4` stationary cutter uses the rational 4/5–3/5 profile point `(rho,z)=(9/5,2/5)` as exact fillet equality, plus signed `179/100` and `181/100` neighbours;
- the same rounded boundary witness is transported through simultaneous XYZ motion at `t=1/2`, proving that corner-radius support is not a constant-Z shortcut;
- a forward/reverse retrace remains two journal leaves while producing the same sampled swept-set membership as the forward leaf alone;
- discontinuous engaged leaves are rejected as teleportation;
- a nonlinear derived leaf with no engagement binding is rejected;
- an MC-058 leaf with `e=1/10` demonstrates definite inside, definite outside and an unresolved shell; and
- a point inside the corner cutter's enclosing radius-`R` cylinder but outside its actual lower fillet is rejected, catching flat-cylinder substitution.

The contract mutation suite also rejects binary-float authority, deletion of retraces, loss of varying-Z support, removal of `UNCERTIFIED`, promotion of the bounded sandwich to topology authority, dependency drift and premature MC-B acceptance.

## Evidence class and limitations

This is deterministic construction/model evidence, not native CAD-kernel evidence. It establishes an executable, source-faithful construction for the MC-018 cutter slice and a sound MC-058-derived enclosure interface for the remaining admitted fixed-axis path classes. It does not establish the programme-wide statement that every material/topology query can already be decided exactly and finitely.

Accordingly:

- **PO-02 remains OPEN.** MC-018 contributes the fixed-axis flat/corner-radius milling slice; MC-019–MC-023 and later integration remain required.
- **PO-04 remains OPEN.** Exact/validated material/event classification, including singular/equality cases outside this task's exact slice, remains downstream.
- **PO-05 remains OPEN.** This task does not discharge inherited transcendental event/termination blockers.
- **PO-06 remains OPEN.** The sweep sandwich is one error-transfer component, not the complete source-to-engineering-output certificate chain.
- **MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.**

No protected `research/rcs-*` history, source/audio/provenance evidence, canonical journal semantics, positive-volume rules, or durable body/lineage records are modified by MC-018.

## Verification

```text
python3 research/machining-completeness/tasks/MC-018/verify.py --contract
python3 research/machining-completeness/tasks/MC-018/verify.py --self-test
python3 tools/mc_workflow.py verify MC-018
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

## Downstream use

MC-019–MC-023 may reuse the source-binding and fail-closed sweep interface but must implement their own cutter/process semantics rather than relabeling MC-018 as universal coverage. MC-031/MC-038 may consume this evidence when integrating PO-02/MC-B, while retaining every other open proof, topology, output and resource obligation.
