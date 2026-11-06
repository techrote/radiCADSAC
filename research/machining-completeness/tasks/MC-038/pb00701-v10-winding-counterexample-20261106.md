# MC-038 / PB-007-01 — source-pinned V10 phase-winding / physical sign-transfer obstruction

**Date:** 6 November 2026 (UTC). **Status:** bounded C research candidate; no required PB/PO discharge. **Evidence class:** \`DETERMINISTIC_MODEL\`. **Owner/write set:** this task-local verifier, this report, the JSON receipt and its dedicated CI only; main and shared proof/programme/77 ledgers stay with their existing integrator. **Expensive/native permit:** none requested or used.

## 1. Falsifiable route and exact original

Candidate shortcut \`GLOBAL_STRICT_PHASE_DIFFERENCE_MONOTONICITY_PLUS_ENDPOINT_KNOT_SIGNS_IMPLIES_NO_HIDDEN_SIGN_EVENTS\` assumes that a globally strictly monotone signed first-harmonic phase difference, together with equal external and internal-knot physical signs, suffices to assert no hidden physical sign events or at most one full-source event. This would incorrectly replace exact *ordered phase winding* with a one-bit monotonicity flag. The test falsifies this specifically defined shortcut; it is **not** a claim about the actual implemented #397 theorem, general analytic-event impossibility, or a proof that every category-3 case is solvable.

Historical **actual frozen** case:
\`composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0\`,
original-source SHA-256 \`57d3c14096ccedfb7faea5023f5a09bada2ca274748f2207c36d77bbc790927c\`,
canonical frozen-row SHA-256 \`c5ba85453dc65e0d18675353986394ae5b34af6219a741ce14af0c332ffc47cd\`.
Original source-time \`t∈[0,2]\`; true physical source knot \`t=1\`; phase turns \`-1/2+2t\`. Original full splines are H0 cosine zero with degree-zero knots [0,1,2]; H1 cosine one with the same degree-zero knots; H1 sine degree-one with knots [0,0,1,1,2,2] and controls [1/2,-1/2,-1/2,-1/2]. There are no other channels. The verifier re-reads the **immutable** Git blob \`5841c331579489b25caef38cd412bdbf286f9134\`, verifies the complete source and row hashes, and rejects changed grammar, source-time, source knots, coefficient vector or phase.

Historical V54 disposition is still **BLOCKED**, with its second source span refused by V43 (\`CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED\`). Prior V2 independent original-source registry blob \`e52d3baf3692a011cf86234eeaa992ef407d99fd\` already registers this exact source as \`COMPLETE_SOURCE_SPECIFIC\`. Therefore this argument **must not** be counted as a newly resolved historical source or an A reduction. It is a bounded independent source-bound falsification and explanatory ordered-event witness.

## 2. Complete mathematical witness on the original physical source

Set \(\theta(t)=2\pi(-1/2+2t)=-\pi+4\pi t\). Its original physical function is

\[
F(t)=
\begin{cases}
\cos\theta(t)+(1/2-t)\sin\theta(t),&0\le t\le1,\\
\cos\theta(t)-(1/2)\sin\theta(t),&1\le t\le2.
\end{cases}
\]

The pieces and phase agree at \(t=1\); in fact \(F(1)=-1\), so the true knot is **not** a physical zero. For each \(n=0,\ldots,8\), exactly \(\theta(n/4)=(n-1)\pi\). Hence the **exact** physical signs are

\[
F(n/4)=(-1)^{n-1}\in\{-1,+1\}.
\]

Thus \(F(0)=F(1)=F(2)=-1\), while the signs at the nine ordered quarter-nodes alternate. These are exact integer half-turn evaluations, not floating-point samples or a numerical zero scan.

On the first source span let \(\alpha(t)=\arctan(1/2-t)\) and \(\delta(t)=\theta(t)-\alpha(t)\). Because the H1 amplitude \(R(t)=\sqrt{1+(1/2-t)^2}\) is strictly positive, \(F(t)=R(t)\cos\delta(t)\). Exact differentiation gives

\[
\delta'(t)=4\pi+\frac{1}{1+(1/2-t)^2}>0.
\]

For any quarter-cell \([n/4,(n+1)/4]\subseteq[0,1]\), \(\Delta\theta=\pi\), while \(\alpha\) decreases by strictly less than \(\pi/2\), since \(1/2-t\in[-1/2,1/2]\) and the arctangent range is strictly inside \((-\pi/4,\pi/4)\). Thus \(0<\Delta\delta<3\pi/2<2\pi\). The ordered zeros of \(\cos\delta\) are spaced by \(\pi\), so there can be at most two zeros inside a quarter-cell. Endpoint values are nonzero and have opposite signs; every zero is simple because \(\delta'\ne0\), so an odd number of crossings is required. At most two and odd means **exactly one simple crossing in each of the first four quarter-cells**.

On the second source span \(\alpha(t)=\arctan(-1/2)\) is constant and \(\delta'(t)=4\pi>0\). Every quarter-cell has exactly \(\Delta\delta=\pi\), and opposite nonzero endpoint signs. Thus **exactly one simple crossing** is present in each of the remaining four quarter-cells.

All eight roots lie strictly inside disjoint rational isolating intervals
\((0,1/4), (1/4,1/2), (1/2,3/4), (3/4,1), (1,5/4), (5/4,3/2), (3/2,7/4), (7/4,2)\).
Their complete physical order, simple multiplicity, odd parity and alternating NEGATIVE/POSITIVE maximal sign cells follow without a root scanner, interval-width timeout or unproved global theorem. The exact root parameters need not be expressed in elementary form.

**Decisive falsifier:** globally strictly increasing \(\delta\), equal negative external signs and equal negative knot sign coexist with **eight distinct internal simple physical roots**. The shortcut cannot establish ordered sign-transfer, even in this exceptionally simple original first-harmonic grammar.

## 3. Adversarial scope, cost and refusal policy

The checked certificate only admits this exact original in its source-specific entry point. The reusable lemma \`proof_cell\` separately requires C=1, a linearly nonincreasing sine coefficient S with exact endpoint range \([-1/2,1/2]\), increasing affine phase and exact half-turn endpoints advancing by exactly one half-turn. These hypotheses guarantee an angle drift smaller than \(\pi/2\) per cell. Unsupported phase rates, changed knot/interval/source/time, rotated or missing harmonics, reversed orientation, non-lattice endpoints, H0 drift, other phase windings and source custody changes **refuse**. Zero/identity sources and quadratic tangencies do not satisfy this admitted grammar and are never inferred solved from endpoint signs. Synthetic cells at width \(2^{-120}\), using exactly proportionate phase rate, verify two closely spaced ordered simple crossings without a tolerance-based collapse; they are **test controls only**.

Computational work is bounded: pinned input reads at 300,000 bytes, two immutable Git-blob hashes, exact source and V2 identity checks, and eight rational cell certificates plus standard-library adversaries. No precision budget, wall-clock timeout, or numeric convergence criterion decides physical truth. Branch/source/CI errors must leave Draft/blocked.

## 4. Matched frozen historical census and acceptance boundary

| Measure | Before | After | Delta |
|---|---:|---:|---:|
| Original frozen V54 sources | 121 | 121 | 0 |
| Uncertified V54 routes | 20 | 20 | 0 |
| Missing ordered premises | 30 | 30 | **0** |
| Prior complete original-source V2 witnesses | 50 | 50 | 0 |
| New REQUIRED PB/PO discharges | 0 | 0 | 0 |

Newly resolved historical case IDs: **none**. The source's new winding argument is an independent C-style falsification of a specifically proposed endpoint/monotonicity shortcut, not a new general owner-to-consumer grammar proof; its pre-existing V2 complete result is explicitly recognized. The general coupled and sine-bearing analytic event theorem is still **unproved**. PB-007-01/02/03/04 and PO-02/04/05/07/08 remain OPEN. MC-B and MC-1 remain \`NOT_ESTABLISHED\`, all 26 operations remain supported, and source/journal/topology/durable-body/engineering STEP/native geometry authorization and evidence custody are unchanged.

## 5. Reproduce

\`\`\`sh
python3 research/machining-completeness/tasks/MC-038/pb00701-v10-winding-counterexample-20261106.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
\`\`\`

The dedicated GitHub Actions workflow checks out and prints the **literal PR head SHA** in each job; tests and source checks must pass on the final corrected head. Independent source-critical review and coordinator-approved merge/main readback are separate gates. Existing #397 main integration and other workers' write sets must not be disturbed.
