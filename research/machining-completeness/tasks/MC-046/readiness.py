#!/usr/bin/env python3
"""MC-046 T2 preregistered PLAN_ONLY preflight. No native campaign or capability result."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
MC004 = ROOT / "research/machining-completeness/tasks/MC-004/qualification-contract-v1.json"
MC004_BLOB = "22d5f976718edac9a8ccce3cb46f799b76e85ab4"
SCHEMA = "radicadsac-mc046-t2-plan-only/1.0"
TIERS = ("T2-G10", "T2-G100", "T2-G1000", "T2-G10000")


class Refused(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise Refused(reason)


def unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in obj, f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def read_json(raw: bytes, *, allow_floats: bool = False) -> Any:
    """Do not allow JSON ambiguity, float conversion, invalid Unicode or codepoint loss."""
    def no_float(value: str) -> Any:
        raise Refused("float number not permitted in T2 preparation manifest")

    def no_constant(value: str) -> Any:
        raise Refused("nonfinite JSON constant not permitted")

    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys,
                            parse_float=(float if allow_floats else no_float), parse_constant=no_constant)
        queue = [result]
        while queue:
            item = queue.pop()
            if isinstance(item, str):
                item.encode("utf-8")  # rejects unpaired surrogate code points
            elif isinstance(item, dict):
                queue.extend(item.keys())
                queue.extend(item.values())
            elif isinstance(item, list):
                queue.extend(item)
        return result
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise Refused("invalid JSON syntax, depth or Unicode") from exc


def blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def load_contract() -> dict[str, Any]:
    # Windows checkout may rewrite LF to CRLF. Compare the canonical tracked
    # Git blob, not the platform-specific working-tree representation.
    relative = MC004.relative_to(ROOT).as_posix()
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"HEAD:{relative}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
        )
        dirty = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain",
             "--untracked-files=no", "--", relative],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Refused("tracked MC-004 source cannot be verified") from exc
    require(not dirty.stdout.strip(), "MC-004 working-tree source has uncommitted changes")
    raw = result.stdout
    require(blob(raw) == MC004_BLOB, "reviewed MC-004 source blob drift")
    contract = read_json(raw, allow_floats=True)
    require(isinstance(contract, dict) and
            contract.get("schema") == "radicadsac-mc-qualification-contract/1.0",
            "unexpected MC-004 qualification contract")
    require(contract.get("native_geometry_claimed") is False and
            contract["execution_protocol"].get("paid_or_native_execution_authorized_by_this_contract") is False,
            "MC-004 must not authorize execution")
    return contract


def by_id(items: Any, key: str) -> dict[str, dict[str, Any]]:
    require(isinstance(items, list), f"{key} profiles absent")
    result = {}
    for row in items:
        require(isinstance(row, dict) and isinstance(row.get(key), str) and row[key] not in result,
                f"ambiguous {key} profile")
        result[row[key]] = row
    return result


def expected_plan(contract: dict[str, Any]) -> dict[str, Any]:
    profiles = by_id(contract["workload_profiles"], "id")
    resources = by_id(contract["resource_envelopes_primary_reference"], "profile")
    accuracy = by_id(contract["accuracy_profiles"], "id")
    scope = contract["required_operation_coverage"]
    require(isinstance(scope, list) and len(scope) == 26 and
            len(set(scope)) == 26 and all(isinstance(x, str) and x for x in scope),
            "26 distinct operation IDs required")
    require(contract["reference_hardware"]["primary"].get("id") == "MC-RH-Q1",
            "primary reference hardware drift")
    require(contract["execution_protocol"].get("final_required_completed_repeats") == 3 and
            contract["execution_protocol"].get("repeats_are_sequential") is True,
            "sequential three-repeat contract drift")
    for profile_id in ("A-SEMANTIC", "A-ENGINEERING"):
        require(profile_id in accuracy and
                all(tier in accuracy[profile_id].get("required_for", []) for tier in TIERS),
                f"{profile_id} T2 accuracy coverage missing")
    tiers = []
    for tier in TIERS:
        p = profiles.get(tier)
        r = resources.get(tier)
        require(p is not None and r is not None and p.get("required") is True,
                f"required tier {tier} missing")
        count = int(tier.split("G")[1])
        require(type(p.get("genuine_geometry_changing_sections")) is int and
                p["genuine_geometry_changing_sections"] == count and
                type(p.get("redundant_history_control_sections")) is int and
                p["redundant_history_control_sections"] == count,
                f"{tier} source geometry/redundancy counts drifted")
        require(type(r.get("session_wall_seconds_max")) is int and
                type(r.get("peak_rss_gib_max")) is int and
                type(r.get("timeout_seconds")) is int and
                0 < r["session_wall_seconds_max"] <= r["timeout_seconds"],
                f"{tier} invalid source resource envelope")
        tiers.append({
            "profile": tier,
            "geometry_change_target": count,
            "redundant_history_control_target": count,
            "geometry_change_evidence": "NOT_MATERIALIZED",
            "redundant_control_evidence": "NOT_MATERIALIZED",
            "resource_envelope": copy.deepcopy(r),
            "observed_results": None,
        })
    return {
        "schema": SCHEMA,
        "source_contract_git_blob": MC004_BLOB,
        "evidence_class": "PLAN_ONLY",
        "execution_authorized": False,
        "native_capability_established": False,
        "qualification_claim": False,
        "fixture_state": "NOT_MATERIALIZED",
        "generator_id": contract["workload_generation"]["algorithm_id"],
        "generator_seed_sha256": contract["workload_generation"]["seed_sha256"],
        "reference_hardware_id": "MC-RH-Q1",
        "accuracy_profiles": ["A-SEMANTIC", "A-ENGINEERING"],
        "required_operation_coverage": copy.deepcopy(scope),
        "sequential_repeats": 3,
        "parallel_repeats": False,
        "tiers": tiers,
    }


def typed_equal(actual: Any, expected: Any) -> bool:
    """Exact types: bool must never compare equal to 0/1; floats cannot masquerade as ints."""
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            typed_equal(actual[key], value) for key, value in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            typed_equal(a, b) for a, b in zip(actual, expected))
    return actual == expected


def check_plan(plan: Any, contract: dict[str, Any]) -> None:
    require(isinstance(plan, dict), "proposal must be a JSON object")
    baseline = expected_plan(contract)
    for key, expected in baseline.items():
        require(key in plan and typed_equal(plan[key], expected),
                f"T2 preparation contract drift or forbidden claim: {key}")
    require(plan.keys() == baseline.keys(), "unreviewed T2 preparation fields forbidden")
    # This is intentionally never a geometry/capability pass or a native execution permit.


def self_test(contract: dict[str, Any]) -> int:
    valid = expected_plan(contract)
    check_plan(valid, contract)
    check_plan(read_json(json.dumps(valid, ensure_ascii=True).encode("utf-8")), contract)
    mutants: list[tuple[str, Any]] = []
    def mutate(label: str, fn) -> None:
        changed = copy.deepcopy(valid)
        fn(changed)
        mutants.append((label, changed))
    mutate("omit G10000", lambda x: x["tiers"].pop())
    mutate("duplicate G100", lambda x: x["tiers"].__setitem__(2, copy.deepcopy(x["tiers"][1])))
    mutate("one tier relabelled", lambda x: x["tiers"][0].__setitem__("profile", "T2-G100"))
    mutate("geometry target reduced", lambda x: x["tiers"][1].__setitem__("geometry_change_target", 99))
    mutate("redundant controls reduced", lambda x: x["tiers"][2].__setitem__("redundant_history_control_target", 0))
    mutate("geometry and redundant conflated", lambda x: x["tiers"][0].pop("redundant_control_evidence"))
    mutate("invented material change witness", lambda x: x["tiers"][0].__setitem__("geometry_change_evidence", "ASSERTED"))
    mutate("invented redundant witness", lambda x: x["tiers"][3].__setitem__("redundant_control_evidence", "ASSERTED"))
    mutate("fake success results", lambda x: x["tiers"][0].__setitem__("observed_results", {"pass": True}))
    mutate("relaxed time budget", lambda x: x["tiers"][3]["resource_envelope"].__setitem__("timeout_seconds", 9999))
    mutate("relaxed peak RSS", lambda x: x["tiers"][1]["resource_envelope"].__setitem__("peak_rss_gib_max", 20))
    mutate("replace Q1 baseline", lambda x: x.__setitem__("reference_hardware_id", "FASTER-HOST"))
    mutate("change generation seed", lambda x: x.__setitem__("generator_seed_sha256", "0" * 64))
    mutate("narrow operation scope", lambda x: x["required_operation_coverage"].pop())
    mutate("duplicate operation", lambda x: x["required_operation_coverage"].__setitem__(0, x["required_operation_coverage"][1]))
    mutate("drop accuracy", lambda x: x.__setitem__("accuracy_profiles", ["A-SEMANTIC"]))
    mutate("reorder/skip tiers", lambda x: x["tiers"].reverse())
    mutate("fewer repeats", lambda x: x.__setitem__("sequential_repeats", 2))
    mutate("parallel repeats", lambda x: x.__setitem__("parallel_repeats", True))
    mutate("fabricated fixture", lambda x: x.__setitem__("fixture_state", "FROZEN"))
    mutate("pretend native permission", lambda x: x.__setitem__("execution_authorized", True))
    mutate("pretend proof accepted", lambda x: x.__setitem__("native_capability_established", True))
    mutate("pretend qualified", lambda x: x.__setitem__("qualification_claim", True))
    mutate("wrong contract hash", lambda x: x.__setitem__("source_contract_git_blob", "0" * 40))
    mutate("boolean instead of count", lambda x: x["tiers"][0].__setitem__("geometry_change_target", True))
    mutate("undeclared new fields", lambda x: x.__setitem__("dispatch_native", True))
    for name, proposal in mutants:
        try:
            check_plan(proposal, contract)
        except Refused:
            pass
        else:
            raise AssertionError(f"unsafe preparation manifest admitted: {name}")
    raw_cases = [
        (b'{"a":1,"a":1}', "duplicate JSON key"),
        (b'{"a":NaN}', "nonfinite JSON constant"),
        (b'{"a":1e999}', "float number"),
        (b'{"a":"\\ud800"}', "invalid JSON"),
        (b'{"a":', "invalid JSON"),
        (b'\xff', "invalid JSON"),
    ]
    for raw, reason in raw_cases:
        try:
            read_json(raw)
        except Refused as exc:
            assert reason in str(exc), (raw, str(exc))
        else:
            raise AssertionError(f"ambiguous/invalid JSON admitted: {raw!r}")
    return len(mutants) + len(raw_cases)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--contract", action="store_true")
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--emit-plan", action="store_true")
    group.add_argument("--check-plan", type=Path)
    args = p.parse_args()
    try:
        contract = load_contract()
        if args.self_test:
            count = self_test(contract)
            print(f"MC-046 PLAN_ONLY: {count} mutations refused; two synthetic plans admitted; zero native claims")
        elif args.emit_plan:
            print(json.dumps(expected_plan(contract), sort_keys=True, indent=2))
        elif args.check_plan is not None:
            check_plan(read_json(args.check_plan.read_bytes()), contract)
            print("MC-046 PLAN_ONLY structural proposal check passed; NOT native/geometry qualification")
        else:
            expected_plan(contract)
            print(f"MC-046 MC-004 source blob pinned {MC004_BLOB}; MC-041 capability NOT VERIFIED HERE; no native authorization")
    except (Refused, OSError, KeyError, TypeError) as exc:
        p.exit(2, f"REFUSED: {exc}\n")


if __name__ == "__main__":
    main()
