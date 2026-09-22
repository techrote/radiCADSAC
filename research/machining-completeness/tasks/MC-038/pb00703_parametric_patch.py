#!/usr/bin/env python3
"""Exact-rational tensor-product parametric boundary patch codec for PB-007-03 v5.

This is a bounded exact nominal boundary-source language. It does not certify
trimmed shells, watertightness, orientation, inside/outside solid membership,
or importer/kernel validity.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json

SCHEMA = "radicadsac-exact-rational-parametric-patch/1.0"
ROLES = {"stock", "cutting", "holder"}


def q(value) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("exact rational authority must not be bool/float")
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


def _text(value, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _degree(value, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise TypeError(f"{name} must be a positive integer")
    return value


def _knots(raw, name: str):
    if not isinstance(raw, list) or len(raw) < 4:
        raise ValueError(f"{name} must be a finite knot vector")
    out = tuple(q(v) for v in raw)
    if any(a > b for a, b in zip(out, out[1:])):
        raise ValueError(f"{name} must be nondecreasing")
    return out


def _domain(raw, name: str):
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        raise ValueError(f"{name} must contain exact [lo,hi]")
    lo, hi = map(q, raw)
    if not lo < hi:
        raise ValueError(f"{name} must have positive extent")
    return (lo, hi)


def _point3(raw):
    if not isinstance(raw, (list, tuple)) or len(raw) != 3:
        raise ValueError("control point must contain exact x/y/z")
    return tuple(q(v) for v in raw)


def normalize_patch(source):
    if not isinstance(source, dict):
        raise TypeError("patch descriptor must be an object")
    allowed = {
        "schema", "source_id", "patch_id", "role", "units", "frame_id",
        "u_parameter_id", "v_parameter_id", "degree_u", "degree_v",
        "knots_u", "knots_v", "parameter_domain_u", "parameter_domain_v",
        "control_points", "weights", "source_uncertainty", "authority_kind",
    }
    unknown = set(source) - allowed
    if unknown:
        raise ValueError(f"unreviewed parametric-patch fields: {sorted(unknown)}")
    if source.get("schema") != SCHEMA:
        raise ValueError("unsupported parametric-patch schema")
    if source.get("authority_kind") != "BOUNDARY_PATCH_ONLY":
        raise ValueError("v5 authority_kind must be BOUNDARY_PATCH_ONLY")

    source_id = _text(source.get("source_id"), "source_id")
    patch_id = _text(source.get("patch_id"), "patch_id")
    role = source.get("role")
    if role not in ROLES:
        raise ValueError("role must be stock, cutting or holder")
    units = _text(source.get("units"), "units")
    frame_id = _text(source.get("frame_id"), "frame_id")
    u_parameter_id = _text(source.get("u_parameter_id"), "u_parameter_id")
    v_parameter_id = _text(source.get("v_parameter_id"), "v_parameter_id")
    if u_parameter_id == v_parameter_id:
        raise ValueError("u/v parameter identities must remain distinct")

    degree_u = _degree(source.get("degree_u"), "degree_u")
    degree_v = _degree(source.get("degree_v"), "degree_v")
    knots_u = _knots(source.get("knots_u"), "knots_u")
    knots_v = _knots(source.get("knots_v"), "knots_v")
    domain_u = _domain(source.get("parameter_domain_u"), "parameter_domain_u")
    domain_v = _domain(source.get("parameter_domain_v"), "parameter_domain_v")

    cps_raw = source.get("control_points")
    weights_raw = source.get("weights")
    if not isinstance(cps_raw, list) or not cps_raw or not isinstance(cps_raw[0], list) or not cps_raw[0]:
        raise ValueError("control_points must be a nonempty rectangular [u][v] grid")
    nu = len(cps_raw)
    nv = len(cps_raw[0])
    if any(not isinstance(row, list) or len(row) != nv for row in cps_raw):
        raise ValueError("control_points must be rectangular")
    if not isinstance(weights_raw, list) or len(weights_raw) != nu:
        raise ValueError("weights grid must match control_points")
    if any(not isinstance(row, list) or len(row) != nv for row in weights_raw):
        raise ValueError("weights grid must be rectangular and match control_points")

    control_points = tuple(tuple(_point3(p) for p in row) for row in cps_raw)
    weights = tuple(tuple(q(w) for w in row) for row in weights_raw)
    if any(w <= 0 for row in weights for w in row):
        raise ValueError("NURBS weights must be exact positive rationals")

    if len(knots_u) != nu + degree_u + 1:
        raise ValueError("knots_u/control_points/degree_u cardinality mismatch")
    if len(knots_v) != nv + degree_v + 1:
        raise ValueError("knots_v/control_points/degree_v cardinality mismatch")

    active_u = (knots_u[degree_u], knots_u[nu])
    active_v = (knots_v[degree_v], knots_v[nv])
    if not active_u[0] < active_u[1] or not active_v[0] < active_v[1]:
        raise ValueError("active knot domain must have positive extent")
    if domain_u != active_u or domain_v != active_v:
        raise ValueError("declared parameter domains must equal the exact active knot domains")

    if "source_uncertainty" not in source:
        raise ValueError("source_uncertainty must be explicit")
    uncertainty = q(source["source_uncertainty"])
    if uncertainty < 0:
        raise ValueError("source_uncertainty must be non-negative")

    return {
        "schema": SCHEMA,
        "source_id": source_id,
        "patch_id": patch_id,
        "role": role,
        "units": units,
        "frame_id": frame_id,
        "u_parameter_id": u_parameter_id,
        "v_parameter_id": v_parameter_id,
        "degree_u": degree_u,
        "degree_v": degree_v,
        "knots_u": knots_u,
        "knots_v": knots_v,
        "parameter_domain_u": domain_u,
        "parameter_domain_v": domain_v,
        "control_points": control_points,
        "weights": weights,
        "source_uncertainty": uncertainty,
        "authority_kind": "BOUNDARY_PATCH_ONLY",
    }


def canonical_source_object(source):
    p = normalize_patch(source)
    return {
        "schema": p["schema"],
        "source_id": p["source_id"],
        "patch_id": p["patch_id"],
        "role": p["role"],
        "units": p["units"],
        "frame_id": p["frame_id"],
        "u_parameter_id": p["u_parameter_id"],
        "v_parameter_id": p["v_parameter_id"],
        "degree_u": p["degree_u"],
        "degree_v": p["degree_v"],
        "knots_u": [qtext(v) for v in p["knots_u"]],
        "knots_v": [qtext(v) for v in p["knots_v"]],
        "parameter_domain_u": [qtext(v) for v in p["parameter_domain_u"]],
        "parameter_domain_v": [qtext(v) for v in p["parameter_domain_v"]],
        "control_points": [
            [[qtext(c) for c in point] for point in row]
            for row in p["control_points"]
        ],
        "weights": [[qtext(w) for w in row] for row in p["weights"]],
        "source_uncertainty": qtext(p["source_uncertainty"]),
        "authority_kind": p["authority_kind"],
    }


def canonical_source_bytes(source) -> bytes:
    return json.dumps(
        canonical_source_object(source),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def source_sha256(source) -> str:
    return hashlib.sha256(canonical_source_bytes(source)).hexdigest()


def _basis_vector(knots, degree: int, count: int, parameter: Fraction):
    lo, hi = knots[degree], knots[count]
    if parameter < lo or parameter > hi:
        raise ValueError("parameter lies outside exact active knot domain")
    if parameter == hi:
        out = [Fraction(0) for _ in range(count)]
        out[-1] = Fraction(1)
        return tuple(out)

    prev = [
        Fraction(1) if knots[i] <= parameter < knots[i + 1] else Fraction(0)
        for i in range(len(knots) - 1)
    ]
    for d in range(1, degree + 1):
        cur = []
        limit = len(knots) - d - 1
        for i in range(limit):
            value = Fraction(0)
            left_den = knots[i + d] - knots[i]
            if left_den != 0:
                value += (parameter - knots[i]) / left_den * prev[i]
            right_den = knots[i + d + 1] - knots[i + 1]
            if right_den != 0:
                value += (knots[i + d + 1] - parameter) / right_den * prev[i + 1]
            cur.append(value)
        prev = cur
    out = tuple(prev[:count])
    if len(out) != count or sum(out, Fraction(0)) != 1:
        raise AssertionError("exact basis partition-of-unity failure")
    return out


def evaluate_patch(source, u, v):
    p = normalize_patch(source)
    u = q(u)
    v = q(v)
    bu = _basis_vector(p["knots_u"], p["degree_u"], len(p["control_points"]), u)
    bv = _basis_vector(p["knots_v"], p["degree_v"], len(p["control_points"][0]), v)

    numerator = [Fraction(0), Fraction(0), Fraction(0)]
    denominator = Fraction(0)
    for i, ui in enumerate(bu):
        if ui == 0:
            continue
        for j, vj in enumerate(bv):
            if vj == 0:
                continue
            coeff = ui * vj * p["weights"][i][j]
            denominator += coeff
            point = p["control_points"][i][j]
            for axis in range(3):
                numerator[axis] += coeff * point[axis]
    if denominator <= 0:
        raise AssertionError("positive-weight NURBS denominator must remain positive")
    point = tuple(value / denominator for value in numerator)
    status = "EXACT_NOMINAL_BOUNDARY_POINT" if p["source_uncertainty"] == 0 else "UNCERTIFIED_SOURCE"
    return {
        "status": status,
        "point": [qtext(value) for value in point],
        "u": qtext(u),
        "v": qtext(v),
        "source_id": p["source_id"],
        "patch_id": p["patch_id"],
        "source_sha256": source_sha256(source),
        "source_uncertainty": qtext(p["source_uncertainty"]),
        "solid_membership_certified": False,
        "trim_certified": False,
        "shell_certified": False,
    }


def classify_source_descriptor(descriptor):
    if not isinstance(descriptor, dict):
        return {
            "status": "BLOCKED",
            "blocker": "PB-007-03",
            "reason": "MISSING_SOURCE_DESCRIPTOR",
        }
    if descriptor.get("schema") == SCHEMA:
        try:
            p = normalize_patch(descriptor)
        except (TypeError, ValueError, ZeroDivisionError) as exc:
            return {
                "status": "SEMANTIC_BLOCKER",
                "blocker": "PB-007-03",
                "reason": "INVALID_EXACT_PARAMETRIC_PATCH",
                "detail": str(exc),
            }
        return {
            "status": "EXACT_NOMINAL_BOUNDARY_SOURCE",
            "source_id": p["source_id"],
            "patch_id": p["patch_id"],
            "source_sha256": source_sha256(descriptor),
            "source_uncertainty": qtext(p["source_uncertainty"]),
            "certifying_exact_boundary": p["source_uncertainty"] == 0,
            "solid_membership_certified": False,
            "requires_independent_trim_shell_membership_authority": True,
        }
    opaque_kind = descriptor.get("format") or descriptor.get("representation") or descriptor.get("schema")
    return {
        "status": "BLOCKED",
        "blocker": "PB-007-03",
        "reason": "OPAQUE_OR_UNREVIEWED_FREEFORM_SOURCE_REQUIRES_EXACT_LOWERING_OR_CERTIFIED_SOURCE_AUTHORITY",
        "opaque_kind": opaque_kind,
    }


def request_solid_membership(source, point, *, shell_certificate=None):
    normalize_patch(source)
    if not isinstance(point, (list, tuple)) or len(point) != 3:
        raise ValueError("solid-membership query point must contain x/y/z")
    tuple(q(v) for v in point)
    return {
        "status": "BLOCKED",
        "blocker": "PB-007-03",
        "reason": "EXACT_PATCH_BOUNDARY_IS_NOT_INDEPENDENTLY_CERTIFIED_CLOSED_TRIMMED_SOLID_MEMBERSHIP",
        "shell_certificate_consumed": False,
        "solid_membership_certified": False,
    }
