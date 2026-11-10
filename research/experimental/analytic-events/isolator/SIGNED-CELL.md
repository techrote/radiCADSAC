# A1-F3 — Signed local cell around a certified algebraic-time Fourier event

**10 November 2026. Research-only / DETERMINISTIC_MODEL / Draft HOLD.** Source baseline: accepted radiCADSAC main 48222d6c40b15ad42cc36d56e6d25f3b284e7fc9. Source path restricted to research/experimental/analytic-events/isolator. No shared proof registry, historic original, MC-038 producer, native geometry, STEP, or production change.

## Existing mechanisms and the missing interface

MC-038 #453 has a bounded rational-interval H0/H1/H2 complete-event method that can refuse tangencies and genuine knot zeros; finite budget failure is not a no-root proof. A1 #470's algebraic_degree.py proves exact multiplicity and crossing parity at a source-local irrational algebraic time but leaves sign UNDETERMINED. A1-F2's Kronecker fallback separately expands irreducible minimal-polynomial admission. A2 #471 is the distinct knot-sided local-germ owner; B1 #473 has separately typed Bernstein certificates. This result is **one local signed event cell**, not a universal root algorithm.

## Exact admitted grammar and theorem

A canonical rational-polynomial Fourier piece is

    F(t) = H0(t) + sum(h=1,2)[ C_h(t) cos(h*pi*(a+b*t)) + S_h(t) sin(h*pi*(a+b*t)) ]

with rational polynomial coefficients of degree at most 16, rational a,b, b nonzero and explicit **pi units**, rather than #453/A2's 2*pi phase units. A trusted A1 gem receipt must independently prove that a primitive irreducible integer polynomial m of degree 2..8 has **exactly one** distinct real root alpha in a rational bracket (l,h), with no endpoint zero, and that all five polynomial channels have common m-adic valuation r >= 1.

**Theorem (conditional local signed-cell soundness).** Divide each channel exactly by m^r to form cofactor G. If a closed rational interval certificate establishes either G(t)>0 for all t in [l,h] or G(t)<0 for all t in [l,h], then F has exactly one zero on [l,h], namely alpha, of exact multiplicity r. Its strict signs on (l,alpha) and (alpha,h) are respectively sgn(G)*sgn(m(l))^r and sgn(G)*sgn(m(h))^r. Hence odd r is CROSS, even r is TOUCH. There is no implicit knot ownership or global zero-set claim.

**Proof.** Exact divisibility gives F=m^r G. Since m is irreducible in characteristic zero, alpha is simple; one-root Sturm and nonzero endpoints show m has constant, opposite signs on the two open halves. Since G is strictly signed on the whole bracket, it has no zero, so F vanishes only at alpha. Algebraic-irrational alpha and rational b!=0 make beta=a+b*alpha algebraic irrational. The quantity exp(i*pi*beta) is transcendental by Gelfond–Schneider. At least one quotient Fourier channel Q(alpha) is nonzero by the minimality of r; the Laurent polynomial in this transcendental quantity is therefore nonzero. Thus G(alpha)!=0 independently of the interval sign guard, proving the exact order r.

**Effective local promise-termination:** For the already certified alpha, shrink rational Sturm-isolating brackets towards alpha while growing point-enclosure precision. The cofactor is analytic and G(alpha)!=0, so its value approaches a fixed nonzero value; rational Taylor/Machin enclosures converge, and a valid rational derivative majorant multiplied by bracket radius tends to zero. A fair refinement must eventually prove strict sign. This is a conditional terminating *local* construction. The finite implementation with 4..32 series terms and finite source caps can refuse; such refusal does not imply absence of a root. Neither arbitrary transcendental event discovery nor blanket Continuous Skolem decidability is asserted.

## Independent rational verifier

The cofactor sign primitive uses only Python Fraction arithmetic:

