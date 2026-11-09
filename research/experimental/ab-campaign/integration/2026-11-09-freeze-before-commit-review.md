# B5 — Freeze-before-commit: a source-critical B2/B3/B1 composition falsifier

**Checkpoint:** 9 November 2026 · third B5 review · **Draft / HOLD**. This is a bounded independent *research-model contract* review, not a native CyberSand failure or a fresh geometry/root theorem. It supplements [the previous source-critical discovery matrix](2026-11-09-source-critical-scoreboard.md); do not silently replace that dated evidence with later heads.

## Authority, exact producing identities and scope

| Scope | Reviewed identity | Reconciliation |
| --- | --- | --- |
| radiCADSAC accepted main | `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9` | `AGENTS.md`, DR-0026, `handoffs/current-authority.json`, MC-1 protocol, MC-038 [#100](https://github.com/techrote/radiCADSAC/issues/100), [#324](https://github.com/techrote/radiCADSAC/issues/324); [#397](https://github.com/techrote/radiCADSAC/pull/397), [#453](https://github.com/techrote/radiCADSAC/pull/453), [#462](https://github.com/techrote/radiCADSAC/pull/462) retained as independently scoped prior work |
| CyberSand accepted main | `d4b18e7f06839b35c8f6a66195206da0f33c5fa3` | `AGENTS.md`, Water pressure optimization, LCB/pressure reference and the #470/#471/#522 accepted optimization boundaries; immutable native World and actual Rapier/worker ownership remain authoritative |
| A1 [#470](https://github.com/techrote/radiCADSAC/pull/470) | `858d3d9bc1f93af34054d64df306a6e9aafb3c0f` | Newly restricted signed H2 square-lift; 8 authored tests reported executed locally; A3 exact-head independent proof/source review still pending |
| A2 [#471](https://github.com/techrote/radiCADSAC/pull/471) | `3b6eaf70e1e7422b7ac8e8e9ff6f0fef85281978` | Pre-conversion knot bound repaired; A3 independently finds oversize direct `reversed_spline` control arrays; still HOLD for source contract |
| B1 [#473](https://github.com/techrote/radiCADSAC/pull/473) | `5d2ebcbf6293a289410de1cf123a1fb612e7529c` | New `producer_codec.py` checks A1/A2 JSON serializers against **external** SHA-256 source/window pins; does not execute/authenticate producing modules or independently own pin custody |
| B2 [CyberSand #556](https://github.com/techrote/cybersand/pull/556) | `90d87d4611ed09ae034b95f99fa7bc17125cff3e`; `sparse_fence.py` blob `f20d33ea7ec30be91107a0cdb3248b9358ee2b9c` | Sparse, witnessed-event fixed-point model; **new packet-alias counterexample below** |
| B3 [CyberSand #555](https://github.com/techrote/cybersand/pull/555) | `d9ad65194e3482f91be2cd64aa3d0690e53ee263` | Historical successful receipt is now typed `HISTORICAL_ACK_ONLY`; no new current-epoch authority, no second mutation |
| B4 [CyberSand #554](https://github.com/techrote/cybersand/pull/554) | `f8f57d15fbb223342f66734216aa9c53b8e51ff6`; alias challenge blob `d37a226a24649a0e541425c4ec2e33a4f8ff9930` | Independently authored exact-B2-blob executable challenge (new source); its **execution on the full B2 checkout is not yet established** |
| B5 [#472](https://github.com/techrote/radiCADSAC/pull/472) | before this checkpoint `43046ce5e76d73a4c37cd066d685a015bb42bed4` | Single B5-owned additive report; no cross-lane edits |

Current authority: MC-B and MC-1 **NOT_ESTABLISHED**; `production_authorized=false`. The 121/20/30/50 historical census and 26 machining operations are unchanged. CyberSand default Water remains FreeMass, PressureFlow opt-in, MAT-AUTH and physical hash unchanged. No native/paid/STEP campaigns. At inspection the four radiCADSAC A/B Draft heads each had **17/17 ordinary hosted workflows completed successfully**; these workflows are not registered A1/A2/B1 exact-head research-unit qualification. CyberSand B2 and B3 documentation/source-scope passed and native/GDExtension were skipped by Draft policy; B4's updated documentation/provenance was in progress. All research candidates remain Draft and unmerged.

## Decisive B2 falsifier: accepted payload is not the consumed payload

**Claim attacked:** a complete, accepted set of worker packets is sufficient to evaluate or skip the next bounded synchronous state transition against its *accepted authoritative input*.

At source-locked `sparse_fence.py`, `Packet.make(generation, tick, shard, events)` computes `events = tuple(events)`, then records a SHA-256 `check`. Its frozen dataclass freezes the `events` **attribute**, not nested mutable events. `Fence.accept` checks `check == digest(..., p.events)` once, then stores the **same Packet object**. `Fence.advance` checks shard count, event shape, overlaps and global owners, but **does not recheck the stored digest**; it passes the presently observed `p.events` into `engine.step`, which applies them.

An executable minimal control reusing precisely the published `digest` serialization and `Packet.make` shallow-wrap expressions was run separately with Python `hashlib`, `json` and `dataclasses`:

```python
event = ["pressure", 0]
packet = Packet.make(0, 0, 0, (event,))
accepted_check = packet.check
event[1] = 1
assert packet.events[0] is event
assert digest(0, 0, 0, packet.events) != accepted_check
```

The two deterministic checks were `09e93b0857d8fb02d87cbf870f3ec96aef92018eb94ef6223e486c4f49da4a6c` before mutation and `fbf7b4b22681831a756c813989eb8bfe9afa789e6c818d84290f9e5718877322` after. The former is still stored in the frozen Packet. The full B2 model itself **was not executed** in this independent B5 control; the missed recheck and subsequent consumption are findings from source inspection, not invented full-run evidence.

**Implication:** with all four shards present (or one shard in the one-worker model), a caller retaining an event-list alias can change `["pressure", 0]` to `["pressure", 1]` *after* `Fence.accept` and before `Fence.advance`. The latter accepts the event as well-typed and commits a transition different from the formerly digest-accepted input. A `set` event has the same alias class. B4's [exact-blob challenge runner](https://github.com/techrote/cybersand/blob/f8f57d15fbb223342f66734216aa9c53b8e51ff6/research/solver-certificates/performance/b2_barrier_alias_falsifier.py) contains the broader 1/4-worker pressure/set oracle; request its exact-head execution to quantify any full-state divergence.

This falsifies the model's **freeze/custody premise**, not its pure radius-1 two-phase fixed-point lemma, and does not demonstrate a defect in CyberSand's actual native worker barrier. A digest without immutable custody is a mutation sentinel, not an authenticated ownership witness.

## Minimal reusable rule: validated snapshot must linearize at consumption

Let `A` be the canonical, finite packet sequence validated for generation `g`, tick `e`, complete producer roster `W` and declared dependency edges `D`. Let `C` be the input actually consumed by a stage. A sufficient *contract* for transferring a conditional deterministic proof from validation to computation is:

[
operatorname{Complete}(W,g,e)
land operatorname{TrustedCustody}(A)
land operatorname{Canonical}(A)
land (C=A)
land operatorname{DependenciesCurrent}(D,g,e).
]

If the validated and consumed inputs are identical, stage determinism makes the checked conditional proof apply to the consumed transition. If packets can change between validation and consumption, `C=A` does not follow: this counterexample disproves that missing implication. This is ordinary immutable-snapshot/transaction linearization, **not a novel mathematical theorem** or proof of the CyberSand native read/write graph.

A prospective source-typed interface should distinguish:

| Type | Meaning | Allowed action |
| --- | --- | --- |
| `WAITING_FOR_OWNER_BARRIER` | Missing authoritative shard/producer | **BLOCK**; not even full recomputation can repair absent input |
| `WITNESS_DRIFT` / `UNTRUSTED_PACKET` | Supplied payload changed, ownership/pin provenance missing or stale | **REFUSE without mutation**; invalidate affected derived proofs |
| `COMPLETE_UNKNOWN_DEPENDENCY` | All authoritative inputs present but range/effect cannot be bounded | **RECOMPUTE** reference stage; no sleep/reuse |
| `COMPLETE_VERIFIED_INPUT` | Stable, canonical producer-owned snapshot; complete epoch, relevant dependency state and policy | May consult **one already-skippable stage's** scoped certificate; not a generic tick skip |
| `HISTORICAL_ACK_ONLY` | Old B3 successful transfer acknowledgement, no new fence | Observe historical transaction; **never spawn or authorize fresh operation** |

**Precise B2 correction request:** enforce fully immutable, bounded, typed nested event tuples (including all constructors, not only `Packet.make`); commit an owned deep snapshot at `accept`; and/or independently recompute and compare every packet digest under the complete barrier **before applying any event**. Reject source-witness drift atomically, preserve the negative control and show 1/4-shard pressure/set adversarial full-state-oracle outcomes. Mere outer `tuple(...)` and a frozen dataclass are inadequate. Source authentication beyond the local trusted owner remains a separate assumption, even after the alias repair.

## Cross-programme reconciliation and scoped discoveries

- **A1/A2/B1:** A1's new H2 square-lift shows one *restricted* transcendental double-touch family; A2's corrected bounded knot import has a separate direct-reversal size hole. B1's D2 serializer reconstruction materially narrows the old self-asserted-envelope gap, but caller-supplied pins do not authenticate the actual A1/A2 producing objects. The same `validated source != authenticated source` distinction remains; actual producer-module replay and external pin custody are the next decisive checks. No broad H2 isolation or new original-source coverage is admitted.
- **B2:** New sparse model removes its predecessor's mandatory per-tick whole-grid copy/diff in the *declared toy stage*. The earlier O(N) cost-floor falsifier remains valid for the earlier implementation; the new alias gap prevents declaring accepted authoritative packet input. Even after correction, real native gas/pressure, moving bodies, reactions and parcel sidecars must be inventoried before any general sleeping. B2's quiet/mixed abstract work ratios remain **non-native accounting**.
- **B3:** The earlier B4/B5 historical receipt replay warning has been addressed at the new B3 head by `HISTORICAL_ACK_ONLY`. This is an actual narrowed model-contract improvement, not yet native current-epoch handoff acceptance. Contact producer identity, momentum/impulse parity and World-applied policy remain unverified.
- **B4:** Historical #470 collider-packet stage p50 reduction is still separately source-qualified; p95 whole-tick differences vary with A/B/B/A arm order, including a no-packet control improvement. No new B2/B3 real tick reduction has been established. The B4 alias runner is useful as a *contract falsifier*, not a performance benchmark.
- **B5 integration:** No candidate meets source-verified independent review plus unconflicted exact-head research-admission requirements for an integration merge. Preserve candidates, flaws and correction trails; do not merge or create a new dispatcher.

### Review disposition and one highest-value next seam

**GO** for the narrow source-level shallow-alias counterexample and B3's typed historical-ack correction. **HOLD** on B2's packet-authority premise, A1/A2/B1 genuine producer custody, any native throughput/physical-law admission, and all MC gates. **NO-GO** for treating a matching self-issued digest as a stable authoritative event receipt.

**One decisive next experiment:** ask B4 to execute its exact-pinned `b2_barrier_alias_falsifier.py` on B2 head `90d87d46` *before and after B2's minimal deep-freeze/revalidation correction*, checking 1/4-worker complete and incomplete barriers, pressure and set events, exact state/original packet equality, and zero mutations on refusal. This tests the proposed transfer law without creating hot-path proof machinery. B1's genuine producer/pin challenge and A3's A2 reversal control can continue independently.

**Evidence class:** source-locked review, bounded independently executed shadow mutation, author-reported deterministic tests and ordinary hosted workflow checks. **Not** full exact-head authored-module execution, native simulation, physical hash parity, independent proof acceptance, actual worker participation or measured throughput. No files outside B5's isolated research subtree were written.
