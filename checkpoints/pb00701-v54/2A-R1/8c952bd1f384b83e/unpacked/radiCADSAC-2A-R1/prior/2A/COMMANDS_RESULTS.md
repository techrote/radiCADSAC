# Commands, reading batches and results

## Execution boundary

Start recorded at **2026-10-04T14:59:15Z**. Isolated workspace: this packet root. No sibling repository or existing agent tree was modified. The only repository service operations were reads: fetch/fetch_file, issue/comment reads, branch comparisons, PR metadata, check/job metadata and one historical decoded job log. No remote write endpoint, dispatch/rerun, setting change, native test, GPU or USB operation was invoked.

Connector calls do not expose a per-call timeout setting. They were finite individual reads and bounded pages/ranges, not polling. Local shell commands used explicit tool timeouts, generally 10 or 20 seconds; the initial HTTP probe additionally used `timeout 30`, curl `--max-time 25` and `--connect-timeout 8`. No unbounded shell read or verifier was run.

## Finite read batches

1. Read AGENTS/current authority, issue #275 complete body and all five comments, current branch identities, current execution and implementation authority. Long comment responses were completed using bounded individual-comment pages.
2. Compare main against both existing v54 branches; inspect their committed workflows. Read the baseline run's jobs/artifacts and the failed recovery run's jobs/log once. Inspect complete six-entry staging directory metadata; independently rehash its tree entries locally.
3. Read accepted v53 model/checker/report/boundary/verifier, #271 complete body/comments, #100 body and its final acceptance comment, PR #273/#274 metadata. Compare the accepted implementation merge with current main. Read merged-v53/current-main check metadata once each; do not poll.
4. Inspect original v7 amplitude/source logic, selected v52/v51/v50 routing/boundaries and v53 fixture/test ranges. Retain verified original files. Stop without running the residual or enumerating owner families.

The exact file coverage and source URLs are in `records/source-reading-manifest.csv`. API result summaries are in the other `records/` files. These are curated observations; this packet does not claim to contain every raw tool response.

## Commands and actual results

| Command / operation | Bound | Result |
|---|---|---|
| Initial direct `curl` of GitHub branch/main | outer 30 s; curl 25 s / connect 8 s | DNS failure, HTTP 000; log retained; no clone or credential workaround |
| GitHub code search for existing v53 source | One query | Empty despite independently fetched existing file; not used as absence evidence |
| All-state PR queries by each named v54 branch | One query each | `[]` for both; global branch universe not asserted |
| Generic job-log / single-artifact metadata fetch | Individual read attempts | Rejected endpoint forms; no bypass. Dedicated job-log read worked; supported run artifact listings returned zero. |
| Persist original UTF-8/JSON source; `python tools/check_source_blobs.py` | 20 s tool timeout for batch | Eight final files match original Git blob IDs; local SHA-256 also recorded |
| `python tools/retain_contract_sources.py` | 20 s batch | Current-authority and v53 boundary JSON retained byte-identically; source hash assertions passed; no repository code executed |
| v7 source text-transfer validation | Finite local comparison | Initial mismatch caught; a parenthesis transcription error corrected against fetched source; final original blob `a086b625…` matches. No remote/source-semantic edit. |
| `PYTHONDONTWRITEBYTECODE=1 timeout 10s python tools/import_smoke.py` | 10 s | **PASS**, once. Imported only v53 verifier definitions; no `contract`, `self_test`, predecessor module or fixture execution |
| `PYTHONDONTWRITEBYTECODE=1 timeout 10s python tools/index_recovered_source.py` | 10 s | Parsed four retained Python files; produced symbol/import index and eight direct missing module paths. Not owner enumeration or a transitive graph. |
| Reconstruct staging Git tree hash from six returned entries | 20 s batch | Exact `a8ea1728d54bc7c0b00f5bfca7e0694b7500c960` match. Does not authenticate unread blob contents by itself. |
| Packet file-hash/ZIP CRC/extraction checks | Finite local packaging script | Results in the separately linked archive verification report; reproducible extracted-file verification script included |

## Tests deliberately not executed

No complete v53/v52 or predecessor verifier. No current or proposed v54 test. No reversed-source replay. No owner-wide fixture/classifier evaluation. No proof regeneration, derivative selection, adapter implementation, native campaign or shared-resource test.

Historical CI success/failure is explicitly distinguished from local tests in `records/evidence-runs.json`. The failed recovery log excerpt is only an excerpt of the fully read historical log. It does not become a local decompression test.

## Reproduction inside an extracted packet

```sh
python tools/check_source_blobs.py
python tools/verify_packet.py .
```

Both validate the packet, not PB-007-01. The single import-only smoke source is included for inspection. Do not invoke the retained repository verifier with `--contract --self-test` from this sparse source tree and describe missing-dependency failures as theorem failures.
