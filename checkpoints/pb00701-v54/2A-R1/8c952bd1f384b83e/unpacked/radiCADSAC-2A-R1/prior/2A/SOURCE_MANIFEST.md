# Source manifest and completeness statement

## Retained source

`records/exported-blobs.json` is the manifest of eight complete original files. `logs/source-blob-check-final.json` gives every byte count, expected/actual Git blob SHA-1, local SHA-256 and match result. `tools/check_source_blobs.py` reproduces those checks without Git history, network access or repository execution.

The main-source baseline is `9734776b3cef3d7039be9623e8872df2c2a85174`. Files from the two candidate branches are stored separately under `source/forensic/` and `source/recovery/`, never overlaid onto main. All retained original bytes match their fetched Git blob identity; no unverified compressed/inline implementation fragment is included as source.

Retained files are the v53 model, checker, verifier and JSON boundary; original v7 coupled B-spline model; current-authority JSON; and both existing v54-named scaffolding workflows. The local v53 model and v7 module are **not import-ready** because required predecessor dependencies are absent. Only the verifier's import-only path was tested.

## Read but not necessarily exported

`records/source-reading-manifest.csv` and `.json` list 22 main files with immutable Git blob identities, stable source URLs, exact complete/partial reading coverage, purpose and whether full bytes are retained locally. A connector-reported full-file SHA on a range response is not a local whole-file hash check; the manifest distinguishes the two.

The complete #275 body/comments, #271 body/comments and #100 body/relevant final comment were read. Structured claim/acceptance records are normalized observations, not claimed verbatim raw API archives. The other 66 #100 comments and historical Genesis/founding contracts were not reread. See `records/coverage-and-limitations.json`.

## Trees, archives and provenance limits

Current commit/tree identities were obtained from live read-only API metadata. The `.v54-bootstrap` subtree's complete six-entry metadata was independently reconstructed to its Git tree hash. Its individual blob contents were not downloaded. The MC-038 task-directory listing was truncated by the tool response and was not exported or treated as complete.

**No complete main Git tree, tracked-source archive or Git history was recovered locally.** Individual hash-verified files do not establish snapshot completeness. The packet archive is complete relative to its own file/hash manifest, not a complete repository export.

Known historical source archives were not accessible from their current run artifact listings. There was no repeated archive repair attempt, workflow dispatch, CI rerun or malformed-payload execution.
