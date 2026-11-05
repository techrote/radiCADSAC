# MC-047 — Capture-first hard-process-exit custody qualification (5 November 2026)

## Question and ownership

**Task:** MC-047, issue #109. **Evidence:** platform/process execution using synthetic MODEL_ONLY campaign inputs; not native material, STEP, durability or production authority. This is auxiliary qualification of the accepted MC-045/MC-047 readers. The independent MC-038/PB-007 proof worker owns its own branches and issue #100.

**Starting authority:** main b53b28c7fe1bb8196aac8a7616c1d9a2fcf3e06d, after #401 guarded integration and seven-workflow landed-main qualification. [Coordination claim](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6653351678).

**Concrete untested seam:** existing MC-047 hard-process-exit tests interrupt canonical ledger writes and the actual MC-045 appender. They do not test a child dying after flushing next-slot retained stdout/stderr but BEFORE writing the associated canonical ledger row. A valid committed prefix must not allow extra, uncommitted captures to be admitted as evidence.

**Falsifier:** either actual MC-045 audit_ledger() or MC-047 audit() accepts the unexpected captured files without a matching ledger slot. Refusal must preserve the original ledger/capture hashes and all fault bytes.

## File-level write set

- New research/machining-completeness/tasks/MC-047/capture_first_process_crash_qualification.py — subprocess fault harness
- This task-specific RAG document
- New .github/workflows/mc1-mc047-capture-first-process-crash.yml — exact-head Linux/Windows CI

No edits to accepted MC-045/MC-047 sources, proof/programme registries, MC-038/#100, DR-0026, current authority, frozen audits, native STEP, body/topology/journal, or production sources.

## Contract and decisive negative controls

Each independent temporary fixture begins with a real accepted MC-045 append_attempt(), one valid synthetic row, indexed empty slot-zero retained stdout and stderr files. Both actual auditors must first return a non-authorizing valid partial-prefix result.

The independent Python child then exclusively creates next-slot capture files using os.open / os.write / os.fsync and immediately calls os._exit(29). It never appends the corresponding ledger row. Three modes are tested:

1. Partial stdout: precisely 17 flushed bytes in next-slot stdout, no next-slot ledger record.
2. Complete stdout: complete flushed bytes in next-slot stdout, no next-slot ledger record.
3. Both streams: flushed next-slot stdout and stderr, no next-slot ledger record.

For all modes, require actual child exit 29, exact expected bytes and filenames, original ledger byte identity and parsed row, SHA-256 identity of original captures, unchanged absence of append lock, plus **specific** error text "retained capture inventory has missing or unexpected paths" from both accepted auditors. Test only temporary fixtures; no real evidence is cleaned up.

## Verification commands

- python research/machining-completeness/tasks/MC-047/capture_first_process_crash_qualification.py --contract
- python research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
- python research/machining-completeness/tasks/MC-047/verify.py --contract
- python tools/validate_machining_completeness.py

Run the dedicated workflow on Ubuntu 24.04 and Windows Server 2022 with exact literal PR-head checkout verification, along with existing applicable MC-1 checks. Preserve failed runs and logs, never replace them with later passing results.

## Evidence classification and nonclaims

A flushed capture followed by os._exit is a repeatable **platform/process** experiment on a *synthetic fixture writer*, not an actual native campaign capture transaction. It demonstrates deterministic fail-closed read-only admission for visible orphaned files; it does not certify crash atomicity, actual native capture order, hardware power-loss durability, race-proof filesystem custody, safe recovery/resumption, native STEP geometry, engineering use or a complete cross-platform campaign.

MC-041 accepted capability and MC-042 STEP artifacts remain prerequisites for genuine MC-047 qualification. PB-007-01..04 and PO-02/04/05/07/08 remain OPEN. MC-B, MC-F and MC-1 remain NOT_ESTABLISHED. All 26 operations are mandatory; production is unauthorized.

## Review and handoff

Inspect final literal source, actual child-exit oracle, fsync ordering, preservation invariants, negative refusal specificity, cross-platform CI identities, and original failed logs if any. Remain DRAFT after authoring; separate-session critical review, guarded expected-head integration if admissible, and landed-main CI are needed. Owner-account AI-assisted COMMENTED review is not external human approval.
