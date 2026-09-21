# Actual sweeps, material candidates and conventional reconstruction

Status: MC-016 early representability screen and MC-017 source-level independent-consumer probe completed with explicit open blockers; MC-C remains not established and candidate/native reconstruction remains under investigation. Owners: MC-016–044 and MC-054. [Proof](02-COMPLETENESS-ARGUMENT.md), [oracles](03-ORACLE-AND-CORPUS.md), [qualification](05-QUALIFICATION.md).

## Sweep contract

Start mandatory native cases from stock, qualified effective cutter, setup and engaged motion. A hand-authored final removal solid or oracle-derived field is a labelled analytic control, not evidence that the machining action was solved.

For each admitted tool/motion constructor derive effective cutting region, finite length/shoulders, endpoints, self-overlap, reversal, orientation and certified error. Milling flat/rounded/ball/corner-radius tools must follow the actual arbitrary admitted fixed-axis XYZ trajectory, not nearest-XY height. Side/reoriented/form/undercut operations cannot assume one top-down material interval. Meshing an already built field is distinct from native cutter-sweep construction; mesh Boolean tests need independent cutter and sweep construction certificates first.

Lathe reductions need proved rotational symmetry and correct relation between spindle phase and feed time. Taking all spindle angles independently of time can change synchronized cutting. Test internal shoulders, realistic rounded/form tools, finish retraces, tiny removal, thin webs, complete parting and re-chucking. Material whose symmetry was broken by milling or eccentric setup cannot be restored by choosing an axisymmetric provider.

Rigid transforms and line/arc/polyline/spline approximations retain source meaning and complete error accounting. A centreline fitting bound alone is not a swept-volume enclosure. Exact duplicates/collinear simplification/redundancy require contextual equivalence proof; jitter is not retrace. Report raw samples, canonical segments, unique sweeps and actual changes separately.

## Candidate roles and selection

| Role | Test first | Decisive obstruction |
|---|---|---|
| Exact arrangement/cell reference | Equality, multiple roots, full language | Only planar/algebraic subset or inexact constructions behind an exact label |
| Adaptive interval/implicit | Sound cell bounds plus critical events | Infinite refinement at equality or uncertified topology |
| Multi-/tri-directional | Multi-interval full-3D support and re-clamping | Off-ray components, hidden height-field assumptions |
| Native Manifold/mesh | Actual independently constructed cutter Booleans | Sweep error before Boolean, feature loss, failed reconstruction |
| Sparse volume/level set | Local certified refinement | Resampling/extraction changes topology or imposes a floor |
| Native B-rep/process provider | Proved admission and analytic speed | Valid-but-wrong material or universal fast-path assumptions |

Keep representation-neutral nominal expressions and certificates. Compare domain obstruction first, then bound quality, output feasibility, latency, memory, expression growth and implementation burden. Distinguish native cost from Python callback/evaluator overhead. Source rejection and minimal counterexamples precede full engines. MC-026 selects one primary and one independent challenger, records unproved gaps and produces bounded implementation blueprints; it is not a completeness declaration.

## Early output screen

MC-016 starts alongside proof/oracle development from early independently known machining witnesses, not after the complete material engine. Regular-closed material need not have a closed manifold boundary. Test singular pinches, touching shells/cavities, exact-zero/positive bridges, multiple components and empty states. An arbitrary CSG pathology without a physically plausible machining construction is not a product-domain obstruction.

Explore analytic recovery, certified trimmed boundaries, validated parametric/spline patches and qualified decompositions/grouped-solid alternatives. Any changed mapping from durable bodies to output solids, contacts or downstream meaning requires an explicit versioned MC-054 profile decision and appropriate product approval. An unresolved genuine product choice blocks only affected output tasks; it cannot be silently resolved by dropping material, adding internal faces or narrowing D. If no acceptable mapping is demonstrated, MC-1 remains blocked.

### MC-016 representability screen

The completed MC-016 screen is recorded in `research/machining-completeness/tasks/MC-016/representability-screen-v1.json`. It separates schema-level structural feasibility from native output and consumer qualification.

Historical RCS-011 provides a bounded native positive witness for regular nonempty material: 32 successful STEP-required exact-strategy attempts wrote and freshly re-read AP242DIS millimetre B-rep within that campaign's budgets. The same source is a mandatory negative control because its retrace-jitter freehand batch produced a **valid-but-materially-wrong** B-rep. B-rep validity therefore cannot stand in for material correctness.

The public STEP schema/resource definitions provide structural routes for ordinary `MANIFOLD_SOLID_BREP`, `BREP_WITH_VOIDS` for enclosed disjoint cavities, and multiple manifold-solid representation items. Structural expressibility is not interoperability proof. The screen leaves five blockers open:

- **RB-016-01** — no source-bound machining-generated native `BREP_WITH_VOIDS` write/read plus independent-consumer witness;
- **RB-016-02** — disconnected multi-solid representation lacks qualified durable-body/lineage mapping and independent-consumer preservation;
- **RB-016-03** — no qualifying native STEP witness preserves the certified positive micro-feature boundary; the historical 1 µm external comparison refused resolution-qualified authority;
- **RB-016-04** — exact-zero point/edge contact, touching cavities and singular pinches require an MC-054 profile decision plus MC-017 independent-consumer evidence; tolerance healing/fusion is forbidden;
- **RB-016-05** — empty-material output semantics and downstream handling remain unqualified; no epsilon residual solid or fake nonempty STEP may be invented.

