# Adversarial manufacturing corpus specification

Status: RCS-003 implementation candidate  
Date: 2026-09-16  
Machine-readable corpus: `research/rcs-003/corpus-v1.json`  
Schema: `rcs-003-corpus/1.0`

## Purpose and scope

This document defines the implementation-independent adversarial manufacturing fixture corpus used by RCS-006 onward. The corpus turns routine-but-pathological machining conditions into deterministic, parameterized research inputs without making any CAD kernel's output the definition of truth.

The corpus is designed to test OpenSimachinist research hypotheses involving Boolean robustness, tolerance/equivalence, provenance, topology, process-specific solvers, alternate representations and STEP reconciliation.

It is not a benchmark-results file. Backend observations belong in later result records keyed to the exact corpus/family revision.

## Evidence status

- **SOURCE:** programme invariants, fixture discipline and failure taxonomy come from `AGENTS.md`, `docs/01-MSAC-GEOMETRY-CONTRACT.md`, `docs/04-REVISED-RESEARCH-ROADMAP.md`, `docs/06-RESEARCH-METHOD.md`, `docs/08-TERMINOLOGY.md`, `docs/09-FOUNDATION-AUDIT.md` and accepted journal decisions.
- **PROPOSAL accepted by this issue when merged:** the fixture schema, parameter families, physical-oracle structure and lifecycle below.
- **MEASURED:** none yet. RCS-003 specifies the workload. RCS-006 measures implementations against it.

## Hypothesis and falsification criteria

### Hypothesis

A corpus that preserves manufacturing semantics separately from backend geometry can make pathological cases reproducible across kernels while still allowing parameter sweeps around contact, tolerance, operation-count and connectivity thresholds.

### Falsification criteria

The corpus design is insufficient if any of the following becomes true during RCS-006 or later work:

- a fixture cannot be interpreted without a hidden backend coordinate, unit or tolerance convention;
- a real manufacturing failure cannot be minimized without destroying the semantic fact that caused it;
- expected physical intent has to be overwritten with an OCCT/other-kernel result to make testing possible;
- body-separation cases cannot distinguish material connectivity from later scrap/export selection policy;
- parameterized cases cannot identify the limiting member at coincidence/tangency/cut-through boundaries;
- result records cannot unambiguously identify the exact fixture revision and parameter tuple exercised.

If any criterion is met, revise the corpus schema rather than quietly teaching the harness backend-specific assumptions.

## Fixture identity and versioning

A concrete fixture instance is identified by:

1. corpus ID and semantic version;
2. fixture family `id`;
3. family `revision`;
4. complete ordered parameter tuple;
5. policy references for units, frames, tolerance and result interpretation.

Published benchmark results must retain this identity permanently.

Changing prose alone is not a semantic fixture change. Changing any of the following requires a new family revision or corpus version:

- physical intent;
- parameter domain or limiting-case meaning;
- expected-result classification;
- body-count/connectivity expectation;
- units or coordinate-frame semantics;
- tolerance-policy semantics;
- minimization invariant.

## Units and coordinate frames

Corpus v1 uses:

- dimensional unit: millimetres (`mm`);
- angular unit where required: radians (`rad`);
- time, if introduced by a materializer: seconds (`s`) unless the canonical journal fixture carries its own exact integer convention;
- frame: `right-handed-z-up-workpiece-v1`.

`right-handed-z-up-workpiece-v1` means:

- the fixture's workpiece frame is right-handed;
- +Z is the declared fixture-up axis;
- all stock, cutter-envelope and trajectory coordinates are interpreted in the workpiece frame unless a concrete materialized journal explicitly carries a transform chain;
- process-specific axis conventions, such as lathe spindle axis, must be stated by the materializer and not inferred from a backend default.

RCS-003 does not replace the canonical journal contract. A harness may materialize these families into `msac-journal/1.0` fixtures. When it does, the journal's explicit frame graph and integer numeric convention become authoritative for that materialized instance.

## Tolerance policy

`rcs-003-fixture-policy-v1` deliberately separates physical intent from implementation resolution.

Rules:

- exactly zero parameter members represent exact coincidence/contact/retrace/cut-through thresholds where stated;
- strictly positive overlap/removal dimensions represent physical volume, however small;
- lower-dimensional point/edge/face contact without positive-volume overlap is not material removal;
- a backend may report inability to represent a tiny intended change, but must not cause the fixture oracle to be rewritten as “no change”;
- backend fuzzy values, entity tolerances, snapping, regularization and export tolerances are result/configuration metadata, not fixture semantics;
- later tolerance research may add policy variants, but must preserve the v1 oracle for comparisons.

