# Authoritative source manifest — cumulative R1 packet

All complete byte exports are listed in `records/source-manifest.json` with ref, repository path, Git blob, SHA-256, byte/line counts, upstream URL, and prior-versus-new provenance. Eighteen unique ref/path entries are retained: eight reused and ten new. Duplicate preservation copies under `prior/2A/source/` do not add to this count.

## Newly recovered files

The first file recovered was the actual fixture helper. All ten files are at immutable commit `9734776b3cef3d7039be9623e8872df2c2a85174`. All are complete Git-blob matches. Paths are under `research/machining-completeness/tasks/MC-038/` except `MC-032/event_engine.py`.

| Order | File | Bytes / lines | Git blob | Recovery purpose |
|---|---|---|---|---|
| 1 | `test_pb00701_piecewise_product.py` | 9566 / 190 | `c847b27a8981aa3743291a60e267ee8d91d5b5d5` | Original exact encoder, power/physical-piece helpers and source reversal |
| 2 | `test_pb00701_mixed_owner_span.py` | 11725 / 212 | `f25e76dab22e47b6573a4c2fd8c1170677c887fb` | Core fixture helpers; source alias and deferred no-search guards |
| 3 | `test_pb00701_mixed_owner_span_integration.py` | 23909 / 375 | `050e6b2110d9d706a9cf96006b79e069adb7beac` | Exact candidate factory and preserved reversed-source assertions |
| 4 | `pb00701_piecewise_product_model.py` | 19289 / 308 | `6ca7a321bd027f3ed2a22059e9aa856c76485f8a` | Unchanged v52 lowering, knot continuity and composition |
| 5 | `pb00701_ordered_product_certificate.py` | 2401 / 49 | `81af2b07cb800a1e0636a8c737b9a492d774bb34` | Unchanged v51 supplied-product witness checker |
| 6 | `pb00701_ordered_product_model.py` | 24279 / 410 | `d36c5f5ce3b12840273d8483c467ff41a6e9ae01` | Unchanged v51 ordered wrapper and product/strict direction boundary |
| 7 | `pb00701_algebraic_child_map_model.py` | 21857 / 481 | `c055e7f392a921b386a1a99cc70b5004121ae7f6` | Unchanged v45 representation and import-time path loader |
| 8 | `MC-032/event_engine.py` | 10017 / 288 | `789a709c5141479a343035d1b7055dd4e53534e1` | Exact MC-032 rational/polynomial engine used by that loader |
| 9 | `pb00701_mixed_boundary_model.py` | 15678 / 334 | `4c4c9697b2237790d2e7ac8b96ec1dcdf2398303` | Unchanged mixed-boundary arithmetic and finite derivative recipes |
| 10 | `pb00701_vanishing_source_factor_model.py` | 21736 / 386 | `dfd554bf9ee41c96f9009f8ed8ceae485e134a5d` | Unchanged v50 source/classifier and finite strict-owner dispatch |

## Reading and checking coverage

Full content was transferred for each new file; imports and import-time path loaders were inspected statically. This is not a theorem-by-theorem audit of those source bodies. All 14 cumulative Python files were AST-inspected: 119 ordinary import sites plus one literal dynamic source load. No third-party import was observed in these files; dependencies inside missing modules remain unknown. Three of nine explicit additional pins in the retained v53 boundary currently have recovered bytes, and all three match. No full pin closure or contract test is claimed.

R1 reread AGENTS.md and the execution protocol without retaining them as new repository files. The prior 22-file source/reading manifest is preserved unchanged under `prior/2A/records/`; read-only excerpts there are not complete byte exports. Source files whose paths were already read partially in 2A still count as newly recovered when their complete bytes are first retained here.

## Integrity and negative transfer results

The v45 child-map file initially covered only lines 1–440 and failed its full-file Git blob check. Final-newline variants did not resolve that failure. The actual immutable tail at lines 441–481 was retrieved and the complete 481-line file now matches the original blob. The incomplete text was never admitted as a verified file or executed. This is a local selected-range omission, not corruption of the authoritative repository. See `logs/child-map-range-completeness.json`.

A single bounded direct raw-file byte GET failed DNS (curl exit 6) and returned no source. It was not retried. All actual new bytes came through the authenticated connector. No old ZIP/gzip recovery or source-export workflow was attempted.

After the one import smoke, all 18 source Git blobs and SHA-256 values still matched. See `logs/post-smoke-source-integrity.json`. Package SHA256SUMS authenticates every packaged file except itself; it does not supply missing Git history or certify mathematical behavior.
