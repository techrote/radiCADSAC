# MSAC implementation roadmap

Status: founding production roadmap  
Handoff: `msac-handoff/1.0`

## Roadmap principle

Build the **productive engineering loop first**. The first stages must prove that direct simulated lathe/mill motion can become canonical manufacturing intent, survive save/replay/undo, drive the backend, support inspection and produce STEP. The compact Gate-4 proof is **journal → backend → valid STEP**, reached through direct lathe/mill interaction rather than a conventional feature-tree detour.

Do not make publication polish, content breadth, workshop chores or game systems prerequisites for the engineering loop.

Each stage has a measurable exit. A stage is not complete merely because UI or scene code exists.

## Stage 0 — clean repository, Godot shell and CI

Goal: establish a clean MSAC production repository independent of radiCADSAC history.

Deliverables:

- current supported stable Godot baseline selected and pinned/documented;
- project structure separating product UI, machine modules, semantic project model and backend client;
- headless/unit-test path suitable for hosted CI where possible;
- Linux CI and documented Windows developer/run path;
- coding/test/governance `AGENTS.md` derived from this handoff;
- dependency/provenance notices;
- minimal application shell that reports version/build information.

Measurable exit:

- clean checkout opens/builds/tests without radiCADSAC;
- CI is green on the founding matrix;
- smoke test proves semantic core can run headlessly independently of rendering;
- no OpenSimachinist/OCCT private type is introduced into the frontend public model.

Initial issue: MSAC-001.

## Stage 1 — programme model and machine-module substrate

Goal: establish physical/product semantics before implementing detailed machine graphics.

Deliverables:

- stable MSAC-side semantic model for projects, definitions, frames, tools/setups and material-body IDs;
- versioned OpenSimachinist request/response types independent of transport;
- machine-module interface for kinematics, process state, tool/setup interaction and canonicalization hints;
- no Godot node identity in durable semantic contracts;
- fake backend/test double for capability/status testing.

Measurable exit:

- fixture definitions load/validate and survive serialization;
- machine-module test fixture produces physical state in explicit frames;
- frontend API schema includes all founding request/status families without OCCT types;
- backend test double can report capabilities, pending/reconciled/success/refusal states deterministically.

Issues: MSAC-002, MSAC-003.

## Stage 2 — canonical journal, persistence and undo/recovery

Goal: make direct physical interaction durable and replayable independently of a geometry worker.

Deliverables:

- device-independent logical control layer;
- machine physical state sampling;
- deterministic bounded canonicalization pipeline;
- `msac-journal/1.0` producer/validator;
- immutable workpiece revisions/material-body transitions;
- atomic project persistence;
- undo/redo/branch-head navigation;
- crash/restart recovery from last durable semantic revision;
- optional raw telemetry kept separate from journal authority.

Measurable exit:

- the same normalized physical trace produces deterministic logical canonical output under a pinned policy;
- rate/deadzone changes do not reinterpret existing committed history;
- repeated finishing/retrace remains journal-visible;
- save/reload preserves journal, definitions and revision graph;
- injected mid-write failure cannot corrupt the previously committed project;
- derived backend/preview caches may be absent without making the project unreadable.

Issues: MSAC-004, MSAC-005, MSAC-006.

## Stage 3 — backend client, preview and engineering-status loop

Goal: connect MSAC to OpenSimachinist semantics without coupling the render loop to exact geometry latency.

Deliverables:

- replaceable backend transport adapter;
- capability discovery/version negotiation;
- request identity/lifecycle and stale-response handling;
- responsive preview path tagged with semantic revision;
- explicit pending/reconciled/success/refusal/failure presentation;
- crash/timeout retry/replay workflow;
- reconciliation request path.

Measurable exit:

- simulated backend latency does not stall the render/control loop;
- stale response for an old UI head cannot overwrite the current preview/engineering display;
- forced crash/timeout becomes a recoverable status with durable project state intact;
- a reconciled backend state can replace/refresh preview without changing journal meaning;
- unsupported capability is refused rather than fabricated locally.

Issues: MSAC-007, MSAC-008.

## Stage 4 — thin lathe productive vertical slice

Goal: prove direct manual turning creates authoritative engineering state through the common journal/backend contract.

Minimal interaction slice:

- simple cylindrical stock;
- one setup/tool revision;
- spindle and basic feed motion;
- OD/facing-class supported action;
- optional exact finishing retrace.

Deliverables:

- usable manual controls for the slice;
- machine/DRO state;
- engagement semantics;
- canonical journal commit;
- backend capability check;
- preview plus reconciled result;
- one useful dimensional inspection;
- STEP path via common exporter later in Stage 6 if necessary.

