# MSAC founding handoff

Status: RCS-015 clean production-repository founding package  
Version: `msac-handoff/1.0`  
Date: 2026-09-17  
Frontend architecture: `sac-machine-module-client-v1`  
Backend consumed: `semantic-provider-hybrid-v1`

## Purpose

This directory is the clean founding specification intended to seed a future **MSAC — Machinist Simulation Aided Creator** production repository. It is written for an implementation agent that has not read the founding conversation and should not need to reconstruct the chronological research history in `radiCADSAC` before beginning useful product work.

The production repository must be created separately. RCS-015 does **not** create or populate it.

## Read this package in order

1. `00-FOUNDING-SPEC.md` — product/SAC purpose, target user, interaction principles, machine modules, journal production, backend boundary, state/status model, inspection, STEP UX and persistence requirements.
2. `01-IMPLEMENTATION-ROADMAP.md` — measurable implementation stages that establish a productive engineering loop before publication polish.
3. `02-INITIAL-ISSUE-GRAPH.md` — initial autonomous production issues with dependencies, prompts and acceptance criteria.
4. `03-INTEGRATION-ESCAPE-ROUTES.md` — backend/control/integration unknowns and safe fallback/refusal doctrine.
5. `04-CLEAN-REPO-BOOTSTRAP-CHECKLIST.md` — checklist for creating the MSAC repository without importing genesis history.
6. `handoff-v1.json` — machine-readable handoff/Gate-4 manifest used by validation.

## Product contract carried into production

MSAC is a productive engineering creation environment whose modelling interface is **direct simulated machining**. It is not a conventional sketch/extrude/feature-tree CAD tool wearing a game-like camera, and it is not a machining game whose engineering export is incidental.

The first serious target user is an experienced machinist who is comfortable with console-game controls. Initial machine scope is **lathe and mill only**.

The founding product constraints are:

- machining knowledge should transfer directly into digital geometry creation;
- simulation physicality exists to improve intuition/control, not to impose workshop chores;
- geometry-critical dimensions, setup/tool frames, motion and material semantics are trustworthy while visual effects may be approximate;
- undo/redo is first-class and dramatic machine mistakes are recoverable;
- gamepad/manual control remains remappable and empirically testable rather than permanently frozen in the genesis handoff;
- first-person machinist and workpiece-follow/free-flight camera modes are product requirements, but cameras never define engineering coordinates;
- MSAC produces the accepted `msac-journal/1.0` manufacturing intent and consumes a semantic OpenSimachinist API; neither OCCT objects nor Godot scene identity cross the stable boundary;
- preview geometry is disposable; committed/reconciled engineering state is distinguished visibly;
- STEP is the primary engineering output and export status must communicate actual conformance/qualification state;
- material-body separation is explicit; no hidden “largest body” rule is allowed;
- the first roadmap proves the **lathe/mill → canonical journal → backend → valid STEP** core loop before workshop breadth, progression, content or visual polish dominates.

## Relationship to the OpenSimachinist handoff

MSAC consumes the programme-facing contract already frozen conceptually by RCS-013/RCS-014. OpenSimachinist owns geometry-provider/reconciliation implementation; MSAC owns interaction, machine simulation, canonical operation production, project UX and presentation of engineering state/status.

The sibling handoff is a contract reference, not a runtime source dependency. Each production repository begins with its own clean history and may evolve independently behind versioned compatibility rules.

## Archaeology rule

Implementation agents may follow evidence links into `radiCADSAC` when a requirement needs to be challenged, reproduced or qualified. They should **not** copy the genesis repository wholesale, import obsolete research issue history, or treat rejected experiments as production requirements.

## Gate 4 statement

This handoff satisfies the roadmap's MSAC Gate-4 content requirements when validated and merged:

- the backend boundary is stable enough to consume;
- the canonical operation-journal/canonicalization contract is defined;
- preview and authoritative engineering state are separated;
- backend error/status semantics are mapped into product UX;
- machine-module and backend provider responsibilities are separated explicitly;
- initial lathe/mill capabilities and limitations are documented;
- an early productive engineering core-loop roadmap exists and does not wait for universal kernel research.

Gate 4 means **MSAC implementation can begin against explicit contracts and escape routes**. It does not assert that all backend research, independent STEP interoperability qualification, final control mappings or publication polish are complete.
