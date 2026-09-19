# Autonomous execution protocol

Status: adopted operational contract. Scope: MC-1 research only. Shared specification: [programme](00-PROGRAMME.md). Task definitions and typed edges: `research/machining-completeness/task-graph-v1.json`; actual GitHub numbers: `github-map-v1.json`.

## Select and claim one task

Read current main, `AGENTS.md`, `handoffs/current-authority.json`, this protocol, task scope and referenced canonical specifications. Inspect the issue body/comments and any branch/PR bearing the stable `MC-NNN` marker. Resume an existing implementation owner; absence of commits is not abandonment. Do not create a duplicate branch, issue or competing implementation. Record exact base/head, ownership and intended write paths in the issue checkpoint.

Run `python3 tools/validate_machining_completeness.py --self-test` and `python3 tools/mc_workflow.py ready`. Readiness is based on reviewed repository artifacts and required gates, never merely GitHub closed state. Verify current-main integration and live ownership before treating a printed task as dispatchable. `ready` does not dispatch a campaign or authorize expenditure.

## Two kinds of dependency

`artifact` means a reviewed, source-bound work product is available, including an honestly documented negative finding or open-lemma register where the consumer explicitly permits provisional input. It enables exploratory reasoning/probes, not a capability claim. `capability` means the named non-compensating gate has genuinely passed with evidence. Preserve and propagate all open assumptions in dependent results.

Early proof, oracle controls, output representability and consumer-access investigations can proceed together after their required domain/precision drafts are reviewed. The whole F01–F16 corpus is not a prerequisite for the first exact output witness. Candidate falsification does not wait for the proof it challenges. Final MC-B/D/E/F acceptance still requires the actual complete evidence.

## Bound each implementation

Every task has one objective, excluded work, specific outputs and falsification/verification obligations. Before coding a later algorithm-dependent task, MC-026 must supply a reviewed blueprint naming the selected algorithm, covered constructor slice, exact functions/modules, certificate interface, decisive tests, retained open obligations and bounded execution plan. Limit a leaf PR to one coherent algorithm/interface result; if that cannot be reviewed reliably, split named child issues under the same integration owner before implementation. Do not turn a conditional task into an entire engine epic or quietly remove parent acceptance criteria.

Tasks own `research/machining-completeness/tasks/MC-NNN/` for their report, implementation, tests and outcome record. Shared interfaces/registries are integration-owned; a child supplies a proposed patch and coordinates its merge instead of racing another writer. Avoid broad formatting/refactoring of unrelated files.

## Concurrency and merge locks

Logical readiness does not imply safe simultaneous writes. Each task declares write-set and lock names. Independent reasoning and isolated task directories can run concurrently. Serialize shared domain/precision changes, certificate/schema changes, selected-provider integration, topology/reconstruction interfaces, qualification profile, authority/status registries and issue synchronization. The `programme-registry` lock belongs to the current integrator, not every contributor simultaneously.

Native permits hold the global `expensive-campaign` lock across platforms/matrix jobs. Only one expensive campaign may execute at a time; its repeated measurements are sequential. Compiler, solver, library and worker threads are jointly bounded. This policy does not authorize a new scheduler, remote service or job clone. Do not cancel another owner's work.

## Required issue checkpoint and prompt

A coding agent must state: task ID; live main/base/head and existing PR; satisfied/provisional prerequisites; exact owned paths; hypothesis and decisive counterexample; planned verification command; required permit or absence thereof; current blockers and the next bounded action. Then execute the task, not just restate the plan.

The implementation prompt in each issue is scoped by its task record and canonical documents. Follow source facts rather than inherited optimistic language. No convenient domain narrowing, oracle substitution, tolerance inflation, dropped bodies, guessed lineage, model/native substitution, mesh-wrapped STEP or timeout-as-success is allowed.

## Verification and artifacts

Each completed leaf adds `report.md`, `outcome.json` and, where executable work is claimed, a deterministic `verify.py` under its task directory. The verification entry point must support `--contract` for cheap structural/control checks and document any native invocation separately. `python3 tools/mc_workflow.py verify MC-NNN` checks the outcome structure and calls only the declared cheap contract verifier; it is not a universal geometry checker. Native stage/certificate checkers are implemented and independently challenged by their owning research tasks.

An outcome identifies source/configuration, input/profile hashes, claim/PO coverage, assumptions, actual method/evidence class, positive and negative controls, artifacts/digests, verification commands, resources/permit, review and downstream invalidations. Distinguish COMPLETED_RESEARCH, NEGATIVE_RESULT, BLOCKED and CAPABILITY_ACCEPTED. A negative investigation can be reviewable and mergeable while capability remains open. A candidate cannot self-certify the final verdict.

Keep raw failure artifacts and a durable attempt ledger, not only successful normalized rows or expiring CI uploads. Freeze measurement source separately from integration-check head; do not create a self-referential document/commit/workflow-ID loop.

## Branch, PR and integration

Work on the existing task branch or create one from reconciled main only when no owner exists. Open a PR with scope, negative findings, evidence bindings, invalidation map and commands. Planning/static checks do not imply native qualification. Native-relevant changes retain all applicable native gates; planning-only impact routing must be tested fail-closed and cannot use a skip label as proof of non-impact.

Review the final diff, exact-head checks and acceptance criteria. Do not weaken tests to accommodate runner errors. Merge only after required applicable checks pass, verify the merge on main, then close the implementation issue with its exact research outcome. Update task outcomes/gates only from evidence; generated issue metadata is a navigation aid, not the capability source of truth.

## Blockers and revisions

Record the precise blocker, affected descendants and unaffected work. Add a focused decision/research child when a missing route or external permission is discovered; preserve stable IDs and avoid duplicate owners. Permission/credential, destructive action or genuinely irreconcilable product decisions require the appropriate authority. A missing consumer license/access or native budget blocks that path, not all independent research.

A changed primitive, numeric contract, oracle, output profile or dependency version invalidates named downstream claims/certificates, even if fixtures did not change. Preserve old evidence and link supersession. Mandatory failures never disappear from the denominator except through reviewed physical/domain correction. New fixture meaning or accuracy creates a new version.

## Repeatable GitHub reconciliation

`python3 tools/mc_workflow.py sync --check` is read-only drift detection; `sync --apply` is explicit reconciliation of managed blocks for stable task markers and exact milestone titles. Search open and closed issues and all milestones first; duplicate stable IDs are a hard conflict. Preserve notes outside managed blocks, unrelated labels, assignments and closed state. Never reopen or close capability automatically. Re-running an unchanged sync must perform zero writes.

An interrupted sync retains its action ledger and actual IDs. Resume missing work rather than recreating existing objects. Serialize updates; verify actual body/milestone/graph parity after writes. Native GitHub sub-issue relationships are navigation; the typed repository graph controls execution.
