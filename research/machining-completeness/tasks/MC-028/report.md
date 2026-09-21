# MC-028 — Native mesh/Manifold Boolean candidate falsification

Status: **NEGATIVE_RESULT** as total MC-1 material/engineering-output authority; retained only as a bounded future native mesh Boolean challenger/derived provider behind independent certification.  
Issue: #90.  
Source baseline: `e21aa9fa45959ebc3a6f3a3a56fca26a4cb6af1f`.  
Evidence class: pinned upstream source inspection + dependency-bound exact-rational controls + reviewed representation argument.  
Native/paid execution: **none**.

## Question and falsification criterion

MC-028 asks whether a native triangle-mesh/Manifold Boolean route can become the authoritative material engine when its operands are independently qualified **actual cutter sweeps**, rather than the historical LevelSet sampling route.

The hypothesis under test is deliberately strong: a finite floating triangle-mesh Boolean provider is sufficient as the **sole** MC-1 material authority and engineering-output source for every admitted operation. It is falsified if a required source-faithful material distinction cannot be exact authoritative truth in that representation without an external certified relation, or if the representation cannot by itself satisfy the conventional primary engineering-output contract.

That strong role is **falsified**. This is not a claim that Manifold is a poor mesh Boolean library. It is a contract result: the programme requires exact/non-compensating material distinctions and conventional engineering output that a finite floating triangle boundary mesh, by itself, does not encode.

## Deduplication and dependency binding

No open MC-028 PR or branch existed at dispatch. The task consumes, without rewriting:

- **MC-010** — independent exact-rational controls;
- **MC-016** — engineering-output representability boundaries;
- **MC-018** — actual flat/corner-radius fixed-axis sweeps;
- **MC-019** — actual finite ball/round simultaneous-XYZ sweeps; and
- **MC-020** — actual form/nonconvex/accessible-undercut bounded sweeps.

The verifier imports and executes the producing MC-018/019/020 sweep modules directly. It does **not** build a candidate from LevelSet samples, centreline substitution, AABB/hull replacement, or a new task-local reinterpretation of source motion.

## Upstream source facts pinned for the candidate

The evaluated upstream candidate is `elalish/manifold` **v3.5.3**, tag commit `0edd9d54876f3135e431575214dd6d8a72866fee`. The release tarball SHA-256 is `9545a1c944280673553d0c97602def29f62afa4ade4b27ad1593bb13aa266218`.

Pinned v3.5.3 source establishes:

- `include/manifold/manifold.h` describes Manifold's internal representation as an oriented **2-manifold triangle mesh**, with MeshGL/MeshGL64 mesh I/O and a separate `LevelSet` constructor;
- `include/manifold/common.h` aliases ordinary `MeshGL` to single precision, `MeshGL64` to double precision, and uses double for core vectors/matrices; and
- `include/manifold/mesh.h` states that polygonal faces reconstructed from output triangles are planar within output tolerance, and that mesh tolerance may collapse edges shorter than tolerance and may be enlarged as floating-point error accumulates.

These are source facts, not extrapolated native measurements. They establish what kind of state the candidate stores. They do not claim a particular native Boolean failure on v3.5.3.

## Actual-sweep qualification control

The acceptance criterion requiring independently qualified sweeps is exercised before the candidate argument:

1. MC-018 supplies a finite flat cutter at exact boundary `x=1` and an exact outside neighbour `x=1000001/1000000`.
2. MC-019 supplies the curved ball-end nose. For a stationary unit-radius ball nose, `(3/5, 0, 1/5)` is exactly on the spherical boundary because `3^2/5^2 + (1/5-1)^2 = 1`. The signed Z-neighbours at `200001/1000000` and `199999/1000000` classify inside/outside respectively.
3. MC-020 supplies a nonconvex box-union form cutter whose central gap remains empty, plus an exact positive-width `1/1000000` cutter feature.

The source sweep is therefore independent of any downstream mesh approximation. Candidate Boolean success cannot redefine the operand.

## Decisive curved-boundary obstruction

The MC-019 control gives a minimal exact counterexample to “finite triangle mesh equals exact material”.

In the XZ section of the unit ball nose, consider the exact endpoints `(0,0)` and `(1,1)`. Their straight chord is `z=x`. The exact rational sphere point `(3/5,1/5)` satisfies

`x^2 + (z-1)^2 = 1`

but does **not** satisfy the chord equation because `1/5 != 3/5`.

This is not a tessellation-quality complaint. An open spherical patch has nonzero curvature; a finite union of planar triangle interiors cannot be identical to that patch. Refinement can reduce geometric error, but finite faceting remains an approximation unless a separate exact/certified surface/material relation owns correctness.

