# MC-038 / PB-007-01 — Original V10 phase-alias event-key information-loss falsification

**Date:** 5 November 2026 UTC. **Claim:** bounded negative **C**, against the proposed phase-modulo-one-only event deduplication interface, not an existing accepted implementation. **Evidence:** \`DETERMINISTIC_MODEL\` (not native geometry, independent oracle or engineering STEP). **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Pre-implementation reservation:** [#324 comment 6664016659](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6664016659); [live-main amendment](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6664056975).

## Obligation, route and falsifier

The relevant still-open obligation is **PB-007-01**: source-matched physical event completeness, original-time exact ordering, endpoint/knot-sided physical sign and multiplicity/parity, with downstream PO-04/05/08 adjacency. The general analytic event theorem is an unproved target.

The specific **proposed** shortcut \`PHASE_MOD_ONE_EVENT_KEY_IS_COMPLETE_FOR_VARIABLE_AMPLITUDE_SOURCE\` constructs a physical event key using only the global phase reduced modulo one turn. It identifies/deduplicates candidate zero events at different source times whenever their phases agree modulo one, even though the original time-varying B-spline amplitude has not been retained. The falsifier is a single original source with an exact physical root \`r\` and another source-time point \`r+1/2\` with exactly the same phase modulo one but *nonzero* physical value.

A correct method that retains global source-time, original amplitude controls and independently certified source-bound event locators is **not** challenged. A phase-only candidate generator that retains source identity and separately resolves amplitudes is likewise not falsified.

## Frozen original source and producing identity

Original v54 case:

\`composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0\`

- Canonical original source SHA-256: \`57d3c14096ccedfb7faea5023f5a09bada2ca274748f2207c36d77bbc790927c\`
- Entire frozen row SHA-256: \`c5ba85453dc65e0d18675353986394ae5b34af6219a741ce14af0c332ffc47cd\`
- Original source parameter \`source-time-t\`, closed interval **[0,2]**, true original B-spline knot **t=1** (not an invented phase partition).
- Global affine phase in **turns**: \(\beta(t)=-1/2+2t\), angular phase \(2\pi\beta(t)=-\pi+4\pi t\).
- Original cosine harmonic zero \(H_0\): degree-zero, knots \([0,1,2]\), controls \((0,0)\).
- Original cosine harmonic one \(H_1\): degree-zero, knots \([0,1,2]\), controls \((1,1)\).
- Original sine harmonic one \(S_1\): degree-one, knots \([0,0,1,1,2,2]\), controls \((1/2,-1/2,-1/2,-1/2)\).
- No other harmonics. The original sine amplitude is continuous at the true knot: both sides have value \(-1/2\).

The historical V10 first source span was \`CERTIFIED\`. The second was refused by V43 with \`CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED\`, so the frozen *whole source* remains \`BLOCKED\`. The separately accepted v2 register already records this complete original as \`COMPLETE_SOURCE_SPECIFIC\`; the present result does **not** supply a new historical whole-source witness. The distinct \`tail100\` case, SHA-256 \`21a0dde2ee6783f4465ab0c23dbef08fc400a4c8f2169cc5b851a3b0c3f5e23b\`, is explicitly not substituted for \`tail0\`.

## Source-exact physical reconstruction

Original degree-zero and degree-one clamped B-spline basis extraction, before any analytic-root analysis, yields

\[
F(t)=\begin{cases}
-\cos(4\pi t)+(t-\frac12)\sin(4\pi t), &0\le t\le1,\\[2mm]
-\cos(4\pi t)+\frac12\sin(4\pi t), &1\le t\le2 .
\end{cases}
\]

This is the **actual original whole-source function**, not a separately invented proxy. Both formulas agree at the true knot \(t=1\), where \(F(1)=-1\). At both exterior endpoints \(F(0)=F(2)=-1\). Thus the source knot and exteriors are **nonroots**, and there is no discontinuity or identity-zero component in this source.

## Complete exact prefix events and physical orientation

For each \(k=0,1,2,3\), let \(I_k=(k/4,(k+1)/4)\). The factor \(\sin(4\pi t)\) has fixed nonzero sign \((-1)^k\) on \(I_k\). Its reciprocal cotangent is well-defined, and

\[
 F(t)=\sin(4\pi t)g(t),\qquad
 g(t)=t-\frac12-\cot(4\pi t).
\]

Throughout each \(I_k\),

\[
 g'(t)=1+4\pi\csc^2(4\pi t)>0,\qquad
 \lim_{t\downarrow k/4}g(t)=-\infty,\quad
 \lim_{t\uparrow(k+1)/4}g(t)=+\infty.
\]

These are exact analytic trigonometric limit and derivative identities; they are not numerical samples or interval-refinement stopping heuristics. By continuity and strict monotonicity, **precisely one root \(r_k\)** occurs in each strict rational bracket \(I_k\). It is *simple*, because \(F'(r_k)=\sin(4\pi r_k)g'(r_k)\ne0\); its physical derivative orientation is \((-1)^k\). Quarter-grid endpoints yield \(F=-\cos(4\pi t)=\pm1\), hence none is an additional root. The original prefix has four and only four simple interior roots, in strict increasing source-time order. Its signs alternate: \(-,+,-,+,-\).

## Complete exact tail events and physical orientation

On each original second-piece quarter bracket
\[
J_k=(1+k/4,\,1+(k+1)/4), \qquad k=0,1,2,3,
\]
\[
F(t)=\sin(4\pi t)h(t),\qquad h(t)=\frac12-\cot(4\pi t).
\]

Here \(h'(t)=4\pi\csc^2(4\pi t)>0\), with endpoint limits \(-\infty\) and \(+\infty\). Thus precisely one distinct *simple* tail root occurs in each \(J_k\), with derivative orientation \((-1)^k\). At the quarter-grid boundaries \(F=\pm1\), so there are no additional roots. **The whole original has exactly eight isolated, order-one physical roots**, with no closed continuum or exterior/knot event, and its nine physical nonzero cells alternate signs beginning and ending negative. This is a source-specific complete proof, not a new generic V43 certificate or repair of the old V43 refusal.

## Decisive phase alias

Choose the exact implicit root \(r_0\in(0,1/4)\), uniquely characterized by

\[
\cot(4\pi r_0)=r_0-\frac12.
\]

Its shifted alias \(r_0+1/2\in(1/2,3/4)\) lies **within the same original prefix span**, eliminating knot/child interpretation ambiguity. The original phase law gives

\[
\beta(r_0+1/2)-\beta(r_0)=2(1/2)=1.
\]

Therefore these two *different source times* have precisely identical phase modulo one turn and precisely identical sine/cosine values. However the original sine amplitude is affine in source time, so

\[
 F(r_0+1/2)-F(r_0)=\frac12\sin(4\pi r_0)>0.
\]

Since \(F(r_0)=0\), the alias point is **strictly positive**, not a root. In fact, a valid root also exists elsewhere in \((1/2,3/4)\), but its source-time coordinate is **not** \(r_0+1/2\). Both zero-status mismatch and positional error are fatal to the proposed phase-key-only event interface.

No phase wrap, rational grid scan, floating tolerance, bisection cap, integer overflow or timeout proves this conclusion. The proof uses the exact original rational B-spline identities plus established calculus for sine and cotangent on finite intervals. The classical analytic facts are reviewed in this RAG proof; the Python checker does **not** machine-formalize real analysis.

## Executable custody and falsification

\`pb00701_v10_phase_alias_boundary.py\` binds the two actual frozen Git blobs, canonical entire-row/source SHA-256s, original B-spline parameter/knot/controls/phase, original observed V43 failure, matching v2 already complete source evidence, 121 frozen IDs, the **exact 50-ID historical blocked-v2 set**, and full before/after evidence-class provenance. It uses rational arithmetic for original coefficients and phase alias. Its dynamically constructed machine receipt must match \`pb00701-v10-phase-alias-boundary-20261105.json\`. None of the synthetic variants is substituted into the frozen population.

\`\`\`sh
python3 research/machining-completeness/tasks/MC-038/pb00701_v10_phase_alias_boundary.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
\`\`\`

There are **21 adversarial refusals**: source/phase/knot/endpoint/control/historical-disposition changes, nonadmitted tangent/identity-zero/2^-100-close prospective variants and forged receipt/closure/gate fields. The latter three are **rejected as outside this exact source**, not proved absent as a general theorem. The finite verification cost is two pinned file reads (121 original rows and 50 source-specific evidence rows), bounded canonical hashes, a fixed small rational control reconstruction and exactly 21 mutation checks. Python integer arithmetic does not decide the analytic theorem. A corrupted input or failed check returns refusal/failure; resource limits are not truth.

## Frozen v54 census, proof status and dependency unlock

Pinned frozen corpus Git blob: \`5841c331579489b25caef38cd412bdbf286f9134\`. Pinned executable v2 evidence register Git blob: \`e52d3baf3692a011cf86234eeaa992ef407d99fd\`.

| Same pinned original population | Before | After | Delta |
|---|---:|---:|---:|
| Frozen original source cases | 121 | 121 | 0 |
| Historical uncertified source-route refusals | 20 | 20 | 0 |
| Historical missing ordered source premises | 30 | 30 | 0 |
| Already accepted complete source-specific witnesses | 50 | 50 | 0 |
| Newly resolved historical source case IDs | 0 | 0 | 0 |

**A: NOT ACHIEVED. B: NOT ACHIEVED. C: bounded negative mathematical finding only, subject to independent admission.** Specifically, no required PB-007-01/02/03/04 or PO-02/04/05/07/08 is discharged. The historical 20/30 refusals are *preserved* rather than overwritten, despite v2 whole-source evidence. The correct next theorem interface must carry **global source-time coordinates, original amplitude and source identity**, plus separately checked event locations, exact root orders/one-sided physical signs and actual knot-point semantics. This result eliminates only a lossy interface, not general analytic-event isolation, and must not be used as a proxy for wider blocker closure.

MC-B and MC-1 remain \`NOT_ESTABLISHED\`. All **26** supported machining operations remain mandatory. Preserve genuine geometry/positive-volume material, original process-time phase, journal, durable disconnected material bodies, topology and uncertainty semantics, conventional usable engineering STEP plus independent consumer, source/evidence custody and original failures. No native/paid campaign, production repo or domain narrowing is authorized. A separate coordinated integration session must source-review the exact final draft head, check literal-head CI, and only then consider a guarded merge and independently qualified landed-main runs.