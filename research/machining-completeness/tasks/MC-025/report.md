# MC-025 — Adaptive interval/implicit candidate falsification

Status: **NEGATIVE_RESULT** as a total/general MC-1 fallback; retained as a bounded certified material representation/accelerator after separate event and finite-progress certification.  
Issue: #87.  
Source baseline: `9668fa058a97219880897a483ac25c530ccfc67b`.  
Evidence class: dependency-bound reviewed argument + deterministic exact-rational adaptive controls.  
Native/paid execution: **none**.

## Question and decision

MC-025 asks whether certified adaptive interval/implicit material can remove fixed-pitch discretization floors without falling into infinite equality refinement. The answer is split.

- **Fixed-pitch floor: avoidable on certified bounded cases.** An adaptive representation need not inherit a globally chosen voxel/pitch floor. When every cell carries sound outward material bounds and every decisive boundary/critical event is supplied by a separately certified event procedure, exact event insertion can refine only where needed. The task-local controls preserve exact tangency, a `1/1000000` positive material web, complete removal, split material and exact retrace idempotence using rational arithmetic.
- **Generic equality termination: not supplied by adaptivity.** Adaptive subdivision is a representation/refinement strategy, not an exact equality oracle. The exact `1/3` control remains strictly inside a positive-width dyadic cell at every finite bisection depth. Width tends to zero, but no finite depth proves equality unless the event is introduced by a separately justified exact/validated event decision.
- **General fallback: falsified.** MC-008 already preserves the MC-007 proof blockers for required tangential/multiple/singular transcendental events and general coupled phase-sensitive motion. MC-025 cannot erase those blockers by “refine until small”, maximum depth, epsilon, timeout or independent phase coverage.

MC-025 therefore completes as a negative candidate result for the **total general fallback** role. Certified adaptive interval/implicit material remains a useful bounded provider or accelerator behind a strict admission predicate. It does not close PO-08, MC-B, MC-C or MC-1.

## Dependency binding

The machine contract `adaptive-implicit-falsification-v1.json` pins the exact reviewed outcomes from:

| Task | Result | Bound `outcome.json` Git blob |
|---|---|---|
| MC-008 | `COMPLETED_RESEARCH` | `a4b3f3451abedd06f2467a8e11741cdc63826e2b` |
| MC-010 | `COMPLETED_RESEARCH` | `4960730316f89dbb3fbf958d054127fa4fc0d789` |
| MC-016 | `COMPLETED_RESEARCH` | `606a7d0b8be61131b2272f2eb161d6a4dbba703a` |

MC-008 supplies the fail-closed arithmetic/event discipline and its retained proof blockers. MC-010 supplies independent exact-rational boundary/material controls. MC-016 supplies the output-side micro-feature and singular-contact blockers. No historical RCS/Genesis source is rewritten.

## Candidate hypothesis

The retained hypothesis is deliberately conditional:

> Given sound outward cell enclosures, a separately justified exact or validated critical-event certificate, an input-derived finite progress witness, preserved shared time/feed/spindle-phase correlation and unchanged regularized-removal semantics, adaptive subdivision can avoid a fixed global pitch while maintaining a certified material sandwich.

The candidate is admitted only when all six conditions in the machine contract are checked. Failure dispatches once to another reviewed owner or returns the inherited typed blocker. It may not cycle providers or weaken the source request.

Binary floating predicates, a global epsilon, a fixed pitch and a maximum subdivision depth are all forbidden as decisive correctness authority.

## Sound cell and error contract

The adaptive representation is required to maintain a material sandwich `L ⊆ M ⊆ U`.

- A lower/material-certified cell may be added to `L` only after material membership is proved for the whole cell.
- `U` may include unresolved cells, but unresolved cells are not success.
- Numeric width/error may bound **where** an unresolved boundary can be; it cannot decide discrete topology, exact equality, durable body identity or lineage.
- A small numeric width may not delete positive-volume material.
- Topology requires its own discrete certificate rather than being inferred from a Hausdorff/error scalar.

This is the central distinction between “adaptive accuracy” and “complete finite semantics”.

## Exact-rational adaptive controls

`verify.py --contract` runs a small independent 1D material model using `fractions.Fraction`. It is intentionally not native geometry evidence.

### Exact event split

Stock `[0,3]` with certified removal `[1,2]` is partitioned exactly at events `1` and `2`. Material measure is exactly `2` with two positive-measure components. No background pitch participates.

### Positive micro-web

Stock `[0,3]` removes `[0,1]` and `[1000001/1000000,3]`. Exact event insertion retains the surviving web `[1,1000001/1000000]` with measure exactly `1/1000000`. A coarse cell size or tolerance is not allowed to erase it.

### Tangent boundary

Stock `[0,1]` with a removal interval beginning exactly at `1` has zero positive-measure overlap. Material remains exactly `1`. Exact contact is not promoted into removal.

### Exact empty material

Removing `[0,1]` from stock `[0,1]` yields measure `0` and zero material components. Empty material is explicit; no epsilon residual is invented.

