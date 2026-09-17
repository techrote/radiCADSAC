#!/usr/bin/env python3
"""Create per-platform and combined RCS-019 conformance evidence summaries."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path} root must be object")
    return value


def signature(result: dict[str, Any]) -> str:
    rows = [{"id": r["id"], "family": r["family"], "actual": r["actual"]} for r in result["results"]]
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def per_platform(py: Path, node: Path, runner_os: str) -> dict[str, Any]:
    a, b = load(py), load(node)
    if a.get("failure_count") != 0 or b.get("failure_count") != 0:
        raise SystemExit("cannot summarize failing conformance path")
    sa, sb = signature(a), signature(b)
    if sa != sb:
        raise SystemExit("independent implementations disagree")
    return {
        "schema": "rcs-019-platform-result/1.0",
        "runner_os": runner_os,
        "host_observation": platform.platform(),
        "vector_schema": a["vector_schema"],
        "vector_count": a["result_count"],
        "logical_signature_sha256": sa,
        "implementations": {
            a["implementation"]: a["runtime"],
            b["implementation"]: b["runtime"],
        },
        "all_vectors_match_expected": True,
        "independent_paths_agree": True,
    }


def combined(directory: Path) -> dict[str, Any]:
    files = sorted(directory.glob("platform-*.json"))
    if len(files) < 2:
        raise SystemExit(f"need at least two platform results, found {len(files)}")
    items = [load(p) for p in files]
    oses = {x.get("runner_os") for x in items}
    if not {"Linux", "Windows"} <= oses:
        raise SystemExit(f"required Linux and Windows results, observed {sorted(oses)}")
    sigs = {x.get("logical_signature_sha256") for x in items}
    if len(sigs) != 1:
        raise SystemExit("cross-platform logical signatures diverge")
    if not all(x.get("all_vectors_match_expected") and x.get("independent_paths_agree") for x in items):
        raise SystemExit("one platform did not satisfy conformance")
    return {
        "schema": "rcs-019-cross-platform-result/1.0",
        "platforms": items,
        "logical_signature_sha256": next(iter(sigs)),
        "cross_platform_logical_identity": True,
        "required_platforms_present": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path)
    parser.add_argument("--node", type=Path)
    parser.add_argument("--runner-os")
    parser.add_argument("--combine", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.combine:
        result = combined(args.combine)
    else:
        if not (args.python and args.node and args.runner_os):
            parser.error("per-platform mode requires --python, --node and --runner-os")
        result = per_platform(args.python, args.node, args.runner_os)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
