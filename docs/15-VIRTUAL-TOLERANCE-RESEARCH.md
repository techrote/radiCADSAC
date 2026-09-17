# Virtual tolerance, uncertainty, and equivalence research

Status: RCS-007 measured research output  
Date: 2026-09-17  
Baseline: OCCT 8.0.1, tag `V8_0_1`, commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

## Purpose and scope

RCS-007 tests whether MSAC/OpenSimachinist should handle difficult near-geometry through one enlarged epsilon or through explicit, scoped manufacturing/numerical policies. The fixtures target routine machining situations: coincidence, tangency, retracing, tiny positive removals and long operation histories.

The work reuses the RCS-003 physical-intent corpus and the executable RCS-006 OCCT baseline. It does not select a production representation; it provides evidence and a provisional policy for RCS-008/RCS-009 and later RCS-013 synthesis.

## Source baseline

**SOURCE:** OCCT B-rep faces, edges and vertices carry entity tolerances. Those tolerances are representation/validity state, not a complete manufacturing-tolerance model.

Pinned sources:

- `BRep_TFace.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRep/BRep_TFace.hxx
- `BRep_TEdge.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRep/BRep_TEdge.hxx
- `BRep_TVertex.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingData/TKBRep/BRep/BRep_TVertex.hxx

**SOURCE:** `BOPAlgo_Options` defines `FuzzyValue` as an **additional tolerance for the operation to detect touching or coinciding cases**. It is an algorithm option distinct from stored B-rep entity tolerances.

- `BOPAlgo_Options.hxx`: https://github.com/Open-Cascade-SAS/OCCT/blob/b8f597c677811d1f9f4d8a97f5ae2825c0353a42/src/ModelingAlgorithms/TKBO/BOPAlgo/BOPAlgo_Options.hxx

**MEASURED BASELINE:** RCS-006 supplies the exact OCCT worker used here: non-destructive Booleans, `RunParallel=false`, explicit fuzzy value, process isolation, geometry metrics and pinned dependency identity.

## Hypotheses and falsification criteria

### H1 — One enlarged Boolean epsilon is insufficient

**HYPOTHESIS:** one operation-wide fuzzy tolerance cannot preserve signed physical intent across coincidence, tangency, micro-removal and long histories.

**Falsification criterion:** a single fuzzy policy must preserve the RCS-003 physical oracle across the tested families without introducing semantic loss or order-dependent final material.

**RESULT:** not falsified. `0.0001 mm` fuzzy tolerance produced four physical-oracle mismatches and order-dependent material in the 100-step accumulation chain.

### H2 — Operation-local uncertainty is safer than global equivalence

**HYPOTHESIS:** a bounded, operation-local contact relation can avoid definitive wrong answers by deferring uncertain contact rather than globally merging nearby geometry.

**Falsification criterion:** decisive classifications outside the uncertainty band materially violate the physical oracle, or the model cannot retain signed intent inside the band.

**RESULT:** not falsified on the smoke corpus. There were 12 explicit uncertain-contact deferrals, zero decisive local-classification mismatches, and all positive skim commands retained removal intent. The cost is relocated work: deferral requires later reconciliation and is not itself a geometry solution.

### H3 — Proven exact retraces may skip redundant exact recomputation

**HYPOTHESIS:** journal events can remain preserved while redundant exact geometry work is skipped when the same material-removal envelope is already established.

**Falsification criterion:** N repeated finishing passes differ geometrically from the one-effective-pass reference.

**RESULT:** not falsified in six smoke records spanning repeat counts 1, 10 and 100 at fuzzy values `0` and `0.0001 mm`; all were equivalent in validity, solid/face/edge counts and volume within the experiment budget.

### H4 — Quantization and perturbation are not neutral general solutions

**HYPOTHESIS:** fixed-grid equivalence causes grid aliasing/intent loss, while perturbation can choose physically different sides of a machining boundary.

**RESULT:** supported. The `0.0001 mm` grid erased the `0.000001 mm` positive skim, and zero-fuzzy `±0.0001 mm` perturbations around both coincidence and tangency produced different material semantics.

## Policy channels are not one epsilon

The programme must keep these channels conceptually distinct:

| Channel | Meaning | Must not silently become |
|---|---|---|
| Input/sampling resolution | Resolution of captured/imported trajectory. | Manufacturing tolerance. |
| Machine/control resolution | Smallest meaningful commanded machine-state increment. | Numerical uncertainty. |
| Manufacturing tolerance | Allowed deviation of produced engineering result. | Permission to erase a commanded cut. |
| Numerical uncertainty | Bound/estimate from computation/representation. | User intent or identity. |
| Topological equivalence | Purpose-specific rule for topology sameness. | Mere metric proximity. |
| Contact classification | Local clearance/overlap/contact/unresolved decision. | Durable naming. |
| Preview tolerance | Interactive visualization error budget. | Authoritative geometry. |
| Export tolerance | Accuracy budget for STEP reconciliation. | Solver convenience. |
| Validation tolerance | Acceptance threshold used by conformance checks. | Geometry modification rule. |

**MEASURED/INFERENCE:** a positive cut can be far smaller than a backend fuzzy or manufacturing-acceptance value and still carry explicit removal intent. The smoke test demonstrated this directly at `0.000001 mm` depth.

## Candidate model A — OCCT global fuzzy Boolean

The measured control uses `BRepAlgoAPI_Cut::SetFuzzyValue` on otherwise identical operations.

The smoke profile executed 26 backend sweep attempts with zero worker failures. With fuzzy `0`, the selected signed contact and skim members matched the physical oracle. With fuzzy `0.0001 mm`, four real material changes were silently lost while the resulting B-reps remained valid one-solid shapes:

| Fixture | Physical member | Fuzzy | Expected | Measured removal |
|---|---:|---:|---|---:|
| Coincidence | `-0.0001 mm` penetration | `0.0001 mm` | removal | approximately `0 mm³` |
| Tangency | `-0.0001 mm` penetration | `0.0001 mm` | removal | `0 mm³` |
| Positive skim | `0.000001 mm` depth | `0.0001 mm` | removal | `0 mm³` |
| Positive skim | `0.0001 mm` depth | `0.0001 mm` | removal | `0 mm³` |

At `0.001 mm` penetration/depth, the same fuzzy value retained the expected material change. This is therefore scale-sensitive semantic suppression, not simply “more robustness.”

**INFERENCE:** OCCT fuzzy tolerance remains useful as an explicit backend knob, but it cannot define programme manufacturing tolerance or the truth of material change.

## Candidate model B — operation-local interval classification

For a signed contact coordinate `d` and local uncertainty half-width `u`, the experiment classifies:

- `d < -u` → confidently overlapping; execute removal;
- `d > +u` → confidently clear; no interaction;
- `|d| <= u` → defer uncertain contact without rewriting signed intent.

The smoke research value was `u = 0.0001 mm`. It produced 12 uncertain-contact deferrals and zero decisive mismatches. Decisive `±0.001 mm` members correctly distinguished overlap from clearance. Positive skim operations remained removal intent rather than being classified from contact distance.

This is an **improvement in semantic safety**, not proof of a complete solver. It deliberately relocates ambiguous cases to an explicit reconciliation stage. RCS-009 must determine which such states may remain deferred and for how long.

The relation is local compatibility, not durable identity.

## Candidate model C — semantic replay collapse

The prototype compared repeated identical OD finishing with one effective finishing execution while preserving the conceptual journal event stream.

**MEASURED:** all six records were geometrically equivalent, including 100 repeats at both fuzzy settings. For the 100-repeat records the measured baseline/one-pass geometry-time ratios were about `2.20×` at fuzzy `0` and `25.42×` at fuzzy `0.0001 mm`.

The timing ratios are indicative only: run ordering/cache effects were not controlled as a performance benchmark. The important result is **zero measured geometry divergence** under the tested repeated envelope.

**INFERENCE:** semantic replay collapse is promising for exact retraces, but production authorization must depend on durable semantic/provenance proof from RCS-008, never transient OCCT identity or proximity alone.

## Anchored quantization

For `Q(x)=round(x/q)*q`, bucket equality is a true equivalence relation. The smoke comparator used `q = 0.0001 mm`.

**MEASURED:** the `0.000001 mm` positive skim quantized to zero in both backend-fuzzy configurations, creating two mismatch records for one physical fixture member. Thus transitivity was obtained by erasing valid sub-grid intent.

The algebraic boundary probe also used `x=0.000049 mm` and `y=0.000051 mm`: only `0.000002 mm` apart, yet they quantized to `0` and `0.0001 mm` respectively.

**INFERENCE:** fixed quantization can be valid where a grid is itself an explicit machine/control contract; it is unsuitable as universal arbitrary-geometry truth.

## Controlled perturbation

At fuzzy `0`, `±0.0001 mm` neighbors around both coincidence and tangency were direction-sensitive: negative penetration removed material, exact/positive contact did not.

At fuzzy `0.0001 mm`, the negative neighbor no longer removed material. That does **not** show perturbation becoming neutral; it is the same fuzzy semantic-loss mechanism measured above.

**INFERENCE:** perturbation is a diagnostic unless manufacturing semantics explicitly determine the permitted side and bound. Random hidden jitter is rejected.

## Algebraic properties and failure modes

For local metric compatibility `a ~ b` iff `|a-b| <= u`, choose `a=0`, `b=0.75u`, `c=1.5u`. Then `a~b` and `b~c`, but not `a~c`. The relation is reflexive and symmetric but not transitive.

**INFERENCE:** transitive closure of “close enough” can merge endpoints outside the intended uncertainty. It must not become global topology identity.

Fixed-grid bucket equality is transitive but discontinuous at cell boundaries and relocates coordinates. These are different failure modes; neither algebraic property alone establishes manufacturing correctness.

For uncertainty accumulation the experiment records a conservative correlated bound `N*u` and an RSS diagnostic `sqrt(N)*u`. RSS is not accepted as a correctness bound without an independence argument.

The accumulation experiment provides stronger empirical evidence. With `0.00001 mm` nested finishing increments:

- `N=10`, fuzzy `0`: both orders matched the analytic volume target;
- `N=100`, fuzzy `0`: both orders matched within about `1.46e-11 mm³`;
- `N=10`, fuzzy `0.0001 mm`: both orders returned valid one-solid B-reps but each missed the target by about `0.753980352 mm³`;
- `N=100`, fuzzy `0.0001 mm`: deepest-first matched the target, while shallow-to-deep missed by about `7.539633873 mm³`; the final volumes differed by `7.539633873064304 mm³` despite identical intended final material.

This demonstrates both **valid-but-wrong geometry** and **operation-order dependence** from applying a fuzzy value larger than the individual incremental removals.

## Experiment design

The executable package is under `research/rcs-007/`:

- `experiment-plan-v1.json` — hypotheses, constants and smoke/baseline sweeps;
- `harness/run_tolerance_campaign.py` — backend/contact/quantization/perturbation orchestration;
- `harness/repeated_finish_worker.cpp` — repeated and ordered finishing-chain OCCT experiments;
- `harness/reconcile_results.py` — explicitly distinguishes deferred classifications from definitive answers and checks analytic-volume correctness;
- `tools/validate_rcs007.py` — static/runtime evidence gate.

The accepted smoke evidence was produced by workflow run `35191482255`, artifact `10483269288`, digest `sha256:745cfab6f747361b8b0b9f2eb2a6528fc73d3c11b5c9203764d0e81d54608ec6`. A durable compact record is `research/rcs-007/measured-summary-v1.json`.

The `baseline` profile expands offsets, fuzzy values, skim depths, repeats and chain counts without changing the result semantics.

## Measured results

**MEASURED:** 26 contact/skim backend attempts completed with zero worker failures. Four OCCT fuzzy-control records violated physical intent; all four were valid B-reps, so validity alone did not expose the error.

**MEASURED:** the operation-local model produced zero **decisive** classification mismatches and 12 explicit deferrals. It therefore avoided asserting the wrong material result in the uncertain band, but it did not eliminate the need to resolve those cases later.

**MEASURED:** anchored quantization erased the `0.000001 mm` positive skim. The algebraic probe independently demonstrated grid-boundary discontinuity.

**MEASURED:** all six repeated-finishing records were equivalent to the one-effective-pass reference. This supports further provenance-backed replay-collapse research.

**MEASURED:** two fuzzy accumulation cases breached the analytic physical oracle. One 100-step case became order-dependent by `7.539633873064304 mm³` while both outputs remained valid one-solid B-reps.

**MEASURED:** two zero-fuzzy perturbation pairs were direction-sensitive, confirming that blind perturbation can switch physical material semantics.

No crash, worker error or timeout occurred in the accepted smoke campaign.

## Export and STEP reconciliation

RCS-005 remains authoritative. Internal uncertainty, contact deferral or semantic replay does not relax STEP success criteria.

Before STEP success, any internal mechanism must reconcile to conventional B-rep geometry with explicit selected bodies, valid topology, bounded dimensions/volume, required analytic preservation, explicit units and the required serialized/read-back/interoperability gates.

If an uncertain relationship still admits materially distinct outcomes beyond the declared export/validation budgets, export must be refused or remain unqualified. Manufacturing tolerance cannot be used as permission for unmeasured healing.

## Interaction with RCS-008 and RCS-009

RCS-008 must define backend-independent semantic identity/provenance sufficient to prove an operation is a safe replay/retrace candidate. The RCS-007 result does not authorize collapse from transient face IDs, B-rep handles or proximity.

RCS-009 must evaluate which lower-dimensional/uncertain contact states can remain deferred until a natural reconciliation boundary. It must not turn the non-transitive local compatibility relation into global topology identity.

## Provisional architecture recommendation

**MEASURED/INFERENCE, confidence medium-high for the tested scope:** reject a programme-wide epsilon and reject global transitive “virtual equivalence” built from metric closeness.

Carry forward this policy:

- separate the nine tolerance/resolution/uncertainty channels;
- treat kernel entity tolerance and OCCT fuzzy value as explicit backend state, not manufacturing truth;
- use bounded uncertainty for operation-local contact classification, with an explicit unresolved/deferred state;
- preserve the sign and semantic meaning of explicit positive material-removal commands even inside numerical uncertainty bands;
- permit semantic replay collapse only with durable provenance proof and unchanged canonical journal history;
- use quantization only where the grid is itself a declared contract;
- use perturbation diagnostically unless a deterministic semantic side is known;
- validate geometry against physical oracles because valid topology can still be materially wrong;
- reconcile any internal uncertainty/deferred representation back to RCS-005-conforming conventional STEP geometry or refuse export.

This is recorded in `DR-0010`. The numerical research constants (`0.0001 mm` local band/grid, `0.000001 mm` nominal per-operation uncertainty) are **not** production defaults. RCS-008–RCS-012 and RCS-013 may revise the implementation model while preserving or explicitly overturning the measured separation-of-concerns conclusion.

## Open questions

**OPEN:** derive operation-local numerical uncertainty from actual sampling, approximation and kernel evidence rather than a fixed research value.

**OPEN:** determine safe reconciliation boundaries by process: pass end, tool withdrawal, setup change, checkpoint, export or another boundary.

**OPEN:** define the minimum durable proof for semantic replay collapse in RCS-008.

**OPEN:** determine which uncertain/lower-dimensional states merit deferred representation in RCS-009.

**OPEN:** decide whether backend-increased entity tolerances require an independent cap/rebuild policy before export.

**OPEN:** repeat the strongest findings across broader RCS-003 members and later non-OCCT candidates; this report does not claim universal computational-geometry behavior.