Therefore a Manifold-style finite triangle mesh can consume a certified approximation of the MC-019 sweep, but the mesh cannot silently become the exact canonical material truth for the curved source operation.

## Positive micro-material and tolerance boundary

MC-020's exact-rational box-union route proves a positive cutter/material width of exactly `1/1000000` before any mesh conversion. MC-1 treats positive material as non-compensating: it cannot be deleted merely because a downstream representation regards it as small.

The upstream MeshGL contract explicitly permits an edge shorter than tolerance to be collapsed, uses at least a bounding-box-derived baseline tolerance when creating a Manifold, and permits tolerance growth with accumulated floating-point error. Those behaviours are legitimate mesh-processing semantics, but they cannot be promoted into the programme's material predicate.

A mesh route may therefore be admitted only when an **external exact or outward-certified relation/error envelope** proves that all required positive material survives. “The mesh is manifold” or “the Boolean returned success” is not that certificate.

## Exact-zero contact boundary

The deterministic material control uses stock interval `[0,1]`.

- sweep `[1,2]`: exact tangency, positive overlap `0`;
- sweep `[999999/1000000,2]`: exact positive overlap `1/1000000`;
- sweep `[1000001/1000000,2]`: separated, positive overlap `0`.

A tolerance-based coincidence rule is not allowed to identify those three states. Exact-zero contact cannot be healed into a positive bridge, and the positive one-millionth case cannot be rounded away. Mesh epsilon/tolerance may be useful for robust mesh processing; it is not MC-1 correctness authority.

## Nonconvex bounded compatibility

The result is not “mesh Boolean is useless”. MC-020's box-union control deliberately includes separated cutter boxes with a central gap. The exact source class is polygonal and can be tessellated without inventing curved boundaries. A later native Manifold experiment may be valuable as a bounded Boolean challenger or acceleration provider for admitted cases.

That retained role is conditional. The independently qualified source sweep remains authoritative, mesh approximation/error is certified externally, unknown/tolerance-ambiguous cases fail closed, and no result is promoted from “mesh succeeded” to “canonical material proved”.

## Body, lineage and engineering-output boundary

Triangle components, Manifold decomposition results, OriginalIDs, face IDs, run ordering, or connectivity are not the programme's durable body identity or lineage authority. Those semantics remain journal-owned.

Likewise, a successful manifold mesh is not conventional primary engineering geometry. MC-016 already established that faceted/tessellated wrapping is not a STEP-success substitute. STEP remains mandatory primary output.

Existing blockers are propagated rather than duplicated or closed:

- **PB-007-03** — no universal finite exact source codec for every admitted arbitrary form/undercut cutter instance;
- **RB-016-02** — durable multi-body mapping and independent engineering-output preservation remain unqualified;
- **RB-016-03** — native STEP preservation of certified positive micro-material remains unqualified;
- **RB-016-04** — exact-zero/touching/singular engineering output remains unqualified without healing/fusion.

## Reviewed retained role

MC-028 therefore records this candidate disposition:

- **no:** finite floating triangle mesh as sole material authority;
- **no:** mesh validity/manifoldness as proof of MC-1 material correctness;
- **no:** tolerance/epsilon as authority for positive-volume or exact-zero distinctions;
- **no:** mesh components as durable body identity/lineage;
- **no:** mesh Boolean output as primary STEP or independent-consumer qualification;
- **yes, provisionally:** bounded derived/challenger native mesh Boolean provider after independently qualified actual sweeps and an external exact/certified material/error authority;
- **yes, provisionally:** acceleration/visualization/approximate material work where uncertainty remains explicit and failure dispatch is non-cycling.

No native v3.5.3 campaign was required to falsify the total-authority hypothesis because the mismatch is representational and source-contract-level. Any later native experiment must be separately permitted and can qualify implementation robustness/performance without rewriting this result.

## Capability state and protected semantics

No capability gate changes. MC-A remains `ACCEPTED`. **MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.**

Historical `research/rcs-*` evidence is unchanged. **source/audio/provenance** meaning, canonical operation-journal authority, positive-volume semantics, durable body/lineage semantics, and mandatory conventional STEP output are preserved.

## Verification

```text
python3 research/machining-completeness/tasks/MC-028/verify.py --contract
python3 research/machining-completeness/tasks/MC-028/verify.py --self-test
python3 tools/mc_workflow.py verify MC-028
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The exact PR head must pass `mc1-static` before merge. The merged SHA must then pass the same workflow on `main` before issue #90 may be closed as completed research.
