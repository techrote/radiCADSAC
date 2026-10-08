#!/usr/bin/env python3
"""Package the bounded R1 recovery observations; never execute repository proofs."""
import json
from pathlib import Path
from datetime import datetime, timezone

R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'records/source-manifest.json').read_text())
new=[r for r in manifest if r['batch']=='2A-R1_NEW']
smoke=json.loads((R/'logs/import-smoke.stdout.txt').read_text())
run=json.loads((R/'logs/import-smoke-command.json').read_text())
deps=json.loads((R/'records/dependency-map.json').read_text())
queue=json.loads((R/'records/residual-recovery-queue.json').read_text())
now=datetime.now(timezone.utc).isoformat()
roles={
 'test_pb00701_piecewise_product.py':'Original exact encoder, power/physical-piece helpers and source reversal',
 'test_pb00701_mixed_owner_span.py':'Core fixture helpers; source alias and deferred no-search guards',
 'test_pb00701_mixed_owner_span_integration.py':'Exact candidate factory and preserved reversed-source assertions',
 'pb00701_piecewise_product_model.py':'Unchanged v52 lowering, knot continuity and composition',
 'pb00701_ordered_product_certificate.py':'Unchanged v51 supplied-product witness checker',
 'pb00701_ordered_product_model.py':'Unchanged v51 ordered wrapper and product/strict direction boundary',
 'pb00701_algebraic_child_map_model.py':'Unchanged v45 representation and import-time path loader',
 'event_engine.py':'Exact MC-032 rational/polynomial engine used by that loader',
 'pb00701_mixed_boundary_model.py':'Unchanged mixed-boundary arithmetic and finite derivative recipes',
 'pb00701_vanishing_source_factor_model.py':'Unchanged v50 source/classifier and finite strict-owner dispatch'}

checkpoint=f'''# CHECKPOINT — radiCADSAC #275 / PB-007-01 v54 / 2A-R1

**Status: PARTIAL. Readiness: MORE_NAMED_SOURCE_RECOVERY_NEEDED.**  
Recorded: {now}. No successor chunk executed.

## Result and stop boundary

The ten-file recovery batch is complete and byte-verified. The exact three-file fixture chain is now retained, but its transitive source closure is not importable. The one import-only smoke failed at `pb00701_vanishing_source_factor_model.py:18` with:

```text
ModuleNotFoundError: No module named 'pb00701_algebraic_endpoint_model'
```

The command exited **1**, without timeout ({run['elapsed_seconds']:.3f} seconds; 15-second limit). No fixture factory, reversed residual, test method, contract verifier or full predecessor chain ran. There is no new measured owner, margin or mathematical refusal in R1.

## Restored authority

The actual input `radiCADSAC-2A-packet.zip`, SHA-256 `074e172c6c7995d3022b985a0a06ae1542a0c01b8fb6d06b62210fca3738309d`, passed CRC/readability, all 52 manifest hashes and the exact 53-file check. Its extracted files remain unchanged under `prior/2A/`. The eight reused original source files were independently rehashed before use.

Selected immutable source commit remains `9734776b3cef3d7039be9623e8872df2c2a85174`, tree `b0240e4d02a6165f8799d7af432ea36416009667`. Live main, both v54-prefix refs and #275 metadata showed no relevant change. Issue #275 remains the existing owner, open, with five comments and last update `2026-10-03T10:10:22Z`. Trees and acceptance context are reused from the verified earlier packet, not re-derived from a full local checkout. See `AUTHORITY_LEDGER.md` for limits.

## Portable material

`source/` contains **18 unique ref/path entries**: eight reused plus ten newly recovered; 16 are pinned-main files and two are historical branch workflow scaffolds. The 14 retained Python files were inspected statically for imports. Every source entry matches the upstream Git blob and separately recorded SHA-256; all 18 were rechecked after the smoke. Three available v53 historical pins match; the other six pinned files are not retained. This is **not** a complete authenticated Git tree, Git history, runnable v54 implementation or complete predecessor export.

The old 22-file reading manifest remains under `prior/2A/records/`. It is not a claim that 22 full source files were previously recovered. Complete current byte coverage is solely `records/source-manifest.json`.

## Exact next recovery boundary

The next immediate file is `research/machining-completeness/tasks/MC-038/pb00701_algebraic_endpoint_model.py`, named by the actual import exception. The other statically visible import-time gap is `pb00701_algebraic_endpoint_certificate.py`, imported at v51 model line 14. Their own imports remain unknown, so recovering those two must not be advertised as guaranteed closure.

The unchanged source wrapper additionally enters `pb00701_mixed_multicut_model.classify_required_analytic_event`; this file is not recovered. The retained v7 lowerer still imports missing `pb00701_rational_turn_model.py`. Conditional owner checkers and other proof/runtime references, plus explicitly deferred test/full-verifier references, are listed with source lines in `records/residual-recovery-queue.json`. Fifteen visible missing module references are **not** a complete transitive count or an owner count.

Choose another specifically bounded **source recovery** increment, not owner enumeration, existing-v54-adapter review or acceptance verification. No canonical v54 inventory/adapter bytes were recovered or trusted. The malformed historical payload was not retried. No source imports were altered or mocked to obtain success.

## Preserved limits

Historical target: `EXACT_RATIONAL_AMPLITUDE_DOMINANCE` / `SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE`. Those strings are inspected existing assertions, not fresh runtime results. Whole-span nonzero-sign evidence is not derivative/monotonicity authority. Original source, actual owners, refusal semantics and all 26 operations are unchanged. PB-007-01 remains globally OPEN; MC-B and MC-1 remain NOT_ESTABLISHED; v54 acceptance is not established. No remote writes, workflow dispatch, coordination writes, native/shared-resource execution, successor issues or 2B work occurred.

## Navigation

Read `SOURCE_DEPENDENCY_MAP.md`, `SOURCE_MANIFEST.md`, `COMMANDS_RESULTS.md` and `FINDINGS.md`. `logs/import-smoke.stdout.txt` and `.stderr.txt` preserve the actual exception and traceback. `tools/verify_packet.py` verifies package hashes and source blobs without importing source. The ZIP's external verification JSON separately records archive integrity; it is not implementation acceptance.
'''
(R/'CHECKPOINT.md').write_text(checkpoint)

