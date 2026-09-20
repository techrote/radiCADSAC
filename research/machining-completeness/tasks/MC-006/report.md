# MC-006 — Exact algebraic/cell reference route for covered constructors

Status: **COMPLETED_RESEARCH** — conditional exact reference route established for the semialgebraic slice; no capability gate changes.  
Issue: #68.  
Source baseline: `5b5db0e5b112e37111b42b4933af8469606337a0`.  
Evidence class: source inspection + reviewed argument + deterministic exact model controls.  
Native/paid execution: **none**.

## Purpose

MC-006 had one bounded question: whether the algebraic subset of the locked MC-1 domain has a concrete finite exact reference calculus, rather than an unnamed “exact fallback”. The answer is **yes, conditionally on an actual finite semialgebraic source description**. This is useful as a mathematical reference and falsification route; it is not evidence that every admitted machining constructor is algebraic, nor that CAD/QE is practical as a production kernel.

The machine-readable contract is `algebraic-reference-route-v1.json`. `verify.py --contract` checks its dependency bindings, denominator preservation, theorem-source inventory, local lemma DAG, open-claim guards, exact Sturm controls, and exact regularized box-cut controls.

## Hypothesis and decisive falsification

Hypothesis: a machining step whose stock, cutting solid, setup and engaged pose relation are finite Boolean combinations of polynomial sign conditions over rational/real-algebraic constants can be reduced to a first-order formula over a real closed field. Existential sweep membership and regularized material update therefore have a terminating quantifier-elimination/cell-decomposition reference route. A finite history of only such steps remains in that class.

The hypothesis is falsified for any claimed covered constructor if its true source semantics require a transcendental relation, if a denominator/sign side condition is omitted, or if exact equality can only be resolved by tolerance, iteration cap or timeout. Such a case is retained as an open obligation; the machining domain is not narrowed to rescue the algebraic route.

## Source inspection — exact results used

The programme source register's T02 was inspected beyond its abstract. The inspected copy was Saugata Basu, *Algorithms in Real Algebraic Geometry: A Survey*, arXiv:1409.1534v1 / the Purdue-hosted PDF: <https://arxiv.org/abs/1409.1534v1> and <https://www.math.purdue.edu/~sbasu/raag_survey2011_final.pdf>.

The relevant hypotheses/results actually read were:

- §1.1 defines a semialgebraic set over a real closed field by finitely many polynomial sign atoms and identifies an ordered coefficient domain as the effective input setting.
- Theorem 2.1 is the Tarski-Seidenberg quantifier-elimination statement for first-order formulas built from those polynomial sign atoms.
- Definitions 2.2–2.3 define cylindrical algebraic decomposition and `P`-invariance. Theorem 2.4 states that for every **finite** polynomial set `P ⊂ R[X1,…,Xk]` with `R` real closed, a `P`-adapted cylindrical decomposition exists and is computable; the stated arithmetic-complexity bound is doubly exponential. This is the finite-progress fact used here, not a performance promise.
- §2.2.2, Definitions 2.11–2.12, gives Thom encodings and real univariate representations for exact algebraic points. MC-006 therefore does not need binary floating point to name an irrational cell/root sample.
- Definition 3.4, Proposition 3.5 and Theorem 3.6 describe roadmap connectivity machinery and its finite arithmetic complexity under the stated algebraic/semi-algebraic input hypotheses. MC-006 treats this as a reference endpoint for later topology integration; the citation alone does **not** close PO-07.

For the task-local exact root controls, Sturm's theorem was also inspected with its interval/Sturm-series hypotheses: <https://encyclopediaofmath.org/wiki/Sturm_sequence>. The verifier square-free-reduces repeated roots before applying an exact rational Sturm sequence and refuses root endpoints rather than perturbing them.

These sources establish algorithmic existence/finite progress in their stated mathematical setting. They do not certify a chosen software package, implementation, kernel, STEP path or resource envelope.

## Effective exact language

The MC-006 reference language is deliberately narrower than the full product domain. Coefficients are rational or explicitly represented real algebraic numbers. Algebraic numbers use a square-free defining polynomial plus rational isolating interval/Thom encoding; multivariate points may use real univariate representations. Sets are finite Boolean combinations of exact polynomial sign conditions. Rational expressions are cleared only when denominator nonzero/sign conditions are proved.

MC-003's exact source profile is compatible with this language for rational quantities, rational-knot non-rational B-splines, exact rigid transforms whose normalization introduces algebraic constants, and bounded circle-arc images whose rational turn fractions induce algebraic endpoint constants. A certifying predicate may not use binary floating JSON values, a global epsilon, flush-to-zero, timeout, or an iteration cap as its truth criterion.

## Constructive route

For a covered step, the reference route is:

1. Decode the finite MC-003 source into exact rational/algebraic constants while retaining units, setup/body identity and semantic boundaries.
2. Expand stock, tool and motion into a finite semialgebraic formula. If this cannot be done without changing meaning, stop coverage at this boundary.
3. Define swept-set membership by `x ∈ S ⇔ ∃t,y: E(t) ∧ T(y) ∧ K(t,y,x)`, where engagement, tool membership and pose relation are all semialgebraic.
4. Apply effective real quantifier elimination to obtain an equivalent quantifier-free material/sweep formula. The existence of a finite route is the claim; practical cost remains separately qualified.
5. Apply the MC-002 material rule exactly: `M_next = closure(interior(M \ S))`. Interior and closure can themselves be stated in first-order real formulas and eliminated. This cannot delete a positive-volume sliver merely because it is small.
6. Build a sign-invariant finite cell decomposition for exact material/sign queries, with algebraic sample points represented exactly.
7. Use exact task-local topology controls now; carry general roadmap/cell-complex connectivity to MC-008/MC-032/MC-038 rather than pretending the citation is already a universal implementation.
8. Repeat for a finite ordered history. The remaining operation count is a trivial outer progress measure; geometry steps retain their theorem-specific finite algorithms. Durable body/lineage identity remains source semantics, not a CAD-cell or provider-topology handle.

