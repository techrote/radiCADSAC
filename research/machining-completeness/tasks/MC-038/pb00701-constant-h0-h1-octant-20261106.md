# MC-038 / PB-007-01 — constant-H0/H1 exact octant critical-event source transfer

**6 November 2026 · prospective restricted constructive research · DETERMINISTIC_MODEL · NO MERGE.**

Issue [#100](https://github.com/techrote/radiCADSAC/issues/100); source/write coordination [#324](https://github.com/techrote/radiCADSAC/issues/324). Authoritative main at task start: 48222d6c40b15ad42cc36d56e6d25f3b284e7fc9. PR #397 retains exclusive main-integration custody. This changes **no** existing source, proof/programme/77/authority file, frozen V54/V2 evidence, geometry, STEP or production code.

## Contribution and novelty boundary

PR #444 certifies exact physical events on **zero-H0, affine-H1** source spans with oriented octant phase nodes, and correctly refuses any nonzero H0. PR #443 independently produces a **prospective source-specific** constant-H0 mutation of the frozen V12 original that has two simple roots in its previously root-free second span. This result does not claim to discover those roots again.

The new contribution is a **generic restricted constructive event and signed-region certificate** for arbitrary rational **constant H0 and constant nonzero H1 cosine/sine coefficients** under a nonstationary rational-affine phase. It uses exact rational-plus-sqrt(2) endpoint value and derivative signs, an exact algebraic critical-value comparison, and a theorem proving that an octant phase cell contains **zero roots, one simple root, or one exact order-two tangency**. When a cell contains two simple roots but lacks a pair of disjoint rational isolating intervals, the executable **REFUSES** a complete source-to-consumer certificate even though the analytic count is known. This deliberate refusal is not a no-root assertion.

The scope is complementary to #444's affine H1 / H0=0 certificate; neither theorem implies the other in its full admitted grammar.

The emitted status is **COMPLETE_RESTRICTED_CONSTANT_H0_H1_OCTANT_SPAN**, deliberately **not** a complete original B-spline-source admission. The field span_spec_sha256 identifies only the prospective constant-span input; original_source_sha256 and original_row_sha256 are separately pinned to the unchanged frozen V12 historical record in the producing contract. Arbitrary user-supplied constant-span JSON is not automatically authenticated as a historical B-spline span. The accepted frozen V12 original has H0=0 and affine H1 on the prefix, so this new constant-H0/H1 theorem **does not admit the full V12 source**. The unchanged V12 *constant second span* supplies source-pinned prospective test inputs only.

## Formal theorem

For a source-time interval [a,b] with rational endpoints, let

\[
F(t)=h+C\cos\theta(t)+S\sin\theta(t),\qquad
\theta(t)=2\pi(u+rt),
\]

where h,C,S,u,r are rational, (C,S) is nonzero, and r is nonzero. Decompose the interval at exact octant phase nodes satisfying u+rt=k/8. On a single cell the angular span has absolute magnitude pi/4, including for negative phase rate.

Let q=C^2+S^2>0. The source-time derivative is

\[
F'(t)=2\pi r[-C\sin\theta(t)+S\cos\theta(t)].
\]

The nonzero sinusoidal derivative has successive stationary zeros **pi apart in theta**. Therefore an octant interval contains at most one strict interior stationary point. Endpoint derivative signs are exact because at theta=k*pi/4 the cosine and sine lie in Q(sqrt(2)); signs of a+b*sqrt(2), for rational a,b, are decided by exact squared comparisons with no approximation or floating point.

If both derivative endpoints have the same strict sign (or one is zero and the other is nonzero), the physical function is strictly monotone in the open cell. Opposite nonzero physical endpoint signs certify exactly one simple root; matching signs certify no root. An octant cell cannot have derivative zero at both ends because pi/4 < pi and q>0.

If the derivative signs are opposite, exactly one interior stationary point exists. A derivative change negative to positive identifies a strict minimum of value h-sqrt(q), and a positive to negative change identifies a strict maximum of value h+sqrt(q). Their exact signs are decidable without taking square roots: compare h^2 with q, accounting for h and the extremum kind.

- A nonzero stationary value opposite to one endpoint gives exactly one simple root on that side, with strict rational bracket (a,b).
- A stationary value with neither endpoint of opposing sign certifies zero roots.
- If the stationary value is **exactly zero**, the single interior root has exact order two: F'=0, and F'' at the stationary root is nonzero because q>0 and r≠0. There is no sign reversal across it. Both endpoint signs must match the permitted extremum side.
- If the stationary value opposes **both** endpoint signs, there are exactly two simple events within one octant cell. That cell is explicitly **REFUSED_NONTRUTH: TWO_ROOTS_SAME_OCTANT_UNBRACKETED**, because the current emitter has no rational split between them. This is a known limitation of the *certificate interface*, not an impossibility or a claim of zero roots.

Every emitted event carries a strict **rational source-time bracket** and simple/order-two multiplicity. Brackets from different octant cells are disjoint; ordered signed open regions are reconstructed from node signs, flipping at simple crossings but not at order-two tangencies. The source-time order follows the physical interval, including decreasing external phase. No root coordinates are falsely described as rational; tangency points and first-harmonic turning points may be transcendental in source time.

## Frozen source custody and constructive challenge

- Original frozen V54 source: composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0.
- Frozen source spec SHA-256: ee15e947924b45640dd16634247a476bb230fdc145fef94407d9a7c219928cd5; whole row SHA-256: d0acef7c69cb8ac1ba128b988e83817a91feff78509dd18007d0e56a506336c3.
- Original exact Git blobs: V54 5841c331579489b25caef38cd412bdbf286f9134; V2 e52d3baf3692a011cf86234eeaa992ef407d99fd.
- Original V12 domain [0,2] and true knot t=1; beta=t/4. Its second span has exactly constant C=2/3 and S=-1/3, original H0=0. The original first span has **affine** H1 and is NOT in this theorem grammar.

For **prospective** H0 bias 7/10 on this unmodified H1 tail, exact physical node values at t=1,3/2,2 are respectively

\[
11/30>0,\quad 7/10-\sqrt2/2<0,\quad 1/30>0.
\]

Their signs are +,-,+. The first octant cell has strictly negative derivative throughout and hence one simple crossing in **(1,3/2)**. The second octant cell has a unique strict interior minimum with value 7/10-sqrt(5)/3 <0 and exact endpoint signs -,+, so it has one simple crossing in **(3/2,2)**. There are **two and only two** ordered simple tail roots and open signed regions **+,-,+**. (The tighter second bracket (7/4,2) from #443 is still valid; the present generic certificate intentionally uses the coarser rational octant bracket.)

For prospective H0=3/4, exact node signs are +,+,+, and h-sqrt(5)/3>0 by 9h^2>5. The tail has **zero roots**. These results reproduce already established #443 prospective mathematics through a different, parameterized reusable admission mechanism; they do not change historical evidence.

## Exact adversarial controls

The verifier includes **eleven** independent test methods spanning positive and negative controls for: (1) two simple source-ordered H0-biased tail roots; (2) root-free larger H0; (3) an **exact order-two tangency** at generally irrational source time using C=-3/5,S=-4/5,h=1; (4) a **genuine two-root same-octant cell** with h=199/200 which must refuse despite matching positive endpoints; (5) reversed phase orientation with one crossing; (6) exact octant-node zero and zero phasor refusals; (7) exact Q(sqrt2) sign comparisons and malformed source inputs; (8) both minimum and maximum interior critical points, including their respective exact order-two tangencies and two-root refusals; (9) derivative-zero phase endpoints, and (10) bounded, duplicate-aware disk JSON ingress, nested containers, long integer, nonfinite number and 400001-byte controls, without counting brackets inside quoted strings as container nesting.

All arithmetic is exact Python Fraction integer arithmetic. Rational source tokens are canonical, at most 640 characters and 512 numerator/denominator bits, derived rationals at most 2048 bits, original input files at most 400000 bytes read with a 400001-byte cap *before* JSON decoding, JSON depth at most 32, and source octant cells at most 128. Exceeding a budget results only in a typed refusal; it never proves the absence of roots. JSON from other sources is never trusted as historical custody.

Reproduce on the **literal PR head**:

~~~sh
python3 research/machining-completeness/tasks/MC-038/pb00701_constant_h0_h1_octant_20261106.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
~~~

The dedicated three-job hosted workflow checks these paths separately. It requires exact head checkout, full 50-source producing V54/V2 replay and current MC-1 static validation. Distinct-session source-critical mathematical and parser review is required before promotion from Draft; #397 alone controls main integration after release.

## Matched nonclaims

Frozen V54 corpus remains **121 originals**: **20 route refusals, 30 missing ordered premises**, with **50 already-complete original V2 witnesses**. All before/after deltas are zero, newly closed historical originals are [], and no PB/PO obligation is discharged. The historical original V12 source is unchanged, including H0=0, its physical events and prior V43 route refusal.

PB-007-01/02/03/04 and PO-02/04/05/07/08 remain OPEN; MC-B and MC-1 remain NOT_ESTABLISHED. Evidence class DETERMINISTIC_MODEL only. No independent native geometry, material reconstruction, B-rep/STEP engineering output, manufacturing acceptance, body/topology/journal/provenance, 26-operation domain change, or production authorization is claimed. This is a narrowly constructive mathematical research result, not acceptance of MC-038 or a generalized analytic-event theorem.
