# RCS-021 — Manual/freehand mill independent material oracle and bounded fallback research

Status: measurement in progress on issue #40 branch  
Date: 2026-09-17  
Issue: RCS-021 / #40

## Purpose and boundary

RCS-011 established a useful fixed-orientation milling hierarchy, but it also produced two decisive negative results: an arbitrary near-coincident retrace could return a valid one-solid B-rep with materially wrong volume, and dense sampled cutter-pose B-rep fallback exhausted its 30-second containment bound in every tested attempt. RCS-012 separately demonstrated that a coarse volumetric representation can be robust yet erase a real positive sub-cell feature.

RCS-021 therefore does not ask which backend produces the nicest topology. It asks what the material set physically is, how independently that truth can be bounded, and which fallback representations can participate without silently redefining manufacturing intent.

The qualified domain is founding fixed-axis milling. Simultaneous XYZ translation is in scope for flat-end motion. Arbitrary tool-axis rotation/five-axis motion remains out of scope and must be refused or researched separately.

## Hypotheses

### H1 — independent material truth can expose valid-but-wrong B-rep

**PROPOSAL:** a representation-neutral, OCCT-independent material-set oracle can bound the final material strongly enough to distinguish the RCS-011 sequential retrace result from its valid-but-wrong n-ary freehand batch.

**FALSIFICATION:** the oracle interval contains both materially incompatible results, or the same oracle fails its closed-form controls.

### H2 — a machining-native directional field is a credible bounded fallback

**PROPOSAL:** a dexel/tri-dexel-style material representation can retain self-crossing, retrace, overlap, cut-through and stationary-engagement material semantics without one B-rep Boolean per path segment.

**FALSIFICATION:** deterministic repeats disagree, material bounds fail to overlap the independent oracle, the two-body cut-through is lost, or positive sub-tolerance removal is silently erased.

### H3 — resolution is a separate error channel

**PROPOSAL:** candidate uncertainty should shrink explicitly with refinement and must not be hidden inside manufacturing tolerance.

**FALSIFICATION:** finer representation resolution widens its declared uncertainty without explanation, changes material semantics without a bounded transition, or causes a real positive feature to be snapped to zero.

### H4 — maintained external fallback evidence is useful but not authoritative by itself

**PROPOSAL:** Manifold 3.5.3 can provide an executable external robustness comparator for the same material field.

**FALSIFICATION:** the pinned release cannot execute in hosted CI or supplies no useful independent material/topology comparison. Even success does not qualify mesh state for STEP by itself.

### H5 — capability must narrow before truth does

**PROPOSAL:** if a representation cannot close its error/reconciliation budget on a fixture, the correct outcome is refinement, `accepted_pending`, or refusal rather than unbounded acceptance.

**FALSIFICATION:** the recommendation treats watertightness, B-rep validity or visual plausibility as sufficient proof of engineering correctness.

## Independent material oracle

The independent oracle is built from the cutter trajectory itself rather than from OCCT topology or a fallback mesh. For a flat-end cutter at path parameter `t`, a point is inside the occupied cutter volume when its XY distance from the cutter axis is at most the tool radius and its Z coordinate is above the tool-tip plane. The segment field is therefore

`max_t min(radius - horizontal_distance(t), point_z - tip_z(t))`.

Constant-depth and pure-plunge cases simplify directly. For simultaneous XYZ translation, the implementation solves the maximum by bisection over field level. At a candidate level, XY feasibility is an interval of segment parameters inside an expanded disk and Z feasibility is an interval satisfying a linear tip-height inequality. Their intersection is an exact monotone feasibility test up to the declared numeric solve error.

The rounded/ball-nose fixture uses the physically relevant vertical-axis lower hemisphere plus the cutter body extending upward. It is intentionally not dependent on RCS-011's sphere-only comparison proxy. RCS-021 currently restricts this rounded-tool field to constant-Z paths; unsupported rounded simultaneous-Z motion is not projected into that model.

The union of qualified segment fields is treated as 1-Lipschitz. An adaptive octree evaluates the field at a cell centre and uses the cell half diagonal to prove whole-cell removal or whole-cell material retention. Cells that cannot be proven at the configured depth contribute an explicit material-volume interval instead of being guessed. The campaign records interval width, boundary spatial half-diagonal, node count and an independent XY connectivity estimate.

### Closed-form validation

The oracle has deliberately simple controls whose material volume/connectivity are known without OCCT or the dexel candidate:

- stationary flat cutter → cylindrical removal;
- straight constant-depth flat slot → stadium area × depth;
- exact tangency → zero positive-volume removal;
- pure 1 µm plunge → positive cylindrical removal;
- stock-spanning through strip → exactly two remaining material bodies.

A hosted campaign cannot be accepted if these truths fall outside the oracle's conservative material interval.

## Tri-dexel / directional material field

Machining literature has long used multi-dexel workpiece representations built from independent orthogonal ray sets for material-removal simulation. RCS-021 measures the same architectural idea without making ray IDs part of durable programme identity.

The executable candidate retains an analytic remaining-material height for each sampled XY column. It derives X-, Y- and Z-direction interval counts from that field, giving a direct representation-complexity metric while preserving programme-owned operation/body/boundary lineage externally. Each XY column also carries a conservative height interval based on its sampling-cell support radius, so the whole model reports a lower/upper material-volume interval rather than only a centre-sample estimate.

