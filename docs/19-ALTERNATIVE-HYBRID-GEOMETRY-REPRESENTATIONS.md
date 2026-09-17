# Alternative and hybrid geometry representation trade study

Status: RCS-012 research output  
Date: 2026-09-17  
Issue: RCS-012 / #12

## Purpose and boundary

RCS-012 prevents OCCT/B-rep assumptions from defining the solution space by comparing alternative material representations against the same manufacturing semantics and STEP obligations already accepted by the programme.

The question is not whether another representation can draw or mesh the workpiece. The question is whether it can improve robustness, scaling or regularized material semantics **without losing the ability to reconcile to conventional usable STEP geometry within declared tolerances**.

This report combines:

- **MEASURED** stdlib-only experiments for two non-OCCT candidates;
- **SOURCE** review of pinned current releases for CGAL, Manifold and OpenVDB;
- **INFERENCE** about suitable hybrid roles;
- explicit rejection/defer reasons where evidence does not support a first-class role.

## Hypotheses and falsification criteria

### H1 — deferred/cell material state can decouple operation count from boundary complexity

**PROPOSAL:** for a bounded manufacturing subset, material can remain a set expression or cell complex and only unique physical boundaries need to drive evaluation.

Falsified if exact retraces/repeats require work proportional to journal event count, if lower-dimensional contact creates spurious material change, or if cut-through body separation cannot be represented.

### H2 — voxel/SDF state is robust but resolution-bounded

**PROPOSAL:** sparse volumetric occupancy can provide a useful local escape route for pathological topology, but it cannot be authoritative for features below its grid/error budget and loses analytic surface semantics unless retained separately.

Falsified if a fixed coarse grid nevertheless preserves the sub-cell physical oracles exactly, or if analytic STEP reconciliation is intrinsic rather than a reconstruction problem.

### H3 — no reviewed alternative justifies replacing the complete exact/analytic pipeline

**PROPOSAL:** the strongest result will be a hybrid architecture: retain manufacturing semantics and analytic provenance globally, use alternative representations only where their strengths are decisive, and reconcile bounded fallback regions before STEP export.

Falsified if a reviewed candidate simultaneously provides robust pathological set operations, durable semantic identity, analytic geometry preservation/recovery, acceptable licensing/build cost, and direct RCS-005 STEP conformance with less architectural complexity.

## Executable experiment design

`research/rcs-012/experiment-plan-v1.json` maps eight bounded axis-aligned proxies to RCS-003 families. The geometry is deliberately minimal so the representation itself is tested rather than a cutter-envelope implementation.

Two candidates run twice per case:

1. `exact-orthogonal-cell-deferred-csg` — decimal-valued stock/removal boxes, exact duplicate-envelope canonicalization, exact orthogonal decomposition, six-neighbour material connectivity;
2. `sparse-voxel-center-0p5mm` — deterministic 0.5 mm cubic occupancy by centre classification with the same connectivity rule.

Metrics are material volume, body count, tested/occupied cells, raw versus unique envelope count, runtime, peak RSS where available, analytic-semantic retention, representation error bound, reconciliation class and a deterministic engineering signature.

## Measured results

The committed reference run contains eight cases × two candidates × two repeats = 32 attempt records.

| Candidate | Volume-oracle exact attempts | Body-oracle exact attempts | Max measured volume error | Nondeterministic case groups |
|---|---:|---:|---:|---:|
| exact orthogonal cell / deferred CSG | 16/16 | 16/16 | 0 mm³ | 0 |
| sparse voxel centre, 0.5 mm | 12/16 | 14/16 | 0.2 mm³ | 0 |

### Sub-tolerance plunge

**MEASURED:** the 0.001 mm plunge removes exactly 0.1 mm³ in the orthogonal-cell model. The 0.5 mm occupancy model reports the original 4000 mm³ stock unchanged: it misses the removal completely.

**INFERENCE:** a voxel/SDF fallback can be robust while still being physically wrong below its sampling scale. Its resolution is therefore a distinct declared tolerance/error channel, not a hidden implementation detail.

### Tiny positive-volume cusp

**MEASURED:** the 0.001 mm-wide cusp contains 0.2 mm³ and remains one body in the exact cell model. The 0.5 mm occupancy model reports zero material and zero bodies.

**INFERENCE:** watertight/regularized volumetric processing does not automatically preserve manufacturing intent. A coarse fallback may erase a legitimate positive-volume feature and even change material-body existence.

### Cut-through separation

**MEASURED:** both candidates represent the aligned through-slot as 5600 mm³ in two disconnected bodies.

**INFERENCE:** volumetric and cell representations are naturally capable of multi-body material semantics; body loss is not inherent to these representation families. The export/reconciliation layer still must preserve all selected bodies per DR-0009.

### Operation-count scaling

**MEASURED:** the `mill-very-high-segment-count` proxy records 100000 raw operations but only one unique removal envelope. Exact duplicate-envelope canonicalization evaluates one physical boundary set while retaining the raw operation count as provenance.

**INFERENCE:** manufacturing history and material-evaluation complexity should not be forced to scale identically. This independently reinforces RCS-007/RCS-008: semantic journal history remains durable while safe equivalence/canonicalization may reduce geometry work.

