# MC-045 auxiliary — bounded retained-capture inventory traversal (6 November 2026)

**Status:** proposed source-level repair on an isolated branch; never a native capability or production acceptance. **Related issues:** [MC-045 #107](https://github.com/techrote/radiCADSAC/issues/107) (accepted historical static harness) and [MC-047 #109](https://github.com/techrote/radiCADSAC/issues/109) (platform/recovery qualification still open). **Source base:** main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`, accepted `campaign_harness.py` Git blob `b13507ec72a9c6dea11227a14efc1a18f851269a`. This is a distinct direct-reader improvement, not a duplicate of [MC-047 PR #422](https://github.com/techrote/radiCADSAC/pull/422).

## Defect and falsifiable admission boundary

The accepted `MC-045/campaign_harness.py:verify_retained_captures` uses a bounded **ledger-derived expected-name set** for exactly two streams per row, but subsequently computes `{entry.name for entry in capture_dir.iterdir()}` without an entry budget. Even though the resulting set must equal the expected names, a directory with arbitrarily many surplus entries causes the checker to enumerate and allocate each name **before** refusing. This is resource amplification during *read-only evidence inspection*; it does not imply successful or authentic native output.

**Claim under test:** after streaming and validating the expected retained bytes, inventory membership must stop immediately on an unexpected filename and must refuse if an expected filename is missing. Each matching name is consumed at most once from the ledger-derived set, so there is no allocation over surplus names. Existing successful full-prefix replay, hash validation, one-link regular-file identity, append quarantine, duplicate/missing evidence and all permit checks must continue to hold. The checker must **never** authorize campaign dispatch or recovery.

## Implementation and deterministic controls

In the same accepted MC-045 source entry point, replace the unbounded `actual` directory set with a membership check against the already-built `expected` set. On each directory entry: if its name is absent from the remaining expected set, immediately refuse with the existing inventory mismatch error; otherwise remove it from the set. At end, refuse if any expected name remains. This remains a cooperative snapshot check; no false claim of atomic filesystem consistency is made.

The embedded `self-test` exercises an actual retained six-file, three-attempt positive control and on-disk surplus-file refusal, then a deterministic adversarial generator producing a single unexpected entry followed by an assertion if iteration resumes. A positive checker stops after one yielded surplus entry; the original full-directory set comprehension would exhaust the generator and fail. Original hard-link, missing-file, digest mutation, ledger crash/quarantine and post-hash mutation tests remain in the same self-test.

Reproduce without native tools:

```sh
python research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python research/machining-completeness/tasks/MC-045/verify.py --self-test
python tools/validate_machining_completeness.py --self-test
```

The dedicated Windows/Linux workflow pins literal PR-head checkout and checks exact Git SHA before running both MC-045 deterministic suites. Final exact commit, CI run links, failed-run custody and review disposition belong in the PR handover; a green synthetic PR-merge workflow is not a literal-head demonstration.

## Nonclaims, dependencies and follow-on

**Evidence class:** `DETERMINISTIC_MODEL` / local files only. This does not provide an atomic or adversarial-filesystem directory snapshot, total resource caps for an arbitrarily large permit, platform-native physical recovery, B-rep geometry, native STEP, capability qualification, or manufacturing authority. MC-047 has a separate plan-bounded metadata fingerprint improvement in #422; the MC-045 direct verifier uses ledger-derived names and improves a different read path. Explicit permits, capped resource accounting and sequential repeats remain required for any future genuine campaign.

PB-007-01–04 and MC-B/MC-D/MC-E/MC-F/MC-1 remain open / `NOT_ESTABLISHED`. All 26 required machining operations remain mandatory. Do not merge while the independent #397 integration owner holds `main`, or without distinct-session source review, exact-head CI and subsequent landed-main checks. No accepted outcome, canonical authority, proof/programme register, frozen source or production file is changed.
