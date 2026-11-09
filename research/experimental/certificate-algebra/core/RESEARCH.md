# B1-C1/C2: source-bound certificate composition and local reuse

**Status:** speculative research candidate, 9 November 2026. **Evidence class:** DETERMINISTIC_MODEL. **Review:** A3/B5 independent challenge requested; Draft / DO NOT MERGE. **Write set:** `research/experimental/certificate-algebra/core/**` only. This does not close MC-038, establish MC-B/MC-1, authorize production, or demonstrate native/STEP/physical correctness.

## Hypothesis, admitted source grammar and provenance

The admitted source is a finite, ordered, *contiguous C0* list of closed rational intervals, each with a rational polynomial in normalized local coordinate u=(t-L)/(R-L). The exact interval and canonical power-basis coefficients are independently SHA-256-bound per leaf. The entire ordered sequence and mutation generation have a separate snapshot hash. A leaf statement is exactly one of POS, NEG or ZERO, supported by a rational Bernstein coefficient vector.

POS means every coefficient is nonnegative, with at least one strictly positive; NEG is analogous; ZERO means every coefficient is zero. Unknown/mixed coefficients are refused. These are sufficient criteria, not a complete test for arbitrary polynomial signs. Zero intervals and endpoint events are explicitly distinguished from interior root claims. The digest is content binding, **not** proof of who authored or authenticated the original B-spline, machining journal or tool state. A new source has to be independently admitted before it can inherit a certificate.

The untrusted-journal replay verifier reads a base source, checks every supplied exact Bernstein vector against the actual polynomial and source hash, checks all continuity seams, then applies each declared operation under its checked predecessor/source version. Output hashes are recomputed, not trusted. `Verified` objects are in-process derived state, not safe-to-deserialize security tokens. Stale predecessor, extra fields, bad resource budgets, forged source, noncanonical rationals and false sign assertions produce `Refusal` (NONTRUTH).

## C1 theorem: complete zero set on the sign cone

Write p(u)=sum(b_i * binomial(n,i) * u^i * (1-u)^(n-i)). On 0<u<1 each Bernstein basis term is strictly positive. Hence a weak-sign nonzero vector b yields a *strict* sign throughout the open interval; the all-zero vector yields the identity-zero function.

For a finite *verified C0* partition whose every leaf is so classified, **every zero belongs to a whole identity-zero piece or an exactly zero-valued partition endpoint**. There cannot be an undiscovered interior root. Identity-zero adjacent pieces merge into maximal reported closed zero intervals; isolated endpoints are classified BOUNDARY, CROSS (opposite certified inward signs) or TOUCH (equal inward signs). At a nonsmooth seam, TOUCH is topological sign behaviour, **not** an assertion of equal derivatives or root multiplicity.

**Infinite family covered:** p(u)=1+c*u*(1-u) for every rational c>=0 has Bernstein coefficients (1,1+c/2,1), hence strictly positive on (0,1). The finite tests sample 112 pairs (numerator,denominator); that evidence challenges the implementation, whereas the argument establishes the infinite family.

**Counterexample to an invalid extrapolation:** p(u)=(u-1/2)^2 has a tangent interior root and mixed-sign degree-two Bernstein coefficients; it is refused, not mislabeled a zero-free span. Likewise p(u)=u-1/2 is refused. The method is deliberately incomplete outside its cone.

## C2 theorem: closure and incremental invalidation

**Exact rational split.** Source restriction u=alpha+beta*v, beta>0, yields rational polynomial coefficients by binomial expansion. De Casteljau subdivision of the *verified* Bernstein vector uses convex combinations with 0<alpha<1. It preserves weak nonnegative/nonpositive cones and, for nondegenerate child interiors, strict positivity/negativity. Thus the child certificates follow from the parent without a fresh full leaf sign proof. The newly created cut seam is checked exactly. Identity-zero remains identity-zero.

**Signed affine time change.** For t=offset+rate*x with rational nonzero rate, transform the rational interval bounds and polynomial coefficients exactly. Negative rate reverses interval order, reverses Bernstein vectors, and swaps inward sided claims. Sign and event types remain valid. Rate zero is refused as non-invertible.

**Static concatenation.** Two verified partitions can be joined only when their endpoint positions and *values* coincide; their leaf sign claims then compose. This is not a material Boolean or a topology theorem.

