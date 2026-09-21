# MC-017 — Independent engineering-consumer access and measurement probe

Status: **completed source-level consumer research with an explicit native-execution/access blocker; no consumer qualification claimed**  
Issue: #79  
Source baseline: `57689b7128d5c8f9531a1efe398ea6a12daa9804`

## Question and falsification criterion

MC-017 asks whether there is an engineering-consumer route that is meaningfully independent of the producer/candidate geometry stack, can consume the exported STEP file itself, can measure useful material/body observables under an explicit error model, and can perform a follow-on operation on the imported geometry.

The path is rejected if it shares decisive OCCT/Open CASCADE or Manifold geometry with the producer-side candidate, reads only the producer's in-memory B-rep, accepts repair/inference/partial/invalid-preserved import as success, drops or fuses material/bodies, treats approximate ray-grid measurement as exact, heals singular/exact-zero states without an approved profile, or performs the claimed downstream operation by replaying nominal machining authority instead of consuming the imported STEP result.

MC-017 is an early access/protocol investigation, not MC-E qualification and not authorization for a native campaign.

## Reconciled authority

The formal task-graph dependency is MC-001 and remains satisfied by the reviewed `MC-001/outcome.json` artifact. MC-016 is **not** added as a hidden dependency. Its accepted representability screen is consumed only as a contextual live obligation because RB-016-01 through RB-016-05 explicitly name MC-017 as an independent-consumer owner for affected output semantics.

The execution protocol requires native permits and the global `expensive-campaign` lock for native campaigns and explicitly states that readiness does not authorize expenditure or native work. No such permit was present for this task, and no pre-existing source-bound MC-1 STEP-through-independent-consumer measurement was available to adopt. MC-017 therefore records a reproducible path and exact blocker rather than fabricating observed interoperability.

## Source-level independent consumer candidate

A credible independent candidate exists in current BRL-CAD source at commit `0d745fca358e6b4655552186da4221206f4b7483` (18 September 2026). The date is recorded from that pinned upstream commit rather than inferred from the current branch:

- `step-g` reads ISO 10303-21 files, selects schema plugins from `FILE_SCHEMA`, and documents AP203/AP203e2/AP214 plus AP242 editions 1–4.
- The documented strict route exposes `--strict --exact --repair none --reject-invalid-objs`, plus machine-readable `--report` and `--summary` outputs. This is suitable for a fail-closed consumer probe because partial output, repair, inference and preserved-invalid geometry need not be accepted as success.
- The inspected `step-g` target directly links BRL-CAD `libbrep`/`librt`, STEPcode and OpenNURBS. That direct target definition does not name OCCT/Open CASCADE or Manifold. BRL-CAD's import architecture independently describes STEPcode-owned instances and OpenNURBS-based geometry/topology work.
- `gqa` is a BRL-CAD quantitative geometry analysis path over the imported `.g` database. It can report volume, bounding box, overlaps and gaps using progressively refined ray grids with explicit spacing limits.
- BRL-CAD documents Boolean union, difference and intersection, giving a concrete downstream operation family that can consume the imported object rather than replaying the producer's nominal history.

The exact external source commit, paths and Git blob identities are frozen in `consumer-probe-v1.json`.

This is **source-level independence evidence only**. Inspecting the direct target is not a complete transitive dependency audit, and no BRL-CAD binary was executed here. The result is therefore `SOURCE_VIABLE_EXECUTION_UNQUALIFIED`, not measured native interoperability.

## Fail-closed probe protocol

The recorded probe consumes the exact STEP bytes and binds them by SHA-256, records the source `FILE_SCHEMA`, producer profile and accuracy contract, then imports using the strict template:

`step-g --strict --exact --repair none --reject-invalid-objs --report IMPORT.json --summary SUMMARY.csv -o OUTPUT.g INPUT.step`

A qualifying run must return success with aggregate report outcome `complete`. Partial publication, safe repair, permissive inference and invalid-preserved B-reps are all rejection states for MC-1 qualification even if BRL-CAD can make them inspectable.

