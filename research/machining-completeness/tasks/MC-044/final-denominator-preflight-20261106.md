# MC-044 — Source-pinned final-output denominator PLAN_ONLY preflight

**Status:** 6 November 2026. Engineering preparation only. Issue [#106](https://github.com/techrote/radiCADSAC/issues/106), isolated from the MC-038/PB-007 mathematical owner, main integration owner and production.

## Falsifiable acceptance gap and scope

MC-044 eventually decides MC-E from **actual native** STEP Layers A–D and a **genuinely independent** consumer, on the mandatory final fixture set. There was no executable admission guard ensuring that a future qualification preparation packet retains the *complete* accepted fixture and operation denominator, all output classes and independent negative controls. A proposal that drops F16, one machining operation or the malformed/materially-wrong STEP controls must refuse *before* anyone promotes it to a campaign.

This increment supplies `qualification_readiness.py`, a deterministic `PLAN_ONLY` generator and exact-equality checker. It is not a STEP reader, a fixture generator, a native test runner, an independent measurement system or a gate verifier. It deliberately contains **no success receipt parser**.

## Accepted source identity

The code checks **tracked Git objects at HEAD**, not checkout-translated bytes, and rejects tracked worktree changes:

| Source | Repository file | Git blob |
|---|---|---|
| MC-004 operation/accuracy contract | `MC-004/qualification-contract-v1.json` | `22d5f976718edac9a8ccce3cb46f799b76e85ab4` |
| Mandatory constructed fixture registry | `fixture-families-v1.json` | `d38b1bff84166b1d0fe2c91b94006ccfdce0f287` |
| MC-054 engineering-output profile | `MC-054/engineering-output-profile-v1.json` | `6d9d5924a39e5369a1999c48a9c508dc05fd818e` |
| MC-017 source-only independent-consumer route | `MC-017/consumer-probe-v1.json` | `5b8a878cd451165b0814ad16ce6d7f7f59d5e5b6` |

Paths above are relative to `research/machining-completeness/tasks/` except `fixture-families-v1.json`, which is under `research/machining-completeness/`. Full repository paths are defined in the checker. The original accepted 26 operations are copied, not replaced by a convenient subset. All F01–F16 are `BUILT` as *fixtures/oracle controls*, not native geometry results. Required output classes EO-054-01..06 retain the explicit `EMPTY_MATERIAL` branch, with no fake STEP artifact. Layers A–D apply to *nonempty* future output; actual applicability needs certified nominal material state.

MC-017 supplies only a candidate BRL-CAD/STEPcode/OpenNURBS import path, with strict/no-repair, volume grid refinement and required positive and negative controls. It has **never executed the required source-bound MC-1 consumer campaign**. The generated packet preserves that boundary rather than asserting independent validation.

## Contract and execution

Run:

```sh
python3 research/machining-completeness/tasks/MC-044/qualification_readiness.py --self-test
python3 research/machining-completeness/tasks/MC-044/qualification_readiness.py --emit-plan > /tmp/mc044-plan.json
python3 research/machining-completeness/tasks/MC-044/qualification_readiness.py --check-plan /tmp/mc044-plan.json
python3 tools/validate_machining_completeness.py --self-test
```

The checker refuses any change in pinned source identity, fixture IDs/owners/mandatory state, 26-operation inventory, six output classes, required A–D layer labels for future nonempty cases, empty-state branch, the MC-017 independent-consumer controls or any attempt to assign simulated native results, output-gate acceptance, production authorization or step-file success. It bounds plan input to 256 KiB and rejects duplicate JSON keys/nonfinite constants. The complete in-memory plan is emitted as sorted JSON and re-imported through a real temporary file.

Negative controls cover missing and duplicate fixtures/operations, mutated fixture identifiers, false Layer-D/consumer success, dropping empty handling, losing negative controls, changing source hashes and premature authorization. This is an *exact structural and source-pin refusal contract*, not an atomic filesystem security protocol.

## Independent and blocked dependencies

**Available now:** MC-004 reviewed operation/workload artifact, F01–F16 constructed witnesses, MC-054 output-profile decision, MC-017 source-level consumer investigation. These admit only planning and synthetic negative verification. They are not themselves real A–D STEP evidence.

**Still blocked:** MC-038/PB-007 mathematical completeness, MC-041 native MC-D capability, MC-042 source-authenticated real STEP export/readback, MC-043 genuine independent imported-solid use, and final MC-044 MC-E decision. The open RB-016-01..05 and XB-017-01 consumers remain explicit. MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`, with all 26 machining operations mandatory. No native/paid campaign, production repository or manufacturing authorization.

## Handoff and invalidation

The output is a **preparation proposal**. Later native owners must introduce separately reviewed measurement/evidence schemas, exact file hashes, nominal certificates, error bounds, required fixture/negative-control evidence and explicit permits. Do not convert this `PLAN_ONLY` packet into evidence by changing status strings. Any accepted source-profile or fixture-domain revision requires a new reviewed source-pinned preparation version and rerun. This change is limited to MC-044-local code/docs plus one dedicated test workflow, with no proof, shared gate, registry or authority writes.