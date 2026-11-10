# A1-F6 — Complete projective H2 root atlas on half-turn boundaries

**10 November 2026 · SPECULATIVE RESEARCH · DETERMINISTIC_MODEL · Draft/HOLD.** Accepted baseline main: 48222d6c40b15ad42cc36d56e6d25f3b284e7fc9. Existing A1 Draft PR #470 pre-edit head: 7c52524c88a8a8988e61ba4024e55366172d62ce. Preregistered scoped lease and falsifier: [#324 comment 6759490496](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6759490496). Only the A1 isolator research subtree may change.

## Existing mechanism and missing lemma

[MC-038 #453](https://github.com/techrote/radiCADSAC/pull/453) certifies bounded rational interval sign and isolated *simple* H0/H1/H2 crossings, but can refuse tangencies, structural-knot zeros and inadequate budgets. [#376](https://github.com/techrote/radiCADSAC/pull/376) already establishes an exact rational-constant H1 Cayley quadratic partition with pole handling and quarter-turn endpoints. A1-F4 only isolates polynomial-carrier zeros if the trig cofactor is rigorously strictly signed; A1-F2 covers a special squared-source family. [#385](https://github.com/techrote/radiCADSAC/pull/385) supplies a genuine V43 nonconstant-amplitude counterexample to naive Cayley *polynomial* rationalisation. The missing reusable result is an **unconditional global H0/H1/H2 constant-rational-amplitude quartic atlas**, not another historical V12/V6 source proof.

## Admitted grammar and falsifier

On physical time t, let

\[
F(t)=h+c_1\cos(\pi q(t))+s_1\sin(\pi q(t))
+c_2\cos(2\pi q(t))+s_2\sin(2\pi q(t)),\qquad q(t)=a+bt.
\]

All seven source parameters are rational **constants**, b nonzero. The input is one finite interval expressed by ordered phase endpoints qlo, qhi belonging to (1/2)Z. The physical closed interval is the increasing reordering of (qlo-a)/b and (qhi-a)/b. Mathematical claim: every finite such rational source. **Executable budgets:** canonical rational tokens of at most 128 bits, phase magnitude at most 4096, phase width at most 32, 8192 Sturm subdivision nodes per chart and requested projective bracket precision 2–72 bits. Budgets may refuse a mathematically covered input and do not imply an unconditional algorithm under finite computer resources.

**Preregistered falsifier:** an admitted source with an omitted/duplicate finite/pole/endpoint event, wrong multiplicity or CROSS/TOUCH/sided sign, a close-root collapse, lost zero continuum, wrong reversal for b<0, forged receipt or source accepted, or exhausted budget reported as certified absence. A degree-three nonzero numerator must have an order-one pole CROSS; degree-two an order-two pole TOUCH; degree-four no pole zero.

## Exact quartic projective theorem and proof

Set x = tan(pi q/2) away from poles q odd integers. Exact circle rationalisation gives cos(pi q)=(1-x²)/(1+x²) and sin(pi q)=2x/(1+x²). Consequently

\[
F=\frac{N(x)}{(1+x^2)^2}
\]
\[
N(x)=(h+c_1+c_2)+(2s_1+4s_2)x+(2h-6c_2)x^2
 +(2s_1-4s_2)x^3+(h-c_1+c_2)x^4.
\]

This transformation is a rational linear bijection: for arbitrary rational n0,...,n4,

\[
h=\frac{3(n_0+n_4)+n_2}{8},\quad
c_1=\frac{n_0-n_4}{2},\quad s_1=\frac{n_1+n_3}{4},
\quad c_2=\frac{n_0+n_4-n_2}{8},\quad s_2=\frac{n_1-n_3}{8}.
\]

Thus **every rational quartic** is represented, not just constructed toy subfamilies. On each chart 2k-1<q<2k+1, x strictly increases with phase because dx/dq=(pi/2)(1+x²)>0. Half-integer phase endpoints map exactly to x=-1,0,+1 or infinity. Exact Euclidean division and squarefree Sturm sequences count all roots of N on each projective x interval. Exact rational brackets, disjoint and strictly avoiding roots at their endpoints, isolate every distinct finite root. Repeated polynomial gcds determine multiplicity <=4. The denominator is positive, and the x→time map has nonzero derivative at finite x, preserving root multiplicities. An odd root crosses; an even root touches. Each zero-free cell has a complete root-exclusion count and exact rational sample for its **strict** sign; sampling does not establish absence.

At a pole q=2k+1, reciprocal u=1/x gives

\[
F=\frac{u^4N(1/u)}{(1+u^2)^2},\qquad \frac{du}{dq}=-\frac{\pi}{2}\ \text{at the pole}.
\]

For nonzero N of degree d, the pole is a zero **iff** d<4, with multiplicity 4-d. Phase-left sign is sign(leading coefficient N); phase-right sign is (-1)^d times that sign. Every shared internal pole is emitted just once. For a finite half-integer endpoint with N(x0)=0, exact repeated linear deflation gives its one-sided multiplicity/sign. Negative affine phase rate reverses physical event order **and** exchanges left/right signed germs. Identity N≡0 implies all five input coefficients vanish by invertibility: the entire physical closed interval is a single zero continuum, not an empty finite event set.

Finite charts, degree <=4, a strict rational Cauchy root bound, exact Sturm counts and finite root separation give finite rational isolation in the ideal exact-arithmetic algorithm. The executable's refusal caps remain distinct from termination proof. No polynomial bit-complexity or practical throughput claim is made: rational coefficient growth and arbitrarily close algebraic roots can be expensive.

The root receipt supplies an **algebraic projective-coordinate bracket**, and physical time is implicit, via q_root=2k+2 arctan(x_root)/pi and t_root=(q_root-a)/b. **It does not claim that transcendental physical root times are exact rationals**, and a projective x bracket is not silently treated as a rational physical-time bracket. Successful receipt replay reconstructs the entire source-derived proof; SHA-256 binds the supplied JSON but does **not** authenticate a native B-spline producer.

## Reproduction and qualification

Two standalone Python standard-library files in this directory: **projective_h2_atlas.py** (exact source parser, quartic/Sturm/pole/endpoint, signed events and fully reconstructive verifier) and **test_projective_h2_atlas.py** (independent rational inverse and adversarial controls). From this directory run:

    python3 -m unittest -v test_projective_h2_atlas.py

The locally executed byte-for-byte source inputs were Git hashed as:
- model: 0079076b9257faf57cabcb3fbdeda71a97551b3c
- tests: eba2c7ddc434ba2dde1acef25c000cab560d9cb7

**Local CPython 3 deterministic evidence: 12/12 unittest methods PASS**. Controls include 31 independent rational quartics × 6 exact double-angle identities, four distinct roots, order-2/3/4 events, period and pole de-duplication, exact phase-boundary tangency, negative-rate reversal, identity continuum, x=2^30 finite root alongside an exact order-3 pole, close root pairs with spacing down to 2^-48, forged receipts and malformed grammar, plus 72 parameter-family witnesses. Independently generated SymPy 1.14 cases (deterministic seed 20261110) compared **240/240** quartic real-root multiplicity sets and pole orders without discrepancy. Finite oracle checks corroborate but do not prove the infinite theorem. They are **DETERMINISTIC_MODEL**, not engineering-geometry, native, STEP or MC-B acceptance. Literal published blob readback and post-upload CI/independent reviewer remain separately required; do not assume hosted CI ran this mathematical test.

## Provenance, prior art, and negative scope

This is a **classical Cayley/Sturm application** over a fully represented quartic coefficient family, not a claimed new transcendence theorem or general trigonometric-polynomial amplitude root algorithm. Nearby [#368](https://github.com/techrote/radiCADSAC/pull/368) already handles degree-zero H4 local structural-knot jets; it is not this global H2 quartic atlas. For established root isolation/real algebraic geometry see Basu, Pollack and Roy, *Algorithms in Real Algebraic Geometry*, 2nd ed., Springer 2006, [DOI 10.1007/3-540-33099-2](https://doi.org/10.1007/3-540-33099-2). More general continuous exponential-polynomial zero questions remain difficult; Chonev, Ouaknine and Worrell, *On the Skolem Problem for Continuous Linear Dynamical Systems*, ICALP 2016, [DOI 10.4230/LIPIcs.ICALP.2016.100](https://doi.org/10.4230/LIPIcs.ICALP.2016.100). General polynomial-*amplitude* H0/H1/H2 is **outside** this theorem (cf. #385); no blanket continuous-Skolem decidability.

**A3 review requested:** execute literal published source/test blobs, independently attack x=0/±1 chart boundaries, negative-b sided signs, odd-integer pole multiplicity, repeated irrational algebraic x roots, bisection exactly at rational roots, the forged-receipt path, and source-hash/certificate semantics. Compare #376 pole convention. **A2/B1 consumers:** do not attach an exact mathematical event receipt to physical source without independent complete #462 knot/control producer authentication, explicit pi-versus-2pi phase adapter, source and real physical-time ownership, and typed implicit-root support. This model does not attest to genuine B-spline knots; it has source_authentication=UNVERIFIED. The source grammar does not allow a nonsmooth physical spline join; a complete physical atlas across knots would require separate verified per-span compositions.

**Protected programme policy unchanged:** historical 121 originals / 20 refused routes / 30 missing premises / 50 complete witnesses, every delta zero and no historical closures; all 26 supported operations; PB/PO obligations OPEN, MC-B and MC-1 NOT_ESTABLISHED; production_authorized=false. No MC-038, proof registry, authority, native, STEP, simulation or production files modified. Draft/HOLD until literal-head CI and independent direct source review.
