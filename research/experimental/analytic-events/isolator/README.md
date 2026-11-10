# A1 — Exact algebraic-time zeros for polynomial-amplitude Fourier sources

**9 November 2026 · Research only · Independent review required.** This is an application of established transcendence and cyclotomic theory, **not** a new theorem of transcendence and **not** a complete physical event partitioner.

## Falsifiable problem and scope

Determine whether a polynomial-amplitude H0/H1/H2 trigonometric source is exactly zero at an algebraic time, without numerical zero tests or source-specific root enumeration. A decisive falsifier is a nonzero source vanishing at a real irrational-algebraic time where its rational-polynomial Fourier channels do not all vanish. Further falsifiers: incorrectly classifying the rational-phase cancellation 1−sin(π/2), accepting a zero phase-rate under the irrational-time theorem, misstating polynomial multiplicity, mistaking an identically zero piece for isolated roots, or accepting a forged receipt.

The admitted span grammar is

\[
F(t)=C_0(t)+\sum_{k=1}^{m}\left(C_k(t)\cos(k\pi\beta(t))+S_k(t)\sin(k\pi\beta(t))\right),\qquad
\beta(t)=a+bt,
\]

where all channels belong to Q[t], a and b are rational, and **b is nonzero for the irrational-time result**. Phase is an affine number of *π-turns*, not radians. The **mathematical argument** applies to every finite harmonic order and polynomial degree; the **executable** is restricted to H0/H1/H2, degree ≤16 per channel, 256-bit input rationals, and either rational times (cyclotomic order ≤128) or roots of primitive integer quadratics with positive nonsquare discriminant (quadratic coefficients ≤128 bits).

This is a **per-analytic-span** result. B-spline source extraction, genuine knots, sided continuity, endpoint ownership, physical time mapping and whole-source provenance require independent authenticating consumers. A correct local event is not automatically a valid whole-source physical event.

## General algebraic-zero dichotomy (mathematical proof; pending A3 challenge)

Let α be a real algebraic time and b≠0.

**Rational time.** For α rational, the phase β(α)=p/d is rational (in lowest terms), so F(α) belongs to the cyclotomic field Q(ζ), where ζ=exp(2πi/(4d)). It is exactly zero iff a rational polynomial representing 2F(α) has zero remainder modulo Φ_(4d).

Specifically, because i=ζ^d and exp(iπp/d)=ζ^(2p), define, with all exponents interpreted modulo N=4d,

\[
T(X)=2C_0(\alpha)+\sum_{k=1}^{m}
\left[C_k(\alpha)(X^{2kp}+X^{-2kp})
+S_k(\alpha)(X^{d-2kp}-X^{d+2kp})\right].
\]

Then 2F(α)=T(ζ), and **F(α)=0 iff T mod Φ_N is identically zero**. Φ_N is irreducible over Q. This includes exact sine and cosine cancellations where individual polynomial channels do not vanish, and it does not require a floating-point approximation.

**Irrational algebraic time.** For algebraic irrational α, β(α)=a+bα is algebraic irrational. The 1934 **Gelfond–Schneider theorem** gives transcendence of z=exp(iπβ(α))=(-1)^(β(α)), using the logarithm iπ of -1. Multiplying F(α) by 2 and expressing sine and cosine via z gives a Laurent polynomial in z with **algebraic** coefficients:

\[
2F(\alpha)=2C_0(\alpha)+\sum_{k=1}^{m}
\left[(C_k(\alpha)-iS_k(\alpha))z^k
+(C_k(\alpha)+iS_k(\alpha))z^{-k}\right].
\]

A nonzero polynomial over the algebraic numbers cannot vanish at transcendental z. Hence the equality

\[
F(\alpha)=0
\quad\Longleftrightarrow\quad
C_0(\alpha)=C_1(\alpha)=S_1(\alpha)=\cdots=C_m(\alpha)=S_m(\alpha)=0.
\]

Thus **all irrational-algebraic zeros are common roots of the coefficient polynomials**. With an effective algebraic-number representation, a polynomial GCD and certified algebraic root isolation suffice in principle to enumerate them. No transcendental-time zeros are covered.

