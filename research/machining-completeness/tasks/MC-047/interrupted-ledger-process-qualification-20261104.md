# MC-047 — Subprocess interrupted-ledger append refusal (4 November 2026)

Status: DRAFT; model-only platform/process qualification, not programme acceptance.

## Source authority and unmet criterion

Selected issue: [MC-047 #109](https://github.com/techrote/radiCADSAC/issues/109). Exact base main df36a07bae551dcc3fd4c7ec63774cae56b49d6c, after [MC-047 #387](https://github.com/techrote/radiCADSAC/pull/387). Accepted [MC-045 campaign harness](../MC-045/campaign_harness.py) implements exclusive append locks, JSONL and fsync. [MC-047 preflight](verify.py) audits evidence read-only. Existing [subprocess tests](single_writer_process_qualification.py) cover contention, race and dead-owner lock, but do not exercise a process terminated after fsync of only a partial ledger line.

Separate proof owner [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100) and draft #388 own different paths; no source proof or shared registry changes are authorized here.

## Falsifiable hypothesis and tests

An abruptly terminated writer may leave a valid historical JSONL prefix followed by an incomplete durable record. The fixture must show the original prefix survives byte-for-byte, fault suffix is accounted for exactly, the stale lock refuses append, and after test-only lock removal canonical replay and preflight still refuse. No truncation, guessed completion or resumption is permitted.

Run from repository root:

- python research/machining-completeness/tasks/MC-047/interrupted_ledger_process_qualification.py --contract --self-test
- python research/machining-completeness/tasks/MC-047/single_writer_process_qualification.py --contract --self-test
- python research/machining-completeness/tasks/MC-047/verify.py --contract --self-test
- python research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
- python tools/validate_machining_completeness.py

New test executes two distinct child-process crashes in fresh temporary directories on Ubuntu 24.04 and Windows 2022 with Python 3.12: (a) 17-byte fragment of canonical next attempt, (b) entire canonical JSON object without final newline. Child writes under the real lock, fsyncs the fragment, writes a marker and exits with os._exit(29). The child deliberately bypasses admitted append_attempt to inject an OS-level fault into disposable synthetic evidence.

For each mode, controls require literal post-sync marker, exact prefix and partial suffix, SHA-256 custody, stranded lock, refusal with specific locked message, and refusal from read-only preflight with specific unterminated ledger line 2 message. After test-only manual lock removal, append/strict load/preflight must still refuse with that exact line error and preserve every ledger and capture byte. A clean original prefix in a separate file must remain parseable and extend through the accepted model append API, without repairing the damaged ledger or authorizing resumed campaigns.

Any unrelated ValueError is a failure, not a successful refusal. All fixtures are ephemeral and MODEL_ONLY.

## Evidence classification, prohibitions and next gate

PLATFORM/PROCESS actual child exit on pinned Windows/Linux runners, plus DETERMINISTIC_MODEL synthetic attempts; not actual native machining, actual STEP, proof closure, transaction atomicity, power-loss guarantee, hostile-filesystem safety, network filesystem lease, cross-host lock, automatic stale-lock reclaim, resumption approval, MC-F or MC-1.

Native MC-047 still requires accepted MC-041 capability and MC-042 native STEP artifact. Future work should build independently reviewed crash-consistent capture/ledger custody and explicit operator recovery protocol, then qualify physical/native operations under an authorized permit. No 26-operation scope or gate change.

## Integration

Dedicated .github/workflows/mc1-mc047-interrupted-ledger-process.yml pins literal source commit SHA on Ubuntu/Windows and executes source-matched upstream contracts and static validation. Keep this PR draft pending separate-session final-head code review, terminal CI and guarded integration. Owner-account COMMENTED is not human APPROVED. Preserve failures in test source, logs and review history.
