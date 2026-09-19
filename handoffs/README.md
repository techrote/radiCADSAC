# radiCADSAC handoff index

**Current bootstrap route (2026-09-19):** use `genesis-release-v2.json` consistency revision `2.1`, `v2/opensimachinist/`, `v2/msac/`, and `evidence-dependencies-v2.1.json`. Read `../docs/37-GENESIS-V2-BOOTSTRAP-CONSISTENCY.md` before autonomous bootstrap.

The remainder of this document records the immutable **Genesis-v1 historical freeze**. Its package trees and launch wrappers remain archaeology/provenance, not current bootstrap instructions.

Genesis-v1 freeze baseline audited: `7f16e4fe310ac3b5e5a4d08547273efaceff0c7f`  
Date: 2026-09-17

## Purpose

This directory is the clean launch boundary between the `radiCADSAC` genesis/R&D record and the two independent production repositories. The production repositories must start with fresh Git histories. They may copy or adapt the frozen handoff **contents**, but must not fork or import the radiCADSAC Git history, research branches, issue history, failed experiments, or obsolete planning as production history.

RCS-016 does not create either production repository. It freezes exactly what is approved to seed them, records the shared boundary audit, preserves unresolved research, and provides reproducible launch instructions that require no founding-chat context.

The machine-readable companion is `handoffs/genesis-release-v1.json`.

## Frozen package identities

The package content is frozen by Git tree identity, not by a mutable branch name.

