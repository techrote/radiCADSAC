# Provenance, semantic identity, and topological naming research

Status: RCS-008 measured research output  
Date: 2026-09-17  
Baseline: OCCT 8.0.1, tag `V8_0_1`, commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

## Purpose and scope

RCS-008 asks what may remain *identical* when manufacturing actions regenerate, split, merge or replace B-rep topology. The programme requires durable manufacturing semantics for replay, diagnostics and robustness policies, while saved intent must remain independent of one geometry kernel's private entity IDs.

The central distinction is:

- **semantic identity/lineage** identifies manufacturing concepts, material bodies, operations, tool envelopes and boundary roles;
- **topology realization** is a backend-specific face/edge/solid arrangement that realizes that meaning at one revision.

The first can be durable. The second is allowed to change. Provenance is not a geometry oracle and cannot justify a geometry change that fails the RCS-003/RCS-005/RCS-006 physical or export checks.

## Inputs and accepted constraints

**SOURCE / ACCEPTED:** RCS-002 makes the canonical manufacturing journal authoritative, gives workpiece revisions durable material-body IDs, preserves split/merge transitions and treats backend B-rep snapshots as derived artifacts.

**MEASURED / ACCEPTED:** RCS-007 found exact repeated finishing passes geometrically equivalent to one effective pass in its tested fixtures, while `DR-0010` explicitly deferred any recomputation-elision authorization to RCS-008 and forbids using proximity/transient topology identity as the proof.

**SOURCE:** OCCT `BRepTools_History` records operation-local `Generated`, `Modified` and `Removed` relations for vertices, edges, faces and solids and can merge sequential histories:

- https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRepTools/BRepTools_History.hxx

**SOURCE:** the OCCT Boolean API exposes history and result simplification composes same-domain-unification history:

- https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKBO/BRepAlgoAPI/BRepAlgoAPI_BuilderAlgo.hxx

**SOURCE:** `ShapeUpgrade_UnifySameDomain` records modifications while merging neighboring faces/edges on coincident geometry:

- https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKShHealing/ShapeUpgrade/ShapeUpgrade_UnifySameDomain.hxx

**SOURCE:** `TopTools_ShapeMapHasher` uses `TopoDS_Shape::IsSame`, demonstrating that OCCT's topology-map equality is an OCCT topology-object relation rather than a manufacturing identity contract:

- https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/TopTools/TopTools_ShapeMapHasher.hxx

**SOURCE:** OCAF `TNaming_NamedShape` stores evolution type plus old/new shape pairs. `TNaming` is useful implementation prior art, but its concrete subject is OCCT/OCAF topology:

- https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ApplicationFramework/TKCAF/TNaming/TNaming_NamedShape.hxx
- https://occt3d.com/dev/doc/overview/html/occt_user_guides__ocaf.html

