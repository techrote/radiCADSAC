# Provenance, semantic identity, and topological naming research

Status: RCS-008 research output; runtime measurements pending hosted smoke at initial commit  
Date: 2026-09-17  
Baseline: OCCT 8.0.1, tag `V8_0_1`, commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

## Purpose and scope

RCS-008 asks what may remain *identical* when manufacturing actions regenerate, split, merge or replace B-rep topology. The programme requires durable manufacturing semantics for replay, diagnostics and later robustness policies, but it explicitly forbids making saved intent depend on one geometry kernel's private entity IDs.

The central distinction is:

- **semantic identity/lineage** answers which manufacturing concept, material body, operation, tool envelope or boundary role a state descends from;
- **topology realization** is a backend-specific face/edge/solid arrangement that realizes that meaning at one revision.

The first can be durable. The second is allowed to change.

RCS-008 does not make provenance a geometry oracle. It cannot turn two geometrically different states into the same engineering result, and it cannot excuse a failed physical/STEP validation. Geometry remains measured under RCS-003/RCS-005/RCS-006.

## Inputs and accepted constraints

**SOURCE / ACCEPTED PROGRAMME CONTRACT:** RCS-002 makes the canonical manufacturing journal authoritative, gives workpiece revisions durable material-body IDs, preserves split/merge transitions, and treats backend B-rep snapshots as derived artifacts.

**MEASURED / ACCEPTED RESEARCH INPUT:** RCS-007 found that exact repeated finishing passes were geometrically equivalent to one effective pass in its tested fixtures, but explicitly deferred any recomputation-elision authorization to RCS-008. `DR-0010` forbids using proximity, transient face IDs or global tolerance equivalence as the proof.

**SOURCE:** OCCT `BRepTools_History` records operation-local `Generated`, `Modified` and `Removed` relations for vertices, edges, faces and solids and can merge sequential histories:

- https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRepTools/BRepTools_History.hxx

**SOURCE:** OCCT Boolean API exposes this history and defines modified/generated/deleted queries; result simplification merges same-domain-unification history into the operation history:

- https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKBO/BRepAlgoAPI/BRepAlgoAPI_BuilderAlgo.hxx

**SOURCE:** `ShapeUpgrade_UnifySameDomain` explicitly records modifications while merging neighboring faces/edges on coincident geometry:

- https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKShHealing/ShapeUpgrade/ShapeUpgrade_UnifySameDomain.hxx

**SOURCE:** OCCT's `TopTools_ShapeMapHasher` equality is `TopoDS_Shape::IsSame`; it is therefore a topology-object relation inside OCCT, not a manufacturing semantic identity contract:

- https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/TopTools/TopTools_ShapeMapHasher.hxx

**SOURCE:** OCAF `TNaming_NamedShape` stores an evolution type and old/new shape pairs. It is useful prior art for persistent naming, but remains tied to OCAF/OCCT topology representation:

- https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ApplicationFramework/TKCAF/TNaming/TNaming_NamedShape.hxx
- https://occt3d.com/dev/doc/overview/html/occt_user_guides__ocaf.html

## Prior persistent-naming research

Persistent naming is a long-standing parametric-model problem rather than an OCCT-specific accident.

- J. Kripac, *A mechanism for persistently naming topological entities in history-based parametric solid models*, Solid Modeling 1995 / Computer-Aided Design 29(2), describes naming through modeling history rather than transient entity numbering. DOI: https://doi.org/10.1145/218013.218024
- D. Agbodan, D. Marcheix and G. Pierra, *Persistent Naming for Parametric Models*, WSCG 2000, emphasizes using model hierarchy/design intent to resolve names: https://dspace.zcu.cz/items/9b7bd9bf-1a69-4450-b52c-e16e79476e33
- Later persistent-identification work similarly treats split/merge and ambiguous matching as a semantic/history problem rather than assuming stable face indices; e.g. the macro-parametrics implementation study: https://academic.oup.com/jcde/article/3/2/156/5743487

**INFERENCE:** MSAC has an advantage over generic imported CAD: its canonical journal already contains unusually rich manufacturing intent. The programme should use that explicit process history rather than attempt to infer all identity from final geometry.

## Hypotheses and falsification criteria

### H1 — transient topology identity is not durable

**HYPOTHESIS:** independently replayed engineering-equivalent geometry can have different OCCT topology identity, and real split/merge/replacement operations necessarily make one-to-one identity incomplete.

