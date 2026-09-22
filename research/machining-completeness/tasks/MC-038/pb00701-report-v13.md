# PB-007-01 v13 — exact nonvanishing even-multiplier multi-harmonic reduction

Issue: #188  
Parent integration gate: MC-038 / #100  
Source baseline: `423d742d3f615f448d58d30332dacc60c51313ba`  
Disposition: **bounded exact multi-harmonic subgrammar established; PB-007-01 remains OPEN**  
Native/paid execution: **none**

## Decision

**RAG: AMBER.** v12 removed the remaining global-zero-free-component restriction for the qualified coprime single-harmonic family. The next residual is genuinely multi-harmonic coupled exact-event authority. v13 establishes one substantive multi-harmonic construction without inventing a new transcendental zero oracle: an exact source-derived `{h,3h}` family whose event expression factors into a globally nonvanishing even-harmonic multiplier times a carrier already covered by v10/v11/v12.

This does not close `PB-007-01`. Multi-harmonic predicates outside this exact factor family remain open, as do any carrier cases outside established single-harmonic authority. `PB-007-02` remains dependent, `PB-007-03` remains OPEN, `PB-007-04` remains `OPEN_PROPAGATED`, PO-04/05/08 remain OPEN, and `MC-B` / `MC-1` remain `NOT_ESTABLISHED`.

## Exact factorization

On one exact rational-polynomial lowered span let

`alpha = 2*pi*h*theta_turn(s)`, with integer `h>0`, and define

`F = (lambda + cos(2*alpha)) * (A(s) cos(alpha) + B(s) sin(alpha))`.

The product-to-sum identities give exactly

- `C_h = (lambda + 1/2) A`,
- `S_h = (lambda - 1/2) B`,
- `C_3h = A/2`,
- `S_3h = B/2`.

v13 does not accept a caller assertion that this factorization exists. From the original lowered source coefficients it reconstructs `A=2*C_3h` and `B=2*S_3h`, obtains candidate rational `lambda` independently from the cosine and sine channels, requires the two candidates to agree, and verifies all four polynomial identities exactly. Any extra nonzero harmonic, missing channel, wrong `3h` relation, or coefficient perturbation prevents the route from being selected.

## Exact nonvanishing proof

For exact rational `|lambda|>1`, the real bound `-1 <= cos(2*alpha) <= 1` gives

`|lambda + cos(2*alpha)| >= |lambda|-1 > 0`.

Therefore the multiplier is globally nonzero on the entire source span. No numerical value of `pi`, trigonometric sampling, epsilon, approximate minimization, timeout, or resource budget participates in this proof. The exact threshold `|lambda|=1` and the entire `|lambda|<1` region remain fail-closed because the multiplier may vanish.

Since multiplication by a smooth nonzero factor does not alter zeros or their finite multiplicities, the original multi-harmonic event has exactly the carrier zero set and multiplicities.

## Carrier dispatch

The carrier `A cos(alpha)+B sin(alpha)` is not re-solved by v13. It is delegated only to established authority:

1. v10 exact dual-projective single-harmonic route;
2. v11 exact phase-dominance route for the qualified v10 monotonicity residual;
3. v12 exact finite component-root partition when neither projective component is globally zero-free.

The acceptance fixture uses coprime `A=s-1/3`, `B=2/3-s`, `lambda=2`, `h=1`. Both carrier components have source roots, so the carrier requires v12; the expanded event is genuinely multi-harmonic and is not the v8 common-polynomial-factor family.

A carrier with a nonconstant common polynomial factor remains owned by v8 rather than being relabelled. A carrier still outside v10/v11/v12 remains a typed `PB-007-01` blocker.

## Boundary and adversarial controls

The deterministic verifier covers the exact `lambda=1` boundary, exact `1+1/1000000` and `1-1/1000000` neighbours, a negative `lambda<-1` multiplier, source-coefficient perturbation, extra/missing/wrong harmonics, prior v8 ownership, unsupported carrier residual, source-parameter mismatch, binary-float authority, resource-refusal laundering, historical-v12 mutation, frozen-denominator shrinkage and false MC-B promotion.

The test deliberately first confirms that v12 leaves the genuine `{h,3h}` fixture blocked and then confirms that v13 certifies it with an exact factorization and a v12 carrier certificate.

## Programme effect

`PB-007-01` remains **OPEN**. The newly covered family is useful but bounded; the residual still contains general multi-harmonic rational-polynomial modulation and any exact single-harmonic local cells not admitted by v10/v11/v12. This is a constructive advance, not an impossibility theorem and not permission to retry MC-B.

`PB-007-02` remains **OPEN and dependent on PB-007-01**. `PB-007-03` remains OPEN. `PB-007-04` remains OPEN_PROPAGATED. PO-04, PO-05 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`.

The next pre-gate priority is a broader exact PB-007-01 multi-harmonic factor/decision construction, not another integration-gate pass.

## Protected semantics

The denominator remains exactly 26 admitted operations. Historical source/audio/provenance and Genesis evidence are unchanged. Canonical-journal meaning, exact shared time/path/phase correlation, source uncertainty, positive-volume material, cutter/holder access semantics, durable body/lineage identity, typed refusal/`UNCERTIFIED`, and conventional STEP output meaning remain unchanged.

No native, paid, production or expensive campaign is authorized or run.

## Verification

```text
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v13.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v13.py --self-test
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

All historical PB-007-01 gates remain in `mc1-static`. The workflow must pass on the exact PR head before merge and independently on the exact merged `main` SHA afterward.
