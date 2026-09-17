# DR-0014 — Bounded hybrid representation fallbacks preserve analytic semantics

Status: accepted  
Date: 2026-09-17  
Decision scope: initial representation/fallback policy input to RCS-013

## Context

The programme must treat coincidence, tangency, sub-tolerance cuts, slivers, retraces, self-crossing motion and high operation counts as normal manufacturing inputs while still producing conventional usable STEP B-rep geometry.

RCS-009 established value in regularized material semantics and bounded topology deferral. RCS-010/RCS-011 established that process-specialized analytic strategies can outperform indiscriminate generic Boolean replay in important lathe/mill subsets. RCS-012 tested two non-OCCT material representations and reviewed current exact, mesh and sparse-volumetric alternatives.

The architecture therefore needs an explicit rule for when a non-B-rep representation may participate without becoming a silent lossy replacement for engineering state.

## Decision

The programme accepts **bounded hybrid representation fallbacks** as an architecture input for Gate 2.

Fixed rules:

- The canonical journal, semantic material/body lineage and known analytic/process geometry remain representation-independent programme state.
- No triangle-mesh, voxel/SDF or other discretized representation becomes the default authoritative whole-workpiece engineering state merely because it is robust or watertight.
- A difficult local region may be evaluated in a cell, deferred-set, mesh, voxel/SDF or other fallback when its representation error and semantic scope are explicit.
- Known analytic boundaries must be retained through provenance/semantics where possible rather than discarded and reverse-engineered later.
- Backend-specific cell, voxel, triangle or regenerated B-rep identity is not durable programme identity.
- Reconciliation must preferentially recover known analytic boundaries from provenance before fitting genuinely unknown residual geometry.
- Any discretized fallback has an explicit spatial/error budget distinct from manufacturing tolerance, numerical uncertainty and STEP export tolerance.
- Before a fallback-derived result may be called successful engineering output, it must reconcile to conventional B-rep and satisfy the accepted RCS-005 STEP conformance gates. If it cannot, export is refused rather than silently degraded.
- External candidate engines remain behind programme-owned contracts and are replaceable. RCS-012 does not select Manifold, OpenVDB, CGAL or another library as a mandatory production dependency.

## Alternatives considered

### Whole-model mesh-authoritative kernel

Rejected for the founding architecture. Robust manifold mesh operations are valuable, but triangle meshes do not natively preserve the analytic planes/cylinders/cones and conventional exact engineering representation required by the STEP contract.

### Whole-model voxel/SDF-authoritative kernel

Rejected for the founding architecture. RCS-012 measured direct semantic loss when a 0.5 mm occupancy representation encountered a 0.001 mm plunge and a 0.001 mm positive-volume cusp. Resolution therefore cannot be hidden or chosen solely for performance.

### Exact arithmetic everywhere

Deferred. Exact predicates/constructions can remove a class of numerical ambiguity, but they do not themselves provide manufacturing semantics, provenance, operation-count scaling, topology policy or STEP reconciliation. Targeted exact components remain candidates where measured failures justify them.

### CGAL Nef_3 as the default core

Deferred. Its set-closed polyhedral model is relevant prior art, but CGAL 6.2.1 records the Nef_3 package as GPL v3-or-later, and the representation still requires analytic B-rep reconstruction for the programme's STEP output. Both are material architecture costs.

### B-rep only, with no alternative escape route

Rejected as an architecture constraint. The accepted programme invariants explicitly permit unconventional internal representations, and RCS-009/RCS-011 already expose cases where early/conventional topology commitment or dense generic replay is an avoidable robustness/performance liability.

## Evidence

### Measured RCS-012 evidence

The deterministic RCS-012 campaign exercised eight shared physical-oracle cases with two non-OCCT candidates over two repeats each.

The exact orthogonal-cell/deferred-set prototype matched all 16 volume attempts and all 16 body-count attempts exactly within its bounded axis-aligned subset, including lower-dimensional contact and a two-body through cut.

The 0.5 mm sparse occupancy prototype remained deterministic and represented the aligned through-cut correctly, but it missed a real 0.001 mm plunge (0.1 mm³ removal) and erased a complete 0.001 mm positive-volume cusp (0.2 mm³), changing that case from one body to no represented material.

A 100000-operation exact-retrace proxy reduced to one unique removal envelope for material evaluation while retaining the raw operation count, demonstrating that material-evaluation complexity need not scale identically with durable journal history when equivalence is proven.

### Sourced evidence

Current pinned source review for RCS-012 records:

- CGAL 6.2.1 (`v6.2.1`, published 2026-09-04): `Kernel_23` LGPL v3-or-later; `Nef_3` GPL v3-or-later;
- Manifold 3.5.3 (`v3.5.3`, published 2026-09-07): Apache-2.0; upstream targets guaranteed-manifold triangle-mesh output and robust mesh Booleans;
- OpenVDB 13.1.0 (`v13.1.0`, published 2026-09-16): Apache-2.0; sparse hierarchical volumetric grid/tool infrastructure.

Full source links and interpretation are in `docs/19-ALTERNATIVE-HYBRID-GEOMETRY-REPRESENTATIONS.md`.

## Consequences

- RCS-013 may define local fallback islands without committing the complete workpiece to one representation.
- The architecture needs explicit representation/error metadata and a dispatch/reconciliation boundary.
- Provenance from RCS-008 becomes an active reconstruction asset, not only audit history.
- RCS-005 remains the final authority for whether reconciled geometry can be exported successfully.
- Manifold and sparse-grid/OpenVDB-style techniques are credible implementation candidates for local fallbacks, but production adoption requires a workload-specific benchmark rather than this decision alone.
- Exact-predicate libraries or programme-owned exact arithmetic should be introduced at measured failure seams rather than as a blanket rewrite.

## Reversibility

High before production handoff. The rule deliberately preserves backend replaceability and does not fix a concrete fallback library. Reversibility becomes lower if saved project meaning ever starts depending on backend-specific fallback topology; this decision explicitly prohibits that dependency.

## Reconsideration trigger

Reconsider the scope of bounded fallbacks if later measurements show one alternative representation can satisfy pathological material semantics, analytic preservation/recovery, performance, licensing and RCS-005 STEP conformance across the full initial lathe/mill workload with lower total complexity than the hybrid approach.

Conversely, narrow a fallback implementation if its reconstruction error, integration cost, licensing or runtime cannot satisfy the Gate-2 architecture constraints.
