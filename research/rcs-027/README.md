# RCS-027 — Genesis v2 synthesis and freeze

RCS-027 is the final Genesis-v2 synthesis issue. It consumes RCS-018 through RCS-026, regenerates versioned v2 handoffs without modifying Genesis-v1 package meaning, and closes the single RCS-026 Gate-5 blocker with an exact-pinned Windows/MSVC OCCT 8.0.1 STEP campaign.

## Files

- `evidence-matrix-v1.json` — one entry for every Genesis-v2 predecessor.
- `decision-delta-v1.json` — Genesis-v1/v2 decision audit.
- `windows-step-qualification-v1.json` — frozen exact-head Windows STEP closure evidence after hosted CI.
- `bootstrap_occt_windows.ps1` — exact OCCT 8.0.1 worker-only Windows bootstrap.
- `summarize_windows_step.py` — deterministic three-run programme-level STEP projection and closure record.
- `test_contract.py` — adversarial/boundary checks.

## Protected boundaries

The campaign may not rewrite canonical journal meaning, discard disconnected bodies, promote backend topology identity, reset propagated error, relax manufacturing tolerance, erase positive-removal intent, mutate source/audio identity or provenance, or report Layer-D interoperability qualification not supported by RCS-022 evidence.

## Gate-5 rule

The branch starts with `pending_windows_step_evidence`. Only a successful exact-pinned three-repetition Windows/MSVC export/read-back campaign may change that to `accepted`. The campaign must preserve `interoperability_unqualified` at Layer D; its job is to establish the missing Windows kernel/export execution, not to manufacture independent-consumer success.

After final-head validation and merge, the verified merge commit is the target of the documented Genesis-v2 tags.
