# MC-1 task and milestone roadmap

Status: canonical execution hierarchy for MC-1. Stable task IDs are repository authority; GitHub issue numbers are navigation bindings. A closed issue does not pass a capability gate.

## Milestone hierarchy

- **MG-00 — Authority, evidence and execution safety**: 2 task(s).
- **MG-01 — Domain and numeric contract**: 4 task(s).
- **MG-02 — Constructive completeness argument**: 3 task(s).
- **MG-03 — Independent oracles and adversarial corpus**: 8 task(s).
- **MG-04 — Actual sweep and process semantics**: 7 task(s).
- **MG-05 — Candidate falsification and selection**: 7 task(s).
- **MG-06 — Early output representability**: 3 task(s).
- **MG-07 — Native material realization**: 3 task(s).
- **MG-08 — Topology and reconstruction**: 5 task(s).
- **MG-09 — Composed headless engineering journey**: 3 task(s).
- **MG-10 — Independent STEP qualification**: 3 task(s).
- **MG-11 — Native scale, platforms and recovery**: 4 task(s).
- **MG-12 — Adversarial final audit**: 4 task(s).
- **MG-13 — Decision and conditional handoff**: 2 task(s).

## Task graph

| Task | Package | Objective | Dependencies | Gate |
|---|---|---|---|---|
| **MC-001** — Authority, evidence and historical-claim reconciliation | MG-00 | Reconcile the stronger machining-completeness mandate against Genesis-v2.1 without rewriting historical evidence. | none | — |
| **MC-002** — Machining domain grammar and physical-validity contract | MG-01 | Define the supported physically realizable lathe/fixed-axis mill domain independently of solver convenience. | MC-001 (artifact) | — |
| **MC-003** — Numeric, curve, transform and encoding sufficiency audit | MG-01 | Establish exact source semantics and any versioned precision extension needed by MC-1 without changing old journal meaning. | MC-002 (artifact) | — |
| **MC-004** — Candidate-independent workload, accuracy and resource contract | MG-01 | Preregister intended machining workloads, accuracy vectors, reference hardware and usable resource envelopes without tuning them to a candidate. | MC-002 (artifact) | — |
| **MC-005** — MC-A domain-lock integration review | MG-01 | Review MC-002–004 as one domain/precision/workload contract and decide MC-A. | MC-002 (artifact), MC-003 (artifact), MC-004 (artifact), MC-056 (artifact) | MC-A |
| **MC-006** — Exact algebraic/cell reference route for covered constructors | MG-02 | Instantiate a concrete terminating exact/reference calculus for the semialgebraic subset and small topology controls. | MC-002 (artifact), MC-003 (artifact) | — |
| **MC-007** — Timed, trigonometric and phase-sensitive constructive route | MG-02 | Establish a finite semantics-preserving route for admitted motion not covered by the algebraic subset. | MC-002 (artifact), MC-003 (artifact) | — |
| **MC-008** — Termination, certified arithmetic and proof-obligation DAG | MG-02 | Integrate arithmetic escalation, event decisions, finite progress, error composition and the PO-01–12 lemma DAG into checkable research contracts. | MC-003 (artifact), MC-006 (artifact), MC-007 (artifact) | — |
| **MC-009** — Research schemas, result binding and programme verdict verifier | MG-03 | Implement versioned fixture/result/outcome/claim schemas and a programme-owned verifier that rejects stale, mismatched or incomplete evidence. | MC-001 (artifact), MC-003 (artifact) | — |
| **MC-010** — Independent exact controls and oracle-independence foundation | MG-03 | Create small independent material/sweep/topology controls that do not inherit the historical shared-field decisive mathematics. | MC-002 (artifact), MC-003 (artifact), MC-009 (artifact) | — |
| **MC-011** — Physical adversarial corpus F01–F04 | MG-03 | Construct and validate F01 jittered crossing, F02 thin web, F03 rounded XYZ remachining and F04 reoriented-stock families. | MC-002 (artifact), MC-003 (artifact), MC-010 (artifact), MC-055 (artifact) | — |
| **MC-012** — Physical adversarial corpus F05–F08 | MG-03 | Construct F05 internal passage, F06 lathe finish/parting, F07 lathe–mill–lathe and F08 accessible form/undercut families. | MC-002 (artifact), MC-003 (artifact), MC-010 (artifact), MC-055 (artifact) | — |
| **MC-013** — Physical adversarial corpus F09–F12 | MG-03 | Construct F09 phase turning, F10 many bodies, F11 singular boundary and F12 scale/precision families. | MC-002 (artifact), MC-003 (artifact), MC-010 (artifact), MC-055 (artifact) | — |
| **MC-014** — Physical adversarial corpus F13–F16 | MG-03 | Construct F13 genuine geometric growth, F14 redundant history, F15 boundary-crossing reconstruction and F16 empty/exhausted-body families. | MC-002 (artifact), MC-003 (artifact), MC-010 (artifact), MC-055 (artifact) | — |
| **MC-015** — Independent certificate checker and oracle attack suite | MG-03 | Implement/challenge certificate checking independently from candidate implementations and attack the oracle stack for common-mode errors. | MC-009 (artifact), MC-010 (artifact) | — |
| **MC-016** — Early machining-generated B-rep/STEP representability screen | MG-06 | Determine early whether difficult valid material states have a defensible conventional engineering representation strategy. | MC-002 (artifact), MC-003 (artifact), MC-010 (artifact) | MC-C |
| **MC-017** — Independent engineering-consumer access and measurement probe | MG-06 | Establish at least one genuinely independent downstream solid-consumer path and a defensible measurement/follow-on-operation method early. | MC-001 (artifact) | — |
| **MC-018** — Actual flat/corner-radius milling sweep construction | MG-04 | Implement and qualify actual finite fixed-axis milling sweeps for flat and corner-radius cutter families over admitted 3D trajectories. | MC-005 (capability), MC-010 (artifact), MC-058 (artifact) | — |
| **MC-019** — Actual rounded/ball simultaneous-XYZ milling sweeps | MG-04 | Close the historical constant-Z rounded limitation with actual varying-Z rounded/ball cutter sweeps. | MC-005 (capability), MC-010 (artifact), MC-058 (artifact) | — |
| **MC-020** — Form, nonconvex and accessible undercut sweep construction | MG-04 | Implement/qualify actual sweeps for admitted form/nonconvex/undercut cutters with validated access and cutting-region semantics. | MC-005 (capability), MC-010 (artifact), MC-058 (artifact) | — |
| **MC-021** — Lathe rotational reduction and axisymmetry admission | MG-04 | Prove and implement the exact conditions under which conventional turning may reduce to a meridian/rotational material domain. | MC-005 (capability), MC-010 (artifact), MC-058 (artifact) | — |
| **MC-022** — Phase-sensitive and synchronized lathe sweep construction | MG-04 | Implement/qualify spindle/feed-correlated turning required by the domain without replacing time correlation by independent angle coverage. | MC-005 (capability), MC-010 (artifact), MC-007 (artifact), MC-058 (artifact) | — |
| **MC-023** — Re-clamp, reorientation and multi-setup sweep composition | MG-04 | Qualify common-frame transforms and body-target semantics across repeated setups and lathe↔mill transitions. | MC-005 (capability), MC-010 (artifact), MC-058 (artifact) | — |
| **MC-024** — Exact arrangement/cell candidate falsification | MG-05 | Determine the useful coverage and decisive obstructions of exact/cell methods as general reference or fallback. | MC-006 (artifact), MC-007 (artifact), MC-010 (artifact), MC-016 (artifact) | — |
| **MC-025** — Adaptive interval/implicit candidate falsification | MG-05 | Test whether certified adaptive material with exact critical events can avoid fixed-pitch floors and infinite equality refinement. | MC-008 (artifact), MC-010 (artifact), MC-016 (artifact) | — |
| **MC-026** — Candidate selection and algorithm-specific implementation blueprints | MG-05 | Select one primary design and one genuinely independent challenger/control from evidence, then decompose the selected route into reviewable native leaf blueprints. | MC-024 (artifact), MC-025 (artifact), MC-027 (artifact), MC-028 (artifact), MC-029 (artifact), MC-030 (artifact), MC-049 (artifact) | — |
| **MC-027** — Multi-/tri-directional material candidate falsification | MG-05 | Extend/test directional material beyond height-field assumptions with multiple intervals, reorientation and certified full-3D relations. | MC-010 (artifact), MC-016 (artifact), MC-019 (artifact), MC-023 (artifact) | — |
| **MC-028** — Native mesh/Manifold Boolean candidate falsification | MG-05 | Evaluate native mesh Boolean material operations using independently constructed actual cutter sweeps, distinct from historical LevelSet sampling. | MC-010 (artifact), MC-016 (artifact), MC-018 (artifact), MC-019 (artifact), MC-020 (artifact) | — |
| **MC-029** — Sparse volume/level-set candidate falsification | MG-05 | Evaluate sparse volumetric/level-set methods under explicit resampling, refinement, topology and reconstruction contracts. | MC-010 (artifact), MC-016 (artifact), MC-018 (artifact), MC-019 (artifact), MC-020 (artifact) | — |
| **MC-030** — Native B-rep/process provider and total-dispatch design | MG-05 | Evaluate qualified native B-rep/process specializations and design total noncycling dispatch to the general route. | MC-010 (artifact), MC-016 (artifact), MC-018 (artifact), MC-019 (artifact), MC-020 (artifact), MC-021 (artifact), MC-022 (artifact), MC-023 (artifact) | — |
| **MC-031** — Native sweep-to-material evaluator integration | MG-07 | Implement the selected material evaluator over actual qualified sweeps with certified relation to nominal material. | MC-005 (capability), MC-026 (artifact), MC-018 (artifact), MC-019 (artifact), MC-020 (artifact), MC-021 (artifact), MC-022 (artifact), MC-023 (artifact) | — |
| **MC-032** — Certified classification and critical-topology event engine | MG-07 | Implement finite inside/outside/boundary, equality, root and topology-critical event decisions needed by the selected complete route. | MC-005 (capability), MC-026 (artifact), MC-008 (artifact), MC-015 (artifact) | — |
| **MC-033** — Regularized material bodies, durable lineage and finite-history state | MG-07 | Implement programme-owned body transitions and regularized material semantics across split/disappearance/remachining without kernel/private identity leakage. | MC-005 (capability), MC-026 (artifact), MC-015 (artifact) | — |
| **MC-034** — Analytic boundary recovery from machining provenance | MG-08 | Recover qualified planes/cylinders/cones/spheres/tori and other exact analytic surfaces from material/provenance without inventing geometry. | MC-038 (capability), MC-031 (artifact), MC-032 (artifact), MC-033 (artifact), MC-054 (artifact) | — |
| **MC-035** — Certified nonanalytic boundary patch extraction | MG-08 | Construct bounded nonanalytic/approximate boundary patches for the approved profile with complete relation to nominal material. | MC-038 (capability), MC-031 (artifact), MC-032 (artifact), MC-033 (artifact), MC-054 (artifact) | — |
| **MC-036** — Trim, incidence, seam and solid assembly | MG-08 | Build correct edge curves, p-curves, incidences, orientations, seams, shells and solids across analytic/approximate/provider boundaries. | MC-038 (capability), MC-032 (artifact), MC-034 (artifact), MC-035 (artifact), MC-054 (artifact) | — |
| **MC-037** — Reconstructed-solid comparison and end-to-end error certificate | MG-08 | Independently compare reconstructed engineering solids to nominal material and bind the complete source→reconstruction error budget. | MC-038 (capability), MC-015 (artifact), MC-031 (artifact), MC-032 (artifact), MC-033 (artifact), MC-034 (artifact), MC-035 (artifact), MC-036 (artifact) | — |
| **MC-038** — MC-B constructive-coverage integration decision | MG-08 | Integrate domain, proof, sweep, candidate and output-construction arguments into the reviewed constructive coverage gate before full native implementation claims. | MC-005 (capability), MC-006 (artifact), MC-007 (artifact), MC-008 (artifact), MC-016 (artifact), MC-018 (artifact), MC-019 (artifact), MC-020 (artifact), MC-021 (artifact), MC-022 (artifact), MC-023 (artifact), MC-026 (artifact), MC-054 (artifact), MC-058 (artifact) | MC-B |
| **MC-039** — Finite-history closure and provider-handoff integration | MG-09 | Demonstrate closure over finite compositions, provider transitions and repeated reconcile cycles using real selected implementations. | MC-031 (artifact), MC-032 (artifact), MC-033 (artifact), MC-034 (artifact), MC-035 (artifact), MC-036 (artifact), MC-037 (artifact) | — |
| **MC-040** — Composed headless material-to-engineering journey | MG-09 | Execute the actual research chain from canonical machining input through sweep/material/topology/reconstruction and STEP preparation. | MC-039 (artifact) | — |
| **MC-041** — MC-D mandatory-suite native engineering closure | MG-09 | Qualify the complete native material→topology→reconstruction chain on every mandatory valid MC-1 case at frozen requests. | MC-038 (capability), MC-011 (artifact), MC-012 (artifact), MC-013 (artifact), MC-014 (artifact), MC-015 (artifact), MC-040 (artifact), MC-055 (artifact) | MC-D |
| **MC-042** — Exact STEP profile implementation and Layers A–C qualification | MG-10 | Export the actual reconstructed engineering state under a pinned profile and independently verify file/read-back geometry against nominal authority. | MC-037 (artifact), MC-054 (artifact) | — |
| **MC-043** — Independent STEP consumer measurement and engineering-use continuation | MG-10 | Use the independent path from MC-017 to measure/import actual MC-1 STEP files and perform a meaningful downstream operation. | MC-017 (artifact), MC-040 (artifact), MC-042 (artifact) | — |
| **MC-044** — MC-E independent output qualification | MG-10 | Decide exact-profile Layer-D and overall independent engineering output qualification across the mandatory final fixture set. | MC-041 (capability), MC-042 (artifact), MC-043 (artifact) | MC-E |
| **MC-045** — Native campaign harness, permit and resource-accounting qualification | MG-11 | Build the bounded native campaign harness and enforce explicit permits, sequential repeats, nested-parallelism/resource accounting and durable attempt capture. | MC-056 (artifact), MC-009 (artifact) | — |
| **MC-046** — Native genuine-geometry scale ladder | MG-11 | Measure 10/100/1k/10k genuine geometry-changing sections plus separate redundant-history controls on the accepted native path. | MC-041 (capability), MC-004 (artifact), MC-045 (artifact) | — |
| **MC-047** — Windows/Linux fault, replay and derived-cache recovery qualification | MG-11 | Qualify the accepted path on pinned Windows/MSVC and Linux with crash/timeout/kill/cache-corruption/interrupted-output recovery. | MC-041 (capability), MC-042 (artifact), MC-045 (artifact) | — |
| **MC-048** — MC-F practical native qualification decision | MG-11 | Decide practical viability from the preregistered workload, native scale, platform and recovery evidence. | MC-044 (capability), MC-046 (artifact), MC-047 (artifact) | MC-F |
| **MC-049** — Candidate-blind final-challenge generator and custody freeze | MG-12 | Freeze final adversarial generators, seeds/commitments and oracle procedures before candidate selection hardens. | MC-005 (artifact), MC-009 (artifact), MC-010 (artifact), MC-011 (artifact), MC-012 (artifact), MC-013 (artifact), MC-014 (artifact), MC-015 (artifact) | — |
| **MC-050** — Adversarial proof, implementation and certificate audit | MG-12 | Challenge domain coverage, proof assumptions, implementation refinement, oracle independence, certificate trust and all skips/pending/timeouts. | MC-038 (capability), MC-041 (capability), MC-044 (capability), MC-048 (capability), MC-057 (artifact) | — |
| **MC-051** — Final traceability, invalidation and repository consistency audit | MG-12 | Verify bidirectional requirement→proof→code→fixture→run→artifact→decision traceability and repository/GitHub consistency before final decision. | MC-050 (artifact) | — |
| **MC-052** — Final MC-1 machining-completeness decision | MG-13 | Decide whether MC-1 is actually established, using gates and proof obligations rather than issue closure or scores. | MC-005 (capability), MC-038 (capability), MC-041 (capability), MC-044 (capability), MC-048 (capability), MC-050 (artifact), MC-051 (artifact) | MC-1 |
| **MC-053** — Conditional clean production handoff regeneration | MG-13 | Only after an MC-1 PASS, generate fresh versioned OpenSimachinist/MSAC handoff specifications reflecting the accepted machining-completeness evidence. | MC-052 (capability) | — |
| **MC-054** — Engineering-output profile decision for singular and grouped material | MG-06 | Resolve any product/profile change needed to represent valid singular/multi-solid/empty machining states without silently changing material meaning. | MC-005 (artifact), MC-016 (artifact), MC-017 (artifact) | — |
| **MC-055** — Immutable historical corpus import and strengthened-version map | MG-03 | Import all inherited RCS-021 and decisive prior controls by exact immutable identity, preserving old parameterizations separately from stronger MC-1 requests. | MC-001 (artifact), MC-009 (artifact) | — |
| **MC-056** — Planning/native CI impact routing and campaign safety guard | MG-00 | Prevent documentation/planning work from accidentally dispatching the historical native test catalogue while preserving fail-closed native coverage for semantic/code changes. | MC-001 (artifact) | — |
| **MC-057** — Independent challenge ownership and final held-out execution | MG-12 | Arrange honestly independent review/challenge ownership where available and execute the frozen MC-049 held-out set against the exact accepted candidate/configuration. | MC-041 (capability), MC-044 (capability), MC-048 (capability), MC-049 (artifact) | — |
| **MC-058** — Certified curve, transform and swept-volume approximation contract | MG-04 | Qualify admitted line, arc, polyline and spline trajectories and rigid transforms without replacing actual cutter sweeps by centreline fitting or silently changing saved nominal intent. | MC-003 (artifact), MC-008 (artifact), MC-010 (artifact) | — |

