# MC-045 — Native campaign harness, permit and resource-accounting qualification

Result: **COMPLETED_RESEARCH**. This task qualifies the static permit/admission/accounting harness and deterministic fault controls. It does **not** authorize or execute a native or paid geometry campaign and does not qualify any geometry candidate.

## Hypothesis and falsification criterion

A programme-owned harness can fail closed before dispatch when a campaign plan is not exactly bound to a reviewed permit, exceeds its resource envelope, attempts parallel repeats or hidden nested oversubscription, lacks durable attempt capture, or relies on an unverified paid tariff. The hypothesis is falsified if any such mutation is admitted, if a non-success terminal can become PASS, or if reserved resource consumption cannot be reproduced exactly from the permit and plan.

## Source and reviewed inputs

The implementation was started from `main` `25ca84ad82022e832b9198ec313178f8d1500130`. Formal task dependencies are the accepted MC-056 workflow-safety artifact and MC-009 evidence-binding artifact. MC-004 is consumed as a reviewed auxiliary qualification/resource contract; it is not added as a graph dependency.

The implementation is `campaign_harness.py`, governed by `campaign-harness-contract-v1.json`. Authority objects use canonical JSON and reject binary floating-point quantities. Plans bind the permit ID, exact source SHA, candidate configuration digest, frozen fixture-profile digest and platform ID. Commands are argv arrays; shell command strings are not authority.

## Permit admission

A permit records a programme approval authority/evidence token, exact source/configuration/profile/platform, allocated vCPUs, process/thread ceilings, job/repeat counts, timeout, memory, storage and egress caps, retention path, stop rules and the `expensive-campaign` lock. Issue existence is never approval. Placeholder approval evidence is rejected. A paid campaign requires a current verified tariff basis; guessed or inherited prices are rejected.

`NATIVE_BOUNDED` permits additionally require the caller to opt in with `--allow-native`. That flag is only a second fail-closed check; it is not approval and cannot manufacture a permit. MC-045 itself uses only the synthetic `MODEL_ONLY` self-test permit and performs no native dispatch.

## Parallelism and accounting

Repeated measurements are strictly sequential. `max_processes × threads_per_process` may not exceed allocated vCPUs, and plan limits may not exceed permit limits. Reserved vCPU consumption is computed as:

`allocated_vcpus × timeout_seconds × max_jobs × sequential_repeats`

Minutes are retained as an exact rational numerator/denominator rather than binary floating point. The deterministic control uses 4 vCPUs × 10 seconds × 1 job × 3 sequential repeats = 120 reserved vCPU-seconds = exactly 2 vCPU-minutes.

Runner wall time, process CPU time and allocated vCPUs remain distinct observations. The harness does not infer billable cost without an explicit verified provider tariff/billing basis.

## Durable attempts and fault controls

Every attempt is validated against the same source/config/profile/platform permit binding and appended to canonical UTF-8 JSONL with an `fsync` after each record. Timeout, resource exhaustion, crash and incomplete states remain first-class retained terminals and cannot be promoted to PASS.

The deterministic adversarial suite rejects:

- placeholder or missing approval authority;
- source/config/profile/platform binding drift;
- parallel repeat copies;
- nested worker oversubscription;
- timeout, memory, storage or egress over-plans;
- an unverified paid tariff;
- a missing/mismatched `expensive-campaign` lock;
- non-success terminal promotion.

It separately retains three ordered successful sequential repeats and injected TIMEOUT, RESOURCE_EXHAUSTED and CRASH attempts.

## Scope and retained limitations

This is platform/process evidence for admission, accounting and evidence retention, not native geometry evidence. It does not demonstrate candidate correctness, STEP correctness, performance on MC-RH-Q1, Windows/Linux recovery, or any MC-B through MC-F gate. Actual native execution still requires a separately approved versioned permit and the programme-wide campaign lock.

Protected historical `research/rcs-*` sources, source/audio/provenance identities, canonical-journal semantics, positive-volume semantics and durable-body/lineage semantics are untouched. MC-A remains accepted; MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`.
