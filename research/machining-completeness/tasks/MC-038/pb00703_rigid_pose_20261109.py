#!/usr/bin/env python3
"""PB-007-03: exact rational proper-rigid setup pushforward of any v4 source.

A finite polynomial/Boolean source P(u), u=R^T(X-t), becomes P(R^T(X-t)).
This constructs *nominal source membership*, not access, native or STEP truth.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

TASK = Path(__file__).resolve().parent
sys.path.insert(0, str(TASK))
import pb00703_source_codec as v4

AXES = ("x", "y", "z")
MAX_SOURCE_BYTES = 131072
MAX_NODES = 1024
MAX_INPUT_TERMS = 4096
MAX_OUTPUT_TERMS = 8192
MAX_DEGREE = 12
MAX_RATIONAL_BITS = 512
MAX_OUTPUT_BYTES = 1048576


class OpenSourceBudget(Exception):
    """Finite execution bound; PB-007-03 remains OPEN for this valid source."""


def _budget(test, message):
    if not test:
        raise OpenSourceBudget(message)


def _bits(v):
    _budget(v.numerator.bit_length() <= MAX_RATIONAL_BITS and
            v.denominator.bit_length() <= MAX_RATIONAL_BITS,
            "RATIONAL_BIT_BUDGET")
    return v


def _q(v):
    return _bits(v4.q(v))


def _qstr(v):
    return v4.qtext(_bits(v))


def _sha(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"),
                                  ensure_ascii=False).encode("utf-8")).hexdigest()


def _parse_pose(source, pose):
    if not isinstance(pose, dict) or set(pose) != {"matrix", "translation", "source_frame", "target_frame"}:
        raise ValueError("pose must bind exactly matrix/translation/source_frame/target_frame")
    if pose["source_frame"] != source["frame_id"]:
        raise ValueError("source_frame does not match exact source")
    if not isinstance(pose["target_frame"], str) or not pose["target_frame"].strip():
        raise ValueError("target frame is required")
    raw = pose["matrix"]
    if not isinstance(raw, list) or len(raw) != 3 or any(not isinstance(row, list) or len(row) != 3 for row in raw):
        raise ValueError("rotation must be 3x3")
    R = tuple(tuple(_q(x) for x in row) for row in raw)
    tr = pose["translation"]
    if not isinstance(tr, list) or len(tr) != 3:
        raise ValueError("translation must be a rational triple")
    t = tuple(_q(x) for x in tr)
    for i in range(3):
        for j in range(3):
            dot = sum((R[k][i] * R[k][j] for k in range(3)), Fraction(0))
            if dot != (1 if i == j else 0):
                raise ValueError("not an exact orthogonal rigid rotation")
    det = (R[0][0]*(R[1][1]*R[2][2]-R[1][2]*R[2][1])
           - R[0][1]*(R[1][0]*R[2][2]-R[1][2]*R[2][0])
           + R[0][2]*(R[1][0]*R[2][1]-R[1][1]*R[2][0]))
    if det != 1:
        raise ValueError("pose is not a proper right-handed rigid rotation")
    return R, t


def _sum(a, b):
    result = a.copy()
    for exp, coeff in b.items():
        result[exp] = _bits(result.get(exp, Fraction(0)) + coeff)
        if not result[exp]:
            del result[exp]
    _budget(len(result) <= MAX_OUTPUT_TERMS, "TERM_BUDGET")
    return result


def _mul(a, b):
    result = {}
    _budget(len(a) * len(b) <= MAX_OUTPUT_TERMS * 8, "EXPANSION_BUDGET")
    for ea, ca in a.items():
        for eb, cb in b.items():
            ex = tuple(ea[i] + eb[i] for i in range(3))
            _budget(sum(ex) <= MAX_DEGREE, "DEGREE_BUDGET")
            result[ex] = _bits(result.get(ex, Fraction(0)) + ca * cb)
    result = {k: v for k, v in result.items() if v}
    _budget(len(result) <= MAX_OUTPUT_TERMS, "TERM_BUDGET")
    return result


def _pow(form, exponent):
    result = {(0, 0, 0): Fraction(1)}
    for _ in range(exponent):
        result = _mul(result, form)
    return result


def _pullback_terms(terms, forms):
    result = {}
    for exponents, coefficient in terms:
        _budget(sum(exponents) <= MAX_DEGREE, "DEGREE_BUDGET")
        term = {(0, 0, 0): _bits(coefficient)}
        for axis in range(3):
            if exponents[axis]:
                term = _mul(term, _pow(forms[axis], exponents[axis]))
        result = _sum(result, term)
    if not result:
        raise ValueError("pullback of nonzero polynomial unexpectedly zero")
    return [{"coefficient": _qstr(coeff), "exponents": list(exp)}
            for exp, coeff in sorted(result.items())]


def _pullback_node(node, forms, tally):
    tally[0] += 1
    _budget(tally[0] <= MAX_NODES, "NODE_BUDGET")
    op = node[0]
    if op in {"poly_le", "poly_ge"}:
        tally[1] += len(node[1])
        _budget(tally[1] <= MAX_INPUT_TERMS, "INPUT_TERM_BUDGET")
        return {"op": op, "terms": _pullback_terms(node[1], forms)}
    if op in {"union", "intersection"}:
        return {"op": op, "children": [_pullback_node(c, forms, tally) for c in node[1]]}
    if op == "difference":
        return {"op": op, "left": _pullback_node(node[1], forms, tally),
                "right": _pullback_node(node[2], forms, tally)}
    if op == "complement":
        return {"op": op, "child": _pullback_node(node[1], forms, tally)}
    raise AssertionError(op)


def lower_exact_source(source, pose, instance_id):
    """Return source and SHA-bound derivation receipt; never change input source.

    The transformed bounding box is conservative *only as source extent*:
    the full pulled-back polynomial/Boolean solid, not its AABB, is material truth.
    """
    if not isinstance(instance_id, str) or not instance_id.strip():
        raise ValueError("distinct durable instance_id required")
    if not isinstance(source, dict):
        raise TypeError("source must be an exact source descriptor")
    _budget(len(json.dumps(source, sort_keys=True, default=str)) <= MAX_SOURCE_BYTES,
            "SOURCE_BYTE_BUDGET")
    src = v4.normalize_source(source)
    if instance_id == src["source_id"]:
        raise ValueError("transformed instance must have a distinct durable source identity")
    R, t = _parse_pose(src, pose)
    # local coordinate u_i = sum_j R[j][i] * (world_j - t_j).
    forms = []
    for i in range(3):
        f = {(0, 0, 0): _bits(-sum((R[j][i]*t[j] for j in range(3)), Fraction(0)))}
        for j in range(3):
            if R[j][i]:
                exp = tuple(1 if k == j else 0 for k in range(3))
                f[exp] = _bits(R[j][i])
        forms.append({k: v for k, v in f.items() if v})
    bounds = {}
    for i, axis in enumerate(AXES):
        lo, hi = t[i], t[i]
        for j, old_axis in enumerate(AXES):
            a, b = src["bounds"][old_axis]
            coeff = R[i][j]
            lo += coeff * (a if coeff >= 0 else b)
            hi += coeff * (b if coeff >= 0 else a)
        bounds[axis] = [_qstr(lo), _qstr(hi)]
    out = {
        "schema": v4.SCHEMA,
        "source_id": instance_id,
        "role": src["role"],
        "units": src["units"],
        "frame_id": pose["target_frame"],
        "bounds": bounds,
        "solid": _pullback_node(src["solid"], forms, [0, 0]),
        "source_uncertainty": _qstr(src["source_uncertainty"]),
    }
    canon = v4.canonical_source_object(out)
    _budget(len(v4.canonical_source_bytes(canon)) <= MAX_OUTPUT_BYTES, "OUTPUT_BYTE_BUDGET")
    pose_canonical = {
        "source_frame": src["frame_id"], "target_frame": pose["target_frame"],
        "matrix": [[_qstr(x) for x in row] for row in R],
        "translation": [_qstr(x) for x in t],
    }
    receipt = {
        "schema": "radicadsac-pb00703-rigid-pose/1.0",
        "method": "EXACT_POLYNOMIAL_PULLBACK_RIGHT_HANDED_RATIONAL_RIGID",
        "original_sha256": v4.source_sha256(source),
        "output_sha256": v4.source_sha256(canon),
        "original_source_id": src["source_id"],
        "instance_id": instance_id,
        "role": src["role"],
        "units": src["units"],
        "source_uncertainty": _qstr(src["source_uncertainty"]),
        "pose": pose_canonical,
        "pose_sha256": _sha(pose_canonical),
        "access_certified": False,
        "native_or_step_certified": False,
        "pb00703_discharge": False,
    }
    return canon, receipt


def verify_exact_receipt(source, pose, instance_id, supplied_output, supplied_receipt):
    """Replay all source/pose authority; never trust caller's cached receipt."""
    output, receipt = lower_exact_source(source, pose, instance_id)
    if v4.canonical_source_bytes(supplied_output) != v4.canonical_source_bytes(output):
        raise ValueError("output AST/bounds/source identity changed")
    if supplied_receipt != receipt:
        raise ValueError("source/pose/provenance receipt changed")
    return True


