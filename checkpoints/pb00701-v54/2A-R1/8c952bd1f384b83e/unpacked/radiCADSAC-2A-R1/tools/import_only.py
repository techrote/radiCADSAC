#!/usr/bin/env python3
"""One ordinary fixture-module import; do not call its factory, tests or proofs."""
import importlib
import json
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source/main'
TASK = SOURCE / 'research/machining-completeness/tasks/MC-038'
sys.path.insert(0, str(TASK))
report = {'check': 'IMPORT_ONLY', 'module': 'test_pb00701_mixed_owner_span_integration',
          'factory_called': False, 'residual_case_run': False, 'full_verifier_run': False,
          'python_version': sys.version, 'bytecode_write_enabled': not sys.dont_write_bytecode,
          'isolated_mode': bool(sys.flags.isolated), 'source_search_path': str(TASK)}
code = 0
try:
    target = importlib.import_module(report['module'])
    report.update(status='PASS', module_path=str(Path(target.__file__).relative_to(SOURCE)),
                  candidate_factory_present=callable(getattr(target, 'candidate', None)))
except Exception as exc:
    code = 1
    report.update(status='IMPORT_FAILED', exception_type=type(exc).__name__,
                  exception_message=str(exc), missing_module=getattr(exc, 'name', None),
                  traceback=traceback.format_exc())
    traceback.print_exc()
loaded = []
for name, module in sorted(sys.modules.items()):
    location = getattr(module, '__file__', None)
    if location:
        try:
            rel = Path(location).resolve().relative_to(SOURCE)
        except ValueError:
            continue
        loaded.append({'module':name, 'repository_path':rel.as_posix()})
report['successfully_loaded_source_modules_remaining_in_sys_modules'] = loaded
print(json.dumps(report, indent=2))
raise SystemExit(code)
