# MC-047 — Actual appender hard-process-exit qualification

**Date:** 5 November 2026 UTC. **Evidence:** DETERMINISTIC_MODEL plus real Linux/Windows process fault-injection; no native machining. **Issue:** [MC-047 #109](https://github.com/techrote/radiCADSAC/issues/109). **Authoritative base:** main at 2ab90bd3ec684f92830b9863ab870bdbe188c1b5, after [MC-045 #396](https://github.com/techrote/radiCADSAC/pull/396) merged. No changes to current authority, proof owner, frozen audit or production.

## Scope and falsification

The accepted [interrupted-ledger process test](interrupted_ledger_process_qualification.py) directly writes raw JSONL bytes from a worker. It does not execute the actual accepted [MC-045 append_attempt](../MC-045/campaign_harness.py) through a hard process exit. This isolated MC-047 process harness fills that test gap without changing the writer.

Run a separate Python child using the accepted [MODEL_ONLY process authority](single_writer_process_qualification.py). Two deliberate crashes are required:

1. **Partial real write:** intercept only the real unbuffered ledger descriptor, write the first 17 bytes of the canonical next row, and immediately call os._exit(29), skipping cleanup.
2. **Complete write, before fsync:** permit the lock initialization fsync, then terminate at the second fsync (the ledger durability call) following the real complete-row write.

Both controls require an exact child exit code and exact ledger bytes matching the targeted crash point, with the original committed ledger prefix and retained capture hashes unchanged. The actual append lock must still exist. A competing actual append, MC-045 audit, and independent MC-047 audit must refuse with the expected lock-related reason, not merely an arbitrary exception. Every worker has a bounded timeout/kill path.

A deliberate **test-only manual lock deletion** follows to demonstrate the distinction between parseability and durability: a 17-byte torn ledger line must still fail strict JSONL replay; a complete but non-fsynced row may parse correctly but must never become a claim of durable or programme-accepted output. Deleting a real quarantine lock is not authorized by this experiment.

## Reproduction

From the repository root run:

- python3 research/machining-completeness/tasks/MC-047/actual_appender_crash_process_qualification.py --contract
- python3 research/machining-completeness/tasks/MC-047/verify.py --contract
- python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
- python3 tools/validate_machining_completeness.py

Source-matched CI is [.github/workflows/mc1-mc047-actual-appender-crash-process.yml](../../../../.github/workflows/mc1-mc047-actual-appender-crash-process.yml), on Ubuntu 24.04 and Windows Server 2022 with exact PR-head checkout verification. Retain failures, exact-head run identifiers and any artifacts. A passed CI job establishes only the specifically executed controls.

## Independence and gates

The three added paths are this document, the Python MC-047 process harness, and the dedicated workflow. They do not modify accepted MC-045 writer code, existing MC-047 verifier, current authority, shared registries, MC-038, issue #100 or frozen V54/V2 evidence. Separate MC-038 proof owner owns PB-007; this is not a second proof worker. No expensive campaign, native solver or manufacturing dispatch occurs.

MC-047's true cross-platform native qualification remains blocked on accepted MC-041 capability and MC-042 STEP artifact dependencies. This test does **not** demonstrate power-loss durability, crash-atomic transactions, cross-host locks, hostile filesystem safety, automated recovery, native STEP correctness, MC-B, MC-F, MC-1 or production readiness. All 26 required operations remain in scope. The PB-007 mathematical obligations remain open until independently and formally accepted.

## Review and integration

Final exact-head source review must inspect process death placement, byte-identity oracles, refusal cause, cross-platform behavior and log evidence. A self/owner-account COMMENTED review is not independent human APPROVED. No same-session merge; reconcile current main and other writers again before guarded integration. Source checkout and negative evidence must remain verifiable without this conversation.
