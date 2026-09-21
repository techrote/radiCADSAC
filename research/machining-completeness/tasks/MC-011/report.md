# MC-011 — Physical adversarial corpus F01–F04

## Disposition

`COMPLETED_RESEARCH` for fixture construction and deterministic oracle witnessing only. This task builds F01–F04 as new prospective MC-1 records; it does **not** establish a native geometry candidate, MC-B, or MC-1.

Base: `4dc3213b230d88ea662f16a19e14384dc6727979` (MC-055 merged).

## Hypothesis and falsification criterion

Hypothesis: the first four mandatory adversarial families can be specified as physically realizable fixed-axis milling histories with exact source values and at least one candidate-independent, deliberately discriminating oracle path per family.

Falsify the task if any family requires engaged teleportation, unheld material, an implicit/tolerance-defined feature, candidate output to set expected truth, a shared decisive candidate implementation, or if its boundary corruption is not distinguishable by the recorded oracle.

## Constructed families

- **F01 — Jittered crossing pocket.** One held body receives a self-crossing pocket path, an exact reverse near-retrace displaced by `1/1000 mm`, and an exact tangent boundary pass. The rational analytic oracle distinguishes the zero-overlap tangent from the `1/1000 mm` penetrating neighbour without epsilon authority.
- **F02 — Final thin web.** A stock-spanning fixed-axis slot is evaluated at tip heights `+1/1000000`, `0`, and `-1/1000000 mm`. The positive case retains a real bottom web and one component; exact zero changes connectivity to two retained bodies. MC-010's structurally separate cell-set oracle gives exact volume/component controls, while the MC-011 analytic path independently probes the sweep boundary.
- **F03 — Rounded XYZ remachining.** A finite spherical cutting region follows continuous segments that each change X, Y and Z, then exactly reverses and retraces them. Exact point-to-segment squared distance over rationals supplies tangent and signed-neighbour controls and detects a deliberately flattened-Z corruption.
- **F04 — Reoriented stock.** A top cut is followed by an explicit non-cutting re-clamp of the same durable body. The second setup uses an exact proper 90-degree rigid transform mapping machine +Z to common-frame +X. Top-only, side-only, overlap and survivor points make loss of the reorientation observable.

All expected truth is preregistered exact fixture mathematics. Historical RCS records are provenance/adversarial seeds only and were not rewritten or promoted.

## Oracle independence

`fixture_oracle.py` uses only `Fraction` plus basic exact vector/matrix arithmetic. It imports no RCS implementation and no candidate geometry. F02 additionally consumes the already-reviewed MC-010 exact cell oracle as a second path. The two paths share fixture literals and exact rational arithmetic, not decisive geometry code.

This is bounded control evidence, not a universal oracle. F01/F03/F04 deliberately use discriminating exact membership/metamorphic witnesses rather than claiming full exact material reconstruction. MC-015 still owns deeper checker/certificate and independence challenge.

## Physical-validity boundaries

Every engaged path is finite and continuous. Fixed-axis orientation is explicit per setup. Holder/approach clearance is recorded. F04's body is explicitly retained and re-clamped before side access; backend topology handles do not define identity. Positive-volume material is never removed by a tolerance rule, and the F02 zero threshold retains both disconnected bodies.

No native or paid campaign was executed. No production bootstrap is authorized.

## Registry and historical-verifier reconciliation

`fixture-families-v1.json` now marks F01–F04 `BUILT` and leaves F05–F16 `UNBUILT`. `BUILT` means the family record and its independent control path exist; it does not mean a candidate passed.

The programme validator now permits only `UNBUILT`/`BUILT` and rejects a `BUILT` family whose owner is still `NOT_STARTED`. MC-055's verifier was corrected so its historical statement (“none were built by MC-055”) remains frozen in the MC-055 artifact rather than incorrectly requiring the live future registry to stay forever `UNBUILT`.

## Adversarial verification

The task verifier rejects or detects:

- binary floating-point authority values;
- candidate-defined expected truth or a shared decisive RCS geometry import;
- loss of the F01 tangent/penetrating distinction or exact jitter amplitude;
- rounding F02's positive web to zero;
- loss of F02 component/volume threshold behaviour;
- flattening F03's simultaneous XYZ motion;
- loss of F03 exact retrace equivalence or signed spherical boundary;
- replacing F04's re-clamp rotation with identity;
- fixture-registry denominator/state drift;
- mutation of dependency artifacts or protected `research/rcs-*` sources.

## Remaining open work

F05–F16 remain unbuilt under MC-012 through MC-014. MC-015 retains the deeper oracle/certificate review. Native material/topology/reconstruction correctness, STEP engineering qualification, MC-B through MC-F, and MC-1 remain `NOT_ESTABLISHED`.
