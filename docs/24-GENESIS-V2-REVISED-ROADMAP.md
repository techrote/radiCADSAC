# Genesis v2 revised research roadmap

Status: proposed current post-freeze research plan pending merge of this planning PR  
Date: 2026-09-17  
Supersedes for future genesis work: the stopping point of `04-REVISED-RESEARCH-ROADMAP.md`; Genesis-v1 evidence and decisions remain historical/accepted until explicitly superseded.

## Purpose

Genesis v2 is a bounded qualification tranche between the accepted Genesis-v1 architecture and production-repository creation. It exists because several architecture-driving choices were supported by narrow smoke campaigns or isolated experiments. The tranche is intentionally focused on evidence capable of changing a foundational semantic, provider, reconciliation, export, or platform boundary.

Genesis v2 must not become an indefinite attempt to solve CAD universally. When these issues finish, remaining narrow implementation questions move to the production repositories.

## Starting state

The programme starts Genesis v2 from:

- RCS-001 through RCS-017 accepted on `main`;
- semantic-provider hybrid architecture selected by RCS-013;
- Genesis-v1 handoffs frozen by RCS-016;
- process-isolated OCCT workers strengthened by RCS-017's measured same-process configuration cross-talk;
- unresolved capability risks recorded in `research/rcs-013/unresolved-v1.json` and the Genesis-v1 handoffs.

## Gate 5 — Genesis v2 foundation-qualified

Gate 5 is reached only when:

1. the selected contracts compose in an executable research vertical slice;
2. canonical journal normalization has deterministic conformance vectors and cross-platform evidence;
3. the lathe provider is fed realistic tool-derived envelopes rather than oracle target profiles alone;
4. arbitrary/manual milling has an independent material oracle and a qualified bounded fallback or an explicitly narrowed product capability boundary;
5. a concrete STEP exporter profile has independent Layer-D interoperability evidence or remains explicitly unqualified with a recorded blocker;
6. uncertainty/error budgets propagate through the actual manufacturing/reconciliation pipeline rather than existing only as policy labels;
7. provider handoff/deferred-state/reconciliation cycles have been stressed without silent lineage/body/error-budget corruption;
8. current OCCT evidence has been compared against the pinned 8.0.1 control where upstream changes could alter backend-private choices;
9. Windows/MSVC plus Linux scale/soak/fault-recovery evidence exists for the research architecture;
10. all architecture-impacting contradictions are reconciled into versioned decisions and new **Genesis-v2** handoff packages without rewriting Genesis-v1 package identity.

## RCS-018 — Integrated semantic contract vertical slice

### Objective

Build a research-only executable slice that proves the accepted journal/revision/lineage/status/provider/reconciliation/worker/STEP boundaries can compose coherently.

### Required evidence

At minimum exercise:

- one lathe trace and one mill trace from canonical operation fixtures;
- journal ingress and immutable revision creation;
- durable material-body IDs and lineage events including at least one split;
- provider dispatch using existing accepted research providers/adapters;
- `accepted_pending` → reconciliation/status transition;
- supervised process-isolated worker execution and timeout/error mapping;
- explicit STEP export request using the RCS-005 gates available at this stage;
- undo/replay from an earlier revision and regeneration of derived state;
- machine-readable event/status trace suitable for later RCS-025/RCS-026 use.

### Boundary

This is **not** production OpenSimachinist. No Godot integration, production RPC/ABI, final persistence database, UI, rendering, deployment service or generalized scheduler is authorized.

### Dependencies

RCS-013, RCS-017, and the accepted Genesis-v1 handoff contracts.

## RCS-019 — Canonicalizer conformance and deterministic normalization

### Objective

Turn RCS-002's logical canonicalization contract into executable conformance evidence.

### Required evidence

- deterministic vectors for units, transforms, q15 rotations, ties-to-even quantization, timestamp collisions, engagement boundaries, near-zero/full-circle arcs, spline/polyline fallback, overflow/refusal and setup changes;
- equivalent physical motion sampled at materially different rates;
- 10k–100k sample traces including noisy analogue feeds;
- at least two independently implemented decision paths (for example a reference canonicalizer plus an independent verifier/implementation) so one bug cannot define the oracle;
- Linux and Windows execution where feasible in hosted CI;
- stable logical output or explicitly bounded equivalence under the RCS-002 replay contract.

### Dependencies

RCS-002, RCS-003, RCS-007.

## RCS-020 — Realistic lathe tool-envelope qualification

### Objective

Test the missing upstream half of the RCS-010 architecture: deriving the axisymmetric material-removal envelope from realistic tool geometry, orientation and motion.

### Required scope

- representative external turning insert with nonzero nose radius and multiple orientations;
- representative internal boring tool/envelope;
- grooving/parting tool including complete cut-through/body separation;
- at least one undercut/reachability case that exposes a capability boundary;
- OD, facing, shoulder, taper/chamfer, blind/through ID and retrace cases where applicable;
- comparison against an independent analytic/high-resolution physical oracle, not only another copy of the same provider calculation;
- feed resulting envelopes into the existing axisymmetric material-domain reconstruction and STEP checks.

