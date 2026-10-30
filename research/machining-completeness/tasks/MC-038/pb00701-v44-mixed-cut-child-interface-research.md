# MC-038 / PB-007-01 — frozen V44 complete mixed-cut Q(alpha) child restrictions

**Status:** bounded source-matched deterministic-model research candidate, 30 October 2026. Initial baseline `main=c7f6a8e415380b2534096ae6db5239c399b809be` following [PR #316](https://github.com/techrote/radiCADSAC/pull/316). Final-head GitHub Actions, exact-head review and merged-main qualification must be recorded separately; this memo alone asserts none of those. **Owner:** [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Frozen case:** `harvested:verify_pb00701_v44:ffaea08e30c9`, original-source SHA-256 `d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2`. No native geometry/STEP evidence, no native or paid permit.

## Gap, hypothesis and falsifiers

[The complete-root source proof and atlas](pb00701_v44_source_proof_cell_atlas.py) orders three mixed rational/real-algebraic orientation proof cuts and reports four physical sign/root cells; [global-derivative proof](pb00701_v44_global_derivative.py) proves `F'(t)>=m>0` on the entire **original** `t in [0,1]`. [V45 bridge](pb00701_v44_v45_monotone_child_bridge.py) constructs actual two-child `Q(alpha)` channel/phase restrictions at the single irrational cut. [Independent sign proof](pb00701_v44_irrational_cut_source_sign.py) establishes that the original-source physical value is positive at that irrational orientation cut without using the inherited atlas sign during evaluation.

This bounded increment tests whether **all four**, not just the two V45 children, admit actual source-matched `Q(alpha)` polynomial and phase restrictions with exact inverses and a strictly positive inherited derivative. It also derives the ordered physical root counts from **new** independently computed nonzero cut signs, using monotonicity, and cross-checks rather than assumes the original atlas labels. Falsifiers: any mismatched original-source or predecessor pin, improper algebraic embedding identity, non-strict or contradictory cut value, nonpositive field width, mismatched exact restricted polynomial/phase, invented physical cut event, incomplete root conservation, unbounded/forged report or authority promotion must refuse.

## Exact construction

The original source function, unchanged from frozen V44, is

`F(t) = sum_h [P_h(t) cos(2*pi*h*(o+r*t)) + Q_h(t) sin(2*pi*h*(o+r*t))]`, with phase turns `o=-1/8`, `r=1/16`, `t in [0,1]`, `P_1=-3/2+t+2t^2`, `Q_1=-1/2-t+2t^2`, `P_2=1/100000000`, `Q_2=0`.

The only irrational proof cut in the frozen mixed partition is the common V41/V45 embedding `alpha=1/sqrt(2)`, the unique positive root of `2*alpha^2-1=0`. Its identity with the actual V41 source cut is replayed through exact polynomial GCD and Sturm common-root verification, not interval overlap or a decimal approximation. The other interior cuts are rational source coordinates. No multi-field compositum is claimed: all endpoints are either rational or members of **one** shared exact field `Q(alpha)`.

Reconstruct the exact original rational-source span; independently replay the full source derivative lower bound `m>0` and the V45/field binding. For each rational source boundary `q`, evaluate the original finite rational-phase trig interval `F(q) in [A,B]`; round outward to the existing exact 2^-32 dyadic grid; require a **strict nonzero** sign. For the only irrational source boundary reuse #316's independently transported exact Sturm/rational-source Lipschitz witness, still verifying its exact output. Only after all five signs are independently constructed are they compared to the preserved V44 proof atlas. A failed strict sign is nontruth, not a zero event.

For successive ordered exact endpoints `a_i,b_i in Q(alpha)`, require `w_i=b_i-a_i>0`. Define actual normalized source restriction `t=a_i+w_i*u`, `0<=u<=1`; for each original harmonic/channel compute the polynomial `P_h(a_i+w_i*u)` and `Q_h(a_i+w_i*u)` by exact field polynomial composition, then reconstruct the original polynomial using the inverse map to verify no coefficient or channel was lost. Phase is exactly `o_i=o+r*a_i`, `r_i=r*w_i`, in the **same field**. Original-source `F'(t)>=m>0` implies `dF_i/du=w_i*F'(a_i+w_i*u)>=m*w_i>0` on every **closed child**, including their shared proof-cut endpoints. The exact positive field element `m*w_i` is recorded and checked. It is not evaluated numerically.

From independent strictly nonzero ordered boundary signs and positivity of the closed-child derivative, an adjacent negative-to-positive pair has exactly one simple open physical zero; equal signs have none; any positive-to-negative transition contradicts the replayed derivative proof. On this pinned case the five signs should be `[-,-,+,+,+]`, yielding four open-root counts `[0,1,0,0]`. These are checked against the preexisting complete original-source proof only **after** deriving them; no proof cut is itself a physical event. The source-wide complete-root theorem is still a distinct qualification dependency.

## Verification and negative scope

Run on a literal exact repository checkout:

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v44_mixed_cut_child_interface.py --contract --self-test
python3 tools/validate_machining_completeness.py
```

The focused workflow explicitly checks out the literal PR head or push SHA. Adversarial tests cover exact field polynomial/phase reverse composition, every positive width/derivative lower element, exact rational trig interval containment, original-source zero at a rational boundary, independent irrational sign and resource refusal, source/pin drift, altered proof cut/sign/physical-event flags, incomplete partition, forged field/child/report/gate and report size/cycle. The report is source-recomputed and byte-for-byte canonical-replayed, not accepted on plausible asserted fields. Preserve every failed run and mathematical correction in the issue checkpoint.

**Limits:** This is a one-source, one-shared-field **DETERMINISTIC_MODEL** restriction, not a generally terminating real-algebraic compositum, a general transcendental value-equality/zero/multiplicity decider, a general nonmonotone or multi-owner event isolation proof, a replacement for V47/V49's own historical admitted constructors, or native material/topology, conventional B-rep, STEP or independent engineering use. Historic v54 for this frozen source stays `BLOCKED`; PB-007-01, MC-038, MC-B and MC-1 remain open/not established, all 26 admitted operation families remain mandatory, `production_authorized=false`. No authority/domain/corpus files are changed.
