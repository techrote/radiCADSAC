# MC-004 — Candidate-independent workload, accuracy and resource contract

Status: **COMPLETED_RESEARCH** as a reviewed qualification/preregistration artifact, subject to exact-head CI and merge. This task does **not** execute a native campaign, prove candidate correctness, establish practical scale, qualify STEP, or change MC-A.

## Purpose and falsification criterion

MC-004 fixes the qualification request before candidate evaluation. The accepted artifact is `qualification-contract-v1.json`, schema `radicadsac-mc-qualification-contract/1.0`, based on authoritative main `047e43f07cf94eda70292679c78f38c4f661dd81` and the reviewed MC-002 outcome blob `930db704e9dd29955e7af99ba793c74e0cfda325`.

The task would be falsified as complete if an admitted MC-002 operation could disappear from the denominator, if candidate results could tune workload/accuracy/resource thresholds, if T2 stopped short of the 10/100/1k/10k geometry-changing ladder, if repeated runs could be parallelized to disguise cost, if reference hardware remained candidate-selectable, or if timeout/resource refusal could be converted into success.

## Candidate-independent freeze

Before any candidate qualification, MC-004 freezes:

- the admitted-operation denominator inherited from MC-002;
- workload profile identities and deterministic workload-generation seed;
- the distinction between genuine material-changing sections and redundant/no-new-removal history;
- semantic, engineering and precision-boundary accuracy vectors;
- named primary and secondary reference hardware;
- final repeat count and sequential-repeat rule;
- latency, memory and timeout envelopes;
- the rule that timeout, resource exhaustion, pending/refusal, crash, material mismatch and invalid certificate are non-pass outcomes.

A later profile can change only prospectively through a reviewed new version. An already observed failure cannot be retroactively converted into a pass by changing the profile. Provider or candidate limitations cannot remove required cases.

## Workload contract

`T0-DECISIVE` is the cheap correctness frontier. It requires at least twelve small valid controls spanning real removal, equality/coincidence, tangency/contact, sub-tolerance positive cuts, positive-volume slivers, exact retrace/no-new-removal, whole-body removal, parting/multi-body, threading phase, eccentric turning, fixed-axis helical milling and re-clamp/cross-machine continuation.

`T1-DOMAIN` requires at least one valid fixture for every currently admitted MC-002 operation ID. Invalid physical controls remain separate and do not inflate the solved-valid denominator.

T2 is fixed as four mandatory scale cells: exactly 10, 100, 1,000 and 10,000 independently established positive-volume geometry-changing sections. Each has a separate redundant-history control with the same nominal section count. Source samples, canonical segments, journal events, adapter counters or repeated traversal are not substitutes for independently established material changes.

The candidate-blind workload generator is identified as `mc004-candidate-blind-workload-v1` with seed SHA-256 `7b5197a80c458cad264f135ef943339097285a68a201dc88250c943ac7586e74`. Materialized fixture bytes, generator revision and source hashes must be frozen before candidate execution. Candidate feedback is forbidden from changing generated cases.

## Accuracy vectors

`A-SEMANTIC` is non-compensating. Positive-volume material cannot be silently deleted or invented; durable body identity/count and explicit empty-state semantics must remain exact under the MC-002 contract; required topology events must match the independent certificate/oracle contract; invalid controls must be rejected for the correct reason.

`A-ENGINEERING` requests a maximum 5 µm two-sided boundary Hausdorff error, 5 µm reported dimensional error, 5 µrad reported angular error and `1e-6` relative volume error on the applicable engineering cells. These tolerances are measurement/comparison limits, not topology rules. They never authorize merging or deleting a positive-volume feature.

`A-PRECISION-BOUNDARY` requests 0.5 µm / 0.5 µm / 0.5 µrad bounds on selected T0/T1 precision-stress fixtures. Failure is preserved as evidence and may not turn the fixture into an exclusion.

Nominal algorithmic error and source/measurement uncertainty remain separate channels. The profile is compatible with MC-003 exact-source semantics without making MC-003 a new graph dependency for MC-004.

## Reference hardware and usable resource envelope

