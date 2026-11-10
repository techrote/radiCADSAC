# A1 — Signed H2 square-lift from a transcendental-root H1 family

**9 November 2026 · Research-only · Draft/HOLD · independent A3 challenge requested.** This is a bounded positive certificate class, not an MC-038 gate result or a general terminating exponential-polynomial zero algorithm.

## Source baseline and preregistered falsifier

Accepted main: 48222d6c40b15ad42cc36d56e6d25f3b284e7fc9. Existing A1 Draft #470 source before this increment: 281705e947fd7812300d1d2605d3cdf60cdb005e. Scope of this increment: the new square_lift.py, test_square_lift.py and this report, exclusively within research/experimental/analytic-events/isolator/. Lease: [#324 comment 6753843681](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6753843681). Read [AGENTS.md](../../../../AGENTS.md), [DR-0026](../../../../docs/decisions/DR-0026-machining-completeness-programme.md), [MC-1 protocol](../../../../docs/machining-completeness/07-EXECUTION-PROTOCOL.md), [implementation ledger](../../../../docs/machining-completeness/77-MC038-CURRENT-IMPLEMENTATION-STATE.md), and [issue #100](https://github.com/techrote/radiCADSAC/issues/100).

**Falsifier:** any extra zero; wrong multiplicity or crossing parity; a root outside the prescribed strict rational bracket; an algebraic rather than transcendental root; false C0 sided-knot status; acceptance of nonpositive amplitudes, source/phase replay, forged receipts or unbounded coefficient vectors. An independently authenticated source/primitive receipt is a prerequisite for any later integration claim.

## Admitted grammar and resource assumptions

Let k be an integer at least 3, u=t-k, t in [k,k+1], and c=k+1/2. Let P_L(u) and P_R(u) be rational polynomials, strictly positive on [0,1/2] and [1/2,1] respectively, with exactly matching value at u=1/2. Let R(u) be a strictly positive rational polynomial on [0,1], or the zero polynomial as a separate continuum case. Define the physical source

\[
G(t)=R(u)\bigl(\sin(\pi t)-t\cos(\pi t)\bigr),\qquad F(t)=P(u)G(t)^2,
\]

where P is selected by side. **Phase uses PI_TURNS with offset 0 and rate 1**, never an implicit 2π conversion. This is a C0 two-piece H0/H1/H2 rational-polynomial source; a nonzero derivative jump at c makes the physical join genuinely nonsmooth.

The executable subset bounds 3≤k≤10000, degrees P and R ≤3, rational numerator/denominator bit length ≤128, and finite tuple/list source vectors of at most four entries. An exact Bernstein coefficient test must return all strictly positive coefficients on each cell; otherwise it refuses. This is a sufficient positivity cone, not a complete positivity algorithm. All source coefficients, polynomial operations, brackets, seam and endpoint values are exact fractions. Resource budget refusal is NONTRUTH, not zero absence. The mathematical parameter family is infinite; the executable limits are deliberate implementation budgets.

## Lemma 1: H1-to-H2 square-lift (standard algebra, compositional consequence)

For any H1 source G=A+B cos θ+C sin θ with authenticated complete event/sign partition and any continuous piecewise polynomial P>0, F=P G² has the **same zero set**. Every smooth root of G with exact order m has order 2m in F, no sign crossing; F>0 wherever G≠0; identity-zero G pieces become identity-zero F pieces. At a nonsmooth knot, use separate sided germs and require the actual C0 source correspondence: a single global smooth multiplicity cannot be assumed there.

For the implemented source, put Q=P R². The exact double-angle identity yields

\[
F(t)=Q(t)\left(\frac{1+t^2}{2}+\frac{t^2-1}{2}\cos(2\pi t)-t\sin(2\pi t)\right).
\]

The H0 channel is Q(1+t²)/2; the H2 cosine channel is Q(t²−1)/2; the H2 sine channel is −Qt; H1 channels vanish. The checker constructs all channel polynomials on both sides in exact rational power basis, and its tests independently verify polynomial coefficient identities. **It does not blindly accept caller-provided #453 signed certificates.**

## Lemma 2: a complete restricted event partition with a transcendental time

For every integer k≥3, the base function g(t)=sin(πt)−t cos(πt) has exactly one zero ρ_k on the entire closed interval [k,k+1]. It lies in the strict **rational** bracket

\[
k+\frac12-\frac{1}{3k}<\rho_k<k+\frac12,
\]

is a simple zero of g, and is transcendental. Consequently, for positive admitted P and R, **F has exactly one order-two TOUCH, no CROSS, and is strictly positive on the two nonroot components** [k,ρ_k) and (ρ_k,k+1]. The root is an implicit transcendental locator, not an exact rational timestamp.

**Proof — count and order.** On [k,k+1/2), g=0 is equivalent to h(t)=tan(πt)−t=0. Since h'(t)=πsec²(πt)−1>0, h(k)=−k<0 and h tends to +∞ as t approaches k+1/2 from below, there is exactly one simple root. On (k+1/2,k+1], tangent is nonpositive while t>0, so there are no roots; at c=k+1/2, g(c)=(-1)^k≠0. At the root cos(πt)≠0, so g has order one and P R²g² has order two.

**Proof — rational close-knot bracket.** Put l=c−1/(3k). Then tan(πl)=cot(π/(3k))<3k/π<k<l by π>3 and cot x<1/x for x in (0,π/2). Thus h(l)<0 and its sole root is strictly inside (l,c). In particular 0<c−ρ_k<1/(3k), proving arbitrarily close root/knot geometry as k grows, without numerical sampling or a presumed minimum separation.

