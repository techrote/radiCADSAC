# MC-024 — Exact arrangement/cell candidate falsification

Status: **NEGATIVE_RESULT** as a general MC-1 fallback; retained as a bounded exact reference/control provider.  
Issue: #86.  
Source baseline: `07ea9c6c07b2836473162fa1f9dda18695b9a549`.  
Evidence class: dependency-bound source/theory review + deterministic exact-rational machining controls.  
Native/paid execution: **none**.

## Question and decision

MC-024 asks whether an exact arrangement/cell method can serve not merely as a useful mathematical reference, but as the general fallback behind a total machining dispatcher. The result is deliberately split:

- **Useful bounded role: retained.** For an operation instance that actually satisfies the MC-006 finite-semialgebraic admission hypotheses, exact quantifier elimination plus finite sign-invariant cell decomposition remains a defensible reference/control route. The task-local controls independently exercise exact tangency, a positive `1/1000000` material web, body separation, exact empty material and retrace idempotence with rational arithmetic.
- **General fallback role: falsified.** MC-007 already records open required cases where the needed unconditional exact finite route is not established: tangential/multiple/singular transcendental events (`PB-007-01`), general coupled helical/spindle-feed/eccentric sweeps (`PB-007-02`), and admitted source instances lacking a finite exact constructive encoding (`PB-007-03`). An exact-cell dispatcher cannot erase those blockers by productizing phase, sampling, adding epsilon or dropping operations.

Accordingly MC-024 completes as a negative candidate result, not as a capability acceptance. Exact/cell remains available as a bounded reference or optional provider after a checkable admission predicate. It is **not** the programme's total general fallback and does not close PO-08, MC-B, or MC-1.

## Dependency binding

The machine contract `exact-cell-falsification-v1.json` pins the exact reviewed outcomes from MC-006, MC-007, MC-010 and MC-016 by Git blob SHA. MC-007 is consumed as a `NEGATIVE_RESULT`; its open blockers remain evidence, not defects to edit away. MC-016 contributes output-side constraints that matter even where material cells are exact.

No historical RCS/Genesis artifact is rewritten. This task does not change source/audio/provenance meaning, canonical journal semantics, positive-volume material semantics, durable body identity or lineage.

## Candidate hypothesis and admission predicate

The retained exact/cell hypothesis is conditional and instance-local:

> If stock, cutter, setup and engaged motion have a **proved finite semialgebraic encoding** over rational/real-algebraic constants, with all denominator/sign side conditions proved and all shared time/feed/phase correlations preserved, then the MC-006 reviewed real-closed-field route provides a terminating exact reference construction.

The admission predicate therefore requires all of the following before exact/cell can own a case:

1. a finite semialgebraic encoding is actually proved for the concrete source instance;
2. coefficients/constants are rational or explicitly represented real algebraic values;
3. denominator and sign side conditions are proved rather than assumed;
4. time/path/feed/spindle-phase correlation remains shared and exact;
5. the history is finite; and
6. MC-002 regularized-removal semantics are preserved exactly.

Failure of any requirement must dispatch once to another reviewed owner or return the inherited typed blocker. It may not cycle providers, reinterpret the request, or silently accept a numerical approximation as an exact decision.

Binary floating predicates and a global epsilon are not accepted as decisive truth for this route.

## Small decisive machining controls

`verify.py --contract` contains a deliberately small exact-rational arrangement model. It is not native geometry evidence. Its purpose is to falsify common ways an “exact cells” proposal could quietly weaken semantics.

### Tangent boundary

A unit stock box is touched exactly at its `x=1` face by a cutter beginning at `x=1`. The regularized material volume remains exactly `1` with one connected component. Boundary contact alone cannot be inflated into positive removal.

### Positive micro-web

A `3 × 1 × 1` stock is cut from `x=0..1` and from `x=1000001/1000000..3`. The surviving web has exact volume `1/1000000` and remains one positive-volume component. No tolerance or sewing rule may delete it.

### Complete cut-through

Removing the full `x=1..2` slab from the same stock leaves exact material volume `2` and exactly two positive-volume components. A “keep largest body” policy is invalid.

### Exact empty material

Cutting the entire unit stock yields material volume `0` and zero material components. The correct result is explicit empty material, not a fake residual cell.

