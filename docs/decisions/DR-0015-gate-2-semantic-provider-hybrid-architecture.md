# DR-0015 — Gate 2 selects a semantic-provider hybrid OpenSimachinist architecture

Status: accepted  
Date: 2026-09-17  
Decision scope: initial OpenSimachinist architecture and Gate-2 exit

## Context

RCS-005 and RCS-007 through RCS-012 now provide accepted evidence for STEP conformance, tolerance/uncertainty, semantic identity, deferred topology, specialized lathe and mill strategies, and alternative/hybrid representations. The programme needs an initial architecture that can start productive implementation without pretending every pathological computational-geometry case has been solved.

The stable programme invariants require the manufacturing journal and project meaning to survive backend replacement, STEP to remain the mandatory engineering output, disconnected bodies to remain explicit, and OCCT/private backend data structures not to cross the stable MSAC/OpenSimachinist boundary.

## Decision

The programme accepts **`semantic-provider-hybrid-v1`** as the initial OpenSimachinist architecture and declares **Gate 2 — architecture-choice ready — satisfied**.

The fixed architecture rules are:

1. The canonical manufacturing journal, immutable workpiece/material-body revisions, semantic lineage, setup/tool/machine definitions and versioned policies are programme-owned durable authority.
2. Kernel topology, provider-private material domains, pending/deferred removal state, preview meshes, fallback cells/meshes/voxels and reconciled B-rep caches are replaceable derived state.
3. The stable MSAC/OpenSimachinist API carries manufacturing/revision/body/lineage/status semantics. OCCT types, Godot objects and fallback topology identities do not cross it.
4. Geometry dispatch is process/provider aware. The RCS-010 fixed-axis axisymmetric lathe domain is first-class for its qualified subset; milling follows the RCS-011 hierarchy rather than one universal sweep algorithm.
5. OCCT 8.0.1 remains the initial isolated exact/parametric B-rep, validation, reconciliation and STEP baseline. A wholesale OCCT fork is not selected.
6. Physical subtraction follows accepted regularized material semantics and may use bounded deferred topology. Connectivity/body-retention decisions, topology-dependent exact queries, provider handoff and STEP export can force reconciliation.
7. Local hybrid fallback representations are permitted only with explicit scope/error metadata and semantic provenance. They are not authoritative whole-model engineering state and must reconcile to conventional B-rep before successful STEP export.
8. Tolerance, uncertainty, contact, topology equivalence, preview, export and validation policies remain separate channels. A global fuzzy epsilon is not programme manufacturing truth.
9. Durable identity remains semantic lineage rather than B-rep face/edge identity. Geometry-recomputation elision requires semantic/provenance proof and never deletes the journal event.
10. RCS-005 remains the export authority: body selection is explicit, solid B-rep is mandatory for success, and writer success alone is insufficient.
11. Geometry/STEP workers default to process isolation with timeouts until RCS-017 supplies measured evidence allowing a narrower concurrency boundary.
12. Unresolved research remains explicit and may cause handoff, deferral or refusal. It is not disguised as solved merely to exit Gate 2.

The machine-readable architecture and ranked unresolved register are `research/rcs-013/architecture-v1.json` and `research/rcs-013/unresolved-v1.json`.

## Alternatives considered

### Deep OCCT fork as the initial kernel

Rejected initially. RCS-004 identified possible narrow fork seams but did not justify wholesale divergence. A fork would add upstream synchronization and licensing/derived-code maintenance while leaving semantic journal/provenance/process-domain problems unsolved.

### Monolithic isolated OCCT B-rep architecture

Rejected as the universal architecture while retaining OCCT as a major provider/reconciler. RCS-007 showed valid-but-wrong fuzzy outcomes, RCS-009 showed bounded deferral can avoid unnecessary topology materialization, and RCS-010/RCS-011 showed process-specific strategy value.

### Whole-model mesh/voxel/SDF authority

Rejected for the founding architecture. RCS-012's 0.5 mm occupancy candidate missed a real 0.001 mm plunge and erased a 0.001 mm positive-volume cusp/body. Conventional analytic STEP reconstruction would also remain required.

### One universal exact-arithmetic/Nef-style core

