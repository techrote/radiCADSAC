# RCS-022 — STEP Layer-D independent interoperability qualification

RCS-022 closes the remaining STEP interoperability evidence gap without changing the established geometry, journal, tolerance, body-preservation, or provenance contracts.

## Boundary under test

The candidate exporter is pinned to OCCT 8.0.1 at source commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`, AP242DIS, manifold-solid B-rep, tessellation disabled, explicit mm/inch output, `Greatest` precision mode, and `0.0001` file-unit precision. Every disconnected solid is transferred independently; no body may be discarded to make export succeed.

Layer C remains a fresh same-OCCT readback and is deliberately *not* counted as independent interoperability evidence.

Layer D uses two implementations that do not link OCCT:

- `step-io 0.2.4` is the independent Part-21/schema-aware parser. It reports the identified schema, file units, B-rep solid count, face count, analytic surface classes, and navigation warnings.
- `vcad-kernel-step 0.10.0` is the independent downstream B-rep consumer. Its imported solid/body count and degradation report are authoritative for this test; `vcad-kernel-tessellate 0.10.0` supplies a bounded mesh-derived bbox/volume diagnostic and is not promoted over the strict OCCT Layer-C B-rep checks.

The founding RCS-005 text named STEPcode as a concrete parser candidate. RCS-022 does not treat that product name as normative: the requirement is an independent schema-capable Part-21 parser. `step-io` satisfies that role while remaining independently implemented from OCCT.

## Matrix and adversarial controls

`fixture-plan-v1.json` covers metric and inch-equivalent blocks, analytic cylinder/cone, through/blind holes, disconnected two-body parting and mill cut-through, an RCS-020-qualified fixed-axis material-domain representative reconstructed as conventional B-rep, same-domain healing, and a trimmed curved result. The RCS-020 case is intentionally described as a representative conventional reconstruction rather than an exact replay of circular tool-nose geometry; RCS-020 itself did not qualify exact toroidal nose preservation. The RCS-021 cut-through invariant is consumed as a disconnected-body preservation case; directional/dexel material states are never exported directly as STEP.

Adversarial controls require deterministic detection of wrong units, omitted bodies, invalid/open non-solids, analytic degradation, excessive dimensional/volume deviation, schema/parser failure, and downstream consumer failure. A positive-case interoperability disagreement does not get hidden by widening tolerances or substituting tessellated output: the final verdict becomes `interoperability_unqualified` and retains exact blockers.

## Run

CI builds the exact OCCT baseline through the existing RCS-006 bootstrap, then builds both Rust probes from exact direct dependency versions and runs:

```text
python3 research/rcs-022/run_campaign.py \
  --exporter <rcs022_step_exporter> \
  --parser-probe <rcs022-stepio-probe> \
  --consumer-probe <rcs022-vcad-probe> \
  --out-dir <evidence-dir>/step \
  --output <evidence-dir>/measured-summary-v1.json
python3 tools/validate_rcs022.py --summary <evidence-dir>/measured-summary-v1.json
```

Each exported STEP file is SHA-256 digested into the evidence record along with fixture source, exporter profile, expected body set, and independent observations. Generated STEP files are evidence artifacts, not canonical source/journal state.

## Closure rule

`interoperability_qualified` requires every positive case and every negative control to pass. `interoperability_unqualified` is also a valid research conclusion only when all adversarial controls work and every interoperability blocker is preserved explicitly. The latter closes the research question but does **not** authorize STEP Layer-D production qualification.
