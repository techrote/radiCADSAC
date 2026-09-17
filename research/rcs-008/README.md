# RCS-008 provenance and semantic-identity research

Status: research package for RCS-008  
Baseline: OCCT 8.0.1 / `V8_0_1` / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

This package tests how manufacturing ancestry can remain meaningful when exact B-rep topology is regenerated, split, merged, replaced or unified. It deliberately separates **programme semantic lineage** from OCCT `TopoDS_Shape` identity.

## Contents

- `experiment-plan-v1.json` — hypotheses, relation vocabulary and deterministic cases.
- `harness/provenance_worker.cpp` — pinned-OCCT probe for Boolean/unification history and transient topology identity.
- `harness/run_provenance_campaign.py` — process-isolated campaign plus backend-independent semantic-lineage prototype.
- `../../tools/validate_rcs008.py` — static and runtime evidence validator.

The architectural research report is `docs/16-PROVENANCE-SEMANTIC-IDENTITY-RESEARCH.md`. The programme recommendation is recorded in `docs/decisions/DR-0011-semantic-lineage-not-topology-id.md`.

## Model under test

The prototype names durable manufacturing concepts—material body, setup/tool revision, canonical operation, tool envelope, boundary role and reconciliation event—and relates them with explicit lineage edges:

- `preserved`;
- `generated`;
- `split`;
- `merged`;
- `replaced`;
- `retired`;
- `ambiguous`.

Concrete OCCT faces/edges/solids are **attachments/evidence**, not the semantic node identity itself. A genuine topology split therefore creates new descendant realizations rather than pretending one old face ID survived twice. A merge has multiple parents. If manufacturing semantics cannot discriminate descendants, the relation stays `ambiguous`.

## Reproduction

With the exact RCS-006 OCCT installation available through `RCS006_OCCT_PREFIX`:

```bash
cmake -S research/rcs-008/harness -B .build/rcs008 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$RCS006_OCCT_PREFIX"
cmake --build .build/rcs008 --parallel 2
export LD_LIBRARY_PATH="$RCS006_OCCT_PREFIX/lib:$RCS006_OCCT_PREFIX/lib64:${LD_LIBRARY_PATH:-}"
python3 research/rcs-008/harness/run_provenance_campaign.py \
  --worker .build/rcs008/rcs008_provenance_worker \
  --profile smoke \
  --out-dir .results/rcs008-smoke
python3 tools/validate_rcs008.py --results-dir .results/rcs008-smoke
```

The worker checks the OCCT runtime version. The RCS-006 bootstrap separately pins and verifies the exact upstream commit/build profile.

## Cases

The smoke profile runs:

1. **Independent replay** — independently reconstruct the same Boolean result and compare engineering metrics with OCCT `IsSame` face identity.
2. **Material split** — through-cut one stock body into two solids and inspect one-to-many operation history.
3. **Overlapping mill cuts** — execute sequential overlapping removal envelopes and inspect modification/replacement evidence.
4. **Same-domain merge** — fuse adjacent solids, then explicitly unify same-domain faces and inspect history/fan-in.
5. **Lathe exact retrace** — apply the same OD finishing envelope twice and compare geometry plus second-operation history.
6. **Synthetic symmetric ambiguity** — demonstrate the programme rule that an underdetermined descendant must remain ambiguous rather than being named from backend order.

## CI interpretation

A zero relation count for a particular OCCT history class is a legitimate negative research result; it is not rewritten as success. CI fails when the worker cannot build/run, the protocol/evidence is incomplete, a required scenario disappears, or the programme model silently promotes backend topology identity to durable identity.

Measured findings are interpreted in the report only after the hosted smoke campaign has produced validated evidence.
