#!/usr/bin/env python3
"""Bounded exact-rational semialgebraic source codec for PB-007-03.

This is a deliberately bounded constructive source language.  It does not turn
opaque STEP/B-rep/mesh/import success into exact source authority and it does not
claim to cover every admitted imported/form/undercut source in MC-002.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json

SCHEMA = "radicadsac-exact-semialgebraic-source/1.0"
ROLES = {"stock", "cutting", "holder"}
AXES = ("x", "y", "z")


def q(value) -> Fraction:
    """Parse an authority rational without accepting binary floating values."""
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("authority rationals must not be bool/float")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, dict) and set(value) == {"numerator", "denominator"}:
        n, d = value["numerator"], value["denominator"]
        if not isinstance(n, str) or not isinstance(d, str):
            raise TypeError("canonical rational numerator/denominator must be strings")
        return Fraction(int(n), int(d))
    raise TypeError(f"unsupported exact rational type: {type(value).__name__}")


def qtext(value) -> str:
    value = q(value)
    return f"{value.numerator}/{value.denominator}"


def _nonempty_text(value, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def normalize_bounds(bounds):
    if not isinstance(bounds, dict) or set(bounds) != set(AXES):
        raise ValueError("exact source bounds must contain exactly x/y/z")
    out = {}
    for axis in AXES:
        pair = bounds[axis]
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError(f"{axis} bound must have exact lower/upper endpoints")
        lo, hi = map(q, pair)
        if not lo < hi:
            raise ValueError(f"{axis} bound must have positive extent")
        out[axis] = (lo, hi)
    return out


def _normalize_exponents(raw):
    if not isinstance(raw, (list, tuple)) or len(raw) != 3:
        raise ValueError("polynomial exponent vector must be [x,y,z]")
    out = []
    for exponent in raw:
        if isinstance(exponent, bool) or not isinstance(exponent, int) or exponent < 0:
            raise TypeError("polynomial exponents must be non-negative integers")
        out.append(exponent)
    return tuple(out)


def normalize_terms(raw_terms):
    if not isinstance(raw_terms, list) or not raw_terms:
        raise ValueError("polynomial atom requires a non-empty finite term list")
    combined = {}
    for term in raw_terms:
        if not isinstance(term, dict) or set(term) != {"coefficient", "exponents"}:
            raise ValueError("polynomial term must contain coefficient and exponents only")
        exponent = _normalize_exponents(term["exponents"])
        combined[exponent] = combined.get(exponent, Fraction(0)) + q(term["coefficient"])
    cleaned = [(exp, coeff) for exp, coeff in combined.items() if coeff != 0]
    if not cleaned:
        raise ValueError("zero polynomial is not a solid-classifying atom")
    cleaned.sort(key=lambda item: item[0])
    return tuple(cleaned)


def normalize_solid(node):
    if not isinstance(node, dict):
        raise TypeError("solid node must be an object")
    op = node.get("op")
    if op in {"poly_le", "poly_ge"}:
        if set(node) != {"op", "terms"}:
            raise ValueError("polynomial atom has unreviewed fields")
        return (op, normalize_terms(node["terms"]))
    if op in {"union", "intersection"}:
        if set(node) != {"op", "children"}:
            raise ValueError("boolean node has unreviewed fields")
        children = node["children"]
        if not isinstance(children, list) or len(children) < 2:
            raise ValueError(f"{op} requires at least two finite children")
        normalized = [normalize_solid(child) for child in children]
        normalized.sort(key=_canonical_node_bytes)
        return (op, tuple(normalized))
    if op == "difference":
        if set(node) != {"op", "left", "right"}:
            raise ValueError("difference node has unreviewed fields")
        return (op, normalize_solid(node["left"]), normalize_solid(node["right"]))
    if op == "complement":
        if set(node) != {"op", "child"}:
            raise ValueError("complement node has unreviewed fields")
        return (op, normalize_solid(node["child"]))
    raise ValueError("unsupported solid grammar; PB-007-03 remains fail-closed")


def _canonical_node_object(node):
    op = node[0]
    if op in {"poly_le", "poly_ge"}:
        return {
            "op": op,
            "terms": [
                {"coefficient": qtext(coeff), "exponents": list(exp)}
                for exp, coeff in node[1]
            ],
        }
    if op in {"union", "intersection"}:
        return {"op": op, "children": [_canonical_node_object(child) for child in node[1]]}
    if op == "difference":
        return {"op": op, "left": _canonical_node_object(node[1]), "right": _canonical_node_object(node[2])}
    if op == "complement":
        return {"op": op, "child": _canonical_node_object(node[1])}
    raise AssertionError(op)


def _canonical_node_bytes(node):
    return json.dumps(_canonical_node_object(node), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def normalize_source(source):
    if not isinstance(source, dict):
        raise TypeError("source descriptor must be an object")
    allowed = {
        "schema", "source_id", "role", "units", "frame_id", "bounds",
        "solid", "source_uncertainty",
    }
    unknown = set(source) - allowed
    if unknown:
        raise ValueError(f"unreviewed exact-source fields: {sorted(unknown)}")
    if source.get("schema") != SCHEMA:
        raise ValueError("unsupported exact source schema")
    source_id = _nonempty_text(source.get("source_id"), "source_id")
    role = source.get("role")
    if role not in ROLES:
        raise ValueError("source role must be stock, cutting or holder")
    units = _nonempty_text(source.get("units"), "units")
    frame_id = _nonempty_text(source.get("frame_id"), "frame_id")
    bounds = normalize_bounds(source.get("bounds"))
    solid = normalize_solid(source.get("solid"))
    if "source_uncertainty" not in source:
        raise ValueError("source uncertainty must be explicit and separate from nominal geometry")
    uncertainty = q(source["source_uncertainty"])
    if uncertainty < 0:
        raise ValueError("source uncertainty must be non-negative")
    return {
        "schema": SCHEMA,
        "source_id": source_id,
        "role": role,
        "units": units,
        "frame_id": frame_id,
        "bounds": bounds,
        "solid": solid,
        "source_uncertainty": uncertainty,
    }


def canonical_source_object(source):
    src = normalize_source(source)
    return {
        "schema": src["schema"],
        "source_id": src["source_id"],
        "role": src["role"],
        "units": src["units"],
        "frame_id": src["frame_id"],
        "bounds": {axis: [qtext(src["bounds"][axis][0]), qtext(src["bounds"][axis][1])] for axis in AXES},
        "solid": _canonical_node_object(src["solid"]),
        "source_uncertainty": qtext(src["source_uncertainty"]),
    }


def canonical_source_bytes(source) -> bytes:
    return json.dumps(canonical_source_object(source), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def source_sha256(source) -> str:
    return hashlib.sha256(canonical_source_bytes(source)).hexdigest()


def _point(point):
    if not isinstance(point, (list, tuple)) or len(point) != 3:
        raise ValueError("point must contain exact x/y/z")
    return tuple(q(value) for value in point)


def _poly_value(terms, point):
    x, y, z = point
    coords = (x, y, z)
    total = Fraction(0)
    for exponents, coefficient in terms:
        term = coefficient
        for coordinate, exponent in zip(coords, exponents):
            term *= coordinate ** exponent
        total += term
    return total


def _inside_node(node, point):
    op = node[0]
    if op == "poly_le":
        return _poly_value(node[1], point) <= 0
    if op == "poly_ge":
        return _poly_value(node[1], point) >= 0
    if op == "union":
        return any(_inside_node(child, point) for child in node[1])
    if op == "intersection":
        return all(_inside_node(child, point) for child in node[1])
    if op == "difference":
        return _inside_node(node[1], point) and not _inside_node(node[2], point)
    if op == "complement":
        return not _inside_node(node[1], point)
    raise AssertionError(op)


def _has_zero_atom(node, point):
    op = node[0]
    if op in {"poly_le", "poly_ge"}:
        return _poly_value(node[1], point) == 0
    if op in {"union", "intersection"}:
        return any(_has_zero_atom(child, point) for child in node[1])
    if op == "difference":
        return _has_zero_atom(node[1], point) or _has_zero_atom(node[2], point)
    if op == "complement":
        return _has_zero_atom(node[1], point)
    raise AssertionError(op)


def _inside_bounds(bounds, point):
    return all(bounds[axis][0] <= point[i] <= bounds[axis][1] for i, axis in enumerate(AXES))


def _on_bound(bounds, point):
    return any(point[i] in bounds[axis] for i, axis in enumerate(AXES))


def classify_nominal_point(source, point):
    """Classify exact nominal source membership without laundering source uncertainty.

    BOUNDARY_CANDIDATE is deliberately conservative: an exact atom/bounding equality
    is reported rather than claiming a topological boundary after Boolean cancellation.
    """
    src = normalize_source(source)
    p = _point(point)
    if not _inside_bounds(src["bounds"], p):
        return {
            "status": "EXACT_NOMINAL",
            "relation": "OUTSIDE",
            "source_id": src["source_id"],
            "source_sha256": source_sha256(source),
        }
    inside = _inside_node(src["solid"], p)
    if _on_bound(src["bounds"], p) or _has_zero_atom(src["solid"], p):
        relation = "BOUNDARY_CANDIDATE"
    else:
        relation = "INSIDE" if inside else "OUTSIDE"
    return {
        "status": "EXACT_NOMINAL",
        "relation": relation,
        "closed_predicate_membership": inside,
        "source_id": src["source_id"],
        "source_sha256": source_sha256(source),
    }


def classify_certifying_point(source, point):
    """Expose nominal exactness separately from nonzero source uncertainty."""
    src = normalize_source(source)
    nominal = classify_nominal_point(source, point)
    if src["source_uncertainty"] != 0:
        return {
            "status": "UNCERTIFIED_SOURCE",
            "reason": "NONZERO_SOURCE_UNCERTAINTY_REQUIRES_PROPAGATED_ENCLOSURE",
            "source_uncertainty": qtext(src["source_uncertainty"]),
            "nominal_relation": nominal["relation"],
            "source_id": src["source_id"],
            "source_sha256": nominal["source_sha256"],
            "is_exact_material_truth": False,
        }
    return nominal


def validate_tool_bundle(cutting_source, holder_source):
    cutter = normalize_source(cutting_source)
    holder = normalize_source(holder_source)
    if cutter["role"] != "cutting" or holder["role"] != "holder":
        raise ValueError("tool bundle must preserve distinct cutting and holder roles")
    if cutter["units"] != holder["units"] or cutter["frame_id"] != holder["frame_id"]:
        raise ValueError("cutting and holder sources require common explicit units/frame")
    if cutter["source_id"] == holder["source_id"]:
        raise ValueError("cutting and holder sources require distinct durable source identities")
    return {
        "status": "EXACT_NOMINAL_TOOL_BUNDLE",
        "cutting_sha256": source_sha256(cutting_source),
        "holder_sha256": source_sha256(holder_source),
        "access_certified": False,
    }


def classify_source_descriptor(descriptor):
    """Prospective dispatch boundary: exact codec or a typed PB-007-03 blocker."""
    if not isinstance(descriptor, dict):
        return {"status": "BLOCKED", "blocker": "PB-007-03", "reason": "MISSING_SOURCE_DESCRIPTOR"}
    if descriptor.get("schema") == SCHEMA:
        try:
            src = normalize_source(descriptor)
        except (TypeError, ValueError, ZeroDivisionError) as exc:
            return {"status": "SEMANTIC_BLOCKER", "reason": "INVALID_EXACT_SOURCE", "detail": str(exc)}
        return {
            "status": "EXACT_NOMINAL_SOURCE",
            "source_id": src["source_id"],
            "source_sha256": source_sha256(descriptor),
            "source_uncertainty": qtext(src["source_uncertainty"]),
            "certifying_exactness": src["source_uncertainty"] == 0,
        }
    opaque_kind = descriptor.get("format") or descriptor.get("representation") or descriptor.get("schema")
    return {
        "status": "BLOCKED",
        "blocker": "PB-007-03",
        "reason": "OPAQUE_OR_UNREVIEWED_IMPORT_REQUIRES_EXACT_SOURCE_LOWERING_OR_CERTIFIED_UNCERTAINTY_ROUTE",
        "opaque_kind": opaque_kind,
    }


def polynomial_atom(op, terms):
    return {"op": op, "terms": terms}


def linear_le(axis: int, coefficient, constant):
    """Return coefficient*coord + constant <= 0."""
    exp = [0, 0, 0]
    exp[axis] = 1
    return polynomial_atom("poly_le", [
        {"coefficient": coefficient, "exponents": exp},
        {"coefficient": constant, "exponents": [0, 0, 0]},
    ])


def box_solid(x0, x1, y0, y1, z0, z1):
    x0, x1, y0, y1, z0, z1 = map(q, (x0, x1, y0, y1, z0, z1))
    if not (x0 < x1 and y0 < y1 and z0 < z1):
        raise ValueError("box requires positive volume")
    return {
        "op": "intersection",
        "children": [
            linear_le(0, -1, x0), linear_le(0, 1, -x1),
            linear_le(1, -1, y0), linear_le(1, 1, -y1),
            linear_le(2, -1, z0), linear_le(2, 1, -z1),
        ],
    }


def unit_sphere_solid():
    return polynomial_atom("poly_le", [
        {"coefficient": "1", "exponents": [2, 0, 0]},
        {"coefficient": "1", "exponents": [0, 2, 0]},
        {"coefficient": "1", "exponents": [0, 0, 2]},
        {"coefficient": "-1", "exponents": [0, 0, 0]},
    ])
