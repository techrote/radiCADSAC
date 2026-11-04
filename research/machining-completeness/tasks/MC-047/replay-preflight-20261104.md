# MC-047 — Read-only interrupted-capture replay preflight (4 November 2026)

**Evidence class:** `DETERMINISTIC_MODEL` (synthetic controls only). **Disposition:** provisional engineering interface, NOT MC-047 acceptance. **Current gates:** PB-007-01–04 OPEN; MC-B, MC-D, MC-F and MC-1 NOT_ESTABLISHED; production not authorized.

## Source authority and dependency boundary

- Branch base: `fd287d09d8e794646bb93aa7143338f2a257f970` (accepted `main` at claim); MC-045 source blob: `680ef4fb0f968fe0f4c472d8c3e0769e7d6dfbb8`.
- Accepted upstream: MC-045 campaign harness replay and digest checking, integrated via PR #377; MC-009 evidence contracts. This is an auxiliary post-proof readiness preflight **independent of PB-007 mathematics**, not an MC-047 native qualification.
- Blocking prerequisites: MC-041 **capability** acceptance is absent; MC-042 native STEP artifact and independent qualification are not established; no approved native/paid campaign permit, pinned cross-host tests or durable third-party attestation supplied.
- Scope reservation: [#324](https://github.com/techrote/radiCADSAC/issues/324). Existing proof draft #376 has disjoint five-file MC-038 ownership. No edits to MC-045 upstream or shared registries.

## Hypothesis and falsifier

MC-045's existing row, sequence, canonical JSONL and capture digest checks can be composed into a read-only fail-closed recovery **inspection**: a strict complete ledger or valid prefix is differentiated from orphan/torn/missing/tampered evidence without erasing bytes or claiming safe resumption.

**Falsifier:** any crash-window mutation escapes refusal, any negative terminal becomes a programme PASS, or a partial prefix authorizes automatically continuing paid/native work.

## Implementation / controlled output

`verify.py` uses the actual MC-045 Python source (no local copied implementation), enforces its permit/plan, sequence, canonical JSONL and SHA-256 captured-byte validators, checks ledger and capture inventory for symlinks/non-regular entries, and compares metadata snapshots before and after read-only inspection. It never writes an inspected ledger or capture. It records precisely the digest read from the validated JSONL.

Valid complete slots yield `FULL_SLOT_LEDGER_NOT_PROGRAMME_ACCEPTED`; valid partial slots yield `PARTIAL_PREFIX_NOT_AUTHORIZED_TO_RESUME`. Both contain `resumption_authorized: false` and `programme_acceptance_established: false`. Unreadable/invalid evidence refuses with exit 2. `--allow-native-evidence` is an explicit **read-only inspection acknowledgement** of a native-class record; it authorizes no dispatch, permits, repair or results claim.

## Reproducible test contract

```sh
python3 -m py_compile research/machining-completeness/tasks/MC-047/verify.py
python3 research/machining-completeness/tasks/MC-047/verify.py --contract --self-test
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python3 tools/validate_machining_completeness.py --self-test
```

Thirteen explicitly asserted synthetic controls: complete and partial positive classifications; missing stderr after stdout capture; orphan stdout before ledger commit; committed row with missing stdout; torn trailing JSONL; modified capture digest; duplicate attempt identity; skipped repeat group; capture symlink; ledger symlink; preserved non-PASS CRASH terminal; and an injected post-hash/pre-snapshot capture mutation. The targeted workflow `.github/workflows/mc1-mc047-replay-preflight.yml` executes the contract and upstream self-test with pinned Python 3.12 on Ubuntu 24.04. Tests write exclusively to temporary local directories and do not execute native geometry, paid jobs or network requests.

## Known limitations / explicit NON-CLAIMS

This is not a transaction writer, recovery algorithm, repair procedure, concurrent-write lock, atomic capture+ledger commit, cross-process crash durability proof, or custody attestation. The path-stat pre/post snapshot detects ordinary concurrent modifications, **not** adversarial ABA, TOCTOU, inode replacement in all circumstances, or a filesystem durability guarantee. The MC-045 underlying append remains single-writer and quadratic in repeated prefix validation. This does not establish native machining, STEP correctness, Windows/MSVC behaviour, MC-047 capability, MC-F or production authorization. Data may be safely *read/diagnosed* only after the evidence producer is quiesced and source identities are preserved.

**Future prerequisite:** after independent exact-head review and terminal CI, conduct bounded fault-injected write-side transactional recovery work in a separately owned branch; only after MC-041/MC-042 capability/artifact acceptance and explicit campaign permits proceed to actual pinned Windows/Linux qualification. Do not mark MC-047 complete based on this provisional auxiliary result.
