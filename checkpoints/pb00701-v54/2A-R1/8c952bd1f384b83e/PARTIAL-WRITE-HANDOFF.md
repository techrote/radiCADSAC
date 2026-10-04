# PARTIAL-WRITE-HANDOFF

Canonical partial-save branch: `checkpoint/radicadsac-2a-r1-8c952bd1f384b83e-partial`.

An earlier write attempt created branch `checkpoint/radicadsac-2a-r1-8c952bd1f384b83e` at commit `e10c0d79e5001b81d1a115c7c2950bba4aaa2d1e`. Readback/local Git-blob comparison found that its `ORIGINAL-PACKET.zip` blob and loose `SOURCE_DEPENDENCY_MAP.md` blob did not match the expected local Git blob identities. That branch was left untouched—no force-push, deletion, or replacement—and is not the verified checkpoint.

This clean partial branch is rooted directly at the historical assessed commit and contains only payloads that can be verified by exact Git-blob identity plus publication metadata. The complete exact 2A-R1 packet is therefore an external fallback dependency for restoring the omitted generated records.

Expected exact packet: 218,929 bytes; SHA-256 `72eaa52c10be6951ec4ca68a8813fab6bb920da575b437a9bb82ea35762272d2`; 106 ZIP members; original verification PASS.

No source recovery, imports, tests, owner enumeration, workflow dispatch, issue/PR/comment write, merge, or active implementation mutation was performed during this save.
