#!/usr/bin/env python3
"""Verify exported bytes against Git blob identities, without requiring a Git tree."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()

def main() -> int:
    rows = json.loads((ROOT / 'records/exported-blobs.json').read_text())
    results = []
    for row in rows:
        rel = Path(row['local_path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError(f'Unsafe manifest path: {rel}')
        data = (ROOT / rel).read_bytes()
        actual = blob_sha(data)
        results.append({'path': rel.as_posix(), 'bytes': len(data),
                        'expected_git_blob': row['git_blob'], 'actual_git_blob': actual,
                        'sha256': hashlib.sha256(data).hexdigest(), 'match': actual == row['git_blob']})
    out = {'scope': 'individual fetched blobs only; NOT a complete Git tree', 'results': results,
           'all_match': all(r['match'] for r in results)}
    print(json.dumps(out, indent=2))
    return 0 if out['all_match'] else 1

if __name__ == '__main__':
    sys.exit(main())
