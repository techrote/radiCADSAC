# MC-043 — Strict JSON numeric and Unicode-scalar evidence ingress

**Date:** 5 November 2026 (UTC). **Status:** bounded, provisional **STRUCTURAL_PREFLIGHT_ONLY** implementation and tests; no MC-043, MC-E, MC-B or MC-1 acceptance.
**Parent:** [MC-043 #105](https://github.com/techrote/radiCADSAC/issues/105). **Coordination:** [issue #324](https://github.com/techrote/radiCADSAC/issues/324).
**Source baseline:** main `10dfeb8e1b1f00f8db34060fc9051302dab483a9` following MC-043 #410 integration.

## Authority and separation

DR-0026, `handoffs/current-authority.json`, `AGENTS.md`, MC-1 programme/execution protocol, accepted MC-054 `MC-ENG-OUTPUT/1.0`, and the existing `consumer_receipt_preflight.py` define this narrow boundary. This is neither a proof-closure worker nor a native geometry campaign. Separate MC-038/PB-007 draft branches, mathematical source/evidence owners, shared proof/programme registries, frozen v54/v2 corpus, issue #100 and the current-state document are excluded.

The preflight checks receipt structure and exact artifact byte bindings with deliberately **NON-STEP** synthetic input. Success is `STRUCTURAL_PREFLIGHT_ONLY`, never independent STEP import, native machining geometry or manufacturing qualification.

## Defect and counterexamples

Python's default `json.loads` converts the syntactically valid JSON exponent token `1e999` into a nonfinite IEEE-754 float. JSON nonfinite lexemes `NaN` and `Infinity` are already rejected by this preflight's `parse_constant`, but that handler does not intercept exponent overflow. An ignored nested auxiliary field can therefore introduce an infinite Python value while a completely consistent synthetic manifest/receipt package passes structural checks.

Python also accepts unpaired escaped UTF-16 surrogate halves (for example, the JSON escape `\ud800`) as string values even though they are not Unicode scalar values. Such data could be propagated as malformed identity or receipt metadata across future consumers despite exact raw-byte hashes.

**Hypothesis/falsifier:** the actual raw-byte reader must refuse both classes in any nested key/value *before* `check()` receives them, while retaining finite JSON numeric fields and valid paired surrogate escapes. The correction fails if any malformed wire token is admitted or a legitimate one-body, grouped multi-body or empty synthetic control breaks.

## Bounded correction

- `consumer_receipt_preflight.py`: `finite_json_float()` rejects exponent-overflow nonfinite floats; `reject_unpaired_surrogates()` iteratively traverses parsed JSON keys and values and refuses lone surrogate code points. Existing duplicate-key/nonfinite-constant refusal is preserved.
- `verify.py`: seven new adversarial raw-byte controls exercising the actual `read_json_bytes()` → `check()` path: positive/negative overflowing exponents, high/low surrogate values/keys (including nested objects), and explicit NaN/Infinity regressions. A valid finite numerical metadata field and paired surrogate escape are accepted through a full structural check, alongside existing geometry-state positive envelopes.
- This RAG note is the third task-scoped file. No workflow, authority, output schema or mathematical source edit is required.

**Limitations:** finite floats remain Python binary floats; this does not provide exact decimal arithmetic, canonical JSON signing, producer authenticity or atomic hostile-filesystem custody. Unknown auxiliary fields are still permitted. There is no STEP parse, imported geometry or independently measured engineering operation.

## Reproduction and qualification

From repository root:

```sh
python3 research/machining-completeness/tasks/MC-043/verify.py --contract --self-test
python3 tools/validate_machining_completeness.py
```

Qualify the **literal final PR SHA** using `mc1-mc043-step-descriptor-custody.yml` on Ubuntu 24.04 and Windows Server 2022, plus `mc1-mc043-receipt-preflight.yml` and the static programme checks. Preserve any failed run IDs and job logs. An independent session must review the source before conditional expected-head integration and merged-main qualification.

## Nonclaims and prerequisites

PB-007-01/02/03/04 remain **OPEN**; MC-B, MC-E, MC-F and MC-1 remain **NOT_ESTABLISHED**. All 26 machining operations and durable-body/journal/topology requirements remain in scope. Full MC-043 requires source-authenticated MC-040/042 native STEP and an actual independent MC-017 consumer and meaningful downstream engineering operation. No paid campaign, production repository or manufacturing use is authorized.
