# A1-F7 — Short-window zero-capacity bound for polynomial-amplitude H0/H1/H2

**10 November 2026 · Research-only DETERMINISTIC_MODEL · Draft / HOLD.** Preregistered [#324 lease 6760347473](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6760347473). Accepted main at start: 48222d6c40b15ad42cc36d56e6d25f3b284e7fc9; A1 predecessor #470 at 2aa6fe5a2bfa9941a1c0516116453895bb531022. Three new A1-owned files only.

## Admitted mathematical grammar

For one nonidentically zero analytic span on a compact rational physical-time interval [L,R]:

\[
F(t)=P_0(t)+\sum_{h=1}^{H}\bigl(P_h(t)\cos(h\pi(a+bt))+Q_h(t)\sin(h\pi(a+bt))\bigr).
\]

The coefficients are rational polynomials, a,b are rational, b is nonzero, and harmonics are distinct positive integers. Define m0 = degree(P0)+1 when nonzero and 0 otherwise; mh = 1+max(degree(Ph),degree(Qh)) for nonzero harmonic pair and 0 otherwise. Set n=m0+2*sum(mh) and hmax to the maximal active harmonic or 0. All counts are **real zero multiplicities on one analytic continuation**, including endpoints. A nonsmooth knot has separate sided orders, not one global Taylor multiplicity.

Proof covers any finite H and polynomial degree. Executable admits H0/H1/H2, canonical rational coefficient bit length at most 128, individual polynomial degrees at most 16, and bounded cuts. Its supplied-source compiler handles only clamped degree-2 C0 two-span B-splines with rational knots [L,L,L,K,K,R,R,R], five rational controls per Fourier channel, and one rational affine phase. It reconstructs exact quadratic Bernstein polynomials with controls [0,1,2] and [2,3,4]. Shared control 2 proves coefficientwise continuity at this genuine *supplied* knot K. It does not authenticate repository physical-source ancestry, arbitrary knots or NURBS weights.

## Theorem — capacity ceiling, not complete isolation

**Classical short-interval disconjugacy lemma:** If hmax>0 and the closed interval I has length strictly less than 1/(hmax*abs(b)), a nonzero F has **at most n-1 real zeros counted with multiplicity** in I. If hmax=0, the same n-1 bound holds globally for nonzero polynomial P0.

For span width w, set N=floor(w*hmax*abs(b))+1, or N=1 for a polynomial. The N exact rational equal intervals have length strictly less than 1/(hmax*abs(b)). Consequently

\[
Z(F;[L,R])\le N(n-1).
\]

Roots on a subdivision boundary may be counted twice, harmless for an upper bound. For all-zero Fourier channels (n=0), the entire analytic span is a **zero continuum**: no finite isolated-root bound applies. Adjacent identity-zero pieces combine into maximal continua; the endpoints are not silently promoted to isolated points.

### Proof

Write D=d/dt, lambda_h=h*pi*b and L_h=D²+lambda_h². Operator D^m0 kills P0 and L_h^mh kills polynomial-amplitude harmonic h. On a *different* complex frequency j, L_h acts on e^(i*lambda_j*t) times polynomials via the triangular polynomial operator D²+2i*lambda_j*D+(lambda_h²-lambda_j²), invertible because the diagonal is nonzero. D is invertible on nonzero-frequency polynomial-amplitude spaces. L_h is degree-preserving and invertible on the zero-frequency polynomial component. On its own harmonic,

\[
L_h(e^{i\lambda_ht}P)=e^{i\lambda_ht}(P''+2i\lambda_hP'),
\]

and each application reduces positive polynomial degree exactly one without canceling the leading coefficient.

For each L_h on a short interval I, choose its midpoint c and u(t)=cos(lambda_h*(t-c)). The strict width assumption ensures u>0 on **the entire closed interval**. The identity

\[
L_h f = u^{-1}D\bigl(u^2D(f/u)\bigr)
\]

and Rolle's theorem, counting derivative multiplicities and endpoint zeros, imply that L_h lowers the total zero count by at most two; D lowers it by at most one. Intermediate transformed functions remain nonzero because the operator action on the selected surviving frequency is invertible.

If P0 is active, eliminate all nonzero harmonics with their L_h^mh, retaining a nonzero polynomial of degree m0-1. Differentiate m0-1 times to reach a nonzero constant. The total possible root-count loss is 2*sum(mh)+m0-1 = n-1.

Otherwise choose a surviving active harmonic j. Eliminate P0 with D^m0, other harmonics with L_h^mh for h different from j, and apply L_j^(mj-1). The result is a nonzero constant-amplitude sine/cosine combination. The total operator order is m0+2*sum_{h!=j}(mh)+2*(mj-1)=n-2. This final sinusoid has at most **one zero** on I because its adjacent zeros are spaced 1/(j*abs(b)) and our interval is strictly shorter. Hence the original F has at most (n-2)+1=n-1 real zeros with multiplicity. QED.

**Limit:** this does NOT locate, bracket, decide existence of, or assign signs adjacent to unknown roots. For arbitrary integer k>0 the three degree-two polynomials t(t-2^-k), t² and t²+2^(-2*k) have the same capacity 2 but respectively two arbitrarily close simple zeros, one double tangency and no real roots. No root separation, exhaustive event atlas or general termination follows.

## Source identity, genuine spline knots and negative controls

Supplied H0 controls [0,0,0,0,1], L=0,K=1,R=2, all other channels zero, reconstruct an exact real quadratic C0 B-spline with F=0 on [0,1] and F=(t-1)² on [1,2]. The zero set contains continuum [0,1], not an isolated knot point {1}. H0 controls [1,0,0,0,2] produce order-2 zero germs on both sides of K, but unequal leading coefficients. Therefore knot topology is typed SIDED_GERMS_REQUIRED, never a global knot Taylor order.

For 1-cos(2*pi*t) on [-1/8,1/8], n=3, and the double zero at 0 saturates capacity 2. Signed negative b leaves capacity unchanged. |b|=7/3 over [0,1] generates three strict windows. The test module also constructs 72 exact factored rational polynomials of degrees 1..12 with known roots saturating their capacity; separate close-root controls reach 2^-96. Identity-zero continua, forged input/receipt/source identity, hostile Python equality objects, invalid rationals, unsupported splines, zero phase-rate and finite-budget refusal are explicit adversarial tests.

The SHA-256 claim is over canonical **supplied** source data only, not signed original-source custody. The checker recomputes its receipt and refuses hostile Python value types instead of trusting dictionary equality. Failure of budget admission is NONTRUTH, never a no-root result. A consumer must obtain true source/knot ancestry independently from #462, with A2/B1 sided event contracts.

## Commands, budgets and prior art

From research/experimental/analytic-events/isolator run:

    python3 -m unittest -v test_zero_capacity.py

Standalone CPython stdlib; exact Fraction arithmetic for all source and cut calculations, no numeric trigonometry, paid/native work, STEP generation or physics code. Bit limit 128 for coefficient rational components; degree limit 16; n<=128; N<=256 per span; two clamped C0 quadratic supplied spline pieces. Cost is exact polynomial reconstruction plus O(N) rational cut output; not a native execution cost claim.

This is **classical generalized Rolle/disconjugacy/Chebyshev-space reasoning applied to the project grammar**, not a novel mathematical theorem or universal decidability result. See W. A. Coppel, *Disconjugacy*, LNM 220 (Springer, 1971), S. Karlin and W. Studden, *Tchebycheff Systems* (1966), and [Chonev, Ouaknine, Worrell, ICALP 2016, DOI 10.4230/LIPIcs.ICALP.2016.100](https://doi.org/10.4230/LIPIcs.ICALP.2016.100) for the distinct hard problem of effective bounded exponential-polynomial zero decisions.

Existing [#453](https://github.com/techrote/radiCADSAC/pull/453) certifies bounded zero-free/single-simple-root cells, but refuses unresolved multiplicity and is not globally terminating; A1-F6 provides complete constant-amplitude H2 quartic events only. F7 gives a **necessary count ceiling for arbitrary polynomial amplitudes**, not an isolation route. It can falsify an impossible claimed count, but cannot certify a smaller count as complete. General nonconstant-amplitude transcendental tangency, physical-time order and arbitrary-knot source authentication remain open.

**Independent A3 falsifier requested:** attack positive-cosine factorization at closed endpoints, Rolle multiplicity accounting, surviving-frequency noncancellation, and true two-span knot continuity. Next highest-value theorem seam: effective existence/localization of transcendental multiple roots, not repeated frozen-original specimen proofs. Independent exact-head test replay is still a gate for integrating this research.

## Protected authority and disposition

Mathematical GO subject to A3 challenge; integration **HOLD**. No MC-038 proof registry/producer, main, production, native, STEP, engine, evidence census or protected authority change. Historical **121 original / 20 refused / 30 missing / 50 complete**, all **26 machining operations**, PB/PO OPEN, MC-B/MC-1 **NOT_ESTABLISHED**, and production_authorized=false remain unchanged.
