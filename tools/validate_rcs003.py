#!/usr/bin/env python3
"""Deterministic semantic coverage validation for the RCS-003 corpus."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "research/rcs-003/corpus-v1.json"
SCHEMA = ROOT / "research/rcs-003/corpus.schema.json"
DOC = ROOT / "docs/11-ADVERSARIAL-MANUFACTURING-CORPUS.md"
README = ROOT / "research/rcs-003/README.md"

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)}: cannot parse JSON: {exc}")
        return None


for required in (CORPUS, SCHEMA, DOC, README):
    if not required.is_file():
        fail(f"missing required RCS-003 artifact: {required.relative_to(ROOT)}")

corpus = load_json(CORPUS) if CORPUS.is_file() else None
schema = load_json(SCHEMA) if SCHEMA.is_file() else None

if schema is not None:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        fail("corpus.schema.json: unexpected JSON Schema dialect")
    if schema.get("properties", {}).get("corpus_schema", {}).get("const") != "rcs-003-corpus/1.0":
        fail("corpus.schema.json: corpus_schema const must be rcs-003-corpus/1.0")

if isinstance(corpus, dict):
    if corpus.get("corpus_schema") != "rcs-003-corpus/1.0":
        fail("corpus-v1.json: unexpected corpus_schema")
    if corpus.get("version") != "1.0.0":
        fail("corpus-v1.json: v1 artifact must declare version 1.0.0")

    refs = corpus.get("policy_refs")
    expected_refs = {
        "units": "si-mm-rad-s-v1",
        "frames": "right-handed-z-up-workpiece-v1",
        "tolerance": "rcs-003-fixture-policy-v1",
        "result_policy": "physical-intent-v1",
    }
    if refs != expected_refs:
        fail("corpus-v1.json: policy_refs are incomplete or unexpected")

    families = corpus.get("fixture_families")
    if not isinstance(families, list) or not families:
        fail("corpus-v1.json: fixture_families must be a non-empty list")
        families = []

    seen: set[str] = set()
    domains: dict[str, int] = {"lathe": 0, "mill": 0, "generic": 0}
    all_tags: set[str] = set()
    classifications: set[str] = set()
    separation_domains: set[str] = set()

    for index, family in enumerate(families):
        where = f"fixture_families[{index}]"
        if not isinstance(family, dict):
            fail(f"{where}: family must be an object")
            continue

        family_id = family.get("id")
        domain = family.get("domain")
        if not isinstance(family_id, str) or not family_id:
            fail(f"{where}: missing string id")
            continue
        if family_id in seen:
            fail(f"{where}: duplicate id {family_id}")
        seen.add(family_id)

        if domain not in domains:
            fail(f"{family_id}: domain must be lathe, mill, or generic")
        else:
            domains[domain] += 1
            if not family_id.startswith(domain + "-"):
                fail(f"{family_id}: id prefix must match domain")

        if family.get("revision") != 1:
            fail(f"{family_id}: corpus v1 family revision must be 1")

        tags = family.get("tags")
        if not isinstance(tags, list) or not tags or not all(isinstance(v, str) and v for v in tags):
            fail(f"{family_id}: tags must be non-empty strings")
            tags = []
        if len(tags) != len(set(tags)):
            fail(f"{family_id}: duplicate tags")
        all_tags.update(tags)

        intent = family.get("physical_intent")
        if not isinstance(intent, str) or len(intent.strip()) < 8:
            fail(f"{family_id}: physical_intent is missing or too short")

        setup = family.get("setup")
        if not isinstance(setup, dict):
            fail(f"{family_id}: missing setup")
        else:
            if setup.get("units") != "mm":
                fail(f"{family_id}: setup.units must be mm")
            if setup.get("frame") != "right-handed-z-up-workpiece-v1":
                fail(f"{family_id}: setup.frame must be explicit canonical fixture frame")
            for key in ("stock", "operation_model"):
                if not isinstance(setup.get(key), str) or not setup[key].strip():
                    fail(f"{family_id}: setup.{key} must be non-empty")

        axes = family.get("parameter_axes")
        if not isinstance(axes, list) or not axes:
            fail(f"{family_id}: parameter_axes must be non-empty")
        else:
            axis_names: set[str] = set()
            for axis in axes:
                if not isinstance(axis, dict):
                    fail(f"{family_id}: parameter axis must be an object")
                    continue
                name = axis.get("name")
                if not isinstance(name, str) or not name:
                    fail(f"{family_id}: parameter axis requires name")
                elif name in axis_names:
                    fail(f"{family_id}: duplicate parameter axis {name}")
                else:
                    axis_names.add(name)
                if not isinstance(axis.get("unit"), str) or not axis["unit"]:
                    fail(f"{family_id}: axis {name!r} requires explicit unit")
                values = axis.get("values")
                if not isinstance(values, list) or not values:
                    fail(f"{family_id}: axis {name!r} requires values")

        expected = family.get("expected")
        if not isinstance(expected, dict):
            fail(f"{family_id}: missing expected object")
        else:
            classification = expected.get("classification")
            allowed = {
                "no_material_change",
                "regularized_material_change",
                "body_separation_or_merge",
                "ambiguous_or_unsupported",
            }
            if classification not in allowed:
                fail(f"{family_id}: invalid expected classification")
            else:
                classifications.add(classification)
            connectivity = expected.get("connectivity")
            if connectivity not in {"unchanged", "connected", "disconnected", "parameter_dependent", "not_applicable"}:
                fail(f"{family_id}: invalid connectivity")
            body_count = expected.get("body_count")
            if not ((isinstance(body_count, int) and not isinstance(body_count, bool) and body_count >= 0) or body_count == "parameter-dependent"):
                fail(f"{family_id}: body_count must be non-negative integer or parameter-dependent")
            if classification == "body_separation_or_merge":
                separation_domains.add(str(domain))

        oracle = family.get("oracle")
        if not isinstance(oracle, str) or len(oracle.strip()) < 8:
            fail(f"{family_id}: oracle is missing or too short")

        minimization = family.get("minimization_preserves")
        if not isinstance(minimization, list) or not minimization or not all(isinstance(v, str) and v for v in minimization):
            fail(f"{family_id}: minimization_preserves must be non-empty strings")

    minimum_counts = {"lathe": 10, "mill": 12, "generic": 7}
    for domain, minimum in minimum_counts.items():
        if domains[domain] < minimum:
            fail(f"corpus-v1.json: {domain} coverage too small ({domains[domain]} < {minimum})")

    required_tags = {
        "coincidence",
        "coplanarity",
        "tangency",
        "lower-dimensional-contact",
        "sliver",
        "sub-tolerance",
        "retrace",
        "noise",
        "self-crossing",
        "topology-explosion",
        "large-operation-count",
        "high-segment-count",
        "separation",
        "multi-body",
        "tolerance-accumulation",
    }
    missing_tags = sorted(required_tags - all_tags)
    if missing_tags:
        fail(f"corpus-v1.json: missing required semantic coverage tags: {missing_tags}")

    if not {"lathe", "mill"}.issubset(separation_domains):
        fail("corpus-v1.json: lathe and mill must each contain body separation/merge fixtures")

    if "no_material_change" not in classifications or "regularized_material_change" not in classifications or "body_separation_or_merge" not in classifications:
        fail("corpus-v1.json: required expected-result classes are not represented")

    lifecycle = corpus.get("lifecycle")
    if not isinstance(lifecycle, dict):
        fail("corpus-v1.json: missing lifecycle")
    else:
        for key in ("minimization", "regression", "versioning"):
            if not isinstance(lifecycle.get(key), str) or len(lifecycle[key].strip()) < 20:
                fail(f"corpus-v1.json: lifecycle.{key} is missing or insufficient")

if errors:
    print("RCS-003 corpus validation failed:")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)

print("RCS-003 corpus validation passed")
