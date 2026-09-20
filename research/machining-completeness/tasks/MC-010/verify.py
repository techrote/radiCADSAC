#!/usr/bin/env python3
"""Cheap structural, boundary and adversarial verification for MC-010."""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
CONTRACT_PATH = TASK / "oracle-foundation-v1.json"
ORACLE_PATH = TASK / "independent_exact_oracle.py"


def fail(message: str) -> None:
    raise AssertionError(message)


def load_oracle():
    spec = importlib.util.spec_from_file_location("mc010_independent_exact_oracle", ORACLE_PATH)
    if spec is None or spec.loader is None:
        fail("cannot load independent oracle")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def box(module, raw):
    if len(raw) != 6:
        fail("box requires six coordinates")
    return module.Box.make(*raw)


def cells_as_tuples(cells):
    return [
        [str(v) for v in (c.x0, c.x1, c.y0, c.y1, c.z0, c.z1)]
        for c in sorted(cells)
    ]


def exact(value: str) -> Fraction:
    return Fraction(value)


def assert_material(module, material, expected):
    got_volume = module.total_volume(material)
    if got_volume != exact(expected["volume"]):
        fail(f"volume mismatch: {got_volume} != {expected['volume']}")
    got_components = module.component_count(material)
    if got_components != expected["components"]:
        fail(f"component mismatch: {got_components} != {expected['components']}")
    if "cells" in expected:
        if cells_as_tuples(material) != expected["cells"]:
            fail(f"cell partition mismatch: {cells_as_tuples(material)} != {expected['cells']}")


def verify_import_independence(contract):
    source = ORACLE_PATH.read_text(encoding="utf-8")
    digest = hashlib.sha256(source.encode()).hexdigest()
    wanted = contract["independent_control"]["source_sha256"]
    if digest != wanted:
        fail(f"independent oracle source digest drift: {digest} != {wanted}")

    allowed = set(contract["independent_control"]["allowed_import_roots"])
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    if imported - allowed:
        fail(f"unapproved independent-oracle imports: {sorted(imported - allowed)}")

    forbidden = {
        "research.rcs-021",
        "rcs-021",
        "material_oracle",
        "tridexel",
        "manifold_fallback",
        "tools.mc_evidence_verifier",
    }
    lowered = source.lower()
    hits = sorted(x for x in forbidden if x.lower() in lowered)
    if hits:
        fail(f"historical/candidate decisive geometry leaked into independent oracle source: {hits}")


