# MC-045: Uncertain append / fsync quarantine (5 November 2026)

## Source authority and bounded scope

- Initial authoritative `main`: `5f3f564888c0b28ced362ba3e71a64c67317ffa3` (MC-045 #390 landed; separate MC-038 #391 landed).
- Primary task: [MC-045 #107](https://github.com/techrote/radiCADSAC/issues/107); downstream consumer [MC-047 #109](https://github.com/techrote/radiCADSAC/issues/109).
- Exclusive [coordination claim](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6646945416).
- Write set: this document and `campaign_harness.py`. Neither proof-owner sources, #100, frozen v54/v2, current authority, 77, programme/fixture registries, task graph, nor native/STEP sources were changed.
- This is a `MODEL_ONLY` deterministic filesystem error-injection improvement; no approved native campaign or production dispatch is represented.

## Defect, correction, and falsifier

Before this repair, `append_attempt` released its exclusive-create `<ledger>.append.lock` even when the ledger write returned a short length or when its `fsync` failed. For a short write, an incomplete JSONL tail usually makes replay refuse; for a fully written row whose `fsync` failed, a subsequent reader may see valid JSONL and unknowingly treat the uncertain row as reliable append evidence. Neither condition is safe for a retry.

The implementation adds `UncertainLedgerDurabilityError(ContractError)`, emitted only after an attempted ledger write reports a short count, throws `OSError`, or `fsync` throws `OSError`. The single-writer lock context retains **its own verified lock inode** on this typed failure so that any subsequent cooperating appender refuses pending explicit forensic/manual recovery. Existing lock identity checks still refuse a replaced lock. Validation/refusal before mutation continues to release its lock; successful writes continue to `fsync` and unlock.

The intended counterexamples are (1) a positive 17-byte short return after an existing valid record, (2) `EIO` after writing 17 bytes, (3) `EIO` from the ledger `fsync` following a complete row write, and (4) a 17-byte first-row short append to a new ledger. Each must refuse and retain the lock. The earlier valid prefix must remain byte-identical; incomplete tails must remain unparseable; no second append is admitted while quarantined. Actual short/durability faults are injected with a test-local descriptor wrapper, not inferred from timestamps or operating system behaviour.

## Verification and impact

Run:

```bash
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python3 research/machining-completeness/tasks/MC-047/verify.py --self-test
python3 tools/validate_machining_completeness.py
```

Use the accepted MC-047 Linux/Windows single-writer and interrupted-ledger workflows for process regression. All CI must be bound to the exact final PR head; passing a synthetic merge ref alone is insufficient for acceptance. Retain the original failures and any newly found regression evidence; do not edit existing frozen fixtures to make a test pass. The fault wrapper is deliberately isolated from ordinary `os` operations and restored after each injected attempt.

## Explicit limitations and follow-on work

- **No atomic rollback:** a partial write remains on disk. A complete row after failed `fsync` may also remain visible but must not be treated as confirmed durable evidence.
- **No process-crash/power-loss guarantee:** an actual abrupt death before a Python exception cannot execute the quarantine handler; the existing stale-lock behaviour is still the protective mechanism for those cases.
- **No automatic recovery:** retaining the lock requires explicit manual identity, source, digest, repeat-order and capture inspection before any separate recovery operation. Deleting the lock is not an implicit recommendation or acceptance policy.
- **No hostile-filesystem, cross-host/distributed-lease, true transactional capture, Windows physical MSVC, native STEP, geometry or manufacturing qualification.**
- PB-007-01/02/03/04 and relevant PO obligations remain OPEN; MC-B, MC-F and MC-1 remain `NOT_ESTABLISHED`, all 26 operations remain required, and production remains unauthorized.

A later native recovery task requires accepted MC-041 capabilities, MC-042 STEP artifacts, a bounded native permit and independently verified source-matched evidence. This task is independent of the PB-007 proof theorem and does not discharge any mathematical obligation.
