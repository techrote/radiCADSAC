# MSAC initial production issue graph

Status: founding production issue set  
Handoff: `msac-handoff/1.0`

## Execution doctrine for every issue

Each issue below is written so an autonomous implementation agent can work from the clean MSAC repository and its checked-in founding documents. Current `main` and accepted in-repository decisions are authoritative; later explicit decisions may supersede this founding handoff.

Every issue must use branch → PR → automated checks → merge → `main` verification discipline. Acceptance criteria are product/engineering contracts, not suggestions.

## MSAC-001 — Repository foundation, Godot shell and deterministic CI

Dependencies: none.

### Autonomous implementation prompt

Read the founding specification, roadmap, bootstrap checklist and current repository governance. Work on a branch. Establish the clean Godot project/repository structure, semantic-core test path, deterministic CI, version/build reporting, dependency provenance and documented Windows developer/run path. Do not pull radiCADSAC history into the repository and do not add OCCT as a frontend dependency. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If blocked, record exact evidence and stop rather than claiming completion.

### Acceptance criteria

- clean checkout can execute the founding test/smoke path without radiCADSAC;
- Godot/product code is separated from semantic core/backend client boundaries clearly enough for headless tests;
- Linux hosted CI is green and Windows build/run instructions exist;
- version/build smoke output exists;
- dependency/provenance records do not invent a licence for the MSAC project itself;
- no OpenSimachinist/OCCT private type appears in the frontend public model.

## MSAC-002 — Programme model and OpenSimachinist semantic client contracts

Dependencies: MSAC-001.

### Autonomous implementation prompt

Read the founding specification, `msac-journal/1.0` contract summary copied into the clean repo, and OpenSimachinist programme-facing API/status requirements. Work on a branch. Implement versioned frontend semantic types for projects/definitions/revisions/material bodies and the transport-independent backend request/response/status contract. Include deterministic serialization/tests and a backend test double. Do not choose transport as semantic authority and do not expose Godot or OCCT object identity. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If blocked, record exact evidence and stop.

### Acceptance criteria

- founding request families and status vocabulary are represented/tested;
- contract versions and revision/body IDs are explicit;
- schema/public model contains no OCCT/Godot/private topology identity;
- deterministic fake backend can exercise success, pending, reconciliation, refusal and representative failure responses;
- unsupported contract versions fail explicitly.

## MSAC-003 — Machine-module, tool, setup and frame extension contracts

Dependencies: MSAC-002.

### Autonomous implementation prompt

Read the machine-module doctrine, canonical frame/definition rules and initial lathe/mill scope. Work on a branch. Implement stable MSAC-side interfaces/data models for machine kinematics/process semantics, immutable tool/setup definitions and explicit canonical frames. Provide small lathe and mill test modules sufficient to prove the extension seam without building polished machines. Keep exact geometry/provider internals behind the backend boundary. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If blocked, record evidence and stop.

### Acceptance criteria

- machine modules can expose physical axes/process/engagement state in explicit frames;
- tool/setup geometry-critical changes create new immutable revisions;
- frame parentage/transform semantics are validated;
- lathe and mill stubs exercise the same extension contract;
- no machine module owns backend-private topology.

## MSAC-004 — Device-independent manual-control and physical machine-state pipeline

Dependencies: MSAC-002.

### Autonomous implementation prompt

Read the control principles and target-user requirements. Work on a branch. Implement the device event → remappable logical action → machine physical state boundary with testable deadzone/response/profile configuration. Use a representative gamepad profile plus keyboard/testing input, but do not freeze a permanent final mapping. Ensure durable engineering data begins after device mapping. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If blocked, record evidence and stop.

### Acceptance criteria

- logical controls are independent of specific hardware IDs;
- response/deadzone changes predictably change future physical motion but cannot reinterpret committed journal values;
- simultaneous continuous controls are representable;
- control profile can be serialized as product/user config without entering authoritative operation meaning;
- deterministic test input can drive physical machine state headlessly.

## MSAC-005 — Canonical `msac-journal/1.0` producer and bounded normalization

Dependencies: MSAC-003, MSAC-004.

### Autonomous implementation prompt

Read the complete canonical-journal contract material shipped into the clean repo, including `nm-nrad-ns-q15-v1`, frame rules, semantic boundaries, bounded fitting and fixture examples. Work on a branch. Implement normalized physical trace validation, deterministic segmentation/canonicalization, explicit error budgets, canonical quantization and journal-operation generation. Prefer a simple certifiable line/polyline baseline before clever fitting. Preserve repeated/retraced operations. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If blocked, preserve the failing trace as a fixture and stop.

### Acceptance criteria

