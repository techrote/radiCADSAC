# PB-007-01 v46 — exact algebraic-irrational phase endpoints

Status: bounded endpoint-only research; deterministic model and reviewed argument.
Owner: #257 / MC-038. Baseline: verified v45 `e5efc6e441483b2ba594928b84aaa76cc7af1dc3`.
PB-007-01 remains OPEN. MC-B and MC-1 remain NOT_ESTABLISHED.

## Scope and preserved authority

The source is the existing finite, commensurate-harmonic grammar, on one exactly
lowered span. In its local coordinate t it is

`F(t) = C_0(t) + sum_{h>0} [C_h(t) cos(2*pi*h*(o+r*t)) + S_h(t) sin(2*pi*h*(o+r*t))]`.

Every amplitude is a rational polynomial, h is an integer, o and r are rational,
and r is nonzero. A source-owned algebraic-irrational orientation cut alpha lies
in (0,1). V45 supplies its irreducible minimal polynomial, selected real embedding
and exact Q(alpha) arithmetic. Harmonic-zero sine must vanish. All amplitudes,
including harmonic-zero and non-anchor channels, remain present.

The high-level adapter first executes the complete predecessor and adds evidence
only for unresolved v44/v45 algebraic-cut endpoint obligations. Already certified
physical events retain their owner. Unknown source fields, noncommensurate or
independent phase laws and nonexact source values retain predecessor rejection.
Known ignored caller metadata stays ignored, not promoted to evidence.

This interface does not solve whole-child derivative signs or root isolation,
combine multiple number fields, or certify a whole-span event. It returns the
entire predecessor physical event result unchanged. Independent two-child
representations do not become a full multi-cut event partition.

## Endpoint equality: a new, explicitly scoped reduction

Let tau=o+r*alpha and z=exp(2*pi*i*tau). Since r is a nonzero rational and alpha is
algebraic irrational, tau and 2*tau are algebraic irrational. Apply the
Gelfond–Schneider theorem with algebraic base -1 (neither 0 nor 1), algebraic
irrational exponent 2*tau, and the chosen logarithm i*pi of -1. Its any-value
formulation gives transcendence of z. A transcendental number over Q cannot be
algebraic over the algebraic numbers: a polynomial relation would involve only
finitely many algebraic coefficients, and transitivity of algebraicity would
make z algebraic over Q.

At alpha the source becomes a Laurent polynomial over Q(alpha,i). The collected
coefficients are C_0(alpha) at power zero and

`(C_h(alpha)-i*S_h(alpha))/2` at h,
`(C_h(alpha)+i*S_h(alpha))/2` at -h.

Multiplying by z^H removes negative powers without changing equality since z is
nonzero. Therefore F(alpha)=0 if and only if every collected coefficient is zero.
Because the chosen Q(alpha) embedding is real, this is equivalent to every
C_h(alpha) and S_h(alpha) being zero. V46 regenerates these exact reductions;
it never compares approximate trig terms to decide equality.

The historical v8 executable route used a narrower product-factor coincidence
exclusion. That code and its scope are unchanged. V46 proves the additional
algebraic-coefficient Laurent reduction above; it does not pretend v8 already
implemented this endpoint oracle. Neither general exponential sums with
independent phases nor transcendental source coefficients are admitted here.

## Physical multiplicity and identity

For each nonzero amplitude polynomial determine its finite order of vanishing
at alpha using exact derivatives and minimal-polynomial reduction. Identically
zero channels have no finite order and do not set the minimum. For nonidentity
sources let m be the minimum of the finite orders. All amplitudes have a local
factor (t-alpha)^m. Factoring it out of F yields an analytic function whose value
at alpha has coefficients p^(m)(alpha)/m!, with at least one nonzero coefficient.
The same Laurent argument proves this remaining function nonzero. Thus the
physical multiplicity of F is exactly m, including m=0 for a nonzero endpoint.

There is no omitted cancellation involving pi. When taking the mth derivative,
all terms in which derivatives hit a phase factor contain a lower-order
amplitude jet; those jets vanish. The first surviving amplitude jets retain all
channels. Multiplicity is never copied from a selected A or B orientation root.
For a real analytic scalar predicate the sign changes exactly when m is odd.

If every source amplitude is identically zero, return the inherited
`DEGENERATE_IDENTITY_ZERO` blocker with no finite multiplicity. No sign search
is attempted. Zero rational phase rate is predecessor-owned, not a
Gelfond–Schneider case.

For global source coordinate s=L+W*t with W>0, the cut is L+W*alpha, local phase
is (global_o+global_r*L)+(global_r*W)*t, and physical mth jet scaling is W^(-m).
V46 records these exact relations. Both v45 children meet at the same physical
endpoint; a single endpoint certificate is not two physical roots.

## Exact sign bounds

Only the algebraically proved NONZERO branch enters refinement. Every stage has
an integer n>0. It performs 2n exact Sturm bisections of the canonical alpha
interval and uses n terms of each series. The stage number is witness size, not
a correctness threshold. The following bounds are rational and checkable.