1. Enclose pi by the exact Machin identity pi=16*atan(1/5)-4*atan(1/239), with signed alternating arctangent remainders.
2. Reduce each harmonic rational phase modulo 2 exactly into [-1,1), and enclose sin/cos by rational Taylor polynomials with Lagrange remainders. Propagate pi argument uncertainty using Lipschitz constant one.
3. Compute the exact midpoint enclosure [v0,v1] for G. On [l,h], put T=max(1,abs(l),abs(h)), amplitude bound A(P)=sum_i abs(P_i)*T^i and derivative bound D(P)=sum_{i>=1} i*abs(P_i)*T^(i-1). Then the derivative bound is L=D(H0)+sum_h [D(C_h)+D(S_h)+(22/7)*h*abs(b)*(A(C_h)+A(S_h))].
4. Widen the midpoint enclosure by L*(h-l)/2. Admit only if the resulting entire closed-interval enclosure excludes zero. Record the pi enclosure, midpoint value enclosure, derivative bound, cofactor sign, local zero count, multiplicity and both sided signs.

The exported certify boundary independently calls the existing exact algebraic_degree.certify before building this certificate. The exported verify boundary replays that germ via algebraic_degree.verify, reruns all arithmetic and requires equality of the whole receipt. SHA-256 binds supplied source identity, not authorization or authentic B-spline provenance. The lower-level signed_from_verified_germ is an untrusted computational kernel, not an admission API. Refusals such as COFACTOR_SIGN_UNKNOWN, missing valuation, inappropriate germ, exhausted term cap and forged receipt never mean root-free. Rational intermediate growth can be expensive and has not been profiled for native applicability.

## Pre-registered falsifiers and evidence

Refute this implementation if exact rational controls show any accepted wrong sided sign (including pure harmonic cases with no H0), unrecognized negative phase rate, wrong even TOUCH, missed cofactor zero, wrong polynomial divisibility, forged source/germ admission, or a wide low-budget bracket erroneously accepted. Important adversarial domains include very narrow algebraic-root brackets, continuum/identity-zero input, real knot boundaries and explicit pi-versus-2pi substitution.

Locally executed: **6/6 standard-library unittest methods PASS** with exact rational arithmetic: pure H1 cosine crossing without DC, an H0/H1/H2 positive mixed crossing, negative-rate H2 negative touch, ten rational coefficient-family controls, quarter-turn interval encodings and forced wide-bracket/low-budget refusals. Git source/test bytes were reread after publication and must remain pinned to their blob identities. The 6 tests call the **independent interval kernel with explicit test-only germ fixtures**, not the complete original algebraic_degree module. Thus full source-level certify/verify replay, independent A3 execution, GitHub dedicated exact-head mathematical acceptance and B-spline producer authentication remain unqualified.

Command from this directory: python3 -m unittest -v test_signed_cell.py

## Published prior art, limits and next action

These are compositions of established Sturm (1829), Gelfond–Schneider (1934), Machin's arctangent identity and Taylor remainder/interval-analysis arguments, not newly discovered transcendence. Source-critical background: Chonev, Ouaknine, Worrell, *On the Skolem Problem for Continuous Linear Dynamical Systems* (ICALP 2016), https://doi.org/10.4230/LIPIcs.ICALP.2016.100 ; *On the zeros of exponential polynomials* (JACM 2023), https://people.mpi-sws.org/~joel/publications/zeros-exp-polys23abs.html . Their stronger decision problem must not be conflated with an admitted algebraic-time local sign theorem.

**A3 handoff:** execute exact published sibling algebraic_degree, attack period/phase normalization and interval error, independently replay forged source/receipt, test rational brackets arbitrarily close to alpha and an identity-zero source. **B1 handoff:** strict closed cofactor sign is not equivalent to a generic B1 POS Bernstein receipt which can vanish at an endpoint. Any interop requires separately authenticated source, phase-unit adapter and genuine knot ownership. No multi-piece/global signed root partition is yet shown.

Historical census 121/20/30/50, mandatory 26 operations, MC-B and MC-1 NOT_ESTABLISHED and production_authorized=false remain unchanged.
