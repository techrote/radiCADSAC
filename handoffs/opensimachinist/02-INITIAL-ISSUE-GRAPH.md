# Initial OpenSimachinist production issue graph

Status: founding issue plan; create these only after the clean production repository is explicitly authorized and bootstrapped.

## Execution protocol for every production issue

Each issue below is intended to be copied/adapted into the future OpenSimachinist repository. The issue itself, the production repository's `AGENTS.md`, accepted handoff documents copied into that clean repository, prerequisite implementations and current `main` are authoritative.

**Required execution sequence for every issue:** work on a branch → implement and test → open a PR → add/repair automated checks → merge only after all required checks pass → verify the merge landed on `main` → close the issue only when its acceptance criteria are genuinely satisfied. If blocked, record the exact blocker and evidence and stop without merging.

No issue may weaken the founding semantic boundary merely to satisfy its local tests.

## Dependency graph

| Issue | Purpose | Depends on |
|---|---|---|
| OSM-001 | Repository foundation, build and CI | — |
| OSM-002 | Programme API and semantic data contracts | OSM-001 |
| OSM-003 | Journal ingress and immutable revision substrate | OSM-002 |
| OSM-004 | Semantic lineage persistence | OSM-003 |
| OSM-005 | Process-isolated worker supervisor + pinned OCCT adapter | OSM-001, OSM-002 |
| OSM-006 | Generic B-rep reconciliation/validation vertical slice | OSM-003, OSM-004, OSM-005 |
| OSM-007 | STEP conformance/export vertical slice | OSM-006 |
| OSM-008 | Axisymmetric lathe provider vertical slice | OSM-004, OSM-006 |
| OSM-009 | Mill fixed-orientation strategy vertical slice | OSM-004, OSM-006 |
| OSM-010 | Deferred-material coordinator | OSM-006 |
| OSM-011 | Bounded fallback adapter seam | OSM-006, OSM-010 |
| OSM-012 | End-to-end journal-to-STEP benchmark slice | OSM-007, OSM-008, OSM-009 |
| OSM-013 | Pathological freehand mill fallback qualification | OSM-009, OSM-011 |
| OSM-014 | Real lathe tool-envelope qualification | OSM-008 |
| OSM-015 | Independent STEP interoperability qualification | OSM-007, OSM-012 |

## OSM-001 — Repository foundation, build and CI

### Purpose

Create a clean production repository with reproducible native build/test infrastructure and explicit dependency provenance, without importing the radiCADSAC Git history.

### Autonomous implementation prompt

Read the founding handoff package and current repository rules. Establish the smallest production skeleton that can build a native version/provenance smoke executable and run deterministic unit tests. Use a C++17-capable toolchain and CMake/Ninja baseline unless current repository evidence has already accepted a compatible alternative. Add Linux hosted CI and a documented Windows build path. Add third-party license/notice/provenance structure before adding geometry dependencies.

Do not add OCCT, a transport protocol, Godot bindings or optional fallback libraries merely to make the repository look complete. Do not import genesis branches/history.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- Clean checkout configures, builds and tests without radiCADSAC access.
- CI runs formatting/static/unit/smoke checks on the supported baseline.
- Windows build instructions/toolchain assumptions are explicit.
- Dependency provenance manifest and license/notice directory exist.
- Version/provenance smoke output is deterministic enough for CI assertions.
- No production API/backend architecture is accidentally coupled to build-system internals.

## OSM-002 — Programme API and semantic data contracts

### Purpose

Implement versioned programme-facing semantic schemas before selecting transport/deployment glue.

### Autonomous implementation prompt

Implement production types/schemas for the founding request families (`capabilities`, canonical operation application, revision commit/replay, material query, preview, reconciliation, reconciled inspection and STEP export), common request identity, common response identity and engineering status envelope. Preserve the handoff's public/private type boundary. Represent schema versioning/migration hooks explicitly but do not choose RPC/ABI merely as a side effect of defining data.

Add schema-level tests proving forbidden private implementation identities do not appear in the public contract and unsupported versions fail explicitly.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- All founding request families and statuses are represented/versioned.
- Common revision/body/operation/setup/tool/frame/policy identity is representable.
- Structured diagnostics can carry provider/backend build provenance without becoming durable project identity.
- Public schemas contain no `TopoDS_*`, OCCT handles, Godot objects, triangle-index identity or voxel/cell identity.
- Round-trip serialization tests are deterministic for canonical examples.
- Transport remains replaceable/unselected.

## OSM-003 — Journal ingress and immutable revision substrate

### Purpose

Make canonical manufacturing intent, immutable definitions/revisions and material-body sets executable independently of any geometry kernel.

