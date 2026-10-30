# SCHEDUSWARM.md — radiCADSAC task-lane policy

```yaml
scheduswarm_version: 1
status: active
hub: https://github.com/techrote/scheduswarm
coordination_ledger: https://github.com/techrote/radiCADSAC/issues/324
max_active_lanes: 3
project_concurrency_budget: 2
successors_per_lane: 1
integration_writes_parallel: false
```

## Authority

Scheduswarm is execution coordination only. `AGENTS.md`, `handoffs/current-authority.json`, DR-0026, MC-1 programme/execution/roadmap documents, issue-specific proof contracts and accepted decision records remain authoritative.

Every lane must re-read the relevant authority and live repository/CI/PR state before selecting work.

## Limits

**Maximum active lanes = 3.** Up to three logical chains may exist, including waiting/scheduled lanes.

**Project concurrency budget = 2.** At most two radiCADSAC lanes should intentionally execute or be launched in the same coordination window. A third lane waits/staggers.

These are deliberately different: lane count limits coordination complexity; concurrency limits simultaneous proof/source/CI/write pressure.

## Lane classes

| Lane class | Purpose | Typical ownership |
|---|---|---|
| proof-critical | reduce/discharge/falsify a current PB-007/MC-B proof obligation | one bounded proof/source case family |
| engineering-readiness | proof-independent downstream harness/readiness work | non-overlapping source/tests/docs |
| adversarial | independent falsification/source-bound challenge outside current proof owner | isolated fixtures/analysis |
| integration | serialized programme/current-authority/status reconciliation | shared authority surfaces |

There must never be two workers claiming the same PB/PO obligation, historical source cases or theorem owner/write set.

## Serialized surfaces

Only the integration owner may intentionally update shared authority while multiple lanes are active:

- `handoffs/current-authority.json`;
- DR-0026 status/decision integration;
- `docs/machining-completeness/00-PROGRAMME.md`;
- `07-EXECUTION-PROTOCOL.md`;
- `12-ROADMAP.md`;
- `77-MC038-CURRENT-IMPLEMENTATION-STATE.md`;
- shared proof/programme registries and final MC-B/MC-1 promotion records.

Proof and readiness lanes may prepare isolated proposals but must not race these surfaces.

## Safety gates

- MC-1 remains NOT_ESTABLISHED until the actual accepted programme gates say otherwise.
- Do not treat synthetic/deterministic-model evidence as native engineering geometry.
- Do not narrow supported operations/domain, rewrite frozen audits, promote PB-007/MC-B/MC-1, bootstrap production repos, or authorize expensive/native campaigns without their separate authority.
- Preserve all 26 operation scope, STEP requirements, durable bodies, journal/topology semantics and source/evidence custody.
- A green test/PR does not by itself discharge a mathematical proof obligation.

## Live ownership and successor discipline

Use issue #324 comments plus branches/PRs as append-only ownership leases. State lane/class, exact PB/issue or downstream criterion, historical cases when relevant, branch/PR/write set, prerequisite gates and successor ID.

A lane creates exactly one successor only when substantive dependency-ready work remains. If its next step depends on another active lane, it waits/stops rather than repeatedly polling. A new parallel lane requires non-overlap and free capacity.

Every run reports exact main/branch/PR SHAs, before/after proof census where applicable, accepted/refused claims, exact CI/evidence, retained failures, blocked dependencies and successor/stop disposition.
