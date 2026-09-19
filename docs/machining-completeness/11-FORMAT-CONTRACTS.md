# Research artifact, verdict and traceability formats

Status: minimum contract for implementation by MC-009/015 and subsequent owners. Adoption creates valid registries and structural checks, not a working geometric certificate verifier. Schema versions are research-local; do not change public journal/API enums implicitly.

## Canonical registries

`programme-v1.json` binds mandate, baseline, source-plan digest, gates, invariants and production hold. `task-graph-v1.json` owns bounded work, milestone/package hierarchy, typed prerequisites, acceptance/verifications, owned paths, locks and expected outputs. `github-map-v1.json` binds stable IDs to actual issue/milestone IDs. `proof-obligations-v1.json`, `fixture-families-v1.json`, `evidence-ledger-v1.json`, `authority-map-v1.json` and `outcomes-v1.json` are separately versioned material. A field's presence is not acceptance evidence.

Use exact numeric encodings and explicit units for quantities. Hash canonical bytes with an identified algorithm/normalization, not an unspecified JSON pretty print. Every version-changing semantic edit records parent identity, reason, affected claims and invalidation; never edit a frozen result to conceal failure.

## Fixture and oracle record

Required bindings: stable fixture/version and domain version; stock/tool/setup and canonical history digests; physical witness and its independent validity disposition; exact parameter encoding; constructor/mechanism/chronology coverage; original versus strengthened request; typed accuracy vector; topology/analytic requirements; required stages; oracle identity, derivation and independence graph; generator source/seed or held-out commitment; expected invalid-control category if applicable.

A mandatory valid fixture cannot have candidate output as its expected result. Empty and invalid controls are explicit classes. Oracle enclosures must be tight enough to distinguish declared defects; wide intervals remain inconclusive.

## Claim and proof record

Each PO/lemma has ID/version, quantified domain, assumptions and statuses, effective coefficients, construction, finite termination argument, proof/review method, trusted base, counterexample obligations, exact implementation/checker references, fixture witnesses, findings and review attribution. A reviewed argument is not automatically machine checked. OPEN/REFUTED/REVIEWED/ACCEPTED are different states; acceptance requires the promised review/evidence rather than a name change.

## Result and certificate record

Bind run/attempt ID; source and exact configuration; fixture/input/domain/profile/request hashes; candidate and claimed domain; execution terminal reason; material/topology/reconstruction and STEP A/B/C/D verdicts; bounds, numeric method, certificate/checker identities; raw/canonical/unique-work and topology counts; platform/compiler/arithmetic/dependency pins; timing/memory/allocated resources/permit/cost basis; durable artifacts/digests; parent result and supersession.

Missing stages are NOT_EXECUTED. A timeout is an incomplete observation, not proof of impossibility. The programme verifier must reject mismatched/stale source, input, profile, accuracy, checker or exported-file identities, missing required stages, unvalidated bounds and consumer evidence for another file. Adapter `SOLVED` text is never sufficient.

Certificates explicitly state relations between candidate geometry and nominal material, coverage of unresolved cells, error channels, topology/identity correspondence, arithmetic assumptions and aggregation. Surface distance, directional material error and topology need their own covered statements. Exact/directed numeric serialization is checked. Negative controls attack each binding and each semantic requirement.

## Outcome and gate record

Task `outcome.json` contains task ID, result kind, source/configuration, artifacts/digests, cheap/native commands actually run, evidence classes, accepted and open claims, review and blockers/affected descendants. `COMPLETED_RESEARCH` or `NEGATIVE_RESULT` may release a reviewed-artifact dependency; neither automatically releases a capability dependency. `CAPABILITY_ACCEPTED` requires the named gate's full evidence and reviewer disposition. Closed GitHub issues alone release nothing.

Current registries may record NOT_STARTED or BLOCKED without inventing artifacts. MC-001 adoption is a planning outcome only. Every gate remains NOT_ESTABLISHED at initial adoption.

## Verification interface and stopping

A leaf implementation supplies a deterministic `verify.py --contract` and documents native verification separately with exact bounded permit. The workflow helper checks metadata and invokes cheap contract tests only; it cannot transform a metadata pass into geometry acceptance. MC-009 implements schema/version/source-binding verification; MC-015 independently implements/challenges actual certificate checks; native task owners provide stage-specific executable verification.

Preserve every failure and incomplete attempt durably. Unavailable external evidence is explicit and blocks only the affected claim. Record invalidation edges after changes to domain, arithmetic, primitive, oracle, provider, reconstruction, consumer/profile or dependency version. Re-run only affected evidence under a new permit. A final accepted claim must be traversable from requirement to proof, code, fixture/oracle, run/certificate, engineering artifact and decision, and back again.
