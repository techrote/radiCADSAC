# PB-007-01 v52 report — original source cross-knot composition

Date: 2026-10-02. Corrective owner: #269. Reviewed base: `08f22be41d14cd13fd17c00aa43b987259e887a9` (v51).  
Evidence class: deterministic exact-arithmetic model. Actual acceptance is the executed repository verifier plus final-head and merged-main evidence on #269/#100.

## Recorded gap and implementation

V51 supplies finite ordered-root/sign-cell evidence for each lowered source span
but explicitly does not glue genuine source knots or check arbitrary full-source
routing envelopes. V52 consumes the ORIGINAL SOURCE B-spline controls, degrees,
knots, harmonics, requested interval, source ID and shared rational-affine phase.
Its checker regenerates exact source lowering using the unchanged v7 arithmetic,
then validates every supplied v51 witness against the actual original channels.
A digest or supplied polynomial list is not source authority.

The new layer proves physical continuity at every shared rational source knot by
exact rational-turn evaluation of the complete right-minus-left expression.
Same-sign endpoints are not equality evidence. Individual amplitude continuity
is not necessary where their physical expression cancels exactly. Nonzero jumps
remain typed blockers for this bounded global construction and preserve all
predecessor evidence, without declaring the manufacturing input invalid.

Globally ordered events namespace local IDs and identify only both copies of the
same exact source knot. Shared zeros count once and retain BOTH one-sided analytic
orders. At a nonsmooth source knot no single analytic multiplicity is invented
or obtained by adding orders. A crossing/tangency is determined from the two
proved nonzero neighborhood signs. Opposite strict carrier directions on two
actual source pieces are not misclassified as a smooth-span contradiction.

Elementary cells retain every source knot and exact global/source bindings.
Maximal nonzero open sign cells include the bridge knot point only when its
physical value is proved nonzero and continuous. Physical roots, including even
ones with equal side signs, still separate cells. Completeness checks compare
all consecutive boundary pairs, both endpoint neighborhood signs, exact span
counts minus duplicated zero joins, and global open-root/maximal-cell counts.

The new finite checker re-lowers the full original source, checks only supplied
proofs and reconstructs the join and coverage certificates. Source/carrier
classifiers, derivative selection and irrational sign searches are disabled in
its tests. Exact resource failures remain non-truth; unrelated exceptions
propagate. The separately retained predecessor envelope is not new truth evidence.

## Hypothesis, candidate and falsification

The candidate comprises two real B-spline pieces on global [0,2], phase u/4.
Each carrier has local polynomial `t-1/2`, cosine harmonic one amplitude 1/100,
and sine harmonic two amplitude 1/200. Left/right physical factors are
`(t-1)^2*(2*t^2-1)^2` and `t^3*(2*t^2-1)^2`, applied to EVERY amplitude.

Expected after actual execution: each span retains v19-owned strict carrier plus
v50/v51 product evidence, and the global source has five distinct open roots.
The knot u=1 should count once, with local orders [2,3] and opposite neighborhood
signs. Negating only the right source piece should give a tangency with the SAME
orders. The main expected sign cells are NEGATIVE/POSITIVE/POSITIVE/NEGATIVE/
POSITIVE/POSITIVE. The tests execute complete predecessors before accepting
these outcomes; this report does not substitute expectations for execution.

Decisive failures include an unqualified span, forged lowering/source/control
binding, matching signs accepted as physical equality, a missed/duplicated knot
root, sum-of-orders reported as analytic multiplicity, incorrect nonzero bridge
coverage, replacement proof search in the checker, altered old results, or a
resource limit becoming successful evidence.

## Tests and reproducibility

Six original-source controls independently expand Bernstein coefficients back
to powers; check repeated knots and unioned channel partitions; different degrees;
cropped source/global phase maps; Boolean/float/unknown-field rejection; and
unchanged input data. Twelve actual-source integration methods cover principal
acceptance, crossing versus tangency with equal local orders, physical harmonic
cancellation at a nonzero join, same-sign unequal and tiny-jump blockers, both
exterior roots, reversal/affine/cropped source, whole-source negation, classifier-
free checking, adversarial lowering/span/knot/root/cell mutations, stale proofs
after updating visible source digests, missing owner/single-span precedence,
exact resources and unrelated exceptions. The complete v51 self-test (and its
full v50 regression) is also required.

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v52.py --contract --self-test
```

The editing environment has no complete local GitHub checkout; there is no claim
of new local test execution or substituted predecessor integration. Repository
CI is the execution authority. One pre-publication multiline test guard syntax
error was corrected with `ExitStack` before opening a PR; assertions and theorem
premises were unchanged. Actual attempt outcomes must be retained in the issue
ledger, including any further required repairs.

The focused workflow checks the exact PR head and independently checks the merged
main SHA after landing. Repository `mc1-static` must also pass on the final head
or identical verified synthetic merge tree. Use expected-head-protected squash
merge only after green; verify exact main/parent/tree and independent merged-main
checks before explicit issue completion. No final outcome is assumed from an
unrun verifier or written documentation.

## Scope and preserved programme

Nine new scoped files only; the original source modules and v7/v44-v51 historical
evidence remain unchanged. The verifier freezes their hashes, source authority,
protected semantics and 26 operations through the inherited v51 contract.

This is bounded continuous piecewise product composition, not a general analytic
zero solver, discontinuous point-value policy, global analytic multiplicity at
nonsmooth knots, native topology, material-body transition or STEP qualification.
PB-007-01 remains OPEN globally; PB-007-02 dependent; PB-007-03 OPEN;
PB-007-04 OPEN_PROPAGATED; PO-04/05/08 OPEN; MC-B and MC-1 NOT_ESTABLISHED.
All source/audio/provenance, canonical journal, exact time/path/phase, uncertainty,
positive-volume material, cutter/holder, body/lineage, refusal/UNCERTIFIED and
conventional STEP semantics remain intact. No native/paid/production/expensive
campaign, registry, settings or automation change.

Standalone proof and interfaces: `docs/machining-completeness/76-PB00701-PIECEWISE-PRODUCT.md`.
