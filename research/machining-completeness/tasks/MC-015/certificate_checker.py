#!/usr/bin/env python3
"""Independent exact certificate checker for MC-015.

Checks bounded programme certificate statements without importing candidate
geometry or fixture-oracle implementations. A PASS proves only the recorded
certificate obligations, not universal witness completeness or MC-B.
"""
from __future__ import annotations

import copy
import hashlib
from fractions import Fraction
from typing import Any

SCHEMA = "radicadsac-mc015-certificate/1.0"
PREFIX = "sha256:"
TERMINALS = {"SUCCEEDED", "TIMEOUT", "RESOURCE_EXHAUSTED", "REJECTED", "ERROR", "CRASH", "NOT_EXECUTED"}
STATES = {"MATERIAL", "VOID", "BOUNDARY"}
RELATIONS = ("lower_subset_nominal", "nominal_subset_upper", "lower_subset_candidate", "candidate_subset_upper")


class CertificateError(ValueError):
    pass


def fail(message: str) -> None:
    raise CertificateError(message)


def safe(value: Any, where: str = "root") -> None:
    if isinstance(value, float):
        fail(f"binary float forbidden at {where}")
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            safe(item, f"{where}[{i}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                fail(f"non-string key at {where}")
            safe(item, f"{where}.{key}")
        return
    fail(f"unsupported value at {where}")


def obj(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{where} must be an object")
    return value


def arr(value: Any, where: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{where} must be an array")
    return value


def text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{where} must be a non-empty string")
    return value


def digest(value: Any, where: str) -> str:
    value = text(value, where)
    if len(value) != 71 or not value.startswith(PREFIX) or any(c not in "0123456789abcdef" for c in value[7:]):
        fail(f"{where} must be lower-case sha256:<64-hex>")
    return value


def q(value: Any, where: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        fail(f"{where} must be exact integer/rational authority")
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str) and value:
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise CertificateError(f"{where} is not an exact rational") from exc
    fail(f"{where} must be an integer or rational string")


def independent(value: Any, where: str, candidate: str) -> str:
    authority = text(value, where)
    if authority == candidate or authority.startswith("candidate:"):
        fail(f"{where} cannot be candidate authority")
    return authority


def validate(certificate: dict[str, Any]) -> None:
    c = obj(certificate, "certificate")
    safe(c)
    if c.get("schema") != SCHEMA:
        fail("certificate schema/version mismatch")
    text(c.get("certificate_id"), "certificate_id")
    text(c.get("fixture_id"), "fixture_id")
    family = text(c.get("family"), "family")
    if len(family) != 3 or family[0] != "F" or not family[1:].isdigit() or not 1 <= int(family[1:]) <= 16:
        fail("family must be F01..F16")
    if c.get("expected_class") not in {"VALID_NONEMPTY", "VALID_EMPTY", "INVALID_CONTROL"}:
        fail("expected_class invalid")
    if c.get("terminal_reason") not in TERMINALS:
        fail("terminal_reason invalid")

    candidate = obj(c.get("candidate"), "candidate")
    cid = text(candidate.get("identity"), "candidate identity")
    digest(candidate.get("source_digest"), "candidate source")
    digest(candidate.get("config_digest"), "candidate config")
    checker = obj(c.get("checker"), "checker")
    independent(checker.get("identity"), "checker identity", cid)
    digest(checker.get("source_digest"), "checker source")
    oracle = obj(c.get("oracle"), "oracle")
    independent(oracle.get("identity"), "oracle identity", cid)
    digest(oracle.get("source_digest"), "oracle source")
    if oracle.get("independent_from_candidate") is not True:
        fail("oracle must be independent from candidate")
    if arr(oracle.get("shared_decisive_components"), "shared_decisive_components"):
        fail("oracle cannot share decisive geometry with candidate")
    independent(c.get("expected_authority"), "expected authority", cid)

    m = obj(c.get("material"), "material")
    lower = q(m.get("lower_volume"), "lower_volume")
    nominal = q(m.get("nominal_volume"), "nominal_volume")
    observed = q(m.get("candidate_volume"), "candidate_volume")
    upper = q(m.get("upper_volume"), "upper_volume")
    band = q(m.get("band_volume"), "band_volume")
    allowed = q(m.get("max_symmetric_difference"), "max_symmetric_difference")
    if min(lower, nominal, observed, upper, band, allowed) < 0:
        fail("negative material volume/bound")
    if not lower <= nominal <= upper:
        fail("nominal material outside sandwich")
    if not lower <= observed <= upper:
        fail("candidate material outside sandwich")
    if band != upper - lower:
        fail("band must equal exact upper-minus-lower volume")
    if abs(observed - nominal) > band:
        fail("volume disagreement exceeds band")
    if band > allowed:
        fail("band exceeds preregistered allowance")
    relations = obj(m.get("relations"), "material.relations")
    if set(relations) != set(RELATIONS):
        fail("incomplete sandwich relation inventory")
    for name in RELATIONS:
        rec = obj(relations[name], f"relation {name}")
        if rec.get("state") != "PROVED":
            fail(f"relation {name} is not PROVED")
        independent(rec.get("authority"), f"relation {name} authority", cid)
        digest(rec.get("evidence_digest"), f"relation {name} evidence")

    seen: set[str] = set()
    for i, raw in enumerate(arr(c.get("probes"), "probes")):
        probe = obj(raw, f"probe {i}")
        pid = text(probe.get("id"), f"probe {i} id")
        if pid in seen:
            fail("duplicate probe id")
        seen.add(pid)
        independent(probe.get("authority"), f"probe {pid} authority", cid)
        digest(probe.get("evidence_digest"), f"probe {pid} evidence")
        if probe.get("expected") not in STATES or probe.get("candidate") not in STATES:
            fail(f"probe {pid} state invalid")

    topo = obj(c.get("topology"), "topology")
    for key in ("expected_components", "candidate_components"):
        if not isinstance(topo.get(key), int) or isinstance(topo.get(key), bool) or topo[key] < 0:
            fail(f"{key} must be a non-negative integer")
    required = arr(topo.get("required_durable_body_ids"), "required body ids")
    actual = arr(topo.get("candidate_durable_body_ids"), "candidate body ids")
    if any(not isinstance(x, str) or not x for x in required + actual):
        fail("durable body ids must be non-empty strings")
    if len(required) != len(set(required)) or len(actual) != len(set(actual)):
        fail("durable body ids must be unique")
    if not isinstance(topo.get("lineage_preserved"), bool):
        fail("lineage_preserved must be boolean")
    independent(topo.get("authority"), "topology authority", cid)
    digest(topo.get("evidence_digest"), "topology evidence")

    if c["expected_class"] == "VALID_NONEMPTY" and nominal <= 0:
        fail("VALID_NONEMPTY requires positive nominal material")
    if c["expected_class"] == "VALID_EMPTY" and nominal != 0:
        fail("VALID_EMPTY requires exact zero nominal material")


def check(certificate: dict[str, Any]) -> tuple[str, list[str]]:
    validate(certificate)
    c = certificate
    if c["expected_class"] == "INVALID_CONTROL":
        return "INVALID", ["EXPECTED_INVALID_CONTROL"]
    if c["terminal_reason"] != "SUCCEEDED":
        return "INCOMPLETE", ["TERMINAL_NOT_SUCCEEDED"]
    reasons: list[str] = []
    candidate_volume = q(c["material"]["candidate_volume"], "candidate_volume")
    if c["expected_class"] == "VALID_EMPTY":
        if candidate_volume != 0:
            reasons.append("EXPECTED_EMPTY_HAS_MATERIAL")
    elif candidate_volume <= 0:
        reasons.append("EXPECTED_NONEMPTY_LOST_ALL_MATERIAL")
    for probe in c["probes"]:
        if probe["candidate"] != probe["expected"]:
            reasons.append(f"PROBE_{probe['id']}_MISMATCH")
    topo = c["topology"]
    if topo["candidate_components"] != topo["expected_components"]:
        reasons.append("COMPONENT_COUNT_MISMATCH")
    if set(topo["candidate_durable_body_ids"]) != set(topo["required_durable_body_ids"]):
        reasons.append("DURABLE_BODY_IDENTITY_MISMATCH")
    if topo["lineage_preserved"] is not True:
        reasons.append("DURABLE_LINEAGE_NOT_PRESERVED")
    return ("FAIL", reasons) if reasons else ("PASS", ["INDEPENDENT_CERTIFICATE_OBLIGATIONS_PASS"])


def _d(label: str) -> str:
    return PREFIX + hashlib.sha256(label.encode()).hexdigest()


def sample(expected_class: str = "VALID_NONEMPTY") -> dict[str, Any]:
    empty = expected_class == "VALID_EMPTY"
    nominal = "0" if empty else "1000001/1000000"
    bodies = ["B-EXHAUSTED"] if empty else ["B-MAIN"]
    components = 0 if empty else 1
    return {
        "schema": SCHEMA,
        "certificate_id": "MC015-CONTROL-001",
        "fixture_id": "MC015-F02-CONTROL",
        "family": "F16" if empty else "F02",
        "expected_class": expected_class,
        "expected_authority": "programme:mc015-independent-control",
        "terminal_reason": "SUCCEEDED",
        "candidate": {"identity": "candidate:synthetic", "source_digest": _d("candidate-source"), "config_digest": _d("candidate-config")},
        "checker": {"identity": "programme:mc015-certificate-checker/1.0", "source_digest": _d("checker")},
        "oracle": {"identity": "programme:mc015-independent-control", "source_digest": _d("oracle"), "independent_from_candidate": True, "shared_decisive_components": []},
        "material": {
            "lower_volume": nominal, "nominal_volume": nominal, "candidate_volume": nominal, "upper_volume": nominal,
            "band_volume": "0", "max_symmetric_difference": "1/1000000",
            "relations": {name: {"state": "PROVED", "authority": "programme:mc015-independent-control", "evidence_digest": _d("relation:" + name)} for name in RELATIONS},
        },
        "probes": [] if empty else [
            {"id": "thin-web", "authority": "programme:mc015-independent-control", "evidence_digest": _d("probe:web"), "expected": "MATERIAL", "candidate": "MATERIAL"},
            {"id": "channel", "authority": "programme:mc015-independent-control", "evidence_digest": _d("probe:channel"), "expected": "VOID", "candidate": "VOID"},
            {"id": "tangent", "authority": "programme:mc015-independent-control", "evidence_digest": _d("probe:tangent"), "expected": "BOUNDARY", "candidate": "BOUNDARY"},
        ],
        "topology": {"expected_components": components, "candidate_components": components, "required_durable_body_ids": bodies, "candidate_durable_body_ids": list(bodies), "lineage_preserved": True, "authority": "programme:mc015-independent-control", "evidence_digest": _d("topology")},
    }


def self_test() -> None:
    base = sample()
    assert check(base)[0] == "PASS"
    assert check(sample("VALID_EMPTY"))[0] == "PASS"
    micro = sample()
    for key in ("lower_volume", "nominal_volume", "candidate_volume", "upper_volume"):
        micro["material"][key] = "1/1000000"
    assert check(micro)[0] == "PASS"

    def reject(name: str, mutate) -> None:
        cert = copy.deepcopy(base)
        mutate(cert)
        try:
            decision, _ = check(cert)
        except CertificateError:
            return
        if decision == "PASS":
            raise AssertionError(f"failed to reject corruption: {name}")

    cases = [
        ("binary float", lambda c: c["material"].__setitem__("candidate_volume", 1.0)),
        ("timeout", lambda c: c.__setitem__("terminal_reason", "TIMEOUT")),
        ("resource exhaustion", lambda c: c.__setitem__("terminal_reason", "RESOURCE_EXHAUSTED")),
        ("candidate checker", lambda c: c["checker"].__setitem__("identity", c["candidate"]["identity"])),
        ("dependent oracle", lambda c: c["oracle"].__setitem__("independent_from_candidate", False)),
        ("shared decisive code", lambda c: c["oracle"].__setitem__("shared_decisive_components", ["shared-field"])),
        ("candidate expected truth", lambda c: c.__setitem__("expected_authority", c["candidate"]["identity"])),
        ("candidate proof authority", lambda c: c["material"]["relations"]["lower_subset_candidate"].__setitem__("authority", c["candidate"]["identity"])),
        ("inverted bound", lambda c: c["material"].__setitem__("lower_volume", "2")),
        ("nominal outside", lambda c: c["material"].__setitem__("nominal_volume", "2")),
        ("candidate outside", lambda c: c["material"].__setitem__("candidate_volume", "2")),
        ("fake band", lambda c: c["material"].__setitem__("band_volume", "1/1000000")),
        ("unproved inclusion", lambda c: c["material"]["relations"]["candidate_subset_upper"].__setitem__("state", "ASSUMED")),
        ("lost thin material", lambda c: c["probes"][0].__setitem__("candidate", "VOID")),
        ("filled channel", lambda c: c["probes"][1].__setitem__("candidate", "MATERIAL")),
        ("collapsed tangent", lambda c: c["probes"][2].__setitem__("candidate", "MATERIAL")),
        ("wrong topology", lambda c: c["topology"].__setitem__("candidate_components", 2)),
        ("lost body", lambda c: c["topology"].__setitem__("candidate_durable_body_ids", [])),
        ("lost lineage", lambda c: c["topology"].__setitem__("lineage_preserved", False)),
        ("positive rounded empty", lambda c: c["material"].__setitem__("candidate_volume", "0")),
        ("duplicate probe", lambda c: c["probes"].append(copy.deepcopy(c["probes"][0]))),
    ]
    for name, mutate in cases:
        reject(name, mutate)

    broad = copy.deepcopy(base)
    broad["material"].update({"lower_volume": "0", "upper_volume": "2", "band_volume": "2"})
    reject("overbroad certificate", lambda c: c["material"].update(broad["material"]))

    bad_empty = sample("VALID_EMPTY")
    bad_empty["material"].update({"candidate_volume": "1/1000000", "upper_volume": "1/1000000", "band_volume": "1/1000000"})
    assert check(bad_empty)[0] == "FAIL"


if __name__ == "__main__":
    self_test()
    print("MC-015 independent certificate checker self-test passed")
