# OpenSimachinist v2 clean-repository bootstrap checklist

- Create a new empty production repository; do not transplant radiCADSAC Git history.
- Copy/adapt this handoff specification as founding documentation and record the Genesis-v2 tag/merge SHA as provenance.
- Establish Windows and Linux CI before provider code.
- Pin language/build dependencies and OCCT 8.0.1 exact source commit; retain license notices.
- Define programme-owned journal/revision/body/lineage/source/audio/provenance types before OCCT integration.
- Make OCCT/private provider types impossible in stable serialized/API contracts.
- Import canonicalizer, error-budget, material-oracle and STEP fixtures as conformance tests with their evidence references.
- Add adversarial tests for private-ID persistence, body loss, positive-removal erasure, error reset, lineage guessing and false STEP qualification.
- Implement worker process isolation before parallel job scheduling.
- Keep preview/mesh state derived and non-authoritative.
- Treat all committed material bodies as default STEP selection.
- Expose `accepted_pending`, refusals, budget breaches and `interoperability_unqualified` as normal engineering statuses.
- Record any deliberate change to founding profile/capability in a production decision record and rerun its qualification gate.
- Do not create MSAC-specific UI/game dependencies inside the backend.
