# PB-007-01 v17 — exact source-derived even-trigonometric multiplier route

Issue: #196  
Parent integration gate: MC-038 / #100  
Source baseline: `12e65ad2b032fcb9c4ac84b28b2b53195f9f194a`  
Disposition: **bounded exact multi-harmonic family broadened; PB-007-01 remains OPEN**  
Native/paid execution: **none**

## Result

v17 extends the v15/v16 multiplier construction from finite even-cosine multipliers to a source-derived finite real even-trigonometric multiplier

`M(alpha)=lambda_0+sum_{k=1}^m(c_k*cos(2k*alpha)+s_k*sin(2k*alpha))`

multiplying the established carrier `A(s)*cos(alpha)+B(s)*sin(alpha)`. This is a bounded constructive repair only. It does not establish the general coupled analytic grammar, PB-007-01, MC-B, or MC-1.

## Exact source inversion

Let `q=A-iB`, `m_0=lambda_0`, and `m_k=(c_k-i*s_k)/2` for `k>0`. The exact positive-frequency coefficient at source harmonic `(2r+1)h` is

`p_r=q*m_r+conj(q)*m_{r+1}`,

with `m_{m+1}=0`. v17 does not trust multiplier metadata. It derives the normalized highest multiplier phase from the exact polynomial-vector relation

`p_{m-1}=a*p_m+rho*conj(p_m)`.

When `p_m` and `conj(p_m)` are exact-linearly independent, `rho=m_m/conj(m_m)` is determined over Gaussian rationals. The irrelevant real product scale is normalized to `c_m=1` when possible, otherwise `s_m=1`; that real nonzero scale is absorbed into the carrier. The remaining `m_k` are recovered recursively and every original source coefficient is regenerated exactly. If the top phase is underdetermined, or any source identity fails, the route fails closed.

This preserves source/audio/provenance authority: caller factorization, coefficient, projective, root-count or sign assertions never establish the route.

## Exact real-projective nonvanishing

With `t=tan(alpha)`, each `cos(2k alpha)` and `sin(2k alpha)` is rational in `t` with denominator `(1+t^2)^k`. Multiplying `M` by the known-positive denominator `(1+t^2)^m` produces an exact rational polynomial numerator `N(t)`.

The certificate covers the complete real projective line, not only finite `t`:

- the projective point at infinity is checked exactly by the degree-`2m` homogeneous leading value `lambda_0+sum(-1)^k*c_k`;
- an exact rational Cauchy bound encloses every finite real root strictly;
- MC-032 Sturm authority proves the finite distinct-real-root count inside that bound is zero;
- the multiplier sign is established by exact rational evaluation and checked against the leading sign.

There is no numerical trigonometry, binary-float pi, epsilon/tolerance, sampling, approximate minimization, timeout, or resource-exhaustion truth authority.

## Routing and multiplicity

v15/v16 retain precedence for their previously admitted even-cosine family. v17 requires at least one genuinely nonzero sine multiplier coefficient. Carrier event and multiplicity authority remains exclusively with v10/v11/v12; a nonconstant carrier gcd remains owned by v8. Multiplication by the proved smooth globally nonzero multiplier preserves the carrier zero set and every finite event multiplicity.

## Adversarial boundary

The executable controls cover a genuine sine multiplier that v16 blocks, positive and negative multiplier signs, exact infinity roots, repeated finite roots, algebraic-irrational finite roots, exact `+/-1/1000000` neighbours around a nonvanishing/root boundary, malformed and missing source data, wrong harmonic lattices, underdetermined top phase, historical-route precedence, carrier common factors, source-parameter mismatch, caller metadata forgery, binary-float authority, exact-resource refusal, historical-v16 mutation, frozen-denominator shrinkage and false MC-B promotion.

## Programme effect

**PB-007-01 remains OPEN.** The surviving branch includes coupled analytic/multi-harmonic predicates that do not admit this exact normalized source factorization, source maps whose top multiplier phase is not uniquely recoverable under the bounded v17 contract, and carrier cells outside established v10/v11/v12 authority. This result is not an impossibility theorem.

PB-007-02 remains dependent on PB-007-01; PB-007-03 remains OPEN; PB-007-04 remains OPEN_PROPAGATED; PO-04, PO-05 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`. The frozen 26-operation denominator remains unchanged.

All protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics are preserved. No native, paid, production or expensive campaign is authorized or executed by this package.