### Pi

The Machin identity is `pi=16*atan(1/5)-4*atan(1/239)`.
The exact Gaussian-integer product `(5+i)^4*(239-i)=114244*(1+i)` verifies the
tangent identity exactly. The selected angle
`4*atan(1/5)-atan(1/239)` lies strictly between 0 and 4/5 using
`x-x^3/3 < atan(x) < x` for the two positive arguments. Since pi>2, this angle
lies in (0,pi/2); its tangent is 1, so it is pi/4. This supplies the branch, not
just an unexplained integer identity.

For 0<x<1 the n-term alternating arctangent sum and that sum plus the next signed
term bound atan(x). The finite geometric identity for 1/(1+t^2), integrated from
0 to x, proves the remainder sign and bound x^(2n+1)/(2n+1). The rational pi
interval is 16 times the first interval minus 4 times the second, with directed
endpoint arithmetic. No decimal value of pi is treated as exact.

### Amplitudes, phase and trigonometric functions

Evaluate each reduced Q(alpha) amplitude and the affine phase on the exact root
interval using rational interval Horner arithmetic. For each harmonic subtract
an exact integer from the turn interval; periodicity makes this an identity,
not a phase approximation. Multiply that interval by the directed interval for
2*pi to get [a,b]. Set rational center c=(a+b)/2 and radius rho=(b-a)/2.

Use the n-term sine or cosine Taylor polynomial at c. Its actual degree is
2(n-1)+1 for sine or 2(n-1) for cosine. Since every real derivative of sine/cosine
has absolute value at most 1, the Lagrange remainder is bounded by
`|c|^(degree+1)/(degree+1)!`. On the full interval, Lipschitz constant 1 adds rho
to this error. Intersect with [-1,1]. Multiply by the directed amplitude interval,
retain every nonzero channel, and sum all contribution intervals. A sign is
certified only when the complete interval strictly excludes zero.

### Finite termination and independent checking

The equality branch was decided finitely before refinement. As n increases,
root and pi enclosures converge, interval evaluations of fixed polynomials
converge, reduced angle centers are eventually bounded, and the factorial
Taylor remainder plus radius tends to zero. The complete enclosure therefore
converges to the already-proved nonzero endpoint. Some finite stage strictly
excludes zero. Doubling n visits unbounded precision without an arbitrary cap.
An interrupted computation is resource refusal, never evidence of a sign.

`pb00701_algebraic_endpoint_certificate.py` rebuilds source-owned v45
representations, field/phase bindings, Laurent coefficients and all jets. It
checks a finite supplied sign witness without rerunning the sign search. It
recomputes every interval and separately audits Machin/Taylor sums and remainders
by direct rational summation rather than the generator's recurrence. Forged
bounds, omitted contributions, false zeros, changed real embeddings and
changed sources fail closed. A Python verifier is not a proof-assistant
formalization; its arithmetic is adversarially tested in repository CI.

## Interfaces and remaining work

`build_source_endpoint_evidence` consumes exact already-lowered source maps and
regenerates all cut/child material. `decide_required_event_endpoints` runs the
complete predecessor on the admitted source grammar first and attaches only
unresolved endpoint evidence. `classify_required_analytic_event` still delegates
the entire physical event to v45. Neither endpoint adapter consumes an analytic
cut or dispatches an algebraic child to a rational-only classifier.

Next dependency: qualify a whole-closed-child root/derivative route over the
represented algebraic interval, then exact event composition. Endpoint success
alone neither counts roots in a child nor proves its monotonicity. Multiple
independent algebraic boundaries may additionally need exact compositum or
source-coordinate interval handling. Preserve the earlier negative evidence.

## Evidence and sources

Primary theorem checked: Ivan Niven, *Irrational Numbers*, Chapter X, Theorem 10.1,
MAA (1956), pp. 134–150, DOI 10.5948/9781614440116.011. The publisher's displayed
statement explicitly permits any value and explains the logarithm branch:
https://www.cambridge.org/core/books/abs/irrational-numbers/gelfondschneider-theorem/BEB195D155B5E21FC90467893CFBEE6E

Independent educational derivation of the Machin identity and series:
https://www.math.brown.edu/~res/M10/machin.pdf

V46's full rational branch/remainder derivation is given above, rather than
relying on an approximate library or a table of constants. Local arithmetic
smoke tests use an independent, noncommitted SymPy helper because this session
cannot clone the repository. Full source integration, predecessor pins and
acceptance are established by the focused GitHub CI, not that local helper.

The frozen machining denominator remains 26 operations. Protected
source/audio/provenance, canonical journal, exact time/path/phase, source
uncertainty, positive-volume material, cutter/holder access, durable body/lineage,
refusal/UNCERTIFIED and conventional STEP semantics are unchanged. No native,
paid, production or expensive campaign is authorized.