Deferred rather than selected. Exact constructions can improve numerical robustness but do not supply manufacturing semantics, provenance, operation scaling or analytic STEP reconstruction. The reviewed CGAL `Nef_3` package also carries GPL-3+ licensing implications.

### Wait for every unresolved pathology before selecting architecture

Rejected by the programme stopping rule. Gate 2 requires evidence sufficient for a productive architecture with escape routes, not a universal CAD-kernel proof.

## Evidence

### STEP and stable boundary

- DR-0004 / RCS-001 fixes an implementation-independent MSAC/OpenSimachinist semantic boundary.
- DR-0009 / RCS-005 requires conventional B-rep, explicit body preservation/selection, read-back and interoperability qualification for STEP success.

### Tolerance and provenance

- RCS-007 measured four physical-oracle failures from OCCT fuzzy `0.0001 mm` despite valid B-reps and measured approximately `7.5396 mm³` order dependence in one 100-operation chain.
- RCS-007's operation-local uncertainty model deferred 12 uncertain cases with zero decisive oracle mismatches.
- RCS-008 measured engineering-equivalent independent reconstruction with zero same-face identity matches and genuine split/merge ancestry. This supports semantic lineage rather than persistent topology identity.

### Deferred topology

- RCS-009's bounded candidate matched all eight tested physical/body oracles while reducing 227 immediate Boolean operations to six, deferring two zero-volume contacts and eliding 218 provenance-equivalent recomputations.
- Its cut-through case reconciled to two bodies and passed automated STEP round-trip evidence.

### Lathe specialization

- RCS-010 completed nine cases with zero acceptance failures and all 21 enabled STEP strategy combinations passing automated round-trip gates.
- The direct axisymmetric representation preserved true analytic planes/cylinders/cones in the measured set and preserved 100 retrace journal events while proving 99 material no-ops.

### Mill hierarchy

- RCS-011 measured 88 attempts: 76 successes, two geometric-tolerance breaches and ten contained timeouts.
- A strict 50-segment collinear canonical batch preserved measured material while reducing 50 cuts to one and faces from 1137 to 16.
- A one-shot retraced/jittered freehand batch produced a valid but materially wrong result, and all ten dense sampled-pose B-rep fallback attempts timed out. These are decisive constraints on dispatch.

### Alternative/hybrid representations

- RCS-012's exact orthogonal-cell/deferred prototype matched all 16 tested volume and body-count attempts in its narrow subset.
- Its 0.5 mm sparse occupancy prototype matched only 12/16 volume and 14/16 body-count attempts, including complete loss of a 0.001 mm cusp/body. This supports bounded local fallback with explicit resolution rather than whole-model discrete authority.

## Consequences

- RCS-014 can generate the clean OpenSimachinist founding handoff from one selected architecture rather than a list of unresolved alternatives.
- RCS-015 can define the MSAC integration boundary without depending on OCCT/private provider state.
- Production implementation can begin with vertical slices: semantic revisions/lineage, a qualified lathe route, a qualified mill route, reconciliation/validation and STEP export.
- Provider-private representations may be replaced or invalidated without migrating project meaning.
- The production status model must distinguish pending, reconciled, refusal, physical/geometric failure and STEP qualification rather than flattening all outcomes to success/failure.
- Exact dependency versions/build profiles and exporter qualifications remain observable provenance.
- RCS-017 remains useful and can optimize deployment, but its absence no longer blocks architecture selection because the current process-isolation boundary is safe and reversible.

## Reversibility

The selected **semantic ownership boundary** has low reversibility because coupling durable project meaning to private kernel objects would undermine the programme invariants. The exact providers, OCCT version, fallback libraries, physical process boundary and transport/ABI are deliberately high-reversibility choices.

A narrow OCCT fork, targeted exact arithmetic, a different B-rep engine or new local fallback may be introduced when reproducible evidence justifies it without changing saved manufacturing meaning.

## Reconsideration trigger

Reconsider the architecture if production-scale evidence shows that provider handoff/reconciliation dominates the workload, one alternative representation can satisfy the complete initial lathe/mill + STEP contract with materially lower complexity, or a critical RCS-005 conformance requirement cannot be met through the selected reconciliation boundary.

RCS-017 may revise the process-isolation deployment default if it demonstrates safe instance-local concurrency for the intended operations/configuration. Such a revision does not require changing the stable programme API.
