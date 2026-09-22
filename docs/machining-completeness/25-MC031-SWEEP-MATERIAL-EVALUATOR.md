# MC-031 — Source-bound sweep-to-material evaluator

MC-031 integrates the selected material route with the reviewed sweep/setup constructors already established by MC-018 through MC-023. It is intentionally not a second geometry implementation and does not promote a new capability gate.

The frozen 26-operation domain is preserved. Fixed-axis flat/corner milling consumes MC-018; ball/round milling consumes MC-019; bounded form/accessible-undercut milling consumes MC-020; certified axisymmetric lathe reduction consumes MC-021; bounded synchronized/phase-sensitive lathe construction consumes MC-022; and re-clamp/multi-setup state consumes MC-023. Composite operations cite every constructor owner they require.

Material mutation is stricter than closed sweep membership. A boundary hit with zero exact positive-volume witness is touching only and does not remove material. Positive removal requires both the qualified sweep result and an independent positive-volume witness. `UNCERTIFIED`, `RESOURCE_REFUSAL`, source/event blockers and semantic mismatches do not mutate canonical material. Machining never adds material.

Every evaluator request is bound to canonical source, common workpiece frame, exact input revision and durable journal-owned `body_id`. The complete inherited finite-cutter error expression remains explicit across setup transitions. Backend topology/component identity, epsilon, binary float, sampling/refinement depth, timeout and derived directional/mesh/level-set observations are not truth authority.

The bounded integration deliberately leaves three producing obligations visible: `PB-007-02` for general coupled spindle/feed/eccentric membership, `PB-007-03` for universal arbitrary form/imported source encoding, and propagated `PB-007-04` for durable connectivity/body transitions now routed to MC-033. MC-032's surviving analytic-event blocker also remains authoritative where applicable. PO-02 therefore remains open and MC-B remains `NOT_ESTABLISHED`.

Verification is executable in `research/machining-completeness/tasks/MC-031/verify.py`. It freezes the actual consumed sweep-module blobs, checks exact 26-operation coverage, exercises exact tangency and `±1/1000000` neighbours, phase/feed correlation, access/holder evidence, stale revisions, inherited-error preservation, body-transition deferral and certificate mutation attacks. Historical source/audio/provenance evidence, canonical-journal semantics, positive-volume material meaning, durable body/lineage identity and the conventional STEP requirement remain unchanged.
