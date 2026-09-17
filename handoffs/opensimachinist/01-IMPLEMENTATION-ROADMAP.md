# OpenSimachinist implementation roadmap

Status: founding production roadmap  
Handoff: `opensimachinist-handoff/1.0`

## Roadmap principle

Implementation begins with **measurable vertical slices**. The production project is not tasked with “rewriting a CAD kernel.” Each stage must preserve the semantic ownership boundary and produce something executable/testable before the next layer is added.

Every milestone must keep the accepted genesis corpus/result vocabulary available as regression input and must record implementation/provider versions used to generate derived engineering state.

## Stage 0 — clean repository and deterministic build

Goal: establish a production repository whose history begins from the handoff rather than from radiCADSAC archaeology.

Deliverables:

- repository governance/`AGENTS.md` derived from this handoff;
- C++17-capable core/worker build with reproducible CMake/Ninja baseline;
- Linux CI plus documented Windows build path;
- formatting/static/unit-test jobs;
- dependency provenance manifest and license/notice directory;
- no mandatory optional fallback libraries;
- generated semantic/schema code, if any, reproducible from checked-in definitions.

Measurable exit:

- clean checkout builds/tests without access to radiCADSAC;
- CI is green on the minimal supported matrix;
- dependency manifest identifies every linked third-party component and exact pin;
- a smoke executable returns build/version/provenance information.

Initial issue: OSM-001.

## Stage 1 — semantic contract and immutable data substrate

Goal: make programme-owned state executable before geometry complexity arrives.

Deliverables:

- versioned programme API schema independent of transport;
- `msac-journal/1.0` logical concepts represented in production types;
- immutable workpiece revisions and explicit material-body sets/transitions;
- definition registry for setup/tool/machine/policies/frames;
- semantic lineage graph representation with split/merge/replacement/ambiguity;
- engineering status/diagnostics envelope;
- serialization/migration tests without OCCT types in public schemas.

Measurable exit:

- deterministic fixture journal can be parsed, validated, committed into immutable revisions, replayed and serialized/deserialized losslessly at the semantic level;
- invalid ancestry, unresolved definitions, frame cycles and unsupported contract versions fail explicitly;
- public schema inspection proves no `TopoDS_*`, OCCT handle, Godot, triangle-index or voxel/cell identity leakage;
- split/merge lineage fixture survives round-trip persistence.

Issues: OSM-002, OSM-003, OSM-004.

## Stage 2 — isolated OCCT baseline and reconciliation slice

Goal: prove the stable API can drive replaceable exact engineering machinery without making it project authority.

Deliverables:

- process-isolated worker supervisor with timeout/crash containment;
- exact OCCT 8.0.1 source/build pin and startup verification;
- backend adapter for primitive stock, simple subtraction and validation;
- conventional B-rep reconciliation result envelope;
- body-count/validity/volume/bounds/analytic-class diagnostics;
- deterministic backend build/profile provenance.

Measurable exit:

- a representative canonical operation fixture passes semantic ingress → isolated worker → validated B-rep → programme response;
- forced worker crash/timeout is contained and reported without corrupting the supervising process or semantic revision store;
- backend cache can be deleted and rebuilt from journal/revision/lineage state;
- disconnected cut-through produces explicit multiple material bodies rather than implicit deletion.

Issues: OSM-005, OSM-006.

## Stage 3 — STEP integrity vertical slice

Goal: make one end-to-end committed state exportable under the programme's four-layer acceptance model.

Deliverables:

- export candidate/body-selection API;
- AP242-family OCCT profile with exact implementation/schema naming;
- millimetre and inch unit handling;
- explicit multi-body export strategy;
- Layer A/B/C automated validation and export record/file digest;
- interoperability qualification harness/record format, initially allowed to remain `interoperability_unqualified` until independent consumer evidence exists.

Measurable exit:

- canonical stock/removal fixture produces a committed revision and conventional STEP B-rep;
- fresh read-back preserves body count, scale, required analytic classes and declared geometry/volume budgets;
- explicit subset export records selected/omitted durable body IDs;
- invalid/unreconciled state refuses export rather than emitting mesh fallback;
- release cannot claim fully qualified STEP success before Layer D evidence exists.

Issues: OSM-007 and later OSM-015.

## Stage 4 — qualified lathe vertical slice

Goal: demonstrate the first process-specialized provider behind the same semantic API.

Initial supported slice:

- fixed spindle axis;
- cylindrical OD turning;
- facing;
- shoulder;
- linear taper/chamfer-class profile;
- simple cylindrical through/blind boring;
- exact finishing retrace.

Deliverables:

- provider support predicate;
- axial/radial material state private to the provider;
- provenance/lineage events for accepted operations;
- reconciliation to analytic B-rep;
- STEP path reusing the common conformance adapter;
- explicit refusal/handoff for unsupported tool-envelope/non-axisymmetric semantics.

