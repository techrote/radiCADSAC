# MC-038 / PB-007-01 — Signed original-source roots evade phase-only lattice enumeration

**5 November 2026 · bounded mathematical route falsification C · DETERMINISTIC_MODEL**. Parent [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). [Prior exclusive scoped claim](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6652913045).

## Hypothesis, exact scope and evidence boundary

The precisely challenged shortcut, **GENERALIZED_SQUARE_PHASE_LATTICE_ENUMERATES_SIGNED_MULTI_HARMONIC_EVENTS**, extends the integer/half-integer phase-turn lattice plus affine amplitude-root enumeration of a *strictly nonnegative squared-component* source to an **arbitrary signed multi-harmonic** rational B-spline source, without a proof of possible inter-term cancellation roots. Falsifier: an authenticated original-source root outside every such candidate.

This is *not* an allegation that [draft PR #397](https://github.com/techrote/radiCADSAC/pull/397) actually makes this mistake. Its bounded theorem requires proven nonnegative square identities and refuses nonadmitted sine channels and amplitudes. The original physical V17 roots were already independently established for a different signed-multiplier claim in [merged PR #391](https://github.com/techrote/radiCADSAC/pull/391); this investigation identifies their distinct **candidate-completeness implication**, and does not count them as newly discovered mathematics or historical closure.

**Named obligation:** PB-007-01 (physical analytic events), downstream ordered physical sign transfer PO-04/05/08. This is not a general analytic-event decision theorem, a correction to an accepted V17 owner, or a discharge of any required PB/PO. Do not promote a failed candidate-only route into a universal impossibility.

## Exact historical source identity and original semantics

Frozen original **composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100**. Canonical source SHA-256 **e85d997c9f4d828b1b748c964b375c21e4acef1b1e9046e074b1f7e29011d08f**; original whole-row SHA-256 **41e86bc30392515873fb55bdd844d154236a81426fd3639c3bd5491dad30f05a**. Pinned v54 corpus Git blob **5841c331579489b25caef38cd412bdbf286f9134**, qualified v2 complete-source register blob **e52d3baf3692a011cf86234eeaa992ef407d99fd**.

Original source-time parameter t on **closed [0,2]**, genuine knot at t=1, global rational phase turns β(t)=t/4 and angle θ(t)=πt/2. Each present channel is a degree-one B-spline with original two-piece knots [0,0,1,1,2,2]; no artificial knot or reparametrization is introduced.

| Original physical harmonic | [0,1] B-spline controls | [1,2] B-spline controls |
|---|---|---|
| Cosine H0 | 0, 0 | 0, 100 |
| Cosine H1 | 1, −3/2 | −3/2, −3/2 |
| Cosine H3 | −1/3, 1/6 | 1/6, 1/6 |
| Sine H1 | −3/2, 1 | 1, 1 |
| Sine H3 | −1/6, 1/3 | 1/3, 1/3 |

Historical v54 status: **BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE** despite two individually CERTIFIED child spans. A pre-existing *COMPLETE_SOURCE_SPECIFIC* v2 witness already binds the original source hashes and interval. Neither original status nor witness is modified.

## Exact mathematical proof

On the actual first original piece [0,1], define a(t)=t−1/3, b(t)=2/3−t, R(t)=a(t)cosθ(t)+b(t)sinθ(t), and M(t)=−2+sin(2θ(t)). Using exact identities

\[
\sin(2\theta)\cos\theta=(\sin3\theta+\sin\theta)/2,\qquad
\sin(2\theta)\sin\theta=(\cos\theta-\cos3\theta)/2
\]

the four nonzero harmonic coefficients are exactly C1=−2a+b/2, C3=−b/2, S1=−2b+a/2, S3=a/2. Each coefficient agrees with the original B-spline endpoint values, so the original **physical** F(t)=M(t)R(t). The factor M∈[−3,−1] never vanishes; this is a strict exact bound.

On 0≤t<1/3, b cosθ>0 and R=b cosθ[tanθ−q(t)] with q(t)=(1/3−t)/(2/3−t). Exact derivative q′(t)=−1/[3(2/3−t)²]<0, while (tanθ)′=(π/2)sec²θ>0. Thus the difference is strictly increasing and any zero is unique and **simple**. At t=1/6, tan(π/12)=2−√3<1/3=q(1/6), since 3>(5/3)²; at t=1/4, tan(π/8)=√2−1>1/5=q(1/4), since 2>(6/5)². Consequently there is exactly one root r1∈(1/6,1/4). On [1/3,2/3], a,b≥0 with at least one positive and cosθ,sinθ>0, so R>0. The exact reflection R(1−t)=R(t) gives the only further simple root r2=1−r1∈(3/4,5/6). Their physical first-span sign sequence is **+,−,+**, and derivative crossing signs **−,+** because M<0. Neither root is a tangency or identity continuum.

Now compute the entire **strengthened** candidate set of the challenged method, including phase quarter-turn nodes in addition to integer/half-integer turns. On the original first span β∈[0,1/4] those phase nodes are t=0 and t=1; the affine carrier-amplitude zeros are a=0 at 1/3 and b=0 at 2/3. No multiplier zeros exist. The total candidate set is therefore exactly **{0,1/3,2/3,1}**. Both exact open root brackets are disjoint from all four candidates. A root enumerator restricted to these candidates necessarily misses **both** physical simple roots.

Original knot F(1)=2/3>0. On the right piece, harmonic-zero C0=100(t−1); all other coefficients are constant. Exact trigonometric bounds give |F′−100|≤2π<44/7, so F′>656/7>0, and F(2)=304/3>0. The original closed source therefore has exactly the two first-piece roots, without any knot duplication or omitted exterior root.

This is a **decisive counterexample to the precisely specified candidate-only extrapolation**, not a refutation of the square theorem on its own correct admitted domain, and not an impossibility proof for more general signed analytic-event methods.

## Reproducible executable evidence and adversarial controls

Run:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v17_signed_nonlattice.py --contract --self-test

The new checker intentionally reuses the source-matched [already merged V17 verifier](verify_pb00701_v17_negative_multiplier_sign_erasure.py): that module checks the original source and whole-row hashes, every actual B-spline control and phase, mathematical factorization, exactly two simple root brackets, true knot/tail signs, complete 121-case original census and 50-source v2 binding. It separately rechecks the new lattice candidate set and its failure. The full independent source-producer replay runs in the dedicated CI workflow, not as substituted stored success.

The checker also executes 15 inherited original V17 adversarial mutation refusals, five new candidate/bracket mutation refusals, three machine-claim mutation controls and three prospective exact nonclaims: an even tangency, two rational roots separated by 2^-99, and a formal identity-zero trigonometric expression. Prospective tests do **not** prove the general algorithm or create new historical source entries. No floating-point scan, arbitrary timeout or budget exhaustion establishes root absence or multiplicity.

## Frozen before/after evidence and strict nonpromotion

| Frozen census | Before | After | Delta |
|---|---:|---:|---:|
| Original sources | 121 | 121 | 0 |
| Historical route refusals | 20 | 20 | 0 |
| Missing ordered premises | 30 | 30 | 0 |
| Previously complete source-specific witnesses | 50 | 50 | 0 |

**Newly resolved historical case IDs: none.** This limited research result is C (negative candidate-route admissibility), **not** A or B. Evidence is **DETERMINISTIC_MODEL**, not native geometry, independent oracle or actual engineering STEP. PB-007-01/02/03/04 and PO-02/04/05/07/08 remain OPEN; MC-B and MC-1 remain NOT_ESTABLISHED. All 26 supported machining operations, physical source semantics, durable bodies, original journal, topology, usable conventional STEP, explicit native/paid permits and production prohibitions remain intact.

**Critical path:** a terminating general signed non-square nonconstant-amplitude multi-span event solver, capable of exact cancellation roots, identity-zero components, tangency, multiplicity, knot-sided physical germs and ordered physical sign transfer. This research PR stays DRAFT until an independent final-head mathematical/source review and guarded integration, then separate landed-main CI.
