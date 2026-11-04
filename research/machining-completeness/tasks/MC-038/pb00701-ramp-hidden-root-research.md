# MC-038 / PB-007-01 — exact positive-exterior hidden-interior-root counterexample

**Status:** source-bound deterministic-model mathematics; no general PB/MC gate claim.  
**Date:** 4 November 2026. **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100).  
**Pre-registered hypothesis and write set:** [#100 comment 6628861062](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6628861062).  
**Proof obligation tested:** PB-007-01 exact physical event completeness, category-3 ordered physical sign transfer across an original B-spline source knot.

## Original historical source authority

Frozen v54 original corpus Git blob: `5841c331579489b25caef38cd412bdbf286f9134`.  
Current 50-source supplemental proof registry Git blob: `e52d3baf3692a011cf86234eeaa992ef407d99fd`.  
Original case ID: `composite:DELEGATED_V6_CONSTANT_MODULATION:tail100`.  
Original canonical source SHA-256: `f6a0eb06c66af415fbb8abdfe62f9b36a2a2bf154e535d83307a80228e044ad5`.  
Historical v54 second-span owner/refusal: `PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION / BLOCKED / V27_CHILD_NOT_CERTIFIED`. First original span was certified by V6. The **historical v54 source is separately already proved source-specifically** by [the exact A=100 knot theorem](pb00701-v6-tail100-knot-source-research.md) and the current 50-source registry. Historical v54 labels do not change.

The source grammar is `RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE`: `source-time-t` in [0,2], affine phase turns `t/4`, true original source knot t=1, degree-one fully clamped H0 cosine spline knots [0,0,1,1,2,2] controls [0,0,0,100], and degree-zero H1 cosine spline knots [0,1,2] controls [1,1]. No sine channels.

## Falsified proposed shortcut, and exact source mutation

**Proposed (false) rule:** an exact zero at the original source knot and strictly positive values at both exterior endpoints are sufficient to conclude no further strictly interior root; equivalently, they do not suffice to label that knot TOUCHING or certify a complete ordered sign partition.

Retain the original source parameter, knots, spline degrees, phase law, H1 harmonic and zero sine channels. Change **only** the fourth H0 control 100 to the canonical rational A=3/2. New prospective-source SHA-256: `e4bd5090915c3ff4dac70092918b154b43b5233105b8c86575cf4cc1a8480f9e`. This is **not** any frozen v54 case and cannot increase historical source closure. The exact original-source lowering is

\[
F_A(t)=
\begin{cases}
\cos(\pi t/2), & 0\le t\le1,\\
A(t-1)+\cos(\pi t/2), & 1\le t\le2.
\end{cases}
\]

Both source pieces meet at F(1)=0. In both A=100 and A=3/2, the exterior values are **strictly positive**: F(0)=1 and F(2)=A-1>0. Coefficient equality and global smooth multiplicity at t=1 are **not** assumed.

## Mathematical proof of the extra exact root and signs

Write x=t-1 on the right source span. Its exact physical equation is

\[
G_A(x)=Ax-\sin(\pi x/2),\quad 0\le x\le1.
\]

Its right derivatives are `G'_A(x)=A-(π/2)cos(π x/2)` and `G''_A(x)=(π/2)^2 sin(π x/2)>0` for every 0<x<1. Thus the derivative is strictly increasing, and the graph is strictly convex; this is a theorem about a continuous real function, **not a numerical scan**. For A=3/2, the classical exact bound 3<π<22/7 implies `G'_A(0)=3/2-π/2<0`, while `G'_A(1)=3/2>0` and `G_A(1)=1/2>0`. Since G(0)=0, the function is initially negative, has one strict minimum and returns through zero exactly once in 0<x<1 with derivative strictly positive. There are **no** additional right-open roots, by strict monotonicity after the unique minimum and negativity before it.

The crossing is explicitly bracketed without approximations:

- At x=1/4: `G(1/4)=3/8-sin(π/8)<0`. Exact identity `sin²(π/8)=(2-√2)/4` and inequality `√2<23/16` (squaring: 2<529/256) give `sin²(π/8)>9/64=(3/8)²`.
- At x=1/2: `G(1/2)=3/4-√2/2>0`, since `9/16>1/2`.

Hence the new, unique simple strictly interior root r lies in the **source-coordinate bracket (5/4,3/2)**. It need not have a rational coordinate, and no artificial rational root value is invented.

On 0<t<1, cos(π t/2)>0. At the true knot, the left one-sided derivative is `-π/2<0` and the right one is `3/2-π/2<0`; each one-sided vanishing order is 1, with no global smooth multiplicity claim. Immediately to the right the physical sign is negative. The extra root r is simple and crosses from negative to positive. Maximal open sign cells are **(+,-,+)** and there are **two distinct closed-source roots**: t=1 and r.

For the original historical A=100, `G'_100(0)=100-π/2>0` and strict convexity makes the derivative positive throughout the right span. Thus there are no right-open roots and the true source knot t=1 is a one-sided-order [1,1] **TOUCHING** event with signs (+,+), one distinct root. This contrast falsifies the shortcut while maintaining positive exterior signs in *both* sources.

## Additional exact controls and admitted grammar

The bounded deterministic checker admits only a rational final H0 control A, preserving every other original source field and its producing frozen SHA. The selected exact proof divides rational A into:

- `0<=A<1`: strict convexity and G(0)=0, G(1)=A-1<0 imply G(x)<0 in the open right span, no extra root, right negative.
- `A=1`: strictly convex with G(0)=G(1)=0 implies G(x)<0 for 0<x<1; t=2 is a separately identified exterior endpoint zero.
- `1<A<=3/2`: G'(0)<0 and G(1)>0 prove precisely one simple right-open crossing.
- `A>=11/7`: the exact bound π/2<11/7 makes G'(0)>0; G''>0 then proves no right-open root.
- `3/2<A<11/7`: **REFUSAL**, because the deliberately coarse rational π bounds do not settle the derivative sign. This is *not* a proof of actual nonmonotonicity or impossibility. Negative A and noncanonical/binary/oversized rational input also refuse.

For a near-endpoint adversarial source choose A=1+2^-100. Its extra root r is **very close to t=2**. At local x=3/4, `G(3/4)<0`, because `sin(3π/8)=√(2+√2)/2>√3/2>99/128>=3A/4`. For x in [3/4,1], `cos(πx/2)<=cos(3π/8)=√(2-√2)/2<2/5`, which follows from `√2>34/25`. Hence `G'(x)>1-(11/7)(2/5)=13/35>1/3`. The mean-value theorem yields `0<2-t_r<3*2^-100`; a finite approximation or root search is neither necessary nor authoritative.

Identity-zero mutation of the H1 channel is outside the admitted original anchor and **refuses**, not a fabricated isolated root list. The historical A=100 source is the touching control, A=1 the endpoint-root control, and A=3/2 the crossing control. The verifier also checks forbidden knot, phase, source-parameter, source-hash and certificate mutations, rational input bounds and every historical case/evidence source hash.

All admitted decisions use finitely many rational comparisons; for `3/2<A<11/7` the decision terminates in a nontruth refusal. The proof depends on explicit classical identities and calculus inequalities; it does not assert general decidability.

## Historical before/after and nonclaims

The unchanged pinned v54 historical case census is **121 total / 20 route-refused / 30 missing-ordered-premise**. The current reconciled registry already has **50 complete source-specific mathematical witnesses**: 49 finite and 1 continuum. This proof changes **none** of these numbers, source hashes, producer classifications or historical statuses; new historical IDs resolved = **0**. Its new slope-3/2 original B-spline source is a prospective adversarial case, not a v54 recovery. It falsifies only the stated sign/knot/exterior shortcut.

Evidence class: `DETERMINISTIC_MODEL`. PB-007-01/02/03/04, global theorem coverage, MC-B, MC-1, native material/topology, engineering STEP and production authorization are **not** established. All 26 supported operations and durable source/journal/lineage/body and refusal semantics remain unchanged.

## Reproduction and handover

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_ramp_hidden_root.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py --self-test
```

The attached `pb00701-ramp-hidden-root.json` is an exact recomputed machine receipt, not a historical-v54 rewrite. The GitHub Actions workflow checks the literal head and 50-source source/custody verifier. The earliest proof-owner H0–H2 two-span path is separately reserved; no shared proof/authority/77 ledger write is part of this leaf. Independent source review, literal-head CI and guarded main reconciliation are required before merge. Preserve any failed CI or refused candidate unaltered for audit.
