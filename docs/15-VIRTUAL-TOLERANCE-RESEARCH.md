# Virtual tolerance, uncertainty, and equivalence research

Status: RCS-007 research report; experiment plan and provisional interpretation  
Date: 2026-09-17  
Baseline: OCCT 8.0.1, tag `V8_0_1`, commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

## Purpose and scope

RCS-007 asks whether MSAC/OpenSimachinist should treat geometric tolerance as one enlarged epsilon or as several explicit manufacturing and numerical policy channels. The practical target is routine machining input that repeatedly creates coincidence, tangency, retracing, very small removals and long operation histories.

This report does **not** choose a production kernel representation. It compares tolerance/equivalence mechanisms using the RCS-003 physical-intent corpus and the RCS-006 pinned OCCT benchmark substrate, then produces provisional architecture input for RCS-013.

The primary danger is semantic conflation: a dimension may be acceptable within a manufacturing tolerance while a commanded positive cut is still physically meaningful; two surfaces may be close enough to classify as uncertain contact without being globally identical; preview tolerance may be much looser than export or validation tolerance. A single number cannot safely stand for all of these meanings.

## Source baseline

**SOURCE:** OCCT 8.0.1 B-rep faces carry their own tolerance alongside the underlying surface. The corresponding edge and vertex representations also carry entity tolerances, as recorded by the accepted RCS-004 audit. These local kernel tolerances are part of B-rep validity and representation, not a complete manufacturing-policy model.

Pinned source:

- `BRep_TFace.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRep/BRep_TFace.hxx
- `BRep_TEdge.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRep/BRep_TEdge.hxx
- `BRep_TVertex.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRep/BRep_TVertex.hxx

**SOURCE:** `BOPAlgo_Options` describes `FuzzyValue` as an **additional tolerance for the operation to detect touching or coinciding cases**. It is an operation option, separate from the stored entity tolerances. The same API exposes per-instance parallel control and a distinct process-global parallel mode.

Pinned source:

- `BOPAlgo_Options.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKBO/BOPAlgo/BOPAlgo_Options.hxx

**MEASURED BASELINE:** RCS-006 established a reproducible single-threaded, non-destructive OCCT 8.0.1 worker with explicit per-operation fuzzy value, process isolation, topology/volume metrics, repeatability checks and STEP round-trip evidence. That harness is reused rather than inventing a second measurement convention.

## Hypotheses and falsification criteria

### H1 — One enlarged Boolean epsilon is insufficient

**HYPOTHESIS:** increasing one operation-wide fuzzy tolerance can rescue some near-contact computations, but it cannot simultaneously preserve signed physical intent, sub-tolerance removal and unrelated nearby geometry over a broad operating range.

**Falsified if:** one fuzzy-value policy consistently preserves the RCS-003 physical oracle across coincidence, tangency, positive micro-skims, repeated passes and accumulation chains without creating new semantic errors.

### H2 — Operation-local uncertainty is safer than global equivalence

**HYPOTHESIS:** an explicit uncertainty/contact relation scoped to one operation can identify ambiguous near-contact without globally merging entities or rewriting commanded intent.

**Falsified if:** the local model either cannot make deterministic progress at practical reconciliation boundaries or produces more physical-oracle violations than the conventional baseline without compensating robustness benefit.

### H3 — Proven exact retraces may skip exact recomputation without losing intent

**HYPOTHESIS:** a repeated machining event can remain in the durable journal while an exact geometry backend skips a redundant recomputation when the same cutter/material envelope is already established in the same semantic context.

**Falsified if:** executing the repeated baseline and executing the first material-changing envelope once do not remain geometrically equivalent on the tested repeated-finishing fixtures, or if the proof condition cannot be represented without relying on transient kernel identity.

### H4 — Global quantization and blind perturbation expose useful failure modes but are not neutral semantics

**HYPOTHESIS:** fixed-grid quantization can provide a mathematically transitive equivalence relation only by introducing grid-boundary discontinuities and coordinate relocation; controlled perturbation can reveal sensitivity but cannot choose a physically correct side without semantic information.

**Falsified if:** either comparator preserves signed physical intent across the sweep without boundary or direction-dependent failures.

## Policy channels are not one epsilon

RCS-007 keeps these policy channels distinct even if an implementation later derives some from shared configuration.

