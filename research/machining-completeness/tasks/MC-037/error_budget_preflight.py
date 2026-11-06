#!/usr/bin/env python3
"""MC-037 exact-rational error-ALLOCATION planning seam; no geometric certification."""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
SOURCE_PINS = {
    "MC-003": (
        "research/machining-completeness/tasks/MC-003/numeric-encoding-contract-v1.json",
        "a5538cab698c806fdedcef7cf563b650638348e0",
    ),
    "MC-015": (
        "research/machining-completeness/tasks/MC-015/certificate-attack-contract-v1.json",
        "f9b7324644db9af125baf14b37c06bae16a24ff3",
    ),
}
STAGES = (
    "source_normalization", "sweep", "material", "topology",
    "reconstruction", "step_handoff",
)
SCHEMA = "radicadsac-mc037-error-allocation-plan/1.0"
MAX_FILE = 32768  # Auxiliary proposal parsing budget, not an MC-1 domain bound.
MAX_DIGITS = 32  # Local preflight resource cap, NOT a tolerance/precision floor.
INT = re.compile(r"(?:0|[1-9][0-9]*)\Z")
RATIONAL = re.compile(r"(0|[1-9][0-9]*)/([1-9][0-9]*)\Z")

class Refused(ValueError):
    """Expected fail-closed planning refusal; never a native verdict."""

