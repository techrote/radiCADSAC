# Propagated uncertainty and error-budget algebra

Status: RCS-023 measured research output  
Date: 2026-09-18  
Issue: RCS-023 / #42  
Model: `rcs-uncertainty-budget/1.0`

## Purpose and scope

RCS-007 proved that one enlarged tolerance cannot safely stand for manufacturing tolerance, numerical uncertainty, contact policy and export acceptance. RCS-023 closes the next gap: it defines how bounded errors move through the manufacturing pipeline, how ambiguity survives decision boundaries, and when a later exact/export claim must fail closed.

The result is an executable conservative interval model. It is not a production geometry engine and it does not claim probabilistic calibration of providers.

## Inputs retained from accepted research

This work preserves the accepted programme constraints rather than reopening them:

- canonical journal intent remains durable and provider independent;
- positive material-removal intent cannot be erased by fuzzy/numerical convenience;
- local uncertainty/contact compatibility is not global identity;
- semantic lineage is programme-owned rather than backend topology identity;
- fallback/deferred material may be bounded internally but must reconcile to conventional B-rep before STEP success;
- STEP success continues to mean RCS-005 Layers A–D, with RCS-022 currently retaining `interoperability_unqualified` for its exact profile.

## Hypotheses and falsification criteria

The executable plan freezes six hypotheses before interpretation. The central falsification conditions are unsafe decisive contact inside an uncertainty band, silent loss of the 1 nm positive-removal witness, acceptance of naive RSS/max-only handoff algebra, loss of order sensitivity through transforms, or export success despite a known breach/unknown channel.

The committed deterministic campaign does not falsify those hypotheses.

## Channel contract

### Composable numerical/representation channels

The v1 algebra admits these bounded geometric error contributions:

- source/canonicalization quantization;
- trajectory fitting/simplification;
- frame translation;
- frame rotation converted to a spatial displacement bound at a declared radius;
- tool-envelope construction;
- provider numerical algorithm error;
- fallback/discretization/representation error;
- reconciliation/fitting/stitching error.

### Non-error policy/requirement channels

These remain distinct and are **not** numerically added into the uncertainty sum:

- manufacturing tolerance/requirement;
- topology/contact classification policy;
- STEP/export/validation budgets.

The implementation rejects attempts to insert these policy channels as numerical error contributions. This is intentional: a 0.01 mm manufacturing tolerance does not make an unknown numerical error equal to zero and does not authorize erasing a 0.000001 mm positive removal command.

## Composition algebra

Let a stage's scalar spatial error be represented by interval `E=[l,u]`. For two errors whose dependence is unknown, v1 uses the Minkowski sum:

`E_total = E1 + E2 = [l1+l2, u1+u2]`.

For symmetric half-widths this reduces to conservative addition of half-widths.

### Transform propagation

A local error remains attached to the stage where it is introduced. Downstream sensitivity/gain applies to that term. For a bounded angular transform with radius `r` and angle `theta`, the spatial displacement uses the conservative chord inequality:

`2 r sin(theta/2) <= r theta`.

The campaign's order-sensitive witness places unequal local errors around a ×2 gain. The two resulting bounds are 45 nm and 30 nm. Therefore stage errors cannot safely be detached from the transform graph and summed as context-free epsilons.

### Correlation and RSS

Unknown correlation uses conservative composition. RSS is a diagnostic only unless independence is justified explicitly.

The campaign uses 100 repeated 1 nm errors. A same-sign systematic source produces a 100 nm error, while the RSS diagnostic is 10 nm. Treating RSS as the correctness bound would under-bound the measured construction by 10×.

Cancellation is permitted only when the terms are proven to derive from the same bounded source and their coefficients are known. The paired `+1/-1` same-source control cancels exactly; unrelated errors are never cancelled because they happen to have opposite nominal signs.

### Provider handoff

A provider/representation boundary carries:

`source residual + conversion residual + destination residual`.

The campaign's 8 nm + 6 nm + 4 nm handoff yields an 18 nm conservative half-width. A max-only rule would report 8 nm and silently discard two known sources.

## Decision semantics at physical boundaries

For a signed gap `d` and propagated error interval `E`, the physical relation is `d+E`:

- if the entire interval is negative: decisive overlap/material interaction;
- if the entire interval is positive: decisive clearance/no interaction;
- if zero is contained: `accepted_pending`.

With a 10 nm uncertainty band, the `-10 nm`, exact-tangent and `+10 nm` members all remain pending because zero lies on/in their physical interval. The `-20 nm` and `+20 nm` witnesses are decisive.

This strict one-sided rule prevents hidden snapping at exact/tangent/near-coincident boundaries.

## Positive sub-tolerance material intent

A positive material-removal command is handled differently from an inferred contact-only interaction. A commanded depth `p > 0` remains signed positive intent. If `p+E` is entirely positive, material change is decisive. If the interval crosses zero, the result is `accepted_pending`, never `decisively_no_material_change`.

The committed witness is a 1 nm removal depth under a 5 nm uncertainty half-width. Its physical-depth interval is `[-4,+6] nm`; the result remains pending with positive intent explicitly preserved.

## Repeated-operation and correlated-error findings

The repeated chain demonstrates two important non-properties:

1. square-root accumulation is not a correctness guarantee without independence;
2. numerical signs are not permission to cancel unless they refer to a proven shared source relationship.

This is directly relevant to long manufacturing journals: operation count and error correlation may differ from unique physical-boundary count, and semantic replay/collapse must be based on provenance proof, not statistical wishful thinking.

