# PB-007-01 exact-event decision boundary

Status: **bounded exact extension established; full PB-007-01 remains OPEN**.  
Corrective issue: #164.  
Parent gate: MC-038 / #100.  
Source baseline: `732b8e73e8e4669d51489df5f1975e21b5227a11`.

## Decision

The programme now has an unconditional exact route for one useful nontransversal analytic sublanguage: finite rational trigonometric polynomials on a source-bound pole-free quarter-turn window. Under `x = tan(theta/2)`, the predicate becomes an exact rational polynomial numerator divided by `(1+x^2)^n`; the positive denominator leaves real sign/root/multiplicity questions to MC-032's exact rational polynomial and Sturm machinery.

This does **not** close `PB-007-01`. The frozen source grammar also admits arbitrary rational-turn endpoints and piecewise-polynomial/B-spline path and feed terms coupled to trigonometric phase. No reviewed construction currently proves that every required tangential, multiple-root or singular event in that broader bounded analytic grammar reduces to the new exact sublanguage or otherwise has an unconditional finite exact decision procedure.

## Authority boundary

The new executable model is `research/machining-completeness/tasks/MC-038/pb00701_event_model.py`; the versioned machine-readable review is `pb00701-decision-boundary-v3.json`; deterministic/adversarial verification is `verify_pb00701.py`. Historical MC-007, MC-032 and MC-038 v1/v2 evidence remains intact and pinned by Git blob identity.

The exact subroute accepts only rational coefficients and one shared source parameter. Binary floating point, a global epsilon, finite sampling density, subdivision limits, timeout and resource refusal cannot decide sign or exact zero. Independent phase/path projection remains forbidden.

## Exact controls

The verifier covers a simple zero (`sin(theta)`), an even-multiplicity tangency (`1-cos(theta)`), an odd-multiplicity singular crossing (`sin(theta)^3` through an exact harmonic identity), exact signed `1/1000000` neighbours, and a hidden-two-root `cos(2 theta)` interval. Unsupported non-cardinal endpoints, tangent-half pole crossings, polynomial-modulated/general coupled analytic grammars, source-parameter mismatch, float authority and resource-result laundering all fail closed.

## Programme effect

`PB-007-01`, PO-04, PO-05 and PO-08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`. The 26-operation denominator is unchanged; synchronized lathe threading, eccentric turning and fixed-axis helical milling remain in scope. No native, paid or production execution is authorized by this result.

The next pre-gate repair priority after this bounded investigation is `PB-007-02`. MC-B must not be retried for acceptance while the required pre-gate claims remain open.

## Protected semantics

Source/audio/provenance, canonical-journal meaning, exact time/path/phase correlation, positive-volume material, durable body/lineage, historical negative evidence and conventional STEP semantics are unchanged. `BLOCKED`, `UNCERTIFIED`, `RESOURCE_REFUSAL`, timeout and refinement exhaustion remain non-success outcomes.
