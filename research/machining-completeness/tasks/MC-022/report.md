# MC-022 — Phase-sensitive and synchronized lathe sweep construction

Status: **COMPLETED_RESEARCH — required timed lathe constructors now have finite source-faithful construction routes, with a bounded exact phase/feed implementation and independent F09 controls; inherited general transcendental/event blockers remain OPEN.**

Issue: #84  
Source baseline: `b01a2665ef8e5b83200260dcd0815b990544ef31`  
Native/paid execution: **none**

## Hypothesis and falsification criterion

Hypothesis: the phase-sensitive lathe slice can be constructed without replacing spindle/feed chronology by independent angular coverage if every engaged piece retains one exact source time parameter that simultaneously drives cutter state, feed and unwrapped spindle phase. Required source constructors can therefore be finite even when a later geometric membership/equality query reaches the unresolved analytic boundary inherited from MC-007.

The task is falsified if a synchronized state can be created by selecting feed and phase from different source times; if modulo-one phase erases multi-turn chronology; if exact engagement endpoints are trimmed; if eccentric turning is silently replaced by a full rotational orbit; if a tangent/multiple/singular analytic query is guessed by epsilon, angle sampling or timeout; or if the bounded model disagrees with the candidate-independent MC-013 F09 phase-turning oracle.

## Finite timed constructors

`phase_sensitive_lathe.py` implements exact-rational finite source laws over closed semantic time intervals. A `TimedSegment` carries exact `(t,r,z,phase)` endpoint values. Evaluation uses one affine source parameter for all channels and retains **unwrapped** phase.

Two required MC-022 operation families receive explicit finite routes:

- `lathe_threading_synchronized`: finite exact rational timed segments. For the bounded phase/feed radial-turning subtype, body-fixed azimuth alignment times are enumerated exactly from the unwrapped rational phase interval. Feed is evaluated at those same exact times. Multi-turn histories therefore produce a finite ordered set of exact candidate alignments rather than an independent phase×feed product.
- `lathe_eccentric_turning`: finite symbolic timed placement `base + R(2*pi*phase(t))*offset`, with exact rational unwrapped phase tied to the same source time. Quarter-turn controls are evaluated exactly with rational coordinates. General arbitrary-phase analytic predicates remain on the MC-007 certified/fail-closed route; they are not decimalized into fake exact geometry.

A `TimedProgram` is a finite ordered composition. Shared semantic boundaries remain present and must agree exactly if two closed pieces meet. Disengaged gaps remain gaps rather than being fitted over.

A zero-spindle-advance interval is not falsely converted into two endpoint alignments. If its body azimuth is continuously aligned, the isolated-alignment helper fails closed so a downstream route must preserve the complete source interval; if it is not aligned, the exact result is empty.

## Exact phase/feed controls and F09

The bounded exact membership model uses the condition that a body-fixed azimuth `theta` meets machine angle zero exactly when

```text
phase(t) + theta = integer turns
```

For an affine rational phase law with nonzero phase advance over a finite interval, the relevant integers form a finite interval and are enumerated exactly. Every resulting time is rational. Feed and axial cutter-band membership are evaluated at that same time, so a state admitted only by independent phase and feed choices is rejected.

The verifier binds the existing candidate-independent MC-013 **F09 Phase-dependent turning** corpus and oracle by Git blob identity. It compares the MC-022 implementation against F09's midpoint, same-phase/wrong-feed, exact start/end equality and signed end-neighbour witnesses. It also adds a two-turn control that must expose two distinct alignment times while retaining the difference between unwrapped phase `0` and `2` turns.

This use of F09 is supplementary independent control evidence; candidate output is not used to generate expected truth.

## Eccentric controls

The executable eccentric control deliberately avoids arbitrary floating trigonometry. With exact base `(10,20)` and offset `(2,1)`, cardinal phases produce:

```text
0 turn   -> (12,21)
1/4 turn -> (9,22)
1/2 turn -> (8,19)
3/4 turn -> (11,18)
```

An `1/8`-turn state remains a symbolic exact placement with its exact turn fraction. Attempting to promote it to an exact rational Cartesian result through the cardinal control fails closed.

This distinction is important: a **finite constructor** does not imply that every downstream transcendental equality has acquired an unconditional exact finite decision theorem.

## Event route and MC-058 transfer

MC-022 consumes the MC-007 decision boundary rather than rewriting it:

- a certified value interval excluding zero is `SEPARATED`;
- a zero-containing value interval with derivative separated from zero is `TRANSVERSAL`;
- a leaf where value and derivative can both contain zero is `TRANSCENDENTAL_EVENT_BLOCKER`.

The blocker is a typed non-success result. It is not empty sweep, no-op, successful construction, provider refusal, or permission to drop the request.

MC-058's actual finite-cutter transfer is retained verbatim:

```text
e_total = e_inherited + e_translation + rho*e_rotation + e_tool
```

`rho` covers the complete cutting region. Error channels do not reset at timed-piece boundaries, and centreline-only error is not a sweep certificate when orientation/cutter extent contributes.

## Boundary and adversarial verification

`verify.py` exercises:

- exact midpoint interpolation with shared radial/feed/phase time;
- exact threading lead-per-turn arithmetic;
- exact F09 midpoint, wrong-feed, start/end equality and signed-neighbour cases against the independent MC-013 oracle;
- multi-turn alignment enumeration with unwrapped chronology;
- reverse spindle-phase chronology;
- stationary-phase interval rejection rather than endpoint sampling;
- semantic shared-boundary continuity;
- exact cardinal eccentric placements plus rejection of non-cardinal exact-rational promotion;
- separated, transversal and unresolved analytic event states;
- the MC-058 finite-cutter error composition; and
- rejection of binary-float/bool authority values.

Contract attacks must fail if they enable independent phase coverage, erase unwrapped phase, make saved operations mutable, trim engagement boundaries, drop either required operation, substitute sampled/full-angle eccentric or threading coverage, reinterpret the analytic blocker as success, permit centreline-only certification/error reset, delete positive material, claim native geometry, close PB-007 blockers, promote MC-B, or let candidate output define the F09 expected truth.

## Proof and programme boundary

MC-022 closes the **constructor gap** for the current phase-sensitive lathe operation families: required timed constructors now have finite, inspectable, source-faithful routes and a bounded exact executable phase/feed subtype.

It does **not** discharge the stronger analytic proof obligations:

- **PB-007-01 remains OPEN** for unconditional exact decisions at required tangential, multiple-root and singular transcendental events.
- **PB-007-02 remains OPEN** for unconditional general coupled spindle/feed/eccentric sweep membership beyond algebraically reducible or certified separated/transversal slices.

Those blockers propagate to later candidate/native/integration owners rather than being hidden by this task. `PO-02`, `PO-04`, `PO-05` and `PO-06` remain OPEN. MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.

No native or paid campaign ran. Historical `research/rcs-*`, source/audio/provenance records, canonical-journal semantics, positive-volume rules and durable body/lineage semantics were not modified.

## Verification

```text
python3 research/machining-completeness/tasks/MC-022/verify.py --contract
python3 research/machining-completeness/tasks/MC-022/verify.py --self-test
python3 tools/mc_workflow.py verify MC-022
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```