This is not a claim that all positive-volume features must survive final STEP export unchanged. It is a claim that any intentional cleanup must be explicit, bounded, measured and attributable to a named policy.

## Expected result classes

Every family declares one of four classes.

### `no_material_change`

The limiting member performs no positive-volume addition/removal. Typical examples are exact retracing, coplanar re-facing and pure tangency.

This class does not mean “the kernel must return byte-identical topology.” It means the physical material set should be equivalent within the fixture's declared oracle.

### `regularized_material_change`

The family expresses real volumetric removal/addition while allowing later research to test alternative topology or regularization representations. The expected physical material is still defined independently of implementation.

### `body_separation_or_merge`

The defining event changes material-body connectivity. Body count and connectivity are part of the fixture oracle.

RCS-003 intentionally does **not** choose which resulting body is “the part,” “scrap,” or export-selected. Both/all bodies remain legitimate material-state outputs until a later explicit policy decides otherwise.

### `ambiguous_or_unsupported`

Reserved for cases where the programme intentionally lacks a unique physical oracle or where the requested semantics fall outside declared programme scope. Corpus v1 does not use this as a dumping ground for kernel failures.

## Parameterized family rules

Each family contains one or more explicit parameter axes. Parameter axes are chosen to sweep the geometry through important regime boundaries rather than encode a single magic reproducer.

Required sweep concepts include:

- signed separation around coincidence/coplanarity;
- signed penetration around tangency/contact;
- feature/removal scale through sub-tolerance regimes;
- segment/operation counts from trivial to stress-scale;
- noise amplitude for analogue/freehand paths;
- connectivity parameters around exact cut-through;
- angle/orientation perturbation where relevant.

A harness may sample only a tractable subset in CI, but it must preserve the full family definition for heavier campaigns.

## Lathe corpus

Corpus v1 includes:

- repeated exact finishing passes;
- sub-tolerance skims;
- tangential shoulder contact;
- facing exactly to an existing plane;
- OD/ID surface retracing;
- bore/shoulder meetings;
- path reversal;
- noisy analogue feed;
- long redundant operation sequences;
- representative parting/cut-through producing disconnected material bodies.

### Lathe separation semantics

`lathe-parting-cut-through` treats complete radial cut-through as a transition from one connected material body to two disconnected volumetric bodies. The physical oracle keeps both bodies. A later retained-part/scrap selection policy may classify them, but classification is not part of this fixture's truth condition.

## Mill corpus

Corpus v1 includes:

- existing-edge following;
- coplanar face skims;
- tangent corner entry/exit;
- repeated identical slots;
- overlapping slots/pockets;
- tiny cusps;
- self-crossing freehand paths;
- retraced jittery paths;
- sub-tolerance plunges;
- point/edge/face lower-dimensional touches;
- cut-through producing disconnected material bodies;
- very high segment counts.

### Mill separation semantics

`mill-cut-through-separation` defines a through-slot that disconnects material into two bodies. As with lathe parting, neither body is silently deleted by the fixture definition.

## Generic corpus

Corpus v1 includes:

- coincidence/coplanarity;
- barely overlapping solids;
- point/edge/face-only contact;
- positive-volume slivers;
- tolerance-accumulation chains;
- topology-explosion sequences;
- connected-to-disconnected transitions.

These generic families are not substitutes for manufacturing fixtures. They isolate lower-level mechanisms so later research can tell whether a failure is process-specific or representation-level.

## Physical oracle versus backend observation

A fixture's `oracle` says what material state the operation intends physically.

A backend result record must instead capture observations such as:

- accepted/rejected input;
- status/error;
- crash/hang/timeout;
- topology validity;
- material-body count/connectivity;
- bounding box, volume, area and dimensions;
- geometric deviation;
- topology counts and minimum feature statistics;
- analytic surface classes retained/lost;
- runtime and memory;
- STEP writer/read-back/interoperability results;
- deterministic repeatability;
- exact backend/version/build/tolerance configuration.

A backend result may disagree with the fixture oracle. That disagreement is the research finding.

## Baseline result metadata contract for RCS-006

RCS-006 should emit one machine-readable observation per concrete family member with at least:

