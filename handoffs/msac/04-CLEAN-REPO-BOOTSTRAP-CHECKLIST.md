# MSAC clean-repository bootstrap checklist

Status: founding bootstrap checklist  
Handoff: `msac-handoff/1.0`

## Repository creation boundary

- Create a **new Git history** for the MSAC production repository.
- Do not fork/copy the full radiCADSAC repository or its research branches/issues.
- Do not create the production repository as part of the RCS-015 handoff unless separately authorized.
- Suggested project identity: **MSAC — Machinist Simulation Aided Creator**.
- Preserve the founding architecture name `sac-machine-module-client-v1` in initial docs for traceability, not as a branding requirement.

## Initial files to author freshly

Create fresh production-native versions of at least:

- `README.md` — product purpose, first supported slice and run instructions;
- `AGENTS.md` — branch/PR/testing/engineering authority rules;
- Godot project/config and source layout;
- semantic contract/schema module or generated-code source definitions;
- test harness and deterministic fixtures;
- backend test double/client adapter;
- `docs/architecture.md` — programme-owned vs derived state;
- `docs/project-format.md` — persistence/version/migration rules;
- `docs/backend-contract.md` — semantic request/status/capability model;
- `docs/testing.md` — headless/unit/integration/user-qualification strategy;
- `THIRD_PARTY_NOTICES`/dependency provenance mechanism as appropriate.

Do not invent the MSAC repository's final licence during bootstrap if the user has not selected one. Record third-party licences accurately and leave project licensing as an explicit decision if still open.

## Dependency policy

- Select/document a current supported stable Godot baseline for the new production repo; do not assume a historical genesis version is automatically the right production pin.
- Keep the canonical semantic/project core testable without rendering where practical.
- Consume OpenSimachinist through the semantic client boundary, not by linking frontend project state to OCCT.
- Treat backend transport as replaceable.
- Optional input/controller libraries or plugins must not redefine journal semantics.
- Do not make radiCADSAC a runtime/build dependency.

## CI baseline

Initial CI should include, as soon as the corresponding files exist:

- repository/document validation;
- semantic unit tests;
- journal/project serialization/replay tests;
- machine-module contract tests;
- backend test-double contract/status tests;
- headless Godot smoke path where supported by the chosen Godot baseline;
- format/lint/static checks appropriate to selected languages;
- project save/reload fixture test;
- generated schema/code reproducibility check where generation is used;
- **Linux hosted CI** as the default automated path;
- a documented **Windows build path** for the intended developer/user environment.

Do not require a live OpenSimachinist binary for every frontend unit test. Real-backend integration should be a distinct test layer.

## Initial issue creation order

Create the founding production issues from `02-INITIAL-ISSUE-GRAPH.md`, preserving IDs in titles/descriptions if useful. The dependency order is approximately:

1. MSAC-001 repository/CI;
2. MSAC-002 semantic client model;
3. MSAC-003 machine-module contracts and MSAC-004 control pipeline in parallel;
4. MSAC-005 canonical journal producer;
5. MSAC-006 persistence/undo/recovery;
6. MSAC-007 backend adapter and MSAC-008 state presentation;
7. MSAC-009 lathe and MSAC-010 mill slices as dependencies permit;
8. MSAC-011 inspection/body management;
9. MSAC-012 STEP UX;
10. MSAC-013 integrated productive lifecycle;
11. MSAC-014/015 control/camera qualification as productive-core dependencies permit.

Each production issue should retain its autonomous prompt and acceptance criteria rather than becoming a one-line title.

## Development workflow rule

For every production issue:

1. synchronize/read current `main` and current in-repo contracts;
2. work on a dedicated branch;
3. add/update tests and documentation with implementation;
4. open a PR;
5. repair CI/review failures;
6. **merge only after all required checks pass**;
7. **verify the merge landed on `main`**;
8. close the issue only when acceptance is genuinely satisfied;
9. if blocked, record exact evidence rather than broadening semantics or claiming success.

This is the required **branch → PR → automated checks → merge → `main` verification** discipline.

## First executable milestone

Do not begin with a detailed workshop scene.

The first executable milestone should prove:

- product shell runs;
- semantic/project core initializes;
- a deterministic fake backend can advertise capabilities and states;
- a machine-module stub can produce explicit physical state;
- CI can test the above headlessly enough to catch regressions.

## First productive proof

The earliest integrated engineering goal is:

`direct lathe/mill interaction` → `physical machine state` → `msac-journal/1.0` → `OpenSimachinist semantic API` → `authoritative status/reconciliation` → `inspection` → `STEP`.

The first lathe and mill slices may be narrow. Narrow qualified capability is preferable to broad visual simulation presented as engineering truth.

## Fixture/provenance import rule

The production repo may copy **specific accepted logical fixtures/contracts** needed for independent testing, provided each copied fixture records:

- genesis source repository and source commit;
- original logical contract/version;
- whether the fixture is normative programme input or merely regression evidence;
- any production-native transformation performed during import.

Do not import entire research directories when one compact fixture/spec is sufficient.

## Handoff integrity checks before production work

Before first implementation PR, verify:

- the six human-readable MSAC handoff documents and manifest are available as source material;
- the OpenSimachinist programme-facing boundary is represented without backend-private types;
- `msac-journal/1.0` concepts/numeric/frame rules required by the first slice are locally documented/testable;
- STEP is described as primary engineering output, not optional polish;
- preview is explicitly non-authoritative;
- multi-body semantics are not reduced to one “primary” body;
- no unresolved research question is asserted as solved;
- integration escape routes are retained.

## Do not do during bootstrap

- Do not copy obsolete/rejected genesis research into production docs as requirements.
- Do not use Godot scene/node IDs as project identity.
- Do not store controller axes/deadzones as canonical machining operations.
- Do not implement a sketch/extrude feature-tree CAD workflow as the primary interaction shortcut.
- Do not bind the frontend public model to OCCT.
- Do not treat preview mesh as save/export authority.
- Do not silently discard detached material.
- Do not report `interoperability_unqualified` STEP as fully qualified.
- Do not make game/publication polish a prerequisite for the first engineering vertical slices.

## Genesis reference

RCS-015 was generated from radiCADSAC `main` at:

`2e77ea087b01ac1415c4c76ff1dc0661aab286fb`

The important clean source material is this `handoffs/msac/` package plus the sibling OpenSimachinist handoff when shared contract details are needed. The production history should reference radiCADSAC by commit/URL for archaeology rather than importing its Git history.

RCS-016 will later cross-check and freeze both handoffs together; that future freeze does not prevent MSAC implementation planning from being coherent now.
