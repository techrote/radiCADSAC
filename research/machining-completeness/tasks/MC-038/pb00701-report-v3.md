# PB-007-01 follow-up — exact nontransversal transcendental-event decision boundary

Issue: #164  
Parent integration gate: MC-038 / #100  
Source baseline: `732b8e73e8e4669d51489df5f1975e21b5227a11`  
Disposition: **bounded exact extension established; PB-007-01 remains OPEN**  
Native/paid execution: **none**

## Purpose

This follow-up executes the first surviving pre-gate repair named by MC-038 after the MC-031/032/033 producing-owner retry. It does not redo broad defect discovery and it does not rewrite historical MC-007, MC-032 or MC-038 evidence. Its purpose is narrower: establish the strongest exact nontransversal analytic-event subroute justified by the frozen source language, then decide whether that route actually discharges `PB-007-01` for the full required domain.

The answer is mixed. A useful exact subroute is now constructive and executable for finite rational trigonometric polynomials on source-bound quarter-turn windows that remain on one tangent-half-angle branch. That subroute decides root counts and repeated-root structure using exact rational polynomial arithmetic. It is **not** sufficient to close `PB-007-01`, because the admitted MC-003/MC-007 grammar also contains arbitrary rational-turn endpoints and piecewise-polynomial path/feed terms coupled to trigonometric phase, yielding a broader analytic predicate family for which no unconditional finite exact decision construction has been established here.

## Preserved authority

The following historical artifacts are inputs, not mutable targets:

- `MC-007/transcendental-route-v1.json`: finite exact source decomposition plus a fail-closed boundary for unresolved tangential/multiple/singular transcendental events;
- `MC-032/event_engine.py` and `MC-032/outcome.json`: exact rational-polynomial sign/root/multiplicity machinery and the certified separated/transversal analytic adapter;
- `MC-038/constructive-coverage-review-v1.json`: historical blocked MC-B review;
- `MC-038/gate-scope-retry-v2.json`: current pre-gate blocker classification, with `PB-007-01` first in repair priority.

Their Git blob identities are pinned by `pb00701-decision-boundary-v3.json` and checked by the follow-up verifier. This addendum supplements them; it does not make their earlier negative/open state disappear retroactively.

## Exact bounded subroute

For a finite real trigonometric polynomial

`f(theta) = a_0 + sum_k (a_k cos(k theta) + b_k sin(k theta))`

with exact rational coefficients, use the exact substitution

`x = tan(theta / 2)`.

Then

`cos(theta) = (1 - x^2) / (1 + x^2)` and `sin(theta) = 2x / (1 + x^2)`.

Repeated-angle recurrences therefore reduce the complete finite trigonometric polynomial to

`f(theta) = P(x) / (1 + x^2)^n`

for an exact rational polynomial `P`. For finite real `x`, the denominator is strictly positive. Root presence, sign, multiplicity and sign change are consequently properties of `P` and can be delegated without approximation to the already reviewed MC-032 rational-polynomial/Sturm machinery.

The implementation is `pb00701_event_model.py`. It deliberately admits only source windows whose exact turn-fraction endpoints map to rational tangent-half coordinates by the current proof: quarter-turn endpoints on one pole-free monotonic branch. The implementation does not approximate unsupported endpoints. A non-cardinal rational turn, a window crossing a tangent-half pole, an unreviewed analytic grammar or a missing shared source parameter terminates with a typed blocker/semantic failure.

## Boundary controls

The deterministic verifier exercises nontransversal cases that the earlier certified-analytic adapter intentionally could not decide:

- `sin(theta)` at `x=0`: exact simple crossing, multiplicity 1;
- `1-cos(theta)` at `x=0`: exact tangency, multiplicity 2, no sign change;
- `sin(theta)^3`, represented exactly by `(3 sin(theta)-sin(3 theta))/4`: exact singular crossing, multiplicity 3, with sign change;
- exact `-1/1000000` and `+1/1000000` tangent-half neighbours remain opposite signs rather than being collapsed by tolerance;
- `cos(2 theta)` on the pole-free quarter-turn window contains two open roots, both found by exact Sturm counting rather than midpoint sampling;
- identity-zero input remains blocked for separate semantic handling rather than being assigned an invented event type.

Adversarial controls additionally reject binary-float coefficients/endpoints as correctness authority, independent source-parameter projection, non-cardinal endpoints, pole-crossing windows, polynomial-modulated/general coupled analytic predicates, denominator shrinkage, resource refusal as a truth value, protected-semantic weakening, false PB closure and MC-B promotion.

## Why PB-007-01 remains open

The bounded reduction above is exact, but it is not the full required analytic grammar. MC-003 admits exact rational B-splines and exact timed phase laws; MC-007/MC-022 retain common time/path/spindle-phase correlation for synchronized threading, eccentric turning and helical milling. On a source piece, geometric event equations may therefore contain polynomial or spline-derived terms multiplied or composed with trigonometric phase terms. Arbitrary exact rational turn endpoints are also valid source data and need not have rational tangent-half coordinates.

Nothing in the new reduction proves that every required event can be partitioned finitely into the implemented constant-coefficient/cardinal-window sublanguage. In particular, the follow-up does not establish an unconditional exact decision procedure for all tangential, multiple-root or singular events in the broader bounded trigonometric/analytic predicate family.

The prior MC-007 source inspection remains relevant background: certified numerical zero isolation terminates under separated/transversal hypotheses, while the exact tangential branch is materially harder. Later exponential-polynomial literature likewise contains major decidability results conditional on Schanuel-type assumptions. Neither observation is treated as an impossibility theorem for the exact radiCADSAC grammar. Conversely, the lack of an impossibility theorem is not authority to close the blocker.

Therefore:

- `PB-007-01` remains **OPEN**;
- PO-04 remains **OPEN**;
- PO-05 remains **OPEN**;
- PO-08 remains **OPEN**;
- MC-B remains **NOT_ESTABLISHED**;
- MC-1 remains **NOT_ESTABLISHED**.

The correct next dependency-ready pre-gate branch is `PB-007-02`, not another MC-B acceptance retry.

## Protected semantics and resource policy

The frozen 26-operation denominator is unchanged. The three operation classes historically affected by the MC-007 general analytic route remain admitted: synchronized lathe threading, eccentric turning and fixed-axis helical milling. No operation is removed merely because a general event can still block.

Source/audio/provenance, canonical-journal meaning, exact time/path/phase correlation, positive-volume material, durable body/lineage, conventional STEP semantics and historical negative evidence are unchanged. `BLOCKED`, `UNCERTIFIED`, `RESOURCE_REFUSAL`, timeout or refinement exhaustion do not become success. No native, paid, production or expensive campaign is authorized or run by this follow-up.

## Verification

The follow-up is checked independently of the historical MC-038 verifier:

```text
python3 research/machining-completeness/tasks/MC-038/verify_pb00701.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701.py --self-test
python3 research/machining-completeness/tasks/MC-038/verify.py --contract
python3 research/machining-completeness/tasks/MC-038/verify.py --self-test
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The repository `mc1-static` workflow is required on the exact PR head before merge and again on the exact merged `main` SHA afterward.
