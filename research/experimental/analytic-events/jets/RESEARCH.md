# A2 — separated-amplitude cyclotomic moments and exact sided germs

**Status:** Research-only Draft; independent review outstanding. **Date:** 9 November 2026. **Evidence:** deterministic model, not native geometry, STEP or a complete event partition.

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

## Prior art, nonclaims and follow-on

This is an application/refinement of established **exponential-polynomial** and **cyclotomic** theory; novelty is not asserted. Relevant primary/academic sources:

- *Value distribution of exponential polynomials and their role in the theories of complex differential equations and oscillation theory*, Bulletin of the London Mathematical Society (2022): https://doi.org/10.1112/blms.12719 — polynomial-exponential independence, ODE context and known zero-order principles.
- Achim Schweikard, *Real Zero Isolation for Trigonometric Polynomials* (1992): https://research.uni-luebeck.de/en/publications/real-zero-isolation-for-trigonometric-polynomials/ — pre-existing exact constant-amplitude trig multiplicity algorithms.
- Patrikalakis, Maekawa and Cho, MIT Hyperbook B-spline algorithms: https://web.mit.edu/hyperbook/Patrikalakis-Maekawa-Cho/node18.html — established knot multiplicities and exact Bernstein extraction.
- Prior radiCADSAC [rational-phase point checker](../../../machining-completeness/tasks/MC-038/pb00701_rational_phase_point.py), plus [#100/6733118691](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6733118691), already give cyclotomic local jets and the basic polynomial-amplitude ODE bound; do not count those as A2 inventions.

A3 should independently try to falsify the separated-degree/pi-independence step, interval signs, tight bound and knot identity for negative rates, high degree, zero-frequency channels and tight resource cases. B1 should critique source identity, typed negative results, sided signs and compact certificate format. Neither review is preapproved or performed by the author.

**No MC-038 gate promotion; no historical source closure; no native or STEP claims; no changes to shared authority, registries, workflows or original evidence.** The next meaningful result is an independent review and exact-head test, not another already-complete V12 or V6 source witness.
