# Source/dependency map — after 2A-R1

## Scope and selected source

This is a recovered-source and import-readiness map, not a canonical proof-owner inventory. Main is pinned to `9734776b3cef3d7039be9623e8872df2c2a85174`. All named local source paths below are under `research/machining-completeness/tasks/MC-038/` unless explicitly marked MC-032. A recovered file is not necessarily successfully imported. `records/dependency-map.json` separates source edges from actual runtime evidence in the smoke log.

## Exact fixture chain recovered

```text
test_pb00701_mixed_owner_span_integration.py
  candidate() -> source.encode / source.physical_piece / source.power / core.anchor
  imports test_pb00701_mixed_owner_span.py as core
    imports test_pb00701_piecewise_product.py as source
      imports pb00701_piecewise_product_model.py as m
```

All three fixture files now have complete checked bytes. The actual helper's `reverse_source` reflects source knots about lo+hi, reverses the original controls, updates affine phase offset by rate*(lo+hi), negates phase rate, and preserves other original fields by deepcopy. The factory and helper functions were not called.

The preserved existing residual assertions are in integration lines 221–238, within `MixedSourceTests.test_cropped_global_maps_reversal_and_source_negation_preserve_physical_counts`. This method contains other transform checks as well; it is not represented as a dedicated one-case verifier. R1 executed neither this method nor a reconstructed subset of it.

## Import-time closure and actual failure

```text
integration -> core -> v53 mixed-owner model
  -> v52 piecewise-product model
     -> algebraic-child-map model
        -> [file-path load] ../MC-032/event_engine.py   RECOVERED
     -> mixed-boundary model                         RECOVERED
  -> v51 ordered-product model
     -> v50 vanishing-source-factor model
        -> algebraic-endpoint model                  MISSING; actual failure
     -> algebraic-endpoint certificate               MISSING; static next gap
  -> ordered-product certificate                     RECOVERED
```

The child-map loader occurs at lines 22–27 and executes the actual adjacent MC-032 source by `spec_from_file_location`, not by a normal import. Its file was recovered as the eighth file. A normal import-name-only scan would miss this path dependency. No stand-in or source edit was used.

The smoke normally imported the integration module, without invoking its factory. It reached the v50 model's import at line 18 and raised `ModuleNotFoundError` for `pb00701_algebraic_endpoint_model`. The traceback, return code 1 and absence of timeout are retained. This does not establish either historical target string in a new run.

## Known source/proof runtime edges

V53 `build_mixed_source_evidence` retains the complete v52 outcome. V52 calls v51 `build_ordered_source_evidence`; v51 delegates first to v50 `classify_required_analytic_event`; that method imports **missing `pb00701_mixed_multicut_model`** at v50 line 354. Its own dependency chain is not recovered. This is a separate obstacle to actual residual execution even after import-time gaps close.

The retained v7 B-spline module still imports missing `pb00701_rational_turn_model` at line 10. V52 lower_source calls the actual v7 lowerer. V50 finite owner checking imports specific supplied-witness checkers conditionally, while factor-root construction and endpoint checking have their own missing dependencies. These are recorded as reference sites, not assumed always-needed case paths.

## Visible residual queue

**Missing means not retained in this partial export, not absent from the repository.**

The queue has fifteen distinct missing module references in inspected source, not fifteen owners or a proved remaining closure size. Every unavailable file's own imports and byte identities must be established when it is actually retrieved. Prior metadata can guide discovery but is not a retained file.

