# MC-046 — Bounded PLAN_ONLY proposal ingress

Status: **draft engineering qualification candidate**, 5 November 2026. Source base: `main=7715cc245b4843aa469d1c9a7f5bd53b9fc59623` after independently integrated MC-045 #416. Parent issue: [MC-046 #108](https://github.com/techrote/radiCADSAC/issues/108). Coordination claim: [#324 comment 6668380747](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6668380747), with task-scoped workflow-label amendment [6668391922](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6668391922).

## Purpose and concrete defect

`readiness.py --check-plan PATH` previously consumed `Path.read_bytes()` without an input-size bound, then parsed and iteratively traversed arbitrarily nested JSON. An external proposal path could consume uncontrolled memory and excessive validation work before the fail-closed `PLAN_ONLY` plan comparison. These hazards are separate from, and do not weaken, the accepted MC-004 source-blob pin or the four mandatory T2 tiers.

Hypothesis: bounding proposal input to **1,048,576 bytes** and **32 object/list containing levels**, with a `MAX+1` file read and structural refusal before acceptance, preserves canonical valid plans and rejects oversized/deep plans. This is **resource hygiene**, not proof of hostile-filesystem atomicity or native geometry.

## Independent write scope

- `research/machining-completeness/tasks/MC-046/readiness.py`: explicit raw byte/depth limit, finite bounded read of the local proposal, refusal of nonregular paths, source-matched positives and executable negative tests.
- `.github/workflows/mc1-mc046-t2-readiness.yml`: replace stale count-specific label for the existing adversarial test step; retain same Ubuntu/Windows matrix, SHA checkout, commands and authority checks.
- This task-specific RAG note.

No changes to MC-004, MC-041, proof source, issue #100, authority, frozen audit, shared programme records or production code.

## Falsification and expected controls

Run:
```sh
python3 research/machining-completeness/tasks/MC-046/readiness.py --contract
python3 research/machining-completeness/tasks/MC-046/readiness.py --self-test
python3 research/machining-completeness/tasks/MC-046/readiness.py --emit-plan > proposal.json
python3 research/machining-completeness/tasks/MC-046/readiness.py --check-plan proposal.json
python3 tools/validate_machining_completeness.py
```

Existing 26 plan mutations and six malformed JSON cases remain. New negative controls must refuse a >1 MiB raw JSON buffer, 33-level array and object nesting, an oversized on-disk proposal, an actual post-lstat file-growth injection, and a directory as a proposal file. New positive controls admit 32-level array JSON and a canonical emitted plan read from a real file. Expected total: **38 negative/refusal controls**, plus the original two canonical structural positive controls and the two new direct boundary/roundtrip positives. A passing syntax-only or mocked check must never be described as native T2 qualification.

Exact-head Actions: `mc1-mc046-t2-readiness.yml` on Ubuntu 24.04 / Windows Server 2022, plus the repository's MC-1 static validator. Record workflow run IDs and any failures on the PR before claiming qualification. Do not merge in this authoring session; require separate review and guarded integration.

## Risk and limitations

- This bounded preflight is for *cooperative local* proposal files. A pathname may be replaced after the stat check; this does **not** establish atomic or cryptographically authenticated file custody, security against hostile concurrent writers, or a stable snapshot.
- `MC004_BLOB=22d5f976718edac9a8ccce3cb46f799b76e85ab4` remains the exact accepted contract. No change to the 10/100/1,000/10,000 genuinely geometry-changing section targets, separate redundant-history controls, all 26 operations, seed, MC-RH-Q1 or sequential repeats.
- `PLAN_ONLY`, `NOT_MATERIALIZED` and false execution/qualification flags remain mandatory. No native/paid campaign, actual STEP execution, accepted MC-D/MC-F/MC-B, MC-1 or production authorization is implied.

## Next prerequisites

1. Literal-head Windows/Linux and MC-1 static CI; source-critical review and preserved failures.
2. Distinct-session independent admission of the exact reviewed branch; protected merge and merged-main CI if accepted.
3. For genuine T2 measurements, separately accepted MC-041 native capability, formally accepted mathematical obligations, source-frozen fixtures and explicit bounded permits remain prerequisites. Retain every required domain/operation and negative result.
