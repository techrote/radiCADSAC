# radiCADSAC #275 / PB-007-01 v54 / 2A-R1 — partial Git-save handoff

**Status: PARTIALLY_SAVED**

Canonical partial checkpoint:
- Branch: `checkpoint/radicadsac-2a-r1-8c952bd1f384b83e-partial`
- Commit: `ef4addd2f671a9a7491838b0218441186809b954`
- Tree: `32ed6e9868df801d8b624fb8b7620ddc322b7c1c`
- Parent/base: `9734776b3cef3d7039be9623e8872df2c2a85174`
- Directory: `checkpoints/pb00701-v54/2A-R1/8c952bd1f384b83e/`

The branch is exactly one commit ahead of the assessed base, zero behind, and all 25 changed paths are confined to the checkpoint directory. Remote tree readback matched the exact Git blob IDs for `CHECKPOINT.md`, the packet-verification JSON, and all 18 retained source entries.

The complete packet was **not** verified as a single remote Git blob in this bounded save. Use the fallback packet at `/mnt/data/radiCADSAC-2A-R1-git-checkpoint-fallback.zip`, SHA-256 `72eaa52c10be6951ec4ca68a8813fab6bb920da575b437a9bb82ea35762272d2`, 218929 bytes, 106 ZIP members, CRC PASS. It contains the dependency map, commands/results, residual queue and retained earlier 2A material omitted from the remote partial branch.

An earlier noncanonical write attempt exists at branch `checkpoint/radicadsac-2a-r1-8c952bd1f384b83e`, commit `e10c0d79e5001b81d1a115c7c2950bba4aaa2d1e`. Readback detected blob mismatches for its packet ZIP and dependency-map transfer. Per the save contract it was left untouched rather than force-updated. Do not use it as the checkpoint.

Research state is unchanged: source recovery PARTIAL; PB-007-01 OPEN; v54 acceptance unestablished; MC-B/MC-1 NOT_ESTABLISHED; all 26 operations protected. No source recovery, import/test execution, owner enumeration, PR/comment/review/merge, workflow dispatch/rerun, or active branch mutation was performed during checkpoint publication.
