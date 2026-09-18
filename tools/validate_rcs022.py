#!/usr/bin/env python3
"""Validate static and measured RCS-022 contracts without inventing success."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "research/rcs-022/fixture-plan-v1.json"
PROFILE = ROOT / "research/rcs-022/profile-v1.json"
REQUIRED = {
    "metric-block", "inch-equivalent", "analytic-cylinder", "analytic-cone",
    "through-hole", "blind-hole", "two-body-parting", "mill-cut-through",
    "lathe-accepted-r020", "healed-same-domain", "trimmed-curved",
}
NEGATIVE = {
    "wrong_unit_scale", "omitted_body", "invalid_open_non_solid",
    "analytic_degradation", "excessive_dimension_volume_deviation",
    "parser_schema_failure", "downstream_import_failure",
}
EXPECTED_BOUNDS = {
    "wall_timeout_s": 8,
    "cpu_limit_s": 6,
    "address_space_limit_bytes": 1073741824,
}


def fail(msg: str) -> None:
    raise SystemExit(f"RCS-022 validation failed: {msg}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary")
    args = ap.parse_args()
    plan = json.loads(PLAN.read_text())
    profile = json.loads(PROFILE.read_text())

    if plan.get("schema") != "rcs-022-fixture-plan/1.0":
        fail("fixture schema")
    ids = {x["id"] for x in plan.get("cases", [])}
    if ids != REQUIRED:
        fail(f"fixture matrix mismatch: {sorted(ids ^ REQUIRED)}")
    if set(plan.get("negative_cases", [])) != NEGATIVE:
        fail("negative matrix mismatch")

    exporter = profile.get("exporter", {})
    if exporter.get("version") != "8.0.1":
        fail("OCCT version not pinned")
    if exporter.get("source_commit") != "b8f597c677811d1f9f4d8a97f5ae2825c0353a42":
        fail("OCCT commit not pinned")
    if exporter.get("schema_mode") != "AP242DIS":
        fail("schema mode")
    if exporter.get("tessellated") is not False:
        fail("tessellated substitution must be off")

    layer_d = profile["layer_d"]
    if layer_d["parser"].get("product") != "step-io" or layer_d["parser"].get("version") != "0.2.4":
        fail("independent parser pin")
    if layer_d["solid_consumer"].get("product") != "vcad-kernel-step" or layer_d["solid_consumer"].get("version") != "0.10.0":
        fail("independent consumer pin")
    if "no OCCT dependency" not in layer_d["parser"].get("implementation", ""):
        fail("parser independence must be explicit")
    if "no OCCT dependency" not in layer_d["solid_consumer"].get("implementation", ""):
        fail("consumer independence must be explicit")

    bounds = profile.get("execution", {}).get("independent_probe_bounds", {})
    if bounds.get("wall_timeout_seconds") != EXPECTED_BOUNDS["wall_timeout_s"]:
        fail("independent probe wall bound drift")
    if bounds.get("cpu_limit_seconds") != EXPECTED_BOUNDS["cpu_limit_s"]:
        fail("independent probe CPU bound drift")
    if bounds.get("address_space_bytes") != EXPECTED_BOUNDS["address_space_limit_bytes"]:
        fail("independent probe address-space bound drift")

    if args.summary:
        s = json.loads(Path(args.summary).read_text())
        if s.get("schema") != "rcs-022-measured-summary/1.0":
            fail("summary schema")
        if s.get("profile_id") != profile.get("id"):
            fail("summary/profile binding")
        if s.get("qualification_status") not in {
            "interoperability_qualified", "interoperability_unqualified"
        }:
            fail("verdict")
        observed_bounds = s.get("probe_resource_bounds", {})
        for key, expected in EXPECTED_BOUNDS.items():
            if observed_bounds.get(key) != expected:
                fail(f"summary probe bound drift: {key}")

        got = {x["case"]["id"] for x in s.get("positive_cases", [])}
        if got != REQUIRED:
            fail("summary positive matrix incomplete")
        ngot = {x["id"] for x in s.get("negative_cases", [])}
        if ngot != NEGATIVE:
            fail("summary negative matrix incomplete")
        if not s.get("all_negative_controls_pass"):
            fail("adversarial controls did not all detect their faults")

        all_pos = all(x.get("qualified") for x in s["positive_cases"])
        if s.get("all_positive_qualified") is not all_pos:
            fail("all-positive aggregate drift")
        if (s["qualification_status"] == "interoperability_qualified") != all_pos:
            fail("verdict does not match positive evidence")

        expected_blockers: set[str] = set()
        for case in s["positive_cases"]:
            cid = case["case"]["id"]
            if case["exporter"].get("status") == "exported":
                digest = case.get("step_sha256", "")
                if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                    fail(f"missing/invalid STEP digest for {cid}")
                if "consumer" not in case or "consumer_mesh_diagnostic" not in case:
                    fail(f"missing separated consumer observations for {cid}")
                if case["consumer"].get("status") == "accepted" and case["consumer"].get("mode") != "import-only":
                    fail(f"consumer import observation is not import-only for {cid}")
                if case["consumer_mesh_diagnostic"].get("status") == "accepted" and case["consumer_mesh_diagnostic"].get("mode") != "import-plus-mesh-diagnostic":
                    fail(f"consumer diagnostic mode mismatch for {cid}")
            checks = case.get("checks", {})
            if case.get("qualified") != bool(checks) or case.get("qualified") != all(checks.values()):
                fail(f"case qualification/check mismatch for {cid}")
            expected_blockers.update(f"{cid}:{name}" for name, ok in checks.items() if not ok)

        for neg in s["negative_cases"]:
            if not neg.get("passed"):
                expected_blockers.add(f"negative:{neg['id']}")

        actual_blockers = set(s.get("blockers", []))
        if actual_blockers != expected_blockers:
            fail(
                "blocker set is not exact: "
                f"missing={sorted(expected_blockers - actual_blockers)} "
                f"extra={sorted(actual_blockers - expected_blockers)}"
            )
        if s["qualification_status"] == "interoperability_unqualified" and not actual_blockers:
            fail("unqualified verdict must retain exact blockers")

    print("RCS-022 validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
