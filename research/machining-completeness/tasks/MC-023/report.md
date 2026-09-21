# MC-023 — Re-clamp, reorientation and multi-setup sweep composition

## Result

**COMPLETED_RESEARCH_BOUNDED_COMPOSITION_ESTABLISHED.** From source baseline `318f9173466c20116236167183d8524e076e34c0`, the task establishes and executable-checks the common-frame composition contract required to carry already-certified tool sweeps across immutable re-clamps, full-3D reorientation, and lathe↔mill setup transitions without rewriting source history or guessing material-body identity.

This is not a native Boolean/topology result and does not advance MC-B. No native or paid campaign was run.

## Hypothesis and falsification criterion

Hypothesis: a provider sweep expressed in its immutable setup-local frame can be composed with preceding/following operations by mapping it into one durable common workpiece frame, provided the operation binds the exact input revision and durable target `body_id`, transform direction/order/handedness are explicit, and MC-058 uncertainty is carried monotonically.

Falsify the route if changing frame convention changes the intended material membership; if an inverse or order-swapped transform is silently accepted; if a re-clamp mutates earlier geometry; if a stale revision or guessed body target is accepted; if one body’s sweep removes another body; or if any transition resets inherited uncertainty.

## Authority reconciled

The task consumes MC-005 capability acceptance, the MC-010 independent exact-control foundation, and the MC-058 curve/rigid-transform enclosure contract. It also preserves the already accepted journal/identity decisions: DR-0008 requires immutable single-parent revisions and explicit material-body transitions, while DR-0011 makes durable identity semantic lineage rather than backend topology identity.

MC-023 deliberately does not claim that its bounded box-union controls are the production material engine. Their role is to make transform and targeting semantics executable and falsifiable before downstream native material realization.

## Composition contract

For every active setup, local cutter/sweep coordinates map to the durable common workpiece frame as

`p_common = R_setup * p_local + t_setup`.

Transforms are immutable records. Composition uses declared parent-from-child order; substituting the inverse, swapping multiplication order, changing units, or introducing a reflection is a semantic error rather than an approximation choice. The executable exact controls use proper signed-permutation rotations plus rational translations so all transform predicates are exact; generic admitted transforms route through MC-058 exact/algebraic or outward-certified evaluation and otherwise remain `UNCERTIFIED`.

A re-clamp or machine transition is a non-cutting journal event. It creates the next immutable revision/setup context but does not reinterpret prior operations, alter material, rename bodies, or reset inherited error.

Every cut binds the exact input revision and durable target `body_id`. Backend solid order, current largest body, nearest geometry, or “only body” heuristics are forbidden target selectors. Unrelated durable bodies remain unchanged. If connectivity actually changes, DR-0008 requires an explicit `material_body_transition`; this bounded control does not invent split/merge topology and therefore cannot silently guess the transition.

## Exact and boundary controls

The executable model starts with two durable bodies. Body A is exact stock `[0,4]^3`; body B is a separate `[10,12]×[0,2]×[0,2]` stock. An identity-frame lathe control sweep removes A’s `x∈[0,1]` slab. A non-cutting reclamp then installs the proper 90-degree setup transform

`R = [[0,-1,0],[1,0,0],[0,0,1]], t=(4,0,0)`.

A mill-local sweep `[0,4]×[0,1]×[0,4]` consequently maps exactly to common-frame `[3,4]×[0,4]×[0,4]`. The test checks a retained centre probe, independently removed lathe and mill probes, and an unrelated body-B probe. Around the transformed `x=3` boundary, exact equality and ±`1/1000000` signed neighbours are checked independently. The exact transform round-trip is identity.

Adversarial controls make forward-vs-inverse mapping and transform-order swaps observably different, reject a determinant `-1` reflection, reject stale revision binding and missing target-body resolution, and verify that the reclamp itself changes no material. Binary floating-point/bool certifying scalars are rejected.

The MC-058 transfer remains exactly:

`e_total = e_inherited + e_translation + rho*e_rotation + e_tool`.

With `e_inherited=1/4000`, `e_translation=1/1000`, `rho=5`, `e_rotation=1/10000`, and `e_tool=1/2000`, the exact control gives `9/4000`. Re-clamp and machine transition cannot reset this channel.

## Lathe↔mill interpretation

The composition interface is provider-neutral: a producing lathe or mill task supplies a source-bound certified sweep in the current setup-local frame plus exact revision/body binding. MC-023 transforms that evidence into the common frame and composes material intent; it does not rewrite or reinterpret the producing operation. This supports lathe→mill and mill→lathe history composition as a semantic routing contract.

Provider limitations remain provider limitations. In particular, this task does not convert MC-021/MC-022 bounded constructor evidence into a universal capability claim and does not discharge MC-007 transcendental/coupled-event blockers.

## Protected semantics and open work

Historical source/audio/provenance evidence is unchanged. The canonical journal remains immutable; positive-volume material cannot be erased by a frame tolerance; durable body/lineage identity remains independent of topology IDs; negative research results remain intact.

Still open downstream: native Boolean/material realization, automatic connectivity/split detection and explicit body-transition realization, reconstruction/STEP/independent-consumer qualification, unresolved provider analytic-event blockers, and practical scale. `MC-B`, `MC-C`, `MC-D`, `MC-E`, `MC-F`, and `MC-1` remain `NOT_ESTABLISHED`.

## Verification

- `python3 research/machining-completeness/tasks/MC-023/verify.py --contract`
- `python3 research/machining-completeness/tasks/MC-023/verify.py --self-test`
- `python3 tools/mc_workflow.py verify MC-023`
- repository MC-1 static/adversarial CI, including zero-drift issue synchronization
