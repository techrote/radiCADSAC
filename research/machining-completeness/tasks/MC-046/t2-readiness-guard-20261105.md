# MC-046 T2 scale-ladder preparation: source-bound, fail-closed PLAN_ONLY control

**Date:** 5 November 2026 UTC. **Owner:** independent proof-adjacent MC-046 #108 implementation lane. **Status:** DETERMINISTIC_MODEL / PLAN_ONLY, no native or paid campaign, no MC-041 capability acceptance, no manufacturing result.

## Authority and dependency

- Governing decision: `docs/decisions/DR-0026-machining-completeness-programme.md`; current authority `handoffs/current-authority.json` is `NOT_ESTABLISHED`, `production_authorized=false`.
- Candidate-independent MC-004 source: `research/machining-completeness/tasks/MC-004/qualification-contract-v1.json`, immutable Git blob `22d5f976718edac9a8ccce3cb46f799b76e85ab4`. The preflight refuses any mismatch.
- Accepted MC-045 static permit/accounting artifact is available, but this preflight **does not** issue a permit, run any campaign or consume billed resources.
- MC-041 native composed capability dependency remains **NOT_ESTABLISHED**: this work cannot satisfy MC-046's final T2 scale or MC-F practical gate. PB-007-01 through PB-007-04, MC-B and MC-1 remain OPEN/NOT_ESTABLISHED. All 26 required operations remain mandatory.
- This is a new `MC-046` task-scoped file, not a modification of the MC-038 proof or MC-043 STEP consumer owner. It changes no proof registry, task graph, frozen evidence, native executor, handoff or current authority.

## Hypothesis, acceptance and falsifier

**Hypothesis:** a candidate-independent T2 *preparation* envelope can be machine-validated against the exact accepted MC-004 source without accidentally changing the 10/100/1,000/10,000 genuinely geometry-changing section targets, the equal-size but **separate** redundant-history controls, 26-operation coverage, A-SEMANTIC/A-ENGINEERING profiles, three sequential repeats, Q1 reference hardware, exact generator ID/seed or preregistered T2 wall/RSS/timeout ceilings. The preflight must prevent even a well-formed proposal from asserting native execution, materialized fixtures, independent volume witnesses or a successful qualification.

**Falsifier:** an independently mutated proposal containing a narrower domain, different target, omitted redundant control, relaxed limit, different source contract or false success/permit state is accepted.

This is intentionally a **strict readiness-template validator**, not a general benchmark report parser. Future source-authenticated materialization and measured-result schema must be separately versioned and reviewed. A proposed valid JSON plan is not a physically correct sample, independent geometric witness or completed tier.

## Implemented interface

`research/machining-completeness/tasks/MC-046/readiness.py` provides:

```text
python3 research/machining-completeness/tasks/MC-046/readiness.py --contract
python3 research/machining-completeness/tasks/MC-046/readiness.py --self-test
python3 research/machining-completeness/tasks/MC-046/readiness.py --emit-plan
python3 research/machining-completeness/tasks/MC-046/readiness.py --check-plan /path/to/proposal.json
python3 tools/validate_machining_completeness.py
```

The generated proposal has literal `PLAN_ONLY`, `NOT_MATERIALIZED`, `execution_authorized=false`, `qualification_claim=false`, `native_capability_established=false`, no measured results and no invented case/fixture hashes. It binds the exact MC-004 Git blob, seed, generator ID, operation inventory, accuracy profiles, Q1 hardware, T2 counts, four distinct resource envelopes and three sequential repeats. Unknown fields, type confusion (including Boolean-versus-integer), duplicate JSON keys, nonfinite constants, float numbers and invalid Unicode are refused. This file is not a scheduler or producer; it performs **zero native actions**.

## Reproducible controls and nonclaims

The integrated deterministic self-test admits the in-memory generated plan and its canonical JSON roundtrip, and rejects 26 adversarial semantic mutations plus six JSON ingress corruptions (32 negative controls total). Explicit negatives cover a false 10k tier, count conflation, fabricated certificates, fake successful measurements, relaxed memory/time ceilings, wrong hardware, changed seed, duplicate/missing operation, missing accuracy class, 2 repeats, parallel execution, native permission/acceptance claims, Boolean count, extra dispatch fields, duplicate keys, NaN, overflowing exponents, lone Unicode surrogate, malformed JSON and invalid UTF-8.

GitHub Actions `.github/workflows/mc1-mc046-t2-readiness.yml` runs the same source-bound preflight on literal PR-head / merged-main checkout for Ubuntu and Windows, and MC-1 static validation. Host platform PASS means only this deterministic parser/test harness passed, not that its host equals MC-RH-Q1 or that T2 geometry was executed. Test failures and workflow job IDs must remain discoverable; do not replace failures with later green runs in the acceptance narrative.

## Follow-on contract after PB-007 / MC-041

First accept the complete PB-007 mathematical proof, MC-B and genuinely source-matched MC-041 composed native capability through their separate authorities. Then establish prospective, frozen fixture bytes and independent positive-volume material-change certificates for all four tiers and separate zero-additional-removal controls. Only then seek bounded native campaign permit, authentic MC-RH-Q1/platform manifests, exact MC-045 resource ledger and captured crash/timeout failures, candidate-blind T2 execution and engineering-usable STEP verification. No completed PASS may be inferred from this preparation artifact.

**Unresolved:** source generator materialization, independently established volume-positive witness per section, redundant-history non-removal witnesses, actual native candidate/exact build, approved resource permit, three measured sequential repeats, pass/fail against MC-004 envelopes and signed/frozen evidence. These remain explicitly blocked rather than silently marked ready.
