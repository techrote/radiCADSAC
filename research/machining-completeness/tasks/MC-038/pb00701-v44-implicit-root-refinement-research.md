# MC-038 / PB-007-01 — frozen V44 exact original-source implicit-root refinement

**Status:** candidate bounded deterministic-model research, 30 October 2026. **Parent:** [MC-038 / #100](https://github.com/techrote/radiCADSAC/issues/100). **Preregistered scope:** [#6514965979](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6514965979). **Exact base:** `8c4c2a0c744ea2f578905fa663dd212e49a39ce1` (merged/qualified PR #312). This file does not itself record later workflow results or claim acceptance.

## Purpose and theorem being consumed

The source is precisely `harvested:verify_pb00701_v44:ffaea08e30c9`, original source SHA-256 `d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2`, with rational original parameter `t in [0,1]` and affine phase turns `-1/8+t/16`. Historical frozen v54 remains `BLOCKED`, including the lack of a true algebraic-child analytic/derivative certificate.

PR #310 already proved **exactly one simple physical root on the complete original source**, with rational strict isolation `(9/16,37/64)`, negative left sign and positive right sign. PR #311 then replayed this complete theorem and the three exactly ordered nonphysical algebraic/rational proof cuts into four original-source proof cells with open-root counts `[0,1,0,0]`. PR #312 added an independent exact cyclotomic rational-point query consumer, which can refuse for cyclotomic orders beyond its pinned budget.

This leaf answers a *different* bounded question: can the **one already-proved implicit physical root** be enclosed in a strictly narrower rational source-coordinate interval without falsely declaring its coordinate rational or algebraic, manufacturing a V41/V47 analytic child, or running numerical sample heuristics? Yes, conditioned on a sequence of **strict exact rational enclosure sign decisions** at the bisection points. The unchanged original `pb00701_transverse_trig_interval.Span.evaluate` computes rational outward enclosures from Machin-like rational bounds for pi and Taylor-Lagrange bounds for sine/cosine. `strict_sign` accepts a sign only if the **entire** rational enclosure lies strictly to one side of zero. No IEEE binary floating-point decision is taken.

Given source continuity, a certified unique simple crossing, and certified opposite nonzero signs at the current strict rational bounds `a < b`, the intermediate-value theorem places the unique root strictly inside `(a,b)`. At `m=(a+b)/2`, a proved nonzero sign equal to the left sign replaces `a` by `m`; otherwise an equal-to-right sign replaces `b` by `m`. Both endpoints remain strict and opposite; the new interval is exactly half as wide. The procedure is fully deterministic, exact-rational and bounded to **0–12** halvings. An unresolved sign returns `RESOURCE_REFUSAL`, never a falsely narrowed truth bracket, partial solution, inferred equality or arbitrary root type.

This is a **refinement of a source-matched preexisting complete-root proof**, not a new independent complete-root theorem, and not a proof of arbitrary-root algebraicity. A strict interval enclosure does not decide whether an *unresolved* sample point is exactly zero; it refuses. The same interval engine underpins #310, so this is not an independent physical root oracle. No new root count, multiplicity, global topology or general analytic function closure is inferred.

## Exact source custody and fail-closed interface

- Direct pinned #311 atlas model Git blob: `2028684883f78ceed14ce92865810ef11409b7eb`. The atlas's `pins()` transitively verifies #310 model `5d38a42fd8e23dc7930788e2b0c080caf567e851` and the historical source/corpus, exact B-spline lowerer, interval and algebraic-coordinate producers, plus unchanged 26-operation domain and current authority.
- Direct pinned #312 point consumer Git blob: `6d1805dacdf73f003d7431416d77754635e3f950`; no mutation to #310/#311/#312 or earlier historical versions.
- A caller-supplied atlas is replayed completely by the original #311 producer, not merely shape-checked or believed by comparing local signs. The fresh original B-spline and complete single-root proof are independently reconstructed by #310 from its pinned frozen corpus.
- `refine(steps=8, supplied_atlas=None)` returns a finite complete exact rational interval trace, including each source midpoint, strict nonzero sign, exact rational trig enclosure, retained root-containing half and strict source-coordinate bracket. Steps may only be canonical Python integers in `[0,12]` (not bools, floats or strings).
- Initial/final endpoint signs and strict source bracket are checked against the source root witness and its proven monotone cell. Each exactly halved width and opposite endpoint sign is a validation invariant; a zero-inclusive midpoint enclosure is not truth.
- `attempt()` maps resource exhaustion or unknown sign to typed nontruth; `validate_report()` source-recomputes the complete requested trace and rejects forged signs, brackets, source identities or capability flags. No caller-supplied midpoint, source coefficients, child polynomial or root arithmetic is accepted.

## Adversarial regressions and verification

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v44_implicit_root_refinement.py --contract --self-test
```

The verifier checks the exact initial strict source bracket, eight point-by-point *rational enclosure* bisections (independently reading and testing the recorded rational interval endpoints), twelve bounded halvings and exact width, source/pin drift, plausible forged atlas, non-integer/invalid budgets, undecidable midpoint resource nontruth, impossible midpoint sign, full submitted-result replay and forgery, and explicit no-promotion flags. The focused Actions job must execute literal branch head with raw checkout SHA, followed by `mc1-static` and source-anchored technical review; no result is accepted until expected-head-protected merge and actual matching merged-main gates are verified. Historical failures, if any, must remain visible.

## Nonclaims and programme consequences

The method is limited to one exact frozen source with one already-certified simple crossing. It does **not** solve the general V41/V47 analytic child map or closed-child derivative theorem, does not establish an exact algebraic *physical root coordinate*, and does not replace #312's cyclotomic point-event test. It never promotes a **proof cut** into a physical event. Extending it would require explicit new source-family admission, completeness proofs, resource contracts and an independently reviewable consumer; copying this frozen-case trace is insufficient.

Historical v54 remains `BLOCKED`; PB-007-01/02/03/04, the relevant pre-gate proof obligations, MC-B and MC-1 remain OPEN/`NOT_ESTABLISHED`. No native material, topology/lineage, B-rep, conventional usable STEP, independent consumer qualification, paid native campaign, MSAC implementation or production repository work is authorized. The fixed lathe/mill 26-operation denominator, canonical journal, cutter/holder, phase/time, body identity and explicit refusal/UNCERTIFIED semantics remain unchanged.
