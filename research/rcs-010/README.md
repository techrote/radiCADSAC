# RCS-010 lathe-specialized material-domain research

Status: RCS-010 research candidate pending measured CI evidence  
Date: 2026-09-17  
Pinned backend: OCCT 8.0.1 / `V8_0_1` / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

## Purpose

RCS-010 tests whether common fixed-axis turning should be solved primarily in an axisymmetric **axial/radial material domain** rather than by replaying every canonical journal event as an independent 3D B-rep Boolean.

This is research infrastructure. It does not define the production OpenSimachinist API, persistence encoding, tool library, scheduler, or general machining kernel.

## Compared strategies

Every concrete case is reduced to the same physical target material profile, then measured through three materially different strategies:

1. **Repeated 3D subtraction** — construct the completed removal envelope and apply it once for every canonical geometry event. This deliberately represents the operation-count/topology work imposed by an immediate 3D replay architecture.
2. **Batched 3D removal** — construct the same completed removal envelope, then subtract it from stock once. This measures how much benefit comes merely from batching before attributing benefit to a new representation.
3. **Axisymmetric 2D material domain** — apply OD, facing, taper and ID operations directly to a piecewise-linear `(z, radius)` material section, then revolve the final section into a conventional exact OCCT B-rep for validation and STEP.

The 2D solver uses decimal arithmetic for its material profile and analytic volume oracle. The OCCT worker independently reconstructs the profile and measures the resulting 3D B-rep.

## Semantic boundaries

- The canonical journal remains authoritative and immutable.
- Exact retraces remain journal events. `provenance_noop_events` reports geometry recomputations that the material-domain state proves unnecessary; it does not delete history.
- No global fuzzy tolerance is used to decide material removal.
- Positive material changes remain changes even when small.
- The axisymmetric solver is valid only while stock, tool-removal semantics and resulting material are rotationally symmetric about the declared spindle axis.
- Live tooling, eccentric stock, interrupted/non-axisymmetric features, arbitrary 5-axis motion and chuck/fixture collision semantics are explicit exclusions and require another provider.
- Tool nose radius and orientation are represented here only through the **completed canonical removal envelope**. Production envelope generation from insert geometry remains a separate implementation task.

## Coverage

The founding plan covers:

- OD turning;
- facing;
- a stepped shoulder;
- a simple linear taper/chamfer-class boundary;
- through boring;
- blind boring to an internal shoulder;
- repeated finishing;
- exact retracing;
- bounded noisy analogue input canonicalized into one geometry envelope.

The broader profile adds the blind-bore and analogue cases to the hosted smoke subset.

## Files

- `experiment-plan-v1.json` — versioned shared cases and acceptance oracles.
- `harness/profile_solver.py` — deterministic 2D axial/radial material solver and analytic volume oracle.
- `harness/lathe_worker.cpp` — pinned-OCCT reconstruction, repeated/batched 3D comparisons, B-rep metrics and STEP round-trip probes.
- `harness/run_lathe_campaign.py` — campaign orchestration and cross-strategy acceptance checks.
- `harness/CMakeLists.txt` — worker build against the accepted minimal OCCT install.
- `measured-summary-v1.json` — added only after a successful measured campaign is pinned and reviewed.

## Reproduce

```bash
export RCS006_OCCT_PREFIX="$PWD/.deps/rcs006/occt-8.0.1"
bash research/rcs-006/harness/bootstrap_occt.sh
bash research/rcs-006/harness/verify_occt_install.sh

cmake -S research/rcs-010/harness -B .build/rcs010 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$RCS006_OCCT_PREFIX"
cmake --build .build/rcs010 --parallel 2

export LD_LIBRARY_PATH="$RCS006_OCCT_PREFIX/lib:$RCS006_OCCT_PREFIX/lib64:${LD_LIBRARY_PATH:-}"
python3 research/rcs-010/harness/run_lathe_campaign.py \
  --worker .build/rcs010/rcs010_lathe_worker \
  --profile smoke \
  --out-dir .results/rcs010-smoke
python3 tools/validate_rcs010.py --results-dir .results/rcs010-smoke
```

Use `--profile baseline` for the larger research set.

## Interpretation rule

A strategy is not accepted because it merely returns a shape. Required cases must produce valid conventional B-reps, preserve the physical material/body oracle, agree with the analytic material-domain volume, preserve expected analytic surface classes, and pass the automated portion of the RCS-005 STEP contract where export is enabled.

Runtime and topology counts are comparative evidence, not correctness oracles. A faster wrong result fails.
