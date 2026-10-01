# PB-007-01 v47 — algebraic-interval monotonicity and single-cut composition

Status: bounded deterministic-model construction; PB-007-01 remains OPEN.
MC-B and MC-1 remain `NOT_ESTABLISHED`. The domain remains 26 operations.
Owner: MC-038 / #259. Reviewed base: v46 / PR #258 at
`2b67c7e6b4befff04dfc456af6afb0894aafc4e8`.

## Scope and hypothesis

V45 represents an algebraic single-cut bisection; v46 decides the physical
predicate at the shared irrational endpoint. Neither supplies the complete
closed-child derivative proof needed to consume that cut. V47 supplies that
proof for a bounded lift of the preserved v42 transition and v43 correlated
handoff identities, then composes exactly two qualified children. No arbitrary
multi-cut partition, multi-generator compositum or universal solver is claimed.

The hypothesis is that exact rational Sturm sequences evaluated in the selected
real field can establish every polynomial premise of those derivative theorems
on `[0,alpha]` and `[alpha,1]`. Failure of either complete child margin, endpoint
relation or source binding blocks the parent. Endpoint success alone never
qualifies a child. Historical successful sources retain their complete result
and owner; unknown source fields retain predecessor rejection.

## Exact polynomial boundary authority

For a nonzero rational polynomial p, construct MC-032's Sturm sequence of its
square-free part. Evaluate every member at each boundary using Horner evaluation
in the v45 selected real field, including rational boundaries embedded in that
field. Reducing p modulo alpha's minimal polynomial is only p(alpha); it is not
p(0), p(1) or p at another boundary.

If a sequence member vanishes at a boundary x, find its first nonzero derivative
of order j. Its immediate right sign is the sign of that derivative; its immediate
left sign is multiplied by `(-1)^j`. The positive factorial is irrelevant to
sign. The derivative search terminates because the member is a nonzero polynomial.
Identically zero polynomials are handled separately, with no finite root count.

Let V be the number of variations after zero signs are omitted. The distinct
open-root count is `V(left+) - V(right-)`. Thus a root exactly at either boundary
is excluded from the open count, while its exact multiplicity is reported from
its original polynomial jets. Repeated roots are counted distinctly by the
square-free Sturm chain; their multiplicities are never read from that chain.

Strict positivity on a complete closed child requires positive values at both
endpoints and zero open roots. The v43 weak-sign premise permits endpoint zeros
but still requires zero open roots and a consistent nonzero inward sign; even
interior tangencies are deliberately outside this inherited sufficient test.
The identically zero B-prime channel is explicitly permitted only as the v43
zero contribution. A weak premise can never replace a strict complete margin.

