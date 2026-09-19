#!/usr/bin/env python3
import argparse, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
p=argparse.ArgumentParser(); p.add_argument("--contract",action="store_true"); p.parse_args()
a=json.loads((ROOT/"handoffs/current-authority.json").read_text())
assert a["programme"]=="MC-1" and a["production_authorized"] is False
assert (ROOT/"docs/decisions/DR-0026-machining-completeness-programme.md").exists()
assert (ROOT/"docs/machining-completeness/08-SOURCES-AND-EVIDENCE.md").exists()
print("MC-001 contract verification passed")
