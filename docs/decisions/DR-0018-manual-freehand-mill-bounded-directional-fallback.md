# DR-0018 — Manual/freehand milling requires independent material truth and bounded directional fallback

Status: **accepted**  
Date: 2026-09-17  
Decision scope: Genesis-v1 fixed-axis manual/freehand milling  
Accepted evidence: RCS-021 / PR #53 / workflow `35280105714` / artifact `10522213307` / SHA-256 `bbdf14b8474753393d98d42babb94fee7c7309fed9a6a38c93962b289db391ba`.

## Context

RCS-011 showed that conventional kernel success is not a sufficient manufacturing oracle. Its near-coincident `retrace-jitter` one-shot batch returned a valid one-solid B-rep while leaving effectively full stock rather than the material removed by the exact sequential reference. Its dense sampled-pose fallback also exhausted bounded execution. RCS-012 showed the complementary risk: coarse volumetric occupancy can be deterministic and robust while erasing real positive sub-resolution material change.

DR-0014 already permits bounded internal hybrid representations, but requires explicit representation error, programme-owned lineage, analytic preservation and conventional B-rep reconciliation before STEP. RCS-021 supplies the missing independent material truth and measures a directional/deferred material representation plus a maintained external comparator.

## Decision

The programme adopts these rules for fixed-axis manual/freehand milling:

- **Material truth is independent of OCCT success.** `IsDone`, valid B-rep, one-solid topology, watertight mesh or visual plausibility are not sufficient proof of correct material removal.
- **The RCS-021 cutter-field/octree oracle is accepted as an independent regression/material oracle for its measured domain.** Closed-form material/connectivity controls passed and it independently rejected the live RCS-011 valid-but-wrong one-shot retrace while accepting the sequential reference.
- **The canonical journal remains durable intent.** Fallbacks may reduce derived geometric work but may not compact away journal history, provenance, control uncertainty or physically positive removal.
- **Directional/deferred material state is accepted only as a bounded fallback.** Admission is per qualified domain/case and requires candidate material bounds to overlap the independent oracle, deterministic repeats, correct body/connectivity semantics, and declared volume/spatial budgets.
- **The founding `0.5 mm` directional configuration is not universally qualified.** Five measured fixtures closed the `150 mm3` material-interval plus `0.4 mm` spatial-support budgets; nine remain `accepted_pending_refinement`.
- **Measured refinement may promote a fixture class only when the bound actually closes.** At `0.25 mm`, `retrace-jitter` and `ball-rounded` closed the declared material-volume budget. `simultaneous-xyz` (`225.8125 mm3`) and `cut-through` (`300.0 mm3`) did not and therefore remain pending for authoritative fallback despite correct material/body semantics.
- **Resolution cannot erase physical truth.** The positive `1 um` plunge is retained analytically/semantically; a representation that cannot resolve it must preserve an explicit uncertainty/witness or refuse authoritative use.
- **Disconnected material remains valid.** The through-cut physically leaves two bodies; the independent control, directional candidate and executed external comparator all preserved two.
- **Backend-local identities are non-durable.** Octree cells, dexels/ray intervals, mesh triangles and regenerated B-rep topology do not become project identity.
- **Known analytic/process boundaries survive fallback through programme provenance.** Reconciliation recovers known boundaries before generic fitting of genuinely unknown residual geometry.
- **STEP remains a mandatory reconciliation boundary.** Directional or mesh state is not STEP-authoritative. It must reconcile to conventional B-rep and pass RCS-005 before the result is successful engineering output.
- **Capability narrows before error budgets do.** If bounds do not close, the outcome is refinement, `accepted_pending`, `refused_unsupported` or `refused_unresolved_ambiguity`; manufacturing tolerance is not widened to manufacture success.
- **External engines remain replaceable comparators/providers.** Manifold 3.5.3 is accepted as measured external evidence, not as durable semantics or authority.

## Alternatives considered

### Trust exact per-segment OCCT subtraction as the sole oracle

