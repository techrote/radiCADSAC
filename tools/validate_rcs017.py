#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "research/rcs-017/README.md",
    ROOT / "research/rcs-017/experiment-plan-v1.json",
    ROOT / "research/rcs-017/harness/CMakeLists.txt",
    ROOT / "research/rcs-017/harness/concurrency_probe.cpp",
    ROOT / "research/rcs-017/harness/run_concurrency_campaign.py",
    ROOT / "docs/21-OCCT-CONCURRENCY-ISOLATION.md",
    ROOT / "docs/decisions/DR-0016-occt-process-isolation-default.md",
    ROOT / ".github/workflows/rcs017.yml",
]


def require(cond, msg):
    if not cond:
        raise SystemExit(msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir")
    args = ap.parse_args()
    for p in REQUIRED:
        require(p.exists(), f"missing required RCS-017 file: {p.relative_to(ROOT)}")

    plan = json.loads((ROOT / "research/rcs-017/experiment-plan-v1.json").read_text())
    require(plan.get("schema") == "rcs017-experiment-plan/1.0", "unexpected experiment-plan schema")
    require(plan.get("occt", {}).get("version") == "8.0.1", "OCCT version must be pinned to 8.0.1")
    require(plan.get("occt", {}).get("commit") == "b8f597c677811d1f9f4d8a97f5ae2825c0353a42", "OCCT commit pin mismatch")
    strategies = set(plan.get("execution_topologies", []))
    require({"sequential", "threads-one-process", "process-isolated"} <= strategies, "missing required execution topology")

    readme = (ROOT / "research/rcs-017/README.md").read_text().lower()
    for term in ["destep_parameters", "interface_static", "setrunparallel", "setparallelmode", "topods_tshape"]:
        require(term in readme, f"README missing required topic: {term}")
    require("process isolation" in readme or "process-isolat" in readme,
            "README missing process-isolation boundary")

    decision = (ROOT / "docs/decisions/DR-0016-occt-process-isolation-default.md").read_text()
    require("Status: accepted" in decision, "DR-0016 must be accepted")
    require("process" in decision.lower() and "thread" in decision.lower(), "decision must compare process and thread boundaries")

    if args.results_dir:
        summary_path = Path(args.results_dir) / "summary.json"
        require(summary_path.exists(), "missing RCS-017 summary.json")
        s = json.loads(summary_path.read_text())
        require(s.get("schema") == "rcs017-concurrency-summary/1.0", "bad measured-summary schema")
        require(s.get("sequential", {}).get("attempts", 0) > 0, "no sequential evidence")
        require("threads" in s and "processes" in s and "global_parallel_state" in s, "missing measured strategy evidence")
        require(s.get("occt", {}).get("commit") == "b8f597c677811d1f9f4d8a97f5ae2825c0353a42", "measured OCCT pin mismatch")
    print("RCS-017 validation passed")

if __name__ == "__main__":
    main()