Persistent naming is a longstanding CAD problem. Kripac's history-based persistent naming work (DOI https://doi.org/10.1145/218013.218024), Agbodan/Marcheix/Pierra's design-intent hierarchy approach (https://dspace.zcu.cz/items/9b7bd9bf-1a69-4450-b52c-e16e79476e33), and later macro-parametric persistent-identification work (https://academic.oup.com/jcde/article/3/2/156/5743487) all reinforce that topology naming requires history/semantics rather than transient numbering alone.

## Hypotheses and falsification criteria

### H1 — transient topology identity is not durable

**HYPOTHESIS:** independently replayed engineering-equivalent geometry can have different OCCT topology identity, and real split/merge/replacement operations make one-to-one identity incomplete.

**Falsification criterion:** independent reconstruction preserves a complete, stable, semantically meaningful one-to-one OCCT face/edge identity mapping through replay, split, merge and replacement.

**RESULT:** not falsified. Independent reconstruction produced engineering-equivalent geometry with zero cross-result `IsSame` face matches. The split and same-domain cases additionally measured one-to-many and many-to-one ancestry.

### H2 — operation history is useful evidence but not programme identity

**HYPOTHESIS:** `BRepTools_History` supplies useful local ancestry but cannot be the durable programme identity because its endpoints are OCCT topology objects and its relation semantics are operation/backend specific.

**Falsification criterion:** tested OCCT history alone supplies backend-independent durable names for material bodies/boundaries across replay and regeneration.

**RESULT:** not falsified. History usefully captured split, overlapping-cut and same-domain ancestry, while independent replay and exact retrace regenerated equivalent topology with zero `IsSame` face identities.

### H3 — semantic retrace proof can authorize geometry reuse

**HYPOTHESIS:** the journal can preserve every manufacturing event while a backend avoids redundant exact recomputation when provenance proves the same target material body, setup/tool revisions and material-removal envelope with no intervening intersecting mutation.

**Falsification criterion:** the exact-retrace fixture changes committed material despite satisfying that proof tuple.

**RESULT:** not falsified in the smoke fixture. The repeated OD finish preserved identical measured engineering invariants/volume while all three faces were reported modified and zero face identities survived.

### H4 — ambiguity must remain explicit

**HYPOTHESIS:** some split/merge cases lack enough manufacturing information to choose a unique descendant name, so ambiguity must remain a first-class state.

**Falsification criterion:** every deliberately symmetric case admits a backend-independent semantic discriminator without adding information absent from manufacturing history.

**RESULT:** not falsified conceptually. The prototype emits an explicit two-candidate `ambiguous` relation and forbids resolution by backend enumeration/address.

## Candidate semantic lineage model

The proposed programme-level object is a versioned **semantic lineage graph** whose nodes are manufacturing-semantic anchors rather than raw B-rep subshapes.

Initial anchor classes:

- `stock_region`;
- `material_body`;
- `setup_revision`;
- `operation`;
- `tool_revision`;
- `tool_envelope`;
- `material_boundary_role`;
- `reconciliation_event`.

Initial relation classes:

- `preserved`;
- `generated`;
- `split`;
- `merged`;
- `replaced`;
- `retired`;
- `ambiguous`.

Concrete B-rep faces/edges/solids are versioned attachments/evidence. They can be replaced or rebuilt without rewriting semantic lineage. The research prototype uses deterministic hashes of canonical semantic keys to demonstrate reproducibility; this is not a production commitment to hashes or numeric topology IDs.

## Split, merge, replacement, and ambiguity semantics

### Split

A `split` relation records the semantic parent plus causing operation and multiple descendants. It never clones one topology ID into multiple entities. Material-body split uses RCS-002's stronger body-transition contract.

**MEASURED:** the through-cut changed one valid stock solid into two valid result solids. Of six source faces, OCCT history reported eight modified-face relations, four one-to-many source faces and only two source faces retaining identity.

### Merge

A genuine many-to-one semantic merge records multiple parents. Same-domain unification is usually a topology reconciliation merge, not material-body fusion.

**MEASURED:** the adjacent-box fused solid had 10 faces before explicit same-domain unification and 6 afterward, with unchanged volume to numerical noise. OCCT history reported 10 modified-face relations, four detected many-to-one descendants and zero source-face identities preserved.

### Replacement

Later overlapping machining can replace/split portions of an existing boundary while the retained material-body semantic identity remains stable.

**MEASURED:** the second overlapping mill cut changed volume from `19980 mm³` to approximately `19140 mm³`. OCCT history over the 11 source faces reported seven modified face relations, three one-to-many source faces, one removed source face and six identity-preserved source faces. A simple one-ID-per-face model therefore loses the mixed preserved/replaced/split semantics.

### Ambiguity

If manufacturing semantics do not distinguish candidates, the model records `ambiguous`; resolution by face order, address/handle/hash, nearest-neighbor tie-breaking or global tolerance closure is forbidden. A later semantic event may resolve the ambiguity explicitly.

## Deterministic replay contract

Stable for the same journal revision/policy versions:

- canonical operation identity/order;
- material-body lineage identity;
- immutable setup/tool definition revisions;
- semantic lineage event identity;
- uniquely justified semantic boundary roles.

Not stable by contract:

- OCCT `TopoDS_Shape` identity;
- face/edge enumeration order;
- kernel handles/addresses/hashes;
- concrete face/edge identity after split/merge/replacement/reconciliation;
- serialization order inside backend snapshots.

A replay is correct when committed engineering state satisfies the same manufacturing/geometry contract and semantic lineage reconstructs consistently, not when every face pointer survives.

## Lathe example

For an OD finishing operation on a retained material body, the durable proof inputs are target body lineage, immutable setup/tool revisions, canonical removal envelope and process semantics.

A later exact retrace is a candidate for skipping redundant geometry recomputation only if:

1. target material-body lineage is identical;
2. setup/coordinate interpretation is identical;
3. geometry-critical tool revision is identical;
4. canonical material-removal envelope is identical;
5. relevant process semantics are identical;
6. no intervening material mutation intersects that envelope;
7. the new journal event remains recorded.

**MEASURED:** the first and second `19.999 mm` target-radius finish results both had one valid solid, three faces, six edges and volume `75390.68405228197 mm³`. The second operation nevertheless reported all three source faces modified and zero `IsSame` face matches. This is direct evidence that semantic retrace proof is more durable than face identity.

## Mill example

For overlapping slot passes, operation 1 creates/removes material and establishes semantic boundary roles. Operation 2 overlaps that envelope and can replace/split earlier boundaries.

The lineage graph may record:

`slot-floor@op1 --replaced by op2--> overlap-reconciled-floor@op2`

while material-body identity remains the retained body when connectivity does not change. Concrete OCCT `Modified`/`Generated` history attaches backend evidence to that event. If a cut-through creates disconnected material, RCS-002 `material_body_transition` supplies the stronger durable split; there is no implicit "largest solid wins" rule.

## OCCT operation-history evidence

The executable worker uses pinned OCCT 8.0.1 public APIs:

- `BRepAlgoAPI_Cut::History()` for through split and overlapping cuts;
- `ShapeUpgrade_UnifySameDomain::History()` for explicit reconciliation;
- independent reconstruction plus `TopoDS_Shape::IsSame` comparison;
- repeated lathe finishing plus second-operation history.

Validated hosted evidence:

- workflow run `35206566700`;
- evaluated branch head `7ac2e08db6adef619b5dc693965a6e0552c307dd`;
- artifact `rcs008-provenance-smoke`, ID `10490421492`;
- digest `sha256:d0522ab66e0c5a471428a7d9a0876f8409c5cc0828321deb0dd7ceb587974baa`;
- durable compact record `research/rcs-008/measured-summary-v1.json`.

All five worker cases completed with zero worker/protocol failures.

## Naive topology identity failure

Four naive schemes are rejected as durable programme identity:

1. **OCCT face/edge object identity** — backend-private and absent across independent regeneration;
2. **face/edge enumeration index** — representation order rather than manufacturing meaning;
3. **nearest geometric match** — ambiguous under symmetry and vulnerable inside uncertainty bands;
4. **globally transitive proximity identity** — contradicted by RCS-007's measured tolerance/equivalence failure modes.

**MEASURED:** two independently created Boolean results each had one valid solid, 11 faces, 48 edges, `18240 mm³` volume and the same surface-type histogram/bounds under the harness comparison, yet cross-result `IsSame` face matches were **zero**.

This is the simplest direct failure of transient topology identity. The measured split and same-domain cases demonstrate the deeper structural failure: ancestry can genuinely be one-to-many or many-to-one even within one backend execution.

## Minimum provenance for practical robustness

Minimum useful programme provenance for a committed material operation:

- parent workpiece revision and target material-body ID;
- canonical operation ID/type;
- immutable setup revision;
- immutable tool revision;
- canonical material-removal envelope or equivalent process descriptor;
- resulting material-body transition if connectivity changes;
- lineage events for semantically important boundaries;
- backend realization/version evidence for diagnostics;
- explicit uncertainty/ambiguity status where matching is not unique.

This supports replay optimization, regression minimization and traceability without persisting every transient B-rep edge.

## Interaction with RCS-007

RCS-007's local uncertainty/contact relation is deliberately **not** lineage identity. `|a-b| <= u` may mean "classification unresolved" for one operation; it cannot prove durable sameness and its transitive closure is forbidden.

Provenance may prove two passes reference the same canonical envelope, but it cannot override signed material intent. A positive cut does not become a no-op merely because provenance says it resembles a previous pass.

## Interaction with RCS-009

Deferred topology strengthens the separation. RCS-009 may represent material/contact semantics before concrete faces/edges are committed. Semantic lineage can name material bodies, pending boundary roles, causing operations/tool envelopes and unresolved relations without early face IDs. Later reconciliation attaches concrete topology or emits split/merge/replacement lineage.

RCS-008 does not decide how long topology may be deferred or which representation stores it.

## STEP/export traceability

RCS-005 remains authoritative for export success. STEP correctness does not depend on carrying the complete lineage graph.

Before export, selected material bodies must be explicit and conventional B-rep geometry must satisfy units/dimension/volume/topology/analytic/interoperability gates. Optional names/properties or a sidecar may map exported topology to semantic nodes for diagnostics.

Unresolved provenance is acceptable only when it cannot change exported geometry/body selection. If ambiguity affects which material is retained/exported, export must refuse rather than guess.

## Prototype and fixture evidence

The deterministic package under `research/rcs-008/` compiles against the exact cached RCS-006 OCCT installation and emits `rcs-008-results/1.0`.

**MEASURED smoke summary:** 5 worker cases, 0 failures; independent replay equivalent with 0 face identities; split into 2 solids with 4 one-to-many source faces; overlapping mill replacement produced 7 modified/generated face relations; same-domain reconciliation reduced 10 faces to 6 with 4 many-to-one descendants; exact lathe retrace remained equivalent with 0 face identities. The semantic prototype additionally emits one explicit unresolved symmetric ambiguity and a complete retrace-proof tuple.

The semantic graph contains no OCCT object IDs. Hash tokens are deterministic research IDs derived from semantic keys, not a production identifier mandate.

## Architecture recommendation

**MEASURED/INFERENCE, confidence high for the tested distinction:** adopt a programme-level semantic lineage graph as RCS-013 architecture input and use OCCT operation history as one backend evidence adapter rather than the durable identity system.

Carry forward these rules:

- material-body and manufacturing-operation identity remain programme/journal owned;
- semantic boundary names derive from manufacturing role/history only when uniquely justified;
- split/merge/replacement are explicit lineage, not fictitious one-to-one persistent face names;
- ambiguous matches remain ambiguous;
- concrete kernel topology identity is derived/versioned state;
- `BRepTools_History`/`TNaming` are useful OCCT evidence/prior art, not the stable external contract;
- replay optimization requires semantic proof plus geometry validation and never deletes the journal event;
- provenance informs but does not replace RCS-007 uncertainty/physical checks;
- RCS-009 may defer topology without losing lineage;
- STEP remains a geometry/body conformance claim, with provenance metadata optional unless required to disambiguate material selection.

This recommendation is recorded as `DR-0011` and remains subject to RCS-013 architecture synthesis.

## Unresolved questions

**OPEN:** how much semantic boundary naming production should create eagerly versus on demand.

**OPEN:** how to store/index large lineage graphs compactly across very long manufacturing histories.

**OPEN:** choose production identifier mechanics (UUID/event ID/content-addressed/hybrid) without making topology dictate the choice.

**OPEN:** test lineage adapters across non-OCCT representations in RCS-012.

**OPEN:** determine whether STEP should carry a small semantic token or whether a sidecar diagnostic manifest is more interoperable.

**OPEN:** define exact invalidation/intersection tests for retrace proofs in RCS-010/RCS-011.

**OPEN:** quantify lineage/history storage and query cost at large operation counts.
