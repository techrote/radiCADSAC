# MC-045 — ledger inode/alias append admission (4 November 2026)

Status: draft, implementation test required; **DETERMINISTIC_MODEL / LOCAL_FILESYSTEM_PROCESS** only. Parent [MC-045 #107](https://github.com/techrote/radiCADSAC/issues/107). Source base `803d2ad93dd9e6d7409b4961423ccbc17ce90578`. Intended PR: `fix/mc045-ledger-inode-alias-20261104`.

## Contract and falsifiable defect

`campaign_harness.append_attempt` already held a cooperative per-*pathname* exclusive-create append lock. Previously it parsed a ledger using `path.open("rb")` and subsequently opened the same textual pathname for append using `path.open("ab")`. A symlink or hard link could alias a different path with a *different* lock name. Both paths could therefore append to the same physical inode, defeating per-name serialization and potentially altering retained evidence. A path replaced after replay could also redirect the later append. No mathematical, native kernel or manufacturing success is implied.

**Hypothesis:** static non-aliased inode admission and a descriptor held throughout replay/append stop the alias and deterministic name-swap controls while preserving ordinary existing/new ledger appends. **Falsifiers:** an aliased ledger accepts an append, a swapped ledger name is appended after replay, or a clean append incorrectly refuses.

## Implementation boundary

- Under the existing cooperative append lock, classify the ledger with `lstat` rather than following final-component symlinks. Existing ledgers must be regular, have a nonzero filesystem inode and link count exactly 1; absence is allowed only for exclusive creation.
- Use one `O_RDWR|O_APPEND` file descriptor across canonical JSONL replay, sequence validation and `fsync`. An absent ledger uses `O_CREAT|O_EXCL`. Where supported, use `O_NOFOLLOW` for existing files. The same streaming parser supplies both the read-only reader and the held-descriptor writer.
- Compare descriptor and named-path device/inode, link count, length and modification/change-time snapshots before and after replay. On a mismatch, refuse without writing. Continue preserving interrupted/corrupted record refusal and stale lock behavior. New runs cannot silently reclaim stale locks.
- This is not a security boundary against hostile actors with arbitrary write access, mutation after the last check, parent-directory substitution, distributed filesystem semantics, time metadata forgery, power loss or crash-atomic multi-artifact transactions. A short or interrupted append still requires manual evidence review.

## Deterministic controls

Run:

```sh
python research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python research/machining-completeness/tasks/MC-047/verify.py --contract --self-test
python research/machining-completeness/tasks/MC-047/single_writer_process_qualification.py --contract --self-test
python research/machining-completeness/tasks/MC-047/interrupted_ledger_process_qualification.py --contract --self-test
python tools/validate_machining_completeness.py
```

Existing MC-045 canonical replay, resources, ledger corruption, capture digest/alias and cross-process controls must remain passing. Newly added controls exercise (1) both a base path and alternative hardlink path to the same inode, refusing both; (2) a symlinked ledger, refusing with unchanged target (POSIX mandatory; Windows only where symlink privilege is present); (3) a POSIX parser-triggered atomic file-name replacement after replay, refusing without altering replacement contents; and (4) subsequent ordinary independent ledger append succeeds without a stranded lock. Tests may not substitute model controls for native qualification.

## Scope, dependencies and remaining gate

Exactly one existing source file and this task-local RAG file change. No MC-038 source, proof, programme or frozen evidence, current authority, task graph, issued #100 evidence, STEP or manufacturing implementation changes. The prerequisite for this local model-only test is the already accepted MC-045 source-matched campaign harness; **MC-041**, **MC-042**, the full **PB-007** mathematical contract, **MC-B**, **MC-F**, **MC-1** and real Windows/MSVC native/STEP qualification remain unestablished unless independently accepted under their separate gates. All 26 supported operations remain required; production remains unauthorized.

Do not merge on local inspection alone. Require literal final-head CI, source-level review including negative evidence, conflict/owner recheck, conditional guarded integration and independent merged-main checks. Same-account AI `COMMENTED` does not constitute human `APPROVED`.