Measurable exit:

- target operation can be performed without sketch/extrude CAD;
- committed path/revision survives save/reload/replay;
- backend result meets qualified lathe provider semantics;
- repeated finishing remains journal-visible;
- unsupported lathe motion is labeled/refused/pending rather than converted silently.

Issue: MSAC-009.

## Stage 5 — thin mill productive vertical slice

Goal: prove the same project/control/backend architecture handles a second machine family.

Minimal interaction slice:

- simple box stock;
- fixed-orientation cutter;
- straight/strictly qualified path;
- overlap or cut-through body case.

Deliverables:

- mill machine-module kinematics/control mapping;
- physical path and engagement sampling;
- bounded canonicalization;
- backend strategy/capability status presentation;
- explicit material-body split handling where exercised.

Measurable exit:

- direct manual milling creates committed journal/revision through the same API substrate as lathe;
- qualified path produces expected material/body state;
- detached body is not silently dropped;
- a known pathological/freehand case routes to pending/fallback/refusal rather than false success;
- save/replay remains deterministic at the semantic level.

Issue: MSAC-010.

## Stage 6 — inspection, material bodies and STEP productive proof

Goal: make the direct-machining loop genuinely useful as an engineering creation tool.

Deliverables:

- machine-axis/DRO display with display-unit independence;
- authoritative measurement query UX;
- body list/selection and retained/detached presentation;
- reconciliation-on-inspection where required;
- STEP export dialog/workflow;
- default all-body export and explicit subset selection;
- conformance/status presentation including `interoperability_unqualified` where applicable;
- export history/record.

Measurable exit:

- user can inspect a committed dimension and know whether it came from preview or reconciled engineering state;
- multi-body cut-through is intelligible/selectable;
- at least one lathe and one mill committed revision reach **canonical journal → backend → conventional valid STEP** Layer A-C success;
- subset export records omitted body IDs;
- unreconciled/invalid state refuses STEP rather than falling back to mesh.

Issues: MSAC-011, MSAC-012.

## Stage 7 — integrated productive core and lifecycle proof

Goal: validate that the whole core loop survives normal editing and failures before visual/game scope expands.

Scenario:

1. create stock/setup/tool definitions;
2. operate a lathe or mill manually;
3. canonicalize/commit manufacturing intent;
4. receive preview/engineering status;
5. inspect/reconcile;
6. undo, redo and create a branch;
7. save/restart/reload;
8. export selected body/bodies to STEP;
9. delete derived caches and replay;
10. compare the rebuilt engineering result under accepted validation policy;
11. inject worker failure and verify recovery.

Measurable exit:

- both machine-family smoke scenarios use the same project/journal/backend infrastructure;
- durable semantic IDs/history survive restart and cache deletion;
- backend failure cannot destroy last committed project state;
- qualified STEP outcome and unqualified/failure outcomes are distinguishable;
- all scenarios are covered by automated/reproducible tests.

Issue: MSAC-013.

## Stage 8 — control and camera qualification

Goal: improve the direct-manipulation advantage only after the engineering loop exists.

Deliverables:

- configurable logical input actions/control profiles;
- target-user gamepad usability protocol;
- fine/coarse control and simultaneous-axis evaluation;
- first-person machinist camera;
- workpiece-follow/free-flight camera;
- accessibility/input alternatives where practical;
- no camera/device state leakage into engineering transforms.

Measurable exit:

- target-user test can perform representative lathe/mill slice under a recorded control profile;
- mapping can be changed without schema/journal changes;
- camera-mode switch does not alter machine/setup/workpiece coordinates;
- usability findings can revise defaults without invalidating saved manufacturing intent.

Issues: MSAC-014, MSAC-015.

## Product-priority boundary

After Stage 7 is green, broader product work may expand in parallel: richer machines/tooling, workshop presentation, visual FX/audio, onboarding, game/publication features and additional manufacturing processes.

Before Stage 7, such work must not displace the engineering blockers needed to prove direct machining → authoritative state → inspection → STEP → replay/recovery.

## Milestone discipline

A visual result is not sufficient evidence of engineering success. Product milestones should assert physical/project/backend invariants through deterministic tests and qualified backend results.

When an interaction is outside current authoritative capability, the correct product behavior is explicit pending, handoff or refusal. A clearly labeled visual-only simulation may be acceptable for an uncommitted/unsupported interaction, but the product must not widen tolerance, discard bodies, invent geometry, silently alter a path or substitute mesh output to make the engineering workflow appear successful.
