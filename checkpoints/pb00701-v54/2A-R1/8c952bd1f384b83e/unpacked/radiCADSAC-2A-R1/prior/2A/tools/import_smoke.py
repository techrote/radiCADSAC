#!/usr/bin/env python3
"""One import-only smoke: no contract(), self_test(), or predecessor execution."""
from pathlib import Path
import importlib.util
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'source/main/research/machining-completeness/tasks/MC-038/verify_pb00701_v53.py'
before=set(sys.modules)
spec=importlib.util.spec_from_file_location('chunk2a_v53_import_only',path)
if spec is None or spec.loader is None:
    raise RuntimeError('Cannot create import specification')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
after=set(sys.modules)-before
assert not any(name.startswith(('pb00701_', 'test_pb00701_', 'verify_pb00701_')) for name in after)
assert module.BASE=='7126dabf013ef95b0965b74008466e12f0650ef8'
assert module.PINS['pb00701_piecewise_product_model.py']=='6ca7a321bd027f3ed2a22059e9aa856c76485f8a'
print(json.dumps({'status':'PASS','scope':'IMPORT_ONLY_V53_VERIFIER',
 'contract_called':False,'self_test_called':False,'predecessor_modules_imported':False,
 'reversed_source_replayed':False,'owner_inventory_verified':False,'v54_accepted':False},indent=2))
