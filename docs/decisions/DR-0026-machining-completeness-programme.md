# DR-0026 — Machining completeness is the pre-production requirement

Status: accepted programme decision on merge of the MC-1 adoption PR. Date: 19 September 2026. This is an authority decision, not geometry qualification.

## Context and authority

The user explicitly required 100% coverage of material states obtainable through the supported real lathe/mill processes, including compounded pathological geometry, and rejected a premature application/vertical-slice roadmap. The supplied `radiCADSAC-machining-completeness-research-plan-v1.0.md` was prepared against `e86c15ca0479240a0045ebc80c83973137b58c60`. Its SHA-256 is `b7cb369e1fef31bb6a02d02960931b3090424114395af9487babf6c0ecbb609c`. The subsequent explicit user request authorizes repository documentation, planning, issue creation and consistency reconciliation. It supersedes the file's delivery-only restriction for those actions, not for production creation or expensive campaigns.

## Decision

MC-1 is the current programme. Work stays in radiCADSAC until constructive domain coverage, faithful native implementation, conventional engineering realization, independent STEP qualification and practical viability are established. Read `docs/machining-completeness/00-PROGRAMME.md` and `handoffs/current-authority.json` before any historical handoff.

Gate 5 remains accepted for the historical foundation and bounded/refusal policies it actually established. DR-0024/0025 and Genesis-v2.1 package/evidence identities are preserved. Their recommendation to transfer unresolved machining coverage to production is superseded for current execution. No old positive result is erased; no model, safe refusal, parser result or pending state becomes completed machining geometry.

The target is the supported physically realizable machining domain, not every arbitrary mathematical surface and not the subset convenient for a solver. An ordinary valid operation cannot be excluded after failure. The domain grammar and output profile require explicit research and review; no representation winner, minimum feature size, geometric epsilon or customer tolerance is selected here.

## Alternatives rejected

Starting a Godot/application vertical slice would not resolve the geometry question. Treating 5/14 bounded directional results, pooled refinement counts, or 13 LevelSet comparisons as completeness would overstate evidence. Rewriting frozen Gate-5 artifacts would destroy provenance. Requiring all proofs to be accepted before any falsification experiment would create a research deadlock.

## Consequences and verification

Use reviewed-work-product dependencies for exploratory work and separate accepted-capability gates for qualification. Negative research results can complete a bounded investigation without satisfying a capability. Native/paid campaigns require explicit bounded permits; one expensive campaign at a time, sequential repeats, and no runner resizing or benchmark cloning by implication.

Root routing, issue graph, evidence labels, schema checks and CI impact routing must agree. Historical geometry inputs, tests and package hashes remain intact. Production repository creation remains separately unauthorized even after a future MC-1 pass.

## Reversibility

A later explicit user/product decision may change the domain or output contract. Record the reason, version, impact, affected claims and invalidated evidence; never retroactively alter a failed fixture or saved journal. Algorithm choices are deliberately reversible. The current MC-1 capability status is `NOT_ESTABLISHED`.

## Sources

[Accepted Gate-5 discussion](https://github.com/techrote/radiCADSAC/issues/46#issuecomment-5739613315), [consistency repair](https://github.com/techrote/radiCADSAC/issues/60#issuecomment-5740726821), `docs/00-FOUNDING-BRIEF.md`, and the source/evidence register in `docs/machining-completeness/08-SOURCES-AND-EVIDENCE.md`.
