# MC-029 — Sparse volume/level-set candidate falsification

Status: **NEGATIVE_RESULT** as total MC-1 material/engineering-output authority; retained only as a bounded derived accelerator/challenger behind independent source/material certification.  
Issue: #91.  
Source baseline: `4f99c99b524049a9e288416f6329e2b14badaded`.  
Evidence class: dependency-bound deterministic exact-rational controls + reviewed representation argument.  
Native/paid execution: **none**.

## Question and falsification criterion

MC-029 evaluates finite sparse sampled volumes and narrow-band level-set representations under explicit resolution, refinement, resampling and extraction contracts. It does not redo MC-025's adaptive-event/termination investigation or MC-028's triangle-mesh representation result.

The strong hypothesis is that finite sparse sampled/level-set state can be the **sole authoritative material and engineering-output representation** for every admitted operation. The hypothesis is falsified if sub-cell positive material, exact-zero contact, topology or source-faithful boundaries remain unresolved unless an independent exact or outward-certified relation is retained.

That total-authority role is **falsified**. Sparse volumes remain useful when treated as derived state with explicit uncertainty and non-cycling failure dispatch.

## Dependency and deduplication boundary

The contract pins accepted outputs from MC-010, MC-016, MC-018, MC-019 and MC-020. Actual sweep meaning is inherited from MC-018/019/020; MC-029 does not reconstruct source motion from voxels. MC-025 already established that adaptivity does not create an exact equality oracle; that proof blocker is not relitigated here. MC-028 already establishes that an extracted finite triangle mesh cannot silently become exact material or STEP authority.

## Decisive sub-cell positive-material control

Consider one sampled cell `[0,1/1000]` with samples only at its end nodes. A positive material feature `[499/1000000,501/1000000]` has exact width **1/500000** and lies strictly between those nodes. The node membership vector is `[false,false]` both with and without that feature.

Therefore finite node signs do not determine sub-cell positive material or topology. A rule such as “all corners have the same sign, therefore the cell is uniform” is unsound unless another certified relation proves uniformity. Increasing resolution may eventually sample a particular feature, but a finite pitch by itself is not a universal exactness certificate and cannot authorize deletion of positive material smaller than the pitch.

## Resolution, refinement and error contract

Every retained level-set/volume use must keep the full additive error budget explicit:

`e_total = e_source + e_sampling + e_resampling + e_extraction`

`e_source` is inherited from the source-faithful sweep/material relation and may never reset merely because a voxel grid is built. `e_sampling` covers reconstruction within represented cells. `e_resampling` covers interpolation/regridding or frame changes. `e_extraction` covers isosurface/mesh extraction or downstream conversion. Unknown or unjustified terms yield **UNCERTIFIED**, not success.

The exact control uses `1/1000000 + 1/2000000 + 1/4000000 + 1/4000000 = 1/500000`. A smaller requested pitch can reduce a justified sampling term, but it cannot erase the other terms or certify discrete topology.

## Boundary and exact-zero controls

For stock `[0,1]`:

- sweep `[1,2]` is exact tangency with zero positive overlap;
- sweep `[999999/1000000,2]` removes exactly `1/1000000` positive measure;
- sweep `[1000001/1000000,2]` is separated.

Band width, grid pitch, interpolation tolerance or extraction tolerance may not fuse these three states. A scalar Hausdorff/error envelope describes geometric uncertainty; it does not by itself authorize topology changes, positive-material deletion, or exact-zero healing.

## Topology, body and lineage boundary

Surface extraction success, connected voxel components, sparse-tree node IDs or component enumeration are not durable body identity or lineage authority. Discrete claims require an independent exact/certified topology witness tied to the canonical journal/body revision. The same rule applies to split/merge and exact-zero touch cases.

Extracted isosurfaces/meshes are likewise not primary engineering geometry. **STEP remains mandatory** under MC-016/MC-054; MC-029 does not close native STEP or independent-consumer blockers.

## Retained bounded role

Sparse volume/level-set methods remain eligible as bounded derived accelerators or challengers only when all of the following hold: the source-faithful sweep/material relation is independently qualified; all four error terms are explicit and conservative; unresolved positive-volume/exact-zero/topology cases fail closed; discrete topology/body claims use a separate witness; and primary STEP qualification remains external. Provider failure may dispatch once to another reviewed owner but may not cycle or weaken the original request.

## Retained blockers and capability state

Existing identities are propagated, not duplicated: **PB-007-03**, **RB-016-02**, **RB-016-03** and **RB-016-04** remain open. No native or paid campaign ran. MC-A remains `ACCEPTED`; **MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`**.

Protected historical `research/rcs-*` evidence, **source/audio/provenance**, canonical operation-journal authority, positive-volume semantics and durable body/lineage semantics are unchanged.

## Verification

```text
python3 research/machining-completeness/tasks/MC-029/verify.py --contract
python3 research/machining-completeness/tasks/MC-029/verify.py --self-test
python3 tools/mc_workflow.py verify MC-029
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The exact PR head must pass `mc1-static` before merge, and the merged SHA must pass the same workflow on `main` before issue #91 is closed.
