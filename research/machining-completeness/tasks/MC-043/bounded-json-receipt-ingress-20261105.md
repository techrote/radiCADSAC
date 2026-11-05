# MC-043 — bounded structural receipt JSON ingress (2026-11-05)

**Owner/task:** Prepare radiCADSAC Engineering; MC-043 [#105](https://github.com/techrote/radiCADSAC/issues/105). **Base main:** `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. **Branch:** `fix/mc043-bounded-json-receipt-ingress-20261105`. Coordination claim: [#324/6672106938](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6672106938).

## Observable defect and falsification

Previous CLI `Path.read_bytes()` allocated the entirety of both manifest and consumer receipt files before parsing. `json.loads` had no explicit nesting or integer-token budget. Overbudget and pathologically nested structural evidence could exhaust resources before typed refusal. The falsifier is a >1 MiB receipt/manifest accepted, unbounded allocation before a resource check, >32 nested JSON containers parsed, or a >128 decimal-digit JSON integer admitted.

## Bounded correction and exact controls

The source now rejects raw JSON exceeding **1,048,576 bytes**, recursively nested containers exceeding **32 levels**, and integers exceeding **128 decimal digits**. A quote/escape-aware **decoded-character** scanner applies the depth limit **before** JSON parsing, after bounded byte decoding with the same UTF-8/16/32 encoding detection as Python's JSON reader. `read_json_file` reads **MAX+1 bytes** on actual regular-file handles and refuses oversized files before invoking any JSON parser. Existing duplicate-key, finite-float, Unicode scalar, receipt binding, descriptor STEP custody and structural checks are preserved.

The existing 47 rejected mutations, four positive synthetic structural controls and actual file-swap/alias cases remain. Ten new refusal controls cover oversized in-memory JSON, excessive nesting, oversized integer token, malformed excess delimiter, actual oversized disk-file read and actual CLI exit-2 `REJECTED` results on both manifest and receipt. Positive boundary controls exercise the exact 1 MiB size, depth 32, a 128-digit integer and quoted non-container delimiters. Additional admissible UTF-16LE/BE and UTF-32LE/BE/BOM-bearing positive controls contain U+0122 (low byte 0x22) and forty literal brackets, while genuine over-depth UTF-16/32 and malformed UTF-8 are refused. Existing manifest/receipt wire format is unchanged.

## Evidence and source custody

Required qualification on literal final head: `python3 research/machining-completeness/tasks/MC-043/verify.py --contract --self-test`, `python3 tools/validate_machining_completeness.py`, MC-043 receipt-preflight CI, and all applicable Windows/Linux step-custody controls. Record failed intermediate heads and exact Actions run/job evidence; do not treat green unrelated workflows as sufficient. This is **an unmerged candidate** until separately reviewed and qualified. An owner-account `COMMENTED` review is not independent human `APPROVED`.

## Explicit nonclaims and prerequisites

The resource guard is not atomic descriptor/path custody for the manifest/receipt, cryptographic authentication of producer/consumer, STEP parsing, native material execution, independent consumer performance, an engineering geometry verdict or a production permit. Its positives use SYNTHETIC NON-STEP bytes. MC-043 still requires source-authenticated MC-040/042 actual native STEP evidence and an independently executed consumer engineering operation. PB-007-01..04 remain OPEN; MC-B, MC-D, MC-E, MC-F and MC-1 remain NOT_ESTABLISHED; all 26 operations are mandatory. No mathematical, gate, authority, frozen corpus, native or production files are changed.


## Distinct-session 5 November encoding-correctness repair (admission review #5793821320)

The first qualified candidate scanned **raw bytes**, assuming UTF-8, while Python's `json.loads(bytes)` already admitted UTF-16/32. In those encodings a valid code point such as U+0122 contains a `0x22` byte that impersonated a quote, falsely counting bracket characters in a string as JSON nesting. Independent adversarial reproduction established a valid depth-one document rejected on UTF-16LE/BE and UTF-32LE/BE, while the same JSON in UTF-8 passed. The corrected candidate decodes at most 1 MiB with Python's existing JSON encoding detector, scans actual characters **before JSON parsing**, and preserves all previously admitted encodings and strict refusal hooks. Tests add six positive encoded variants, two negative genuinely deep alternate-encoding variants and malformed UTF-8 (57 total refusals). The corrected head remains **Draft / no merge** pending fresh literal-head CI and a new independent review; do not reuse the superseded head's successful runs.
