# AGENTS.md — radiCADSAC research protocol

## Repository purpose

`radiCADSAC` is the immutable-ish genesis/R&D repository for two later production projects:

1. **MSAC** — Machinist Simulation Aided Creator, the user-facing Godot engineering creation environment.
2. **OpenSimachinist** — the manufacturing-native geometry/STEP backend and research kernel.

This repository is not either production codebase. Preserve failed ideas, negative results, architectural alternatives, and decision history here. Production repositories will be generated later from clean handoff specifications.

## Current foundation documents

Research after RCS-001 must treat these as the current foundation unless a later accepted decision explicitly supersedes part of them:

- `docs/00-FOUNDING-BRIEF.md` — preserved product intent;
- `docs/01-MSAC-GEOMETRY-CONTRACT.md` — Gate-1 MSAC/backend contract;
- `docs/04-REVISED-RESEARCH-ROADMAP.md` — current programme sequence/gates;
- `docs/06-RESEARCH-METHOD.md` — evidence/reproducibility rules;
- `docs/08-TERMINOLOGY.md` — accepted research vocabulary;
- `docs/09-FOUNDATION-AUDIT.md` — reconciled invariants, hypotheses and Gate-1 result;
- `docs/24-GENESIS-V2-REVISED-ROADMAP.md` — completed Genesis-v2 qualification plan;
- `docs/35-GENESIS-V2-SYNTHESIS-AND-GATE5.md` — accepted Gate-5 synthesis;
- `docs/37-GENESIS-V2-BOOTSTRAP-CONSISTENCY.md` and DR-0025 — current bootstrap consistency clarification;
- `handoffs/genesis-release-v2.json` plus `handoffs/evidence-dependencies-v2.1.json` — current production-bootstrap routing and exact evidence pins;
- `docs/decisions/` — accepted/proposed/superseded programme decisions.

Historical/superseded material remains useful evidence of how the programme evolved but must not override a newer accepted decision silently.

## Non-negotiable programme invariants

- The primary product is useful engineering geometry, not a machining game.
- The initial target user is an experienced machinist comfortable with console-game controls.
- Initial machine/process scope is **lathe and mill only**.
- User interaction is direct simulated machining; do not collapse the concept back into conventional sketch/feature-tree CAD.
- Machine simulation must aid creation rather than impose chores. Chatter, crashes, dirt, wear, etc. may provide feedback or spectacle but must not make geometry creation needlessly punitive.
- Undo/redo and replayability are first-class requirements.
- **STEP is mandatory primary engineering output.** STL may be derived from the committed/reconciled solid but is not an acceptable fallback architecture.
- Pathological geometric cases such as coincidence, tangency, sub-tolerance cuts, sliver remnants, retraced paths, self-crossing paths, and very large operation counts are normal manufacturing inputs, not invalid edge cases.
- Machine/process semantics must survive the MSAC↔geometry boundary; do not reduce every operation prematurely to anonymous `A - B` Boolean operands.
- The canonical operation journal is the durable source of manufacturing intent. Geometry implementation/state is replaceable and versioned.
- Saved manufacturing intent/history must not depend on one kernel's private data structures.
- Internal geometry may use unconventional, deferred, approximate, implicit, hybrid, or provenance-aware representations. Exported STEP must resolve to conventional usable engineering geometry within declared tolerances.
- Do not expose OCCT-specific types as the stable programme-level API.
- Units, coordinate frames, transforms and tolerance policies must be explicit/versioned rather than hidden implementation assumptions.
- Disconnected material-body states created by parting/cut-through are valid research workload and may not be silently discarded.

## Research execution rules

Every research issue must be completable by an autonomous contributor using the issue plus the repository documentation it references.

For each issue:

1. Read this file, `docs/00-FOUNDING-BRIEF.md`, `docs/01-MSAC-GEOMETRY-CONTRACT.md`, `docs/04-REVISED-RESEARCH-ROADMAP.md`, `docs/06-RESEARCH-METHOD.md`, `docs/08-TERMINOLOGY.md`, `docs/09-FOUNDATION-AUDIT.md`, applicable accepted decision records, and any issue-specific references.
2. Inspect current `main` before work; newer accepted decisions supersede older speculative material unless the issue explicitly asks to challenge them.
3. State hypotheses and falsification criteria before drawing conclusions.
4. Prefer primary sources: source code, standards documentation, upstream technical docs, papers, and reproducible experiments.
5. Distinguish source fact, inference, proposal and unresolved question, and subtype architecture-impacting measurements as native geometry/kernel, independent oracle, deterministic model, or platform/process evidence under `docs/06-RESEARCH-METHOD.md`. A deterministic model result may not be promoted to native geometry capability.
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

Avoid vague references such as `as discussed earlier`. Restate the material needed to understand the claim.

Use terms consistently with `docs/08-TERMINOLOGY.md`. If a research result requires a terminology change, update the terminology/decision record explicitly rather than silently redefining a word inside one report.

## Decision discipline

Research does not become architecture merely because it is interesting. Material decisions should be recorded under `docs/decisions/` with:

- context;
- decision;
- alternatives;
- evidence;
- consequences;
- reversibility;
- status: proposed / accepted / superseded / rejected.

Accepted decisions must distinguish fixed programme requirements from still-open implementation choices.

## Handoff discipline

The **current** production bootstrap outputs are the consistency-corrected Genesis-v2 packages under `handoffs/v2/opensimachinist/` and `handoffs/v2/msac/`, bound by `handoffs/genesis-release-v2.json` consistency revision `2.1`. Resolve imported conformance/evidence assets only through `handoffs/evidence-dependencies-v2.1.json`.

The v1 packages under `handoffs/opensimachinist/` and `handoffs/msac/` remain historical freezes and must not be used as the current autonomous bootstrap input.

Do not copy the entire genesis repository into a production repository. Generate fresh implementation plans and requirements from the current handoff so the production histories begin cleanly while this repository preserves the original research record.
