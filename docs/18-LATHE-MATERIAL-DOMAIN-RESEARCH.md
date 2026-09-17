# RCS-010 — Lathe-specialized material-domain solver research

Status: candidate implementation awaiting measured RCS-010 CI evidence  
Date: 2026-09-17  
Pinned measurement backend: OCCT 8.0.1 / `V8_0_1` / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

## Research question

Can a substantial, useful subset of fixed-axis turning be represented and updated more robustly as a 2D axial/radial material set, with conventional 3D B-rep construction deferred to explicit reconciliation boundaries, without sacrificing physical material semantics, analytic geometry, provenance, or STEP output?

The question is narrower than “can a lathe be represented in 2D?” The programme requires direct simulated machining, deterministic replay, exact retraces, very small positive removals, noisy controller input, later interoperability with general mill geometry, and conventional validated STEP output.

## Hypotheses and falsification criteria

### H1 — Axisymmetric material-domain sufficiency

**PROPOSAL:** OD turning, facing, simple shoulders/tapers and representative ID boring can be expressed as regularized updates to a piecewise axial/radial material section and reconstructed into the same physical solid as conventional 3D removal.

Falsified if representative supported cases disagree in volume/body connectivity/bounds beyond the declared comparison budget, or reconstruction creates invalid/non-conventional B-reps.

### H2 — Operation-count decoupling

**PROPOSAL:** the material-domain representation can preserve every canonical journal event while avoiding one 3D topology update per redundant/retraced event.

Falsified if replay correctness requires materializing each exact retrace into 3D topology, or if the reduced update path loses manufacturing lineage required by RCS-008.

### H3 — STEP and analytic geometry preservation

**PROPOSAL:** reconciliation by revolving the final piecewise-linear profile retains planes/cylinders/cones for the tested domain and satisfies the automated RCS-005 STEP write/read-back gates.

Falsified if supported cases require spline approximation, lose bodies, fail B-rep validation, or breach STEP geometry budgets.

### H4 — Specialized domain is not universal

**PROPOSAL:** axisymmetric material should be an explicitly dispatched process domain with controlled handoff/reconciliation, not a hidden approximation of arbitrary machining.

Falsified if there is no reliable semantic condition for knowing when axisymmetry applies or when it must yield to another provider.

## Competing strategies

The RCS-010 campaign deliberately separates representation benefit from simple batching.

**Repeated 3D subtraction** starts with a conventional cylinder, constructs the completed removal envelope, and performs one `BRepAlgoAPI_Cut` for every canonical geometry event. It models the topology-update pressure of naïve journal-to-Boolean replay while keeping cutter-envelope generation constant.

**Batched 3D subtraction** constructs the same completed removal envelope but subtracts it once. If this strategy performs as well as the 2D approach, the evidence supports batching rather than necessarily adopting a new material representation.

**Axisymmetric 2D material domain** updates a piecewise-linear radial interval field over spindle-axis coordinate `z`. The state carries outer and inner radii at section endpoints; OD/taper/facing/ID operations update that regularized material set directly. Reconciliation builds a closed `(radius,z)` section and revolves it through `2π` using the pinned OCCT worker.

All three strategies are judged against the same 2D analytic material volume and the same reconstructed target, not against screenshots or writer return codes.

## Material-domain definition

For the RCS-010 fixed-axis subset, material is represented by finite axial sections

`S_i = [z_i, z_{i+1}] × [r_inner(z), r_outer(z)]`

where inner and outer radius are linear over each section and satisfy

`0 <= r_inner(z) < r_outer(z)`.

The 3D material set is the solid of revolution of the union of these radial intervals around the spindle axis. Section volume is integrated analytically as the difference of two conical frusta. This makes volume a representation-independent oracle rather than a measurement copied from OCCT.

The prototype uses decimal arithmetic for the 2D state. This is **not** a production numeric-format decision; RCS-002 durable journal numerics remain authoritative.

## Operation semantics tested

### OD turning and shoulders

An OD operation over `[z0,z1]` applies `r_outer(z) := min(r_outer(z), target(z))`. Constant target radius represents cylindrical OD turning. Restricting the interval creates a shoulder without inventing separate feature-tree identity.

### Facing

Facing to a new front coordinate removes all material below the reconciled axial plane. Repeating the same face location is a material no-op but remains a journal event.

### Taper/chamfer-class outer boundary

A simple taper uses a linear target radius over an axial interval. Its revolution should remain a true conical surface rather than a spline approximation.

### ID boring

An ID operation applies `r_inner(z) := max(r_inner(z), target_radius)` over its axial interval. The plan contains both through and blind boring; the latter introduces an internal shoulder plane.

### Repeated/retraced finishing

The first material-changing pass updates the profile. Exact repeats are retained as canonical journal/provenance events but should not alter the material domain. This consumes the RCS-008 semantic-lineage rule; the prototype does not infer equality from transient B-rep identity.

### Noisy analogue feed

A bounded raw radial sample set is checked against its declared canonicalization envelope. The research prototype then applies one nominal canonical OD envelope. This tests the architectural separation between high-rate interaction samples and canonical geometry intent established by RCS-002; it is not a general curve-fitting algorithm.

## Tool-envelope scope

