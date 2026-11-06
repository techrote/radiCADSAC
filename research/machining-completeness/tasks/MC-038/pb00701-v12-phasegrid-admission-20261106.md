# MC-038 / PB-007-01 — V12 original exposes a necessary phase-grid theorem refusal

**6 November 2026 · bounded negative C / direct-admission limitation · DETERMINISTIC_MODEL**

Parent: [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100).
Independent research claim: [#324/6694241367](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6694241367).
The challenged implementation is [Draft PR #441](https://github.com/techrote/radiCADSAC/pull/441) at **literal head** `b1774a01898e423a1e3f62d0b0f881f65156ff23`, not a claim about future revisions. Accepted main: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`.

## Hypothesis, outcome and admitted negative scope

**Falsified direct-application proposal:** the unmodified rational quarter-turn H1 phase-grid event theorem in #441 can certify the whole-source physical zero partition of the frozen V12 category-3 historical original merely because the original source meets its structural H1, rational-phase and quarter-turn-knot grammar.

The original **does meet** those necessary structural conditions, but its very first original source piece has **two** simple interior physical roots inside **one** quarter-turn phase cell, while both cell endpoints are negative. The #441 sufficient theorem correctly **refuses** this source at `ANGULAR_DRIFT_NOT_CERTIFIED_BELOW_PI`. Consequently it cannot supply this original's missing generic owner-to-consumer ordered-event premise as-is. This is a decisive refusal for this **precisely specified route**, *not* a defect in #441, not general impossibility and not an assertion that V12's roots were unknown. The complete original-source signed result was already established by the accepted V12 component-prefix/V2 producer and [#378](https://github.com/techrote/radiCADSAC/pull/378).

**Named obligations:** PB-007-01 and PO-04/05/08 remain OPEN. PB-007-02/03/04 and PO-02/07 remain OPEN. MC-B/MC-1 remain `NOT_ESTABLISHED`.

## Exact source custody and physical semantics

The frozen original is `composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0`, source SHA-256 `ee15e947924b45640dd16634247a476bb230fdc145fef94407d9a7c219928cd5`, whole-row SHA-256 `d0acef7c69cb8ac1ba128b988e83817a91feff78509dd18007d0e56a506336c3`. Its original source-time domain is **[0,2]**, genuine original knot **1**, original phase turns \(\beta(t)=t/4\), zero H0, and continuous clamped affine first harmonic cosine/sine coefficients:

\[
\begin{aligned}
C(t)&=t-\frac13,& S(t)&=\frac23-t,&0\le t\le 1,\\
C(t)&=\frac23,& S(t)&=-\frac13,&1\le t\le 2,\\
F(t)&=C(t)\cos(\pi t/2)+S(t)\sin(\pi t/2).
\end{aligned}
\]

All coefficients, phase, source time and knot are original, untransformed. The literal source is in immutable V54 corpus Git blob `5841c331579489b25caef38cd412bdbf286f9134`. Its **preexisting** complete whole-source witness is in V2 Git blob `e52d3baf3692a011cf86234eeaa992ef407d99fd`, producing source `pb00701_component_prefix_composition.py` (blob `530e552bb41c020456fdf0f17506cb18577896f3`). The original V54 disposition is **BLOCKED** (source's V43 correlated closed handoff); this historical label is not rewritten.

## Exact mathematical demonstration — two simple roots, not zero

On the first physical piece, the phase advances from 0 to \(\pi/2\), so **[0,1] is one literal quarter-turn grid cell**. Let \(q=C^2+S^2\) and \(W=CS'-SC'\). Direct exact arithmetic gives

\[
q_{\min}=\frac1{18}\quad(t=1/2),\qquad
q_{\max}=\frac59\quad(t=0,1),\qquad
W=-\frac13.
\]

Thus \(q>0\). A continuous coefficient orientation \(\varphi=\operatorname{atan2}(S,C)\) exists and has \(\varphi'=W/q<0\). The physical angular difference \(\delta=\pi t/2-\varphi\) has \(\delta'=\pi/2+1/(3q)>0\), so it is strictly increasing. At the left endpoint, \((C,S)=(-1/3,2/3)\) lies in quadrant II, giving \(\delta(0)\in(-\pi,-\pi/2)\). At the right endpoint, \((C,S)=(2/3,-1/3)\) lies in quadrant IV, giving \(\delta(1)\in(\pi/2,\pi)\). This exact angular order **crosses precisely** \(-\pi/2\) and \(+\pi/2\), and no other zero of \(\cos\delta\). Both physical roots are **simple**, because \(F=\sqrt q\cos\delta\), \(q>0\) and \(\delta'>0\) at each crossing. The signed cells on [0,1] are **NEGATIVE → POSITIVE → NEGATIVE**.

Independent exact sign controls are

\[
F(0)=-\frac13,\quad
F(1/3)=\frac13\sin(\pi/6)=\frac16>0,\quad
F(2/3)=\frac13\cos(\pi/3)=\frac16>0,\quad
F(1)=-\frac13.
\]

On the second original piece, \(C=2/3>0\), \(S=-1/3<0\) and \(\pi t/2\in[\pi/2,\pi]\). Therefore \(F<0\) throughout [1,2] (including the true knot and far endpoint). The **whole original source has exactly two simple roots**, both strictly between 0 and 1, and three maximal signed cells. No transcendental root scan, numeric tolerance, timing cap or assumed decidability is used for this proof.

## Why the proposed direct #441 certificate necessarily refuses

For the first cell, the local phase advance is one quarter turn. Using the conservative exact rational \(3<\pi<22/7\) and the exact norm/Wronskian:

\[
W/q\in[-6,-3/5],\qquad
\delta'\in(21/10,53/7).
\]

The tested strict sufficient certificate bounds the full cell drift by \(\max(|L|,|U|)<3<\pi\); here **\(U=53/7>3\)**. Therefore #441 returns `ANGULAR_DRIFT_NOT_CERTIFIED_BELOW_PI`, with the source **REFUSED_NONTRUTH**, not zero roots. Indeed two interior roots with equal negative endpoint signs mathematically exclude the proposed *at-most-one-per-grid-cell* sufficient conclusion. This does not imply actual nonmonotonicity: here \(\delta'\) is strictly positive. The failure is in the **sufficient angular-drift budget**, not existence, ordering or solvability.

## Independently recomputed 121-source direct-admission census

Against the **same immutable 121 V54 originals and 50 V2 complete source registrations**, with exact source IDs and preserved before/after denominator, independent Python Fraction source decoding finds:

| Direct unchanged #441 grammar/certificate category | All 121 | Historical 50 unresolved |
|---|---:|---:|
| Meets necessary original-source phase/affine H1/grid grammar | 4 | 2 |
| Fully satisfies exact per-grid-cell derivative and drift certificate | 2 | 1 |
| Not directly fully admitted | 119 | **49** |

The four structurally eligible originals are `harvested:verify_pb00701_v10:a3af56296a12` (admitted; historically certified), `harvested:v19:951efe10f570` (refused), the V10 `tail0` (admitted; historically blocked), and the selected V12 `tail0` (refused). The harvested V19 and V12 first-span algebra agrees and both refuse the drift bound. The V10 case already had complete V2 evidence. Thus **no new original closure** follows from the direct route, even where it admits a frozen original.

| Matched historical measure | Before | After | Delta |
|---|---:|---:|---:|
| Original sources | 121 | 121 | 0 |
| V54 uncertified routes | 20 | 20 | 0 |
| Missing ordered premises | 30 | 30 | 0 |
| Existing complete V2 original-source witnesses | 50 | 50 | 0 |
| REQUIRED PB/PO discharges | 0 | 0 | 0 |

Newly resolved case IDs: **none**. This census is a **direct unchanged application** boundary, not a universal source-grammar impossibility result. In particular, algebraic root decomposition, finer-than-quarter-grid subdivision with a different proved certificate, alternative component partitions and general analytic-event work remain valid research avenues.

## Independent verification and adversarial scope

Run on the literal PR head:

```bash
python3 research/machining-completeness/tasks/MC-038/pb00701_v12_phasegrid_admission_20261106.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
```

The machine receipt `pb00701-v12-phasegrid-admission-20261106.json` is **recomputed and byte-source pinned** by the executable. Tests challenge source and phase substitution, changed original knots, zero grid nodes, duplicate-key/nonfinite/big JSON inputs, genuine algebraic order-two tangency and two distinct exact algebraic roots separated by \(2^{-119}\). The last two controls are **synthetic arithmetic refusals/contrasts only**; they are not secretly added to the 121-source corpus or counted as a PB theorem. The verifier uses bounded local rational arithmetic; a resource refusal is never counted as mathematical zero.

## Disposition and next dependency unlock

This is a new **C** against an unchanged direct application of #441 to frozen category-3 V12, not an A or B. It does not contradict #441's proven restricted sufficient theorem or the accepted earlier V12 source-specific proof. Independent mathematical/source review and literal-head CI qualify the receipt; keep Draft on any failed gate. Existing #441 and #397 owners retain their branches and exclusive main integration rights. No shared proof/programme registry or current-state ledger mutation, V54 historical rewrite, native/STEP work, domain narrowing or production authorization follows.

**Next critical-path step:** formulate a reusable exact owner-to-consumer ordered sign-transfer interface that can admit **multi-event source spans with equal endpoint signs**, or certify a finer source-preserving partition with exact completeness and continuity. Require original-source case/phase/knot custody and exact sign/order/multiplicity/parity guarantees, then measure an actual historical ordered-premise delta. Maintain all 26 supported operations and full native engineering STEP contract.
