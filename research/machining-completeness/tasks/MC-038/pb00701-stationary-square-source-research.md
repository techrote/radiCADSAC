# PB-007-01 — complete stationary squared-amplitude sources

Status: deterministic research implementation, 3 November 2026. Task:
[MC-038 / #100](https://github.com/techrote/radiCADSAC/issues/100).
Preregistration: [6593958987](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6593958987).
Local proof, distinct verifier, independent review and hosted qualification are
separate gates; the final observed verification record is appended below.

## Bounded contribution and prior overlap

This checker takes a complete original single-span B-spline source and rational
polynomial hints P,Q. It reconstructs every original coefficient in global t
and verifies

\[
F(t)=C_0(t)+C_1(t)\cos(2\pi b)
    =P(t)^2\cos^2(\pi b)+Q(t)^2\sin^2(\pi b),
\]

where the original phase rate is exactly zero and
`C0=(P^2+Q^2)/2`, `C1=(P^2-Q^2)/2`. The admitted degrees are at most three for
P/Q and six for the source coefficients. The checker accepts valid bounded new
sources outside its demonstration inventory; names and hashes are not an
admission allowlist.

The repository already has stationary-polynomial authority for quarter-integer
original phase turns, through `cardinal_pair` in
`verify_pb00701_stationary_polynomial_order.py`. The original full-angle
convention makes b=1/4 a cardinal case there, although both half-angle squared
weights used here are positive. Integer, half-integer and quarter-integer
controls overlap that prior authority. The useful additional theorem admits
general bounded rational phases such as b=1/5 by exact positivity and common
polynomial factors, without evaluating their algebraic trigonometric weights.
Polynomial isolation and multiplicity arithmetic are established techniques
being reused; this leaf supplies the complete source-bound stationary proof.

The [coprime moving checker](pb00701-coprime-square-source-research.md) and
[shared-factor moving checker](pb00701-shared-square-source-research.md) retain
their nonzero-rate contracts. This implementation preserves the supplied rate
zero. It does not replace it with one, patch a moving guard or present a moving
source certificate as stationary authority.

## Exact phase cases

Canonical rational reduction classifies the phase without floating arithmetic.
For reduced b, denominator one means an integer, denominator two means an odd
half-integer, and every other denominator gives both weights strictly positive.
This includes negative offsets without a tolerance or sign/parity ambiguity.

| Exact branch | Original source | Complete physical reduction |
|---|---|---|
| Integer b | F=P² | Roots of P; P identically zero gives a continuum |
| Odd half-integer b | F=Q² | Roots of Q; Q identically zero gives a continuum |
| Both weights strictly positive | F=P²c+Q²s, c,s>0 | Roots of gcd(P,Q), except the both-zero pair is a continuum |

The inactive amplitude in either active-square branch remains fully bound by
the original coefficient identities. It cannot add physical roots. For
P=t−1/3 and Q=t−2/3, the integer branch has only 1/3, the half-integer branch
has only 2/3, and the both-positive branch has no roots.

An active-zero continuum does not require zero original coefficient channels.
At integer b, P=0,Q=1 gives C0=1/2,C1=−1/2 and F=0 throughout the closed source.
At b=−1/2, P=1,Q=0 gives the corresponding cancellation. Replacing either
continuum by an empty finite root list would assert the wrong proposition.
Malformed inactive hints or changed controls still fail full reconstruction.

For the both-positive branch and a nonzero amplitude pair, compute monic G and
check exact identities P=G P0, Q=G Q0. A fresh conditional Euclidean computation
and coefficientwise Bézout identity `A P0+B Q0=1` exclude simultaneous residual
amplitude zeros. Therefore

\[
F=G^2H,\qquad
H=P_0^2\cos^2(\pi b)+Q_0^2\sin^2(\pi b)>0
\]

at every real source point. This proves that the complete physical zero set is
exactly the closed polynomial zero set of G. No trigonometric evaluation at an
algebraic root or exact trigonometric coefficient field is needed. Zero P with
nonzero Q, or zero Q with nonzero P, is valid in this branch.

## Orders, coordinates and components

The selected nonzero polynomial has degree at most three. Its complete closed
root set is established by the qualified guarded GCD/Sturm/isolation stage,
with the actual original exteriors and an empty moving-carrier boundary list.
The full returned proof is checked: square-free reduction, division identities,
one-sided Sturm counts, every searched gap, midpoint conservation, strict
isolator bounds, multiplicity chains and the complete closed count.

A selected root of polynomial multiplicity m has physical source order **2m**.
The remaining factor is analytic and strictly positive at that root. The
maximum finite order is six. No moving-carrier order two is added. Thus
P=(t−1)^3,Q=(t−1)^2 at a both-positive stationary phase gives order four,
while a cubic active amplitude at an integer/half-integer phase gives order six.

Coordinates can be exact rationals or a square-free defining polynomial with
a certified unique open rational isolator. Such a descriptor need not use a
minimal or irreducible polynomial and does not establish irrationality. A
rational root may legitimately remain represented in that format. Physical
cell boundaries reference the selected root, never a bracket endpoint.

At most three finite roots and four positive components occur. Every interior
touch splits components even when both signs are positive. Nonzero original
exteriors are included in adjacent cells; exterior roots retain only inward
order/sign, with outside fields null. At a noncardinal phase a nonzero exterior
value need not be rational, so the output records its proved positive sign and
leaves the scalar value unclaimed.

A continuum has a closed interval, exact identity reason and null finite
counts/events/nonzero cells. The polynomial isolator is not called on the zero
polynomial. This type has no finite cardinality or isolated-root order claim.

## Original source reconstruction

The input grammar requires two explicit cosine channels, harmonics zero and
one, no sine channels, and one fully clamped span per coefficient. Coefficient
degrees can differ and valid degree elevation remains admissible. Each complete
control vector is lowered using

\[
B_{i,d}(t)=\binom di
\left(\frac{t-lo}{hi-lo}\right)^i
\left(\frac{hi-t}{hi-lo}\right)^{d-i}.
\]

The checker validates every basis, partition of unity, global polynomial,
clamped endpoint and source identity. Nonunit intervals and negative origins
retain their actual global meaning. The source hash binds all original knots,
controls, degrees, interval, parameter ID and the unchanged phase law.

A bounded arbitrary parameter ID is allowed. A changed valid source or phase
can receive a fresh certificate; reusing an old certificate after rebinding
fails. Opposite signs of valid P/Q hints can describe the same squared source
and remain separately bound. No selected control or supplied success flag can
replace the complete identities.

## Checked reuse and public failure boundaries

`certify_source(spec,P,Q)` computes a fresh proof or throws typed refusal;
`check_source` returns that proof or atomic nontruth. `validate_certificate`
preflights the candidate and compares it to a fresh actual source proof.
Public source inputs accept no proof callback, expected count or trusted root
list. `source_from_polynomials` is a bounded fixture constructor only.

The actual stages are `lower_stationary_source`,
`classify_stationary_phase`, `select_stationary_polynomial`,
`isolate_stationary_polynomial` and `assemble_stationary_zero_set`. Each returned
proof is separately checked before becoming source truth. The report formatter
revalidates actual retained source, phase, selection, isolation and topology
premises; a failed stage cannot be replaced by saved success.

Only conditional arithmetic, source-coefficient checking, GCD/Bézout and complete
polynomial isolation are reused from the qualified modules. The old conditional
coefficient checker has no moving-phase premise and checks the actual original
zero-rate binding. Neither moving public certifier, moving lowerer, moving
fixture constructor, phase lattice, residual-source builder nor moving jet
routine supplies this stationary proof.

## Finite resource envelope

Every raw source and hint token is checked before rational construction on the
public proof path, including inactive amplitudes. Tokens are canonical reduced
ASCII integer/ratio strings with at most 128-bit operands. Original endpoints
lie in [−2,2], |b|≤8 and the canonical original rate is zero. Source and hint
degrees, exact types, controls and knot lengths are checked before computation.

Derived rational arithmetic has the unchanged **4096-bit pre-operation growth
guard**. The complete polynomial search has a global **128-midpoint** budget,
including endpoint tightening. The JSON envelope is 4 MiB, 131072 value nodes,
depth 48 and bounded strings; code/reference files are individually bounded to
256 KiB. Duplicate keys, floats/exponent numbers, Boolean aliases, cycles/shared
containers, overlarge paths and exhausted work yield atomic nontruth.

The both-positive proof uses internal bounded quotient/Bézout arithmetic. It
does not construct a derived B-spline residual source, so it does not impose the
moving shared checker's separate 128-bit raw residual-control conversion limit.
For example P=Q=2^100*t on [0,2^-100], b=1/5 has bounded original controls and
a 201-bit derived coefficient that remains inside the arithmetic envelope.
This is a legitimate different theorem path, not a widened dependency limit.
Derived root coordinates likewise retain the 4096-bit envelope.

## Exact custody and workflow

Seven project inputs are captured and checked before project execution: the
qualified shared model, its coprime arithmetic model and five nonexecuted
references. The new loader compiles the shared module from its exact checked
buffer. Its subsequent loader reads the retained buffers, compiles the checked
coprime bytes and retains the same context buffers. Stale bytecode, preload
registrations and post-read path replacement cannot substitute source authority.
Assertions and future flags are preserved. Python and the standard library
remain trusted; no hostile-code sandbox is claimed.

MC032 remains a nonexecuted algorithm reference. No saved moving demonstration
report is replayed as stationary proof. The generated workflow covers exactly
these seven input paths and the five new owned paths: **twelve paths** in each
trigger, with the literal requested revision checked out.

## Demonstrations and falsifiers

Eight examples exercise all three branches: integer and half-integer active
roots, two algebraic-format common roots at b=1/5, a repeated common root at
b=1/3, disjoint amplitude zeros at b=1/5, and three closed continua including
nonzero-channel cancellation. Their expected mathematical projection is five
finite sources with five interior root occurrences and ten positive cells,
plus three continua. Actual generated totals are checked below after execution;
these numbers are not input authority.

With epsilon=2^-120, P=0,Q=1 is a continuum at b=1 and strictly positive at
b=1+epsilon. Similarly P=1,Q=0 distinguishes b=±1/2 from b=±1/2+epsilon.
All operands fit the raw envelope; ordinary floating rounding would erase the
difference. Other decisive controls include cubic exterior roots, order six,
valid elevation, negative/nonunit domains, rational algebraic-format roots,
large derived coefficients/coordinates and actual stage failures.

Mutations must reject wrong full controls, altered inactive hints, missing
common factors, false Bézout/Sturm/count evidence, changed phase classification,
moving order inflation, omitted exterior or midpoint roots, merged touches,
fabricated irrationality or nonzero scalar values, and continuum/empty-finite
confusion. A failed fresh proof never becomes a successful empty root list.

## Programme disposition

The [programme](../../../../docs/machining-completeness/00-PROGRAMME.md),
[DR-0026](../../../../docs/decisions/DR-0026-machining-completeness-programme.md)
and [execution protocol](../../../../docs/machining-completeness/07-EXECUTION-PROTOCOL.md)
remain authoritative. This bounded supplied-source family does not establish
arbitrary stationary harmonic algebra, multiple source pieces, a general
analytic solver, native material/topology or useful STEP.

No member is added to the frozen fifty-source or 121-source populations. Old
twenty-route-refusal/thirty-missing-premise dispositions and all 26 operations
remain unchanged. PB-007-01/02/03/04 stay open, MC-B/MC-1 stay NOT_ESTABLISHED
and production remains unauthorized. OpenSimachinist gains a bounded exact
predicate class; MSAC gains reproducible original-source/phase evidence, not
a new application interface or production project.

## Observed verification

The shared polynomial dependency qualified at main
`61ede6367fde4ea90bc396d4e0dfd14d484c78b3`, with shared model blob
`e445aae10a2a0eab49b4e958d030fa19f0cd3f7a` and coprime arithmetic blob
`4db47f79acff3c036e67ba03dd11b9bfb0a96bdb`, following
[acceptance 6597781477](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6597781477).
Only then were the final dependency pins bound and this source proof executed.

The first fresh model contract passed with exactly five finite sources, five
interior roots, ten positive cells and three continua. Three root coordinates
are rational and two use algebraic-format descriptors; four physical roots
have order two and one has order four. These values are derived from actual
record-level proofs and are not admitted as external count authority.

The distinct-author verifier passed the fresh contract and **39 actual unittest
methods** on first integration: 8.105 seconds in the test phase and 8.648053
seconds for the full command. An earlier static planning count of forty had
included the module-level test-suite factory; the observed executed method
count is thirty-nine. No extra test was added merely to change that count.
The valid 201-bit derived coefficient and 161-bit derived root-coordinate
controls passed, as did the moving-route prohibition and both-module custody
controls. The model required no correction from that integration run.

A third standalone reviewer oracle imports no candidate or project code and
uses complete known polynomial factors rather than Sturm for root counts.
It matched all eight original sources and phase branches, 112 direct original
Bernstein nodes, 21 count receipts, 96 sided-sign receipts, 113 division
identities and all physical roots/cells/continua. Canonical report SHA-256:
`d0efb29e08c08077f823ff1a2119c0c715f392073754ec9877466082beffe913`.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/machining-completeness/tasks/MC-038/pb00701_stationary_square_source.py --write-report --contract
PYTHONDONTWRITEBYTECODE=1 python3 research/machining-completeness/tasks/MC-038/verify_pb00701_stationary_square_source.py --contract --self-test
```

Repository validation passed with 361 Markdown files and two fixtures; the
machining-completeness and CI-impact self-tests passed. These timings and tests
describe deterministic research, not native performance. Final distinct review,
literal-head hosted checks, guarded merge and independent landed-main acceptance
remain separate integration gates, recorded on the PR and issue #100.
