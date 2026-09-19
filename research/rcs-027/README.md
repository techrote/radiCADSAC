# RCS-027 — Genesis v2 synthesis and freeze

RCS-027 is the final Genesis-v2 synthesis issue. It consumes RCS-018 through RCS-026, regenerates versioned v2 handoffs without modifying Genesis-v1 package meaning, and closes the single RCS-026 Gate-5 blocker with an exact-pinned Windows/MSVC OCCT 8.0.1 STEP campaign.

## Files

- `evidence-matrix-v1.json` — one entry for every Genesis-v2 predecessor plus RCS-027 closure binding.
- `decision-delta-v1.json` — Genesis-v1/v2 decision audit.
- `windows-step-qualification-v1.json` — frozen successful Windows STEP closure evidence and immutable workflow/artifact identity.
- `bootstrap_occt_windows.ps1` — exact OCCT 8.0.1 worker-only Windows bootstrap.
- `summarize_windows_step.py` — deterministic three-run programme-level STEP projection and closure record.
- `test_contract.py` / `test_gate5_freeze.py` — adversarial/boundary checks.

## Windows OCCT install-layout contract

The shared RCS-022 STEP harness consumes a stable installation-root contract: `include/opencascade`, `lib`, and `bin`. OCCT's native Windows layout instead uses `inc` plus compiler-qualified `win64/<compiler>/lib` and `win64/<compiler>/bin` paths. The RCS-027 Windows bootstrap therefore selects OCCT's supported `INSTALL_DIR_LAYOUT=Unix` with versioned include directories disabled. This changes installation layout only; it does not change the exact OCCT source commit, compiler pin, selected worker toolkits, STEP profile, body semantics, or process-isolation policy.

The post-install guard deliberately verifies the same `include/opencascade` and `lib` paths that the RCS-022 harness consumes, and the workflow loads runtime DLLs from the corresponding `bin` directory. Native configure/build/install output and the PowerShell transcript are both retained in the always-uploaded Gate-5 evidence directory so future bootstrap failures remain diagnosable.

## Protected boundaries

The campaign may not rewrite canonical journal meaning, discard disconnected bodies, promote backend topology identity, reset propagated error, relax manufacturing tolerance, erase positive-removal intent, mutate source/audio identity or provenance, or report Layer-D interoperability qualification not supported by RCS-022 evidence.

## Gate-5 result

Gate 5 is accepted. Workflow run `35417316840` completed the exact pinned Windows/MSVC campaign for three repetitions, passed all seven negative controls and preserved the required Layer-D state `interoperability_unqualified`. The frozen record includes the source head, workflow/run identity, artifact id/digest and live-summary digest.

Freeze provenance and merge readiness are separate by design: the evidence file binds the immutable successful evidence-producing run, while the final PR head must independently pass the same RCS-027 workflow and all inherited checks. Embedding a final-head run ID into its own commit would be self-referential.

After final-head validation and merge, the verified merge commit is the target of the documented Genesis-v2 tags.
