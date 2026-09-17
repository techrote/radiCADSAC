# RCS-006 baseline benchmark harness

Status: research harness for RCS-006  
Baseline: OCCT 8.0.1 / `V8_0_1` / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

This directory contains the disposable, reproducible benchmark substrate used by RCS-006 and later comparative research. It is not production OpenSimachinist code.

## Contents

- `benchmark-plan-v1.json` — pinned representative campaign derived from RCS-003 and RCS-005.
- `result.schema.json` — stable attempt-result schema for later RCS-007–RCS-012 comparisons.
- `harness/bootstrap_occt.sh` — obtains and builds the exact OCCT baseline.
- `harness/CMakeLists.txt` and `harness/occt_worker.cpp` — isolated OCCT measurement worker.
- `harness/run_campaign.py` — process-isolated campaign runner, timeout controller, oracle evaluator, repeatability checker and report generator.

## Reproduce on Linux

From repository root:

```text
bash research/rcs-006/harness/bootstrap_occt.sh
cmake -S research/rcs-006/harness -B .build/rcs006 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$PWD/.deps/rcs006/occt-8.0.1"
cmake --build .build/rcs006 --parallel 2
LD_LIBRARY_PATH="$PWD/.deps/rcs006/occt-8.0.1/lib:${LD_LIBRARY_PATH:-}" \
  python3 research/rcs-006/harness/run_campaign.py \
  --worker .build/rcs006/rcs006_occt_worker \
  --profile baseline \
  --out-dir .results/rcs006-baseline
```

For the hosted-CI subset use `--profile smoke`. Results are written as `results.jsonl`, `campaign.json`, `summary.md`, and STEP files for applicable cases.

`bootstrap_occt.sh` verifies the exact source commit before building and records the source pin in the install prefix. The C++ worker also refuses to run against an OCCT runtime version other than 8.0.1.

## Isolation and failure containment

Every concrete fixture attempt runs in a fresh worker process. The Python campaign runner applies a per-attempt timeout and records exit code, stderr and wall time. A kernel crash or hang therefore terminates one attempt rather than the campaign process. Later backends should preserve this worker boundary even if their implementation language differs.

Backend failures are **measurements**, not harness failures. The campaign classifies them using `docs/06-RESEARCH-METHOD.md` and still emits results. CI should fail only when the harness cannot build/run/emit valid records, not merely because the pinned baseline exposes a reproducible geometry defect.

## Recorded measurements

The OCCT worker reports:

- B-rep validity;
- vertex/edge/face/shell/solid counts;
- volume and surface area;
- bounding box;
- smallest face area and edge length;
- analytic surface and curve classes;
- Boolean operation count;
- geometry and total runtime;
- process peak RSS where the host exposes it;
- STEP transfer/write/read status;
- fresh-session read-back validity/body count/geometry metrics;
- STEP round-trip bounding-box and volume deviation;
- serialized schema excerpt and unit markers;
- deterministic file digest for diagnostics.

The runner adds source-fixture identity, RCS-005 fixture identity, host/tool metadata, physical-oracle classification and repeatability signatures.

## Parameter sweeps

`benchmark-plan-v1.json` stores concrete members of parameter families. Add new members by retaining the same `source_family_id` and changing only declared parameters. The runner validates that every referenced RCS-003 family and RCS-005 STEP fixture exists before launching work.

The founding baseline includes coincidence/coplanarity, tangency/lower-dimensional contact, thin removal, repeated/retraced cuts, a 200-operation stress member, lathe OD removal, lathe parting, mill cut-through and STEP round-trip in millimetres/inches.

## STEP scope

RCS-006 automates the open portions of the RCS-005 contract: pre/post geometry metrics, AP242DIS baseline writing, unit markers, fresh OCCT read-back, body count, validity, analytic-class retention and geometric budgets. It does **not** claim that OCCT self-readback constitutes independent interoperability qualification. STEPcode and downstream CAD/CAM qualification remain separate RCS-005 profile evidence.

## Portability rule

Later research may replace the worker while keeping the campaign/result envelope. Backend-specific diagnostic payloads belong inside the `worker` object. Programme comparisons should rely on the stable top-level fixture identity, classification, timing, host, backend and normalized geometry/STEP metrics rather than private OCCT object identity.
