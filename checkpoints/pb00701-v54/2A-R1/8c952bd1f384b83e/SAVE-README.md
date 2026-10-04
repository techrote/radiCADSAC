# SAVE-README — radiCADSAC #275 / PB-007-01 v54 / 2A-R1

Inactive archival checkpoint only. This preserves the completed **2A-R1** turn and does not continue recovery, enumerate owners, implement adapters, or establish v54/PB-007-01/MC-B/MC-1 acceptance.

- Source: `techrote/radiCADSAC` #275, PB-007-01 v54, chunk 2A-R1.
- Historical assessed commit: `9734776b3cef3d7039be9623e8872df2c2a85174`; tree `b0240e4d02a6165f8799d7af432ea36416009667`.
- Live `main` matched that commit at save preflight, so there is no main/base delta to integrate.
- Payload ID: `8c952bd1f384b83e`, derived from SHA-256 `8c952bd1f384b83eae3200fc7a944010ac00a4218115f79ac5acb06c89b450d7` over the sorted original 105-entry `path\0sha256\n` packet manifest.
- Canonical payload: `ORIGINAL-PACKET.zip`, SHA-256 `72eaa52c10be6951ec4ca68a8813fab6bb920da575b437a9bb82ea35762272d2`. It is the exact uploaded packet and contains all 106 packet files, including retained earlier 2A material.
- The original verification records 105 manifest entries, 18 source entries checked against Git blobs, and 10 newly recovered files in R1. It explicitly says this is not a complete Git tree and not proof/v54 acceptance.
- `CHECKPOINT.md` and `SOURCE_DEPENDENCY_MAP.md` are exact loose copies of the corresponding packet members.
- `recovered-source/` exposes all 18 retained source entries by reusing their exact recorded Git blob objects. Their commit/path/blob/SHA-256 provenance remains in the packet source manifest and is linked by `RESTORE-MAP.json`.
- `SAVED-PAYLOAD-SHA256SUMS` covers the canonical packet, loose checkpoint/map/verification files, and the 18 direct recovered-source copies. Publication metadata files are intentionally outside that checksum set to avoid self-reference.

## Preserved historical result

Status is **PARTIAL / MORE_NAMED_SOURCE_RECOVERY_NEEDED**. The one import-only smoke exited 1 with `ModuleNotFoundError: No module named 'pb00701_algebraic_endpoint_model'`. No fixture factory, reversed-v53 residual case, test method, contract verifier or full predecessor chain ran; there is no new runtime owner/sign/refusal evidence.

The residual queue contains 15 statically visible missing module references. That is not a complete transitive dependency closure and not an owner count. Historical target strings `EXACT_RATIONAL_AMPLITUDE_DOMINANCE` / `SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE` are retained assertions, not fresh R1 runtime results. Whole-span nonzero-sign evidence is not derivative/monotonicity authority.

PB-007-01 remains OPEN; v54 acceptance is unestablished; MC-B and MC-1 remain NOT_ESTABLISHED; all 26 operations remain protected.

## Missing dependency and next action

Immediate recorded gap: `research/machining-completeness/tasks/MC-038/pb00701_algebraic_endpoint_model.py`. The statically visible sibling gap is `pb00701_algebraic_endpoint_certificate.py`; their own dependencies remain unknown.

One next action: perform another bounded authoritative-source recovery increment beginning with those named files and inspect their imports before expanding. Do not begin owner enumeration merely because this checkpoint is durable.
