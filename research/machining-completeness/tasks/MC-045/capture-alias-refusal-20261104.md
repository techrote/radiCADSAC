# MC-045 standalone retained-capture alias refusal — 2026-11-04

## Authority and task scope

- Issue: [MC-045 #107](https://github.com/techrote/radiCADSAC/issues/107); programme [MC-1](../../../../docs/machining-completeness/00-PROGRAMME.md).
- Source base: `34e91a5691b9f83ff1afd746fc964c7666bf142b`.
- Owner: independent proof-adjacent MC-045 qualification lane. Coordination claim: [#324](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6639831886).
- Exact source path: `research/machining-completeness/tasks/MC-045/campaign_harness.py`.
- Evidence class: **DETERMINISTIC_MODEL / MODEL_ONLY**, not native geometry, native STEP, physical Windows qualification, production readiness, or proof acceptance.
- Prerequisite gates: mathematical PB-007-01..04 open; MC-B, MC-F and MC-1 NOT_ESTABLISHED; production not authorized; all 26 operations remain required.

## Falsification / previously admitted evidence

`verify_retained_captures(rows, capture_dir)` was independently hashing each expected `000000.stdout.bin` / `000000.stderr.bin` file. Since two *distinct filenames* may be **hard links to one inode**, different retained records could pass with the same empty-content SHA-256 despite not having distinct capture file identities. The stand-alone MC-045 `audit-ledger` CLI uses this verifier directly, while the later MC-047 read-only preflight already refuses such aliases. The inconsistency allowed the MC-045-only path to admit alias-shaped custody.

## Implementation

For each expected retained capture, read one `lstat` snapshot, refuse nonregular files and symlinks, require an available nonzero inode identity, and refuse a repeated `(st_dev, st_ino)` among expected captures before digest verification. The SHA-256 check, exact filename inventory check and ledger-row identity checks remain in place. This rejects obvious aliases even when both digests are identical. On a filesystem that cannot supply usable inode identities, refuse rather than claim custody qualification.

## Deterministic controls

Run:

```bash
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python3 research/machining-completeness/tasks/MC-047/verify.py --contract --self-test
python3 tools/validate_machining_completeness.py --self-test
python3 tools/validate_machining_completeness.py
```

The MC-045 self-test retains positive, independently created empty stdout/stderr files and exercises two negative aliases: within one attempt and across separate attempts. Each mutation is undone, and the positive control is replayed. The retained missing/modified/unexpected-file and corrupt-ledger negatives remain unchanged. No paid or native workload is dispatched.

## Residual limitations and handoff

This is **static file-identity admission**, not atomic evidence custody. A hostile concurrent writer may replace paths between `lstat` and open, and an inode number can be recycled. Neither cross-process append locking, safe transaction commit, endpoint attestation, Windows physical filesystem proof, nor native geometry/STEP validation is established. A later bounded follow-on should pin open descriptors and compare `fstat` identity to the admitted snapshot, then separately address capture/ledger atomic transactions. Do not promote a green synthetic test into MC-F/MC-1 acceptance.

Review the PR at the final exact head and inspect CI before any guarded integration. An owner-account AI-assisted COMMENTED review is not an independent human APPROVED review.
