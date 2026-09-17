# RCS-007 virtual tolerance research

Status: measured RCS-007 experiment package  
Baseline: OCCT 8.0.1 / `V8_0_1` / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`  
Build profile: `release-shared-cxx17-worker-only-headless-v4`

This directory compares conventional operation-wide fuzzy tolerance with manufacturing-aware local classification and semantic replay rules. It is research infrastructure, not production OpenSimachinist code.

## Files

- `experiment-plan-v1.json` — candidate models, separated tolerance-policy channels and deterministic sweep profiles.
- `harness/run_tolerance_campaign.py` — orchestrates RCS-006 worker sweeps, policy comparisons, perturbation probes, repeated-pass tests and accumulation chains.
- `harness/reconcile_results.py` — converts raw model predictions into the accepted evidence semantics: uncertain contact is explicitly deferred rather than scored as a no-op, and accumulation chains are checked against analytic geometry rather than topology alone.
- `harness/repeated_finish_worker.cpp` — small OCCT worker for repeated OD finishing and ordered tolerance-accumulation chains.
- `harness/CMakeLists.txt` — builds the RCS-007 worker against the same pinned worker-only headless OCCT install as RCS-006.
- `measured-summary-v1.json` — durable compact summary/provenance of the accepted hosted smoke evidence.

The main interpretation is in `docs/15-VIRTUAL-TOLERANCE-RESEARCH.md`; the architecture decision is `docs/decisions/DR-0010-separate-tolerance-channels-and-local-uncertainty.md`.

## Reproduce the hosted experiment

Bootstrap the exact baseline as documented by RCS-006:

```bash
export RCS006_OCCT_PREFIX="$PWD/.deps/rcs006/occt-8.0.1"
bash research/rcs-006/harness/bootstrap_occt.sh
```

Build both workers:

```bash
cmake -S research/rcs-006/harness -B .build/rcs006 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$RCS006_OCCT_PREFIX"
cmake --build .build/rcs006 --parallel 2

cmake -S research/rcs-007/harness -B .build/rcs007 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$RCS006_OCCT_PREFIX"
cmake --build .build/rcs007 --parallel 2
```

Run and validate the smoke profile:

```bash
export LD_LIBRARY_PATH="$RCS006_OCCT_PREFIX/lib:$RCS006_OCCT_PREFIX/lib64:${LD_LIBRARY_PATH:-}"
python3 research/rcs-007/harness/run_tolerance_campaign.py \
  --worker .build/rcs006/rcs006_occt_worker \
  --finish-worker .build/rcs007/rcs007_finish_worker \
  --profile smoke \
  --out-dir .results/rcs007-smoke
python3 research/rcs-007/harness/reconcile_results.py \
  --results-dir .results/rcs007-smoke
python3 tools/validate_rcs007.py --results-dir .results/rcs007-smoke
```

Use `--profile baseline` for the broader sweep; the interpretation pass and validator are unchanged.

## Evidence discipline

Backend failures, oracle mismatches, quantization regressions, perturbation sensitivity and order dependence are research results. The campaign does not fail merely because a candidate model performs badly; CI fails when the experiment cannot build/run or its evidence contract is incomplete.

An uncertain local-contact classification is neither success nor a no-op. It is preserved as a deferred result so later reconciliation work can decide it without rewriting the original signed manufacturing intent.

Generated `.results/` data is CI/runtime evidence. The full hosted artifact is not committed, but `measured-summary-v1.json` preserves its run/artifact digest and architecture-relevant measurements.
