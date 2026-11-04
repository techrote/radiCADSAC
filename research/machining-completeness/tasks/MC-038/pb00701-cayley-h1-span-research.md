# MC-038 / PB-007-01 — exact rational-Cayley first-harmonic source-span event atlas

**Status:** bounded mathematical research implementation, 4 November 2026; source-level review / literal-head CI / integration still required. **Evidence class:** DETERMINISTIC_MODEL only. **Gate:** PB-007-01 OPEN, MC-B and MC-1 NOT_ESTABLISHED.

## Purpose, source authority and falsifiable scope

The goal is a *reusable exact ordered physical event/sign partition of an original-source span* when its Fourier coefficients are rational constants and its affine phase passes through integer/half-integer turns at the endpoints. This is a bounded **child-span theorem**, not an original-source whole-span composer and not a general transcendental event decision theorem.

Prerecorded owner, cost bounds, expected/refused results, original source hashes and independent controls: [MC-038 issue #100, comment 6631338149](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6631338149). Current source authority at inception: main e0d66d075bf69309e283022744e4fd79717b2638. Frozen source corpus Git blob 5841c331579489b25caef38cd412bdbf286f9134. Post-v54 fifty-source evidence Git blob e52d3baf3692a011cf86234eeaa992ef407d99fd. Original v54 refusals and accepted complete source-specific witnesses are not modified.

**Admitted grammar:** one closed source-time span [lo,hi], lo < hi rational; rational A,C,S; physical source function

\[
F(t)=A+C\cos(2\pi(\alpha+\beta t))+S\sin(2\pi(\alpha+\beta t)),
\]

where alpha and beta are rational, beta>0, and both endpoint phase turns p0,p1 belong to (1/2)Z. Maximum phase span 64 turns for this public executable; larger input returns NONTRUTH refusal. The entire exact source is not silently reduced to a cosine-only surrogate. The independent verifier also checks the original B-spline harmonic inventory, true knot, clamped control sequences and constant right-span lowering for each frozen anchor. Missing sine channels, nonconstant right-piece amplitudes or changed original specifications are not admitted as those anchors.

The *candidate completeness theorem is falsified* if any admitted constant-coefficient source has an omitted physical root, wrong order, false identity-zero classification, incorrectly ordered event, incorrect endpoint germ, sign or parity.

## Correctness and termination argument

Let p=alpha+beta*t, z=tan(pi*p) on one open phase strip n-1/2 < p < n+1/2. Since beta>0, p strictly increases. Exact double-angle identities give

\[
F(t)=\frac{(A-C)z^2+2Sz+(A+C)}{1+z^2}.
\]

The denominator is strictly positive. Thus every and only open-strip zero is an exact real zero of the degree-at-most-two rational polynomial P(z); the discriminant scaled by four is D=C²+S²-A². If A-C is nonzero, D<0 certifies no roots; D=0 yields one order-two root, D>0 yields two ordered order-one roots. If A-C=0, solve the linear polynomial (or report no finite roots). In particular, root coordinates are represented **implicitly**, as exact signed quadratic radicals and phase branch integers; the implementation never claims a radical phase coordinate is rational. Rational and signed-radical comparisons decide whether a root lies at, inside or outside exact half-integer phase endpoints. Under the admitted endpoint condition, this reduces to its exact sign relative to zero or a strip boundary.

**At phase poles p=n+1/2**, z is undefined but the original F is well-defined. Here F=A-C. A pole is a physical zero only when A=C; the zero has order one when S is nonzero, otherwise order two when A is nonzero. The all-zero triple A=C=S=0 is separately typed as a closed identity-zero continuum. No zero is lost by division by a trigonometric factor.

At an integer or half-integer phase endpoint p, the exact value is A+C or A-C, respectively. If nonzero its sign is decisive. If zero, the one-sided first derivative sign is that of (+/-) S times direction into the span; if S=0 the first nonzero local term is quadratic with sign(A). This is an exact one-sided germ and does not treat an endpoint root as an extra interior sign cell. Across each isolated event, source signs flip precisely on odd order and remain on even order. The final independently evaluated right endpoint germ must match the propagated sign; mismatches reject. For a double-root tangency, no sign change is fabricated.

Since p1-p0<=64 and phase is strictly increasing, finitely many integer strips and poles intersect the domain; each carries at most two finite roots, with at most one pole event at a boundary. Signed radical comparisons terminate by rational arithmetic, including exact equality, so no numeric scan, finite tolerance, timeout or arbitrary subdivision cap serves as a true root predicate. The 64-turn admission bound only controls workload; exceeding it is a refusal, not a proof of no zero. The source-level asymptotic event algorithm has O(1 + phase turns) strip enumeration, with rational big-integer cost dependent on input bit length. This proves the specified bounded grammar only, not general polynomial/trigonometric analytic decidability.

## Two original frozen V43-refused child spans

Both case IDs are historical frozen v54 BLOCKED, and were already **COMPLETE_SOURCE_SPECIFIC** in the independently registered fifty-source v2 evidence. These tests do not revise that status or add new frozen-case coverage.

| Frozen original source ID | Canonical SHA-256 | Original phase turns | Exact V43 child on [1,2] | Ordered physical signs |
|---|---|---|---|---|
| composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0 | 57d3c14096ccedfb7faea5023f5a09bada2ca274748f2207c36d77bbc790927c | -1/2+2t | A=0, C=1, S=-1/2 | −,+,−,+,− |
| composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail0 | 1535f364cd4d3c1a3bf34f57f394ad70a17ad1327880a0a47f25f3ecff5c7560 | 2t | A=0, C=1/8, S=1 | +,−,+,−,+ |

For both original V43 right spans, the exact phase covers two turns and the Cayley numerator has one simple zero in each relevant half-turn, producing exactly **four distinct strictly interior simple crossings**, no endpoint zero and no identity continuum. The original source parameter, global phase and actual true knot t=1 are retained. The V10 left span contains nonconstant sine amplitude; the V11 left span contains a quadratic cosine amplitude. **Neither left span is silently admitted or composed by this bounded child atlas.** The historical evidence that those entire sources are complete remains the separately executed fifty-source registry.

These exact child results are deliberately redundant with established source-specific proofs. Their new contribution is an executable source-checked *parametric method grammar* for constant rational H0/H1 spans with exact endpoint-phase constraints, including events, parity and endpoint germs rather than only passing examples.

## Positive, negative and adversarial qualification

Run from the repository root:

    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_cayley_h1_span.py --contract --self-test
    python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract

The exact source verifier checks frozen Git blobs, full canonical original source SHA-256, complete admissible channel controls, degree and true knots, both original historical child dispositions and pre-existing complete evidence rows. It executes a 2,401-case rational coefficient/phase grid plus source/phase/refusal/knot/harmonic mutation rejections. The core checks identity-zero, negative-rate/bad-phase/refusal, root-free nonzero, pole roots, rational tangent, exact endpoint zero and a near-tangency split separated at scale 2^-100 or closer. This is adversarial implementation testing, not an independent general mathematical oracle or native geometry.

Accepted receipts are machine-readable at [pb00701-cayley-h1-span.json](pb00701-cayley-h1-span.json). The implementation's exact implicit event descriptors may be inspected using its verifier's --emit mode. The pinned older raw failed V43 attempts are never rewritten.

## Before/after census and nonclaims

| Pinned category | Before | After | Delta |
|---|---:|---:|---:|
| Frozen original source denominator | 121 | 121 | 0 |
| Historical refused route sources | 20 | 20 | 0 |
| Missing ordered premise sources | 30 | 30 | 0 |
| Registered complete source-specific witnesses | 50 | 50 | 0 |

New frozen source IDs closed: **none**. PB-007-01 through PB-007-04 and PO-04/05/08 retain their unresolved universal obligations. MC-B and MC-1 remain NOT_ESTABLISHED. This is DETERMINISTIC_MODEL proof research, not an independent geometric oracle, native material/topology qualification, usable engineering STEP or permission to launch production repositories or paid/native campaigns.

No existing MC-1 domain or 26 supported operations are narrowed. Journal intent, process semantics, durable disconnected bodies/lineage, topology, numerical policies, exact source ownership, UNDECIDED/UNCERTIFIED nontruth and historical failure custody remain protected.

## Next critical-path step

Obtain distinct-session source-level review, exact PR-head CI and guarded integration for this bounded method only. Then, independently from the active H0–H2 degree-zero composer, prove how a complete closed original-source composition consumes certified *nonconstant* source child events with exact knot point value, separate one-sided orders, zero intervals (including half-open membership), interior-event isolation and physical signs, without promoting source-specific witnesses into a universal PB-007 theorem.
