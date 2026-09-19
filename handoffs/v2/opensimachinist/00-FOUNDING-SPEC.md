# OpenSimachinist Genesis v2 founding specification

## Product role

OpenSimachinist is the manufacturing-native engineering backend for MSAC. It consumes canonical manufacturing intent and produces durable revision/body/status results plus reconciled engineering geometry. It is not the user interface, game loop or a conventional feature-tree CAD system.

## Stable programme boundary

The durable authority consists of `msac-journal/1.0`, immutable revisions, canonical operation IDs, durable material-body IDs, explicit split/merge transitions, semantic lineage, versioned setup/tool/policy references, source/audio identity and provenance. Backend topology, BRepGraph UIDs, process IDs, mesh/dexel cell IDs and cache keys are never durable meaning.

Required request families include capabilities, apply canonical operations, commit/replay revision, query material state, request preview, request reconciliation, inspect reconciled geometry and export STEP. Statuses must distinguish `accepted_pending`, `reconciled`, `success`, `refused_unsupported`, unresolved ambiguity, budget/tolerance breach, invalid/wrong geometry, kernel failure/crash/timeout and `interoperability_unqualified`.

## Canonicalization, tolerances and error budgets

OpenSimachinist accepts the canonical journal rather than raw controller sampling. Units, frames, transform direction and quantization policy are explicit. Production canonicalizers must pass the RCS-019 policy vectors.

Manufacturing tolerance is not numerical solver error. Carry canonicalization/fit/transform/tool-envelope/provider/representation/reconciliation bounds as separate contributions. Unknown dependence composes conservatively. Positive material-removal intent survives uncertainty. Unknown required bounds or known budget excess fail closed; a user tolerance cannot silently absorb them.

## Provider architecture

Use semantic-provider hybrid dispatch. Provider admission is capability-driven and replay-stable.

For lathe, the founding axisymmetric provider requires qualified rotational material semantics, a qualified realistic tool-envelope class/orientation, reachability and explicit body/connectivity handling. Measured supported families include the bounded RCS-020 circular-nose external/internal turning subset, facing/shoulder/taper, rounded groove and complete parting. Unsupported undercuts/form/live-tool/eccentric work hands off or returns `refused_unsupported`.

For mill, use qualified exact fixed-axis strategies first. The RCS-021 independent material-set oracle is a regression truth source for the measured fixed-axis domain. Directional material state is a bounded fallback only where its material/spatial/error budgets close. Otherwise remain `accepted_pending` for refinement/reconciliation or refuse explicitly. Five-axis/tool reorientation and rounded simultaneous-Z are not founding capabilities.

## Deferred state and reconciliation

Deferred/provider-private state is disposable derived state. Exact connectivity/body selection, committed engineering inspection and STEP export are hard reconciliation boundaries. In addition, use a finite observable deferred-state resource guard to prevent unbounded pending growth. The RCS-025 value `2` is a stress fixture, not a production constant.

Reconciliation replaces and validates derived state from programme authority; it is not error cancellation. Ambiguous lineage returns pending/refusal, never a guessed mapping. Provider handoffs append source+conversion+destination error contributions.

## OCCT workers and concurrency

Pin founding OCCT to 8.0.1 commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`. RCS-024 found no safety/correctness basis for moving to the tested 8.1.0.dev1 snapshot. Isolate OCCT logical jobs in processes because STEP and parallel configuration include process-global mutable state. Intra-worker parallelism is opt-in only for explicitly qualified operations and must not multiplex conflicting global configuration.

Worker crash/timeout/kill cannot mutate durable authority. Derived cache loss/corruption is recovered from journal/revision/body/lineage/source/provenance authority.

## STEP contract

STEP is mandatory primary engineering output. STL/mesh is derived, not a fallback architecture. Default body selection is **all committed material bodies**; disconnected parting/cut-through states may not be dropped.

Founding profile: `rcs-022-occt-ap242dis-layer-d/1.0`, OCCT 8.0.1, AP242DIS, `STEPControl_ManifoldSolidBrep`, explicit mm/in, tessellation off, assembly auto, surface curves on, non-manifold off, `Greatest` precision with `0.0001` selected file-unit value.

STEP can start only from reconciled conventional B-rep whose body/material/validity/error gates pass. The current independent Layer-D state is **`interoperability_unqualified`**. Successful serialization, OCCT read-back, independent Part-21 parse or clean independent B-rep import does not change that status. Never widen tolerance, discard bodies, heal silently after export or substitute tessellation to claim success.

## Platform and scale boundary

Genesis v2 qualifies programme-level deterministic semantics on hosted Linux/GCC and Windows/MSVC through 100,000 journal events, including process faults, replay and cache recovery. These are research qualification tiers, not production SLAs. Production must keep equivalent invariants and add operational telemetry.

## Preview and engineering authority

Preview may be approximate, stale or GPU-derived and must be labelled by revision/status. Preview cannot authorize STEP, body selection, material claims or inspection. Engineering queries bind to a programme revision and its reconciled state.

## Versioning and migration

Persist schema/profile/provider-policy versions alongside durable intent. Old journal/source/audio/provenance meaning is immutable. A future backend/provider may regenerate derived state but cannot silently reinterpret saved manufacturing intent.

## Founding non-capabilities

Do not pretend universal five-axis, live-tool turning, arbitrary form-tool reachability, universally exact topology naming, Layer-D-qualified STEP interoperability or production-tuned capacity. Each has an explicit handoff/pending/refusal/requalification path.
