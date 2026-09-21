# MC-019 — Actual rounded/ball simultaneous-XYZ milling sweeps

## Disposition

`COMPLETED_RESEARCH` for bounded deterministic sweep construction and independent-control agreement only. MC-019 implements a finite fixed-axis ball/round cutter slice over exact stationary/line/polyline motion and a fail-closed MC-058 nonlinear-leaf interface. It does **not** establish native-kernel geometry, topology, engineering-output qualification, MC-B, or MC-1.

Base: `dfda6423da5ae5d779b143e07c0ffe18c0925cd0` (MC-018 merged).

## Hypothesis and falsification criterion

Hypothesis: the MC-A `mill_ball_round` constructor can preserve its complete finite cutting region over simultaneous XYZ motion without the historical constant-Z projection, while exact rational line/polyline cases agree with an independent F03 spherical-sweep witness and nonlinear source motion remains conservatively bounded through MC-058.

Falsify the task if the construction projects varying-Z motion to a plane, replaces the rounded nose by a full flat cylinder, uses centreline-only/infinite cutter geometry, deletes source retraces, loses engagement/source binding, imports candidate geometry into the independent oracle, or turns an MC-058 uncertainty shell into exact membership/topology truth.

## Cutter and exact construction

For cutter radius `R>0` and finite axial length `L>=R`, local cutter coordinates use the lower ball nose

`0 <= z <= R` and `rho^2 + (z-R)^2 <= R^2`,

plus the finite cylindrical upper region

`R <= z <= L` and `rho^2 <= R^2`.

This is the `c=R` rounded limit intentionally excluded from the MC-018 corner-radius constructor; it is not a zero-length sphere and not an infinite cylinder. Orientation is fixed within an admitted milling operation, so the exact line/polyline construction translates the complete cutter without suppressing Z motion.

For each exact rational line leaf, the upper cylinder is decided by intersecting the source parameter with the exact axial slab and minimizing the XY distance quadratic. The lower nose is decided by intersecting the same source parameter with local `z in [0,R]` and minimizing exact 3-D squared distance to the moving sphere centre `p(t)+(0,0,R)`. Stationary leaves are the zero-length line case. No binary floating point or global epsilon participates in equality decisions.

## Independent varying-Z control

MC-011's prospective F03 oracle is pinned as an independent control, not imported by the MC-019 implementation. The MC-019 verifier separately loads the pinned exact-rational `ball_polyline_sweep_removes` oracle and compares it against the new constructor.

The decisive control uses a tip path from `(0,0,0)` to `(2,0,-2)`, so X and Z change simultaneously. At `t=1/2`, the sphere centre is `(1,0,0)`. The probe `(1/3,1/3,-2/3)` has centre residual `(-2/3,1/3,-2/3)`, exact squared norm `1`, and zero dot product with motion `(2,0,-2)`. It is therefore a true lower-nose tangent, not merely a path endpoint or seam coincidence. The `y=3/10` neighbour is inside and `y=2/5` is outside. Both MC-019 and the independently pinned MC-011 oracle agree on all three. Replacing the actual Z-varying path by `(0,0,0)->(2,0,0)` rejects the tangent, directly detecting the historical constant-Z corruption.

Stationary lower-nose tangency, tip/below-tip and top/above-top controls additionally bind finite axial extent. A point accepted by the enclosing flat cylinder but rejected by the rounded nose detects cylinder substitution.

## MC-058-derived nonlinear slice

Circular-arc, helical, spline, piecewise and timed/phase source motion is consumed only through finite source-bound MC-058 line leaves with certified Euclidean translation enclosure `e`. Missing engagement/source binding is rejected. A nonlinear source does not become an exact line merely because its supplied translation error is zero.

The complete cutter is contained by the line-swept cylinder of radius `R+e` and axial interval `[-e,L+e]`. For a sound inner witness, the exact cutter contains the cylinder of radius `R/2` over `z in [R/2,L]`; eroding that cylinder by `e` gives radius `R/2-e` and axial interval `[R/2+e,L-e]` when nonempty. Thus bounded leaves return only `INSIDE`, `OUTSIDE` or `UNCERTIFIED`. The unresolved shell is not promoted into equality, topology, or a capability pass.

## Boundary and adversarial evidence

The deterministic verifier covers:

- exact lower-nose tangency with signed neighbours;
- simultaneous XYZ lower-nose tangency checked against the independent MC-011 F03 oracle;
- explicit constant-Z flattening corruption;
- finite tip/top boundaries and signed axial neighbours;
- a flat-cylinder substitution counterexample;
- retrace idempotence while preserving both source leaves;
- engaged-teleport rejection;
- unbound/unknown nonlinear-source rejection;
- zero-error nonlinear-source refusal on the exact-line path;
- bounded-leaf `INSIDE`/`OUTSIDE`/`UNCERTIFIED` controls, including a large-error uncertainty case;
- contract mutations for binary-float authority, constant-Z projection, varying-Z loss, oracle/dependency drift, topology promotion and premature MC-B acceptance.

## Proof and capability boundary

**PO-02 remains OPEN:** MC-019 contributes only the ball/round fixed-axis milling slice; form/undercut, lathe and multi-setup constructors remain downstream. **PO-04 remains OPEN:** this task does not establish universal material/event classification. **PO-05 remains OPEN:** inherited transcendental equality and finite-progress obligations are not discharged. **PO-06 remains OPEN:** the MC-058 sweep sandwich is only one part of the complete source-to-engineering-output error chain.

No native or paid campaign ran. **MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.** Historical `research/rcs-*` evidence, source/audio/provenance, canonical-journal semantics, positive-volume rules and durable body/lineage semantics are unchanged.

## Downstream routing

MC-027/028/029 and later integration may consume the reviewed ball/round sweep artifact subject to their own dependencies and proof obligations. The next MG-04 package-order task is MC-020, which must address admitted form/nonconvex/accessible-undercut cutters without treating this ball/round result as a general cutter proof.
