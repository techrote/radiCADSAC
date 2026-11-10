# B5 — Applied-policy custody falsifier across B3→B2

**Date:** 2026-11-10. **Status:** RESEARCH REVIEW / HOLD; no production or MC-038 gate admission.

## Exact baseline and ownership

- radiCADSAC accepted main: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; B5 Draft [#472](https://github.com/techrote/radiCADSAC/pull/472), initial reviewed head `8200c6c086d27e0d51381f1b1779383696b1e50e`.
- CyberSand accepted main: `d4b18e7f06839b35c8f6a66195206da0f33c5fa3`.
- B3 Draft [CyberSand #555](https://github.com/techrote/cybersand/pull/555) exact head `aedb37ab671888a2c9914ad01d8c33c330cbc3f1`, [model source](https://github.com/techrote/cybersand/blob/aedb37ab671888a2c9914ad01d8c33c330cbc3f1/research/solver-certificates/handoff/handoff_contract.py) Git blob `523810bee1d9b219a421557181ecae108d222ef2`.
- B2 [#556](https://github.com/techrote/cybersand/pull/556) head `571c9626d435bd4d68fa472b770968e28f836042`; B4 [#554](https://github.com/techrote/cybersand/pull/554) head `23742c8c293c5ea7f9c05fd9fa5cb6a12f445eaf`. B1 [radiCADSAC #473](https://github.com/techrote/radiCADSAC/pull/473) head `27b146d9fae4e7dd406eb443bb221af2d1962882`; A1/A2 [#470](https://github.com/techrote/radiCADSAC/pull/470)/[#471](https://github.com/techrote/radiCADSAC/pull/471) heads `3d7238bc`/`bce8bde5`.
- Authorized write set: ONLY `research/experimental/ab-campaign/integration/**` in radiCADSAC. This review does not modify any author's branch or CyberSand production source.

Current authority [handoffs/current-authority.json](https://github.com/techrote/radiCADSAC/blob/main/handoffs/current-authority.json): MC-1 `NOT_ESTABLISHED`, `production_authorized=false`. MC-B is likewise `NOT_ESTABLISHED`; retain frozen 121/20/30/50 original census and 26 machining operations. CyberSand default Water `freemass_v1`, native authoritative World, worker fence, Rapier main-thread authority, MAT-AUTH and physical-hash/saved-state policy unchanged.

## Preregistered falsifier and six source-pinned structural checks

**Hypothesis:** B3's `World.signed_inertial_world_enabled` is described as a World-construction immutable applied-law option, but the research model may permit unversioned mutation of this field between `prepare` and `commit`. If so, the *same* prepared negative-vertical IN intent that an unsigned World rejected can commit without a fresh authenticated policy receipt, generation, source revision or epoch.

At the pinned model blob, all six independently inspected source predicates are true:

1. `World` is an ordinary mutable `@dataclass`, with `signed_inertial_world_enabled: bool = False`, not a frozen policy field.
2. `World.start` admits an explicitly unsigned World with valid FreeMass seed.
3. `prepare` pins generation, epoch, source record signature and request fields, but not the applied World-policy identity.
4. `commit` checks `not w.signed_inertial_world_enabled` from the **live mutable field** in its unsigned-upward refusal.
5. `World.assert_invariants` checks seeded IN against the **current** boolean; it does not prove that the boolean is the originally applied policy.
6. `material_identity` includes the boolean and therefore *would detect a change if independently checked*, but `commit` does not compare that full identity to a prepare-time witness.

Construct `World.start(3, [Record("water", Owner.FREE_MASS, 256)], signed_inertial_world_enabled=False)`; prepare `water → IN`, amount 256, velocity `(0,-8)`, `allow_signed_inertial=True`. First `commit(fenced=True)` refuses `UNSIGNED_UPWARD`. Set `w.signed_inertial_world_enabled=True` directly, without advancing epoch or source revision. The second identical `commit(fenced=True)` reaches the candidate commit path, and the current invariant predicate approves the new IN state. **Predicted source-level result:** model `COMMITTED`, not a native-policy-authenticated admission.

The accompanying [exact Git-blob-pinned executable challenge](policy_mutation_probe.py) refuses a different Python source blob; it exercises this negative control and an ordinary genuinely signed-World positive control. Run against an actual checkout of B3's pinned head:

```sh
python3 research/experimental/ab-campaign/integration/policy_mutation_probe.py /path/to/cybersand/research/solver-certificates/handoff/handoff_contract.py
```

**Qualification distinction:** six source predicates were checked against the published exact blob. This report does **not** claim that the complete pinned Python module/checker was executed in this session; the predicted runtime result remains for independent literal-head replay. No native runtime, actual worker, physical hash or benchmark was executed.

## Proof boundary and precise correction request

This is a **research-model custody gap**, not a counterexample to the *conditional* induction theorem that assumes all mutations are admitted transactions; direct external dataclass assignment is outside that theorem. It does show that a self-reported field cannot itself establish the *trusted and immutable applied-policy* premise for a prospective consumer. Source-value snapshots are not source authority, and value equality is not a monotone ABA witness.

Require one of two explicit outcomes:

- **Tighten model:** an immutable, trusted construction/restore policy receipt bound to World generation and the prepared request; `commit` refuses if the applied policy witness is absent/stale or disagrees. No public mutable model field should silently grant extra physics permission.
- **Narrow claim:** state that an externally trusted World owner exclusively controls policy fields, and all direct mutation is out of scope. Consumers must obtain an independent native applied-policy receipt rather than trusting a B3 model boolean or a caller-supplied hash.

A good independent regression has (a) unsigned negative-IN refusal, (b) unversioned False→True policy-flip refusal **without** mutating source/epoch, (c) legitimate signed negative-IN acceptance, (d) policy rollback/restore invalidating old prepared intents, and (e) B2 `UNKNOWN→RECOMPUTE` whenever applied policy provenance or worker fence is missing. The trusted receipt belongs at an owner barrier, **not** a hot per-cell check.

B2's immutable packet witness addresses accepted effects, not this policy authority; B1's source-hash certificate cannot prove a mutable external producer's policy either. The cross-lane common seam is **a complete custody chain across proof, current owner and full dynamic dependencies**. No B2/B3 same-law native tick gains are established.

## Bounded discovery matrix, comparison to baseline

| Lane | Bounded scientific contribution | Independent status and falsifier | Net newly demonstrated production gain |
|---|---|---|---|
| A1 | Restricted algebraic-time zero-order oracle; classical Gelfond–Schneider/Sturm tools | A3 finds modular-irreducibility witness *incompleteness* on translated `u⁴−10u²+1`; correct refusal; global isolator still HOLD | 0 new MC-038 classes |
| A2 | Rational-phase cyclotomic jets, sided knots, local product valuation; classical analytic/ODE facts | A3 input-size parser corrections; 4/3 vs 3/4 exact knot challenge still needs literal-head replay | 0 |
| B1 | Bernstein cone, closed-nonzero endpoints, split/affine/journal; standard Bernstein/de Casteljau | Necessary endpoint witness repaired B5's strict-positive composition counterexample; original producer custody still HOLD | 0 |
| B2 | Bounded fixed-point skip and frozen worker-effect/epoch model | False locality under remote gas/actor, high-churn negative abstract cost (3.089× retained from prior model); native whole-state parity unverified | 0 |
| B3 | Typed Water handoff and exclusive owner/quantity model | Signed-IN seed correction plus **new current-policy mutability witness** here; no native producer/restore receipt | 0 |
| B4 | Historical #470 same-host ABBA collider-packet reanalysis | Narrow packet-stage p50 reductions 94.41%/94.07%; no-packet negative control and missing worker/hash evidence prohibit global attribution | No new A/B native gain |
| B5 | Dependency completeness, nonzero closure, authority seams | This conditional policy-custody falsifier; code authored, source-static checks 6/6; exact module execution pending | 0 |

**GO:** review and replay the exact-source negative control; **HOLD:** source-typed native consumption, generalized proof composition and speed/physical correctness claims. No research merge yet qualifies; generic hosted successes are not dedicated proof-module execution.

## Handoff and STOP

Request B3 and independent B4 to execute the pinned challenger and classify its result as either current-source reproduced or falsified; then explicitly bind future signed-policy admission to trusted owner provenance or narrow the theorem premise. B2 should refuse reuse on unknown applied-policy/rollback dependencies. B5 should not keep expanding theorem variants absent a new verified producer boundary. STOP after this bounded research review; no production or MC gate changes.