text='''# Authority and recoverability ledger — R1 delta

This extends, and does not replace or silently rewrite, `prior/2A/AUTHORITY_LEDGER.md` and its machine records. The source selector is unchanged. Remote refs were read once; no final lock or publication check is claimed.

| Reference | Observed commit | Root tree | R1 disposition |
|---|---|---|---|
| main | `9734776b3cef3d7039be9623e8872df2c2a85174` | `b0240e4d02a6165f8799d7af432ea36416009667` | Live ref unchanged; immutable tree reused from verified 2A |
| mc038/pb00701-v54-recovery | `823a8624739c337aeb41470cfebebd2ea2a931ca` | `99f93a6c2dcc5e60965ceefc9a5e9ec25409f4bd` | Unchanged; only recovery scaffold per preserved comparison |
| mc038/pb00701-v54-finite-owner-coverage | `8cec4953dc898e70270c654f5453b108bb80d47b` | `6afc28d6b83f5c631b63c67d3e9b1ad93188e6a2` | Unchanged; baseline workflow and incomplete staging per preserved comparison |

## Current instructions and issue

AGENTS.md and `docs/machining-completeness/07-EXECUTION-PROTOCOL.md` were reread completely at the selected immutable commit; their reported blobs match prior records. They are reading evidence, not additional newly exported files. `handoffs/current-authority.json` was read from the retained hash-verified bytes. The current user's recovery-only and read-only contract overrides remote publication, ownership announcements and full-verifier requirements in older execution instructions for this chunk; acceptance requirements are not waived.

The complete #275 body was reread. State OPEN, comments 5, updated 2026-10-03T10:10:22Z match the prior packet. Existing comments and their contradictions were reused from the verified packet rather than reread as an opening audit. No newly published work was identified on the inspected refs or issue. No global search for arbitrary unnamed branches/PRs was performed. The prior branch-specific no-PR results and PR273/274 acceptance records remain historical evidence, not newly queried results.

## Accepted baseline versus unaccepted work

The accepted bounded v53 implementation is `a13702b28fcc349442e78cfb1e971eb94991a69e`, checked tree `17fe7642600b12edd573e21b57933e5811cea991`, followed by the documentation-only PR274 reconciliation at selected main. PR273/274 and #271/#100 acceptance metadata are retained under `prior/2A/records/`. No CI result was fetched or rerun in R1. No historical inventory counts or adapter claims become verified through source recovery.

The malformed staging archive and expired source exports were neither retried nor recreated. No recoverable accepted v54 source was obtained; this increment consists exclusively of authoritative unchanged predecessor files at main. The historical two workflow files are preserved separately from main code and are not enabled or run locally.

## Evidence endpoints and authentication boundary

The fresh reads are recorded with URLs and response identifiers in `records/authority-refresh.json`. Source reads used authenticated `GitHub.fetch_file` at the selected immutable commit, followed by a local `sha1("blob " + length + NUL + bytes)` match. SHA-256 is independently recorded for portability. This authenticates individual file content against connector-reported blob/ref identities; it does not verify a complete Git tree, commit ancestry or a new acceptance decision.
'''
(R/'AUTHORITY_LEDGER.md').write_text(text)

