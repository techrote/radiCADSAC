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

## Hypothesis, executed candidate and falsification

The candidate comprises two real B-spline pieces on global [0,2], phase u/4.
Each carrier has local polynomial `t-1/2`, cosine harmonic one amplitude 1/100,
and sine harmonic two amplitude 1/200. Left/right physical factors are
`(t-1)^2*(2*t^2-1)^2` and `t^3*(2*t^2-1)^2`, applied to EVERY amplitude.

This actual source has now executed successfully in the repository. Both pieces
retain v19-owned strict carrier and unchanged v50/v51 product evidence. V52
certifies five distinct OPEN roots. The knot u=1 counts once, with one-sided
orders [2,3], opposite neighborhood signs and no invented global analytic
multiplicity. Negating only the right piece preserves those orders but makes the
knot a tangency. The main six maximal sign cells have signs
NEGATIVE/POSITIVE/POSITIVE/NEGATIVE/POSITIVE/POSITIVE.

Decisive failures include an unqualified span, forged lowering/source/control
binding, matching signs accepted as physical equality, a missed/duplicated knot
root, sum-of-orders reported as analytic multiplicity, incorrect nonzero bridge
coverage, replacement proof search in the checker, altered old results, or a
resource limit becoming successful evidence. Tests explicitly challenge these
conditions; successful counts alone are not the acceptance rule.

## Actual repository execution checkpoint

Implementation head `639c87ff710663e267ff2399f1b9cc8f355b9733` passed focused
**37021963532** and repository `mc1-static` **37021963708** on the first attempt.
The focused log (job **110887010209**) confirms exact-head checkout and PASS for
all six new source/core tests and twelve new actual-source integration methods.
It also executes the full preserved v51/v50 regression: seven v51 core, thirteen
v51 integration, seven v50 core and eleven v50 integration methods, with inherited
v48/v49 contracts. No test or mathematical predicate was weakened to obtain green.

The new core/integration groups reported 0.052 / 10.301 seconds on Ubuntu 24.04.5
and CPython 3.12.14. These are model execution observations, not native geometry
qualification, performance acceptance thresholds or mathematical resource bounds.

The actual integration confirms nonzero physical knot continuity from harmonic
cancellation despite unequal amplitude limits, coalescing six elementary cells
into five maximal cells with the knot point covered. Same-sign but unequal values,
including the tiny positive jump control, correctly BLOCK the new global result.
Both exterior-root orders, cropped/global/reversed sources, full source negation,
unknown-field/Boolean/float rejection, stale proofs after visible digest updates,
all source/span/join/root/cell corruptions, resource non-truth and unrelated
exception propagation are covered. The finite full-source checker passes with
source/carrier classification, derivative selection and sign searches disabled.

## More than one knot and final-head acceptance

After this first passing checkpoint, the verifier adds a distinct three-span
actual-source control to falsify a possible single-join-only implementation.
Use left/right factors as above and middle factor
`t^3*(t-1)^2*(2*t^2-1)^2`, on global [0,3] with the same phase law and carrier
formula. The required result is eight globally ordered roots, two distinct knot
crossings counted once each, local orders [2,3] at both joins and nine sign cells.
It also challenges swapped join records and repeated span witnesses, and checks
the full original source with replacement searches disabled.

These additional assertions and the reconciled report do not change the model,
finite checker, original eighteen test methods or historical evidence. They must
pass on the final head and independent merged-main run before #269 is closed.
Their actual outcome and exact final head/tree/merge/run identities are recorded
in the issue ledger rather than presumed from the earlier passing checkpoint.

## Reproduction and integrity

Six original-source controls independently expand Bernstein coefficients back
to powers; check repeated knots and unioned channel partitions; different degrees;
cropped source/global phase maps; Boolean/float/unknown-field rejection; and
unchanged input data. Twelve actual-source integration methods cover the cases
above; the verifier additionally executes the three-span control and full
preserved v51/v50 tests.

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v52.py --contract --self-test
```

The editing environment has no complete local GitHub checkout; there is no claim
of new local test execution or substituted predecessor integration. The actual
GitHub checkout produced the evidence above. One pre-publication multiline test
guard syntax error was corrected with `ExitStack` before opening the PR; assertions
and theorem premises were unchanged. No CI repair was required at the recorded
checkpoint. Further attempted failures, if any, must remain in the issue ledger.

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
