# AB-001 — Authenticated dependency closure for reusable mathematical certificates

Status: **Research model / independently falsifiable hypothesis**. 9 November 2026. No native implementation, gameplay change, MC-1 gate admission or claimed original theorem.

## Frozen review baseline

- radiCADSAC `main=48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; `handoffs/current-authority.json` says `MC-1 NOT_ESTABLISHED`, `production_authorized=false`; historical 121/20/30/50 and 26 operations unchanged.
- CyberSand `main=d4b18e7f06839b35c8f6a66195206da0f33c5fa3` (9 Nov, 21:32 UTC); #542 merged; no production edits in this research branch. Its liquid family policy admits immutable per-World/per-material family, NOT dynamic per-cell transitions. PressureFlow gas heads, Rapier and ballistic state are potentially nonlocal external inputs.
- A1 Draft [#470](https://github.com/techrote/radiCADSAC/pull/470) `4b8be57cb6436f42a5614cd51f89c280752c99ad`: classical Gelfond–Schneider/cyclotomic algebraic-time point classifier. A3 [review](https://github.com/techrote/radiCADSAC/pull/470#pullrequestreview-5833060107) identifies zero-rate continuum and direct-Source shape/receipt defects; HOLD. No global event coverage.
- A2 Draft [#471](https://github.com/techrote/radiCADSAC/pull/471) `706a102463a3054959f93a241c43c1732279dfbb`: rational-time local cyclotomic moment valuation and side germ. A3 [review](https://github.com/techrote/radiCADSAC/pull/471#pullrequestreview-5833085453): conditional mathematical GO, input-string preparse resource/qualification HOLD; no global root isolation.
- #397 owns current MC-038 main integration. [#453](https://github.com/techrote/radiCADSAC/pull/453) is a restricted complete H0/H1/H2 **simple-root** event partition with typed tangency/knot-root refusals. [#462](https://github.com/techrote/radiCADSAC/pull/462) establishes a conditional composite B-spline knot/reparameterisation result on a non-main parent. Neither establishes arbitrary topology or full machining completeness.
- B1 initial [#324 preregistration](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6752064357): Bernstein no-interior-root and source-local update contract, no independently reviewed publication at this checkpoint. B2/B3/B4 not independently qualified at checkpoint; no CyberSand runtime speedup claim.

## Claim AB-001 (classical deterministic dependency lemma)

Let S and S' be complete immutable snapshots of a declared state domain X, and let a certificate verifier/result function f_i be deterministic, with fixed semantics/policy key K_i. Assume a declared finite dependency set D_i is *complete*: for every admissible state pair agreeing at all locations in D_i, f_i(S,K_i)=f_i(S',K_i). If S and S' agree on D_i, and K_i agrees, an authenticated previously checked f_i(S,K_i) is reusable for S'.

**Proof.** The antecedent is precisely the stated dependency-completeness property; substitute equality on D_i. The difficulty is *proving D_i complete*, not the trivial reuse implication. This is an established dependency-tracking result, not a newly discovered theorem.

### Required scope for an analytic event certificate

- Raw source identity and its normalized effective Fourier expression must remain separately authenticated; dropping dead `h=0` sine modes cannot permit raw-source custody forgery.
- Include exact rational coefficients, active channel count, phase rate and offset, source coordinate/affine orientation, polynomial span, genuine knot/control vectors, algorithm/schema version, and claimed resource/refusal policy.
- Local point certificates (A1/A2) do not imply a whole-interval sign partition. B1 C1's same-sign Bernstein vector condition is sufficient for strict interior sign because every Bernstein basis element is strictly positive for 0<u<1; identity-zero spans and exact endpoints must still be classified and joined correctly.
- B1 C2 (one-piece update => at most two adjacent seams rechecked) is conditional on unchanged partition indexing, shared global parameters, exact neighbouring source custody and absence of cross-piece/nonlocal dependencies. Affine global reparameterisation is not a one-piece edit.

### Required scope for a CyberSand solver result

- The complete dependency closure must include authoritative cells and hidden sidecars, material/variant policy, gas topology/heads and pressure, moving Rapier bodies/contact, ballistic parcels, scheduled/external transactions, source/sink events, phase/worker barriers, mutation/epoch identity, and any RNG if applicable.
- If a dependency is omitted, unknown, computed globally, or dynamically changes identity, **UNKNOWN => invalidate and recompute**; local radius alone is insufficient for shared gas/pressure or global actor interactions.
- A single step's certificate is not a multi-step guarantee. For bounded-radius synchronous phases the affected set must be propagated through successive dependency cones; mixed solver/actor and nonlocal phases need explicit additional dependency edges.
- Skipping region evaluation requires a stronger *stasis/effect* certificate that a full step would leave all authoritative outputs and emitted side effects equal, not only a memoized diagnostic equal. A stale hash or a returning-to-same-visible-value ABA mutation is not enough if history, receipts, impulses or side effects are observable.
- Strict engineering performance admission must measure certificate creation/invalidation cost as well as saved work, actual worker participation and identical-law state/parity. No speedup inferred from the toy model.

## Deterministic falsifiers

`python3 -m unittest -v toy_dependency_oracle.py` (Python stdlib; isolated from production) executes four controls: (1) exhaustively proves correct reuse for 64 6-cell binary states times six one-cell mutations under a declared radius-one rule; (2) a far-away mutation alters a global pressure-like derived field while local D_i would wrongly authorize reuse; (3) two local ticks transmit influence farther than one-cell halo; (4) ABA restores visible state but changes accumulated events. These are illustrative counterexamples to *overbroad* locality, not validations of CyberSand's actual solver.

## Independent prior art and novelty boundary

- Acar, Blelloch, Harper, *Adaptive Functional Programming*, TOPLAS 2006, DOI [10.1145/1186632.1186634](https://doi.org/10.1145/1186632.1186634): dynamic dependence graphs and correctness of change propagation.
- Acar, Blume, Donham, *A Consistent Semantics of Self-Adjusting Computation*, JFP 2013, DOI [10.1017/S0956796813000099](https://doi.org/10.1017/S0956796813000099): mutation-aware self-adjusting semantics.
- Neither `AB-001` nor B1's provisional Bernstein proposition should be reported as new mathematics. A publishable advance would need a genuinely new sound and efficient typed cross-solver dependency contract, or substantial new mathematics with independent novelty review.

## Actionable handoff

1. **A1** repair direct `Source` validation/zero-phase continuum, rerun *new module's exact-head tests*, and request independent checker re-review; hosted umbrella 17/17 checks alone are not module-specific coverage.
2. **A2** bound rational string length *before* Fraction parsing, rerun exact-head germ tests and independent new-head source challenge; keep rational-time restrictions explicit.
3. **B1** independently verify C1 Bernstein/germ proof with zero endpoint, identity intervals, forged raw source and changed shared time-map; only then consider research-only merge.
4. **B2/B3** treat pressure compartments/actor impulses as potentially nonlocal dependency edges and ownership/epoch changes as invalidators. Require an exact full-recompute oracle before proposing any skipped tick.
5. **B4** distinguish exact-law parity and measured native tick improvement from synthetic cache hit counts; report negative overhead results.

**Disposition: RESEARCH-ONLY HOLD for production.** No MC-B/MC-1 change, no historical corpus/gate promotion, no default physics changes, no main merge authorization.
