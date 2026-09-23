# PB-007-01 v40 — exact signed-B anti-diagonal direct rotated-coordinate certificate

Status: **bounded executable authority added; PB-007-01 remains OPEN; MC-B / MC-1 remain NOT_ESTABLISHED**.

## Baseline and scope

V40 starts from verified v39 main `a92115689da4713d30ba74d65c033897e877a4f7`. Complete v39 authority always runs first. V40 consumes only residual exact lowered spans and does not alter any historical route, endpoint/root/multiplicity semantics, the frozen 26-operation machining denominator, or protected source/audio/provenance and downstream contracts.

The new bounded family addresses the complementary anti-diagonal phase cells in which `X=cos(theta)+sin(theta)` is the fixed-sign dominant rotated coordinate. It removes the need for `A=(C+S)/2` itself to have one strict sign when `B=(C-S)/2` has a source-owned strict sign.

## Exact construction

From source-owned exact rational quadratures regenerate

`A=(C+S)/2`, `B=(C-S)/2`, `A'=(C'+S')/2`, `B'=(C'-S')/2`.

MC-032 exact endpoint/Sturm authority proves either `B>0` or `-B>0` on the complete closed local span and derives `sigma_B`. Define

`Bbar=sigma_B B > 0`, `Atilde=-sigma_B A`, `Bbar'=sigma_B B'`, `Atilde'=-sigma_B A'`.

The anti-diagonal phase cell is exact rational-turn containment

`1/16+k/2 <= h*phi <= 3/16+k/2`.

It is not backed by new numerical trigonometry. Subtracting exactly one quarter-turn maps it to the already-qualified v34-v39 diagonal cell. For `theta'=theta-pi/2`, `X'(theta')=-Y(theta)` and `Y'(theta')=X(theta)`. Therefore the historical exact rational bounds transfer directly:

- fixed-sign `X`, with `|X| > 2856/2197`;
- `|Y| < 99/182`;
- `|X| < 99/70`;
- `2*pi > 6`.

For both `sigma_A` signs V40 proves

`P_sigma=Bbar*(2856/2197)-sigma_A*Atilde*(99/182)>0`.

Every finite sign orthant over `Atilde'`, `Bbar'` and every non-anchor residual then proves

`6*|h*r|*P_sigma - sigma_Ap*(99/70)*Atilde' - sigma_Bp*(99/182)*Bbar' - sum sigma_i R_i > 0`

through the existing MC-032 closed-interval exact positivity authority. Equality and resource refusal fail closed.

## #243 algebraic contract reconciliation

The #243 prose contains one sign typo in the displayed oriented derivative identity. With its own definitions, exact multiplication by `-sigma_B` gives

`(-sigma_B)D=Atilde'X-Bbar'Y+2*pi*h*r*(Bbar X+Atilde Y)`,

not `Atilde'X+Bbar'Y+...`. The implementation, artifact, verifier and documentation use the exact minus sign. This does **not** relax or modify the complete-margin theorem because the `Bbar'` term is bounded through both finite sign orthants; its coefficient remains `99/182`. The issue thread records this reconciliation explicitly.

The physical derivative is unchanged, and certified sign recovery is

`sign(D)=-sigma_B*sign(h*r)*anti_diagonal_projection_sign`.

## Acceptance source and adversarial boundary

The primary exact source is

- `C_1=19/20+s/10`;
- `S_1=-21/20+s/10`;
- hence `A=-1/20+s/10` crosses zero and `B=1` is strictly positive;
- exact phase interval `[1/16,3/16]` turns;
- a nonzero tiny harmonic-2 COS channel remains live in the residual.

Complete v39 blocks this source at its strict-sign-of-A boundary. V40 derives `sigma_B=+1`, `Bbar=1`, `Atilde=1/20-s/10` and certifies the complete derivative. The adversarial suite exercises both B orientations, positive and negative phase rates, opposite anti-diagonal cells, exact B-sign/cell/phase-gap/complete-margin equality boundaries with rational neighbours, resource refusal, source mismatch, binary-float rejection, forged authority, historical v30/v34/v35/v36/v37/v38/v39 precedence and exact endpoint/root/multiplicity preservation.

## Programme effect

This is a sufficient bounded extension only. PB-007-01 remains OPEN, PB-007-02 remains dependent, PB-007-03 remains OPEN, PB-007-04 remains `OPEN_PROPAGATED`, PO-04/05/08 remain OPEN, and MC-B / MC-1 remain `NOT_ESTABLISHED`. Do not retry MC-B from this result. No native, paid, production or expensive campaign is authorized.

Protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume material, cutter/holder, durable-body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics remain unchanged.