a=json.loads((R/'records/authority-refresh.json').read_text())
a['read_endpoints']=[
 {'resource':'/response/turn66','url':'https://api.github.com/repos/techrote/radiCADSAC/git/ref/heads/main','method':'GET'},
 {'resource':'/response/turn67','url':'https://api.github.com/repos/techrote/radiCADSAC/git/matching-refs/heads/mc038/pb00701-v54','method':'GET'},
 {'resource':'/response/turn68','url':'https://github.com/techrote/radiCADSAC/issues/275','method':'GitHub.fetch_issue; full body'},
 {'resource':'/response/turn69','url':'https://github.com/techrote/radiCADSAC/blob/9734776b3cef3d7039be9623e8872df2c2a85174/AGENTS.md','method':'GitHub.fetch_file; full read; no new export'},
 {'resource':'/response/turn71','url':'https://github.com/techrote/radiCADSAC/blob/9734776b3cef3d7039be9623e8872df2c2a85174/docs/machining-completeness/07-EXECUTION-PROTOCOL.md','method':'GitHub.fetch_file; full read; no new export'}]
(R/'records/authority-refresh.json').write_text(json.dumps(a,indent=2)+'\n')

text='''# Authoritative source manifest — cumulative R1 packet

All complete byte exports are listed in `records/source-manifest.json` with ref, repository path, Git blob, SHA-256, byte/line counts, upstream URL, and prior-versus-new provenance. Eighteen unique ref/path entries are retained: eight reused and ten new. Duplicate preservation copies under `prior/2A/source/` do not add to this count.

## Newly recovered files

The first file recovered was the actual fixture helper. All ten files are at immutable commit `9734776b3cef3d7039be9623e8872df2c2a85174`. All are complete Git-blob matches. Paths are under `research/machining-completeness/tasks/MC-038/` except `MC-032/event_engine.py`.

| Order | File | Bytes / lines | Git blob | Recovery purpose |
|---|---|---|---|---|
'''
for r in new:
 name=Path(r['repository_path']).name
 display='MC-032/event_engine.py' if name=='event_engine.py' else name
 text+=f"| {r['recovery_order']} | `{display}` | {r['bytes']} / {r['lines']} | `{r['git_blob']}` | {roles[name]} |\n"
text+='''
## Reading and checking coverage

Full content was transferred for each new file; imports and import-time path loaders were inspected statically. This is not a theorem-by-theorem audit of those source bodies. All 14 cumulative Python files were AST-inspected: 119 ordinary import sites plus one literal dynamic source load. No third-party import was observed in these files; dependencies inside missing modules remain unknown. Three of nine explicit additional pins in the retained v53 boundary currently have recovered bytes, and all three match. No full pin closure or contract test is claimed.

R1 reread AGENTS.md and the execution protocol without retaining them as new repository files. The prior 22-file source/reading manifest is preserved unchanged under `prior/2A/records/`; read-only excerpts there are not complete byte exports. Source files whose paths were already read partially in 2A still count as newly recovered when their complete bytes are first retained here.

## Integrity and negative transfer results

The v45 child-map file initially covered only lines 1–440 and failed its full-file Git blob check. Final-newline variants did not resolve that failure. The actual immutable tail at lines 441–481 was retrieved and the complete 481-line file now matches the original blob. The incomplete text was never admitted as a verified file or executed. This is a local selected-range omission, not corruption of the authoritative repository. See `logs/child-map-range-completeness.json`.

A single bounded direct raw-file byte GET failed DNS (curl exit 6) and returned no source. It was not retried. All actual new bytes came through the authenticated connector. No old ZIP/gzip recovery or source-export workflow was attempted.

After the one import smoke, all 18 source Git blobs and SHA-256 values still matched. See `logs/post-smoke-source-integrity.json`. Package SHA256SUMS authenticates every packaged file except itself; it does not supply missing Git history or certify mathematical behavior.
'''
(R/'SOURCE_MANIFEST.md').write_text(text)