Measurable exit:

- selected RCS-003/RCS-010-derived fixtures meet physical/body oracles;
- repeated finishing event stays in journal while proven material no-op may avoid recomputation;
- reconstruction retains expected planes/cylinders/cones;
- provider-private state can be discarded/rebuilt;
- end-to-end STEP Layer A-C passes for the qualified subset.

Issues: OSM-008, then OSM-014 for real tool-envelope expansion.

## Stage 5 — qualified mill vertical slice

Goal: implement the accepted hierarchy without reintroducing a universal freehand shortcut.

Initial supported slice:

- fixed tool orientation;
- explicit/recognized simple operations where semantics are supplied;
- strict collinear/simple-path canonical batches with equivalence proof;
- exact per-segment cutter-envelope removal baseline;
- overlap and cut-through with explicit body semantics.

Deliverables:

- strategy dispatcher with recorded selected strategy;
- strict canonicalization/equivalence predicate;
- segment-envelope baseline;
- physical oracle checks independent of B-rep validity;
- bounded failure/timeout behavior;
- no arbitrary freehand n-ary batch fallback.

Measurable exit:

- representative RCS-003/RCS-011 simple/overlap/cut-through fixtures meet material and body oracles;
- known collinear batching case demonstrates equivalent material with lower operation/topology burden;
- a pathological freehand case is explicitly routed to pending/fallback/refusal rather than being declared success from a valid-but-wrong B-rep;
- qualified mill results pass common reconciliation and STEP Layer A-C.

Issues: OSM-009; pathological fallback qualification is OSM-013.

## Stage 6 — bounded deferred material and fallback seams

Goal: add robustness escape routes without allowing alternate representations to become silent whole-model truth.

Deliverables:

- deferred-material ledger/coordinator;
- hard reconciliation triggers for connectivity, exact topology queries, provider handoff and export;
- resource/time/query thresholds with diagnostics;
- fallback adapter capability/error/provenance contract;
- one deliberately narrow fallback prototype selected from measured workload need, not library fashion.

Measurable exit:

- proven zero-volume contact and semantic retrace can defer/elide unnecessary B-rep work while preserving intent;
- pending state cannot grow without bound under tested thresholds;
- fallback state declares resolution/error and cannot export until reconciled;
- a deliberately too-coarse fallback is rejected by the physical oracle, proving the guardrail works;
- conventional B-rep reconciliation/refusal remains authoritative at engineering boundaries.

Issues: OSM-010, OSM-011.

## Stage 7 — integrated productive-core loop

Goal: demonstrate the backend can support a useful MSAC core loop without waiting for all later robustness research.

End-to-end scenario:

1. load/create canonical stock and immutable definitions;
2. ingest canonical lathe or mill operation;
3. commit a new semantic revision and lineage events;
4. produce responsive preview/engineering status;
5. reconcile on demand;
6. inspect material bodies/geometry;
7. export selected bodies under the STEP profile;
8. delete derived caches and deterministically replay the revision;
9. compare replay result to the accepted engineering validation policy.

Measurable exit:

- at least one lathe and one mill scenario run through the same public programme API;
- revision/body/lineage identity remains stable across derived-cache deletion and replay;
- process/provider diagnostics show which implementation/profile produced derived geometry;
- corpus smoke subset runs in CI with crash/timeout isolation;
- STEP Layer A-C is green for qualified cases;
- unresolved features return explicit pending/refusal/qualification statuses rather than false success.

Issue: OSM-012.

## Parallel qualification/research after productive core exists

These items should run in parallel with ordinary implementation rather than block the entire founding project:

- OSM-013 — pathological arbitrary/self-crossing/retraced freehand mill fallback;
- OSM-014 — real insert nose radius/orientation, grooving/parting and undercut envelope qualification;
- OSM-015 — independent STEP parser/CAD/CAM consumer qualification;
- concurrency/global-state measurement equivalent to genesis RCS-017, with process isolation retained until evidence permits relaxation;
- curved/non-orthogonal fallback reconstruction;
- provider-handoff performance measurement;
- targeted exact-arithmetic experiments only at reproduced failure seams;
- release-time license compliance audit.

## Milestone discipline

A stage is not complete because code exists. Each exit condition must be covered by automated tests or a versioned reproducible qualification record. Geometry changes must be checked against physical/material oracles, not just “kernel returned valid.” Negative cases remain tests.

If a milestone cannot preserve manufacturing intent within its declared capability, the correct result is explicit pending/handoff/refusal plus a minimized regression fixture. Do not widen tolerance, drop bodies, substitute mesh output or silently switch semantic meaning to make a milestone green.
