# Baseline benchmark and validation harness

Status: RCS-006 research artifact  
Date: 2026-09-16  
Result schema: `rcs-006-result/1.0`

## Purpose

RCS-006 converts the accepted adversarial corpus, OCCT audit and STEP conformance contract into a common measurement substrate. It answers a narrower question than the later robustness tracks: **what does the pinned baseline actually do on representative manufacturing workloads, under a reproducible configuration, and how do we record that without losing failures?**

The harness is deliberately disposable research infrastructure. It is not the production OpenSimachinist kernel, scheduler, API or representation architecture.

## Inputs

The harness consumes:

- `research/rcs-003/corpus-v1.json` for physical intent and parameterized manufacturing families;
- `docs/12-OCCT-8.0.1-AUDIT.md` and `research/rcs-004/audit-map.json` for the exact OCCT baseline and isolation risks;
- `research/rcs-005/conformance-v1.json` and `research/rcs-005/fixtures-v1.json` for STEP success/refusal criteria and round-trip budgets.

The baseline is fixed to Open CASCADE Technology **8.0.1**, tag `V8_0_1`, commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`.

## Hypothesis and falsification criteria

### Baseline hypothesis

**PROPOSAL:** A small process-isolated runner around stock OCCT 8.0.1 is sufficient to measure the accepted corpus reproducibly before introducing virtual tolerance, provenance-aware equivalence, deferred topology or process-specialized representations.

This hypothesis is falsified if the harness itself cannot distinguish kernel failure from orchestration failure, cannot reproduce the same concrete fixture, or cannot record enough geometry/STEP evidence for RCS-007–RCS-012 to compare alternatives.

### Determinism hypothesis

**PROPOSAL:** Repeated single-threaded/non-destructive OCCT runs should preserve stable engineering invariants for the same concrete fixture even if runtime, memory addresses, file metadata or floating formatting differ.

The tested invariant is therefore not bitwise B-rep identity. It is stable validity, body count, topology diagnostics, bounded numeric metrics and STEP read-back metrics after quantization. Divergent stable signatures are classified as `nondeterministic result` rather than hidden.

## Harness architecture

The harness has two layers.

### Campaign orchestrator

`research/rcs-006/harness/run_campaign.py` owns:

- fixture-plan loading and validation against RCS-003/RCS-005;
- parameter expansion through explicit concrete cases;
- one subprocess per attempt;
- per-attempt timeout;
- crash/exit-code capture;
- physical-oracle checks;
- RCS-005 STEP budget checks;
- repeatability signatures;
- JSONL result records and Markdown summaries.

### OCCT worker

`research/rcs-006/harness/occt_worker.cpp` owns only one attempt. It constructs the requested analytic stock/tool proxy, performs the baseline Boolean strategy, validates/measures the result and optionally writes/reads STEP.

The worker uses:

- `BRepAlgoAPI_Cut` with non-destructive mode enabled;
- `RunParallel=false` for the deterministic baseline;
- explicit per-case fuzzy tolerance, zero in the founding plan;
- `BRepCheck_Analyzer` for B-rep validity;
- `BRepGProp`, `BRepBndLib` and topology exploration for metrics;
- `STEPControl_Writer`/`STEPControl_Reader` with explicit `DESTEP_Parameters` for STEP cases.

The worker refuses an OCCT runtime whose reported version is not 8.0.1. The bootstrap independently verifies the exact source commit before building.

## Process isolation and timeout doctrine

A geometry algorithm crash or hang is a **result**, not permission to lose the rest of a campaign.

Each attempt therefore runs in a new process. The orchestrator can terminate a timed-out worker and continue. This contains:

- access violations / signals;
- uncaught kernel failures;
- allocator corruption confined to one process;
- hangs;
- process-local OCCT state contamination between attempts.

RCS-017 remains responsible for deliberately testing same-process concurrency/global-state cross-talk. RCS-006 does not infer thread safety from process-isolated success.

## Result schema

Each attempt records a top-level stable envelope plus a backend-specific worker payload. The stable envelope includes:

- plan/profile/case identifiers;
- RCS-003 source family;
- optional RCS-005 STEP fixture;
- backend/version/source revision/build profile;
- attempt number;
- failure-taxonomy classification;
- wall time;
- notes and captured stderr;
- normalized geometry and STEP observations.

The OCCT worker additionally records Boolean count, validity, topology counts, volume, area, bounding box, smallest face/edge statistics, analytic classes, runtime, RSS and STEP diagnostics.

Later backends may use a different worker implementation while retaining the attempt/result contract. The stable result schema must not grow OCCT object IDs into programme-level identity.

## Failure taxonomy

RCS-006 uses the research-method categories rather than a single pass/fail bit:

- rejected input;
- algorithm returned error/status;
- invalid topology;
- valid topology but wrong geometry;
- geometric tolerance breach;
- crash;
- hang/timeout;
- excessive runtime;
- excessive memory;
- nondeterministic result;
- STEP writer failure;
- STEP round-trip failure;
- downstream consumer failure.

`success` is added for a measured attempt that satisfies the physical oracle and applicable automated STEP gates.

A backend defect does not make the harness CI invalid. CI fails when the harness cannot build, execute representative attempts or produce structurally valid result artifacts. Negative baseline results are preserved.

## Founding experiment set

The hosted smoke profile deliberately exercises every RCS-006 minimum category:

| Requirement | Representative concrete case |
|---|---|
| Coincidence/coplanarity | `coincident-face-zero` |
| Tangency/lower-dimensional contact | `tangent-contact-zero` |
| Sliver/sub-tolerance removal | `thin-skim-1um` |
| Repeated/retraced operations | `repeated-slot-20` |
| High operation count | `repeated-slot-200` |
| Lathe | `lathe-od-finish`, `lathe-parting` |
| Mill | `mill-cut-through` |
| STEP export/re-import | parting, mill separation, analytic cylinder and inch block cases |

The broader `baseline` profile adds signed coincidence/tangency neighbors, additional skim depths, overlapping slots and metric/inch peers.

## Manufacturing proxies and limits

The founding worker deliberately uses simple analytic **material-removal envelope proxies** rather than pretending to simulate flute-level tool geometry:

- OD finishing removes an analytic annular envelope;
- parting uses a full-width slab representing the completed cut-through material set;
- milling slots use analytic prism envelopes;
- tangent/coincident cases use exact analytic placements.

These proxies are appropriate for the baseline robustness questions because the RCS-003 oracle concerns resulting material semantics, not animation of cutting edges. RCS-010/RCS-011 later test richer process-specific solver strategies.

The worker does not yet materialize every RCS-003 family. The plan is intentionally representative and parameter-sweep-capable rather than a one-off fixture pile.

## STEP integration

For applicable cases the worker:

1. measures the pre-export result;
2. transfers every selected solid as a manifold solid B-rep using the pinned AP242DIS baseline mode;
3. writes one STEP file;
4. inspects basic serialized schema/unit markers;
5. reads the file in a fresh `STEPControl_Reader`;
6. measures read-back validity/body count/bounds/volume/analytic classes;
7. reports absolute/relative deltas for the RCS-005 budgets.

This exercises the automated geometry round-trip portion of `msac-step-conformance/1.0`. It does not substitute OCCT self-readback for STEPcode or independent CAD/CAM qualification.

## Parameter sweeps

Concrete cases are declared in `benchmark-plan-v1.json`; parameters are data, not hard-coded campaign branches. New sweep members should preserve the RCS-003 family ID and change only explicit values such as:

- signed separation/overlap;
- removal depth;
- repeat/operation count;
- tool/slot width;
- fuzzy tolerance;
- export unit.

This makes later RCS-007 tolerance sweeps and RCS-010/RCS-011 process comparisons able to reuse the same orchestration/result substrate.

## Reproduction and CI

Full commands are in `research/rcs-006/README.md`.

Hosted CI builds or restores the pinned OCCT installation, compiles the worker, executes the smoke profile twice, validates emitted records and uploads the campaign artifacts. Heavier/broader campaigns use the same commands with `--profile baseline` and can run outside hosted CI without changing semantics.

## Architecture implications

**INFERENCE:** process-isolated experiment workers are a good research boundary even if production later chooses a different deployment topology. They keep crashes/hangs measurable and make backend substitution straightforward.

**INFERENCE:** the result schema, physical-oracle mapping and STEP metrics are more durable than the specific OCCT worker. RCS-007–RCS-012 should extend adapters/results rather than cloning independent benchmark conventions.

**OPEN:** baseline measurements may show that some source-family expectations need a more faithful cutter-envelope proxy. Such corrections must preserve the RCS-003 physical intent and version the concrete benchmark plan; they must not be tuned merely to make OCCT pass.
