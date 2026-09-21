# MC-023 — Multi-setup composition contract

MC-023 fixes the semantic handoff between tool-sweep providers and multi-setup workpiece history. It does **not** select a production geometry kernel or claim MC-B.

## Common-frame rule

Each immutable setup records an explicit right-handed transform from setup-local coordinates into the durable common workpiece frame:

`p_common = R_setup * p_local + t_setup`.

Provider sweeps are transformed into that common frame before material intent is composed. The inverse is not interchangeable with the declared mapping, and transform composition order is semantic. The executable control model uses exact rational translations and proper signed-permutation rotations; general admitted transforms must use MC-058 exact/algebraic or outward-certified evaluation and otherwise fail closed as `UNCERTIFIED`.

## Re-clamp and machine transitions

A re-clamp or lathe↔mill transition is a non-cutting immutable journal event. It creates the next setup context without changing prior geometry, source operations, durable bodies, lineage, or accumulated uncertainty. Historical setup transforms are never edited in place.

Every subsequent cut binds both its exact input revision and durable target `body_id`. Backend topology identity, enumeration order, proximity, largest-body selection and “only body” guessing are forbidden. If a cut changes material connectivity, the existing DR-0008 rule applies: the committed result needs an explicit `material_body_transition`; ambiguity remains explicit rather than being guessed.

## Full-3D exact control

The MC-023 test composes a lathe-frame slab removal with a 90-degree reoriented mill-frame slab removal on one durable body while a second body is present. The mill-local box `[0,4]×[0,1]×[0,4]` maps exactly to common-frame `[3,4]×[0,4]×[0,4]`. Exact boundary equality and ±`1/1000000` signed neighbours are tested, as are transform round-trip, inverse-direction confusion, composition-order swap, reflection rejection, stale-revision rejection and unrelated-body preservation.

MC-058 error transfer remains monotone across every setup transition:

`e_total = e_inherited + e_translation + rho*e_rotation + e_tool`.

A re-clamp does not create a new zero-error origin.

## Scope boundary

MC-023 establishes bounded composition semantics, not native Boolean correctness, automatic connectivity reconstruction, universal provider event solving, STEP interoperability or scale. Provider-specific open blockers remain propagated. Historical source/audio/provenance and negative evidence are unchanged, and `MC-B` through `MC-F` plus `MC-1` remain `NOT_ESTABLISHED`.
