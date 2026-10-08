#!/usr/bin/env python3
"""Write normalized observations from read-only GitHub reads in chunk 2A.
These are curated records, not raw API responses or a complete Git export.
"""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
MAIN='9734776b3cef3d7039be9623e8872df2c2a85174'
IMPL='a13702b28fcc349442e78cfb1e971eb94991a69e'
FORENSIC='8cec4953dc898e70270c654f5453b108bb80d47b'
RECOVERY='823a8624739c337aeb41470cfebebd2ea2a931ca'
REPO='https://github.com/techrote/radiCADSAC'
API='https://api.github.com/repos/techrote/radiCADSAC'
T='research/machining-completeness/tasks/MC-038/'
def write(name,obj): (ROOT/name).write_text(json.dumps(obj,indent=2)+'\n')
refs=[
 {'name':'main','commit':MAIN,'tree':'b0240e4d02a6165f8799d7af432ea36416009667','parents':[IMPL],
  'evidence':'LIVE_COMMIT_AND_BRANCH_API','acceptance':'v53 accepted; current main is documentation reconciliation; not v54 acceptance'},
 {'name':'v53 implementation landing / PR 273','commit':IMPL,'tree':'17fe7642600b12edd573e21b57933e5811cea991','parents':['7126dabf013ef95b0965b74008466e12f0650ef8'],
  'evidence':'LIVE_COMMIT_API_PLUS_ACCEPTANCE_LEDGER','acceptance':'ACCEPTED_BOUNDED_V53'},
 {'name':'mc038/pb00701-v54-recovery','commit':RECOVERY,'tree':'99f93a6c2dcc5e60965ceefc9a5e9ec25409f4bd','parents':[MAIN],
  'evidence':'LIVE_COMMIT_BRANCH_COMPARE_APIS','acceptance':'NO_V54_ACCEPTANCE; only recovery workflow added'},
 {'name':'mc038/pb00701-v54-finite-owner-coverage','commit':FORENSIC,'tree':'6afc28d6b83f5c631b63c67d3e9b1ad93188e6a2','parents':['acc79884eb872344b2544f00e0cac0140f79fecd'],
  'evidence':'LIVE_COMMIT_BRANCH_COMPARE_APIS','acceptance':'UNACCEPTED_FORENSIC_STAGING; six chunks and baseline workflow only'}]
for r in refs:r['source_url']=API+'/git/commits/'+r['commit']
write('records/authority-ledger.json',{'repository':'techrote/radiCADSAC','observed_date_utc':'2026-10-04','mutable_ref_observation':'Branches read once near start; no continuous polling or final ref lock',
 'status':'PARTIAL','refs':refs,'full_git_tree_exported':False,'commit_objects_locally_rehashed':False,
 'local_blob_hashes':'exported-blobs.json','staging_subtree_metadata_hash':'staging-tree.json',
 'programme':{'operation_denominator':26,'PB-007-01':'OPEN','MC-B':'NOT_ESTABLISHED','MC-1':'NOT_ESTABLISHED','v54_acceptance':False},
 'authority_order':['Current user 2A read-only/bounded execution contract','AGENTS/current-authority/DR-0026/current execution protocol','Issue 275 scoped task body; comments are evidence claims, not acceptance','Accepted v53 source bytes, #271/#100 ledger and independent CI metadata','Current-state navigation records; historical roadmap/report text remains scoped history'],
 'source_date_not_github_signature_validation':'Commit/tree fields were inspected via connector. Signature verified flags reported by GitHub were not independently cryptographically validated.'})
comparisons=[
 {'base':MAIN,'head':RECOVERY,'ahead':1,'behind':0,'files':[{'path':'.github/workflows/mc1-pb00701-v54-recovery-bootstrap.yml','status':'added'}]},
 {'base':MAIN,'head':FORENSIC,'ahead':7,'behind':0,'files':[{'path':'.github/workflows/mc1-pb00701-v54.yml','status':'added'}]+[{'path':f'.v54-bootstrap/part{i:02}','status':'added'} for i in range(6)]},
 {'base':IMPL,'head':MAIN,'ahead':1,'behind':0,'files':[{'path':'docs/machining-completeness/77-MC038-CURRENT-IMPLEMENTATION-STATE.md','status':'modified'},{'path':T+'current-implementation-state-v1.json','status':'modified'}]}]