| Channel | Programme meaning | Must not silently substitute for |
|---|---|---|
| Input/sampling resolution | Resolution of captured/manual trajectory or imported observations. | Manufacturing acceptance or B-rep entity tolerance. |
| Machine/control resolution | Smallest meaningful commanded/represented machine-state increment. | Numerical uncertainty or export accuracy. |
| Manufacturing tolerance | Allowed deviation of the produced engineering result from intended dimensions. | Permission to erase a commanded operation. |
| Numerical uncertainty | Bound/estimate on uncertainty introduced by computation/representation. | User intent or global entity identity. |
| Topological equivalence | Rule for when topology may be treated as the same for a stated purpose. | Mere metric proximity. |
| Contact classification | Local decision about clearance, overlap, contact or unresolved near-contact. | Durable naming or global snapping. |
| Preview tolerance | Error budget suitable for responsive visualization. | Authoritative geometry/export. |
| Export tolerance | Accuracy budget for reconciliation into conventional STEP B-rep. | Internal solver convenience. |
| Validation tolerance | Threshold used by conformance checks to accept/reject measured deviations. | Automatic modification of the geometry being validated. |

**INFERENCE:** a positive 1 µm skim can be within a later manufacturing acceptance band and still be explicit material-removal intent. RCS-003 therefore requires the solver to preserve the distinction between “commanded removal is smaller than an accuracy channel” and “no removal was intended.”

## Candidate model A — OCCT global fuzzy Boolean

This is the measured control, not the programme recommendation.

For each selected RCS-003 fixture the RCS-006 worker executes the same Boolean with a sweep of `BRepAlgoAPI_Cut::SetFuzzyValue`. It then compares material-volume change and validity with the physical oracle.

Advantages:

- already supported by the pinned kernel;
- operation-local configuration rather than a permanent programme-wide global epsilon;
- directly relevant to touching/coincident cases according to upstream documentation;
- cheap to test and useful as one backend tuning channel.

Risks:

- the value widens an algorithmic detection tolerance rather than expressing manufacturing intent;
- a single fuzzy value applies to the operation even when only one local relationship is uncertain;
- it can make a tiny positive overlap/removal indistinguishable from contact;
- successful topology does not prove physically correct geometry;
- a value that helps one scale may be excessive at another scale.

**PROPOSAL:** retain fuzzy tolerance as an explicit backend parameter/diagnostic lever, never as the sole programme tolerance model.

## Candidate model B — operation-local interval classification

Define a signed separation/contact coordinate `d` for the relation currently being classified and a local uncertainty half-width `u` derived from explicit uncertainty sources. The experiment uses a fixed research value to expose behavior; production derivation remains open.

For a material-removal boundary:

- `d < -u`: confidently overlapping; execute material removal;
- `d > +u`: confidently clear; no material interaction;
- `|d| <= u`: uncertain/contact band; preserve intent and defer/reconcile rather than globally merging the entities.

This is deliberately a **local compatibility/contact relation**, not a durable topology identity relation.

For an explicitly commanded positive skim, the command semantics remain “remove material” even when the depth lies inside a numerical uncertainty band. The geometry result may become deferred, unqualified or require a higher-confidence reconciliation path, but the system must not silently reinterpret the operation as a no-op merely because the numerical band is larger than the commanded depth.

Advantages:

- localizes uncertainty to the relationship that caused it;
- preserves signed intent outside the uncertain band;
- separates “cannot currently resolve confidently” from “these objects are the same forever”;
- permits different uncertainty bounds for different operations or representations.

Costs and risks:

- uncertain states require a reconciliation policy rather than immediate forced topology;
- the relation is not transitive and therefore cannot be used as global identity;
- provenance/semantic context is required to know which relation is being classified;
- poor uncertainty estimates merely relocate the boundary problem.

## Candidate model C — semantic replay collapse

The canonical manufacturing journal remains immutable and records every user operation, including retraced passes. Geometry execution can nevertheless collapse a redundant exact recomputation when all of these are established:

1. the operation is semantically the same material-removal envelope in the same setup/context;
2. the previous committed material state already contains that envelope result;
3. no intervening operation invalidates the proof;
4. skipping recomputation does not alter status/provenance required by the programme contract.

The RCS-007 prototype tests the geometric half of this hypothesis by comparing N repeated identical finishing cuts with the result after the first effective cut. RCS-008 owns the durable provenance/identity machinery needed to make the proof safe in a production architecture.

This model is materially different from fuzzy tolerance: it does not change coordinate equivalence or enlarge an intersection threshold. It avoids asking the Boolean kernel to solve a known semantic no-op repeatedly.

