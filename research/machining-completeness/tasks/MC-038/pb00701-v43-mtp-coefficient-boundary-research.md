# MC-038 / PB-007-01 — Original V43 rational-MTP theorem-admission boundary

**Status:** 5 November 2026, qualified only after final-head source review and CI. **Evidence:** bounded mathematical negative result C, `DETERMINISTIC_MODEL`; no PB-007 or MC-B/MC-1 capability discharge. **Owner:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Claim reservation:** [#324/6646630527](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6646630527). **Preregistration:** [#100/6646636319](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6646636319). **Source-selection main:** `5f3f564888c0b28ced362ba3e71a64c67317ffa3`.

## Research question and named obligation

PB-007-01, relevant required PO-04/05/08, seeks exact event/zero/order/multiplicity and finite termination for rational-B-spline trigonometric original sources and source-time composition. These obligations remain open. A potentially useful published theorem exists:

Rizeng Chen, Haokun Li, Bican Xia, Tianqi Zhao and Tao Zheng, **“Isolating Bounded and Unbounded Real Roots of a Mixed Trigonometric-Polynomial,”** *Journal of Symbolic Computation* **121** (2024), article 102250, DOI [10.1016/j.jsc.2023.102250](https://doi.org/10.1016/j.jsc.2023.102250), [arXiv:2301.05847](https://arxiv.org/abs/2301.05847), [PDF](https://arxiv.org/pdf/2301.05847). Their defined mixed trigonometric-polynomial (MTP) class is `P(x,sin x,cos x)` with **P belonging to Q[X,S,C]**; the paper claims isolation of bounded roots and multiplicities without Schanuel's conjecture. Its scope is importantly more constructive than an open-ended appeal to general exponential-polynomial decidability.

**Falsifiable proposed shortcut:** `DIRECT_RATIONAL_MTP_PHASE_NORMALIZATION`: because original B-spline amplitudes and affine phase coefficients are rational in source time, the substitution to a single real radian phase coordinate `x=2πp(t)` always produces a rational-coefficient MTP, so the cited isolation theorem applies *verbatim*. Test a specific frozen originally refused nonconstant-amplitude source, not a synthetic analogue.

**Negative acceptance:** if exact source reconstruction and published rational coefficient grammar match, but the normalized function provably cannot equal any `P(x,sin x,cos x)` over Q, the shortcut is false for this original. **Refusal:** source, provenance, phase or mathematical field claims disagree; do not replace by scanning, a timeout, or sampled trigonometric values. This is NOT a finding that the cited method is incorrect or that no exact solver can exist.

## Pinned original source and physical semantics

The exact frozen V54 corpus is `pb00701-finite-owner-corpus-v54.json`, Git blob `5841c331579489b25caef38cd412bdbf286f9134`; the source-specific complete-evidence V2 register is Git blob `e52d3baf3692a011cf86234eeaa992ef407d99fd`. Both are unchanged.

- Original case ID: `harvested:verify_pb00701_v9:4e7b85fa122a`; producer `verify_pb00701_v9`.
- Canonical original source SHA-256: `a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10`.
- Original entire-row SHA-256: `62346bbddca22c4271a14c10aa130327013ac7cf8daa0b0ae515257e8f28cfad`.
- Original physical source parameter `source-time-t`, exact closed interval `[0,1]`; **one** fully clamped degree-one B-spline source piece, knot vector `[0,0,1,1]`, no true internal knot. Cosine H1 controls `[1,1]`; sine H1 controls `[-1/2,1/2]`; no other nonzero channels.
- Original phase in **turns** `p(t)=t/8`; physical angular argument `θ(t)=2πp(t)=πt/4`. This is the original source-time map, not an independent phase re-projection.
- Historical V54 `BLOCKED` at owner `PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF`, precise failure `CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED`. V2 already contains a `COMPLETE_FINITE_SOURCE_ZERO_SET` source-specific witness, so a new proof for this same ID must not count again.

The exact degree-one clamped Bernstein source gives cosine amplitude 1 and sine amplitude `t-1/2`. Therefore the physical function on the **original** closed interval is

\[
F(t)=\cos(\pi t/4)+(t-\tfrac12)\sin(\pi t/4),\qquad 0\le t\le1.
\]

The endpoint values are `F(0)=1`, `F(1)=3sqrt(2)/4>0`; **those endpoint signs alone do not certify absence of interior roots**. Root completeness remains the separately registered, previously accepted source-specific witness.

## The exact field obstruction

Normalize to the radian phase coordinate `x=πt/4`; hence `t=4x/π` and original domain becomes `0≤x≤π/4`. The exact transformed physical function is

\[
G(x)=\cos x+\left(\frac{4x}{\pi}-\frac12\right)\sin x.
\]

**Lemma 1 (rational MTP Fourier field).** For any `P∈Q[X,S,C]`, `P(x,sin x,cos x)` expands into a finite sum `Σ_k q_k(x)e^{ikx}` with `q_k∈Q(i)[x]`, since `S=(z-z^{-1})/(2i)`, `C=(z+z^{-1})/2`, `z=e^{ix}` and `Q(i)[x,z,z^{-1}]` is closed under finite polynomial arithmetic.

**Lemma 2 (unique finite exponential-polynomial coefficients).** If `Σ_k r_k(x)e^{ikx}=0` on any nonempty real open interval for finitely many distinct integer k and complex polynomial coefficients `r_k(x)`, all `r_k` vanish identically. Analytic continuation gives a complex-analytic identity. To isolate term j, apply `∏_{k≠j}(D-ik)^(degree(r_k)+1)`; it annihilates every other term and becomes an invertible polynomial differential operator on the remaining bounded-degree `r_j`, because every frequency difference `i(j-k)` is nonzero. This is the same standard independence principle already used in the repository's affine-phase identity analysis. It does not assume Schanuel.

**Lemma 3 (nonrational normalized coefficient).** The coefficient of `e^{ix}` in the transformed original is

\[
q_{+1}(x)=\frac12+\frac{4x/\pi-1/2}{2i}.
\]

Its coefficient of x is `2/(iπ)=-2i/π`, not an element of `Q(i)`, because **π is transcendental** (the standard Lindemann theorem), hence `1/π∉Q`. If some rational polynomial `P(x,sin x,cos x)` represented G on this interval, Lemma 1 would give a coefficient in `Q(i)[x]` at frequency 1; Lemma 2 would force equality with `q_{+1}`, a contradiction.

**C conclusion:** the exact original V43 source does **not** belong to the paper's rational-coefficient `Q[x,sin x,cos x]` MTP class after direct single-phase normalization. Rational B-spline controls in physical time do *not* automatically imply rational polynomial coefficients in the radian phase variable. The proposed **direct, unextended** theorem-admission shortcut is false.

This does **not** challenge the paper's root isolation theorem on its admitted class, prove that an extension to the effective coefficient field `Q(π)` is impossible, rule out a separate auxiliary-variable/cyclotomic method, or decide event isolation for the full PB-007 source grammar. No general undecidability assertion follows. The previously merged [V43 Cayley nonrationality challenge, PR #385](https://github.com/techrote/radiCADSAC/pull/385), concerns a different **tan-half-angle denominator-clearing** shortcut; this challenge specifically tests a distinct published **rational-MTP coefficient-field assumption**.

## Executable qualification, limitations and falsifiers

Entry point, Python standard library only:

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v43_mtp_coefficient_boundary.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
```

The first command checks both immutable Git blob identities; canonical SHA-256 of the exact full original row and source; original B-spline controls/knots, phase, owner/refusal; all 121 unique original rows; exactly 20/30 historically unresolved cases; and each of 50 V2 matching original-source/whole-row hashes with 49 finite and one continuum proof. It reconstructs the original linear amplitudes with rational operations. Finite exact Laurent-Fourier checks validate `sin²+cos²=1`, `2sin(x)cos(x)=sin(2x)`, and an admitted rational constant-amplitude control. Eleven negative source/owner/phase mutations fail closed. Prospective even tangency, identity-zero and roots separated by `2^-200` **do not acquire a source event/root classification from a coefficient-field proof**; they remain typed nonclaims. A matching machine receipt is checked on self-test.

The executable **does not mechanically prove** transcendence of π, exponential-polynomial independence or correctness of the published algorithm. Those are mathematical proof premises documented explicitly above; review must audit them directly. This is a bounded literature-admission falsifier with exact source binding, not a solver or a numeric experiment. Cost: two pinned local JSON reads (121+50 records), O(121+50) hashes/comparisons, constant-size rational Fourier checks and eleven mutations. No resource-cap result is counted as truth; no native or paid execution authorized. Actual GitHub exact-head/merged-main CI must separately qualify changed-head custody.

## Census and nonpromotion

| Frozen v54 / v2 measure | Before | After | Delta |
|---|---:|---:|---:|
| Unique original sources | 121 | 121 | 0 |
| Historical route refusals | 20 | 20 | 0 |
| Missing ordered premises | 30 | 30 | 0 |
| Registered complete original-specific witnesses | 50 | 50 | 0 |

**Newly resolved original IDs: none.** The source-specific V43 witness was already complete. Its old V43 refusal remains intact. PB-007-01/02/03/04, required PO-02/04/05/07/08 and the general nonconstant-amplitude/multi-span analytic-event and physical sign-transfer theorem remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`. No modification to all 26 required operations, original source meaning, manufacturing journal, durable bodies, topology/lineage, native STEP/independent consumer, proof/programme registry, production or campaign restrictions.

## Critical-path follow-up

Assess whether the published MTP root isolation proof can **actually be extended** to rational-affine-phase B-spline amplitudes over an explicitly certified coefficient field containing π and correct transformed interval endpoints, or find a different unconditional theorem that covers this exact source grammar. Any proposed extension must provide a complete terminating exact root/count/multiplicity/sign/order/refusal contract and independent original-source tests, not just citations or a field handwave. Reserve changes to shared programme/proof interfaces with the MC-038 owner, rather than amending the frozen V54 classifier or this historical source.
