# Native, STEP, platform and resource qualification

Status: protocol requirements; no MC-1 campaign has been executed or authorized by adoption. Owners: MC-039–050. [Formats](11-FORMAT-CONTRACTS.md), [execution](07-EXECUTION-PROTOCOL.md).

## STEP closure

Layer A is reconciled authoritative pre-export engineering state. Layer B checks actual file structure, explicit units, selected profile and full selected body payload. Layer C is fresh-process read-back and comparison. Layer D requires independent parsing plus a genuinely independent downstream engineering consumer and meaningful follow-on operation. A parser/viewer/self-read alone is not Layer-D engineering qualification.

The inherited RCS-022/027 profile remains `interoperability_unqualified` until new exact-profile evidence replaces that status. Record consumer application/kernel/version, settings, geometry-access/measurement method, dimensions/material/topology/body mapping, diagnostics and follow-on operation. Diagnose exporter, representation, consumer, adapter and oracle separately; do not relax a gate because a consumer's tessellated metrics are poor.

Test mm and inches against the same physical error requirements. The inherited numeric writer precision `0.0001` in file units is 0.1 micrometre for mm and 2.54 micrometres for inches; neither setting certifies achieved geometric error. Freeze the actual configuration and complete error chain. At least one independent engineering-consumer path must qualify; a second is preferred, not required in place of correctness.

## Campaign ladder

| Tier | Required work | Admission |
|---|---|---|
| T0 | Tiny decisive actual-sweep, equality, off-ray/3D and difficult reconstruction controls | Explicit bounded permit; discriminating oracle |
| T1 | Complete composed mandatory families, strengthened inherited cases and precision/topology boundaries | Real native reconstruction/output path and checked certificates |
| T2 | 10, 100, 1,000 and 10,000 genuinely geometry-changing sections, plus separate redundant-history controls | Lower tier correct, cost projection approved, exact workload frozen |
| T3 | 100k or larger native stress selected by measured need | Separate explicit authorization; never inferred from synthetic events |
| T4 | Locked complete qualification, Windows/MSVC and Linux, sequential repeats and independent consumer | Exact candidate/configuration and approved execution budget |

MC-004 preregisters intended machining sessions, named reference hardware, requested accuracy and usable latency/memory envelopes independently of candidate outcomes. Pilots may inform a reviewed revision prospectively, never retrospectively pass a failure. The T2 tiers are required; unavailable budget delays them, not turns a smaller tier into a pass.

### MC-004 preregistered qualification profile

The canonical machine-readable profile is `research/machining-completeness/tasks/MC-004/qualification-contract-v1.json`. It is a requirements/design artifact only: it does not authorize native or paid execution and it does not claim that any implementation meets the limits.

The candidate-independent workload generator is `mc004-candidate-blind-workload-v1`, with the fixed seed SHA-256 `7b5197a80c458cad264f135ef943339097285a68a201dc88250c943ac7586e74`. Materialized fixture bytes, generator revision and source hashes must be frozen before candidate execution. Candidate feedback may not change the generated cases. T1 includes at least one valid fixture for every admitted MC-002 operation. T2 remains exactly 10/100/1,000/10,000 independently established positive-volume material-changing sections, with a distinct redundant-history control at each size.

Three accuracy vectors are fixed. `A-SEMANTIC` is non-compensating: positive-volume material, durable body identity/count, explicit empty state and required topology transitions cannot be traded for a numerical tolerance. `A-ENGINEERING` requests at most 5 µm two-sided boundary Hausdorff error, 5 µm dimensional error, 5 µrad angular error and `1e-6` relative volume error on applicable engineering cells. `A-PRECISION-BOUNDARY` requests 0.5 µm / 0.5 µm / 0.5 µrad on selected T0/T1 stress fixtures. These tolerances never authorize deletion or merging of a positive-volume feature, and source/measurement uncertainty remains separate from nominal algorithmic error.

The primary reference hardware is `MC-RH-Q1`: AMD Ryzen 5 5600X, 6 physical cores / 12 hardware threads, 64 GiB DDR4-3200, local NVMe SSD, with a 12-thread CPU cap and no mandatory GPU. Exact board/firmware/OS/compiler/dependency pins are recorded at execution. The non-gating secondary baseline is `MC-RH-B1`: AMD Ryzen 5 2600X, 6 physical cores / 12 hardware threads, 32 GiB DDR4-3000 and local SSD. Faster hardware may be reported additionally but cannot silently replace the primary reference.

On `MC-RH-Q1`, the frozen maximums are 5 s/case and 2 GiB RSS for T0, 30 s/case and 4 GiB for T1, then session limits of 10 s/4 GiB, 60 s/6 GiB, 300 s/12 GiB and 1,200 s/24 GiB for T2-G10/G100/G1000/G10000 respectively. Hard timeouts are 10, 60, 20, 120, 600 and 1,800 seconds respectively. A correct candidate outside these limits remains outside the practical gate; the profile is not relaxed after observing it.

Final required cells use three completed sequential repeats. Parallel copies cannot be used to inflate sample count or disguise cost. Timeout, resource exhaustion, pending/refusal, crash, material mismatch and invalid certificate are non-pass states. A smaller required tier cannot substitute for a larger one. Any profile revision is prospective, versioned and reviewed; an already observed failure cannot be retroactively converted into success.

