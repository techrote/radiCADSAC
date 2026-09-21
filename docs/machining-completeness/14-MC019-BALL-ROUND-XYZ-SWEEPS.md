# MC-019 ball/round simultaneous-XYZ sweep construction

Status: **MC-019 completed bounded deterministic research; programme-wide sweep and completeness obligations remain open.** The machine-readable contract is `research/machining-completeness/tasks/MC-019/ball-round-sweep-contract-v1.json`.

## Scope

MC-019 covers the admitted fixed-axis `mill_ball_round` cutter family. It closes the historical constant-Z rounded construction gap for exact stationary/line/polyline motion and provides a conservative MC-058 interface for admitted nonlinear source motion. It does not cover form/nonconvex/undercut cutters (MC-020), lathe process semantics (MC-021/022), or multi-setup composition (MC-023).

The cutter has radius `R>0` and finite axial length `L>=R`. In cutter-local coordinates its lower nose is `0<=z<=R`, `rho^2+(z-R)^2<=R^2`; its upper region is `R<=z<=L`, `rho^2<=R^2`. This is the `c=R` rounded limit deliberately excluded from MC-018. Neither a full sphere detached from finite shaft semantics nor a radius-`R` flat cylinder is an acceptable substitute.

## Exact stationary/line/polyline construction

Each saved source leaf remains immutable and bound to its exact closed engagement interval. For the upper cylinder, the source parameter is intersected with the exact local axial slab and exact quadratic XY distance is minimized. For the lower nose, the same source parameter is intersected with local `z in [0,R]` and exact 3-D squared distance to the moving sphere centre is minimized. All authority scalars are exact rationals; binary floating point and a global epsilon are rejected as correctness authority.

The construction handles simultaneous X/Y/Z translation directly. A varying-Z path cannot be flattened to constant Z, and a retrace can be geometrically idempotent without being deleted from source history. Engaged teleportation is invalid.

## Independent F03 witness

The implementation does not import MC-011 geometry. The verifier separately pins and loads MC-011's exact-rational F03 spherical-polyline witness. For tip path `(0,0,0)->(2,0,-2)`, the probe `(1/3,1/3,-2/3)` is an exact lower-nose tangent: at `t=1/2` the sphere-centre residual is `(-2/3,1/3,-2/3)`, whose squared norm is `1` and whose dot product with motion `(2,0,-2)` is `0`. `y=3/10` is the inside signed neighbour and `y=2/5` is outside. MC-019 and the independent F03 oracle agree on all three, while the deliberately flattened tip path `(0,0,0)->(2,0,0)` rejects the tangent.

Stationary nose tangency, finite tip/top neighbours and a point accepted by the enclosing flat cylinder but rejected by the real rounded nose provide additional boundary controls.

## MC-058 nonlinear source leaves

Circular-arc, helical, spline, piecewise and timed/phase motion is consumed only as finite source-bound line leaves carrying certified Euclidean translation error `e`. The complete cutter is enclosed by line-swept cylinders of radius `R+e` and axial interval `[-e,L+e]`.

For a guaranteed inner witness, the real cutter contains a radius-`R/2` cylinder over `z in [R/2,L]`; eroding by `e` yields radius `R/2-e` and axial interval `[R/2+e,L-e]` when nonempty. Classification is therefore only `INSIDE`, `OUTSIDE` or `UNCERTIFIED`. A zero numerical leaf error does not turn a nonlinear source class into an exact line, and an uncertainty shell does not become a topology or exact-zero decision.

## Proof and programme boundary

MC-019 is deterministic construction/model evidence. No native or paid campaign ran. **PO-02, PO-04, PO-05 and PO-06 remain OPEN. MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.** Protected historical `research/rcs-*` source/audio/provenance evidence, canonical journal semantics, positive-volume material rules and durable body/lineage semantics are unchanged.
