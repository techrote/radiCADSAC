# MC-038 / PB-007-01 — frozen V54 versus already-complete V2 signed-source novelty boundary

**6 November 2026. Evidence:** `DETERMINISTIC_MODEL`. **Status:** bounded negative/falsification of a *proposed acceptance-counting route*, **not** a proof that the new algorithms in #421/#423 are wrong, a universal mathematical impossibility, or an accepted PB-007 / MC-B / MC-1 result. Parent: [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). Coordination: [#324](https://github.com/techrote/radiCADSAC/issues/324).

## Falsifiable hypothesis and exact source scope

Proposed route `REPEAT_SOURCE_WITNESS_IMPLIES_NEW_V54_ORDERED_PREMISE`: an additional source-specific event/order/sign certificate on each of three frozen V54 category-3 sources can immediately be counted as three **new unique historical source closures**, turning the historical `30` missing ordered premises into `27`, even where the producing V2 50-source register already contains the exact same complete signed events and original-source cells.

**Falsification:** the already-landed, independently pinned producing V2 proof establishes the *same original source*, entire original source interval, true knot, event order, sided signs, root order/parity and maximal source sign cells. If a genuinely new **general owner/consumer** proof obligation and its fresh executable consumer are established, this particular counting-route falsification does not exclude that different result. A second proof *method* is not the same as a new historically missing *source result*.

