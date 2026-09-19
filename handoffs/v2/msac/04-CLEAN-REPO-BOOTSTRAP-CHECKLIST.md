# MSAC v2 clean-repository bootstrap checklist

- Create a new empty product repository; import specifications, not genesis Git history.
- Record Genesis-v2 verified merge/tag as source provenance.
- Configure Windows-first CI and a Linux validation path.
- Define project/save schema before UI feature sprawl.
- Implement backend-neutral journal/revision/body/lineage/status types.
- Protect source/audio identity and provenance in save/replay/migration tests.
- Import canonicalization/body/status/error/STEP fixtures only through `handoffs/evidence-dependencies-v2.1.json`; retain exact source commit + blob SHA provenance.
- Keep preview buffers, mesh/dexel state and provider IDs out of authoritative saves.
- Use async backend calls; never run kernel work on the UI thread.
- Add explicit pending/refusal/crash/timeout/reconciliation UX.
- Persist programme-owned pending-intent transactions and test save/crash/restart after deleting all backend/provider caches.
- Test connectivity/body-selection behavior for lower-dimensional contact and already-distinct durable bodies; never infer merge identity from backend coincidence.
- Make all committed material bodies the STEP default.
- Display exact STEP profile and `interoperability_unqualified` qualification truth.
- Add adversarial tests that generated-file success cannot masquerade as Layer-D qualification.
- Keep machine simulation helpful; non-engineering spectacle may not silently change canonical material intent.
