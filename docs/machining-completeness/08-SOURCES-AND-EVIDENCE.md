# Source, conversation and inherited-evidence register

Status: source inspection and planning reconciliation, 19 September 2026; no native geometry rerun. Planning baseline: `e86c15ca0479240a0045ebc80c83973137b58c60`. Original source-plan SHA-256: `b7cb369e1fef31bb6a02d02960931b3090424114395af9487babf6c0ecbb609c`.

## Conversation reconciliation

The latest explicit user mandate requires 100% of the supported actually machinable domain and rejects moving to an application/game-engine vertical slice while geometry remains unresolved. The source plan correctly distinguishes that target from all arbitrary surfaces. The current request authorizes repository-native adoption, supporting documents, issues and review; the source file's earlier delivery-only prohibition no longer blocks these planning actions. It does not authorize production repositories or expensive campaigns.

Earlier advice to start production is superseded by DR-0026. Earlier informal pooled refinement counts are not a unified engineering qualification. Repository discussions were inspected for all existing issue/PR comments in the exact-baseline inventory; no open issue or PR existed before this adoption. There were no existing milestones. Historical owners and useful evidence remain preserved.

The [#46 final acceptance](https://github.com/techrote/radiCADSAC/issues/46#issuecomment-5739613315) accepts bounded Gate 5, explicitly retaining Layer-D unqualified status and distinct measured/final-head identities. The [#60 consistency acceptance](https://github.com/techrote/radiCADSAC/issues/60#issuecomment-5740726821) records merge `e86c15c…`, pending-intent durability, interior-component semantics and the native/model distinction. The [#41 Layer-D result](https://github.com/techrote/radiCADSAC/issues/41#issuecomment-5731391007) records consumer memory/metric failures rather than qualified interoperability. The [#44](https://github.com/techrote/radiCADSAC/issues/44#issuecomment-5737392646) and [#45](https://github.com/techrote/radiCADSAC/issues/45#issuecomment-5738042215) records are interpreted at their model/platform/native scopes, with later #46/#60 clarifications controlling current interpretation. Earlier time-stamped blocked comments are not current blockers when later accepted evidence supersedes them.

## Pinned repository sources

All paths below refer to the planning baseline. Internal source/run/artifact bindings inside measured files remain the producing identities; the planning baseline is not substituted for them.

| ID | Path | Git blob |
|---|---|---|
| R01 | `docs/00-FOUNDING-BRIEF.md` | `27833137d8060966947804897388f8b64082dd3e` |
| R02 | `docs/10-CANONICAL-JOURNAL-CONTRACT.md` | `6f843bf1423caf4f1fb82ee045654051ba30d829` |
| R03 | `docs/13-STEP-CONFORMANCE-CONTRACT.md` | `ec2ed117dcced4830f5d9836fa9088b1ad1218c0` |
| R04 | `research/rcs-021/measured-summary-v1.json` | `b5f0cd8c06fdde15680e4a25da36cf81d762f996` |
| R05 | `docs/35-GENESIS-V2-SYNTHESIS-AND-GATE5.md` | `ef5cb4b42edfd27b945731beca333ca072b8d802` |
| R06 | `docs/37-GENESIS-V2-BOOTSTRAP-CONSISTENCY.md` | `2babf5bd450950d446622bae962f66729b2358a0` |
| R07 | `research/rcs-021/material_oracle.py` | `18a54212fcab0634c54d7516916267fb2a4cbbac` |
| R08 | `research/rcs-021/manifold_fallback.py` | `f6bc5cd0624f43201ccc46e7124342e669ce310a` |
| R09 | `research/rcs-021/field.py` | `43dd9dc361bc960190370ba98fe2bb51938e9b58` |
| R10 | `AGENTS.md` | `2ddedabb8f3de9162fccd66ad06d55289228afd1` |

Resolve a pinned source with `git show e86c15ca0479240a0045ebc80c83973137b58c60:<path>` and verify its blob before using it as historical evidence. The adopted RAG authority index distinguishes preserved historical text from current execution rules.

## Claims that may and may not be carried forward

R04 reports fourteen cases: five closed its bounded directional criterion at 0.5 mm and nine remained pending refinement. Two selected refinements at 0.25 mm closed the old 150 mm³ interval criterion; simultaneous XYZ and cut-through did not. These settings cannot be pooled into seven fully qualified end-to-end engineering solutions. The Manifold path executed thirteen cases with reported oracle-interval/body agreement; the 160-segment case was not executed through that adapter, and a small-feature result was resolution-refused as authority.

R07 imports `column_height`, `known_volume` and `removal_field` from R09. R08 supplies R09's `final_field` to `Manifold.level_set`. Thus they are useful alternatives to OCCT but do not independently derive the sweep mathematics. R07 connectivity is an XY occupancy flood fill using column height. R09's rounded routine explicitly rejects varying Z. Its epsilon/finite-iteration floating implementation and caller-supplied oracle error are not imported as MC-1 certified arithmetic without proof and independent tests. These are inspected source properties, not a claim that all prior results are wrong.

RCS-018/025 demonstrate deterministic semantic/coordinator composition, not native fallback-to-B-rep completeness. RCS-026's 100k event tier is coordinator/platform evidence, not 100k independently established geometry changes. RCS-022/027 provide native export/read-back and bounded parser/consumer observations; Layer D remains `interoperability_unqualified`.

Historical comparison pins are OCCT `8.0.1` at `b8f597c677811d1f9f4d8a97f5ae2825c0353a42` and Manifold `3.5.3` at `0edd9d54876f3135e431575214dd6d8a72866fee`. New dependencies/versions need exact source/build-feature/license/notice manifests and differential qualification. Live documentation is not a lockfile.

## External primary references and reading limits

| ID | Primary source | Use and limit |
|---|---|---|
| T01 | [CGAL Nef polyhedra](https://doc.cgal.org/latest/Nef_3/index.html) | Inspected regularization and manifold conversion restrictions; polyhedral facts do not prove curved machining coverage. |
| T02 | [Basu, real algebraic geometry survey, v1](https://arxiv.org/abs/1409.1534v1) | Record/abstract identifies quantifier elimination/topological algorithms; full theorem instantiation is MC-006 work, not completed here. |
| T03 | [Cheng, Gao, Li, singular algebraic-surface meshing, v1](https://arxiv.org/abs/0903.3524v1) | Record/abstract distinguishes singular and regular processing; hypotheses and full proof still need inspection. |
| T04 | [CGAL kernel](https://doc.cgal.org/latest/Kernel_23/index.html) | Predicate/construction exactness distinction; not end-to-end certification. |
| T05 | [Manifold official documentation](https://manifoldcad.org/docs/html/index.html) | Mesh Boolean/LevelSet capabilities; no implied continuous-sweep or B-rep qualification. |
| T06 | [OpenVDB overview](https://www.openvdb.org/about/) | Sparse-volume/level-set tooling, not certified nominal topology. |
| T07 | [CGAL isosurfacing](https://doc.cgal.org/latest/Isosurfacing_3/index.html) | Inspect adaptive assembly assumptions/crack limitations before adoption; no blanket rejection of adaptive methods. |
| T08 | [NIST STEP analyzer](https://www.nist.gov/services-resources/software/step-file-analyzer-and-viewer) | Syntax/entity/validation inspection differs from independent engineering-use/material proof. |
| T09 | [OCCT STEP translator](https://occt3d.com/dev/doc/overview/html/occt_user_guides__step.html) | Profile implementation reference; check against the exact selected build. |

Consulted during this adoption/source-plan review; full paper proofs were not read or certified here. Every future research report records the exact sections/theorems actually inspected and any unresolved applicability. Do not cite a title/abstract as if it proved a required construction.

## Operational references

[GitHub token permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token), [milestone REST API](https://docs.github.com/en/rest/issues/milestones), [repository contents API](https://docs.github.com/en/rest/repos/contents), and [workflow triggering](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow) inform the bounded idempotent planning synchronizer. It never dispatches native jobs or creates production repositories.

The exact-baseline read-only inventory ran as GitHub Actions run `35472758067`, source `3fd3afec86106838f303579b70cf4e88088931dc`. Its archive SHA-256 is `32eea8e0d9aace2f726d09f9f72942ebba36848e7c583def5a21baf4cd48cfc3`; downloaded inventory ZIP SHA-256 is `4ea10ab177d7f483bf8030d376ed723269fbcc97e35979ba78bef66d2139b2ca`. This is source/platform inventory evidence only. The earlier inventory run `35472739082` collected data but failed artifact publication because the explicitly scoped hidden directory was omitted; the publication configuration was corrected, not counted as a successful retained artifact.
