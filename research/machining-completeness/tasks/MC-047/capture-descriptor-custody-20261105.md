# MC-047 — Retained-capture descriptor custody and substitution rejection

**Date:** 2026-11-05 (UTC). **Lane:** proof-adjacent MC-047 #109; no independent proof closure.  
**Base:** main `09aafd00a304c577a4d422f24f35aa069847f654` following separately accepted #398.  
**Branch:** `fix/mc047-capture-descriptor-custody-20261105`.  
**Authority:** AGENTS.md, DR-0026, MC-1 programme/protocol/roadmap, task graph and current-authority.json. All MC-B/MC-D/MC-E/MC-F/MC-1 capability gates remain independent. Production remains unauthorized.

## Defect and falsification criterion

The accepted MC-045 `verify_retained_captures` checks `capture.lstat()` (regular, unique inode, link count 1) and then calls `sha256_file`, which previously **reopened the pathname** without comparing its inode with the admitted `lstat`. An unrelated regular inode containing identical bytes and SHA-256 could be substituted between those operations. An auditor would see a matching digest while crossing a custody/identity boundary. Both MC-045 authoritative audit and MC-047 preflight call this same helper.

The repair opens each capture once via an OS descriptor, checks `fstat` against the admitted `lstat` and the current pathname (identity, regular type, unique-link policy and size), hashes with bounded `os.read` on that descriptor, then checks the descriptor's before/after metadata and the final pathname identity. Use `O_NOFOLLOW` and `O_NONBLOCK` when provided by the platform. `fstat` ctime is compared only to subsequent `fstat`, **not** to `lstat`: Windows differs in ctime reporting for those APIs.

The strict negative oracle is **not** a hash mismatch: a same-content replacement must be refused with an identity-specific error even though SHA-256 remains unchanged.

## Reproducible deterministic acceptance

```sh
python research/machining-completeness/tasks/MC-047/capture_descriptor_custody_qualification.py --contract
python research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python research/machining-completeness/tasks/MC-047/verify.py --contract
python tools/validate_machining_completeness.py
```

The task-scoped harness uses only synthetic `MODEL_ONLY` capture records: valid positive, same-length hash corruption refusal, same-digest inode substitution at descriptor open, recovery of the original fixture, and POSIX-only symlink-at-open plus pathname swap during descriptor reading. The POSIX-only post-open pathname swap is excluded on Windows because live-file rename/delete sharing differs; the mandatory pre-open same-content substitution executes on both Linux and Windows. Each mutation asserts that its own hook fired and that the substituted content remained digest-identical.

Hosted exact-source Linux/Windows workflow: `.github/workflows/mc1-mc047-capture-descriptor-custody.yml`. Existing MC-1 static, MC-047 replay and process regression checks remain required at final PR head. Retain any initial CI failures. Same-session source review is `COMMENTED` only, not external `APPROVED`; do not merge without distinct-session independent integration.

## Bounds and dependencies

**Independent now:** synthetic evidence custody and deterministic capture validation using already accepted MC-045/MC-047 interfaces; no native/paid permit, STEP, MC-038 owner code, #100 comments, frozen source/corpus, 77, task graph, authority or programme register edits.

**Not established:** atomic snapshot under an adversarial writer, a reliable race-free directory handle on all platforms, protection against a hostile kernel/filesystem, directory reparenting/cross-host aliases, power-loss durability, automatic recovery, native STEP validity, actual body reconstruction or engineering consumer use. A transient substitution removed before both checks can escape observation. All 26 required operations remain in scope and production=false. MC-041 capability and MC-042 artifact evidence remain prerequisites for genuine native MC-047 qualification. MC-B and PB-007-01..04 remain open absent separate formal acceptance.

## Evidence handover

Record actual reviewed PR head, source/blob identities, exact-head CI run/job IDs, terminal results, failed runs and artifacts in the PR conversation after they become available. This file deliberately does not invent execution results, merge status or gate decisions.
