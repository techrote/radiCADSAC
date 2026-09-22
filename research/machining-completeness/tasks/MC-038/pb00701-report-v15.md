# PB-007-01 v15 — exact finite strict-dominance even-cosine multiplier family

Issue: #192  
Parent integration gate: MC-038 / #100  
Source baseline: `c61fc3338992f40e3382eb75d69d2a3bfbe5003e`  
Disposition: **bounded exact finite multi-harmonic family established; PB-007-01 remains OPEN**  
Native/paid execution: **none**

## Decision

**RAG: AMBER.** v14 established the normalized degree-2 multiplier producing `{h,3h,5h}`. v15 replaces that fixed-degree detector with an exact finite family

`M(alpha)=lambda_0 + sum_{k=1}^m lambda_k*cos(2*k*alpha)`, `m>=3`,

multiplying the already-qualified single-harmonic carrier. The multiplier and carrier are reconstructed from unfactored source harmonic coefficient maps, every redundant coefficient inference is checked exactly, and global nonvanishing is accepted only from exact rational strict dominance. No new transcendental zero oracle is introduced.

This does not close `PB-007-01`. General multi-harmonic coupled predicates outside this factor family remain open, as do carrier cases outside established single-harmonic authority. `PB-007-02` remains dependent, `PB-007-03` remains OPEN, `PB-007-04` remains `OPEN_PROPAGATED`, PO-04/05/08 remain OPEN, and `MC-B` / `MC-1` remain `NOT_ESTABLISHED`.

## Exact finite source inversion

Let

`F=M(alpha)*(A(s)*cos(alpha)+B(s)*sin(alpha))`,

where `alpha=2*pi*h*theta_turn(s)`, `h>0`, and

`M(alpha)=lambda_0 + sum_{k=1}^m lambda_k*cos(2*k*alpha)`.

The product contains only odd harmonics `(2r+1)h`. The source coefficient ratios satisfy

- `c_0=C_h/A=lambda_0+lambda_1/2`,
- `s_0=S_h/B=lambda_0-lambda_1/2`,
- for `1<=r<m`, `c_r=(lambda_r+lambda_{r+1})/2` and `s_r=(lambda_r-lambda_{r+1})/2`,
- at the highest harmonic, after normalization, `c_m=s_m=1/2`.

The highest nonzero multiplier coefficient is normalized to `lambda_m=1` by absorbing its exact nonzero scalar into the carrier. This removes only product scale ambiguity. v15 does not trust a caller-supplied normalization: it reconstructs `A=2*C_top` and `B=2*S_top` from the actual highest source channels.

The coefficient vector is then inverted exactly:

- `lambda_0=(c_0+s_0)/2`,
- `lambda_1=c_0-s_0`,
- for every `1<=r<m`, `lambda_r=c_r+s_r` and `lambda_{r+1}=c_r-s_r`.

Every coefficient except the endpoints is inferred redundantly from adjacent harmonic channels. All overlapping values must agree exactly. The implementation then regenerates every expected cosine and sine source polynomial and compares it exactly with the source. A missing intermediate harmonic may represent an exact zero map, but no tolerance fills a near-zero channel. Wrong/even/non-lattice nonzero harmonics, inconsistent adjacent inference, missing top carrier authority, and perturbed source equations fail closed.

## Exact multiplier nonvanishing

For every real `alpha`, each cosine term has absolute value at most one, hence

`|sum_{k=1}^m lambda_k*cos(2*k*alpha)| <= sum_{k=1}^m |lambda_k|`.

The only admitted nonvanishing certificate is therefore the exact rational condition

`|lambda_0| > sum_{k>=1}|lambda_k|`.

The canonical contract token is `|lambda_0|>sum_{k>=1}|lambda_k|`. The verifier records the exact positive margin

`|lambda_0|-sum_{k>=1}|lambda_k|`.

Equality and the entire sub-threshold region fail closed. No binary floating point, epsilon, numerical trigonometry, sampling, approximate minimization, timeout, or resource exhaustion is correctness authority.

Because the multiplier is smooth and globally nonzero, multiplication by it preserves exactly the carrier zero set and every finite root multiplicity.

## Carrier dispatch and historical ownership

v15 first calls the v14 classifier. Any event already certified by v14 or an earlier route remains owned there. Only the surviving residual finite multi-harmonic span is considered for v15.

The carrier `A*cos(alpha)+B*sin(alpha)` is delegated without reimplementation to the established v10/v11/v12 authority. A nonconstant common polynomial factor remains owned by v8. Thus v15 broadens source factorization coverage without changing historical single-harmonic proofs or route precedence.

The principal acceptance fixture uses `m=3`, producing a genuine `{h,3h,5h,7h}` source that v14 cannot recognize. Its coprime carrier has roots in both components, so the delegated carrier route exercises v12 component-root partitioning. A second finite-degree control exercises `m=4`, including an exactly absent intermediate harmonic channel reconstructed as zero.

## Boundary and adversarial controls

The deterministic verifier covers exact dominance equality, exact `+1/1000000` and `-1/1000000` neighbours, positive and negative `lambda_0`, mixed-sign higher coefficients, a broader `m=4` case, an exact missing-zero intermediate harmonic, inconsistent adjacent coefficient inference, a one-source-equation perturbation, missing/zero top authority, wrong/even/non-lattice harmonics, v14 route preservation, v8 common-factor ownership, unsupported carrier residual, source-parameter projection mismatch, binary-float authority, forged coefficient/factor metadata, resource-refusal laundering, historical-v14 mutation, frozen-denominator shrinkage, and false MC-B promotion.

The positive v15 fixture is first passed through v14 and is required to remain blocked. v15 must then derive its full finite coefficient vector from the source and return an established carrier certificate. This prevents the new route from merely relabelling historical authority.

## Programme effect

`PB-007-01` remains **OPEN**. The finite strict-dominance multiplier family is materially broader than v14 but does not decide arbitrary multi-harmonic exponential-polynomial predicates and is not an impossibility theorem for the residual.

`PB-007-02` remains **OPEN and dependent on PB-007-01**. `PB-007-03` remains OPEN. `PB-007-04` remains OPEN_PROPAGATED. PO-04, PO-05 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`.

The next pre-gate priority remains a substantive PB-007-01 repair on the residual multi-harmonic grammar unless a different PB-007 branch becomes independently higher priority. Another integration-gate retry is not justified by this bounded construction.

## Protected semantics

The denominator remains exactly 26 admitted operations. Historical source/audio/provenance and Genesis evidence are unchanged. Canonical-journal meaning, exact shared time/path/phase correlation, source uncertainty, positive-volume material, cutter/holder access semantics, durable body/lineage identity, typed refusal/`UNCERTIFIED`, and conventional STEP output meaning remain unchanged.

No native, paid, production or expensive campaign is authorized or run.

## Verification

```text
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v15.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v15.py --self-test
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

All historical PB-007-01 gates remain in `mc1-static`. The workflow must pass on the exact PR head before merge and independently on the exact merged `main` SHA afterward.
