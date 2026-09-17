# RCS-012 alternative and hybrid geometry campaign

Status: research artifact for RCS-012  
Date: 2026-09-17  
Runtime schema: `rcs-012-result/1.0`

## Purpose

This campaign asks where non-OCCT representations can improve robustness without weakening the programme requirement that successful export resolves to conventional usable STEP B-rep geometry.

The experiment deliberately does **not** attempt to replace the complete geometry kernel. It compares two non-OCCT material-set representations on shared RCS-003 physical oracles and combines those measurements with pinned primary-source review of CGAL, Manifold and OpenVDB.

## Reproduce

No third-party runtime dependency is required for the two executable candidates:

```bash
python3 research/rcs-012/harness/run_campaign.py \
  --out-dir .results/rcs012 \
  --repeats 2
python3 tools/validate_rcs012.py --results-dir .results/rcs012
```

The campaign writes `results.jsonl`, `summary.json`, and `summary.md`.

## Executed candidates

### Exact orthogonal cell + deferred CSG

The first prototype stores stock and subtractive envelopes as decimal-valued analytic axis-aligned boxes. Exact duplicate envelopes are canonicalized for evaluation while the raw operation count remains recorded. Material is evaluated by an orthogonal decomposition induced by every unique boundary plane.

Within this deliberately bounded subset this gives exact volume, explicit disconnected-body topology, exact lower-dimensional contact semantics, and zero representation error. It is evidence for **cell/deferred-set ideas**, not a claim that an axis-aligned box evaluator solves arbitrary machining.

### Sparse 0.5 mm occupancy

The second prototype classifies deterministic 0.5 mm cubic cell centres. It is intentionally coarse so the resolution cost of voxel/SDF-style fallback is measurable rather than hidden.

It preserves robust coarse occupancy and obvious through-cut separation, but it loses analytic surface classes unless those are retained separately and it cannot represent features below its sampling scale reliably.

## Shared fixtures

`experiment-plan-v1.json` contains eight bounded proxies tied to RCS-003 source families:

- lower-dimensional contact;
- sub-tolerance plunge;
- repeated identical slot;
- overlapping slots/pockets;
- cut-through separation;
- tiny positive-volume cusp;
- very high segment/operation count with equivalent envelope;
- tangent corner contact.

The proxies preserve each cited physical oracle while intentionally narrowing geometry to the smallest domain needed for a representation comparison.

## Measured headline

Two repeats across eight cases produced 16 attempts per candidate. The exact cell/deferred candidate matched all volume and body-count oracles with stable engineering signatures. The 0.5 mm occupancy candidate was deterministic but missed the 0.001 mm plunge entirely and erased the entire 0.001 mm cusp, changing that case from one positive-volume body to no represented material.

The committed reference is `measured-summary-v1.json`; CI reruns the campaign rather than trusting that file alone.

## Primary-source pins

Source review is pinned to versions current on 2026-09-17:

- CGAL 6.2.1, release `v6.2.1` (published 2026-09-04). `Kernel_23` records LGPL v3-or-later; `Nef_3` records GPL v3-or-later.
- Manifold 3.5.3, release `v3.5.3` (published 2026-09-07), Apache-2.0. Upstream describes guaranteed-manifold triangle-mesh output and a mesh Boolean intended to be robust to edge cases.
- OpenVDB 13.1.0, release `v13.1.0` (published 2026-09-16), Apache-2.0. Upstream defines the project as a sparse volumetric grid/data-structure and tool suite.

Pinned URLs and architecture interpretation are in `docs/19-ALTERNATIVE-HYBRID-GEOMETRY-REPRESENTATIONS.md`.

## Boundary

A watertight mesh or stable voxel set is not STEP conformance. Any non-B-rep fallback must carry an explicit error budget and a reconciliation path. Analytic/process/provenance information should be retained outside the fallback representation wherever possible so reconstruction does not have to infer facts the programme already knew.
