# PB-007-01 v10 — exact dual-projective ratio and endpoint-multiplicity route

## RAG status

**AMBER — the exact single-harmonic route now tolerates either projective modulation denominator and certifies admitted endpoint zeros as simple; PB-007-01 remains OPEN.** Corrective issue #182 is additive to immutable PB-007-01 v3/v6/v7/v8/v9 evidence. The frozen 26-operation denominator and protected source/audio/provenance semantics remain unchanged. MC-B and MC-1 remain `NOT_ESTABLISHED`.

## Constructive extension

After v7 lowers exact rational B-spline modulation to local rational power-basis polynomials, v8 consumes common-factor cases and v9 consumes the non-common single-harmonic family when `B(s)` is zero-free:

`F(s)=A(s) cos(h theta(s)) + B(s) sin(h theta(s))`.

v10 retains all v9 admission premises: exactly one positive harmonic, exact rational `A` and `B`, `gcd(A,B)=1`, a nonzero exact-rational affine phase law and the exact opposed-sign derivative condition. It removes only two previously named residual restrictions.

First, the projective denominator is no longer hard-wired to `B`. If `B` is zero-free, v9 tangent ownership remains authoritative. If `B` has source zeros but `A` is zero-free, v10 uses

`cot(pi*u(s)) = -B(s)/A(s)`, where `u(s)=2*h*theta_turn(s)`.

With

`D=A B' - A' B`, `r_t=-A/B`, and `r_c=-B/A`,

we have

`r_t'=D/B^2`, and `r_c'=-D/A^2`.

Thus the same exact v9 sign certificate for `D` makes the tangent event function strictly monotone with the phase direction and the cotangent event function strictly monotone against it. No floating approximation of `pi`, tolerance, sampling or timeout is needed.

## Cotangent chart authority

Cotangent poles occur at `u=n`. Because the admitted phase is rational affine, every induced source cut is exact rational. One-sided cotangent values at a pole are represented symbolically as infinities. The original event is not singular there: `sin(pi*u)=0`, `cos(pi*u)=+/-1`, and exact authority has already proved `A` nonzero on the whole closed span. Therefore every internal cotangent pole is exactly a non-event.

At finite rational source boundaries,

`cot(pi*u)=tan(pi*(1/2-u))`.

v10 therefore reuses the v6 exact rational-turn algebraic endpoint representation and exact polynomial equality/sign refinement. It does not introduce a numerical cotangent implementation.

## External endpoint multiplicity

v9 deliberately blocked an external endpoint equality. v10 closes that bounded gap for this exact single-harmonic family.

Let `phi=pi*u`. At a finite tangent-chart root, exact differentiation gives

`F'/cos(phi) = (-D + pi*u'*(A^2+B^2))/B`.

At a finite cotangent-chart root,

`F'/sin(phi) = (D - pi*u'*(A^2+B^2))/A`.

The selected chart denominator is nonzero, `u'` is a nonzero rational, and `A^2+B^2` is a positive rational at the rational endpoint. If the endpoint root were multiple, either formula would force

`pi = D / (u'*(A^2+B^2))`,

an exact rational number. That contradicts the irrationality of `pi`. Hence every admitted finite external endpoint zero is exactly simple. The certificate records the endpoint values, modulation norm, exact phase rate and resulting impossible rational value for `pi`; no numerical derivative test participates.

## Adversarial boundary

The deterministic controls include a genuine v9-denominator-zero case with zero-free `A` that succeeds through cotangent authority; the exact interior `B=0` point is checked as a non-event; ordinary zero-free-`B` cases remain owned by v9; left and right endpoint equalities are certified multiplicity one; exact `+/-1/1000000` endpoint neighbours remain distinct; cotangent pole crossings use exact rational cuts; and inputs with neither `A` nor `B` zero-free fail closed.

The suite also retains failures for derivative-sign-changing/nonmonotone cases, multiple harmonics, source-parameter mismatch, binary-float/epsilon/caller certificate authority, resource-refusal laundering, historical-evidence mutation, denominator shrinkage and false MC-B promotion. Common-factor inputs remain owned by v8.

## Remaining blocker

PB-007-01 remains **OPEN**. v10 does not establish a universal exact route for multi-harmonic predicates, derivative-sign-changing/nonmonotone single-harmonic predicates, single-harmonic spans where neither modulation component is zero-free, or the broader required analytic/source family. This is not an impossibility theorem.

PO-04, PO-05 and PO-08 remain OPEN; PB-007-02 remains dependent on PB-007-01; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; MC-B and MC-1 remain `NOT_ESTABLISHED`.

No native, paid, production or expensive campaign is authorized. Source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics are preserved.
