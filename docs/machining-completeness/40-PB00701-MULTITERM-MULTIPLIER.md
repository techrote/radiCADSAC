# PB-007-01 v14 — exact strict-dominance multi-term multiplier route

## Contract

This document records a bounded constructive extension of `PB-007-01` after v13. It applies only to exact rational-polynomial lowered spans whose nonzero harmonics are exactly `{h,3h,5h}`, `h>0`, and whose source coefficient maps prove the normalized factorization

`F=(lambda+mu*cos(2*alpha)+cos(4*alpha))*(A*cos(alpha)+B*sin(alpha))`,

with `alpha=2*pi*h*theta_turn` and exact rational `lambda,mu`.

The route derives rather than trusts the factorization. It reconstructs `A=2*C_5h` and `B=2*S_5h`, infers `mu` independently from the `3h` cosine and sine channels, infers `lambda` independently from the `h` cosine and sine channels, and requires exact agreement together with all six identities

- `C_h=(lambda+mu/2)A`,
- `S_h=(lambda-mu/2)B`,
- `C_3h=((mu+1)/2)A`,
- `S_3h=((mu-1)/2)B`,
- `C_5h=A/2`,
- `S_5h=B/2`.

All coefficient comparisons use exact rational polynomial arithmetic. Caller-supplied factor metadata, binary floats, epsilon comparisons, sampling and numerical trigonometry are not authority.

## Nonvanishing theorem

The multiplier is accepted only under the exact strict-dominance condition

`|lambda|>|mu|+1`.

Since `|cos(2*alpha)|<=1` and `|cos(4*alpha)|<=1`,

`|mu*cos(2*alpha)+cos(4*alpha)|<=|mu|+1`.

Thus

`|lambda+mu*cos(2*alpha)+cos(4*alpha)|>=|lambda|-|mu|-1>0`.

The implementation records the exact rational margin. Equality and the sub-threshold region remain fail-closed; no numerical minimizer or approximate trigonometric bound may substitute for the stated certificate.

A smooth globally nonzero multiplier preserves the carrier zero set and every finite root multiplicity. The carrier is therefore delegated only to existing v10/v11/v12 exact authority. A nonconstant carrier gcd remains owned by v8. Any carrier outside those routes remains `PB-007-01` rather than being sampled or approximated into a decision.

## Boundary requirements

The deterministic controls include exact strict-dominance equality and signed `1/1000000` neighbours, both signs of `lambda` and `mu`, inconsistent independent parameter reconstruction, one-equation perturbations, malformed harmonic sets, zero required channels, historical v13 ownership, v8 common-factor ownership, unsupported carrier cases, source-parameter mismatch, binary-float/epsilon and forged-metadata attacks, resource refusal, historical-evidence drift, denominator shrinkage and false MC-B promotion.

The positive fixture must be rejected by v13 and certified by v14, and its carrier must exercise v12 component-root partitioning. This prevents the extension from merely relabelling a historical single-harmonic or `{h,3h}` route.

## Programme state

`PB-007-01` remains **OPEN**. This exact `{h,3h,5h}` factor family does not establish a universal finite exact route for the remaining multi-harmonic coupled grammar. `PB-007-02` remains dependent, `PB-007-03` remains OPEN, `PB-007-04` remains `OPEN_PROPAGATED`, PO-04/05/08 remain OPEN, and `MC-B` / `MC-1` remain `NOT_ESTABLISHED`.

The frozen 26-operation denominator remains unchanged. Protected source/audio/provenance, canonical-journal, exact time/path/phase, source-uncertainty, positive-volume, cutter/holder, durable body/lineage, refusal/`UNCERTIFIED`, and conventional STEP semantics are unchanged. No native, paid, production or expensive campaign is authorized by this route.
