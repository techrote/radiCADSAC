# MC-038 / PB-007-01 — Rational-amplitude H1 rephasing cannot eliminate frozen sine channels

**6 November 2026. Evidence:** \`DETERMINISTIC_MODEL\`, exact source-bound mathematics. **Claim:** one precisely bounded C falsification; not a general analytic event theorem, A reduction, B discharge, or native/STEP qualification.

## Question and falsifiable method

Proposed shortcut: \`H1_RATIONAL_AMPLITUDE_REPHASING\`. For the actual original H1 coefficient pair \((C(t),S(t))\), claim that a time-dependent real phase-frame function \(\phi(t)\), perhaps nonlinear, can replace the pair by a *single* cosine-harmonic with a **rational function** amplitude \(A(t)\) in original source time without losing coefficient orientation, adding harmonics, or changing the original physical source parameter. Formally the proposed representation is

\[
(C(t),S(t))=A(t)(\cos\phi(t),\sin\phi(t)),\qquad A(t)\in\mathbb R(t).
\]

The necessary exact identity is \(A(t)^2=C(t)^2+S(t)^2\) throughout the original interval. This is stricter than an arbitrary functional rewrite valid only after substituting one particular physical phase; it challenges the *coefficient-preserving H1 frame rotation* route only.

**Falsify this negative result** by showing that either pinned original's exact first-span coefficients or source identity are wrong, or providing a genuine real rational function \(A(t)\) satisfying the necessary identity on an open original interval. Numerical agreement, a fitted amplitude, phase aliasing or a refusal from a bounded search do not count.

## Original historical sources, not surrogate fixtures

Read the pinned source blob \`5841c331579489b25caef38cd412bdbf286f9134\` and accepted 50-source V2 register blob \`e52d3baf3692a011cf86234eeaa992ef407d99fd\`.

| Frozen case | Source SHA-256 | Original source and first-span H1 |
| --- | --- | --- |
| \`composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0\` | \`4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2\` | \([0,2]\), true knot \(t=1\), phase turns \(t/8\); \([0,1]\): \(C=t-\frac12,\ S=1\). Historical **missing ordered premise**. |
| \`harvested:verify_pb00701_v9:4e7b85fa122a\` | \`a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10\` | \([0,1]\), one source span and no interior knot, phase turns \(t/8\); \(C=1,\ S=t-\frac12\). Historical **uncertified V43 route**. |

For V9, exact original clamped cosine H1 degree-one Bernstein controls \([-1/2,1/2]\) and sine H1 degree-zero control \(1\) lower to these first-span polynomials. Harmonic-zero cosine controls are exactly zero; its second span is retained as a separate original piece rather than silently erased. For harvested V43, degree-one controls \([1,1]\) and \([-1/2,1/2]\) on the original \([0,1]\) give the displayed coefficients. Global phase is not reset at a knot.

The executable verifier independently extracts the exact first-span affine controls and verifies source SHA-256, producer, original spline knots, harmonic inventory, time, knot, phase, historical refusal category and the already accepted full V2 witness. It does *not* accept typed caller assertions of root positions or events.

## Decisive exact impossibility argument

On **each** selected original interval, the squared norm is exactly

\[
q(t)=C(t)^2+S(t)^2=(t-\tfrac12)^2+1
=t^2-t+\frac54.
\]

Its discriminant is

\[
\Delta=(-1)^2-4(1)(5/4)=-4<0.
\]

Over \(\mathbb C\), \(q\) has two **distinct simple roots** \(t=\frac12+i\) and \(t=\frac12-i\). Every square of a nonzero rational function in \(\mathbb R(t)\) (indeed \(\mathbb C(t)\)) has **even order at every complex zero and pole**. Therefore \(q\) is not a square in \(\mathbb R(t)\); a fortiori it is not a square in \(\mathbb Q(t)\) or in rational-polynomial/finite polynomial-spline amplitude grammar.

Thus no choice of \(\phi(t)\), even nonlinear and real-valued, can rotate either original \((C,S)\) coefficient pair to \((A,0)\) while retaining a rational-function amplitude on the first original open span. Neither adding a fixed phase offset nor choosing a variable rational-affine or nonlinear phase avoids this amplitude obstruction, *provided the proposed transformation remains coefficient-preserving and rational-amplitude*. This result does **not** prohibit a radical amplitude \(\sqrt{q(t)}\), a generalized analytic-event method, other independent function identities, or more harmonics. It is no claim of universal impossibility.

This is distinct from [PR #434](https://github.com/techrote/radiCADSAC/pull/434), which excludes **one constant** phase-frame rotation by two-vector determinants, and from [PR #432](https://github.com/techrote/radiCADSAC/pull/432), which proves that discarding H1 orientation and retaining only the norm cannot identify physical zeros. Here **all variable phase frames** are allowed but a rational-amplitude representation is required.

## Exact tests, stopping conditions and evidence

\`pb00701_h1_rational_rephase_obstruction_20261106.py\` verifies the source-custody and necessary norm identity using exact \`Fraction\` arithmetic. No sample grid, transcendental approximation, timeout, floating tolerance or resource cap proves non-square status. The symbolic negative-discriminant argument is finite and terminates after fixed-degree arithmetic; the selected original and V2 population are finite pinned records.

Adversarial checks include changed original controls, phase and source parameter, changed historical disposition, typed receipt promotion, duplicate JSON keys, nonfinite JSON, and an extremely small \(2^{-120}\) nonzero sine control which leaves the exact discriminant strictly negative. **Positive/nonclaim controls** include a Pythagorean coefficient pair \((3t,4t)\) with rational amplitude \(5t\), an even-order tangency \((t-\frac12,0)\) and an identity-zero coefficient pair \((0,0)\); the narrow negative discriminator must *refuse* these rather than claim impossibility. The latter cases are synthetic adversaries, not new frozen corpus sources or newly solved physical event roots.

The exact source read cap is 600 KB per pinned JSON artifact; inputs are bounded, and a cap or malformed file refuses without mathematical truth. Neither the verifier nor the receipt decides physical root count, multiplicity, sign, event order or parity for this grammar. The originals already have complete V2 signed source-specific evidence; those remain the authoritative event witnesses.

Reproduction from repository root:

\`\`\`sh
python3 research/machining-completeness/tasks/MC-038/pb00701_h1_rational_rephase_obstruction_20261106.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
\`\`\`

The adjacent JSON receipt is recomputed type-sensitively on every \`--contract\` execution. The dedicated workflow checks the literal PR-head SHA and runs these commands; independent mathematical/source review and post-merge checks remain required.

## Matched before/after and programme disposition

| Frozen measure | Before | After | Delta |
| --- | ---: | ---: | ---: |
| Original sources | 121 | 121 | 0 |
| Uncertified historical routes | 20 | 20 | 0 |
| Missing ordered premises | 30 | 30 | 0 |
| Existing complete signed V2 source witnesses | 50 | 50 | 0 |
| Required PB/PO discharges | 0 | 0 | 0 |

**Changed historical IDs: none.** The V9 missing-premise case and harvested V43 route-refusal case remain historically unchanged. The 50 source-specific V2 witnesses (49 finite, one continuum) are not recounted as new generic closures. No frozen audit, historical failed proof or source artifact is rewritten.

**Next critical-path action:** develop an admitted sine-bearing, coefficient-orientation-preserving analytic-event and ordered physical sign-transfer theorem that works directly on original rational spline coefficients and global affine phase, or prove that a *different specifically proposed* algorithm fails. Unjustified rational-amplitude rephasing is excluded for these source anchors, but the full target theorem remains open.

PB-007-01/02/03/04 and PO-02/04/05/07/08 remain **OPEN**; MC-B and MC-1 remain \`NOT_ESTABLISHED\`. This exact bounded C has no native geometry, independent oracle or genuine engineering STEP evidence. All 26 supported machining operations, original source/knot/phase, journal, durable disconnected bodies and topology, mandatory STEP and evidence custody remain unchanged. No native/paid campaign or production repository is authorized.
