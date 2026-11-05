# MC-047 — Read-only ledger alias custody, 5 November 2026

**Source authority and baseline:** `techrote/radiCADSAC` main `25ba9f389e8d0d085e300a1ddb6a4996450a18f0` after merge of #400. Source owner: independent MC-047 proof-adjacent engineering lane; issue #109, coordination claim [#324](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6652211249). The main branch was not edited by the authoring task.

## Specific defect and acceptance criterion

The accepted `MC-045.append_attempt` refuses symlinked, special and externally hard-linked ledger paths via `_ledger_metadata`. Before this change `MC-045.audit_ledger` omitted that identity check and re-opened a caller-supplied pathname; the source-matched `MC-047.fingerprints` checked the ledger's basic file type but not external hard-link count. A byte-valid JSONL alias could therefore be reported as read-only replay-valid despite not meeting the appender's custody requirements.

**Pass criterion:** Both actual read-only auditors reject a symbolic link and an external hard link (whether supplied as the alias pathname or the canonical pathname now having link count > 1); after the alias is removed, the same canonical ledger remains readable; mutated evidence cannot silently pass merely because bytes and digest are unchanged. Reject before any status promotion or campaign restart.

## Implementation boundary

- `MC-045/campaign_harness.py`: `audit_ledger` now invokes the accepted `_ledger_metadata` identity policy before the first ledger read and again after its second content pass. Check same path metadata fingerprint and change-time within the same observation interface. No change to `append_attempt`, lock behavior, permit/plan schema, CLI status or dispatch.
- `MC-047/verify.py`: fingerprint inventory now includes `st_nlink`, and rejects unavailable/non-regular or multiply-linked ledgers. Existing quarantine pre/post checks and capture double-hashing remain intact.
- `MC-047/ledger_alias_custody_qualification.py`: independent, temporary-directory, MODEL_ONLY controls execute both real auditor implementations, test valid partial-prefix acceptance **without programme success**, genuine hard-link aliases, conditional real OS symlink aliases, exact evidence-byte preservation, and deterministic same-byte second-read inode replacement. The oracle requires an alias-specific refusal; unrelated errors cannot silently pass.
- `.github/workflows/mc1-mc047-ledger-alias-custody.yml`: GitHub-hosted Ubuntu 24.04 and Windows Server 2022, literal PR-head checkout verification, Python 3.12 compile, bounded controls and original MC-045/MC-047 regressions.

## Tests and refusals

Run from repo root:

```bash
python research/machining-completeness/tasks/MC-047/ledger_alias_custody_qualification.py --contract
python research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python research/machining-completeness/tasks/MC-047/verify.py --contract
python tools/validate_machining_completeness.py --self-test
python tools/validate_machining_completeness.py
```

The portable hard-link controls are mandatory, not optional. Symlink creation is conditional only where host privileges prevent creation, with its execution status printed. A same-byte replacement test injects a different inode before the real MC-045 second ledger read; the original bytes and digest alone must not suffice. All fixtures and mutations live inside disposable temporary directories; no historical evidence or accepted run is altered.

## Explicitly blocked or not established

This is **cooperative local filesystem custody**, not a proof against adversarial create/remove/recreate windows, filesystems with unreliable inode/link reporting, path-parent substitution, distributed locking, power loss, write atomicity, durable evidence snapshots or a trustworthy external attestor. Tests use synthetic MODEL_ONLY campaign records; no native tool, STEP, physics or machine execution. MC-047's MC-041 **capability** and MC-042 **artifact** prerequisites remain unresolved, native cross-host qualification not performed. PB-007-01/02/03/04 remain open; MC-B, MC-F and MC-1 `NOT_ESTABLISHED`; all 26 supported operations required; no production authorization.

A passing PR-head CI result qualifies only this bounded source candidate. Require separate-session source-critical review, correct literal head, guarded merge and independent merged-main CI before treating the improvement as accepted.