- same normalized trace/policy produces identical logical journal output;
- explicit units/frames/times/engagement/tool/setup refs validate;
- normalization never crosses semantic boundaries;
- certified error includes quantization contribution;
- fitter/simplifier falls back when it cannot certify the requested bound;
- repeated/retraced manufacturing motion remains journal-visible.

## MSAC-006 — Project persistence, immutable revision graph, undo/redo and crash recovery

Dependencies: MSAC-005.

### Autonomous implementation prompt

Read the save/versioning and immutable-history requirements. Work on a branch. Implement the durable project package/model around journal, immutable definitions, revision/body transitions and mutable selected head; implement atomic saves/checkpoints, undo/redo branching and restart recovery. Treat preview/backend caches as disposable. Include fault-injection tests for interrupted writes. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If blocked, record exact corruption/recovery evidence and stop.

### Acceptance criteria

- save/reload losslessly preserves authoritative semantic state;
- undo/redo moves the selected head without rewriting historical operations;
- editing after undo creates a branch without silently deleting old history;
- interrupted save leaves last committed project readable;
- absent/corrupt derived cache is safely discarded/rebuilt;
- unsupported schema/migration is explicit rather than silently reinterpreted.

## MSAC-007 — OpenSimachinist adapter, capability discovery and resilient request lifecycle

Dependencies: MSAC-002, MSAC-006.

### Autonomous implementation prompt

Read the stable backend request/status contract, process-isolation assumptions and integration escape routes. Work on a branch. Implement a replaceable client transport seam, capability/version discovery, request IDs, cancellation/stale-response policy, retry/replay hooks and representative crash/timeout handling. Keep the semantic project store independent of worker lifetime. Test against the fake backend first and one real backend path when available. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If the real backend is unavailable, satisfy fake/contract coverage, record the blocked integration evidence and do not falsely claim real-path acceptance.

### Acceptance criteria

- transport can be replaced without changing semantic request/response types;
- capability/version mismatch is explicit;
- stale response cannot overwrite current project-head presentation;
- worker crash/timeout leaves committed semantic state intact and retry/replay possible;
- representative backend statuses/diagnostics are preserved rather than flattened.

## MSAC-008 — Preview, authoritative engineering state and status presentation

Dependencies: MSAC-007.

### Autonomous implementation prompt

Read the preview-versus-engineering-state doctrine and status vocabulary. Work on a branch. Implement the workpiece presentation model that can show immediate/local motion, revision-tagged preview, pending/reconciled engineering state and diagnostics without conflating them. Include reconciliation request UX and explicit unsupported/failure presentation. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If blocked by missing real geometry, use deterministic test-double geometry while preserving state semantics and record the limitation.

### Acceptance criteria

- preview is keyed to semantic revision and clearly non-authoritative;
- pending/reconciled/success/refusal/failure states are distinguishable;
- an old preview/backend response cannot become current silently;
- exact query/reconciliation can be requested explicitly;
- no save/export code treats preview mesh as engineering authority.

## MSAC-009 — Thin lathe productive vertical slice

Dependencies: MSAC-003, MSAC-005, MSAC-007, MSAC-008.

### Autonomous implementation prompt

Read the qualified fixed-axis lathe capability subset and product-priority rule. Work on a branch. Build the smallest usable lathe machine interaction that drives physical state → canonical journal → OpenSimachinist → preview/reconciled state. Use cylindrical stock, one setup/tool and OD/facing-class motion; include DRO/control feedback and an exact finishing retrace fixture. Do not add broad workshop content or unsupported tool claims. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If blocked on backend qualification, record exact capability/status and preserve the journal fixture.

### Acceptance criteria

- direct simulated lathe operation produces committed manufacturing intent without feature-tree CAD;
- supported operation reaches qualified backend engineering state;
- finishing retrace stays journal-visible;
- project survives save/reload/replay;
- unsupported lathe semantics are pending/refused/labeled rather than approximated silently;
- machine/DRO state is usable enough to control the slice.

## MSAC-010 — Thin mill productive vertical slice

Dependencies: MSAC-003, MSAC-005, MSAC-007, MSAC-008.

### Autonomous implementation prompt

Read the initial fixed-orientation mill hierarchy and known negative freehand evidence. Work on a branch. Build the smallest usable mill machine interaction that drives physical state → canonical journal → backend through the same project/client substrate as lathe. Exercise a strict straight/qualified path plus overlap or cut-through/body split; include one deliberately pathological case to prove honest pending/fallback/refusal behavior. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If blocked, preserve the failing canonical path and exact backend status.

### Acceptance criteria

- direct simulated mill path commits/replays through common semantic infrastructure;
- qualified path satisfies expected material/body result;
- disconnected body is retained/presented;
- pathological/freehand case cannot become false success solely from a valid-looking preview/B-rep;
- project and backend diagnostics identify selected capability/strategy state.