for x in comparisons:x['source_url']=API+'/compare/'+x['base']+'...'+x['head'];x['complete_changed_file_list_returned']=True
write('records/branch-comparisons.json',comparisons)
prs=[{'pr':273,'merged':True,'head':'e4d5646fd3b16e0f152c70fd817904df74426a8b','merge':IMPL,'base':'7126dabf013ef95b0965b74008466e12f0650ef8','changed_files':9},
 {'pr':274,'merged':True,'head':'eb7b94500a3fc216a1834566364add8e6093aa5e','merge':MAIN,'base':IMPL,'changed_files':2}]
write('records/pr-evidence.json',{'prs':prs,'named_v54_branch_pr_queries':[{'branch':n,'state':'all','result':[]} for n in ['mc038/pb00701-v54-recovery','mc038/pb00701-v54-finite-owner-coverage']],
 'limit':'Branch-specific absence only. Global issue search with is:pr returned a plain issue and was not used as negative proof.'})
checks=[
 {'run':37041568030,'job':110952689911,'head':IMPL,'name':'verify','conclusion':'success','class':'LIVE_CHECK_RUN_METADATA'},
 {'run':37041567973,'job':110952689742,'head':IMPL,'name':'validate','conclusion':'success','class':'LIVE_CHECK_RUN_METADATA'},
 {'run':37048808608,'job':110976772764,'head':MAIN,'name':'validate','conclusion':'success','class':'LIVE_CHECK_RUN_METADATA'},
 {'run':37050900358,'job':110983746740,'head':'528e55f3260222e96c12a9f1bc473ab673fc3403','name':'baseline','conclusion':'success','class':'LIVE_JOB_METADATA','checkout_in_workflow':MAIN,'artifacts_now':0,'retention_days':1},
 {'run':37107690114,'job':111159336398,'head':RECOVERY,'name':'recover','conclusion':'failure','class':'LIVE_JOB_METADATA_AND_FULL_DECODED_LOG_READ','failure':'gzip: stdin: unexpected end of file','upload':'skipped'},
 {'run':37040746459,'head':'e4d5646fd3b16e0f152c70fd817904df74426a8b','name':'v53 final-head focused','conclusion':'PASS','class':'ACCEPTANCE_LEDGER_REPORTED_NOT_INDEPENDENTLY_REQUERIED'},
 {'run':37040746380,'name':'v53 final-head static via merge ref','conclusion':'PASS','class':'ACCEPTANCE_LEDGER_REPORTED_NOT_INDEPENDENTLY_REQUERIED'},
 {'run':37048706057,'head':'eb7b94500a3fc216a1834566364add8e6093aa5e','name':'reconciliation PR static','conclusion':'PASS','class':'ACCEPTANCE_LEDGER_REPORTED_NOT_INDEPENDENTLY_REQUERIED'}]
for c in checks:c['url']=REPO+'/actions/runs/'+str(c['run'])
write('records/evidence-runs.json',checks)
claims=[
 (5962246401,'2026-10-02T22:08:29Z','43 route cases; 41 final identifiers; 5 supported / 20 adapters / 15 missing-premise / 1 blocker, plus two literal emitters','Claims local completion, 21 tests and full v53 passed','UNVERIFIED_UNPUBLISHED; incompatible with later progress accounting'),
 (5964187550,'2026-10-03T01:39:00Z','14 families unresolved','Conservative continuation says work incomplete, no v54 acceptance','REPORTED_CLAIM; incomplete publication confirmed by live branch comparisons'),
 (5964233252,'2026-10-03T01:45:14Z','No canonical count established','Claims clean recovery branch and locally tree-verified baseline archive','Branch existence verified; former local archive verification not reproduced'),
 (5966598172,'2026-10-03T07:04:34Z','43 rows: 5 supported / 30 proposed adapters / 6 missing-premise / 2 blockers','Amplitude and 28 more adapters reportedly replayed; test expectation mismatch; no implementation published','Counts/replay unverified. Runtime refusal string confirmed in v52 source, alleged v54 test not recovered'),
 (5968122740,'2026-10-03T10:10:22Z','Earlier 43-row figure remains working state only','Recovery workflow failed on truncated six-part gzip stream; no PR or acceptance','Workflow/head/failure verified; no stronger impossibility-of-salvage conclusion')]
