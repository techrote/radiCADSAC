# RCS-011 mill cutter-sweep research

This directory contains the disposable research harness for RCS-011. It compares a hierarchy of fixed-orientation milling strategies against common RCS-003 physical fixtures while retaining the RCS-005 STEP gate.

## Files

- `experiment-plan-v1.json` — strategy definitions, shared cases, recognition guard fixtures, budgets and smoke profile.
- `harness/mill_worker.cpp` — one-attempt OCCT 8.0.1 worker.
- `harness/run_mill_campaign.py` — process-isolated campaign orchestration, reference comparison, repeatability checks and evidence generation.
- `harness/CMakeLists.txt` — worker build against the exact RCS-006 OCCT installation.
- `measured-summary-v1.json` — added only after a successful hosted measured campaign and pinned to that evidence.

## Reproduce

Use the exact OCCT installation created by RCS-006:

```bash
export RCS006_OCCT_PREFIX="$PWD/.deps/rcs006/occt-8.0.1"
bash research/rcs-006/harness/bootstrap_occt.sh
bash research/rcs-006/harness/verify_occt_install.sh

cmake -S research/rcs-011/harness -B .build/rcs011 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$RCS006_OCCT_PREFIX"
cmake --build .build/rcs011 --parallel 2

export LD_LIBRARY_PATH="$RCS006_OCCT_PREFIX/lib:$RCS006_OCCT_PREFIX/lib64:${LD_LIBRARY_PATH:-}"
python3 research/rcs-011/harness/run_mill_campaign.py \
  --worker .build/rcs011/rcs011_mill_worker \
  --profile smoke \
  --repeats 2 \
  --out-dir .results/rcs011-smoke

python3 tools/validate_rcs011.py --results-dir .results/rcs011-smoke
```

The campaign writes `campaign.json`, `results.jsonl`, `measured-summary.json`, `summary.md`, and applicable STEP files. Worker processes are individually timeout-bounded by the orchestrator.

## Result interpretation

`success` means the attempt produced a valid B-rep satisfying the case body/material oracle and, where enabled, automated STEP write/read-back budgets. It does not mean the entire strategy is selected for production.

A `sampled_fallback` geometry-budget breach is preserved as expected negative evidence because that strategy explicitly approximates the swept envelope. Structural harness failures, nondeterminism in required exact strategies, invalid topology, wrong body count, or required STEP failures remain CI failures.

The `plunge-1um` case is deliberately diagnostic rather than an architecture pass gate because RCS-007 already established that tiny positive removals can fall below conventional kernel resolution. The event remains physical material intent even if the pinned OCCT baseline loses it.
