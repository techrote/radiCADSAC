# MC-021 — Lathe rotational reduction and axisymmetry admission

Status: **COMPLETED_RESEARCH — sufficient rotational-reduction admission predicate established for a bounded exact quotient path; phase-sensitive/eccentric cases remain routed to MC-022.**

Issue: #83  
Source baseline: `11e7023edff0469b4b9f72193e8096512075afae`  
Native/paid execution: **none**

## Hypothesis and falsification criterion

Hypothesis: a lathe operation may be reduced exactly to a meridian/rotational material domain when the selected durable target material is already invariant under the declared spindle rotation, the setup maps that material axis exactly and coaxially onto the spindle axis, and the engaged cutter placement factors as

```text
K(q, theta) = R_theta A(q)
```

over the **product domain** `Q × S1`. `A(q)` is the phase-independent meridian placement and every admitted meridian state `q` receives the complete spindle phase orbit `S1`.

Under those conditions the cutter sweep is invariant under spindle rotation. Regularized subtraction of an invariant sweep from invariant target material remains invariant, so exact material membership may be represented in the `(r,z)` quotient without changing the source operation.

The hypothesis is falsified for this task if equality/signed-neighbour controls disagree, if off-axis points with the same exact radius classify differently, if simultaneous radial/axial motion can pass by independently choosing different source parameters, if tangent zero-volume contact is treated as positive removal, if a parting control loses one material component, or if any nonaxisymmetric/eccentric/phase-sensitive/partial-orbit case is admitted by the predicate.

This is a **sufficient predicate**, not a claim that every reducible lathe history must satisfy this particular certificate form.

## Why operation names are insufficient

`lathe_od_turning`, `lathe_facing`, grooving or another conventional label does not itself prove axisymmetry. A continuously fed finite cutter can retain spindle/feed phase correlation; synchronized threading is explicitly phase-sensitive; eccentric workholding is noncoaxial; and a previously milled target may already be nonaxisymmetric even if the next cutter orbit is rotationally symmetric.

Accordingly MC-021 does not replace source process semantics with a heuristic such as “lathe means 2D”. Admission requires an explicit target-axisymmetry certificate and an exact full-orbit factorization witness. Cases lacking either are rejected from this fast path, not approximated into it.

## Sufficient admission predicate

All of the following are required:

- the exact durable target body carries an axisymmetry certificate bound to the current setup revision;
- the source setup transform is exact and maps the material axis coaxially to the declared spindle axis;
- cutter meridian placement is independent of spindle phase;
- engaged semantics factor as `Q × S1`, not a one-dimensional synchronized graph in time/phase;
- every meridian state receives the complete phase orbit, not a finite angular sample;
- engagement endpoints and source history remain authoritative and immutable;
- cutting and non-cutting tool regions remain distinct;
- physical access and holder-clearance witnesses remain present;
- durable body identity is retained separately from quotient components.

The predicate rejects eccentric setup, phase synchronization, timed/phase geometry dependence, partial-phase engagement, compound live-tool kinematics, sampled-angle authority and global-epsilon authority. Rejected phase-sensitive cases route to **MC-022**. Re-clamp/reorientation and multi-setup composition remain **MC-023**.

## Bounded exact executable subtype

`rotational_reduction.py` provides an exact-rational research implementation over finite meridian rectangles. A rectangle `[r0,r1] × [z0,z1]`, with rational bounds and `r0 >= 0`, denotes its exact solid of revolution. Its volume is retained symbolically as

```text
pi * (r1^2 - r0^2) * (z1 - z0)
```

so no decimal approximation of π enters predicate authority.

The canonical cutter control is a finite positive-volume cylindrical wedge whose complete spindle orbit has an exact rational meridian rectangle. Stationary and exact rational line translations in the meridian quotient are implemented. For a line, the same exact source parameter must satisfy both radial and axial bands; an endpoint AABB or independently chosen radial/axial parameters is insufficient.

Cartesian controls use exact squared-radius comparisons. Off-axis 3-4-5 points provide rational radii without trigonometric evaluation or binary floating point.

## Boundary and adversarial controls

The deterministic verifier exercises:

- stationary full-orbit cutter equality plus exact signed radial neighbours;
- off-axis points with the same exact radius, including a 3-4-5 construction, to test true rotational invariance;
- simultaneous radial/axial line motion with one shared exact parameter and a deliberate decoupled-coordinate false positive;
- exact tangency against an axisymmetric stock boundary, which removes zero positive volume, and a rational signed penetration that removes positive volume;
- an exact parting cut through `r=0..R`, producing two positive-volume meridian material components and preserving both;
- symbolic exact `pi`-coefficient volume conservation for that parting control;
- rejection of nonaxisymmetric target material even when the cutter orbit is rotationally invariant;
- rejection of eccentric, synchronized, timed-phase, partial-orbit and sampled-angle cases;
- contract mutations attempting to weaken target/setup binding, admit angular sampling, merge durable bodies, erase holder/access semantics, rewrite saved history, close inherited proof blockers or promote MC-B.

## Proof and programme boundary

MC-021 establishes only the exact **admission condition and bounded quotient implementation**. It does not construct the general phase-sensitive spindle/feed sweep. In particular:

- `PB-007-01` remains **OPEN** for required tangential/multiple/singular transcendental phase events outside the admitted full-orbit factorization;
- `PB-007-02` remains **OPEN** for the general coupled helical/spindle-feed/eccentric route;
- `PB-007-03` remains propagated from the arbitrary form/undercut cutter-codec gap; MC-021 does not redefine or close it.

`PO-02`, `PO-04`, `PO-05` and `PO-06` remain **OPEN**. MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.

No native or paid campaign ran. Historical `research/rcs-*`, source/audio/provenance records, canonical-journal semantics, positive-volume rules and durable body/lineage semantics were not modified.

## Verification

```text
python3 research/machining-completeness/tasks/MC-021/verify.py --contract
python3 research/machining-completeness/tasks/MC-021/verify.py --self-test
python3 tools/mc_workflow.py verify MC-021
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```