text='''# Source/dependency map — after 2A-R1

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

The queue has fifteen distinct missing module references in inspected source, not fifteen owners or a proved remaining closure size. Every unavailable file's own imports and byte identities must be established when it is actually retrieved. Prior metadata can guide discovery but is not a retained file.

| Module | Disposition / use | Observed reference |
|---|---|---|
'''
for q in queue:
 name=q['module']; refs=q['observed_import_sites']
 site=refs[0]['from_module']+':'+str(refs[0]['line'])
 if name in deps['fixture_import_time_missing_modules']:
  why='Immediate fixture import-time recovery'
 elif name=='pb00701_mixed_multicut_model':
  why='Fixed predecessor classifier; needed before residual can execute'
 elif name=='pb00701_rational_turn_model':
  why='Original v7 dependency; unavailable module imports remain unknown'
 elif name in ('test_pb00701_mixed_boundary','verify_pb00701_v51','verify_pb00701_v52'):
  why='Deferred other-owner test helper / full-verifier dependency; not fetched for R1 smoke'
 elif name=='pb00701_algebraic_monotone_cut_model':
  why='Only a deferred no_search guard reference in inspected bytes; case necessity unproved'
 elif name=='pb00701_algebraic_orientation_cut_model':
  why='Deferred representation/classifier references; selected-case necessity not established'
 else:
  why='Conditional proof/checker runtime reference; preserve exact branch use'
 text+=f'| `{name}.py` | {why} | `{site}` |\n'
text+='''
For all sites, function scopes and exact candidate paths, use `records/residual-recovery-queue.json`. This table does not authorize fetching every entry blindly or bypassing missing imports. The three verifier/helper files are deliberately deferred from minimal fixture work.

## External/environment boundary

Ordinary imports observed outside repository modules were Python standard-library modules. No missing installed third-party package was observed. The smoke used Python 3.13.5, whereas historical CI evidence in the earlier packet used Python 3.12.14; no numerical regression parity across those environments is claimed. All deeper source/package requirements remain unknown until their source is inspected. The current actual blocker is a missing repository file, not an invented package installation requirement.

## Preserved amplitude and ordered-span boundaries

The retained v7 `_dominance_certificate` supplies a rational coefficient-bound strict nonzero sign and its `SEPARATED_BY_EXACT_RATIONAL_AMPLITUDE_DOMINANCE` witness relation; the producer's separate route_kind is `EXACT_RATIONAL_AMPLITUDE_DOMINANCE`. This is not a derivative certificate. Its original-source binding and full finite checking would still need explicit review before any adapter is accepted.

The v53 strict/product view interface, v50 strict-owner checking, v51 complete direction extraction and v52 physical knot continuity are retained unchanged. V52's actual runtime discontinuity token remains `PHYSICAL_SOURCE_KNOT_DISCONTINUITY`. No predicate was changed to match a historical expectation. The comment's `97/200` margin and historical v54 adapter/inventory/test counts remain unverified claims in R1.

## Readiness decision

More specifically named recovery is required: begin with the observed algebraic-endpoint model gap and the statically named endpoint certificate, inspecting their imports before expanding. Do not begin canonical owner enumeration from this incomplete source closure. Neither recovered imports nor an eventual import PASS alone establishes that the reversed residual ran or that v54 is accepted.
'''
(R/'SOURCE_DEPENDENCY_MAP.md').write_text(text)

findings={
 'status':'PARTIAL','readiness':'MORE_NAMED_SOURCE_RECOVERY_NEEDED','source_batch_complete':True,
 'new_source_file_count':10,'cumulative_source_entries':18,'cumulative_main_files':16,
 'cumulative_python_files':14,'ordinary_import_sites':119,'dynamic_source_loads':1,
 'visible_missing_module_references':15,'visible_missing_references_are_complete_closure':False,
 'fixture_import':'FAILED','actual_missing_module':smoke['missing_module'],
 'smoke_returncode':run['returncode'],'smoke_timed_out':run['timed_out'],
 'factory_called':False,'residual_case_run':False,'new_owner_result':None,'new_margin_result':None,
 'canonical_owner_inventory_created':False,'v54_implementation_recovered':False,'full_git_tree_verified':False,
 'remote_writes':0,'native_shared_resources_used':False,'full_verifier_run':False,
 'next_immediate_files':['research/machining-completeness/tasks/MC-038/pb00701_algebraic_endpoint_model.py',
                         'research/machining-completeness/tasks/MC-038/pb00701_algebraic_endpoint_certificate.py'],
 'readiness_rationale':'Batch cap reached with authoritative bytes gained, but normal fixture-module import fails; deeper fixed classifier source also absent.',
 'recorded_at':now}
