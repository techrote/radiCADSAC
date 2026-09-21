# MC-015 — Independent certificate checker and oracle attack suite

Status: completed research on the MC-015 branch. Issue: #77. Source baseline: `045a6a85972ad381cfcc0ccfc014e4dca8c5a970`. This task does not execute native geometry, qualify STEP, or change any capability gate.

## Purpose and hypothesis

MC-009 established identity/schema binding and MC-010 established a bounded structurally separate exact rational control. MC-011 through MC-014 then constructed the mandatory F01–F16 prospective fixture families. MC-015 asks whether a programme-owned checker can reject corrupt certificate inputs and common-mode oracle mistakes without importing the candidate implementation or accepting candidate output as truth.

The hypothesis is deliberately bounded: exact certificate arithmetic, independent authority/source identity, discriminating material probes, topology and durable-body obligations can be checked by a small separate implementation. The decisive falsification criterion is any required corruption or materially wrong control being accepted as `PASS`.

## Inputs and independence graph

The task consumes MC-009 and MC-010 as its typed artifact dependencies. The current reviewed MC-011–MC-014 outcomes and MC-055 immutable historical import are auxiliary evidence, not rewritten dependencies. `certificate-attack-contract-v1.json` pins their producing Git blobs, the F01–F16 registry, the MC-009 binding verifier, the MC-010 exact-cell oracle, every MC-011–MC-014 fixture witness oracle and the MC-055 historical import contract.

The MC-015 checker imports only Python standard-library exact-data machinery (`Fraction` plus structural helpers). It does not import `field.py`, RCS geometry code, any candidate geometry implementation, MC-010's cell evaluator or any MC-011–MC-014 fixture oracle. The verifier separately checks the import graph of those oracle sources. This preserves the earlier conclusion that the historical RCS-021 `material_oracle.py`, tridexel and Manifold paths share decisive `field.py` mathematics and therefore cannot be relabelled as independent simply because they are separate executables.

## Certificate semantics

`certificate_checker.py` accepts exact integers/rational strings only on the authority path and rejects binary floats. A candidate certificate binds candidate source/configuration, an independently owned checker, an independently owned oracle and an expected-truth authority that cannot be candidate-owned.

The material certificate uses a checked sandwich: `L ⊆ M ⊆ U` for nominal material and `L ⊆ B ⊆ U` for candidate material. The four inclusion statements must be independently evidenced as `PROVED`; exact lower, nominal, candidate and upper volumes must be ordered consistently; `band_volume` must equal exact `volume(U)-volume(L)`; and that band may not exceed the preregistered symmetric-difference allowance. This makes a broad interval that contains both correct and materially wrong answers fail rather than count as success.

Scalar material bounds are explicitly insufficient. Material/void/boundary witness probes are non-compensating: a lost thin web, filled channel or collapsed tangent fails even when aggregate volume remains inside the band. Exact component count is also non-compensating, as are durable body identity and lineage. A body may reach exact empty material while its durable identity remains recorded; a positive residual cannot be rounded to empty.

A non-success terminal (`TIMEOUT`, `RESOURCE_EXHAUSTED`, rejection, error, crash or not-executed) cannot become `PASS`. A physically valid exact-empty certificate can pass only when material is exactly zero and all independent topology/body obligations pass.

## Adversarial and boundary controls

The deterministic self-test starts from positive exact controls and then independently corrupts each decisive class. It rejects binary-float authority; timeout/resource refusal as success; candidate-owned checking, expected truth or inclusion proof; false oracle-independence metadata; shared decisive geometry; inverted or inconsistent sandwiches; nominal/candidate material outside the sandwich; false or over-broad uncertainty bands; unproved inclusions; lost positive thin material; filled void/channel; tangent collapse; wrong component count/added bridge; lost durable body identity; lost lineage; positive residual rounded to empty; and duplicate witness identity.

Boundary positives include an exact `1/1000000` positive material witness, an exact boundary/tangent state distinct from material and void, and valid exact-empty material with retained exhausted-body identity. The existing MC-009 binding verifier is rerun by the MC-015 verifier so stale identity/profile/checker/result corruptions remain independently covered rather than being replaced by the new certificate checks.

## Findings

The bounded hypothesis survives the required controls. A small programme-owned checker can distinguish the deliberately materially wrong controls covered by the certificate without sharing candidate geometry. This is useful infrastructure for later candidate falsification and native material/reconstruction work.

The result is not a universal geometry oracle. The checker can only validate the certificate statements and discriminating witnesses it is given; it does not prove that those witnesses are complete over the entire machining domain. F01–F16 being `BUILT` still means fixture/oracle construction only. No candidate has thereby passed any family, and no deterministic-model result is promoted to native geometry evidence.

## Preserved negative/open evidence

MC-007's transcendental/tangential blockers remain open. General curved/timed/phase-sensitive completeness, arbitrary imported solids, universal topology, native reconstruction and independent STEP qualification remain downstream obligations. Historical Genesis/RCS results, including failures, timeouts, refusals and resource bounds, are not rewritten. The canonical journal, source/audio/provenance meaning, positive-volume semantics, durable body identities and lineage semantics are unchanged.

MC-A remains `ACCEPTED`. MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`. No native or paid campaign was run and production remains unauthorized.

## Verification

Deterministic commands:

```text
python3 research/machining-completeness/tasks/MC-015/certificate_checker.py
python3 research/machining-completeness/tasks/MC-015/verify.py --contract
python3 research/machining-completeness/tasks/MC-015/verify.py --self-test
python3 tools/mc_workflow.py verify MC-015
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The repository static workflow additionally compiles both MC-015 Python entry points, reruns all previously completed MC task contract checks and displays the evidence-ready frontier.

## Downstream implications

Later candidate and native tasks may consume this checker as an artifact only. Any change to canonical binding semantics, an oracle source pinned here, the historical import contract, F01–F16 fixture meaning, or the MC-015 checker itself invalidates affected downstream certificates and requires a reviewed new revision. Such a revision appends/supersedes evidence; it does not edit historical producing records or shrink the mandatory denominator.
