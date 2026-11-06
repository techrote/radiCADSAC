#!/usr/bin/env python3
"""MC-048 exact, source-pinned PLAN_ONLY practical-cell preflight. No native execution."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
MC046 = ROOT / "research/machining-completeness/tasks/MC-046/readiness.py"
MC046_BLOB = "e1b5f8d5c20e246632a39f8eb793948c20261051"
SCHEMA = "radicadsac-mc048-practical-cell-plan-only/1.0"
PLATFORM_CANDIDATES = ("ubuntu-24.04", "windows-2022")
TRACKS = ("GENUINE_GEOMETRY_CHANGE", "REDUNDANT_HISTORY_CONTROL")


def verified_mc046():
    """Refuse drift from the accepted MC-046 checker before importing its local code."""
    rel = MC046.relative_to(ROOT).as_posix()
    try:
        raw = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"HEAD:{rel}"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout
        dirty = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain",
             "--untracked-files=no", "--", rel],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("MC-046 source custody unavailable") from exc
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if actual != MC046_BLOB or dirty.strip():
        raise ValueError("accepted MC-046 source drift or dirty working tree")
    spec = importlib.util.spec_from_file_location("mc048_pinned_mc046_readiness", MC046)
    if spec is None or spec.loader is None:
        raise ValueError("accepted MC-046 module cannot be loaded")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def expected_matrix(mc: Any, contract: dict[str, Any]) -> dict[str, Any]:
    """Prepare nonpooled genuine/redundant control cells; no fabricated measurements."""
    plan = mc.expected_plan(contract)
    mc.check_plan(plan, contract)
    mc.require(len(plan["tiers"]) == 4, "four preregistered T2 tiers required")
    mc.require(plan["sequential_repeats"] == 3 and plan["parallel_repeats"] is False,
               "three sequential repeats required")
    mc.require(len(plan["required_operation_coverage"]) == 26, "26 operations required")
    slots = []
    for platform in PLATFORM_CANDIDATES:
        for tier in plan["tiers"]:
            for track in TRACKS:
                count = (tier["geometry_change_target"] if track == TRACKS[0]
                         else tier["redundant_history_control_target"])
                for repeat in range(1, 4):
                    slots.append({
                        "slot_id": f"{platform}/{tier['profile']}/{track}/r{repeat}",
                        "platform_candidate": platform,
                        "tier": tier["profile"],
                        "track": track,
                        "sequential_repeat": repeat,
                        "target_sections": count,
                        "attempt_state": "NOT_EXECUTED",
                        "attempt_artifact_sha256": None,
                        "observed_wall_seconds": None,
                        "observed_peak_rss_gib": None,
                    })
    mc.require(len(slots) == 48 and len({s["slot_id"] for s in slots}) == 48,
               "invalid practical-cell denominator")
    return {
        "schema": SCHEMA,
        "mode": "PLAN_ONLY",
        "source_mc046_git_blob": MC046_BLOB,
        "source_mc004_git_blob": mc.MC004_BLOB,
        "platforms_are_provisional_candidates": True,
        "platform_candidates": list(PLATFORM_CANDIDATES),
        "mc046_source_plan": plan,
        "fixture_state": "NOT_MATERIALIZED",
        "recovery_evidence": "NOT_EXECUTED",
        "execution_authorized": False,
        "native_result_claimed": False,
        "mc_b_established": False,
        "mc_d_established": False,
        "mc_e_established": False,
        "mc_f_established": False,
        "mc_1_established": False,
        "slots": slots,
    }


def check_matrix(candidate: Any, mc: Any, contract: dict[str, Any]) -> None:
    """Strict typed field equality: omitted/pooled/forged cells cannot pass."""
    baseline = expected_matrix(mc, contract)
    mc.require(type(candidate) is dict, "practical-cell proposal must be an object")
    for key, required in baseline.items():
        mc.require(key in candidate and mc.typed_equal(candidate[key], required),
                   f"practical-cell proposal drift or unsupported claim: {key}")
    mc.require(candidate.keys() == baseline.keys(),
               "unreviewed practical-cell proposal fields forbidden")


def self_test(mc: Any, contract: dict[str, Any]) -> int:
    baseline = expected_matrix(mc, contract)
    check_matrix(baseline, mc, contract)
    check_matrix(mc.read_json(json.dumps(baseline).encode("utf-8")), mc, contract)
    mutations = []

    def mutate(label: str, edit) -> None:
        obj = copy.deepcopy(baseline)
        edit(obj)
        mutations.append((label, obj))

    mutate("drop candidate platform", lambda m: m["platform_candidates"].pop())
    mutate("invent platform", lambda m: m["platform_candidates"].append("PROVEN_NATIVE"))
    mutate("drop tier", lambda m: m["slots"].__setitem__(
        slice(None), [s for s in m["slots"] if s["tier"] != "T2-G1000"]))
    mutate("drop redundant history", lambda m: m["slots"].__setitem__(
        slice(None), [s for s in m["slots"] if s["track"] != TRACKS[1]]))
    mutate("drop Windows", lambda m: m["slots"].__setitem__(
        slice(None), [s for s in m["slots"] if s["platform_candidate"] != "windows-2022"]))
    mutate("drop third repeat", lambda m: m["slots"].__setitem__(
        slice(None), [s for s in m["slots"] if s["sequential_repeat"] != 3]))
    mutate("duplicate cell", lambda m: m["slots"].__setitem__(1, copy.deepcopy(m["slots"][0])))
    mutate("fake slot name", lambda m: m["slots"][0].__setitem__("slot_id", "forged"))
    mutate("alter tier", lambda m: m["slots"][0].__setitem__("tier", "T2-G100"))
    mutate("conflate track", lambda m: m["slots"][0].__setitem__("track", TRACKS[1]))
    mutate("reduce genuine sections", lambda m: m["slots"][0].__setitem__("target_sections", 1))
    mutate("reduce redundant sections", lambda m: m["slots"][3].__setitem__("target_sections", 0))
    mutate("boolean repeat", lambda m: m["slots"][0].__setitem__("sequential_repeat", True))
    mutate("invent success", lambda m: m["slots"][0].__setitem__("attempt_state", "PASS"))
    mutate("fake artifact", lambda m: m["slots"][0].__setitem__("attempt_artifact_sha256", "0" * 64))
    mutate("invent wall", lambda m: m["slots"][0].__setitem__("observed_wall_seconds", 1))
    mutate("invent RSS", lambda m: m["slots"][0].__setitem__("observed_peak_rss_gib", 1))
    mutate("fake recovery", lambda m: m.__setitem__("recovery_evidence", "PASS"))
    mutate("authorize native", lambda m: m.__setitem__("execution_authorized", True))
    mutate("fake native result", lambda m: m.__setitem__("native_result_claimed", True))
    mutate("fake MC-F", lambda m: m.__setitem__("mc_f_established", True))
    mutate("fake MC-1", lambda m: m.__setitem__("mc_1_established", True))
    mutate("make platforms authoritative", lambda m: m.__setitem__("platforms_are_provisional_candidates", False))
    mutate("drop operation", lambda m: m["mc046_source_plan"]["required_operation_coverage"].pop())
    mutate("reduce repeats", lambda m: m["mc046_source_plan"].__setitem__("sequential_repeats", 2))
    mutate("alter timeout", lambda m: m["mc046_source_plan"]["tiers"][0][
        "resource_envelope"].__setitem__("timeout_seconds", 9999))
    mutate("wrong source blob", lambda m: m.__setitem__("source_mc046_git_blob", "f" * 40))
    mutate("invent field", lambda m: m.__setitem__("admitted_native", True))
    mutate("reorder slots", lambda m: m["slots"].reverse())
    mutate("boolean section count", lambda m: m["slots"][0].__setitem__("target_sections", True))
    for label, altered in mutations:
        try:
            check_matrix(altered, mc, contract)
        except mc.Refused:
            pass
        else:
            raise AssertionError(f"unsafe practical-cell proposal admitted: {label}")

    invalid = [
        (b'{"x":1,"x":1}', "duplicate JSON key"),
        (b'{"x":NaN}', "nonfinite JSON"),
        (b'{"x":1e999}', "float number"),
        (b'{"x":' + b"8" * 200 + b"}", "digit limit"),
        (b" " * (mc.MAX_PROPOSAL_BYTES + 1), "byte limit"),
    ]
    for raw, reason in invalid:
        try:
            mc.read_json(raw)
        except mc.Refused as exc:
            if reason not in str(exc):
                raise AssertionError(f"wrong refusal {reason}: {exc}") from exc
        else:
            raise AssertionError(f"bad JSON admitted: {reason}")

    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "mc048-plan.json"
        path.write_text(json.dumps(baseline, sort_keys=True), encoding="utf-8")
        check_matrix(mc.read_proposal(path), mc, contract)
        wrong = copy.deepcopy(baseline)
        wrong["slots"][0]["attempt_state"] = "SUCCESS"
        path.write_text(json.dumps(wrong), encoding="utf-8")
        try:
            check_matrix(mc.read_proposal(path), mc, contract)
        except mc.Refused:
            pass
        else:
            raise AssertionError("forged on-disk success admitted")
    return len(mutations) + len(invalid) + 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--contract", action="store_true")
    choice.add_argument("--self-test", action="store_true")
    choice.add_argument("--emit-plan", action="store_true")
    choice.add_argument("--check-plan", type=Path)
    args = parser.parse_args()
    try:
        mc = verified_mc046()
        contract = mc.load_contract()
        expected = expected_matrix(mc, contract)
        if args.self_test:
            count = self_test(mc, contract)
            print(f"MC-048 PLAN_ONLY: {count} adversarial refusals; 48 slots; NO native claims")
        elif args.emit_plan:
            print(json.dumps(expected, indent=2, sort_keys=True))
        elif args.check_plan is not None:
            check_matrix(mc.read_proposal(args.check_plan), mc, contract)
            print("MC-048 PLAN_ONLY: 48 unexecuted slots source-matched; NO native capability or permit")
        else:
            check_matrix(expected, mc, contract)
            print(f"MC-048 pinned MC-004 {mc.MC004_BLOB}, MC-046 {MC046_BLOB}; 48 slots; MC-F NOT ESTABLISHED")
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"REFUSED: {exc}\n")


if __name__ == "__main__":
    main()
