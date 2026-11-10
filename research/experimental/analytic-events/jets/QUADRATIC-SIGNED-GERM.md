# A2-QUAD-SIGN-003 — Certified sided signs at quadratic-irrational physical time

**10 November 2026 · DETERMINISTIC_MODEL · Draft/HOLD.** Scope restricted to research/experimental/analytic-events/jets/** in existing A2 [Draft #471](https://github.com/techrote/radiCADSAC/pull/471).
Accepted main at preregistration: 48222d6c40b15ad42cc36d56e6d25f3b284e7fc9; pre-edit A2 head fb0bb9f893ad8266ccaba89f64c6583a696e2cf2.
[Source lease and preregistered falsifiers](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6760626220).

## Exact admitted domain and A1 distinction

[A1 #470](https://github.com/techrote/radiCADSAC/pull/470) already proves multiplicity at irrational algebraic time using Gelfond–Schneider but explicitly returns sign=UNDETERMINED. This **A2 companion** supplies certified absolute sign and both sided signs in a deliberately restricted quadratic-time grammar; it is neither a global isolator nor a new fundamental theorem.

On rational physical window (L,R), an analytic (not physically authenticated) source is

    F(t) = P0(t) + sum(h=1..2)[Ph(t)*cos(2*pi*h*(a+b*t))
                                + Qh(t)*sin(2*pi*h*(a+b*t))],

where every channel has rational polynomial coefficients and a,b are rational with b!=0. The selected strictly interior algebraic time is

    t0 = u + v*sqrt(D), u,v rational, v!=0, D positive integer nonsquare.

The phase is measured in **2*pi turns**, not A1's pi-turn convention. Mathematical proof allows arbitrary finite degree/harmonic count. Executable grammar restricts each channel to degree<=12, harmonics H0/H1/H2, rational input fields <=96 bits, 2<=D<=1024, and bounded sign precision. Only an analytic span is certified, not B-spline source/knot custody or its neighboring pieces.

## Conditional theorem and proof

Let M(t)=(t-u)^2-D*v^2, irreducible over Q, and r be the minimum multiplicity of M as factor over all nonzero polynomial channels. If every channel is identically zero, F is an **identity-zero analytic continuum**, not a zero of finite multiplicity.

Otherwise factor F(t)=M(t)^r*G(t), leaving at least one residual channel polynomial nonzero at t0. Since b*v!=0, alpha=a+b*t0 is algebraic irrational. The Gelfond–Schneider theorem implies z=exp(2*pi*i*alpha)=(-1)^(2*alpha) is transcendental. G(t0) is a nonzero Laurent polynomial in z over algebraic coefficients (including i): distinct harmonics have distinct Laurent exponents and at least one residual coefficient does not vanish. Therefore G(t0)!=0 and the exact germ order is r.

    right_sign = sign(v)^r * sign(G(t0))
    left_sign  = (-1)^r * right_sign

The omitted factor (2*sqrt(D))^r is positive. An odd positive r is a crossing and an even positive r is a tangency. r=0 is a genuine nonzero point. This is an infinite-family lemma, not established by finite sampling; it combines classical transcendence and Taylor factorization.

**Sign termination:** enclose sqrt(D) by rational bounds obtained with integer isqrt; enclose pi with the alternating rational Machin formula 16 atan(1/5)-4 atan(1/239). Reduce rational phase intervals modulo integral turns into (-1/2,1/2). Taylor sums for sin/cos at an exact rational angle midpoint have Lagrange remainder bounds, and the 1-Lipschitz property covers angle uncertainty. Rational interval arithmetic encloses G(t0). Because G(t0)!=0, *unbounded* refinement eventually separates zero and terminates with a correct strict sign. **This finite prototype** tries n=6,10,16,24,36,52 and refuses if separation is unavailable. It never converts precision exhaustion to exact zero or sign. Receipts include compact outward-rational endpoints, precision and exact source/time hash; strict replay requires builtin JSON primitives, bounded tree and recomputation.

## Bounded executed checks and retained negative result

Run from the jets directory:

    python3 -m unittest -v test_quadratic_signed_germ.py

**7/7 unit methods PASS** on the local source bytes subsequently uploaded and independently Git-blob-matched. The controls include 112 polynomial-family instances F=(t²-D)^k[1-sin(2*pi*b*t)] for D=2,3,5,7, k=0..6, t0=±sqrt(D), b=±1/4. The trigonometric factor is strictly positive at irrational phase: sin=1 would force a rational quarter turn. Its right sign is sign(t0)^k, with the expected opposite left sign for odd k. An independent formal-derivative oracle checked 36 minimal-polynomial multiplicities including shifted/scaled sqrt(D); 4 near-quarter-turn rational-convergent signs required increased interval precision but were certified positive. Additional controls exercised negative amplitude, negative rate, odd/even event type, identity-zero, forbidden constant-rate, untrusted physical time, source substitution, bool/int collision and malicious Python equality.

**Budget refusal (negative control retained):** t0=sqrt(2), F(t)=1-sin(2*pi*b*t), b=q/(4p), p=22127936779729111812853639, q=15646814150613670132332869. This exact source fits the 96-bit input budget and has mathematically positive value, but a separate standalone CPython run returned CERTIFIED_SIGN_BUDGET_EXHAUSTED at the finite precision cap. **This is not an exact-zero verdict.** No native, paid or expensive campaign was run.

A forgery falsifier is any wrong sign/order, failure to reverse odd-order sides at the negative root, accepting a phase-constant algebraic-time theorem, confusing identity-zero with finite multiplicity, accepting substituted source/receipt or claiming physical B-spline authenticity from supplied polynomials. The executable admits *supplied* rational source channels/window, and SHA-256 does not authenticate external custody.

## Prior art and precise acceptance boundary

- [Gelfond–Schneider (1934), formalization by Karatarakis–Wiedijk (March 2026)](https://arxiv.org/abs/2603.24823): algebraic irrational powers of algebraic nontrivial bases are transcendental.
- Rational polynomial division and Taylor's theorem are standard algebra/calculus. Rational Machin bounds follow the classical alternating arctangent expansion; see [DLMF elementary functions](https://dlmf.nist.gov/4).
- [A1 #470](https://github.com/techrote/radiCADSAC/pull/470): existing algebraic-time zero/order oracle, no absolute sign.
- [A2 #471](https://github.com/techrote/radiCADSAC/pull/471): existing rational-time cyclotomic local germs; this adds a distinct irrational-time sign route.
- [#462](https://github.com/techrote/radiCADSAC/pull/462): independently scoped rational B-spline affine/knot transformations; no source-codec integration or structural-knot authority is inferred.

**A3 review:** challenge rational interval formulas, near-quarter-turn precision refusal, negative-root sign, source/receipt forgeries and theorem assumptions. **B1 review:** define a trustworthy producer bridge with explicit pi-vs-2*pi scaling, complete B-spline controls and actual knot ancestry before consuming a sign. A local germ **never** certifies all open roots, global event order, topology/Boolean closure, physical continuity or native/STEP correctness.

**Authority unchanged:** original 121/20/30/50 census, 26 machining operations, historical evidence, open MC-038 PB/PO obligations; MC-B and MC-1 remain NOT_ESTABLISHED; production_authorized=false. Draft/HOLD, independent review and exact-head checks pending, no merge.
