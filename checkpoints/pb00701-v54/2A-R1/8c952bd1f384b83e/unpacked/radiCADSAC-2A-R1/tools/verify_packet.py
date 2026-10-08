#!/usr/bin/env python3
"""Verify a complete packet file set and original Git blobs; never import source."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify(root: Path) -> dict:
    root = root.resolve()
    manifest = root / 'SHA256SUMS'
    expected = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        value, name = line.split('  ', 1)
        rel = PurePosixPath(name)
        if len(value) != 64 or rel.is_absolute() or '..' in rel.parts or name in expected:
            raise ValueError('Unsafe or duplicate manifest entry: ' + name)
        int(value, 16)
        expected[name] = value
    actual = set()
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('Symlinks not permitted: ' + str(path))
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
    if actual != set(expected) | {'SHA256SUMS'}:
        raise ValueError('File-set mismatch: ' + repr(actual ^ (set(expected) | {'SHA256SUMS'})))
    for name, value in expected.items():
        if digest((root / name).read_bytes()) != value:
            raise ValueError('SHA256 mismatch: ' + name)
    sources = json.loads((root/'records/source-manifest.json').read_text())
    seen = set()
    for row in sources:
        name = row['local_path']
        if name in seen or name not in expected:
            raise ValueError('Source entry missing or duplicate: ' + name)
        seen.add(name)
        raw = (root/name).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()
        if blob != row['git_blob'] or digest(raw) != row['sha256'] or len(raw) != row['bytes']:
            raise ValueError('Original source identity mismatch: ' + name)
    # Recheck the original nested packet without requiring its removed outer prefix.
    prior = root/'prior/2A'
    old_expected = {}
    for line in (prior/'SHA256SUMS').read_text().splitlines():
        value, name = line.split('  ', 1)
        if digest((prior/name).read_bytes()) != value:
            raise ValueError('Prior packet changed: ' + name)
        old_expected[name] = value
    old_actual = {p.relative_to(prior).as_posix() for p in prior.rglob('*') if p.is_file()}
    if old_actual != set(old_expected) | {'SHA256SUMS'}:
        raise ValueError('Prior packet set changed')
    return {'status':'PASS','packet_files':len(actual),'manifest_entries':len(expected),
            'original_source_entries_verified':len(sources),
            'new_source_entries':sum(r['batch']=='2A-R1_NEW' for r in sources),
            'prior_files':len(old_actual), 'prior_manifest_entries':len(old_expected),
            'complete_git_tree':False,'proof_or_acceptance_verified':False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args()
    print(json.dumps(verify(args.root),indent=2))


if __name__ == '__main__':
    main()