write('records/issue275-claims.json',[{'comment_id':i,'created_at':d,'count_claim':c,'progress_claim':p,'disposition':s,'url':REPO+'/issues/275#issuecomment-'+str(i)} for i,d,c,p,s in claims])
write('records/issues-and-acceptance.json',{
 '275':{'state':'open','comment_count':5,'body_read':'complete','all_comment_bodies_read':True,'url':REPO+'/issues/275'},
 '271':{'state':'closed','state_reason':'completed','comment_count':5,'body_read':'complete','all_comment_bodies_read':True,'acceptance_comment':5958928408,'url':REPO+'/issues/271#issuecomment-5958928408'},
 '100':{'state':'open','comment_count':67,'body_read':'complete','comments_read':[5958929084],'other_66_comments_not_read':True,'url':REPO+'/issues/100#issuecomment-5958929084'},
 'record_kind':'Normalized observations and citations; not verbatim API response archival'})
files=[
 ('AGENTS.md','d7a3a2d9277d03306704227e9db9399beef042b6','complete','research protocol'),
 ('handoffs/current-authority.json','fa0233323a0804d8a5d3eb7cd892a274a6173fab','complete','current programme selector'),
 ('docs/decisions/DR-0026-machining-completeness-programme.md','81a701d78c1858140464f9e8d90aaa0f1776dd88','complete','current accepted programme decision'),
 ('docs/machining-completeness/00-PROGRAMME.md','c44578620beba129ef809891e39919d51acff0ea','complete','programme authority'),
 ('docs/machining-completeness/07-EXECUTION-PROTOCOL.md','9e79ce30e7e57138e4a594e19df73b9935b391b4','complete','execution authority; remote-write clauses deferred this turn'),
 ('docs/machining-completeness/12-ROADMAP.md','bcbfca9c1b58db3d33197a21d38a885e49291e6d','complete across initial read and overlapping lines 60-EOF','stale v52 frontier; routing context retained'),
 ('docs/machining-completeness/77-MC038-CURRENT-IMPLEMENTATION-STATE.md','4fc3710483c66cc3b90c7f99626865eb9e196bf5','complete','accepted v53 navigation ledger'),
 ('docs/machining-completeness/78-PB00701-MIXED-OWNER-SPANS.md','34c07ab80b918639eb57e58cf07f8991170a95de','complete','ordered-span contract'),
 (T+'current-implementation-state-v1.json','9f0bc8402a4d06cbe850338cef3ca9dde3297d58','complete','machine current-state ledger'),
 (T+'report.md','5ee4e085f922f6c1bf39fa493af0d3aae130de1e','complete','historical gate review; stale v52 navigation note'),
 (T+'outcome.json','2b821f6c14e1ba36c8121aab9b13e13b21b81f9f','complete','historical BLOCKED MC-B outcome'),
 (T+'pb00701_mixed_owner_span_model.py','0d7b334accaec307ef2016a1bec2fa22cb115920','complete, ranges 1-240 and 241-EOF','v53 constructor and fixed predecessor wrapper'),
 (T+'pb00701_mixed_owner_span_certificate.py','91bfc606539d05f054a86ee381af59926502c167','complete','finite full-source checker'),
 (T+'verify_pb00701_v53.py','7995627b8ff784c17947b2db746a588b5ed18d7b','complete','verifier and inherited pins; import-only smoke'),
 (T+'pb00701-report-v53.md','0ad24327f9839d8ade12a6fa98ab2238438d9a08','complete','accepted bounded result report'),
 (T+'pb00701-mixed-owner-spans-v53.json','006ceb86365616462de3b77689950e9b849d349d','complete','v53 contract/boundary and pins'),
 (T+'pb00701_piecewise_product_model.py','6ca7a321bd027f3ed2a22059e9aa856c76485f8a','partial: 1-170, 235-EOF; 171-234 not read','v52 lowering/continuity/wrapper; middle assembly not reread'),
 (T+'pb00701_ordered_product_model.py','d36c5f5ce3b12840273d8483c467ff41a6e9ae01','partial: 1-100','v51 product owner and direction-extraction entry'),
 (T+'pb00701_vanishing_source_factor_model.py','dfd554bf9ee41c96f9009f8ed8ceae485e134a5d','partial: 1-100, 105-235','v50 supported strict owners and finite routing'),
 (T+'pb00701_coupled_bspline_model.py','a086b625e1a6dea8bd202699d161167bb69cc9e7','complete across full response prefix and overlapping 345-EOF; persisted exact blob proves complete bytes','v7 source lowerer and original amplitude route'),
 (T+'test_pb00701_mixed_owner_span.py','f25e76dab22e47b6573a4c2fd8c1170677c887fb','partial: 1-100','fixture imports and no-search guard'),
 (T+'test_pb00701_mixed_owner_span_integration.py','050e6b2110d9d706a9cf96006b79e069adb7beac','partial: 1-170, 205-310','candidate and explicit reversed residual assertions')]
