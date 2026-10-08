# Current authority and RAG reading index

Status: current routing under DR-0026. Every retrieval/implementation agent must distinguish a statement's historical phase from current execution authority.

## Authority order

The current explicit user mandate as recorded in DR-0026 and `handoffs/current-authority.json` governs MC-1. Read 00-PROGRAMME, the relevant specification and 07-EXECUTION-PROTOCOL next. The task graph defines work ownership and dependencies; outcome/gate/PO registries define evidence status, not GitHub issue closure.

Preserved founding invariants and versioned journal/body/provenance/uncertainty contracts remain applicable unless an explicit later accepted decision changes a named part. The new domain/precision/profile investigations do not silently reinterpret old saved journals or v2 package identities.

## Reading routes

| Question | Read |
|---|---|
| What is authorized now? | DR-0026, `handoffs/current-authority.json`, 00-PROGRAMME |
| Which task may run and who owns it? | 07-EXECUTION-PROTOCOL, 12-ROADMAP, task graph and live issue/PR |
| What machining and numerical meaning must survive? | 01-DOMAIN-AND-SEMANTICS; existing docs/10 journal contract |
| What is proved versus open? | 02-COMPLETENESS-ARGUMENT; PO/assumption registry; exact reviewed claim artifact |
| Which oracle and fixture detects a wrong answer? | 03-ORACLE-AND-CORPUS; fixture/oracle manifests |
| How should material become engineering geometry? | 04-REPRESENTATION-AND-RECONSTRUCTION; approved profile decision |
| What counts as qualification or authorized compute? | 05-QUALIFICATION; exact protocol/permit and stage evidence |
| What did previous research actually establish? | 08-SOURCES-AND-EVIDENCE; pinned historical source and its internal producing identities |
| What is the current capability decision? | 06-MC1-DECISION and gate registry |
| How is an artifact/claim encoded and checked? | 11-FORMAT-CONTRACTS; programme verifier implementation |

## Historical and retained material

`docs/00-FOUNDING-BRIEF.md`, foundational semantic contracts and accepted invariant decisions remain valuable normative inputs, interpreted with the explicit MC-1 overlay. `docs/04-REVISED-RESEARCH-ROADMAP.md`, `docs/07-RESEARCH-ISSUE-GRAPH.md`, architecture synthesis, Genesis-v2 roadmap/synthesis/delta/bootstrap-consistency documents describe their completed historical phases. Current-read wrappers carry a notice where necessary; source evidence remains available at its original commit/blob.

The v1 and v2 handoff trees, release/evidence manifests and launch specifications are preserved historical foundation, not present permission to bootstrap a production repository. All wording such as current, next or production-owned inside a preserved historical record is scoped to that record's phase, not a silent override of DR-0026.

Research RCS-001–027 source/results remain historical evidence. A model/native distinction, unqualified consumer result or negative experiment must travel with any retrieved excerpt. Do not detach optimistic summary language from its explicit scope or later consistency correction.

## Document contract

Each substantial new report states purpose/domain, assumptions, method, source facts, hypotheses, positive/negative findings, exact source/configuration, evidence class, unresolved obligations, implications and next action. Small standalone headings and stable links make it usable without chat history. External abstracts are marked as abstracts, dependency documentation is not a build pin, and proposed settings are not customer requirements.

The generated `authority-map-v1.json` inventories current and historical Markdown paths and their routing class. New documents must be registered; an unclassified current-entry document is a consistency failure. Preserve large shared material here instead of copying it into every issue.

## Preserved PB-007-01 v54 recovery packets

Evidence class: **SOURCE / archival preservation**. The complete 2A-R1 packet for [issue #275](https://github.com/techrote/radiCADSAC/issues/275) is retained separately from active implementation. Its source recovery remains **PARTIAL**. The [current implementation state](77-MC038-CURRENT-IMPLEMENTATION-STATE.md) remains the v53 authority; this record supplies no v54 acceptance or programme-gate promotion.

| Record | Immutable location | Meaning |
|---|---|---|
| Complete packet archive | [Complete 2A-R1 directory](https://github.com/techrote/radiCADSAC/tree/2858a6c41cc8b3347de7eb3c74df429793db472e/checkpoints/pb00701-v54/2A-R1/8c952bd1f384b83e) | 114 files: six supplied originals, all 106 original R1 members and two new preservation documents. The new manifest covers 113 entries, excluding itself. |
| Earlier canonical partial checkpoint | [`ef4addd2`](https://github.com/techrote/radiCADSAC/tree/ef4addd2f671a9a7491838b0218441186809b954/checkpoints/pb00701-v54/2A-R1/8c952bd1f384b83e) | Retains 19 mapped original members plus one external receipt with exact bytes and modes; it did not preserve the complete packet hierarchy. |
| Earlier noncanonical attempt | [`e10c0d79`](https://github.com/techrote/radiCADSAC/tree/e10c0d79e5001b81d1a115c7c2950bba4aaa2d1e/checkpoints/pb00701-v54/2A-R1/8c952bd1f384b83e) | Its `ORIGINAL-PACKET.zip` and `SOURCE_DEPENDENCY_MAP.md` do not match the authenticated originals. Retained for provenance, not as the source of the complete archive. |

The complete archive is on `checkpoint/radicadsac-2a-r1-8c952bd1f384b83e-complete`. Read its [preservation record](https://github.com/techrote/radiCADSAC/blob/2858a6c41cc8b3347de7eb3c74df429793db472e/checkpoints/pb00701-v54/2A-R1/8c952bd1f384b83e/PRESERVATION.md) and [manifest](https://github.com/techrote/radiCADSAC/blob/2858a6c41cc8b3347de7eb3c74df429793db472e/checkpoints/pb00701-v54/2A-R1/8c952bd1f384b83e/PRESERVATION-MANIFEST.json) for exact paths, original receipts, member mappings and historical failures. Earlier branches and original claims remain unchanged.

The original `radiCADSAC-2A-R1-packet.zip` and `radiCADSAC-2A-R1-git-checkpoint-fallback.zip` are byte-identical: **218,929 bytes** each, SHA-256 `72eaa52c10be6951ec4ca68a8813fab6bb920da575b437a9bb82ea35762272d2`. The earlier `radiCADSAC-2A-packet.zip` is **82,825 bytes**, SHA-256 `074e172c6c7995d3022b985a0a06ae1542a0c01b8fb6d06b62210fca3738309d`. All three ZIPs retain their filenames under `originals/`. R1's 106 files are unpacked under `unpacked/radiCADSAC-2A-R1/`; all 53 earlier 2A members already occur there under `prior/2A/`, without a duplicate extraction.

The directory identifier is the first 16 characters of the normalized payload SHA-256 `8c952bd1f384b83eae3200fc7a944010ac00a4218115f79ac5acb06c89b450d7`: 105 original checksum records sorted by relative path and serialized as UTF-8 `path + NUL + lowercase digest + LF` (11,692 bytes). It is distinct from the original `SHA256SUMS` file's byte hash, `d85536f434634f29b1ac61d8861f061524b4c0b6d0d45951fe664f36bdabc894` (11,797 bytes).

The retained recovery increment added ten source files and preserved 18 source entries, including 14 Python files inspected statically. Its historical import smoke exited **1**; no fixture factory, test method, owner enumeration or acceptance verifier ran. The packet's missing-module list is not a complete transitive dependency closure or proof-owner count. Preservation introduces no new runtime owner, margin or refusal result and executes no archived code. PB-007-01 remains open; v54 acceptance, MC-B and MC-1 remain unestablished by this packet. All 26 protected operations retain their meaning and constraints; the production hold remains in force.
