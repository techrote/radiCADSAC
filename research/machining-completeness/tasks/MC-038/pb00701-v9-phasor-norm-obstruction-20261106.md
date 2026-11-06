# MC-038 / PB-007-01 — original V9 phasor-norm-only event decision is impossible

**Date:** 6 November 2026. **Evidence:** \`DETERMINISTIC_MODEL\`; exact analytic counterexample for a *specified candidate information-loss route*. **Outcome requested:** bounded negative **C**, not MC-B or PB-007 acceptance. The companion source below is an admissible-grammar *synthetic adversary*, not another frozen historical case. See the adjacent JSON receipt and executable for source matching.

## 1. Precise route and falsifier

Proposed restricted route \`COMMON_H1_PHASOR_NORM_ONLY_ZERO_DECISION\`: for a rational two-span first-harmonic source

\[
F(t)=C_1(t)\cos\theta(t)+S_1(t)\sin\theta(t),\quad
\theta(t)=2\pi(\alpha+\beta t),
\]

discard the coefficient-vector *orientation*, retain only its algebraic squared norm
\[
R^2(t)=C_1(t)^2+S_1(t)^2,
\]
the exact source time, true knots and phase law, and decide the complete physical zero count, zero order and signed cells from those retained data alone.

**Falsifier:** two sources with identical \((R^2,\alpha,\beta,\text{source time},\text{knots})\) but different physical zero sets. Then no deterministic or terminating method whose *entire decisive input* is that projection can provide the correct answers for both. This says nothing about a method that retains \(C_1,S_1\) and the phase correlation. It is **not** a claim made about PR #397's restricted sine-free square theorem; this is a hypothetical proposed *extension* to sine-bearing sources.

## 2. Pinned original and baseline

Actual frozen V54 case:

\`composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0\`

- Frozen 121-case V54 corpus Git blob: \`5841c331579489b25caef38cd412bdbf286f9134\`.
- Complete 50-case V2 registry Git blob: \`e52d3baf3692a011cf86234eeaa992ef407d99fd\`.
- Canonical original \`spec\` SHA-256: \`4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2\`.
- Complete V54 case-row SHA-256: \`406ec73609a8213051afd3361478416e496c782b2b89ae2a857b772146059279\`.
- Owner source: \`verify_pb00701_v10\`; first span \`PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO\`, second \`DELEGATED_V6_CONSTANT_MODULATION\`.
- Original source time \(t\in[0,2]\); genuine C0/C1/S1 B-spline knot \(t=1\); phase turns \(p(t)=t/8\), so \(\theta(t)=\pi t/4\).
- H0 is identically zero, C1 has degree-one clamped controls \((-1/2,1/2,1/2,1/2)\) and knots \((0,0,1,1,2,2)\), S1 has degree-zero controls \((1,1)\) and knots \((0,1,2)\).

Exact rational B-spline lowering, with the original source parameter (not span-relative phase reinitialization), yields

\[
(C_1(t),S_1(t))=
\begin{cases}
(t-\tfrac12,1)&0\le t\le1,\\
(\tfrac12,1)&1\le t\le2.
\end{cases}
\]

This original was historically \`BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE\` in V54, **but already \`COMPLETE_SOURCE_SPECIFIC\` in the accepted V2 replay**. Its exact signed result is therefore preexisting; it cannot be counted as a newly resolved original.

## 3. Exact same-grammar companion

Construct a companion only by replacing S1 controls \((1,1)\) with \((-1,-1)\). All source time, knots, degrees, H0/C1 coefficients and affine phase are unchanged. Both rational B-spline piece joins remain continuous at \(t=1\). Write the frozen original as \(F_+(t)\) and the companion as \(F_-(t)\).

On each complete original-source span, both have identical squared coefficient norms:

\[
R_+^2(t)=R_-^2(t)=
\begin{cases}
(t-\tfrac12)^2+1=t^2-t+\tfrac54,&0\le t\le1,\\
\tfrac54,&1\le t\le2.
\end{cases}
\]

The norm is **strictly positive everywhere**, including the true knot. The phase law and knot positions likewise coincide. The two physically observed functions are nevertheless:

\[
F_\pm(t)=\begin{cases}
(t-\tfrac12)\cos(\pi t/4)\pm\sin(\pi t/4),&0\le t\le1,\\
\tfrac12\cos(\pi t/4)\pm\sin(\pi t/4),&1\le t\le2.
\end{cases}
\]

## 4. Rigorous distinct root sets, orders and signed cells

Let \(\theta=\pi t/4\), using the classical exact inequalities \(2<\pi<4\) and \(\tan x>x\) for \(0<x<\pi/2\). The latter follows strictly from \((\tan x-x)'=\tan^2 x>0\) on this interval and equality at zero. All calculations here refer to the original global \(t\) and its preserved phase.

**The original \(F_+\):** On \([0,1]\), \(\cos\theta>0\) and
\[
F_+(t)=\cos\theta\,[h(t)],\quad
h(t)=t-\tfrac12+\tan(\pi t/4).
\]
Now \(h(0)=-1/2<0\), \(h(1/2)=\tan(\pi/8)>0\), and
\[
h'(t)=1+\tfrac{\pi}{4}\sec^2(\pi t/4)>0
\]
on the whole first span. The intermediate value theorem and strict derivative give **exactly one** \(r\in(0,1/2)\), with derivative \(F'_+(r)=\cos(\pi r/4)\,h'(r)>0\): **multiplicity one**, odd parity and a NEGATIVE→POSITIVE crossing. For \(t\in[1/2,1]\) both terms of \(F_+\) are nonnegative and the sine term is positive. On the second span \(\theta\in[\pi/4,\pi/2]\); \(\tfrac12\cos\theta+\sin\theta>0\). Hence there are no other source, knot or endpoint roots, and precisely two maximal open signed cells \((0,r)\) NEGATIVE and \((r,2)\) POSITIVE. The knot is nonzero with value \(3/(2\sqrt2)>0\).

**The companion \(F_-\):** On \([0,1/2]\), \((t-1/2)\cos\theta\le0\) and \(-\sin\theta\le0\), with at least one term strictly negative, so \(F_-<0\). On \([1/2,1]\), \(\cos\theta>0\), and
\[
\tan(\pi t/4)>\pi t/4>t/2\ge t-\tfrac12,
\]
so \(F_-=\cos\theta\,[t-\tfrac12-\tan\theta]<0\). On \([1,2)\), \(\tan\theta\ge\tan(\pi/4)=1>1/2\), so \(F_-<0\); at \(t=2\), \(F_-(2)=-1\). Thus the companion has **zero physical roots** on the complete closed source and one maximal NEGATIVE nonzero cell. Its knot is nonzero with value \(-1/(2\sqrt2)\).

These conclusions use strict analytic inequalities and exact rational original-source lowering. They do not rely on sampled values, timeout, a subdivision cap or approximate root coordinates. They also establish termination for the *bounded decision*: a fixed finite number of exact source identity, rational coefficient and symbolic inequality checks; no unbounded refinement loop. The candidate norm-only route is falsified because it must return the same answer for the two identical projections, while the mathematically correct answers differ.

## 5. Adversarial and refusal scope

The machine checker reads and Git-blob-pins the actual 121-source V54 corpus and 50-source V2 evidence before selecting the original. It rejects source/phase/knot/harmonic/control substitution, broken continuity, changed historical counts, missing V2 prior evidence, altered machine conclusions and a Python \`True\` value substituted for an integer discharge count. It rebuilds the original exact clamped B-spline polynomials, flips only S1, and verifies the squared-polynomial identity over both spans with \`fractions.Fraction\`, not floating point.

Supplementary **synthetic, non-source-closure** algebraic controls show why amplitude-only projection cannot stand in for identity-zero, tangencies, endpoint germs or roots separated by \(2^{-120}\). They do not claim to discharge any part of the general theorem. The counterexample itself already settles the bounded C claim without these examples. A source-specific V2 signed proof already exists, so no duplicate proof is promoted to a new ordered premise.

The argument is an information-loss noninjectivity theorem for the **specified projection only**. It does not forbid a full coefficient-aware algorithm, show mathematical nonmonotonicity of a V43 refusal, establish impossibility of exact analytic root decision, or resolve general coupled spindle/feed/eccentric, topology or STEP tasks.

## 6. Independent reproduction and custody

From the branch checkout:
~~~sh
python3 research/machining-completeness/tasks/MC-038/pb00701_v9_phasor_norm_obstruction_20261106.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract --self-test
python3 tools/validate_machining_completeness.py
~~~

The adjacent machine receipt fixes 121 original-source IDs, 20 historical route refusals, 30 missing ordered premises and 50 preexisting complete V2 original-source witnesses **both before and after**, all with delta **zero**. Zero newly closed historical cases, zero required PB/PO discharges. This is \`DETERMINISTIC_MODEL\` plus a source-bound mathematical counterexample, not a native geometry run, independent geometry oracle, genuine engineering STEP or production authorization.

PB-007-01/02/03/04, PO-02/04/05/07/08 remain OPEN; MC-B and MC-1 remain NOT_ESTABLISHED; all 26 required machining operations, source semantics, body/topology/journal custody and evidence refusals remain intact. **No shared authority, historical evidence, ledger, acceptance register, native permission or production file is changed.**

## 7. Dependency conclusion

Reject \`COMMON_H1_PHASOR_NORM_ONLY_ZERO_DECISION\` as an approach to complete nonstationary sine-bearing ordered physical events. A viable successor must preserve the phase-correlated oriented coefficient channels (or prove an information-equivalent representation), with independently checkable exact zero/order/parity and sided-sign transfer. This is a narrow screening/falsification **C**, not a solution to PB-007-01. PR stays Draft until distinct-session source/CI admission and existing #397 main-integration custody are resolved.