exports=json.loads((ROOT/'records/exported-blobs.json').read_text()); bypath={r['repository_path']:r for r in exports if r['commit']==MAIN}
source=[]
for path,sha,coverage,purpose in files:
 source.append({'path':path,'commit':MAIN,'git_blob':sha,'reading_coverage':coverage,'purpose':purpose,
  'url':REPO+'/blob/'+MAIN+'/'+path,'exported_complete_bytes':path in bypath,
  'local_path':bypath.get(path,{}).get('local_path'),
  'identity_verification':'LOCAL_GIT_BLOB_MATCH' if path in bypath else 'CONNECTOR_REPORTED_FULL_FILE_BLOB; local full bytes not retained'})
write('records/source-reading-manifest.json',source)
with (ROOT/'records/source-reading-manifest.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=source[0].keys());w.writeheader();w.writerows(source)
write('records/coverage-and-limitations.json',{
 'main_source_files_listed':len(source),'all_source_files_in_repository_read':False,
 'main_MC038_tree':'73794bae7f7c2face00cdfb389410e405ccf4625','MC038_listing':'tool output truncated; not fully exported/read; not used as a complete-tree absence proof',
 'staging_tree_metadata':'complete six entries; independently reconstructed tree-object hash only',
 'full_snapshot_available_locally':False,'complete_runtime_dependency_closure':False,'git_history_available':False,
 'foundation_documents_listed_in_AGENTS_but_not_reread':['docs/00-FOUNDING-BRIEF.md','docs/01-MSAC-GEOMETRY-CONTRACT.md','docs/04-REVISED-RESEARCH-ROADMAP.md','docs/06-RESEARCH-METHOD.md','docs/08-TERMINOLOGY.md','docs/09-FOUNDATION-AUDIT.md','historical Genesis handoff/evidence trees'],
 'other_not_read':['Every historical owner emitter/proof/checker before v19/v47/v48/v49','Complete v52/v51/v50 bodies and transitive imports','Full v53 direct/integration suites','Old v54 decompressed payload or any recovered adapter implementation','Full logs of accepted v53 focused/static checks (metadata and acceptance records read)'],
 'no_execution':['No complete predecessor verifier','No v54 verifier','No reversed-source execution','No domain owner enumeration/classification','No adapter implementation or review acceptance','No native/GPU/USB/shared resources'],
 'transport_limits':['Direct shell GitHub DNS failure','GitHub code search returned no result for known existing source; not an absence proof','Generic job-log URL rejected; dedicated decoded-log tool worked','Generic single-artifact metadata URL rejected; allowed run artifact listings worked and both were empty','Connector timeout knobs unavailable; calls were individually bounded by finite batch count rather than CI polling'],
 'scope_status':'PARTIAL; explicit read coverage retained rather than claiming all inherited AGENTS historical reading complete'})
print('Wrote normalized authority, comparison, issue-claim, CI and source-reading records.')