**Boundary:** collapse is not allowed merely because two transient B-rep objects happen to compare equal or lie near each other.

## Anchored quantization

A fixed global grid can define

`Q(x) = round(x / q) * q`

and treat values as equivalent when their quantized representatives are equal. Unlike the interval compatibility relation, bucket equality is reflexive, symmetric and transitive.

The cost is geometric relocation and grid-boundary discontinuity. Two coordinates only `0.02q` apart can lie on opposite sides of a half-cell boundary and become inequivalent, while two farther-apart coordinates inside one cell become identical. A positive sub-grid skim can quantize to zero and disappear despite explicit removal intent.

**INFERENCE:** anchored quantization can be valid for a deliberately defined canonical control grid or serialization channel, but it is unsuitable as the universal truth model for arbitrary manufacturing geometry.

## Controlled perturbation

Controlled perturbation evaluates an exact contact together with deterministic signed neighbors. It is useful for discovering whether a computation is structurally unstable around a degeneracy.

It is not automatically semantics-preserving. At a machining boundary, `-δ` can mean real cutter penetration while `+δ` means clearance. If those neighbors produce different material sets, choosing a perturbation direction without manufacturing context changes the problem rather than resolving it.

**PROPOSAL:** use perturbation as a diagnostic or explicitly justified local tie-breaker only when the semantic side and error bound are known. Do not introduce random jitter as a hidden robustness policy.

## Algebraic properties and failure modes

### Interval compatibility is not transitive

Let `a ~ b` mean `|a-b| <= u`. Choose:

- `a = 0`;
- `b = 0.75u`;
- `c = 1.5u`.

Then `a ~ b` and `b ~ c`, but `a !~ c`. The relation is reflexive and symmetric, but not transitive.

**INFERENCE:** taking a transitive closure of local “close enough” relationships can merge geometry across a chain whose endpoints exceed the intended uncertainty. RCS-007 therefore forbids using the local interval relation as programme-wide topological identity.

### Anchored bucket equality is transitive but discontinuous

Fixed-grid bucket equality is an equivalence relation. However, `x = 0.49q` and `y = 0.51q` are separated by only `0.02q` yet fall into adjacent rounded buckets. Moving the grid origin can change the classification without changing the physical relationship.

### Locality requirements

An equivalence/contact decision must identify at least:

- operation/revision context;
- entities/semantic boundaries being compared;
- purpose of the decision (contact classification, replay collapse, export reconciliation, etc.);
- uncertainty source and bound;
- lifetime/reconciliation boundary.

A relation established for one operation must not silently propagate to unrelated geometry.

### Deterministic replay

The same journal, policy version, backend version and explicit tolerance inputs must reproduce the same classification decisions. Random perturbation is therefore excluded from the default model. If deterministic symbolic perturbation is later used, its ordering rule and semantic effect must be versioned.

### Uncertainty accumulation

RCS-007 records two bounds for a chain of `N` operations each assigned a nominal uncertainty `u`:

- conservative correlated upper bound: `N*u`;
- root-sum-square diagnostic: `sqrt(N)*u`.

The latter is **not** accepted as a correctness bound unless independence is justified; sequential geometry errors are commonly correlated. The experiment also executes the same nested finishing envelopes shallow-to-deep and deep-to-shallow. Any final geometry divergence is direct evidence of order sensitivity that an uncertainty policy must expose rather than hide.

## Experiment design

The machine-readable plan is `research/rcs-007/experiment-plan-v1.json`.

The campaign has four measured components:

1. **OCCT fuzzy sweeps** — RCS-006 `coincident_face`, `tangent_contact` and `thin_skim` cases across signed offsets/depths and fuzzy values.
2. **Repeated finishing** — a dedicated pinned-OCCT worker applies the identical OD finishing envelope 1…N times, compared with one effective execution representing semantic replay collapse.
3. **Tolerance-accumulation chain** — nested OD finishing envelopes are applied in ascending and descending depth order; final validity/topology/volume and runtime are compared.
4. **Controlled perturbation pairs** — exact contact is compared with deterministic `±δ` neighbors for coincidence and tangency.

For every contact/skim member the campaign also evaluates operation-local interval and anchored-quantization classifications against the same physical oracle. Candidate-model failure is recorded as data rather than converted into a green result.

Hosted CI runs a tractable smoke matrix; `--profile baseline` expands the parameter sweep using the same code and result schema.

Runtime artifacts:

