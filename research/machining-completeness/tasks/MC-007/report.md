# MC-007 — Timed, trigonometric and phase-sensitive constructive route

Status: **NEGATIVE_RESULT** — a finite fail-closed conditional route is established for exact source decomposition and proved separated/transversal analytic events, but an unconditional finite exact decision route for all required tangential/multiple/singular transcendental events is **not established**. No capability gate changes.  
Issue: #69.  
Source baseline: `66eb051dbd0f7ec030fbf005710582ee9d6ab36d`.  
Evidence class: source inspection + reviewed argument + deterministic exact model controls.  
Native/paid execution: **none**.

## Purpose

MC-007 owns the motion semantics that MC-006 deliberately did not algebraize: general nonzero-pitch helical motion, timed spindle/path correlation, phase synchronization, eccentric turning and other coupled spindle/feed cases. The task is not allowed to make those cases disappear merely because a preferred exact calculus does not cover them.

The bounded question was therefore whether the exact source language fixed by MC-003 supplies a finite semantics-preserving decision route for every required analytic event, or whether a precise proof boundary remains. The result is mixed and deliberately recorded as a negative research result rather than an overclaim.

The machine-readable artifact is `transcendental-route-v1.json`. `verify.py --contract` checks dependency binding, the full 26-operation denominator, shared time/path/phase correlation, the fail-closed decision boundary, propagated proof blockers, protected semantics, deterministic boundary controls and adversarial mutations.

## Hypothesis and decisive falsification

Hypothesis: MC-003's finite exact time knots and exact rational turn fractions permit every affected motion to be split into finitely many compact pieces while retaining one common time/path/phase variable. On a piece where certified enclosures prove separation or a transversal/simple crossing, a finite validated analytic route can decide the relevant event. Algebraically reducible subproblems can dispatch to MC-006 without changing semantics.

The stronger hypothesis — that this alone yields an unconditional finite exact decision procedure for every tangential, multiple-root or singular trigonometric/analytic equality required by the admitted domain — is **not established**. Any purported route whose decisive step is an epsilon sign, sampling density, arbitrary subdivision cap, timeout, jitter, or an assumption that tangency cannot occur is rejected.

## Source inspection and the obstruction

The principal external source inspected for the exact-zero issue was:

- Ventsislav Chonev, Joël Ouaknine and James Worrell, *On the Skolem Problem for Continuous Linear Dynamical Systems*, arXiv:1506.00695v2 / ICALP 2016: <https://arxiv.org/abs/1506.00695v2>.

The paper is relevant because solutions of linear ODEs with algebraic data are exponential polynomials, a well-studied analytic zero-decision setting that already contains nontrivial oscillatory behaviour. The inspected material reports the bounded Continuous Skolem problem as open unconditionally in that setting and gives a bounded decidability result subject to Schanuel's conjecture. MC-007 does not elevate that conditional result into an unconditional programme theorem.

More directly useful for implementation discipline, §2.1 describes a finite-precision zero-finding procedure using computable function values and a derivative bound. Its termination argument assumes there is no tangential zero (`f(t)=f'(t)=0`). The paper explicitly identifies tangential zeros as the difficult branch. That is exactly the distinction needed here: certified numerical enclosure can close separated/transversal cases, but repeated refinement is not itself an exact tangent/multiple-root decision procedure.

This source does **not** prove that the exact MC-007 grammar is undecidable. MC-007 therefore records a proof blocker, not an impossibility theorem. Conversely, the absence of an impossibility theorem is not permission to claim a finite exact route that has not been established.

## Exact source decomposition

MC-003 already provides the semantics needed to avoid the most dangerous approximation error. A timed phase piece has finite exact time knots; path progress, tool pose and spindle phase are tied to the same time law; phase is represented by exact turn fractions and remains available unwrapped when chronology/synchronization matters. A helical arc combines an exact circular sweep with exact axial progression.

MC-007 preserves those facts as follows:

1. split only at exact time knots, engagement boundaries and setup/context transitions;
2. retain one common exact parameter for tool path, axial feed, spindle rotation and eccentric transform;
3. never replace a synchronized history by the Cartesian product of independent path and phase coverage;
4. preserve semantic boundaries even when two neighboring pieces happen to meet geometrically;
5. preserve setup, target-body, journal and provenance identities independently from whatever analytic representation is used for the geometry query.

The decomposition is finite because the source itself is finite. This establishes finite **source decomposition**, not finite successful solution of every downstream transcendental equality.

## Conditional constructive route

For each finite analytic piece the route is:

1. decode all source quantities exactly and retain the common time/path/phase variable;
2. form the required event/membership expression without decimalizing symbolic turn semantics or uncoupling correlated variables;
3. if exact simplification proves that the query belongs to the MC-006 algebraic language, dispatch that subproblem to the MC-006 exact route;
4. otherwise evaluate outward-certified rational enclosures together with a justified derivative/transversality bound;
5. accept `SEPARATED` only when zero is excluded by enclosure;
6. accept a simple crossing only when the value enclosure/sign evidence and derivative enclosure jointly certify transversality;
7. if zero remains possible and tangency, multiplicity or singularity cannot be ruled out or exactly decided by an established finite method, terminate the research/evaluation branch with `TRANSCENDENTAL_EVENT_BLOCKER`;
8. never reinterpret that blocker as empty sweep, no-op, success, provider refusal, or permission to remove the operation from the denominator.

This is fail-closed and finite as a **decision protocol** because the unresolved branch stops with a typed blocker instead of refining indefinitely. It is not a proof of constructive completeness, because a required valid machining request may still land on that blocker.

## Boundary and adversarial controls

The task-local verifier uses only exact `Fraction` arithmetic for its decisive model controls. It checks:

- exact interpolation over finite time knots;
- retention of unwrapped phase across multiple turns;
- correlation of axial/path progress and phase through one shared parameter;
- rejection of a state that would be admitted only by independent phase × path coverage;
- exact separated-event classification;
- a simple-root/transversal classification with derivative separated from zero;
- fail-closed classification for tangency/multiple-root/singular cases where both value and derivative can contain zero;
- explicit symbolic/algebraic dispatch rather than approximate relabelling.

Adversarial mutations are rejected when they enable independent phase coverage, claim an unconditional full route, remove a proof blocker, enable global epsilon predicate authority, treat Schanuel's conjecture as an unconditional programme premise, shrink the 26-operation denominator, accept MC-B, weaken protected body/provenance semantics or promote the deterministic model to native geometry evidence.

These controls demonstrate that the research contract behaves correctly at the exact boundary. They do not provide the missing transcendental decision theorem.

## Operation coverage and no domain shrinkage

The three operation classes handed off by MC-006 remain exactly:

- `lathe_threading_synchronized`;
- `lathe_eccentric_turning`;
- `mill_thread_helix_fixed_axis`.

They remain admitted operations. The complete MC-002 denominator remains **26**. Their difficult analytic branches are not changed to optional, approximated away, or redefined as independent angle coverage.

For all three, exact finite source decomposition is available. Some instances may be algebraically reducible or certifiably separated/transversal and therefore have a finite constructive route. The general cases remain subject to `PB-007-01` and `PB-007-02` until a stronger exact analytic decision construction is established.

## Proof blockers and downstream effect

`PB-007-01` — **OPEN**: finite exact decision for tangential, multiple-root or singular events in the required bounded trigonometric/analytic predicate grammar. A refinement loop plus a timeout is not a solution.

`PB-007-02` — **OPEN**: unconditional semantics-preserving decision route for general coupled helical/spindle-feed/eccentric sweep membership outside the algebraically reducible and proved-transversal slices.

`PB-007-03` — propagated from MC-006: finite exact constructive source representation for every admitted imported-stock and arbitrary form/undercut cutter instance remains open.

`PB-007-04` — propagated downstream: universal exact topology/connectivity certification remains work for MC-008/MC-032/MC-038.

Consequently:

- PO-02 remains **OPEN** — required motion classes still have general analytic-event blockers.
- PO-03 remains **OPEN** — universal finite-composition closure cannot be claimed while a required piece can block.
- PO-04 remains **OPEN** — equality/multiple-root classification is not established for the full analytic grammar.
- PO-05 remains **OPEN** — the protocol terminates truthfully, but successful realization for every admitted request is not established.
- PO-07 remains **OPEN** — universal topology/connectivity remains downstream.
- MC-B and MC-1 remain **NOT_ESTABLISHED**.

MC-008 may consume this negative result as an artifact dependency. It must integrate and expose these blockers in its termination/arithmetic/proof-obligation DAG; it may not erase them merely because MC-007's investigation is complete.

## Protected semantics and non-claims

No Genesis-v2.1 evidence, historical negative evidence, source/audio/provenance data, canonical journal meaning, durable body/lineage meaning, or provider result is rewritten. Exact time/path/phase correlation is preserved. Positive-volume material remains material. A timeout or provider failure is never success.

MC-007 makes **no** native sweep/material correctness claim, no unconditional transcendental-decision claim, no topology-completeness claim, no practical performance claim, no STEP/B-rep qualification claim, no MC-B acceptance and no production/native/paid-execution authorization.

## Verification

```text
python3 research/machining-completeness/tasks/MC-007/verify.py --contract
python3 tools/mc_workflow.py verify MC-007
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The repository `mc1-static` workflow is required on the exact PR head before merge and again on `main` after merge.
