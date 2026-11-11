# B1-D20 — exact-current-source cross-consumer metamorphic qualification

**Date:** 2026-11-11. **Evidence class:** DETERMINISTIC_MODEL / local CPython; not native geometry, STEP, engineering-output or solver evidence. **Disposition:** GO for bounded research tests; HOLD for independently authenticated A1/A2 cross-producer admission and review; NO-GO for native/STEP adoption on present economics. **Draft PR:** #473, DO NOT MERGE.

## Source and ownership
- Accepted main remained `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; the D19 parent was `c99e70e03d5cb29cdf5abfbbdd29c970ba62a8d8`; B1 source-test addition landed at `36c59778bdef2bd47513a60cec6b957e6fb884d7`.
- Reconstructed the complete 27 D19 Python files from the D19 exact-source archive, checked each actual Git SHA-1 blob against the D19 manifest, and independently queried the **current D19-head GitHub Contents directory**; 27/27 hashes agreed. The added test blob was fetched again from GitHub and matched locally: `7d65395dbf735e71cf3b22fba4ecebe21969f2ac`, 4,078 bytes.
- Scope of new changes: one deterministic test and this report under `research/experimental/certificate-algebra/core/**`. No A1/A2, MC-038, CI, shared/proof registry, native, physics, or production changes. Do not relabel any outside producer head.

## New independent evaluation controls
`test_metamorphic_consumer_properties.py` tests 150 fixed-seed, positive rational-polynomial sources of degree 0–3. Each source is admitted through actual `base_record → verify_base`. Seven exact evaluation points per source, compared to direct `Piece.at`, test:
- real `split` de Casteljau/restriction invariance;
- signed `affine` reparameterisation in both orientations, including negative-time orientation;
- real E1 product by an independently replayed constant-2 parent;
- real E4 quotient by a separately replayed globally-positive constant-2 denominator, with strictly positive open-cell and closed-denominator claims.

Second test exercises C0 two-piece `CROSS` and `TOUCH` at a genuine source partition seam, verifying exact sided-event reversal under `t = 2 - x`. This is mathematical/model cross-consumer agreement, not a source-authenticated B-spline knot or topology proof.

**Observed:** new 2/2 test methods PASS; complete pre-existing 106 tests plus two new methods **108/108 PASS**, no skips, CPython 3.13.5. All model evaluations agreed. No new falsifier or repair is asserted. Existing malicious Python equality, nested/deep primitive input, source/hash swap, split/affine invalidation and size-refusal cases are included in the same complete run. `experiment.py` PASS.

## Fresh fair recomputation check
For the same deterministic 32-piece/64-edit workload:
- fresh full reproving: **81.739 ms** median; trusted incremental: **30.958 ms** median (2.64×);
- fresh full proof plus complete strict readmission: **207.132 ms** median; incremental plus equivalent strict readmission: **159.322 ms** median (**1.30×**, **47.810 ms saved/64 edits = 0.747 ms/edit**).
- All per-edit state hashes match. The remaining gross savings vanish if incremental-only physical source custody, dependency-cone audit, native reconstruction and STEP/consumer verification cost >= 47.810 ms over the same workload. None of those extra costs is measured here. This does not justify native/STEP promotion or predict CyberSand solver performance.

## Producer and programme gates
A1 #470 genuine current model event verification was independently rerun in D20 at `fe0dada7c430053c4c387f17a062909da9aab8bc`: the exact-zero event verified, the nonzero control verified, altered result/source refused. Two current A1 producer blobs (`5a8e52898725aa10b427de4e5736cb1cf5578d68`, `77f0ba7700002b7a376dfcc2c29b820ea4def485`) and both current B1 bridge blobs matched fresh GitHub current-head source identities. B1 still correctly refuses explicit current A1 producer-head admission because its codec stamps historical revision `281705e947fd7812300d1d2605d3cdf60cdb005e`. The physical window `[0,1]` was **research-supplied**, not authenticated spline-source ancestry. Current A2 #471 head `d9cb56e74e876efb203e04003aadcf8bd368a369` actual `source → point_germ/knot_germ → verify` remains **NOT EXECUTED** here. B1 `phase_bridge.PRODUCERS` still names historical A1/A2 revisions, so there is **no authenticated current producer admission**. Independently held physical B-spline control, knot and window ancestry remains unestablished. A3 and B5 second-source execution and review are requested in the existing #471/#472 comments; this local session is not independent A3/B5 acceptance.

The accepted frozen census **121/20/30/50**, **26 machining operations**, MC-B and MC-1 `NOT_ESTABLISHED`, `production_authorized=false` and all prior evidence remain unchanged. No merge, production bootstrap, or paid/native campaign.

## Reproduction
```bash
python3 -m unittest discover -s research/experimental/certificate-algebra/core -p 'test_*.py' -v
python3 research/experimental/certificate-algebra/core/experiment.py
python3 research/experimental/certificate-algebra/core/bench_b1_fair_boundary_20261110.py
```
The B1 tree must be read at the **published literal PR head**; do not mix earlier producer bridges with a later producer source, or treat Git blob matches as custody of physical machining input.