### Autonomous implementation prompt

Implement journal ingress/validation for the `msac-journal/1.0` logical contract: canonical numeric tokens, explicit frames/transforms, immutable setup/tool/machine/policy definitions, semantic operation references and immutable workpiece revisions. Implement parent-revision/body-set checks and deterministic semantic replay of the revision graph. Derived geometry/artifact references must be optional disposable attachments only.

Use fixtures for metric/imperial-equivalent physical meaning, frame graph validation, branching history, unsupported schema versions and explicit body transitions. Do not reinterpret old operations under new policies silently.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- Canonical journal fixture validates and becomes immutable revision state.
- Definition refs/frame graph/parent ancestry/body refs are checked deterministically.
- Derived geometry caches can be absent without invalidating semantic history.
- Branching selects immutable history rather than mutating past operations.
- Invalid/overflow/cyclic/unresolved inputs return explicit status/diagnostics.
- Persistence round-trip preserves physical and revision meaning.

## OSM-004 — Semantic lineage persistence

### Purpose

Implement durable backend-independent ancestry for material bodies, operations and removal envelopes.

### Autonomous implementation prompt

Implement the accepted semantic-lineage relation model, including material-body identity, operation/tool-envelope ancestry, split, merge, replacement, retained/omitted classification hooks and explicit ambiguous ancestry. Choose a concrete persistent encoding/indexing/migration strategy without exposing backend topology IDs. Backend history may be attached as evidence only.

Include fixtures where equivalent geometry is rebuilt with different topology identity and where one source becomes multiple descendants / multiple sources reconcile to one descendant. Ambiguity must remain explicit rather than being resolved by enumeration order, object hash/address, nearest topology or tolerance closure.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- Lineage persistence survives serialize/reload/replay.
- Split/merge/replacement/ambiguity are first-class typed relations.
- Persistent IDs remain valid when all derived B-rep topology is discarded.
- Backend history evidence cannot overwrite semantic ancestry silently.
- Exact-retrace equivalence proof inputs can be expressed.
- Migration/version behavior is documented and tested.

## OSM-005 — Process-isolated worker supervisor and pinned OCCT adapter

### Purpose

Establish the founding exact B-rep dependency behind a crash/hang-containing deployment boundary.

### Autonomous implementation prompt