### Decision impact

Refine the first-class lathe-provider capability predicate and decide which tool/process classes are exact, conservative, delegated or refused.

### Dependencies

RCS-002, RCS-007, RCS-008, RCS-009, RCS-010.

## RCS-021 — Manual/freehand mill material oracle and bounded fallback campaign

### Objective

Resolve the largest Genesis-v1 MVP capability gap: arbitrary canonicalized manual/freehand milling where RCS-011's n-ary batch was valid-but-wrong and dense sampled-pose B-rep fallback timed out.

### Required approach

1. establish an **independent material-set oracle** for decisive fixtures; OCCT per-segment subtraction may remain a comparator but cannot be the sole truth source;
2. evaluate a machining-native multi-dexel/tri-dexel style representation or equivalent directional material field;
3. evaluate at least one maintained external mesh/volumetric/exact candidate selected from evidence (for example Manifold, OpenVDB, targeted CGAL/exact arithmetic) when practical;
4. compare against qualified RCS-011 strategies using the same physical oracle and error budgets.

### Required fixtures

- self-crossing paths;
- exact and jittered retraces;
- simultaneous XYZ/freehand motion;
- flat and ball/rounded cutter envelopes;
- tangent/near-coincident entry/exit;
- sub-tolerance positive removal;
- cut-through/body separation;
- very high segment/sample counts.

### Decision impact

Either qualify a bounded local fallback for initial manual milling or explicitly narrow the initial product capability with a refusal/pending policy. A watertight mesh alone is not success.

### Dependencies

RCS-002, RCS-003, RCS-007, RCS-009, RCS-011, RCS-012.

## RCS-022 — STEP Layer-D independent interoperability qualification

### Objective

Qualify a concrete production-candidate STEP exporter profile beyond OCCT self-readback.

### Required evidence

- exact exporter build/profile/schema/unit/healing configuration pinned;
- independent Part-21/schema parsing using a tool that is not the exporter implementation;
- at least one genuinely independent downstream solid/CAD/CAM consumer where legally and operationally available; a second consumer is preferred;
- implementation/kernel provenance of each consumer recorded so an OCCT-based importer is not misrepresented as independent geometry evidence;
- metric and inch fixtures;
- analytic plane/cylinder/cone retention;
- holes/voids and multi-body parting/cut-through;
- representative lathe and mill results;
- refusal rules for any profile/fixture that cannot be independently qualified.

### Closure rule

If no qualifying independent downstream solid consumer is accessible, record the exact blocker and leave the exporter profile `interoperability_unqualified`; do not close the research question by substituting another OCCT wrapper.

### Dependencies

RCS-005, RCS-006, RCS-010, RCS-011, RCS-017.

## RCS-023 — Propagated uncertainty and error-budget algebra

### Objective

Turn RCS-007's successful separation of tolerance channels into an executable uncertainty/error propagation model.

### Required propagation path

Canonicalization/quantization → coordinate transforms → tool-envelope construction → provider-local material operation → deferred/hybrid representation → reconciliation → validation/export comparison.

### Required evidence

- explicit algebra/rules for combining bounded translation/orientation/numerical/representation errors without conflating them with manufacturing tolerance;
- decisive versus ambiguous/contact classification rules;
- parameter sweeps across chained transforms and repeated operations;
- positive-volume sub-tolerance intent must not disappear merely because accumulated uncertainty is larger than the feature;
- `accepted_pending`/ambiguity must remain explicit when a safe decision cannot be made;
- export must refuse or expose a budget breach rather than silently widening the project requirement.

### Dependencies

RCS-002, RCS-005, RCS-007, RCS-009, RCS-012.

## RCS-024 — Current OCCT differential, concurrency minimization and BRepGraph/history probe

### Objective

Determine whether newer OCCT source materially changes backend-private choices while preserving 8.0.1 as the reproducible control.

### Required evidence

- pin the current stable release and, only if useful, a specific current-upstream commit separately from 8.0.1;
- reproduce decisive RCS-007 fuzzy/valid-but-wrong cases, RCS-011 pathological Boolean/sweep cases and RCS-017 STEP/global-state concurrency counterexamples on both baselines where APIs permit;
- minimize the RCS-017 STEP tolerance cross-talk to the smallest public-API reproducer and identify whether newer upstream behavior fixes/changes it;
- inspect/test BRepGraph or successor history/topology facilities only as backend-private aids for history, cache freshness and mapping—never as durable programme identity;
- assess build/platform/API migration cost and upstream maintenance implications;
- recommend retain-8.0.1, upgrade, or selectively backport/wrap with explicit evidence.

### Dependencies

RCS-004, RCS-006, RCS-008, RCS-011, RCS-017.

## RCS-025 — Provider handoff, deferred-state and reconciliation stress campaign

### Objective

Stress the architectural seams unique to the semantic-provider hybrid rather than testing providers only in isolation.

### Required scenarios

