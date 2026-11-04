# MC-047 — Read-only custody alias and restored-mtime mutation refusal

**Date:** 4 November 2026. **Evidence class:** `DETERMINISTIC_MODEL` / synthetic offline negative tests. **Disposition:** bounded post-proof recovery-preflight hardening; **NOT** MC-047 native acceptance.

## Authority and exact baseline

- Authoritative branch base when claimed: `2cbc2f2991672fdebe21ecc1100a63a0a91a8908` (merged MC-045 tariff PR #380), 4 November 2026. Always reverify main before integration.
- Task: [MC-047 #109](https://github.com/techrote/radiCADSAC/issues/109), coordination [#324](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6637286110). This changes only MC-047's existing read-only verifier and this task-scoped memo.
- Accepted upstream: MC-045 deterministic canonical ledger and retained-capture verifier, plus MC-047's 13 synthetic crash-window controls from merged #379. All actual geometry dependencies remain open: MC-041 native capability and MC-042 native STEP artifact.
- `handoffs/current-authority.json` denies production; DR-0026 and programme keep 26 operations in scope. PB-007-01–04 remain open; MC-B, MC-F and MC-1 are **NOT_ESTABLISHED**. Neither a proof owner nor an expensive-campaign permit is altered by these checks.

## Concrete source defect, hypotheses and falsification

`MC-047/verify.py:fingerprints` originally inventoried per-path device/inode metadata but **did not check identity uniqueness**. Two different capture filenames hard-linked to the same empty byte stream passed both SHA-256 and inventory checks; a later write to one filename could silently modify the other's retained bytes. This is not independent file custody.

The same pre/post fingerprint compared inode, mode, size and `st_mtime_ns` but omitted `st_ctime_ns`. On Linux/POSIX, after initial digest verification, a same-size byte rewrite followed by explicit mtime restoration can evade those old metadata fields.

**Hypothesis:** an alias-free inventory combined with POSIX change-time metadata refuses these two attacks without changing valid full/partial prefix classifications or promoting a failed terminal to PASS.

**Falsifier:** any hard-linked stdout/stderr alias accepted as two independent captures; any POSIX equal-length post-digest rewrite with restored mtime accepted by a quiescent read-only audit; or any existing good fixture refused solely due to the additional metadata.

## Implementation and executable evidence

- Record `st_ctime_ns` alongside device, inode, mode, size and nanosecond modification time in both pre- and post-inspection fingerprints.
- Require distinct `(st_dev, st_ino)` among ledger and *all* capture entries. Reject hard-linked aliases before trusting any ledger result.
- Add an explicit hardlink negative fixture with two correctly hashed empty streams referring to one inode.
- Add a POSIX-only post-hash mutation injector: a valid four-byte capture is rewritten to different four-byte content; the injector restores its prior nanosecond mtime; the verifier must refuse based on the changed ctime.
- Preserve the original 13 controlled tests and the successful `FULL_SLOT_LEDGER_NOT_PROGRAMME_ACCEPTED` / `PARTIAL_PREFIX_NOT_AUTHORIZED_TO_RESUME` statuses.

Run from repository root:

```sh
python3 -m py_compile research/machining-completeness/tasks/MC-047/verify.py
python3 research/machining-completeness/tasks/MC-047/verify.py --contract --self-test
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python3 tools/validate_machining_completeness.py --self-test
```

Existing `.github/workflows/mc1-mc047-replay-preflight.yml` matches changed MC-047 source and verifies literal PR head on Ubuntu 24.04 / Python 3.12. Its targeted workflow and MC-1 static CI must both be terminal before integration; after merge rerun checks on *merged main*. Do not infer qualification from an earlier SHA.

## Security, platform and acceptance limitations

This check rejects **static** hardlink identities present during the two inventory snapshots. The `st_ctime_ns` behaviour is a POSIX metadata signal, **not a cross-platform guarantee**; some Windows APIs report creation time as ctime, and coarse timestamps, hostile concurrent writers, races before/after snapshots, ABA or inode reuse may bypass detection. Filesystem identity is not a cryptographic independent custody attestation. No write-side transaction/lock, fsync policy, recovery/resumption permission, native Windows/MSVC qualification, actual STEP/solid correctness or manufacturing authorization is established.

All local test outputs are synthetic. Under these limitations, the verifier can support **read-only diagnosis of quiescent retained evidence**, not a native proof, permission to resume interrupted campaigns or MC-047 acceptance.

## Following prerequisites

Independent exact-head technical review and CI, guarded integration, merged-main CI, then separately owned durable capture transaction/locking and cross-platform fault-injection work with explicit permits. Native practical acceptance remains blocked on MC-041/MC-042 and separate MC-F/MC-1 decisions.