## End-to-end pipeline traces

### Lathe representative path

The lathe trace carries canonical quantization → trajectory fit → translation → rotation → tool envelope → provider execution → bounded representation handoff → B-rep reconciliation.

The final conservative spatial half-width is **14.5 nm**. The fixture's decisive pre-provider overlap remains one-sided and the reconciled result fits the declared 20 nm dimension/surface budget, therefore its geometric budget state is `export_eligible`.

This does not bypass RCS-005 body/validity/analytic/unit/read-back/interoperability checks.

### Mill fallback representative path

The mill path exercises the same front-end stages, an exact provider residual, the RCS-021-style bounded fallback and B-rep reconciliation.

Before reconciliation the fallback is explicitly `bounded_representation_inexact`. After reconciliation the total half-width is **17.5 nm**, within the fixture's 20 nm geometric budget. Only then is its geometric budget state `export_eligible`.

This demonstrates the required distinction between "bounded enough to keep working internally" and "resolved enough to claim conventional engineering export".

## Reconciliation and fail-closed export rules

The deterministic controls are:

- 10 nm fallback + 5 nm reconciliation = **15 nm**: geometric budget passes under 20 nm;
- 18 nm fallback + 8 nm reconciliation = **26 nm**: `error_budget_breach`;
- known 3 nm provider residual plus an unmeasured reconciliation fit: `refused_accuracy_unproven`, even under a much larger nominal manufacturing tolerance.

A missing bound is not zero. A requested tolerance is not permission to invent a bound. A breach is not repaired by widening the tolerance without an explicit user/profile decision.

## RCS-005 mapping

RCS-005 requires at least dimension, surface, angular and volume acceptance budgets plus exact body/connectivity/validity semantics.

RCS-023 v1 makes the **linear/spatial** error path executable. Its final scalar spatial half-width can be compared with applicable `max_dimension_error_nm` and `max_surface_deviation_nm` after conversion.

It does **not** infer `max_volume_error_abs_mm3`, `max_volume_error_rel` or angular accuracy from that scalar without a geometry-specific sensitivity/Jacobian proof. Those remain separate acceptance channels. This prevents the new model from becoming another magic epsilon under a different name.

Export geometric eligibility requires:

1. all required composable error channels bounded;
2. no relevant unresolved contact/positive-intent ambiguity;
3. reconciliation complete;
4. final propagated spatial bound no larger than every applicable requested dimension/surface budget;
5. all other RCS-005 gates evaluated separately.

RCS-022's current independent-interoperability qualification remains unchanged.

## RCS-018 and RCS-025 coordinator integration

The budget trace is derived execution evidence linked to durable programme IDs. Durable context may include journal event, revision, material-body and semantic-operation identity; provider-private `TopoDS_*`, kernel handles, process IDs and equivalent identities remain forbidden.

Recommended transition semantics:

- one-sided physical interval → decisive accepted result;
- interval crossing a decision boundary → `accepted_pending` with signed intent and trace retained;
- bounded fallback before B-rep → `accepted_pending` plus `bounded_representation_inexact` detail;
- known propagated excess → budget-breach failure, not healing;
- unknown required error/incomplete reconciliation → refusal for exact/export requests;
- provider transition → append source/conversion/destination error contributions rather than resetting the budget.

RCS-025 must preserve this trace through repeated defer/reconcile/provider transitions. A handoff is acceptable only if the destination can state how the inherited bound and its own conversion/provider residuals consume the remaining requested budget.

## Provenance and protected semantics

Uncertainty accounting is not allowed to rewrite source semantics. The executable trace validates durable context and rejects provider-private identity keys. Journal/revision/body identifiers pass through unchanged.

This also preserves the RCS-008 conclusion that backend topology identity is diagnostic rather than durable programme identity.

## Architecture recommendation

The following rules should become programme contract:

- distinct numerical/representation channels; no universal epsilon;
- conservative interval composition where dependence is unknown;
- explicit evidence requirement before RSS/cancellation is used for correctness;
- strict one-sided physical classification around decision boundaries;
- signed positive-removal intent preserved through ambiguity;
- provider handoff retains source+conversion+destination residuals;
- unknown required bounds fail closed;
- manufacturing requirements and export budgets remain comparison criteria, not solver error;
- conventional STEP success requires completed reconciliation and RCS-005 conformance;
- budget/provenance traces stay programme-owned and backend-independent.

Provider-private implementation may choose richer local error representations, interval arithmetic, affine arithmetic, exact predicates, interval geometry or validated numerics, provided the programme-facing handoff can conservatively project them into the contract and does not claim a tighter bound than it can demonstrate.

## Known limitations

- v1 propagates a scalar spatial envelope, not a full anisotropic covariance/polytope field;
- geometry-specific mapping into volume error is not automated;
- the fixture bounds exercise the algebra rather than calibrating production provider tolerances;
- no statistical independence model is accepted for production by this issue;
- RCS-022 independent interoperability remains separately unqualified.

These are explicit limits, not hidden assumptions.

## Reproduction

```bash
python3 -m unittest discover -s research/rcs-023 -p 'test_*.py' -v
python3 research/rcs-023/run_campaign.py \
  --out-dir .results/rcs023 \
  --compare-reference research/rcs-023/reference-results-v1.json
python3 tools/validate_rcs023.py --results-dir .results/rcs023
```

The deterministic campaign uses only the Python standard library. CI compares live results against the committed reference evidence and exercises adversarial boundary tests.
