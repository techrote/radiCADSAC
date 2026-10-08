# Actual-artifact inventory — v54 recovery baseline

This inventories recoverability, not owners. “Absent” is bounded to the inspected directory or branch delta, never inferred from a truncated repository tree.

| Artifact group | Classification | Evidence / limitation |
|---|---|---|
| Recovery helper `.github/workflows/mc1-pb00701-v54-recovery-bootstrap.yml` | **Committed and inspectable; unaccepted scaffolding** | Exact local bytes match blob `849bdbbbaf9a2a1e569bb199e2414c909eaa4776`; only recovery-branch addition |
| Baseline `.github/workflows/mc1-pb00701-v54.yml` | **Committed and inspectable; not v54 verification** | Exact local bytes match blob `bb0fbd6a766bb06f3f68bb282a76d444f4c62c4b`; checks out main and runs v53 |
| `.v54-bootstrap/part00`–`part05` | **Committed opaque staging, payload unaccepted** | Complete six-entry metadata and blob IDs retained; each 8,000 bytes; no local content/decompression/salvage attempt |
| Parts beyond `part05` in the staging directory | **Absent from inspected complete directory metadata** | Tree `a8ea1728d54bc7c0b00f5bfca7e0694b7500c960`, `truncated:false`; final commit's “6/10” suggests an incomplete intended export, but is not a payload manifest |
| Valid standalone v54 model/adapters/checker/tests | **Claimed/unavailable; no such additions in either named branch delta** | Claims of local work are not backed by published implementation paths in the inspected comparisons; no valid recovered code established |
| Canonical v54 owner inventory, report, boundary and evidence results | **Claimed/unavailable** | Historical numerical statements exist, but no accepted source-bound inventory bytes were recovered |
| Alleged corrected v54 discontinuity test | **Claimed/unavailable** | v52's runtime string is independently visible; the test and proposed change are not available for review |
| Valid recovered-but-unaccepted v54 adapter implementation | **None demonstrated in this chunk** | Not equivalent to proof that partial salvage is impossible; no malformed fragment promoted |
| v54 PR or landing on the two named branches | **Absent in the all-state branch-specific PR queries** | Both queries returned `[]`; global unknown branches/deleted local work not covered |
| Historical main source export, run `37050900358` | **Previously reported/exported; unavailable from current artifact listing** | Successful upload metadata; one-day retention configured; zero artifacts now; former local tree replay not reproduced |
| Earlier v53 export artifact `11238467420`, run `37033679813` | **Previously reported; unavailable from current run listing** | Zero artifacts now; no archive bytes available locally |
| Accepted v53 model/checker/verifier/boundary | **Committed, read completely, retained and blob-verified** | Four files under `source/main/.../MC-038`; acceptance belongs to v53 only |
| Original v7 coupled B-spline/amplitude model | **Committed predecessor, retained and blob-verified** | `a086b625e1a6dea8bd202699d161167bb69cc9e7`; no implementation edits |
| v53 report and RAG document 78 | **Committed and inspectable; fully read but not exported here** | Immutable SHA/URLs in source-reading manifest |
| v52 lowering/continuity, v51 ordering, v50 strict router, v53 fixture/tests | **Committed and inspectable; selectively read; local full bytes missing** | Exact read ranges and remote blob IDs retained; not an executable local chain |
| Complete main tree/history | **Not recovered locally** | Partial file export must not be labelled a checkout or a reproduced root tree |

## Exact missing inputs

The direct local import frontier is in `findings/local-import-frontier.json`. Four retained Python files have eight direct missing module files across module-level and lazy imports. The complete transitive closure has not been established.

For the actual reversed-source residual, obtain complete `test_pb00701_mixed_owner_span_integration.py`, `test_pb00701_mixed_owner_span.py` and `test_pb00701_piecewise_product.py`, plus the model/checker/arithmetic chain described in `SOURCE_DEPENDENCY_MAP.md`. The original fixture encoder and transformation must not be replaced by a handwritten approximation.

For the canonical owner audit, the fixed historical classifier chain and its actual route emitters/checkers must be inspected after recovery. Neither old count table is a substitute for those source bytes. Historical comments do not provide enough material to treat 20, 30, 41 or 43 as verified inventory totals.

## Access boundary

GitHub connector reads work; direct shell GitHub DNS does not. Both known source-export runs have empty artifact listings. No exporter was dispatched, no remote branch was modified, and no opaque staging payload was executed. A locally serialized v7 file initially failed its blob check due to a text-transfer parenthesis error; the mismatch was corrected against the fetched original and the final bytes match exactly. The failure is recorded, not hidden as a successful first transfer.