**Single-piece update.** For an immutable previous snapshot with fixed piece domains and independent local source semantics, replacing piece i can alter only its local sign claim and its two adjoining C0 seams. Verify the new leaf and these seams; every unaffected leaf is still the same hashed polynomial and all nonadjacent seams compare the same endpoints. Generation increments. This is a *static local dependency theorem*, **not** a theorem that an unchanged CyberSand cell is insulated from distant pressure, moving bodies, reactions, contact or future causal effects. B2/B3 must independently prove those influence bounds before using this principle for solver sleeping or handoff.

The code includes exact Bernstein conversion, signed-domain transformations, source/hash receipts, typed event and zero-continuum classification, local update, static concatenation and an independent JSON operation-history replay for split/affine/replace. Replaying a serialized journal must check all base certificates and subsequent transitions; no historical proof validity is granted merely because a saved file claims a cache hit.

## Falsifiers and independent qualification

The tests challenge source substitution, false sign receipts, non-C0 seams, extra fields, rational aliases, reversed affine phase, stale predecessor/snapshot hashes, forbidden split, sign-changing/tangent interior roots, zero continua, positive-touch and negative-to-positive crossing at knots. Exact Fraction probes on dozens of rational points are **non-authoritative checks**, not a substitute for the two algebraic proofs. There is no reliance on native, paid API or CI runners.

Run from this directory with Python 3.11+ stdlib only:

```bash
python3 -m unittest -v test_certificate_algebra.py
python3 experiment.py
```

**Author-local result:** 7/7 test methods PASS; 112 positive parametric members and multiple adversarial receipt substitutions exercised. The 32-piece/64-local-update deterministic comparison uses identical polynomial states in a full-snapshot rescan and incrementally verified update scheme: **2,080 vs 96 full-leaf checks**, 2,015 vs 155 continuity-seam checks, and zero changed-leaf omissions. Full-leaf check ratio = 65/3 (~21.67). These are **certificate-work counts only**. Not measured: actual wall-clock speed, hashing/allocator overhead, source ingestion, memory, native physics tick, Rapier, topology, STEP or real CyberSand gameplay. No simulated 21x speedup is claimed.

Caps: polynomial degree <=24, rational numerator/denominator bit length <=1024, <=512 base pieces, <=1024 replay steps. Budget exhaustion or unsupported sign/grammar is a refusal, not proof of no root. No implementation or claim for arbitrary H1/H2 trigonometric expressions, nonlinear reparameterization, all rational B-splines/NURBS source provenance, general machining/Boolean operations or physical solver influence.

## Prior art, novelty and interfaces

The mathematical ingredients are established:
- Bertot, Guilhot, Mahboubi, *A formal study of Bernstein coefficients and polynomials* (2011), Mathematical Structures in Computer Science 21(4), DOI https://doi.org/10.1017/S0960129511000090 — formal Bernstein/de Casteljau properties.
- Hamadneh et al., *Optimization and Positivity Certificates of Rational Functions using Bernstein Form* (2019), https://arxiv.org/abs/1906.11037 — Bernstein positivity literature.
- [#462](https://github.com/techrote/radiCADSAC/pull/462) already establishes different B-spline knot insertion/affine source covariance contracts. It is consulted as prior work; no code imports or overlapping writes. This B1 result is *narrower* in function class but explicitly models source-typed reusable certificate dependencies.
- [#453](https://github.com/techrote/radiCADSAC/pull/453) handles finite-interval simple H0/H1/H2 events with interval certificates. B1 cannot replace its difficult root isolation or lift its tangency refusals. Linking them requires an independently validated source codec and richer event-certificate types.

No novelty is asserted for Bernstein positivity, subdivision or elementary finite dependency graphs. The exploratory integration question is whether typed source-identity, transform provenance and invalidation contracts can scale to general geometry and genuine physically safe solver work elimination.

## Review requests and next research seams

**A3:** seek a proof flaw, especially an endpoint/identity-zero misclassification, signed-affine side reversal, replay forgery or counterexample to claimed local dependence. Independently reproduce selected Fraction tests; challenge the explanation as well as the code. **B5:** inspect whether this typed sign-cone certificate and #462 source contract can compose *without changing shared MC authority*. **B2/B3:** specify independently proved finite-range physical dependencies before attempting any CyberSand optimisation. The first valuable extension would be a type-safe bridge to source-authenticated B-spline subpieces and to already verified event-root cells, not further V12/V6 special-case closures.

**Historical authority invariant:** 121 original sources, 20 route refusals, 30 missing ordered premises, 50 pre-existing complete witnesses; all 26 machining operations unchanged. Zero new original closures and no PB/PO discharge. MC-B/MC-1 remain **NOT_ESTABLISHED** and `production_authorized=false`.
