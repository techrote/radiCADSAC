# MC-038 / PB-007-01 — V10 tail100 V43 refusal: exact simple crossing

**29 October 2026 | DETERMINISTIC_MODEL / source-bound proof only | issue #100**

This investigation corrects the **unverified** V10 research hypothesis recorded in [PR #283 merged checkpoint](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6487895645). The earlier prospective expression omitted the original half-turn phase offset and incorrectly suggested a root-free, positive tail. The actual frozen source contains an interior physical zero. This negative finding does not alter v54 history or the accepted V9-tail proof.

## Exact source, provenance, question

Frozen source: research/machining-completeness/tasks/MC-038/pb00701-finite-owner-corpus-v54.json, Git blob 5841c331579489b25caef38cd412bdbf286f9134, exact case ID:

composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail100

The pinned 121-case corpus records 11 V43 CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED refusals (one harvested, ten manufactured composites). The first original source span [0,1] in this case is V10 CERTIFIED; its second [1,2] is V43 BLOCKED; the whole historical v54 disposition is BLOCKED.

The original source parameter is source-time-t, denoted s, on [0,2]; exact phase turns are phi(s)=-1/2+2s. Clamped degree-zero/one source splines lower as follows:

| Channel | First span [0,1] | V43-refused span [1,2] |
|---|---|---|
| C0 | 0 | 100(s-1) |
| C1 | 1 | 1 |
| S1 | 1/2-s | -1/2 |

Every channel is continuous at s=1. The verifier checks complete original source/knot/control/degree identities, lowers the pieces through the pinned reviewed PR #283 source-lowering helper (Git blob 2a8079ee2cf012bc2a12794c4c5ff19ebd760007), and verifies the frozen owner/status/denominator. This is not an independent B-spline codec or a general V43 theorem.

## The half-turn sign error in the previous research lead

The correct original source expression on [1,2] is

\[
F(s)=100(s-1)+\cos(2\pi(-1/2+2s))-\tfrac12\sin(2\pi(-1/2+2s)).
\]

Writing theta(s)=4*pi*s-pi, this is equivalently

\[
F(s)=100(s-1)-\cos(4\pi s)+\tfrac12\sin(4\pi s).
\]

The original phase offset -1/2 reverses both first-harmonic trigonometric channels relative to the previously proposed expression with a positive cosine and negative sine. At theta(1)=3*pi, theta(2)=7*pi, one has exactly

\[
F(1)=-1,\qquad F(2)=99.
\]

The previous source-wide positive-sign hypothesis is therefore **falsified**; the actual physical function has at least one open root by continuity. Do not issue a closed-span POSITIVE certificate for this source.

## Exact uniqueness, sign and strict root bracket

Direct differentiation yields

\[
F'(s)=100-4\pi\sin(\theta(s))-2\pi\cos(\theta(s)).
\]

By absolute sine/cosine bounds and the classical exact rational inequality 3<pi<22/7,

\[
F'(s)\ge100-6\pi>100-132/7=568/7>0.
\]

Thus F is strictly increasing on the entire closed second span. It has precisely one simple interior root, with NEGATIVE physical sign before and POSITIVE afterward.

A sharper rational source-coordinate bracket follows without numerical trigonometry. At s=101/100, theta=3*pi+pi/25, and

\[
F(101/100)=1-\cos(\pi/25)+\tfrac12\sin(\pi/25)>0,
\]

using the exact quadrant relations 0<pi/25<pi/2, cos(pi/25)<1, sin(pi/25)>0. Since F(1)=-1, the unique root lies in (1,101/100). This is an exact sign/uniqueness witness, **not an algebraic defining polynomial or closed-form source root**.

## Deterministic controls

Execute from the repository root:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v43_v10_tail_crossing.py --contract --self-test

The verifier pins the corpus and prior helper Git blobs; checks the 121-case/11-V43-refusal denominator, source parameter, exact phase and knot/control continuity; verifies the rational endpoint/derivative bounds and the source-root bracket; and checks unpromoted domain/programme authority. Adversarial mutations alter phase offset/rate, harmonic source controls, source parameter, physical knot, harmonic inventory, case origin and historical V10/V43 owner/refusal/disposition.

## Limits and landing gates

This proves only one V43-refused source-span simple crossing; it does not replace the historical BLOCKED V43 owner, certify the whole multi-span source, solve cross-knot composition, or establish general V43 derivative authority, analytic zero termination, cross-owner ordered roots, native material/solid geometry or engineering STEP.

The 43-owner inventory, 121-case historical v54 evidence, #275, canonical operation journal, timed phase/provenance, positive-volume material, durable bodies/lineage, typed resource refusal/UNCERTIFIED, 26-operation domain and conventional STEP obligations remain unchanged. PB-007-01/02/03/04 remain OPEN; MC-B and MC-1 remain NOT_ESTABLISHED; production and paid/native work are not authorized.

Required before merge: passing literal-head focused and mc1-static checks, distinct technical/proof review of final head, expected-head-protected merge, reviewed-head/landed-tree equality, merged-main qualification and durable issue #100 checkpoint. No successor issue is created.
