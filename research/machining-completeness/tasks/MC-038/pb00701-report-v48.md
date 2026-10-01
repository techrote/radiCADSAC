# PB-007-01 v48 — mixed-root producer correction

Evidence class: deterministic model. Owner: #261. Reviewed source base:
`8033c8102acc0cf1db77b259a56cee5cb85998ea` (v47/#260).
PB-007-01 remains OPEN; MC-B/MC-1 remain NOT_ESTABLISHED; 26 operations retained.

## Finding and repair

The existing v47 tests documented an avoidance of rational orientation endpoint
roots. V48 targets that producer defect, not broad discovery. V44 leaves
endpoint factors in its irrational-root isolation workspace and can raise
`Sturm open interval endpoint is an exact root`. After interior rational-root
deflation, it can instead raise `multiplicity interval is not source-root unique`
because the workspace interval still includes a removed full-source root.
Both failures are executed as negative regression controls against pinned v44.

The corrected workspace strips rational endpoint and interior factors while
keeping all physical source amplitudes intact. Irrational isolating intervals
are refined until FULL-source uniqueness and nonzero rational interval endpoints
are established. Source multiplicity and exact open/closed counts are regenerated;
incomplete accounting cannot coexist with CERTIFIED. Finite distinct-root
separation proves termination, not a resource or refinement cap.

A versioned consumer reuses unchanged v45 source-bound bisections, v46 endpoint
proofs and v47 complete closed-child inequalities/composition. Prior success and
source rejection retain precedence. Recovery from two known producer exceptions
requires independent historical source validation; unrelated exceptions are not
swallowed and no global monkeypatch is used. The finite checker regenerates all
root, source, map, derivative and endpoint evidence.

## Acceptance evidence and execution

The actual-source test replaces A by t*A in the v47 handoff witness. It requires
a reproduced public predecessor exception, restored complete single-cut
certification, V42-left/V43-right ownership, one open physical root, and no
invented physical root at the irrational proof cut. Endpoint-factor, mixed-root,
repeated-root, source-scaling/coordinate and corruption tests accompany it.

Run `python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v48.py --contract --self-test`.
The focused workflow runs these tests once, with actual repository dependencies.
Exact-head and merged-main run identities belong in the issue acceptance ledger,
not self-referential source metadata. The previous local v47 candidate ZIP is not
an input and has not overwritten any landed implementation.

## Unchanged and unresolved

This is a root-production correction and bounded source-adapter restoration,
not a new derivative theorem or full multi-cut solver. An unqualified complete
child margin remains BLOCKED. Historical source pins and programme registries
are unchanged. PB-007-02 dependent, PB-007-03 OPEN, PB-007-04 OPEN_PROPAGATED,
PO-04/05/08 OPEN, MC-B/MC-1 NOT_ESTABLISHED. Preserve source/audio/provenance,
canonical journal, exact time/path/phase, uncertainty, material, cutter/holder,
body/lineage, refusal/UNCERTIFIED and conventional STEP semantics. No native,
paid, production or expensive campaign ran.
