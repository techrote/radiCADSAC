# Authority and recoverability ledger — chunk 2A

## Status and evidence vocabulary

**PARTIAL: authority and recoverability reconciled; complete executable source recovery not established.** The observation window is 4 October 2026. Mutable refs were read once near the start rather than polled. Full source identity and reading limits appear in the machine-readable manifests.

**Verified record/source fact** means directly inspected repository bytes, API metadata, a decoded historical job log, or an independently matched local Git object hash. **Reported claim** means a comment/report's assertion of a previous local result not replayed here. **Interpretation** is explicitly identified. **Unknown** is not treated as either success or proof of absence. GitHub's commit-signature verification flags are reported metadata, not an independent local signature audit.

## Current authority order

The user's current bounded, read-only 2A contract governs execution and supersedes the issue's full landing instructions for this turn only. Acceptance requirements remain in force for any eventual v54 result.

`AGENTS.md` selects `handoffs/current-authority.json`, which routes to DR-0026 and MC-1's programme/execution protocol. These identify MC-1 as pre-production and `NOT_ESTABLISHED`. #275 supplies the scoped finite-owner task. Actual accepted source, the #271/#100 acceptance records and matching historical CI metadata establish the predecessor. Current-state documents are navigation, not a substitute for acceptance evidence; older speculative/completion comments cannot override the actual published tree.

The current protocol, DR-0026, programme, roadmap, selected task and dedicated implementation ledger were read. The inherited Genesis/founding documents listed in AGENTS were not all reread; `records/coverage-and-limitations.json` records that gap. This is not a full programme/foundation audit.

## Commit/tree ledger

| Ref / role | Commit | Root tree | Direct parent / disposition |
|---|---|---|---|
| Live `main`, PR #274 reconciliation | `9734776b3cef3d7039be9623e8872df2c2a85174` | `b0240e4d02a6165f8799d7af432ea36416009667` | `a13702b28fcc349442e78cfb1e971eb94991a69e`; only two ledger files changed |
| Accepted v53 implementation, PR #273 | `a13702b28fcc349442e78cfb1e971eb94991a69e` | `17fe7642600b12edd573e21b57933e5811cea991` | `7126dabf013ef95b0965b74008466e12f0650ef8`; bounded v53 accepted |
| Existing recovery branch | `823a8624739c337aeb41470cfebebd2ea2a931ca` | `99f93a6c2dcc5e60965ceefc9a5e9ec25409f4bd` | Live main; +1 workflow only |
| Existing forensic staging branch | `8cec4953dc898e70270c654f5453b108bb80d47b` | `6afc28d6b83f5c631b63c67d3e9b1ad93188e6a2` | `acc79884eb872344b2544f00e0cac0140f79fecd`; ahead main by seven commits, workflow + six chunks |

The exact commit API URLs are retained in `records/authority-ledger.json`. The complete changed-file lists returned for these small comparisons are in `records/branch-comparisons.json`. No complete root-tree export was reconstructed locally.

## Accepted v53 evidence