**Falsification criterion:** independent reconstruction preserves a complete, stable, semantically meaningful one-to-one OCCT face/edge identity mapping through the tested replay, split, merge and replacement cases.

### H2 — operation history is useful evidence but not programme identity

**HYPOTHESIS:** `BRepTools_History` provides valuable local ancestry evidence but cannot by itself be the durable programme identity because its endpoints are OCCT topology objects and its relation semantics are operation/backend specific.

**Falsification criterion:** the tested OCCT history alone supplies backend-independent durable names for material bodies and semantic boundaries across replay/regeneration and could be serialized without exposing OCCT topology identity.

### H3 — semantic retrace proof can authorize geometry reuse

**HYPOTHESIS:** the journal can preserve every manufacturing event while a backend avoids redundant exact recomputation when provenance proves the new operation has the same target material body, setup/tool revisions and material-removal envelope, with no intervening intersecting material mutation.

**Falsification criterion:** the exact-retrace fixture changes committed material despite satisfying that semantic proof tuple.

### H4 — ambiguity must remain explicit

**HYPOTHESIS:** some split/merge cases do not contain enough manufacturing information to choose a unique descendant name. A durable model should represent an ambiguous candidate set rather than select by backend enumeration/address.

**Falsification criterion:** every deliberately symmetric ambiguous case admits a backend-independent semantic discriminator without introducing information absent from the manufacturing history.

## Candidate semantic lineage model

The proposed programme-level object is a versioned **semantic lineage graph**. Its nodes are manufacturing-semantic anchors, not raw B-rep subshapes.

Initial anchor classes are:

- `stock_region` — a semantically identified region inherited from stock definition when useful;
- `material_body` — durable connected-material identity already required by RCS-002;
- `setup_revision` — immutable setup/frame context;
- `operation` — canonical journal operation identity;
- `tool_revision` — immutable geometry-critical tool definition;
- `tool_envelope` — canonical material-removal envelope identity for an operation or recognized pass;
- `material_boundary_role` — a semantic boundary such as a finished OD, shoulder, slot floor or bore wall when uniquely justified;
- `reconciliation_event` — an explicit operation that changes/rebuilds topology representation without pretending the manufacturing history vanished.

Initial lineage relation classes are:

- `preserved` — semantic concept remains represented without a meaningful lineage fork;
- `generated` — child semantic boundary/body is introduced by an operation;
- `split` — one semantic parent produces multiple semantically distinguishable descendants;
- `merged` — multiple semantic parents become one descendant;
- `replaced` — a later realization supersedes an earlier semantic boundary realization;
- `retired` — no current realization remains, while history remains queryable;
- `ambiguous` — evidence gives multiple candidates and no accepted semantic discriminator chooses one.

IDs may be UUIDs, content-derived tokens or another implementation-independent scheme. The research prototype uses deterministic hashes of canonical semantic keys solely to demonstrate reproducibility. **The contract is not that topology gets a stable numeric ID.**

Concrete B-rep faces/edges may be attached to semantic nodes as versioned derived evidence. Such attachments can disappear and be rebuilt without rewriting journal identity.

## Split, merge, replacement, and ambiguity semantics

### Split

A topology/material split does not clone an old topology ID into two entities. A `split` relation records one parent semantic node plus the causing operation and multiple new descendant nodes.

Material-body split is stronger than face split: RCS-002 workpiece revision state must list the resulting body IDs. Boundary-level descendants can additionally carry semantic roles such as retained-side wall or parted end face when the operation defines them.

### Merge

A genuine many-to-one semantic merge creates a descendant with multiple parents. Same-domain face unification is usually a **topology reconciliation merge**, not material-body fusion; the lineage graph therefore records it as boundary/reconciliation ancestry rather than falsely rewriting material-body history.

### Replacement

Overlapping later machining commonly replaces part of an existing boundary with a new boundary. The earlier node remains historical; the new node records the later operation and ancestry. Whether some untouched portions are `preserved` and others `replaced` is decided by operation/history evidence plus geometry validation, not proximity alone.

### Ambiguity

If two descendants are geometrically/symmetrically indistinguishable and manufacturing semantics do not identify left/right, retained/scrap, feature role, or another discriminator, the model records `ambiguous` with its candidate set.

It is forbidden to resolve this by:

- face enumeration order;
- memory address or handle identity;
- an OCCT hash value;
- arbitrary nearest-neighbor tie-breaking;
- global tolerance closure.

