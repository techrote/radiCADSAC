# PB-007-01 v49 — exact mixed-boundary multi-cut monotone composition

Status: bounded deterministic-model construction established by actual repository
integration for MC-038 / #263. Final-head and independent merged-main checks are
mandatory before closure; producing identities are recorded in #263's ledger.
PB-007-01 remains OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`.
The machining domain remains frozen at 26 operations.
Reviewed base: `d13d1e24d13f087a999a68228c200136d9aedf79` (v48).
No historical source, evidence, journal or programme registry is overwritten.

## Scope, hypothesis and falsification

V49 generalizes the v47/v48 composition representation, not their derivative
inequalities. A complete finite partition at source-owned orientation roots and
an explicitly fixed historical phase-boundary family qualifies only when every
closed cell has a complete physical derivative certificate. Failure of any cell,
endpoint or binding prevents parent certification.

The source `A=t^2-t+469/2500`, `B=t/2-1/4`, `C1=A+B`, `S1=A-B`,
`C2=1/100000000`, phase `-1/8+t/16` on `[0,1]`, is now verified BLOCKED by
complete v48 and certified by four V43/V42/V42/V43 children. None of the three
individual cuts qualifies both entire children through those recipes. This
novelty was executed in full repository CI, not inferred from local algebra.

## Independent endpoint fields and exact partition

Each boundary is rational or a selected real generator of an irreducible minimal
polynomial with v45 canonical root index/isolation. A cell is its ordered endpoint
pair plus unchanged parent-coordinate source. Conjugates are distinct embeddings.
No unrelated field subtraction, artificial midpoint, normalized algebraic width
or undocumented Q(alpha,beta) compositum is used. Global source/phase endpoint
values are affine evaluations in each endpoint's own field. The positive rational
parent width supplies the original-parent/global derivative scaling.

Rational order uses rational subtraction; rational/algebraic order uses one field
sign test. Equal minimal polynomials compare root indices. Distinct irreducible
minimal polynomials cannot share a root, so refining their exact rational
isolations to separation terminates. Interval overlap is never root equality.

The corrected v48 producer supplies full-source rational endpoints, rational
interior roots, irrational roots, multiplicities and complete accounting. Add only
crossings of `-3/16+k/2` and `-1/16+k/2` for each active positive harmonic through
the exact rational-affine phase. Enumerating integers in its finite phase range
produces a finite rational cut set. No recursive source subdivision or heuristic
sample point is used. Exact equal cuts merge all causes; endpoint roots never
produce zero-width cells. Consecutive boundaries cover the parent without gaps
or overlaps. Source knots already delimit the lowered parent spans.

The candidate B root at 1/2 coincides with harmonic 2's diagonal boundary and is
one cut with both causes. Independent v45 bisections are endpoint evidence only,
not normalized maps for the multi-cut children. Each actual cell declares
`normalized_child_map: null` and an unchanged-parent boundary-pair representation.

## Boundary-local Sturm proof

Construct the rational Sturm sequence of the square-free part of nonzero original
rational p(t). Evaluate every member independently at both boundaries. At a zero,
the first nonzero derivative of order j determines local sign: to the right its
sign, to the left that sign times `(-1)^j`. The positive factorial is irrelevant.
Finite jets apply to sequence members and to original p.

With V denoting variations, the distinct open-root count is
`V(left+) - V(right-)`. A common number field is unnecessary. Endpoint roots are
excluded; multiplicity comes from original p, not the square-free polynomial.
Identity-zero polynomials receive no finite root count.

Strict positivity requires positive values at both endpoints and zero open roots.
The inherited weak-sign predicate permits endpoint zeros but still excludes
interior roots, including even tangencies. Inward jets determine its sign, not an
invented midpoint. Weak admission is permitted only for appropriate V43 channels,
never the complete strict margin.

Primary reference: Manuel Eberl, [Sturm's Theorem, AFP](https://isa-afp.org/entries/Sturm_Sequences.html).
This formal theorem reference does not assert that the repository adapter itself
is Isabelle-formalized.

## Uniform phase containment

For rational nonzero r, phase o+r*t is monotone. Select a candidate diagonal cell
using the exact floor of `2*(h*(o+r*t_min)+3/16)`. A nonzero rational-affine image
of an irrational endpoint is irrational and cannot equal an integer boundary;
exact isolation refinement reaches a unique floor. Rational values, including
integer equality, are direct. Both endpoint containment inequalities are then
checked exactly. Negative r reverses phase range, not source order.

Uniform containment allows the preserved bounds L=2856/2197, U=99/182,
W=99/70, K=44/7. With X=cos+sin, Y=cos-sin and diagonal parity d:
`L <= d*Y <= W`, `|X| <= U`, `6 < 2*pi < K` throughout the entire closed cell.
This is not a sample-based sign claim.

## Complete unchanged derivative inequalities

From physical source regenerate `A=(C+S)/2`, `B=(C-S)/2`, A-prime and B-prime.
The selected derivative is `A'*X+B'*Y+2*pi*h*r*(A*Y-B*X)` in the original parent
coordinate. V42 proves strict B-prime sign and the sufficient margin
`L*|B'|-U*|A'|-K*|h*r|*(W*|A|+U*|B|)-sum|R| > 0`.
The physical derivative sign is sign(B-prime)*d.

V43 proves nonzero weak sign sigma_A of A and sets `eta=sigma_A*sign(h*r)`.
It proves one weak sign of eta*B-prime, permitting identically zero B-prime.
Let c=L for favorable/zero B-prime and c=W for adverse B-prime; require
`c*eta*B'+6*L*eta*h*r*A-U*|A'|-K*U*|h*r*B|-sum|R| > 0`.
The physical derivative sign is eta*d. The favorable phase term stays correlated.

R retains harmonic-zero and every non-anchor amplitude/phase derivative. Both
selected amplitude/phase channels remain represented by the full identity.
Enumerate every finite sign orthant and prove each rational margin strictly
positive using boundary-local Sturm. These are the unchanged v47 mathematical
inequalities over a new interval representation. Equality still fails. No weak
predicate, numerical trig oracle or relaxed threshold replaces strict dominance.

## Endpoint evidence, composition and checking

Rational boundaries retain v19/v6 rational-turn evaluation. Irrational boundaries
use v46 equality/multiplicity/checked rational sign enclosures bound through their
source-regenerated v45 bisections. Orientation multiplicity is never copied into
physical multiplicity.

The v47 strict-monotone child summary supplies zero/one open simple root from
endpoint signs. Endpoint zeros must agree with derivative-implied simplicity and
independent v46 multiplicity. Adjacent strict closed children of one smooth source
must agree in derivative direction at the shared boundary; a contradiction
rejects. This restriction does not alter separate original spline-span semantics.

After full source/partition/cell/derivative/endpoint validation, unchanged v27
composition counts each shared physical equality once with matching multiplicity.
A nonzero proof cut contributes no physical root. Cut positions are opaque exact
boundary records, requiring no cross-field subtraction.

The finite checker regenerates the source partition and witness-specified
mode/harmonic recipes; it never searches alternate routes to rescue bad evidence.
It uses the v46 endpoint checker, not a fresh endpoint sign search, and compares
the entire assembled source/cause/cell/map/count/capability record. Unknown grammar
and refusal behavior retain complete v48 precedence.

## Executed evidence, termination and residual scope

Initial exact PR head `acabfbce7edb63864ae32b19ab849f67d0a7cb43` passed focused
**36938994942** and static **36938994888** on the first attempt. Actual CI passed
14 core plus 11 source-integration methods, including the genuine predecessor
residual, five-child different-minimal-polynomial variant, mixed/repeated roots,
external and internal physical roots, corruption, rates/global coordinates,
resources and unchanged ownership. No implementation repair was needed. The
three checked model/checker files are also byte-identical to the preserved
candidate and pinned in the evidence artifact. The earlier local-only status
remains historical in PR commits, not the current acceptance claim.

Independent Fraction/Bernstein margin checks run alongside Sturm/field checks.
All source maps, rational and irrational endpoint APIs and the public classifier
were exercised by actual repository integration, not offline substitutes.

Root separation, field sign, floor and v46 refinement terminate from their
non-equality/nonvanishing premises. Polynomial operations and orthants are finite.
Memory/recursion/overflow are non-truth resource refusals; a workflow timeout
never proves a mathematical result. Exact final-head and independent merged-main
checks remain required before issue disposition, recorded on #263/#100.

General nonmonotone coupled zero isolation, noncommensurate phases, arbitrary
partition searches and normalized multi-generator maps remain unqualified. No
native geometry, STEP realization, MSAC UI or production OpenSimachinist claim
follows. Protected source/audio/provenance, journal, exact time/path/phase,
uncertainty, material, cutter/holder, body/lineage, refusal/UNCERTIFIED and
conventional STEP semantics remain intact. No native/paid/production campaign.
