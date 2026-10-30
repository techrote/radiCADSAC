# SCHEDUSWARM.md — radiCADSAC v2 dispatcher policy

```yaml
scheduswarm_version: 2
status: active
hub: https://github.com/techrote/scheduswarm
queue_branch: scheduswarm/queue
coordination_ledger: https://github.com/techrote/radiCADSAC/issues/324
max_active_lanes: 3
project_concurrency_budget: 2
successors_per_lane: 1
integration_writes_parallel: false
automatic_dispatch_allowed: false
```

## Authority

Scheduswarm is execution coordination only. `AGENTS.md`, `handoffs/current-authority.json`, DR-0026, MC-1 programme/execution/roadmap documents, issue-specific proof contracts and accepted decisions remain authoritative.

Every dispatched worker must re-read applicable authority and live repository/CI/PR state before selecting work.

## Queue and completion

The dispatcher watches `scheduswarm/queue:.scheduswarm/tasks/*.md`.

Workers do **not** create scheduled-task successors. At completion they publish the project handoff, write `.scheduswarm/completions/<task_id>.json`, then write zero or one same-lane successor task envelope. Extra parallel task envelopes require the lane-admission test and free capacity.

## Limits and lane classes

Maximum active lanes: **3**. Project concurrency budget: **2**. Same-lane successor maximum: **1**.

| Lane | Purpose |
|---|---|
| proof-critical | reduce/discharge/falsify a current PB-007/MC-B obligation |
| engineering-readiness | proof-independent downstream readiness |
| adversarial | independent falsification/source challenge |
| integration | serialized programme/current-authority reconciliation |

Never run two workers on the same PB/PO obligation, historical source cases or theorem-owner write set.

## Serialized surfaces

Only integration work may intentionally update shared authority while parallel lanes are active: `handoffs/current-authority.json`, DR-0026 integration, `00-PROGRAMME.md`, `07-EXECUTION-PROTOCOL.md`, `12-ROADMAP.md`, `77-MC038-CURRENT-IMPLEMENTATION-STATE.md`, shared proof/programme registries and final MC-B/MC-1 promotion records.

## Safety gates

- MC-1 remains NOT_ESTABLISHED until actual accepted programme gates say otherwise.
- Synthetic/deterministic-model evidence is not native engineering geometry.
- Do not narrow supported operations/domain, rewrite frozen audits, promote PB-007/MC-B/MC-1, bootstrap production repos, or authorize expensive/native campaigns without separate authority.
- Preserve all 26-operation scope, STEP requirements, durable bodies, journal/topology semantics and evidence custody.
- Green CI/PRs do not themselves discharge mathematical obligations.

## Dispatch commissioning

`automatic_dispatch_allowed: false`. Start with confirmation-mode dispatch. Automatic mode requires an explicit later policy change after the local UI adapter is commissioned.

## Live ownership

Use issue #324, branches/PRs and immutable queue records. Each task must state exact issue/acceptance criterion/write set. Do not race a shared mutable current-state file.
