# MC-038 / PB-007-01 — positive original V23 source with physical derivative sign reversal

**Status:** bounded mathematical negative result C, pending PR review/integration (4 November 2026). **Evidence:** DETERMINISTIC_MODEL. Parent [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100); [preregistration](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6637934041); [exclusive ADD-only path claim](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6637933168).

## Exact falsifiable route

The candidate **GLOBAL_SINGLE_DERIVATIVE_SIGN_REQUIRED** asserts that proving a single, global sign of the *physical* derivative on the complete original analytic source span is a **necessary** admission premise for certifying the lack of open physical roots. This source falsifies that necessity. The sufficient use of monotonicity where independently proved, or piecewise derivative analysis with complete event and boundary evidence, is not being challenged.

Historical source: **harvested:verify_pb00701_v52:2250401ce435**; canonical specification SHA-256 **4a3ee3f47b9347429c13830abef382301c7963b0af518f0977390c2d3ffba040**. Literal source parameter **v52-original-source**, true interval **[0,1]**, affine phase turns **1/4 - t/24**, one original fully clamped Bernstein span with **no internal knot**. Historical V23 route owner **PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR** refused **NONCONSTANT_AMPLITUDE_PHASE_DEPENDENT_ANCHOR_NOT_CERTIFIED**. The historical refusal cannot itself establish nonmonotonicity; this new proof uses exact derivative signs from the original controls.

The complete Fourier/source representation is

\[
F(t)=A_0(t)+A_1(t)\cos\theta(t)+B_2(t)\sin(2\theta(t)),\qquad
\theta(t)=\pi/2-\pi t/12.
\]

Original amplitudes are fully clamped polynomial B-splines, hence Bernstein polynomials on the original t coordinate:

| Channel | Degree | Exact ordered original controls |
|---|---:|---|
| A0 (cos harmonic 0) | 7 | 0, 0, 1/1512, 1/756, 13/7560, 37/20412, 13/7776, 49/34992 |
| A1 (cos harmonic 1) | 6 | 0, 0, 1/54000, 1/27000, 23/486000, 7/145800, 49/1166400 |
| B2 (sin harmonic 2) | 6 | exactly A1/2 controlwise |

Each channel degree n has n+1 repeated zero knots and n+1 repeated one knots. No additional harmonics, substitutions, phase resets or unrecorded endpoint values are admitted.

## Exact positivity and left boundary multiplicity

For a Bernstein basis \(B_i^n(t)\), with \(i\ge2\),

\[
B_i^n(t)=t^2\frac{n(n-1)}{i(i-1)}B_{i-2}^{n-2}(t).
\]

The first two amplitude controls are all zero, so each amplitude factors exactly as \(t^2 Q(t)\) with a lower-degree Bernstein Q. All A0 quotient controls are **strictly positive**, with minimum \(49/34992\); all A1 and B2 quotient controls are nonnegative. Since \(\theta\in[5\pi/12,\pi/2]\), both \(\cos\theta\ge0\) and \(\sin 2\theta\ge0\), and therefore

\[
F(t)\ge\frac{49}{34992}t^2\quad\text{for all }0\le t\le1.
\]

Thus there are **zero open roots**, and the only closed-source root is at t=0. Clamped Bernstein derivatives give

\[
F(0)=F'(0)=0,\quad
F''(0)=7\cdot6\cdot\frac1{1512}=\frac1{36}>0.
\]