RCS-010 distinguishes **material-removal envelope semantics** from individual insert/flute rendering. The founding comparison uses an oracle-derived completed removal envelope so that the experiment isolates the representation/update strategy.

A production lathe provider would still need a tool-envelope generator that accounts for insert/nose radius, orientation, compensation convention, plunge/retract semantics, undercuts and interference. This experiment therefore supports or rejects the material-domain architecture independently of claiming those tool-geometry problems solved.

Nose radius is especially important: in an axisymmetric `(z,r)` domain a fixed-axis turning insert can often be represented by a 2D swept profile/Minkowski-style envelope, but that construction must be verified separately. RCS-010 does not silently replace a radiused insert with a sharp point in the user-facing manufacturing contract.

## Reconciliation and handoff boundaries

The 2D domain is backend-private derived state. It may remain authoritative for the supported axisymmetric operation sequence while the canonical journal remains durable authority.

Reconciliation to conventional B-rep is required at least for:

- primary STEP export;
- handoff to a non-axisymmetric mill/general provider;
- a query that requires conventional topological entities rather than material dimensions;
- setup/process transition where spindle-axis symmetry no longer applies;
- any failed/ambiguous domain-membership test.

RCS-009 regularized material semantics still apply: lower-dimensional contact metadata need not become physical material, positive-volume removal cannot be suppressed by a broad fuzzy tolerance, and body/connectivity decisions force reconciliation where needed.

## Explicit supported domain

The candidate is intended for workpiece material that is rotationally symmetric around one known spindle axis and operations whose **completed removal envelope** is also axisymmetric about that same axis. The founding useful subset includes:

- cylindrical OD turning;
- facing;
- shoulders;
- linear tapers/chamfers;
- cylindrical through and blind boring;
- exact retraces/repeated finishing;
- canonicalized analogue-controlled variants of those operations.

## Explicit exclusions and fallback requirements

The axisymmetric provider must refuse or hand off, not approximate silently, for:

- live tooling, cross holes, flats, keyways or any other non-axisymmetric removal;
- eccentric/off-centre stock or operations;
- arbitrary milling/freehand XYZ cutter envelopes;
- operations whose tool orientation/process semantics produce a non-axisymmetric material envelope;
- general 5-axis machining;
- unsupported undercuts or insert-envelope configurations until their 2D envelope semantics are proven;
- material states already containing non-axisymmetric geometry from another provider unless a valid axisymmetric subproblem can be isolated explicitly.

The handoff result is a conventional reconciled solid plus semantic lineage; no OCCT topology ID becomes the durable cross-provider identity.

## Metrics and acceptance oracle

For every hosted smoke case the campaign requires:

- all three strategies to execute;
- valid B-rep output;
- expected material-body count;
- volume agreement with the independent 2D analytic oracle;
- repeated and batched 3D results to agree with the axisymmetric reconstruction in volume and bounds;
- expected analytic surface classes in the axisymmetric result with no B-spline surface substitution;
- exact backend/version pinning;
- expected journal/provenance/canonicalization counts;
- AP242DIS manifold-solid write/read-back with unit/body/volume/bounds validation where STEP is enabled.

Topology counts and runtime are recorded as comparative evidence. They are not allowed to override a physical correctness failure.

## Relationship to accepted RCS-007/RCS-008/RCS-009 results

RCS-007 prohibits treating a broad fuzzy epsilon as material semantics. The RCS-010 2D state therefore acts on explicit commanded/canonical target geometry; small positive removal remains representable.

RCS-008 places durable identity in manufacturing lineage rather than regenerated faces/edges. RCS-010 can consequently rebuild the 3D B-rep from the material profile without requiring face identity preservation. Exact retrace recomputation is elided only because the operation semantics/profile prove no material change; the journal event is retained.

RCS-009 permits bounded deferred topology while requiring conventional validated reconciliation at export/provider boundaries. The axisymmetric profile is a process-specialized instance of that pattern, with a stronger material representation than the generic pending-removal prototype for fixed-axis turning.

## Measurement status

No architecture decision is accepted merely from the prototype design. `research/rcs-010/measured-summary-v1.json` will be created only after the pinned OCCT hosted campaign completes and its artifact is reviewed. Until then DR-0013 remains proposed.

## Architecture recommendation pending evidence

If the hypotheses pass, the recommended Gate-2 input is a **first-class axisymmetric lathe process provider**, not a universal kernel replacement. It would own supported fixed-axis turning material updates and reconcile/handoff to a conventional/general representation at explicit boundaries. A batched 3D strategy remains an important comparator and likely fallback for unsupported axisymmetric tool-envelope cases.

If the material-domain reconstruction fails geometry/STEP requirements or batching yields equivalent robustness with materially lower complexity, the recommendation must be narrowed accordingly rather than preserving the proposal by assertion.

## Open questions carried forward

- exact/conservative 2D envelopes for realistic insert geometry and nose radius;
- grooving/parting and undercut classes where radial connectivity can change;
- axisymmetric subproblem extraction after earlier non-axisymmetric machining;
- incremental inspection/topological-query behavior while the 2D state is unreconciled;
- policy for switching repeatedly between lathe and mill providers without topology/provenance churn;
- performance on histories much larger than the hosted smoke set;
- production numeric representation and robust planar/profile data structure.
