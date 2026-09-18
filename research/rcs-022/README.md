# RCS-022 — STEP Layer-D independent interoperability qualification

RCS-022 closes the remaining STEP interoperability research gap without changing the established geometry, journal, tolerance, body-preservation, source, or provenance contracts. The measured outcome is **`interoperability_unqualified`**: the independent parser and B-rep consumer succeeded across the matrix, but the declared independent consumer metric gate did not.

## Boundary under test

The candidate exporter is pinned to OCCT 8.0.1 at source commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`, AP242DIS, manifold-solid B-rep, tessellation disabled, explicit mm/inch output, `Greatest` precision mode, and `0.0001` file-unit precision. The observed serialized schema identifier is `AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF {1 0 10303 442 1 1 4 }`. Every disconnected solid is transferred independently; no body may be discarded to make export succeed.

Layer C remains a fresh same-OCCT readback and is deliberately *not* counted as independent interoperability evidence.

Layer D uses two implementations that do not link OCCT:

- `step-io 0.2.4` is the independent Part-21/schema-aware parser. It reports the identified schema, file units, B-rep solid count, face count, analytic surface classes, and warnings.
- `vcad-kernel-step 0.10.0` is the independent downstream B-rep consumer. Its imported solid/body count and degradation report are observed separately from `vcad-kernel-tessellate 0.10.0`, which supplies bounded mesh-derived bbox/volume diagnostics.

The founding RCS-005 text named STEPcode as a concrete parser candidate. RCS-022 preserves the actual invariant—independent schema-capable Part-21 parsing—while using `step-io` as the measured implementation. The complete Rust dependency graphs are frozen in committed `Cargo.lock` files and CI builds them with `--locked`.

## Matrix and adversarial controls

`fixture-plan-v1.json` covers metric and inch-equivalent blocks, analytic cylinder/cone, through/blind holes, disconnected two-body parting and mill cut-through, an RCS-020-qualified fixed-axis material-domain representative reconstructed as conventional B-rep, same-domain reconciliation, and a trimmed curved result. The RCS-020 case does not claim exact replay of circular tool-nose geometry. The RCS-021 cut-through invariant is consumed as a disconnected-body preservation case; directional/dexel material states are never exported directly as STEP.

Adversarial controls require deterministic detection of wrong units, omitted bodies, invalid/open non-solids, analytic degradation, excessive dimensional/volume deviation, schema/parser failure, and downstream consumer failure. A positive-case interoperability disagreement does not get hidden by widening tolerances or substituting tessellated output.

## Run

CI builds the exact OCCT baseline through the existing RCS-006 bootstrap, then builds both independent Rust probes from committed lockfiles and runs:

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

## Frozen result

The final pre-freeze measured campaign at source head `be3812856d600e3fa09bc8462ff0e2c2b851fcd9` was workflow run `35349677095`, job `105614535156`. Evidence artifact `10549412055` has SHA-256 `d30bce4672da74d3714cb16d655f5b102ba1ce46e46f4d754684eade377b30d0`. `frozen-result-v1.json` preserves the durable condensed observations and all eleven exact STEP artifact hashes.

All eleven positive fixtures passed Layer C, independent `step-io` parsing and clean independent vcad B-rep import with exact body counts and zero skipped faces. Both disconnected-body fixtures remained two bodies independently. All seven adversarial controls passed.

The profile still fails full Layer-D qualification. Nine vcad metric children attempted a 1,610,612,736-byte allocation under the declared 1 GiB child limit. The analytic-cylinder and analytic-cone metric paths completed but their 64-triangle mesh volumes missed the material-volume reference by about 33.76% and 14.84%, above the declared 2% diagnostic bound. These blockers are preserved as evidence rather than hidden by changing the envelope after observation.

The explicit `ShapeUpgrade_UnifySameDomain` case kept one body, zero bbox change and about `9.09e-13 mm3` volume change while reducing ten coplanar planar faces to six.

## Closure rule

The RCS-022 research question is complete because the concrete profile is reproducible, independently exercised, adversarially tested, and its negative result is precisely bounded. It does **not** authorize production Layer-D STEP qualification. A future positive qualification requires a new measured run satisfying every declared gate, with requalification whenever any exporter/schema/healing/body-policy/parser/consumer/resource-envelope dependency changes.
