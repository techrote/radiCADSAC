# Authority and recoverability ledger — R1 delta

This extends, and does not replace or silently rewrite, `prior/2A/AUTHORITY_LEDGER.md` and its machine records. The source selector is unchanged. Remote refs were read once; no final lock or publication check is claimed.

| Reference | Observed commit | Root tree | R1 disposition |
|---|---|---|---|
| main | `9734776b3cef3d7039be9623e8872df2c2a85174` | `b0240e4d02a6165f8799d7af432ea36416009667` | Live ref unchanged; immutable tree reused from verified 2A |
| mc038/pb00701-v54-recovery | `823a8624739c337aeb41470cfebebd2ea2a931ca` | `99f93a6c2dcc5e60965ceefc9a5e9ec25409f4bd` | Unchanged; only recovery scaffold per preserved comparison |
| mc038/pb00701-v54-finite-owner-coverage | `8cec4953dc898e70270c654f5453b108bb80d47b` | `6afc28d6b83f5c631b63c67d3e9b1ad93188e6a2` | Unchanged; baseline workflow and incomplete staging per preserved comparison |

## Current instructions and issue

AGENTS.md and `docs/machining-completeness/07-EXECUTION-PROTOCOL.md` were reread completely at the selected immutable commit; their reported blobs match prior records. They are reading evidence, not additional newly exported files. `handoffs/current-authority.json` was read from the retained hash-verified bytes. The current user's recovery-only and read-only contract overrides remote publication, ownership announcements and full-verifier requirements in older execution instructions for this chunk; acceptance requirements are not waived.

The complete #275 body was reread. State OPEN, comments 5, updated 2026-10-03T10:10:22Z match the prior packet. Existing comments and their contradictions were reused from the verified packet rather than reread as an opening audit. No newly published work was identified on the inspected refs or issue. No global search for arbitrary unnamed branches/PRs was performed. The prior branch-specific no-PR results and PR273/274 acceptance records remain historical evidence, not newly queried results.

## Accepted baseline versus unaccepted work

The accepted bounded v53 implementation is `a13702b28fcc349442e78cfb1e971eb94991a69e`, checked tree `17fe7642600b12edd573e21b57933e5811cea991`, followed by the documentation-only PR274 reconciliation at selected main. PR273/274 and #271/#100 acceptance metadata are retained under `prior/2A/records/`. No CI result was fetched or rerun in R1. No historical inventory counts or adapter claims become verified through source recovery.

The malformed staging archive and expired source exports were neither retried nor recreated. No recoverable accepted v54 source was obtained; this increment consists exclusively of authoritative unchanged predecessor files at main. The historical two workflow files are preserved separately from main code and are not enabled or run locally.

## Evidence endpoints and authentication boundary

The fresh reads are recorded with URLs and response identifiers in `records/authority-refresh.json`. Source reads used authenticated `GitHub.fetch_file` at the selected immutable commit, followed by a local `sha1("blob " + length + NUL + bytes)` match. SHA-256 is independently recorded for portability. This authenticates individual file content against connector-reported blob/ref identities; it does not verify a complete Git tree, commit ancestry or a new acceptance decision.
