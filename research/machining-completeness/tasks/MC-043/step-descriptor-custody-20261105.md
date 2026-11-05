# MC-043 STEP evidence descriptor/alias custody qualification

Status: **provisional implementation and negative controls; not independent STEP consumer acceptance** (2026-11-05 UTC).  
Owner: MC-043 / [issue #105](https://github.com/techrote/radiCADSAC/issues/105). Coordination: [#324](https://github.com/techrote/radiCADSAC/issues/324).  
Base main: `22b6bafaa22f7ef2e14fd2b43606cab9a0eba00a` (merged MC-1 #404); branch: `fix/mc043-step-descriptor-custody-20261105`.  
Evidence class: **DETERMINISTIC_MODEL / local-filesystem source-level custody controls**; no native geometry, STEP parser, BRL-CAD invocation or paid native run.

## Accepted sources and exact scope

The task is governed by AGENTS.md, DR-0026, MC-1 00-PROGRAMME, 07-EXECUTION-PROTOCOL, 12-ROADMAP, 77-MC038-CURRENT-IMPLEMENTATION-STATE, task graph, issue #105, and the accepted MC-043 receipt-preflight source. The provisional MC-017 BRL-CAD consumer probe is source-viable but has no measured import; MC-040 and MC-042 do not supply a qualified native STEP-through-independent-consumer transaction. The primary MC-038/PB-007 mathematical owner and issue #100 are out of scope.

The original MC-043 `consumer_receipt_preflight.py` checked `safe_file()` and subsequently reopened the pathname to hash bytes. That was a byte-integrity test, not an exclusive file identity check. An attacker or concurrent external writer could replace the approved path with another inode containing exactly the expected bytes, or retain an external hard link to the same inode. A SHA-256 match alone does not establish the local artifact custody boundary.

## Bounded correction and falsification

The preflight's STEP artifact hash now uses a checked, read-only file descriptor. It requires a regular, uniquely linked inode; opens with `O_NOFOLLOW` where available; compares dev/inode/mode/link count/size/mtime/ctime metadata across initial `lstat`, descriptor `fstat` before/after reading, and final pathname `lstat`; and refuses filesystem exceptions instead of treating them as success. All receipt, body, item, seam, lineage and empty-material rules remain unchanged.

**Falsification criterion:** an external hard-link alias or a deterministic same-byte inode substitution between initial path examination and descriptor acquisition or between descriptor acquisition and data read is accepted as `STRUCTURAL_PREFLIGHT_ONLY`, or existing valid empty/nonempty structural controls stop passing.

Tests in `verify.py` preserve two synthetic positive controls and all original 34 negative controls. Three additional required refusals are: (1) same-byte external alias (hard link); (2) replacement before `os.open` with exact same bytes; (3) replacement after checked `os.open` but before `os.fdopen`/hash. The two swap controls assert injection executed and original expected bytes remain unchanged. Total required negative controls: **37**.

Run on each Windows/Linux hosted platform at literal PR-head commit:

```sh
python3 -m py_compile research/machining-completeness/tasks/MC-043/consumer_receipt_preflight.py research/machining-completeness/tasks/MC-043/verify.py
python3 research/machining-completeness/tasks/MC-043/verify.py --contract --self-test
python3 tools/validate_machining_completeness.py
```

The dedicated Actions workflow `mc1-mc043-step-descriptor-custody.yml` must guard `git rev-parse HEAD` against the PR's literal head (or push commit) and run the same commands on Ubuntu and Windows. The existing MC-043 workflow remains unchanged. Retain all failed attempts and run IDs in the PR handoff.

## Boundaries, assumptions and remaining risks

This control does **not** establish atomic protection against a malicious privileged actor swapping file paths out and back between snapshots, mid-file content rewriting with forged metadata, network/cross-host locking or power-loss durability. Nor does it attest that any purported STEP content is STEP; the positive bytes are deliberately synthetic NON-STEP data, testing metadata refusal only. Hash collision is outside the bounded model, and Windows inode/ctime semantics cannot be assumed identical to Unix. The receipt still does not directly bind actual independent consumer process executions, gqa measurements or downstream material correctness. Other source certificate/lineage files are still digest declarations without raw-byte custody here.

MC-043's independent import and engineering-operation acceptance stays OPEN. MC-B, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`; PB-007-01/02/03/04 remain OPEN; all 26 required operations are unchanged. No production, release, native campaign or permit is authorized.

## Integration / invalidation discipline

Review exact resulting diff and failed negative controls first. Literal-head and supplemental static CI, followed by an independent source-critical review, are required before any Ready/merge choice. On review admission, guarded merge and merged-main CI are separate steps. This patch concerns only provisional MC-043 receipt evidence custody; it does not modify source corpora, proof cases, canonical outcomes, accepted MC-B/MC-1 gate states, programme/shared schemas, or the primary proof worker's files.

Next prerequisite: a source-authenticated MC-042 STEP artifact and MC-040 composed material journey, followed by actual independent BRL-CAD process logs/results and material correctness challenges under the appropriate native permit.