## Candidate-family trade study

| Family | Robust set semantics | Analytic preservation | STEP reconciliation | Scaling potential | License/integration | RCS-013 role |
|---|---|---|---|---|---|---|
| Exact orthogonal cells + deferred CSG | Strong in measured bounded subset | Strong for retained source primitives | Exact planar reconstruction in measured subset; general curved case open | Strong when envelopes canonicalize | Programme-owned prototype | **Promote concept** as bounded deferred/cell technique, not universal kernel |
| Sparse voxel / SDF | Strong coarse occupancy; explicit resolution floor | Lost unless retained out-of-band | Surface extraction + recognition/fitting required | Strong with sparse hierarchy/GPU options | OpenVDB 13.1.0 Apache-2.0 is compatible candidate infrastructure | **Promote as local fallback/preview/recovery**, never silent authoritative replacement |
| CGAL exact predicates/constructions | Strong numerical predicate foundation | Depends on representation layered above kernel | Does not itself provide manufacturing STEP reconciliation | Potentially higher arithmetic cost; benchmark needed | CGAL 6.2.1 `Kernel_23` LGPL-3+ | **Research substrate / targeted component candidate** |
| CGAL Nef_3 | Set-closed polyhedral topology is highly relevant | Polyhedral; analytic surfaces not native | Requires analytic reconstruction or conversion before STEP | Unknown on target workloads until benchmarked | CGAL 6.2.1 Nef_3 is GPL-3+; material licensing constraint | **Defer direct integration; retain as prior art/experimental comparator** |
| Manifold mesh Boolean | Upstream targets guaranteed manifold output and robust edge-case Booleans | Triangle mesh, though source IDs/properties can preserve ancestry hints | Analytic B-rep reconstruction remains external | Upstream emphasizes performance and parallelism | Manifold 3.5.3 Apache-2.0, low mandatory dependency burden | **Promising local mesh fallback candidate**, not STEP-authoritative state |
| OpenVDB sparse grids / level sets | Natural regularized volumetric semantics | Grid samples do not natively preserve analytic surfaces | Requires meshing/analytic recognition/reconciliation | Sparse hierarchy designed for large volumetric domains | OpenVDB 13.1.0 Apache-2.0; larger dependency/build footprint | **Promising local volumetric fallback**, especially bounded pathological regions |

## Primary-source review

### CGAL 6.2.1

Pinned release: https://github.com/CGAL/cgal/releases/tag/v6.2.1, published 2026-09-04.

CGAL exposes exact-predicate/exact-construction kernels that remain relevant to intersection/classification robustness. This addresses arithmetic ambiguity but does not by itself define manufacturing semantics, durable provenance, deferred topology or STEP reconstruction.

Package licensing is not uniform. At `v6.2.1`:

- `Kernel_23/package_info/Kernel_23/license.txt` states **LGPL (v3 or later)**;
- `Nef_3/package_info/Nef_3/license.txt` states **GPL (v3 or later)**.

Nef polyhedra remain important prior art because they are closed under Boolean set operations and admit richer set/topology states than a conventional manifold B-rep. However, Nef_3's polyhedral domain does not preserve native analytic cylinders/cones and its GPL package license is a materially different integration constraint from the core kernel package. RCS-013 should not casually treat "CGAL" as one licensing or representation choice.

### Manifold 3.5.3

Pinned release: https://github.com/elalish/manifold/releases/tag/v3.5.3, published 2026-09-07. License: Apache-2.0 (`LICENSE`).

Upstream describes Manifold as a library for manifold triangle meshes whose primary goal is guaranteed manifold output and whose mesh Boolean is intended to be robust to edge cases. The library also preserves arbitrary vertex properties and source-related IDs, which could be useful evidence when a local mesh fallback must later reconcile against semantic/provenance state.

**INFERENCE:** this is attractive for a *bounded fallback island* where an exact/analytic B-rep route fails, especially because the dependency/license burden is modest. It is not by itself a solution to the programme because a triangle mesh lacks the analytic surfaces and conventional exact engineering representation required by RCS-005.

### OpenVDB 13.1.0

Pinned release: https://github.com/AcademySoftwareFoundation/openvdb/releases/tag/v13.1.0, published 2026-09-16. License: Apache-2.0 (`LICENSE`).

OpenVDB is a sparse hierarchical volumetric grid/data-structure and tool suite. This is directly relevant to local SDF/level-set material state and large sparse workspaces.

**INFERENCE:** a sparse grid can regularize pathological local topology and is well suited to preview, collision/material queries, repair and bounded fallback. It cannot be accepted as authoritative engineering state without a chosen resolution/error policy and a demonstrated B-rep reconstruction path. The measured 0.5 mm prototype deliberately demonstrates the failure mode that such a policy must prevent.

## Analytic geometry and STEP reconciliation

RCS-005 remains the controlling export contract. The alternatives divide into two broad classes:

- representations that can **retain known analytic primitives/provenance** while deferring topological commitment;
- representations that discretize geometry and therefore require later **recognition/fitting/reconstruction**.

