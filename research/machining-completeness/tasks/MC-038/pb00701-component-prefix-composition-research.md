# MC-038 — five original component-prefix and tail compositions

**Recorded:** 2 November 2026. **Owner:** [MC-038 / issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Preregistration:** [comment 6591325199](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6591325199). **Source baseline:** `e0514500aeca59afa4924dcc2da3ca0c2688d9ac`. **Evidence class:** deterministic exact source-bound model research.

## Purpose and bounded result

This leaf completes the missing original first-span event/endpoint proof for five sources whose second spans already have qualified mathematical proofs. It reconstructs the original harmonic coefficients, proves the common carrier's complete zero set, verifies nonvanishing multipliers, reexecutes four pinned tail producers and composes the actual original intervals across a continuous nonzero source knot.

The full closed-source results are:

| Original source family | Tail | Prefix roots on (0,1) | Tail roots on (1,2) | Complete roots on [0,2] | Maximal physical signs |
|---|---:|---:|---:|---:|---|
| V12 component partition | 0 | 2 | 0 | **2** | negative, positive, negative |
| V12 component partition | 100 | 2 | 1 | **3** | negative, positive, negative, positive |
| V13 nonvanishing even multiplier | 0 | 2 | 0 | **2** | negative, positive, negative |
| V16 Chebyshev multiplier | 100 | 2 | 1 | **3** | negative, positive, negative, positive |
| V17 projective even multiplier | 0 | 2 | 0 | **2** | positive, negative, positive |

Every listed physical root is simple. None of these sources has an exterior root, source-knot root or continuum-zero component. Exact original case IDs, full source and whole-row SHA-256 values, original controls, phases, historical owners/refusals and proof receipts are retained in the [machine report](pb00701-component-prefix-composition.json).

The former tail-only classifications were correct descriptions of their proof scopes. This new composition adds complete source-specific witnesses; it preserves the frozen V54 **121 original sources / 20 route refusals / 30 missing ordered premises** record. Updating the separately registered evidence inventory remains an integration task after qualification. The four V10/V11 tail-only sources are outside this leaf.

## Original source custody and lowering

All five sources use `source-time-t` on [0,2], with original piece boundaries [0,1,2] and phase turns `t/4`, hence theta=pi*t/2. Every original amplitude is a constant or affine polynomial represented by fully clamped degree-zero or degree-one B-spline pieces. The new lowerer expands each original piece into the original t coordinate and verifies every channel's left/right value at t=1 exactly.

The wrapper admits exactly these frozen records:

- `composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0`
- `composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail100`
- `composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail0`
- `composite:PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER:tail100`
- `composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail0`

The V12 records retain their `v19` harvesting origin. Each historical first-span owner remains `CERTIFIED`; each second span retains `PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF`, `BLOCKED`, and `CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED`. The new mathematical proof does not infer an ordered event view merely from those historical labels.

## Exact common-carrier lemma

On the first original span define

\[
R(t)=(t-1/3)\cos(\pi t/2)+(2/3-t)\sin(\pi t/2),\qquad 0\le t\le1.
\]

The exported `carrier_prefix_proof()` establishes this lemma on its stated interval. A later consumer must separately prove that its own original coefficients and phase have the required factorization; the lemma contains no original-source binding by itself.

The substitution t→1−t exchanges the two amplitudes and exchanges sine and cosine, so R(1−t)=R(t). For theta=pi*t/2,

\[
R'(t)=\cos\theta-\sin\theta+
\frac\pi2\left[-(t-1/3)\sin\theta+(2/3-t)\cos\theta\right].
\]

On [0,1/3], theta lies in [0,pi/6]. Thus cos(theta)≥sqrt(3)/2>5/6 and sin(theta)≤1/2. Both terms inside the square brackets are nonnegative. Consequently **R'(t)>1/3** on the entire closed interval.

On [1/3,2/3], both amplitudes are nonnegative and not simultaneously zero, while sine and cosine are strictly positive. Hence R is strictly positive throughout that interval. Reflection establishes strict decrease on [2/3,1].

Two exact half-angle identities give strict source-root brackets:

- At t=1/6, R/cos(theta)=−1/6+(1/2)tan(pi/12)<0 because tan(pi/12)=2−sqrt(3)<1/3. The strict radical comparison follows from 3>(5/3)^2=25/9.
- At t=1/4, R/cos(theta)=−1/12+(5/12)tan(pi/8)>0 because tan(pi/8)=sqrt(2)−1>1/5. The strict radical comparison follows from 2>(6/5)^2=36/25.

The intermediate value theorem and strict derivative therefore give exactly one simple root in (1/6,1/4). Reflection gives exactly one more in (3/4,5/6), with no other zeros. The complete carrier signs are **negative, positive, negative**, and R(0)=R(1)=−1/3.

The rational cuts at 1/3 and 2/3 delimit the argument. They are positive points, not physical zero events or original source knots. The reported root coordinates are implicit unique original-source roots within strict rational brackets; no rational or algebraic coordinate is asserted.

## Original harmonic factor reconstruction

Each original first span is exactly M(theta)R(t). Set c=cos(theta), s=sin(theta), a=t−1/3 and b=2/3−t. The implementation reconstructs cos(h*theta)=T_h(c) and sin(h*theta)=s*U_(h−1)(c) by exact Chebyshev recurrence, independently for the constant and t coefficient of every original amplitude.

| Family | Exact multiplier | Nonvanishing proof on the original prefix | Effect on carrier signs |
|---|---|---|---|
| V12 | 1 | Exactly one | Preserves |
| V13 | 1+2c² | In [1,3] | Preserves |
| V16 | P(c²), P(z)=409−782z+352z²+32z³ | At least 4495/416>0 | Preserves |
| V17 | sin(2theta)−2 | In [−2,−1] | Reverses |

For V16, substitute w=1−z in [0,1]. Exact polynomial expansion gives

\[
P=11-18w+448w^2-32w^3
\ge11-18w+416w^2
\ge11-\frac{18^2}{4\cdot416}=\frac{4495}{416}>0.
\]

For V17, product-to-sum reduction is checked directly using sin(2theta)=2sc and s²=1−c²:

\[
(2sc-2)(ac+bs)
=\bigl[(-2a+2b)c-2bc^3\bigr]+s\bigl[-2b+2ac^2\bigr].
\]

Every coefficient of these expressions must match the independently lowered original source. Added or removed harmonics, a nonzero prefix bias, a changed coefficient, or a mismatched multiplier refuses the proof. At any carrier root, (MR)'=M*R'≠0, so all physical prefix roots remain simple.

The earlier V41/V13 fixed-source proof uses sine harmonic **4**, while this V13 source uses harmonic **3**. It supplies no transplanted carrier receipt here; the new lemma and exact original factor reconstruction establish the required result directly.

## Replayed tails and whole-source composition

Four pinned producers run their existing `contract()` entry points against their own pinned original inputs:

| Producer | Actual second-span result used |
|---|---|
| [V12 tail contrast](verify_pb00701_v43_v12_tail_contrast.py) | Tail0 strictly negative, root-free; tail100 one simple negative-to-positive crossing in (1,101/100), derivative >689/7 |
| [V13 even factor](verify_pb00701_v43_v13_even_factor.py) | Tail0 strictly negative and root-free |
| [V16 Chebyshev crossing](verify_pb00701_v43_v16_chebyshev_crossing.py) | Exactly one simple negative-to-positive crossing in (3/2,7/4), with derivative >795/14 in the crossing interval and signs proved over the remainder |
| [V17 positive turn](verify_pb00701_v43_v17_positive_turn.py) | Tail0 strictly positive and root-free |

Producer code blobs and freshly replayed result digests are checked before normalization. The results retain their original [1,2] scope. The new lowerer independently computes and compares the actual source endpoint values:

| Source | F(0) | F(1), from both original pieces | F(2) |
|---|---:|---:|---:|
| V12 tail0 | −1/3 | −1/3 | −2/3 |
| V12 tail100 | −1/3 | −1/3 | 298/3 |
| V13 tail0 | −1 | −1/3 | −2 |
| V16 tail100 | −11/3 | −409/3 | 278/3 |
| V17 tail0 | 2/3 | 2/3 | 4/3 |

The knot is continuous channel-by-channel and nonzero in every case. Its point sign agrees with the adjacent proved sign cells. Consequently the composition concatenates the strictly ordered original root brackets, sums the distinct root counts and merges the adjacent equal-sign cells across t=1. It adds no knot event. Several tails are genuinely nonmonotone; their complete sign/root proofs do not require a false global-monotonicity assertion.

## Input safety, falsifiers and reproducibility

Public source/report inputs are bounded typed JSON before serialization, hashing or legacy parsing. Canonical bytes distinguish booleans from integers. Guards reject floats, custom objects, cycles, duplicate keys, excessive depth/nodes/container sizes/aggregate bytes, oversized integers and noncanonical rational tokens. Exact rational strings are lexically bounded ASCII integers or reduced ratios before `Fraction` construction; exponent and decimal strings cannot request expanded integers. Dependency and report reads are bounded before allocation.

Only pinned repository originals reach the historical producer functions. Caller rows must match the full original-record and source digests before any legacy proof executes. Fresh replay refusal or drift aborts the result; it cannot become a coverage classification. The private structural composition helper assumes mathematical views already established by the fixed prefix proof and pinned tail replay; it is not a public verifier of arbitrary truth assertions.

The 20 adversarial test methods challenge original harmonic coefficient identities independently of source hashes, V17 sign reversal, polynomial multiplier positivity, phase/knot/continuity, cross-source substitutions, fake proof-cut and knot events, bracket ordering and multiplicity, omitted tail evidence, changed/failed producers, canonical rational/resource parsing, boolean/integer aliases and false authority/completeness claims.

Run from the repository root:

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_component_prefix_composition.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
python3 tools/validate_repo.py
python3 tools/validate_machining_completeness.py --self-test
```

The machine report is deterministically reproduced with `python3 research/machining-completeness/tasks/MC-038/pb00701_component_prefix_composition.py --write-report`. Its recorded timestamp identifies this fixed research result rather than the time of each replay.

## Programme implications and retained obligations

The source-specific mathematical composition supplies missing complete event evidence for these five sources. For MSAC it preserves the exact source parameter, provenance and manufacturing-intent semantics. For OpenSimachinist it provides finite original-source root/sign evidence that a future source-bound consumer may integrate after checking the declared hypotheses. It establishes no generic V43 event solver, universal proof-consumption interface or arbitrary source-family coverage.

The 26-operation domain, original phase/source custody, canonical journal, material/body/lineage, refusal, `UNCERTIFIED`, conventional usable engineering STEP, historical source corpus and historical verdicts remain intact. PB-007 obligations remain open; MC-B and MC-1 remain `NOT_ESTABLISHED`; production authorization is false. No native geometry, topology, B-rep, independent STEP-consumer or production qualification follows from this deterministic result.

Qualification requires a distinct review of the final source, literal-head focused/static CI, matching reviewed/synthetic/landed trees, an expected-head guarded merge, independent merged-main checks and the issue #100 checkpoint. Registry/current-state changes follow qualified landing and belong to the integrator. This leaf creates no successor issue, scheduler or native/paid campaign.
