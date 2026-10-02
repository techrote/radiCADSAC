# PB-007-01 v52 — continuous piecewise product roots and sign cells

Date: 2026-10-02. Issue: #269. Reviewed base: `08f22be41d14cd13fd17c00aa43b987259e887a9` (v51).  
Evidence class: deterministic exact-arithmetic research model. Acceptance is determined by the executed verifier and verified issue ledger, not this document or an issue's closed state.  
PB-007-01 remains OPEN globally. MC-B/MC-1 remain **NOT_ESTABLISHED**. Coverage remains **26 operations**.

## Purpose and bounded scope

V51 establishes an ordered physical-root/sign-cell decomposition of a checked
product `F=gH` on one already-lowered rational polynomial source span. It expressly
does not glue real source knots or validate an arbitrary full B-spline routing
envelope. V52 adds a separate certificate for the ORIGINAL SOURCE: rational
B-spline controls, degrees, knots, harmonics, requested global interval, shared
source parameter ID and one rational-affine phase law.

The initial extension requires every lowered span to have a checked v51 product
witness and every shared knot to have equal physical one-sided values. It does
not change old span proofs, add a new general analytic solver, or declare valid
manufacturing histories outside this sufficient family invalid. Discontinuous
point-value policy, unsupported span owners, native topology, material-body
transitions and STEP realization remain separate obligations.

## Exact source lowering and provenance

`lower_source` uses the preserved v7 normalizers and exact polynomial piece
lowerer. It takes the finite sorted union of all original channel knots inside
the requested interval, plus the two requested exteriors. Every adjacent pair
has positive rational width. Repeated knots identify one boundary, not duplicate
or zero-width spans. Channels may have different degrees and knot sets.

The source certificate retains each original normalized spline and reconstructs
all local rational amplitude polynomials in `t=(u-left)/(right-left)`, both
one-sided amplitude limits, the exact positive affine parent map, the original
source identity and the GLOBAL phase `offset+rate*u`. The span proof is checked
against this regenerated material. Copying the expected digest, editing the
claimed lowering, or removing a channel does not validate stale evidence.
Cropped intervals preserve original controls and restrict them exactly; no
resampling or tolerance changes the saved source.

The source wrapper runs complete v51 first and retains its complete predecessor
result. It augments only fully covered multi-span results. Older owners,
rejections, single-span results and resource outcomes keep their disposition.
The old envelope is retained as history, not promoted into truth authority for
V52. The independent finite V52 entry point re-lowers the original source itself.

## Physical continuity is equality, not equal signs

At a rational source knot `k`, all positive harmonic channels use the same exact
phase turn `offset+rate*k`. Let `F_minus(k)` and `F_plus(k)` be the two analytic
extensions from the neighboring lowered spans. Construct the right-minus-left
amplitude differences from the original source limits and evaluate their complete
trigonometric expression through the preserved v19/v6 rational-turn endpoint API.

Only an exact ZERO result proves `F_minus(k)=F_plus(k)`. Same-sign nonzero values
may differ; an arbitrarily small rational jump may not be discarded. A nonzero
difference returns `PHYSICAL_SOURCE_KNOT_DISCONTINUITY`, leaves predecessor
span evidence intact and does not reclassify the manufacturing input as invalid.
This package supplies no point-value convention for that discontinuous case.

Conversely, continuity of every individual amplitude is unnecessarily strong.
Different channel limits can cancel at the common rational phase so that the
PHYSICAL function is continuous. The test source with a nonzero shared knot
uses this case. V52 proves equality of the complete physical expression rather
than rejecting it on channel-wise discontinuity or accepting it from endpoint
signs alone.

For the supported equal-limits case, either inherited one-sided endpoint
convention gives the same physical value. V52 checks that the two finite span
proofs identify the exact same GLOBAL knot and have compatible physical endpoint
relations. The original source knots are not arbitrary proof-subdivision cuts.

## Shared physical roots and two-sided local orders

Each span has a finite checked analytic root order at its own endpoint. At a
shared physical zero, V52 keeps BOTH orders and both nonzero inward neighborhood
signs. A piecewise polynomial-modulated source need not be analytic across a real
spline knot. Therefore no single global analytic multiplicity is inferred there.

In particular, one-sided orders `(2,3)` do not imply multiplicity five, two, or
three for a common analytic extension. The certificate sets
`analytic_multiplicity=null` and retains `one_sided_orders=[2,3]`. It also retains
the source/phase/endpoint proof bindings and the positive global derivative
scales `width^(-order)` for each side.

The physical knot event is a CROSSING if the left and right nonzero neighborhood
signs differ; otherwise it is a TANGENCY. Two sources can have the same local
orders and different event kinds by negating one analytic piece while preserving
the zero join. Smooth-span derivative compatibility from v47/v49 must not be
misapplied here: opposite strict CARRIER directions on different real source
spans are permitted when their checked physical source limits compose.

The knot root appears ONCE in the ordered union. Non-knot roots preserve their
span's analytic multiplicity, including implicit simple carrier roots and exact
algebraic repeated factor roots. The exterior roots retain their single inward
analytic orders. No source knot or proof boundary becomes a physical root just
because it partitions the source.

## Global ordering and covered sign cells

A per-span algebraic or implicit root remains attached to its original selected
real field, local witness and exact positive affine GLOBAL image. Span indices
namespace all local IDs. Adjacent original spans are exactly ordered by their
rational source endpoints. Only the preceding right exterior and following left
exterior are identified, at their exact common source knot. No subtraction of
unrelated field elements, arithmetic on implicit roots or new compositum is used.