def source_pins(pins=SOURCE_PINS):
    if set(pins) != {"MC-003", "MC-015"}:
        raise Refused("source pin inventory changed")
    for key, (rel, expected) in pins.items():
        path = ROOT / rel
        if path.is_symlink() or not path.is_file():
            raise Refused(f"{key} source missing or aliased")
        try:
            got = subprocess.run(
                ["git", "hash-object", str(path)], cwd=ROOT, check=True,
                text=True, capture_output=True
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise Refused(f"{key} source Git identity unavailable") from exc
        if got != expected:
            raise Refused(f"{key} accepted Git source changed")

def exact_keys(value, names, where):
    if type(value) is not dict or set(value) != set(names):
        raise Refused(f"{where} has missing, surplus or wrong-typed fields")

def rational(token):
    if type(token) is not str:
        raise Refused("rational allocation must be a string, never a JSON number")
    match = RATIONAL.fullmatch(token)
    if match is None:
        raise Refused("noncanonical rational token")
    a, b = match.groups()
    if len(a) > MAX_DIGITS or len(b) > MAX_DIGITS:
        raise Refused("rational token exceeds auxiliary digit budget")
    n, d = int(a), int(b)
    if math.gcd(n, d) != 1:
        raise Refused("unreduced rational token")
    return Fraction(n, d)

def propose():
    return {
        "schema": SCHEMA,
        "status": "PLAN_ONLY_NOT_EXECUTED",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_blobs": {key: blob for key, (_, blob) in SOURCE_PINS.items()},
        "trial_request_metres": "1/1000000",
        "stage_allocations_metres": {key: "1/10000000" for key in STAGES},
        "native_measurements": None,
        "independent_geometry_comparison": None,
        "po_06_established": False,
        "po_09_established": False,
        "mc_b_established": False,
        "mc_d_established": False,
        "mc_1_established": False,
        "production_authorized": False,
    }

FIELDS = tuple(propose())

def validate(obj):
    """Check a provisional allocation denominator only; not measurements."""
    exact_keys(obj, FIELDS, "plan")
    for key, expected in (
        ("schema", SCHEMA), ("status", "PLAN_ONLY_NOT_EXECUTED"),
        ("evidence_class", "DETERMINISTIC_MODEL"),
    ):
        if type(obj[key]) is not str or obj[key] != expected:
            raise Refused(f"unaccepted {key}")
    exact_keys(obj["source_blobs"], SOURCE_PINS, "source pins")
    if any(type(obj["source_blobs"][k]) is not str or
           obj["source_blobs"][k] != SOURCE_PINS[k][1] for k in SOURCE_PINS):
        raise Refused("accepted source blob identity mismatch")
    if obj["native_measurements"] is not None or obj["independent_geometry_comparison"] is not None:
        raise Refused("proposal must not contain fabricated measurement or consumer evidence")
    for key in (
        "po_06_established", "po_09_established", "mc_b_established",
        "mc_d_established", "mc_1_established", "production_authorized"
    ):
        if type(obj[key]) is not bool or obj[key] is not False:
            raise Refused(f"unauthorized success promotion: {key}")
    request = rational(obj["trial_request_metres"])
    if request <= 0:
        raise Refused("zero trial request cannot be accepted")
    exact_keys(obj["stage_allocations_metres"], STAGES, "stage allocations")
    amounts = [rational(obj["stage_allocations_metres"][stage]) for stage in STAGES]
    if any(v <= 0 for v in amounts):
        raise Refused("all six stage allocations must be positive")
    total = sum(amounts, Fraction(0))
    if total > request:
        raise Refused("stage allocations exceed provisional trial request")
    # This successful PREPARATION has no geometric interpretation.
    return {
        "status": "ALLOCATIONS_WITHIN_PROVISIONAL_REQUEST_NOT_GEOMETRY_QUALIFIED",
        "stages": len(STAGES),
        "native_executed": False,
        "geometry_qualified": False,
        "mc_1_established": False,
        "production_authorized": False,
    }

def pairs_unique(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise Refused("duplicate JSON property")
        obj[k] = v
    return obj

def invalid_number(value):
    raise Refused("nonfinite or floating JSON authority token")

def read_file(path):
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise Refused("plan must be a singly linked regular file")
        with path.open("rb") as handle:
            opened = os.fstat(handle.fileno())
            ident = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_nlink)
            if not stat.S_ISREG(opened.st_mode) or ident(before) != ident(opened):
                raise Refused("file/descriptor identity mismatch")
            raw = handle.read(MAX_FILE + 1)
            after_read = os.fstat(handle.fileno())
            if ident(opened) != ident(after_read):
                raise Refused("plan changed during read")
        if ident(before) != ident(path.lstat()):
            raise Refused("plan pathname changed during read")
    except OSError as exc:
        raise Refused("plan filesystem custody unavailable") from exc
    if len(raw) > MAX_FILE:
        raise Refused("plan parsing byte budget exceeded")
    try:
        return json.loads(
            raw.decode("utf-8", errors="strict"), object_pairs_hook=pairs_unique,
            parse_float=invalid_number, parse_constant=invalid_number,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Refused("malformed or non-UTF8 JSON plan") from exc

def verify_file(path):
    source_pins()
    return validate(read_file(path))

def self_test():
    source_pins()
    n = 0
    baseline = propose()
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "plan.json"
        def write(obj):
            path.write_text(json.dumps(obj, sort_keys=True), encoding="utf-8")
        def accept(obj):
            nonlocal n
            write(obj)
            out = verify_file(path)
            assert out["native_executed"] is False and out["mc_1_established"] is False
            n += 1
        def refuse():
            nonlocal n
            try:
                verify_file(path)
            except Refused:
                n += 1
            else:
                raise AssertionError("incorrect MC-037 planning input admitted")
        accept(baseline)
        patches = [
            lambda x: x.pop("stage_allocations_metres"),
            lambda x: x["stage_allocations_metres"].pop("topology"),
            lambda x: x["stage_allocations_metres"].update({"unknown": "1/10"}),
            lambda x: x["stage_allocations_metres"].update({"sweep": "1/1"}),
            lambda x: x["stage_allocations_metres"].update({"sweep": "0/1"}),
            lambda x: x["stage_allocations_metres"].update({"sweep": "-1/10"}),
            lambda x: x["stage_allocations_metres"].update({"sweep": "2/20"}),
            lambda x: x["stage_allocations_metres"].update({"sweep": "1/02"}),
            lambda x: x["stage_allocations_metres"].update({"sweep": 0.1}),
            lambda x: x["stage_allocations_metres"].update({"sweep": "9"*64+"/1"}),
            lambda x: x.update({"trial_request_metres": "0/1"}),
            lambda x: x.update({"trial_request_metres": True}),
            lambda x: x.update({"status": "PASS"}),
            lambda x: x.update({"evidence_class": "NATIVE_GEOMETRY"}),
            lambda x: x.update({"native_measurements": {"success": True}}),
            lambda x: x.update({"independent_geometry_comparison": []}),
            lambda x: x.update({"mc_b_established": True}),
            lambda x: x.update({"po_06_established": 0}),
            lambda x: x["source_blobs"].update({"MC-015": "0"*40}),
            lambda x: x["source_blobs"].update({"MC-999": "0"*40}),
            lambda x: x.update({"extra_success": True}),
        ]
        for mutate in patches:
            obj = copy.deepcopy(baseline)
            mutate(obj)
            write(obj)
            refuse()
        write(baseline)
        raw = path.read_text(encoding="utf-8")
        for poisoned in (
            raw.replace('"mc_1_established": false',
                        '"mc_1_established": true, "mc_1_established": false'),
            raw.replace('"MC-015":', '"MC-015": "0", "MC-015":'),
            raw.replace('"po_09_established": false', '"po_09_established": NaN'),
            raw.replace('"po_09_established": false', '"po_09_established": 1.0'),
            "{broken json",
            "\ufeff" + raw,
            raw + " " * (MAX_FILE + 1),
        ):
            path.write_text(poisoned, encoding="utf-8")
            refuse()
        try:
            source_pins({"MC-003": SOURCE_PINS["MC-003"],
                         "MC-015": (SOURCE_PINS["MC-015"][0], "0"*40)})
        except Refused:
            n += 1
        else:
            raise AssertionError("wrong source identity accepted")
        write(baseline)
        alias = Path(folder) / "alias.json"
        try:
            os.link(path, alias)
        except OSError:
            pass
        else:
            refuse()
            alias.unlink()
        try:
            alias.symlink_to(path)
        except (OSError, NotImplementedError):
            pass
        else:
            try:
                verify_file(alias)
            except Refused:
                n += 1
            else:
                raise AssertionError("symlinked proposal accepted")
            alias.unlink()
    print(f"MC-037 exact-rational allocation seam: {n} controls passed; "
          "PLAN_ONLY, no measured error, native geometry, PO-06/09 or MC-1.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--emit-proposal", action="store_true")
    group.add_argument("--check-file", type=Path)
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        elif args.emit_proposal:
            source_pins()
            print(json.dumps(propose(), indent=2, sort_keys=True))
        else:
            print(json.dumps(verify_file(args.check_file), sort_keys=True))
    except Refused as exc:
        print(f"REFUSED: {exc}")
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
