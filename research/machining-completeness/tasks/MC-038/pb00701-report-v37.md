# PB-007-01 v37 report — exact phase-correlated two-polynomial shared factor

## RAG status

**AMBER** — the bounded v37 corrective route is implemented and testable, but PB-007-01 remains open globally and MC-B / MC-1 remain `NOT_ESTABLISHED`.

## Established bounded route

V37 derives a canonical monic exact rational-polynomial GCD `G` from source-owned selected-harmonic quadratures, exact-divides `C_h=N*G` and `S_h=D*G`, regenerates both products coefficientwise, and requires `G` to have one strict sign. With `A=(N+D)/2`, `B=(N-D)/2`, `X=cos(theta)+sin(theta)`, and `Y=cos(theta)-sin(theta)`, it retains the complete derivative

`G'*(A*X+B*Y)+G*(A'*X+B'*Y)+2*pi*h*r*G*(A*Y-B*X)`.

The quotient-derivative contribution `N'*G*cos(theta)+D'*G*sin(theta)` is therefore never dropped. The exact diagonal cell uses the preserved bounds `L=2856/2197`, `U=99/182`, `W=99/70`, and `2*pi>6`. MC-032 endpoint/Sturm strict positivity proves `A>0`, both `sigma_B` phase gaps, and the complete finite orthant family over `A*G'`, `B*G'`, `A'*G`, `B'*G`, and every non-anchor derivative residual.

## Acceptance evidence

The primary source is `C_1=(9/10+s/100)(1+3s/4)^2`, `S_1=(1+s/200)(1+3s/4)^2`, with exact phase span `[-3/16,-1/16]` and a live tiny non-anchor `h=2` COS term. V36 blocks it because `C_1/S_1` is not an exact polynomial. V37 derives monic `G=16/9+8s/3+s^2`, exact quotients `N=81/160+9s/1600`, `D=9/16+9s/3200`, and retains both nonzero quotient derivatives through the full sign-family proof.

Adversarial coverage includes positive/negative phase rates, opposite diagonal-cell parity, exact cell/`A>0`/phase-gap/complete-margin equalities with signed rational `1/1000000` neighbours, zero/open/left-endpoint/right-endpoint outcomes, coprime quadratures, constant/zero/sign-changing GCD cases, malformed nonzero exact division remainder, forged GCD/quotient/factor/cell/bound/margin/root evidence, source-coordinate mismatch, binary floats, and exact resource refusal. Historical v30, v34, v35, and v36 successes retain precedence; v33 theorem-boundary evidence remains pinned.

## Preserved contracts

PB-007-01 remains open; PB-007-02 remains dependent; PB-007-03 remains open; PB-007-04 remains `OPEN_PROPAGATED`; PO-04/05/08 remain open. The domain denominator remains exactly **26 operations**. MC-B and MC-1 remain `NOT_ESTABLISHED`. Protected source/audio/provenance, canonical journal, exact time/path/phase, source uncertainty, positive-volume material, cutter/holder, durable-body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics are unchanged. Exact resource refusal is non-truth. No sampling, numerical trigonometry, binary-float authority, epsilon/tolerance, approximate root ordering, arbitrary subdivision cap, native campaign, paid campaign, production authorization, or expensive execution is introduced.

## Remaining red boundary

The next residual conservatism is the requirement for a nonconstant shared polynomial factor. The next bounded repair should test the direct rotated-coordinate identity for arbitrary exact source quadratures: `A=(C+S)/2`, `B=(C-S)/2`, derivative `A'*X+B'*Y+2*pi*h*r*(A*Y-B*X)`, with the same exact phase-gap and complete residual orthant discipline. If current exact authority cannot discharge that construction, record the precise theorem/algorithmic blocker rather than weakening correctness authority or retrying MC-B.
