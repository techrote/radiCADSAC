# B1-E1 — Source-bound Bernstein product closure

Status: **speculative research / DETERMINISTIC_MODEL / Draft / HOLD**, 10 November 2026. Scope: `research/experimental/certificate-algebra/core/**`, [B1 Draft PR #473](https://github.com/techrote/radiCADSAC/pull/473). This does not alter MC-038, native/STEP capability, material physics, simulation authority, or programme gates. The preserved historical baseline remains 121 originals, 20 route refusals, 30 missing ordered premises, 50 complete witnesses, 26 machining operations, MC-B/MC-1 `NOT_ESTABLISHED`, and `production_authorized=false`.

## Question and admitted contract

Can independently verified B1 sign certificates for two rational-polynomial C0 piecewise sources be multiplied **without rerunning a new full Bernstein-conversion leaf proof for each product**, while preserving exact zero-set/event classification?

**Admitted:** two B1 `b1-snapshot-v1` base records, each independently verified from untrusted raw exact source and receipt, with one external *expected snapshot hash* per input. Same ordered, closed, contiguous rational piece intervals in both sources, C0 continuity in each operand, degree sum at most 24 per cell, and B1 rational bit caps. Every parent Bernstein vector belongs to POS, NEG or ZERO cone. The input generation is zero for B1's serialized base records; the product is a new derived generation-one snapshot.

**Refuse:** unequal partitions (even if mathematically refinable), absent/stale parent pins, changed raw polynomial or receipt, mixed-sign Bernstein vectors, excessive degree/bit budget, and modified output witness. Parent hashes are **content bindings, not signatures or producer custody**; blindly accepting pins calculated from attacker-supplied changed records does not authenticate external A1/A2/B-spline sources. A successful product receipt cannot itself prove that a *machining history* or *physical World state* originated these sources.

This is a multiplication of *functions on the same declared domain*, not a geometry Boolean, NURBS rational-source theorem, intersection/topology proof, implicit-root isolator, or cross-solver update.

## Theorem and proof (infinite rational-polynomial family)

For each cell `[L,R]`, write `u=(t-L)/(R-L)`, and let

`f(u)=Σ_i b_i B_i^n(u)`, `g(u)=Σ_j d_j B_j^m(u)`,

where `B_i^n(u)=C(n,i)u^i(1-u)^(n-i)`. If the two verified B1 leaves certify the exact coefficients `b_i, d_j`, their product has degree `n+m` Bernstein coefficients

`e_k = Σ_(i+j=k) [C(n,i) C(m,j) / C(n+m,k)] b_i d_j`.

**Proof:** multiply the basis polynomials directly; `B_i^n B_j^m = C(n,i) C(m,j)/C(n+m,i+j) · B_(i+j)^(n+m)`. All weights are positive rationals. If both source vectors are weakly one-signed and nonzero, each factor has strict signed value for `0<u<1`; their product's interior sign is the product of signs. Equivalently the exact `e_k` lie in the correct weak-sign cone, with some strictly signed coefficient. If either vector is ZERO, the product is the identity-zero polynomial. Exact power-basis convolution reconstructs `f g` and its canonical source hash independently of any supplied result hash. The verifier derives the output `e_k` by the displayed identity rather than treating a declared output vector as evidence.

Since both operands are verified C0 and share all interval endpoints, their product is C0. The product has no unreported interior roots on a non-ZERO leaf. Each product zero on the complete domain is either in a ZERO product interval or at a zero-valued partition endpoint; B1's existing `events()` distinguishes maximal identity intervals from isolated endpoint CROSS/TOUCH/BOUNDARY by inward signs. Endpoint multiplicity and higher derivatives are **not** inferred. Negative factors invert pointwise sign; the product sign law uses both operand signs. This yields a theorem over every admitted rational coefficient/partition family, not only the finite test samples.

An explicit infinite family is `f_c(u)=1+c u(1-u)`, `g_d(u)=-(1+d u(1-u))` for arbitrary `c,d∈Q_{\geq0}`. The degree-two Bernstein vectors are `(1,1+c/2,1)` and `(-1,-1-d/2,-1)`, so each product is strictly negative on the full closed interval. More generally, nonzero signed Bernstein cones permit endpoint-zero cases, without claiming multiplicity preservation.

**Bounded implementation:** `product_cone.py` verifies every original input leaf and seam, computes exact power convolution and Bernstein binomial convolution, validates output source constraints, and emits `b1-bernstein-product-v1` with both parent hashes, derived product hash, ordered child hashes, and signs. `verify_product` independently recomputes the entire witness. The operation adds `O(nm)` rational arithmetic per nonzero product leaf, on top of parental verification; there is no claim that this is cheaper in wall-clock time than one fresh Bernstein conversion. No hot-path proof engine is proposed.

## Falsifiers and bounded evidence

Run from this directory (stdlib Python 3.11+):

```sh
python3 -m unittest -v test_product_cone.py
```

Six deterministic tests cover 56 rational `(c,d)` controls from the infinite family, exact product-source comparison at rational sample times, independent fresh Bernstein recomputation of every generated output leaf, a three-cell signed/endpoint case, a CROSS seam, an identity-zero continuum, wrong partition boundaries, altered raw parents/receipts, changed external pins, forged output hash/sign/leaf list, and degree-budget refusal. Exact rational samples are **checks against implementation errors**, not the proof of the family.

**Exact published-source local result, 10 Nov 2026: 6/6 PASS.** All three Python modules used by this test were byte-for-byte Git-blob matched to the live B1 Draft branch: existing `certificate_algebra.py=d366679ccbd1f57a3c8058857162e74df8efd178`, new `product_cone.py=170c8f648274c1c84dca3fe83ba84ff562ab70f1`, and new `test_product_cone.py=8051987f5b82f74358a792cc25cf1d8b5ac996a4`. An initial run against a reconstructed B1-interface test shim also passed; **that earlier limitation was resolved** by independently reconstructing and Git-blob-verifying the complete existing core, then executing the same six tests unchanged against those exact original source bytes. This is a local exact-published-source run, **not** dedicated hosted literal-head CI or independent A3 review. Ordinary CI checks that do not invoke this test are not a substitute.

A bounded 32-piece control independently verifies two base inputs and then composes one product: **64 base leaf conversions + 32 exact product transforms**, rather than **64 base + 32 freshly re-proved output leaves**. It verifies 62 parent seams without a fresh 31-seam product pass (continuity follows algebraically). This is **proof-work instrumentation only**, not a speedup, throughput benchmark, native kernel result, or real solver-certificate cost reduction. Arithmetic cost, SHA-256, memory and allocations have not been measured.

## Novelty and relation to neighbouring research

The Bernstein product formula and nonnegative-cone closure are **classical algebra**, not a new theorem. This candidate's reusable contribution is a constrained, independently replayable, **source-hashed two-parent multiplication certificate**, including sign/identity-zero semantics and an explicit fail-closed grammar.

- Bertot, Guilhot and Mahboubi, *A formal study of Bernstein coefficients and polynomials*, 2011, DOI: https://doi.org/10.1017/S0960129511000090 — established Bernstein exact identities and formal positivity context.
- [#462](https://github.com/techrote/radiCADSAC/pull/462) proves B-spline knot insertion and affine source-time covariance; this result does not reconstruct knot provenance, duplicate its algorithm, or admit its upstream source objects.
- [#453](https://github.com/techrote/radiCADSAC/pull/453) gives restricted interval event-isolation certificates. B1-E1 requires both factors to have already independently established sign cones; it is **not** a substitute for unknown/tangent root isolation.
- A1 [#470](https://github.com/techrote/radiCADSAC/pull/470) already uses positive polynomial multiplication in its H1-to-H2 square-lift family. This B1 law complements that restricted event result with a generic two-parent polynomial-cone certificate; it does not claim discovery of the positive-multiplier principle.
- B5 [#472](https://github.com/techrote/radiCADSAC/pull/472) requires genuine complete dependencies before certificate reuse. Algebraic content hashes and an exact polynomial product do not prove external producer custody or physical dependency closure.

## Open laws, review and stopping condition

**A3 challenge:** find a counterexample to the Bernstein convolution identity under accepted degree/bit caps, a product leaf where interior sign or reported endpoint event differs, a forged source/receipt accepted under unchanged independent pins, or a source-substitution case that passes with unchanged externally trusted pins. Independently execute the source-matched six-test suite on the exact B1 parent core, and challenge the C0/zero-continuum proof.

**B5 challenge:** assess whether this product signature can consume independently authenticated A1/A2/#462 source and transformation receipts without circular source-pin custody, and whether output result source types can be proposed without suggesting material Boolean or solver authority.

**Unproved/open:** authentic producer-to-physical-domain custody; non-aligned partition common refinement; source transformations requiring knot identities; general mixed-sign polynomial/root isolation; multiplicity/derivative transfer; arbitrary Boolean/topology composition; journal/rollback provenance and CyberSand effect dependency proof; runtime cost. No per-cell production use or generalized source admission is requested.

Stop at **Draft/HOLD** pending distinct A3/B5 review and applicable dedicated hosted exact-head qualification; published-parent local execution is now complete. No merge, MC-038 source edit, production bootstrap, native/paid campaign or authority change.
