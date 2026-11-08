# MC-038 / PB-007-01 — bounded second-order sided physical boundary events

**Research-only / DETERMINISTIC_MODEL / Draft / NO MAIN MERGE.**
This is an additive successor to Ready, unmerged #455 (itself stacked on Ready, unmerged #453), not a production algorithm, original-source proof discharge, or an authenticated spline-knot converter. #397 retains exclusive main integration.

## Question and strictly restricted admission

Can a complete rational certificate cover an **exact rational quarter-turn boundary zero** even when the physical first derivative vanishes exactly, so that #455's strict first-derivative sided guards correctly refuse? Yes, within the source grammar and finite arithmetic budgets below.

An input source is *only* the validated #453 grammar: at most four adjacent rational-polynomial pieces of degree at most three, with coefficientwise continuity of H0/C1/S1/C2/S2 and a globally rational affine phase in units of pi. An interface between such pieces is **declared**, not proved to be an original B-spline knot. The converter in #453 authenticates the separate frozen V44 original, but none of the new tangency fixtures is a newly solved frozen historical source.

For each physical source, use the full law:

\[
F(t)=H_0(t)+\sum_{h=1}^2\left(C_h(t)\cos(h\theta(t))
+S_h(t)\sin(h\theta(t))\right),\qquad
\theta(t)=\pi(a+bt).
\]

All polynomial, phase and interval endpoints are exact rationals. In particular, **nonzero H1 and H2 and nonzero moving phase** are admitted.

## Exact endpoint zero and first-derivative decision

At a boundary \(t_0\), #455 authenticates the complete physical value \(F(t_0)=0\) only if \(a+bt_0\) is a multiple of a half-integer (a quarter-turn in ordinary turns). Trigonometric endpoint values are then exact integers in \(\{-1,0,1\}\).

At that quarter-turn, direct differentiation gives

\[
F'(t_0)=A+\pi B,\quad
A=H'_0+C'_1c_1+S'_1s_1+C'_2c_2,\quad
B=b\big(S_1c_1-C_1s_1+2S_2c_2\big),
\]

where \(c_1,s_1\) are the exact H1 node values and \(c_2=(-1)^m\), with \(m=2(a+bt_0)\). The exact equality test requires **both rational coefficients** \(A=B=0\), not a floating-point near-zero. This is sufficient (and, by irrationality of pi, necessary). If they are not both zero, the existing #455 strict signed-first-derivative guard is used unchanged.

When \(A=B=0\), the verifier searches for an admissible one-sided guard \([l,t_0]\) or \([t_0,r]\) over which a fully rational enclosing interval for \(F''\) has one **strict** sign. It differentiates the *complete* harmonic law:

\[
F''=H_0''+\sum_{h=1}^2\left[
 C_h''\cos(h\theta)+S_h''\sin(h\theta)
 +2\omega_h(-C_h'\sin(h\theta)+S_h'\cos(h\theta))
 -\omega_h^2(C_h\cos(h\theta)+S_h\sin(h\theta))
\right],\qquad\omega_h=h\pi b.
\]

The inclusion enclosure uses #453's rational pi bounds, trigonometric Taylor/Lagrange and phase-drift enclosures, polynomial Horner interval bounds and inclusion-preserving interval products/sums. No sampled sign is used as a proof.

Because \(F(t_0)=F'(t_0)=0\), Taylor's theorem supplies \(F(t_0+h)=h^2 F''(\xi)/2\) on either sided guard. Strict \(F''>0\) thus proves an isolated positive-sided order-two zero; strict \(F''<0\) analogously proves a negative side. The separately checked far endpoint must have the inferred sign.

**Sided order** (1 or 2) is deliberately reported separately for the left and right pieces, and the boundary root is counted exactly once. Two equal signs are a local touch and different signs a crossing. No globally smooth multiplicity or source-knot provenance is inferred.

## Exhaustive remaining interior and proof-carrying receipt

Every guard removes an open punctured neighborhood of the proven boundary zero. The exact complement of each source piece is handed to the #453 source-bound, complete interval/root partition verifier. The child source gets a fresh canonical SHA-256 digest of its **restricted** domain, not its parent's identity (#456 repair).

A receipt includes full-source identity; complete child partition with source-bound digest; each one-sided guard, precision and method/order; physical boundary sign/order; and the total count = one per exact boundary zero plus each certified interior crossing. The checker authenticates source identity and continuity, verifies every child proof independently, rebuilds all sided guards and exact source partitions, and compares the canonical entire receipt. Malformed or forged receipts are NONTRUTH.

## Finite refusal and adversarial cases

Guard lengths are exactly source-span/8, /16, /32, /64, /128 or /256. The inherited rational pi/trigonometric precisions are bounded, as are polynomial degrees, piece count, certificate bits and partition depth. If no guard has strictly signed \(F''\), if one-sided \(F'\) is not exactly zero and #455 cannot prove its sign, if the zero lies at a non-quarter-turn, if a child partition is unresolved, or if resource budgets are exhausted: **raise NONTRUTH and do not return COMPLETE.**

The self-tests include: real moving H1+H2 positive-order-two declared knot touch, negative-order-two knot touch, mixed order two/one touch, order-two exterior endpoint, inherited order-one crossing, a cubic high-order contact that must refuse, exact \(A,B\) equality separation, nonquarterturn refusal, altered left order/kind/root count, false MC-1/PB authority, child-source digest substitution, malformed nested partition, and non-serializable receipt objects.

The high-harmonic simple interior zeros already certified by #453 remain supported through the inherited child partition, not claimed as new historic coverage.

## Acceptance and exclusions

Run the new exact-head workflow's focused tests, the original #455 and #453 focused suites, the real frozen V54/V2 producing reconciliation, and repository-wide MC-1 static validation. A distinct-session source-critical/mathematical review must inspect the exact final head before Ready; do not merge into main.

Frozen historical baseline remains **121 original cases / 20 route refusals / 30 missing ordered premises / 50 preexisting complete V2 witnesses**, all deltas zero, new original IDs [], required PB/PO discharges 0. MC-B and MC-1 remain **NOT_ESTABLISHED**. No native geometry, topology, STEP, output-certification, or production authorization.