def verify_historical_pins(contract):
    for item in contract["historical_shared_decisive_graph"]["files"]:
        path = item["path"]
        proc = subprocess.run(
            ["git", "rev-parse", f"HEAD:{path}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        got = proc.stdout.strip()
        if got != item["blob_sha"]:
            fail(f"protected historical blob changed for {path}: {got} != {item['blob_sha']}")


def validate_independence_claim(claim):
    if claim.get("candidate_output_used_for_expected_truth") is not False:
        fail("candidate output cannot define expected truth")
    if claim.get("decisive_shared_geometry_imports") != []:
        fail("independent control cannot retain decisive shared geometry imports")
    if claim.get("expected_truth_origin") != "task contract exact rational literals reviewed independently of candidate output":
        fail("expected truth origin drift")


def run_controls(contract, module):
    for control in contract["controls"]:
        kind = control["kind"]
        if kind == "subtract":
            stock = box(module, control["stock"])
            cutters = [box(module, raw) for raw in control["cutters"]]
            material = module.subtract_many([stock], cutters)
            assert_material(module, material, control["expected"])
        elif kind == "signed_boundary":
            stock = box(module, control["stock"])
            volumes = {}
            for name in ("gap", "contact", "penetrating"):
                cutter = box(module, control[f"{name}_cutter"])
                volumes[name] = module.total_volume(module.subtract_many([stock], [cutter]))
            expected = control["expected"]
            if volumes["gap"] != exact(expected["gap_volume"]):
                fail("positive gap control changed material")
            if volumes["contact"] != exact(expected["contact_volume"]):
                fail("exact contact removed positive volume")
            if volumes["penetrating"] != exact(expected["penetrating_volume"]):
                fail("signed penetrating neighbour mismatch")
            if not volumes["penetrating"] < volumes["contact"] == volumes["gap"]:
                fail("signed boundary ordering collapsed")
        elif kind == "sweep_subtract":
            stock = box(module, control["stock"])
            cutter = box(module, control["cutter"])
            spec = control["sweep"]
            swept = module.swept_box_axis_parallel(cutter, spec["axis"], spec["start"], spec["end"])
            if cells_as_tuples([swept])[0] != spec["expected_swept_box"]:
                fail(f"{control['id']} swept-set derivation mismatch")
            material = module.subtract_many([stock], [swept])
            assert_material(module, material, control["expected"])
        elif kind == "connectivity":
            for case in control["cases"]:
                material = [box(module, raw) for raw in case["cells"]]
                got = module.component_count(material)
                if got != case["components"]:
                    fail(f"{control['id']} {case['name']} connectivity mismatch: {got}")
        elif kind == "idempotence":
            stock = box(module, control["stock"])
            cutter = box(module, control["cutter"])
            once = module.subtract_many([stock], [cutter])
            twice = module.subtract_many(once, [cutter])
            if once != twice:
                fail("exact retrace was not idempotent")
            assert_material(module, twice, control["expected"])
        else:
            fail(f"unknown control kind {kind}")


def adversarial_controls(contract, module):
    try:
        module.q(0.1)
    except TypeError:
        pass
    else:
        fail("binary float accepted as exact coordinate")
    try:
        module.Box.make(0, 0, 0, 1, 0, 1)
    except ValueError:
        pass
    else:
        fail("zero-volume material cell accepted")

    clean = contract["independent_control"]
    validate_independence_claim(clean)
    corrupt = copy.deepcopy(clean)
    corrupt["candidate_output_used_for_expected_truth"] = True
    try:
        validate_independence_claim(corrupt)
    except AssertionError:
        pass
    else:
        fail("candidate-defined expected truth corruption was accepted")
    corrupt = copy.deepcopy(clean)
    corrupt["decisive_shared_geometry_imports"] = ["research/rcs-021/field.py"]
    try:
        validate_independence_claim(corrupt)
    except AssertionError:
        pass
    else:
        fail("shared decisive geometry corruption was accepted")

    a = module.Box.make(0, 1, 0, 1, 0, 1)
    edge = module.Box.make(1, 2, 1, 2, 0, 1)
    if module.component_count([a, edge]) == 1:
        fail("edge contact was promoted to a volumetric bridge")

    stock = module.Box.make(0, 1, 0, 1, 0, 1)
    cuts = [
        module.Box.make(0, "1/2", 0, 1, 0, 1),
        module.Box.make("500001/1000000", 1, 0, 1, 0, 1),
    ]
    web = module.subtract_many([stock], cuts)
    if module.total_volume(web) != Fraction(1, 1_000_000):
        fail("positive-volume micro-web was erased or inflated")

    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "mc_evidence_verifier.py"), "--self-test"],
        cwd=ROOT,
        check=True,
    )


def verify_contract() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("schema") != "radicadsac-mc-oracle-foundation/1.0" or contract.get("task") != "MC-010":
        fail("wrong MC-010 contract identity")
    if contract["corpus_state"]["F01-F16"] != "UNBUILT":
        fail("MC-010 must not fabricate F01-F16")
    if contract["programme_state"]["MC-B"] != "NOT_ESTABLISHED" or contract["programme_state"]["MC-1"] != "NOT_ESTABLISHED":
        fail("MC-010 cannot promote geometry/programme capability")
    if contract["programme_state"]["native_or_paid_campaign_run"] is not False:
        fail("unexpected native/paid campaign claim")

    verify_import_independence(contract)
    verify_historical_pins(contract)
    module = load_oracle()
    run_controls(contract, module)
    adversarial_controls(contract, module)
    print("MC-010 independent exact controls passed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    args = parser.parse_args()
    if not args.contract:
        parser.error("--contract is required; MC-010 has no native campaign")
    verify_contract()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
