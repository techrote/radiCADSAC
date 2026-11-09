# A2 — separated-amplitude cyclotomic moments and exact sided germs

**Status:** Research-only Draft; A3's *restricted mathematical lemma* review is conditional GO ([review 5833085453](https://github.com/techrote/radiCADSAC/pull/471#pullrequestreview-5833085453)); engineering/receipt acceptance remains HOLD pending independent retest and exact-head validation. **Date:** 9 November 2026. **Evidence:** deterministic model, not native geometry, STEP or a complete event partition.

**Scope/ownership:** research/experimental/analytic-events/jets/** only. See [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100), [#324 A2 lease](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6751700697), and the earlier [12th-order MAX_JET_ORDER=10 budget counterexample](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6735298098). Historical 121 originals / 20 refused routes / 30 missing premises / 50 pre-existing complete witnesses, 26 machining operations, MC-B/MC-1 NOT_ESTABLISHED and production_authorized=false remain unchanged.

## Hypothesis, precise admitted grammar and falsifier

Existing rational-phase point machinery already uses cyclotomic jets and has a capped order 10. The independent A2 claim is stronger: *split polynomial amplitude by degree at the physical source point* and evaluate separate constant-amplitude trigonometric moment sequences. Prove a **structurally sharper local multiplicity bound** than the ordinary polynomial-modulated annihilator and preserve genuine spline-knot sides. No generic interior-root solution is claimed.

Admit a single analytic source piece

\[
F(t)=P_0(t)+\sum_{h\in H}\left(P_h(t)\cos(2\pi h(a+bt))+Q_h(t)\sin(2\pi h(a+bt))\right),
\]

with distinct positive integer harmonics H, rational polynomial amplitudes, and rational a,b,t0 with **b nonzero**. The h=0 sine channel must be canonical zero. The implementation further bounds harmonics to eight entries among 0..8, degree at most 3, cyclotomic field order at most 64, source interval inside [-4,4], absolute phase rate at most 4, source coefficients with rational numerator/denominator size at most 160 bits, and finite sign refinement through 96 Machin/Taylor terms. Resource refusal is NOT mathematical zero or undecidability.

**Falsifier:** Any legal input where the exact local order differs from the separated-moment minimum; where a signed reversal does not swap true spline-knot sides; where an identity-zero interval is mistaken for one physical point event; or where a forged receipt is accepted.

## Theorem: separated-amplitude exact local valuation

Let s=t-t0, and expand each amplitude as its actual rational Taylor polynomial about t0. Group by the amplitude power j:

\[
F(t_0+s)=\sum_{j=0}^{d}s^j A_j(\pi s).
\]

Here A_j(z) is a **constant-amplitude** finite trigonometric sum with algebraic root-of-unity base phase and angular increment 2hbz. Write its Taylor series A_j(z)=sum_k a_{j,k} z^k, with every a_{j,k} in an exact cyclotomic number field Q(zeta_N). Then

\[
[s^n]F(t_0+s)=\sum_{j+k=n} a_{j,k}\pi^k.
\]

**Proof:** Because t0, a, b are rational, all fixed-phase sine and cosine values are algebraic. Each Taylor coefficient above is algebraic. Pi is transcendental over the algebraic numbers. Thus the sum vanishes *iff every coefficient of every distinct power of pi vanishes*. For a fixed n, different amplitude degrees j give different k=n-j, so they cannot cancel. Let r_j be the first k with nonzero a_{j,k}, or infinity if A_j is identically zero. It follows exactly that

\[
\boxed{\operatorname{ord}_{t_0}F=\min_{j:r_j<\infty}(j+r_j).}
\]

If all r_j are infinite, the analytic source piece is identically zero, not a finite-order point root. This is a point-local identity, not a global root-count result.

For each active j, let m_j be the number of nonzero positive harmonic pairs and delta_j=1 if its true zero-frequency coefficient is nonzero. The classical constant-coefficient ODE annihilator

\[
D^{\delta_j}\prod_{h\in H_j}\left(D^2+(2hb)^2\right)
\]

has order M_j=delta_j+2m_j. ODE uniqueness proves 0<=r_j<=M_j-1; the local algorithm needs at most M_j exact algebraic moment tests per amplitude degree. With total max amplitude degree d, union harmonic count m, and constant-channel presence delta, a nonzero analytic source has

\[
\operatorname{ord}_{t_0}F\le d+\delta+2m-1.
\]

Compare the ordinary polynomial-amplitude ODE ceiling N-1, where N=(d0+1)+2 sum_h(d_h+1), omitting inactive channels: the new bound is often much smaller. The infinite family (t-t0)^d (1-sin(theta))^m, at theta(t0)=pi/2, achieves order d+2m and attains this sharper ceiling when the harmonics are 0..m. It includes the previous degree-zero order-12 example as m=6,d=0 and a prospective order-17 cubic-amplitude example as m=7,d=3.

Exact vanishing is checked via residues modulo Phi_N; the first nonzero coefficient's sign is independently enclosed using rational bounds for pi and sine/cosine with Lagrange remainders. The right germ takes that sign, the left germ multiplies it by (-1)^order. If the finite interval refinement has not proved strict sign, return a typed refusal; mathematical sign decidability does not override a runtime cap.

## Genuine B-spline knot and source reparameterisation

The standalone adapter authenticates an actual **clamped rational-control polynomial B-spline**, not a purported pair of lowered spans. It admits degree p=1..3 and complete knot vector [L] repeated p+1 times, [K] repeated p times, then [R] repeated p+1 times, L<K<R. Two polynomial Bernstein/Bezier spans are reconstructed exactly from the 2p+1 shared controls per Fourier channel. The p-multiple interior knot is truly C0: only the actual value must agree; left/right derivatives may differ.

For the prospective cubic example, complete knots [0,0,0,0,1,1,1,2,2,2,2], h0 cosine controls [1,1/3,0,0,0,0,-1], sine controls all zero, phase in turns t/4, the real source lowers to F_left=(t-1)^2 and F_right=-(t-1)^3. At physical knot t=1, the one-sided orders are 2/3 and outer signs +/−; count one physical zero and *no fabricated smooth global multiplicity*. Under negative signed reparameterisation t=2-u, the knot is still at u=1, the phase rate reverses and the sided orders become 3/2 with outer signs −/+.

The adapter also distinguishes a zero interval ending at a knot from a single isolated knot zero. Source receipts bind the whole supplied knot, phase and control vectors by SHA-256; they do NOT establish membership in historical frozen originals. Arbitrary NURBS weights, arbitrary internal knot patterns, nonrational event coordinates, degenerate rate b=0, and open-root enumeration remain outside this admitted implementation.

## Executable controls and status of verification

From repository root on the exact candidate branch:

~~~sh
python3 -m unittest discover -s research/experimental/analytic-events/jets -p 'test_*.py' -v
~~~

A local independent scratch counterpart passed **8 focused tests**, including 28 constructive Laurent-polynomial instances (harmonic count 1..7 × amplitude degree 0..3), exact cyclotomic quarter-turn checks for Phi_4/8/12/16/24/48/60/64, the order-12 counterexample, identity-zero/nonroot, a genuine C0 cubic spline knot, signed reversal, continuum-adjacent knot, source-receipt tampering, invalid knot vectors and typed resource refusals. Those tests are mathematical/model controls, **not hosted literal-head CI**, not original V54/V2 producing replay and not accepted repository capability. Exact-head GitHub CI and independent A3 source-critical review are still required.

Verifier interface: verify_receipt(source, t0, submitted) replays the entire source-bound exact computation; no supplied sign, order, source SHA or cost limit is trusted. B1 should independently assess whether a smaller moment-field witness can be checked without recomputation.

## A3 review response — parser and source-shape correction (9 November 2026)

Independent [A3 review 5833085453](https://github.com/techrote/radiCADSAC/pull/471#pullrequestreview-5833085453) found no counterexample to the normalized nonzero-rate rational-phase valuation lemma, but identified an implementation-resource defect: the string-to-`Fraction` conversion previously ran **before** the 160-bit numerator/denominator limit. An arbitrarily long literal (including a value that later reduces to `1/2`) could consume unbounded parse time/memory. The revised model refuses strings over **128 characters before conversion**. This admits the canonical decimal text of any 160-bit numerator/denominator pair (at most 101 characters including signs and slash) but intentionally refuses unusually padded noncanonical input. It also refuses malformed/non-list spline control arrays, rather than interpreting a seven-character digit string as seven control values or allowing `len(None)` to escape as `TypeError`.

**Falsifier:** An oversized rational literal reaches `Fraction`; a 160-bit canonical numerator/denominator is wrongly refused; a malformed control container is accepted or raises a non-typed exception; any previously admitted exact moment/knot receipt changes despite identical normalized input. The added standalone tests assert the first three classes plus existing full model controls. They do not establish full source-runtime or hosted qualification until they run against the literal revised PR head.

Review classification remains **mathematical restricted-scope conditional GO / implementation HOLD**. This correction is engineering hardening, **not a new theorem, expanded spline grammar, MC-B advancement or native-performance claim**. Resource refusal remains a nontruth outcome. A3 must independently recheck the changed parser and source-shape admission before any acceptance.

## Prior art, nonclaims and follow-on

This is an application/refinement of established **exponential-polynomial** and **cyclotomic** theory; novelty is not asserted. Relevant primary/academic sources:

- *Value distribution of exponential polynomials and their role in the theories of complex differential equations and oscillation theory*, Bulletin of the London Mathematical Society (2022): https://doi.org/10.1112/blms.12719 — polynomial-exponential independence, ODE context and known zero-order principles.
- Achim Schweikard, *Real Zero Isolation for Trigonometric Polynomials* (1992): https://research.uni-luebeck.de/en/publications/real-zero-isolation-for-trigonometric-polynomials/ — pre-existing exact constant-amplitude trig multiplicity algorithms.
- Patrikalakis, Maekawa and Cho, MIT Hyperbook B-spline algorithms: https://web.mit.edu/hyperbook/Patrikalakis-Maekawa-Cho/node18.html — established knot multiplicities and exact Bernstein extraction.
- Prior radiCADSAC [rational-phase point checker](../../../machining-completeness/tasks/MC-038/pb00701_rational_phase_point.py), plus [#100/6733118691](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6733118691), already give cyclotomic local jets and the basic polynomial-amplitude ODE bound; do not count those as A2 inventions.

A3 should independently try to falsify the separated-degree/pi-independence step, interval signs, tight bound and knot identity for negative rates, high degree, zero-frequency channels and tight resource cases. B1 should critique source identity, typed negative results, sided signs and compact certificate format. Neither review is preapproved or performed by the author.

**No MC-038 gate promotion; no historical source closure; no native or STEP claims; no changes to shared authority, registries, workflows or original evidence.** The next meaningful result is an independent review and exact-head test, not another already-complete V12 or V6 source witness.


## Second A3 correction: knot-source finiteness and input budget (9 November 2026)

**Status: deterministic source-contract correction, not a theorem extension.** A3 [review 5833649987](https://github.com/techrote/radiCADSAC/pull/471#pullrequestreview-5833649987) falsified the original resource claim: `tuple(map(rational, knots))` consumed arbitrary source iterators *before* checking the required knot count. A finite 100,000-entry iterable therefore required 100,000 parses, and an inexhaustible iterator never reached the refusal. This is a precise negative result about resource safety, not a counterexample to the cyclotomic local-valuation theorem.

**Repaired admitted grammar:** Knot vectors must now be exact built-in `list` or `tuple` objects of length `3p+2`, for integer B-spline degree `p in {1,2,3}`. This O(1) container/type/length check happens before converting any knots, so no unbounded iterator is touched and at most **11** rational knot conversions occur. The public `reversed_spline` helper enforces the same precondition before reversing and converting. Generator-backed, custom iterable, string, null, oversized and underlength vectors are **typed refusals**, not invalid physical-zero findings. This is deliberately narrower than accepting arbitrary iterables: finite materialization is an explicit source-ingress obligation and not silently inferred. The existing full knot-pattern and control checks still execute after conversion.

**Preregistered falsifier and test:** A 100,000-element built-in list, incorrect 12-knot tuple, string, null, finite generator and an iterator that raises on first consumption must each refuse before element conversion; the bomb iterator's pull count must remain zero even when attempting time reversal. A valid 11-element tuple must still lower its genuine C0 spline. `attempt(...)` must label all malformed inputs `RESOURCE_REFUSAL_OR_BLOCKED` with `is_truth_value=false`. The new `test_knot_count_checked_before_element_conversion` is a regression guard for this input budget. Mathematical generality remains the infinite rational polynomial-amplitude source family specified above; implementation budget and source-ingress constraints are separate from that theorem.

**Unresolved and independent review:** A1 #470's own analogous iterable budget is outside A2 ownership. A1 uses phase scale `pi` and A2/MC-038 `2pi`; B1 #473 supplies a *prospective typed equivalence envelope*, but authentic producer-to-envelope binding is still missing. A3 should execute the complete **literal revised-head** A2 module/tests and challenge both the conversion order and the restriction to built-in containers; B1 should review eventual source certificate integration. Hosted general-purpose CI without an explicit A2 invocation is not qualification.

No source-specific MC-038 witness is promoted. Historical 121/20/30/50, 26 machining operations, PB/PO open status, MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false` and native/STEP bans all persist.
