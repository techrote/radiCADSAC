# B5 review — restored body-footprint alias defeats a certified B2 fixed point

**10 November 2026 · DETERMINISTIC_MODEL/source-critical · Draft/HOLD.**
This is a new **research-model input-admission counterexample**, not evidence of a native CyberSand defect, general pressure-law unsoundness, or a refutation of the conditional pure/fenced fixed-point theorem.

## Exact scope, pins and governance

- CyberSand accepted `main`: `d4b18e7f06839b35c8f6a66195206da0f33c5fa3`.
- B2 [Draft #556](https://github.com/techrote/cybersand/pull/556): `a7103e7ff74caf4d557a55cefa3b8e3244f6e04b`; `research/solver-certificates/invalidation/sparse_fence.py` Git blob `247974c57ac4e45ac5dc087e387a6920c76bf6d7`.
- radiCADSAC accepted `main`: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; B5 [Draft #472](https://github.com/techrote/radiCADSAC/pull/472), confined to `research/experimental/ab-campaign/integration/**`.
- Inspected both `AGENTS.md`, MC-1 authority/DR-0026/protocol, CyberSand worker/World/LCB policy, and current A1/A2/B1/B2/B3/B4 Draft heads. MC-B/MC-1 remain NOT_ESTABLISHED and `production_authorized=false`.

## Pre-registered falsifier and exact source mechanism

**Hypothesis:** `Fence.restore` can admit a same-geometry caller-owned mutable body-footprint set without taking immutable ownership, then install fixed-point certificates that become stale when the caller changes that set outside any witnessed event. A full-reference step against the post-mutation state will disagree with a complete 1- or 4-logical-shard fenced sparse step.

The exact reviewed source implements:

1. `State.body: frozenset[int]` is a **type annotation**, not runtime validation. `State.copy()` makes `cells.copy()`, but shares `self.body` by reference.
2. `Sparse.same_geometry` only checks width, height, cell-list size and storage type. It does not require a `frozenset`, bounded body positions or a source body identity.
3. `Fence.restore` calls `Sparse.restore` then `reset_certificates`, proving a blocked sand pair stable while the mutable set contains its top cell.
4. A later caller mutation `mask.clear()` changes the live `Sparse.state.body` without a `body` event, `revoke`, epoch generation transition or accepted worker-packet witness.
5. Empty packets from **all** logical shards pass the owner fence; `events_apply` has no touched sites; the already-certified tile stays asleep.

Minimal deterministic 4×4 fixture, tile size 2: Rock everywhere except Sand at flat index 0 and Empty at index 4, initially blocked by `body=set({0})`. `Fence.restore` accepts this same-geometry State. After caller `set.clear()`, the authoritative full rule moves the Sand to index 4 at tick 0; the certified sparse tile skips and leaves index 4 Empty. This is one-tick exact-state inequality with a **complete** logical fence, not a missing-worker counterexample. Under true immutable body ownership the skip is valid.

The source-pinned executable [b2_restored_body_alias_adversary.py](b2_restored_body_alias_adversary.py) refuses a mismatched Git blob before importing the **actual B2** model and checks six cases (1/4 logical shards × mutable-unwitnessed, immutable and witnessed-body-clear). From a checkout of this B5 branch, with a separate checkout of B2 #556 at the pinned head:

```sh
python3 research/experimental/ab-campaign/integration/b2_restored_body_alias_adversary.py --cybersand-root /path/to/pinned/cybersand
```

**Execution honesty:** A small independent Python reproduction of the literal `State.copy` alias and blocked-pair update ran locally and confirmed the predicted one-tick mismatch (full index 4 = Sand, skip index 4 = Empty), plus an immutable-body positive control. The new exact-module six-case checker was authored and source-pin inspected, **not executed in this environment**; no full B2 module or native worker run is claimed. Its failure to reproduce the stated mismatch is the falsifier of this review.

## Correct scope and suggested remedy

The research fixed-point theorem expressly assumes **complete, trusted and witnessed dependencies**. An arbitrary external mutation violates that premise. The actionable gap is that a public research restore *admits a source outside that premise* without refusing or canonically owning it. B2's recent **packet nested-payload deep freeze** does not protect `State.body` on construction/restore. Nor does its **4×4→8×2** geometry guard address this same-geometry, same-cell-count alias.

Minimal bounded correction in B2's exclusively owned subtree: on construction and restored-state admission, either demand `type(body) is frozenset` with bounded in-range canonical integral indexes, or copy a validated finite footprint into an owned `frozenset` **before** constructing/refreshing fixed-point certificates. Reject arbitrary iterables, over-capacity sets and caller-mutable state rather than silently claiming all provenance is covered. Retain explicit `body` events and complete-fence semantics; direct mutation of the engine's own publicly exposed `state` remains outside the trusted-owner theorem and needs an explicit trust boundary, not a per-cell hash.

## Updated source-critical A/B matrix and disposition

| Lane | New class / theorem / falsifier | Evidence limit and status |
|---|---|---|
| A1 #470 | Conditional simple-root tiling, signed algebraic-local event and Kronecker fallback. Sturm, transcendence and interval methods are prior art | Conditional mathematical GO; actual physical source and global unrestricted isolation HOLD |
| A2 #471 | Rational-phase local moment bound and genuine knot-sided germs; same local germ can hide an extra open-cell root | Scoped mathematical GO; complete source/continuum coverage HOLD |
| A3 | Independent exact Kronecker fallback replay; irreducible degree-8 budget refusal retained | GO on tested admitted class, not universal algorithm |
| B1 #473 | Rational Bernstein closed-nonzero and differently partitioned C0 product closure, classical de Casteljau algebra | Conditional GO; original spline producer pins, artificial-vs-physical knot and A2 receipt join HOLD |
| B2 #556 | Two-phase pure local fixed point under complete witnessed dependencies; repaired packet alias, counter bound and grid shape | **New** restored body-footprint alias admission falsifier. Runtime HOLD; historical 3.089× high-churn abstract-work regression retained |
| B3 #555 | Conditional Water amount/exclusive-authority model, seed alias now copied into immutable tuple | Applied signed-policy boolean still mutable/unversioned; native contact, rollback and physical hash HOLD |
| B4 #554 | Real historic #470 collider packet-stage p50 reduction 94.41%/94.07%; independent stage-versus-wall accounting | No new whole-tick causal gain: packet-free control and reverse wall-time sign. Actual worker/hash/memory A/B/B/A unavailable |
| B5 #472 | Classical complete-dependency custody law; closed-domain positivity and policy-mutation interop controls | New B2 restored-input custody challenge; no original case closure or production consumer |

**Common reusable seam:** a certificate is only sound *under the consumer's admitted immutable source/epoch/policy and complete influence dependency set*. B1's source pins, B2's accepted packets, B3's prepared intents and A1/A2's local receipts need explicit **producer authority and full state ownership**, not just internally consistent hashes. Unknown influence => recompute only after a complete fence; missing authority => BLOCKED.

**Review request:** B2 to distinguish immutable-input precondition versus explicitly supported mutable restore, and provide a minimal correction/test; B4 to independently execute the source-locked 1/4-shard fixture at the current head. This result does not authorize any production source integration, expensive/native profiling or default solver change. Historic **121/20/30/50**, **26 operations** and MC-038 evidence are unchanged. Newly admitted original machining classes = **0**; independently confirmed native tick reduction from this campaign = **0**.

**Disposition:** GO for adversarial source review; HOLD for exact-module qualification, B2 correction, independent B4 replay and any integration. Keep research Draft/unmerged.
