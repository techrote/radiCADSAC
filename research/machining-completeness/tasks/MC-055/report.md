# MC-055 — Immutable historical corpus import and strengthened-version map

Status: **completed research candidate; no geometry capability promoted**  
Issue: #117  
Source baseline: `2881b90bd790ea53cefe5b14e4734590883b991d`

## Question and falsification criterion

MC-055 asks whether the historical fixtures and decisive controls needed by the MC-1 corpus can be consumed without silently changing their old parameterizations, qualification budgets, negative results, body semantics or producing identities. The task is falsified if any inherited identity is omitted without an explicit unavailable record; if historical evidence has to be rewritten to fit the stronger MC-1 request; if a pending/refused/timeout/resource-bound historical result is promoted to PASS; or if a strengthened F01–F16 request is represented as an edit of an old fixture rather than a new record.

## Dependency reconciliation

MC-001 and MC-009 are completed reviewed artifacts. MC-055 consumes their authority/evidence and result-binding rules only. No existing MC-055 implementation branch or PR existed at dispatch, so this branch is the single implementation owner.

The work is deliberately static. No native geometry, paid runner, external consumer or production bootstrap is required to pin existing evidence identities. Historical source files under `research/rcs-*` are inputs only and are not modified.

## Immutable imports

`historical-corpus-import-v1.json` pins the producing Git blob for every historical source used by this task. The import includes the complete RCS-021 plan, measured summary and implementation lineage; the entire RCS-003 adversarial manufacturing corpus and schema; canonical RCS-002 lathe/mill journal controls; the decisive RCS-011 retrace/fallback negative evidence; and the decisive RCS-012 sub-tolerance/separation evidence.

The complete RCS-003 corpus is imported by its exact source blob, with each source-local `(id, revision)` remaining its record identity. The lathe, retrace, contact, sub-tolerance and separation indexes are views over that immutable source, not copied fixtures with altered numbers. This avoids a second, drifting transcription of historical parameter axes while still making category coverage deterministic and verifiable.

RCS-021 remains exactly fourteen historical cases, in its original profile order. The verifier checks boundary-sensitive members explicitly: the 15.001 mm retrace jitter; the -2.5 mm exact tangent and -2.499 mm penetrating neighbour; the positive 0.000001 mm plunge; the two-body cut-through expectation; and the 160-segment resource-bounded freehand case.

## Historical measured dispositions remain historical

The accepted RCS-021 run remains bound to producing head `70bf1851652f855714fe30ba412f6d4d42c22d44`, workflow `35280105714`, full artifact `10522213307` and its recorded SHA-256. MC-055 does not redownload or rerun it. Its five 0.5 mm bounded passes, nine `accepted_pending_refinement` cells, one resource-bound non-execution and one resolution refusal remain distinct historical dispositions. `simultaneous-xyz` and `cut-through` remain outside the old 150 mm3 interval budget at 0.25 mm.

The RCS-011 near-coincident retrace remains an important negative control: the one-shot `freehand_batch` returned a valid B-rep but the wrong material result, while the sequential reference was materially consistent. The dense sampled-pose fallback remains a 10/10 timeout result in that campaign. Neither outcome may be converted into a solved case by the import.

RCS-012 continues to preserve the positive 1 um plunge/cusp evidence and the two-body cut-through. In particular, the coarse 0.5 mm occupancy result that erased a positive-volume cusp remains evidence of a representation floor, not permission to erase that body in MC-1.

## Strengthened-version map

F01–F16 are mapped to useful historical seeds where such seeds exist, but every family remains a **new record required** under MC-011 through MC-014. A seed is not an inherited pass. Several cases deliberately state that no equivalent historical geometry record exists: reoriented-stock F04, lathe→mill→lathe F07, accessible form/undercut F08, and phase-sensitive turning F09. F16 also records that historical separation evidence does not establish the stronger complete-removal case.

The current `fixture-families-v1.json` remains unchanged and all sixteen mandatory families remain `UNBUILT`. MC-055 therefore unlocks the corpus builders by giving them source-bound historical inputs without pre-answering their physical-witness or independent-oracle obligations.

## Adversarial and boundary verification

The task verifier fails closed on:

- omission or duplication of an RCS-021 identity;
- mutation of any pinned historical Git blob;
- editing any `research/rcs-*` source on the MC-055 branch;
- erasure of old pending, refusal or resource-bound dispositions;
- drift of the exact tangent/penetration, 1 um, cut-through and high-segment witnesses;
- disappearance of required lathe/retrace/contact/sub-tolerance/separation views from RCS-003;
- references to nonexistent historical RCS-003 or RCS-021 seed records;
- reclassification of the RCS-011 valid-but-wrong B-rep or timeout controls;
- deletion of the RCS-012 positive-volume/body-existence and split controls;
- an in-place historical-to-Fxx promotion;
- marking F01–F16 built, MC-B accepted, or MC-1 accepted from import bookkeeping.

## Result

MC-055 is suitable for `COMPLETED_RESEARCH`: all inherited sources selected by this task are present and pinned, so `unavailable_inherited_identities` is explicitly empty rather than implicit. The hosted RCS-021 artifacts are imported by their recorded producing IDs and SHA-256 values but are not rerun. Historical records remain immutable; strengthened MC-1 requests remain separate prospective records.

This result does **not** establish F01–F16, an independent oracle for them, native geometry correctness, MC-B, STEP qualification or MC-1. It runs no native or paid campaign and changes no source/audio/provenance, canonical-journal, durable-body/lineage or historical negative-evidence semantics.

## Downstream effect

With MC-055 accepted as a reviewed artifact, MC-011's final missing artifact dependency is satisfied. MC-011 may build F01–F04 using the immutable historical seeds while preserving its own physical-witness, independent-oracle, schema and corruption-test acceptance criteria. MC-012–MC-014 may consume the same map as their other dependencies become ready. Any later defect in the import contract requires a new reviewed revision and invalidates only dependent evidence that actually consumed the defective identity; it does not rewrite the historical producing record.
