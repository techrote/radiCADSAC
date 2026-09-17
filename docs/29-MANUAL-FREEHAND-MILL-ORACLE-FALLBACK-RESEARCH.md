# RCS-021 — Manual/freehand mill independent material oracle and bounded fallback research

Status: **accepted measured research; merge pending**  
Date: 2026-09-17  
Issue: RCS-021 / #40  
Evidence: PR #53, workflow run `35280105714`, full artifact `10522213307`, SHA-256 `bbdf14b8474753393d98d42babb94fee7c7309fed9a6a38c93962b289db391ba`.

## Purpose and boundary

RCS-011 established a useful fixed-axis milling hierarchy, but also supplied the failure this issue must not hide: the near-coincident `retrace-jitter` one-shot batch could return a valid one-solid B-rep while leaving effectively full stock, and the dense sampled-pose B-rep fallback timed out. RCS-012 separately showed that a coarse volumetric representation can be robust yet erase real positive sub-cell material change.

RCS-021 therefore separates manufacturing truth from candidate geometry representations. The measured domain is fixed-axis milling in the right-handed Z-up workpiece frame. Flat-end simultaneous XYZ translation is measured. The rounded/ball-nose field is qualified only for the committed constant-Z fixture. Arbitrary tool-axis rotation/five-axis motion and rounded simultaneous-Z motion remain outside this evidence.

## Hypotheses and outcome

- **H1 — independent material truth exposes valid-but-wrong B-rep: supported.** The live sequential retrace result was `11490.990137750125 mm3` and lay inside the independent oracle interval; the one-shot batch was `12000.000000001159 mm3`, remained a valid one-solid B-rep, and lay outside the oracle interval.
- **H2 — directional/deferred material state is a credible bounded fallback: partially supported, with capability narrowed.** All fourteen fixtures were deterministic, preserved required body semantics, and had candidate/oracle material intervals that overlapped. At the founding `0.5 mm` pitch, however, only five fixtures closed both the `150 mm3` material-interval and `0.4 mm` spatial-support policy budgets; nine remain `accepted_pending_refinement`.
- **H3 — resolution is a separate error channel: supported.** Refinement tightened the declared spatial bound. The positive `1 um` plunge remained physically positive instead of being snapped to zero. Some material-volume intervals closed with refinement; others did not.
- **H4 — maintained external evidence is useful but not authoritative by itself: supported.** Pinned Manifold 3.5.3 executed on thirteen fixtures. Every executed result lay inside the independent material interval and matched expected body count. The 160-segment case was explicitly excluded from the expensive Python LevelSet callback path by a declared resource bound, and the `1 um` plunge was correctly classified `refused_resolution_budget` for external authoritative use.
- **H5 — capability narrows before truth does: supported.** `simultaneous-xyz` and `cut-through` remained outside the `150 mm3` candidate volume-interval budget even at `0.25 mm`; they are not promoted by widening manufacturing tolerance.

## Independent material oracle

The independent oracle is built from the cutter trajectory rather than from OCCT topology, Manifold mesh topology, or the directional candidate. For a flat-end cutter, each segment field models the swept vertical cutter columns; simultaneous XYZ motion is evaluated by a monotone field-level feasibility solve. The rounded fixture uses a vertical-axis lower hemisphere plus cutter body and is intentionally independent of RCS-011's sphere-only comparison proxy.

The union field is used as a 1-Lipschitz conservative classifier. An adaptive octree certifies complete material or complete removal when the centre-field value clears the cell half diagonal; unresolved leaf cells contribute a lower/upper material-volume interval instead of a guessed classification. The campaign records that interval and a spatial boundary half-diagonal.

Five closed-form controls validated the oracle without OCCT or the candidate representation:

| Control | Closed-form final material | Oracle interval | Bodies | Result |
| --- | ---: | ---: | ---: | --- |
| stationary flat cutter | 11974.86725877128 mm3 | 11966.6748046875–11981.575012207031 | 1 | contained |
| straight flat slot | 11491.095137745191 mm3 | 11385.337829589844–11556.70166015625 | 1 | contained |
| exact tangency | 12000.0 mm3 | 11988.269805908203–12000.0 | 1 | contained |
| `1 um` pure plunge | 11999.999980365046 mm3 | 11994.575500488281–12000.0 | 1 | contained |
| stock-spanning through strip | 11100.0 mm3 | 11062.5–11255.859375 | 2 | contained |

The 160-segment scaling fixture deliberately caps oracle depth at four rather than allowing CI cost to grow without bound. That widens its reported uncertainty and marks `resource_bound_applied=true`; it does not silently change tolerance.

## Directional / tri-dexel candidate

The executable candidate retains analytic remaining-material Z-column heights on an XY lattice and derives X/Y/Z material interval counts from that state. It records volume estimate and conservative bounds, spatial support radius, body count, directional complexity, deterministic engineering signature, runtime/RSS, and the reconciliation class `bounded_directional_material_state_requires_brep_before_step`.

At `0.5 mm` pitch, spatial support radius is `0.35355339059327373 mm`. Five fixtures close the founding `150 mm3` volume-interval budget: `closed-form-stationary-flat`, `tangent-zero`, `tangent-overlap`, `plunge-1um`, and `stationary-near`.

