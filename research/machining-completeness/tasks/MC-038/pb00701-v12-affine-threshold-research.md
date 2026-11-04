# MC-038 / PB-007-01 — V12 affine-H1 endpoint-sign falsification and exact root threshold

**Date:** 4 November 2026. **Status:** bounded exact mathematical research, draft until independently reviewed and literal-head/merged-main qualified. **Evidence:** `DETERMINISTIC_MODEL` only. **Gate:** PB-007-01/02/03/04 OPEN; MC-B and MC-1 NOT_ESTABLISHED.

## Source, authority, and falsifiable candidate

Preregistered on [MC-038 issue #100](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6632449251); distinct [write reservation](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6632453566). Source authority at beginning: `main=e0d66d075bf69309e283022744e4fd79717b2638`. Do not construe the reservation as proof acceptance.

Exact frozen original source case: `composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0`; canonical full specification SHA-256 `ee15e947924b45640dd16634247a476bb230fdc145fef94407d9a7c219928cd5`; whole source row SHA-256 `d0acef7c69cb8ac1ba128b988e83817a91feff78509dd18007d0e56a506336c3`. Source parameter `source-time-t`, interval [0,2], genuine clamped piece knot t=1, affine phase turns t/4. Harmonic-zero degree-zero cosine is identically zero. Harmonic-one degree-one fully clamped cosine/sine B-spline controls, with knots [0,0,1,1,2,2], are respectively

- C1: [-1/3, 2/3, 2/3, 2/3]
- S1: [2/3, -1/3, -1/3, -1/3]

The historical first span had owner V12 CERTIFIED, the second V43 `BLOCKED/CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED`, whole frozen v54 disposition BLOCKED. **The v2 reconciliation already classifies this entire exact source COMPLETE_SOURCE_SPECIFIC.** This work cannot count it again. The independent prior whole-source result is documented in [component-prefix composition research](pb00701-component-prefix-composition-research.md), which demonstrates the original two simple roots; the present contribution is a parametric threshold, including a tangency and arbitrarily near root pair, derived from an unaltered degree-one grammar. This is not a reclassification of the V43 refusal.

**Precisely falsified candidate:** `ENDPOINT_SAME_SIGN_IMPLIES_EMPTY_INTERIOR`: that equal negative original source endpoint/true-knot point signs and a separately root-free second source child are sufficient to certify absence of interior original physical zeros. The frozen source already contradicts the proposal. The family below makes the exact reason and threshold reproducible. This does *not* falsify the independently accepted full source-specific proof or a general analytic solver.

## Fixed admitted source family

For **rational** a strictly between zero and one, keep every original channel degree, clamped source knot, interval, phase and one-sided knot-point policy. Replace the four cosine controls with `[-a, 1-a, 1-a, 1-a]` and the four sine controls with `[1-a, -a, -a, -a]`. The exact literal original frozen record occurs at a=1/3; every other a is a **prospective** source and never part of the 121-case frozen denominator.

On 0≤t≤1 the original clamped B-spline extraction gives C1(t)=t-a and S1(t)=1-a-t. Put x=t−1/2, k=π/2, δ=1/2−a. Angle addition, with physical theta=πt/2, gives the **exact original physical function**

[
F_a(t)=sqrt2,[deltacos(kx)-xsin(kx)].
]

On 1≤t≤2 the original second child has constant C1=1−a and S1=−a, giving

[
F_a(t)=(1-a)cos(kt)-asin(kt)<0,quad 1le tle2,
]

because theta lies between π/2 and π, cosine is nonpositive, sine nonnegative, and at least one negative term is strict at both exteriors. Both source pieces agree at t=1: F_a(1)=−a<0, so the physical true-knot point is nonzero, one-valued and not an event. F_a(0)=−a<0 and F_a(2)=−(1−a)<0. There is no zero in the right child, including its shared knot and terminal endpoint.

For |x|≤1/2, cos(kx)>0, and the ratio

[
G(x)=x	an(kx)
]

is even. On 0<x≤1/2, `G'(x)=tan(kx)+kx sec²(kx)>0`; G(0)=0 and G(1/2)=1/2. Hence the source equation F_a=0 is equivalent to G(x)=δ and **all** roots in the admitted grammar are completely classified, with no arbitrary refinement or interval scan. This proof is degree-aware and only for the precisely declared affine-H1 family; it does not assume general analytic decidability.

## Exact zero events, multiplicity, order, parity and signs

| Rational a | Exact complete zero set | Multiplicity | Maximal ordered physical signs |
|---|---|---|---|
| 0<a<1/2 | t=1/2−x* and 1/2+x*, where unique x*∈(0,1/2) satisfies G(x*)=1/2−a | Two simple roots of order 1, distinct and strictly ordered | (−,+,−) |
| a=1/2 | t=1/2 | One order-two tangency, no sign flip | (−,−) |
| 1/2<a<1 | Empty | None | (−) |

For 0<a<1/2, the two roots are simple because G'(x*)>0 and cos(kx*)>0. The exact even symmetry and strict maximum F_a(1/2)=√2 δ>0 between negative F_a(0)=F_a(1)=−a establish both sign reversals. For a=1/2, `F=-√2 x sin(kx)`, and the exact Taylor germ `-√2 k x²+O(x⁴)` with k>0 establishes order exactly two and negative signs on both sides. For a>1/2, δ<0, so the first term is negative and `x sin(kx)≥0`; therefore the whole prefix is strictly negative, and the right child already is negative.

**Extremely close pair.** Fix rational q=2^-100 and δ=q²=2^-200, a=1/2−δ. Strict concavity of sine on [0,π/2] implies `sin((π/2)q)>q`; also `cos((π/2)q)<1`. Thus `F_a(1/2±q)<√2(δ−q²)=0`, whereas F_a(1/2)>0. Strict monotonic G proves one simple root on each side, both strictly inside `(1/2−q,1/2+q)`, separated by **strictly less than 2^-99**. No numerical sampling, tolerance or timeout serves as the root predicate. Root coordinates remain implicit, not falsely labelled rational.

## Termination, reproducibility, refusal semantics

`pb00701_v12_affine_threshold.py` uses only exact rational arithmetic to choose one of three analytically exhausted regimes, checks rational bit budgets (≤512 bits), constructs exact original-source controls, classifies maximal root/sign cells and emits a source-preserving implicit-root description. The executable does *not* numerically evaluate π, the trigonometric function or solve the transcendental equation. Its completeness follows from the explicit analytic proof above. Bad input, unadmitted a, floating data or exceeded arithmetic limits result in **NONTRUTH REFUSAL**, never an asserted absence of roots.

`verify_pb00701_v12_affine_threshold.py` separately reads and checks the exact frozen Git blob inputs, exact source/row SHA-256, original spline controls/knots/phase and historical V12/V43 dispositions, and the v2 COMPLETE_SOURCE_SPECIFIC witness. It includes 256 exact rational amplitude controls, a=1/3 original, threshold tangency, negative controls, five near-threshold offsets on both sides, the 2^-200 case, malformed parameter refusals and nine source/phase/knot/evidence/refusal mutations. Tests are adversarial implementation checks; the analytic argument is the root-count proof.

Reproduce from repository root:

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v12_affine_threshold.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
```

Machine-readable evidence is [pb00701-v12-affine-threshold.json](pb00701-v12-affine-threshold.json). Earlier failed raw routes and the frozen corpus remain unchanged.

## Historical census and engineering limits

| Exactly pinned class | Before | After | Delta |
|---|---:|---:|---:|
| v54 original source denominator | 121 | 121 | 0 |
| v54 refused routes | 20 | 20 | 0 |
| v54 missing ordered premises | 30 | 30 | 0 |
| post-v54 complete source-specific witnesses | 50 | 50 | 0 |

**Newly resolved historical case IDs: []**. This is a bounded C result only upon independent head review and qualification, **not A or B**, not PB-007-01 universal coverage. PO-02/04/05/07/08, PB-007-01/02/03/04, MC-B and MC-1 remain open or NOT_ESTABLISHED.

No changes to 26 operations, canonical manufacturing journal, durable disconnected bodies, source/time/phase semantics, topology, independent native geometry or conventional usable engineering STEP. No paid/native/production authorization. Do not merge before fresh literal-head CI and independent current-source review; after merge require a distinct merged-main check and separately coordinated ledger update.
