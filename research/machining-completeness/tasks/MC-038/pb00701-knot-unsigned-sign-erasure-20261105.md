# MC-038 / PB-007-01 — original-source knot signed-germ information-loss falsifier

**Date:** 5 November 2026. **Disposition:** source-bound result **C** against an expressly proposed *underspecified* interface, pending independent admission. **Evidence class:** `DETERMINISTIC_MODEL`, exact rational source/proof checks; not native geometry, independent STEP, or a programme-gate pass. Parent [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). [Coordination claim](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6648432842). Starting branch base: `9c4c0371f4ba70e0fff8c15bd08e6c252e53dc29`, after concurrent MC-045 #393 integration; #392 has its own separate active review/integration owner.

## Precise question and falsifier

Under PB-007-01 and the category-3 ordered physical sign-transfer frontier relevant to PO-05/08, consider the candidate `KNOT_SIGN_FROM_ROOT_SET_AND_UNSIGNED_SIDE_ORDERS_ONLY`. Its input is **only** the exact complete physical zero coordinates, source-coordinate interval, the exact location of each true B-spline source knot, global affine phase and unsigned first-nonzero one-sided vanishing orders at the shared knot. Crucially, it **does not** receive the original spline controls, the signed nonzero derivatives/one-sided germs or source sign-cell witnesses. It purports to reconstruct the physical sign cells and classify a shared knot as crossing or touching. This is a hypothetical interface, *not a statement about the existing signed-jet implementation*.

**Decisive falsifier:** two *actual frozen original* source cases have exactly the same restricted input, but their physical sign cells or knot classification differ. This is an information-loss impossibility specifically for the restricted interface; an interface carrying exact sided signed-jet or sample-cell sign evidence is unaffected. This is not an undecidability claim about general analytic root events.

## Exact source authority

Both are source-time `t ∈ [0,2]`, global rational phase turns `p(t)=t/4`, one true source knot `t=1`, cosine harmonic 1 degree-zero controls `[1,1]` and knots `[0,1,2]`, with no sine harmonics. They differ **only** in original harmonic-zero cosine coefficients:

| Historical frozen original ID | Original H0 cosine B-spline | SHA-256 canonical source | v54 reason |
|---|---|---|---|
| `composite:DELEGATED_V6_CONSTANT_MODULATION:tail0` | degree 0; knots `[0,1,2]`; controls `[0,0]` | `9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1` | `V27_CHILD_LEFT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE` |
| `composite:DELEGATED_V6_CONSTANT_MODULATION:tail100` | degree 1; knots `[0,0,1,1,2,2]`; controls `[0,0,0,100]` | `f6a0eb06c66af415fbb8abdfe62f9b36a2a2bf154e535d83307a80228e044ad5` | `V27_CHILD_NOT_CERTIFIED` |

Their independent original complete-row SHA-256 values are respectively `145ac5ce5b533c447c7356e8dc721dbfa5a44562cdc3a37422278fd7bd0199fc` and `0801317d3452c77733a129148d58eaac2f06aa9cd26396a44892e82c524e1db2`. Immutable frozen v54 corpus Git blob: `5841c331579489b25caef38cd412bdbf286f9134`; independently qualified v2 50-source original-source register Git blob: `e52d3baf3692a011cf86234eeaa992ef407d99fd`. The accompanying verifier reads both entire blobs, checks Git blob identities, the case/row/source identities, source spec, historical refusal, and each selected preexisting v2 complete witness. These originals are **not newly resolved** by this work.

## Exact mathematical proof

Direct fully clamped spline evaluation gives, with `x=t−1` on the right span:

```text
F_flat(t) = cos(pi*t/2)                    0 <= t <= 2
F_ramp(t) = cos(pi*t/2)                    0 <= t <= 1
          = 100*(t-1) + cos(pi*t/2)       1 <= t <= 2

F_flat(1+x) = -sin(pi*x/2)
F_ramp(1+x) = 100*x - sin(pi*x/2)
```

On `0 <= t < 1`, both are strictly positive because `0 <= pi*t/2 < pi/2`. Their sole common knot `t=1` has exact value zero. For flat tail and `0 < x <= 1`, `−sin(pi*x/2)<0`, and flat right exterior `F_flat(2)=−1`. For the ramp tail, the classical exact inequality `0 <= sin(y) <= y` for `0 <= y <= pi/2`, combined with `pi<4`, yields

`F_ramp(1+x) >= (100−pi/2)*x > 98*x > 0`.