- `.results/rcs007-smoke/results.json` — detailed machine-readable evidence;
- `.results/rcs007-smoke/summary.md` — aggregate evidence index;
- CI artifact `rcs007-virtual-tolerance-smoke` — preserved hosted-run evidence.

## Measured results

**MEASURED RESULTS PENDING:** the branch defines the executable experiment and static evidence contract before interpretation, as required by `docs/06-RESEARCH-METHOD.md`. This section must be replaced with the successful CI artifact measurements before RCS-007 is merged.

At minimum the accepted evidence must report:

- exact fuzzy-value/offset/depth members where OCCT matches or violates the RCS-003 physical oracle;
- where the operation-local interval model improves or merely relocates a failure;
- where anchored quantization erases or changes signed intent;
- whether repeated exact finishing is geometrically equivalent to semantic replay collapse;
- whether shallow-to-deep and deep-to-shallow accumulation chains are equivalent;
- whether signed perturbation changes the material result around exact contact;
- crashes/errors/timeouts/nondeterminism rather than silently dropping them.

No architecture recommendation becomes final from the experiment definition alone.

## Export and STEP reconciliation

RCS-005 remains authoritative for successful STEP export. Internal uncertainty or deferred contact does not relax the export contract.

Before claiming STEP success, any internal virtual/local relation must be reconciled into ordinary conventional B-rep geometry whose:

- selected material bodies are explicit and preserved;
- topology is valid;
- dimensions, bounding geometry and volume satisfy the declared export/validation budgets;
- required analytic geometry is retained where mandated;
- units/scale are explicit;
- serialized/read-back and qualified interoperability gates pass.

If an uncertain relationship cannot be reconciled within those budgets without choosing materially different outcomes, export must be refused or remain unqualified rather than silently snapping one result into existence.

The manufacturing tolerance channel cannot be reused as permission for arbitrary export healing. Healing/reconciliation remains bounded and measured under the RCS-005 contract.

## Interaction with RCS-008 and RCS-009

RCS-007 deliberately does not solve durable semantic identity. The promising replay-collapse rule requires RCS-008 to define how “same cutter/material envelope in the same context” survives topology replacement without depending on OCCT handles or transient face IDs.

RCS-007 also does not choose a deferred material representation. The operation-local uncertain band creates a clear handoff question for RCS-009: which unresolved lower-dimensional contacts can remain deferred until a pass/tool-withdrawal/checkpoint/export boundary without losing useful material semantics?

Neither later issue should reinterpret the local interval relation as a transitive global equivalence relation.

## Provisional architecture recommendation

**PROPOSAL pending measured CI evidence:** do not adopt a programme-wide “virtual tolerance” number and do not construct global topology identity by transitive closure of metric closeness.

Prefer a versioned policy containing separate channels, with this tentative division of responsibility:

- kernel entity tolerances remain backend validity state;
- OCCT fuzzy tolerance remains an explicit, measured operation parameter rather than programme truth;
- numerical uncertainty feeds operation-local contact classification;
- explicit positive manufacturing commands retain their semantic sign even below a numerical uncertainty band;
- uncertain local contacts may defer/reconcile rather than globally snap;
- proven exact semantic retraces may skip redundant exact geometry computation while remaining in the canonical journal;
- global quantization is reserved for explicitly defined grids/channels, not arbitrary engineering geometry;
- controlled perturbation is diagnostic unless a deterministic semantic side and bound are established;
- STEP export always collapses internal mechanisms back to the RCS-005 conformance contract.

Confidence: **medium before runtime evidence**. This section must be updated from the hosted experiment before merge. RCS-013 may later accept, modify or reject the resulting recommendation when RCS-008–RCS-012 evidence is available.

## Open questions

**OPEN:** how should operation-local numerical uncertainty be derived from input sampling, kernel tolerances, approximation error and operation history rather than supplied as a fixed research value?

**OPEN:** which reconciliation boundaries are safe for each manufacturing process: end of engaged pass, withdrawal, setup change, explicit checkpoint or export?

**OPEN:** what minimum provenance proof is sufficient to authorize semantic replay collapse? This is carried to RCS-008.

**OPEN:** which uncertain lower-dimensional states are worth retaining instead of immediately materializing B-rep topology? This is carried to RCS-009.

**OPEN:** when a backend increases entity tolerance internally, should the programme merely record it as numerical evidence or impose an independent cap/rebuild policy before export?

**OPEN:** broader manufacturing workloads may require scale-dependent uncertainty policies; this issue intentionally tests a bounded representative corpus rather than claiming universal computational-geometry equivalence.