Count source samples, canonical segments, journal events, unique effective cutting regions and independently established material-changing sections separately. Also report components, voids/events, expression nodes/cells/mesh elements/B-rep faces/edges, certificate size, stock/feature scale, coefficient bit length and requested precision. An adapter counter is not independent evidence of new geometry.

## Measurements and repeat protocol

Report per-stage/end-to-end latency, wall/CPU time, actual allocated CPUs/threads, peak memory, output size, platform/compiler/arithmetic/library pins and cost basis. Preserve every attempt, including crashes before a normal record, censored timeouts and incomplete cells. Native, deterministic model and platform/process evidence stay distinct.

Use at least three completed sequential repeats per final required cell under the initial protocol; a different repeat requirement needs justification and review before execution. Do not run parallel copies to obtain a larger sample. Failure counts and all attempts remain visible; finite success never substitutes for the universal argument.

## Platform and recovery

Qualify pinned Windows/MSVC and Linux toolchains. Preserve OCCT/native isolation. Inject timeout, forced termination, crash, corrupt/stale derived cache and interrupted certificate/STEP writing. Reconstruct from unchanged nominal authority and durable pending intent anchored to the last committed revision. Unvalidated partial geometry/certificates/output cannot advance a revision. Verify child-process containment/reaping and deterministic logical results separately from timing noise. This is bounded research recovery, not a production persistence/service epic.

## Execution permit

Every expensive/native campaign needs a versioned permit recording owner/approval evidence, purpose and claim, exact source/config/input and fixture profile, platform, allocated CPUs, compiler/solver/library/process thread limits, maximum jobs and sequential repeats, timeout/memory caps, projected expected/worst consumption, current verified billing basis when applicable, storage/egress, retention location and stop rules. A permit is not inherited indefinitely by a new candidate/precision tier. No tariff or cost number may be guessed from old prices.

Worst reserved vCPU-minutes is the sum of each job's allocated vCPUs × timeout minutes; monetary projection uses the provider's actual billable unit and verified tariff, conservatively rounded. Distinguish reserved runner time from CPU time. Do not assume the smallest runner can exercise a multi-worker test. Keep nested parallelism explicitly bounded.

One active expensive campaign holds the programme-wide `expensive-campaign` lock. Repeats are sequential. Compile once/reuse exact builds when valid. Run cheap decisive controls first and stop on correctness failure before broad matrices. Budget exhaustion yields INCOMPLETE, not capability refusal-as-success. No paid dispatch, runner resize, cancellation of other work or clone job is authorized by issue existence.

### MC-045 permit-bound campaign harness

MC-045 implements the machine-checkable admission/accounting side of this contract in `research/machining-completeness/tasks/MC-045/campaign_harness.py`, with the reviewed contract in `campaign-harness-contract-v1.json`. Permit, plan and attempt authority objects use canonical JSON and reject binary floating-point values. A plan must bind the exact permit ID, source SHA, candidate configuration, frozen fixture profile and platform; shell command strings, parallel repeat copies and process/thread oversubscription are rejected.

The harness distinguishes `MODEL_ONLY` from `NATIVE_BOUNDED`. Its deterministic qualification uses only a synthetic `MODEL_ONLY` permit. A `NATIVE_BOUNDED` plan requires both a separately approved versioned permit and explicit caller opt-in; the opt-in flag is not approval and cannot create missing authority. MC-045 does not authorize native or paid execution.

Reserved vCPU time is computed exactly from allocated vCPUs × timeout × jobs × sequential repeats, while runner wall time and process CPU time stay distinct. Paid monetary accounting fails closed without a current verified tariff/billing basis. Every attempt, including TIMEOUT, RESOURCE_EXHAUSTED and CRASH, is appended to canonical JSONL with `fsync`; non-success terminals cannot become PASS. These controls qualify the harness contract only, not a geometry candidate, platform campaign, STEP result or capability gate.

## Cache, invalidation and stops

Cache keys include source/dependency commit, ABI/compiler, platform, flags, toolkits and relevant configuration. Separate build caches, disposable geometry caches and evidence. Reuse frozen evidence only for unchanged claims/inputs. Semantic, arithmetic, oracle, reconstruction or profile changes invalidate named downstream certificates and trigger affected reruns. Documentation-only changes must not rerun the historical geometry catalogue automatically, while appropriate static checks stay required.

Stop on semantic mismatch, invalid bounds/certificates, uncontrolled growth, bad runner allocation, uncontained workers, lost artifacts or exhausted budget. Record the failure before any diagnosed retry. Retain raw logs, normalized results, certificates, manifests and digests durably beyond expiring CI artifacts; verify retrieval and include hidden output directories explicitly when publishing a narrowly scoped artifact path.

## Verdict policy

A programme-owned verifier binds input/source/profile/accuracy/checker/consumer/file hashes and computes final verdicts. Adapters report observations, not authoritative success. Missing stages are NOT_EXECUTED. Preserve UNKNOWN, PENDING, TIMEOUT, RESOURCE_EXHAUSTED, INVALID_CERTIFICATE and MATERIAL_MISMATCH separately. These research statuses do not change public journal/API enums.

Every required valid nonempty case must pass material, topology, reconstruction and output checks; exact empty outcomes follow their own complete contract. Correct invalid/out-of-process controls are reported separately and never inflate the solved-valid denominator. MC-B through MC-F cannot compensate for one another.
