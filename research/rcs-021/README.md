# RCS-021 — manual/freehand mill independent material oracle and bounded fallback

Status: executable research harness; acceptance depends on hosted measured evidence.  
Issue: RCS-021 / #40  
Date: 2026-09-17

## Purpose

RCS-021 closes the Genesis-v1 manual/freehand milling evidence gap exposed by RCS-011. A successful OCCT Boolean, a valid B-rep, or a watertight fallback mesh is not treated as proof that the correct material was removed. The campaign therefore separates physical truth from every candidate geometry representation.

The founding scope remains fixed-axis milling in the right-handed Z-up workpiece frame. It does not claim arbitrary five-axis cutter reorientation.

## Independent oracle

`material_oracle.py` evaluates the manufacturing path through the representation-neutral cutter field in `field.py`. For the flat-end tool the field is the union of swept vertical cutter columns; simultaneous XYZ motion is evaluated by a monotone field-level feasibility solve rather than by replaying OCCT Booleans. The rounded fixture uses a vertical-axis ball-nose lower hemisphere plus the cutter body above it.

The oracle uses a conservative adaptive octree. The cutter field is constructed as a maximum of 1-Lipschitz segment fields, so at a cell centre `c` with half diagonal `d`:

- `f(c) > d` certifies the complete cell is removed;
- `f(c) < -d` certifies the complete cell remains material;
- otherwise the cell is subdivided, or contributes a conservative interval at the configured depth.

This produces an explicit lower/upper final-material volume interval and a boundary spatial half-diagonal. The oracle is independent of OCCT, Manifold and the directional material candidate.

Closed-form controls cover a stationary flat cutter, a straight stadium slot, zero-volume tangency, a pure positive plunge and a full through-strip producing two material bodies. A known result must lie inside the oracle interval before the campaign can pass.

## Tri-dexel / directional material candidate

`tridexel.py` measures a machining-native directional interval representation. The candidate retains analytic Z-column heights over an XY sampling lattice and derives X/Y/Z material-interval counts from the same remaining-material field. It records:

- a material volume estimate plus conservative lower/upper bounds;
- an XY spatial support radius tied directly to pitch;
- disconnected body count;
- directional interval/representation complexity;
- deterministic engineering signature;
- runtime and peak RSS;
- an explicit `requires_brep_before_step` reconciliation class.

Resolution is a representation error channel, not a manufacturing tolerance. Refinement runs are retained for decisive cases. A positive 1 µm plunge may not be snapped away merely because the directional field or mesh resolution is coarser; it must remain present through analytic evidence or the candidate must refuse authoritative use.

## Manifold external comparator

`manifold_fallback.py` executes the maintained Manifold 3.5.3 Python package, pinned to source commit `0edd9d54876f3135e431575214dd6d8a72866fee`. It evaluates the same programme-owned final-material field through `Manifold.level_set` with explicit edge-length and requested root-tolerance controls.

The Manifold result is deliberately a comparator, not STEP-authoritative state. It records volume, surface area, body count, mesh complexity, status and reported tolerance. Features below the declared external resolution policy are classified `refused_resolution_budget` even though the mesh diagnostic is still executed. Any future engineering use must recover retained analytic boundaries/provenance, reconcile to conventional B-rep, then pass RCS-005.

## RCS-011 revisit

When supplied the pinned `rcs011_mill_worker`, `run_campaign.py` directly reruns:

- `retrace-jitter` with sequential `segment_sweep` and one-shot `freehand_batch`, comparing both volumes with the independent oracle interval;
- `slot-clean` with the old dense `sampled_fallback` under a strict process timeout.

The required regression behavior is stronger than checking kernel status: the exact sequential retrace must agree with the independent material truth while the previously valid-but-wrong one-shot batch must be rejected by that truth. The sampled fallback must terminate with an explicit bounded success/error/timeout classification rather than being allowed to monopolize the campaign.

## Fixture coverage

The committed profile includes self-crossing motion, exact and jittered retrace, simultaneous XYZ, flat-end and rounded/ball-nose tools, tangent and near-tangent entry, positive 1 µm removal, overlapping paths, two-body cut-through, 160-segment freehand motion, and stationary/near-stationary engagement. The 160-segment fixture is deliberately larger than the 50-segment RCS-011 smoke case.

## Reproduction

Static contracts:

```bash
python3 tools/validate_rcs021.py
python3 -m py_compile research/rcs-021/*.py
```

Representation-only campaign with the pinned external package:

```bash
python3 -m pip install --disable-pip-version-check manifold3d==3.5.3
python3 research/rcs-021/run_campaign.py \
  --profile ci \
  --out-dir .results/rcs021-material
python3 tools/validate_rcs021.py --results-dir .results/rcs021-material
```

Full hosted comparison after building the accepted RCS-011 worker against pinned OCCT 8.0.1:

```bash
export LD_LIBRARY_PATH="$RCS006_OCCT_PREFIX/lib:$RCS006_OCCT_PREFIX/lib64:${LD_LIBRARY_PATH:-}"
python3 research/rcs-021/run_campaign.py \
  --profile ci \
  --rcs011-worker .build/rcs011/rcs011_mill_worker \
  --out-dir .results/rcs021
python3 tools/validate_rcs021.py --results-dir .results/rcs021
```

The dedicated GitHub Actions workflow performs both passes and uploads the full result directory. Hosted run/artifact identity is frozen into `measured-summary-v1.json` only after the measured gates pass; no local or predicted values are promoted to evidence.
