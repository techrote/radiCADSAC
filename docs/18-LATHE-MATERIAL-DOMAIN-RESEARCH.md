# RCS-010 — Lathe-specialized material-domain solver research

Status: accepted RCS-010 research result  
Date: 2026-09-17  
Pinned measurement backend: OCCT 8.0.1 / `V8_0_1` / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

## Research question

Can a substantial, useful subset of fixed-axis turning be represented and updated more robustly as a 2D axial/radial material set, with conventional 3D B-rep construction deferred to explicit reconciliation boundaries, without sacrificing physical material semantics, analytic geometry, provenance, or STEP output?

The answer from the founding measured set is **yes for the explicitly bounded axisymmetric subset**, with important scope limits around production tool-envelope generation, parting/grooving connectivity and non-axisymmetric operations.

## Hypotheses and falsification criteria

### H1 — Axisymmetric material-domain sufficiency

**SUPPORTED for the measured subset.** OD turning, facing, shoulders/tapers, through boring and blind boring were expressed as regularized axial/radial updates and reconstructed into valid solids matching the conventional 3D strategies in volume and bounds within the declared budgets.

### H2 — Operation-count decoupling

**SUPPORTED.** Canonical journal history remained intact while material topology work was decoupled from event count. The 100-pass exact-retrace case retained 100 journal events and identified 99 material no-ops; direct axisymmetric material updating required no 3D material Boolean per event.

### H3 — STEP and analytic geometry preservation

**SUPPORTED for the measured subset.** Reconciliation preserved planes/cylinders and a true cone for the taper case, introduced no B-spline surfaces, and all 21 enabled strategy/file combinations passed the automated AP242DIS millimetre manifold-solid write/read-back gates.

### H4 — Specialized domain is not universal

**SUPPORTED as an architecture boundary.** The successful representation has an explicit semantic membership rule—rotationally symmetric material and completed removal envelope about one declared spindle axis—and explicit fallback/refusal conditions for non-axisymmetric work.

## Competing strategies

The RCS-010 campaign separates representation benefit from simple batching.

**Repeated 3D subtraction** starts with a conventional cylinder, constructs the completed removal envelope, and performs one `BRepAlgoAPI_Cut` for every canonical geometry event. It models the topology/update pressure of direct journal-to-Boolean replay while keeping envelope generation constant.

**Batched 3D subtraction** constructs the same completed removal envelope but subtracts it once. This is an important fallback/comparator: it removes much event-count pressure without introducing a persistent 2D representation.

**Axisymmetric 2D material domain** updates a piecewise-linear radial interval field over spindle-axis coordinate `z`. OD/taper/facing/ID operations update that regularized material set directly. Reconciliation builds a closed `(radius,z)` section and revolves it through `2π` using the pinned OCCT worker.

All three strategies are judged against the same independent 2D analytic material volume and reconstructed target, not screenshots or writer return codes.

## Material-domain definition

For the accepted fixed-axis subset, material is represented by finite axial sections

`S_i = [z_i, z_{i+1}] × [r_inner(z), r_outer(z)]`

where inner and outer radius are linear over each section and satisfy

`0 <= r_inner(z) < r_outer(z)`.

The 3D material set is the solid of revolution of the union of these radial intervals around the spindle axis. Section volume is integrated analytically as the difference of two conical frusta. This makes volume a representation-independent oracle rather than a value copied from OCCT.

The prototype uses decimal arithmetic for the 2D state. This is **not** a production numeric-format decision; RCS-002 durable journal numerics remain authoritative.

## Operation semantics tested

### OD turning and shoulders

An OD operation over `[z0,z1]` applies `r_outer(z) := min(r_outer(z), target(z))`. Constant target radius represents cylindrical OD turning. Restricting the interval creates a shoulder without requiring feature-tree identity.

### Facing

Facing to a new front coordinate removes all material below the reconciled axial plane. Repeating the same face location is a material no-op but remains a journal event.

### Taper/chamfer-class outer boundary

