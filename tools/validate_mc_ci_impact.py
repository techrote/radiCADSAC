#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WF=ROOT/".github"/"workflows"
BROAD={"bootstrap-consistency.yml","quality.yml","rcs010.yml","rcs011.yml","rcs012.yml","rcs014-handoff.yml","rcs015-handoff.yml","rcs016-freeze.yml","rcs017.yml","rcs020.yml","rcs021.yml","rcs022.yml","rcs023.yml","rcs024.yml","rcs025.yml","rcs026.yml","rcs027.yml"}
SELECTIVE={"rcs013-architecture.yml","rcs018.yml","rcs019.yml"}
NEEDED=["paths-ignore:","docs/machining-completeness/**","research/machining-completeness/**",".github/workflows/**"]
def event_block(s,event,next_event):
    start=s.index(f"  {event}:")
    end=s.index(f"  {next_event}:",start) if f"  {next_event}:" in s[start+1:] else s.index("\npermissions:",start)
    return s[start:end]
def validate_broad(name,s):
    if "pull_request:" not in s or "push:" not in s: raise AssertionError(f"{name}: missing push/pull_request")
    pr=event_block(s,"pull_request","permissions")
    push=event_block(s,"push","pull_request")
    if "paths:" in pr and "paths-ignore:" not in pr:
        raise AssertionError(f"{name}: unexpectedly classified broad with positive PR paths")
    for label,block in (("push",push),("pull_request",pr)):
        for token in NEEDED:
            if token not in block: raise AssertionError(f"{name}: {label} missing {token}")
def validate_selective(name,s):
    if "pull_request:" not in s or "paths:" not in s:
        raise AssertionError(f"{name}: lost existing positive path routing")
    # GitHub does not permit paths and paths-ignore for the same event.
    pr=s.split("pull_request:",1)[1].split("permissions:",1)[0]
    if "paths-ignore:" in pr: raise AssertionError(f"{name}: invalid PR paths + paths-ignore combination")
    if name=="rcs013-architecture.yml":
        push=event_block(s,"push","pull_request")
        if "paths-ignore:" not in push or "docs/machining-completeness/**" not in push:
            raise AssertionError("rcs013-architecture.yml: MC-only main push would still dispatch")
def validate():
    for n in sorted(BROAD):
        p=WF/n
        if not p.exists(): raise AssertionError(f"missing {n}")
        validate_broad(n,p.read_text(encoding="utf-8"))
    for n in sorted(SELECTIVE):
        p=WF/n
        if not p.exists(): raise AssertionError(f"missing {n}")
        validate_selective(n,p.read_text(encoding="utf-8"))
    mc=(WF/"mc1-static.yml").read_text(encoding="utf-8")
    if mc.count("tools/validate_mc_ci_impact.py") < 3:
        raise AssertionError("mc1-static must watch the impact validator on push and PR and execute it")
    for token in ("pull_request:","docs/machining-completeness/**","tools/validate_machining_completeness.py","python3 tools/validate_repo.py"):
        if token not in mc: raise AssertionError(f"mc1-static missing {token}")
def self_test():
    s=(WF/"quality.yml").read_text(encoding="utf-8").replace("      - 'docs/machining-completeness/**'","      - 'docs/other/**'",1)
    try: validate_broad("mutated-quality",s)
    except AssertionError: pass
    else: raise AssertionError("failed to reject missing push exclusion")
    s=(WF/"rcs018.yml").read_text(encoding="utf-8").replace("  pull_request:\n    paths:","  pull_request:\n    paths-ignore:\n      - 'docs/machining-completeness/**'\n    paths:",1)
    try: validate_selective("mutated-rcs018",s)
    except AssertionError: pass
    else: raise AssertionError("failed to reject paths + paths-ignore")
    print("MC-1 CI impact self-test passed")
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--self-test",action="store_true"); a=p.parse_args()
    validate(); self_test() if a.self_test else print("MC-1 CI impact validation passed")