### Exact retrace

Repeating the same full cut-through produces the same exact material volume and component count as one cut. Raw event/history count is not geometry.

These controls also verify positive-area-face connectivity rather than edge/point bridging.

## Decisive coverage obstruction

The candidate matrix records six classes.

**EC-024-01** is the retained bounded reference domain: finite semialgebraic instances satisfying the admission predicate.

**EC-024-02** is blocked by `PB-007-01`. A generic exact-cell fallback has no reviewed unconditional finite rule for all required tangential/multiple/singular transcendental equality events. “Refine until small,” timeout, epsilon sign or a subdivision cap is not an exact decision.

**EC-024-03** is blocked by `PB-007-02`. General coupled helical/spindle-feed/eccentric sweeps require time/feed/phase correlation. Replacing that curve by the Cartesian product of path coverage and angular coverage changes the swept material and is forbidden.

**EC-024-04** is blocked by `PB-007-03`. Physical admission of imported stock and arbitrary form/undercut cutter instances does not prove those instances have a finite exact polynomial codec.

These three are already sufficient to falsify exact/cell as the programme's total general fallback without shrinking the 26-operation domain.

## Output and identity obstructions

Even when a material arrangement is exact, provider topology is not programme identity.

`RB-016-02` remains open for multiple disconnected positive-volume bodies through conventional engineering output. A cell or connected-component label cannot substitute for durable body identity or lineage, and MC-024 does not qualify independent STEP preservation.

`RB-016-04` remains open for exact-zero contacts, touching cavities and singular pinches. An arrangement can represent an exact material boundary while the engineering-output profile is still unresolved. Healing, tolerance fusion or inventing a positive bridge is prohibited.

These are not reasons to reject exact cells as a reference. They are reasons not to promote a material-reference result into a total engineering fallback.

## Resource obstruction

MC-006 already records the inspected CAD arithmetic-complexity result as doubly exponential in its stated setting. MC-024 does not turn mathematical termination into a practical-resource claim. No native campaign ran, and there is no evidence here that a full-domain exact arrangement is acceptable as the default production path under MC-004/MC-F resource envelopes.

Timeout may falsify practical suitability. It may never be recorded as mathematical success.

## Total-dispatch consequence

For downstream MC-026 selection, the exact/cell candidate has the following bounded role:

- **yes:** exact reference for admitted semialgebraic instances;
- **yes:** independent control/provider candidate where its admission proof is available;
- **no:** total general fallback over all of D;
- **no:** substitute for the MC-007 unresolved analytic route;
- **no:** source codec for arbitrary imported/form geometry by assumption;
- **no:** durable-body/lineage authority;
- **no:** engineering-output/profile qualification;
- **no:** practical-resource qualification.

A future total dispatcher may call exact/cell only behind the explicit admission predicate. Failure must move to another reviewed route or return a truthful blocker; it must not cycle back or weaken the request.

## Retained blockers and downstream effect

The task preserves the existing blocker identities rather than inventing duplicate repair issues:

- `PB-007-01` — OPEN; still affects candidate selection and MC-B integration.
- `PB-007-02` — OPEN; still affects candidate selection and MC-B integration.
- `PB-007-03` — propagated from MC-006; still affects arbitrary-source coverage, candidate selection and MC-B integration.
- `RB-016-02` — OPEN; still affects durable multi-body engineering output.
- `RB-016-04` — OPEN; still affects exact-zero/singular engineering output.

MC-026 may consume this negative result as candidate evidence. It must not convert any retained blocker into an accepted capability.

## Capability state and non-claims

No native or paid execution occurred. This task does not establish a native exact-arrangement implementation, practical CAD/QE performance, universal topology certification, source completeness, STEP qualification, or total dispatch.

MC-A remains `ACCEPTED`. **MC-B remains `NOT_ESTABLISHED`**, as do MC-C, MC-D, MC-E, MC-F and MC-1. The programme denominator is unchanged.

## Verification

```text
python3 research/machining-completeness/tasks/MC-024/verify.py --contract
python3 research/machining-completeness/tasks/MC-024/verify.py --self-test
python3 tools/mc_workflow.py verify MC-024
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The exact PR head must pass `mc1-static` before merge, and the merged `main` must pass the same workflow before the issue is treated as accepted research evidence.
