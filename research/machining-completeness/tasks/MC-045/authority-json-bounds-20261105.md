# MC-045 — bounded authority JSON ingress before campaign accounting

**Date:** 2026-11-05. **Scope:** `campaign_harness.py::load_json`, used for permit and plan file ingress by `validate`, `account`, and `audit-ledger`. **Evidence:** deterministic MODEL_ONLY / local-file contract, **not** native qualification. Based on live main `901bd0174d78598b789b7d23647e4fc2966edca1` and [MC-045 #107](https://github.com/techrote/radiCADSAC/issues/107).

## Reproducible defect and refusal contract

The previously accepted implementation called `path.read_text(encoding="utf-8")` with no byte limit, then recursively visited all dictionaries/lists in `canonical_bytes` without an input depth limit. A syntactically valid but deeply nested or oversized permit/plan could allocate unbounded authority-ingress memory or trigger an uncaught `RecursionError`. A JSON decoder integer-conversion `ValueError` could also bypass the agreed `ContractError` refusal class. No evidence suggested an actual malicious file had been used: this is a deterministic input-boundary correctness hardening.

The new reader caps each **raw on-disk file at 1,048,576 bytes** using an at-most-limit-plus-one byte read, before decoding or JSON parsing. After duplicate-key-safe parsing, it counts dictionary/list **containers**, including the root object, and refuses **depth greater than 32** before recursive canonical encoding. Existing duplicate key, nonfinite constant, binary float, invalid Unicode and nonobject refusals remain enforced. Parser-level `ValueError`, `UnicodeError`, `OverflowError` and `RecursionError` become conservative `ContractError`; intentional `ContractError` reason text is preserved.

## Regression controls

`python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test` exercises the **real load_json disk-file path**. The existing positive synthetic MODEL_ONLY permit and plan are retained. New tests also accept a JSON object at exactly 32 container levels and a literal string containing 42 `[` characters, so lexical punctuation is not falsely counted. New negatives refuse 33 container levels and a valid JSON permit/plan file exceeding the one-MiB byte limit, alongside all existing duplicate-key/nonfinite/surrogate/invalid-syntax checks. Existing campaign accounting and ledger-custody tests execute unchanged.

No paid/native run is required; run applicable hosted MC-045 workflows and full static MC-1 validation at the literal PR head and retain any failures. This branch is **draft, no same-session merge**.

## Limits and source custody

The bounded reader is not a streaming JSON parser and is not proof of atomic file snapshots: data beyond the sentinel is not consumed, and an external concurrent writer could still replace/alter a permit or plan before/while opening it. Separate descriptor-pinned authority readback/alias custody remains future work. JSON objects below the size/depth limit can still be large enough to cost nonzero CPU/memory; this is a defensible bounded refusal, not a security sandbox. Command authorization, tariff/resource accounting, native opt-in, retained captures, canonical journal, original sources/phase, material lineage/bodies, 26 operations and STEP obligations are unchanged.

**Gate:** PB-007-01/02/03/04 OPEN; MC-B, MC-F, MC-1 NOT_ESTABLISHED; production unauthorized.
