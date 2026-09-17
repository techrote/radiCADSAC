# RCS-017 — OCCT concurrency and global-state isolation probe

Status: measured campaign implemented; conclusions are scoped to OCCT 8.0.1 and the tested worker topology.  
Date: 2026-09-17

## Purpose

RCS-017 resolves the concurrency uncertainty carried from RCS-004/RCS-013. It measures the distinction between instance-local OCCT work and process-global configuration, and compares sequential, one-process threaded, and worker-process execution for the OpenSimachinist founding model.

The exact target is OCCT **8.0.1**, upstream commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`, using the accepted RCS-006 `release-shared-cxx17-worker-only-headless-v4` build profile.

## Source facts that define the probe

- `STEPControl_Writer::Transfer` in OCCT 8.0.1 has an overload accepting a `DESTEP_Parameters` value object. The probe uses distinct writers plus explicit per-call schema, unit, model type, tessellation, and precision policy.
- Legacy data-exchange configuration still exposes process-global `Interface_Static` named parameters. RCS-017 does not promote those paths into programme-facing APIs.
- `BOPAlgo_Options` exposes both process-global `SetParallelMode`/`GetParallelMode` and per-instance `SetRunParallel`/`RunParallel`.
- `TopoDS_Shape` copies share the underlying `TopoDS_TShape`; atomic handle lifetime management is not evidence that concurrent mutation is safe. The tested ownership pattern is deliberately read-only shared input plus non-destructive operations.

Primary upstream references are pinned to the same 8.0.1 commit used by the repository audit.

## Hypotheses and falsification

The machine-readable hypotheses are in `experiment-plan-v1.json`. In summary:

1. Explicit `DESTEP_Parameters` with independent sessions/writers should retain conflicting AP203/inch versus AP242/mm policies under concurrent jobs.
2. Explicit per-instance Boolean `SetRunParallel` should remain a job-local policy when the global mode is not mutated concurrently.
3. `BOPAlgo_Options::SetParallelMode` is intentionally process-global and therefore cannot express conflicting per-job policies in one process.
4. Read-only shared `TopoDS_TShape` ownership should remain stable for the immutable-input pattern; this does **not** assert concurrent mutation safety.
5. Process isolation should contain process-global configuration/failure state at tolerable orchestration cost.

## Reproducible experiment

Build the exact RCS-006 OCCT baseline, configure this harness against it, then run:

```bash
cmake -S research/rcs-017/harness -B .build/rcs017 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$RCS006_OCCT_PREFIX"
cmake --build .build/rcs017 --parallel 2
export LD_LIBRARY_PATH="$RCS006_OCCT_PREFIX/lib:$RCS006_OCCT_PREFIX/lib64:${LD_LIBRARY_PATH:-}"
python3 research/rcs-017/harness/run_concurrency_campaign.py \
  --worker .build/rcs017/rcs017_concurrency_probe \
  --profile smoke \
  --out-dir .results/rcs017-smoke
python3 tools/validate_rcs017.py --results-dir .results/rcs017-smoke
```

The campaign preserves stdout/stderr per execution topology and writes `summary.json`. Negative results are evidence: a thread crash, timeout, wrong STEP configuration, invalid readback, or global-state mismatch is recorded rather than hidden behind a success-only benchmark.

## STEP experiment

Every geometry job applies the same deterministic slot cut to immutable shared stock and then exports/read-backs that result. Even-numbered jobs request millimetres, AP242 and `1e-5` write precision. Odd-numbered jobs request inches, AP203 and `1e-3` write precision.

Conformance observations include serialized schema/unit markers, read-back B-rep validity and source-versus-readback volume. These are deliberately stronger than merely checking that a STEP file exists, while the complete programme export contract remains RCS-005.

## Boolean/global-parallel experiment

The ordinary sequential/threaded workload forces the process-global Boolean parallel mode false and alternates `SetRunParallel(true/false)` per operation. This tests per-instance execution without changing global state underneath running algorithms.

A separate stress probe deliberately races conflicting calls to `BOPAlgo_Options::SetParallelMode` and reads the process-global value back. It exists to measure observability of the global control, not to recommend that production code race it.

## Shared-handle ownership boundary

The one-process tests share a copied `TopoDS_Shape` stock object among jobs and use non-destructive Booleans. The campaign compares the shared stock volume before/after threaded use. A stable result supports only the intended immutable-input lifetime pattern. No conclusion is made about concurrent mutation, lazy caches in unmeasured classes, or arbitrary sharing of mutable OCCT objects.

## Process-isolated comparison

The campaign launches multiple independent worker processes concurrently, with each worker exercising both STEP configurations sequentially. It records process return codes, timeouts, geometry/STEP observations and aggregate wall time. This provides an operational comparison against the one-process threaded run while guaranteeing separation of process-global state by address space.

## Architecture recommendation

The RCS-013 architecture should retain **process-isolated OCCT geometry/STEP workers as the founding production default**. Explicit `DESTEP_Parameters`, per-instance Boolean controls and immutable ownership remain required inside each worker; they reduce avoidable global-state dependence but do not erase the existence of `Interface_Static`, `BOPAlgo_Options::SetParallelMode`, or other unmeasured static/global surfaces.

Threaded parallelism may be used *inside one isolated worker* only for APIs whose configuration and ownership have been qualified, and production jobs must not rely on conflicting process-global controls. Removing the process boundary later requires a broader stress/TSAN/platform campaign, not extrapolation from this narrow probe.

## Remaining unknowns

- Thread sanitiser evidence for OCCT itself is not supplied by this campaign.
- Windows/MSVC and macOS concurrency behaviour are not qualified by the Linux CI probe.
- Concurrent mutation of shared topology is explicitly outside scope.
- The campaign does not enumerate every `Interface_Static` consumer or every lazy process-global cache in OCCT.
- Long-duration soak, allocator pressure, cancellation, signal handling and malicious/corrupt STEP inputs remain unqualified.
- Production worker startup/pooling overhead will depend on the eventual service wrapper and workload mix.

## Evidence status

CI uploads the complete `.results/rcs017-smoke` directory for every run. `docs/21-OCCT-CONCURRENCY-ISOLATION.md` records the programme interpretation and DR-0016 records the conservative production boundary. Measured numeric results are taken from the CI artifact for the tested commit; conclusions must be revised if later evidence contradicts them.
