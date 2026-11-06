# MC-037 — Source-pinned rational allocation planning seam (6 November 2026)

**Status: DETERMINISTIC_MODEL / PLAN_ONLY / NOT_EXECUTED.** Issue [MC-037 #99](https://github.com/techrote/radiCADSAC/issues/99). Isolated base: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. This is a future interface/refusal harness, **not** a completion of MC-037, PO-06, PO-09, PB-007, MC-B, MC-D or MC-1.

## Unmet acceptance criterion and falsifier

A downstream reconstructed-solid comparison must not silently lose any of its source-normalization, sweep, material, topology, reconstruction or STEP-handoff *planning allocations*, overbook the requested error budget or convert a proposal into a success receipt. This tool checks only a non-compensating **explicitly ordered six-stage allocation denominator** using exact rationals, rejects ambiguous/malformed/duplicate-key JSON, and refuses unauthenticated source-contract substitution. It makes **no statement** that an actual stage can meet its allocation or that summing allocation tokens proves a valid end-to-end error bound.

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

The source-owned self-test includes canonical stage-order reversal, duplicate and omission, missing/surplus stage, negative/zero/oversubscribed/unreduced/oversized rationals, numeric type confusion, duplicate top-level and nested keys, NaN/float/invalid UTF-8, source pin drift, attempted native/PO/MC gate promotion, file-size and filesystem alias refusal. Optional hard/symlink tests are only counted where the OS supports creation. The checker uses a descriptor/path identity comparison but does not guarantee atomic custody against a malicious concurrent writer.

Expected safe verdict: `ALLOCATIONS_WITHIN_PROVISIONAL_REQUEST_NOT_GEOMETRY_QUALIFIED`, with `native_executed=false`, `geometry_qualified=false`, `mc_1_established=false`, `production_authorized=false`.

No manufacturing release, native STEP success, geometry error certificate, real acceptance result, MC-B/D/E/F/MC-1 gate decision or production authorization follows. All 26 operations and all required source cases remain in scope. The separate #397 owner retains the exclusive main integration lease; **do not merge** this draft until coordination and independent source review, then rerun merged-main CI.

## Same-session source-critical correction

Initial PR head `8d299e93440d5df56f57e8b7333ed48b0957c74d` passed hosted controls but did **not** assert execution-stage order: the stage allocation map was compared only by its key set. Technical [REPAIR comment](https://github.com/techrote/radiCADSAC/pull/433#pullrequestreview-5798822740) preserved that negative finding. The correction introduces explicit required `stage_order` equal to the six source→STEP stages and four on-disk permutation/multiplicity/type refusals. New literal-head qualification is required; first-head green CI is superseded evidence, not final admission.

## 6 November — bounded JSON nesting and deterministic refusal correction

The already-corrected `parse_int` guard does not address a different input hazard: a well-formed JSON document consisting of 10,000 nested arrays around `null` fits within this preflight's 32 KiB byte cap, but the previous `read_file` called `json.loads` without a nesting limit or `RecursionError` catch. An independent CPython 3.13 reproducer raises `RecursionError` for that 20,004-byte specimen, bypassing the expected typed `Refused` result. Parser recursion depth varies by Python runtime; this is an ingress failure-control defect, not a geometric theorem.

The corrected reader scans decoded UTF-8 for JSON container depth before calling `json.loads`, treating escaped quotes/backslashes and quoted delimiters as nonstructural. It refuses more than **32** container levels; Python's JSON decoder remains responsible for exact grammar, bracket matching and Unicode escape rules. Unexpected `RecursionError` or `OverflowError` from the decoder is also translated to typed refusal. New **actual on-disk** controls check depth 33 and 10,000 refusal specifically for the nesting budget, and positive parser-only controls check escaped/quoted bracket sequences and depth 32. Existing all-schema, source identity, exact-rational, stage-order, file custody and nonpromotion tests must continue to pass.

This limit is exclusively for a small auxiliary `PLAN_ONLY` JSON proposal; it is not a limit on native geometry, machining operations, STEP complexity or tolerated manufacturing features. At this correction checkpoint PR #433 is deliberately **Draft**, requiring fresh literal corrected-head Ubuntu/Windows and MC-1 static validation plus a *new distinct-session source review* before Ready. All 26 required operations, PB-007/PO obligations, MC-B/MC-1 `NOT_ESTABLISHED`, native/paid campaigns and production prohibitions remain unchanged. No source/certificate authority is conferred by passing these checks.