## MSAC-011 — Engineering inspection, DRO and material-body management

Dependencies: MSAC-008, MSAC-009, MSAC-010.

### Autonomous implementation prompt

Read the dimensional-inspection, body-separation and reconciliation requirements. Work on a branch. Implement user-facing machine/workpiece coordinate readouts, authoritative measurement-query flow, body list/selection/lineage diagnostics and reconciliation-on-demand. Display units may be metric/imperial but canonical physical meaning is unchanged. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If a requested measurement is not authoritative for pending state, show that honestly and test the path.

### Acceptance criteria

- axis/DRO display is independent of canonical storage unit;
- authoritative vs preview measurement source is visible/tested;
- topology-dependent query can trigger reconciliation/pending state;
- multiple material bodies are listed by durable semantic IDs;
- no largest/first-body inference silently changes selection.

## MSAC-012 — STEP export UX, body selection and conformance-status presentation

Dependencies: MSAC-007, MSAC-011.

### Autonomous implementation prompt

Read `msac-step-conformance/1.0`, body-selection rules and backend export/status contract. Work on a branch. Implement export workflow for committed revisions with all-body default, explicit subset selection, units/profile, reconciliation gating, export record and precise Layer A/B/C versus independent-interoperability qualification status. Never substitute STL/mesh for failed STEP. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If no independently qualified consumer evidence exists, preserve `interoperability_unqualified` rather than claiming full qualification.

### Acceptance criteria

- unreconciled/invalid state cannot be exported as false success;
- all-body default and subset body IDs/omissions are explicit;
- unit/profile and backend/export provenance are visible in export record;
- Layer A/B/C results are preserved;
- independent interoperability status is stated precisely;
- mesh is not an engineering-success fallback.

## MSAC-013 — Integrated productive-core lifecycle and recovery qualification

Dependencies: MSAC-006, MSAC-009, MSAC-010, MSAC-011, MSAC-012.

### Autonomous implementation prompt

Read the productive-core roadmap scenario and all accepted preceding contracts. Work on a branch. Build automated/reproducible lifecycle scenarios for one lathe and one mill project covering direct operation, journal commit, preview/status, inspection/reconciliation, undo/redo/branch, save/restart, STEP export, cache deletion/replay and injected backend failure. Fix integration defects found rather than papering over them. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. Record minimized regression fixtures for any unresolved backend defect.

### Acceptance criteria

- both machine families complete the common productive lifecycle;
- semantic revision/body identities survive restart/cache deletion;
- last durable project survives injected frontend/backend failure;
- qualified STEP, unqualified interoperability and failure/refusal outcomes remain distinguishable;
- no scenario requires radiCADSAC or backend-private project state;
- core-loop regression coverage is part of CI.

## MSAC-014 — Gamepad/control usability qualification with target user

Dependencies: MSAC-004, MSAC-009, MSAC-010.

### Autonomous implementation prompt

Read the target-user and device-independent control doctrine. Work on a branch. Define a reproducible usability protocol and configurable candidate gamepad profiles for representative lathe/mill tasks. Measure fine/coarse control, simultaneous axes, discoverability and error recovery with the target-user class where available. Do not change journal semantics to fit device behavior. Add or update automated tests for mapping/configuration plus human-test documentation/results. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when acceptance criteria are genuinely satisfied. If target-user testing is unavailable, implement/test the instrumentation and protocol but leave the human-qualification criterion explicitly open.

### Acceptance criteria

- mappings remain remappable/versioned product config;
- representative tasks have measurable protocol/results;
- control defaults are evidence-based rather than hard-coded founding folklore;
- changing profile does not reinterpret committed operations;
- target-user qualification status is reported honestly.

## MSAC-015 — First-person and workpiece-follow/free-flight camera system

Dependencies: MSAC-008, MSAC-014.

### Autonomous implementation prompt

Read the camera concept and presentation-only boundary. Work on a branch. Implement first-person machinist and workpiece-follow/free-flight camera modes suitable for machine operation and engineering inspection. Keep camera transforms entirely out of setup/tool/workpiece engineering semantics. Evaluate comfort/occlusion/control interaction and persist only appropriate UI preferences. Add or update automated tests and documentation. Open a PR, repair CI/review failures, merge only after all required checks pass, verify the merge landed on `main`, and close this issue only when its acceptance criteria are genuinely satisfied. If blocked by usability evidence, record the exact issue without changing engineering frames.

### Acceptance criteria

- both founding camera concepts are usable and switchable;
- camera movement/mode switching cannot alter canonical engineering transforms;
- camera preferences are UI state, not manufacturing history;
- engineering inspection can intentionally focus/reference bodies without changing them;
- camera controls coexist with qualified machine controls without hidden binding conflicts.
