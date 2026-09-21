# MC-016 — Early machining-generated B-rep/STEP representability screen

Status: **completed research with open representability blockers; MC-C not established**  
Issue: #78  
Source baseline: `b2fac16b2285b4cb517e3e01c58a9900152327b5`

## Question and falsification criterion

MC-016 asks whether the difficult valid material states already required by MC-1 have a defensible conventional engineering representation strategy early enough to constrain later material/reconstruction work. This is a representability screen, not final STEP qualification and not permission to rewrite material until it becomes convenient for a B-rep kernel.

The task is falsified if any required obstruction class has neither a qualifying native witness nor a precise blocker; if a proposed route heals, fuses, drops or invents material; if a faceted/tessellated wrapper is counted as primary engineering success; if exact-zero and positive-volume neighbours are collapsed by tolerance; or if MC-C is promoted without the required native output and independent-consumer evidence.

## Reconciled authority and evidence

The reviewed artifact dependencies MC-002, MC-003 and MC-010 are available and remain bounded by their recorded open assumptions. Historical evidence is consumed without mutation:

- RCS-011 provides real OCCT 8.0.1 native geometry evidence. Thirty-two successful STEP-required exact-strategy attempts wrote and freshly re-read AP242DIS millimetre B-rep within that campaign's historical budgets. The same campaign also preserves the crucial counterexample that a `freehand_batch` result can be a valid B-rep and still be materially wrong, plus a sampled-pose fallback that timed out 10/10 times.
- RCS-021 preserves a two-body cut-through in its independent oracle, directional material candidate and external comparator, and preserves positive physical removal for the 1 µm plunge while the external comparator refused resolution-qualified authority. MC-010 already established that several RCS-021 implementations share decisive `field.py` mathematics, so those agreements are not promoted into independent derivations.
- RCS-012 is deterministic-model evidence only. Its exact small-cell control preserves a positive 1 µm cusp that coarse 0.5 mm occupancy erases completely. This is a useful boundary witness, not native geometry evidence.

No `research/rcs-*` file is edited or reclassified by MC-016.

## STEP structural facts used by the screen

The screen records public STEP schema/resource facts as source facts, not as evidence that a specific consumer accepts every construction.

`advanced_brep_shape_representation` permits `manifold_solid_brep` representation items and requires at least one manifold solid or mapped item; its representation item set is not restricted to one solid. `manifold_solid_brep` has one outer `closed_shell`. `brep_with_voids` is a manifold-solid subtype with one or more oriented closed-shell voids; ISO 10303-42's published resource text states the informal propositions that each void shell is disjoint from the outer shell and every other void shell and is enclosed by the outer shell.

Public schema/resource references:

- https://www.steptools.com/stds/stp_aim/html/t_advanced_brep_shape_representation.html
- https://www.steptools.com/docs/stp_aim/html/t_manifold_solid_brep.html
- https://www.steptools.com/stds/smrl/data/resource_docs/geometric_and_topological_representation/sys/6_schema.htm

These structural facts are necessary but not sufficient for MC-C: native construction, write/read fidelity, body/lineage binding and independent engineering-consumer behaviour are separate evidence obligations.

## Obstruction/strategy matrix

`representability-screen-v1.json` freezes eight classes.

