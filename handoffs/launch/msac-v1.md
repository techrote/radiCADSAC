# MSAC production-repository launch wrapper v1

Status: frozen launch wrapper; authoritative with `handoffs/genesis-release-v1.json` on accepted `main`  
Assumed repository: `techrote/MSAC`  
Frozen package tree: `e04d53756dd83089d367d756253482bebe791f32`  
Joint freeze baseline: `7f16e4fe310ac3b5e5a4d08547273efaceff0c7f`

## Launch rule

Create a new repository and a new Git history only when separately authorized. Do not fork radiCADSAC and do not copy its `.git`, branches, issues, failed experiments, or obsolete plans into the production repository.

The production founding record must cite:

- genesis repository: `https://github.com/techrote/radiCADSAC`;
- joint freeze baseline: `7f16e4fe310ac3b5e5a4d08547273efaceff0c7f`;
- handoff schema: `msac-handoff/1.0`;
- frozen package tree: `e04d53756dd83089d367d756253482bebe791f32`;
- package origin merge: `7f16e4fe310ac3b5e5a4d08547273efaceff0c7f`;
- manifest blob: `2c195f9944f2710426ef7a20eb40d5c3f96bab6a`.

Use `handoffs/msac/` as source material, especially `00-FOUNDING-SPEC.md`, `02-INITIAL-ISSUE-GRAPH.md`, `03-INTEGRATION-ESCAPE-ROUTES.md`, and `04-CLEAN-REPO-BOOTSTRAP-CHECKLIST.md`. Use the sibling frozen OpenSimachinist handoff only for shared programme-boundary details. Adapt these contents into production-native files rather than preserving the genesis directory layout mechanically.

## Initial production files

Author fresh production-native equivalents of at least:

- `README.md` with SAC product purpose, first productive lathe/mill slice, run instructions and current qualification limits;
- `AGENTS.md` with current-main authority, branch/PR/check/merge verification discipline and issue autonomy requirements;
- a current supported stable Godot project/configuration selected and pinned deliberately at production bootstrap time;
- semantic project/core modules that can be tested without rendering where practical;
- `msac-journal/1.0` producer/schema definitions and deterministic fixtures;
- immutable project/revision/material-body persistence and replay tests;
- machine-module and logical-control contracts;
- backend test double plus OpenSimachinist semantic client adapter;
- preview/authoritative-state/status presentation substrate;
- `docs/architecture.md`, `docs/project-format.md`, `docs/backend-contract.md`, `docs/testing.md`;
- dependency provenance/third-party notices mechanism;
- CI configuration.

Do not copy genesis research directories wholesale. Import only compact accepted logical contracts/fixtures required for independent production tests, and record source repository, source commit/tree, original contract version and any production-native transformation.

## CI foundation

Before broad content work, CI should prove at minimum:

- repository/document validation;
- semantic unit tests;
- journal serialization/canonicalization/replay tests;
- project save/reload and immutable revision tests;
- machine-module contract tests;
- backend test-double request/status/capability tests;
- headless Godot smoke coverage supported by the chosen Godot baseline;
- format/lint/static checks appropriate to the selected languages;
- generated schema/code reproducibility where generation is used;
- hosted Linux CI as the default automated path;
- a documented Windows build/run path for the intended developer/user environment.

Do not require a live OpenSimachinist executable for every frontend unit test. Real-backend integration and STEP qualification should remain distinct integration layers.

## Dependency, licence and provenance foundation

- Select and document the production Godot baseline rather than inheriting an unstated historical version.
- Consume OpenSimachinist only through the semantic client boundary; do not link durable frontend state to OCCT/private geometry identity.
- Keep backend transport replaceable.
- Input/controller plugins may influence future physical motion but must not redefine journal semantics.
- Do not make radiCADSAC a runtime/build dependency.
- Record exact licences/provenance for added dependencies and assets.
- If the MSAC project licence has not been explicitly selected, record it as an open production decision rather than inventing one during bootstrap.

## Founding issue creation order

Create the full autonomous prompts from `handoffs/msac/02-INITIAL-ISSUE-GRAPH.md` and preserve their dependency graph.

Start with:

1. `MSAC-001` — repository foundation, Godot shell and deterministic CI;
2. `MSAC-002` — programme model and OpenSimachinist semantic client contracts;
3. `MSAC-003` machine-module contracts and `MSAC-004` manual-control pipeline in parallel when ready;
4. `MSAC-005` canonical journal producer;
5. `MSAC-006` persistence, immutable revision graph, undo/redo and crash recovery;
6. `MSAC-007` backend adapter and `MSAC-008` authoritative/preview status presentation;
7. `MSAC-009` lathe and `MSAC-010` mill productive slices;
8. `MSAC-011` inspection/body management;
9. `MSAC-012` STEP export UX/conformance presentation;
10. `MSAC-013` integrated productive lifecycle;
11. `MSAC-014` control usability and `MSAC-015` camera system as dependencies permit.

Every issue retains branch → PR → automated checks → merge → `main` verification discipline and closes only when its acceptance criteria are genuinely satisfied.

## Boundary facts that must survive bootstrap

- Direct simulated machining is the modelling interface; do not replace the founding workflow with conventional sketch/feature-tree CAD.
- Godot scene/node state, render meshes, raw controller samples and backend-private topology are not durable engineering authority.
- The canonical project model produces `msac-journal/1.0` physical/process meaning with explicit units/frames/definitions and immutable revisions.
- The OpenSimachinist boundary is semantic/versioned; transport remains replaceable.
- Preview is non-authoritative and may lead backend reconciliation without becoming save/export truth.
- Programme-visible statuses remain distinct, including `accepted_pending`, `reconciled`, refusal/failure classes and `interoperability_unqualified`.
- Multi-body material state and body selection are explicit; there is no implicit largest/first/primary-body rule.
- STEP is the primary engineering output. Export defaults to all committed material bodies unless an explicit subset is selected.
- Worker crash/timeout must be recoverable by replay from durable semantic project state.
- Controls and cameras remain remappable/presentation concerns and must not alter historical manufacturing meaning.

## Unresolved work transfer

Preserve the substance of `03-INTEGRATION-ESCAPE-ROUTES.md`. In particular retain capability/version discovery, pathological-mill pending/fallback/refusal, lathe tool-envelope qualification, STEP interoperability status, deferred reconciliation, process-isolated worker tolerance, crash/replay recovery, semantic IDs, backend-private representation freedom, explicit migrations, remappable controls/cameras and unsupported-operation authority labels.

The frontend must not advertise backend unknowns as solved. Narrow qualified capability is preferable to broad visual behavior presented as engineering authority.

## First bootstrap completion test

Before detailed workshop content, a clean contributor should be able to clone the new production repository and, using only its own checked-in files:

- run the minimal product shell/headless smoke path;
- initialize the semantic/project core;
- exercise a deterministic fake backend advertising capabilities/status;
- exercise a machine-module stub producing explicit physical state;
- serialize/reload a project fixture;
- understand preview versus authoritative state and STEP qualification;
- locate the next dependency-ready production issue.

The new production repository may link back to radiCADSAC for archaeology. Its build, tests, runtime and day-to-day issue execution must not depend on access to radiCADSAC or to any founding conversation.