The other harmonics contribute zero to the left second derivative because their amplitudes vanish at least quadratically and their trig factors vanish at t=0. Therefore the left exterior root has exactly analytic order **two**, with positive inward physical sign. Analyticity and F''(0)>0 imply \(F'(t)>0\) for all sufficiently small positive t, without choosing an approximate epsilon.

## Independently established negative derivative at the original right endpoint

For a fully clamped degree-n Bernstein amplitude, the right derivative is exactly \(n(c_n-c_{n-1})\), using the final two **original** controls. Hence

\[
A_0'(1)=-\frac{133}{69984},\quad
A_1'(1)=-\frac7{194400},\quad
B_2'(1)=-\frac7{388800}.
\]

Also \(A_1(1)=49/1166400\), \(B_2(1)=49/2332800\), \(|\theta'|=\pi/12\), \(|(2\theta)'|=\pi/6\). Bounding both sine and cosine in absolute value by one, and using the rigorous \(\pi<22/7\), gives the strict **physical F derivative** inequality

\[
\begin{aligned}
F'(1)&\le A_0'(1)+|A_1'(1)|+
            \frac{22}{7\cdot12}A_1(1)\\
     &\quad+|B_2'(1)|+\frac{22}{7\cdot6}B_2(1)\\
     &=-\frac{133}{72900}<0.
\end{aligned}
\]

The sign of F' is consequently **positive near 0 and negative at 1**, despite F>0 for every t>0. At least one interior stationary point exists by continuity of F'. No assertion is made about its count, whether it is a zero (it is not), or general nonmonotonic event decidability.

**Decisive C:** strict global single-sign physical derivative certification is not a necessary prerequisite to showing absence of open roots for this admitted original V23 source. Refusals, failed interval derivative certificates and resource caps are not treated as mathematical findings. A correct exact Bernstein/phase-sector alternative already proves this source's positivity and boundary order.

## Reproduction and falsification controls

The [source-bound verifier](pb00701_v23_nonmonotone_positive.py) recomputes the exact rational Bernstein quotient and right derivatives, binds **frozen corpus Git blob 5841c331579489b25caef38cd412bdbf286f9134** and **post-v54 v2 evidence Git blob e52d3baf3692a011cf86234eeaa992ef407d99fd**, checks original SHA-256 and historic owner/refusal, and compares the new [machine receipt](pb00701-v23-nonmonotone-positive.json) rather than trusting a declared PASS. A separate, already qualified [original V23 source witness](pb00701-v23-bernstein-source-research.md) remains intact.

The exact positive and negative controls exercise the original order-two exterior root and both derivative signs, identity-zero rejection, negative Bernstein controls, removed quadratic order, changed phase/source, wrong right derivative, receipt tampering and a **2^-100-close additional root** in the synthetic polynomial \(t^2(t-2^{-100})^2\). That close-root control is **rejected** by the strict Bernstein sufficient-condition grammar rather than falsely reported root-free. It is *not* a new historical-source event proof. No numerical root scan or resource timeout supplies truth.

Commands on a checked-out PR head:

    python3 research/machining-completeness/tasks/MC-038/pb00701_v23_nonmonotone_positive.py --contract --self-test
    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
    python3 tools/validate_machining_completeness.py --self-test

No native/paid execution is needed. Arithmetic consists of bounded exact rational arrays (degrees 7,6,6), limited JSON and pinned source identities; those resource limits yield refusals, not zero facts. A proof/theorem reviewer must independently verify the mathematical endpoint identities and literal source hash.

## Same-denominator historical before/after and gate protection

| Pinned source/provenance and evidence | Before | After | Delta |
|---|---:|---:|---:|
| Frozen original sources | 121 | 121 | 0 |
| Frozen historical route refusals | 20 | 20 | 0 |
| Frozen missing ordered premises | 30 | 30 | 0 |
| Preexisting whole-source V2 witnesses | 50 | 50 | 0 |
| Newly closed historical case IDs | 0 | 0 | 0 |

The selected V23 case already had **COMPLETE_SOURCE_SPECIFIC** evidence in V2. The result is a **new, precisely bounded negative C about one proposed proof route**, not A/B, not repair of the historical V23 owner, and not a newly closed original source. PB-007-01/02/03/04, PO-02/04/05/07/08, the general analytic event theorem and MC-B/MC-1 remain **OPEN / NOT_ESTABLISHED**.

The evidence is **DETERMINISTIC_MODEL**, not independent native geometry/oracle validation or engineering STEP. All 26 supported machining operations, journal, source semantics, multiple durable bodies, topology, original raw failures, independent STEP consumers and production restrictions remain unchanged. **Production authorization: false.** The 77 current-state ledger, shared proof/programme registries and historical v54 files were not edited. Draft PR must receive terminal exact-head CI and independent subsequent-source review before any protected integration.
