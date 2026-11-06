# MC-047 — Bound read-only replay capture inventory to admitted campaign slots

Status: **provisional, candidate qualification only** (6 November 2026 UTC). Owner issue: [MC-047 #109](https://github.com/techrote/radiCADSAC/issues/109). Source starting point: main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`.

## Scope and admission hypothesis

The read-only model replay preflight `MC-047/verify.py::fingerprints` originally accumulated and sorted all directory entries from `captures.iterdir()` before checking whether the inventory was compatible with a validated permit/plan. An unexpected very large directory could grow Python tuples and metadata lookups without an accounting-derived bound, even when the correct outcome is REFUSED.

**Hypothesis:** after `MC-045.validate_plan` accepts a permit/plan, every admissible capture directory has at most `2 * plan.max_jobs * plan.sequential_repeats` entries (one retained stdout and stderr per planned attempt); the original replay implementation must reject the `limit+1`-th entry before further `lstat` and tuple allocation. Missing captures are still independently refused by the existing downstream digest/inventory contract; an incomplete *ledger prefix* is not misclassified as an accepted completed campaign.

**Falsifiers:** a seventh entry is accepted for the synthetic 1-job/3-repeat plan; an ordinary six-entry full-prefix record is refused; a partial prefix no longer reports `PARTIAL_PREFIX_NOT_AUTHORIZED_TO_RESUME`; late quarantine/digest faults bypass; a Windows or Linux regression occurs.

## Increment and source-level contract

Only `research/machining-completeness/tasks/MC-047/verify.py` changes production-adjacent research code. `fingerprints` now requires a nonnegative integer directory-entry budget and checks entry count *at the start* of each enumeration iteration. `audit` computes this budget only after `validate_plan` and passes it to **both** evidence fingerprint snapshots; the same protected plan controls each pass. Prior direct test-injection callbacks now preserve the required budget argument, preventing mocked fingerprints from silently disabling the new contract.

The deterministic original `self_test` adds an on-disk over-budget inventory with exactly six expected streams plus one orphan and checks the **specific** budget-refusal message, not simply any thrown error. The original partial/full-prefix, torn-ledger, orphan-stream, hard-link, lock-quarantine, actual capture mutation, posthash and metadata-masked doublepass controls remain. Expected self-test count changes from 19→20 on POSIX and 18→19 on Windows.

## Verification

```sh
python research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python research/machining-completeness/tasks/MC-047/verify.py --contract --self-test
python tools/validate_machining_completeness.py --self-test
```

The existing `mc1-mc047-replay-preflight` Ubuntu workflow and the other MC-047 Linux/Windows workflows route `verify.py` changes without editing global workflow configuration. Use **exact literal PR-head** checkout and terminal workflows before any admission; preserve failures and record run IDs on the PR. Do not infer Windows qualification from Linux-only jobs.

## Classification, prerequisites and limitations

**Evidence class:** deterministic model and local process/filesystem-contract qualification. No native geometry execution, STEP parsing, recovery, release, resumption, or manufacturing authorization. A finite plan count does not constrain individual retained capture file sizes; the separate MC-045 streaming digest and permit storage contract remain the relevant controls. A hostile writer continually mutating the directory can still race enumeration and both snapshots; this change does not claim atomic or adversarial-filesystem attestation.

**Dependency boundary:** MC-041 genuinely qualified native capability is **not** present, so the MC-047 final Windows/Linux native-recovery acceptance cannot be asserted. All required PB-007 branches remain OPEN; MC-B, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`. All 26 machining operations remain mandatory; no domain or output profile change. Shared proof, programme, authority, frozen audit and issue #100 evidence are untouched. The separate #397/main integration owner must release its reservation before any guarded merge.

## Next action

Run independent source-critical review on the exact new PR head (review account attribution is not human APPROVED). If admitted, coordinate guarded integration after the separate main owner releases, verify landed blobs and run merged-main CI. Full MC-047 native/platform qualification remains blocked on accepted MC-041 plus explicit resource-authorized campaigns and independently frozen workloads.
