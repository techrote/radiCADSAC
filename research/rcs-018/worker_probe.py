#!/usr/bin/env python3
"""Tiny process-isolated provider-adapter probe for RCS-018."""

from __future__ import annotations

import json
import os
import sys
import time


def main() -> int:
    payload = json.load(sys.stdin)
    mode = payload["mode"]
    operation = payload["operation"]
    provider = payload.get("provider") or {}

    if mode == "timeout":
        time.sleep(2.0)
        return 0
    if mode == "crash":
        os._exit(17)
    if mode == "error":
        print(json.dumps({"status": "provider_error", "message": "deterministic injected provider error"}))
        return 2
    if mode != "success":
        print(json.dumps({"status": "provider_error", "message": f"unknown mode {mode}"}))
        return 2

    print(
        json.dumps(
            {
                "status": "provider_candidate",
                "provider_profile": provider["profile"],
                "geometry_evidence": provider["evidence"],
                "material_body_ids": operation.get("target_body_ids", []),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
