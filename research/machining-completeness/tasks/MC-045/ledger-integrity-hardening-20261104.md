# MC-045 — deterministic campaign ledger replay and retained-output digest binding

**Status:** independent, proof-adjacent follow-on to the accepted MC-045 static harness; 4 November 2026. **Source base:** `e0d66d075bf69309e283022744e4fd79717b2638`. **Issue:** [MC-045 #107](https://github.com/techrote/radiCADSAC/issues/107). **Scope:** only the MC-045 task-local campaign-harness implementation and this report. **Evidence class:** DETERMINISTIC_MODEL / PLATFORM_PROCESS_EVIDENCE. **Native execution:** none. **Production:** unauthorized.

## Falsifiable admission/replay gap

The previously accepted `campaign_harness.py` admitted each attempt as a standalone record, but an append could extend a truncated/noncanonical ledger or introduce duplicate attempt IDs or the same repeat/job slot twice. Simply checking that stdout/stderr SHA-256 strings are well-formed also cannot establish correspondence to retained bytes.

A replayable campaign ledger must refuse these mutations *without* discarding negative attempts or conflating successful process exit with programme success. An interrupted final repeat is valid partial evidence; an incomplete ledger is **not** a completed campaign. Multiple jobs within one repeat may terminate in either order; later repeats must not start before all prior repeat slots have been recorded.

## Implemented strict checks

`validate_ledger_sequence(rows, permit, plan, require_complete=False)` establishes:

- Bound on total rows: `max_jobs × sequential_repeats`.
- Unique `attempt_id` and unique `(repeat_index, job_index)` terminal records.
- Repeat-group order: the record at ordinal `i` must belong to repeat `floor(i / max_jobs)`, but job completions within the same group are unordered.
- Each record satisfies the accepted permit/plan/binding/terminal and resource checks.
- Explicit `require_complete=True` refuses a missing planned slot. Default partial-prefix mode preserves a crash/interruption without falsely declaring completion.

`load_ledger` now requires newline-terminated **canonical JSONL bytes**. Truncated final lines, duplicate JSON keys, whitespace-altered/noncanonical records, blank lines and malformed JSON are refused, not silently normalized. `append_attempt` checks the entire existing ledger prefix and next record before appending, then retains the original fsync durability behaviour. It assumes a single writer; this patch **does not** implement cross-process locking or atomic multi-file capture/ledger transactions.

`verify_retained_captures(rows, capture_dir)` independently computes SHA-256 from the retained stdout/stderr bytes for each row, using position-derived `000000.stdout.bin` and `000000.stderr.bin` naming, and rejects a missing/modified/symlinked/unexpected capture. Position-based file names avoid trusting `attempt_id` as a filesystem path. This checks correspondence between stored bytes and recorded identities; **it is not independent attestation** and cannot prove that the process originally produced those bytes. `output_bytes` is not assumed equal to stdout+stderr because its existing meaning may include other output.

## Read-only replay interface

```sh
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py audit-ledger \
  --permit /path/to/approved-permit.json \
  --plan /path/to/plan.json \
  --ledger /path/to/attempts.jsonl \
  --captures /path/to/captures \
  --require-complete
```

Omit `--require-complete` only to inspect incomplete-prefix evidence, **not** to claim that a campaign finished. The `--allow-native` flag solely enables read-only validation of an externally approved native permit; it is not a permit, dispatch capability, or authorization to run a campaign. The reported ledger SHA-256 can be retained in independent custody metadata but cannot establish trusted provenance on its own.

The original `validate`, `account` and `self-test` commands are unchanged; no command here dispatches a native or paid process.

## Deterministic positive/negative qualification

Executable through the task's existing self-test and verifier:

```sh
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python3 research/machining-completeness/tasks/MC-045/verify.py --contract --self-test
python3 tools/validate_machining_completeness.py --self-test
```

Positive controls: complete 3-repeat ledger, accepted partial prefix, genuine TIMEOUT/RESOURCE_EXHAUSTED/CRASH retention, valid capture-byte replay and out-of-order *jobs within one repeat*. Negative controls: incomplete ledger mislabelled complete, duplicate identity, duplicate slot, skipped/reordered repeat, excess rows, invalid row type, damaged stdout capture, absent capture, unregistered extra file, truncated JSONL, noncanonical whitespace, duplicate JSON object keys, blank lines and attempted extension of corrupted ledger without altering existing bytes. All fixtures are synthetic MODEL_ONLY and do not imply native correctness.

## Critical review boundaries and downstream invalidations

- **Performance:** pre-append full-prefix revalidation is linear per append and quadratic over an entire long run. This is a bounded correctness improvement, **not** qualification of the MC-046 10k-scale ladder. Measure and design an independently checkable indexed/single-writer journal before large real campaigns.
- **Concurrency:** one writer is assumed. Concurrent processes, cross-platform file locks, crash atomicity across capture files, and secure custody/signature identities remain separate issues, particularly for MC-047.
- **Evidence authenticity:** two mutually modified artifacts can carry matching hashes. External producing-run attestation and independently retained manifests are necessary before a source/candidate output claim.
- **Gates:** no MC-B, MC-C, MC-D, MC-E, MC-F or MC-1 gate is changed. PB-007-01–04 remain open; all 26 operations remain required. No geometry, STEP or manufacturing capability follows from an audit of synthetic ledger structure.

**Next prerequisite:** fresh exact-head CI, independent technical review of this file-level change, guarded integration only if source and required workflows pass, followed by merged-main qualification. Future MC-046/047 runner integration must retain native output bytes and independent provenance under an explicit permit; it must not substitute synthetic captures for actual measurements.
