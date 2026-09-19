# MC-1 adoption audit

Status: second-pass repository/workflow review of the planning adoption. Date: 19 September 2026. This is an independent-method reread by the same assistant author, **not** independent mathematical peer review or native geometry qualification.

## First complete-pass review

The adoption was checked against every stage in the user request and every section of the source plan. The result is a 14-package / 57-task graph, stable task IDs MC-001–MC-057, typed artifact-versus-capability dependencies, PO-01–PO-12 integration owners, F01–F16 family owners, explicit write/compute locks, current authority routing and a GitHub issue binding for every task.

Repairs applied before this audit include: explicit DR-0026 authority instead of silently rewriting Gate 5; candidate-independent domain/workload decisions; early output representability and consumer-access tracks; immutable historical corpus import; independent checker/oracle attacks; actual varying-Z rounded sweeps; phase-sensitive lathe ownership; singular/grouped output profile ownership; algorithm-specific split/blueprint requirement before native implementation; global expensive-campaign mutex; final held-out ownership; and a conditional handoff only after MC-1 pass.

## Independent-method backward review

Starting at MC-052 and reading dependencies backwards established:
- MC-1 requires MC-A/B/D/E/F capability gates plus final adversarial and traceability reviews; issue closure cannot substitute.
- MC-C is deliberately an early feasibility gate owned by MC-016 and feeds MC-054/MC-B. A blocker may complete the research report but cannot accept MC-C.
- MC-B is accepted before the full native implementation and after proof/sweep/candidate/output-construction routes are reviewed. MC-031–037 require its capability edge.
- MC-D consumes the complete mandatory corpus and actual composed native path. MC-E then consumes exact STEP files and an independent consumer. MC-F follows output qualification plus native scale/platform/recovery.
- MC-053 is unreachable without an MC-1 capability dependency and still does not authorize production repository creation.

The graph is acyclic; no gate owner depends on its own acceptance. MC-026's broad selection role is non-coding integration: its protocol requires later algorithm-specific work to be split before implementation if a blueprint is not reviewably bounded. MC-041, MC-044, MC-048, MC-050 and MC-052 are evidence/gate aggregators, not instructions to implement an entire engine in one task.

## Forward coverage review

Starting at the physical requirement and reading forward established owners for: domain grammar and workholding; numeric/curve sufficiency; workload/accuracy/hardware; algebraic and non-algebraic constructive routes; finite termination/certified arithmetic; independent controls and certificate attacks; all sixteen compounded fixture families; actual mill/lathe/multi-setup sweeps; six candidate roles; complete material/events/body state; analytic and nonanalytic boundary reconstruction; trim/seam/solid assembly; independent reconstructed-to-material comparison; composed history; STEP A–D and downstream continuation; native scale, platforms and recovery; held-out challenge; proof/code/certificate audit; and final traceability.

No ordinary valid operation is assigned to a permanent 'unsupported' bucket merely because a candidate cannot solve it. Missing constructive/output routes keep the relevant gate NOT_ESTABLISHED.

## Concurrency and cost review

The graph uses shared locks for authority, domain, schema, proof, fixture, profile, provider selection and workflow configuration. Expensive native qualification uses one global `expensive-campaign` lock and sequential repeats. Issue creation itself grants no execution permit.

The historical native RCS workflows now ignore MC-1 planning-only paths and workflow-definition-only edits; the dedicated `mc1-static` workflow validates this programme. A separate validator mutation-tests the impact routing. Native-relevant changes outside those planning paths continue to trigger their owning historical workflow, and future MC native tasks must add task-specific workflows/permits instead of abusing planning CI.

## Issue-set review

The live repository contains exactly one issue marker for each MC-001–MC-057 plus programme tracker #62. Every managed task issue includes objective, scope/non-goals, typed dependencies/concurrency, canonical-document links, an autonomous implementation prompt, acceptance criteria, verification, expected artifacts and blocking/stopping conditions. Stable IDs, not issue numbers, are the execution authority.

The native GitHub connector used here does not expose milestone creation, so the milestone hierarchy is represented canonically by MG-00–MG-13 in the repository graph and as grouped checklists in tracker #62. This does not affect dependency execution because typed repository edges, not GitHub milestone status, are authoritative.

## Hidden-assumption review

The plan still deliberately leaves actual research questions unresolved: effective domain language, input precision sufficiency, complete sweep/event routes, certified topology, singular engineering representation, independent Layer-D use and practical native scaling. Those are named tasks/gates, not assumptions filled by the adoption.

The 10/1/0.1 µm ladder, w/8 stress request and initial three-repeat rule remain experiment settings. Reference hardware/usable limits are owned by MC-004. Existing RCS-021 bounded counts and shared-field agreement are retained only at their historical scope. No native geometry measurement was generated during adoption.

## Final planning disposition

The workflow is complete enough for autonomous **research execution**, beginning with the evidence-ready frontier after merge. Geometry completeness itself remains NOT_ESTABLISHED. Production bootstrap remains unauthorized. Any future counterexample reopens the exact owning claim/task and preserves prior evidence instead of restarting or narrowing the programme.


## Corrections discovered during the second live workflow pass

The second live pass caught three adoption-tooling defects before PR delivery. First, the initial CI-cost patch combined GitHub `paths` and `paths-ignore` on three already-selective workflows; GitHub rejects that event-filter combination. Those three files were restored exactly to baseline, while the seventeen broad historical PR workflows retain valid MC planning-only `paths-ignore` routing. The impact validator now distinguishes these two classes and mutation-tests the invalid combination.

Second, MC-001/MC-056 task verifiers originally resolved the repository root one parent too shallow. Both were corrected and are now executed by `mc1-static`, so a structurally present but unusable verifier cannot pass adoption.

Third, the execution protocol promised managed issue reconciliation but the first helper implemented marker presence only. `mc_workflow.py sync --check/--apply` now compares deterministic managed title/body blocks, detects duplicate stable markers as a hard conflict, preserves text outside the managed block, and updates only already-bound issue records. All 57 issues were normalized to that template. The final static gate performs a live zero-drift check with read-only issue permission.
