# AGENTS.md — radiCADSAC research protocol

## Repository purpose

`radiCADSAC` is the immutable-ish genesis/R&D repository for two later production projects:

1. **MSAC** — Machinist Simulation Aided Creator, the user-facing Godot engineering creation environment.
2. **OpenSimachinist** — the manufacturing-native geometry/STEP backend and research kernel.

This repository is not either production codebase. Preserve failed ideas, negative results, architectural alternatives, and decision history here. Production repositories will be generated later from clean handoff specifications.

## Non-negotiable programme invariants

- The primary product is useful engineering geometry, not a machining game.
- The initial target user is an experienced machinist comfortable with console-game controls.
- Initial machine/process scope is **lathe and mill only**.
- User interaction is direct simulated machining; do not collapse the concept back into conventional sketch/feature-tree CAD.
- Machine simulation must aid creation rather than impose chores. Chatter, crashes, dirt, wear, etc. may provide feedback or spectacle but must not make geometry creation needlessly punitive.
- Undo/redo and replayability are first-class requirements.
- **STEP is mandatory primary engineering output.** STL may be derived from the authoritative solid but is not an acceptable fallback architecture.
- Pathological geometric cases such as coincidence, tangency, sub-tolerance cuts, sliver remnants, retraced paths, self-crossing paths, and very large operation counts are normal manufacturing inputs, not invalid edge cases.
- Machine/process semantics must survive the MSAC↔geometry boundary; do not reduce every operation prematurely to anonymous `A - B` Boolean operands.
- The geometry implementation is replaceable. Saved manufacturing intent/history must not depend on one kernel's private data structures.
- Internal geometry may use unconventional, deferred, approximate, implicit, hybrid, or provenance-aware representations. Exported STEP must resolve to a conventional valid engineering solid within declared tolerances.
- Do not expose OCCT-specific types as the stable programme-level API.

## Research execution rules

Every research issue must be completable by an autonomous contributor using the issue plus the repository documentation it references.

For each issue:

1. Read this file, `docs/00-FOUNDING-BRIEF.md`, `docs/01-MSAC-GEOMETRY-CONTRACT.md`, `docs/04-REVISED-RESEARCH-ROADMAP.md`, and any issue-specific references.
2. Inspect current `main` before work; newer accepted decisions supersede older speculative material unless the issue explicitly asks to challenge them.
3. State hypotheses and falsification criteria before drawing conclusions.
4. Prefer primary sources: source code, standards documentation, upstream technical docs, papers, and reproducible experiments.
5. Distinguish measured fact, sourced fact, inference, proposal, and unresolved question.
6. Record negative results. Do not hide failed approaches.
7. Add or update RAG-friendly Markdown: small standalone sections, explicit terminology, stable headings, source links, and concrete conclusions.
8. If code/fixtures are required, make them deterministic and runnable from documented commands.
9. Add automated checks appropriate to the work. Existing checks must remain green.
10. Work on a branch, open a PR, repair failures, and merge only after required automated checks pass. Verify the merge landed on `main` before closing the issue.
11. Do not silently broaden the scope into MSAC implementation or a production OpenSimachinist fork unless the issue explicitly authorizes it.

## Documentation quality / RAG rules

Research documents must be usable independently by a later agent that has not seen the founding conversation.

Each substantial document should include where applicable:

- purpose and scope;
- definitions;
- assumptions and invariants;
- evidence/source links;
- alternatives considered;
- findings;
- unresolved questions;
- implications for MSAC;
- implications for OpenSimachinist;
- recommended next actions;
- status/date/version notes.

Avoid vague references such as “as discussed earlier”. Restate the material needed to understand the claim.

## Decision discipline

Research does not become architecture merely because it is interesting. Material decisions should be recorded under `docs/decisions/` with:

- context;
- decision;
- alternatives;
- evidence;
- consequences;
- reversibility;
- status: proposed / accepted / superseded / rejected.

## Handoff discipline

The final outputs of this repository are clean handoff packages under `handoffs/opensimachinist/` and `handoffs/msac/`.

Do not copy the entire genesis repository into a production repository. Generate fresh implementation plans and requirements from accepted conclusions so the production histories begin cleanly while this repository preserves the original research record.
