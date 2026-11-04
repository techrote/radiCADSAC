# MC-045 — fail-closed exclusive append lock (4 November 2026)

**Class:** auxiliary deterministic `MODEL_ONLY` ledger engineering. **Issue:** [MC-045 #107](https://github.com/techrote/radiCADSAC/issues/107). **Base:** `04f98886e578978600a8148713f866afbb26332a`. **Source:** `campaign_harness.py` (prior blob `28d9de9627b0623f18b7f477ef69a7395a84bfbd`). **Owner:** Prepare radiCADSAC Engineering. **Coordination:** [#324](https://github.com/techrote/radiCADSAC/issues/324).

## Falsifiable defect and bounded change

Before this increment, two cooperative processes could both read the same valid JSONL prefix, independently validate the next identical repeat/job slot, then append both. Each writer had valid individual evidence, but the resulting ledger was noncanonical campaign history.

`append_attempt` now enters an exclusively created adjacent `<ledger>.append.lock` before replaying existing ledger bytes. A competing writer, including an abandoned lock after a crash, receives `ContractError` and does not read/append or delete the other lock. After acquiring the lease, the existing strict JSONL replay, attempt-slot uniqueness/ordering validation, append and `fsync` all run within the critical section. A normal or rejected append releases its own lock after comparing file identity. The lock is never automatically reclaimed by PID/age inference.

## Reproducible deterministic checks

```sh
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python3 research/machining-completeness/tasks/MC-047/verify.py --self-test
python3 tools/validate_machining_completeness.py --self-test
python3 tools/validate_machining_completeness.py
```

New synthetic negative: while an exclusive lock exists, a valid next attempt must fail without changing either the ledger or the existing lock. Positive: removal of that test-owned lock allows exactly one valid append, yields an ordered two-row ledger, and leaves no lock behind. A corrupt JSONL prefix must still refuse append and release its own temporary lock. Existing replay/digest/permit/capture negative tests remain.

## Boundaries / next prerequisite

This protocol serializes **cooperating calls to this helper** on filesystems with reliable atomic exclusive file creation. It does not prevent noncooperating writers, manual lock removal, malicious lock replacement, shared/network filesystems without guaranteed `O_EXCL` semantics, inode recycling or TOCTOU in capture validation. A crash may leave a stale lock; manual recovery must first verify process liveness, preserve ledger/captures, and independently audit custody before explicitly removing the lock. There is still no atomic stdout/stderr/ledger transaction, crash-safe journal replay, cross-platform physical qualification, native STEP, MC-B/MC-F/MC-1 acceptance or manufacturing authority.

PB-007-01–04 remain OPEN; all 26 operations are retained. Treat passing `MODEL_ONLY` controls as a readiness check only.