Primary reviewed candidates: [#421 head `359784454c4eaeda173458b9f4919b07edbdacd8`](https://github.com/techrote/radiCADSAC/pull/421) and [#423 head `cb594e7a1fe286e953e62e5d3c01916120b18337`](https://github.com/techrote/radiCADSAC/pull/423), both compared against authoritative main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. Do not count #425: its separate writer is already repairing the same novelty defect on another original, after [independent HOLD review](https://github.com/techrote/radiCADSAC/pull/425#pullrequestreview-5795715350).

## Exact original-source identities and preexisting signed results

All three are **original frozen sources**, parameter `source-time-t∈[0,2]`, true source knot `1`; no constructed substitute or modified source. The v54 SHA-1 Git blob is `5841c331579489b25caef38cd412bdbf286f9134`, v2 SHA-1 is `e52d3baf3692a011cf86234eeaa992ef407d99fd`.

| Frozen original case | Original source SHA-256 | Older qualified producing proof | Exact old signed event/cells |
|---|---|---|---|
| `composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0` | `f4c2d33cc4c5a52f355ff4ecc36ad6ee38af0ff0fa8c5159aaac5923a10125ff` | [stationary source-knot composer](https://github.com/techrote/radiCADSAC/blob/48222d6c40b15ad42cc36d56e6d25f3b284e7fc9/research/machining-completeness/tasks/MC-038/pb00701_stationary_knot_composition.py), Git blob `d0fbe7e189066fd9398958f1b1814b8147a6a64e` | Unique **simple** root at `1/2` NEG→POS, nonzero positive knot, maximal sign cells NEG and POS |
| `composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100` | `a49b92bbb74a7e016eed471feb64808eb9109a6a42b3ef874243364981a396fd` | Same pinned stationary source-knot composer, previously complete even in V1 | Same entire source signed event and cells; different right source H0 tail retained |
| `composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0` | `e8d2451833854ee7eaf73d4fb70b78b86ba72194b2688876f3bb9ee6ab132ffd` | [exact-zero child full-source witness](https://github.com/techrote/radiCADSAC/blob/48222d6c40b15ad42cc36d56e6d25f3b284e7fc9/research/machining-completeness/tasks/MC-038/pb00701-exact-zero-child-source-completion-witness.json), Git blob `ed0a09595a4e73f7fdb9853d9151b8c7b6fea05f` | Sole zero at **source knot 1**; NEG→POS, sided orders **1/1**, deliberately **no global analytic multiplicity**, two maximal cells NEG/POS |

The stationary originals have phase turns `0`, physical first span `F=t−1/2` and second span `F=1/2` (tail0) or `F=1/2+100(t−1)` (tail100). Thus earlier source-knot composition already certifies the exact same root `1/2` and sign cells in both. The signed source-knot join from PR #421 might contain reusable improvements **for a different scope**. This comparison does **not** falsify the generic correctness of a broader stationary-knot composer; it falsifies *counting these two exact old source events as two newly closed source cases*.

For V23, phase turns `t/12`, H0 cosine `−501/1000`, H2 cosine first-span `t/1000` then `1/1000`, H1 sine first-span `1+t/1000` then `1001/1000`. Existing V2 proof explicitly records its exact event at knot 1 with differing positive sided derivatives, negative/positive one-sided signs, `complete_finite_physical_event_count=1`, full `physical_zero_set=["1"]` and `maximal_nonzero_cells=[−1,+1]`; see the earlier [3 November original-source RAG](https://github.com/techrote/radiCADSAC/blob/48222d6c40b15ad42cc36d56e6d25f3b284e7fc9/research/machining-completeness/tasks/MC-038/pb00701-exact-zero-child-source-completion-research.md). PR #423's alternative derivative bounds do not introduce a new root/cell conclusion, though their method may merit retention.

## Read-only machine qualification and falsifiers

The companion `pb00701_v54_v2_novelty_boundary_20261106.py` recomputes the 121/20/30 historical V54 census and 50 V2 source IDs against their real pinned Git blobs, and checks every V2 case-level historical disposition, source and original row SHA-256, source time/phase/true source-knot edges, producer identity, and complete-source coverage. It **reexecutes** the accepted stationary original-source composer (Sturm-checked ordered spans, exact knot continuity and signed-cell recomposition), and separately checks the prior saved V23 physical knot orders and event cells. Every source is checked on the **full closed [0,2]**, not a selected interior interval.

Adversarial controls mutate original phase, source identity, true knot, V2 level, prior root order, sided sign, physical sign cells, missing original, count-preserving disposition swaps, JSON type aliases, duplicated keys, nonfinite tokens and actual oversized raw file ingress. A mismatch is a **refusal**, never a truth claim; a native STEP or other geometry operation is not involved.

Reproduce at the exact PR checkout:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_v54_v2_novelty_boundary_20261106.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract --self-test
python3 tools/validate_machining_completeness.py
```

The adjacent [machine-readable receipt](pb00701-v54-v2-novelty-boundary-20261106.json) records every exact old/new identity, the candidate heads and source-receipt Git blobs, evidence class, cases and nonpromotions. Hosted CI must authenticate the literal checkout. A passing checker cannot prove any universal analytic event theorem.

## Matched before/after census and decision boundary

| Pinned measure | Before | After | Accepted delta |
|---|---:|---:|---:|
| Frozen original-source IDs | 121 | 121 | 0 |
| Historical uncertified source routes | 20 | 20 | 0 |
| Historical missing ordered premises | 30 | 30 | **0** |
| Already complete registered V2 original sources | 50 | 50 | 0 |
| Newly unique previously unregistered full signed source cases among these 3 | 0 | 0 | **0** |
| Required PB-007 / PO obligations discharged | 0 | 0 | 0 |

**Bounded C conclusion:** the *source-specific repetition → newly unique frozen-source closure* shortcut is falsified **for these three named source identities**, by the already executed and pinned V2 signed event proofs. The draft `30→28`, `30→29`, or combined `30→27` projections are not admissible as novel source-specific closure on this evidence alone. That does **not** show that every V54 generic owner premise was already solved, nor exclude a new reusable owner/consumer theorem: such a claim needs its own specific new proof/implementation, exact source route and independent coverage gate.

Historical V54 failures and V2 positive evidence must both be retained. PB-007-01/02/03/04 and PO-02/04/05/07/08 remain **OPEN**; MC-B and MC-1 remain `NOT_ESTABLISHED`. The original **26 supported operations**, physical source and phase, bodies/topology/journal, native geometry, independent oracle, conventional engineering STEP and consumer qualification retain their requirements. No expensive/native task or production repository is authorized.

**Next critical-path work:** define an actual reusable category-3 owner→signed-child→original-source consumer and prove a previously absent interface/grammar condition against an *original source* that V2 cannot already satisfy; otherwise redirect engineering effort to a missing PB/PO obligation rather than additional selected-source repetitions. Coordinate any acceptance/77-ledger integration separately from the #397 main owner.
