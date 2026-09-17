# RCS-011 — Mill cutter-sweep and process-hierarchy research

Status: accepted RCS-011 research output; architecture input to RCS-012/RCS-013  
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

**MEASURED:** supported, with an important qualification. Explicit analytic operations, per-segment exact sweeps and conservative canonical batching were reliable on their tested domains. A universal one-shot freehand batch was falsified by the `retrace-jitter` fixture, where OCCT returned a valid B-rep with essentially unchanged stock instead of the reference material removal.

### H2 — cutter envelope, not flute animation, is the geometry primitive

**PROPOSAL:** flat-end and ball-end material-removal envelopes can be represented directly for the founding fixed-orientation subset. Individual cutting flutes are irrelevant to the committed material set.

The hypothesis is falsified if the envelope proxy fails a physical oracle that the corresponding canonical tool trajectory should satisfy.

**MEASURED:** supported for the tested fixed-orientation flat/drill/ball envelope cases. The successful exact strategies retained valid solids and the applicable STEP round trips.

### H3 — deterministic canonical batching can reduce work without changing material

**PROPOSAL:** exact duplicate samples and strictly collinear same-direction samples may be removed from a backend-private sweep description before Boolean materialization, while reversals, crossings and jitter remain semantically significant.

The hypothesis is falsified if simplification changes the exact-envelope result beyond the geometry budgets or causes a body/connectivity mismatch.

**MEASURED:** supported for the deliberately narrow simplification rule. The 50-segment straight-line fixture collapsed from 50 material Booleans to one while preserving measured volume; face count fell from 1137 to 16. Repeated stationary engagement collapsed from ten material Booleans to one with identical measured material.

### H4 — strict recognition must be conservative

**PROPOSAL:** explicit semantic tags are authoritative. Automatic recognition is allowed only for a narrowly provable canonical shape, such as a monotone collinear constant-depth path. Bounded analogue jitter must not be rounded into a semantic slot by recognition.

The hypothesis is falsified by any false-positive recognition fixture in the campaign.

**MEASURED:** supported by all five recognition guards: explicit drill, exact two-point slot and dense collinear slot were recognized; the jittered near-slot and self-crossing path were rejected.

### H5 — sampled fallback must declare approximation

**PROPOSAL:** a sampled cutter-pose fallback may be useful as a local escape route only when it reports a geometric under-approximation bound and is not silently promoted to exact engineering state.

The hypothesis is falsified as an *exact* strategy by any shared fixture whose measured final material exceeds the exact-reference error budget. Such a failure is still useful negative evidence for the fallback role.

**MEASURED:** the tested OCCT pose-solid implementation is rejected as an authoritative fallback before fidelity can even be accepted: all ten sampled-fallback attempts across five cases exceeded the 30-second per-attempt bound. The mathematical sampling bound remains useful, but dense overlapping B-rep pose solids are not a viable founding fallback implementation.

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

Measured evidence makes this an **opportunistic candidate, not a universal exact level**. It succeeded on the self-crossing, exact-retrace, through-cut and dense-line fixtures, but the near-coincident `retrace-jitter` case produced a valid yet materially wrong result. RCS-013 must therefore require a narrower applicability proof or use a safer provider/fallback.

### Level 5 — sampled fallback

The experiment samples cutter poses at a declared `0.25 mm` maximum spacing and subtracts the pose solids in one operation. For round cutters the worker reports the straight-segment radial sagitta bound

`r - sqrt(r² - (s/2)²)`.

This implementation was not tractable: every sampled attempt hit the 30-second containment timeout. It is retained as negative evidence and must not be promoted to authoritative engineering state. RCS-012 owns research into a broader non-OCCT fallback representation.

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

The measured stationary fixture used ten repeated segments. Sequential exact evaluation performed ten material Booleans; conservative canonical batching performed one. Both measured `11941.095137745191 mm³`, supporting derived-work collapse while retaining the durable journal events.

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

## Measured campaign

Durable summary: `research/rcs-011/measured-summary-v1.json`. The accepted hosted campaign used OCCT 8.0.1 at the pinned commit and the `release-shared-cxx17-worker-only-headless-v4` build profile. It executed every founding case twice.

The campaign produced **88 attempts**: **76 success**, **2 geometric-tolerance breaches**, and **10 bounded timeouts**. There were **zero harness structural failures** and **zero required-reference failures**. The twelve negative outcomes are deliberately retained as research evidence rather than converted into CI success records.

### High-segment canonicalization

For `high-segment-line`, the exact segment reference performed 50 material Booleans, produced 1137 faces and measured `11602.300888156884 mm³`. Conservative canonical batching recognized the same straight material envelope, performed one material Boolean, produced 16 faces and measured `11602.300888156922 mm³`—a difference of roughly `3.8e-11 mm³`, far below the experiment budget.

On this hosted run the first exact sequential attempt took about `7664 ms`, versus about `22.8 ms` for canonical batching. Timing is environment-specific, but the Boolean/topology reduction is algorithmic evidence rather than a benchmark-only speed claim.

A one-shot unsimplified freehand batch also used one material Boolean on this case, but retained 150 overlapping envelope primitives, 1137 faces and took about `26.5 s`. Merely reducing the top-level Boolean call count does not guarantee lower geometric complexity.

### Near-coincident retrace counterexample

