# Recovery progress

Observed: restored and verified the real 2A packet, then rechecked its eight source Git blobs. Main and both v54-prefix refs match the prior ledger. Issue #275 remains open, five comments, last updated 2026-10-03T10:10:22Z. No newly published source in the inspected refs supersedes recovery.

Three new source files are retained so far, in order: the actual piecewise source helper, mixed-owner direct tests, mixed-owner integration tests. Their full Git blob identities match authenticated connector reads; no functions/tests have run. The literal fixture chain is now present but its imported model closure remains incomplete.

The helper reverses B-spline knots about lo+hi, reverses controls, adjusts the phase offset by rate*(lo+hi), and negates the phase rate; the source ID is retained by deepcopy. This is source reading, not a replay.

Shell transport: one current-environment bounded immutable raw-file GET failed DNS (curl exit 6), with no bytes retained. No retry; continue authenticated connector file transfer only. No historical export/staging recovery was retried.

## Later R1 increment — 2026-10-04T16:40Z onward

The earlier three-file paragraph is an intermediate checkpoint, not final coverage. The batch finished with ten new full files; all now match their immutable Git blobs. The actual dynamic MC-032 engine dependency was included. One import smoke failed at the v50 module's missing algebraic-endpoint model. No factory or residual ran. The final CHECKPOINT.md and source manifest supersede this progress count, not the preserved prior acceptance/claims evidence.
