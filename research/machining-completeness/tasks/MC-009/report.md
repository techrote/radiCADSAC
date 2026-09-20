# MC-009 — Research schemas, result binding and programme verdict verifier

Status: completed research implementation for issue #71. Source baseline: `fa93162caa6e4e16c188674b19bac7a501c5f415` (post-MC-008). This task is **binding and verification infrastructure only**: it does not establish native geometry correctness, oracle mathematics, topology completeness, STEP engineering qualification, practical performance or any new capability gate.

## Question and hypothesis

**Question.** Can MC-1 express fixture, result, task-outcome, claim and programme-verdict records in a versioned, deterministic form and reject stale, mismatched, incomplete or candidate-self-certified evidence before later oracle/native work consumes it?

**Hypothesis.** A small programme-owned verifier can make the important identities non-optional and fail closed on mismatches without changing the independently frozen machining domain, accuracy request, historical Genesis evidence, canonical journal meaning, durable body/lineage semantics or existing negative results.

**Falsification criterion.** The hypothesis fails if any required adversarial corruption is accepted, if a timeout/resource refusal can become a pass, if a candidate can author its own accepted claim/programme verdict, if a missing required stage is silently omitted, or if the mechanism requires rewriting protected historical evidence instead of versioning/adapting new MC-1 records.

## Inputs and dependency bindings

MC-009 consumes only its declared artifact dependencies:

- MC-001 `outcome.json`, Git blob `2efd52cf39102d5722c6bbf281828361e943d6a4`, `COMPLETED_RESEARCH`;
- MC-003 `outcome.json`, Git blob `8f335f59f36c8761844806f9059af4a4f1671044`, `COMPLETED_RESEARCH`.

The task does not reinterpret either dependency. In particular, MC-003 remains the authority for exact source/numeric semantics; MC-009 merely forbids ambiguous binary-floating serialization in its own identity-binding objects.

## Implemented artifacts

`research/machining-completeness/schema-catalog-v1.json` defines five research-local record contracts:

- `radicadsac-mc-fixture/1.0`;
- `radicadsac-mc-result/1.0`;
- `radicadsac-mc-task-outcome/1.0`;
- `radicadsac-mc-claim/1.0`;
- `radicadsac-mc-programme-verdict/1.0`.

`tools/mc_evidence_verifier.py` is the programme-owned cheap verifier. It canonicalizes binding-safe JSON deterministically, computes `sha256:` object identities, validates each record kind, and checks a fixture/result/verdict bundle transitively rather than trusting duplicated status text. Its authority is deliberately narrow: it verifies schemas and identities, not geometric truth.

`verifier-contract-v1.json` freezes the dependency identities, schema-catalog/verifier hashes, corruption corpus, boundary controls, F01–F16 denominator guard, capability guard and protected semantics used by the task-local verifier.

## Binding semantics

A fixture record binds its stable ID/version and scope to the domain identity; mandatory-family fixtures bind F01–F16, while independent controls/historical imports may omit a family mapping; stock/tool/setup/history digests; an independently authoritative physical-validity witness; exact parameter encoding; mechanism/chronology coverage; profile and exact accuracy vector; topology/analytic requirements; explicit required stages; oracle identity/independence; candidate-blind generator identity; and expected-result authority. Candidate output is forbidden as physical witness or expected truth.

A result record binds the exact fixture digest, domain, profile, accuracy, all four input digests, candidate identity/source/configuration, checker identity, execution terminal reason, bounds-validation disposition, optional exported-file identity and **all seven stage slots**: material, topology, reconstruction and STEP A/B/C/D. Every stage is present even when its state is `NOT_EXECUTED`; omission is invalid.

A programme verdict is a separate programme-owned object. It binds the fixture and result digests and repeats the exact domain/profile/accuracy, candidate source/configuration, checker and exported-file identity expected by the decision. The verifier recomputes the only binding-level decision it is allowed to make. A non-success terminal reason, unvalidated bounds or any non-PASS required stage yields `INCOMPLETE`; a candidate-provided `SOLVED`/final/gate/capability verdict field is rejected rather than imported.

An accepted claim requires `MC-1-programme` authority plus bound evidence references. A task outcome remains a task result and is not a programme or capability verdict. These distinctions make it impossible for issue closure or candidate status text alone to promote evidence.

## Canonical bytes and exact quantities

