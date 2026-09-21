# MC-014 — Physical adversarial corpus F13–F16

Status: **COMPLETED_RESEARCH pending exact-head CI at authoring time**. Issue #76. Source baseline `f5bce8ec716e0de193cc162c110d1dfdb9bbb3d1`.

## Hypothesis and falsification criterion

The final F13–F16 tranche can be made candidate-independent and physically discriminating without turning operation count, retrace count, partition/provider ownership or disappearance of exhausted material into substitutes for physical truth. The task is falsified if any tier can claim growth without new positive-volume material removal, if retraces add material change, if reconstruction interfaces can hide a gap/overlap, if exact empty material is represented by deleting durable identity/provenance, or if expected truth depends on candidate/historical geometry output.

## Dependency reconciliation

MC-002, MC-003, MC-010 and MC-055 are consumed only through their accepted immutable artifacts. Historical RCS material is provenance/adversarial motivation only and never supplies current expected truth. The full F01–F16 denominator remains mandatory; this task changes only F13–F16 from `UNBUILT` to `BUILT`.

## F13 — genuine geometric growth

F13 contains five tiers adding 1, 2, 4, 8 and 16 distinct top-accessible pockets in previously uncut material. Every pocket is an exact `1 x 8 x 1 mm` rational box and the tiers add exactly `8, 16, 32, 64, 128 mm^3` of new material removal. The increment therefore doubles at every tier and the cumulative removal is `8, 24, 56, 120, 248 mm^3`. IDs are unique and x-intervals are disjoint, so the growth cannot be produced by retraces, no-ops or event-count padding.

## F14 — redundant long history

F14 is a 67-entry history containing four independently located material-changing pockets and 63 exact retraces. The only change steps are 1, 17, 34 and 51. Exact set/idempotence semantics give a final removed volume of `32 mm^3`; a forbidden event-count interpretation would report `536 mm^3`. This makes long redundant history a direct adversarial control rather than a performance-only stress case.

## F15 — boundary-crossing reconstruction

F15 is one continuous top-access channel spanning `x=[12,28]`, crossing a patch boundary at 16, an adaptive-cell boundary at 20 and a provider boundary at 24. Exact reconstruction yields four contiguous segments with volumes `32 mm^3` each and exactly the same `128 mm^3` whole feature. At the provider interface, exact continuity, a `+1/1000 mm` gap and a `-1/1000 mm` overlap are three distinct states. Provider/patch ownership is therefore bookkeeping and cannot create, delete, duplicate or bridge material.

## F16 — empty and exhausted bodies

F16 starts with two durable `400 mm^3` bodies. Each first receives an independently witnessed `36 mm^3` top pocket, leaving `364 mm^3`, then is exhausted by a full-area raster to exact zero while sacrificial support remains below the part. One-body exhaustion preserves the other positive body; final exhaustion records both as `EXACT_EMPTY` while retaining durable identity/lineage records. A `+1/1000000 mm` residual slab has exact positive volume `1/10000 mm^3` and cannot be rounded to empty; zero and negative-overtravel neighbours remain distinct.

## Independence and protected semantics

`fixture_oracle.py` uses exact `Fraction` arithmetic and standard-library typing only. It imports no RCS, candidate geometry, OpenCascade, Manifold or provider implementation. Its SHA-256 is pinned by the corpus contract. Protected `research/rcs-*` blobs remain unchanged; source/audio/provenance, canonical-journal, positive-volume, durable-body/lineage and historical negative-evidence semantics are preserved.

## Programme state

F01–F16 are now all constructed as mandatory `BUILT` prospective fixture records. This completes corpus construction only. No native or paid geometry campaign was run; no candidate has passed these fixtures; no certificate/oracle-attack qualification is implied. `MC-A` remains `ACCEPTED`; `MC-B` through `MC-F` and `MC-1` remain `NOT_ESTABLISHED`.

## Verification

The deterministic verifier checks dependency blob identities, oracle source/import independence, real per-tier material growth, exact-retrace idempotence, cross-interface exact coverage and signed corrupt neighbours, exact positive/empty/overtravel body states, live registry progression, protected historical blobs, branch diff hygiene and deliberately corrupted controls. Static CI must compile the oracle/verifier, run `mc_workflow.py verify MC-014`, validate programme contracts and confirm managed-issue zero drift before merge.
