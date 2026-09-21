# MC-026 — Candidate selection and algorithm-specific implementation blueprints

Status: **COMPLETED_RESEARCH** as a bounded candidate-selection and implementation-blueprint result; no native capability gate is promoted.  
Issue: #88.  
Source baseline: `b4739cb1941918e6d26d32800b622d631adfad99`.  
Native/paid execution: **none**.

## Selection question and decision

MC-026 consumes the completed MC-024/025/027/028/029/030 evidence plus the pre-selection MC-049 challenge freeze. The selected primary material route is `PRIMARY_CERTIFIED_ADAPTIVE_IMPLICIT`: a source-bound certified adaptive interval/implicit evaluator driven by the actual qualified MC-018..023 sweep constructors, with critical equality/topology events delegated to an independently certified event service rather than inferred from refinement depth, cell size, tolerance or timeout.

This is a design selection, not a theorem that every admitted request can already terminate successfully. `PB-007-01`, `PB-007-02` and `PB-007-03` remain typed, fail-closed terminals where their producing obligations are still unresolved. `UNCERTIFIED`, `RESOURCE_REFUSAL` and `SEMANTIC_BLOCKER` likewise remain valid non-success outcomes.

The independent challenger/control is `EXACT_CELL_SEMIALGEBRAIC_CONTROL`, retaining MC-024's exact arrangement/cell route only for inputs with a proved finite semialgebraic encoding. Independence is structural: separate material representation, separate classification implementation, separate certificate/result namespace, and no shared adaptive-cell classification code. Agreement between primary and challenger is useful evidence but cannot promote either route to total-domain authority or close inherited blockers.

## Why the other candidates remain secondary

MC-027 directional intervals remain a derived index/accelerator because finite sampled rays do not determine arbitrary hidden positive-volume 3D material. MC-028 native mesh/Manifold Boolean remains a bounded derived challenger because finite floating faceting/tolerance cannot become exact curved-material, exact-zero, durable-body or STEP authority. MC-029 sparse volume/level-set state remains a derived accelerator because finite sampling cannot determine sub-cell positive material and its source/sampling/resampling/extraction error terms must remain explicit.

MC-030's four sufficient fast providers are retained in front of the selected primary. A request may invoke at most one fast provider and then at most one general primary invocation. Fast success requires an independent material certificate; failure or uncertified success falls once to the primary. The general route does not redispatch to fast providers, so the provider graph remains noncycling.

## Complete current-domain accounting

The MC-002 domain contract currently contains 26 required operation IDs. MC-026 partitions all 26 exactly once and keeps every one in the denominator:

- conventional lathe operations enter `FP-LATHE-AXISYMMETRIC` only when MC-021's sufficient predicate holds, otherwise `PRIMARY_CERTIFIED_ADAPTIVE_IMPLICIT`; arbitrary form-tool source encoding still propagates `PB-007-03` where applicable;
- `lathe_threading_synchronized` and `lathe_eccentric_turning` enter `FP-LATHE-PHASE-BOUNDED` only when the bounded MC-022 predicate holds, otherwise the primary while preserving `PB-007-01`/`PB-007-02`;
- ordinary fixed-axis milling enters `FP-MILL-ANALYTIC-TRANSLATION` only when its sufficient predicate holds, otherwise the primary;
- form, accessible-undercut and fixed-axis helical-form milling enter `FP-FORM-BOX-UNION` only for the bounded exact subtype and otherwise the primary while retaining `PB-007-03`;
- re-clamp, cross-machine, retained-body and disappearance compositions enter the primary/body-state path without inventing a label-only fast provider.

Output-side obligations do not disappear through material-route selection. `RB-016-02`, `RB-016-03` and `RB-016-04` remain open for durable multi-body engineering output, certified micro-material preservation and exact-zero/touching/singular output qualification respectively.

## Reviewable native leaf blueprints

No duplicate task family is created. The selected design is decomposed under the existing downstream owners:

- `MC031-A`: source-bound evaluator ingress and MC-030 dispatch adapter; consume actual sweeps and preserve common-frame, revision, `body_id`, engagement and inherited MC-058 error.
- `MC031-B`: certified adaptive implicit general evaluator; sound outward bounds, with unresolved cells remaining `UNCERTIFIED`; no pitch/depth/epsilon/timeout truth authority.
- `MC031-C`: non-authoritative directional/mesh/sparse accelerator adapters; cache/component identity never becomes durable body/lineage.
- `MC032-A`: exact algebraic critical-event kernel for exact-zero, multiplicity and sign controls in the admitted algebraic subset.
- `MC032-B`: certified transcendental/phase event service preserving shared time/feed/spindle correlation and retaining `PB-007-01`/`PB-007-02` until producing-owner evidence exists.
- `MC032-C`: finite-progress and blocker terminalization; resource exhaustion remains refusal/uncertified and cannot create provider cycles.
- `MC033-A`: regularized durable body state machine for split, disappearance and explicit empty state without backend topology identity leakage.
- `MC033-B`: programme-owned lineage-transition certificates; touching boundaries do not merge bodies without volumetric evidence.
- `CTRL-026-A`: exact-cell differential challenger harness on proved semialgebraic instances using independent MC-010/MC-015 comparison.
- `CERT-026-A`: frozen challenge/certificate binding preserving MC-049 identities and honest custody labels.

These are blueprints inside MC-031/032/033, not new issue identities. Those native tasks remain downstream of the MC-038 capability gate and are not authorized by MC-026 alone.

## Frozen challenge custody

The MC-049 set remains exactly 64 candidate-blind records under `PUBLIC_PRESELECTION_PREREGISTRATION`. MC-026 does not execute or alter that set and does not relabel it as secret, independent or held-out. Later independent custody/execution remains owned by MC-057.

## Boundary and adversarial controls

The deterministic selection model verifies every current MC-002 required operation enters the primary route, rejects operations outside the frozen domain, rejects missing source/common-frame binding, and preserves phase-event, form-source and body-transition obligations. Fast provider success without its independent certificate falls to the primary. Challenger success cannot override an `UNCERTIFIED` primary result, and accelerator observations never become canonical authority.

The adversarial verifier rejects denominator shrinkage, primary-totality promotion, challenger-totality promotion, loss of challenger implementation independence, provider cycles, a second general invocation, accelerator promotion, MC-049 challenge-count or candidate-blindness drift, inherited blocker closure, blueprint reassignment outside MC-031/032/033, and premature MC-B acceptance.

## Retained blockers and capability state

`PB-007-01`, `PB-007-02`, propagated `PB-007-03`, `RB-016-02`, `RB-016-03` and `RB-016-04` remain open. Native evaluator/classifier/body-state implementation, reconstruction and independent STEP qualification remain downstream work.

MC-A remains `ACCEPTED`; **MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`**. Historical source/audio/provenance, canonical-journal intent, positive-volume material, durable body/lineage semantics and the conventional STEP requirement are unchanged.

## Verification

```text
python3 research/machining-completeness/tasks/MC-026/verify.py --contract
python3 research/machining-completeness/tasks/MC-026/verify.py --self-test
python3 tools/mc_workflow.py verify MC-026
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The exact PR head must pass `mc1-static` before merge, and the merged SHA must pass the same workflow on `main` before issue #88 is closed.
