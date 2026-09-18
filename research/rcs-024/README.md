# RCS-024 — current OCCT differential, concurrency minimization and BRepGraph/history probe

Status: **measured, decision frozen, and guarded by exact-pin CI**.

## Purpose

RCS-024 re-tests the exact OCCT 8.0.1 founding control against a distinct, exact current-upstream snapshot without converting the programme into a rolling-upgrade exercise. The durable manufacturing journal, body transitions, tolerance/error budgets, STEP obligations and programme provenance remain authoritative above OCCT.

## Pins and why the current candidate is not called stable

- Founding control: OCCT **8.0.1**, tag `V8_0_1`, commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`.
- Current differential candidate: OCCT **8.1.0.dev1**, exact upstream commit `3d097a0328e71b826377d4814ab05ec3c3d23871`.
- At execution on 2026-09-18, upstream `V8_0_1` was still the latest stable release. Issue #43 permits an exact current-upstream commit for questions not represented by the stable release. The candidate is a development snapshot, not a production recommendation.

Primary upstream sources used for source audit include the two exact commits and the STEP writer/actor plus BRepGraph ItemUID, history and VersionStamp implementation surfaces.

## Hypotheses and falsification

The pre-registered hypotheses are in `experiment-plan-v1.json`. The tests are intentionally capable of falsifying a preferred architecture: STEP writer isolation is judged from serialized uncertainty rather than object ownership assumptions; Boolean validity is insufficient if the material oracle disagrees; and BRepGraph usefulness does not imply that its identifiers become durable programme identity.

## STEP cross-talk minimization

`harness/diff_worker.cpp --probe step` reduces the RCS-017 stress case to four writes of the same simple solid. Two fresh writers establish sequential controls. The cross-talk case creates two distinct writers, sets conflicting tolerances (`0.00001 mm` and `0.001 mm`) before either transfer, then transfers the first writer after the second has been configured. Each output is parsed for `UNCERTAINTY_MEASURE_WITH_UNIT` and independently read back as a B-rep.

Both exact pins reproduce the same defect: the first writer's sequential `0.00001 mm` control serializes `0.001 mm` in the cross-talk case.

## Concurrency ownership probe

`--probe parallel` separates job-local `BRepAlgoAPI_Cut::SetRunParallel(true)` from process-global `BOPAlgo_Options` state. Both pins keep the process-global flag false after the per-instance setter, but a deterministic two-thread hand-off shows one thread observing the other's process-global setting. Process isolation therefore remains required.

## RCS-007 decisive replays

The exact positive-removal control uses a `0.000001 mm` skim with `0.0001 mm` OCCT fuzzy value. The analytic expected removal is `0.0075398221888583 mm³`; both pins measure zero removal while reporting a valid B-rep.

The 100-step repeated-finish chain uses `0.00001 mm` increments with `0.0001 mm` fuzzy value. Both pins reproduce an order delta of `7.539633873064304 mm³`.

The operation journal's positive-removal intent is never erased merely because a Boolean returns valid topology.

## RCS-011 decisive replays

The `retrace-jitter` fixture uses two 30 mm horizontal flat-end-mill traversals, radius `2.5 mm`, separated by `0.001 mm`. Segment-by-segment and one-shot n-ary batch results are both valid, yet differ by `509.00986225103406 mm³` on both pins.

A `slot-clean` dense sampled fallback uses `0.25 mm` spacing and an **8 second child-process bound**. Both pins time out, preserving the bounded-failure classification rather than allowing an unbounded research job.

## BRepGraph/history practical probe

The same probe is compiled against both exact pins. A box is imported into `BRepGraph`, then the graph-native history and freshness facilities are exercised with:

- one-to-many history with `split_image_count == 2`;
- many-to-one history with `merge_origin_count == 2`;
- a `VersionStamp` captured before `graph.Clear()` and required to become stale;
- a rebuild in a fresh graph with a valid `ItemUID`, recording whether a numerical UID collision occurs across graph instances.

Both pins pass the 2/2 history and stale-after-clear controls and both reproduce a numerical UID collision across a fresh graph rebuild. That collision is intentional evidence against treating graph-local UID numbers as canonical operation, body, source or provenance identity.

The probe also uncovered a harness-lifetime trap: `FindModified()` / `FindOriginals()` return pointers into layer-owned mutable containers. The repaired harness snapshots scalar counts before subsequent `Record`/`Clear` mutations. Static adversarial validation rejects reintroducing borrowed-pointer use across the clear boundary.

## Build and migration surface

Both pins use the same headless C++17 shared-library toolkit set:

`TKernel TKMath TKG2d TKG3d TKGeomBase TKBRep TKGeomAlgo TKTopAlgo TKPrim TKBO TKShHealing TKDE TKXSBase TKDESTEP`

BRepGraph lives inside `TKBRep`; it requires no additional toolkit. The measured installed footprints are `83,056,872` bytes for baseline and `82,947,242` bytes for candidate. This small difference is not a safety or upgrade justification.

The candidate bootstrap independently verifies its exact source commit, verifies `OCC_VERSION_COMPLETE=8.1.0` plus `OCC_VERSION_DEVELOPMENT=dev1`, disables OCCT's automatic Git suffix with `USE_GIT_HASH=OFF`, and binds runtime evidence to `OCC_VERSION_STRING_EXT=8.1.0.dev1`.

## Reproduce

The authoritative Linux commands are encoded in `.github/workflows/rcs024.yml`. In outline:

```text
bash research/rcs-006/harness/bootstrap_occt.sh
bash research/rcs-024/bootstrap_candidate.sh
cmake ... research/rcs-024/harness ... # once per exact pin
python3 research/rcs-024/run_differential.py ... --out-dir .results/rcs024
python3 tools/validate_rcs024.py --results-dir .results/rcs024
```

The workflow retains bootstrap and probe-build logs even on failure. `run_differential.py` writes a partial machine-readable record before continuity gates so a failed boundary remains inspectable. The candidate cache key includes its exact upstream commit and bootstrap hash. An unpinned `master` build is never accepted as durable evidence.

## Architectural guardrails

Regardless of comparative outcome:

- process isolation remains the founding scheduler boundary unless a later issue performs broad, multi-surface qualification;
- OCCT/BRepGraph UID/history stays backend-private and may annotate or accelerate reconstruction, never replace the canonical manufacturing journal;
- STEP remains mandatory primary engineering output;
- topology validity never overrides material/semantic oracles;
- tolerance is not widened to make a failing fixture pass;
- disconnected material bodies, source identity and provenance cannot be silently discarded.

## Result handoff

The normalized durable evidence is `measured-result-v1.json`. Its first successful source was workflow run `35400220872`, head `5ee2dda2677ca9f6dc19da8e3210bb19e982819d`, artifact `10569839655`, artifact SHA-256 `65d61055cd637a09aa61ca6ac6bfc3c661adfbd18cceaf17668a794bbd23a3ae`.

The classification is **same defects; no upgrade case**. OCCT 8.0.1 remains the founding baseline, process isolation remains mandatory, and BRepGraph may be used selectively behind a backend-private adapter. `docs/32-OCCT-CURRENT-DIFFERENTIAL.md` and DR-0021 carry the programme-level interpretation. The branch must not merge until the exact final head passes RCS-024 plus all existing pull-request workflows.
