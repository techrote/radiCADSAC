#!/usr/bin/env python3
"""Verify an extracted chunk packet's exact file set and SHA-256 contents.
This does not verify repository completeness or any mathematical certificate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re


def verify(root: Path) -> dict:
    root = root.resolve(strict=True)
    manifest = root / 'SHA256SUMS'
    expected = {}
    for number, line in enumerate(manifest.read_text(encoding='utf-8').splitlines(), 1):
        digest, sep, name = line.partition('  ')
        path = Path(name)
        if not sep or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise ValueError(f'Malformed SHA256SUMS line {number}')
        if not name or path.is_absolute() or '..' in path.parts or name == 'SHA256SUMS':
            raise ValueError(f'Unsafe/self-referential path on line {number}')
        if name in expected:
            raise ValueError(f'Duplicate manifest entry: {name}')
        expected[name] = digest
    actual = set()
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError(f'Symlink not permitted: {path}')
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
    required = set(expected) | {'SHA256SUMS'}
    if actual != required:
        raise ValueError(f'File-set mismatch: missing={sorted(required-actual)}, extra={sorted(actual-required)}')
    for name, digest in expected.items():
        measured = hashlib.sha256((root/name).read_bytes()).hexdigest()
        if measured != digest:
            raise ValueError(f'SHA-256 mismatch: {name}')
    return {'status':'PASS','manifest_entries':len(expected),'total_files':len(actual),
            'exact_file_set':True,'all_contents_readable':True,'all_sha256_match':True,
            'full_git_tree_or_proof_acceptance_implied':False}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path,nargs='?',default=Path.cwd())
    args=parser.parse_args()
    print(json.dumps(verify(args.root),indent=2))

if __name__=='__main__':
    main()
