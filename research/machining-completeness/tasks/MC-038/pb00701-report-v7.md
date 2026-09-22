# PB-007-01 follow-up v7 — exact B-spline lowering and coupled analytic theorem boundary

Issue: #172  
Parent integration gate: MC-038 / #100  
Source baseline: `08834827a5277d782a7ddcd7437a6e1527353620`  
Disposition: **exact rational B-spline lowering and bounded exact coupled subroutes established; PB-007-01 remains OPEN**  
Native/paid execution: **none**

## Purpose

PB-007-01 v6 removed the arbitrary-rational-turn endpoint restriction for constant-coefficient rational trigonometric polynomials. The surviving source grammar is broader. MC-003 admits finite non-rational B-splines with exact rational knots/control points, and MC-022 retains path/feed/spindle phase on one exact source parameter. Once those source channels modulate trigonometric phase, event predicates are no longer constant-coefficient Fourier polynomials.

This v7 follow-up does not rewrite v3 or v6. It implements the exact source-side lowering that was previously missing, dispatches every span that really reduces to already-proved exact machinery, adds a conservative exact zero-free certificate, and records the remaining theorem boundary without sampling, epsilon, timeout or an unproved conjecture.

## Exact B-spline lowering

`pb00701_coupled_bspline_model.py` accepts scalar B-splines with integer degree, finite exact rational nondecreasing knots and finite exact rational controls. Cardinality is checked exactly (`#knots = #controls + degree + 1`), knot multiplicity may not exceed `degree + 1`, and the source domain is the exact interval `[k_degree, k_ncontrols]`.

The implementation splits only at exact source knots. Each nonzero knot span is lowered by Cox-de Boor recursion to an exact rational polynomial in the local coordinate

` s = (u - u_lo) / (u_hi - u_lo) `.

Repeated knots remain explicit semantic boundaries. Zero-width knot intervals are skipped because they have no open span; they are never merged by epsilon. Each span records exact one-sided endpoint limits. A degree-1 clamped `[0,1]` spline with controls `[0,1]` lowers to `s`; the degree-2 controls `[0,1,0]` lower to `2s - 2s^2`. A degree-1 internal knot repeated to multiplicity two retains the exact discontinuity rather than fitting across it.

All cosine/sine modulation channels are lowered against the union of their exact knot boundaries and must cover the requested source interval. The affine phase law

`turn(u) = phase_turn_offset + phase_turn_rate * u`

uses the same durable `source_parameter_id`. An independent parameter projection is rejected.

## Exact terminating subroutes

Every finite lowered span is reviewed in order.

1. **Exact rational amplitude dominance.** If the harmonic-zero constant term strictly dominates the exact sum of absolute values of every remaining local polynomial coefficient, then `|s^i| <= 1` and `|sin|,|cos| <= 1` give a rational positive separation margin. This proves the span zero-free without sampling.

2. **Stationary cardinal phase.** If phase rate is exactly zero and the stationary phase is a quarter turn for every active harmonic, all trig values are rational `0/±1`. The event becomes a rational polynomial in `s` and is classified by the existing MC-032 exact event/Sturm machinery, including endpoint multiplicity and open-span multiple roots.

3. **Constant modulation.** If every lowered modulation polynomial is exactly constant and the phase rate is nonzero, the span is exactly the v6 constant-coefficient problem. It delegates to `RATIONAL_TRIG_POLYNOMIAL_RATIONAL_TURN_WINDOW`, retaining exact rational-turn endpoints, algebraic tangent endpoint isolation, exact endpoint equality/multiplicity and one-sided Sturm root counts.

No route is selected from a sampled numerical fit. Degree reduction occurs only after exact coefficient cancellation.

## Residual coupled branch

A genuine residual remains when at least one modulation polynomial is nonconstant and the trigonometric phase advances. Each such span has the exact form

`sum_k p_k(u) cos(2*pi*k*(a+b*u)) + q_k(u) sin(2*pi*k*(a+b*u))`

with rational power-basis `p_k,q_k` and exact rational `a,b`.

The repair now represents this branch exactly; it does **not** supply a general exact zero/multiplicity decision procedure for it. The implementation returns a typed `PB-007-01` blocker instead of iterating until a floating tolerance or resource limit happens to choose a sign.

The functions are structurally exponential-polynomial / restricted-Pfaffian-style on compact pole-free pieces. Effective restricted-Pfaffian algorithms are a plausible future constructive route, but the present repository does not yet contain or qualify the exact coefficient/sign/oracle machinery needed to instantiate those algorithms for this source profile. Continuous-Skolem literature is relevant background on exact exponential-polynomial zero questions, but this report does not claim a reduction, hardness theorem or impossibility result for this narrower commensurate trigonometric family.

Accordingly this is a sharpened constructive boundary, **not an impossibility theorem**.

## Boundary and adversarial controls

The deterministic verifier checks exact linear, quadratic and repeated-knot lowering; exact one-sided span limits; exact constant cancellation; v6 delegation for constant modulation; exact stationary-cardinal polynomial classification; strict rational amplitude dominance; and the typed residual blocker.

It also rejects source-parameter mismatch, independent phase projection, binary-float knots/controls/source bounds/phase, an injected epsilon authority field, malformed knot/control cardinality, excessive knot multiplicity, empty/inverted intervals, unsupported authority fields and resource-refusal laundering. Artifact attacks cannot shrink the frozen operation denominator, close PB-007-01/PO-04/05/08, accept MC-B, run native/paid work or weaken protected semantics.

## Programme effect

`PB-007-01` remains **OPEN**. The missing implementation detail has been narrowed: B-spline source semantics are now finitely and exactly lowered, but the general nonconstant-modulation/nonzero-phase zero decision route is not yet established.

`PB-007-02` remains **OPEN and dependent on PB-007-01** for general coupled membership boundary/equality events. `PB-007-03` remains OPEN. `PB-007-04` remains OPEN_PROPAGATED. PO-04, PO-05 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`.

This result does not justify another MC-B retry. Because the PB-007-01 residual is now a theorem/algorithm-qualification boundary rather than another obvious source-lowering omission, the next independently dependency-ready repair is a broader exact PB-007-03 source construction unless a reviewed effective restricted-Pfaffian route is first supplied.

## Protected semantics

The denominator remains exactly 26 admitted operations. Historical source/audio/provenance and Genesis evidence are unchanged. Canonical-journal meaning, exact shared time/path/phase correlation, source uncertainty, positive-volume material, holder/access semantics, durable body/lineage identity, typed refusal/`UNCERTIFIED`, and conventional STEP output meaning remain unchanged.

No native, paid, production or expensive campaign is authorized or run.

## Verification

```text
python3 research/machining-completeness/tasks/MC-038/verify_pb00701.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701.py --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v6.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v6.py --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v7.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v7.py --self-test
python3 research/machining-completeness/tasks/MC-038/verify.py --contract
python3 research/machining-completeness/tasks/MC-038/verify.py --self-test
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

`mc1-static` must pass on the exact PR head before merge and independently on the exact merged `main` SHA afterward.