## Coverage boundary — no domain shrinkage

The algebraic route directly covers the **semialgebraic instances** of stationary, line, polyline, rational-knot non-rational spline and finite piecewise motions; bounded circular-arc images; algebraic rigid transforms; regularized removal; empty-material transitions; and the exact small body-split controls. For mill operations made from those pieces, this gives a concrete reference route when the actual stock and cutting solid also have finite semialgebraic definitions.

Coverage is conditional for every stock/cutter category because MC-002 names physical semantic classes, not a universal exact polynomial codec for every imported stock or arbitrary form/undercut tool. Likewise, a pure spindle circle/arc can be algebraic, but a spindle/feed relation is not allowed to become independent angle coverage just to fit the calculus.

The following **general cases are deliberately not claimed by MC-006**:

- nonzero-pitch `helical_arc`;
- `timed_phase_motion`;
- `phase_synchronization`;
- generic coupled spindle/feed sweeps where angle/time/feed correlation generates a helical or other analytic relation.

Those cases flow to **MC-007**, including synchronized threading, eccentric turning and fixed-axis helical milling in their general forms. The full frozen denominator remains all 26 MC-002/MC-005 operations. No provider refusal or algebraic-route inconvenience removes an operation.

## Deterministic boundary and adversarial controls

`verify.py --contract` performs no native geometry work. It uses Python `Fraction` arithmetic only for the decisive task-local controls:

- Sturm isolation for both roots of `x²-2` with rational non-root endpoints;
- a repeated root `(x-1)²`, after exact square-free reduction;
- a tangent cutter whose contact has zero volume and leaves stock unchanged;
- a full-cross-section interior cut that yields exactly two positive-volume retained components;
- complete material removal yielding the explicit empty result;
- a `1/1,000,000`-volume sliver that must survive exactly;
- a disjoint cutter that is an exact no-op.

Adversarial mutations must be rejected if they promote this deterministic model to native evidence, enable a global epsilon, smuggle the helical operation into direct algebraic coverage, shrink the denominator, hide the MC-007 handoff, accept the still-open universal topology lemma, accept MC-B, weaken protected journal semantics, or erase the inspected theorem inventory.

These controls are intentionally small. They establish that the research contract handles equality, repeated roots, tangency, splits, empty material and positive-volume remnants without heuristic tolerances. They are not an independent full-domain material oracle; MC-010 owns that later programme work.

## Local lemma DAG and proof-obligation effect

MC-006 records seven local claims. Source-to-polynomial expansion is conditional on an actual semialgebraic constructor instance. Semialgebraic sweep QE, regularized removal and finite sign-invariant decomposition have reviewed reference routes under the inspected hypotheses. Exact algebraic sample identity and the small boundary controls are also instantiated. The final universal topology/connectivity lemma remains explicitly open.

Accordingly:

- PO-02 remains **OPEN** — the route covers only the semialgebraic sweep slice and is not the actual full sweep implementation.
- PO-03 remains **OPEN** — finite covered composition is closed, but full-domain composition requires the MC-007 branch and later integration.
- PO-04 remains **OPEN** — exact equality/root machinery is concrete, but MC-032 still owns integrated classification soundness.
- PO-05 remains **OPEN** — finite progress is established only for this slice; MC-008 integrates the complete route.
- PO-07 remains **OPEN** — small topology controls pass, but universal connectivity/body certification is not yet established.
- MC-B remains **NOT_ESTABLISHED**.

## Open obligations and downstream invalidation map

`OQ-006-01`: every admitted stock/cutter **instance** still needs a finite exact constructive representation or another semantics-preserving route. Imported stock and arbitrary form/undercut source geometry make this especially important. A downstream proof that assumes “all tools are polynomial” without resolving this is invalid.

`OQ-006-02`: MC-007 owns the general helix/timed-phase/spindle-feed route. Replacing correlation by independent full-angle coverage would invalidate sweep/material claims.

`OQ-006-03`: MC-008/MC-032/MC-038 own the universal topology/connectivity construction and its integration. CAD-cell labels alone are not durable body identity.

`OQ-006-04`: practical CAD/QE cost remains a resource concern for MC-004/MC-046/MC-048. A timeout can falsify practical suitability but cannot be reported as mathematical success.

Any later change to MC-002 domain constructors, MC-003 exact source semantics, the algebraic language, or the meaning of regularized removal invalidates the affected MC-006 lemmas and must preserve this artifact as historical evidence rather than editing it into apparent continuity.

## Protected semantics and non-claims

No Genesis-v2.1 evidence, source/audio/provenance data, historical negative evidence, canonical journal meaning, body-lineage meaning or provider result was rewritten. Positive-volume material remains material. Durable body identity remains separate from geometry cells/provider handles.

MC-006 makes **no** native-kernel correctness claim, no practical CAD/QE performance claim, no STEP/B-rep qualification, no MC-B acceptance, no MC-1 acceptance and no production/native/paid-execution authorization.

## Verification

```text
python3 research/machining-completeness/tasks/MC-006/verify.py --contract
python3 tools/mc_workflow.py verify MC-006
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The repository `mc1-static` workflow is also required on the exact PR head before merge and again on `main` after merge.
