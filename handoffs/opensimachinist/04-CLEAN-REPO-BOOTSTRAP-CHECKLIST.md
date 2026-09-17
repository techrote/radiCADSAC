# Clean OpenSimachinist repository bootstrap checklist

Status: founding checklist. Execute only when creation/population of the production repository is explicitly authorized.

## Source material to carry forward

- [ ] Copy/adapt the **contents** of `handoffs/opensimachinist/`, not the radiCADSAC Git history.
- [ ] Preserve the handoff version and source genesis commit in the production founding record.
- [ ] Create a production `AGENTS.md` that makes the handoff, current `main`, accepted production decisions and issue-specific contracts authoritative.
- [ ] Preserve concise archaeology links to radiCADSAC decision/evidence paths for challenge/reproduction; do not make production build/tests depend on the genesis repository.
- [ ] Do not copy obsolete/rejected planning documents as active requirements.
- [ ] Do not erase negative findings from the handoff constraints when shortening docs.

## Repository governance

- [ ] Start a new Git history with a clear founding commit from the approved handoff.
- [ ] Define branch/PR/CI/merge/verification discipline before feature implementation.
- [ ] Require issues to contain autonomous context, dependencies, acceptance criteria and reproducible checks.
- [ ] Establish decision-record format for production architecture/capability changes.
- [ ] Add a regression-fixture policy: minimized negative cases are retained permanently unless explicitly superseded.
- [ ] Keep generated artifacts/build output out of source history unless they are deliberate qualification records.

## Build and CI foundation

- [ ] Establish a C++17-capable native toolchain baseline.
- [ ] Add deterministic CMake/Ninja build or an explicitly accepted equivalent.
- [ ] Add Linux hosted CI for configure/build/unit/static/smoke checks.
- [ ] Document and test a Windows build path early; do not let Linux CI become an accidental platform decision.
- [ ] Add a version/provenance smoke executable or endpoint.
- [ ] Separate fast semantic/unit tests from heavier geometry/qualification campaigns.
- [ ] Ensure optional fallback providers can be disabled without breaking the minimal core build.

## Dependency and provenance foundation

- [ ] Create a machine-readable dependency provenance manifest.
- [ ] Create a third-party licenses/notices directory.
- [ ] Pin OCCT 8.0.1 to `V8_0_1` / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42` for the founding baseline.
- [ ] Record source URL, exact commit/version, build options, compiler/toolchain, linkage mode and local patches for each dependency.
- [ ] Keep OCCT behind adapter/worker boundaries; do not expose its types in public schemas.
- [ ] Do not add Manifold/OpenVDB/CGAL-style dependencies until a qualified production issue requires them.
- [ ] Treat the reviewed CGAL Nef GPL-3+ constraint as material if that package is considered.
- [ ] Schedule a release-specific license compliance audit before distributing binaries; do not treat genesis notes as legal sign-off.

## Programme semantic substrate

- [ ] Define/version programme API semantics before transport bindings.
- [ ] Implement public request/response/status schemas without OCCT/Godot/topology-private identities.
- [ ] Represent `msac-journal/1.0` canonical numeric/frame/definition concepts.
- [ ] Implement immutable workpiece revisions and explicit material-body sets/transitions.
- [ ] Implement semantic lineage with split/merge/replacement/ambiguity.
- [ ] Version tolerance/uncertainty, provider-dispatch and export/conformance policies independently.
- [ ] Make derived geometry/cache identity explicitly disposable/rebuildable.

## Geometry execution foundation

- [ ] Use supervised out-of-process geometry workers by default.
- [ ] Implement per-job timeouts and crash containment before broadening workload.
- [ ] Verify worker/backend build/runtime versions at startup or request boundary.
- [ ] Keep provider capability predicates explicit and observable.
- [ ] Implement physical/material oracles in tests; do not use “valid B-rep” as the only correctness condition.
- [ ] Preserve all disconnected material bodies until explicit retention/export policy selects otherwise.
- [ ] Keep the nine founding tolerance/policy channels distinct.

## STEP foundation

- [ ] Implement export candidate with committed revision, explicit body selection, unit, profile and budgets.
- [ ] Implement Layer A pre-export validation.
- [ ] Implement Layer B serialized-file/schema/unit/body validation.
- [ ] Implement Layer C fresh read-back geometry/body/scale/analytic validation.
- [ ] Preserve `interoperability_unqualified` until Layer D independent evidence is current.
- [ ] Support millimetre and inch scale tests.
- [ ] Default to exporting all material bodies; make subset export explicit/auditable.
- [ ] Never use STL/mesh or faceted-only STEP as primary engineering success fallback.

## Corpus and regression migration

- [ ] Recreate/import only the representative fixture definitions needed by production tests, with provenance to their genesis family IDs.
- [ ] Include coincidence/coplanarity, tangency/contact, thin removal, retrace, high-operation-count, lathe, mill, cut-through/multi-body and STEP unit cases.
- [ ] Keep known valid-but-wrong global-fuzzy and freehand batching cases as negative controls.
- [ ] Keep known sampled-pose timeout and coarse-discrete feature-loss cases as negative controls where the relevant implementation seam exists.
- [ ] Define a stable production result record before broad benchmark growth.
- [ ] Separate backend defect results from harness/infrastructure failures.

## Initial issue creation

- [ ] Create OSM-001 first.
- [ ] Create remaining initial issues from `02-INITIAL-ISSUE-GRAPH.md` with dependency links preserved.
- [ ] Preserve branch → PR → automated checks → merge → `main` verification wording in each autonomous issue.
- [ ] Do not create downstream issues as “implement everything” epics; retain the vertical-slice acceptance criteria.
- [ ] Carry the unresolved register into production issue/research tracking without marking unknowns solved.

## Founding audit before implementation campaign begins

- [ ] A new contributor can understand product purpose, invariants, API semantics, architecture, lathe/mill initial scope, STEP success criteria and explicit unknowns without reading the founding conversation.
- [ ] Every major inherited architecture rule has an archaeology link to an accepted genesis decision/evidence source.
- [ ] No rejected genesis alternative is presented as an active production requirement.
- [ ] No OCCT/Godot/private representation type is part of the stable public contract.
- [ ] No unresolved research question is asserted as solved.
- [ ] The first implementation milestone is measurable and small enough to complete independently.
- [ ] The repository can proceed if optional fallback research is delayed because handoff/refusal paths are explicit.

When every applicable founding item above is satisfied, begin OSM-001/OSM-002 work in the clean production repository. Do not use radiCADSAC as the production working tree.
