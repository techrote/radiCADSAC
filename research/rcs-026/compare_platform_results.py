#!/usr/bin/env python3
"""Compare RCS-026 logical cross-platform evidence without conflating timing metadata."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--linux", type=Path, required=True)
    parser.add_argument("--windows", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    linux = load(args.linux)
    windows = load(args.windows)
    mismatches: list[str] = []
    if linux["logical_projection"] != windows["logical_projection"]:
        mismatches.append("logical_projection")
    if linux["logical_signature_sha256"] != windows["logical_signature_sha256"]:
        mismatches.append("logical_signature_sha256")
    if linux["platform"]["toolchain"]["compiler_id"] not in {"GCC", "Clang"}:
        mismatches.append("linux_compiler_family")
    if windows["platform"]["toolchain"]["compiler_id"] != "MSVC":
        mismatches.append("windows_compiler_family")
    if linux["pins"] != windows["pins"]:
        mismatches.append("pins")
    summary = {
        "schema": "rcs-026-cross-platform-summary/1.0",
        "status": "pass" if not mismatches else "fail",
        "mismatches": mismatches,
        "logical_signature_sha256": linux["logical_signature_sha256"],
        "linux": {"system": linux["platform"]["system"], "toolchain": linux["platform"]["toolchain"], "highest_completed_journal_tier": linux["scale"]["highest_completed_journal_tier"]},
        "windows": {"system": windows["platform"]["system"], "toolchain": windows["platform"]["toolchain"], "highest_completed_journal_tier": windows["scale"]["highest_completed_journal_tier"]},
        "comparison_rule": "programme-level canonical/status/body/lineage/replay invariants only; timing and memory observations are measured per platform and are not required to be bitwise equal",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
