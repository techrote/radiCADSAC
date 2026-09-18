# OCCT current differential and backend-private history contract

Status: **RCS-024 measured and frozen. OCCT 8.0.1 remains the founding baseline; the 8.1.0.dev1 snapshot does not justify an upgrade.**

## Question

Does current pinned OCCT evidence justify changing the founding 8.0.1 baseline, the process-isolated worker boundary, or the programme's independent manufacturing identity/provenance model?

## Compared builds

| Role | OCCT version | Exact commit | Release status |
|---|---|---|---|
| founding control | 8.0.1 | `b8f597c677811d1f9f4d8a97f5ae2825c0353a42` | latest stable at 2026-09-18 |
| differential candidate | 8.1.0.dev1 | `3d097a0328e71b826377d4814ab05ec3c3d23871` | pinned development snapshot |

The distinct comparison is intentionally a development snapshot because no newer stable release exists. Recency is not qualification.

## Evidence families

RCS-024 carries forward only the decisive controls needed by the recorded repair path:

- minimized RCS-017 STEP tolerance cross-talk with distinct writers and sequential controls;
- job-local `SetRunParallel` versus process-global `BOPAlgo_Options` state;
- RCS-007 positive sub-tolerance material removal and order-sensitive repeated finish;
- RCS-011 retrace-jitter one-shot batching and a bounded sampled-fallback pathology;
- BRepGraph one-to-many/many-to-one history, graph-generation freshness, and rebuild identity observations.

This is a differential investigation, not a new broad defect search.

## Measured result

The first successful exact-pin evidence was produced by pull-request workflow run `35400220872` on head `5ee2dda2677ca9f6dc19da8e3210bb19e982819d`, artifact `10569839655`, SHA-256 `65d61055cd637a09aa61ca6ac6bfc3c661adfbd18cceaf17668a794bbd23a3ae`. The normalized durable record is `research/rcs-024/measured-result-v1.json`. Final-head CI must reproduce the contract before merge.

| Control | OCCT 8.0.1 | OCCT 8.1.0.dev1 | Classification |
|---|---|---|---|
| STEP sequential 0.00001 mm writer | `0.00001 mm` | `0.00001 mm` | control intact |
| STEP first writer after conflicting 0.001 mm writer configured | `0.001 mm` | `0.001 mm` | same cross-talk defect |
| process-global parallel flag observed across threads | yes | yes | same global-state interference |
| 0.000001 mm positive skim, expected removal `0.0075398221888583 mm³` | measured `0`, valid B-rep | measured `0`, valid B-rep | same valid-but-materially-wrong defect |
| 100-step finish-chain order delta | `7.539633873064304 mm³` | `7.539633873064304 mm³` | same order sensitivity |
| retrace-jitter batch/reference volume delta | `509.00986225103406 mm³` | `509.00986225103406 mm³` | same valid-but-materially-wrong defect |
| bounded sampled fallback | timeout at 8 s | timeout at 8 s | same bounded failure |
| BRepGraph split / merge history | `2 / 2` | `2 / 2` | usable on both pins |
| pre-clear VersionStamp stale after `Clear()` | true | true | freshness boundary works on both pins |
| numerical ItemUID collision across fresh graph rebuild | true | true | graph UID number is not programme identity |
| installed worker-only footprint | `83,056,872` bytes | `82,947,242` bytes | negligible difference; not an upgrade reason |

The candidate therefore lands in **same defect** for every decisive manufacturing/concurrency control exercised here. It supplies no measured safety or correctness improvement that could justify replacing the stable 8.0.1 founding baseline.

During harness repair, an apparent BRepGraph discrepancy was traced to the probe retaining pointers returned by `FindModified()` / `FindOriginals()` across later history mutation and `graph.Clear()`. Those pointers refer to layer-owned mutable containers. The probe now snapshots scalar evidence before mutation and has adversarial guards preventing that lifetime error from returning. This was a harness defect, not an OCCT pin delta.

## BRepGraph interpretation

BRepGraph history/UID/freshness facilities are useful *inside derived OCCT state*. The measured 2-way split, 2-origin merge and stale-after-clear controls confirm that both pins expose practical reconciliation/freshness mechanisms. The measured numerical UID collision after rebuilding a fresh graph is a direct counterexample to promoting compact graph identity into programme identity.

Accordingly:

- canonical operation IDs describe durable manufacturing intent independently of the kernel;
- body IDs and body transitions survive kernel replacement/rebuild;
- source/provenance identity is not inferred from topology coincidence;
- graph-local UID equality across rebuilds is not semantic equivalence;
- algorithm history is reconciliation evidence, not the manufacturing journal itself;
- BRepGraph may be wrapped behind a backend-private adapter, but its types and IDs do not cross the stable programme identity boundary merely for convenience.

## Concurrency contract

The minimized STEP test reproduces the RCS-017 cross-talk defect identically on both pins: a writer whose sequential `0.00001 mm` output is correct serializes `0.001 mm` after another writer has configured that conflicting tolerance before the first transfer. The parallel-state probe also reproduces process-global cross-thread observation on both pins.

Therefore process-isolated OCCT workers remain the founding scheduler boundary. Per-operation parallelism may be enabled inside an isolated worker only for explicitly qualified operations. Process-global configuration must not be multiplexed between logical jobs in one address space.

## Robustness contract

The current development snapshot reproduces every decisive material-oracle failure seen on the baseline: zero measured removal for positive skim intent, the same order-sensitive finish-chain delta, the same retrace-jitter batching disagreement, and the same bounded sampled timeout. A valid B-rep remains a structural result, not a material oracle.

Positive-removal intent, operation-local uncertainty, exact body count, source/provenance and the RCS-023 propagated error budget retain authority over a kernel result. No tolerance is widened and no body, source, journal or provenance requirement is relaxed to make a fixture pass.

## Build/migration contract

Both pins use the same C++17/headless worker-only toolkit set. BRepGraph is already supplied by `TKBRep`; it is not a candidate-only dependency. The measured installed footprint differs by only 109,630 bytes in the candidate's favour, which is not material to the safety decision.

Any future baseline move must separately account for compiler/CMake requirements, source/API changes, Windows/Linux packaging, dependency availability, license/provenance and complete regression evidence.

## Decision

**Retain OCCT 8.0.1.** Preserve process isolation. Permit selective backend-private BRepGraph history/UID/freshness use where useful, while keeping canonical journal/body/source/provenance identity kernel-independent. Re-open upgrade qualification only for an exact released candidate (or a deliberately accepted fork under a separate decision) with the same or stronger material, STEP, concurrency and provenance evidence.
