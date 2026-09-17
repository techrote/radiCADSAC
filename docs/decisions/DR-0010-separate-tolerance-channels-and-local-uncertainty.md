# DR-0010 — Separate tolerance channels and keep uncertainty local

Status: accepted research decision; subject to RCS-013 architecture synthesis  
Date: 2026-09-17  
Evidence: RCS-007 on pinned OCCT 8.0.1

## Context

MSAC routinely creates exact coincidence, tangency, retraced passes, very small positive cuts and long sequences of near-identical manufacturing operations. A conventional geometry kernel offers several tolerance mechanisms, but those mechanisms do not all mean the same thing as manufacturing tolerance, numerical uncertainty or user intent.

RCS-007 compared operation-wide OCCT fuzzy Boolean tolerance, operation-local uncertainty/contact classification, semantic replay collapse, anchored coordinate quantization and controlled perturbation using the RCS-003/RCS-006 fixtures.

## Decision

The programme will not define one universal epsilon or one global “virtual tolerance” equivalence relation.

Until RCS-013 synthesizes the final architecture, the programme model keeps at least these channels conceptually distinct:

- input/sampling resolution;
- machine/control resolution;
- manufacturing tolerance;
- numerical uncertainty;
- topological equivalence;
- contact classification;
- preview tolerance;
- export tolerance;
- validation tolerance.

Additional fixed rules from this research decision are:

1. Backend entity tolerances and OCCT Boolean fuzzy tolerance remain explicit backend state/parameters; neither is programme-level manufacturing truth.
2. Metric closeness within a local uncertainty band may be used as an operation-local **compatibility/contact relation**, but not as durable global identity and not through transitive closure.
3. A local uncertain-contact result means **defer/reconcile**, not “no material change”. The original signed manufacturing intent remains available.
4. Explicit positive material-removal commands are not silently converted to no-ops merely because their magnitude is below a numerical, fuzzy or manufacturing-tolerance channel.
5. Exact semantic retraces may be candidates for skipping redundant exact-geometry recomputation while their journal events remain preserved, but only after RCS-008 supplies a durable provenance/identity proof. Kernel object identity or proximity alone is insufficient.
6. Fixed-grid quantization is allowed only where a grid is itself an explicit contract. It is not the authoritative equivalence mechanism for arbitrary engineering geometry.
7. Controlled perturbation may be used as a deterministic diagnostic, or as an explicitly bounded tie-breaker only when manufacturing semantics determine the permitted side. Random hidden jitter is not an accepted robustness policy.
8. Internal uncertainty/deferred state must reconcile to conventional geometry satisfying the RCS-005 STEP conformance contract. If materially distinct outcomes cannot be resolved within the declared export/validation budgets, export is refused or remains unqualified.

## Alternatives considered

### One programme-wide enlarged epsilon

Rejected. In the RCS-007 smoke experiment, OCCT fuzzy value `0.0001 mm` silently erased real material removal for a `-0.0001 mm` coincident penetration, a `-0.0001 mm` tangent penetration, a `0.000001 mm` positive skim and a `0.0001 mm` positive skim. All four outputs remained valid one-solid B-reps, demonstrating that topological validity does not protect physical intent.

The same fuzzy value also produced geometrically wrong but valid results in nested finishing chains and made the 100-step chain order-dependent.

### Global pairwise “within u” equivalence

Rejected as durable identity because `|a-b| <= u` is not transitive. Transitive closure can merge endpoints farther apart than the intended uncertainty.

### Anchored global quantization

Rejected as the general engineering truth model. Bucket equality is transitive, but the experiment’s `0.0001 mm` grid erased the `0.000001 mm` positive skim, and its algebraic boundary example placed coordinates only `0.000002 mm` apart into different buckets.

### Blind perturbation/jitter

Rejected. With zero fuzzy tolerance, deterministic `±0.0001 mm` neighbors around both coincidence and tangency produced different material semantics: negative penetration removed material while positive clearance did not.

### Always execute every exact retrace

Not required as a programme invariant. Six repeated-finishing smoke records, including 100 repeats at fuzzy values `0` and `0.0001 mm`, were geometrically equivalent to the one-effective-pass reference. The production proof condition remains deferred to RCS-008.

## Evidence

RCS-007 hosted smoke evidence:

- workflow run: `35191482255`;
- evaluated branch head: `e8ba0a4909ec619b9fefb4f9d9896c4025d45dfc`;
- artifact: `rcs007-virtual-tolerance-smoke`, ID `10483269288`;
- artifact digest: `sha256:745cfab6f747361b8b0b9f2eb2a6528fc73d3c11b5c9203764d0e81d54608ec6`;
- durable summary: `research/rcs-007/measured-summary-v1.json`.

Measured highlights:

- 26 fuzzy/contact/skim attempts; zero worker failures;
- 4 OCCT global-fuzzy physical-oracle mismatches;
- 12 local uncertain-contact deferrals and zero decisive local-classification mismatches;
- 2 anchored-quantization mismatch records, both representing the same `0.000001 mm` physical skim under the two backend fuzzy settings;
- zero non-equivalent repeated-finishing collapse records across 6 tests;
- 2 accumulation cases with analytic-volume breaches; the 100-step `0.0001 mm` fuzzy chain differed by `7.539633873064304 mm³` between operation orders despite both results being valid one-solid B-reps;
- 2 direction-sensitive perturbation pairs with zero fuzzy tolerance.

Upstream OCCT 8.0.1 explicitly describes `BOPAlgo_Options::FuzzyValue` as an additional tolerance for detecting touching/coinciding cases; it is not documented as manufacturing tolerance or intent semantics.

## Consequences

- RCS-008 must make any replay-collapse proof semantic/provenance based and backend-independent.
- RCS-009 may use a local unresolved/contact state, but must not turn the non-transitive compatibility relation into global topological identity.
- RCS-010/RCS-011 process-specialized solvers should consume explicit operation semantics and may avoid generic Boolean calls for known retraces or process-specific limiting cases.
- RCS-013 should define a versioned tolerance-policy object/schema rather than a single scalar tolerance.
- Validation must continue to measure physical geometry, not accept a valid B-rep as sufficient evidence.
- STEP reconciliation remains governed by RCS-005 and may refuse unresolved ambiguous geometry.

## Reversibility

High for numerical values and the exact uncertainty model; medium for the separation-of-concerns rule. Specific uncertainty propagation, reconciliation timing and process-specific policies are deliberately open.

The prohibition on silently equating manufacturing tolerance, numerical uncertainty and topology identity is intended to be durable because reversing it would reintroduce the measured semantic-loss failure mode.

## Reconsideration trigger

Reconsider this decision if RCS-008–RCS-012 produce reproducible evidence that a different equivalence/uncertainty model preserves signed manufacturing intent, avoids order dependence, remains deterministic, and satisfies RCS-005 export conformance with materially lower complexity or cost.
