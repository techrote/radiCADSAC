# PB-007-01 v49 — exact mixed-boundary multi-cut monotone composition

Status: implementation candidate for MC-038 / #263. Local core validation is
complete; full-repository source acceptance and landing remain pending.
PB-007-01 remains OPEN; MC-B and MC-1 remain `NOT_ESTABLISHED`.
The machining domain remains frozen at 26 operations.

Reviewed immutable base: `d13d1e24d13f087a999a68228c200136d9aedf79` (v48).
No historical source, evidence, journal or programme registry is overwritten.

## Scope, hypothesis and falsification

This package generalizes the v47/v48 composition representation, not the
supported derivative inequalities. It qualifies a complete finite partition
at source-owned orientation roots and an explicitly fixed historical
phase-boundary family only if every closed cell has a complete physical
derivative certificate. Endpoint decisions alone do not qualify an interval.
Failure of a single cell or endpoint prevents parent certification.

The recorded candidate is

`A=t^2-t+469/2500`, `B=t/2-1/4`, `C1=A+B`, `S1=A-B`, `C2=1/100000000`,
with phase `-1/8+t/16` on `[0,1]`.

Local exact tests prove the V43/V42/V42/V43 inequalities on four successive
cells. They also show that none of the three isolated candidate bisections
qualifies both entire children through those recipes. Complete executable
v48 residual status must additionally be established by repository integration;
local inequalities alone are not proof of predecessor novelty.

## Representation: independent endpoint fields

Each boundary is either an exact rational or the selected real generator of an
irreducible rational minimal polynomial with canonical real-root index and
isolating interval from v45. A cell is the ordered pair of those boundaries
with the unchanged parent-coordinate source material.

The two endpoint fields may differ. Even conjugates of one minimal polynomial
are distinct real embeddings. No subtraction of unrelated field elements,
synthetic midpoint, normalized algebraic width, or undocumented compositum
Q(alpha,beta) is performed. Global source and phase values are affine evaluations
at each boundary separately. The positive rational parent width supplies the
original-parent/global derivative scaling.

Rational/rational order uses rational subtraction. Rational/algebraic order is
a sign test in the selected field. Equal minimal polynomials compare real-root
indices. Distinct irreducible minimal polynomials cannot share a root; refining
their rational isolations until disjoint therefore terminates. Overlapping
isolations are never equated.

## Source-derived finite partition

The corrected v48 producer supplies full-source rational endpoint, interior
rational and irrational orientation records, multiplicities and accounting.
It is not replaced by the historically faulty v44 producer.

Add crossings, for every active positive harmonic, of precisely
`-3/16+k/2` and `-1/16+k/2` for integer k through the rational-affine parent phase.
These are the existing v34/v42/v43 diagonal-cell boundaries. Enumerate only the
integers in the exact closed harmonic-phase range; there is no recursive search
for convenient source cuts. Every crossing maps to a rational parent parameter.
No other phase-cut family, arbitrary midpoint or adaptive source cut is used.

Merge exact equal boundaries, retaining all causes and original multiplicities.
Existing source knots already delimit lowered parent spans. Endpoint roots
attach to exterior boundaries, never producing zero-width children. Consecutive
ordered boundaries cover the entire parent without gaps or overlaps. The
candidate B root at 1/2 coincides with harmonic 2's diagonal-cell boundary and
must appear exactly once with both causes.

V45 independent single-cut bisections remain source-bound endpoint evidence
for each irrational boundary. They are not normalized maps of the new children.
Each new cell explicitly has `normalized_child_map: null` and an unchanged-parent
boundary-pair representation.

## Boundary-local Sturm proof

Construct the rational Sturm sequence of the square-free part of nonzero
original rational p(t). Evaluate each member independently at each boundary
with rational arithmetic or that boundary's selected field. At a zero, the
first nonzero derivative of order j determines the local sign: to the right it
is the derivative sign; to the left it is multiplied by `(-1)^j`. The positive
factorial is irrelevant to sign. This finite jet calculation applies both to
sequence members and to the original p.

With V denoting sign variations, the distinct open-root count is
`V(left+) - V(right-)`. The endpoints need not inhabit one number field.
Endpoint roots are excluded from the open count; multiplicity comes from the
original polynomial, not its square-free part. The identically zero polynomial
has a separate disposition and is not assigned a finite root count.

Strict positivity requires positive endpoint values and zero open roots. The
inherited weak-sign sufficient predicate permits endpoint zeros but excludes
interior roots, including even interior tangencies. Its sign comes from inward
jets, not an invented midpoint. It is used only for the favorable V43 channels,
never for a complete strict margin.

