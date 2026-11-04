# MC-045 follow-up — Fail-closed attempt success and output-digest identities

Status: **implementation proposed; qualification pending literal-head CI** (4 November 2026). Evidence class: `DETERMINISTIC_MODEL` / `PLATFORM_PROCESS_EVIDENCE` (contract checking only). This is an amendment to the already accepted static MC-045 harness, **not** a change to its capability/gate verdict, and not an MC-038/PB-007 proof.

## Authority, exact source and ownership

- Base/main observed before implementation: `35c4d8fbd1ff9e54cbacabb8109b19e7d0c31dfb`.
- Existing static MC-045 harness: `research/machining-completeness/tasks/MC-045/campaign_harness.py`, starting blob `209f031bf6f1b7f51feda3f75477274e44cc983f`.
- Selected issue: [MC-045 #107](https://github.com/techrote/radiCADSAC/issues/107). Original accepted static MC-045 result and review remain preserved.
- Disjoint owner: MC-038/PB-007 maintains its own proof/evidence; concurrent RCS-002 owns `tools/validate_repo.py` and `tools/test_validate_repo_journal.py`. Neither is edited here.
- Exact write set: the MC-045 harness and this task-local report. No proof/programme registries, frozen historical evidence, authority, CI workflows, STEP or native runner are touched.
- No native campaign, paid permit, production creation or proof-gate claim authorized.

## Falsifiable failure

The pre-change `validate_attempt()` required nonempty output hash strings but did not check that they were canonical SHA-256 identities; and it did not require a zero process exit for a `SUCCEEDED` terminal. Consequently, a manually assembled attempt could claim `terminal_reason=SUCCEEDED` and `programme_pass=true` while carrying `return_code=1`, `return_code=null`, arbitrary `stdout_sha256` or a malformed `stderr_sha256`, and pass validation before entering a durable ledger. Unhashable malformed terminal values could also cause a membership-check `TypeError` rather than a named refusal. Such evidence must fail closed.

## Bounded mitigation and acceptance controls

`validate_attempt()` now checks canonical lowercase `sha256:` followed by 64 hexadecimal digits for both captured stream digests and requires an integer process return code, with `return_code == 0` for `SUCCEEDED`. Non-success terminals may retain a null or integer return code; failures cannot carry `programme_pass=true`.

The existing `MODEL_ONLY` self-test remains authoritative for the original controls: three sequential successful synthetic attempts, three retained fault terminals (TIMEOUT, RESOURCE_EXHAUSTED, CRASH), exact reserved 120 vCPU-seconds, permit/plan binding mismatch refusals, oversubscription and cap refusals. Added deterministic negative cases:

| Mutation | Required verdict |
|---|---|
| Successful attempt with exit code 1 or null | REFUSE |
| Successful attempt with `true` or `"0"` exit code | REFUSE |
| Output digest `unknown` | REFUSE |
| Output digest wrong alphabet, uppercase or 63 hex digits | REFUSE |
| Missing or null stderr digest | REFUSE |
| Terminal as array or unrecognized string | REFUSE (not traceback) |
| Crashed attempt with list return code | REFUSE |
| Zero-exit successful process with `programme_pass=false` | ACCEPT as process success, **not** programme pass |
| Crash return code 139, or timeout null | Preserve valid non-pass terminal |

These controls have no bearing on source-specific PB-007 ordered-premise closure.

## Exact commands and gates

```sh
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python3 research/machining-completeness/tasks/MC-045/verify.py --self-test
python3 tools/mc_workflow.py verify MC-045
python3 tools/validate_machining_completeness.py --self-test
```

The final PR head must pass its applicable automatic GitHub CI, including `mc1-static`, before a source-reviewed guarded merge. Preserve any failures/unfinished checks; a locally passing deterministic self-test is not native qualification.

## Retained limitations and nonclaims

This is a **static attempt-admission integrity** fix. It does not cryptographically attest that stream bytes actually correspond to the supplied digest; a downstream collector must compute hashes itself. It does not establish authenticity of a programme-issued permit, uniqueness of a complete multi-attempt ledger, native candidate correctness, independent STEP import, Windows/Linux platform qualification, or real billing. Those remain separately owned and cannot be inferred from successful deterministic controls. No historical corpus count, operation denominator or gate changes: PB-007-01–04 OPEN; MC-B and MC-1 NOT_ESTABLISHED; production unauthorized.