### Retrace idempotence

Applying the same `[1,2]` removal twice produces the exact same material measure and component count as one removal. Refinement/event count is not geometry.

## Why adaptive refinement does not decide equality

The machine contract includes an exact `1/3` counterexample under dyadic bisection of `[0,1]`.

At depth `n`, every cell boundary is `k/2^n`. Since `1/3 = k/2^n` would imply `3k = 2^n`, no finite integer `k,n` can satisfy it. Therefore `1/3` remains strictly inside a positive-width dyadic cell at every finite depth. The uncertainty width is exactly `2^-n`, so it converges to zero without ever becoming an exact equality decision.

This directly falsifies the idea that “keep subdividing until sufficiently small” is, by itself, a terminating exact event procedure. A separately certified critical-event mechanism can inject `1/3` exactly and eliminate the local uncertainty; without such a mechanism the required equality remains unresolved.

## Coverage classification

The candidate matrix separates six cases.

**AI-025-01 — piecewise rational axis-aligned controls:** retained as a task-local model/reference role with exact event locations.

**AI-025-02 — proved separated/transversal analytic events:** conditionally admissible through the MC-008 A2 discipline, but only with an input-derived finite stopping/isolation witness.

**AI-025-03 — tangential/multiple/singular transcendental equality:** blocked by existing `PB-007-01`. Shrinking uncertainty is not exact equality.

**AI-025-04 — general coupled helical/spindle-feed/eccentric event geometry:** blocked by existing `PB-007-02`. Shared time/feed/spindle-phase correlation must remain intact; independent phase coverage is not a semantics-preserving substitute.

**AI-025-05 — positive micro-feature engineering realization:** material-model preservation does not discharge `RB-016-03`. No qualifying native STEP evidence yet proves preservation at the certified micro-feature boundary.

**AI-025-06 — exact-zero/singular engineering output:** material classification does not discharge `RB-016-04`. Healing, tolerance fusion or inventing a bridge is forbidden.

These are existing blockers, not new duplicate defect classes.

## Resource and termination consequence

Adaptivity removes a **fixed-pitch floor**, not the need for a finite correctness argument. Cell counts can still grow sharply near complex boundaries, and an unresolved exact event can cause refinement to continue forever unless a finite event/stopping certificate exists.

Accordingly:

- fixed depth may be a resource limit but not a correctness proof;
- timeout may be a truthful practical failure but not semantic success;
- reaching a requested cell width may certify a numeric band only when the governing theorem permits it;
- unresolved topology/equality remains unresolved regardless of width.

Practical production viability therefore remains open for later resource/implementation tasks.

## Total-dispatch consequence

For MC-026 candidate selection, the adaptive interval/implicit candidate has this bounded role:

- **yes:** adaptive certified material representation when its soundness/event admission predicate is met;
- **yes:** accelerator or optional provider for cases with proved finite event/stopping certificates;
- **yes:** avoids a global fixed-pitch discretization floor on such cases;
- **no:** generic exact equality solver;
- **no:** total general fallback over all admitted machining histories;
- **no:** substitute for the MC-008/MC-007 blocked transcendental/coupled-event route;
- **no:** engineering-output qualification for micro-features or singular contacts;
- **no:** durable body/lineage authority;
- **no:** practical-resource qualification.

Failure must move once to another reviewed route or return a typed blocker. Provider cycling, epsilon promotion and denominator shrinkage remain forbidden.

## Retained blockers

MC-025 preserves four existing blocker identities:

- `PB-007-01` — OPEN; required tangential/multiple/singular transcendental equality remains without an unconditional finite exact decision route.
- `PB-007-02` — OPEN; general coupled helical/spindle-feed/eccentric event geometry remains without a complete constructive route.
- `RB-016-03` — OPEN; native engineering-output preservation of certified positive micro-features remains unqualified.
- `RB-016-04` — OPEN; exact-zero contacts/touching cavities/singular pinches still require an explicit output profile and independent-consumer evidence.

MC-026 may consume the negative candidate evidence but must retain those blockers until their actual owners close them from evidence.

## Capability state and non-claims

No native or paid campaign ran. MC-025 does not establish a production adaptive solver, a universal critical-event engine, universal topology certification, STEP preservation, durable body/lineage mapping or practical scale.

MC-A remains `ACCEPTED`. **MC-B remains `NOT_ESTABLISHED`**, as do MC-C, MC-D, MC-E, MC-F and MC-1. The 26-operation denominator is unchanged. Protected source/audio/provenance, canonical-journal, positive-volume material, durable body/lineage and historical negative-evidence semantics are unchanged.

## Verification

```text
python3 research/machining-completeness/tasks/MC-025/verify.py --contract
python3 research/machining-completeness/tasks/MC-025/verify.py --self-test
python3 tools/mc_workflow.py verify MC-025
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The exact PR head must pass `mc1-static` before merge, and merged `main` must pass the same workflow before issue #87 is treated as accepted research evidence.
