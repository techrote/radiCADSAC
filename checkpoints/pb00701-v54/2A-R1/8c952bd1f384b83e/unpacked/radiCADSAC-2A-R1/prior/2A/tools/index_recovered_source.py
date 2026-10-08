#!/usr/bin/env python3
"""Static source indexing only; no imports or owner classification are executed."""
from pathlib import Path
import ast
import json

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'source/main/research/machining-completeness/tasks/MC-038'
rows=[]; missing={}
for path in sorted(BASE.glob('*.py')):
    tree=ast.parse(path.read_text(),filename=str(path))
    imports=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            imports += [{'module':a.name,'line':node.lineno} for a in node.names]
        elif isinstance(node,ast.ImportFrom) and node.module:
            imports.append({'module':node.module,'line':node.lineno})
    functions=[{'name':n.name,'start_line':n.lineno,'end_line':n.end_lineno} for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
    rows.append({'path':path.relative_to(ROOT).as_posix(),'functions_and_classes':functions,'imports_at_any_scope':imports})
    for item in imports:
        name=item['module']
        if name.startswith(('pb00701_', 'test_pb00701_', 'verify_pb00701_')) and not (BASE/(name+'.py')).is_file():
            missing.setdefault(name+'.py',[]).append({'from':path.name,'line':item['line']})
(ROOT/'findings/source-symbol-index.json').write_text(json.dumps(rows,indent=2)+'\n')
(ROOT/'findings/local-import-frontier.json').write_text(json.dumps({
 'scope':'Direct imports appearing in the four retained Python files only; not the complete dependency closure',
 'repository_code_executed':False,'files':missing,'transitive_closure_complete':False},indent=2)+'\n')
print(json.dumps({'syntax_parsed_files':len(rows),'missing_direct_import_files':list(missing),'scope':'static parsing, no theorem tests'},indent=2))