A simple taper uses a linear target radius over an axial interval. The measured revolution retained a true conical surface rather than a spline approximation.

### ID boring

An ID operation applies `r_inner(z) := max(r_inner(z), target_radius)` over its axial interval. Both through boring and blind boring to an internal shoulder were measured successfully.

### Repeated/retraced finishing

The first material-changing pass updates the profile. Exact repeats are retained as canonical journal/provenance events but do not alter the material domain. This consumes the RCS-008 semantic-lineage rule; equality is not inferred from transient B-rep identity.

### Noisy analogue feed

Nine raw radial samples were checked against a declared `0.01 mm` canonicalization envelope and represented as one canonical OD geometry event while preserving the raw/journal evidence. The measured geometry matched the other strategies and passed STEP. This tests the RCS-002 interaction/canonical-intent separation; it is not a general curve-fitting algorithm.

## Tool-envelope scope

RCS-010 distinguishes **material-removal envelope semantics** from individual insert/flute rendering. The founding comparison uses an oracle-derived completed removal envelope so that the experiment isolates representation/update strategy.

A production lathe provider still needs a tool-envelope generator accounting for insert/nose radius, orientation, compensation convention, plunge/retract semantics, undercuts and interference. The measured result therefore supports the material-domain architecture independently of claiming those tool-geometry problems solved.

Nose radius is especially important: in an axisymmetric `(z,r)` domain a fixed-axis turning insert can often be represented by a 2D swept profile/Minkowski-style envelope, but that construction remains to be qualified. RCS-010 does not silently replace a radiused insert with a sharp point in the user-facing manufacturing contract.

## Reconciliation and handoff boundaries

The 2D domain is backend-private derived state. It may remain authoritative for a supported axisymmetric operation sequence while the canonical journal remains durable authority.

Reconciliation to conventional B-rep is required at least for:

- primary STEP export;
- handoff to a non-axisymmetric mill/general provider;
- a query requiring conventional topological entities rather than material dimensions;
- setup/process transition where spindle-axis symmetry no longer applies;
- any failed/ambiguous domain-membership test.

RCS-009 regularized material semantics continue to apply: lower-dimensional contact metadata need not become physical material, positive-volume removal cannot be suppressed by broad fuzzy tolerance, and body/connectivity decisions force reconciliation where needed.

## Explicit supported domain

The accepted architecture input is for workpiece material rotationally symmetric around one known spindle axis and operations whose **completed removal envelope** is also axisymmetric about that axis. The measured useful subset includes:

- cylindrical OD turning;
- facing;
- shoulders;
- linear tapers/chamfers;
- cylindrical through and blind boring;
- exact retraces/repeated finishing;
- bounded canonicalized analogue-controlled variants of those operations.

## Explicit exclusions and fallback requirements

The axisymmetric provider must refuse or hand off, not approximate silently, for:

- live tooling, cross holes, flats, keyways or other non-axisymmetric removal;
- eccentric/off-centre stock or operations;
- arbitrary milling/freehand XYZ cutter envelopes;
- operations whose tool orientation/process semantics produce a non-axisymmetric material envelope;
- general 5-axis machining;
- unsupported undercuts or insert-envelope configurations until their 2D envelope semantics are proven;
- material states already containing non-axisymmetric geometry from another provider unless a valid axisymmetric subproblem is explicitly isolated.

The handoff result is a conventional reconciled solid plus semantic lineage; no OCCT topology ID becomes durable cross-provider identity.

## Metrics and acceptance oracle

Every hosted case required all three strategies to execute, valid B-rep output, expected material-body count, agreement with the independent 2D analytic volume, cross-strategy volume/bounds agreement, expected analytic surface classes with no B-spline substitution, exact backend/version pinning, expected journal/provenance/canonicalization counts, and AP242DIS manifold-solid write/read-back validation where enabled.

Topology counts and runtime are comparative evidence. They do not override physical correctness.

## Measured RCS-010 results

