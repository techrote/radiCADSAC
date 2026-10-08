#!/usr/bin/env python3
"""Bound the single R1 import attempt and preserve failure/timeout exactly."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
cmd = [sys.executable, '-I', '-B', str(ROOT/'tools/import_only.py')]
record = {'command':cmd, 'cwd':str(ROOT), 'timeout_seconds':15,
          'started_at':datetime.now(timezone.utc).isoformat(), 'attempt':1}
env = os.environ.copy()
env.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
t0 = time.monotonic()
try:
    done = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=15, check=False)
    record.update(returncode=done.returncode, timed_out=False)
    stdout, stderr = done.stdout, done.stderr
except subprocess.TimeoutExpired as exc:
    record.update(returncode=None, timed_out=True)
    stdout = exc.stdout or b''
    stderr = exc.stderr or b''
    if isinstance(stdout,bytes): stdout=stdout.decode('utf-8',errors='replace')
    if isinstance(stderr,bytes): stderr=stderr.decode('utf-8',errors='replace')
record['elapsed_seconds'] = time.monotonic()-t0
(ROOT/'logs/import-smoke.stdout.txt').write_text(stdout)
(ROOT/'logs/import-smoke.stderr.txt').write_text(stderr)
(ROOT/'logs/import-smoke-command.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
print(stdout)