A later operation may supply enough semantic context to resolve the ambiguity; resolution itself is a versioned lineage event.

## Deterministic replay contract

The following are expected to be stable for the same accepted journal revision and semantic-policy versions:

- canonical operation identities/order;
- durable material-body lineage identities;
- referenced setup/tool definition revisions;
- semantic lineage relation/event identities;
- uniquely justified semantic boundary roles.

The following are explicitly **not** required to remain identical:

- OCCT `TopoDS_Shape` identity;
- face/edge enumeration order;
- kernel handle/address/hash;
- concrete face/edge identity after a genuine split, merge, replacement or reconciliation rebuild;
- serialization order inside a backend snapshot.

A backend replay is correct when committed engineering state satisfies the same manufacturing/geometry contract and the semantic lineage can be reconstructed consistently—not when every face pointer is reused.

## Lathe example

Consider an OD finishing operation on `body-A` using `tool-revision-T7`, `setup-revision-S2`, targeting a canonical cylindrical removal envelope to radius 19.999 mm.

The journal records each pass. The lineage model can name:

- the retained material body;
- the finishing operation;
- the immutable tool/setup revisions;
- the material-removal envelope;
- a semantic `finished_od` boundary role if uniquely supported.

For a later exact retrace, the prototype requires this proof tuple before geometry-recompute elision is even a candidate:

1. same target material-body lineage;
2. same setup revision and coordinate interpretation;
3. same geometry-critical tool revision;
4. same canonical material-removal envelope;
5. same relevant process semantics;
6. no intervening material mutation intersecting that envelope;
7. preserve the new journal event even if exact geometry recomputation is skipped.

RCS-007 geometry equivalence is corroborating evidence, not the identity proof itself.

## Mill example

For overlapping slot passes, operation 1 can generate a semantic slot-floor/wall boundary role from the retained stock body. Operation 2 overlaps that removal envelope and may replace/split portions of the first boundary.

The lineage graph therefore records operation ancestry such as:

`slot-floor@op1 --replaced by op2--> overlap-reconciled-floor@op2`

while the workpiece material-body identity remains the retained body if connectivity did not change. OCCT `Modified`/`Generated` history can attach concrete topology evidence to this transition, but the programme node remains operation/body/role based.

If a mill cut-through creates disconnected material, the stronger RCS-002 `material_body_transition` supplies the durable body split. No "largest solid wins" rule is allowed.

## OCCT operation-history evidence

The executable RCS-008 worker uses only the pinned OCCT 8.0.1 baseline and public history facilities.

The cases deliberately exercise:

- `BRepAlgoAPI_Cut::History()` for a through split;
- a second overlapping cut for replacement/modification ancestry;
- `ShapeUpgrade_UnifySameDomain::History()` for explicit same-domain reconciliation;
- repeated lathe finishing for exact-retrace behavior;
- independent reconstruction for `TopoDS_Shape::IsSame` comparison.

History statistics count face-level modified/generated/removed relations, one-to-many source fan-out and detected many-to-one descendants. A zero count is preserved as a negative result; the harness does not manufacture ancestry that OCCT did not report.

## Naive topology identity failure

Naive persistent naming strategies tested/rejected conceptually are:

1. **save the OCCT face/edge object identity** — backend-private and unavailable after independent reconstruction/backend replacement;
2. **save face index/enumeration order** — not a semantic invariant and unstable under topology changes;
3. **nearest geometric match** — ambiguous under symmetry and can conflate boundaries inside RCS-007 uncertainty bands;
4. **globally transitive proximity identity** — explicitly rejected by RCS-007 because local metric compatibility is non-transitive and fuzzy tolerance caused valid-but-wrong material.

The independent-replay worker provides a direct executable check: it constructs the same engineering result from independently created operands, compares geometry invariants, then counts cross-result `IsSame` face matches.

The split/unification cases demonstrate the deeper limitation: even within one backend execution, topology can legitimately be one-to-many or many-to-one, so one immutable face ID cannot model ancestry without lying about what changed.

## Minimum provenance for practical robustness

The minimum useful programme provenance for a committed material operation is:

- parent workpiece revision and target material-body ID;
- canonical operation ID/type;
- immutable setup revision;
- immutable tool revision;
- canonical material-removal envelope or equivalent process-semantic descriptor;
- resulting material-body transition, if connectivity changes;
- lineage event(s) for semantically important boundary roles;
- backend realization/version evidence used to diagnose the committed result;
- explicit uncertainty/ambiguity status where matching is not unique.

