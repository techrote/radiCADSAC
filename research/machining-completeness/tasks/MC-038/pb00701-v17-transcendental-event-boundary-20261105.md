# MC-038 / PB-007-01 — Both original V17 physical event coordinates are transcendental

**5 November 2026 · bounded negative C · DETERMINISTIC_MODEL.** Parent: https://github.com/techrote/radiCADSAC/issues/100. Preimplementation ownership and exact hypothesis: https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6655142630.

## Falsifiable proposed route and mathematical consequence

The precise candidate ALGEBRAIC_COORDINATES_ONLY_FOR_ALL_RATIONAL_AFFINE_PHASE_PHYSICAL_EVENTS asserts that the physical zero events of every original rational-B-spline / rational-affine-phase harmonic source have algebraic coordinate values. A root enumerator whose **event coordinates themselves** must be algebraic numbers, each represented by an exact polynomial over the rationals, would then be complete.

We disprove this property for two interior roots of one actual frozen source. This is a substantive mathematical distinction from the previously demonstrated phase-lattice omission in merged #402: **the roots themselves are transcendental**, not merely off a proposed rational candidate lattice. The result does not affect an interface that represents a transcendental root *implicitly* by an exact defining analytic function and verified rational brackets. The existing v2 witness does exactly that. No claim is made that all analytic root isolation is impossible or that an accepted implementation uses the falsified shortcut.

Named blocker is PB-007-01; downstream PO-04, PO-05 and PO-08 require exact root order, multiplicity and physical sign transfer. This result is negative route admission C, not a required full proof obligation discharge.

## Frozen physical source and independent identities

Original frozen case: composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100. Canonical source SHA-256 e85d997c9f4d828b1b748c964b375c21e4acef1b1e9046e074b1f7e29011d08f, whole-row SHA-256 41e86bc30392515873fb55bdd844d154236a81426fd3639c3bd5491dad30f05a. Original v54 Git blob 5841c331579489b25caef38cd412bdbf286f9134; v2 complete-source evidence Git blob e52d3baf3692a011cf86234eeaa992ef407d99fd.

Original source-time t lies on [0,2], has the actual knot t=1, global affine phase in turns t/4, and precisely the C0/C1/C3/S1/S3 degree-one B-splines on knots [0,0,1,1,2,2]. Original first-span controls: C0 (0,0), C1 (1,-3/2), C3 (-1/3,1/6), S1 (-3/2,1), S3 (-1/6,1/3); the second-piece controls are (0,100), (-3/2,-3/2), (1/6,1/6), (1,1) and (1/3,1/3). They are read and authenticated in the executable rather than treated as independent surrogate functions.

Exact trigonometric multiplication and original Bernstein controls give on [0,1]

\[
F(t)=\bigl(-2+\sin(\pi t)\bigr)
\left[\left(t-\frac13\right)\cos\frac{\pi t}{2}
+\left(\frac23-t\right)\sin\frac{\pi t}{2}\right].
\]

The multiplier lies in [-3,-1], so roots are exactly those of the bracketed carrier R(t). Strictly monotone tangent-minus-rational comparisons establish **exactly one simple root** r1 in (1/6,1/4). Reflection R(1-t)=R(t) gives exactly one further simple root r2=1-r1 in (3/4,5/6). There are no other first-span roots. The true knot has F(1)=2/3>0; the right original span is strictly increasing and positive. These are the existing source-specific root facts proved in accepted #391 and independently checked again in #402; no root is newly discovered here.

## New theorem: both implicit roots are transcendental

Write theta=pi*t/2. On either root interval cos(theta)>0 and the rational denominator used below is nonzero.

For r1 in (1/6,1/4), R(r1)=0 implies

\[
\tan(\pi r_1/2)=q_1(r_1)=\frac{1/3-r_1}{2/3-r_1}.
\]

The rational function q1 is strictly decreasing and satisfies q1(1/6)=1/3, q1(1/4)=1/5. Thus q1(r1) lies in (1/5,1/3), a strict subset of (0,1). For r2 in (3/4,5/6), the zero equation gives

\[
\tan(\pi r_2/2)=q_2(r_2)=\frac{r_2-1/3}{r_2-2/3}
\]
with q2(3/4)=5 and q2(5/6)=3; q2(r2) lies strictly in (3,5), a subset of (1,infinity).

**Case I — no rational root coordinate.** Suppose either root r is rational. Then u=q_j(r) is rational and finite, while z=exp(i*pi*r) is a root of unity. Hence z and z^-1 are algebraic integers. Their sum

\[
m=z+z^{-1}=2\cos(\pi r)=\frac{2(1-u^2)}{1+u^2}
\]

