# MC-038 / PB-007-01 — exact affine source-time covariance for rational B-splines

**8 November 2026. Research-only DETERMINISTIC_MODEL. Draft; no main merge.** Parent: [Ready PR #458](https://github.com/techrote/radiCADSAC/pull/458) at 7c3d2f8aa510ab61d04ae7eb6611e77983ba397e, with #457 → #455 → #453. [PR #397](https://github.com/techrote/radiCADSAC/pull/397) retains exclusive accepted-main integration.

## Problem and falsifiable hypothesis

Change the rational source-time parameter by an invertible affine map, old_t = a + b*new_t, with b nonzero, while preserving the *entire* source's H0/C1/S1/C2/S2 moving-phase physical function. Transform each clamped B-spline knot u to (u-a)/b; if b is negative, reverse BOTH knot and control sequences. Transform affine moving phase offset to offset + slope*a and slope to slope*b. Then F_new(t) = F_old(a+b*t) identically on the transformed domain, preserving physical root count and types. For negative b, the left/right signs and sided orders of exact knot/exterior boundary events must swap.

**Falsifiers:** a single wrong rational coefficient polynomial on a mapped full source span; wrong structural knot identity/multiplicity; wrong physical knot time, order or sided sign; altered phase or source digest; mismatch between top-level claimed precision and either verified child; forged event/receipt/claim; resource or input refusal classified as physical truth.

## Mathematical proof and source-to-source certificate

The Cox–de Boor recurrence has affine covariance and reversal symmetry. Crucially, the verifier *independently* lowers both supplied B-spline source vectors using the #458 rational basis/Newton compiler. It finds exactly one covering original polynomial source piece for each transformed piece and checks every coefficient in the exact rational power basis by expanding P(a+b*t) with binomial coefficients. This checks whole-piece equality across all five fields, not just selected sample points. The inherited moving harmonic phase is transformed exactly, so full two-harmonic physical equality follows.

Genuine structural knot witnesses are rebuilt from the transformed supplied knot vectors and compared with exact rational transport of the original multiplicities. Both separate complete physical event certificates are independently source-replay-verified, including their claimed binary precision. The verifier does not rerun potentially expensive root searches; differing correct interior subdivisions are allowed. Exact old physical boundary events are mapped rationally, with source-piece boundary indices reversed for negative scale and both sided signs and sided orders interchanged. The total physical root counts must coincide.

**Limits:** rational canonical |a|,|b| ≤ 8, b nonzero; after transform the complete domain must still be within [-8,8]. Inherit #458 degree ≤3, at most four distinct union pieces, at most 24 controls per field, exact rational/receipt budgets and parent complete event requirement. Higher-order contacts or proof-budget limits can refuse NONTRUTH; refusal does not falsify mathematical function equality. Negative source-time orientation is **not** permission to physically reverse a machining history, and the supplied source SHA is **not** frozen-original provenance.

## Adversarial test plan and execution

Eight focused tests: genuine double-knot, two-harmonic second-order touch with non-symmetric rational reversal; unequal sided order under reversal; actual knot crossing with swapped signs; positive half-rate affine time; nonzero H0, C1, S1, C2 and S2 simultaneously; source/precision/provenance/event-tampering refusals; boolean, noncanonical, zero and over-budget map refusals; and 160 independent randomized exact degree-0..3 B-splines with 4,000 rational basis comparisons including endpoints and interior knots. The parent rejects discontinuous degree-zero coefficient functions; randomized degree-zero controls are equal to respect that scope.

Reproduce on the PR head:

- python3 research/machining-completeness/tasks/MC-038/pb00701_bspline_affine_time_covariance_20261108.py --contract --self-test
- python3 research/machining-completeness/tasks/MC-038/pb00701_genuine_bspline_knot_bridge_20261108.py --contract --self-test
- python3 research/machining-completeness/tasks/MC-038/pb00701_generic_second_order_boundary_20261108.py --contract --self-test
- python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
- python3 tools/validate_machining_completeness.py

A dedicated literal-head workflow additionally runs inherited generic and zero-boundary tests, original V54/V2 full producing reconciliation and repository-wide MC-1 static checks. Failed runs are preserved, not hidden; independent distinct-session mathematical/source review is required before a Ready transition.

## Historical and production nonclaims

V54 **121 originals / 20 historical route refusals / 30 missing ordered premises** and V2 **50 already complete original source witnesses** remain unchanged; newly closed historical IDs empty, required PB/PO discharge zero. MC-B and MC-1 remain NOT_ESTABLISHED. No native kernel, physical machine time reversal, topology/body semantics, engineering B-rep/STEP, consumer acceptance, expensive campaigns or production authorization. No edits to accepted main, #397, #421, frozen evidence, shared authority/proof/programme registries or other workers' branches. Main integration remains with #397 in dependency order.
