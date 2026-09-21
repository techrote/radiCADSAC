# MC-021 lathe rotational reduction and axisymmetry admission

Status: **bounded exact admission predicate established; phase-sensitive and eccentric turning remain outside this fast path.** The machine-readable contract is `research/machining-completeness/tasks/MC-021/lathe-rotational-reduction-contract-v1.json`.

## Scope

MC-021 defines when a conventional-lathe material operation may be represented in an exact meridian `(r,z)` quotient without changing the MC-A domain or rewriting the saved operation. It is an admission rule for a fast/reference path, not a statement that all lathe operations are axisymmetric.

## Full-orbit theorem

Let `R_theta` denote rotation around the declared spindle axis. Let the exact durable target material `M` be invariant under every `R_theta`. Let the source setup be exactly coaxial, and let engaged cutter placement factor as

```text
K(q, theta) = R_theta A(q)
```

for `(q,theta)` in the product domain `Q × S1`, where `A(q)` is independent of spindle phase and every `q` receives the complete phase circle.

Then the cutter sweep

```text
S = union_(q,theta) K(q,theta)(T)
```

is invariant under the same rotations. Since `M` and `S` are invariant, `closure(interior(M \ S))` is invariant as well. Exact material membership can therefore be represented by orbit coordinates `(r,z)` for that operation.

The product-domain condition is essential. A synchronized time/phase trajectory is generally a one-dimensional graph rather than `Q × S1`; replacing it by independent full-angle coverage changes the sweep.

## Admission requirements

The reduction requires a target-axisymmetry certificate bound to the exact durable body and setup revision, exact coaxial setup mapping, phase-independent meridian placement, complete phase coverage for each meridian state, immutable source history and exact engagement boundaries. Cutting and non-cutting tool regions, access and holder-clearance witnesses, and durable body identities remain outside the quotient's authority and must be preserved explicitly.

Operation labels are not proof. OD turning, facing, grooving or form turning may use the quotient only when the source witness satisfies the predicate.

## Mandatory rejection and routing

The fast path rejects:

- eccentric or tilted/noncoaxial setup;
- synchronized/threading semantics whose material depends on spindle/feed phase;
- timed-phase geometry dependence;
- partial-turn engagement;
- finite angular sampling presented as full rotational authority;
- a nonaxisymmetric target body, including one made nonaxisymmetric by earlier milling;
- compound live-tool kinematics outside the current MC-A tranche;
- global-epsilon or binary-float exact-contact authority.

Phase-sensitive and eccentric cases route to **MC-022**. Re-clamp/reorientation and cross-setup composition remain **MC-023**.

## Exact bounded control representation

The executable control uses finite exact-rational meridian rectangles. Revolving `[r0,r1] × [z0,z1]` gives a regular axisymmetric solid with exact symbolic volume coefficient

```text
(r1^2 - r0^2) * (z1 - z0)
```

multiplying π. Stationary and line-translated cutter rectangles are tested with one shared exact source parameter. Cartesian validation uses `x^2 + y^2` and rational 3-4-5 radii rather than trigonometric sampling.

A parting control explicitly yields two retained meridian components. Those quotient components do not create or merge durable manufactured-body identities by themselves; body transitions remain source-bound.

## Programme boundary

MC-021 does not close `PB-007-01`, `PB-007-02` or `PB-007-03`, does not establish a general phase-sensitive lathe sweep, and does not claim native geometry, reconstruction or STEP capability. **PO-02, PO-04, PO-05 and PO-06 remain OPEN. MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.**

No native or paid campaign ran. Protected historical source/audio/provenance, canonical-journal, positive-volume and durable body/lineage semantics are unchanged.
