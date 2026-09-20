# MC-008 — Termination, certified arithmetic and proof-obligation DAG

Status: **COMPLETED_RESEARCH** — integrated research/contract artifact with explicit open proof blockers. This is not MC-B acceptance and does not establish native geometry capability.  
Issue: #70.  
Source baseline: `cd42f951191489284d3ab2aaba2cdc05c035cda9`.  
Evidence class: reviewed argument + design contract + deterministic exact controls.  
Native/paid execution: **none**.

## Purpose and bounded question

MC-008 integrates the exact-source contract from MC-003, the conditional exact semialgebraic route from MC-006, and the deliberately negative/non-universal analytic result from MC-007 into one finite, checkable proof/arithmetic contract. The task is not to invent a new universal solver or to erase MC-007's counterevidence. It asks a narrower question: can the programme make its arithmetic escalation, termination discipline, error composition and PO-01–12 dependency structure explicit enough that later tasks cannot accidentally convert an unresolved case into success?

The machine-readable authority added by this task is `termination-proof-dag-v1.json`. The shared `proof-obligations-v1.json` is reconciled to the same dependency statements while preserving its existing capability states: PO-01 remains accepted from MC-005 and PO-02 through PO-12 remain open.

Canonical context remains the [MC-1 programme](../../../../docs/machining-completeness/00-PROGRAMME.md), [constructive completeness argument](../../../../docs/machining-completeness/02-COMPLETENESS-ARGUMENT.md), and [execution protocol](../../../../docs/machining-completeness/07-EXECUTION-PROTOCOL.md).

## Dependencies and exact bindings

MC-008 consumes three artifact dependencies exactly:

| Task | Result | Bound `outcome.json` Git blob |
|---|---|---|
| MC-003 | `COMPLETED_RESEARCH` | `8f335f59f36c8761844806f9059af4a4f1671044` |
| MC-006 | `COMPLETED_RESEARCH` | `0319e00b492c57e4a11e3e78ef9a2e15ff67e52e` |
| MC-007 | `NEGATIVE_RESULT` | `8d54872292dfd9f632c79c76994a467d26eaaf9c` |

The MC-007 negative result is consumed as negative evidence. `PB-007-01` through `PB-007-04` remain explicit blockers; artifact readiness is not capability acceptance.

## Hypothesis and falsification criterion

Hypothesis: the programme can define a finite escalation discipline in which exact source semantics are retained, semialgebraic cases use MC-006, proved separated/transversal analytic cases use MC-007's bounded validated route, and every required uncovered case terminates immediately in a typed proof blocker. In parallel, PO-01 through PO-12 can be expressed as an acyclic DAG with quantified statements, premises and stable integration owners.

The hypothesis is falsified if any of the following is required to make the contract close:

- an untyped/global epsilon or binary-floating sign becomes predicate authority;
- timeout, arbitrary iteration depth, jitter, sampling density or provider cycling is counted as semantic success;
- a required operation or positive-volume/material/topology case is removed from the denominator;
- an unknown error component is silently replaced by zero or a guessed tolerance;
- numeric error is allowed to compensate for topology, material, body identity or lineage;
- PO dependencies form a cycle, an owner disappears, or an open PO/blocker is promoted without evidence;
- MC-007's tangential/multiple/singular transcendental obstruction is relabelled out of scope.

The implemented contract rejects each of these adversarial mutations.

## Arithmetic escalation contract

The escalation has four explicit terminally finite tiers.

**A0 — exact source.** Preserve MC-003's exact integer/rational/algebraic/symbolic-turn semantics and finite piece boundaries. Lost source precision is never reconstructed by guesswork.

**A1 — exact algebraic.** If the actual predicate satisfies the MC-006 semialgebraic hypotheses, dispatch to its exact QE/CAD/root route. Failure to meet those hypotheses does not license epsilon classification.

**A2 — validated directed enclosure.** For analytic cases, use MC-007 only when separation/transversality and an input-derived finite stopping or isolation witness are proved. Directed enclosures and derivative bounds remain outward and source-bound.

**A3 — fail-closed proof blocker.** If a required equality, topology or source case lacks a proved A0–A2 route, terminate with a typed blocker while retaining the case in the 26-operation denominator.

This is a total *research-status* dispatch: every branch terminates either in a certified decision under stated hypotheses or in an explicit unresolved blocker. It is not a total successful geometry decision procedure, so MC-B remains `NOT_ESTABLISHED`.

## Finite progress witnesses

Four bounded progress contracts are now explicit.

1. **Finite journal composition (`FP-008-01`).** For a finite history of length `n`, the measure is `n-i`; a successful step consumes exactly one next journal operation. The terminal states are `i=n` or an explicit blocker/refusal. Dropping or reordering an operation is not progress.
2. **MC-006 exact algebraic route (`FP-008-02`).** Termination is supplied by the inspected exact algorithm under its admitted hypotheses, not by a wall-clock or iteration cap. Resource refusal remains unsolved.
3. **MC-007 proved analytic route (`FP-008-03`).** With an input-derived finite depth/isolation witness `N`, the measure is `N-k`. Each validated refinement increments `k`; absence of such a bound does not permit indefinite subdivision.
4. **Uncovered required branch (`FP-008-04`).** Once a necessary premise is missing, zero additional refinement is required: the branch terminates immediately as a typed `PROOF_BLOCKER`.