**MEASURED:** hosted workflow run `35214872300`, job `105180888767`, artifact `10493944652`, digest `sha256:7a2511d30fbcdf4dc04b9e8a969b2a3387a84d90226d1f2784249899ca81096c`, against exact OCCT commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`.

The complete nine-case founding set—OD finish, facing, shoulder, taper, through bore, blind bore, repeated finish, 100-pass exact retrace and bounded noisy feed—had **0 acceptance failures**. Maximum cross-strategy volume delta versus the axisymmetric result was approximately `1.82e-12 mm³`; maximum bounding-box delta was approximately `2.13e-14 mm`, both far inside the declared research budgets.

The axisymmetric taper retained `1 cone + 1 cylinder + 2 planes`. The through bore retained two cylindrical surfaces and two planes. The blind bore retained three cylindrical surfaces and three planes. No measured axisymmetric case introduced a B-spline surface.

All **21/21** enabled strategy STEP round-trips passed. The largest measured STEP volume delta was approximately `3.89e-10 mm³` (taper) and the largest bounding-box delta was approximately `2.13e-14 mm`.

The campaign represented 135 journal events and 9 raw analogue samples. It recorded 118 provenance-equivalent material no-ops. Repeated 3D replay performed 127 material Booleans, batched 3D performed 9 and the direct axisymmetric material-domain path performed 0 material Booleans before reconciliation.

For the 100-pass exact retrace, repeated 3D conceptual runtime was approximately `708.36 ms`, batched 3D `6.50 ms`, and direct axisymmetric reconstruction `1.10 ms`. Aggregate campaign totals were approximately `858.86 ms`, `63.74 ms`, and `10.20 ms` respectively. These small hosted timings strongly justify further specialization work but are not production throughput promises.

One useful non-failure was topology non-identity: the blind-bore axisymmetric reconstruction had six faces while repeated/batched 3D had five, despite equivalent valid material and successful STEP. This directly reinforces RCS-008: semantic lineage, not face-count/topology identity, must survive provider reconciliation.

Durable aggregate and representative evidence is recorded in `research/rcs-010/measured-summary-v1.json`.

## Relationship to accepted RCS-007/RCS-008/RCS-009 results

RCS-007 prohibits treating a broad fuzzy epsilon as material semantics. The RCS-010 2D state therefore acts on explicit commanded/canonical target geometry; small positive removal remains representable.

RCS-008 places durable identity in manufacturing lineage rather than regenerated faces/edges. RCS-010 can rebuild the 3D B-rep from the material profile without requiring face identity preservation. Exact-retrace recomputation is elided because operation semantics/profile prove no material change while the journal event remains.

RCS-009 permits bounded deferred topology while requiring conventional validated reconciliation at export/provider boundaries. The axisymmetric profile is a process-specialized instance with a stronger material representation for fixed-axis turning.

## Architecture recommendation

**ACCEPT:** make the verified axisymmetric axial/radial material domain a **first-class lathe geometry process provider** for the explicitly supported subset, not a universal kernel replacement.

Use the provider while material and removal-envelope semantics remain axisymmetric. Reconcile to conventional B-rep at STEP, general-topology query and provider-handoff boundaries. Preserve canonical journal/provenance independently of provider-private profile state. Keep batched 3D subtraction as an important fallback for axisymmetric operations whose specialized envelope implementation is not yet qualified, and route non-axisymmetric operations to general/mill providers.

This recommendation is architecture input for RCS-013; it does not freeze the production profile data structure, numeric type or deployment ABI.

## Open questions carried forward

- exact/conservative 2D envelopes for realistic insert geometry and nose radius;
- grooving/parting and undercut classes where radial connectivity can change;
- axisymmetric subproblem extraction after earlier non-axisymmetric machining;
- incremental inspection/topological-query behavior while the 2D state is unreconciled;
- policy for repeated lathe↔mill provider switching without topology/provenance churn;
- performance on histories much larger than the hosted set;
- production numeric representation and robust planar/profile data structure.
