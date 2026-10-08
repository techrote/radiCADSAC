# Narrow source/dependency map for the next audit

## Scope

All paths below are under `research/machining-completeness/tasks/MC-038/` unless stated otherwise, pinned to `9734776b3cef3d7039be9623e8872df2c2a85174`. This is a source-recovery and audit-entry map, **not a canonical owner inventory or a complete transitive dependency graph**. Full-byte exports and reading limits are separate in `SOURCE_MANIFEST.md`.

## Original source to current finite view

| Layer | Entry points / authority | What is established; what remains to recover |
|---|---|---|
| Actual v53 residual fixture | `test_pb00701_mixed_owner_span_integration.candidate()` and `MixedSourceTests.test_cropped_global_maps_reversal_and_source_negation_preserve_physical_counts` | The constructor and explicit reversal assertions were read at lines 1–170 and 205–310. Full file is not retained. |
| Fixture encoding and transformation | Integration imports `test_pb00701_mixed_owner_span as core`; `core.source` is **`test_pb00701_piecewise_product`**; `core.anchor` supplies exact rational channels | Core lines 1–100 were read. Recover the full source module before using `encode`, `physical_piece`, `power`, or `reverse_source`. The transformation definition itself was not read. Do not rebuild it from prose. |
| v53 current source wrapper | `pb00701_mixed_owner_span_model.build_mixed_source_evidence(spec)` | Full retained, blob-verified. Runs `v52.build_piecewise_source_evidence` first, retains unsupported/failed predecessor results, re-lowers source and compares every span's source material. Actual owner comes from `physical['spans'][i]['route_kind']`, not a wished-for adapter. |
| v52 source wrapper | `pb00701_piecewise_product_model.build_piecewise_source_evidence(spec)` | Read lines 235–EOF. Calls `v51.build_ordered_source_evidence`; only complete ordered-source envelopes enter its new composition scope. Missing per-span V51 evidence produces `NOT_ALL_SOURCE_SPANS_HAVE_V51_PRODUCT_WITNESSES`. |
| v51 / fixed earlier chain | `pb00701_ordered_product_model.build_ordered_source_evidence`; v50 `classify_required_analytic_event` referenced by accepted no-search test | v51 wrapper body and the full historical source-classifier chain have not been inspected here. Recover these to trace actual owner emitters/reachability. Do not derive that chain from version numbers alone. |
| Original source lowering | v52 `lower_source`, `source_args`; original v7 `_normalise_harmonic_splines`, `_master_boundaries`, `_piece_from_normal`, `bspline_piece` | v52 first 170 lines read; v7 full bytes retained. Every original rational B-spline control, channel degree/knot, harmonic, source identity, requested interval and affine phase stays authoritative. Parent span maps have exact positive width. |
| Span view construction | v53 `strict_components`, `regenerate_view`, `build_ordered_span_view` | Full retained. Views retain actual historical owner and full underlying witness. Source material/hash and parent map are regenerated. The normalized view alone is never authority. |
| Full finite checker | `pb00701_mixed_owner_span_certificate.validate_ordered_span_view` and `validate_mixed_certificate(candidate, spec)` | Full retained. Regenerates original lowering, checks supplied witnesses, regenerates knots and full composition; compares exact complete structures. |

## Already accepted v53 interface constants — not the full owner set

`pb00701_vanishing_source_factor_model.OWNERS` explicitly maps:

| Actual historical owner identifier | Version / finite checker route |
|---|---|
| `PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR` | 19; v19 `_monotone_anchor_route`, exact equality to supplied route |
| `PB00701_V47_EXACT_ALGEBRAIC_SINGLE_CUT` | 47; `pb00701_algebraic_monotone_cut_certificate.validate_single_cut_event` |
| `PB00701_V48_MIXED_ROOT_SINGLE_CUT` | 48; `pb00701_mixed_orientation_consumer.validate_single_cut_event` |
| `PB00701_V49_MIXED_BOUNDARY_MULTICUT` | 49; `pb00701_mixed_multicut_certificate.validate_multicut_event` |

`pb00701_ordered_product_model.V50_OWNER` is `PB00701_V50_VANISHING_SOURCE_FACTOR`. Its ordered product view is distinct from strict views. The v53 code admits these four strict owners or the V50 physical product owner; that tells us the current interface scope, not how many owners the complete historical chain emits.

