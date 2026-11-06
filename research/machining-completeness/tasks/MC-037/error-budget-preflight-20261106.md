# MC-037 — Source-pinned rational allocation planning seam (6 November 2026)

**Status: DETERMINISTIC_MODEL / PLAN_ONLY / NOT_EXECUTED.** Issue [MC-037 #99](https://github.com/techrote/radiCADSAC/issues/99). Isolated base: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. This is a future interface/refusal harness, **not** a completion of MC-037, PO-06, PO-09, PB-007, MC-B, MC-D or MC-1.

## Unmet acceptance criterion and falsifier

A downstream reconstructed-solid comparison must not silently lose any of its source-normalization, sweep, material, topology, reconstruction or STEP-handoff *planning allocations*, overbook the requested error budget or convert a proposal into a success receipt. This tool checks only a non-compensating **six-stage allocation denominator** using exact rationals, rejects ambiguous/malformed/duplicate-key JSON, and refuses unauthenticated source-contract substitution. It makes **no statement** that an actual stage can meet its allocation or that summing allocation tokens proves a valid end-to-end error bound.

The six equal positive allocations in the positive synthetic proposal and the 1 micrometre illustrative trial request are **test fixtures**, not a customer tolerance, minimum representable feature, approved MC-004 campaign, or a production bound. The 32-digit rational and 32 KiB file caps apply only to this cheap auxiliary preflight, not the machining domain or native arithmetic.

## Exact source custody and dependencies

Read-only accepted Git blob pins, verified by `git hash-object` on the current checkout:

- MC-003 `numeric-encoding-contract-v1.json`: `a5538cab698c806fdedcef7cf563b650638348e0` — exact source semantics and refusal of binary-float authority.
- MC-015 `certificate-attack-contract-v1.json`: `f9b7324644db9af125baf14b37c06bae16a24ff3` — independent certificate-trust and material/body controls.

Issue #99's MC-038 **capability** prerequisite remains blocked; MC-031–036 and MC-015 **artifact** dependencies are not falsely promoted. This harness uses no solver/kernel/oracle, candidate source or native geometry and does not change shared source/certificate specifications. A future MC-037 owner must replace its example allocations with independently justified requirements and ultimately prove actual independent geometric error statements with a certified composition rule, rather than reusing this PLAN_ONLY result as evidence.

## Verification

Run from the repository root:

```bash
python research/machining-completeness/tasks/MC-037/error_budget_preflight.py --self-test
python research/machining-completeness/tasks/MC-037/error_budget_preflight.py --emit-proposal > proposal.json
python research/machining-completeness/tasks/MC-037/error_budget_preflight.py --check-file proposal.json
python tools/validate_machining_completeness.py
```

The source-owned self-test includes missing/surplus stage, negative/zero/oversubscribed/unreduced/oversized rationals, numeric type confusion, duplicate top-level and nested keys, NaN/float/invalid UTF-8, source pin drift, attempted native/PO/MC gate promotion, file-size and filesystem alias refusal. Optional hard/symlink tests are only counted where the OS supports creation. The checker uses a descriptor/path identity comparison but does not guarantee atomic custody against a malicious concurrent writer.

Expected safe verdict: `ALLOCATIONS_WITHIN_PROVISIONAL_REQUEST_NOT_GEOMETRY_QUALIFIED`, with `native_executed=false`, `geometry_qualified=false`, `mc_1_established=false`, `production_authorized=false`.

No manufacturing release, native STEP success, geometry error certificate, real acceptance result, MC-B/D/E/F/MC-1 gate decision or production authorization follows. All 26 operations and all required source cases remain in scope. The separate #397 owner retains the exclusive main integration lease; **do not merge** this draft until coordination and independent source review, then rerun merged-main CI.