[PR #273](https://github.com/techrote/radiCADSAC/pull/273) is merged, with final head `e4d5646fd3b16e0f152c70fd817904df74426a8b`, original base `7126dabf013ef95b0965b74008466e12f0650ef8`, and merge `a13702b28fcc349442e78cfb1e971eb94991a69e`. The PR lists nine changed files. [PR #274](https://github.com/techrote/radiCADSAC/pull/274) is merged at current main; its head is `eb7b94500a3fc216a1834566364add8e6093aa5e`, and it changes only the Markdown and JSON current-state ledgers.

The complete [#271 acceptance comment 5958928408](https://github.com/techrote/radiCADSAC/issues/271#issuecomment-5958928408) and relevant [#100 comment 5958929084](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-5958929084) explicitly accept only bounded v53. #271 is closed as completed; #100 remains open.

| Evidence | What was independently read in 2A |
|---|---|
| Final v53 focused `37040746459`, static `37040746380` | PASS reported in accepted issue/PR records; full run logs not reread here |
| Merged v53 focused `37041568030`, job `110952689911` | Live check metadata: completed/success, exact implementation merge head |
| Merged v53 static `37041567973`, job `110952689742` | Live check metadata: completed/success, exact implementation merge head |
| Reconciliation PR static `37048706057` | PASS reported in acceptance ledger, not independently requeried |
| Current-main validation `37048808608`, job `110976772764` | Live check metadata: completed/success, exact current-main head |

The accepted report describes seven direct and fourteen integration test methods. Their historical execution is not a fresh local test result. This turn did not recheck every final-head/tree equality asserted by the historical acceptance ledger; the current and implementation root-tree identities and documentation-only transition were independently inspected.

## Existing v54 branches and evidence

The all-state, branch-specific PR queries return empty arrays for both named v54 branches. This is precise branch-specific evidence, not a global assertion about every possible branch or deleted unpublished work. The issue search service unexpectedly returned a plain issue for an `is:pr` query and was not used as absence proof.

The current forensic head's message says `stage reviewed implementation payload 6/10`. Its `.v54-bootstrap` tree has six blobs, each 8,000 bytes. The directory tree metadata was independently hashed. No remaining part is present in that complete directory listing. The wording “reviewed” in a commit message does not establish that any contained implementation passed its acceptance contract.

The recovery workflow fetched that forensic branch and decoded those six chunks. The complete historical job log was read once using the dedicated read-only log tool. At `2026-10-03T07:50:44.9613355Z`, gzip reports an unexpected end of file, and the step exits 1. The tar extraction/upload does not complete. See `logs/recovery-job-111159336398-excerpt.txt` and [run 37107690114](https://github.com/techrote/radiCADSAC/actions/runs/37107690114).

This confirms that the published six-part stream failed the recorded recovery procedure. It does not establish that no individual file could ever be salvaged. No fragment from that malformed stream is used as implementation authority here.

## Historical exports and present source access

The v54-named baseline workflow actually checks out exact main and runs the complete **v53** verifier; its filename is not evidence of v54 acceptance. The success of [run 37050900358](https://github.com/techrote/radiCADSAC/actions/runs/37050900358) was verified via job metadata. The workflow uploaded a tracked-source archive with one-day retention. Its current artifact list is empty.

The earlier v53 baseline [run 37033679813](https://github.com/techrote/radiCADSAC/actions/runs/37033679813), which once supplied artifact `11238467420`, also has an empty current artifact list. That old archive's SHA-256 and reproduced tree are claims in the accepted v53 report, not a currently available local export. No workflow was dispatched to recreate it.

Direct local HTTPS access failed at DNS resolution. Read-only connector access successfully retrieved immutable individual files. Eight full original files were persisted and matched against Git blob IDs; the result is reusable but incomplete. Source files remain available through this access route even though old exported archives are unavailable.

## Contradictions resolved or retained

The old roadmap and historical MC-038 report still call v52 the latest frontier. Dedicated v53 ledgers, merged PR metadata, commit comparison, acceptance records and live merged-main checks establish v53 as the later accepted bounded implementation. The old text remains historical; no rewrite was attempted.

The current-state ledger's “no successor selected here” is a dated v53 navigation statement. It does not negate the later live #275 task. Conversely, #275's existence and later comments do not establish v54 implementation or acceptance.

Counts and adapter completion remain unresolved beyond the explicit v53 interface constants. Published branches contain staging, not an inspectable canonical v54 inventory. The conservative no-acceptance conclusion is corroborated; the numerical classification and replay claims cannot yet be corroborated.

**Programme state remains unchanged:** PB-007-01 OPEN globally; MC-B/MC-1 NOT_ESTABLISHED; all 26 operations retained. No native material/topology/STEP capability follows from accepted deterministic-model event evidence.