- lathe provider → generic/exact provider transition;
- mill exact strategy → bounded fallback → B-rep reconciliation;
- repeated defer → exact query → reconcile → defer cycles;
- split/merge/body selection while pending state exists;
- semantic lineage mapping across regenerated topology;
- undo/replay across provider changes;
- curved/non-orthogonal local fallback boundaries where qualified by RCS-021;
- accumulated uncertainty/error budgets from RCS-023;
- repeated reconciliation checkpoints and measurable resource growth.

### Metrics

Correct material/body set, lineage consistency, geometry deviation, analytic recovery, topology validity, pending-state size, reconciliation cost, memory, determinism, STEP eligibility/status and explicit refusal behavior.

### Dependencies

RCS-018, RCS-020, RCS-021, RCS-023, RCS-024. Consume RCS-022 for export qualification where available.

## RCS-026 — Windows/Linux scale, soak and fault-recovery qualification

### Objective

Test whether the research architecture remains deterministic and operationally contained on the Windows-first target platform and under long-running workloads.

### Required matrix

- Windows/MSVC and Linux/GCC or Clang with exact toolchain versions;
- canonicalizer conformance vectors from RCS-019;
- process-isolated OCCT workers and representative lathe/mill/provider-handoff workloads;
- 10k–100k operation/replay histories where tractable;
- repeated STEP export/read-back cycles and currently available Layer-D checks;
- worker crash/timeout/kill/recycle injection;
- corrupted/stale derived cache discard and journal replay;
- memory/RSS growth, latency distributions, nondeterminism and orphan-process/resource checks;
- repeated runs sufficient to detect intermittent failures rather than one green smoke execution.

### Dependencies

RCS-018, RCS-019, RCS-020, RCS-021, RCS-024, RCS-025. Consume RCS-022/RCS-023 evidence where applicable.

## RCS-027 — Genesis v2 synthesis, Gate-5 decision, handoff regeneration and freeze

### Objective

Synthesize RCS-018 through RCS-026 into the final pre-production foundation and generate new v2 handoffs without rewriting Genesis v1.

### Required tasks

- compare every Genesis-v1 architecture decision with new evidence and mark it retained, refined, superseded or still unresolved;
- reconcile contradictions rather than selecting convenient runs;
- update architecture/status/capability/error-budget/provider/export decisions only when supported;
- define exact remaining production-owned research and safe escape routes;
- generate fresh standalone packages under versioned Genesis-v2 paths (for example `handoffs/v2/opensimachinist/` and `handoffs/v2/msac/`);
- generate a machine-readable v1→v2 decision/evidence delta and a Genesis-v2 freeze manifest;
- preserve existing Genesis-v1 package trees/manifests unchanged in meaning;
- provide clean production-repository bootstrap issue graphs from v2 evidence;
- define/publish or precisely document immutable Genesis-v2 tag names against the verified final merge.

### Gate-5 closure rule

If any unresolved item still threatens the stable journal/API/material-body/provider/reconciliation/STEP success semantics, Gate 5 is not accepted and this issue remains open with the blocker named. Performance tuning or optional later capability does not by itself block Gate 5 when a safe bounded/refusal policy exists.

### Dependencies

RCS-018 through RCS-026.

## Parallel execution graph

After this planning PR merges:

- RCS-018 may start immediately;
- RCS-019, RCS-020, RCS-021, RCS-022, RCS-023 and RCS-024 are dependency-ready from Genesis-v1 outputs and can largely proceed in parallel;
- RCS-025 waits for the provider/fallback/uncertainty/current-OCCT evidence it integrates;
- RCS-026 waits for the integrated and handoff-stress substrate;
- RCS-027 waits for all Genesis-v2 evidence.

## Global issue execution contract

Every Genesis-v2 issue must:

1. read `AGENTS.md`, the founding documents, `06-RESEARCH-METHOD.md`, this roadmap, the Genesis-v2 issue graph, all declared predecessor outputs, applicable accepted decisions, and the issue itself;
2. inspect current `main` before work;
3. state hypotheses, baseline, fixtures, metrics and falsification criteria before interpreting results;
4. prefer primary sources and pin every external dependency/version/commit;
5. preserve negative results and distinguish MEASURED/SOURCE/INFERENCE/PROPOSAL/OPEN claims;
6. add deterministic machine-readable evidence and RAG-quality Markdown where applicable;
7. add/extend automated validation and keep existing checks green;
8. work on a dedicated branch, open a PR, repair CI, merge only after required automated checks pass, verify the merge landed on `main`, and close the issue only when acceptance criteria are genuinely satisfied;
9. if blocked, record exact evidence/blocker in-repo and on the issue rather than weakening acceptance criteria;
10. not create/populate production repositories unless a later explicit user instruction authorizes it.

## Genesis v2 stopping rule

After Gate 5, implementation starts. Remaining questions must either have a safe refusal/defer/handoff policy or be demonstrably implementation-local. Genesis v2 does not wait for general five-axis machining, live-tool turning, perfect topology naming, universal exact arithmetic, final UI/game design or every future STEP profile.
