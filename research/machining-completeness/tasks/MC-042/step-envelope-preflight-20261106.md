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

One new independent script: `step_envelope_preflight.py`. Optional caller-supplied candidate `--step PATH --sha256 64hex`, or synthetic `--self-test`. The checker reads at most **1 MiB + 1 byte** from one opened descriptor, requires a regular file and one link, checks original and final path/descriptor metadata, binds **SHA-256 of actual bytes**, and conservatively recognizes the one-HEADER/one-DATA Part-21 section envelope while masking escaped strings and comments. It requires a `FILE_SCHEMA` declaration and at least one balanced, terminated DATA entity-constructor marker. The lexical guard refuses missing closing parentheses, missing instance semicolons, malformed extra instances and trailing DATA junk while deliberately NOT attempting STEP/AP242 grammar or geometry validation. It scans every top-level DATA instance in a bounded linear pass, not merely one successful constructor in a potentially truncated inventory. The 1 MiB limit, ASCII-only inspection and single-DATA restriction are **provisional constraints on this auxiliary checker, not restrictions on admissible native STEP / customer geometry or manufacturing input**. A later real native-scale importer may need a separately qualified streaming reader.

The positive in-test record deliberately contains `#1=NOT_A_REAL_BREP(...)`: it is **NOT valid proof of geometric STEP, not a genuine B-rep, not a producer file**. A syntactic recognized result is labelled `STRUCTURAL_ENVELOPE_ONLY_NOT_STEP_QUALIFIED`, with `native_step_parsed=false`, `geometry_qualified=false`, `mc_e_established=false`, `mc_1_established=false`, `production_authorized=false`. No producer authenticity is inferred merely from a provided digest.

## Executable verification

```sh
python research/machining-completeness/tasks/MC-042/step_envelope_preflight.py --self-test
python tools/validate_machining_completeness.py --self-test
python tools/validate_machining_completeness.py
```

The isolated `.github/workflows/mc042-step-envelope-preflight.yml` uses a **literal PR-head** checkout and checks its SHA before execution on hosted Ubuntu/Windows. On-disk refusals cover absent/mismatching digest, bad source pin, missing/duplicate section markers, missing schema/entity, unterminated quotes/comments, non-ASCII and byte budget. Four original on-disk lexical mutations refuse an open DATA constructor, missing instance semicolon, surplus closing parenthesis and unbalanced header. Six further on-disk controls expose/refuse malformed *subsequent* DATA instances or arbitrary trailing junk after an otherwise complete first instance; two added positive controls accept complete two-instance (including complex constructor) synthetic records with quoted section decoys. These are intentionally not STEP semantic-validity, schema, topology or geometry tests. Hard-link and symlink controls count only if creation succeeds; a real pathname replacement counts only if the OS permits it. Maintain source-critical review and preserve CI failures.

## Downstream blockers and next action

This is **DETERMINISTIC_MODEL**, not a STEP parser, AP242 schema validator, manifold-solid check, material/volume/body comparer, native run, BRL-CAD import, or STEP Layers A–D acceptance. MC-042 still requires MC-037 reconstruction authority, real MC-040/MC-041 engineering capability, source-bound native STEP generation, independent read-back and full per-fixture accuracy/error accounting. MC-043 and MC-044 remain separately unqualified. All 26 machining operations stay mandatory. MC-038/PB-007 mathematical obligations remain open. No permissions for paid runs, resumption, STEP qualification, manufacturing or production are changed.

Do not merge this research PR while the separate #397 owner holds main. Obtain distinct-session source-critical review of the exact head, then coordinate guarded merge and merged-main Windows/Linux qualification if accepted.

### 6 November distinct-session HEADER truncation repair