## Concurrency lanes

- **Definitions/proof:** MC-002–008; serialize shared domain/proof/schema writers.
- **Oracle/corpus:** MC-009–015 and MC-055; isolated family work can overlap, fixture-registry writes cannot.
- **Output feasibility:** MC-016/017/054 runs early; qualification-profile decisions serialize.
- **Sweeps/candidates:** MC-018–030 plus MC-058 may overlap only when dependency, write-set and permit constraints are satisfied; MC-058 is the shared curve/transform/swept-approximation contract for actual sweep work.
- **Native realization:** MC-031–044 consumes accepted interfaces and real predecessor artifacts; no competing authority writers.
- **Expensive qualification:** tasks carrying `expensive-campaign` never overlap; final repeats are sequential.
- **Audit/decision:** MC-049 freezes challenges before selection; MC-050/051/052 are serialized final integrity steps.

## First frontier after adoption

MC-001 and MC-056 close adoption/evidence/workflow-safety foundations. MC-002 is the next domain foundation; MC-017 can investigate consumer access independently. MC-003/004 follow reviewed domain work; MC-005 decides MC-A. MC-058 becomes evidence-ready after MC-003/008/010 and then constrains the actual sweep construction tasks. Proof/oracle/output work may consume reviewed artifacts provisionally, but capability edges remain strict.

See `research/machining-completeness/task-graph-v1.json` for the machine-readable authority and `07-EXECUTION-PROTOCOL.md` for ownership, locks, permits and idempotent reconciliation.

## MC-038 pre-gate remediation routing

The MC-038 blocker review found that MC-031/032/033 were package-order predecessors whose producing work was circularly gated on MC-B. Issue #156 corrects only that orchestration boundary: MC-031/032/033 consume the already accepted MC-A (`MC-005`) capability plus their existing artifact dependencies so they can produce pre-gate evidence. MC-B remains `NOT_ESTABLISHED`; MC-034/035/036/037 and other genuinely post-gate work retain their MC-038 capability dependency. This routing change does not close any PB-007/RB-016/proof obligation, narrow the 26-operation denominator, or authorize production/native/paid execution.
