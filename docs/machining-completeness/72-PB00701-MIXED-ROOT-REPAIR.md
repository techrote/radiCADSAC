# PB-007-01 v48 — mixed rational/algebraic orientation-root repair

Status: bounded deterministic-model corrective package, owned by #261 under
MC-038/#100. Base: v47 main `8033c8102acc0cf1db77b259a56cee5cb85998ea`.
PB-007-01 remains OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`.
The independently defined domain remains 26 operations.

## Why this correction precedes broader partitioning

V47's actual-source endpoint test explicitly avoided orientation polynomials
with rational endpoint roots because its preserved v44 cut producer could not
handle them. This is an implementation defect in the existing producer, not a
missing transcendental theorem. V46 already supplies the relevant endpoint
layer and v47 already supplies the bounded complete closed-child inequalities.

Two same-path failures are retained as executable negative evidence:

* `t*(2*t^2-1)` retains the t factor in v44's supposedly irrational isolation
  workspace. Its root counter rejects a zero at the source interval endpoint.
* `(t-3/5)*(2*t^2-1)` has an interval isolating the irrational root after rational
  deflation that still contains the removed rational root of the original
  polynomial. Full-source multiplicity then correctly refuses nonunique input.

No weakened multiplicity or endpoint predicate fixes either error. The workspace
and final full-source certificate must have different, explicit obligations.

## Isolation and full-source binding

Let p be the original nonzero rational orientation polynomial and sf its
square-free part. Enumerate interior rational roots by the preserved exact
rational-root theorem. Remove factors for 0, 1 and those interior rational roots
from sf only in the isolation workspace w. This does not divide any amplitude
in the physical source and does not change its value, derivatives or roots.

The workspace has no rational root inside the unit interval and no root at its
endpoints. The existing exact Sturm isolation therefore yields dyadic intervals
with one irrational workspace root. For each such interval, continue exact
bisection until both endpoints are nonroots of sf and the full-source sf open
root count is exactly one. The target is irrational, so it never equals a
rational midpoint. There are finitely many distinct roots of sf, with positive
separation from the target; consequently the additional refinement terminates.
No arbitrary denominator, depth, precision, elapsed-time or resource threshold
is used as correctness evidence.

Certificates retain p's primitive coefficients and the complete primitive sf,
not the deflated workspace polynomial. Multiplicity is recomputed against p.
V45's irreducible minimal-factor selection and selected real embedding verify
irrationality; a caller label is insufficient. Rational and endpoint roots have
separate exact multiplicity records. The number of interior rational roots plus
irrational certificates MUST equal the independent MC-032 open Sturm count.
Failure raises an integrity error, not CERTIFIED with a false accounting flag.
Endpoint roots are excluded from the open count and are not internal cuts.

The original coefficients are retained separately from primitive/root-normalized
coefficients: scaling a source is not erased from provenance. A/B shared roots
are deduplicated by the preserved exact gcd/Sturm comparison, never by overlapping
approximate intervals. Distinct cuts retain exact order.

## Consumer integration without historical mutation

The new producer feeds the unchanged v45 bisection builder. Those source-bound
representations feed the unchanged v47 complete derivative recipes and v46
endpoint generator/checker. The new consumer only replaces the faulty root
production stage; it does not weaken any inequality, invent a phase sector,
omit an amplitude, or count an orientation root as a physical event.

The new checker regenerates the full original source, all root accounting, the
selected bisection, the witness-specified finite derivative recipes, external
rational endpoints and internal v46 endpoint evidence. It does not search for
a different derivative route or rerun an endpoint sign search. Then it invokes
the same v47/v27 physical event composer. A valid cut with unproved complete
child margins still yields BLOCKED. No full multi-cut/compositum is claimed.

The high-level source interface first calls complete v47. A previous success,
semantic rejection or typed resource refusal is returned unchanged. Only the
two named legacy root-isolation ValueErrors can select a recovery path. Even
then, complete v41 source validation/lowering is run independently before new
work. Exception text is not source admission, root evidence or mathematical
truth. Unrelated exceptions propagate; unknown source fields are not stripped.
There is no global monkeypatch or temporary dependency replacement.

## Verification and decisive source

`python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v48.py --contract --self-test`

The proposed actual-source regression modifies the verified v47 witness only
by replacing A with t*A, retaining B, C=A+B, S=A-B, phase and the live non-anchor
harmonic. The original boundary now has a rational A root at t=0 and retains
its irrational interior A root. Tests must reproduce complete-v47's legacy
exception and then establish a checked V42-left/V43-right event. Both phase
directions and a non-unit global source interval are covered independently.
No claim depends on the witness being newly monotone rather than newly reachable
through repaired source-root production.

Other tests cover rational roots on/inside the initial isolation interval,
nearby exact rational neighbors, repeated endpoint/irrational factors, rational-only
and identity inputs, complete counts, A/B deduplication, field construction,
forged source/count/multiplicity/isolation/map/endpoint records, unknown fields,
resource refusal and successful predecessor ownership. CI executes actual
repository dependencies, not the old ZIP's local arithmetic substitute.

## Preserved programme state

Historical v44-v47 source and evidence remain byte-pinned and unchanged.
PB-007-02 remains dependent, PB-007-03 OPEN, PB-007-04 OPEN_PROPAGATED,
PO-04/05/08 OPEN, MC-B/MC-1 NOT_ESTABLISHED. Source/audio/provenance, journal,
exact time/path/phase, uncertainty, positive-volume material, cutter/holder,
body/lineage, refusal/UNCERTIFIED and conventional STEP semantics are preserved.
No native, paid, production or expensive campaign is authorized.

After this repair the next constructive problem remains broader exact cut
composition and residual child theorem coverage, not the resolved endpoint
implementation gap. A source still failing complete derivative margins remains
explicitly unresolved. MSAC and OpenSimachinist receive no production capability
promotion from this research leaf.