def attempt(source, pose, instance_id):
    """Typed bounded source dispatch; budget refusal is OPEN, not invalid machining."""
    try:
        out, rec = lower_exact_source(source, pose, instance_id)
    except OpenSourceBudget as ex:
        return {"status": "BLOCKED", "blocker": "PB-007-03",
                "reason": "RESOURCE_BUDGET_OPEN", "detail": str(ex)}
    except (ValueError, TypeError, ZeroDivisionError, OverflowError, RecursionError) as ex:
        return {"status": "SEMANTIC_BLOCKER", "reason": "INVALID_OR_UNSUPPORTED_EXACT_POSE",
                "detail": str(ex)}
    return {"status": "EXACT_NOMINAL_SOURCE", "source": out, "receipt": rec,
            "certifying_exactness": out["source_uncertainty"] == "0/1"}


def world_to_local(pose, point):
    """Exact inverse for independent source-domain controls."""
    R, t = _parse_pose({"frame_id": pose["source_frame"]}, pose)
    x = tuple(_q(v) for v in point)
    if len(x) != 3:
        raise ValueError("world point must be a triple")
    return tuple(sum((R[j][i] * (x[j] - t[j]) for j in range(3)), Fraction(0))
                 for i in range(3))


if __name__ == "__main__":
    if "--contract" in sys.argv:
        assert v4.SCHEMA == "radicadsac-exact-semialgebraic-source/1.0"
        assert MAX_DEGREE > 0 and MAX_INPUT_TERMS > 0
        print("PB-007-03 rigid-pose exact-source constructor contract PASS")
    else:
        raise SystemExit("use --contract; run test_pb00703_rigid_pose_20261109.py --self-test")