Integrate the exact OCCT 8.0.1 baseline (`V8_0_1`, commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`) behind programme-owned adapters. Implement out-of-process worker supervision, per-job timeouts, runtime/build-version verification and structured crash/kernel diagnostics. Preserve explicit per-call configuration where available and do not infer thread safety from process-isolated success.

Keep OCCT shared-library/build provenance explicit. Do not expose OCCT types in public contracts and do not create a deep fork without a reproduced narrow failure/decision.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- Worker refuses a mismatched OCCT runtime/source/build profile.
- Supervisor contains a forced crash and timeout and continues serving later requests.
- Structured diagnostics preserve exact backend/toolchain identity.
- No OCCT type leaks through the programme API.
- Minimal primitive/validation call succeeds through the worker boundary.
- Dependency/license provenance is updated for the exact linked configuration.

## OSM-006 — Generic B-rep reconciliation and validation vertical slice

### Purpose

Prove canonical manufacturing state can be realized as replaceable conventional engineering geometry.

### Autonomous implementation prompt

Implement a deliberately narrow generic B-rep path through the worker: create representative stock, apply simple qualified material removal, validate topology/geometry, compute body/volume/bounds/analytic metrics and return programme statuses. Implement the reconciliation envelope and cache identity so derived B-rep can be deleted and reconstructed from semantic state.

Include a cut-through/disconnected-body case. Physical/material oracles, not `BRepCheck_Analyzer` success alone, determine correctness.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- End-to-end semantic request → worker → reconciled engineering response works.
- Validity, body count, volume/bounds and analytic-class diagnostics are emitted.
- Disconnected cut-through preserves all expected bodies.
- Derived cache deletion + replay recreates equivalent engineering state within policy.
- Valid-but-wrong geometry is detected by fixture oracle.
- Failure/status taxonomy remains programme-facing and structured.

## OSM-007 — STEP conformance/export vertical slice

### Purpose

Implement Layers A-C of the founding STEP contract and the record format needed for later Layer-D qualification.

### Autonomous implementation prompt

Implement export candidates with explicit body selection, units, named export/conformance profile, geometry budgets and reconciliation state. Add AP242-family OCCT export using exact implementation/schema naming; do not label OCCT `AP242DIS` as Edition-4 certification. Validate pre-export state, serialized file structure/unit/body semantics and fresh-session geometry read-back. Add millimetre/inch equivalence and multi-body fixtures. Record deterministic export metadata/file digest.

A writer return code is not success. Refuse preview/unreconciled/invalid/unqualified requests using the stable status/error model. Never substitute STL/mesh for primary success.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- Layers A, B and C are automated for representative fixtures.
- `MANIFOLD_SOLID_BREP`/appropriate conventional solid representation is enforced for success.
- mm/in physical scale and required analytic classes survive read-back within budget.
- Default export includes all committed bodies; subset export is explicit/auditable.
- Invalid/unresolved state refuses correctly.
- Result remains `interoperability_unqualified` until Layer-D profile evidence exists.

## OSM-008 — Axisymmetric lathe provider vertical slice

### Purpose

Implement the accepted first-class fixed-axis lathe material-domain provider behind the common API.

### Autonomous implementation prompt

Implement an axial/radial material representation and support predicate for the qualified founding subset: cylindrical OD turning, facing, shoulder, linear taper/chamfer-class boundaries, cylindrical through/blind boring and exact/repeated finishing. Reconstruct conventional B-rep at reconciliation boundaries and preserve analytic planes/cylinders/cones. Preserve every journal event while permitting geometry recomputation elision only with semantic-lineage proof.

Explicitly hand off/refuse unsupported real insert envelope, grooving/undercut, eccentric/live-tool/non-axisymmetric cases. Do not hide them under a generic approximation.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- Qualified RCS-010-derived fixtures meet physical/body oracles.
- Support predicate/refusal behavior is deterministic and tested.
- Repeated retrace preserves semantic event while proven material no-op can avoid recomputation.
- Reconciliation retains expected analytic primitives and validity.
- Derived provider state can be discarded/replayed.
- Qualified cases pass the common STEP A-C pipeline.

## OSM-009 — Mill fixed-orientation strategy vertical slice

### Purpose

Implement the accepted milling hierarchy for a useful fixed-orientation subset without introducing an unsafe universal sweep shortcut.

### Autonomous implementation prompt

Implement strategy dispatch for recognized simple operations, strictly proven canonical batches and exact per-segment cutter-envelope removal. Record which strategy executed. Cover collinear simplification, overlap and cut-through. Build physical/material oracles independent from B-rep validity.

Do not implement arbitrary freehand n-ary batching as a success fallback and do not use dense sampled-pose B-rep subtraction as the universal fallback. Pathological cases must route to pending/fallback/refusal until OSM-013 or later qualification proves a bounded route.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- Representative fixed-orientation fixtures meet material/body oracles.
- Strict canonical batch demonstrates equivalent output and lower burden on its proven domain.
- Exact per-segment route provides correctness baseline.
- Known pathological freehand fixture cannot be falsely classified as success by valid B-rep alone.
- Cut-through body semantics are preserved.
- Qualified cases reconcile/export through common infrastructure.

## OSM-010 — Deferred-material coordinator

### Purpose

Implement bounded deferred topology/material work while preserving hard engineering reconciliation boundaries.

### Autonomous implementation prompt

Implement pending removal/contact state with regularized material semantics. Permit proven zero-volume contact deferral and provenance-proven recomputation elision. Force reconciliation before connectivity/body-retention decisions, topology-dependent exact queries, provider handoff that changes assumptions, export and explicit reconciled-geometry requests. Define measured resource/time/query thresholds rather than allowing pending state to grow indefinitely.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- Pending/deferred state is explicit in public status/diagnostics.
- Hard reconciliation triggers are covered by tests.
- Resource threshold forces deterministic reconciliation/refusal under stress fixture.
- Zero-volume contact can remain semantic evidence without spurious material body.
- Positive-volume intent is never erased because it is numerically inconvenient.
- Replayed/reconciled result matches physical/body oracle.

## OSM-011 — Bounded fallback adapter seam

### Purpose

Create a representation-agnostic seam for local robust alternatives without selecting an unqualified library as whole-model authority.

### Autonomous implementation prompt

Define and implement fallback adapter contracts for supported domain, error/resolution budget, source operation/body provenance, reconciliation state and refusal conditions. Implement one deliberately narrow test adapter sufficient to prove orchestration and guardrails; it may be a simple exact-cell prototype rather than a production third-party dependency.

Prove that a too-coarse/insufficient fallback result is rejected by the physical oracle and cannot export directly. Known analytic boundaries should be reconstructible from semantic/provenance knowledge before generic fitting where the test domain permits.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- Fallback capability/error/provenance/reconciliation contract is versioned/tested.
- Adapter state is local/derived and cannot become durable body identity.
- Insufficient resolution produces explicit failure, not silent geometry loss.
- Fallback state cannot satisfy STEP without conventional B-rep reconciliation.
- Core build remains usable with optional external fallback libraries disabled.

## OSM-012 — End-to-end journal-to-STEP benchmark slice

### Purpose

Demonstrate a productive backend loop through one qualified lathe and one qualified mill scenario.

### Autonomous implementation prompt

Build deterministic integration fixtures that exercise: canonical journal ingress → immutable revision/lineage → provider dispatch → engineering status/preview → reconciliation → material inspection → STEP Layers A-C → derived-cache deletion → replay → engineering equivalence comparison. Use the same public programme API for both process families and preserve provider/build provenance.

Include crash/timeout containment and a small adversarial regression subset. The integration test must accept explicit pending/refusal states for unsupported cases instead of broadening capability claims.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- One lathe and one mill scenario complete the common API path.
- Revision/body/lineage identity survives cache deletion/replay.
- Replay geometry is equivalent within the declared validation policy.
- STEP A-C passes for qualified cases.
- Adversarial smoke subset runs with process isolation/timeouts.
- Results record provider/backend/policy versions and strategy choices.

## OSM-013 — Pathological freehand mill fallback qualification

### Purpose

Resolve the highest-priority known mill capability gap without resurrecting strategies already falsified by genesis evidence.

### Autonomous implementation prompt

Research and implement candidate bounded local strategies for arbitrary/self-crossing/retraced freehand mill paths. Reproduce the genesis valid-but-wrong n-ary batching and dense sampled-pose timeout cases as negative controls. Evaluate candidates against material/volume/body oracles, operation scaling, error bounds, analytic recovery and reconciliation cost. Prefer a local replaceable fallback over changing durable architecture.

Do not call a candidate successful because it is watertight/valid. If no candidate meets the declared capability, preserve explicit refusal and record the negative result.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- Negative-control RCS-011 pathologies are reproduced or equivalently pinned.
- At least two materially different candidate strategies are evaluated or a documented evidence-based reason limits the set.
- Accepted candidate, if any, has explicit support/error/reconciliation contract and passes physical oracles.
- Failure remains refusal/pending if no candidate qualifies.
- No stable API/project semantics change is required unless separately decided.

## OSM-014 — Real lathe tool-envelope qualification

### Purpose

Extend the axisymmetric provider from simplified qualified envelopes toward real turning-tool semantics.

### Autonomous implementation prompt

Model and qualify insert nose radius, orientation, approach direction and representative grooving/parting/undercut envelopes inside or adjacent to the axisymmetric material domain. Use explicit tool-definition revisions and semantic provenance. Compare specialized-domain result with an independent/general reference on representative fixtures and verify reconciliation/analytic fidelity.

Do not claim eccentric/live-tool/non-axisymmetric support. Preserve provider handoff/refusal for those cases.

Work on a branch. Open a PR. Add/repair automated checks. Merge only after all required checks pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- Real tool geometry/revision enters support predicate deterministically.
- Representative nose-radius/orientation fixtures meet physical oracle.
- Grooving/parting connectivity/body semantics are explicitly tested before capability is claimed.
- Unsupported undercut/tool-orientation cases refuse/handoff explicitly.
- Reconciliation and STEP A-C pass where the operation is declared qualified.

## OSM-015 — Independent STEP interoperability qualification

### Purpose

Turn automated self-readback into a concrete qualified production export profile.

### Autonomous implementation prompt

Define an exact exporter/profile version and run the representative STEP fixture matrix through an independent Part-21/schema parser plus at least one independent downstream CAD/CAM consumer where available; a second consumer is preferred for release qualification. Record application/version/platform/import settings/kernel independence where known and objective body/dimension/solid/analytic observations. Store qualification records keyed to exporter/dependency/profile versions.

Do not treat screenshots as sufficient evidence and do not infer Edition-4 certification from OCCT naming. Any disagreement is recorded/investigated rather than hidden.

Work on a branch. Open a PR. Add/repair automated checks where automation is possible. Merge only after all required checks pass and required qualification records pass. Verify the merge landed on `main`; close only when the acceptance criteria are genuinely satisfied.

### Acceptance criteria

- Exact qualified profile/exporter/dependency versions are pinned.
- Independent parser accepts representative files without definite schema errors.
- At least one recorded independent CAD/CAM consumer qualification checks solid/body count, physical dimensions/scale and accessible solid/B-rep state.
- Multi-body and analytic-retention fixtures are covered where consumer exposes them.
- Qualification invalidates/requires rerun on material exporter/profile changes.
- Production can distinguish `success` from `interoperability_unqualified` based on current evidence.