Before a native result can count, the same environment must exercise three controls: a separately sourced known-good conventional STEP solid with independently known coarse properties, a deliberately malformed/unsupported/incomplete STEP that must fail or remain non-complete under the same strict policy, and the preserved valid-but-materially-wrong negative class when a source-bound exported instance exists. A consumer saying “valid solid” is never allowed to overwrite material truth.

## Measurement method and limits

`gqa` is useful precisely because it is downstream of the STEP import and uses BRL-CAD's own analysis path. The protocol requires body/object inventory, bounding box, volume convergence, overlaps and gap diagnostics from the imported database. At least three explicitly recorded grid refinements are required, with a declared lower spacing limit and cross-view convergence checked against the task's error budget.

This measurement route is intentionally labelled **approximate**. It cannot, by itself, prove an exact-zero contact, a singular boundary or the survival of a positive micro-feature. In particular, RB-016-03 remains open unless the complete MC-1 error/sampling argument demonstrates that the consumer probe can actually discriminate the protected feature. No amount of “looks right” or converged coarse volume may erase positive material.

## Follow-on engineering-use method

The downstream operation is deliberately simple and discriminating: create a BRL-CAD-native probe cutter and evaluate a Boolean difference whose retained operand is the independently imported STEP object. Then re-run inventory and measurement on the Boolean result.

The operation only counts if it consumes the imported geometry. Replaying the nominal machining journal, substituting producer-side geometry, or reconstructing a fresh authority object is not downstream engineering use. The coarse material change must match an independently derived control within the declared measurement error budget.

This method is sufficient to define a meaningful next native probe without pretending that BRL-CAD CSG success establishes the full machining domain or STEP profile.

## Profile semantics retained

The source-level route does not close MC-016's representability blockers:

- regular nonempty manifold output has a credible independent consumer route, but execution is still unqualified;
- enclosed disjoint cavities remain under RB-016-01 until an actual source-bound STEP import preserves void topology and measurement;
- disconnected positive-volume components remain under RB-016-02 until every durable body survives independently with defensible source mapping;
- positive micro-material remains under RB-016-03 because ray-grid measurement is not automatically a micro-feature certificate;
- exact-zero contacts, touching cavities and singular pinches remain under RB-016-04 and require the versioned MC-054 profile decision without healing/fusion;
- empty material remains under RB-016-05 and must use an explicit empty-output contract rather than a fake epsilon solid or placeholder nonempty file.

## Blocker and downstream routing

**XB-017-01 — OPEN:** the BRL-CAD path is source-viable, but this task has no explicit native-execution permit/`expensive-campaign` lock and no pre-existing source-bound MC-1 STEP-through-BRL-CAD result. Consequently no actual import, measurement or follow-on engineering operation can be claimed as observed evidence.

This is not a missing software-license problem: BRL-CAD's public source provides the candidate path. It is an execution-evidence/access boundary under the programme's own safety protocol. The existing downstream task MC-043 already owns actual independent STEP consumer measurement and engineering-use continuation, so no duplicate issue is created. XB-017-01 propagates to MC-043, MC-044 and MC-052.

MC-054 is not blocked from doing its profile-decision work: it may consume the source-level candidate, fail-closed protocol and explicit limits as MC-017's reviewed artifact. Candidate/reconstruction research may also continue while preserving the MC-016 blockers. MC-045 may independently establish the native campaign harness/permit mechanism.

## Result

MC-017 is suitable for `COMPLETED_RESEARCH`: it identifies and source-binds a credible independent downstream stack, provides a defensible fail-closed import/measurement/follow-on-operation protocol, records known-good/bad control requirements and explicit profile semantics, and converts the missing execution evidence into a precise blocker rather than a false pass.

No native or paid campaign ran. No consumer result is reported as measured. MC-C remains **NOT_ESTABLISHED**; MC-B, MC-D, MC-E, MC-F and MC-1 also remain `NOT_ESTABLISHED`. MC-A remains accepted from its own evidence.

Protected source/audio/provenance semantics, canonical-journal authority, positive-volume material, durable body/lineage semantics and all historical negative evidence remain unchanged.
