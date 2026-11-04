# MC-047 — Post-digest content mutation preflight

**Date:** 4 November 2026. **Status:** provisional isolated implementation; source and CI acceptance pending. **Evidence class:** `DETERMINISTIC_MODEL` / synthetic read-only controls, not native or platform qualification.

## Authority, scope and source

Baseline: accepted `main=f10927c509079959af7c0f80c11b0211ae581503` (merged PR #381). Selected [MC-047 #109](https://github.com/techrote/radiCADSAC/issues/109) under the [MC-1 execution protocol](../../../../docs/machining-completeness/07-EXECUTION-PROTOCOL.md). Core implementation is the accepted `../MC-045/campaign_harness.py`, whose source is not changed. The PB-007 mathematical owner works separately on MC-038; [PR #382](https://github.com/techrote/radiCADSAC/pull/382) owns unrelated mathematical files.

The MC-041 actual native capability prerequisite remains open; MC-042 native output evidence is not qualified. No permit, native run, Windows runner, paid work, production bootstrap, authority change or programme gate assertion is introduced.

## Failure model and testable claim

The prior read-only preflight read and hashed ledger and retained captures **once**, then compared filesystem metadata snapshots. On a filesystem where `st_ctime_ns` denotes creation time rather than POSIX change time, a same-length in-place rewrite with restored `st_mtime_ns` could evade the final snapshot. A ledger rewrite after its first digest read had the same class of risk.

This repair performs a **second, streaming SHA-256 pass** over the retained capture bytes, comparing them to the original validated rows; it then re-reads the canonical JSONL ledger and compares the exact digest and row records to the first-pass source. The final metadata snapshot remains a further non-cryptographic control. A change between first and second passes must refuse admission even if its metadata appears unchanged.

## Deterministic adversarial verification

Run from repository root:

```sh
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py --self-test
python3 research/machining-completeness/tasks/MC-047/verify.py --self-test
python3 tools/validate_machining_completeness.py --self-test
python3 tools/validate_machining_completeness.py
```

Original **15 POSIX / 14 non-POSIX** MC-047 controls remain. Two new adversarial tests deliberately hold the fingerprint output constant to model metadata-insensitive filesystems:

1. Replace a correctly hashed retained stdout capture with different **equal-length** bytes after the first successful capture digest pass, while restoring its modification time; require refusal from the second capture digest pass.
2. Replace the source-bound canonical JSONL ledger with another **equal-length, still canonical** row whose source hash differs, after the first ledger digest; restore its modification time and require refusal from the second ledger digest comparison.

Positive full-slot and partial-prefix MODEL_ONLY controls must continue to pass with explicit `programme_acceptance_established=false` and `resumption_authorized=false`. Expected control totals are **17 POSIX / 16 non-POSIX** after the additions; these numbers must be verified by exact-head CI, not inferred from this document.

## Limits and invalidation

The two passes are linear in the retained file sizes but double capture hashing and repeat ledger reading. They do **not** make a multi-file filesystem snapshot atomic, prevent mutation after the last pass, defeat an adversary who can replace files with their original contents between passes, supply cross-process locking, preserve crash-safe capture transactions, or prove authenticated external custody. Windows/MSVC, native geometry, STEP usability, body/state fidelity and meaningful performance remain separate, blocked qualification requirements. A synthetic pass cannot establish MC-F, MC-B, MC-1, native capability or production readiness.

If the accepted MC-045 capture naming/ledger encoding contract changes, re-run and re-review this preflight against the exact new source before reusing its result. Do not merge without final-head review, applicable CI and guarded main reconciliation. Historical negative evidence and all 26 required operations remain unchanged.
