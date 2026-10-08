# radiCADSAC — PB-007-01 v54 baseline reconciliation packet

**Chunk 2A: PARTIAL.** Start with [CHECKPOINT.md](CHECKPOINT.md).

This packet preserves verified read-only findings and a partial set of authenticated original files. It is not a repository checkout, a complete Git tree, a v54 implementation or acceptance evidence.

- [Authority ledger](AUTHORITY_LEDGER.md): live refs/trees, accepted v53 evidence, existing v54 scaffolding and contradictions.
- [Artifact inventory](ARTIFACT_INVENTORY.md): published, unaccepted, claimed/unavailable and bounded-absence distinctions.
- [Source/dependency map](SOURCE_DEPENDENCY_MAP.md): exact residual fixture and producer/checker entry points, amplitude sign versus strict derivative, and missing audit inputs.
- [Claims reconciliation](CLAIMS_RECONCILIATION.md): incompatible #275 count/completion assertions remain unverified.
- [Source manifest](SOURCE_MANIFEST.md) and [commands/results](COMMANDS_RESULTS.md): retained bytes, actual read/test coverage, negative results and limitations.

`records/` contains normalized source/authority/evidence metadata. `findings/` includes a static source-symbol index and the direct missing-import frontier. `source/` keeps main and the two candidate-branch exports separate. `tools/` contains local integrity/indexing scripts; none accesses GitHub or runs a full proof suite.

`SHA256SUMS` covers every other file in this packet. Its own digest is excluded to avoid self-reference; the outer ZIP SHA-256 and full archive/extraction check are provided in the accompanying verification JSON. `python tools/verify_packet.py .` validates an extracted copy, including exact file-set equality.

The next direction is **source recovery**. No successor prompt was written and no successor work was executed. Preserve 26 operations, original-source binding, historical owners and refusal semantics. PB-007-01 remains OPEN globally; MC-B/MC-1 NOT_ESTABLISHED.
