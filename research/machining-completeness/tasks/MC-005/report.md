# MC-005 — MC-A domain-lock integration review

## Disposition

**MC-A: ACCEPTED for the current MC-1 tranche.** This is a requirements/domain-lock decision only. It does not establish constructive completeness, native geometry correctness, B-rep/STEP realization, independent consumer qualification, practical scale, MC-1 acceptance, production authorization, or permission for paid/native execution.

Exact starting `main`: `0ef8235ed9bd7e807a04f7ad048dae2929c131c3` (post-MC-004). Task owner: issue #67. Integration locks: `domain-contract`, `programme-registry`. No pre-existing MC-005 branch or PR was found before creating `mc-005-domain-lock-integration`.

## Hypothesis and falsification

The hypothesis was that the reviewed MC-002 domain/physical-validity artifact, MC-003 exact numeric/source artifact, MC-004 candidate-independent qualification artifact and MC-056 execution-safety artifact form one internally consistent current-tranche contract without provider-driven narrowing or reinterpretation of historical semantics.

The review would reject MC-A if any admitted MC-002 operation disappeared from the MC-004 denominator; any admitted trajectory/setup/phase constructor lacked finite exact MC-003 semantics; a candidate/provider could redefine physical validity, workload, accuracy or resource limits; an in-scope product boundary remained ambiguous; legacy journal/body/provenance meaning changed in place; or the integration depended on unexecuted native evidence.

None of those falsifiers applies after the product-boundary reconciliation below.

## Dependency bindings

The review consumes the already accepted artifacts without rewriting them:

- MC-002 outcome blob `930db704e9dd29955e7af99ba793c74e0cfda325`; domain contract blob `23de82f5240a72509f7afe4acd5948b65bc4ff13`.
- MC-003 outcome blob `8f335f59f36c8761844806f9059af4a4f1671044`; numeric/encoding contract blob `a5538cab698c806fdedcef7cf563b650638348e0`.
- MC-004 outcome blob `4f032ac5ff2584c48084fac3282c137a00731d40`; qualification contract blob `22d5f976718edac9a8ccce3cb46f799b76e85ab4`.
- MC-056 outcome blob `e9b971c593ca1a90baf17f9ae9a5a568dd313ac3`.

Historical MC-002/003/004 records remain historical evidence of what each task had and had not decided at its own completion. MC-005 adds an integration decision; it does not edit those artifacts to make them appear retrospectively complete.

## Domain integration

The frozen denominator is the same 26 admitted operations in MC-002 and MC-004. It spans ordinary conventional lathe operations, fixed-axis three-axis milling, fixed-axis simultaneous XYZ and helical motion, phase-sensitive threading/eccentric turning, parting/cut-through and multi-body handling, explicit re-clamp/reorientation, lathe↔mill histories, machining a retained/re-clamped separated body, and complete material removal.

Physical admissibility remains independent of solver success. Engaged teleportation is invalid; stationary engagement is valid; workholding/access/clearance must be witnessed; detached material cannot remain magically fixed; point/edge contact is not a volumetric bridge; positive-volume slivers remain material; durable body identity is not a backend topology handle; and an empty final material state is valid.

### Product-boundary decisions

MC-002 deliberately left `DD-002-04` and `DD-002-05` for MC-005 rather than allowing a provider to decide them. They are now resolved from the programme/founding scope, not from candidate limitations:

- **DD-002-04 — compound lathe live/driven tooling:** simultaneous compound turn-mill/live-tool kinematics are **outside the current MC-1 tranche**. The current tranche is conventional lathe plus fixed-axis three-axis mill. This does not exclude a workpiece merely because a commercial machine could make it with live tooling: the admitted lathe, mill, re-clamp and machine-transition history remains authoritative where it realizes the same manufacturing intent. No currently admitted operation is removed.
- **DD-002-05 — coordinated multi-spindle/transfer machines:** simultaneous multi-spindle/transfer-machine process coordination is **outside the current MC-1 tranche**. Single-workpiece lathe/mill histories, explicit re-chucking/re-clamping, body retention and machine transitions remain in scope. Again, no currently admitted operation is removed.

These are tranche boundaries, not claims that such real machines or processes are impossible or permanently unsupported. Adding either process class later requires a prospective versioned domain/workload revision before candidate qualification. A future candidate failure cannot be turned into an exclusion by invoking these decisions.

## Precision and request integration

MC-003 preserves every existing `msac-journal/1.0` token meaning and adds `mc-exact-source/1.0` for exact rational/symbolic-turn/directed-interval source semantics. The integration retains fail-closed required extensions, new-revision-only migration, no fabricated lost precision, dimensional typing, no global untyped epsilon, no tolerance-as-sign and no silent overflow/nonfinite authority state.

MC-004 independently freezes the same 26-operation denominator, candidate-blind workload generation, T0/T1 controls, 10/100/1,000/10,000 genuine-geometry T2 cells with separate redundant-history controls, the semantic/engineering/precision accuracy vectors, reference hardware, three sequential completed repeats and the non-pass treatment of timeout/resource exhaustion/pending/refusal/crash/material mismatch/invalid certificate. No candidate has been run by MC-005 and no profile is relaxed.

The MC-003 production codec choice remains an implementation detail rather than a semantic-domain gap: the exact source semantics and fail-closed extension behavior are fixed. MC-004's future T3 and provider-tariff questions are later execution-policy questions and do not alter the frozen MC-A request.

## PO-01 and MC-A

PO-01 (Domain fidelity) is accepted for this current tranche because the process boundary, admitted operation denominator, physical-validity rules, source/numeric semantics and frozen qualification request are explicit and mutually consistent, and because the two previously open scope decisions are resolved without denominator shrinkage.

MC-A is therefore accepted. The decision is deliberately narrow: it says **what must be solved and under which precision/workload contract**. It does not say that a terminating solver exists or that any candidate has solved it.

MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`. PO-02 through PO-12 remain open under their existing owners.

## Adversarial and boundary controls

`verify.py` cross-checks the integrated denominator against both MC-002 and MC-004, checks exact dependency blob identities, checks the historical MC-002 boundary decisions before applying the MC-005 resolution, checks MC-003 source semantics and MC-004 freeze policy, and checks the programme/outcome/PO registries.

Its mutation tests reject at least: dropped admitted operations; provider-driven scope decisions; a boundary decision that changes the current denominator; unresolved in-scope product boundaries; promotion to native geometry evidence; candidate-specific qualification; changed workload seed; weakened exact-source profile; weakened protected semantics; and gate/PO registry drift.

## Protected semantics and execution

No Genesis-v2.1 measured artifact, source/audio/provenance identity, canonical journal meaning, durable body/lineage rule, historical negative result or provider-private topology rule is weakened or rewritten. No native geometry or paid campaign was run. No production repository/bootstrap is authorized.

## Verification commands

```text
python3 research/machining-completeness/tasks/MC-005/verify.py --contract
python3 tools/mc_workflow.py verify MC-005
python3 tools/validate_machining_completeness.py --self-test
```

The task is acceptable only if the repository `mc1-static` workflow passes on the exact PR head and the post-merge main commit.
