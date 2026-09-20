# MC-002 — Machining domain grammar and physical-validity contract

Status: **COMPLETED_RESEARCH** as a reviewed artifact dependency. This task does **not** accept MC-A, claim a native geometry implementation, or authorize production/native campaigns.

## Purpose and bounded hypothesis

MC-002 asks whether the current MC-1 product scope can be stated independently of solver convenience as a finite constructor grammar plus physical-validity/witness rules. The decisive counterexample was an ordinary in-scope operation with no explicit constructor/composition route, or a validity rule that depended on candidate success, allowed engaged teleportation, silently machined an unheld separated body, or used backend contact/topology as durable material identity.

The result is `domain-contract-v1.json`, schema `radicadsac-mc-domain-contract/1.1`, bound to source baseline `b4184c3a65123df0f54f93c50fab223cc9e4de4d` and the reviewed MC-001 outcome blob `2efd52cf39102d5722c6bbf281828361e943d6a4`.

## Evidence and claim class

This is requirement/design-contract work: `REQUIREMENT`, `DESIGN_DECISION`, and `DOCUMENTATION_RECONCILIATION`. No native geometry/kernel measurement was run or inferred. Historical Genesis-v1/v2 evidence, frozen handoff identities, source/audio/provenance semantics, STEP qualification, and accepted journal/body/lineage meaning are unchanged.

Authority was reconciled against the founding brief, the MSAC↔geometry contract, the current MC-1 programme/domain specification, and DR-0026. The current MC-1 scope is lathe plus fixed-axis three-axis milling per operation, with explicit non-cutting setup reorientation permitted between operations. That is a tranche boundary, not a claim that the long-term product can never support variable-orientation machining.

## Constructor grammar

The machine-readable contract separates constructors for stock, finite cutting solids, finite continuous trajectories, engagement boundaries, lathe spindle/phase kinematics, setup/re-clamp/machine transitions, and nominal material/body transitions.

Important corrections made during review:

- a drill is represented by a machine-neutral `drill_cutting_solid`, so axial drilling in a lathe is not mislabeled as a mill-only cutter;
- fixed-axis helical milling has an explicit `helical_arc` trajectory constructor rather than pretending a planar circular arc alone expresses simultaneous angular/axial motion;
- eccentric turning explicitly includes a physical external cutter as well as the eccentric setup and phase-sensitive motion;
- retrace/self-crossing and cut-through mill cases explicitly name a cutter instead of relying on an implied provider state.

Exact coefficient/curve/time/transform encodings remain MC-003 work; defining a semantic constructor here does not prejudge its numerical representation or terminating realization.

## Ordinary-operation coverage

The contract explicitly admits 26 required operation/composition classes covering:

- lathe OD/facing/shoulder/profile, ID boring, axial drilling, grooving, complete parting, form turning, synchronized threading, eccentric turning, and exact retrace finishing;
- mill facing, slot/pocket/freehand motion, drilling/plunge, rounded/ball simultaneous XYZ, form/chamfer/countersink work, accessible undercutting, fixed-axis helical threading, general simultaneous XYZ, retrace/self-cross/stationary motion, and cut-through/multi-body states;
- explicit re-clamp/reorientation, lathe→mill→lathe composition, continued machining of a separated retained/re-clamped body, and complete body removal.

Every required ID is present exactly once, every admitted operation references declared constructors and physical witnesses, and provider/kernel success is excluded as an admissibility oracle.

## Physical-validity contract

Physical validity is independent of candidate geometry success. The contract requires bounded volumetric stock, finite cutters with cutting/non-cutting regions distinguished, continuous engaged motion, explicit travel/kinematic feasibility, access/holder/fixture clearance where relevant, and explicit workholding of the durable target body.

An engaged teleport is invalid. A stationary engaged interval is valid. After a connectivity-changing cut, a separated body may only be machined while demonstrably retained by the current setup or after an explicit re-clamp/re-chuck. Parted material is not magically fixed.

Material connectivity and durable body identity remain separate: point/edge contact cannot create a volumetric connection; face contact requires local-interior analysis; coincident/touching boundaries alone do not merge durable bodies; positive-volume slivers remain material; whole-body removal yields an explicit empty/disappearance transition.

## Boundary/pathology policy

Coincidence/coplanarity, tangency and zero-volume contact, sub-tolerance positive cuts, positive-volume slivers, self-crossing/retrace/reversal/stationary segments, large finite histories, whole-body removal, and true no-new-removal outcomes remain ordinary cases. They are not moved outside the domain to protect a candidate.

The task-local verifier attacks those rules adversarially by mutating candidate independence, engaged teleportation, detached-body workholding, contact connectivity, sliver retention, operation coverage, constructor references, parting post-separation handling, helical motion, named domain decisions, and evidence classification. Each negative control must be rejected.

## Named domain decisions and negative findings

Three boundaries are explicit current-MC-1 exclusions rather than solver refusals: continuous cutting-time five-axis tool reorientation, additive processes, and force/deformation/chip dynamics.

Two product-domain questions remain intentionally open and are carried as named decisions rather than silently excluded:

- `DD-002-04`: synchronized lathe live/driven tooling as one compound machine operation versus an explicit setup/machine transition;
- `DD-002-05`: multiple simultaneously controlled spindles/transfer-machine semantics.

These are downstream product/domain decisions. They do not authorize a provider to reject otherwise admitted lathe/mill operations, and they do not make MC-A accepted.

## Downstream implications

MC-003 must supply exact numeric, curve/arc/spline/helical, phase/time, transform, and legacy-journal compatibility semantics. MC-004 must preregister candidate-independent workloads, accuracy vectors, hardware, and resource envelopes. MC-005 must integrate MC-002–004 and is the only MG-01 task authorized to decide MC-A.

Constructive tasks MC-006–008 still owe finite/terminating realization arguments for admitted constructors. Sweep tasks MC-018–023 still owe actual physical cutter/setup realization. MC-054 still owns the engineering-output profile for singular/grouped material states.

## Verification

Cheap deterministic verification:

```text
python3 research/machining-completeness/tasks/MC-002/verify.py --contract
python3 tools/mc_workflow.py verify MC-002
python3 tools/validate_machining_completeness.py
```

The MC-1 static workflow invokes the task verifier after integration. No native campaign, paid runner, external geometry kernel, or production repository is required by this task.
