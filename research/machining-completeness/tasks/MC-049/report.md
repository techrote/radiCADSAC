# MC-049 — Candidate-blind final-challenge generator and custody freeze

Status: **COMPLETED_RESEARCH**. Issue: #111. Source baseline: `3f8e695838b41913b5a05a0b235e7b3ff118e04f`.

## Purpose and scope

MC-049 freezes the programme-owned final adversarial challenge generation contract before MC-026 selects a primary provider or challenger. It does not execute a native geometry candidate, qualify engineering output, create a secret test set, or claim independent custody. The durable authority is `final-challenge-contract-v1.json`; `challenge_generator.py` deterministically materializes the challenge schedule from that contract.

At the recorded baseline, MC-026 and MC-049 were both `NOT_STARTED`, no MC-026 implementation branch or PR existed, and the MC-049 checkpoint was recorded before this branch was created. The verifier pins that baseline and reads the historical outcomes registry from Git so later legitimate MC-026 progress does not make this completed freeze unverifiable.

## Hypothesis and falsification criterion

Hypothesis: the reviewed F01–F16 corpus, oracle/checker sources, MC-A workload/accuracy request, and a candidate-independent deterministic seed are sufficient to freeze a useful final challenge schedule before provider selection.

The hypothesis is falsified for this artifact if candidate identity/configuration/output affects generation; the seed or commitment drifts; any mandatory family/class disappears; a pinned corpus/oracle/checker changes without a reviewed version; binary floating-point tolerance becomes correctness authority; protected material/body/journal semantics weaken; non-success terminal states become PASS; or public preregistration is represented as secret, independent or held-out custody.

## Frozen challenge construction

The generator ID is `mc049-candidate-blind-final-challenge-v1`. Its public seed is the UTF-8 string `radiCADSAC-MC-049-public-preselection-v1`, committed by SHA-256 `45b24a9f9bdf2127bba65a0b5f30842c74a64000ce3292ad0017fbe56e473cae`.

Every mandatory family F01–F16 contributes exactly four non-optional challenge classes:

- `baseline` — the family’s defining compounded machining witness;
- `boundary` — exact equality/signed-neighbour or material/topology boundary relevant to the family;
- `metamorphic` — a relation valid only under the family’s recorded physical qualifications;
- `corruption` — a targeted wrong implementation that must be rejected.

Challenge identities and ordering are SHA-256 derived only from the fixed seed, family ID, class and frozen procedure label. The generator has no candidate input field. It retains `A-SEMANTIC`, `A-ENGINEERING` and `A-PRECISION-BOUNDARY` requests for every family and does not permit the engineering tolerance to delete positive-volume material or alter durable identity.

This produces a deterministic denominator of 64 challenge records. The records remain `FROZEN_NOT_EXECUTED`; generation is not native evidence and is not a candidate PASS.

## Source, oracle and checker binding

The contract pins by Git blob identity:

- the live F01–F16 fixture registry;
- the accepted MC-004 qualification contract and its candidate-blind workload seed commitment;
- the MC-009 evidence-binding contract;
- the MC-010 exact rational control implementation;
- all four F01–F16 corpus tranche files and their task-local oracle implementations;
- the MC-015 certificate attack contract and independent checker;
- all direct MC-049 dependency outcome records MC-005 and MC-009 through MC-015.

A changed pin requires a reviewed MC-049 version before affected generated challenges can be treated as the same freeze. Historical RCS files are not edited or reinterpreted.

## Custody classification

The custody level is deliberately `PUBLIC_PRESELECTION_PREREGISTRATION`.

The seed, generator and generated schedule are visible in the repository, so this is **not an independent held-out set** and no secret seed is claimed. That limitation is a correctness property, not a deficiency to conceal. MC-057 remains the owner for later independent challenge ownership/custody and final execution against an exact accepted candidate/configuration. Any independent layer must record who held the material and when; merely copying this public set to another directory does not create independence.

This design still prevents candidate-driven test tuning because the public schedule is frozen before selection and any later revision is explicit/versioned rather than silently replacing observed failures.

## Adversarial and boundary verification

`challenge_generator.py --self-test` corrupts the authority contract and requires rejection of candidate-derived inputs, seed drift, F01–F16 denominator shrinkage, optionalized families, missing challenge classes, weakened accuracy requests, false held-out/independent labels, timeout-as-success, weakened positive-volume semantics, premature MC-B promotion and binary floating-point tolerance authority.

`verify.py` additionally checks every dependency/source blob pin, the accepted MC-004 workload seed, the 16-family BUILT registry, deterministic generation of exactly 64 unique challenge IDs, complete four-class coverage per family, public custody semantics, the historical pre-MC-026 baseline, programme registry state and static-CI wiring.

## Preserved limits and downstream routing

No native or paid campaign ran and MC-049 authorizes none. No candidate has executed these challenges. MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`; MC-A remains accepted. Existing MC-007, MC-016 and MC-017 blockers retain their owners and are not repaired or erased by a static challenge freeze.

MC-049’s artifact may now be consumed by MC-026 for candidate selection without allowing MC-026 to rewrite the challenge generator. Actual final independent execution remains with MC-057 after its capability prerequisites are genuinely satisfied. MC-050/MC-051/MC-052 remain downstream audit/decision owners.

## Verification

Cheap deterministic verification:

```text
python3 research/machining-completeness/tasks/MC-049/challenge_generator.py --self-test
python3 research/machining-completeness/tasks/MC-049/verify.py --contract
python3 tools/mc_workflow.py verify MC-049
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

These commands perform no native geometry or paid execution.