Primary theorem reference: Manuel Eberl, [Sturm's Theorem, AFP](https://isa-afp.org/entries/Sturm_Sequences.html).
This independently formalized theorem does not imply that this repository's
new adapter has been formalized in Isabelle.

## Exact whole-cell phase containment

For nonzero rational r, phase o+r*t is monotone. Its closed-cell range follows
from its endpoints. Select the possible diagonal cell by the exact floor of
`2*(h*(o+r*t_min)+3/16)`. A nonzero rational-affine transform of an irrational
endpoint is irrational, so cannot equal an integer boundary. Exact isolating
refinement to a unique floor terminates. Rational values, including integer
equality, are handled immediately. This selects only a candidate cell: both
endpoint containment inequalities are then checked independently and exactly.
Negative r reverses phase range without reversing source order.

Uniform containment, rather than favorable values at sampled points, allows
the preserved bounds L=2856/2197, U=99/182, W=99/70 and K=44/7. With X=cos+sin,
Y=cos-sin and diagonal parity d, these give `L <= d*Y <= W`, `|X| <= U` and
`6 < 2*pi < K` on the entire child.

## Unchanged complete derivative inequalities

Regenerate `A=(C+S)/2`, `B=(C-S)/2`, A-prime and B-prime from source. The selected
harmonic derivative in the original parent coordinate is
`A'*X+B'*Y+2*pi*h*r*(A*Y-B*X)`.

V42 proves a strict sign of B-prime and the sufficient margin
`L*|B'|-U*|A'|-K*|h*r|*(W*|A|+U*|B|)-sum|R| > 0`.
Its physical derivative sign is the sign of B-prime times d.

V43 proves a nonzero weak sign sigma_A of A and sets
`eta=sigma_A*sign(h*r)`. Prove one weak sign of eta*B-prime, allowing the
identically zero B-prime channel. Let c=L for favorable/zero B-prime and c=W
for adverse B-prime; require
`c*eta*B'+6*L*eta*h*r*A-U*|A'|-K*U*|h*r*B|-sum|R| > 0`.
The physical derivative sign is eta*d.

In both recipes R retains the harmonic-zero derivative and every non-anchor
amplitude and phase derivative. Both selected amplitude and phase channels
remain represented by the complete rotated-coordinate identity.

Every finite sign orthant is enumerated and its rational margin proved strictly
positive using boundary-local Sturm authority. These are exactly the v47
inequalities with a new interval representation. Equality still fails; no weak
predicate substitutes for a strict margin. No trigonometric sampling, numerical
oracle or relaxed threshold is introduced.

## Endpoints, composition and finite checking

Rational boundaries retain v19/v6 rational-turn authority. Irrational boundaries
use v46 equality, physical multiplicity and its independently checked rational
sign enclosure, bound through the source-regenerated v45 bisection. Orientation
multiplicity is never assumed to be physical multiplicity.

The preserved v47 strict-monotone summary gives one open simple root for opposite
endpoint signs and none for matching nonzero signs. Endpoint zeros must agree
with derivative-implied simplicity and independent v46 multiplicity. All strict
closed children of one smooth lowered span must agree on derivative direction
at shared endpoints; contradiction is rejected. This does not change one-sided
semantics between separate original spline spans.

Only after full source/partition/cell/derivative/endpoint validation may the
unchanged v27 composer sum open roots and count shared physical equality once
with matching multiplicity. Cut coordinates are opaque records and need no
cross-field arithmetic. A nonzero proof cut contributes no physical root.

The finite checker regenerates source partition and witness-specified
mode/harmonic derivative recipes, not alternate successful recipes. It uses
the v46 endpoint checker rather than a fresh endpoint sign search, and compares
the entire assembled record including source binding, causes, cells, counts,
representation and capability flags. No caller-provided proof is authority.

## Termination, evidence and remaining scope

Root separation, selected-field sign, exact floor and v46 sign refinement have
their stated non-equality/nonvanishing termination premises. Polynomial operations
and sign orthants are finite. Memory, recursion and overflow failures are typed
resource refusals; workflow timeouts never establish truth.

Before publication, fourteen local core methods passed against byte-identical
MC-032 and v45 files. No SymPy or substituted field was used. An explicit-source
offline witness additionally checked the two irrational v46 endpoints and finite
rational sign witnesses at three rational boundaries. Neither result exercises
the complete predecessor/source integration. Repository acceptance is pending
until the mandatory complete self-test actually runs successfully.

The remainder includes general nonmonotone coupled zero isolation,
noncommensurate phases, arbitrary partition searches and normalized maps over
multiple algebraic generators. No native geometry or STEP realization claim
follows from this deterministic model. MSAC UI and production OpenSimachinist
remain out of scope. All protected source/audio/provenance, journal, exact
time/path/phase, uncertainty, material, cutter/holder, body/lineage,
refusal/UNCERTIFIED and conventional STEP contracts remain intact.
