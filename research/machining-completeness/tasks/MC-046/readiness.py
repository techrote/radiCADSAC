#!/usr/bin/env python3
"""MC-046 T2 preregistered PLAN_ONLY preflight. No native campaign or capability result."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
MC004 = ROOT / "research/machining-completeness/tasks/MC-004/qualification-contract-v1.json"
MC004_BLOB = "22d5f976718edac9a8ccce3cb46f799b76e85ab4"
SCHEMA = "radicadsac-mc046-t2-plan-only/1.0"
TIERS = ("T2-G10", "T2-G100", "T2-G1000", "T2-G10000")
MAX_PROPOSAL_BYTES = 1 << 20  # bound untrusted PLAN_ONLY JSON before parsing
MAX_JSON_CONTAINER_DEPTH = 32
MAX_INTEGER_DIGITS = 128  # no unbounded JSON big-integer conversion


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

    def bounded_int(token: str) -> int:
        require(len(token.lstrip("-")) <= MAX_INTEGER_DIGITS,
                "T2 preparation integer token exceeds digit limit")
        return int(token)

    require(len(raw) <= MAX_PROPOSAL_BYTES, "T2 preparation JSON exceeds byte limit")
    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys,
                            parse_float=(float if allow_floats else no_float), parse_constant=no_constant,
                            parse_int=bounded_int)
        # Count containing object/list levels, not scalar fields. Avoid recursive
        # traversal; the depth limit is independent of Python recursion limits.
        queue = [(result, 1)]
        while queue:
            item, depth = queue.pop()
            if isinstance(item, str):
                item.encode("utf-8")  # rejects unpaired surrogate code points
            elif isinstance(item, dict):
                require(depth <= MAX_JSON_CONTAINER_DEPTH, "T2 preparation JSON exceeds depth limit")
                queue.extend((value, depth + 1) for value in item.keys())
                queue.extend((value, depth + 1) for value in item.values())
            elif isinstance(item, list):
                require(depth <= MAX_JSON_CONTAINER_DEPTH, "T2 preparation JSON exceeds depth limit")
                queue.extend((value, depth + 1) for value in item)
        return result
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise Refused("invalid JSON syntax, depth or Unicode") from exc


def proposal_identity(metadata: os.stat_result) -> tuple[int, int, int, int, int, int]:
    """Best-effort local-file custody: identity, link count, size, write/change timestamps."""
    return (metadata.st_dev, metadata.st_ino, metadata.st_nlink,
            metadata.st_size, metadata.st_mtime_ns, metadata.st_ctime_ns)


def require_single_regular(metadata: os.stat_result) -> None:
    require(stat.S_ISREG(metadata.st_mode), "T2 preparation proposal must be a regular file")
    require(metadata.st_nlink == 1, "T2 preparation hard-link alias forbidden")
    # Without a filesystem file identifier we cannot bind lstat to fstat.
    require(metadata.st_ino != 0, "T2 preparation stable file identity unavailable")


def read_proposal(path: Path) -> Any:
    """Bound local PLAN_ONLY proposal reads and refuse inconsistent pathname/descriptor identity.

    This is a cooperative local-filesystem custody check, NOT an atomic
    transaction or a guarantee against a hostile filesystem.
    """
    try:
        pathname_before = path.lstat()  # symlinks are not permitted
        require_single_regular(pathname_before)
        require(pathname_before.st_size <= MAX_PROPOSAL_BYTES,
                "T2 preparation JSON exceeds byte limit")
        with path.open("rb") as stream:
            descriptor_before = os.fstat(stream.fileno())
            require_single_regular(descriptor_before)
            require(proposal_identity(pathname_before) == proposal_identity(descriptor_before),
                    "T2 preparation proposal file identity/metadata changed before open")
            require(descriptor_before.st_size <= MAX_PROPOSAL_BYTES,
                    "T2 preparation JSON exceeds byte limit")
            # Always bound descriptor data even if the file grows during read.
            raw = stream.read(MAX_PROPOSAL_BYTES + 1)
            require(len(raw) <= MAX_PROPOSAL_BYTES,
                    "T2 preparation JSON exceeds byte limit")
            descriptor_after = os.fstat(stream.fileno())
            pathname_after = path.lstat()
            require_single_regular(descriptor_after)
            require_single_regular(pathname_after)
            identity = proposal_identity(pathname_before)
            require(identity == proposal_identity(descriptor_after) ==
                    proposal_identity(pathname_after),
                    "T2 preparation proposal file identity/metadata changed during read")
    except OSError as exc:
        raise Refused("T2 preparation proposal custody/read failed") from exc
    return read_json(raw)


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

    # The untrusted proposal path must refuse resource hazards even though the
    # canonical source-bound MC-004 contract remains fixed by its Git blob.
    deep_array = b"[" * (MAX_JSON_CONTAINER_DEPTH + 1) + b"0" + b"]" * (MAX_JSON_CONTAINER_DEPTH + 1)
    deep_object = b'{"child":' * (MAX_JSON_CONTAINER_DEPTH + 1) + b"0" + b"}" * (MAX_JSON_CONTAINER_DEPTH + 1)
    bounded_negative = [
        (b" " * (MAX_PROPOSAL_BYTES + 1), "byte limit"),
        (deep_array, "depth limit"),
        (deep_object, "depth limit"),
        (b'{"number":' + b"9" * 5000 + b"}", "digit limit"),
    ]
    for raw, reason in bounded_negative:
        try:
            read_json(raw)
        except Refused as exc:
            assert reason in str(exc), (reason, str(exc))
        else:
            raise AssertionError(f"unbounded T2 proposal admitted: {reason}")
    # A true boundary value and a valid real-file CLI input remain admissible.
    depth_32 = b"[" * MAX_JSON_CONTAINER_DEPTH + b"0" + b"]" * MAX_JSON_CONTAINER_DEPTH
    assert read_json(depth_32) == json.loads(depth_32)
    with tempfile.TemporaryDirectory() as tmp:
        proposal = Path(tmp) / "proposal.json"
        proposal.write_bytes(json.dumps(valid).encode("utf-8"))
        check_plan(read_proposal(proposal), contract)
        proposal.write_bytes(b" " * (MAX_PROPOSAL_BYTES + 1))
        try:
            read_proposal(proposal)
        except Refused as exc:
            assert "byte limit" in str(exc), str(exc)
        else:
            raise AssertionError("oversized on-disk proposal admitted")
        # Grow an initially small real file after lstat but before open: the
        # MAX+1 descriptor read must still reject it, not trust only st_size.
        proposal.write_bytes(b"{}")
        original_open = Path.open
        growth_executed = [False]

        def grow_before_open(target: Path, *args, **kwargs):
            if target == proposal and not growth_executed[0]:
                growth_executed[0] = True
                with original_open(proposal, "wb") as output:
                    output.write(b" " * (MAX_PROPOSAL_BYTES + 1))
            return original_open(target, *args, **kwargs)

        with patch.object(Path, "open", grow_before_open):
            try:
                read_proposal(proposal)
            except Refused as exc:
                assert "byte limit" in str(exc), str(exc)
            else:
                raise AssertionError("proposal grown after lstat admitted")
        assert growth_executed[0], "after-stat growth fault was not exercised"
        try:
            read_proposal(Path(tmp))
        except Refused as exc:
            assert "regular file" in str(exc), str(exc)
        else:
            raise AssertionError("directory admitted as proposal")

        # A second genuine file with valid (PLAN_ONLY) content must not be read
        # under the original pathname's identity. This is an actual filesystem
        # replacement between lstat and open, not a fabricated stat result.
        proposal.write_bytes(json.dumps(valid).encode("utf-8"))
        substitute = Path(tmp) / "substitute.json"
        substitute.write_bytes(json.dumps(valid).encode("utf-8"))
        saved_original = Path(tmp) / "original.json"
        swapped = [False]

        def replace_before_open(target: Path, *args, **kwargs):
            if target == proposal and not swapped[0]:
                swapped[0] = True
                proposal.replace(saved_original)
                substitute.replace(proposal)
            return original_open(target, *args, **kwargs)

        with patch.object(Path, "open", replace_before_open):
            try:
                read_proposal(proposal)
            except Refused as exc:
                assert "identity/metadata changed" in str(exc), str(exc)
            else:
                raise AssertionError("after-stat pathname replacement admitted")
        assert swapped[0], "real pathname replacement injection not exercised"
        # New pathname is a legitimate independent PLAN_ONLY file after swap.
        check_plan(read_proposal(proposal), contract)

        alias_refusals = 0
        hard_alias = Path(tmp) / "hard-alias.json"
        try:
            os.link(proposal, hard_alias)
        except (OSError, NotImplementedError):
            print("MC-046 custody control: hard-link creation unsupported; not exercised")
        else:
            try:
                read_proposal(proposal)
            except Refused as exc:
                assert "hard-link alias" in str(exc), str(exc)
            else:
                raise AssertionError("hard-linked PLAN_ONLY proposal admitted")
            alias_refusals += 1
            hard_alias.unlink()

        sym_alias = Path(tmp) / "symbolic-alias.json"
        try:
            sym_alias.symlink_to(proposal)
        except (OSError, NotImplementedError):
            print("MC-046 custody control: symlink creation unsupported; not exercised")
        else:
            try:
                read_proposal(sym_alias)
            except Refused as exc:
                assert "regular file" in str(exc), str(exc)
            else:
                raise AssertionError("symlinked PLAN_ONLY proposal admitted")
            alias_refusals += 1
            sym_alias.unlink()
        check_plan(read_proposal(proposal), contract)
        print(f"MC-046 custody: real after-stat replacement refused; {alias_refusals} file-alias controls exercised")
    return len(mutants) + len(raw_cases) + len(bounded_negative) + 4 + alias_refusals


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
            check_plan(read_proposal(args.check_plan), contract)
            print("MC-046 PLAN_ONLY structural proposal check passed; NOT native/geometry qualification")
        else:
            expected_plan(contract)
            print(f"MC-046 MC-004 source blob pinned {MC004_BLOB}; MC-041 capability NOT VERIFIED HERE; no native authorization")
    except (Refused, OSError, KeyError, TypeError) as exc:
        p.exit(2, f"REFUSED: {exc}\n")


if __name__ == "__main__":
    main()