**Proof — transcendence.** If ρ_k were algebraic irrational and tan(πρ_k)=ρ_k, then z=exp(2πiρ_k)=(1+iρ_k)/(1−iρ_k) would be algebraic. But the Gelfond–Schneider theorem makes exp(iπρ_k)=(-1)^ρ_k transcendental, and its square cannot be algebraic: contradiction. If ρ_k were rational, z would be a root of unity in Q(i), hence one of ±1, ±i; then the finite rational tangent could only be 0 or ±1, contradicting ρ_k>3. Thus ρ_k is transcendental.

**Proof — genuine C0 source kink.** At c, g(c)²=1; F(c)=P(c)R(1/2)²>0. The signed derivative discontinuity is

\[
F'_+(c)-F'_-(c)=\left(P'_R(1/2)-P'_L(1/2)\right)R(1/2)^2.
\]

The default P_L=7/4+u/2 and P_R=3/2+u have exact P(c)=2, derivative jump 1/2 and hence genuine nonsmooth physical source knot without a zero at the knot. Endpoints are strictly positive: F(k)=P_L(0)R(0)²k² and F(k+1)=P_R(1)R(1)²(k+1)². For R≡0, the **entire interval is a zero continuum** and the physical derivative jump vanishes, even if the underlying P control-pieces have different derivatives. That is not an isolated knot zero.

## Deterministic checker, adversaries and cost

From the research subtree run:

    python3 -m unittest -v test_square_lift.py

Eight test methods passed locally before publication. Tests include 46 integer k instances, 60 independent positive P/R parameter combinations, exact H0/H2 symbolic identities, a real kink versus smooth structural boundary, identity-zero continuum, source and phase receipt substitutions, invalid inputs, negative/nonpositive multipliers, and refusal without consuming an unbounded iterator. These are **bounded computations testing an infinite-family theorem**, not proof by 46 samples.

The checker emits a typed source-hash/phase/replay receipt with rational root brackets, signed nonzero rule, root count/order, sided knot derivative jump, exact endpoint and seam values. Verification recomputes the full result from the supplied canonical source; receipt equality is not a trusted root-count claim. SHA-256 identifies the *model's supplied vectors*; it is **not** a signature or authentic MC-038 B-spline producer identity. All polynomial operations are fixed-degree, with expanded H2 coefficient degree at most 11; no root-search loop or native/paid campaign is used. The executable restricts k and coefficient bit lengths to cap arithmetic resource growth.

**Important negative result:** the existing algebraic-time A1 oracle cannot enumerate these ρ_k, because every one is transcendental. Nor does #453's directly applied simple-root rule prove F's tangent root: F'=0 at its zero. A trustworthy primitive H1 proof can instead be **transformed** to an H2 tangent certificate if the exact square-lift source correspondence and positivity are themselves independently verified.

## Prior art and current open laws

This is **not a new transcendence theorem**: double-angle algebra, root multiplicity under squaring, Sturm/Rolle-style monotonicity, cyclotomic roots of unity in Q(i), Bernstein positivity and Gelfond–Schneider are established. The contribution is a bounded typed sufficient *event-class closure* that distinguishes a transcendental-time H2 tangency from source-knot nonsmoothness and avoids the algebraic-time enumeration mistake.

Prior repository work: [#453](https://github.com/techrote/radiCADSAC/pull/453) verifies bounded simple-root spans and refuses unsupported tangencies; [#462](https://github.com/techrote/radiCADSAC/pull/462) addresses B-spline insertion and affine covariance, not the source authenticity of this derived family; [A2 #471](https://github.com/techrote/radiCADSAC/pull/471) addresses local rational-phase jets; [B1 #473](https://github.com/techrote/radiCADSAC/pull/473) develops typed composition but lacks fully authenticated producer adapters.

External prior art: Bell, Delvenne, Jungers & Blondel, *The Continuous Skolem-Pisot Problem*, TCS 2010, DOI [10.1016/j.tcs.2010.06.005](https://doi.org/10.1016/j.tcs.2010.06.005), [arXiv:0809.2189](https://arxiv.org/abs/0809.2189); Chonev, Ouaknine & Worrell, *On the Skolem Problem for Continuous Linear Dynamical Systems*, [arXiv:1506.00695](https://arxiv.org/abs/1506.00695). Their broader decidability context is explicitly NOT solved by this restricted source construction.

**Open:** arbitrary H2 tangencies, arbitrary affine phase, rational/irrational source-time changes, actual clamped B-spline control-knot provenance, signature-level source authentication, verified #453 primitive receipt conversion, non-square germs, and complete machinery/STEP/physics. No general Continuous Skolem or Pfaffian decidability claim follows.

**A3 challenge request:** independently falsify the algebraic-irrational/rational root exclusion, monotonic root count, close-knot bracket, one-sided derivative jump and receipt substitution model. **B1 request:** specify a verified producer-to-envelope source adapter and exact phase-unit check before any transformed root certificate can be admitted.

## Programme disposition

MEASURED_DETERMINISTIC_MODEL for the checker and a proof candidate for independent review; no historical original source newly closed. Historical evidence remains 121 originals / 20 route refusals / 30 missing premises / 50 complete source-specific witnesses, with all 26 machining operations intact. Newly discharged PB/PO claims: 0. MC-B and MC-1 remain NOT_ESTABLISHED; production_authorized=false. No MC-038 producer, proof registry, canonical programme, native/STEP engine or production code is edited, and no Draft-to-Ready or merge is authorized.