The elementary decomposition comprises every ordered boundary point and all
intervening nonempty open cells. Each cell binds its original span/cell index,
local proof digest, GLOBAL endpoints and physical sign. The verifier checks
consecutive coverage and agreement with each boundary's inward signs.

At a proved NONZERO continuous source knot, the two adjacent signs equal its
physical sign. Their open cells PLUS THE KNOT POINT form a larger connected
nonzero open interval. A maximal sign cell records all constituent elementary
cell indices and every included nonzero knot. At a physical zero, even an even
root with equal signs on both sides, the cells do not coalesce: the nonzero set
is separated by that root. Thus the maximal open sign cells count is exactly
`number_of_distinct_open_physical_roots+1`.

The closed global root count is independently checked as

```text
sum(span closed-root counts) - number of zero internal source knots.
```

Interior analytic roots, source-knot roots and exteriors have separate records.
The global summary never fabricates a `multiple_roots_open` classification that
would silently assign analytic multiplicity at nonsmooth knots. It states the
analytic multiple roots strictly inside spans, the knot roots without a claimed
global analytic multiplicity, global distinct counts and physical event kinds.

## Finite checking and refusal

Files are under `research/machining-completeness/tasks/MC-038/`.

`build_piecewise_source_evidence(spec)` runs complete historical source authority
and returns it unchanged alongside a new certificate only if the new construction
succeeds. `build_piecewise_certificate(spec, span_proofs)` is the direct supplied-
witness builder. `validate_piecewise_certificate(candidate, spec)` is the finite
truth interface and takes the ORIGINAL SOURCE, not caller-lowered polynomials.

The checker regenerates all source splines/knots/pieces; checks EVERY supplied
v51 span proof against those real pieces; recomputes exact physical differences,
source-knot identification, both-sided orders/signs, global ordered roots and
maximal-cell coverage; and requires exact typed serialization equality with the
candidate. It may not run source/carrier classification, derivative selection,
or the old/new irrational endpoint sign searches to replace a supplied proof.
Preserved finite rational-turn equality evaluation remains its existing exact
arithmetic operation, not a numerical search for a favorable sign.

The composition formula is shared deterministic code; it is not advertised as a
separate full geometry oracle. Independent Bernstein-to-power arithmetic controls,
actual-source positive/negative cases and adversarial source/proof mutations are
additional evidence. V51's independent series/remainder checking remains intact.

Memory/overflow/recursion failures are typed non-truth resource refusals. A new
global failure preserves the successful predecessor result separately. Unrelated
exceptions propagate. A failed equality or missing span witness cannot be repaired
by dropping a knot/channel, picking a replacement proof or changing an epsilon.

## Candidate, tests and acceptance authority

The principal actual source has global `u in [0,2]`, phase `u/4`, and two local
coordinates `t=u` and `t=u-1`. Its carriers are

```text
H(t)=t-1/2 + cos(2*pi*u/4)/100 + sin(4*pi*u/4)/200.
g_left=(t-1)^2*(2*t^2-1)^2; g_right=t^3*(2*t^2-1)^2.
```

Every amplitude is multiplied by its physical factor and encoded as ordinary
rational B-splines. The proposed expected result is five distinct open roots:
two implicit carrier roots, two irrational double factor roots and the shared
knot once. The knot has orders `(2,3)` and is expected to cross. Negating the
right source piece should change the knot to a tangency without changing those
orders. These are falsifiable tests, not acceptance until the actual complete
repository execution succeeds.

The source tests cover independent Bernstein expansion, repeated knots, different
channel degrees/knot sets, exact cropped/global maps and original input integrity.
The integration tests cover original-source novelty beyond v51's unclaimed global
union, all shared-root rules, nonzero physical continuity by harmonic cancellation,
same-sign unequal values and tiny jumps, exterior roots, reversal/negation,
source and certificate corruption, missing owners and resource non-truth. The
finite checker is exercised with classification and proof-selection/search
functions disabled. The full preserved v51 and v50 regressions also run.

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v52.py --contract --self-test
```

The environment used for editing lacks a complete local repository checkout;
full-source claims must come from the actual GitHub checkout, not partial-module
or alternate-oracle stand-ins. No new local test run is claimed in this document.
A multiline test guard syntax mistake was noticed before PR/CI and replaced by
`ExitStack` without changing its assertions. All actual attempts, final-head
checks, checked tree, expected-head merge and independent merged-main checks
belong in the #269/#100 acceptance ledger. Closure requires those checks, not
just successful source publication or this mathematical construction.

## Remaining programme obligations

The result is limited to continuous source knots and full v51 product coverage
of every span. Discontinuous point semantics, other source/span families,
noncommon-factor/nonmonotone analytic coverage and native material/topology/STEP
qualification remain open. These are bounded implementation/theorem obligations,
not claims of mathematical impossibility.

OpenSimachinist gains a source-bound piecewise event primitive; no MSAC interface,
canonical journal, production architecture or saved manufacturing intent changes.
Historical v7 and v44-v51 evidence is pinned and retained. PB-007-01 is OPEN,
PB-007-02 dependent, PB-007-03 OPEN, PB-007-04 OPEN_PROPAGATED, PO-04/05/08 OPEN,
and MC-B/MC-1 NOT_ESTABLISHED. Source/audio/provenance, exact time/path/phase,
uncertainty, positive-volume material, cutter/holder, durable body/lineage,
refusal/UNCERTIFIED and conventional STEP semantics and 26 operations are intact.
No native, paid, production or expensive campaign, registry/settings/schedule
change is authorized or implied by this package.