**Multiplicity and event type.** Let M in Q[t] be irreducible with a simple irrational-algebraic real root α. If some channel is nonzero, let s be the minimum multiplicity of M across all nonzero channels. Factoring M^s from every channel leaves at least one nonvanishing residual at α (irreducibility). The irrational-time equivalence shows the residual full Fourier value is nonzero at α. Therefore F has **exact zero order s** at α if s>0; s=0 proves nonzero. Since M has a simple root, the local function changes sign at α exactly when s is odd. **Absolute adjacent signs and locations of other transcendental zeros remain unproved.** When all channels are identically zero, the whole analytic span is an **IDENTICAL_ZERO_PIECE continuum**.

### Relation to existing work

- [PR #453](https://github.com/techrote/radiCADSAC/pull/453) supplies a bounded, independently rechecked interval certificate for zero-free cells and single-simple-root brackets on H0/H1/H2 sources. It returns typed nontruth for unsupported tangencies or knot zeros and does **not** give global termination. A1 adds a **specified algebraic-time** equality/multiplicity oracle, not a replacement for #453.
- [PR #368](https://github.com/techrote/radiCADSAC/pull/368) already uses cyclotomic source-knot derivative techniques for a bounded *degree-zero constant-amplitude* H4 construction; [PR #397](https://github.com/techrote/radiCADSAC/pull/397) handles a special squared-amplitude structure. The new work is the algebraic-irrational common-channel result and its coupling to arbitrary admitted polynomial-amplitude H2 point tests. Whether this is engineering-useful or independently original as a combination **remains to be evaluated**.
- [PR #385](https://github.com/techrote/radiCADSAC/pull/385) shows why Cayley rationalisation alone fails for affine nonconstant amplitudes. A1 does not rationalise or solve those transcendental-root cases.
- Established mathematical prior art: [Gelfond–Schneider theorem, Encyclopedia of Mathematics](https://encyclopediaofmath.org/wiki/Gel%27fond-Schneider_method); [Karatarakis and Wiedijk, formalization in Lean 4, March 2026](https://arxiv.org/abs/2603.24823); irreducibility of cyclotomic polynomials over Q. **No claim that the underlying mathematical tools were discovered here.**

## Implementation, receipts, verification

The isolated Python module algebraic_zero.py uses only standard-library exact integers and Fraction. It reconstructs Φ_N by exact polynomial division and returns rational-time source-bound certificates containing the time, phase, Φ_N, representative of 2F, exact remainder, and a zero/nonzero/continuum verdict. For quadratic-algebraic times, it validates a primitive irreducible quadratic with positive nonsquare discriminant, emits two **strict rational root-isolating intervals** via floor-square-root bounds, and returns minimum polynomial valuations, exact order and crossing parity at both roots. Both receipt verifiers recompute all output from a supplied source; an over-budget or invalid source raises a typed **Refusal** rather than pretending to prove absence. Return sign is **UNDETERMINED**.

Run in a checked-out repository:

    cd research/experimental/analytic-events/isolator
    python3 -m unittest -v test_algebraic_zero.py
    python3 challenge_sympy.py    # optional independent oracle; SymPy 1.14 tested

Development-local on 9 November 2026: **10/10 deterministic standard-library tests PASS**. Optional SymPy 1.14 challenge: **32/32 cyclotomic polynomial identities**, **209/209 admitted independently symbolic rational-time controls PASS**, **31/240 rational-time cases typed budget refusal**, **0 symbolic unknown**, and **120/120 constructed quadratic valuation checks PASS**. Reproducible seed 241, no numerical sampling accepted as proof, no native/STEP/paid campaign. Tests include cosine/sine/H2 phase cancellation, negative phase rate, 2^−10 near-zero budget refusal, cubic crossing at ±sqrt(2), quadratic tangency, ±sqrt(3), identity-zero piece and forged receipt/source rejection. These executions are **MEASURED_DETERMINISTIC_MODEL**, not independent validation of the theorem.

## 9 November 2026 A3 review repair: constant-phase continuum and forged sources

A3's [source-critical review](https://github.com/techrote/radiCADSAC/pull/470#pullrequestreview-5833060107) identified two checker defects in the first Draft: constant phase (`b=0`) could yield an identically zero function despite nonzero raw coefficient polynomials, and a directly constructed malformed `Source` bypassed factory validation and was subsequently accepted by a receipt verifier. Both were **implementation defects**; the nonzero-rate transcendence theorem does not apply to constant phase.

**New exact classification lemma (classical cyclotomic algebra, not a new theorem):** for `b=0` and rational offset `a=p/d`, write each input polynomial `C_k(t),S_k(t)` as a sum of rational coefficients times `t^j`. Let `T_j(X)` be the Fourier numerator polynomial formed from the coefficient of `t^j`, using the same exponents as rational-time evaluation. Then

`F(t) ≡ 0` on a nonempty open interval iff **for every j**, `T_j(X) mod Φ_(4d)(X) = 0`.

The forward implication follows from the uniqueness of coefficients of a polynomial in `t` over the cyclotomic number field; the reverse follows by reconstruction. This covers **infinitely many rational polynomial source families** under the bounded executable grammar, including nontrivial cosine/sine cancellations. It separates `IDENTICAL_ZERO_PIECE` from a single `EXACT_ZERO` without confusing point equality with zero continua. `b ≠ 0` still uses the existing nonzero-channel criterion (distinct effective harmonics); `b=0` above cyclotomic order 128 refuses. This does NOT enumerate all isolated roots of constant-rate fields or produce their adjacent signs.

Source authentication is now checked both during frozen `Source` construction and at every public evaluation/provenance entry: matched H0/H1/H2 arrays, exact `Fraction` types, immutable trimmed coefficient tuples, phase types, bit and degree budgets. A malicious `object.__setattr__` mutation cannot reuse an earlier receipt without being revalidated. Failures are typed `Refusal` or `verify_*=False`, never a fabricated zero certificate. Registered regressions include A3's exact two counterexamples, direct malformed source, float, noncanonical/oversized input, forged frozen field, and an arbitrary-degree rational polynomial family.

**Evidence:** local stdlib tests and separately derived exact-SymPy checks are model-level evidence; this section records the corrected claim and falsifiers for independent A3 review. Prior [Gelfond–Schneider](https://encyclopediaofmath.org/wiki/Gel%27fond-Schneider_method) and cyclotomic-field results remain established mathematics, not new theorems. No MC-038/MC-B acceptance or general event partition is claimed.

## Known limitations and research handoff

1. **Not a complete analytic event isolator.** It decides equality for specified algebraic times; it does not enumerate, bracket or order all **transcendental** roots. The square of t cos(πt)−1 gives a conceptual source with transcendental multiple zeros and illustrates the missing generality.
2. **No complete physical partition or sided knot semantics.** Sign, all source edges, rational-knot one-sided multiplicity, nonzero cells, exact source codec and continuous composition are outside this module. A2 owns knot/local jet techniques. An isolated zero at an internal span knot must not be silently counted as a whole-source event.
3. **Executable only covers quadratic irrationals.** The theorem covers arbitrary real algebraic irrationals; a future finite algebraic field / primitive minimal polynomial + isolating interval verifier may implement that extension. General trig source zeros remain an open problem.
4. **A3 independent adversary requested:** challenge the chosen branch of complex exponentiation in Gelfond–Schneider, algebraic-coefficient Laurent independence, cyclotomic sine reduction, negative-rate case, root-isolator bounds, multiplicity/common-factor statement and receipt forgery controls. A next A1 task could integrate **sound algebraic-event discovery** with #453's bounded interval solver, preserving typed unresolved transcendental tangencies.
5. **No capability claim.** Frozen original census **121 / 20 / 30 / 50**, 26 supported machining operations, historical evidence, PB-007-01/02/03/04, PO-02/04/05/07/08, MC-B and MC-1 **NOT_ESTABLISHED**, and production_authorized=false are unchanged. No files in historical task, authority, shared registry, native or STEP code have been modified.

**Classification:** SOURCE for literature and existing PR states; mathematically derived argument pending independent review; MEASURED_DETERMINISTIC_MODEL for the local checks; PROPOSAL for future integration. No novelty/production/MC-B claim.