# OpenSimachinist production-repository launch wrapper v1

Status: frozen launch wrapper; authoritative with `handoffs/genesis-release-v1.json` on accepted `main`  
Assumed repository: `techrote/OpenSimachinist`  
Frozen package tree: `d4793b03f31bd9fd58efcea94afba2f69fa3f7f3`  
Joint freeze baseline: `7f16e4fe310ac3b5e5a4d08547273efaceff0c7f`

## Launch rule

Create a new repository and a new Git history only when separately authorized. Do not fork radiCADSAC and do not copy its `.git`, branches, issues, failed experiments, or obsolete plans into the production repository.

The production founding record must cite:

- genesis repository: `https://github.com/techrote/radiCADSAC`;
- joint freeze baseline: `7f16e4fe310ac3b5e5a4d08547273efaceff0c7f`;
- handoff schema: `opensimachinist-handoff/1.0`;
- frozen package tree: `d4793b03f31bd9fd58efcea94afba2f69fa3f7f3`;
- package origin merge: `2e77ea087b01ac1415c4c76ff1dc0661aab286fb`;
- manifest blob: `2d53fc62c8ec5866eff686483ac721983df03b64`.

Use `handoffs/opensimachinist/` as source material, especially `00-FOUNDING-SPEC.md`, `02-INITIAL-ISSUE-GRAPH.md`, `03-UNRESOLVED-RESEARCH-REGISTER.md`, and `04-CLEAN-REPO-BOOTSTRAP-CHECKLIST.md`. Adapt their content into production-native files instead of mechanically preserving the genesis directory layout.

## Initial production files

Author fresh production-native equivalents of at least:

- `README.md` with product purpose, qualified first slice, build/run instructions and current capability limits;
- `AGENTS.md` with current-main authority, branch/PR/check/merge verification discipline, evidence rules and issue autonomy requirements;
- `CMakeLists.txt` plus a deterministic C++17 build baseline or an explicitly accepted equivalent;
- public semantic API/schema definitions with no OCCT/private geometry types;
- immutable journal/revision/material-body semantic model code and tests;
- worker/backend adapter boundary;
- deterministic regression fixtures and result schema;
- `docs/architecture.md`, `docs/api.md`, `docs/journal.md`, `docs/step-conformance.md`, `docs/testing.md`;
- dependency provenance manifest and third-party notices/licence inventory;
- CI configuration;
- production decision-record directory/template.

Do not copy research harnesses wholesale merely because they exist. Import only accepted logical fixtures/contracts or deliberately retained negative controls needed by a production test, and record the exact genesis provenance of each import.

## CI foundation

Before broad implementation, CI should prove at minimum:

- deterministic configure/build on a hosted Linux path;
- native unit/static/schema checks;
- semantic journal/revision/body/lineage tests independent of OCCT where practical;
- a pinned OCCT adapter/worker version-provenance smoke path;
- crash/timeout containment and process-worker smoke coverage;
- representative geometry/STEP validation separately from fast unit tests;
- generated-schema/artifact reproducibility where generation is used;
- a documented and periodically exercised Windows build path.

Keep expensive geometry/qualification campaigns separate from fast semantic checks so the repository can remain productive without weakening the engineering gates.

## Dependency, licence and provenance foundation

- Pin founding OCCT to upstream `V8_0_1` / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42` until a production decision changes it.
- Record exact source URL, commit/version, build options, compiler/toolchain, linkage mode and local patches for dependencies.
- Keep OCCT behind adapter/worker boundaries.
- Do not add CGAL/Manifold/OpenVDB or other fallback dependencies until a production issue justifies and qualifies them.
- Preserve the genesis finding that the reviewed CGAL Nef package carries materially different GPL obligations from less restrictive candidates.
- Perform a release-specific licence/compliance audit before distributing binaries; genesis notes are provenance evidence, not legal sign-off.
- If the project licence itself has not been explicitly selected, leave that as a visible decision rather than inventing one during bootstrap.

## Founding issue creation order

Create the full autonomous prompts from `handoffs/opensimachinist/02-INITIAL-ISSUE-GRAPH.md`. Preserve their dependency graph rather than flattening them into an epic.

Start with:

1. `OSM-001` — repository foundation, build and CI;
2. `OSM-002` — programme API and semantic data contracts;
3. `OSM-003` and `OSM-005` when their dependencies are met;
4. `OSM-004` lineage persistence;
5. `OSM-006` generic B-rep reconciliation/validation vertical slice;
6. `OSM-007` STEP conformance/export;
7. `OSM-008` lathe and `OSM-009` mill qualified provider slices;
8. `OSM-010`/`OSM-011` deferred/fallback seams;
9. `OSM-012` end-to-end journal-to-STEP benchmark;
10. `OSM-013` through `OSM-015` qualification work as dependencies permit.

Every issue retains branch → PR → automated checks → merge → `main` verification discipline and closes only when its acceptance criteria are genuinely satisfied.

## Boundary facts that must survive bootstrap

- The stable API is semantic/versioned; transport remains replaceable.
- `msac-journal/1.0` manufacturing intent and immutable semantic revisions are durable authority.
- OCCT objects and provider-private representations are rebuildable derived state.
- Process-isolated workers are the conservative founding default until measured concurrency evidence supports a different production decision.
- Preview is non-authoritative.
- Multi-body material state is first-class.
- Pathological manufacturing input is normal input, not automatically invalid intent.
- STEP is primary engineering output; failed reconciliation/export is not converted into success by STL/mesh.
- `interoperability_unqualified` remains distinct from writer/read-back success.
- Unsupported/ambiguous cases may be pending, reconciled through another provider, or explicitly refused; they are not silently approximated.

## Unresolved work transfer

Copy the substance of `03-UNRESOLVED-RESEARCH-REGISTER.md` into production tracking. Do not mark those items solved at repository creation. In particular retain the open work on pathological freehand milling, real lathe tool envelopes, independent STEP interoperability, curved hybrid reconciliation, OCCT concurrency/global state, provider handoff cost, lineage persistence encoding, bounded deferred resources, exact-arithmetic seams and release-time compliance.

RCS-017 remains active genesis research on OCCT concurrency/global-state isolation. Production may proceed with process isolation while that research runs; any later relaxation of the boundary should be a production decision backed by its measured evidence.

## First bootstrap completion test

Do not begin provider breadth until a clean contributor can clone the new production repo and, using only its own checked-in files:

- understand product purpose and public semantic boundary;
- configure/build the minimal native substrate;
- run deterministic semantic tests;
- identify the exact dependency/backend build under test;
- see the unresolved capability register;
- understand how STEP success/refusal is judged;
- locate the next dependency-ready production issue.

The new production repository may link back to radiCADSAC for archaeology. Its build, tests, runtime and day-to-day issue execution must not depend on access to radiCADSAC or to any founding conversation.
