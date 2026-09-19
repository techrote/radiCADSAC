#!/usr/bin/env python3
import argparse, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser(); p.add_argument("--contract",action="store_true"); p.parse_args()
subprocess.run([sys.executable,str(ROOT/"tools/validate_mc_ci_impact.py"),"--self-test"],check=True)
print("MC-056 contract verification passed")
