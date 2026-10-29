# MC-038 / PB-007-01 — fixed original-source V27 ordered-root bridge

**Date:** 29 October 2026. **Owner:** [issue #100](https://github.com/techrote/radiCADSAC/issues/100). **Baseline:** `ffdb3278119b80fc0ac6e6b3bcf2bdd14e10b42d` (merged #290). **Evidence:** bounded deterministic-model mathematical research, not a generic ordered-child certificate, a revision of v54, or engineering/native capability.

## Scope, pinned custody and falsification

Only three original v54 records are considered: `harvested:verify_pb00701_v27:271ca62551a6`, `composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail0`, and its `tail100` counterpart. They come from the unchanged 121-case corpus Git blob `5841c331579489b25caef38cd412bdbf286f9134`. Their producing verifier is `verify_pb00701_v27`. Both manufactured sources retain their original historical owners and exactly **BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE** v54 dispositions; the harvested one remains CERTIFIED. The accepted degree-0/1 original B-spline lowerer remains pinned to blob `2a8079ee2cf012bc2a12794c4c5ff19ebd760007`.

The executable asserts complete original controls, knots, fully clamped pieces, physical continuity at the single source knot, source ID, exact global phase and literal historical owner/disposition. It rejects source and proof-report mutations. Any mismatch falsifies admission; a mathematical counterexample falsifies the analytical result. The checker deliberately does **not** run or promote the historical V27 choosing classifier or accept its child root-count summary as an ordered physical certificate.

## Original source and exact phase

The physical source parameter is `s` on [0,2], with phase turns `1/2 - 2s/3`; set `theta(s)=pi - 4pi*s/3`. The only positive harmonics are C2=1/100 and S1; the harmonic-zero channel is C0. On the first physical span [0,1], the original degree-1 sine spline has S1=2+4s, C0=5. On the second [1,2], the sine spline has S1=6; C0 is either 5 (`tail0`) or 5+100(s-1) (`tail100`). In all three expressions the oscillatory part is **exactly** `(1/100)cos(2theta) + S1 sin(theta)`. No rephasing or surrogate coefficients are allowed.

The exact source-turn boundaries are `s=0,3/4,1,9/8,3/2,2`, with phase turns `1/2,0,-1/6,-1/4,-1/2,-5/6`. They are sector proof boundaries, **not physical roots**. In particular, the source knot at s=1 is not a zero.

## First-span unique positive-to-negative crossing

[
F_1(s)=5+\tfrac1{100}\cos(2\theta(s))+(2+4s)\sin\theta(s).
]

On [0,3/4], theta lies in [0,pi], so sin(theta)>=0 and F1>=499/100>0. On [3/4,1], theta lies in [-pi/3,0], with sin(theta)<=0, cos(theta)>=1/2 and sin(2theta)<=0. Direct differentiation gives

[
F_1'(s)=4\sin\theta-\tfrac{4\pi}{3}(2+4s)\cos\theta+
\tfrac{2\pi}{75}\sin(2\theta)<0.
]

At s=1, `F1(1)=999/200-3sqrt(3)<0`, since `27>(999/200)^2`. Thus exactly one simple positive-to-negative root belongs to the strict physical bracket **(3/4,1)**. Both original two-piece sources share precisely this first physical span.

## Second-span root for tail0

[
F_0(s)=5+\tfrac1{100}\cos(2\theta(s))+6\sin\theta(s).
]

On [1,9/8], theta lies in [-pi/2,-pi/3], so sin(theta)<=-sqrt(3)/2 and `F0<=501/100-3sqrt(3)<0`, by the rational-square check `27>(501/100)^2`. At s=9/8, F0=-101/100. On [9/8,3/2], theta lies in [-pi,-pi/2], so cos(theta)<=0, sin(2theta)>=0, and

[
F_0'(s)=-8\pi\cos\theta+\tfrac{2\pi}{75}\sin(2\theta)>0
]

at every interior point of that interval. At s=3/2, F0=501/100>0; on [3/2,2], sin(theta)>=0, so F0>=499/100>0. Therefore **exactly one simple negative-to-positive root** occurs in **(9/8,3/2)**. No physical root occurs at the knot s=1.

## Second-span root for tail100

[
F_{100}(s)=100(s-1)+F_0(s).
]

Over [1,2], cos(theta)<=1/2 and abs(sin(2theta))<=1. With the standard rational strict upper bound pi<22/7, the full closed-span derivative obeys

[
F_{100}'(s)\geq100-(4+2/75)\pi
> 100-(4+2/75)\tfrac{22}{7}
=\tfrac{45856}{525}>0.
]

Here `F100(1)=999/200-3sqrt(3)<0` and `F100(9/8)=1149/100>0`. Therefore **exactly one simple negative-to-positive root** lies in **(1,9/8)**.

## Source-specific composition and required nonclaims

Both original two-span sources have precisely two simple **open** physical roots, one in the first physical span and one in the second. The strict source brackets are disjoint and rational, so their order is established without inventing algebraic or decimal root coordinates. The physical source is continuous and strictly **negative at the shared knot**, giving maximal open sign sequence **positive / negative / positive**; no knot zero or analytic multiplicity across a nonsmooth source knot is inferred.

This single-source-family construction is **not** the missing general V27/V41 checked nested-child composition theorem. It cannot consume arbitrary V27/V41 child route summaries, infer missing multiplicities or certify other category-3 owners. The 121 v54 dispositions, 43-owner inventory, all 26 machining operations, phase/source/provenance/canonical journal/material/body/lineage/refusal/`UNCERTIFIED` semantics, conventional usable STEP obligations and production hold remain unchanged.

## Reproduction, evidence and follow-up

Run `python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v27_fixed_source_order.py --contract --self-test`. The original-source checksum and authority checks use Python standard library only. The exact-rational arithmetic tests complement the explicit analytic sector proof above; they do **not** mechanically verify a generic trigonometric theorem. The focused workflow and `mc1-static` must pass on the exact PR head; distinct AI-assisted technical review must inspect the exact source/proof before any protected merge. If the current head changes, review and CI must be refreshed.

Remaining research: develop an independently checkable general interface for V27/V41 child ordered views and multiplicity/one-sided sign transfer, including mixed owners, endpoint zeros, tangencies, resource refusal and source knots. A historical count-only certificate cannot be promoted to a view merely because this fixed source admits its own proof. Issue #100 and PB-007-01 remain open; MC-B/MC-1 remain `NOT_ESTABLISHED`; native/B-rep/STEP and production authorization remain false.
