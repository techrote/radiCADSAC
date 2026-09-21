# MC-030 — Native B-rep/process provider and total-dispatch design

Status: **COMPLETED_RESEARCH** as a provider-selection/dispatch design; no native capability gate is promoted.  
Issue: #92.  
Source baseline: `fd0662dbefcc1eaa03e2be0503e53860feaa4cf0`.  
Evidence class: source-bound dependency inspection + deterministic dispatch model + adversarial contract review.  
Native/paid execution: **none**.

## Question and decision

MC-030 asks whether qualified native B-rep/process specializations can be retained as useful fast paths without allowing kernel success, topology identity, sampling or implementation convenience to become the canonical material truth, and whether all remaining valid requests can be routed without provider cycles.

The result is a bounded **yes for dispatch design**, not a native-success claim. Four sufficient fast-path admission predicates are frozen and every other source-bound material-changing request is sent to one unique `GENERAL_CERTIFIED_ROUTE`. That general route is a total routing sink, not a promise of total geometric success: unresolved proof obligations remain typed terminal outcomes and are never converted to success.

## Authority preserved

The canonical material authority remains the programme-owned source/material relation bound to the immutable operation journal, exact input revision and durable `body_id`. Native B-rep validity is not material correctness: MC-016 already preserves a historical native B-rep that is valid yet materially wrong. Kernel component identity/order/size is not durable body or lineage authority. A fast provider may terminate successfully only when its result is accompanied by the independently required material certificate.

STEP/B-rep write success is likewise not independent engineering-output qualification. Existing representability and consumer blockers remain open.

## Sufficient fast paths

`FP-MILL-ANALYTIC-TRANSLATION` consumes the MC-018/019 exact fixed-axis stationary/line/polyline translation slices for flat, corner-radius and ball/round cutters. Admission requires exact source/common-frame/body/revision binding, complete finite cutter geometry, zero MC-058 unresolved enclosure, no body-transition obligation and no singular/exact-zero output boundary.

`FP-FORM-BOX-UNION` consumes the bounded MC-020 exact-rational box-union form/undercut codec. Accessible undercuts additionally require the complete cutter-plus-holder `COMPLETE_TOOL_CLEAR` witness. Cutter labels, head-only access or an enclosing hull/AABB are insufficient.

`FP-LATHE-AXISYMMETRIC` consumes MC-021 only when the exact durable target is certified axisymmetric, the setup is coaxial, the meridian is phase-independent, every meridian state receives the full spindle orbit and the admitted meridian codec is exact. Operation names such as “OD turning” are not admission evidence.

`FP-LATHE-PHASE-BOUNDED` consumes the finite MC-022 synchronized/eccentric subtype only when cutter/feed state and unwrapped spindle phase share the exact time parameter, the source is in the certified finite exact subtype and no unresolved transcendental event remains.

All fast paths additionally inherit MC-023 common-frame, exact-revision and durable-body target binding. A re-clamp is a non-cutting setup event, not material removal, and inherited uncertainty does not reset across setup transitions.

## Total noncycling dispatch

The dispatcher is deterministic and request-preserving. A valid request may invoke at most one fast provider and at most one general provider. Exactly one sufficient fast predicate selects that provider. Zero or multiple fast admissions select `GENERAL_CERTIFIED_ROUTE`; an unbound source is `INVALID_SOURCE`.

A fast provider failure, an uncertified result, or even `SUCCESS` without an independent material certificate falls back exactly once to the general route. The general route never dispatches back to a fast provider. Directional material, native mesh Boolean and sparse volume/level-set methods remain derived accelerators or challengers only; none is authority or a recursive fallback owner.

The general route may terminate as `SUCCESS_CERTIFIED`, `PB-007-01`, `PB-007-02`, `PB-007-03`, `UNCERTIFIED`, `RESOURCE_REFUSAL` or `SEMANTIC_BLOCKER`. Timeout, refusal and uncertainty are not success.

## Boundary and adversarial controls

The executable model covers exact flat and varying-Z ball milling, nonlinear/unresolved milling routed general, valid and holder-blocked accessible undercut, exact axisymmetric turning, phase-sensitive turning that is rejected from the axisymmetric path, bounded synchronized phase turning, transcendental-event fallback, body-transition fallback, exact-zero/singular output fallback, stale target binding, non-cutting re-clamp, fast failure fallback and successful fast output without its independent certificate.

The verifier attacks label-only admission, unresolved MC-058 geometry, missing holder/access evidence, phase/axisymmetry confusion, transcendental blocker laundering, stale revision/body binding, B-rep-validity-as-truth, kernel-topology identity, uncertified fast success, resource-refusal success, provider cycles, derived-candidate authority, positive-material deletion, exact-zero healing, blocker closure and premature MC-B promotion.

## Retained blockers and capability state

`PB-007-01`, `PB-007-02` and propagated `PB-007-03` remain open. `RB-016-02` and `RB-016-04` remain open. MC-030 does not invent a universal general solver, close native multi-body/output qualification, or authorize native/paid execution.

MC-A remains `ACCEPTED`; **MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`**. Protected historical `research/rcs-*` evidence, source/audio/provenance, canonical-journal meaning, positive-volume material and durable body/lineage semantics are unchanged.

## Verification

```text
python3 research/machining-completeness/tasks/MC-030/verify.py --contract
python3 research/machining-completeness/tasks/MC-030/verify.py --self-test
python3 tools/mc_workflow.py verify MC-030
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The exact PR head must pass `mc1-static` before merge, and the merged SHA must pass the same workflow on `main` before issue #92 is closed.