The verifier directly challenges missing stopping bounds, zero-depth boundaries, exact final-depth exhaustion, timeout-as-pass, fixed-depth subdivision-as-proof and retry cycles.

## Certified error composition

Numeric error and discrete correctness are deliberately non-compensating.

The ordered numeric pipeline is:

`source_decode → transform → sweep_material → classification_topology → reconstruction → step_export`

For a numeric stage to contribute to a final certificate, its inherited bound and local contribution/transfer must both be known in the admitted exact/directed scalar language. Composition is monotone and outward. If a required component is unknown, the result is `UNCERTIFIED`; it is not zero, inferred from a fixture, or clipped to a requested tolerance.

Topology/connectivity, positive-volume material, and durable body identity/lineage are separate correctness obligations. A small Hausdorff or dimensional bound cannot legalize a lost bridge, deleted sliver, merged body or invented lineage.

## PO-01–12 integrated DAG

Every programme proof obligation now has an explicit quantified statement, premise list, integration owner and acyclic dependency list in both the task contract and shared proof register.

| PO | Owner | State after MC-008 | Direct dependencies |
|---|---|---|---|
| PO-01 domain fidelity | MC-005 | `ACCEPTED` | — |
| PO-02 sweep semantics | MC-031 | `OPEN` | PO-01 |
| PO-03 finite composition | MC-039 | `OPEN` | PO-01, PO-02 |
| PO-04 sound classification | MC-032 | `OPEN` | PO-01, PO-02, PO-03 |
| PO-05 finite progress | MC-038 | `OPEN` | PO-02, PO-03, PO-04 |
| PO-06 error certification | MC-037 | `OPEN` | PO-04, PO-05, PO-07, PO-09 |
| PO-07 topology/connectivity | MC-032 | `OPEN` | PO-01, PO-02, PO-03, PO-04 |
| PO-08 complete dispatch | MC-030 | `OPEN` | PO-01, PO-02, PO-03, PO-04, PO-05 |
| PO-09 engineering realization | MC-037 | `OPEN` | PO-05, PO-07, PO-08 |
| PO-10 STEP preservation | MC-044 | `OPEN` | PO-06, PO-07, PO-09 |
| PO-11 implementation refinement | MC-050 | `OPEN` | PO-02–PO-10 as applicable, plus PO-12 |
| PO-12 resource accounting | MC-048 | `OPEN` | PO-05, PO-08 |

The verifier topologically sorts the graph and adversarially injects both indirect and self cycles. PO-01's accepted evidence is preserved; no later open PO receives accepted evidence merely because its contract is now better specified.

## Propagated blockers

MC-008 does not discharge the four blockers inherited through MC-007:

- `PB-007-01` — unconditional finite exact decision for required tangential/multiple/singular transcendental events remains open;
- `PB-007-02` — unconditional constructive route for general coupled helical/spindle-feed/eccentric sweep membership remains open;
- `PB-007-03` — exact constructive source representation for every admitted imported-stock and arbitrary form/undercut cutter instance remains open;
- `PB-007-04` — universal exact topology/connectivity certification remains open.

They now point only to remaining descendants rather than to MC-008 itself. In particular, MC-038 still receives every blocker relevant to MC-B integration. The denominator remains 26.

## Boundary and adversarial controls

`verify.py --contract` performs structural and executable checks without native geometry or paid execution. It checks exact dependency blob bindings; no binary float anywhere in the certifying artifact; A0–A3 ordering; fail-closed guards; all event branches; progress witnesses; exact rational interval/error arithmetic; unknown-error propagation; zero/final refinement boundaries; both internal-lemma and PO DAG acyclicity; owner/state stability; blocker propagation; protected semantics; shared-register reconciliation; and outcome-registry bindings.

Adversarial mutations deliberately test denominator shrinkage, universal-capability promotion, global epsilon, timeout-as-success, blocker deletion, topology compensation, unknown-error zeroing, premature PO acceptance, PO-owner drift, unquantified claims, DAG cycles, native-evidence promotion and body/lineage weakening.

Verification commands:

```text
python3 research/machining-completeness/tasks/MC-008/verify.py --contract
python3 tools/mc_workflow.py verify MC-008
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The PR must also pass the exact-head `mc1-static` workflow before merge.

## Result and downstream effect

MC-008 is complete as a reviewed integration artifact because its acceptance criterion is a checkable arithmetic/termination/PO contract, not the discharge of every downstream proof obligation. Every required PO now has quantified premises, stable ownership and an acyclic dependency relation, while every unresolved required claim remains explicitly open.

No native geometry result was produced. No paid/native campaign ran. MC-B and MC-1 remain `NOT_ESTABLISHED`. Protected source/audio/provenance, canonical journal, positive-volume material, durable body/lineage and Genesis negative-evidence semantics are unchanged.

This artifact can release later **artifact-dependent** research that needs a stable proof/arithmetic contract. It cannot release any **capability-dependent** task that requires MC-B or another still-open gate.