A positive bridge/sliver remains material even when it is below a convenient writer/sewing tolerance; exact zero remains distinct from a positive bridge or gap. Multiple durable bodies may not be reduced to the largest component or fused merely because shells touch. Faceted or tessellated wrapping may be diagnostic/derived evidence where separately allowed, but it is **not** primary engineering reconstruction success.

MC-C remains **NOT_ESTABLISHED**. MC-016 is a completed bounded research artifact, not a gate pass. Its blockers propagate to candidate/output/reconstruction work until the recorded native, profile and independent-consumer evidence genuinely exists.

### MC-017 independent-consumer probe

MC-017 identifies BRL-CAD's `step-g` plus its BRL-CAD/STEPcode/OpenNURBS analysis path as a **source-viable** independent consumer candidate at pinned upstream commit `0d745fca358e6b4655552186da4221206f4b7483`. The direct `step-g` target is built on BRL-CAD `libbrep`/`librt`, STEPcode and OpenNURBS and does not name OCCT/Open CASCADE or Manifold. This is source-level independence evidence, not a complete transitive runtime dependency audit and **not measured native interoperability**.

The fail-closed probe consumes the exact STEP bytes and records their SHA-256 digest, `FILE_SCHEMA`, producer profile and accuracy contract. The required import route is `step-g --strict --exact --repair none --reject-invalid-objs` with machine-readable report and summary outputs. Only a successful `complete` import counts; partial publication, repair, permissive inference or invalid-preserved geometry is a failed qualification control even when BRL-CAD can retain it for diagnosis.

A native continuation must first prove the environment with an independently known good STEP solid and a bad/incomplete STEP that fails under the same strict policy, and must preserve the valid-but-materially-wrong class as a negative control. BRL-CAD `gqa` can then provide downstream volume, bounding-box, overlap and gap measurements over the imported database, but those are progressively refined ray-grid measurements and remain approximate. They cannot alone certify an exact-zero contact or protected micro-feature. At least three recorded refinements, an explicit grid-spacing limit and convergence within the declared error budget are required.

The meaningful follow-on operation is a BRL-CAD Boolean difference whose retained operand is the independently imported STEP object and whose cutter is created in BRL-CAD. Measurement is repeated on the result. Replaying nominal machining authority or substituting producer-side geometry does not count as downstream engineering use.

**XB-017-01** remains open: the consumer route is source-viable, but no explicit native-execution permit/`expensive-campaign` lock and no pre-existing source-bound MC-1 STEP-through-BRL-CAD result were available to MC-017. Therefore no actual import, measurement or follow-on operation is claimed. MC-043 remains the existing owner of measured independent-consumer continuation, and MC-054 may consume MC-017's source-level path and explicit limits for its output-profile decision without treating any MC-016 blocker as closed.

RB-016-01 through RB-016-05 all remain open. No cavity, disconnected-body, micro-feature, singular/contact or empty-output claim is upgraded by this source inspection. MC-C remains **NOT_ESTABLISHED**.

## Reconstruction chain

Recover exact planes/cylinders/cones/spheres/tori and other qualified analytic pieces from operation provenance where applicable. Construct exact/certified boundary pieces or approved approximate patches; compute trims, edge curves, p-curves, vertices/incidences/orientations; match exact/approximate and cross-resolution seams; bound sewing changes; build closed shells/solids; compare the actual result to nominal material.

Topology requires certified adjacency/arrangements/stratification or an equally reviewed construction, including local-to-global assembly. Cover coincident patches, tangent envelopes, repeated roots, cusps, pinches, point/edge/face contact, cavities meeting exterior and simultaneous events. Preserve voids/channels and all components. Distance or volume alone does not certify topology. Assumed feature separation must be established per case, with a route when it fails.

Durable lineage is programme-owned through splits/disappearance. Kernel handles, tessellation, greatest volume and nearest-face heuristics cannot resolve authority. Ambiguity blocks that case. Existing durable bodies do not fuse at contact.

## No disguised output success

Triangle-per-face B-rep wrapping is not usable engineering reconstruction. True manufactured planar faces are legitimate, but analytic retention, patch quality, trims, dimensions, topology and follow-on engineering operations must demonstrate the intended output. Mesh/STL is diagnostic/derived, not the primary architecture.

Compare reconstructed and fresh-read STEP solids to nominal material independently, not only to the export input B-rep. Check missing/extra material, surface/dimensional and smooth-patch angular error, bodies/voids and protected features. Candidate geometry must be tied to the oracle certificates.

Run both authority continuation from unchanged nominal history and actual engineering-use continuation from reconstructed or independently imported STEP geometry. The latter carries inherited plus new approximation error and must actually consume the exported geometry. Successful journal replay does not prove downstream usability; imported approximation must not silently replace saved authority.

## Empty outcome

Complete removal is a valid solved material/topology/body result. Record that no positive-volume workpiece remains and apply the explicit empty-output contract. Do not fabricate a residual solid or count an empty placeholder STEP as successful nonempty export.