Binding objects allow only JSON null, boolean, integer, string, array and object values. Binary floating values are rejected. Canonical bytes are UTF-8 JSON with object keys sorted, no insignificant whitespace, `ensure_ascii=false`, and compact separators; identity is lowercase `sha256:` over those bytes.

This is an identity rule, not a new numeric model. Physical/numeric quantities remain encoded under their owning exact contract (for example MC-003 exact rational/turn/interval encodings) as strings/integers with explicit units. The verifier does not convert or round them.

## Adversarial and boundary controls

The deterministic self-test starts from one synthetically valid F02-style binding control and requires rejection of all of the following mutations:

- fixture hash mismatch;
- stock/tool/setup/history identity mismatch (explicit history attack included);
- stale profile digest;
- altered accuracy vector;
- missing stage;
- candidate self-verdict field;
- candidate-owned programme verdict;
- candidate source mismatch;
- candidate configuration mismatch;
- checker mismatch;
- exported-file mismatch;
- candidate-defined physical-validity witness;
- oracle marked non-independent;
- candidate-defined expected result;
- binary floating certifying/binding value;
- accepted claim without evidence;
- candidate-owned accepted claim.

Three positive/negative boundary cases are also required. A `TIMEOUT` remains `INCOMPLETE` even when earlier stage records happen to say PASS. Conversely, a physically valid explicit `VALID_EMPTY` result is allowed to pass when all required bindings and stages pass; empty material is not treated as an automatic failure or fake STEP success. An `INDEPENDENT_CONTROL` fixture may also use a null family mapping, so MC-010 controls do not have to impersonate an F01–F16 mandatory family.

The control is a deterministic model of evidence plumbing, not measured geometry evidence.

## F01–F16 and oracle ownership

MC-009 does **not** build the physical adversarial corpus. `fixture-families-v1.json` remains exactly F01–F16, mandatory and `UNBUILT`, preserving MC-011–014 ownership. The new fixture schema exists so those later owners can publish records with complete physical-witness/oracle/request bindings instead of inventing incompatible formats.

Likewise, MC-009 checks that oracle independence is declared and bound. It does not prove that an oracle is mathematically independent or correct; MC-010 and MC-015 own the independent controls and certificate/oracle attacks. A false independence declaration remains a review/certificate defect, not something schema validation can solve.

## Historical and protected semantics

No historical RCS/Genesis measured artifact, source file or producing identity is edited by this task. The canonical journal contract is unchanged. The supported operation denominator is not narrowed. Positive-volume material, durable body identity/lineage, source/audio/provenance meaning, pending/refusal semantics and prior negative evidence remain protected. Historical records that predate these MC-1 schemas remain historical evidence at their producing identities; a later import/adaptation must create a versioned wrapper/binding rather than rewrite the original result.

No native or paid campaign was run. No expensive permit was consumed. Production remains unauthorized.

## Findings and limits

The acceptance criterion is satisfied at the **binding layer**: mismatched hashes, missing stages, stale profiles, altered accuracy and candidate self-verdicts are deterministically rejected, with additional attacks on input, checker, exported-file, oracle and claim authority. A later agent can validate this without chat context using the catalog, task contract and deterministic verifiers.

This result does **not** show that F01–F16 fixtures exist, that a physical witness is correct, that oracle/checker mathematics are independent, that a certificate proves geometry, that any candidate covers the machining domain, or that any STEP output is useful. Those claims remain with their named downstream owners and gates. MC-B through MC-F and MC-1 remain `NOT_ESTABLISHED`.

## Verification

Cheap deterministic commands:

```text
python3 tools/mc_evidence_verifier.py --self-test
python3 research/machining-completeness/tasks/MC-009/verify.py --contract
python3 tools/mc_workflow.py verify MC-009
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

No native verification command exists for MC-009 because no native evidence is claimed.

## Downstream use and invalidation

MC-010 may consume the schemas/verifier as a reviewed artifact and must supply genuine independent controls; MC-015 must independently challenge certificate semantics rather than treating this binding verifier as a certificate checker. MC-045 may later use the result/attempt binding in the bounded native harness, and MC-049 may use fixture/generator commitments for candidate-blind final challenges.

A semantic change to canonical binding bytes, schema required fields, programme-verdict authority, stage inventory, domain/profile/accuracy binding or candidate/checker identity rules creates a new schema/verifier revision and invalidates downstream records that claim the old semantics. Existing negative/historical evidence is retained and superseded explicitly; it is never rewritten into success.
