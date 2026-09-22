#!/usr/bin/env python3
from __future__ import annotations

from collections import deque
from fractions import Fraction
import hashlib
import json
import re
from typing import Any

SCHEMA = "radicadsac-pb00704-exact-partition/1.0"
CERT_SCHEMA = "radicadsac-pb00704-connectivity-certificate/1.0"
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_CELL_KEYS = {
    "body_id",
    "lineage_id",
    "kernel_id",
    "topology_id",
    "provider_component_id",
    "component_id",
    "enumeration_index",
    "volume_rank",
    "nearest_component",
    "proximity_match",
}
AXES = ("x", "y", "z")


class ContractError(ValueError):
    pass


def _fraction(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("binary float/bool is forbidden as exact authority")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, str) or not value:
        raise TypeError("exact rationals must be encoded as nonempty strings or integers")
    if any(token in value.lower() for token in ("nan", "inf", "e")):
        raise ValueError("nonfinite/scientific/approximate scalar is forbidden")
    return Fraction(value)


def _canonical_fraction(value: Any) -> str:
    q = _fraction(value)
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def _require_digest(value: Any, name: str) -> str:
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
        raise ContractError(f"{name} must be a lowercase SHA-256 hex digest")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _canonical_bounds(bounds: Any) -> dict[str, list[str]]:
    if not isinstance(bounds, dict) or set(bounds) != set(AXES):
        raise ContractError("cell bounds must contain exactly x/y/z")
    result: dict[str, list[str]] = {}
    for axis in AXES:
        interval = bounds[axis]
        if not isinstance(interval, list) or len(interval) != 2:
            raise ContractError(f"{axis} interval must contain exactly two endpoints")
        lo, hi = map(_fraction, interval)
        if not lo < hi:
            raise ContractError("every material cell must have strictly positive extent")
        result[axis] = [_canonical_fraction(lo), _canonical_fraction(hi)]
    return result


def _canonical_cell(cell: Any) -> dict[str, Any]:
    if not isinstance(cell, dict):
        raise ContractError("cell must be an object")
    forbidden = FORBIDDEN_CELL_KEYS.intersection(cell)
    if forbidden:
        raise ContractError(f"backend/durable identity fields forbidden in cell: {sorted(forbidden)}")
    if set(cell) != {"cell_id", "bounds"}:
        raise ContractError("cell contains unsupported authority fields")
    cell_id = cell["cell_id"]
    if not isinstance(cell_id, str) or not cell_id:
        raise ContractError("cell_id must be a nonempty programme-local certificate identifier")
    return {"cell_id": cell_id, "bounds": _canonical_bounds(cell["bounds"])}


def canonical_partition(partition: Any) -> dict[str, Any]:
    if not isinstance(partition, dict):
        raise ContractError("partition must be an object")
    required = {
        "schema",
        "frame_id",
        "source_digest",
        "material_digest",
        "event_digest",
        "configuration_digest",
        "revision",
        "cells",
        "completeness_certificate",
    }
    if set(partition) != required:
        raise ContractError("partition fields do not match the bounded certificate contract")
    if partition["schema"] != SCHEMA:
        raise ContractError("unsupported partition schema")
    frame_id = partition["frame_id"]
    if not isinstance(frame_id, str) or not frame_id:
        raise ContractError("frame_id must be nonempty")
    revision = partition["revision"]
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise ContractError("revision must be a nonnegative integer")
    cells_raw = partition["cells"]
    if not isinstance(cells_raw, list):
        raise ContractError("cells must be a finite list")
    cells = [_canonical_cell(cell) for cell in cells_raw]
    ids = [cell["cell_id"] for cell in cells]
    if len(ids) != len(set(ids)):
        raise ContractError("duplicate cell_id")
    cells.sort(key=lambda cell: cell["cell_id"])

    completeness = partition["completeness_certificate"]
    if not isinstance(completeness, dict):
        raise ContractError("completeness_certificate must be an object")
    required_complete = {
        "authority",
        "certificate_digest",
        "certified_complete",
        "certified_empty",
        "independent_of_connectivity_checker",
    }
    if set(completeness) != required_complete:
        raise ContractError("completeness certificate fields do not match contract")
    if completeness["authority"] != "INDEPENDENT_CERTIFIED_PARTITION":
        raise ContractError("partition completeness must come from an independent certified authority")
    _require_digest(completeness["certificate_digest"], "completeness certificate digest")
    if completeness["certified_complete"] is not True:
        raise ContractError("partition must be independently certified complete")
    if completeness["independent_of_connectivity_checker"] is not True:
        raise ContractError("self-certified partition completeness is forbidden")
    if not isinstance(completeness["certified_empty"], bool):
        raise ContractError("certified_empty must be boolean")
    if bool(cells) == completeness["certified_empty"]:
        raise ContractError("empty-state certificate disagrees with supplied exact cells")

    return {
        "schema": SCHEMA,
        "frame_id": frame_id,
        "source_digest": _require_digest(partition["source_digest"], "source_digest"),
        "material_digest": _require_digest(partition["material_digest"], "material_digest"),
        "event_digest": _require_digest(partition["event_digest"], "event_digest"),
        "configuration_digest": _require_digest(partition["configuration_digest"], "configuration_digest"),
        "revision": revision,
        "cells": cells,
        "completeness_certificate": {
            "authority": completeness["authority"],
            "certificate_digest": completeness["certificate_digest"],
            "certified_complete": True,
            "certified_empty": completeness["certified_empty"],
            "independent_of_connectivity_checker": True,
        },
    }


