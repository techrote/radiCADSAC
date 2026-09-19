# MSAC v2 implementation roadmap

## Phase 0 — clean project and contract fixtures
Create clean Godot/application repository, CI, project/version schema and shared programme contract tests. Keep backend transport abstract.

## Phase 1 — machine input and canonicalizer
Implement lathe/mill machine modules, explicit frames/tool/setup state and a policy-versioned RCS-019-conforming canonicalizer. Add deterministic replay fixtures before polished controls.

## Phase 2 — project history and body workflow
Implement immutable revision navigation, body/lineage UI, split/cut-through handling, source/audio/provenance persistence and save/load migration. Provider state stays absent from authoritative saves.

## Phase 3 — backend client/status model
Implement asynchronous request/status handling, reconnect/replay, cancellation boundaries and visible `accepted_pending`/refusal/error states. Never block the UI on long kernel work.

## Phase 4 — engineering preview and inspection
Build revision-keyed preview, pending/stale indicators, DRO/frame controls, exact-query reconciliation triggers and multi-body selection UX. Preview remains non-authoritative.

## Phase 5 — lathe/mill capability UX
Expose RCS-020 lathe admission/reachability and RCS-021 mill exact/fallback/pending/refusal semantics. Unsupported motion is explicit, not visually “accepted”.

## Phase 6 — STEP workflow
Implement all-body default selection, profile/version display, validation progress, error-budget/body failures and explicit Layer-D `interoperability_unqualified` status. Derived STL/mesh must be clearly secondary.

## Phase 7 — usability and production hardening
Tune controller/keyboard UX, autosave/recovery, long-session performance, diagnostics and accessibility without changing engineering semantics. Measure responsiveness separately from backend correctness.
