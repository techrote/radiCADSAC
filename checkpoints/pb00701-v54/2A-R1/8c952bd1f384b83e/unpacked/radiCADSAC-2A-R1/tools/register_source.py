#!/usr/bin/env python3
"""Check persisted connector text against its immutable Git blob before retaining it."""
from pathlib import Path
import argparse, ast, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('blob');p.add_argument('evidence');a=p.parse_args()
repo_path=a.name if a.name.startswith('research/') else 'research/machining-completeness/tasks/MC-038/'+a.name
assert '..' not in Path(repo_path).parts and not Path(repo_path).is_absolute()
local='source/main/'+repo_path
data=(ROOT/local).read_bytes()
actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
assert actual==a.blob,(a.name,actual,a.blob)
manifest_path=ROOT/'records/source-manifest.json';rows=json.loads(manifest_path.read_text())
assert local not in [r['local_path'] for r in rows], 'duplicate recovery'
rows.append({'local_path':local,'repository_path':repo_path,'commit':'9734776b3cef3d7039be9623e8872df2c2a85174','git_blob':actual,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'lines':len(data.splitlines()),'verification':'LOCAL_GIT_BLOB_MATCH','batch':'2A-R1_NEW','evidence':a.evidence,'method':'Authenticated GitHub.fetch_file at immutable ref; complete UTF-8 tool text persisted; Git blob SHA-1 checked; SHA-256 computed independently'})
assert sum(r['batch']=='2A-R1_NEW' for r in rows)<=10
manifest_path.write_text(json.dumps(rows,indent=2)+'\n')
tree=ast.parse(data); imports=[{'line':n.lineno,'module':n.module if isinstance(n,ast.ImportFrom) else x.name} for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom)) for x in (n.names if isinstance(n,ast.Import) else [None])]
print(json.dumps({'name':a.name,'blob_match':True,'new_file_count':sum(r['batch']=='2A-R1_NEW' for r in rows),'imports':imports},indent=2))
