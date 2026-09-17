# RCS-009 regularized material / deferred-topology research

Status: accepted RCS-009 research artifact  
Date: 2026-09-17  
Pinned backend: OCCT 8.0.1 / `V8_0_1` / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

## Purpose

This directory measures a narrow candidate for manufacturing material semantics against the accepted RCS-006 immediate-B-rep baseline. It does **not** introduce a production kernel or claim that deferred topology solves arbitrary CAD geometry.

The candidate keeps the canonical operation journal and semantic lineage intact while allowing private backend state to delay selected topology construction until a reconciliation boundary.

## Competing strategies

The baseline is the RCS-006 worker: each removal event is applied immediately as a non-destructive `BRepAlgoAPI_Cut`.

The accepted RCS-009 candidate is **regularized volumetric material with a bounded deferred removal ledger**:

- a proven point/edge/face-only contact records the semantic contact but does not create a new material B-rep;
- positive-volume removal remains material-changing even when very small;
- provenance-equivalent exact retraces may share one removal-envelope computation while every journal event remains recorded;
- pending unique removal envelopes are reconciled in one multi-tool cut at a checkpoint for the tested fixture class;
- a potential body-connectivity change is a hard checkpoint;
- STEP export always consumes the reconciled, validated B-rep rather than the pending ledger.

`BOPAlgo_CellsBuilder` is also probed on overlapping-removal and cut-through cases. It is treated as a possible reconciliation/cell-selection mechanism, not as the programme's durable material representation.

## Files

- `experiment-plan-v1.json` — deterministic cases linked to RCS-006 fixture IDs and RCS-003 families.
- `harness/deferred_worker.cpp` — candidate reconciliation worker plus CellsBuilder and STEP probes.
- `harness/run_deferred_campaign.py` — process-isolated baseline/candidate comparison and oracle checks.
- `harness/CMakeLists.txt` — worker build against the exact cached RCS-006 OCCT installation.
- `measured-summary-v1.json` — pinned CI run 48 evidence, including workflow/job/artifact provenance, aggregate results and representative measurements.

## Accepted measured result

CI run `35212264059` / job `105172585743` measured eight smoke cases with zero candidate failures. All eight candidate results satisfied the physical/body oracle and matched the immediate baseline final volume and bounds within the campaign tolerance. Immediate materialization used 227 Boolean operations across the set versus 6 for the bounded candidate; two exact zero-volume contacts were deferred and 218 provenance-equivalent repeated-event geometry recomputations were elided. Both CellsBuilder probes reproduced the candidate result, and the two-body cut-through case passed the automated STEP write/read-back boundary.

These numbers establish useful semantics and demonstrate that avoiding known no-op/retrace recomputation can be valuable. They are not a general performance guarantee; the measured one-off `0.0001 mm` skim was slower under the candidate than immediate baseline.

## Reproduce

Use the exact OCCT bootstrap already owned by RCS-006:

```bash
export RCS006_OCCT_PREFIX="$PWD/.deps/rcs006/occt-8.0.1"
bash research/rcs-006/harness/bootstrap_occt.sh
bash research/rcs-006/harness/verify_occt_install.sh

cmake -S research/rcs-006/harness -B .build/rcs006 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$RCS006_OCCT_PREFIX"
cmake --build .build/rcs006 --parallel 2

cmake -S research/rcs-009/harness -B .build/rcs009 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$RCS006_OCCT_PREFIX"
cmake --build .build/rcs009 --parallel 2

export LD_LIBRARY_PATH="$RCS006_OCCT_PREFIX/lib:$RCS006_OCCT_PREFIX/lib64:${LD_LIBRARY_PATH:-}"
python3 research/rcs-009/harness/run_deferred_campaign.py \
  --baseline-worker .build/rcs006/rcs006_occt_worker \
  --candidate-worker .build/rcs009/rcs009_deferred_worker \
  --profile smoke \
  --out-dir .results/rcs009-smoke
python3 tools/validate_rcs009.py --results-dir .results/rcs009-smoke
```

Use `--profile baseline` for the broader case set.

## Interpretation boundary

A baseline failure is research evidence, not a reason to alter the physical oracle. A CellsBuilder failure/warning is likewise preserved as negative evidence. The RCS-009 campaign itself fails when the candidate cannot execute, violates the explicit material/body oracle, fails required structural semantics, or cannot reconcile the required export case through the automated RCS-005 STEP round-trip gates.

The operation journal remains the durable authority for manufacturing intent. A pending removal ledger is discardable backend state and can always be rebuilt from journal/provenance data.
