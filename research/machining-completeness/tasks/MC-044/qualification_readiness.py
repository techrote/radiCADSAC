#!/usr/bin/env python3
"""MC-044 final-output denominator PLAN_ONLY preflight, not native STEP qualification."""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import tempfile
from pathlib import Path

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
SCHEMA = "radicadsac-mc044-final-denominator-plan/1.0"
MAX_PLAN_BYTES = 262144
SOURCES = {
    "MC-004": ("research/machining-completeness/tasks/MC-004/qualification-contract-v1.json",
               "22d5f976718edac9a8ccce3cb46f799b76e85ab4"),
    "F01-F16": ("research/machining-completeness/fixture-families-v1.json",
                 "d38b1bff84166b1d0fe2c91b94006ccfdce0f287"),
    "MC-054": ("research/machining-completeness/tasks/MC-054/engineering-output-profile-v1.json",
               "6d9d5924a39e5369a1999c48a9c508dc05fd818e"),
    "MC-017": ("research/machining-completeness/tasks/MC-017/consumer-probe-v1.json",
               "5b8a878cd451165b0814ad16ce6d7f7f59d5e5b6"),
}


class Refused(ValueError):
    pass


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise Refused(reason)


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON field")
        out[key] = value
    return out


def decode(raw: bytes):
    need(len(raw) <= MAX_PLAN_BYTES, "PLAN_ONLY input exceeds byte limit")
    try:
        def reject_constant(value):
            raise Refused("nonfinite JSON token refused")
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs,
                          parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise Refused("invalid PLAN_ONLY JSON") from exc


