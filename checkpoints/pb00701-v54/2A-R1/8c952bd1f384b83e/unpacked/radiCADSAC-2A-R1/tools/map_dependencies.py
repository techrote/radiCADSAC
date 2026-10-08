#!/usr/bin/env python3
"""Static recovery frontier only. Does not enumerate proof owners or run source."""
import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source/main'
manifest = json.loads((ROOT / 'records/source-manifest.json').read_text())
files = [r for r in manifest if r['local_path'].startswith('source/main/') and r['repository_path'].endswith('.py')]
by_module = {Path(r['repository_path']).stem: r for r in files}
rows, dynamic, dynamic_unresolved, symbols = [], [], [], []

for record in files:
    path = ROOT / record['local_path']
    text = path.read_text()
    tree = ast.parse(text, filename=record['repository_path'])
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    module = path.stem
    for node in ast.walk(tree):
        cursor = node
        scopes = []
        while cursor in parents:
            cursor = parents[cursor]
            if isinstance(cursor, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                scopes.append(getattr(cursor, 'name', '<lambda>'))
        phase = 'FUNCTION_SCOPED_DEFERRED' if scopes else 'MODULE_EXECUTION'
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append({'repository_path': record['repository_path'], 'name': node.name,
                            'start_line': node.lineno, 'end_line': node.end_lineno})
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [x.name for x in node.names] if isinstance(node, ast.Import) else [node.module or '']
            for name in names:
                root_name = name.split('.')[0]
                local = name.startswith(('pb00701_', 'test_pb00701_', 'verify_pb00701_'))
                target = by_module.get(name)
                classification = ('RECOVERED_REPOSITORY_FILE' if target else 'MISSING_REPOSITORY_SOURCE') if local else (
                    'PYTHON_STANDARD_LIBRARY' if root_name in sys.stdlib_module_names else 'EXTERNAL_OR_UNRESOLVED')
                rows.append({'from_module': module, 'repository_path': record['repository_path'],
                             'line': node.lineno, 'imported_module': name, 'phase': phase,
                             'function_scopes': list(reversed(scopes)), 'classification': classification,
                             'target_repository_path': (target['repository_path'] if target else
                                 'research/machining-completeness/tasks/MC-038/' + name + '.py') if local else None})
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'spec_from_file_location':
            expression = ast.get_source_segment(text, node.args[1]) if len(node.args) > 1 else None
            edge = {'from_module': module, 'repository_path': record['repository_path'], 'line': node.lineno,
                    'phase': phase, 'path_expression': expression}
            if module == 'pb00701_algebraic_child_map_model' and expression == 'HERE.parent / "MC-032" / "event_engine.py"':
                target = 'research/machining-completeness/tasks/MC-032/event_engine.py'
                edge.update({'target_repository_path': target, 'imported_module': 'event_engine',
                             'classification': 'RECOVERED_REPOSITORY_FILE' if (SOURCE/target).is_file() else 'MISSING_REPOSITORY_SOURCE',
                             'resolution': 'Literal relative-path expression manually confirmed; not an external package.'})
                dynamic.append(edge)
            else:
                edge['classification'] = 'DYNAMIC_PATH_UNRESOLVED'
                dynamic_unresolved.append(edge)

start = 'test_pb00701_mixed_owner_span_integration'
seen, pending, missing_top = set(), [start], set()
while pending:
    name = pending.pop(0)
    if name in seen:
        continue
    seen.add(name)
    for edge in rows + dynamic:
        if edge['from_module'] != name or edge['phase'] != 'MODULE_EXECUTION':
            continue
        if edge['classification'] == 'RECOVERED_REPOSITORY_FILE':
            pending.append(edge['imported_module'])
        elif edge['classification'] == 'MISSING_REPOSITORY_SOURCE':
            missing_top.add(edge['imported_module'])

queue = []
for name in sorted({r['imported_module'] for r in rows if r['classification']=='MISSING_REPOSITORY_SOURCE'}):
    refs = [r for r in rows if r['imported_module']==name and r['classification']=='MISSING_REPOSITORY_SOURCE']
    if name in missing_top:
        priority = 'IMPORT_TIME_FIXTURE_FRONTIER'
    elif name.startswith(('test_', 'verify_')):
        priority = 'DEFERRED_OTHER_TEST_OR_FULL_VERIFIER'
    else:
        priority = 'SOURCE_OR_PROOF_RUNTIME_FRONTIER'
    queue.append({'module': name, 'repository_path': refs[0]['target_repository_path'],
                  'priority': priority, 'observed_import_sites': refs,
                  'file_bytes_recovered': False, 'own_imports_known': False,
                  'reachability_limit': 'Literal import reference only; actual branch use and deeper dependencies not established.'})
report = {'scope': 'Static import inspection of retained complete Python files only; not owner enumeration.',
          'python_files_inspected': len(files), 'ordinary_import_sites': len(rows),
          'fixture_entry_module': start, 'known_recovered_import_time_modules': sorted(seen),
          'fixture_import_time_missing_modules': sorted(missing_top),
          'ordinary_imports': sorted(rows,key=lambda r:(r['repository_path'],r['line'],r['imported_module'])),
          'dynamic_source_loads': dynamic, 'unresolved_dynamic_source_loads': dynamic_unresolved,
          'third_party_imports_observed': [r for r in rows if r['classification']=='EXTERNAL_OR_UNRESOLVED'],
          'source_dependency_closure_complete': False, 'complete_git_tree': False,
          'caveat': 'Function-scoped imports may be used later. Transitive imports within unavailable files are unknown. Counts are source nodes/sites, not proof owners.'}
(ROOT/'records/dependency-map.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'records/residual-recovery-queue.json').write_text(json.dumps(queue,indent=2)+'\n')
(ROOT/'records/source-symbol-locations.json').write_text(json.dumps(symbols,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('python_files_inspected','ordinary_import_sites','fixture_import_time_missing_modules','third_party_imports_observed','unresolved_dynamic_source_loads')},indent=2))
print('Residual source references:',len(queue))
for row in queue:
    print(row['priority'], row['module'])