At `t=2`, `F_ramp(2)=99`; the left exterior is `F(0)=1` for both. Thus the **complete exact physical zero set** for each source is the singleton `{1}`, with zero strict open-span roots and no exterior roots.

The one-sided knot derivatives are

```text
                     left derivative at 1    right derivative at 1
F_flat                    -pi/2                   -pi/2
F_ramp                    -pi/2                   100 - pi/2
```

All four values are nonzero (`3<pi<4` suffices), so each source has the identical **unsigned one-sided orders** `(1,1)`. The physical sign cells are **`(+,-)`** for the flat tail, a CROSSING, versus **`(+,+)`** for the ramp tail, a TOUCHING. A globally smooth multiplicity is **not assigned**: the original ramp source is only piecewise smooth at the true knot and its one-sided derivative values differ. This fact distinguishes a real source knot from an artificial chart cut.

Let `U(F)` be precisely the interface input tuple (source interval, phase, exact source-knot coordinate, complete root coordinates, unsigned sided orders). Both original sources have the same `U`; let `S(F)` be the physical sign cells and knot event classification. We proved `S(F_flat) != S(F_ramp)`. If a deterministic decoder `D(U)` were correct for both, it would have to return both unequal outputs for the same input—contradiction. Hence this specified proposed handoff is incomplete. Reintroducing signed sided germs, actual source coefficients, or independent physical signs removes the contradictory input equivalence.

## Termination, independent controls and bounded resources

The proof for this pair has finitely many explicit polynomial/B-spline pieces, a fixed exact knot and the standard exact sine sector inequality. It does not numerically search for roots or classify by a timeout, sample or resource cap. The code uses exact `fractions.Fraction` and checks a **Machin arctangent identity** to enclose pi by rational alternating series solely for additional sign-margin adversarial tests, not to make the mathematical proof terminate. The alternating Taylor bound is a rigorous interval for positive rationals less than one; the fixed 30 terms are test precision, not a claim of mathematical truth from exhaustion. Two very close rational slopes, bracketing `pi/2`, check distinct signed **right germ** directions, and do not claim a global root count for those synthetic ramps.

The verifier further rejects each original's case ID, provenance, source interval/parameter, phase, H0/H1 controls/knots, historic V27 status, source/row SHA and v2 metadata mutations; it refuses an identity-zero continuum as an isolated signed root and independently checks even-order tangency and odd-order polynomial parity. Synthetic controls are never added to frozen historical totals. False source-bound root or sign statements are decisive failures.

Reproduce from repository root:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701-knot-unsigned-sign-erasure-20261105.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_frontier.py --contract --self-test
python3 tools/validate_machining_completeness.py --self-test
```

## Before/after accepted evidence, not route status

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| Frozen original source IDs | 121 | 121 | 0 |
| Historical uncertified route cases | 20 | 20 | 0 |
| Historical missing ordered premises | 30 | 30 | 0 |
| Registered complete source-specific witnesses | 50 | 50 | 0 |

Newly closed original case IDs: `[]`. The two selected originals **already** have complete finite source-specific zero-set evidence in v2. Original historical V27 failures and all other raw failures remain preserved. The full 50-case set contains 49 finite zero sets and one continuum, and neither selected case is that continuum. This is a **new limited interface falsification C**, not a new complete-source witness, a universal PB-007 discharge, or a changed frozen census.

## Impact and explicit nonclaims

A generic knot/physical sign-transfer contract needs **signed one-sided germs or other source-bound sign premises**; root coordinates and unsigned endpoint orders alone cannot supply them. This is useful independent input to future PB-007-01 / PO-05/08 interface design. Existing exact signed-jet #298, source-knot #308 and preexisting tail100 and tail0 proofs already use stronger information and are **not invalidated** or accused of incorrect behavior. The result does not solve universal nonconstant-amplitude/multi-span root isolation, provide new native geometry, qualify an independent oracle or conventional usable engineering STEP, or authorize a production repository.

`PB-007-01/02/03/04`, `PO-02/04/05/07/08` remain OPEN; `MC-B` and `MC-1` remain `NOT_ESTABLISHED`. All 26 supported machining operations, source-time and phase semantics, durable journal/body lineage, positive-volume material/topology, safe refusals, actual native STEP and domain requirements stay protected. No shared programme/proof registers, frozen v54/v2 artifacts, 77 ledger, #392, #393 or paid/native campaigns were changed.

**Integration rule:** source-level direct review, literal-head focused + static + full post-v54 CI, distinct corrected-head independent review, guarded merge only when qualified, then exact landed-main recheck. This authored report and receipt on their own are not independent admission or approval.