The primary qualification reference is **MC-RH-Q1**: AMD Ryzen 5 5600X, 6 physical cores / 12 hardware threads, 64 GiB DDR4-3200, local NVMe SSD, CPU thread cap 12, no mandatory GPU. Exact board, firmware, OS, compiler and dependency manifests are recorded when the campaign is actually executed. Faster hardware may be reported additionally but cannot silently replace the reference.

The secondary non-gating practical baseline is **MC-RH-B1**: AMD Ryzen 5 2600X, 6 physical cores / 12 hardware threads, 32 GiB DDR4-3000 and local SSD.

On MC-RH-Q1 the preregistered maximums are:

| Profile | Wall envelope | Peak RSS | Hard timeout |
|---|---:|---:|---:|
| T0-DECISIVE | 5 s per case | 2 GiB | 10 s |
| T1-DOMAIN | 30 s per case | 4 GiB | 60 s |
| T2-G10 | 10 s session | 4 GiB | 20 s |
| T2-G100 | 60 s session | 6 GiB | 120 s |
| T2-G1000 | 300 s session | 12 GiB | 600 s |
| T2-G10000 | 1,200 s session | 24 GiB | 1,800 s |

These are qualification requests, not claims that any current or future implementation already meets them. A candidate that is correct but outside the resource envelope remains outside the practical gate; the target is not weakened to obtain closure.

## Repeat, measurement and failure policy

Final required cells use three completed sequential repeats. Parallel copies cannot be used to enlarge the sample or hide wall-time/resource behaviour. Compile-once/reuse is allowed only for the exact build when valid. Nested parallelism must be bounded and reported.

Every attempt is retained, including pre-record crash, timeout and incomplete cells. Required observations include source samples, canonical segments, journal events, independently established material-changing sections, redundant-history sections, components, voids/events, representation-specific complexity counters, certificate/output size, stock/feature scale, coefficient bit length, requested precision, wall/CPU time, allocated CPUs/threads and peak RSS.

Timeout, resource exhaustion, pending/refusal, crash, material mismatch and invalid certificate are non-pass results. A smaller T2 tier cannot substitute for a larger required tier. Candidate success is never its own oracle.

## Adversarial and boundary verification

`verify.py --contract` binds the qualification denominator to the live MC-002 admitted operation set and rejects, among other things:

- candidate-specific workload or threshold overrides;
- dropped admitted operations;
- feedback-tuned fixture generation;
- reducing the 10k genuine-geometry tier to 1k;
- inflated engineering tolerances;
- treating tolerance as a feature/topology deletion rule;
- candidate-selected reference hardware;
- parallelized final repeats;
- expanding the 10k memory envelope beyond the preregistered practical target;
- timeout-as-pass;
- guessed historical provider tariffs;
- promotion of this design/preregistration artifact to native geometry evidence.

The verifier fail-closes if MC-002 changes its admitted operation set without MC-004 being reconciled.

## Open questions and preserved negative space

`OQ-004-01` leaves T3 (100k+) native stress to measured need and separate explicit authorization. It is not smuggled into MC-004 completion.

`OQ-004-02` leaves provider tariff and monetary budget to campaign-time verification. No historical or guessed price is frozen into the contract.

`DD-002-04` live/driven-tool compound semantics and `DD-002-05` multi-spindle/transfer-machine semantics remain open exactly as inherited from MC-002. MC-004 does not resolve product scope by workload design.

No native geometry, paid runner, production repository, audio/source/provenance rewrite, journal reinterpretation, body/lineage relaxation or historical Genesis-v2.1 evidence replacement occurs in this task.

## Downstream implications

MC-005 can now review MC-002, MC-003 and MC-004 as a single domain/numeric/qualification package and decide whether MC-A is genuinely established. MC-045/046 can later consume the fixed resource/repeat/scale request when native campaign authorization and prerequisite capability gates exist.

MC-A remains `NOT_ESTABLISHED` until MC-005 performs that integration review. T2 practicality is requested, not demonstrated.

## Verification

Cheap deterministic verification:

```text
python3 research/machining-completeness/tasks/MC-004/verify.py --contract
python3 tools/mc_workflow.py verify MC-004
python3 tools/validate_machining_completeness.py
```

The repository `mc1-static` workflow is updated to invoke MC-004 after integration. No native or paid campaign is required or authorized by MC-004.
