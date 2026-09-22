# PB-007-01 v13 — exact nonvanishing even-multiplier multi-harmonic route

## Contract

This document records a bounded constructive extension of `PB-007-01` after v12. It applies only to exact rational-polynomial lowered spans whose nonzero harmonics are exactly `{h,3h}`, `h>0`, and whose source coefficient maps prove

`F=(lambda+cos(2*alpha))*(A*cos(alpha)+B*sin(alpha))`,

with `alpha=2*pi*h*theta_turn` and exact rational `|lambda|>1`.

It does not narrow the supported machining domain and `PB-007-01` remains **OPEN**. MC-B remains `NOT_ESTABLISHED`.

## Source-derived identity

The implementation reconstructs `A=2*C_3h` and `B=2*S_3h` from the lowered source coefficients. It accepts the route only when the same exact rational `lambda` satisfies

`C_h=(lambda+1/2)A`, `S_h=(lambda-1/2)B`, `C_3h=A/2`, and `S_3h=B/2`.

No caller-supplied factorization certificate is authority. Missing, extra, wrong or perturbed harmonic channels fail closed.

## Nonvanishing multiplier

The only multiplier admission rule is exact `|lambda|>1`. Since `-1<=cos(2*alpha)<=1`, this establishes the strict global bound

`|lambda+cos(2*alpha)| >= |lambda|-1 > 0`.

`|lambda|=1` and `|lambda|<1` are not promoted. Binary floating point, epsilon, numerical trigonometry, sampling, approximate minimization, timeout and resource exhaustion are not truth authority.

A smooth globally nonzero multiplier preserves the carrier zero set and every finite root multiplicity exactly.

## Carrier authority

The single-harmonic carrier is delegated to existing exact authority only: v10 dual-projective, v11 phase-dominance, then v12 exact finite component-root partition where applicable. v13 does not reproduce or weaken those proof obligations. A carrier with a nonconstant common polynomial factor remains owned by v8; a carrier outside established v10/v11/v12 authority remains blocked under `PB-007-01`.

## Adversarial boundary

The required deterministic controls distinguish exact `lambda=1` from exact `lambda=1+1/1000000` and `lambda=1-1/1000000`; admit a correctly reconstructed negative `lambda<-1`; reject perturbed factor identities, extra/missing/wrong harmonics, source-parameter mismatch and binary-float authority; preserve resource refusal as non-truth; and reject mutation of historical v12 evidence, shrinkage of the frozen 26-operation denominator or false MC-B promotion.

## Protected semantics

Source/audio/provenance, canonical journal, exact shared time/path/phase, source uncertainty, positive-volume material, cutter/holder access, durable body/lineage, refusal/`UNCERTIFIED`, conventional STEP output, and the frozen 26-operation denominator are unchanged. No native, paid, production or expensive campaign is authorized.