- result schema/version;
- corpus ID/version;
- family ID/revision;
- parameter tuple;
- materialized fixture hash if applicable;
- backend name/version/commit/build configuration;
- tolerance/policy configuration;
- repeat index and seed where applicable;
- failure-taxonomy category;
- completion status;
- validity/topology/connectivity metrics;
- geometry/volume metrics;
- runtime/memory metrics where practical;
- STEP metrics where applicable;
- links/hashes for artifacts and logs.

Backend-specific observations must not be written back into `corpus-v1.json`.

## Failure minimization rules

When a real failure is discovered:

1. Preserve the original journal/trace or exact materialized family member.
2. Record the exact backend/toolchain and result artifact.
3. Create a separate minimized reproducer.
4. Keep the original and minimized form linked by immutable IDs/hashes.
5. Never remove the manufacturing facts required to reproduce the semantic condition: setup, tool envelope, operation order, units/frame, parameter values, physical oracle and body-connectivity expectation.
6. Genericize only as an additional reproducer. Do not replace the manufacturing trace with a generic CAD Boolean testcase.
7. If minimization changes the physical oracle, it is a different fixture, not a minimized equivalent.

## Regression lifecycle

A fixture enters regression status when a result is important enough to track across backend/version changes.

Regression records are append-only observations. They should state:

- first known failing backend/version;
- first known passing backend/version if later fixed;
- whether the failure is deterministic;
- minimized reproducer identity;
- physical-intent fixture identity;
- failure taxonomy;
- linked issue/decision/PR;
- whether the regression remains architecture-relevant.

Do not delete obsolete failures merely because a later backend fixes them; they remain evidence about design sensitivity.

## Determinism and generation

The corpus manifest itself is deterministic JSON data. If a materializer synthesizes noise, jitter or dense trajectories from compact parameters, it must:

- use an explicit algorithm version;
- use an explicit seed or a fully enumerated sample sequence;
- record generated artifact hashes;
- produce byte-identical generated input where practical;
- distinguish generation/canonicalization time from geometry execution time.

## Relationship to the canonical journal

RCS-002 established the durable canonical manufacturing journal. RCS-003 does not invent a competing operation history format.

Instead, a corpus family may be materialized as:

- a pure analytic geometry fixture for representation-level research;
- a canonical `msac-journal/1.0` fixture for manufacturing replay research;
- both, when comparing semantic and geometry-level mechanisms.

When both exist, they must be linked and share the same physical-intent oracle.

## Implications for RCS-006

RCS-006 can now build a harness without deciding fixture semantics itself. It should:

- parse the manifest;
- select parameter tuples;
- materialize/generate backend input deterministically;
- execute in crash/hang-isolated processes where practical;
- emit result records rather than mutate fixture definitions;
- run a tractable CI smoke subset and document heavier campaigns;
- cover at least coincidence, tangency, sliver/sub-tolerance removal, retracing, high operation/segment count, one lathe case, one mill case and STEP read-back where applicable.

## Implications for later research

- RCS-007 can sweep tolerance/equivalence models over the same limiting families.
- RCS-008 can use repeated/overlapping operations and separation cases to test ancestry.
- RCS-009 can use lower-dimensional contact and sliver cases to test regularization/deferred topology.
- RCS-010 can compare lathe 3D versus axial/radial strategies on identical intent.
- RCS-011 can compare mill sweep/process hierarchies on the freehand/overlap corpus.
- RCS-012 can compare alternative representations without changing workload definitions.

## Unresolved questions

- Exact RCS-006 result schema is intentionally deferred to the harness issue.
- Exact subset sizes for CI versus heavy campaigns are deferred to measured harness cost.
- Final STEP body-selection/scrap policy is deferred to RCS-005/RCS-013; RCS-003 only requires that separation be observable and non-lossy.
- Corpus v1 uses a programme-level mm/rad fixture convention; materialized RCS-002 journals continue to use the journal's canonical integer numeric convention.
- Additional 3D tool orientation/5-axis families are outside the initial lathe/mill scope unless later research demonstrates a Gate-2 need.

## Conclusion

Corpus v1 treats coincidence, tangency, retracing, noise, slivers, sub-tolerance removal, high operation counts and body separation as ordinary research workloads. Its physical oracles are independent of any geometry kernel, and its versioning/minimization rules preserve manufacturing semantics across later experiments.
