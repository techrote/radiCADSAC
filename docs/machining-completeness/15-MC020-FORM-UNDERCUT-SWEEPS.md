# MC-020 form, nonconvex and accessible-undercut sweep construction

Status: **MC-020 completed bounded deterministic research; the universal cutter-source and programme-wide sweep obligations remain open.** The machine-readable contract is `research/machining-completeness/tasks/MC-020/form-undercut-sweep-contract-v1.json`.

## Scope

MC-020 addresses the admitted `mill_form`, `mill_accessible_undercut` and local `lathe_form_tool` cutting-region families without changing the MC-A denominator. It supplies an executable bounded source subtype, `exact_rational_box_union_v1`, rather than pretending that every arbitrary formed/undercut cutter already has a universal finite exact codec.

The subtype is a finite nonempty union of strictly positive-volume axis-aligned boxes with exact rational local coordinates. Cutting and non-cutting holder regions are separate. The union may be nonconvex and may contain reentrant voids; neither a convex hull nor a global bounding box is equivalent cutter truth.

`PB-007-03` therefore remains **OPEN** for admitted arbitrary form/undercut source instances outside the bounded subtype. The task does not remove such instances from the domain.

## Exact fixed-axis translation

For stationary, line and polyline motion, point membership in the sweep of one local box is decided by intersecting the exact rational source-parameter bands induced by the x, y and z inequalities. One shared source parameter must satisfy all three coordinates. This directly handles simultaneous XYZ translation and rejects endpoint-AABB false positives caused by decoupling the path coordinates.

The complete cutter sweep is the union of those exact box sweeps. Equality is exact rational equality; binary floating point and a global epsilon are not predicate authority. Engaged path leaves stay continuous and source-bound. Exact retraces may leave the swept set unchanged but remain in immutable source history; engaged teleportation is invalid.

## Independent controls

The verifier pins `research/machining-completeness/tasks/MC-010/independent_exact_oracle.py` by blob SHA and uses its independently implemented exact axis-parallel rational-box sweep for a cross-check. The MC-020 implementation does not import that oracle.

Additional controls include a stepped nonconvex form cutter with tangent and signed neighbours, a reentrant-void probe that an enclosing AABB would incorrectly fill, and a simultaneous-XYZ diagonal sweep with a deliberate decoupled-coordinate false positive.

## Accessible undercuts and holder clearance

An accessible undercut is not established merely because its cutting solid has a mathematical sweep. The physical witness separately records the effective cutting region, the non-cutting holder region, an explicit continuous unengaged approach path and forbidden retained-material/fixture obstacles.

The deterministic access checker tests the **complete tool body**—cutting plus holder—against those obstacles. Closed contact with a forbidden obstacle is collision. A side-entry fixture demonstrates a valid route for a wide undercut head carried by a narrow neck/holder, while a vertical plunge through the retained lips is rejected. A holder-only obstruction separately proves that cutting-region-only clearance is insufficient. Candidate geometry success is never used as the access oracle.

Target material deliberately engaged during the later cutting interval is not mislabeled as a forbidden approach obstacle.

## MC-058 nonlinear source leaves

Circular-arc, helical, spline, piecewise and timed/phase motion is consumed only through source-bound MC-058 leaves carrying a certified Euclidean translation enclosure `e`. For each local cutter box, expanding every coordinate face by `e` gives a conservative outer box because each coordinate displacement is bounded by the Euclidean displacement. Eroding every face by `e`, when a positive-volume core remains, gives a conservative inner box.

The only resulting classifications are `INSIDE`, `OUTSIDE` and `UNCERTIFIED`. A zero-width numerical wish, refinement cap or candidate success cannot turn an uncertainty shell into exact membership, topology or an exact-zero event.

## Lathe boundary

The bounded codec can represent local finite `lathe_form_tool` cutting/holder geometry. That does **not** establish a turning process sweep. Rotational-reduction admission remains MC-021, while phase-sensitive/spindle-feed-correlated construction remains MC-022. MC-020 does not duplicate or pre-empt either owner.

## Proof and programme boundary

MC-020 is deterministic construction/model evidence, not native geometry evidence. `PB-007-03` remains open and propagates to the later candidate/integration path. **PO-02, PO-04, PO-05 and PO-06 remain OPEN. MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.**

No native or paid campaign ran. Protected historical `research/rcs-*` evidence, source/audio/provenance semantics, canonical-journal meaning, positive-volume material rules and durable body/lineage semantics are unchanged.