| Class | Result | Route or blocker |
|---|---|---|
| Regular nonempty manifold material | bounded native witness exists | Advanced B-rep containing `MANIFOLD_SOLID_BREP`; RCS-011 establishes only bounded historical write/read feasibility |
| Enclosed disjoint cavity | structural route exists, no qualifying native witness | `BREP_WITH_VOIDS`; **RB-016-01** until native write/read plus consumer evidence exists |
| Multiple disconnected positive-volume components | material/body witness exists, not STEP qualification | multiple manifold-solid items are structurally expressible; **RB-016-02** until durable-body mapping and consumer preservation are qualified |
| Positive micro-bridge/sliver | boundary witness exists, no qualifying STEP witness | ordinary manifold route only when the feature is retained and tolerances are certified; **RB-016-03** |
| Exact-zero point/edge contact | no qualifying native output witness | decomposition/grouped-solid semantics require MC-054; **RB-016-04** |
| Touching cavity / cavity-to-exterior | no qualifying native output witness | a single `BREP_WITH_VOIDS` route is not defensible for touching shells under the recorded Part 42 propositions; **RB-016-04** |
| Singular pinch/self-contact | no qualifying native output witness | any conventional decomposition/grouped-solid rule needs explicit MC-054 semantics and independent consumer evidence; **RB-016-04** |
| Empty material | no qualifying native output witness | explicit empty outcome, never an invented residual solid or fake nonempty STEP; **RB-016-05** |

## Boundary and adversarial controls

The verifier fails closed if an unwitnessed class loses its blocker, if MC-C is changed to accepted, if multi-body output is replaced by “keep largest”, if empty material is represented by an epsilon solid, if exact contact is allowed to heal, if exact-zero/positive distinction is disabled, or if deterministic-model evidence is relabelled as native geometry. It also pins the accepted dependency and historical evidence Git blobs.

The positive/zero boundary is non-compensating. A positive bridge, cusp or sliver stays material regardless of how inconvenient it is for sewing or export. A zero-volume point/edge contact does not become a positive bridge because a kernel tolerance wants one. Multiple durable material bodies are not fused at contact and small components are not discarded. Empty material is a solved material state only under its explicit output contract.

Faceted or tessellated B-rep can remain diagnostic/derived evidence where another task permits it, but MC-016 does **not** count triangle-per-face/faceted/tessellated wrapping as usable primary engineering reconstruction.

## Negative evidence retained

MC-016 deliberately retains the RCS-011 valid-but-materially-wrong B-rep. “Valid B-rep” is therefore not accepted as a material-correctness predicate. It also retains the RCS-011 timeout result, the RCS-021 1 µm resolution refusal, and the RCS-012 coarse-occupancy deletion of a positive cusp. None becomes success through this screen.

## Blockers and downstream routing

Five explicit blockers remain:

- **RB-016-01** — cavity output lacks a source-bound machining-generated native `BREP_WITH_VOIDS` write/read plus independent-consumer witness.
- **RB-016-02** — disconnected multi-solid output is structurally expressible, but durable-body/lineage mapping and independent-consumer preservation are not qualified.
- **RB-016-03** — no qualifying native STEP witness proves preservation of the certified positive micro-feature boundary; the historical 1 µm external comparison refused authority.
- **RB-016-04** — exact-zero contact, touching-cavity and singular-pinch mappings require an explicit MC-054 engineering-output profile decision and MC-017 consumer evidence. Healing/fusing is not an allowed default.
- **RB-016-05** — empty-material engineering-output semantics and downstream handling remain unqualified; a fake residual solid or placeholder STEP is forbidden.

These blockers constrain MC-038 and later reconstruction/STEP qualification, while MC-016 remains a usable artifact input for candidate falsification. They do not narrow the machining domain.

## Result

MC-016 is suitable for `COMPLETED_RESEARCH`: every required obstruction class has either a bounded source-bound native witness and concrete route or a precise explicit blocker, the structural STEP strategies are recorded independently of candidate convenience, and adversarial rules prevent common semantic escapes.

MC-C remains **NOT_ESTABLISHED**. The screen has not demonstrated native cavity, multi-solid, micro-feature, singular/contact or empty-output qualification through an independent engineering consumer. No native or paid campaign ran. MC-B, MC-D, MC-E, MC-F and MC-1 also remain `NOT_ESTABLISHED`.

The result preserves source/audio/provenance, canonical-journal meaning, positive-volume material, durable body/lineage semantics and all historical negative evidence. Later evidence may close a blocker; it may not rewrite the producing historical record or silently change the material state being represented.
