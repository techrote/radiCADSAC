# DR-0017 — realistic lathe tool-envelope capability

Status: **accepted**  
Date: 2026-09-17  
Issue: RCS-020 / #39  
Evidence: `research/rcs-020/measured-summary-v1.json`

## Context

DR-0013 accepted an axisymmetric axial/radial material domain as a first-class provider for a bounded fixed-axis lathe subset. Its main unresolved upstream assumption was that RCS-010 began from a completed material-removal profile instead of deriving that profile from realistic tool geometry, orientation, canonical tool motion, and reachability.

RCS-020 measured that missing seam using non-zero circular nose radii, multiple approach configurations, boring, rounded grooving/parting, explicit facing, exact retrace, and a deliberate holder-collision undercut.

## Decision

Retain the RCS-010 axisymmetric provider as the preferred first-class fixed-axis lathe material solver **only under an explicit versioned capability predicate** that establishes:

1. immutable tool geometry plus canonical trajectory generate the material envelope within a declared construction/error budget;
2. the derived material envelope is independently validated rather than self-oracled;
3. the operation satisfies the qualified tool/holder reachability predicate;
4. material-body connectivity is represented explicitly, including complete parting;
5. conventional B-rep reconciliation satisfies applicable RCS-005 automated geometry/STEP gates;
6. unqualified reconstruction properties remain explicit instead of being inferred from successful geometry or serialization.

For the RCS-020 measured subset, this admits bounded tool-derived material semantics for:

- OD turning with the tested R0.8 circular-nose external tool class;
- facing;
- shoulder formation;
- linear taper motion with the tested alternate approach configuration;
- exact/repeated finishing and retrace;
- through/blind boring with the tested R0.4 internal tool class;
- rounded grooving under the tested width/corner-radius model;
- complete parting connectivity semantics.

The tested holder-collision undercut is **not** admitted. It returned `refused_unsupported`, demonstrating that rotational representability of a target material set is insufficient proof that the specified manufacturing action belongs in the specialized provider.

Operations outside the qualified envelope/reachability predicate must hand off to another qualified provider or fail closed. They may not be converted silently into target-profile CAD operations.

### Explicitly not accepted by this decision

RCS-020 does **not** qualify:

- exact toroidal/circular-insert-nose analytic surface reconstruction in STEP from the polygon research adapter;
- general holder/fixture collision and reachability outside the bounded probe;
- arbitrary form/undercut tool families;
- live-tool, eccentric, or non-axisymmetric lathe operations.

These remain visible capability or reconstruction questions rather than hidden approximations.

## Alternatives considered

### Leave DR-0013 unchanged and defer tool-envelope derivation to implementation

Rejected. Tool-envelope derivation changes the provider admission predicate and therefore is a founding capability question rather than routine implementation detail.

### Store target radii/profiles in the journal

Rejected. It would replace direct manufacturing intent with backend-derived CAD targets and weaken the accepted journal/backend boundary. Tool/process motion remains durable intent; the provider derives its material consequences.

### Treat insert nose radius or approach angle as rendering-only properties

Rejected. The measured material profiles depend on nose radius, and the reachability predicate depends on approach/holder geometry. Geometry-critical tool properties belong to immutable tool revisions.

### Accept every rotationally symmetric target and ignore holder/reachability

Rejected by the measured undercut fixture. A conservative holder probe found collision and the correct result was refusal rather than profile approximation.

### Require exact analytic insert-nose STEP reconstruction before accepting any material specialization

Rejected as a conflation of two different correctness questions. RCS-020 demonstrates bounded material-set correctness, body semantics, conventional B-rep validity, and automated STEP read-back. Exact preferred analytic reconstruction of nose-generated surfaces remains separately unqualified and must not be inferred from those passes.

## Evidence

Hosted accepted evidence is workflow run **35275577906** from source head `9a90435a7f9cd07ab36eb9185c227c6e827e5ef9`, artifact **10519883446**, artifact ZIP SHA-256 `e595847e03123b9898dd37d83e49f2a983c4633fdf93ce7b20cec53360db1eec`.

Measured findings include:

- all **10 required cases** completed and passed their acceptance classifications;
- **8 one-body tool-derived cases** passed independent material-oracle checks plus downstream RCS-010 repeated/batched/axisymmetric comparison;
- **24/24** enabled STEP strategy read-back attempts passed;
- maximum one-body candidate/oracle material-volume error was **0.0164630791 mm³** under the predeclared `0.05 mm³` campaign budget;
- maximum OCCT strategy-to-axisymmetric volume difference was approximately **7.28e-12 mm³**;
- maximum STEP read-back volume difference was approximately **3.29e-10 mm³**;
- exact retrace retained 20 journal events while comparing **20** repeated 3D material Booleans, **1** batched Boolean, and **0** axisymmetric material Booleans;
- complete rounded parting differed from its closed-form material oracle by approximately **1.89e-05 mm³**, produced two material regions, and the independent OCCT/STEP connectivity control retained **2 solids before and after STEP read-back**;
- the undercut holder collision was detected and returned `refused_unsupported`.

The campaign also produced useful negative research-tool evidence. A uniform numerical integration oracle gave a false `0.3141255 mm³` parting discrepancy because it crossed a material discontinuity. It was replaced with an exact closed-form rounded-groove integral **without changing any acceptance tolerance**; the obsolete numerical value remains recorded diagnostically.

## Consequences

The lathe provider entry predicate is now materially stronger than DR-0013 alone: rotational symmetry is necessary but not sufficient. The backend needs the immutable tool revision, path/frame semantics, a qualified envelope construction, and a qualified reachability result before accepting specialized execution.

MSAC still does not persist RCS-020 polygons, OCCT topology, or target CAD profiles. The programme-facing boundary remains manufacturing-semantic and backend-independent.

Future exact/provenance-assisted analytic reconstruction may improve STEP surface classes without changing durable manufacturing meaning, provided it preserves the accepted material/error/body contract and is independently qualified.

## Reversibility

The qualified subset can be narrowed if later regression evidence falsifies it, or widened through new versioned tool/envelope/reachability qualification. Neither change requires coupling project meaning to OCCT topology.

After production handoff, changing the interpretation of an already accepted tool/process operation requires an explicit capability/policy version change and replay/regression evidence; it is not an invisible provider optimization.
