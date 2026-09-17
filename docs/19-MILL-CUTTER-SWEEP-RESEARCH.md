# RCS-011 — Mill cutter-sweep and process-hierarchy research

Status: research in progress; measured conclusions are accepted only after the RCS-011 CI campaign is green and durable evidence is committed  
Date: 2026-09-17  
Issue: RCS-011  
Pinned geometry baseline: OCCT 8.0.1, tag `V8_0_1`, commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

## Purpose and scope

RCS-011 determines how the initial fixed-orientation milling provider should dispatch between process-semantic operations, exact cutter sweeps, batched removal, arbitrary canonical freehand paths, and an explicit fallback. It does **not** claim to solve general five-axis machining or arbitrary rotating-tool kinematics.

The programme invariant is the final material set, not rendering individual flutes. A cutter envelope represents the volume occupied by the cutting portion of the tool over a canonical trajectory. The durable source of intent remains the canonical manufacturing journal; sweep tessellation, OCCT topology and batching decisions are backend-private derived state.

This work consumes the accepted RCS-007 separate tolerance channels, RCS-008 semantic lineage, RCS-009 regularized volumetric material semantics/bounded deferred topology, and RCS-010 process-provider dispatch precedent. The STEP output gate remains `msac-step-conformance/1.0`.

## Questions

The experiment asks:

- Which milling operations are safe to execute as explicit or strictly recognized analytic envelopes?
- When is an exact fixed-orientation segment sweep sufficient?
- When can adjacent canonical segments be simplified/batched without changing the material set?
- Can self-crossing/retraced freehand paths be represented as a union of fixed-orientation segment envelopes without topology or runtime exploding?
- What does a deliberately approximate sampled-pose fallback lose, and can that loss be bounded rather than hidden?
- How should stationary engaged motion be represented?
- Which reconciliation boundaries should be preferred before STEP, body-connectivity decisions, tool withdrawal, or provider handoff?
- What recognition policy avoids silently converting natural analogue motion into a different manufacturing operation?

## Hypotheses and falsification criteria

### H1 — hierarchy beats a universal sweep

**PROPOSAL:** a five-level dispatch hierarchy can preserve exact material semantics for common fixed-orientation milling while keeping arbitrary canonical freehand motion available.

The hypothesis is falsified if one of the exact hierarchy levels changes volume/body count beyond the declared comparison budget, produces invalid topology on its intended fixture class, or cannot satisfy the applicable STEP round-trip gate.

### H2 — cutter envelope, not flute animation, is the geometry primitive

**PROPOSAL:** flat-end and ball-end material-removal envelopes can be represented directly for the founding fixed-orientation subset. Individual cutting flutes are irrelevant to the committed material set.

The hypothesis is falsified if the envelope proxy fails a physical oracle that the corresponding canonical tool trajectory should satisfy.

### H3 — deterministic canonical batching can reduce work without changing material

**PROPOSAL:** exact duplicate samples and strictly collinear same-direction samples may be removed from a backend-private sweep description before Boolean materialization, while reversals, crossings and jitter remain semantically significant.

The hypothesis is falsified if simplification changes the exact-envelope result beyond the geometry budgets or causes a body/connectivity mismatch.

### H4 — strict recognition must be conservative

**PROPOSAL:** explicit semantic tags are authoritative. Automatic recognition is allowed only for a narrowly provable canonical shape, such as a monotone collinear constant-depth path. Bounded analogue jitter must not be rounded into a semantic slot by recognition.

The hypothesis is falsified by any false-positive recognition fixture in the campaign.

### H5 — sampled fallback must declare approximation

**PROPOSAL:** a sampled cutter-pose fallback may be useful as a local escape route only when it reports a geometric under-approximation bound and is not silently promoted to exact engineering state.

The hypothesis is falsified as an *exact* strategy by any shared fixture whose measured final material exceeds the exact-reference error budget. Such a failure is still useful negative evidence for the fallback role.

## Fixed material and tool model

The research worker uses a `40 × 30 × 10 mm` analytic box stock in the accepted right-handed, Z-up workpiece frame.

The tool models are intentionally process envelopes:

- **flat end mill / cylindrical drill proxy** — a vertical cylinder from the commanded tool-tip plane through the top of stock;
- **flat end-mill horizontal segment** — exact swept cylinder expressed as a stadium prism: two endpoint cylinders plus the connecting oriented rectangular prism;
- **pure plunge** — the deepest vertical cylinder envelope;
- **ball-end proxy** — a sphere at the cutting tip centre;
- **ball-end linear segment** — the exact capsule envelope: endpoint spheres plus a cylinder aligned with the segment.

These are fixed-orientation material-removal envelopes. They are not spindle/flute animation and do not attempt tool deflection, holder collision, helix geometry, or cutting-force physics.

## Strategy hierarchy under test

### Level 1 — explicit analytic

An explicit operation tag, or a canonical path with a proof strong enough for the same semantics, constructs a direct analytic envelope. The campaign uses drilling/plunge, a clean straight slot, and coplanar/positive face skim examples.

### Level 2 — exact segment sweep

Each canonical segment is converted to an exact fixed-orientation cutter envelope and subtracted immediately. This is the high-fidelity baseline for arbitrary canonical polyline motion, but it deliberately pays one material Boolean per segment.

### Level 3 — canonical batch

Consecutive duplicate poses and strictly collinear, same-direction points are removed. Reversals are retained. Exact remaining segment envelopes are passed to one material subtraction.

This is a backend optimization only. The canonical operation journal is not rewritten or compacted.

### Level 4 — freehand batch