This is sufficient to support candidate replay collapse, regression minimization and diagnostic traceability without persisting every transient B-rep edge.

## Interaction with RCS-007

RCS-007's local uncertainty/contact relation is deliberately **not** a lineage identity relation.

`|a-b| <= u` can justify "contact classification unresolved" for one operation. It cannot prove two boundaries are the same durable entity, and its transitive closure is forbidden as identity.

Provenance may inform tolerance policy—for example, proving that two passes reference the same canonical envelope—but it cannot override measured signed material intent. A positive cut does not become a no-op merely because provenance says it resembles a previous pass.

## Interaction with RCS-009

Deferred topology makes the separation even more important. RCS-009 may represent material/contact semantics before concrete faces/edges are committed.

The semantic lineage graph can therefore name:

- a material body;
- a pending boundary role;
- the operation/tool envelope that caused it;
- an unresolved relation;

without requiring an immediate B-rep face ID. When topology is reconciled later, concrete faces attach to those semantic nodes or new split/merge/replacement events are recorded.

RCS-008 does **not** decide how long topology may be deferred or what representation stores it; that remains RCS-009.

## STEP/export traceability

RCS-005 remains authoritative for geometric export success. STEP correctness does not depend on carrying the complete internal lineage graph.

Before export:

- selected material bodies must be explicit;
- geometry must reconcile to valid conventional B-rep;
- units, dimensions, volume, topology and analytic preservation must satisfy the RCS-005 gates;
- unresolved lineage ambiguity is acceptable only when it does not imply materially distinct exported geometry/body selection.

Optional diagnostics may map exported products/faces back to semantic nodes through names/properties or a sidecar manifest, but downstream consumers are not required to understand the full provenance graph for the STEP geometry to be correct.

If provenance ambiguity affects which material is retained/exported, export must refuse rather than guess.

## Prototype and fixture evidence

The deterministic package lives under `research/rcs-008/`. Hosted CI compiles an OCCT worker against the exact RCS-006 installation, executes all worker scenarios in separate processes, emits `rcs-008-results/1.0`, validates the semantic-lineage graph and preserves the artifact.

At the initial report commit, executable smoke measurements are intentionally not asserted as completed. The report will be reconciled with the first validated hosted run before RCS-008 is merged.

The semantic prototype itself is backend-independent: deterministic semantic IDs are hashes of canonical semantic keys, and split/merge/replacement/ambiguous relations contain no OCCT object ID. The hash choice is a research convenience, not an architecture commitment.

## Architecture recommendation

**PROVISIONAL RECOMMENDATION:** adopt a programme-level semantic lineage graph as architecture input for RCS-013, with OCCT operation history used as one backend evidence adapter rather than the durable identity system.

Recommended rules:

- material-body identity and manufacturing-operation identity remain journal/programme owned;
- semantic boundary names derive from manufacturing role/history where uniquely justified;
- topology split/merge/replacement creates explicit lineage rather than preserving a fictitious one-to-one face name;
- ambiguous matches remain ambiguous;
- concrete kernel topology identity is versioned derived state;
- OCCT `BRepTools_History`/`TNaming` are reusable implementation prior art/evidence, not the stable external contract;
- replay optimization requires semantic proof plus geometry validation; it never deletes the journal event;
- provenance informs but never replaces RCS-007 uncertainty and physical geometry checks;
- reconciliation can attach later topology to semantic nodes without forcing RCS-009 to materialize faces early;
- STEP success remains a geometry/body conformance claim, with provenance traceability optional unless needed to disambiguate selected material.

This recommendation is recorded as `DR-0011` and remains subject to RCS-013 architecture synthesis.

## Unresolved questions

**OPEN:** how much semantic boundary naming should production create eagerly versus on demand for selection/diagnostics.

**OPEN:** how to persist large lineage graphs compactly across long histories without weakening auditability.

**OPEN:** whether a content-addressed ID, UUID/event ID, or hybrid is best for production; topology must not dictate the choice.

**OPEN:** how lineage matching behaves across radically different non-OCCT representations in RCS-012.

**OPEN:** whether STEP face/product metadata should carry a small stable semantic token or whether a sidecar diagnostic manifest is cleaner across downstream CAD systems.

**OPEN:** define exact invalidation/intersection tests for replay-collapse proofs in RCS-010/RCS-011 process-specific solvers.

**OPEN:** quantify lineage/history storage and lookup cost at very large operation counts.