The candidate records pitch, spatial support radius, volume estimate and bounds, body count, directional interval counts, runtime, peak RSS and deterministic engineering signature. Selected cases run at 1.0, 0.5 and 0.25 mm pitch to expose scaling and refinement behavior.

The candidate is not conventional B-rep. Its reconciliation class explicitly requires B-rep reconstruction before STEP. Known analytic/process boundaries are to be recovered from semantic provenance first; generic fitting is only for residual geometry that genuinely lacks a known analytic source.

## Maintained external candidate — Manifold 3.5.3

The campaign pins Manifold 3.5.3 / source commit `0edd9d54876f3135e431575214dd6d8a72866fee`, Apache-2.0. The Python binding executes `Manifold.level_set` over the same programme-owned final-material field and records its construction edge length, requested and reported tolerance, volume, surface area, disconnected components, triangle/vertex counts, status and runtime.

The package is an external comparator, not the material oracle. Mesh watertightness or a successful status cannot overrule the independent material interval. A known feature smaller than the declared external resolution policy is explicitly classified `refused_resolution_budget` even when a diagnostic mesh is still generated.

Sources used for this comparison include the upstream v3.5.3 release/API, the 2012 multi-dexel machining study (DOI `10.1016/j.advengsoft.2011.08.003`) and the 2022 tri-dexel machining simulator study (DOI `10.1016/j.procir.2022.05.108`).

## Pathological fixture campaign

The campaign covers:

- self-crossing freehand motion;
- exact retrace;
- 1 µm laterally jittered near-coincident retrace;
- simultaneous XYZ flat-end motion;
- flat-end and rounded/ball-nose cutter geometry;
- exact tangent and 1 µm penetrative near-tangent entry;
- a positive 1 µm plunge/removal;
- overlapping path/pocket-like motion;
- through-cut separating the stock into two bodies;
- 160-segment freehand motion, materially larger than RCS-011's 50-segment smoke fixture;
- stationary and near-stationary engaged motion;
- closed-form stationary and straight-slot controls.

Metrics are captured against the same material semantics rather than backend-specific topology identity.

## RCS-011 live regression revisit

The full hosted job rebuilds the accepted RCS-011 worker against the pinned OCCT 8.0.1 baseline and reruns the decisive controls under RCS-021's independent material truth.

For `retrace-jitter`, sequential `segment_sweep` and one-shot `freehand_batch` are both executed. The acceptance condition is not merely that the batch reproduces its old numerical failure. The independent oracle must classify the sequential result as materially compatible and the valid one-shot B-rep as materially incompatible.

For `slot-clean`, the old dense sampled-pose fallback is rerun under a strict ten-second process boundary. Success, explicit algorithm error and timeout are all preserved as evidence. The prior RCS-011 result—10/10 attempts timing out at 30 seconds—remains part of the evidence chain; a later faster run would not erase that historical result.

## Positive sub-tolerance removal

RCS-012 showed why resolution cannot be conflated with manufacturing tolerance: a coarse occupancy representation can erase real positive material changes. RCS-021 therefore carries a 1 µm pure-plunge witness whose exact closed-form removal is positive. The directional candidate must report less than full-stock material volume. Manifold's much coarser research resolution is explicitly non-authoritative for that witness and should refuse resolution-qualified use rather than claim that the feature does not exist.

This rule generalizes: inability of a representation to resolve a physical feature is a capability limit of that representation, not evidence that the feature is absent.

## Multi-body material and provenance

The stock-spanning through-cut is required to leave two material bodies. Both the independent connectivity control and the directional candidate must preserve that fact. Any external comparator's component count is recorded but cannot replace the programme body/lineage model.

Dexel intervals, octree cells, mesh triangles and regenerated B-rep faces are local diagnostic identities only. Durable identity remains attached to programme-owned operation, material-body and analytic-boundary lineage per RCS-008 and DR-0014.

## Error and reconciliation policy

The campaign keeps separate:

1. path/control semantics in the canonical journal;
2. independent field numeric solve error;
3. independent oracle boundary spatial bound;
4. directional representation pitch/support bound;
5. external mesh construction controls/tolerance;
6. manufacturing tolerance;
7. STEP/export tolerance.

No one of these may silently absorb another. A candidate is only a bounded fallback when its material interval is compatible with the independent oracle, body semantics are correct, deterministic repeats agree, spatial/volume budgets are explicit, and the eventual B-rep reconciliation requirement is retained.

Primary STEP remains conventional B-rep. No dexel or Manifold result becomes successful engineering output until retained analytic semantics are reconciled and the resulting B-rep passes the accepted RCS-005 pre-export, serialization, read-back and independent-consumer qualification policy.

## Measurement status

The harness, source pins, falsification rules and validators are committed before the hosted campaign. Measured values, workflow/artifact identities and the final capability recommendation will be frozen only from successful GitHub Actions evidence. This document must not be promoted to accepted measured research merely because the code compiles or a candidate mesh is valid.

## Expected decision form after measurement

The evidence will resolve to one of three outcomes:

- **bounded directional fallback qualified** for the measured fixed-axis domain, with explicit resolution/reconciliation limits;
- **narrower accepted subset**, with unresolved fixture classes remaining `accepted_pending` or explicitly refused;
- **no adequate fallback**, retaining the independent oracle as a regression truth source while manual/freehand capability is narrowed rather than misrepresented.

That conclusion will be written from the measured campaign rather than selected in advance.