def encoded(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def tracked_source(path: str, expected: str) -> dict:
    """Read exact tracked Git object, not CRLF-translated Windows worktree bytes."""
    try:
        result = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD:" + path],
                                capture_output=True, check=True, text=True)
        need(result.stdout.strip() == expected, "accepted source Git blob drift: " + path)
        status = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain",
                                 "--untracked-files=no", "--", path],
                                capture_output=True, check=True, text=True)
        need(not status.stdout.strip(), "accepted source has local modifications: " + path)
        raw = subprocess.run(["git", "-C", str(ROOT), "cat-file", "blob", expected],
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise Refused("accepted source could not be source-verified: " + path) from exc
    result = decode(raw)
    need(isinstance(result, dict), "accepted source root is not object")
    return result


def source_plan() -> dict:
    mc004 = tracked_source(*SOURCES["MC-004"])
    registry = tracked_source(*SOURCES["F01-F16"])
    output = tracked_source(*SOURCES["MC-054"])
    consumer = tracked_source(*SOURCES["MC-017"])

    need(mc004.get("schema") == "radicadsac-mc-qualification-contract/1.0",
         "unexpected MC-004 contract")
    ops = mc004.get("required_operation_coverage")
    need(isinstance(ops, list) and len(ops) == 26 and
         all(type(s) is str and bool(s) for s in ops) and len(set(ops)) == 26,
         "all 26 distinct machining operations are mandatory")

    need(registry.get("schema") == "radicadsac-mc-fixture-families/1.0",
         "unexpected fixture registry")
    records = registry.get("families")
    need(isinstance(records, list) and len(records) == 16, "F01-F16 fixture count drift")
    fixtures = []
    for i, record in enumerate(records, 1):
        ident = "F%02d" % i
        need(isinstance(record, dict) and record.get("id") == ident and
             record.get("owner") == "MC-%03d" % (11 + (i - 1) // 4) and
             record.get("mandatory") is True and record.get("state") == "BUILT",
             "mandatory fixture identity/owner/construction drift: " + ident)
        fixtures.append({
            "fixture_id": ident, "construction": "BUILT_NOT_NATIVE_QUALIFIED",
            "native_material_topology": "NOT_EXECUTED",
            "step_layers_A_B_C_D": "NOT_EXECUTED",
            "independent_consumer": "NOT_EXECUTED",
            "disposition": "AWAITING_SOURCE_BOUND_EVIDENCE"
        })

    need(output.get("schema") == "radicadsac-mc054-engineering-output-profile/1.0" and
         output.get("native_execution") is False,
         "MC-054 must be accepted research, not an executed native campaign")
    profile = output.get("profile")
    need(isinstance(profile, dict) and profile.get("id") == "MC-ENG-OUTPUT/1.0",
         "wrong MC-054 output profile")
    classes = profile.get("classes")
    need(isinstance(classes, list) and
         [c.get("id") for c in classes] == ["EO-054-%02d" % i for i in range(1, 7)],
         "all six engineering output classes required")
    empty = profile.get("empty_contract")
    need(isinstance(empty, dict) and
         empty.get("success_state") == "EMPTY_MATERIAL" and
         empty.get("step_artifacts") == [] and
         empty.get("representation_pieces") == [] and
         empty.get("require_exhausted_body_lineage") is True and
         empty.get("consumer_geometry_import") == "NOT_APPLICABLE_EMPTY" and
         empty.get("follow_on_geometry_request") == "EMPTY_NO_GEOMETRY" and
         empty.get("placeholder_step_allowed") is False and
         empty.get("epsilon_solid_allowed") is False,
         "manifest-only empty material profile drift")
    need(profile.get("authority_rules", {}).get("step_topology_may_define_body_identity") is False and
         profile["authority_rules"].get("faceted_or_tessellated_primary_success") is False,
         "derived STEP cannot replace canonical material/body authority")

    need(consumer.get("schema") == "radicadsac-mc017-independent-consumer-probe/1.0" and
         consumer.get("native_execution") is False and
         consumer.get("source_level_candidate", {}).get("status") ==
         "SOURCE_VIABLE_EXECUTION_UNQUALIFIED",
         "MC-017 source-only consumer evidence promoted")
    protocol = consumer.get("probe_protocol", {})
    controls = protocol.get("controls_required_before_native_qualification")
    need(isinstance(controls, list) and
         [c.get("id") for c in controls] ==
         ["CTRL-017-GOOD", "CTRL-017-BAD", "CTRL-017-MATERIAL-WRONG"],
         "independent consumer positive and negative controls missing")
    need(protocol.get("measurement", {}).get("minimum_refinement_runs") == 3 and
         protocol.get("measurement", {}).get("may_claim_exact_geometry") is False and
         protocol.get("follow_on_operation", {}).get("must_consume_imported_geometry") is True and
         protocol["follow_on_operation"].get("may_replay_nominal_machining_history_instead") is False,
         "independent consumer measurement/use policy drift")

    return {
        "schema": SCHEMA, "issue": 106, "task": "MC-044",
        "classification": "PLAN_ONLY", "evidence_class": "SOURCE_MATCHED_PREPARATION",
        "accepted_git_blobs": {k: v[1] for k, v in SOURCES.items()},
        "operation_ids": list(ops),
        "fixture_matrix": fixtures,
        "output_profile": "MC-ENG-OUTPUT/1.0",
        "output_classes": [c["id"] for c in classes],
        "layer_requirements_for_nonempty": ["A", "B", "C", "D"],
        "empty_material_route": {
            "state": "EMPTY_MATERIAL", "step_artifacts": [],
            "representation_pieces": [], "consumer_import": "NOT_APPLICABLE_EMPTY",
            "follow_on_geometry": "EMPTY_NO_GEOMETRY",
            "exhausted_lineage_required": True
        },
        "independent_consumer_controls": [c["id"] for c in controls],
        "independent_consumer_refinements_minimum": 3,
        "real_step_files": "NOT_AVAILABLE",
        "native_measurements": None, "manufacturing_authorized": False,
        "mc_a": "ACCEPTED", "mc_b": "NOT_ESTABLISHED",
        "mc_c": "NOT_ESTABLISHED", "mc_d": "NOT_ESTABLISHED",
        "mc_e": "NOT_ESTABLISHED", "mc_f": "NOT_ESTABLISHED",
        "mc_1": "NOT_ESTABLISHED",
        "production_authorized": False
    }


def check_plan(plan, expected) -> None:
    need(type(plan) is dict and encoded(plan) == encoded(expected),
         "PLAN_ONLY denominator/evidence/nonpromotion mismatch")


def read_plan(path: Path):
    try:
        need(path.is_file() and not path.is_symlink(), "proposal path must be regular file")
        with path.open("rb") as inp:
            raw = inp.read(MAX_PLAN_BYTES + 1)
    except OSError as exc:
        raise Refused("cannot read PLAN_ONLY input") from exc
    return decode(raw)


def self_test(expected) -> int:
    check_plan(copy.deepcopy(expected), expected)
    attacks = []
    def mutate(fn):
        q = copy.deepcopy(expected)
        fn(q)
        attacks.append(q)
    mutate(lambda q: q["fixture_matrix"].pop())
    mutate(lambda q: q["fixture_matrix"].append(copy.deepcopy(q["fixture_matrix"][-1])))
    mutate(lambda q: q["fixture_matrix"][0].update(fixture_id="F02"))
    mutate(lambda q: q["fixture_matrix"][15].update(step_layers_A_B_C_D="PASSED"))
    mutate(lambda q: q["fixture_matrix"][1].update(independent_consumer="COMPLETE"))
    mutate(lambda q: q["operation_ids"].pop())
    mutate(lambda q: q["operation_ids"].append(q["operation_ids"][0]))
    mutate(lambda q: q["output_classes"].pop())
    mutate(lambda q: q.update(output_profile="MESHGEO/1.0"))
    mutate(lambda q: q["layer_requirements_for_nonempty"].remove("D"))
    mutate(lambda q: q["empty_material_route"].update(step_artifacts=["fake.step"]))
    mutate(lambda q: q["empty_material_route"].update(exhausted_lineage_required=False))
    mutate(lambda q: q["independent_consumer_controls"].remove("CTRL-017-BAD"))
    mutate(lambda q: q["independent_consumer_controls"].remove("CTRL-017-MATERIAL-WRONG"))
    mutate(lambda q: q.update(real_step_files="VALIDATED"))
    mutate(lambda q: q.update(native_measurements={"volume": 1}))
    mutate(lambda q: q.update(manufacturing_authorized=True))
    mutate(lambda q: q.update(mc_c="ACCEPTED"))
    mutate(lambda q: q.update(mc_e="ACCEPTED"))
    mutate(lambda q: q.update(mc_f="ACCEPTED"))
    mutate(lambda q: q.update(manufacturing_authorized=0))  # bool/int must not alias
    mutate(lambda q: q.update(production_authorized=True))
    mutate(lambda q: q["accepted_git_blobs"].update({"MC-054": "0" * 40}))
    for i, attack in enumerate(attacks):
        try:
            check_plan(attack, expected)
        except Refused:
            continue
        raise AssertionError("accepted mutation %d" % i)
    with tempfile.TemporaryDirectory() as t:
        path = Path(t) / "plan.json"
        path.write_bytes(encoded(expected))
        check_plan(read_plan(path), expected)
        path.write_bytes(b'{"a":1,"a":2}')
        try:
            read_plan(path)
        except Refused:
            pass
        else:
            raise AssertionError("duplicate-key JSON accepted")
        path.write_bytes(b'{"x":NaN}')
        try:
            read_plan(path)
        except Refused:
            pass
        else:
            raise AssertionError("nonfinite JSON accepted")
        path.write_bytes(b" " * (MAX_PLAN_BYTES + 1))
        try:
            read_plan(path)
        except Refused:
            pass
        else:
            raise AssertionError("oversized JSON accepted")
    return len(attacks) + 3


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    cmd = p.add_mutually_exclusive_group(required=True)
    cmd.add_argument("--emit-plan", action="store_true")
    cmd.add_argument("--check-plan", type=Path)
    cmd.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    try:
        expected = source_plan()
        if args.emit_plan:
            print(json.dumps(expected, sort_keys=True, indent=2))
        elif args.check_plan is not None:
            check_plan(read_plan(args.check_plan), expected)
            print("MC-044 source-matched PLAN_ONLY denominator accepted; no native claim")
        else:
            count = self_test(expected)
            print("MC-044 source-pinned PLAN_ONLY: %d mutations refused; no native claim" % count)
        return 0
    except Refused as exc:
        p.exit(2, "MC-044 REFUSED: %s\n" % exc)


if __name__ == "__main__":
    raise SystemExit(main())
