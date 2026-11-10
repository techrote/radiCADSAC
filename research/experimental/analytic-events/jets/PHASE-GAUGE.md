# A2-PHASE-001 — exact rational phase-gauge normalization for local joins

**10 November 2026 — Draft research, deterministic model.** Scope: \`research/experimental/analytic-events/jets/**\` only. Parent A2 Draft #471 (pre-edit head \`41e6190060e25350371693f82e67918d246c04eb\`), accepted main \`48222d6c40b15ad42cc36d56e6d25f3b284e7fc9\`. Lease [#324/6758683095](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6758683095). No historical-source closure or production authority.

## Motivation and preregistered falsifier

A2-JOIN-001 only accepts two analytic sides written with *identical* rational affine phase offset/rate. This can refuse even when the physical functions coincide: \`sin(pi*t/2)\` written as \`sin(2*pi*t/4)\` or as \`cos(2*pi*(1/4-t/4))\`. The former and latter use different signed rates and phase offsets, but their analytic continuations are equal everywhere. Their **authored-source identities are still different**, so equality alone does not authenticate a shared physical B-spline.

Falsifiers: (1) an admitted finite rational source differs from its canonical Fourier expansion as an exact Laurent polynomial, (2) two different functions are classified equal after normalization, (3) a non-quarter phase, bad harmonic or oversized input is silently accepted, or (4) equality of canonical descriptions is misrepresented as proof that the two receipts share a physical source.

## Theorem: common Fourier gauge, restricted coefficients

Take two finite analytic descriptions indexed by \`s=L,R\`:

\[
F_s(t)=P_{s,0}(t)+\sum_{h\in H_s}
[P_{s,h}(t)\cos(2\pi h(a_s+b_st))+
 Q_{s,h}(t)\sin(2\pi h(a_s+b_st))].
\]

Each polynomial has **rational** coefficients; positive integer harmonics are finite and distinct *within the source*; \`a_s\in(1/4)Z\`, \`b_s\in Q\setminus\{0\}\`; a zero-frequency sine channel is forbidden. Let \(\omega_{s,h}=h|b_s|\) for nonzero channels. Choose their positive **rational gcd** \(g\) (take \(g=1\) for no nonzero frequencies). Every \(\omega_{s,h}=k_{s,h}g\) is an integer multiple.

For \(\alpha_{s,h}=2\pi h a_s\), the exact quarter-turn values \(c=\cos\alpha\), \(z=\sin\alpha\) lie in \(\{0,\pm1\}\), and

\[
P\cos(\alpha+2\pi hb_st)+Q\sin(\alpha+2\pi hb_st)
=C\cos(2\pi kgt)+S\sin(2\pi kgt)
\]

with \(C=cP+zQ\), \(S=\operatorname{sgn}(b_s)(-zP+cQ)\). Add the rational polynomial coefficients of colliding frequencies. This constructs an identical analytic function on all real times, with one common phase \((a=0,b=g)\). The two functions agree analytically **iff** their complete normalized coefficient vectors agree: polynomial-exponential functions with distinct frequencies are linearly independent over \(\mathbb C[t]\) (standard exponential-polynomial fact).

If an independently **authenticated genuine C0 physical knot** at rational K connects those two analytic sides, form the difference in this common gauge and apply A2's finite rational-phase local moment bound. A zero difference implies analytically removable *join*, not an identity-zero *physical field*; otherwise its first nonzero derivative decides exactly C^(n-1) regularity. This is conditional composition, not automatic admission of two independently supplied pieces as one physical B-spline.

### Infinite family, without a false novelty claim

Rational signed rates and arbitrary finite rational polynomial degrees create infinitely many different-encoding instances; exact coefficient normalization terminates using rational integer gcd and finite addition. For **H0/H1/H2** an explicit nonremovable family is

\[
F_L(t)=\sin(\pi t/2), \quad
F_R(t)=\sin(\pi t/2)+c(t-1)^p(1-\sin(\pi t/2))^m
\]

for any integer \(p\ge0\), \(m\in\{0,1,2\}\), and \(c\in\mathbb Q\setminus\{0\}\). Encode the left with \((a,b)=(0,1/4)\) sine, and the right with \((a,b)=(1/4,-1/4)\) cosine; the right expansion uses only h0/h1/h2 with rational polynomials. At K=1, \(\sin(\pi t/2)=\cos(\pi(t-1)/2)\), so the difference has first order \(p+2m\), leading coefficient \(c(\pi^2/8)^m\) in \(s=t-1\). The family is a local analytic-join control. To claim it is a genuine B-spline source additionally requires authenticated complete control/knot/phase semantics; the checker does **not** make that claim.

The m=0,p=0 case is not a C0 join and must be refused by a C0 join consumer; it remains a useful algebraic negative control. The difference's vanishing order is not by itself a complete zero-set partition, root-exclusion certificate, signed endpoint provenance, or original machining proof.

## Implemented bounded probe, independent oracle and results

\`python3 research/experimental/analytic-events/jets/phase_gauge_probe.py\` uses only the Python standard library. Its original-description oracle independently builds Gaussian-rational coefficients for \(\exp(\pm2\pi ikgt)\) before checking the normalized sine/cosine coefficients. This compares **complete symbolic Laurent coefficient vectors**, not floating values at sampled points.

Locally executed controls **before publication**:

- **192** exact Fourier source checks: 4 rational denominators x 3 signed numerators x 4 quarter-turn offsets x 4 amplitude degrees, including h0/h1/h2 channels.
- **54** distinct nonremovable paired examples: p=0..8, m=0..2, two rational signed coefficients. Each exact normalized difference is checked against an independently expressed target Fourier source; a separate rational formal Taylor oracle confirms the first \(2m\) defect-series coefficients vanish and the \(2m\) coefficient equals \(2^{-m}\).
- An analytically equal but **nonzero** same-function/different-source control, with unequal whole-input SHA-256 digests.
- **6** deliberately malformed/over-budget sources refusing by typed \`Refusal\` rather than false root or coincidence.

Resource bounded **prototype**: built-in 1–2 sources only, max eight positive harmonics 1..8, max polynomial degree 8, 160-bit numerator/denominator, rate absolute value <=4 and denominator <=32, rational quarter-turn offset, max nine channels. Normalization can create a base frequency and harmonic count **outside A2's runtime export caps** even when the mathematical identity holds. No implicit claim that the current \`cyclotomic_moments.py\` will accept it: integration must check its actual source budget (degree<=3, 0..8 harmonics, field/order, phase-rate and coefficient caps) and return typed budget refusal if needed. Arbitrary rational offsets would require exact cyclotomic coefficient arithmetic rather than the current rational-only quarter-turn gauge; arbitrary irrational offsets/rates remain outside this proof and checker. This run did **not** execute the exact published A2 parent module.

## Composition, prior art and integration limit

The trigonometric addition law, Laurent/complex Fourier coefficient calculus, linear independence of distinct exponential-polynomial frequencies and exact gcd frequency-grid reduction are **established mathematics**. This is a new local **composition interface candidate**, not a new theorem of global root isolation or Continuous Skolem decidability. See [exponential-polynomial survey (2022)](https://doi.org/10.1112/blms.12719), [complex Fourier coefficient exposition](https://mude.citg.tudelft.nl/book/2025/signal/fourier_complex.html), accepted [#462 B-spline affine-transform evidence](https://github.com/techrote/radiCADSAC/pull/462), [#453 exact event partitions](https://github.com/techrote/radiCADSAC/pull/453) and [A2-JOIN-001](ANALYTIC-JOIN.md).

Do **not** infer authenticated original source identity from the normalized coefficient digest. Two nonidentical submissions can normalize to identical analytic functions; the *full submitted knot/control/phase-vector hash* and an independently reviewed exact source-preserving transformation must accompany any physical knot claim. Artificial partition points cannot acquire knot ancestry through gauge equivalence. B1 may consume a **typed conditional analytic-equality witness** but must not promote it to complete physical event topology.

## Status, falsification handoff and stopping rule

**Conditional mathematical GO** for standard exact phase normalization; **HOLD** for A2 parent-module execution, complete B-spline-source provenance, sign/germ integration and independent A3/B1 review. No native/STEP/paid campaign, gate promotion, historical regression, general root enumerator or runtime performance claim. Request A3 to independently challenge signed frequency collision, zero-frequency, provenance forgery and C0 failure (p=m=0); B1 to review split/artificial-knot custody and whether symbolic equality may be transported with source-ancestry evidence. If these fail, preserve the negative result and stop.

Preserve original 121/20/30/50 source census and all 26 machining operations; MC-B/MC-1 \`NOT_ESTABLISHED\`, \`production_authorized=false\`.