| Module | Disposition / use | Observed reference |
|---|---|---|
| `pb00701_algebraic_endpoint_certificate.py` | Immediate fixture import-time recovery | `pb00701_ordered_product_model:14` |
| `pb00701_algebraic_endpoint_model.py` | Immediate fixture import-time recovery | `pb00701_vanishing_source_factor_model:18` |
| `pb00701_algebraic_monotone_cut_certificate.py` | Conditional proof/checker runtime reference; preserve exact branch use | `pb00701_vanishing_source_factor_model:144` |
| `pb00701_algebraic_monotone_cut_model.py` | Only a deferred no_search guard reference in inspected bytes; case necessity unproved | `test_pb00701_mixed_owner_span:58` |
| `pb00701_algebraic_orientation_cut_model.py` | Deferred representation/classifier references; selected-case necessity not established | `pb00701_algebraic_child_map_model:445` |
| `pb00701_mixed_multicut_certificate.py` | Conditional proof/checker runtime reference; preserve exact branch use | `pb00701_vanishing_source_factor_model:138` |
| `pb00701_mixed_multicut_model.py` | Fixed predecessor classifier; needed before residual can execute | `test_pb00701_mixed_owner_span:56` |
| `pb00701_mixed_orientation_consumer.py` | Conditional proof/checker runtime reference; preserve exact branch use | `test_pb00701_mixed_owner_span:57` |
| `pb00701_mixed_orientation_roots_model.py` | Conditional proof/checker runtime reference; preserve exact branch use | `pb00701_vanishing_source_factor_model:212` |
| `pb00701_multiharmonic_monotone_anchor_model.py` | Conditional proof/checker runtime reference; preserve exact branch use | `test_pb00701_mixed_owner_span:60` |
| `pb00701_rational_turn_model.py` | Original v7 dependency; unavailable module imports remain unknown | `pb00701_coupled_bspline_model:10` |
| `pb00701_vanishing_source_factor_certificate.py` | Conditional proof/checker runtime reference; preserve exact branch use | `pb00701_ordered_product_certificate:23` |
| `test_pb00701_mixed_boundary.py` | Deferred other-owner test helper / full-verifier dependency; not fetched for R1 smoke | `test_pb00701_mixed_owner_span:31` |
| `verify_pb00701_v51.py` | Deferred other-owner test helper / full-verifier dependency; not fetched for R1 smoke | `verify_pb00701_v53:63` |
| `verify_pb00701_v52.py` | Deferred other-owner test helper / full-verifier dependency; not fetched for R1 smoke | `verify_pb00701_v53:85` |

For all sites, function scopes and exact candidate paths, use `records/residual-recovery-queue.json`. This table does not authorize fetching every entry blindly or bypassing missing imports. The three verifier/helper files are deliberately deferred from minimal fixture work.

## External/environment boundary

Ordinary imports observed outside repository modules were Python standard-library modules. No missing installed third-party package was observed. The smoke used Python 3.13.5, whereas historical CI evidence in the earlier packet used Python 3.12.14; no numerical regression parity across those environments is claimed. All deeper source/package requirements remain unknown until their source is inspected. The current actual blocker is a missing repository file, not an invented package installation requirement.

## Preserved amplitude and ordered-span boundaries

The retained v7 `_dominance_certificate` supplies a rational coefficient-bound strict nonzero sign and its `SEPARATED_BY_EXACT_RATIONAL_AMPLITUDE_DOMINANCE` witness relation; the producer's separate route_kind is `EXACT_RATIONAL_AMPLITUDE_DOMINANCE`. This is not a derivative certificate. Its original-source binding and full finite checking would still need explicit review before any adapter is accepted.

The v53 strict/product view interface, v50 strict-owner checking, v51 complete direction extraction and v52 physical knot continuity are retained unchanged. V52's actual runtime discontinuity token remains `PHYSICAL_SOURCE_KNOT_DISCONTINUITY`. No predicate was changed to match a historical expectation. The comment's `97/200` margin and historical v54 adapter/inventory/test counts remain unverified claims in R1.

## Readiness decision

More specifically named recovery is required: begin with the observed algebraic-endpoint model gap and the statically named endpoint certificate, inspecting their imports before expanding. Do not begin canonical owner enumeration from this incomplete source closure. Neither recovered imports nor an eventual import PASS alone establishes that the reversed residual ran or that v54 is accepted.