Reference: Manuel Eberl, [Sturm's Theorem, Archive of Formal Proofs](https://isa-afp.org/entries/Sturm_Sequences.html),
provides an independently formalized Sturm theorem. V47's executable boundary
and one-sided-jet adapter is tested research code, not an assertion that this
repository is itself Isabelle-formalized. Its exact arithmetic and zero/sign
operations remain pinned MC-032/v45 authority.

## Uniform phase containment

A harmonic phase is affine in the original lowered-parent coordinate t. Its
range on a closed child is exactly bounded by its two endpoint values. Those
values are compared in the same real field against the preserved rational cell
`[-3/16+k/2, -1/16+k/2]`. A single-cut child has one rational exterior endpoint,
which uniquely selects the possible integer k; exact containment still checks
both endpoints, including equality. Negative phase rates reverse the range but
not the source interval. No rational replacement for alpha is used.

On this cell, write `X=cos(theta)+sin(theta)`, `Y=cos(theta)-sin(theta)`,
`d=(-1)^k`, and `y=d*Y`. The inherited exact v34/v42/v43 bounds are
`L <= y <= W`, `|X| <= U`, `6 < 2*pi < K`, with
`L=2856/2197`, `U=99/182`, `W=99/70`, `K=44/7`.
This uses uniform analytic bounds, not trigonometric samples at the endpoints.

## Complete physical derivative

From the original selected quadratures derive `A=(C+S)/2`, `B=(C-S)/2`.
The complete selected derivative in t is

`A'*X + B'*Y + 2*pi*h*r*(A*Y-B*X)`.

Every selected amplitude derivative is represented by A-prime/B-prime; neither
is discarded. Every non-anchor amplitude derivative, non-anchor phase derivative
and harmonic-zero derivative stays in the explicit residual list R. A zero sine
harmonic is not a physical channel and is accepted only when identically zero.

**V42 lift.** Prove B-prime has strict sign sigma on the closed child. Orient
the derivative by `sigma*d`. Its lower bound is

`L*sigma*B' - U*|A'| - K*|h*r|*(W*|A|+U*|B|) - sum |R|`.

**V43 lift.** Prove A has weak sign sigma_A, allowing its endpoint zero, and set
`eta=sigma_A*sign(h*r)`. Then `eta*h*r*A >= 0`. Prove eta*B-prime has one weak
sign, or is identically zero. Its y contribution is bounded below by
`c*eta*B'`, where c=L for a favorable/zero channel and c=W for an adverse one.
Orient the derivative by `eta*d`; a lower bound is

`c*eta*B' + 6*L*eta*h*r*A - U*|A'| - K*U*|h*r*B| - sum |R|`.

The favorable phase term is kept correlated, exactly as in v43. For either lift,
enumerate every finite sign orthant of the absolute-valued polynomials and prove
each margin strictly positive with the preceding algebraic-interval predicate.
Finite orthant enumeration realizes the pointwise L1 envelope without numerical
minimization or partitioning on residual zeros. Any nonpositive margin refuses
the theorem, including exact equality. This is a sufficient bounded route, not
a test that all other derivatives must fail.

All derivatives and r use the original lowered-parent t. For a global source
interval `[l,u]`, the local phase is `o+r_global*l + r_global*(u-l)*t`, and the
global derivative is the local derivative divided by the positive rational
width. V45's normalized child coefficients remain binding evidence but are not
fed to rational-only polynomial routines. This avoids a mixed-coordinate
chain-rule error.

## Endpoint proof and composition

Exterior rational endpoints retain v19/v6 exact rational-turn authority. The
interior endpoint uses v46's exact equality/multiplicity and checked rational
sign enclosure. A child with strictly nonzero derivative has at most one open
root; opposite endpoint signs imply exactly one by continuity. Any admitted root
is simple. A zero endpoint with v46 multiplicity other than one contradicts a
strict-derivative certificate and is rejected, not relabelled.

A new source-regenerating checker validates the full v45 bisection, field,
original source amplitudes, source_parameter_id, phase, both child maps, every
Sturm/jet/orthant record, all endpoints and both root summaries. The derivative
checker recomputes only the finite witness-specified mode/harmonic recipe, not a
search for an alternate route. V46's independent endpoint checker verifies the
finite sign witness without rerunning sign search.

After binding and qualification, the unchanged v27 composer adds the child
open roots and counts an internal physical root exactly once only when both
endpoint relations and multiplicities agree. Its cut position now carries an
exact Q(alpha) coefficient vector in the enclosing bound field; the composer
only copies that coordinate, never converts it to a rational. A nonzero proof
cut contributes no physical root.

For this one smooth lowered polynomial span, both child derivatives are strict
on their *closed* intervals. Opposite strict directions would contradict their
common derivative at alpha and are explicitly rejected. This does not change
historical composition rules for weak/non-strict or separate spline pieces,
where opposing directions can be legitimate.

## Witnesses and falsification controls

The main source is the recorded candidate:
`A=-1/8+t/2+t^2/10000`, `B=-7/40+7*t/20`, `C_1=A+B`, `S_1=A-B`,
`C_2=1/100000000`, phase `-1/8+t/16`.
The selected root is the unique root of `t^2+5000*t-1250` in `(1/8,1/4)`.
Acceptance requires actual complete predecessor BLOCKED status, followed by
V42-left / V43-right strict closed-child proofs and exact composition.

The suite distinguishes the event-neutral irrational cut from a genuine simple
physical root. For the latter, `q=t^2+t-1`, `B=q`, `A=q^2/100` and a live
non-anchor multiple of q-squared give different orientation multiplicities but
physical multiplicity one. The analogous common order-two source must remain
outside strict monotonicity. Exterior left/right zeros and root-free examples
are tested at the low-level qualified source interface without claiming novelty
when earlier whole-source authority already owns them.

Other controls cover boundary Sturm zeros, internal repeated roots, strict
margin equality and exact signed neighbors, all derivative channels, reversed
phase traversal, source negation, non-unit source intervals, corruption of
source/field/Sturm/orthant/endpoint/map/composition evidence, unknown grammar
fields and exact resource refusal. The focused actual-repository checks, not a
local supporting oracle, are the integration acceptance evidence.

## Termination, resources and remaining work

All polynomial differentiation, Sturm chains and sign orthants are finite.
Field sign decisions terminate from the selected irreducible minimal factor and
convergent exact isolating intervals. V46 sign refinement is entered only after
its nonvanishing proof and has its own termination argument. Resource exhaustion
always remains typed non-truth; there is no precision/depth/timeout-as-truth cap.

Only single-cut bisections with both closed children qualifying are consumed.
Required sources failing these sufficient derivatives, arbitrary multi-cut
partitions, noncommensurate phases and complete coupled zero isolation remain
open. Do not retry MC-B from this package alone. Protected source/audio/provenance,
journal, exact time/path/phase, uncertainty, material, cutter/holder, body/lineage,
refusal/UNCERTIFIED and conventional STEP semantics are unchanged. No MSAC UI,
production OpenSimachinist integration, native or paid campaign is authorized.
