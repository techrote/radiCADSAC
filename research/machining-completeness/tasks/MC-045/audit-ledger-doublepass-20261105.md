# MC-045 — authoritative audit-ledger double-pass custody challenge

**Date:** 5 November 2026 UTC. **Evidence class:** DETERMINISTIC_MODEL / local read-only process controls only. **Issue:** [MC-045 #107](https://github.com/techrote/radiCADSAC/issues/107). **Independent lane:** proof-adjacent; never MC-038/PB-007 closure.

## Source provenance and hypothesis

Starting accepted main: `935185bd63d789bc6786199e5ba434fddb515f6f`, after merged MC-047 quarantine preflight #395. Prior MC-045 CLI `audit-ledger` validated sequence and hashed every retained stdout/stderr once, then checked the cooperative append lock and emitted a success-shaped *validation* record. It did not reread the ledger/capture content after the first hash, even though the accepted MC-047 recovery preflight already uses a second content pass. A same-length capture rewrite or canonical ledger-row replacement during that window could be missed. The post-audit file state was not attested.

**Hypothesis:** a second streaming capture verification and canonical ledger reread, compared to the original rows and digest, refuse deterministic content changes introduced *after* the first hash. Positive unlocked canonical evidence must retain the exact established CLI response structure.

## Implementation and precise write set

Only these paths are changed:
- `research/machining-completeness/tasks/MC-045/campaign_harness.py`: introduce directly testable `audit_ledger()`, retaining `validate_plan`, both lock checks, strict ledger sequence, capture inventory/identity checks, and existing CLI output contract; reread captured content and ledger bytes before reporting. No write or auto-recovery is attempted.
- This task-scoped RAG Markdown report.

No edits to MC-047, the proof owner's separate #392, #100 evidence, accepted shared authority/gate/registry documents, v54/v2 frozen sources, STEP, native machining or production.

## Deterministic acceptance controls

Run from repository root:

```bash
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python3 tools/validate_machining_completeness.py
```

The MC-045 self-test adds a complete three-repeat canonical positive (stdout and stderr retained and uniquely named), then two negative cases that prove the injection actually executed:

1. **Post-first-digest capture rewrite:** change retained stdout `AAAA` to `BBBB`, keep equal length and restore its mtime; demand `retained capture digest mismatch` on the second stream pass. Original ledger bytes and modified capture bytes are explicitly asserted, with no silent repair.
2. **Post-two-capture-passes ledger rewrite:** change one byte in a canonical attempt ID, retaining byte length and JSONL canonicality; demand `ledger bytes changed during audit` after the second ledger read. Original capture bytes remain unchanged.

Fault wrappers restore the original functions in `finally`; unrelated early exceptions or failed injection must not masquerade as a qualified negative. Existing controls continue to cover hardlink/symlink refusal, uncertain append quarantine, prior sequence checks and reproducible process interruption.

## Validation and integration requirements

Require exact final-head static MC-1 and focused MC-047 workflows plus applicable Windows/Linux subprocess suites triggered by this MC-045 change. Keep any failed checks/old failed runs as evidence and correct only verified source/test defects. Review the actual code diff and the injection oracles; the same-account technical COMMENTED review is **not** independent human approval.

Open a **draft PR** from the isolated branch. Do not merge in the originating session. A distinct-session review must recheck main and competing owners, qualify exact final head, guard expected head on merge and verify landed-main checks.

## Explicit limitations and downstream gates

This is an additional cooperative, *read-only* content check, **not** an atomic transaction or frozen snapshot. A malicious writer can still race both passes, replace an inode/path between reads, or mutate bytes after this function returns. The two-pass cost scales with ledger and capture size; platform/native stress and power-loss durability are unmeasured. No recovery authorization is issued. `MODEL_ONLY` evidence is not engineering material, STEP, geometry, or MC-F qualification.

PB-007-01 through -04 and PO-02/04/05/07/08 remain **OPEN**; MC-B, MC-F and MC-1 `NOT_ESTABLISHED`. All 26 required operations remain in scope. No production authorization. No campaign permit.
