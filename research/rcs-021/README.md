# RCS-021 — manual/freehand mill independent material oracle and bounded fallback

Status: **accepted measured research; merge pending**  
Issue: RCS-021 / #40  
Date: 2026-09-17  
Frozen evidence: workflow `35280105714`, full artifact `10522213307`, SHA-256 `bbdf14b8474753393d98d42babb94fee7c7309fed9a6a38c93962b289db391ba`.

## Purpose

RCS-021 closes the Genesis-v1 manual/freehand milling evidence gap exposed by RCS-011. A successful OCCT Boolean, valid B-rep, or watertight fallback mesh is not treated as proof that the correct material was removed. Physical material truth is evaluated independently of every candidate geometry representation.

The founding scope is fixed-axis milling in the right-handed Z-up workpiece frame. Flat-end simultaneous XYZ is measured. Rounded/ball-nose evidence is limited to the committed constant-Z fixture; arbitrary tool-axis rotation/five-axis motion is not qualified.

## Independent oracle

`material_oracle.py` evaluates the manufacturing path through the representation-neutral cutter field in `field.py`. A conservative adaptive octree uses the 1-Lipschitz field plus each cell half diagonal to certify whole-cell material/removal or retain an explicit uncertainty interval.

Closed-form controls cover stationary cylindrical removal, a straight stadium slot, exact tangency, positive `1 um` plunge, and a stock-spanning through strip producing two bodies. All five were contained by the hosted independent oracle.

The live RCS-011 revisit is decisive: sequential `retrace-jitter` produced `11490.990137750125 mm3` and was inside the oracle interval; one-shot `freehand_batch` produced a valid one-solid `12000.000000001159 mm3` result outside the oracle interval.

## Tri-dexel / directional candidate

`tridexel.py` measures a machining-native directional interval representation with analytic Z-column heights. It records material-volume estimate and bounds, XY spatial support, disconnected body count, X/Y/Z interval complexity, deterministic engineering signature, runtime/RSS, and `bounded_directional_material_state_requires_brep_before_step`.

At `0.5 mm` pitch, five of fourteen fixtures close the founding `150 mm3` material-interval and `0.4 mm` spatial-support budgets; nine remain `accepted_pending_refinement`. Measured `0.25 mm` refinement closes the volume budget for `retrace-jitter` and `ball-rounded`, but not for `simultaneous-xyz` or `cut-through`.

The positive `1 um` plunge remains positive; the through-cut retains two material bodies. Resolution is representation error, not permission to erase manufacturing intent.

## Manifold external comparator

`manifold_fallback.py` executes pinned Manifold 3.5.3 at source commit `0edd9d54876f3135e431575214dd6d8a72866fee`. Thirteen fixtures executed; every executed result lay inside the independent material interval and matched expected body count.

The `1 um` plunge is correctly `refused_resolution_budget` for external authoritative use. The 160-segment fixture is explicitly `external_resource_bound_not_executed` because the Python LevelSet callback would duplicate the scaling experiment at disproportionate CI cost.

Manifold remains a comparator, not STEP-authoritative state. Any future engineering use must recover retained analytic boundaries/provenance, reconcile to conventional B-rep, then pass RCS-005.

## RCS-011 bounded revisit

`run_campaign.py --rcs011-worker ...` reruns:

- `retrace-jitter` with sequential `segment_sweep` and one-shot `freehand_batch`, both compared to the independent oracle;
- `slot-clean` with the old dense `sampled_fallback` under a strict `10 s` process bound.

The accepted run independently reproduced the valid-but-wrong one-shot retrace and again contained the sampled fallback as `hang/timeout`.

## Reproduction

Static contracts:

```bash
python3 tools/validate_rcs021.py
python3 -m py_compile research/rcs-021/*.py
```

Representation campaign:

```bash
python3 -m pip install --disable-pip-version-check --only-binary=:all: manifold3d==3.5.3
python3 research/rcs-021/run_campaign.py \
  --profile ci \
  --repeats 2 \
  --out-dir .results/rcs021-material
python3 tools/validate_rcs021.py --results-dir .results/rcs021-material
```

Full hosted comparison after building the accepted RCS-011 worker against pinned OCCT 8.0.1:

```bash
export LD_LIBRARY_PATH="$RCS006_OCCT_PREFIX/lib:$RCS006_OCCT_PREFIX/lib64:${LD_LIBRARY_PATH:-}"
python3 research/rcs-021/run_campaign.py \
  --profile ci \
  --repeats 2 \
  --rcs011-worker .build/rcs011/rcs011_mill_worker \
  --out-dir .results/rcs021
python3 tools/validate_rcs021.py --results-dir .results/rcs021
```

`measured-summary-v1.json` freezes the accepted run identity, artifact digests, representative metrics and deliberately narrowed capability recommendation.
