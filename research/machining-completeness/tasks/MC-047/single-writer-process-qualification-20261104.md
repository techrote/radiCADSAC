# MC-047 — Genuine subprocess ledger-lock and interrupted-owner controls

Status: implementation draft, 4 November 2026. Scope: **platform/process synchronization evidence using synthetic MODEL_ONLY campaign records**. Owning issue: [MC-047 #109](https://github.com/techrote/radiCADSAC/issues/109). Accepted upstream: [MC-045 PR #386](https://github.com/techrote/radiCADSAC/pull/386), merged into source baseline `87b3bfa4387a014f0915a23c7fdf8a6816bcf8c2`. Exact final PR head and CI run IDs belong in the PR evidence checkpoint, not this immutable source file.

## Falsifiable contract

The MC-045 `exclusive_ledger_append_lock` uses `O_CREAT|O_EXCL` and guards canonical ledger replay through write and `fsync`. Existing MC-045 self-test used same-process injected lock files and POSIX replacement. The missing qualification was **separate operating-system processes** challenging the same on-disk lock and slot. The following are mandatory, fail-closed properties:

1. A process demonstrating ownership of the real adjacent lock must prevent a second process from appending. The prior JSONL bytes remain identical.
2. Two subprocesses released from a file barrier against the same one-job/repeat slot must yield precisely one durable append and one refusal. Neither a corrupt JSONL line nor duplicate slot is acceptable.
3. A process killed by `os._exit(17)` *while holding the lock* leaves an observable stale lock; future append attempts must refuse. Only a **deliberate test-operator intervention** deletes the stale lock, after inspecting its contents.
4. Following manual test cleanup, replay and append of the next repeat must succeed; strict replay and canonical JSONL must agree with the original three records.

The test is `single_writer_process_qualification.py` in the same directory. It loads the accepted adjacent MC-045 source by checked repository path, creates fresh temporary files, starts real Python child processes, uses filesystem barriers rather than timing guesses, and enforces 12-second child/barrier timeouts.

## Verification

Run without paid resources or any native geometry:

```sh
python research/machining-completeness/tasks/MC-047/single_writer_process_qualification.py --contract --self-test
python research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python tools/validate_machining_completeness.py --self-test
```

The narrow [MC-047 subprocess workflow](../../../../.github/workflows/mc1-mc047-single-writer-process.yml) (repository root: `.github/workflows/mc1-mc047-single-writer-process.yml`) invokes this against literal PR head or merged-main commit on Ubuntu 24.04 and Windows 2022, Python 3.12. Expected result: the control output reports actual-process MODEL_ONLY PASS on both platforms. Check actual CI job conclusions and final source SHA before describing those outcomes as qualified.

## Interpretation and limits

This does **not** start or certify a native campaign, reserve hardware, establish canonical operation coverage, or authorize manufacturing. Only the test harness Python subprocesses run. Test permits have `dispatch_class=MODEL_ONLY` and never execute their illustrative `command` field. An accepted PROCESS-level synchronization control is not MC-D, MC-F, MC-B or MC-1.

The lock prevents *cooperating* simultaneous Python writers on a local filesystem. It does not establish cross-host distributed filesystem semantics, atomic capture/output custody, durability across power loss, Windows native machining execution, hostile filesystem isolation, ABA protection, or automatic safe stale-lock reclamation. A hard crash can leave a stale lock and a partially written JSONL record, which later replay must refuse; neither the test nor MC-045 repair should silently delete that evidence. A source-level independent review, exact-head CI, guarded merge, and landed-main CI remain required.

## Dependencies and invalidation

Prerequisite artifact: MC-045 `campaign_harness.py` at accepted main containing the lock (#386). MC-041 capability, MC-042 independent native STEP evidence, the PB-007 mathematical proof and release gates are **not** prerequisites for this synthetic control, and remain unsatisfied for later native qualification. Changes to lock acquisition/release, replay ordering, permit schema, subprocess semantics or CI OS/Python pins invalidate this test's specific interpretation and warrant requalification. The frozen MC-038 source/evidence, proof owner and current authority are untouched.