(R/'records/readiness.json').write_text(json.dumps(findings,indent=2)+'\n')
(R/'FINDINGS.md').write_text('''# Findings — 2A-R1

## Observed source and process facts

The prior packet passed fresh independent verification; the eight inherited source exports matched again. Live main and both v54-prefix refs are unchanged. The issue body/metadata does not identify newer published work. Ten actual repository files were recovered at the same immutable main commit, with full Git blob matches and separate SHA-256 values. The original three-file fixture chain is present. No v54 implementation was recovered from the historical staging payload.

A dynamic MC-032/event_engine.py load was found in the actual child-map module and recovered. All fourteen retained Python files were inspected statically for ordinary and direct file-path imports. The one normal fixture-module import failed on the missing algebraic-endpoint model. The source factory and residual never ran. Eighteen source entries remained unchanged after the smoke.

## Reported claims retained, not newly verified

The contradictory historical v54 inventories, adapter counts, broad-test claims, reversed-source margin 97/200 and alleged stale v54 test expectation remain in the prior claims ledger. No accepted v54 bytes or run evidence was recovered to resolve them. The older v53 accepted residual assertion is real source text, but not a new R1 measurement. Older v53 acceptance is preserved, not rerun.

## Interpretation and readiness

The required immediate next recovery target is the module named by the actual import error. The endpoint certificate is a second statically proven import-time dependency. A further missing fixed-predecessor classifier means these two files alone cannot be promised to enable the residual. Recovering exact original source is still the appropriate next phase; starting owner enumeration or adapter review now would substitute missing source with assumptions.

The growth from eight initial missing direct imports to fifteen visible missing references is exposure of more source edges, not a regression or a proof-owner count. No complete transitive graph has been established. Code retrieval/hash checks are process evidence, not mathematical or native acceptance.

## Unknowns and access limits

Imports inside missing modules, complete classifier reachability, the first actual reversed-case output in this workspace, and exact future source-closure size remain unknown. No external package dependency has been observed in the inspected bytes, but deeper environment requirements remain unknown. Current shell raw-file transport failed DNS once; authenticated connector file reads worked. No old artifact recovery was retried.

## Non-promotions

PB-007-01 globally OPEN; v54 acceptance not established; MC-B/MC-1 NOT_ESTABLISHED. All 26 operations, original-source identities, owner provenance and refusal meanings preserved. Whole-span nonzero sign is not monotonicity. No remote publication, source edits, owner enumeration, adapter implementation, full predecessor verifier, successor task or native/shared-resource test occurred.
''')

(R/'README.md').write_text('''# radiCADSAC 2A-R1 recovery packet

Start with **CHECKPOINT.md**. Status is PARTIAL; the ten-file increment is recovered but the exact fixture cannot yet import.

`prior/2A/` preserves the verified preceding 53-file packet unchanged, including its original source/reading manifest and acceptance/claims evidence. `source/` is the cumulative usable partial export; `source/main/` preserves repository-relative layout, including the actual MC-032 path-loaded engine. `source/forensic/` and `source/recovery/` are historical workflow scaffolds only. Do not enable or dispatch them.

Current records are `records/source-manifest.json`, `records/authority-refresh.json`, `records/dependency-map.json`, `records/residual-recovery-queue.json` and `records/readiness.json`. Human navigation is SOURCE_MANIFEST.md, SOURCE_DEPENDENCY_MAP.md, AUTHORITY_LEDGER.md, FINDINGS.md and COMMANDS_RESULTS.md.

To verify a freshly extracted packet without importing repository code:

```sh
python3 -I -B tools/verify_packet.py .
```

The archive verification JSON supplied alongside the ZIP separately binds its SHA-256 and member checks. Successful package verification means only that the exported bytes are intact. This is not a full Git checkout, complete predecessor closure, proof result or v54 acceptance.

The smoke runner is retained for reproducibility, but its recorded R1 execution was once only and failed; do not assume a later run has already happened. No successor prompt is included.
''')
print('CHECKPOINT and substantive reports saved:',now)
