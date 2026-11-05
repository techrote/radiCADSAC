# MC-043 — Typed importer process-exit receipt refusal (2026-11-05)

## Status and authority

**Status:** BOUNDED PROVISIONAL STRUCTURAL PREFLIGHT, draft integration. **Evidence class:** `DETERMINISTIC_MODEL` (synthetic non-STEP artifacts and receipts). **Owning task:** MC-043 / [issue #105](https://github.com/techrote/radiCADSAC/issues/105). **Source base:** `fca8d0c36a91b2cece1b44c99e87aaa99df24dad` on 2026-11-05. **Branch:** `fix/mc043-import-exit-code-type-20261105`.

This work neither invokes an independent STEP consumer nor implements a machining operation. It does not satisfy MC-E, MC-B or MC-1 and cannot be used as a native result. PB-007/MC-038 mathematics, all 26 required operations, STEP output requirements and current authority remain unchanged. Dependencies MC-017, MC-040 and MC-042 remain subject to their actual source/proof/native acceptance.

## Observed defect and falsifiable contract

The accepted `consumer_receipt_preflight.check()` originally admitted the independent-import process exit with `imported.get("exit_code") == 0`. In Python, `False == 0` and `0.0 == 0` both evaluate true. JSON inputs `"exit_code":false` and `"exit_code":0.0` therefore satisfied the clean-process-exit comparison when all other receipt fields and synthetic STEP artifact digests were preserved. Such source documents cannot establish that an integer process exit code was actually recorded, even for a provisional structural receipt. This is an input-type confusion; it is **not** evidence of a real importer or an exploit against a native consumer.

**Contract:** nonempty imported consumer receipts must record `exit_code` with exact Python type `int` and value `0`. An absent value, JSON boolean, JSON non-integer, or nonzero integer must fail closed. Do not change the empty-material path: there is no importer process invocation to record, and an empty transition is not a fabricated STEP success.

## Scoped change

1. Change only the typed exit-code predicate in `research/machining-completeness/tasks/MC-043/consumer_receipt_preflight.py` using `type(...) is int and ... == 0`; all other import, STEP byte-custody, body, contact, seam and follow-on bindings remain unchanged.
2. Extend the actual `check()`-driven mutation suite in `MC-043/verify.py` with two source-matched adversarial receipts: `exit_code=False` and `exit_code=0.0`. Each must raise `Rejected`, not merely compare a fixture against expected data. Existing positive fixtures explicitly retain integer `0` for the nonempty grouped path and no invocation for the empty path.
3. Keep existing refusal cases intact, increasing negative controls from 37 to 39. The two existing positive controls remain unchanged. No workflow, production, mathematics, registry, gate authority, corpus or issue #100 mutation is authorized.

## Reproduction and exact-source qualification

From repository root, run:

```bash
python3 -m py_compile research/machining-completeness/tasks/MC-043/consumer_receipt_preflight.py research/machining-completeness/tasks/MC-043/verify.py
python3 research/machining-completeness/tasks/MC-043/verify.py --contract --self-test
python3 tools/validate_machining_completeness.py
```

The existing `mc1-mc043-step-descriptor-custody` workflow checks out the literal PR head on Ubuntu 24.04 and Windows Server 2022 and includes these tests plus static validation. The existing `mc1-mc043-receipt-preflight` workflow is a supplementary CI check. The test uses `SYNTHETIC_NON_STEP_A/B` byte fixtures; neither receipt nor underlying files are conventional engineering STEP.

## Residual risks and acceptance boundary

This guards only one structural receipt field. The receipt remains self-asserted; imported geometry, independent tool identity, fresh actual STEP parsing, error budgets, downstream engineering use, hostile-filesystem atomicity, and production authorization are **NOT ESTABLISHED**. Existing descriptor/alias checks retain documented cooperative filesystem race limitations. A final MC-043 admission requires source-authenticated native MC-040/042 artifacts and independently measured downstream engineering operations under the separately accepted gates.

## Handover

A later independent reviewer must inspect the final diff and literal-head CI logs, confirm both malicious receipts are actually submitted to `check()`, preserve historical CI failures, and consider a guarded merge only after applicable exact-head checks pass. No AI-authored COMMENT review should be represented as human APPROVED. After integration, independently verify main-push workflow execution before any accepted-main claims.
