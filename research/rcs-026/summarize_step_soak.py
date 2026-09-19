#!/usr/bin/env python3
"""Aggregate repeated live RCS-022 export/read-back runs for RCS-026."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def projection(summary: dict[str, Any]) -> dict[str, Any]:
    positives = []
    for case in sorted(summary["positive_cases"], key=lambda x: x["case"]["id"]):
        positives.append({
            "id": case["case"]["id"],
            "unit": case["case"].get("unit"),
            "qualified": case["qualified"],
            "export_status": case["exporter"].get("status"),
            "parser_status": case["parser"].get("status"),
            "parser_solid_count": case["parser"].get("solid_count"),
            "consumer_status": case["consumer"].get("status"),
            "consumer_solid_count": case["consumer"].get("solid_count"),
            "checks": case["checks"],
        })
    negatives = [
        {"id": x["id"], "passed": x["passed"], "failure_code": x.get("failure_code")}
        for x in sorted(summary["negative_cases"], key=lambda x: x["id"])
    ]
    return {
        "profile_id": summary["profile_id"],
        "qualification_status": summary["qualification_status"],
        "positive_cases": positives,
        "negative_cases": negatives,
        "blockers": sorted(summary.get("blockers", [])),
        "all_positive_qualified": summary["all_positive_qualified"],
        "all_negative_controls_pass": summary["all_negative_controls_pass"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runs = [load(p) for p in args.input]
    projections = [projection(x) for x in runs]
    if len(runs) < 3:
        raise SystemExit("RCS-026 STEP soak requires at least three live repetitions")
    first = projections[0]
    if not all(x == first for x in projections[1:]):
        raise SystemExit("programme-level STEP export/read-back result drifted between repetitions")
    statuses = [x["qualification_status"] for x in projections]
    if any(x != "interoperability_unqualified" for x in statuses):
        raise SystemExit("RCS-022 Layer-D status must remain interoperability_unqualified")
    output = {
        "schema": "rcs-026-step-soak-summary/1.0",
        "status": "pass",
        "live_repetitions": len(runs),
        "platform_scope": "Linux hosted CI with exact OCCT 8.0.1 baseline",
        "comparison_rule": "programme-level export/parser/consumer/body/check status; STEP byte identity and private B-rep identity are not required",
        "qualification_status": statuses[0],
        "projection": first,
        "step_sha256_observations": [
            {x["case"]["id"]: x.get("step_sha256") for x in run["positive_cases"]}
            for run in runs
        ],
        "windows_step_soak": {
            "status": "not_run",
            "gate5_blocker": "No exact-pinned OCCT 8.0.1 Windows/MSVC STEP worker soak is established by this campaign; founding Windows STEP support remains conditional on that evidence.",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "live_repetitions": output["live_repetitions"], "qualification_status": output["qualification_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