Nine fixtures are retained as `accepted_pending_refinement`: `closed-form-horizontal-slot`, `self-cross`, `retrace-exact`, `retrace-jitter`, `simultaneous-xyz`, `ball-rounded`, `overlapping-paths`, `cut-through`, and `high-segment-freehand`.

Selected measured refinement is decisive rather than cosmetic:

| Fixture | 1.0 mm interval | 0.5 mm interval | 0.25 mm interval | 0.25 mm conclusion |
| --- | ---: | ---: | ---: | --- |
| retrace-jitter | 240.0 mm3 | 225.0 mm3 | 108.75 mm3 | closes volume budget |
| ball-rounded | 446.6644355390381 mm3 | 240.42016385971147 mm3 | 129.75900536497647 mm3 | closes volume budget |
| simultaneous-xyz | 404.0 mm3 | 277.25 mm3 | 225.8125 mm3 | remains pending |
| cut-through | 600.0 mm3 | 600.0 mm3 | 300.0 mm3 | remains pending |
| plunge-1um | 0.000020000006770715117 mm3 | 0.000015000005078036338 mm3 | 0.0000062499566411133856 mm3 | positive removal retained |

The `1 um` plunge candidate volume is `11999.999979999993 mm3`, so the measured directional state retains positive removed material of about `0.000020000006770715117 mm3`. This is not evidence that every coarse discretization resolves every microfeature; it is evidence that the RCS-021 adapter preserves this physical witness instead of snapping it away.

The through-cut retains two remaining material bodies in both the independent connectivity control and the directional candidate. This remains true even though its directional volume uncertainty is still too broad for authoritative fallback at `0.25 mm`.

## Maintained external candidate — Manifold 3.5.3

The campaign pins Manifold 3.5.3 / source commit `0edd9d54876f3135e431575214dd6d8a72866fee`, Apache-2.0. It evaluates the same programme-owned final-material field through `Manifold.level_set` with explicit edge-length and requested root-tolerance controls.

Thirteen of fourteen fixtures executed. All thirteen executed material volumes were inside the independent oracle interval and all thirteen matched the expected body count. The 160-segment scaling case was explicitly `external_resource_bound_not_executed`, because the Python callback path would duplicate the directional scaling experiment at disproportionate cost. The `plunge-1um` diagnostic executed but was `refused_resolution_budget`: external mesh success does not authorize it to erase or redefine the independent positive-removal witness.

Manifold therefore remains a maintained external comparator, not STEP-authoritative state.

## RCS-011 live regression revisit

The accepted hosted run rebuilt the RCS-011 worker against pinned OCCT 8.0.1 and reran the decisive controls under the independent oracle.

- `retrace-jitter` / sequential `segment_sweep`: `11490.990137750125 mm3`, valid one-solid B-rep, **inside** the independent oracle interval.
- `retrace-jitter` / one-shot `freehand_batch`: `12000.000000001159 mm3`, valid one-solid B-rep, **outside** the independent oracle interval.
- `slot-clean` / old dense `sampled_fallback`: **hang/timeout at the explicit 10 s process bound**.

This directly validates the founding claim: B-rep validity is not a material oracle, and increasing sampled-pose Boolean work is not a bounded general fallback.

## Positive sub-tolerance removal, multi-body, provenance and STEP reconciliation

RCS-012 showed why resolution cannot be conflated with manufacturing tolerance. RCS-021's `1 um` pure plunge remains positive in the independent closed form and directional state; Manifold correctly refuses resolution-qualified authority for that witness instead of treating it as absent.

The stock-spanning through-cut leaves two material bodies in the independent connectivity control, directional candidate, and external comparator.

Dexel intervals, octree cells, mesh triangles and regenerated B-rep faces are diagnostic identities only. Durable identity remains programme-owned operation/material-body/analytic-boundary lineage. Known analytic/process boundaries are recovered from retained semantics before generic residual fitting.

The campaign keeps path semantics, field numeric error, oracle boundary uncertainty, directional pitch/support, external mesh controls, manufacturing tolerance, and STEP/export tolerance separate. None may silently absorb another.

Primary STEP remains conventional B-rep. No directional or Manifold state is successful engineering output until analytic/provenance reconciliation produces a conventional B-rep and that B-rep passes the accepted RCS-005 pre-export, serialization, read-back and independent-consumer gates.

## Accepted capability recommendation

RCS-021 accepts the **independent material oracle** as a regression/truth source for the measured fixed-axis domain. It also accepts the directional representation as a **bounded fallback mechanism only where its per-case/domain material and spatial budgets close**.

This is deliberately not a universal “tri-dexel solves freehand milling” result. The `0.5 mm` configuration qualifies five measured fixtures under the founding budget and leaves nine pending. Measured `0.25 mm` refinement closes the declared volume budget for `retrace-jitter` and `ball-rounded`, but not for `simultaneous-xyz` or `cut-through`; the remaining unrefined pending fixtures stay pending because no finer measured evidence was collected for them.

Therefore production handoff should route supported manual/freehand paths through the independent oracle plus bounded directional state, refine or use stronger analytic reconciliation when policy requires it, and return `accepted_pending` / explicit refusal when the error budget remains open. Five-axis/tool-reorientation and rounded simultaneous-Z motion remain unqualified.

The frozen machine-readable evidence is `research/rcs-021/measured-summary-v1.json`.
