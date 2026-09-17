# DR-0011 — Durable identity is semantic lineage, not backend topology identity

Status: accepted research decision; subject to RCS-013 architecture synthesis  
Date: 2026-09-17  
Evidence: RCS-002, RCS-004, RCS-007 and RCS-008

## Context

The canonical manufacturing journal must survive backend replacement and deterministic replay. Exact geometry operations, however, routinely split, merge, replace and regenerate B-rep faces/edges. RCS-007 also established that metric closeness/local uncertainty is not a valid global identity relation and that any exact-retrace optimization needs durable semantic/provenance proof.

OCCT 8.0.1 supplies useful operation-local ancestry through `BRepTools_History` (`Generated`, `Modified`, `Removed`) and OCAF supplies `TNaming` evolution/naming facilities, but their concrete endpoints are OCCT topology objects.

## Decision

The programme's durable provenance/identity model is a **semantic lineage graph** independent of backend topology identity.

Fixed research rules are:

1. Durable anchors name manufacturing concepts/events such as material bodies, canonical operations, setup/tool revisions, material-removal envelopes, semantic boundary roles and reconciliation events.
2. Concrete kernel faces/edges/solids are versioned derived attachments/evidence. OCCT `TopoDS_Shape` identity, hashes, addresses and enumeration order do not become durable programme identity.
3. Genuine topology changes use explicit `split`, `merged`, `replaced`, `generated`, `preserved`, `retired` or `ambiguous` lineage relations. A one-to-many or many-to-one event is not forced into fictitious one-to-one naming.
4. Ambiguous ancestry remains explicit. Backend ordering, address/hash, nearest-neighbor tie-breaking and global tolerance closure may not silently resolve it.
5. OCCT `BRepTools_History`, same-domain unification history and `TNaming` are reusable backend evidence/prior art, not the stable external MSAC/OpenSimachinist identity contract.
6. Semantic replay/retrace optimization may skip redundant exact geometry recomputation only when a versioned proof establishes the same target material-body lineage, setup/tool revisions and material-removal envelope, with no intervening intersecting material mutation. The journal event remains preserved.
7. Provenance can inform an RCS-007 contact/equivalence decision but cannot override signed manufacturing intent or measured geometry. Local uncertainty compatibility is not identity.
8. The model permits semantic nodes/relations to exist before concrete topology is materialized, so RCS-009 deferred-topology research is not forced to invent early face IDs.
9. RCS-005 STEP success remains a geometric/body conformance claim. Full internal lineage need not survive STEP, except that unresolved provenance may not be allowed to make body selection/export meaning ambiguous.

The concrete persistence/ID encoding remains open. The RCS-008 prototype's content-derived tokens demonstrate deterministic semantic keys; they are not a production requirement.

## Alternatives considered

### Persist OCCT `TopoDS_Shape` identity

Rejected. It couples saved meaning to one backend and cannot represent independent reconstruction or backend replacement. Genuine split/merge also makes one-to-one identity structurally inadequate.

### Persist face/edge indices

Rejected. Enumeration is representation order, not manufacturing meaning, and changes when topology is rebuilt.

### Match by geometry/proximity only

Rejected as the durable rule. Symmetric geometry is ambiguous; RCS-007 demonstrated that tolerance-based metric compatibility is not transitive and can erase valid signed material changes.

### Make OCAF `TNaming` the programme contract

Rejected as the stable programme boundary. It is valuable OCCT implementation prior art and may be used internally, but it would bind durable project semantics to OCAF/OCCT topology evolution.

### Give every changing face one immortal ID

Rejected. A face can genuinely split into several descendants or several boundaries can merge. Preserving one identifier through such events hides ancestry rather than expressing it.

### Discard provenance and reconstruct names heuristically after replay

Rejected. The canonical journal already contains manufacturing intent that a generic geometric matcher cannot reliably recover, and later robustness/replay diagnostics require explicit ancestry.

## Evidence

Accepted programme evidence:

- RCS-002 makes the journal and material-body transitions durable while backend geometry is derived.
- RCS-004 found `BRepTools_History`/`TNaming` useful but insufficient as backend-independent durable provenance.
- RCS-007 measured exact repeated finishing passes that were geometrically equivalent to one effective pass, while explicitly requiring RCS-008 provenance proof before optimizing replay.
- RCS-007 also measured valid-but-wrong results from a global fuzzy tolerance, showing that proximity/tolerance cannot define semantic identity.

Pinned OCCT sources:

- `BRepTools_History`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRepTools/BRepTools_History.hxx
- Boolean history API: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKBO/BRepAlgoAPI/BRepAlgoAPI_BuilderAlgo.hxx
- same-domain history: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKShHealing/ShapeUpgrade/ShapeUpgrade_UnifySameDomain.hxx
- OCAF named-shape evolution: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ApplicationFramework/TKCAF/TNaming/TNaming_NamedShape.hxx

The RCS-008 executable smoke campaign is the issue-level evidence for independent replay, split, overlapping replacement, same-domain merge and exact retrace behavior. Its validated machine-readable artifact is retained by CI and summarized in the research report before merge.

## Consequences

- RCS-009 can defer topology while retaining manufacturing ancestry independent of faces/edges.
- RCS-010/RCS-011 process solvers can use semantic tool-envelope/body lineage for safe candidate replay collapse and diagnostics.
- RCS-012 alternative representations need only adapt their realization/history evidence to the semantic lineage contract rather than reproduce OCCT naming.
- RCS-013 should version the lineage schema and choose persistence/indexing mechanics without exposing kernel-private identities.
- Regression minimization can retain the exact canonical operation ancestry associated with a geometry failure even if topology differs between backends.
- Export diagnostics may optionally map STEP topology back to semantic nodes without making that metadata the geometry-correctness oracle.

## Reversibility

Medium. The exact graph schema, ID encoding, eager/lazy boundary naming and storage/index strategy are deliberately open. Reversing the backend-independence rule would be high cost because it would couple saved history and downstream APIs to one kernel.

## Reconsideration trigger

Reconsider if later RCS-009–RCS-012 evidence demonstrates a materially simpler model that preserves split/merge/ambiguity semantics, safe replay proof, backend replaceability and RCS-005 export correctness without making topology identity durable manufacturing truth.
