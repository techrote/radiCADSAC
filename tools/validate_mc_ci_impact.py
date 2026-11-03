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

def _static_trigger_block(s):
    """Only count events nested below the active root-level YAML on: key."""
    lines = s.splitlines()
    roots = [i for i, line in enumerate(lines) if line == "on:"]
    if len(roots) != 1:
        raise AssertionError("mc1-static: expected one active root-level on: trigger")
    start = roots[0]
    end = next((i for i in range(start + 1, len(lines))
                if lines[i] and not lines[i][0].isspace()
                and not lines[i].lstrip().startswith("#")), len(lines))
    block = lines[start + 1:end]
    for event in ("push", "pull_request"):
        if block.count(f"  {event}:") != 1:
            raise AssertionError(f"mc1-static: expected one active on.{event} event")
    return "\n".join(block) + "\n"


def _static_event_paths(s, event, next_event):
    """Read active positive paths entries for the checked-in MC static YAML layout.

    Fail closed on unexpected list syntax; this is deliberately not a general
    YAML parser or an assertion about arbitrary GitHub Actions workflows.
    """
    # Do not accept event-looking keys under unrelated root objects.
    block = event_block(_static_trigger_block(s) + "\npermissions:\n", event, next_event)
    if "    paths-ignore:" in block:
        raise AssertionError(f"mc1-static: {event} combines paths with paths-ignore")
    lines = block.splitlines()
    headers = [i for i, line in enumerate(lines) if line == "    paths:"]
    if len(headers) != 1:
        raise AssertionError(f"mc1-static: {event} requires exactly one positive paths list")
    paths = set()
    for line in lines[headers[0] + 1:]:
        if line.startswith("      - "):
            item = line[8:].strip()
            if len(item) < 3 or item[0] not in ("'", '"') or item[-1] != item[0]:
                raise AssertionError(f"mc1-static: {event} malformed path entry: {line}")
            pattern = item[1:-1]
            # GitHub evaluates ordered positive and negative path globs.
            # This restricted checker cannot certify exclusions/re-inclusions.
            if pattern.startswith("!"):
                raise AssertionError(f"mc1-static: {event} negative path pattern requires ordered evaluation")
            paths.add(pattern)
        elif not line.strip() or line.lstrip().startswith("#"):
            continue
        elif len(line) - len(line.lstrip(" ")) <= 4:
            break
        else:
            raise AssertionError(f"mc1-static: {event} malformed positive paths list: {line}")
    return paths


def _static_run_commands(s):
    """Find literal commands in unconditional steps[].run fields, not decoy text."""
    if s.count("\njobs:\n") != 1:
        raise AssertionError("mc1-static: expected one jobs section")
    lines = s.split("\njobs:\n", 1)[1].splitlines()
    if any(line.startswith("    if:") for line in lines):
        raise AssertionError("mc1-static: conditional validation job is not qualified")
    if any(line.startswith(("    continue-on-error:", "    defaults:")) for line in lines):
        raise AssertionError("mc1-static: non-enforcing or custom validation job is not qualified")
    commands = set()
    step = None

    def add_step(step):
        # Required validation commands must not be hidden behind step guards.
        if any(line.startswith(("        if:", "        continue-on-error:", "        shell:")) for line in step):
            # A guarded, failure-tolerant or overridden-shell step cannot
            # establish the required validation execution contract.
            return
        for i, line in enumerate(step):
            if not line.startswith("        run:"):
                continue
            value = line[len("        run:"):].strip()
            # YAML > folds newlines: a required-looking line may just be
            # part of a preceding echo command, never an executed command.
            if value in (">", ">-"):
                raise AssertionError("mc1-static: folded run block cannot prove commands")
            if value in ("|", "|-"):
                # This deliberately does not interpret shell control flow.
                # A literal block proves execution only with one substantive
                # statement, never an exit, heredoc or conditional prelude.
                statements = []
                for subline in step[i + 1:]:
                    if subline and not subline.startswith("          "):
                        break
                    statement = subline.strip()
                    if statement.endswith("\\"):
                        # The next physical YAML line is a shell argument,
                        # not an independent executable statement.
                        raise AssertionError("mc1-static: shell continuation cannot prove commands")
                    if statement and not statement.startswith("#"):
                        statements.append(statement)
                if len(statements) == 1:
                    commands.add(statements[0])
            elif value and not value.startswith("#"):
                commands.add(value)

    for line in lines + ["      - __END__"]:
        if line.startswith("      - "):
            if step is not None:
                add_step(step)
            step = [line]
        elif step is not None:
            step.append(line)
    return commands