For `retrace-jitter`, the per-segment reference produced a valid one-solid result of `11490.990137750125 mm³`. The one-shot freehand batch also returned a valid one-solid B-rep, but its measured volume was `12000.000000001159 mm³`: effectively unchanged stock. Both repeats reproduced the failure.

This is a stronger negative result than an exception. A valid topology result is not evidence of correct material semantics, and arbitrary near-coincident/retraced exact envelopes must not be routed blindly through one n-ary OCCT cut.

### Sampled pose-solid fallback

The `0.25 mm` sampled-pose implementation was attempted twice on each of `slot-clean`, `overlapping-slots`, `self-cross`, `retrace-jitter`, and `ball-path`. All ten attempts reached the 30-second per-attempt timeout and were contained without losing the rest of the campaign.

This implementation is therefore rejected as the authoritative fallback. The result does not reject sampling mathematics in general; it rejects this dense overlapping OCCT B-rep pose-solid construction as a practical founding path. RCS-012 should compare more appropriate fallback representations rather than hiding this cost by loosening the engineering contract.

### Small-contact and diagnostic cases

The exact tangent-contact fixture preserved the full `12000 mm³` stock, while its penetrative neighbor removed measurable material. The `1 µm` plunge remained an explicit diagnostic and produced measurable removal in the tested baseline rather than being silently rounded away. These outcomes reinforce RCS-007's rule that contact/control uncertainty is not a global manufacturing epsilon.

### STEP evidence

There were **32 successful STEP round-trip attempts** among successful STEP-enabled strategies. These included drilling, clean slotting, coplanar skim, self-crossing exact motion, ball-end motion and the two-body through-cut. Successful cases wrote AP242DIS millimetre manifold B-rep and re-read within the campaign's RCS-005 volume/bounding-box budgets.

The two-body `cut-through` case retained two solids through the applicable exact strategies and STEP read-back, preserving the RCS-005 rule that disconnected material must not be silently discarded or fused.

OCCT self-readback remains only the automated geometry gate; it does not replace the independent-consumer qualification required by RCS-005.

## Accepted architecture recommendation

RCS-011 recommends the following bounded policy for the founding fixed-orientation milling provider:

1. **Prefer explicit manufacturing semantics.** If the journal explicitly identifies a supported drill/plunge/slot or another process operation, dispatch to its direct analytic/material-envelope provider.
2. **Permit strict canonical simplification only with a proof.** Exact duplicate engaged samples and strictly collinear same-direction segments may collapse derived geometry work while the original journal events and lineage remain intact.
3. **Keep exact per-segment envelopes as the correctness baseline for general supported fixed-orientation polylines.** They are more expensive, but the measured reference remained reliable across the founding corpus.
4. **Treat one-shot arbitrary freehand batching as opportunistic, not universal.** Self-crossing and some retraces succeeded, but a near-coincident retrace produced a valid materially wrong result. No provider may infer correctness from `IsDone`, B-rep validity or one Boolean call alone.
5. **Reject the tested dense sampled-pose B-rep fallback as authoritative.** Preview/local diagnostic use may be separately bounded, but an authoritative fallback must hand off to a representation/provider whose error and material semantics are controlled. RCS-012 owns that comparison.
6. **Preserve regularized material and semantic lineage across every optimization.** Batching/simplification is backend-private derived work; RCS-008 body/operation identity and RCS-009 reconciliation boundaries remain authoritative.
7. **Reconcile at authoritative boundaries rather than every controller sample.** STEP export, possible body separation, incompatible provider handoff and topology-dependent decisions require reconciled evidence; semantically coherent pass/tool-withdrawal boundaries are preferred when interactive topology is needed.

This policy deliberately does not promise general five-axis support. Tool-axis reorientation requires additional envelope/kinematic research and must be refused or handed to a future provider rather than projected into this fixed-orientation contract.

## RCS-013 inputs

The implementation architecture should expose provider capability and refusal explicitly. For the mill side, RCS-013 should be able to distinguish at least:

- explicit supported analytic/process operation;
- strict canonical exact-envelope optimization;
- exact fixed-orientation segment-envelope path;
- bounded deferred/regularized material state pending reconciliation;
- unsupported or fallback-required path;
- approximate preview-only representation.

Dispatch must carry the canonical operation identity, setup/tool revision, material-body lineage, trajectory/control uncertainty and required reconciliation boundary. It must not pass OCCT topology IDs or make a successful kernel status equivalent to material correctness.

The measured `retrace-jitter` counterexample should become an architecture/regression guard against any future proposal that routes all freehand paths through a single n-ary B-rep cut.

## Source anchors

The executable baseline is exactly OCCT 8.0.1 at commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`.

Primary implementation anchors include:

- Boolean subtraction: `src/ModelingAlgorithms/TKBO/BRepAlgoAPI/BRepAlgoAPI_Cut.hxx`;
- primitive cylinders/spheres/boxes: `src/ModelingAlgorithms/TKPrim/BRepPrimAPI/`;
- B-rep validation: `src/ModelingAlgorithms/TKTopAlgo/BRepCheck/BRepCheck_Analyzer.hxx`;
- STEP translation: `src/DataExchange/TKDESTEP/STEPControl/` and `DESTEP_Parameters.hxx`.

The source pin is inherited from the accepted RCS-004/RCS-006 baseline. No current-master behavior is substituted into the measured campaign.

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
