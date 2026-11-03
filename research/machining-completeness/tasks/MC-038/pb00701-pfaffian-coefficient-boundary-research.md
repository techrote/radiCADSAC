# PB-007-01: a concrete Pfaffian coefficient-domain boundary

Status: bounded deterministic-model research, 2026-11-03. Preregistered in
[MC-038 issue #100, comment 6592881622](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6592881622).
Qualified context base: `828df02d3d61b57bd46b0c4a796ce58685d9c987`.
PB-007-01/02/03/04 remain OPEN; MC-B and MC-1 remain NOT_ESTABLISHED;
production authorization remains false.

## Result and exact scope

One explicit rational B-spline/trigonometric source demonstrates a missing
adapter premise. A formal extension of a published Pfaffian subresultant recipe
introduces a partition coordinate that is algebraic over Q(pi) and
transcendental over Q. The qualified v46 endpoint interface requires coordinates
algebraic over Q. That interface therefore does not automatically cover this
cut. The source itself has an elementary complete zero-set proof.

This is one new research fixture outside the frozen fifty-source cohort. It
does not complete another historical refusal, add a corpus row, modify any
qualified source producer, widen v46, or change a finite census. The useful
result is the concrete coefficient/domain obligation, together with a
reproducible distinction between an auxiliary partition cut and a physical
source event.

The executable model checks exact rational identities and bounds. The memo
supplies the analytic reasoning and identifies pi transcendence as an external
theorem. This division is explicit in the JSON report. No numeric interval is
used to infer algebraicity, and no proof-assistant formalization is claimed.

## Existing boundary and primary references

The existing [coupled B-spline boundary](../../../../docs/machining-completeness/31-PB00701-COUPLED-BSPLINE-BOUNDARY.md)
identifies effective Pfaffian methods as a possible direction whose coefficient
and sign-oracle requirements have not been qualified for this grammar.
The [v46 endpoint contract](../../../../docs/machining-completeness/70-PB00701-ALGEBRAIC-ENDPOINT.md)
uses rational polynomial amplitudes, rational affine turn phase, and a selected
real coordinate algebraic over Q. Its number-field and Gelfond-Schneider
arguments use that coordinate premise.

Barbagallo, Jeronimo and Sabia's
[2016 zero-counting paper](https://arxiv.org/pdf/1506.07406), Section 3,
Notation 9 and Algorithm ZeroCounting in Section 4, takes integer predicate
and differential polynomials. Its rational-endpoint algorithm uses signs at
real algebraic coordinates. The
[2019 decision paper](https://arxiv.org/pdf/1905.10882), Theorem 1, retains
integer polynomials and real-algebraic interval endpoints. These assumptions
must be checked before applying either result.

The [published 2016 article](https://doi.org/10.1016/j.jalgebra.2015.11.050)
is in Journal of Algebra 452, 549-573. An
[author-institution copy](https://ri.conicet.gov.ar/bitstream/handle/11336/55545/CONICET_Digital_Nro.6eba8fad-8fcb-4b03-b234-e6e81624f2d2_A.pdf?isAllowed=n&sequence=2)
places Notation 9 on pages 557-558 and the algorithm on pages 560-561.
The derivation below is this leaf's calculation under a **formal, unqualified
coefficient-field extension**. It is not an application of the cited
integer-coefficient theorem to admitted input.

## One original source, including every channel

Use the original parameter t on the closed interval [0,1], with turn phase t/4:

```
H(t) = t*(1 + cos(pi*t/2)) - sin(pi*t/2).
```

The source belongs to the existing
`RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE` grammar. Its parameter identity
is `pb00701-pfaffian-coefficient-boundary-original-t`.

| Channel | Degree | Knots | Controls | Exact amplitude |
| --- | ---: | --- | --- | --- |
| C0 | 1 | [0,0,1,1] | [0,1] | t |
| C1 | 1 | [0,0,1,1] | [0,1] | t |
| S1 | 1 | [0,0,1,1] | [-1,-1] | -1 |

The two fully clamped degree-one basis functions on [0,1] are 1-t and t.
Their weighted sums give the stated amplitudes exactly. No channel is omitted,
and no local replacement parameter is used in the phase.

Let k=pi/4 and y(t)=tan(k*t). The tangent chart is analytic on (-2,2), which
contains the complete original closed interval. Its differential equation is

```
y' = k*(1+y^2).
```

The standard half-angle identities, with theta=pi*t/2, give

```
cos(theta) = (1-y^2)/(1+y^2),
sin(theta) = 2*y/(1+y^2),
H(t) = 2*(t-y(t))/(1+y(t)^2).
```

The model reconstructs the full numerator from the three actual amplitudes:

```
T*(1+Y^2) + T*(1-Y^2) - 2*Y = 2*(T-Y).
```

The denominator is positive. The constant factor two is also positive, so
removing it preserves zeros and their local orders. The explicitly normalized
polynomial for the next calculation is P=T-Y. Dropping C0 or confusing this
source's turn rate 1/4 with 1/8 changes the source identity and is refused.

## The actual degree-one partition coefficient

First work in Q[K,T,Y], with K a formal indeterminate and derivation

```
D = partial_T + K*(1+Y^2)*partial_Y.
```

Specializing K to k preserves these identities. It changes the differential
coefficient domain to Q(pi); it does not make that polynomial integral.

Exact division gives

```
P = T-Y,
D(P) = 1-K*(1+Y^2),
D(P) = K*(Y+T)*P + r(T),
r(T) = 1-K*(1+T^2).
```

The model independently evaluates the three-by-three Sylvester determinant
for P and D(P), obtaining the same r. Its verifier uses the permutation
determinant formula, rather than the model's cofactor formula.

In Step 1 of the cited recipe the leading coefficient is -1, the degrees in
Y are one and two, and the smallest required even leading-coefficient power
is two. Its reduced polynomial is therefore r. For the pair (P,r), the
degree-one indexed objects are:

| Object | Value |
| --- | --- |
| n0, n1, n2 | 2, 1, 0 |
| N | 1 |
| R0, R1 | P, r |
| tau0, tau1 | -1, r |
| rho2 | r |

Step 3 includes roots of these leading/subresultant coefficient polynomials.
Thus r genuinely occurs in this recipe's partition list. It is constant in Y
but nonconstant in the original parameter T. This is more specific than merely
observing that some unrelated resultant has a root.

The normalization matters at the level of exact certificates. Keeping the
literal numerator 2P instead gives

```
rem_Y(4*D(2P), 2P) = 8*r,
Res_Y(2P,D(2P)) = 8*r.
```

The cut locations agree, but the remainders are different. Both identities
are checked. The report never identifies the literal remainder with r without
the explicit positive normalization.

## A finite strict enclosure for the cut

After K=k, r has one positive root

```
alpha = sqrt(1/k-1) = sqrt(4/pi-1).
```

The model proves a strict rational enclosure for pi using finite Machin
arithmetic. For x=1/5 and 1/239, integration of the finite geometric identity
for 1/(1+x^2) gives

```
x-x^3/3 < atan(x) < x-x^3/3+x^5/5.
```

The Gaussian-integer identity

```
(5+i)^4*(239-i) = 114244*(1+i)
```

supplies the tangent of A=4*atan(1/5)-atan(1/239). The directed rational bounds
place A strictly between zero and 4/5. Also pi=4*atan(1)>2, because the
integrand 1/(1+x^2) is strictly greater than 1/2 on [0,1). Hence
0<A<4/5<1<pi/2. Tangent one in that branch gives A=pi/4. The integer identity
alone, without this branch argument, would not establish Machin's formula.

Combining the arctangent bounds with the correct subtraction directions gives

```
306134117864772/97476408149875 < pi
    < 670143059704/213311234375.
```

These imply 3<pi<22/7 and 3/4<k<11/14. Therefore

```
r(1/2) > 1/56 > 0,
r(3/5) < -1/50 < 0,
r'(t) = -2*k*t < 0 for t>0.
```

There is exactly one positive cut and it lies in (1/2,3/5). The negative root
lies outside [0,1]. The report also checks an exact enclosure for alpha squared
inside (1/4,9/25), using the reciprocal pi bounds. No floating-point arithmetic
or approximate equality is used.

## Why this cut is outside v46

Suppose alpha were algebraic over Q. The field of algebraic numbers is closed
under the rational operations, and 1+alpha squared is nonzero. Thus

```
pi = 4/(1+alpha^2)
```

would be algebraic over Q, contradicting pi transcendence. Alpha is therefore
transcendental over Q, while satisfying pi*T squared+pi-4=0 over Q(pi).

The external theorem is pi's transcendence. The primary bibliographic reference
is F. Lindemann, [Ueber die Zahl pi](https://doi.org/10.1007/BF01446522),
Mathematische Annalen 20 (1882), 213-225. Its publisher record was checked;
the historic transcendence proof is not rederived or computationally proved
by this leaf. The nonalgebraicity conclusion follows from that theorem and the
displayed exact identity, not from alpha's numerical enclosure.

The report's `v46_domain_decision` is a **modeled domain-admission refusal
derived from the pinned v46 contract**. The old v46 module is not executed,
and no submitted transcendental coordinate is smuggled through its rational
minimal-polynomial representation. The refused operation supplies no endpoint
sign or root/nonroot truth value. A separate elementary argument below does
establish the sign for this particular source.

Gelfond-Schneider does not say that every transcendental exponent produces a
transcendental exponential. This leaf makes no such inference. Its narrow
conclusion is that v46's algebraic-coordinate premise fails for this cut.

## The cut is neither a physical zero nor a critical point

On [0,1], y(0)=0 and y(1)=1. The tangent function is strictly convex there:
its second derivative with respect to t is
2*k squared*y*(1+y squared), strictly positive in the interior. A strictly
convex graph lies below its endpoint chord, so

```
y(t) < t for 0<t<1.
```

Since H=2(t-y)/(1+y squared), H is strictly positive throughout (0,1).
Its only zeros on the closed source are the two exterior points. Direct
differentiation gives

```
H'(0) = 2*(1-k) > 0,
H'(1) = 1-2*k < 0.
```

Both have inward one-sided order one. No outside germ is asserted. There is
one maximal connected nonzero component, the open interval (0,1), with
positive sign.

The model checks the exact quotient-rule identity

```
H'(t) = 2*(r(t)+k*(t-y(t))^2)/(1+y(t)^2).
```

At alpha, r vanishes but k>0 and alpha-y(alpha)>0. Therefore H'(alpha)>0,
as well as H(alpha)>0. This partition cut creates no physical root, critical
point, original source knot or new nonzero component. The resultant eliminates
Y independently; its common-root pair (alpha,alpha) is off the actual chain
graph Y=y(T).

## Rescaling does not discharge the missing premises

Set U=k*T. The chain becomes dY/dU=1+Y squared, with integer coefficients.
However, the source polynomial becomes U/k-Y, or U-kY after multiplying by
the positive constant k. The source interval becomes [0,k]. The new source
polynomial still has a nonrational coefficient, and k is a nonalgebraic
interval endpoint. The required coefficient and endpoint assumptions have
not both been restored.

This does not prove that every representation or algorithm must use alpha.
For example, the convexity proof already solves this source. Q(pi) is not
being described as uncomputable. Formal rational-function equality and signs
of suitable nonzero expressions may be handled using pi transcendence and
certified bounds. A broader exact Pfaffian extension might be possible, but
it needs its own coefficient, coordinate, zero/sign and termination contracts.

## Executed bytes, references and finite limits

The implementation imports only Python standard-library modules. It reads
four bounded, exactly pinned files as context references, never as imported
or executed proof producers:

| Reference | Git blob |
| --- | --- |
| Coupled source boundary, document 31 | `6005fc55e2d18e71639e6bc31cfbc1597bf4a915` |
| Algebraic endpoint contract, document 70 | `3d8b6e0c23f1a5488f791e8bb04a4ee76ab8885a` |
| Coupled B-spline model | `a086b625e1a6dea8bd202699d161167bb69cc9e7` |
| V46 endpoint model | `77c18cb5c8c0700072c65969c973e8f3c4c12a99` |

The report records each exact buffer's blob, SHA256, size and nonexecuted use.
The verifier hashes and compiles the model from the same bounded buffer with
`dont_inherit=True, optimize=0`. Preloaded project names and Python bytecode
do not substitute for it. Python and the standard library remain trusted;
no hostile-Python sandbox is claimed.

Public reports allow at most 512 KiB, 16,384 values, depth 24 and 4,096-character
strings. Exact types distinguish booleans from integers; custom values,
floats, cycles and shared containers are refused before serialization.
JSON duplicate keys and nonexact numeric forms are rejected. Rational tokens
are bounded canonical ASCII integers/ratios with at most 256-bit operands;
lexical and normalization checks precede Fraction construction. Polynomial
inputs permit at most 64 terms and total degree six, with 1,024-bit internal
arithmetic operands. The selected calculations stay far below those bounds.

Reference reads are capped at 64 KiB each, model compilation at 128 KiB and
report reads at 512 KiB. Report path text is bounded before constructing or
opening a path. Drift, malformed data, failed identities and exhausted budgets
are typed nontruth, never saved-report fallback.

## Verification and recorded falsifiers

Generate and check the fixed witness from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/machining-completeness/tasks/MC-038/pb00701_pfaffian_coefficient_boundary.py --write-report
PYTHONDONTWRITEBYTECODE=1 python3 research/machining-completeness/tasks/MC-038/verify_pb00701_pfaffian_coefficient_boundary.py --contract --self-test
```

The initial complete focused run passed all **30 tests**. Its contract and
tests completed in approximately 0.20 seconds in the author environment;
timing is observational and is not stored as proof authority. The verifier
decodes the reported polynomials independently and checks their identities
on a complete seven-point Cartesian grid. The admitted total degree is at
most six, so exact equality on that grid proves the multivariate polynomial
identities by repeated univariate interpolation; these are not sampled signs
of an analytic source. It separately uses a permutation determinant formula,
direct alternating-series sums and original source identities.

Meaningful controls omit C0, alter each source channel or phase, reverse the
chain derivative, drop or sign-flip remainder terms, omit the final
constant-in-Y partition coefficient, lose the literal factor eight, alter
Sylvester entries, reverse Machin subtraction or remove its branch evidence,
invent a Q-algebraic coordinate tag, rationalize k, promote alpha to an event
or critical point, split the sole physical cell, borrow the wrong source's
endpoint derivative, and drop the obligations after rescaling. They also
inject an actual polynomial proof failure into the public operation and
require typed nontruth without a certificate digest.

Resource sentinels check refusal before rational construction, file reads or
fresh proof execution. An actual timestamp-and-size-valid stale cache is
demonstrated to load under ordinary import, while the checked bootstrap uses
the source. Further controls cover a preloaded module, path replacement after
read, source assertions and future flags, reference drift, symlinks, oversized
buffers and retained JSON bytes.

The focused workflow has one Python 3.12 job and exactly nine paths in each
PR/main trigger: five owned files and four context references. It checks out
the literal PR head or pushed SHA. Separate repository static and historical
census workflows retain their own scope. Distinct technical review, applicable
head CI, guarded merge, tree equality and independent main-push checks remain
required for qualification.

## Consequences and remaining work

For MSAC, this does not change the modeling interaction, operation semantics,
undo/redo or journal requirements. For OpenSimachinist, it makes a potential
analytic adapter's missing coefficient/endpoint premise explicit; no native
geometry, topology, material state or STEP capability follows from it.

A future constructive route must specify its exact coefficient field,
coordinate representations, physical-versus-auxiliary event policy, sign and
equality procedures, and termination evidence. It may avoid this partition
recipe or prove a different adapter. This leaf does not establish a general
obstruction, undecidability, a Continuous-Skolem reduction, or the necessity
of Schanuel's conjecture.

The frozen 121/20/30 historical dispositions, fifty-source evidence, all old
reports and current-state snapshots are unchanged. All 26 operations,
original source/phase/provenance, journal/material/body/lineage and useful
conventional STEP remain required. PB-007 remains open, both programme gates
remain NOT_ESTABLISHED and production remains unauthorized.
