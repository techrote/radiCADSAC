# MC-012 — Physical adversarial corpus F05–F08

**Disposition:** `COMPLETED_RESEARCH` for prospective fixture construction and independent exact controls only.  
**Issue:** #74  
**Source baseline:** `fd39d24319072492f95eab9cf523b306ce623c41`  
**Native/paid execution:** none.

## Hypothesis and falsification criterion

The four MC-012 families can be made into physically meaningful, candidate-blind prospective records whose decisive boundary facts are independently checkable with exact rational predicates. The construction is falsified if any family requires a teleported/inaccessible cutter, silently deletes positive-volume material or a durable body, depends on candidate output or historical RCS geometry for expected truth, loses its discriminating signed/boundary case, or promotes fixture construction into a native capability claim.

## Authority and independence

MC-012 consumes the reviewed artifacts of MC-002, MC-003, MC-010 and MC-055 at the exact Git blob identities frozen in `physical-corpus-f05-f08-v1.json`. Historical RCS material is used only as provenance/adversarial motivation. It is not copied into the expected-answer path.

`fixture_oracle.py` is a task-local exact-rational witness checker. It imports only Python's `fractions`/typing support and re-derives the small predicates needed here: finite axis-aligned cylinders, 2-D segment distance, finite-radius lathe nose envelopes, parting connectivity threshold, axisymmetric OD removal, exact T-slot/form sweeps, access clearance and proper rational rotations. It is deliberately not a general machining engine.

## F05 — accessible internal passage network

F05 starts from one rectangular body and uses an open top pocket, two top-entering vertical bores and one side-entering cross-bore. The cross-bore intersects both vertical bores below the thin-wall witness plane, so the internal network has explicit exterior access rather than a sealed-cavity insertion.

The two vertical bores have radius `5/2` mm and centres separated by `5001/1000` mm. Their retained wall is therefore exactly `1/1000` mm. The oracle checks a rational probe in that positive wall and a zero-wall neighbour in which moving the second centre from `13001/1000` to `13` mm removes the same probe. The fixture therefore cannot be simplified by a tolerance that rounds the positive wall away.

## F06 — finite-nose lathe finishing and parting

F06 uses the programme's established +Z spindle convention and a real `2/5` mm insert nose radius. Two finishing passes overlap axially; the second remains a journal-visible operation even where the first has already established the surface. An exact meridional probe is reached by both finite-nose envelopes but not by a zero-radius/sharp-point corruption.

The final radial parting cut reaches the spindle axis with finite width. Exact topology controls distinguish a complete zero-core cut (two positive-volume material bodies) from an arbitrarily small positive remaining core (one connected body). Both separated bodies receive durable IDs and are retained before any later scrap policy.

## F07 — lathe → mill → lathe handoff

F07 retains one durable body ID through two explicit non-cutting setup changes. The mill setup uses a proper exact rotation mapping machine +Z to common +X and approaches from the exterior of the turned cylinder.

The first lathe pass establishes an axisymmetric radius. The side mill then removes one of two same-radius points while the 90°-rotated peer survives, creating an exact broken-symmetry witness. The return lathe pass is confined to a separate axial band and performs real removal there. At the mill witness plane the asymmetry must remain; rebuilding from a cylindrical stock approximation would resurrect the removed point and fail verification.

## F08 — physically accessible form/undercut

F08 uses a T-slot/form cutter with a `3` mm head and `1` mm neck. A top starter pocket of radius `7/2` mm admits the head with exactly `1/2` mm radial clearance before a continuous lateral sweep. This forbids teleportation through a surface or sealed cavity.

The exact witness set contains a point removed by the wide head but not by a neck-only cutter, a roof point above that undercut which must survive, and a surface-slot point removed by the neck. An adversarial starter radius of `2999/1000` mm is rejected as physically inaccessible.

## Adversarial and boundary verification

`verify.py` checks the dependency blobs, source digest/import graph, exact family denominator, physical access inequalities, signed/boundary witnesses, durable body identities, setup rotation, protected historical source blobs, programme-state non-promotion and registry state.

The adversarial controls specifically reject binary floating authority, candidate-defined expected truth, shared decisive RCS geometry, F05 wall collapse, F06 sharp-point substitution and positive-core rounding, F07 setup/body reset, F08 undersized access or neck-only substitution, historical-source edits, denominator shrinkage and any claim that `BUILT` means candidate or programme acceptance.

## Contract reconciliation and remaining work

`fixture-families-v1.json` advances only F05–F08 from `UNBUILT` to `BUILT`; F01–F04 stay built and F09–F16 remain mandatory and unbuilt. The canonical oracle/corpus document records the new prospective controls and preserves the meaning of `BUILT`.

No native or paid campaign was run. MC-B through MC-F and MC-1 remain `NOT_ESTABLISHED`. MC-007 proof blockers and other unresolved downstream claims remain open. Protected source/audio/provenance, canonical journal, durable-body/lineage and historical negative-evidence semantics are unchanged.