All canonical freehand segments are retained, including crossings, reversals and retraces, while their exact fixed-orientation envelope set is subtracted in one Boolean. This tests whether material batching can decouple Boolean count from path sample count without inventing process recognition.

### Level 5 — sampled fallback

The fallback samples cutter poses at a declared maximum spacing and subtracts the pose solids in one operation. For round cutters the worker reports the straight-segment radial sagitta bound

`r - sqrt(r² - (s/2)²)`.

The fallback is expected to under-approximate the exact swept envelope between samples. A budget breach is recorded as negative evidence rather than reclassified as success.

## Fixture coverage

`research/rcs-011/experiment-plan-v1.json` maps concrete cases back to RCS-003 families.

The smoke profile covers:

- explicit drilling / plunge semantics;
- clean flat-end slot;
- overlapping slots;
- exact coplanar face skim and a positive skim neighbor;
- `1 µm` positive plunge;
- self-crossing freehand path;
- exact retrace and `1 µm` lateral-jitter retrace;
- exact tangent entry and a penetrative neighbor;
- repeated stationary engaged motion;
- ball-end linear envelope;
- through-slot body separation;
- dense segmentation of a geometrically simple line.

This includes clean machinist-like moves and deliberately messy analogue/freehand cases.

## Recognition policy

Recognition is intentionally asymmetric:

1. explicit journal process semantics are trusted when the selected provider declares support;
2. exact canonical geometric proof may enable a narrow optimization;
3. approximate resemblance is never enough to change manufacturing semantics.

The test recognizer accepts an explicitly tagged drill and a constant-depth monotone collinear slot. It rejects a visually similar jittered slot and a self-crossing path.

A future production recognizer may be richer, but any recognition that changes solver semantics needs falsifiable false-positive tests. Raw controller samples must be canonicalized first; recognition must not hide the bounded trajectory represented by the journal.

## Stationary and near-stationary engaged motion

A stationary engaged cutter still has a material envelope. Repeated stationary samples do not imply repeated physical removal once the pose envelope has already been subtracted. The journal events remain available for replay/provenance, while a provider may collapse duplicate geometry work under the RCS-008/RCS-009 rules.

Near-stationary motion is not automatically stationary. It remains a real segment unless canonicalization policy proves it equivalent within the independent control/sampling trajectory bound. This is separate from manufacturing tolerance and OCCT entity tolerance.

## Topology and reconciliation boundaries

RCS-009 already permits bounded deferred topology. RCS-011 therefore treats the following as hard or preferred boundaries:

- **mandatory:** primary STEP export;
- **mandatory:** possible body separation before retention/scrap/clamping policy;
- **mandatory:** provider handoff to a representation that requires reconciled B-rep;
- **preferred:** tool withdrawal / end of a semantically coherent pass when interactive topology queries are needed;
- **optional:** intermediate canonical samples when the active provider can answer required material queries without materializing every boundary.

The worker itself always returns a conventional B-rep because it is a comparison harness, not the production deferred representation.

## Geometry, topology, performance and STEP metrics

Every attempt records:

- OCCT version/commit;
- input and canonical segment counts;
- material Boolean count;
- cutter-envelope primitive count;
- approximation bound where applicable;
- B-rep validity;
- vertex/edge/face/shell/solid counts;
- volume and surface area;
- bounding box;
- analytic surface classes;
- worker runtime and peak RSS;
- STEP write/read-back status, body count, volume delta and bounding-box delta on selected cases.

Repeated attempts compare a normalized engineering signature rather than bitwise STEP identity.

## Source anchors

The executable baseline is exactly OCCT 8.0.1 at commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`.

Primary implementation anchors include:

- Boolean subtraction: `src/ModelingAlgorithms/TKBO/BRepAlgoAPI/BRepAlgoAPI_Cut.hxx`;
- primitive cylinders/spheres/boxes: `src/ModelingAlgorithms/TKPrim/BRepPrimAPI/`;
- B-rep validation: `src/ModelingAlgorithms/TKTopAlgo/BRepCheck/BRepCheck_Analyzer.hxx`;
- STEP translation: `src/DataExchange/TKDESTEP/STEPControl/` and `DESTEP_Parameters.hxx`.

The source pin is inherited from the accepted RCS-004/RCS-006 baseline. No current-master behavior is substituted into the measured campaign.

## Expected interpretation before measurements

The architecture recommendation is intentionally **not** accepted from this section alone.

The predicted outcome is:

- explicit semantic operations should be preferred when they are truly explicit and supported;
- simple exact sweeps remain the correctness baseline for fixed-orientation motion;
- canonical batching should substantially reduce material-Boolean count on dense collinear/retraced paths;
- freehand batching should preserve arbitrary self-crossing/retraced canonical motion without requiring unsafe recognition;
- a sampled fallback will likely be useful only as bounded local fallback/preview/intermediate evidence unless reconstruction closes its measured gap before an authoritative boundary.

Measured results, negative cases, and the final RCS-013 input will be committed after the hosted campaign executes successfully.

## Boundaries and unresolved questions

This issue does not solve:

- simultaneous tool-axis reorientation or general 5-axis machining;
- holder/fixture collision geometry;
- exact real flute geometry;
- cutting-force/deflection physics;
- automatic feature recognition from uncanonicalized controller motion;
- production scheduling/concurrency;
- the final non-OCCT fallback representation, which remains RCS-012;
- the final provider dispatch API, which remains RCS-013.

A fixed-orientation path that cannot be represented by the exact envelope classes used here must be handed to a broader provider/fallback. It must not be coerced into a supported operation by approximation without an explicit error/status result.