def validate_mc_static(s):
    # Paths and actual run commands are independently mandatory: stray text,
    # comments, echo strings, and conditionally disabled steps cannot satisfy.
    for event, next_event in (("push", "pull_request"), ("pull_request", "permissions")):
        paths = _static_event_paths(s, event, next_event)
        for path in MC_STATIC_INPUTS:
            if path not in paths:
                raise AssertionError(f"mc1-static: {event} does not watch {path}")
    commands = _static_run_commands(s)
    for command in MC_STATIC_COMMANDS:
        if command not in commands:
            raise AssertionError(f"mc1-static: missing active validation command {command}")

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
    # Active YAML structure matters, not just the presence of a matching substring.
    def reject_static(mutant, label):
        if mutant == mc:
            raise AssertionError(f"self-test did not mutate {label}")
        try:
            validate_mc_static(mutant)
        except AssertionError:
            pass
        else:
            raise AssertionError(f"failed to reject {label}")

    # Event-looking keys are not sufficient without an actual root on:.
    reject_static(mc.replace("\non:\n", "\nnot_on:\n", 1),
                  "renamed root on: event")
    for event, next_event in (("push", "pull_request"), ("pull_request", "permissions")):
        block = event_block(mc, event, next_event)
        reject_static(mc.replace(block, block.replace(
            "    paths:\n", "    paths-ignore:\n      - 'tools/**'\n    paths:\n", 1), 1),
                      f"{event} invalid paths + paths-ignore")
        marker = "      - 'tools/validate_repo.py'\n"
        # Prefixing # leaves the old substring intact but disables its route.
        reject_static(mc.replace(block, block.replace(marker, "#" + marker, 1), 1),
                      f"{event} commented-out route")
        # A later negative glob can veto the earlier positive path in GitHub.
        reject_static(mc.replace(block, block.replace(
            marker, marker + "      - '!tools/**'\n", 1), 1),
                      f"{event} negative pattern shadows required path")
        # An identically spelled path under a different event key is not a route.
        reject_static(mc.replace(block, block.replace(marker, "", 1) +
                                 "    branches:\n" + marker, 1),
                      f"{event} path under branches")

    baseline_run = "        run: python3 tools/validate_repo.py"
    for label, decoy in (
        ("echo decoy", "        run: echo python3 tools/validate_repo.py"),
        ("quoted comment decoy", "        run: echo '# python3 tools/validate_repo.py'"),
        ("non-run field", "        with: python3 tools/validate_repo.py"),
        ("guarded validation step", "        if: false\n        run: python3 tools/validate_repo.py"),
        ("multiline shell comment", "        run: |\n          # python3 tools/validate_repo.py"),
        ("folded run echo decoy", "        run: >\n          echo inert\n          python3 tools/validate_repo.py"),
        ("early-exit shell decoy", "        run: |\n          exit 0\n          python3 tools/validate_repo.py"),
        ("here-document shell decoy", "        run: |\n          cat <<'EOF'\n          python3 tools/validate_repo.py\n          EOF"),
        ("false-branch shell decoy", "        run: |\n          if false; then\n          python3 tools/validate_repo.py\n          fi"),
        ("continue-on-error step", "        continue-on-error: true\n        run: python3 tools/validate_repo.py"),
        ("custom shell step", "        shell: 'echo {0}'\n        run: python3 tools/validate_repo.py"),
        ("backslash-continued echo decoy", "        run: |\n          echo inert \\\n          python3 tools/validate_repo.py"),
    ):
        reject_static(mc.replace(baseline_run, decoy, 1), label)
    reject_static(mc.replace("    runs-on: ubuntu-24.04",
                             "    continue-on-error: true\n    runs-on: ubuntu-24.04", 1),
                  "continue-on-error job")
    reject_static(mc.replace("    runs-on: ubuntu-24.04",
                             "    defaults:\n      run:\n        shell: 'echo {0}'\n    runs-on: ubuntu-24.04", 1),
                  "custom job default shell")
    # MC workflow is inline in the real source. Convert it to a multiline
    # step before introducing an inert echo (not a nonexistent source line).
    workflow_run = "        run: python3 tools/mc_workflow.py self-test"
    validate_mc_static(mc.replace(workflow_run,
                                  "        run: |\n          python3 tools/mc_workflow.py self-test", 1))
    reject_static(mc.replace(workflow_run,
                             "        run: |\n          echo python3 tools/mc_workflow.py self-test", 1),
                  "multiline echo decoy")
    print("MC-1 CI impact self-test passed")
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--self-test",action="store_true"); a=p.parse_args()
    validate(); self_test() if a.self_test else print("MC-1 CI impact validation passed")