def _interval_relation(a: list[str], b: list[str]) -> str:
    alo, ahi = map(_fraction, a)
    blo, bhi = map(_fraction, b)
    overlap = min(ahi, bhi) - max(alo, blo)
    if overlap > 0:
        return "INTERIOR_OVERLAP"
    if overlap == 0 and (ahi == blo or bhi == alo):
        return "TOUCH"
    return "GAP"


def cell_relation(a: dict[str, Any], b: dict[str, Any]) -> str:
    aa = _canonical_cell(a)
    bb = _canonical_cell(b)
    relations = [_interval_relation(aa["bounds"][axis], bb["bounds"][axis]) for axis in AXES]
    if all(rel == "INTERIOR_OVERLAP" for rel in relations):
        return "INTERIOR_OVERLAP"
    if "GAP" in relations:
        return "DISJOINT"
    touches = relations.count("TOUCH")
    overlaps = relations.count("INTERIOR_OVERLAP")
    if touches == 1 and overlaps == 2:
        return "FACE_ADJACENT"
    if touches == 2 and overlaps == 1:
        return "EDGE_TOUCH_ONLY"
    if touches == 3:
        return "POINT_TOUCH_ONLY"
    raise AssertionError(f"unclassified exact relation: {relations}")


def _validate_expected_binding(partition: dict[str, Any], expected_binding: Any) -> None:
    required = {
        "frame_id",
        "source_digest",
        "material_digest",
        "event_digest",
        "configuration_digest",
        "revision",
    }
    if not isinstance(expected_binding, dict) or set(expected_binding) != required:
        raise ContractError("expected binding must explicitly name every authority identity")
    for key in required:
        if expected_binding[key] != partition[key]:
            raise ContractError(f"stale/mismatched {key} binding")


def certify_connectivity(partition: Any, expected_binding: Any) -> dict[str, Any]:
    canonical = canonical_partition(partition)
    _validate_expected_binding(canonical, expected_binding)
    cells = canonical["cells"]

    adjacency: dict[str, set[str]] = {cell["cell_id"]: set() for cell in cells}
    contacts: list[dict[str, str]] = []
    for i, first in enumerate(cells):
        for second in cells[i + 1 :]:
            relation = cell_relation(first, second)
            if relation == "INTERIOR_OVERLAP":
                raise ContractError("partition cells have overlapping positive-volume interiors")
            contacts.append({"a": first["cell_id"], "b": second["cell_id"], "relation": relation})
            if relation == "FACE_ADJACENT":
                adjacency[first["cell_id"]].add(second["cell_id"])
                adjacency[second["cell_id"]].add(first["cell_id"])

    components: list[list[str]] = []
    unseen = set(adjacency)
    while unseen:
        seed = min(unseen)
        queue = deque([seed])
        unseen.remove(seed)
        component: list[str] = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for nxt in sorted(adjacency[current]):
                if nxt in unseen:
                    unseen.remove(nxt)
                    queue.append(nxt)
        components.append(sorted(component))
    components.sort(key=lambda group: group[0] if group else "")

    contact_counts = {
        kind: sum(item["relation"] == kind for item in contacts)
        for kind in ("FACE_ADJACENT", "EDGE_TOUCH_ONLY", "POINT_TOUCH_ONLY", "DISJOINT")
    }
    authority_binding = {
        key: canonical[key]
        for key in (
            "frame_id",
            "source_digest",
            "material_digest",
            "event_digest",
            "configuration_digest",
            "revision",
        )
    }
    partition_digest = sha256_json(canonical)
    payload = {
        "schema": CERT_SCHEMA,
        "status": "CERTIFIED_BOUNDED_CONNECTIVITY",
        "route": "EXACT_RATIONAL_AXIS_ALIGNED_COMPLETE_PARTITION_V1",
        "authority_binding": authority_binding,
        "partition_digest": partition_digest,
        "completeness_certificate_digest": canonical["completeness_certificate"]["certificate_digest"],
        "cell_ids": [cell["cell_id"] for cell in cells],
        "components": components,
        "component_count": len(components),
        "exact_empty_material": not cells,
        "contact_counts": contact_counts,
        "durable_identity_authority": False,
        "backend_topology_authority": False,
        "universal_topology_claim": False,
    }
    payload["certificate_digest"] = sha256_json(payload)
    return payload


def make_partition(
    cells: list[dict[str, Any]],
    *,
    frame_id: str = "workpiece-v1",
    source_digest: str = "1" * 64,
    material_digest: str = "2" * 64,
    event_digest: str = "3" * 64,
    configuration_digest: str = "4" * 64,
    revision: int = 1,
    completeness_digest: str = "5" * 64,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "frame_id": frame_id,
        "source_digest": source_digest,
        "material_digest": material_digest,
        "event_digest": event_digest,
        "configuration_digest": configuration_digest,
        "revision": revision,
        "cells": cells,
        "completeness_certificate": {
            "authority": "INDEPENDENT_CERTIFIED_PARTITION",
            "certificate_digest": completeness_digest,
            "certified_complete": True,
            "certified_empty": not cells,
            "independent_of_connectivity_checker": True,
        },
    }


def box(cell_id: str, x0: Any, x1: Any, y0: Any, y1: Any, z0: Any, z1: Any) -> dict[str, Any]:
    return {
        "cell_id": cell_id,
        "bounds": {
            "x": [x0, x1],
            "y": [y0, y1],
            "z": [z0, z1],
        },
    }


def expected_binding(partition: dict[str, Any]) -> dict[str, Any]:
    return {
        key: partition[key]
        for key in (
            "frame_id",
            "source_digest",
            "material_digest",
            "event_digest",
            "configuration_digest",
            "revision",
        )
    }
