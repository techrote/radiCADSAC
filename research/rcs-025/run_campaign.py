#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from stress_model import run_campaign, stable_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--compare-reference", type=Path)
    args = parser.parse_args()
    result = run_campaign()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "campaign-result-v1.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.compare_reference:
        reference = json.loads(args.compare_reference.read_text(encoding="utf-8"))
        if stable_json(reference) != stable_json(result):
            print("RCS-025 deterministic result differs from frozen reference", file=sys.stderr)
            return 2
    print(result["deterministic_core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