The first class should be preferred whenever process semantics already know a plane, cylinder, cone, tool envelope or exact boundary. It is wasteful and risky to discard that knowledge and later infer it from triangles/voxels.

For a local mesh/voxel fallback, the proposed reconciliation order for RCS-013 is:

1. preserve the original semantic operation/envelope and neighboring analytic boundary identities outside the fallback;
2. isolate the smallest region whose topology cannot be committed robustly;
3. perform material-set work in the fallback with an explicit spatial error bound;
4. recover exact known boundaries from provenance first;
5. fit only genuinely unknown residual surfaces, with measured deviation;
6. stitch/reconcile to B-rep;
7. run RCS-005 pre-export, serialized, read-back and interoperability gates;
8. refuse export if reconstruction cannot satisfy the declared budget.

This is deliberately different from "convert the whole workpiece to mesh/voxels and hope to reverse-engineer it later."

## Provenance and semantic identity

RCS-008 established that programme identity cannot depend on topology object identity. Alternative representations strengthen that conclusion: cells, voxels, triangle faces and regenerated B-rep faces will all have different local identity systems.

**INFERENCE:** fallback state should attach to semantic material/body/operation/boundary roles through programme-owned lineage. Backend-specific cell/voxel/triangle IDs are diagnostic implementation details only.

Manifold's source/property mapping may be useful evidence during local reconstruction, but it does not replace the programme lineage model.

## Determinism

**MEASURED:** both executable candidates produced identical engineering signatures on both repeats for every case.

This is intentionally a weaker invariant than byte identity. Runtime and process memory are excluded from the signature; material volume, body count, representation facts and reconciliation class are included.

## Negative results and rejected interpretations

- **REJECTED:** "guaranteed manifold mesh means the project is solved." It does not satisfy analytic STEP obligations by itself.
- **REJECTED:** "voxel/SDF robustness means resolution can be chosen for convenience." The 1 µm plunge/cusp measurements show direct semantic loss when resolution is too coarse.
- **REJECTED:** "exact predicates solve the architecture." Exact arithmetic can improve classification but does not supply manufacturing identity, process semantics, operation scaling or STEP policy.
- **REJECTED for initial direct dependency:** CGAL Nef_3 as the default production core. Its set model is highly relevant, but GPL-3+ package licensing plus polyhedral-to-analytic reconciliation cost make it an experiment/prior-art input rather than the default foundation at Gate 2.
- **DEFERRED:** full Manifold/OpenVDB integration benchmark. The issue acceptance criterion requires two non-OCCT executable approaches, which the programme-owned cell and voxel prototypes provide. External-library integration should be justified by RCS-013's selected fallback architecture rather than added speculatively.

## Recommendation to RCS-013

RCS-012 recommends a **hybrid representation architecture**, not a wholesale non-B-rep replacement:

1. preserve canonical manufacturing journal, semantic lineage and known analytic/process geometry independently of any representation;
2. use specialized analytic/process solvers where RCS-010/RCS-011 show they are strong;
3. allow bounded deferred/cell material state when committing conventional topology early would create avoidable fragility;
4. permit local mesh or sparse-volumetric fallback for pathological regions, with explicit error budgets and provenance links;
5. reconcile fallback regions to conventional B-rep only when needed for committed exact state/export or when another solver requires it;
6. never claim STEP success unless RCS-005 gates pass after reconciliation;
7. keep external fallback engines behind programme-owned contracts so Manifold/OpenVDB/CGAL experiments remain replaceable.

### Ideas to carry into architecture synthesis

- programme-owned representation-neutral material/body lineage;
- local fallback islands rather than whole-model discretization;
- deferred set/cell evaluation driven by unique physical boundaries rather than journal segmentation;
- explicit representation error budgets distinct from manufacturing/export tolerance;
- provenance-assisted analytic reconstruction before generic surface fitting;
- Manifold as a promising mesh-fallback implementation candidate;
- OpenVDB or a lighter sparse-grid structure as a promising volumetric-fallback implementation candidate;
- exact-predicate components where measurements show floating classification is causal.

### Ideas rejected or deferred

- global mesh-only authoritative state: rejected for founding architecture;
- global voxel/SDF-only authoritative state: rejected for founding architecture;
- direct Nef_3 production dependency: deferred due license/domain/reconstruction cost;
- universal exact-arithmetic rewrite: deferred; target exactness at measured numerical failure seams instead.

## Remaining open questions

- What smallest local region boundary allows reliable fallback-to-B-rep stitching without propagating tolerance inflation?
- How well can provenance recover cylinders/cones after mesh/SDF fallback versus generic fitting?
- What adaptive grid policy is sufficient for sub-micron-to-large-part scale without pathological memory growth?
- Does Manifold materially outperform the OCCT fallback cases that actually fail once tested on the shared harness?
- Which exact-predicate seams provide enough robustness leverage to justify CGAL or programme-owned exact arithmetic?
- Should fallback execution be process-isolated together with OCCT; RCS-017 remains the dedicated concurrency/global-state investigation.

These are architecture inputs/follow-up measurements, not reasons to disguise the demonstrated hybrid escape routes as solved production code.