[Independent source-critical REPAIR/HOLD #5796581107](https://github.com/techrote/radiCADSAC/pull/426#pullrequestreview-5796581107) reproduced three malformed HEADER inputs that the predecessor `8fc26447` admitted: removing the terminating semicolon from `FILE_SCHEMA(('AP242'));`, removing the terminator from `FILE_DESCRIPTION(...);`, or adding unmatched top-level `JUNK_AFTER_SCHEMA` before HEADER's `ENDSEC;`. Earlier green CI covered complete DATA-instance lists but did **not** cover these HEADER truncations. The original negative review remains retained as evidence.

The correction adds a **linear lexical HEADER constructor/terminator scan** over already quote/comment-masked text: each top-level named record must have balanced parentheses and its own `;`; exactly one `FILE_SCHEMA` must be present. Four new actual on-disk refusal mutations (the three above plus duplicate FILE_SCHEMA) and one new positive multi-record HEADER control accompany the previous complete DATA-inventory, identity, SHA and source-pin controls. This is an intentionally restricted *synthetic* envelope sentinel, not STEP/AP242 grammar, B-rep geometry or engineering output acceptance; valid native STEP outside this conservative helper's lexical subset requires separate native qualification, not domain restriction.

Any newly repaired branch head needs fresh **literal-head** hosted Windows/Linux checks plus separately identified PR-merge MC-1 static checks; a future *distinct-session* reviewer must admit the exact corrected source before Ready or merge. Preserve [#397's main reservation](https://github.com/techrote/radiCADSAC/pull/397) and all PB-007/MC/production refusals. This correction does not alter MC-054 profile identity or any source/capability authority.

### 6 November detached payload and inter-section gap correction

A distinct-session lexical audit of the corrected HEADER/DATA inventory found an additional source-matched **negative admission witness**: a nonempty unquoted payload placed between `ISO-10303-21;` and `HEADER;`, between `HEADER/ENDSEC;` and `DATA;`, or between `DATA/ENDSEC;` and `END-ISO-10303-21;` was ignored. Separately, `visible_tokens` erased free-standing quoted strings everywhere, so a detached `'literal'` before/after the outer envelope, in those gaps, or after otherwise complete HEADER/DATA records also disappeared and could be admitted. These cases contradict this helper's *complete syntactic envelope* refusal promise, without establishing anything about real STEP grammar or solids.

The corrected sentinel uses a normal quote-masked view **only to identify real section markers**, then a second, bounded linear view which retains one nonwhitespace sentinel per quoted string while masking comments. It refuses all five outside-section regions unless they contain only whitespace/comments, and uses that structural view for the complete HEADER/DATA inventories. **Ten on-disk negative controls** cover the three section gaps, five detached-string locations, and detached quoted records inside HEADER and DATA; one new positive control preserves comment-only inter-section gaps and the original quoted-decoy positive cases. Existing bounded byte, descriptor, SHA, frozen-profile, exact six-section, and conservative refusal checks remain in force. The added second linear scan is limited by the same 1 MiB input cap.

This is still an intentionally restricted **DETERMINISTIC_MODEL lexical sentinel**: positive synthetic records (including `NOT_A_REAL_BREP`) are not AP242, native/STEP parser, B-rep, geometry, material lineage, independent consumer or MC-E evidence. Future code changes require literal-head Windows/Linux CI and separate synthetic PR-merge static qualification; a distinct-session technical admission is required before Ready. No #397 main-integration lease override, PB/MC promotion, production release or paid/native campaign is authorized.

### 6 November duplicate DATA-instance identifier correction (separate task-local session)

The qualified structural scanner previously accepted a complete syntactic sequence containing repeated numeric DATA instance identifiers, e.g. `#1=FIRST(); #1=SECOND();`. An independently executed source-matched extraction confirmed that both an adjacent duplicate and a nonadjacent repeat were accepted despite the otherwise complete-constructor inventory checks. In a real Part-21 DATA section these are ambiguous instance definitions, not two distinct records.

The bounded lexical inventory now retains each decimal instance identifier encountered and refuses any second occurrence before scanning the next constructor; the set is bounded by the pre-existing **1 MiB** byte budget. New *on-disk* negative controls cover adjacent `#1`, nonadjacent `#1` after a valid `#2`, and repeated `#2` following a complex constructor. A new positive three-entity control retains distinct `#1/#2/#3` admission alongside previous two-instance/complex positives. Prior comment/quoted-string masking, exact SHA-256/source pin, alias/path/descriptor checks and all header/section/size refusals remain.

This is only a conservative unambiguous-identity lexical refusal. It does **not** validate entity types, references, AP242 schemas, B-rep validity, topology, native material, independent STEP consumption or output fidelity. The accepted operation denominator **26**, all PB-007 and MC gate states, and production restriction are unchanged. The amended PR must remain **Draft pending fresh literal-head Ubuntu/Windows qualification and a new distinct-session technical review**. No merge while #397 holds exclusive main integration.

### 6 November mandatory Part-21 HEADER triad regression (separate source-critical session)

**Reproduced defect:** The previous *positive* synthetic Part-21 candidate omitted `FILE_NAME`, and `_has_complete_header_inventory` accepted any otherwise complete header constructor sequence provided one `FILE_SCHEMA` occurred. Therefore it accepted a structurally incomplete HEADER while labeling the result a complete lexical envelope. This is a source/fixture correctness problem, not evidence that a native STEP parser or engineering geometry succeeded.

**External source authority:** Library of Congress STEP-file format description (https://www.loc.gov/preservation/digital/formats/fdd/fdd000448.shtml) states that the mandatory HEADER records are `FILE_DESCRIPTION`, `FILE_NAME` and `FILE_SCHEMA`, once each, in precisely that order. The new scanner enforces that minimal structural requirement, rejects out-of-order or duplicated mandatory records and allows additional complete *lexical* records after the triad. It does not validate record argument arity, optional record semantics, the EXPRESS schema, AP242 or actual geometry.

**Corrected deterministic fixture:** The synthetic positive now includes all three mandatory named records with a seven-argument `FILE_NAME` constructor. The previously positive duplicate `FILE_NAME` variant is replaced by a post-triad optional lexical-record positive. New on-disk negative regressions cover omission of each of the three mandatory records, two pairwise ordering errors, duplication of each mandatory record, and a preemptive nonmandatory constructor (**nine new refusal cases**). These run through the existing exact-byte `inspect` path, preserving source-pin, digest, file-custody and refusal semantics. Other prior positive and negative controls remain.

**Custody and limits:** Source changes are confined to this PR's existing MC-042 validator and task-local RAG record. The earlier `b26cd0f3` source, previous green CI and source-critical review remain historical evidence, **not proof of the corrected head**. The new head requires fresh literal-head Ubuntu/Windows focused CI and separate MC-1 static verification. Leave PR **DRAFT** until a later distinct-session review admits the changed code. A separate #397 owner retains exclusive `main` integration; do not merge or write to main. PB-007 OPEN, MC-B/D/E/MC-1 NOT_ESTABLISHED, 26 operations mandatory, no native STEP or manufacturing claim.