| Package | Handoff schema | Package origin merge | Declared input baseline inside manifest | Frozen package tree | Manifest blob |
|---|---|---|---|---|---|
| OpenSimachinist | `opensimachinist-handoff/1.0` | `2e77ea087b01ac1415c4c76ff1dc0661aab286fb` (RCS-014 / PR #33) | `23519b5989b14f1b0947dca77588729585150115` (RCS-013) | `d4793b03f31bd9fd58efcea94afba2f69fa3f7f3` | `2d53fc62c8ec5866eff686483ac721983df03b64` |
| MSAC | `msac-handoff/1.0` | `7f16e4fe310ac3b5e5a4d08547273efaceff0c7f` (RCS-015 / PR #34) | `2e77ea087b01ac1415c4c76ff1dc0661aab286fb` (RCS-014) | `e04d53756dd83089d367d756253482bebe791f32` | `2c195f9944f2710426ef7a20eb40d5c3f96bab6a` |

The **joint freeze baseline** is radiCADSAC `main` at `7f16e4fe310ac3b5e5a4d08547273efaceff0c7f`: this is the first accepted `main` state containing both complete packages. RCS-016 deliberately leaves the two package subtrees unchanged and freezes their exact tree IDs above. That distinction matters: the `source_main` field inside each package manifest records the accepted input state used to author that package, whereas the table above records the exact committed package content now frozen for production bootstrap.

A later production founding record should retain all four identifiers relevant to its package: radiCADSAC repository URL, joint freeze baseline, package tree SHA, and manifest schema/version. This makes the seed reproducible even if `main` later gains more research.

## Shared-boundary consistency audit

RCS-016 compared both founding packages against the accepted programme contracts. No incompatibility was found at the production boundary.

### Journal and durable authority

Both packages use `msac-journal/1.0`; preserve explicit units/frames and immutable setup/tool/policy definitions; treat the canonical manufacturing journal and immutable semantic revisions as durable authority; retain repeated/retraced journal events even when geometry recomputation is later proven redundant; and keep backend/private geometry caches disposable.

The shared canonical contract remains `docs/10-CANONICAL-JOURNAL-CONTRACT.md`. MSAC is the producer of canonical manufacturing intent; OpenSimachinist is the semantic consumer/realizer. Neither package makes raw controller samples, Godot scene identity, OCCT topology identity, or render meshes durable engineering meaning.

### Programme API

Both packages name the same founding request families:

- `capabilities`;
- `apply_canonical_operations`;
- `commit_revision`;
- `replay_revision`;
- `query_material_state`;
- `request_preview`;
- `request_reconciliation`;
- `inspect_reconciled_geometry`;
- `export_step`.

Both treat this as a semantic/versioned contract rather than a frozen transport or ABI. Requests carry semantic revision/operation/setup/tool/frame/policy identity; responses carry programme status, resulting revision/body identity, lineage, provider/reconciliation identity and diagnostics. Backend-private OCCT handles, topology addresses/hashes, Godot node IDs and voxel/cell IDs remain forbidden as durable boundary identity.

The shared external boundary remains `docs/01-MSAC-GEOMETRY-CONTRACT.md`, refined by accepted decisions and the two handoffs without changing its ownership split.

### Status and failure model

Both packages preserve the same programme-visible engineering status classes: `accepted_pending`, `reconciled`, `success`, `refused_unsupported`, `refused_unresolved_ambiguity`, `invalid_topology`, `wrong_geometry`, `tolerance_breach`, `kernel_error`, `crash`, `timeout`, `nondeterministic_result`, `step_writer_failure`, `step_roundtrip_failure`, and `interoperability_unqualified`.

MSAC presents those states and recovery choices; OpenSimachinist produces them from qualified provider/reconciliation/export work. A rendered preview, generated file, or valid-looking B-rep does not overwrite a higher-level physical or conformance failure.

### Preview, reconciliation and material bodies

Both packages treat preview as explicitly non-authoritative. Exact/topology-dependent inspection and STEP require suitable authoritative/reconciled state. Parting and cut-through may create multiple durable material bodies; neither package permits an implicit largest/first/primary-body rule. Body selection at export is explicit, with all committed material bodies the default.

### STEP

Both packages use `msac-step-conformance/1.0`, AP242-family engineering semantics, conventional solid B-rep as the primary engineering representation, explicit units/body selection/budgets, Layer A/B/C validation, and an independent Layer-D interoperability qualification state. `interoperability_unqualified` remains distinct from a writer or round-trip success. STL/mesh is never the fallback that converts failed STEP authority into success.

### Concurrency safety boundary

Both packages remain compatible with process-isolated backend workers. The still-open RCS-017 concurrency/global-state probe may later justify relaxing or refining that deployment boundary, but its absence does not make either frozen handoff inconsistent: process isolation is intentionally the conservative founding default and the unknown is already carried in the OpenSimachinist unresolved register and MSAC escape routes.

## Decision and evidence index

This is the compact archaeology map for production contributors. Production repos should copy only the requirements they need, while retaining links back to these accepted genesis sources for challenge/reproduction.

| Concern | Accepted source/evidence | OpenSimachinist | MSAC |
|---|---|:---:|:---:|
| STEP is primary engineering output | DR-0001, DR-0009, `docs/13-STEP-CONFORMANCE-CONTRACT.md` | yes | yes |
| Journal is durable intent | DR-0002, `docs/10-CANONICAL-JOURNAL-CONTRACT.md` | yes | yes |
| Initial lathe/mill scope | DR-0003 | yes | yes |
| Stable backend boundary / no private kernel types | DR-0004, `docs/01-MSAC-GEOMETRY-CONTRACT.md` | yes | yes |
| Pathological manufacturing input is normal | DR-0005, `docs/11-ADVERSARIAL-MANUFACTURING-CORPUS.md` | yes | yes |
| Canonical numerics, frames and definitions | DR-0006, `docs/10-CANONICAL-JOURNAL-CONTRACT.md` | yes | yes |
| Bounded deterministic canonicalization | DR-0007 | consumes | produces |
| Immutable revisions and body transitions | DR-0008 | yes | yes |
| Separate tolerance/uncertainty channels | DR-0010, RCS-007 | owns geometry translation | presents policy/status |
| Semantic lineage, not topology ID | DR-0011, RCS-008 | owns lineage realization | persists/consumes durable IDs |
| Regularized/deferred topology | DR-0012, RCS-009 | provider/reconciliation policy | status/capability consumer |
| Axisymmetric lathe provider | DR-0013, RCS-010 | implements qualified subset | exposes qualified interaction |
| Mill strategy hierarchy | RCS-011 | implements qualified hierarchy | exposes qualified interaction |
| Bounded hybrid fallbacks | DR-0014, RCS-012 | private local fallback seam | never depends on representation internals |
| Selected backend architecture | DR-0015, RCS-013 | implements `semantic-provider-hybrid-v1` | consumes `semantic-provider-hybrid-v1` |

All decision records DR-0001 through DR-0015 are accepted genesis decisions at this freeze. Later production decisions may supersede them only explicitly and should retain archaeology/provenance.

## Genesis result classification

- **Accepted historical foundation/research:** RCS-001 through RCS-012. Their results remain evidence and regression/provenance sources, but they are no longer active blockers for founding the production repos.
- **Accepted architecture synthesis:** RCS-013 / Gate 2, selecting `semantic-provider-hybrid-v1` with explicit escape routes.
- **Accepted founding handoffs:** RCS-014 OpenSimachinist and RCS-015 MSAC, frozen by the package tree identities above.
- **Genesis freeze:** RCS-016. This index, manifest, launch wrappers and validator constitute its release artifact once merged to `main`.
- **Still-active non-blocking research:** RCS-017 / GitHub #20, OCCT concurrency and global-state isolation. Its result may refine worker topology through a later explicit production decision; it does not invalidate the conservative process-isolated founding contract.
- **Superseded planning artifact:** `docs/02-INITIAL-RESEARCH-PLAN.md` is preserved for archaeology and is superseded by `docs/04-REVISED-RESEARCH-ROADMAP.md` where they differ.
- **Historical review artifact:** `docs/03-PLAN-REVIEW.md` records the critique that produced the revised roadmap; it is evidence, not a production requirement source.

After RCS-016, the roadmap and issue graph describe how the genesis evidence was produced. They are historical programme records rather than a requirement that routine production work be mirrored back into radiCADSAC.

## Unresolved research is intentionally preserved

Do not convert an unknown into a production assumption merely because the genesis phase is frozen.

OpenSimachinist's authoritative unresolved list remains `handoffs/opensimachinist/03-UNRESOLVED-RESEARCH-REGISTER.md` and the `unresolved_ids` array in its manifest. It includes pathological freehand milling fallback, real lathe tool-envelope qualification, production STEP interoperability, curved hybrid reconciliation, OCCT thread/global-state behavior, provider-handoff frequency/cost, semantic-lineage persistence encoding, deferred-resource policy, targeted exact-arithmetic seams, release-time licensing compliance, and later live-tool/non-axisymmetric work.

MSAC's corresponding integration escape routes remain `handoffs/msac/03-INTEGRATION-ESCAPE-ROUTES.md` and the manifest's `integration_escape_routes` array. They preserve capability discovery, pending/fallback/refusal semantics, process-isolated worker tolerance, crash/replay recovery, semantic IDs, backend-private representations, explicit version migration and non-authoritative preview/control/camera seams.

Production issue graphs already contain the work that must qualify these unknowns when they become relevant. RCS-017 stays discoverable here as active research rather than being falsely marked solved.

## Production repository launch boundary

Assumed production repository names, unless the user explicitly chooses different names, are:

- `techrote/OpenSimachinist` for the backend;
- `techrote/MSAC` for the user-facing SAC environment.

Do **not** create either repository merely because this freeze exists. Repository creation/population requires separate authorization.

The final production launch wrappers are:

- `handoffs/launch/opensimachinist-v1.md`;
- `handoffs/launch/msac-v1.md`.

They point to the exact frozen package revision and the project-specific `04-CLEAN-REPO-BOOTSTRAP-CHECKLIST.md`. The launch wrappers cover repository naming assumptions, fresh initial files, CI, issue creation order, licensing/provenance notices, and how to reference radiCADSAC without importing its history.

## Tag and release naming scheme

Recommended immutable names:

- joint genesis freeze: `radiCADSAC-genesis-v1`;
- OpenSimachinist seed: `opensimachinist-handoff-v1`;
- MSAC seed: `msac-handoff-v1`.

All three tags should target the **RCS-016 merge commit on `main`**, because that commit contains this central freeze record while the manifest separately pins each package tree and origin commit. Do not move these tags once published.

The RCS-016 PR cannot truthfully pre-record its own future merge SHA, so tag creation is a post-merge release action rather than part of the PR contents. If tags/releases are desired, after verifying the RCS-016 merge landed on `main` run:

```bash
git fetch origin main --tags
RCS016_MERGE_SHA=$(git rev-parse origin/main)
git tag -a radiCADSAC-genesis-v1 "$RCS016_MERGE_SHA" -m "radiCADSAC genesis handoff freeze v1"
git tag -a opensimachinist-handoff-v1 "$RCS016_MERGE_SHA" -m "Frozen OpenSimachinist handoff v1; package tree d4793b03f31bd9fd58efcea94afba2f69fa3f7f3"
git tag -a msac-handoff-v1 "$RCS016_MERGE_SHA" -m "Frozen MSAC handoff v1; package tree e04d53756dd83089d367d756253482bebe791f32"
git push origin radiCADSAC-genesis-v1 opensimachinist-handoff-v1 msac-handoff-v1
```

Before pushing, verify `RCS016_MERGE_SHA` is the merge commit for the accepted RCS-016 PR rather than a later unrelated commit. A GitHub release, if desired, should be created from `radiCADSAC-genesis-v1` and link this index plus `genesis-release-v1.json`; release creation is not required for the handoff contents themselves to be reproducible.

## Self-contained bootstrap rule

No required production instruction depends on the original conversation or inaccessible chat context. The frozen handoff package, this index, the relevant launch wrapper, and the linked accepted genesis documents contain the information required to found either repository. If a later contributor discovers a requirement that exists only in chat history, it is **not** part of this frozen genesis contract until captured in an explicit repository decision/change.

`radiCADSAC` remains the programme's genesis/R&D record after this freeze. Routine future implementation decisions belong in the two production repositories; only genuinely cross-programme research or explicit archaeology corrections need return here.
