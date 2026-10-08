#!/usr/bin/env python3
"""Write and independently check the cumulative portable archive, without source execution."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile
import zipfile


def h(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--verification', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sources = json.loads((root/'records/source-manifest.json').read_text())
    assert len(sources) == 18
    assert sum(r['batch']=='2A-R1_NEW' for r in sources) == 10
    files = sorted(p for p in root.rglob('*') if p.is_file() and p != root/'SHA256SUMS')
    assert all(not p.is_symlink() for p in root.rglob('*'))
    (root/'SHA256SUMS').write_text(''.join(h(p.read_bytes())+'  '+p.relative_to(root).as_posix()+'\n' for p in files))
    cmd = [sys.executable, '-I', '-B', str(root/'tools/verify_packet.py'), str(root)]
    local = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=10)
    local_result = json.loads(local.stdout)
    prefix = 'radiCADSAC-2A-R1'
    packaged = sorted(p for p in root.rglob('*') if p.is_file())
    args.archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in packaged:
            z.write(p, prefix+'/'+p.relative_to(root).as_posix())
    actual_paths = {prefix+'/'+p.relative_to(root).as_posix() for p in packaged}
    fresh = None
    with zipfile.ZipFile(args.archive) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(set(z.namelist()))
        assert set(z.namelist()) == actual_paths
        for info in z.infolist():
            path = PurePosixPath(info.filename)
            assert not path.is_absolute() and '..' not in path.parts
            assert not stat.S_ISLNK(info.external_attr >> 16)
            rel = path.relative_to(prefix)
            assert h(z.read(info.filename)) == h((root/str(rel)).read_bytes()), str(rel)
        with tempfile.TemporaryDirectory(prefix='packet-verify-', dir=root.parent) as temp:
            dest = Path(temp)
            z.extractall(dest)
            clone = dest/prefix
            got = subprocess.run([sys.executable,'-I','-B',str(clone/'tools/verify_packet.py'),str(clone)],
                                 check=True,capture_output=True,text=True,timeout=10)
            fresh = json.loads(got.stdout)
            assert fresh == local_result
    result = {'status':'PASS','archive_name':args.archive.name,
              'archive_bytes':args.archive.stat().st_size,'archive_sha256':h(args.archive.read_bytes()),
              'zip_crc':'PASS','all_members_readable':True,'unique_safe_members':True,
              'exact_file_set':True,'all_archive_members_match_local_sha256':True,
              'fresh_extraction_verification':fresh,'local_packet_verification':local_result,
              'verified_at_utc':datetime.now(timezone.utc).isoformat(),
              'scope':'Archive/file integrity and original source blob matches only; no complete Git tree or mathematical/v54 acceptance.'}
    args.verification.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
