# PB-007-01 v53 — exact mixed-owner continuous spline spans

Date: 2 October 2026. Issue: #271. Evidence class: DETERMINISTIC_MODEL.
Reviewed main baseline: `7126dabf013ef95b0965b74008466e12f0650ef8` (PR #272).
Implementation scope: bounded source-bound event composition, not native geometry.
Acceptance authority: executed repository tests and the exact-head/merged-main
ledger on #271/#100. This report does not itself declare a branch landed.

## Hypothesis and falsification

V52 can lower the complete original source and compose product-owned spans, but
its supplied-view interface does not admit a neighboring already-checked strict
span without a nonconstant amplitude GCD. A separate `STRICT_SPAN` view should
close that interface boundary without changing physical predicates or historical
ownership. The principal falsifiers are a discontinuous physical join, a missing
complete derivative witness, a different actual owner, a changed original source,
or a checker that selects replacement proofs rather than checking supplied ones.

The preserved V52 pre-edit authority ran successfully on branch head
`4859d419276c49afac5d4419598f2be96b639ce4`, workflow run **37033679813**. Its tracked
archive artifact **11238467420** reproduced tree
`7247ac6daf095d0a54a8ee8dd961deece485f14c` locally. The archive SHA-256 was
`9ae03a24bd230db5a42607d2c796ab7c80c7f951e5820cff6cb2cb1e9895dee0`.
The implementation was tested against these actual modules, not isolated substitutes.
The archive contains the tracked tree, not Git history. Local history-dependent
Genesis bootstrap validation therefore refused missing pinned historical commits;
it was not bypassed. Required `mc1-static` runs use the real full-history checkout.

## Executed principal original-source result

The source encoder constructs ordinary exact rational B-splines for every
physical amplitude on `u in [0,2]`, with phase `u/4`:

```text
left,  t=u:   (2*t^2-1)^2 * (t-1/2 + cos(2*pi*u/4)/100 + sin(4*pi*u/4)/200)
right, t=u-1: t+1/2 + cos(2*pi*u/4)/100 + sin(4*pi*u/4)/200
```

Complete V52 returns `NOT_ALL_SOURCE_SPANS_HAVE_V51_PRODUCT_WITNESSES`. The actual
left owner is V50, with its checked V51 ordered product evidence. The actual right
owner is V19 and its amplitude GCD is one. The left monic common factor is
`t^4-t^2+1/4`, so the normalized quotient carrier is four times the displayed one.
Both physical source limits at the knot are exactly `1/2`.

V53 certifies two distinct open physical roots: a simple crossing followed by an
irrational double tangency. The maximal open sign cells are NEGATIVE, POSITIVE,
POSITIVE. The last cell includes the nonzero source-knot point and elementary
cells 2 and 3. Neither historical route is replaced or relabelled. The complete
V52 predecessor envelope remains separately byte-identical.

## Construction and finite truth interface

`pb00701_mixed_owner_span_model.py` implements the `V51_PRODUCT` / `STRICT_SPAN`
view schema and full-source wrapper. Product views retain the complete unchanged
V51 ordered witness. Strict views retain the original complete V19/V47/V48/V49
route, physical source binding, checked derivative provenance, exact endpoint
relations, implicit root descriptor where applicable, and sign cells.

The existing V50 `validate_carrier` routine is used only as a finite strict-owner
checker router. Its temporary argument does not assert a product or a factorization;
no `g=1` nonconstant factor is manufactured. V51's checked direction extraction
examines every derivative child, and V52's original-source lowering, continuity,
root-union and maximal-cell composition formulas are reused without modification.

`validate_mixed_certificate(candidate, original_spec)` independently regenerates
lowering and all normalized views from supplied historical witnesses, exact
physical knot differences, one-sided orders, root ordering and elementary/maximal
coverage. It does not trust normalized views, caller polynomials, envelope hashes
or claimed counts. Strict endpoint zeros have local multiplicity one. A shared
simple/repeated zero is counted once with orders such as `(2,1)`, never their sum
or a fabricated global analytic multiplicity at a nonsmooth source knot.

The finite checker runs with original/new source classifiers, carrier proof
selection, derivative mode selection and irrational endpoint/factor sign searches
disabled. Preserved deterministic owner-witness recipes and rational-turn
algebraic equality/sign regeneration remain enabled, exactly as in V52. Those
finite operations do not search for a more favorable replacement certificate.

An open strict root is a source-bound `UNIQUE_ANALYTIC_ROOT` bracketed by exact
endpoints, with strict derivative and opposite endpoint sign evidence. Its minimal
polynomial is null and its arithmetic nature UNCLAIMED, even in the test where an
independent rational-turn calculation proves the root happens to be `1/2`.

## Adversarial and source integration evidence

Seven direct test methods and fourteen full-source integration methods execute
many owner/source/mutation subcases. They cover all four actual strict owners,
every closed derivative child, both strict directions, root-free/open/exterior
cases, distinct fields and implicit coordinates, source/witness/view corruption,
unit-factor forgery, and finite checking without replacement searches.

A three-piece all-strict zigzag gives three distinct implicit roots and directions
`(+1,-1,+1)`. A four-piece source with two product and two strict spans gives eight
open roots, four of them double tangencies in two distinct selected quadratic
fields. Both use genuine original B-spline source partitions. Mixed shared-knot
controls prove both crossing and tangency with separate orders `(2,1)` and exact
non-unit global jet scales. Source reversal, cropping, nonconstant live harmonic
amplitudes, differing channel degrees/knot partitions and repeated knots are tested.

Continuity is the full physical difference, not equality of amplitude channels
or endpoint signs. Harmonic cancellation at a nonzero knot is admitted. Positive
same-sign jumps of `1/10` and `1/10^80` remain discontinuity blockers. Original
controls, knots, phase, identity, harmonic and degree changes cannot be rescued by
replacing the source digest or claimed lowering. Typed Boolean/float/unknown
fields preserve historical rejection or ignored-annotation dispositions.

Existing successful all-product V52 output is byte-for-byte unchanged. A direct
all-product V53 view construction also reproduces its counts without rewriting
that historical result. Memory/overflow/recursion refusal at each new stage remains
non-truth and retains the known predecessor; unrelated runtime errors propagate.

## Recorded negative attempts and corrections

The first local integration expected a whole predecessor phase dictionary to
match V52's normalized phase dictionary. The former additionally carries
`shared_parameter`; the corrected binding explicitly checks that identity plus
both exact offset/rate values. No physical or proof predicate was relaxed.

An initial no-search guard named the V48 root-producer module rather than the
actual classifier in `pb00701_mixed_orientation_consumer`. Correcting that test
target allowed the intended disabled-classifier assertion to execute.

Several proposed positive transforms selected older `EXACT_RATIONAL_AMPLITUDE_DOMINANCE`
ownership on root-free spans. In particular, reversing the principal candidate
has that actual owner; V53 explicitly refuses it while retaining the predecessor.
It does not reroute that source to V19 to make a test pass. Positive reversal is
established instead on the genuinely admitted mixed simple/repeated-knot source.
An initial four-piece construction also left a product carrier outside the allowed
strict ownership. The executed continuous zigzag construction supplies actual
admitted owners on every piece. These are fixture-premise corrections, not changes
to historical selection or new checking predicates.

## Verification and remaining boundary

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v53.py --contract --self-test
```

The versioned JSON contract pins the reused V19/V50 and complete V52 artifacts;
V52's inherited contract retains V7/V44–V51 pins. The focused job executes the full
preserved V52 verifier chain once, not duplicate parallel copies. Exact final-head
focused and `mc1-static` success, expected-head-protected squash merge, exact
main/parent/tree confirmation, independent merged-main checks and acceptance
ledger are required before #271 closure. The PR #272 current-state ledger is
updated only after that verified landing.

Unsupported owners need their own finite checked ordering interface. General
noncommon-factor/nonmonotone analytic coverage, discontinuous point-value policy,
implicit-coordinate arithmetic and native material/topology/STEP qualification
remain separate obligations. This bounded result does not retry MC-B.

PB-007-01 OPEN globally; PB-007-02 dependent; PB-007-03 OPEN; PB-007-04
OPEN_PROPAGATED; PO-02/04/05/07/08 OPEN as recorded. MC-B and MC-1 NOT_ESTABLISHED.
All 26 operations, source/audio/provenance, canonical journal, exact time/path/phase,
source uncertainty, positive-volume material, cutter/holder, durable body/lineage,
refusal/UNCERTIFIED and conventional STEP semantics remain protected. No native,
paid, production or expensive campaign, shared-registry or settings change occurs.
