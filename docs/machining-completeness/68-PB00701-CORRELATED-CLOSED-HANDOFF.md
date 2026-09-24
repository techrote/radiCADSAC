# PB-007-01 v43 — correlated closed-handoff authority

**RAG: GREEN for the bounded exact correlated handoff theorem; RED for full PB-007-01 / MC-B / MC-1.**

## Authority boundary

Verified v42 / #247 / PR #248 remains complete predecessor authority. V43 runs only on residual exact lowered spans blocked by v42. It does not weaken v42, v39/v40, historical endpoint semantics, or #245 acceptance.

The motivating blocker is exact: the current v42 and v39 strict closed-span certificates cannot overlap at one handoff endpoint. Their necessary bounds imply an inequality contradicted by

`(44/7)*(99/70)^2 - 6*(2856/2197)^2 = 100719037899/41389887175 > 0`.

V43 therefore supplies one correlated derivative certificate rather than asking two incompatible sufficient certificates to overlap.

## Exact construction

For source-owned `A=(C+S)/2`, `B=(C-S)/2`, `X=cos(theta)+sin(theta)`, `Y=cos(theta)-sin(theta)`,

`D=A'X+B'Y+2*pi*h*r*(A Y-B X)+retained residuals`.

On a verified diagonal cell `Y=d|Y|`. V43 proves an exact weak closed sign for `A`: an endpoint zero is admissible, while an interior root is a blocker owned by #245 partitioning. Choose `eta` so `eta*h*r*A>=0`. The oriented derivative is

`eta*d*D=eta*B'|Y|+2*pi*eta*h*r*A|Y|+eta*d*X*A'-2*pi*eta*d*X*h*r*B+residuals`.

Use the inherited exact bounds

- `L=2856/2197 < |Y|`;
- `|X| < U=99/182`;
- `|Y| < W=99/70`;
- `6 < 2*pi < 44/7`.

The favorable `A Y` channel receives the lower bound `6 L eta*h*r*A`. The oriented `B'Y` term uses `L eta B'` when weakly favorable or `W eta B'` when weakly adverse. The transverse `A'X` and `B X` channels and every non-anchor residual are retained adversely. A finite exact orthant family is discharged by MC-032 closed-interval endpoint/Sturm strict positivity.

No caller orientation, derivative, margin, root or multiplicity metadata is proof authority.

## Handoff semantics

The acceptance parent is blocked by complete v42 and remains blocked by v43 before partition because `A` crosses zero in its open span. Exact partition at the source-owned `A=0` root produces:

1. a predecessor-certified left closed child;
2. a v43-certified right closed child whose local `A` is weakly positive and zero only at its left endpoint.

Historical v27 exact child event composition then certifies the parent. The handoff cut is proof geometry only: it is counted as a physical root only if both exact child endpoint relations independently establish the same equality and compatible multiplicity.

## Fail-closed boundary

Interior weak-sign roots, unsupported phase cells, failed correlated margin, malformed source structure, exact resource refusal, binary-float authority, source-coordinate mismatch, forged proof metadata, or unresolved child composition remain non-certification. Strict margin equality is non-certification.

Sampling, numerical trigonometry, tolerance, epsilon overlap, open/half-open reinterpretation, approximate root ordering, adaptive refinement, arbitrary subdivision depth, timeout and denominator caps are not correctness authority.

## Programme state

PB-007-01 remains OPEN. PB-007-02 remains dependent; PB-007-03 remains OPEN; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/05/08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`. The machining-domain denominator remains 26 operations.

After verified v43 landing, #245 may resume against current authority and must still prove genuinely new exact partition/composition acceptance. Do not retry MC-B solely because v43 lands.
