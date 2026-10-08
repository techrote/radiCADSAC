# radiCADSAC 2A-R1 complete packet preservation

This checkpoint preserves the complete existing **2A-R1 packet**, both exact R1
archive filenames, the exact earlier **2A archive**, and all supplied historical
receipts/handoffs. The underlying source recovery remains **PARTIAL**. Preserving
the files does not establish PB-007-01 v54, MC-B or MC-1 acceptance.

## Scope, identity and layout

Repository/task: [techrote/radiCADSAC issue #275](https://github.com/techrote/radiCADSAC/issues/275),
PB-007-01 v54, chunk 2A-R1. The intended additive branch is
`checkpoint/radicadsac-2a-r1-8c952bd1f384b83e-complete`, based on historical
commit `9734776b3cef3d7039be9623e8872df2c2a85174`, tree `b0240e4d02a6165f8799d7af432ea36416009667`. Actual durable ancestry and remote
byte verification are established separately by the publication record.

All six supplied originals retain their filenames under `originals/`:

| Original | Size | SHA-256 |
|---|---:|---|
| [radiCADSAC-2A-R1-packet.zip](originals/radiCADSAC-2A-R1-packet.zip) | 218,929 bytes | `72eaa52c10be6951ec4ca68a8813fab6bb920da575b437a9bb82ea35762272d2` |
| [radiCADSAC-2A-R1-git-checkpoint-fallback.zip](originals/radiCADSAC-2A-R1-git-checkpoint-fallback.zip) | 218,929 bytes | `72eaa52c10be6951ec4ca68a8813fab6bb920da575b437a9bb82ea35762272d2` |
| [radiCADSAC-2A-packet.zip](originals/radiCADSAC-2A-packet.zip) | 82,825 bytes | `074e172c6c7995d3022b985a0a06ae1542a0c01b8fb6d06b62210fca3738309d` |

The original and fallback R1 archives were compared directly and are
byte-identical. The separately supplied packet-verification JSON, Git-save
verification JSON and partial-write handoff also remain byte-for-byte unchanged
under `originals/`; their filenames, locators and hashes are recorded in the new
[PRESERVATION-MANIFEST.json](PRESERVATION-MANIFEST.json).

Every original R1 ZIP member `<path>` is retained at `unpacked/<path>`, including
the original `radiCADSAC-2A-R1/` root component. All **106 original regular files**
have original mode `100644`; there are no directory members, links or special
files. The original [R1 SHA256SUMS](unpacked/radiCADSAC-2A-R1/SHA256SUMS) covers
105 files and excludes itself.

The earlier 2A ZIP has **53 regular files** and **52 checksum entries**. All 53
members are already present byte-for-byte, with matching `100644` modes, under
`unpacked/radiCADSAC-2A-R1/prior/2A/`. The exact mapping is
`radiCADSAC-2A/<path>` in the earlier ZIP to
`radiCADSAC-2A-R1/prior/2A/<path>` in R1. That existing subtree is the useful
unpacked copy of the earlier packet; no redundant second extraction was added.
The exact earlier ZIP remains preserved separately and its original
[SHA256SUMS](unpacked/radiCADSAC-2A-R1/prior/2A/SHA256SUMS) is unchanged.

This layout contains **114 files**: 106 original R1 members, six supplied
original files, and two new preservation documents. The new manifest covers
113 entries and explicitly excludes itself. New preservation metadata remains
outside both original checksum boundaries.

## Checksum identity clarification

The directory identifier `8c952bd1f384b83e` retains the established **normalized
payload identity**. Parse the original R1 checksum file into its 105 relative
path/digest records, sort by relative path, and serialize each as UTF-8
`path`, a NUL byte, its lowercase hexadecimal SHA-256, then an LF byte.
The resulting 11,692 bytes have SHA-256 `8c952bd1f384b83eae3200fc7a944010ac00a4218115f79ac5acb06c89b450d7`; the directory uses its
first 16 hexadecimal characters.

The SHA-256 of the **original SHA256SUMS file bytes** is instead
`d85536f434634f29b1ac61d8861f061524b4c0b6d0d45951fe664f36bdabc894` (11,797 bytes). The 8 October upload brief conflated these
identities; this note corrects that label without changing either original file
or the historical identifier. The naming algorithm is recorded in the earlier
[SAVE-README.md](https://github.com/techrote/radiCADSAC/blob/e10c0d79e5001b81d1a115c7c2950bba4aaa2d1e/checkpoints/pb00701-v54/2A-R1/8c952bd1f384b83e/SAVE-README.md); its [RESTORE-MAP.json](https://github.com/techrote/radiCADSAC/blob/e10c0d79e5001b81d1a115c7c2950bba4aaa2d1e/checkpoints/pb00701-v54/2A-R1/8c952bd1f384b83e/RESTORE-MAP.json)
also records the raw checksum-file hash correctly. These links are provenance
for the naming convention only: that branch's attempted ZIP/map publication
was noncanonical and is not the source of the archive bytes preserved here.

## Earlier partial and failed publications

The prior [canonical partial checkpoint](https://github.com/techrote/radiCADSAC/tree/ef4addd2f671a9a7491838b0218441186809b954/checkpoints/pb00701-v54/2A-R1/8c952bd1f384b83e) remains at
`ef4addd2f671a9a7491838b0218441186809b954`, branch
`checkpoint/radicadsac-2a-r1-8c952bd1f384b83e-partial`, tree
`32ed6e9868df801d8b624fb8b7620ddc322b7c1c`. Its 25 changed paths included 20
verified payload/source objects: 18 retained source entries, the R1 checkpoint
and the external packet-verification receipt. Live comparison confirmed no
content or mode mismatches among those 20 mapped payloads. They represent **19
of the 106 original packet members** plus one external receipt, leaving **87
original logical member paths** outside that mapping. Eight prior-2A source
copies share bytes with the retained source files, so the contents of 27
original member paths were reachable somewhere in the old checkpoint, without
the complete original hierarchy. Those counts do not mean 27 unique source
files or a complete packet. Full dependency-map, command/output, residual-queue
and prior-2A preservation required the complete packet now retained here.

The earlier [noncanonical attempt](https://github.com/techrote/radiCADSAC/tree/e10c0d79e5001b81d1a115c7c2950bba4aaa2d1e/checkpoints/pb00701-v54/2A-R1/8c952bd1f384b83e), commit
`e10c0d79e5001b81d1a115c7c2950bba4aaa2d1e`, branch
`checkpoint/radicadsac-2a-r1-8c952bd1f384b83e`, had incorrect blob identities for
`ORIGINAL-PACKET.zip` and `SOURCE_DEPENDENCY_MAP.md`. Its old success-sounding
statements are historical attempted-publication claims. They do not authenticate
those two files. Its ZIP tree entry is only 8,853 bytes (Git blob
`21df60c9d3985407dde51581241ca03824b0e65e`), whereas the correct supplied ZIP is
218,929 bytes (Git blob `41895aa1ef91f8a6fc36c8cd877e42182f338521`). Its dependency
map has 172 differing bytes despite the same 8,503-byte length; the correct
original map's Git blob is `b42cccee03b98ee3bdba8daae0f42cd038e6ed08`. Both old
checkpoints retain the same 20 correct mapped payloads described above; the
noncanonical files do not fill the remaining gaps. This archive uses the independently authenticated supplied ZIP
bytes and their exact unpacked members, not those incorrect transfers. Both old
branches remain forensic references; this additive layout rewrites neither.

The retained original save receipt and partial handoff describe the earlier
**PARTIALLY_SAVED** publication. They remain true records of that attempt and are
not rewritten to describe this later archive. Their old omissions are distinct
from the research limitations below.

## Retained recovery evidence and limits

The original R1 work completed a bounded **ten-file source-recovery increment**
and retained **18 source entries**, including **14 Python files** inspected
statically. Fourteen is a file count, not an import-site count. Those retained
bytes were rechecked against their recorded SHA-256 and Git blob identities for
this preservation task; that does not establish a complete Git tree or history.

The saved import smoke exited **1** with the missing
`pb00701_algebraic_endpoint_model` module. No fixture factory, reversed residual,
test method, owner enumeration or acceptance verifier ran. The other named
immediate gap is `pb00701_algebraic_endpoint_certificate.py`; neither these two
names nor the **15 visible missing module references** establish the complete
transitive dependency closure or a proof-owner count. Read the original
[CHECKPOINT](unpacked/radiCADSAC-2A-R1/CHECKPOINT.md),
[dependency map](unpacked/radiCADSAC-2A-R1/SOURCE_DEPENDENCY_MAP.md),
[commands/results](unpacked/radiCADSAC-2A-R1/COMMANDS_RESULTS.md),
[readiness](unpacked/radiCADSAC-2A-R1/records/readiness.json), and
[residual queue](unpacked/radiCADSAC-2A-R1/records/residual-recovery-queue.json).

Contradictory historical v54 inventory/adapter counts, broad-test claims, the
reported `97/200` margin and historical target assertions remain unchanged in
the original [findings](unpacked/radiCADSAC-2A-R1/FINDINGS.md) and
[prior claims reconciliation](unpacked/radiCADSAC-2A-R1/prior/2A/CLAIMS_RECONCILIATION.md).
They are retained claims, not new runtime owner, margin or refusal results.
The failed gzip/bootstrap provenance remains at
[`8cec4953dc898e70270c654f5453b108bb80d47b`](https://github.com/techrote/radiCADSAC/commit/8cec4953dc898e70270c654f5453b108bb80d47b)
(`mc038/pb00701-v54-finite-owner-coverage`) and
[`823a8624739c337aeb41470cfebebd2ea2a931ca`](https://github.com/techrote/radiCADSAC/commit/823a8624739c337aeb41470cfebebd2ea2a931ca)
(`mc038/pb00701-v54-recovery`). The archived workflow scaffolds remain inactive.

## Preservation checks performed

This task checked the supplied archives' expected identities, byte equality of
the R1 pair, all member CRCs and safe paths, all 105 R1 and 52 earlier checksum
records, all 53 prior/R1 member correspondences, original modes, the normalized
payload identifier, and the 18 retained source entries' recorded blob identities.
Historical logs and verification files were read as data. No archived program,
verification script, import smoke, test, workflow or command was executed; no
source recovery, owner audit, patch application or new experiment was performed.

Underlying recovery remains **PARTIAL**; PB-007-01 remains **OPEN**; v54
acceptance, MC-B and MC-1 remain **unestablished by this packet**. All 26 protected
operations retain their original meaning and constraints. Current-main archive
navigation and issue-status harmonization are separate publication steps. The
retained source exports stay inside this archive and are not installed as active
implementation.
