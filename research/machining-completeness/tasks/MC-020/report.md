# MC-020 — form, nonconvex and accessible undercut sweep construction

Status: **completed bounded deterministic research; PB-007-03 and programme-wide sweep/completeness obligations remain open.**

Issue: #82  
Source baseline: `a5b6905bb212afed21a7747cd80a0bf87ee34cca`  
Native/paid execution: **none**

## Hypothesis and falsification criterion

A finite union of strictly positive-volume axis-aligned boxes with exact rational local coordinates is a useful executable source subtype for admitted form/nonconvex/accessible-undercut cutters. For fixed-axis stationary/line/polyline translation, point membership in its sweep can be decided exactly by intersecting the coordinate bands for **one shared source parameter**. A physically accessible undercut route can be checked independently by testing the complete cutting plus non-cutting holder body against explicit retained-material/fixture obstacles along an unengaged approach path.

The bounded hypothesis is falsified if exact equality/signed-neighbour controls disagree, if a reentrant void is filled by a hull/AABB shortcut, if simultaneous XYZ correlation is lost, if the independent MC-010 axis-parallel box control disagrees, if the access checker accepts the deliberately colliding route or ignores a holder-only collision, or if an MC-058 uncertainty shell is promoted to exact membership.

The stronger universal hypothesis is **not established**: the admitted domain still lacks a universal finite exact source codec for arbitrary form/undercut cutting-region instances. That pre-existing gap is `PB-007-03` and remains open rather than being duplicated or hidden by this task.

## Result

`form_undercut_sweep.py` implements a deterministic `exact_rational_box_union_v1` research subtype for `mill_form`, `mill_accessible_undercut`, and the local cutting-region representation of `lathe_form_tool`.

For exact stationary/line/polyline motion, each translated box is tested by intersecting the exact rational parameter intervals induced by its x/y/z inequalities. The same `t` must satisfy every coordinate, so a swept endpoint AABB is not accepted as the path sweep. A finite union preserves nonconvex and reentrant regions as an actual union rather than filling them with a convex hull or global AABB.

For MC-058-derived circular/helical/spline/piecewise/timed leaves, the implementation is deliberately fail-closed. A certified Euclidean translation enclosure `e` expands each box by `e` per coordinate for a conservative outer set and erodes each box by `e` for a conservative inner set when a positive-volume core remains. The result is only `INSIDE`, `OUTSIDE`, or `UNCERTIFIED`; the shell is not topology or exact-zero authority.

## Boundary and adversarial controls

The deterministic verifier exercises:

- a two-box stepped form tool with exact stationary tangency at `x=1`, signed inside/outside neighbours, and a reentrant-void probe that an enclosing AABB would falsely fill;
- a simultaneous XYZ diagonal line with a true shared-parameter boundary point and a deliberate endpoint-AABB false positive that must remain outside;
- an independent MC-010 exact-rational axis-parallel box-sweep cross-check. The MC-010 oracle is pinned by blob SHA and loaded only by the verifier, not by the MC-020 implementation;
- an accessible undercut whose wide head can approach laterally below two retained lips while its narrow neck/holder remains in the slot, plus a vertical plunge that must collide;
- a holder-only obstacle proving that cutting-region-only clearance is insufficient;
- MC-058 bounded inside/outside/uncertified probes, unbound-leaf rejection, retrace preservation, and engaged-teleportation rejection;
- contract mutations that attempt to permit hull substitution, drop holder semantics, close `PB-007-03`, claim a universal arbitrary-form codec, promote the local lathe cutter codec into completed spindle/timed sweep semantics, drift dependency/oracle hashes, or accept MC-B early.

## Access semantics

The access witness is separate from candidate sweep success. An undercut tool records its effective cutting region and non-cutting holder region independently. An explicit unengaged approach path is tested against explicit forbidden retained-material/fixture obstacles using exact closed-set translated-box collision. Contact with a forbidden obstacle is a collision. Target material intentionally engaged during the subsequent cutting interval is not mislabeled as an access obstacle.

This is a bounded physical-validity model, not a universal fixture/holder CAD implementation.

## Constructor coverage and retained blocker

- `mill_form`: bounded exact-rational box-union route is executable for exact stationary/line/polyline motion; MC-058 provides the conservative nonlinear interface.
- `mill_accessible_undercut`: same bounded sweep route plus an explicit complete-body access/holder-clearance witness.
- `lathe_form_tool`: the local finite cutting/holder region can use the same bounded codec, but rotational reduction and spindle/feed/timed process semantics are **not** claimed here. They remain owned by MC-021 and MC-022.
- Arbitrary admitted form/undercut source geometry outside this bounded codec remains `PB-007-03`. The frozen MC-A denominator is unchanged and no constructor is excluded because a provider cannot encode it.

`PB-007-03` remains an OPEN propagated blocker affecting the later candidate/integration path, including MC-026, MC-028, MC-029, MC-030, MC-031 and MC-038.

## Proof and programme boundary

MC-020 contributes a bounded deterministic cutter/sweep/access construction. It does **not** establish every admitted actual tool sweep, universal classification, universal finite progress, native kernel correctness, topology, reconstruction, STEP, or practical scale. PO-02, PO-04, PO-05 and PO-06 remain **OPEN**. MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.

Protected historical `research/rcs-*` evidence, source/audio/provenance semantics, canonical-journal meaning, positive-volume material rules and durable body/lineage semantics were not modified.

## Verification

```text
python3 research/machining-completeness/tasks/MC-020/verify.py --contract
python3 research/machining-completeness/tasks/MC-020/verify.py --self-test
python3 tools/mc_workflow.py verify MC-020
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```
