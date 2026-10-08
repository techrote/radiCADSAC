# radiCADSAC 2A-R1 recovery packet

Start with **CHECKPOINT.md**. Status is PARTIAL; the ten-file increment is recovered but the exact fixture cannot yet import.

`prior/2A/` preserves the verified preceding 53-file packet unchanged, including its original source/reading manifest and acceptance/claims evidence. `source/` is the cumulative usable partial export; `source/main/` preserves repository-relative layout, including the actual MC-032 path-loaded engine. `source/forensic/` and `source/recovery/` are historical workflow scaffolds only. Do not enable or dispatch them.

Current records are `records/source-manifest.json`, `records/authority-refresh.json`, `records/dependency-map.json`, `records/residual-recovery-queue.json` and `records/readiness.json`. Human navigation is SOURCE_MANIFEST.md, SOURCE_DEPENDENCY_MAP.md, AUTHORITY_LEDGER.md, FINDINGS.md and COMMANDS_RESULTS.md.

To verify a freshly extracted packet without importing repository code:

```sh
python3 -I -B tools/verify_packet.py .
```

The archive verification JSON supplied alongside the ZIP separately binds its SHA-256 and member checks. Successful package verification means only that the exported bytes are intact. This is not a full Git checkout, complete predecessor closure, proof result or v54 acceptance.

The smoke runner is retained for reproducibility, but its recorded R1 execution was once only and failed; do not assume a later run has already happened. No successor prompt is included.
