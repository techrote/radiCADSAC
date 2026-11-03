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
MC_STATIC_INPUTS = (
    "docs/machining-completeness/**",
    "research/machining-completeness/**",
    "handoffs/current-authority.json",
    "tools/validate_repo.py",
    "tools/validate_machining_completeness.py",
    "tools/validate_mc_ci_impact.py",
    "tools/validate_bootstrap_consistency.py",
    "tools/mc_workflow.py",
    "tools/mc_evidence_verifier.py",
    ".github/workflows/mc1-static.yml",
)
MC_STATIC_COMMANDS = (
    "python3 tools/validate_repo.py",
    "python3 tools/validate_machining_completeness.py --self-test",
    "python3 tools/validate_mc_ci_impact.py --self-test",
    "python3 tools/mc_workflow.py self-test",
)

def validate_mc_static(s):
    # Running a validator is not enough: edits to each invoked validator
    # must independently dispatch this workflow on PRs and main pushes.
    for event, next_event in (("push", "pull_request"), ("pull_request", "permissions")):
        block = event_block(s, event, next_event)
        if "\n    paths:\n" not in block:
            raise AssertionError(f"mc1-static: {event} lost positive paths routing")
        for path in MC_STATIC_INPUTS:
            if f"      - '{path}'" not in block:
                raise AssertionError(f"mc1-static: {event} does not watch {path}")
    for command in MC_STATIC_COMMANDS:
        if command not in s:
            raise AssertionError(f"mc1-static: missing validation command {command}")

def validate():
    for n in sorted(BROAD):
        p=WF/n
        if not p.exists(): raise AssertionError(f"missing {n}")
        validate_broad(n,p.read_text(encoding="utf-8"))
    for n in sorted(SELECTIVE):
        p=WF/n
        if not p.exists(): raise AssertionError(f"missing {n}")
        validate_selective(n,p.read_text(encoding="utf-8"))
    mc = (WF/"mc1-static.yml").read_text(encoding="utf-8")
    validate_mc_static(mc)
def self_test():
    s=(WF/"quality.yml").read_text(encoding="utf-8").replace("      - 'docs/machining-completeness/**'","      - 'docs/other/**'",1)
    try: validate_broad("mutated-quality",s)
    except AssertionError: pass
    else: raise AssertionError("failed to reject missing push exclusion")
    s=(WF/"rcs018.yml").read_text(encoding="utf-8").replace("  pull_request:\n    paths:","  pull_request:\n    paths-ignore:\n      - 'docs/machining-completeness/**'\n    paths:",1)
    try: validate_selective("mutated-rcs018",s)
    except AssertionError: pass
    else: raise AssertionError("failed to reject paths + paths-ignore")
    mc = (WF/"mc1-static.yml").read_text(encoding="utf-8")
    validate_mc_static(mc)
    # Each previously omitted validator must independently route both events.
    # Drop one event path at a time; every mutated workflow must be rejected.
    for path in ("tools/validate_repo.py", "tools/validate_bootstrap_consistency.py"):
        for event, next_event in (("push", "pull_request"), ("pull_request", "permissions")):
            block = event_block(mc, event, next_event)
            marker = f"      - '{path}'\n"
            if marker not in block:
                raise AssertionError(f"self-test fixture missing {event} {path} path")
            mutant = mc.replace(block, block.replace(marker, "", 1), 1)
            try:
                validate_mc_static(mutant)
            except AssertionError:
                pass
            else:
                raise AssertionError(f"failed to reject absent {event} {path} route")
    mutant = mc.replace("python3 tools/validate_repo.py", "python3 -V", 1)
    try:
        validate_mc_static(mutant)
    except AssertionError:
        pass
    else:
        raise AssertionError("failed to reject missing baseline validation step")
    print("MC-1 CI impact self-test passed")
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--self-test",action="store_true"); a=p.parse_args()
    validate(); self_test() if a.self_test else print("MC-1 CI impact validation passed")
