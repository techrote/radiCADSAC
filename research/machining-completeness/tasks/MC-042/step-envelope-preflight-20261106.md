# MC-042 — Exact-byte STEP Part-21 envelope preflight for future source-bound A–C runs

Status: **PROVISIONAL SOURCE-LEVEL PREPARATION ONLY**, 6 November 2026 UTC. Owner: [MC-042 #104](https://github.com/techrote/radiCADSAC/issues/104). Base: [main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`](https://github.com/techrote/radiCADSAC/commit/48222d6c40b15ad42cc36d56e6d25f3b284e7fc9).

## Purpose, hypothesis and non-goal

A later MC-042 native STEP Layers A–C qualification must bind **the exact STEP input bytes** before attempting independent STEP parsing/read-back, and must fail closed on incomplete, replaced or resource-unbounded inputs. This task adds a small, read-only *syntactic envelope and filesystem custody* sentinel. It consumes no unaccepted theorem and never emits or certifies a valid engineering solid.

**Hypothesis:** a pinned accepted output-profile document and a finite, exact-hash STEP byte candidate can be safely refused before any native import when size, pathname, hard-link custody, header/data envelope, single DATA entity marker or digest preconditions are violated. A synthetic complete envelope can be recognized without asserting geometry validity.

**Falsifiers:** a missing/changed source profile pin or mismatching file SHA-256 is admitted; overbudget/aliased/replaced/truncated/malformed envelope admitted; quoted/commented fake control sections are counted as real; a structural result is promoted to native or STEP geometry acceptance.

## Source facts and authority

* [DR-0026](../../../../docs/decisions/DR-0026-machining-completeness-programme.md) and [MC-1 programme](../../../../docs/machining-completeness/00-PROGRAMME.md) retain MC-B/MC-D/MC-E/MC-1 **NOT_ESTABLISHED**, and do not authorize production.
* [MC-054 output profile](../MC-054/engineering-output-profile-v1.json) is a reviewed **design decision**, not a native or independent-consumer run. Its Git blob is **`6d9d5924a39e5369a1999c48a9c508dc05fd818e`**; the script recomputes this blob in the live checkout with `git hash-object` and refuses drift.
* [MC-017 report](../MC-017/report.md) identifies a **source-viable but unexecuted** independent BRL-CAD/STEPcode consumer route. It does not provide a native success claim.
* MC-054 requires an explicit **manifest-only** outcome for `EMPTY_MATERIAL`; the sentinel refuses an empty STEP file rather than counting it as nonempty. It does **not** implement the empty-state manifest.
* The authorized output is conventional usable advanced B-rep STEP, not tessellated/mesh-wrapped geometry or a synthetic `#1=PLACEHOLDER` record.

## Implementation boundaries

One new independent script: `step_envelope_preflight.py`. Optional caller-supplied candidate `--step PATH --sha256 64hex`, or synthetic `--self-test`. The checker reads at most **1 MiB + 1 byte** from one opened descriptor, requires a regular file and one link, checks original and final path/descriptor metadata, binds **SHA-256 of actual bytes**, and conservatively recognizes the one-HEADER/one-DATA Part-21 section envelope while masking escaped strings and comments. It requires a `FILE_SCHEMA` declaration and at least one balanced, terminated DATA entity-constructor marker. The lexical guard refuses missing closing parentheses and missing instance semicolons while deliberately NOT attempting STEP/AP242 grammar or geometry validation. The 1 MiB limit, ASCII-only inspection and single-DATA restriction are **provisional constraints on this auxiliary checker, not restrictions on admissible native STEP / customer geometry or manufacturing input**. A later real native-scale importer may need a separately qualified streaming reader.

The positive in-test record deliberately contains `#1=NOT_A_REAL_BREP(...)`: it is **NOT valid proof of geometric STEP, not a genuine B-rep, not a producer file**. A syntactic recognized result is labelled `STRUCTURAL_ENVELOPE_ONLY_NOT_STEP_QUALIFIED`, with `native_step_parsed=false`, `geometry_qualified=false`, `mc_e_established=false`, `mc_1_established=false`, `production_authorized=false`. No producer authenticity is inferred merely from a provided digest.

## Executable verification

```sh
python research/machining-completeness/tasks/MC-042/step_envelope_preflight.py --self-test
python tools/validate_machining_completeness.py --self-test
python tools/validate_machining_completeness.py
```

The isolated `.github/workflows/mc042-step-envelope-preflight.yml` uses a **literal PR-head** checkout and checks its SHA before execution on hosted Ubuntu/Windows. On-disk refusals cover absent/mismatching digest, bad source pin, missing/duplicate section markers, missing schema/entity, unterminated quotes/comments, non-ASCII and byte budget. Four additional real on-disk negative mutations refuse an open DATA constructor, missing instance semicolon, surplus closing parenthesis and unbalanced header, without promoting this lexical check to full STEP syntax validation. Hard-link and symlink controls count only if creation succeeds; a real pathname replacement counts only if the OS permits it. Maintain source-critical review and preserve CI failures.

## Downstream blockers and next action

This is **DETERMINISTIC_MODEL**, not a STEP parser, AP242 schema validator, manifold-solid check, material/volume/body comparer, native run, BRL-CAD import, or STEP Layers A–D acceptance. MC-042 still requires MC-037 reconstruction authority, real MC-040/MC-041 engineering capability, source-bound native STEP generation, independent read-back and full per-fixture accuracy/error accounting. MC-043 and MC-044 remain separately unqualified. All 26 machining operations stay mandatory. MC-038/PB-007 mathematical obligations remain open. No permissions for paid runs, resumption, STEP qualification, manufacturing or production are changed.

Do not merge this research PR while the separate #397 owner holds main. Obtain distinct-session source-critical review of the exact head, then coordinate guarded merge and merged-main Windows/Linux qualification if accepted.