Rejected. The live RCS-021 revisit reproduces the RCS-011 distinction: sequential subtraction agrees with independent material truth, while an alternative valid OCCT B-rep is materially wrong. A kernel cannot be its own only oracle for this defect class.

### Accept one-shot freehand batching when topology is valid

Rejected. The live `freehand_batch` result was `12000.000000001159 mm3`, one solid and valid, yet outside the independent material interval; the sequential reference was `11490.990137750125 mm3` and inside.

### Increase the dense sampled-pose timeout

Rejected as a founding fallback. The bounded live revisit again hit the explicit `10 s` timeout. More time does not create a scaling contract, material oracle or representation-error bound.

### Whole-model mesh authority

Rejected. Manifold executed successfully on thirteen fixtures and agreed with independent material/body evidence on each executed case, but mesh success does not intrinsically preserve programme analytic semantics or satisfy conventional STEP obligations.

### Whole-model coarse voxel/SDF authority

Rejected. RCS-012 already demonstrated sub-resolution semantic loss. RCS-021 therefore treats resolution as an explicit representation error channel.

### Qualify every directional fixture because intervals overlap the oracle

Rejected. Overlap demonstrates compatibility, not that the declared uncertainty budget is sufficiently tight. Nine `0.5 mm` cases remain pending despite compatible intervals and correct body semantics.

### Refuse all manual/freehand milling

Not selected as the default because RCS-021 establishes a useful independent oracle and bounded directional subset. Explicit refusal remains the required outcome for unsupported/unclosed classes.

## Evidence

The accepted hosted campaign is workflow run `35280105714` at head `70bf1851652f855714fe30ba412f6d4d42c22d44`.

All required runtime checks passed with no structural failures:

- five closed-form material/connectivity controls were contained by the independent oracle;
- all fourteen directional fixtures were deterministic;
- all fourteen candidate/oracle material intervals overlapped;
- the positive `1 um` plunge was retained;
- the through-cut retained two material bodies;
- the 160-segment fixture exceeded the RCS-011 smoke size and remained explicitly resource bounded where necessary;
- Manifold executed on thirteen fixtures; every executed result lay inside the oracle interval and matched expected body count;
- the live sequential retrace was accepted by independent material truth;
- the live valid one-shot retrace was rejected by independent material truth;
- the old sampled fallback was contained as a `10 s` timeout.

The frozen machine-readable evidence is `research/rcs-021/measured-summary-v1.json`.

## Consequences

- Production handoff may implement manual/freehand material tracking without making per-segment OCCT topology the only source of truth.
- Directional/deferred state can answer bounded material/collision/preview questions before conventional topology is reconstructed, but only inside the domain whose error budget has closed.
- Refinement becomes a policy-controlled operation with explicit benefit/cost evidence, not a hidden tolerance knob.
- Some classes remain `accepted_pending_refinement`; notably the measured `simultaneous-xyz` and `cut-through` directional volume bounds remain too broad at `0.25 mm` despite correct semantics.
- RCS-011 exact per-segment execution remains a high-fidelity comparator/possible fallback, not the independent truth source.
- Manifold remains valuable for independent robustness comparison and multi-body confirmation, but its level-set mesh is non-authoritative until reconciliation.
- Sub-resolution physical features require retained analytic witnesses or refusal.
- Arbitrary tool-axis rotation/five-axis and rounded simultaneous-Z motion require separate evidence.

## Reversibility

High. The independent oracle, directional candidate and external comparator sit behind programme-owned material semantics. No saved-project meaning depends on cell/ray/triangle IDs.

A production cache may later choose a different material representation without changing journal or document semantics, provided it preserves the same explicit material/error/provenance contracts and STEP reconciliation boundary.

## Reconsideration trigger

Reconsider the selected directional fallback when later evidence demonstrates materially tighter certified bounds, better scaling, or simpler analytic STEP reconciliation over the same corpus without weakening provenance or physical truth. Also revisit any fixture class when a finer measured representation closes its declared budget; do not infer promotion from unmeasured refinement.