V50 `validate_carrier` was read at lines 105–235: supplied source material/hash and exact owner are checked before routing. It does not call the predecessor classifier. V53 borrows this router without asserting factorization of the physical source. V50's actual `factor_source` rejects constant amplitude GCD rather than manufacturing nonconstant `g=1` evidence.

V51 `carrier_direction` is entered only after owner checking. Its opening implementation was read; the accepted v53 RAG contract and direct tests require complete consistent direction from every closed derivative child. Recover the remaining direction-extraction body and underlying checkers before treating that obligation as newly audited.

## Amplitude-dominance boundary

The original full v7 file is retained at Git blob `a086b625e1a6dea8bd202699d161167bb69cc9e7`. `_dominance_certificate(cos_polys, sin_polys)` computes

`margin = |harmonic-zero constant| - sum(|other harmonic-zero coefficients|) - sum(|all oscillatory coefficients|)`.

It refuses this route when the margin is nonpositive. On success it records exact POSITIVE/NEGATIVE sign, the rational margin, its bound rule and zero open/multiple root counts. The producer's actual `route_kind` is `EXACT_RATIONAL_AMPLITUDE_DOMINANCE`; the nested witness's `relation` is **`SEPARATED_BY_EXACT_RATIONAL_AMPLITUDE_DOMINANCE`**. These two identifiers must not be conflated.

**Source-derived interpretation:** on a normalized `[0,1]` span, the coefficient triangle bound gives a strictly separated sign over the closed span, including endpoints. The witness does not assert a derivative sign or monotonicity. No derivative claim can be inferred merely from root counts or nonvanishing.

The original producer selects this witness before stationary-phase and constant-modulation alternatives. Any later sign-span adapter must consume/check this real historical witness and re-establish its binding to the original B-spline material; it may not choose a different owner. The existing witness object does not by itself carry the complete original B-spline binding. A trusted hash attached by a caller cannot replace re-lowering and correspondence checking.

The old comment's specific margin `97/200` is **not verified for the reversed fixture here**. No test or fixture was executed to establish it. The future audit must obtain it from the original transformation and unchanged fixed predecessor chain.

## Ordered-span and knot boundary

V53 offers distinct `STRICT_SPAN` and `V51_PRODUCT` evidence. Strict evidence needs an actually checked complete derivative witness, exact exterior relations and consistent local direction. Open roots remain source-bound `UNIQUE_ANALYTIC_ROOT` descriptors, with no assumed minimal polynomial or arithmetic nature.

The reversed principal fixture is intentionally refused with owner `EXACT_RATIONAL_AMPLITUDE_DOMINANCE` and reason `SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE`, retaining the v52 result. This is an accepted test assertion and documented historical result, not a fresh replay in 2A.

V52 `knot_continuity` computes the exact **full physical right-minus-left difference** at the common rational phase turn using v19 `_endpoint_relation`. Same-sign jumps are not continuity. Its actual runtime refusal string is `PHYSICAL_SOURCE_KNOT_DISCONTINUITY`. Shared zero knots retain separate one-sided orders, never their sum or an invented global analytic multiplicity; exact nonzero joins support maximal-cell bridging. The middle of v52 `assemble` was not reread, so its full coverage proof is retained acceptance context rather than a new 2A audit.

`no_search()` in the v53 direct tests identifies producer/classifier, derivative-selector and irrational-sign-search functions that must not be used to rescue a supplied candidate. Finite witness-specified recipes remain distinct from replacement proof search. The full guard and all downstream paths still require recovery before new verification.

## Inputs required for one canonical owner inventory

The later inventory needs one source-bound record per **actual emitted owner identifier under the unchanged fixed chain**, with reachability distinctions for literals that are not final selected owners. Its input contract should retain:

- immutable emitter/module/blob and actual selector/delegation position; separate `route_kind`, witness relation, aggregate status and wrapper kind;
- original exact fixture/source spec, lowering/span identity, actual predecessor result and complete witness; historical owner identity is never rewritten;
- proof capabilities separately: nonzero sign, complete derivative and child direction, root count, exterior relation/multiplicity, ordering and full span coverage;
- the finite supplied-witness checker, exact missing premise or refusal reason, and one justified category: supported; adaptable with proved premises; lacks a named premise; blocker/refusal/non-event;
- exact evidence references and unread/untested boundaries. Counts are derived from this single inventory only after de-duplication and coverage validation.

This document creates no inventory rows and sets no target count. It does not create one task per owner or accept any proposed adapter. Source recovery is the prerequisite next direction.
