# MC-047 — Refuse quarantined append ledgers in the read-only preflight

**Status:** bounded proof-adjacent engineering; candidate pending distinct-session review and exact-head qualification (5 November 2026 UTC).  
**Selected task:** [MC-047 #109](https://github.com/techrote/radiCADSAC/issues/109).  
**Base authoritative main:** `9c4c0371f4ba70e0fff8c15bd08e6c252e53dc29` (includes merged MC-045 PR #393).  
**Evidence class:** `DETERMINISTIC_MODEL`; Linux/Windows process checks are platform/process regression evidence only, not a native machining run.

## Problem and exact source contract

MC-045's authoritative `campaign_harness.py audit-ledger` refuses an adjacent `<ledger>.append.lock`, since a cooperating writer may still be appending or may have deliberately retained a quarantine marker after an uncertain short write, `fsync` error, close error or exceptional unwind. This is intentional even for a canonical, fully parsable JSONL record: syntax and persisted bytes alone do not establish durable custody.

The separate MC-047 `verify.py audit()` previously read and classified a full valid ledger without checking that lock. It could report `FULL_SLOT_LEDGER_NOT_PROGRAMME_ACCEPTED` even when the producer had explicitly quarantined the ledger. Although MC-047 never authorizes resumption or programme success, the apparently successful preflight classification was inconsistent with the source-owned custody policy.

Source at base: `research/machining-completeness/tasks/MC-045/campaign_harness.py` blob `dee4ac33bae6b3d0838780b158f7926d2da02cf0`; MC-047 `verify.py` prior blob `ed4d688de9c4917a8cf4ac585d5b3336f9a7e4ab`. Exact source of the lock contract is `refuse_ledger_append_lock()`, which checks the adjacent lock with `lstat` and refuses regardless of its contents.

## Bounded repair

Call MC-045's existing `refuse_ledger_append_lock(ledger)` **after permit/plan validation and before initial evidence fingerprints**, and **again after the second digest/replay/fingerprint verification and before returning any successful preflight record**. This applies to both partial and complete ledgers, without creating, removing or modifying locks. The second check matters because the adjacent marker is outside the ledger/capture directory fingerprint inventory.

No journal, cached derived state, native geometry, STEP writer, campaign writer or proof code is changed. Existing programme, proof, 26-operation and source-identity contracts are unchanged.

## Deterministic qualification and falsifiers

Run `python3 research/machining-completeness/tasks/MC-047/verify.py --self-test` (or `--contract`). The original controls remain and two negative controls are added:

1. **Existing quarantine over a complete valid 3-slot ledger.** Preflight must raise the exact MC-045 active/quarantined marker refusal. Assert ledger bytes and marker bytes remain intact; test-only marker removal happens only after the verdict.
2. **Late marker added during the second evidence-fingerprint call.** A local test shim captures the second fingerprint snapshot, then adds the marker *before returning that unchanged snapshot*, at the latest useful injection point. Preflight must still refuse for the authoritative marker reason. Verify that both fingerprints were executed, ledger bytes remain identical and marker bytes remain present.

Controls increase from **17 to 19 on POSIX** and from **16 to 18 on Windows**. Previous unlocked partial/full positive controls must remain accepted only within their deliberately non-authoritative statuses. Assert the specific refusal reason; unrelated errors must not count as successful negatives. Run repository `tools/validate_machining_completeness.py` and applicable exact-head Actions workflows. A failed CI invocation or cross-platform test is not discarded as redundant.

**Retained initial negative / corrected integration oracle:** First candidate `564f23d391c289ab44eba0fb2342c53a38cead1d` passed the new 19/18 MC-047 tests but failed both Linux and Windows jobs of [interrupted-ledger CI #41961710877](https://github.com/techrote/radiCADSAC/actions/runs/41961710877). The existing `interrupted_ledger_process_qualification.py` expected a torn JSONL line error while a crash-owner lock remained. This newer preflight must refuse the **lock first**, as the MC-045 CLI already does. The test oracle is corrected to expect that stronger custody refusal **before** test-only lock removal; after removal it retains the independent `unterminated ledger line 2` parsing refusal in *both* append and preflight, plus byte/hash preservation. This is a source contract priority change, not suppressing a failure. Source-only third edited file: `MC-047/interrupted_ledger_process_qualification.py`. The failed logs are retained for independent review.

## Hypothesis and limitations

**Hypothesis:** cooperative single-host MC-047 recovery preflight must never classify a ledger as admitted while an active or retained MC-045 append/quarantine marker is observable at the explicit admission checks.

**Decisive counterexample:** a valid ledger with a persistent lock, or one with a lock introduced just before successful return, still produces a full/partial success status.

This is **not** atomic multi-file evidence custody, distributed locking, a hostile-filesystem TOCTOU defense, lock-free transaction snapshotting, test of real power-loss persistence, a recovery command or a native machining claim. A lock that appears and disappears between checks can still evade detection, and an uncooperative writer can mutate bytes. The correct behavior under uncertainty remains refusal and manual provenance audit, not automatic stale-lock deletion or manufacturing resumption.

MC-041 capability and MC-042 native STEP work remain unqualified prerequisites for MC-047 physical gate acceptance. The full PB-007 mathematical proof and MC-B/MC-F/MC-1 remain `NOT_ESTABLISHED`; the 26-operation contract and production=false remain unchanged.

## Ownership, review and follow-on

Exclusive source scope: `MC-047/verify.py`, `MC-047/interrupted_ledger_process_qualification.py` and this task-local document on isolated `fix/mc047-quarantine-preflight-20261105`. Disjoint MC-038 proof PRs #392 and #394 and issue #100 remain owned separately. This task never claims a proof closure, human approval, actual native platform execution, or production qualification.

Complete exact-head CI/run IDs, original failure links, reviewed head and merge disposition are to be added in the PR discussion after the actual checks. Do not merge this draft until a distinct-session source-level review of the literal final head and required CI; rerun merged-main checks only if accepted and merged.