is both rational and an algebraic integer, so m is an integer. Since m is real and lies [-2,2], it is one of -2,-1,0,1,2. Rearranging yields (m+2)u^2=2-m. At m=-2 this equation is impossible. At m=-1,0,1,2 it requires respectively u²=3,1,1/3,0. The values 3 and 1/3 cannot be rational squares (their prime factor parity is odd); thus a rational finite u must belong to {0,-1,1}. But u on the first original root is in (1/5,1/3), and on the second in (3,5). Both contradict these possibilities. Neither original root is rational.

**Case II — no algebraic irrational root coordinate.** Suppose a root r is algebraic but irrational. Because q_j is a rational function over Q, the finite value u=q_j(r) is algebraic. The trigonometric half-angle identity gives

\[
z=e^{i\pi r}=\frac{1+i u}{1-i u}.
\]

The denominator is nonzero for real finite u; therefore z would be algebraic. But the **Gelfond–Schneider theorem** states that if alpha is algebraic, alpha is neither 0 nor 1, and beta is algebraic irrational, every complex value of alpha^beta is transcendental. Set alpha=-1 and beta=r. Since exp(i*pi*r) is one of the branches of (-1)^r (using log(-1)=i*pi), z is transcendental. Contradiction. The theorem is classical, not proved or machine-formalized by the repository checker.

Combining I and II, **r1 and r2 are transcendental real numbers**. Each is nevertheless a precisely defined source-ordered simple physical event, with certified rational open brackets and physical sign cells (+,-,+). Transcendental root coordinates can be ordered and refined rigorously; algebraic brackets are not algebraic roots.

Reference for the external theorem: Gelfond–Schneider (1934), with contemporary Lean formalization abstract at https://arxiv.org/abs/2603.24823 and theorem statement at https://en.wikipedia.org/wiki/Gelfond%E2%80%93Schneider_theorem. The algebraic-integer rational-square sublemma is proved above and checked by exact rational enumeration. A formal reduction of these V17 roots to that external theorem is given here; the repository tests inspect assumptions, not a formal theorem prover.

## Computational verification, refusal boundaries and cost

The exact source-bound checker verify_pb00701_v17_transcendental_event_boundary.py reads the **original** frozen 121-case source and full v2 50-case evidence from their pinned Git blobs, matches canonical SHA-256, 20 historical route refusals and 30 missing ordered premises, and reuses the already merged original V17 Fourier, knot, phase, root-bracket and nonzero-tail checker. It then independently checks rational tangent ratio endpoints, monotonicity numerator, integer/square contradictions, bracket separation, the source-class scope, receipt identities and strict nonpromotion. There is **no numeric scan and no timeout-as-root-proof**.

Run:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v17_transcendental_event_boundary.py --contract --self-test

The inherited V17 test performs 15 source/report mutation refusals and three prospective exact nonclaims. This leaf adds five source and five receipt mutations, and prospective tangency, identity-zero and 2^-99 separated close-root arithmetic checks. Source mismatches, insufficient hypotheses, out-of-grammar expressions and resource limits must refuse rather than infer algebraicity or zero truth. Input parsing uses the prior 350,000-byte bounded frozen-file checker; finite new rational checks consume constant arithmetic work. Full source-producer replay remains separate in the exact-head CI.

## Historical before/after census and protected programme claims

| Same frozen population | Before | After | Delta |
|---|---:|---:|---:|
| Original frozen sources | 121 | 121 | 0 |
| Historical v54 route refusals | 20 | 20 | 0 |
| Historical missing ordered premises | 30 | 30 | 0 |
| Already complete source-specific witnesses | 50 | 50 | 0 |

The historical V17 disposition remains BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE; v2 already supplies its complete-source witness, 49 finite-source sets and one continuum across the cohort. **Newly closed historical case IDs: none**. Result C falsifies only the algebraic-**coordinate-only** proposed route. It is neither a new frozen-source closure A nor full required PB-007 proof discharge B.

PB-007-01/02/03/04 and PO-02/04/05/07/08 remain OPEN, MC-B and MC-1 NOT_ESTABLISHED. Evidence is DETERMINISTIC_MODEL, not native geometry, independent oracle or actual engineering STEP. The 26 supported operations, phase and manufacturing source semantics, canonical journal, durable material bodies and lineage, topology, engineering STEP output contract, cost restrictions and production authorization=false remain unchanged. Frozen raw failures and historical audits are retained.

## Integration handoff

Only four ADD-only research/checker/receipt/workflow paths are owned on this branch, as reserved in #324. The authoring run must leave a draft PR, not merge or transition it to Ready; separate critical source and mathematical review and exact corrected-head CI are required. An integration agent must recheck live main, owner collision, original and v2 blobs, actual checkout/CI proof, literal head, corrected-head review, then guard and verify any merge with new merged-main CI. Existing #392/#397 and #100 comment ownership are not touched.
