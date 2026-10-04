# SAVE-README — PB-007-01 v54 / 2A-R1 partial Git preservation

**Publication status: PARTIALLY_SAVED.** This is inactive archival checkpoint material only.

The completed 2A-R1 recovery turn remains substantively **PARTIAL / MORE_NAMED_SOURCE_RECOVERY_NEEDED**. The assessed/source commit is `9734776b3cef3d7039be9623e8872df2c2a85174` (tree `b0240e4d02a6165f8799d7af432ea36416009667`); live `main` matched it at save preflight.

Payload ID is `8c952bd1f384b83e`, derived from SHA-256 `8c952bd1f384b83eae3200fc7a944010ac00a4218115f79ac5acb06c89b450d7` over the sorted 105-entry original packet path/hash manifest.

## Saved remotely and verified by identity

- exact `CHECKPOINT.md` bytes;
- exact standalone packet-verification JSON bytes;
- all 18 retained source entries, each stored under `recovered-source/<local_path>` by reusing the Git blob SHA recorded by the original source manifest;
- `SOURCE-PROVENANCE.json`, `RESTORE-MAP.json`, `SAVED-PAYLOAD-SHA256SUMS`, and this publication handoff.

## Not fully saved remotely

The exact 218,929-byte packet ZIP could not be transported as a single verified Git blob through the connector in this bounded save. A first attempted branch revealed blob-identity mismatches for the ZIP and dependency-map transfer during readback, so it is **not** treated as the verified checkpoint. The exact packet remains available as the fallback artifact with SHA-256 `72eaa52c10be6951ec4ca68a8813fab6bb920da575b437a9bb82ea35762272d2`, ZIP CRC PASS, 106 members.

Consequently, the remote partial save does not independently contain the full command/output set, residual-queue JSON, loose dependency map, or prior 2A packet material; those remain inside the exact fallback packet. Their omission is explicit rather than reconstructed from prose.

## Historical result preserved

The R1 import-only smoke exited 1 with `ModuleNotFoundError: No module named 'pb00701_algebraic_endpoint_model'`. No fixture factory, reversed-v53 residual case, test method, contract verifier, or full predecessor chain ran. There is no new runtime owner/sign/refusal evidence. The visible 15 missing-module references are not a complete transitive dependency count or owner count.

PB-007-01 remains OPEN; v54 acceptance is unestablished; MC-B/MC-1 remain NOT_ESTABLISHED; all 26 operations remain protected.

## Next action

Use the exact fallback packet to resume another bounded authoritative-source recovery increment beginning with `pb00701_algebraic_endpoint_model.py` and the statically named `pb00701_algebraic_endpoint_certificate.py`, inspecting their imports before expansion. Do not start owner enumeration from this partial closure.
