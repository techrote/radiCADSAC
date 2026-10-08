# Commands, source reads and actual results — 2A-R1

## Restoration and authority delta

Local commands throughout used explicit container/shell timeouts (typically 10 seconds; the one import supervisor had an outer 20-second limit). Restore used Python zipfile/hashlib to check the actual input archive against `radiCADSAC-2A-packet-verification.json`, reject unsafe paths/symlinks/duplicates, check CRC/read every member, compare all SHA256SUMS entries and the exact file set, then extract into the isolated workspace. Result: PASS, 53 files, 52 hashes. Eight inherited source Git blobs were recomputed and matched. See `logs/prior-packet-restoration.json` and `logs/retained-blob-verification.json`.

Fresh read-only connector calls were main ref, v54-prefix matching refs, issue #275, AGENTS.md, and the execution protocol. No workflow or status calls, dispatch, PR/issue mutation, coordination or source writes occurred. Exact endpoints are in `records/authority-refresh.json`. Reused prior source/reading/acceptance records were inspected locally, not replaced by earlier chat summaries.

## New immutable source transfer batch

Every row uses `GitHub.fetch_file(repository_full_name="techrote/radiCADSAC", path=<path>, ref="9734776b3cef3d7039be9623e8872df2c2a85174")`. Ranges below are the actual requested 1-based ranges; full-file hashes establish complete final byte coverage. Long-file range boundaries were not treated as EOF.

| File | Calls / requested ranges | Final result |
|---|---|---|
| MC-038/test_pb00701_piecewise_product.py | full, response turn70 | blob PASS |
| MC-038/test_pb00701_mixed_owner_span.py | full, turn72 | blob PASS |
| MC-038/test_pb00701_mixed_owner_span_integration.py | 1–205, 206–600; turns73/74 | blob PASS, 375 lines |
| MC-038/pb00701_piecewise_product_model.py | 1–170, 171–500; turns75/76 | blob PASS, 308 lines |
| MC-038/pb00701_ordered_product_certificate.py | full, turn77 | blob PASS |
| MC-038/pb00701_ordered_product_model.py | 1–220, 221–440; turns78/79 | blob PASS, 410 lines |
| MC-038/pb00701_algebraic_child_map_model.py | 1–220, 221–440, 441–800; turns80/81/82 | first 440-line candidate rejected; complete 481-line blob PASS |
| MC-032/event_engine.py | 1–230, 231–600; turns83/84 | blob PASS, 288 lines |
| MC-038/pb00701_mixed_boundary_model.py | 1–220, 221–500; turns85/86 | blob PASS, 334 lines |
| MC-038/pb00701_vanishing_source_factor_model.py | 1–230, 231–520; turns87/88 | blob PASS, 386 lines |

Paths above are relative to `research/machining-completeness/tasks/`. Ten new repository files, not ten calls. The selected path strings came from the earlier mapped fixture chain or actual newly inspected imports. No whole tree or old archive was fetched.

Each transfer was persisted verbatim and checked with:

```sh
python tools/register_source.py <file-or-repository-path> <expected-git-blob> <read-evidence>
```

The script derives the Git blob header/length hash and a separate SHA-256, rejects mismatches and enforces the ten-file cap. Complete final source values are in `records/source-manifest.json`. The negative child-map transfer attempt is recorded in `logs/child-map-range-completeness.json`; it was not executed or retained as authority. No source semantics were edited.

One supplemental bounded raw-byte transport probe ran `timeout 18s curl --fail --silent --show-error --max-time 15 --connect-timeout 5` against the immutable integration-file raw URL. It failed DNS with curl exit 6 and returned no bytes; no retry was performed. Connector file transfer worked. See `logs/immutable-byte-transport-probe.txt`. This was not historical v54 archive recovery.

## Static dependency inspection

```sh
timeout 10s python -I -B tools/map_dependencies.py
```

Result: exit 0; fourteen retained Python files AST-parsed, 119 ordinary import sites, one literal file-path load. No repository functions invoked. The file-path load resolves the original `MC-032/event_engine.py`; it is not a package guess. The static queue has two immediate import-time gaps for the fixture, plus conditional runtime and deferred test/verifier references. Fifteen missing references are only the visible frontier, not the complete transitive closure or a proof-owner inventory. Missing means not present in this export, not absent from GitHub.

## Single import-only smoke — actually executed once

Supervisor command:

```sh
timeout 20s python -I -B tools/run_import_smoke.py
```

The supervisor used `subprocess.run([...], timeout=15, check=False)` to run exactly:

```sh
/opt/pyvenv/bin/python -I -B tools/import_only.py
```

`tools/import_only.py` adds only the packet's original MC-038 directory to its source search path and performs `importlib.import_module("test_pb00701_mixed_owner_span_integration")`. It does not invoke the factory, tests, proof builders or verifiers; does not patch imports; and does not install stand-ins. Ordinary source module initialization executes, including the original MC-032 file loader. Bytecode writing is disabled.

Actual child result: **exit 1, 0.755 seconds, no timeout**, on Python 3.13.5:

```text
ModuleNotFoundError: No module named 'pb00701_algebraic_endpoint_model'
```

The last source location is `pb00701_vanishing_source_factor_model.py:18`. The command record, full stdout JSON and traceback stderr are retained under `logs/import-smoke-*`. The supervisor's own successful recording exit is not an import PASS. This is a source-closure failure, not a mathematics result.

## Case disposition and integrity checks

Reversed residual: NOT RUN. The import prerequisite failed and the ten-file source batch was exhausted. No case command was executed. `logs/residual-case-disposition.json` records `actual_owner=null`, `actual_refusal=null`, and no new margin. The historical expected owner/refusal strings were not substituted for measured output.

All eighteen source blob/SHA256 pairs were rechecked after the smoke: PASS. An independent structural comparison against the three currently available additional historical v53 blob pins also passed; six other additional pins lack bytes, and the verifier itself was not invoked. See `logs/post-smoke-source-integrity.json` and `logs/available-v53-pin-intersection.json`.

Final packaging generates SHA256SUMS, then runs `python3 -I -B tools/verify_packet.py .` and verifies the ZIP independently by CRC/member readability, exact file set, member hashes and a fresh extraction. The external archive-verification JSON records those actual results separately. These checks do not execute source or confer proof/acceptance.
