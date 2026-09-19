#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WF=ROOT/".github"/"workflows"
LEGACY={"bootstrap-consistency.yml","quality.yml","rcs010.yml","rcs011.yml","rcs012.yml","rcs013-architecture.yml","rcs014-handoff.yml","rcs015-handoff.yml","rcs016-freeze.yml","rcs017.yml","rcs018.yml","rcs019.yml","rcs020.yml","rcs021.yml","rcs022.yml","rcs023.yml","rcs024.yml","rcs025.yml","rcs026.yml","rcs027.yml"}
NEEDED=["# MC-1 planning-only impact routing","paths-ignore:","docs/machining-completeness/**","research/machining-completeness/**",".github/workflows/**"]
def check_text(name,s):
    if "pull_request:" not in s: return
    for token in NEEDED:
        if token not in s: raise AssertionError(f"{name}: missing {token}")
def validate():
    missing=[n for n in sorted(LEGACY) if not (WF/n).exists()]
    if missing: raise AssertionError(f"missing legacy workflows: {missing}")
    for n in sorted(LEGACY): check_text(n,(WF/n).read_text(encoding="utf-8"))
    mc=(WF/"mc1-static.yml").read_text(encoding="utf-8")
    for token in ("pull_request:","docs/machining-completeness/**","tools/validate_machining_completeness.py","tools/validate_mc_ci_impact.py"):
        if token not in mc: raise AssertionError(f"mc1-static missing {token}")
def self_test():
    sample=(WF/"quality.yml").read_text(encoding="utf-8").replace("# MC-1 planning-only impact routing","BROKEN",1)
    try: check_text("mutated-quality",sample)
    except AssertionError: pass
    else: raise AssertionError("impact validator failed mutation self-test")
    print("MC-1 CI impact self-test passed")
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--self-test",action="store_true"); a=p.parse_args()
    validate(); self_test() if a.self_test else print("MC-1 CI impact validation passed")
