# B5 — Zero-component invariance under common refinement: topology/provenance contract

**10 November 2026 · independent, bounded research review · Draft/HOLD.**

## Exact source and authority checkpoint

- radiCADSAC accepted main: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; authority blob `fa0233323a0804d8a5d3eb7cd892a274a6173fab`: MC-1 `NOT_ESTABLISHED`, `production_authorized=false`. MC-B remains `NOT_ESTABLISHED`; historical 121/20/30/50 and 26 machining operations are unchanged.
- A1 Draft [#470](https://github.com/techrote/radiCADSAC/pull/470) exact inspected head `8c9667473651bcdb59da6606ca053c94ab52540e`, `carrier_partition.py` blob `d7e2da94343c7f2830b0eca6416b05420876df81`. Genuine physical B-spline authentication explicitly UNVERIFIED. At `certify()`, any true `left_continuum` or `right_continuum` still yields `kind=SINGLE_PHYSICAL_KNOT_ZERO`, though additional flags retain the distinction; independently flagged by A3 in [review 5836323988](https://github.com/techrote/radiCADSAC/pull/470#pullrequestreview-5836323988).
- B1 Draft [#473](https://github.com/techrote/radiCADSAC/pull/473) exact inspected head `1de37944950792ca967db6814cf6db648644e75c`: `rational_quotient.py` blob `e7d53896f6d83addad66e93ab40954fda2ad3c41`, `refined_product.py` blob `1174f8c68b4a0e7181b1ab4056f7422ade8f2b8f`, `certificate_algebra.py` blob `d366679ccbd1f57a3c8058857162e74df8efd178`. Both derived receipts call the **union of parent leaf boundaries** `physical_knots`; no source-origin tag or independently authenticated genuine spline-knot witness accompanies the list.
- Existing [#462](https://github.com/techrote/radiCADSAC/pull/462) research explicitly distinguishes structural knot/control identity under signed affine reparameterisation. It targets an unmerged research branch and is not accepted main or source authorization. [#453](https://github.com/techrote/radiCADSAC/pull/453) handles a separate bounded interval route. [#397](https://github.com/techrote/radiCADSAC/pull/397) owns MC-038 integration; this review alters none of those sources.
- CyberSand accepted main: `d4b18e7f06839b35c8f6a66195206da0f33c5fa3`. Existing #470 collider, #471 cursor, #522 PressureFlow optimisation and #474 lockstep are separate accepted work. B2 #556, B3 #555 and B4 #554 remain Draft; no new B2/B3 speed claim or live physics mutation is qualified here.

## A small exact infinite-family law (classical mathematics)

Let `F(t)=0` on `[0,1]` and `F(t)=(t-1)^2` on `[1,2]`, a valid degree-two C0 clamped B-spline H0 example with actual structural knot at `t=1`, full knots `[0,0,0,1,1,2,2,2]`, controls `[0,0,0,0,1]`. Let the denominator be constant `D(t)=d` for any nonzero rational `d`. Introduce any **representational** rational cuts `0<r<1<s<2` to the exact common-refinement grid `[0,r,1,s,2]`.

**Law.** Every exact de Casteljau/restriction refinement of `F/D` has zero set the *single connected closed component* `[0,1]`, no isolated zero at `1`, and strictly nonzero open intervals in `(1,2]`. The sign on `(1,2]` is `sign(d)`. The genuine structural knot of the numerator remains `1` regardless of `r,s`.

**Proof.** On both left leaves the function is exactly zero. On the two right leaves, local degree-two Bernstein coefficients of `(t-1)^2` over `[a,b]` are `((a-1)^2, (a-1)(b-1), (b-1)^2)`, nonnegative with at least one strictly positive for any `b>a>=1`. Exact division by the nonzero constant `d` preserves the zero set and fixes the sign. The left leaves join into `[0,1]`; the right leaves are strictly signed in their interiors. The point `1` lies in the closed left zero interval, so it cannot be a separate isolated point. The structural numerator source is unchanged by the representational cuts. QED. The operations are established polynomial/Bernstein facts; novelty is **not** asserted.

### Independently bounded control

`python3 research/experimental/ab-campaign/integration/topology_refinement_oracle.py`

An independent standard-library Fraction/Bernstein model was evaluated over **144 rational combinations** (six values of each `r,s`, four signed `d`), with the single-zero-component and both sign cones checked; all 144 passed, plus three invalid-input controls. This is a **deterministic model**, NOT execution of A1/B1's exact published modules or a proof by sampling. The infinite statement follows from the algebraic argument above. Native/STEP/physical-source admission and runtime cost are unavailable.

## Precise cross-lane falsifier and contract

It is invalid to infer an authenticated physical knot from an event partition or a syntactically verified source hash. For arbitrarily chosen different `r,s`, all the above candidates have the *same function and zero set* but different `physical_knots` fields in the present B1 E3/E4 receipt schema when those cuts originate as leaf boundaries. Therefore that field is **partition metadata**, not evidence that a source has a genuine B-spline structural knot at every listed position. Equally, A1's `SINGLE_PHYSICAL_KNOT_ZERO` type, considered alone, cannot establish singleton topology at `1`: the flags must be consumed or the schema refined. This does not falsify B1's quotient zero-transport theorem, A1's local polynomial-carrier theorem or their existing conditional proofs.

**Proposed minimal typed consumer interface, not a new engine:**

1. `partition_boundaries`: all exact leaf cuts, including synthetic refinements; never used as a proof of physical knot existence.
2. `genuine_knot_origins`: **separately authenticated** producer/spline source identity and structural knot/control witness (e.g. #462-compatible), or explicitly `UNVERIFIED`. Track origin for numerator and denominator independently.
3. `zero_components`: maximal closed zero intervals and isolated points disjoint from those intervals; a genuine knot touching a continuum is a *continuum boundary*, not automatically an isolated CROSS/TOUCH.
4. `sided_germs`: actual left/right local order and sign only when established for that specific source and orientation. `UNKNOWN` must not be silently converted to an exact order at a synthetic cut.

**One decisive independent qualification:** reconstruct one genuine spline source and a second syntactically valid, arbitrarily refined representation with identical values but different cut positions, pass both through literal-head A1/B1 and the #462 source witness where supported, and require invariant zero components **plus refusal to upgrade an artificial cut to an authenticated knot**. Include an altered control-vector/unchanged local value substitution and reverse-time orientation. Missing producer authentication remains `HOLD`, not a proved event.

## Discovery disposition

| Lane | Reusable gain | Independent/open issue | Economic significance |
| --- | --- | --- | --- |
| A1/A2 | Restricted complete polynomial-carrier intervals; finite local jets/analytic joins; all classical ingredients | Source genuine-knot authentication, global root completeness beyond admitted grammars and topology-kind consumer contract | Zero newly admitted original MC-038 class |
| A3 | Adversarial detection of knot-component kind conflation and source-parser bypasses | Full literal-head A1/A2/B1 and real producer challenge needed | Avoids unsound promotion |
| B1 | Conditional exact product/refinement/rational-quotient zero transport | Provenance labels and independent parent-pin custody; literal parent suite and A3 review | Proof check-count reduction only; no speed claim |
| B2 | Conservative local invalidation with typed unknown fallback | Exact-head restoration/custody tests not independently executed; 3.089× high-churn abstract-cost regression retained | No native speed gain |
| B3 | Water owner/quantity and policy-drift model guards | Applied policy is still not an authenticated native receipt; malicious raw rewrites still succeed; full model suite outstanding | No native physics/overhead qualification |
| B4 | Reanalysis of historical #470 packet stage | No-packet negative control prevents causal whole-tick speed attribution; physical hash/worker/RAM absent from these profiles | Existing packet-stage gain only |
| B5 | Source-provenance/semantic/topology/authority separation | This exact control and review require independent A3/B1 examination | No merge or production claim |

**Decision: HOLD all cross-lane event-consumer integration.** Request B1 to rename or explicitly subtype the E3/E4 `physical_knots` field and prevent source-knot promotion; A3 to challenge closed zero-component invariance at a genuine continuum-adjacent knot; B4 to keep no-packet/worker/hash negative controls. No author branch edits, production merges, material-law switches, MC-B/MC-1 promotion or expensive campaigns.

Prior art: standard de Casteljau/Bernstein closure and exact rational-function zero equivalence; [Bertot–Guilhot–Mahboubi 2011](https://doi.org/10.1017/S0960129511000090). Source provenance and conservative change propagation also have established antecedents; no novelty credit for mere certificate plumbing.
