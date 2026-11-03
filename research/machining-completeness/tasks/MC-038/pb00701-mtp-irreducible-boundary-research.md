# MC-038: rational-turn boundary for MTP irreducibility lemmas

Status: implemented finite research, 3 November 2026. Local verification is
recorded here; distinct technical review, exact-head hosted checks and integration
acceptance are separate records under [MC-038 / #100](https://github.com/techrote/radiCADSAC/issues/100).

## Result

A direct transfer of two rational-radian polynomial lemmas to the repository's
rational-turn source variable fails on an exact quadratic example. This finding
does not contradict the cited paper or rule out another constructive method.

Let

\[
g(T,Y)=(T-1)^2+Y^2.
\]

This polynomial is irreducible over `Q[T,Y]`. Nevertheless,
`g(t,tan(pi*t))` has a double zero at `t=1`. The coprime pair `T-1` and `Y`
also has that nonzero common root after the same substitution.

The denominator-cleared original source is

\[
\begin{aligned}
F(t)&=(t-1)^2\cos^2(\pi t)+\sin^2(\pi t)\\
&=\frac{(t-1)^2+1}{2}
  +\frac{(t-1)^2-1}{2}\cos(2\pi t),
\qquad \frac12\le t\le\frac32.
\end{aligned}
\]

Its complete closed zero set is exactly `{1}`, with multiplicity two. Both
exterior values are one, and its two maximal nonzero components have positive
sign. The original source remains defined at both poles of the auxiliary tangent
chart. The [model](pb00701_mtp_irreducible_boundary.py),
[certificate](pb00701-mtp-irreducible-boundary.json) and
[verifier](verify_pb00701_mtp_irreducible_boundary.py) bind those statements to
the actual original B-spline controls and global phase.

## Primary theorem scope

Chen, Li, Xia, Zhao and Zheng study rational polynomial expressions in one
radian variable and its trigonometric functions. In the checked
[arXiv:2301.05847v1](https://arxiv.org/pdf/2301.05847), Proposition 5.1
(printed page 30, PDF index 29) makes nonzero roots simple for irreducible
`g(x,tan(x))`, with `g` over `Q`. Proposition 5.2 (printed page 31, PDF index 30)
excludes nonzero common roots for coprime rational bivariate polynomials under
that same substitution. The coefficient field and the same radian variable are
material hypotheses. Their published article is
[Isolating all the real roots of a mixed trigonometric-polynomial](https://doi.org/10.1016/j.jsc.2023.102250),
*Journal of Symbolic Computation* 121 (2024), 102250; theorem numbering here
refers only to the full preprint that was read.

The initial preregistration described pages 29–30 using PDF indices. The correct
printed page numbers are 30–31; the statements and selected hypothesis are
unchanged.

## Authority, source and exact grammar

This five-file leaf was preregistered in
[comment 6593311189](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6593311189)
at qualified main `9eea5786f93c71090d4a3d4c7478d65a3f066d42`.
Root authors its model, verifier, report, memo and workflow. A distinct AI worker
reviews the mathematics and exact files; independent authorship of the verifier
is not claimed for this leaf.

The selected ID is
`research:pb00701:mtp-irreducible-boundary:quadratic-touch`, with original
parameter ID `pb00701-mtp-irreducible-boundary-original-t`. It is a new research
source outside the frozen fifty-source cohort and does not increment that census.

| Original field | Exact value |
|---|---|
| Closed source interval | `[1/2,3/2]` |
| Global phase in turns | `t` |
| Cosine harmonics | `0` and `1` |
| Sine channels | None |
| Degree of both coefficients | `2` |
| Fully clamped knots | `[1/2,1/2,1/2,3/2,3/2,3/2]` |
| Harmonic-zero controls | `[5/8,3/8,5/8]` |
| Harmonic-one controls | `[-3/8,-5/8,-3/8]` |

Writing `u=t-1/2`, the quadratic Bernstein basis is
`((1-u)^2,2*u*(1-u),u^2)`. The executable lowering retains global `t` and
checks its partition identity. The controls give
`C0=((t-1)^2+1)/2` and `C1=((t-1)^2-1)/2` exactly. The amplitude coordinate
`u` is never substituted into the global phase.

The model checks every raw rational token before constructing any Fraction,
requires the full original source schema and then checks the canonical complete
source identity. Each control, harmonic, knot, degree, parameter and phase
remains material even if a different expression happens to define the same
periodic function. Public source admission is fixed to this one source.

Four context files are read as bounded pinned bytes and are **not executed**:

| Context reference | Exact Git blob |
|---|---|
| [Coupled source boundary](../../../../docs/machining-completeness/31-PB00701-COUPLED-BSPLINE-BOUNDARY.md) | `6005fc55e2d18e71639e6bc31cfbc1597bf4a915` |
| [Coupled B-spline model](pb00701_coupled_bspline_model.py) | `a086b625e1a6dea8bd202699d161167bb69cc9e7` |
| [Qualified Pfaffian boundary model](pb00701_pfaffian_coefficient_boundary.py) | `2fe093dca21de8e6dc60e275825955ec0161f6ec` |
| [Qualified Pfaffian boundary certificate](pb00701-pfaffian-coefficient-boundary.json) | `fe82029ab0360d422a9aea716157cf70b6fc9ec1` |

The prior Pfaffian example concerns a coefficient-domain partition cut. This
example concerns a failed direct irreducibility/common-root lemma transfer.
Neither result changes the other source or supplies a universal analytic oracle.

## Irreducibility and the nonzero common root

Treat `g` as a monic quadratic in `Y` over the field `Q(T)`. A factorization
would make `-(T-1)^2` a square in that field. Dividing its square root by the
nonzero rational function `T-1` would then make `-1` a square. This is impossible
because `Q(T)` admits an ordering and a square is nonnegative. The quadratic
criterion and Gauss's lemma establish irreducibility over `Q[T,Y]`.

The certificate checks the complete polynomial, its translated form
`D^2+Y^2`, its monic leading coefficient and its discriminant `-4*(T-1)^2`.
The ordered-field argument and Gauss's lemma are explicit reviewed mathematical
premises. A finite evaluation grid is not claimed to prove a general
irreducibility theorem. Irreducibility over complex coefficients is not claimed.

For the common-root example, `p=T-1` is irreducible and does not divide `q=Y`:
division by `T-1` leaves `Y`. Thus they are coprime in `Q[T,Y]`. Both vanish
at `(T,Y)=(1,0)`, and `tan(pi)=0` supplies the exact analytic binding. The
corresponding radian point is `X=pi`, so this example is outside the hypothesis
that both polynomial coefficients and the independent radian variable use the
paper's original rational-polynomial specification.

## Exact source clearing and the full closed zero set

On the open tangent chart `(1/2,3/2)`, put `Y=tan(pi*t)`. The double-angle
identity gives `cos(2*pi*t)=(1-Y^2)/(1+Y^2)`. The model checks

\[
C_0(t)(1+Y^2)+C_1(t)(1-Y^2)=(t-1)^2+Y^2=g(t,Y).
\]

There is no omitted scalar or extra polynomial factor. Multiplication by
`cos(pi*t)^2` recovers the entire original `F`; near `t=1` this factor is
analytic and nonzero, so it preserves root order.

The full closed-source proof uses `F` directly. With `delta=t-1`,

\[
F(t)=\delta^2+(1-\delta^2)\sin^2(\pi t).
\]

On the exact original domain, `|delta|<=1/2`; hence `delta^2<=1/4` and
`1-delta^2>=3/4`. Since a square is nonnegative,

\[
F(t)\ge\delta^2,
\]

strictly away from `t=1`. At `t=1`, both summands vanish. This proves the
complete closed zero set without numerical sampling, an oracle or an unbounded
search. The executable certificate checks the amplitude identity and exact
rational coefficient margin that the reviewed inequality uses.

At both `t=1/2` and `t=3/2`, the original phase has cosine `-1`, so
`F=C0-C1=1`. The auxiliary tangent has poles there, but the original source does
not. Removing those source endpoints because of a chosen chart would change the
problem.

## Physical multiplicity and component semantics

Let `D=t-1`. The original harmonic cosine has Taylor coefficients
`[1,0,-2*pi^2]` through order two. The two original amplitude jets are
`[1/2,0,1/2]` and `[-1/2,0,1/2]`. Exact polynomial jet multiplication yields

\[
F(1+D)=(1+\pi^2)D^2+O(D^3).
\]

Consequently `F(1)=F'(1)=0` and `F''(1)=2*(1+pi^2)>=2>0`. The source is
analytic, so its physical root has multiplicity exactly two. The formal symbol
`K` in the certificate means `pi`, without a rational approximation.

The root is a positive touch. Its two maximal connected nonzero components are
`[1/2,1)` and `(1,3/2]`, both positive. Equal signs do not join components across
a physical zero. The root lies inside the one original source span; there are
no true interior source knots and no fabricated proof-cut event.

## Why the displayed rescaling does not restore the theorem hypotheses

Set `X=pi*t` and `K=pi`. Clearing `K^2` in `g(X/K,Y)` gives

\[
h(X,Y)=(X-K)^2+K^2Y^2.
\]

The executable identity `h(K*T,Y)=K^2*g(T,Y)` checks the rescaling. The new
coefficients belong to `Q(pi)`. The coefficient of `X^2` is one and the
coefficient of `X` is `-2*pi`. Any nonzero scalar that made the first coefficient
rational would itself be rational; making the second rational would then force
`pi` rational. Therefore no single scalar makes this displayed polynomial have
only rational coefficients. Pi irrationality is an explicit external theorem.

This is a conclusion about this displayed rescaling and these two direct lemma
transfers. It does not prove that all representations or reductions fail. A
solver for a broader coefficient field would need its own exact hypotheses,
proof and implementation. The selected example itself has just been solved
constructively by elementary source identities.

The distinction also matters when reading newer hardness results.
[Collins, Hanzon and Neumann, MFCS 2026](https://doi.org/10.4230/LIPIcs.MFCS.2026.65)
study unbounded ETP decision problems over broader computable fields. Their
Open Problem 1 (printed page 65:16) asks about zeros on bounded intervals with
rational endpoints. That paper supplies no hardness reduction for this bounded,
commensurate original-source grammar. No bounded undecidability or impossibility
conclusion is drawn here.

## Execution, custody and resources

The model imports only the Python standard library. The four context files are
checked and recorded as nonexecuted data. A changed, missing, aliased or oversized
reference refuses the certificate; no saved success replaces the read.

The verifier reads a bounded model buffer, checks its exact Git blob and compiles
that same buffer with source future/assertion semantics. It bypasses project
bytecode and preloaded modules. Its tests contain an actual timestamp/size-valid
stale cache accepted by ordinary Python loading before demonstrating that the
checked loader executes the verified source. A path replacement after the read
cannot change the retained executed bytes. Python and its standard library are
trusted; this is not a hostile-code sandbox.

| Bound | Limit |
|---|---:|
| Model code bytes | 128 KiB |
| Each context reference | 64 KiB |
| JSON bytes / nodes / depth | 512 KiB / 16,384 / 24 |
| Canonical rational operand bits | 256 |
| Reduced polynomial arithmetic result bits | 1,024 |
| Sparse polynomial terms / total degree | 64 / 6 |
| Report path text | 4,096 characters, no NUL |

Each arithmetic operation has already bounded rational operands; a binary
product can form at most a finite 2,048-bit numerator/denominator before its
reduced result is checked against the 1,024-bit limit. Polynomial operations
check degree and term limits throughout. No precision growth loop is used.
Canonical ASCII integer/ratio syntax, reduced form and operand sizes precede
Fraction construction. All source tokens are preflighted before any coefficient
work. JSON rejects floats, duplicate keys, aliases, cycles, excessive containers
and unsupported scalar types before replay.

The public `selected_transfer_probe()` first runs the complete selected
certificate and then returns typed refusal of the direct MTP theorem transfer,
with a digest of the successful boundary evidence. An actual proof failure
returns nontruth with no success digest and no established source zero set.
`validate_report(candidate)` preflights the candidate, reexecutes the proof and
compares canonical bytes. Conditional polynomial/source helpers are not an
arbitrary-source admission route.

## Verification

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python research/machining-completeness/tasks/MC-038/pb00701_mtp_irreducible_boundary.py --write-report
PYTHONDONTWRITEBYTECODE=1 python research/machining-completeness/tasks/MC-038/verify_pb00701_mtp_irreducible_boundary.py --contract --self-test
```

The focused verifier passes **29 tests**. Its arithmetic checks use direct
Bernstein evaluation and differentiation, independent of the model's sparse
polynomial lowering and jet convolution. For submitted degree-at-most-six
polynomials, exact equality on a complete seven-point Cartesian grid proves
polynomial identity by interpolation; this grid supplies no analytic root
completeness claim. The reviewed nonnegative-square argument supplies that
completeness.

Controls exercise every original coefficient; source/phase/knot substitution;
a factored quadratic with positive discriminant; lost tangent factors;
missing nonzero common-point evidence; wrong jet/multiplicity/crossing; merged
touching cells; omitted original chart-pole endpoints; false coefficient-field
rescaling; unwarranted theorem/hardness claims; actual source, irreducibility and
jet failures; saved-success fallback; parser/arithmetic limits; reference drift;
retained read buffers; and real bootstrap cache/preload/future/assertion behavior.

The [workflow](../../../../.github/workflows/mc1-pb00701-mtp-irreducible-boundary.yml)
has one Python job, literal candidate-head checkout, no matrix, and exactly nine
paths in each trigger: five owned files plus four nonexecuted references.
Distinct final review and hosted qualification are recorded separately; this
memo does not claim that those integration steps have already completed.

## Implications and limits

For MSAC, retaining the original time/phase correlation is necessary even when
a nearby theorem uses visually similar expressions. For OpenSimachinist, a
factorization or a phase-coordinate change cannot silently replace exact source
root multiplicity and component evidence. This selected double touch is fully
proved, but the work adds no generic owner adapter, native geometry or STEP
qualification.

The frozen fifty-source census, 121-case history, twenty historical refusals,
thirty historical missing premises, all earlier reports and all navigation
snapshots remain unchanged. PB-007-01/02/03/04 remain **OPEN**; MC-B and MC-1
remain `NOT_ESTABLISHED`; production authorization remains false. All twenty-six
operations, original source/phase/provenance, canonical journal, material/body/
lineage, refusal/`UNCERTIFIED`, and useful conventional STEP obligations remain.
