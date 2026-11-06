# MC-048 — Source-pinned practical-cell denominator preflight (6 November 2026)

**Issue:** [MC-048 #110](https://github.com/techrote/radiCADSAC/issues/110). **Evidence class:** deterministic model and local-file refusal controls. **State:** auxiliary PLAN_ONLY preparation; no native campaign, MC-F decision or programme-registry mutation.

**Source base:** main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. **Pinned accepted artifacts:** MC-004 `qualification-contract-v1.json` Git blob `22d5f976718edac9a8ccce3cb46f799b76e85ab4` and MC-046 `readiness.py` Git blob `e1b5f8d5c20e246632a39f8eb793948c20261051`. The MC-046 source itself imports/validates the first input.

## Objective and bounded falsifier

Preserve the MC-004 scale ladder **10, 100, 1,000, 10,000 genuine geometry-changing sections**, the equal-sized but separate **redundant-history controls**, all **26 mandatory machining operations** and three **sequential** (never parallel) repeat slots. The proposed candidate comparison labels are **Ubuntu 24.04** and **Windows Server 2022**, yielding **2 × 4 × 2 × 3 = 48** independent PLAN_ONLY slots.

These two runner/platform labels are **provisional matrix candidates**, not a new frozen MC-004 platform denominator or evidence that they suffice for MC-F. No native execution/paid campaign, platform adjudication or changed hardware contract is authorized. The matrix is an empty evidence interface: every attempt remains `NOT_EXECUTED`; artifact digests, observed time and RSS are `null`; all gates remain `false`.

Refuse omitted/duplicated/reordered cells, conflated control tracks, changed section/repeat counts, dropped platform candidates, fabricated success/receipts, altered pinned source plan, unknown fields and type substitutions. Use MC-046's accepted strict parser, 1 MiB file and structural bounds, JSON duplicate-key refusal and descriptor/path identity checks for actual on-disk input.

## Commands

```bash
python3 research/machining-completeness/tasks/MC-048/practical_cell_preflight.py --contract
python3 research/machining-completeness/tasks/MC-048/practical_cell_preflight.py --self-test
python3 research/machining-completeness/tasks/MC-048/practical_cell_preflight.py --emit-plan > mc048-plan.json
python3 research/machining-completeness/tasks/MC-048/practical_cell_preflight.py --check-plan mc048-plan.json
python3 tools/validate_machining_completeness.py
```

Dedicated hosted Windows/Linux jobs checkout **literal PR head** and print the exact SHA before applying all controls. Neither the local test suite nor static MC-1 verification is a native geometry test. Failed runs and review findings must be retained.

## Explicit dependencies and nonclaims

- **Read-only accepted inputs:** MC-004 source-bound research contract, MC-046 PLAN_ONLY preparation checker.
- **Unmet capability dependencies:** MC-041 genuine native composed engineering realization, MC-044/MC-E actual independent STEP engineering use, MC-047 native recovery qualification, and a reviewed MC-048/MC-F platform/scale denominator. MC-B/PB-007 remains unproved.
- **Not established:** native solid, geometry-changing evidence, STEP, measured performance, fault recovery, independent consumer results, MC-B/D/E/F/MC-1, manufacturing/production authorization. Correctly blocked or refused attempts remain unsolved, not pass.

## Follow-on

A later qualified native owner may independently freeze actual platform and hardware cells, establish source-authenticated attempt receipts, attach real error/fault/scale metrics and preserved negative evidence, verify accepted MC-D/MC-E prerequisites and submit a separate MC-F decision. This proposal must not be reinterpreted as that output. Review on an exact head; same-account COMMENTED is not independent human APPROVED. **Do not merge while #397's separate owner reserves main.**
