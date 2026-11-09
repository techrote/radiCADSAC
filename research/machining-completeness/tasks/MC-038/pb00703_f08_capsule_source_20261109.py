#!/usr/bin/env python3
"""PB-007-03: exact F08 curved form-tool/stock-source lowerer (bounded, research-only).

Converts rational disk paths, rather than bounding boxes, to the accepted v4
finite semialgebraic solid AST. Each original F08 journal operation remains a
separately bound cutting source. No physical holder/access or native claim.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

PB = "PB-007-03"
FIXTURE_BLOB = "8bb04fd5c643d02c42d2b58e49192ddb346b5b3f"
FIXTURE_PATH = "research/machining-completeness/tasks/MC-012/physical-corpus-f05-f08-v1.json"
SOURCE_SCHEMA = "radicadsac-exact-semialgebraic-source/1.0"
MAX_SEGMENTS = 64
MAX_AUTHORITY_BITS = 1024
MAX_FIXTURE_BYTES = 131072
E0 = (0, 0, 0)
EX = (1, 0, 0)
EY = (0, 1, 0)
EZ = (0, 0, 1)


class OpenSource(Exception):
    """Valid or possibly valid admitted source whose bounded route is not proved."""


class InvalidSource(ValueError):
    """Malformed exact source, as opposed to an uncovered physically valid case."""


def q(value):
    if isinstance(value, bool) or isinstance(value, float):
        raise InvalidSource("binary float/bool cannot carry exact source authority")
    if not isinstance(value, (int, str, Fraction)):
        raise InvalidSource("unsupported rational authority token")
    try:
        v = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise InvalidSource("malformed rational") from exc
    if max(v.numerator.bit_length(), v.denominator.bit_length()) > MAX_AUTHORITY_BITS:
        raise OpenSource("PB-007-03: exact coefficient/input budget; source stays OPEN")
    return v


def qstr(v):
    v = q(v)
    return f"{v.numerator}/{v.denominator}"


def atom(p):
    p = {ex: q(c) for ex, c in p.items() if c}
    if not p:
        raise OpenSource("PB-007-03: identically zero atom needs a separate equality route")
    return {"op": "poly_le", "terms": [
        {"coefficient": qstr(c), "exponents": list(ex)} for ex, c in sorted(p.items())
    ]}


def const(v):
    return {E0: q(v)} if q(v) else {}


def axis(ex):
    return {ex: Fraction(1)}


def add(*parts):
    out = {}
    for p in parts:
        for e, c in p.items():
            out[e] = out.get(e, Fraction()) + c
    return {e: q(c) for e, c in out.items() if c}


def neg(p):
    return {e: q(-c) for e, c in p.items()}


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    out = {}
    for e, c in a.items():
        for f, d in b.items():
            power = tuple(x + y for x, y in zip(e, f))
            if sum(power) > 2:
                raise OpenSource("PB-007-03: degree above proved quadratic route")
            out[power] = out.get(power, Fraction()) + c * d
    return {e: q(c) for e, c in out.items() if c}


def scale(p, c):
    return {e: q(v * q(c)) for e, v in p.items() if v * q(c)}


def sq(p):
    return mul(p, p)


def both(*children):
    return {"op": "intersection", "children": list(children)}


def either(*children):
    return {"op": "union", "children": list(children)}


def le(p):
    return atom(p)


def ge(p):
    return atom(neg(p))


def _point2(pt):
    if not isinstance(pt, (list, tuple)) or len(pt) != 2:
        raise InvalidSource("XY source point must have two exact coordinates")
    return tuple(q(x) for x in pt)


def _interval(interval):
    if not isinstance(interval, (list, tuple)) or len(interval) != 2:
        raise InvalidSource("Z interval requires two exact endpoints")
    a, b = map(q, interval)
    if a == b:
        raise OpenSource("PB-007-03: zero-thickness cutting support is admitted but not lowered")
    return min(a, b), max(a, b)


def xy_disk(center, radius):
    x, y = _point2(center)
    r = q(radius)
    if r < 0:
        raise InvalidSource("negative cutting radius")
    if r == 0:
        raise OpenSource("PB-007-03: radius-zero degeneracy needs explicit solid semantics")
    return le(sub(add(sq(sub(axis(EX), const(x))), sq(sub(axis(EY), const(y)))), const(r * r)))


def capsule_xy_segment(a, b, radius):
    """Exact closed swept disk for a rational planar line segment.

    For v=b-a and u=(p-a)·v, distance² is |p-a|² for u<=0,
    |p-b|² for u>=|v|², and |p-a|²-u²/|v|² otherwise.
    Multiplication by strictly positive |v|² retains exact order.
    """
    ax, ay = _point2(a)
    bx, by = _point2(b)
    r = q(radius)
    if r < 0:
        raise InvalidSource("negative cutting radius")
    if r == 0:
        raise OpenSource("PB-007-03: zero-radius sweep requires a separate degenerate route")
    dx, dy = bx - ax, by - ay
    length2 = dx * dx + dy * dy
    if not length2:
        return xy_disk((ax, ay), r)
    px, py = sub(axis(EX), const(ax)), sub(axis(EY), const(ay))
    u = add(scale(px, dx), scale(py, dy))
    ra = sub(add(sq(px), sq(py)), const(r * r))
    rb = sub(add(sq(sub(axis(EX), const(bx))), sq(sub(axis(EY), const(by)))), const(r * r))
    mid = sub(scale(ra, length2), sq(u))
    return either(
        both(le(u), le(ra)),
        both(ge(sub(u, const(length2))), le(rb)),
        both(ge(u), le(sub(u, const(length2))), le(mid)),
    )


def swept_disk_path(path, radius, z_interval):
    if not isinstance(path, (list, tuple)) or len(path) < 2:
        raise InvalidSource("source path requires two or more actual ordered points")
    if len(path) - 1 > MAX_SEGMENTS:
        raise OpenSource("PB-007-03: finite segment budget exceeded; no source exclusion")
    points = [_point2(pt) for pt in path]
    lo, hi = _interval(z_interval)
    r = q(radius)
    segments = [capsule_xy_segment(a, b, r) for a, b in zip(points, points[1:])]
    region = segments[0] if len(segments) == 1 else either(*segments)
    solid = both(ge(sub(axis(EZ), const(lo))), le(sub(axis(EZ), const(hi))), region)
    bounds = {
        "x": [min(p[0] for p in points) - r, max(p[0] for p in points) + r],
        "y": [min(p[1] for p in points) - r, max(p[1] for p in points) + r],
        "z": [lo, hi],
    }
    return solid, bounds


def make_source(source_id, solid, bounds, *, units="mm", frame_id="F08:S-F08:common", uncertainty="0"):
    if not isinstance(source_id, str) or not source_id or not isinstance(units, str) or not units or not isinstance(frame_id, str) or not frame_id:
        raise InvalidSource("missing source/units/frame authority")
    return {
        "schema": SOURCE_SCHEMA, "source_id": source_id, "role": "cutting",
        "units": units, "frame_id": frame_id,
        "bounds": {axis: [qstr(v) for v in bounds[axis]] for axis in ("x", "y", "z")},
        "solid": solid, "source_uncertainty": qstr(uncertainty),
    }


def lower_f08_operations(fixture, *, provenance=FIXTURE_BLOB):
    """Derive *two distinct* original journal cutting sources; never fuse operations."""
    if not isinstance(fixture, dict) or fixture.get("schema") != "radicadsac-mc-physical-corpus/1.0" or fixture.get("task") != "MC-012":
        raise InvalidSource("unexpected original fixture schema/task")
    found = [f for f in fixture.get("families", []) if f.get("id") == "F08"]
    if len(found) != 1:
        raise InvalidSource("missing or duplicate original F08 family")
    f08 = found[0]
    if f08.get("machine") != "mill" or f08.get("state") != "BUILT" or f08.get("stock", {}).get("units") != "mm":
        raise InvalidSource("F08 physical source authority drift")
    ops = f08.get("operations")
    if not isinstance(ops, list) or len(ops) != 2 or {o.get("id") for o in ops} != {"F08-ACCESS", "F08-TSLOT"}:
        raise InvalidSource("F08 original operation identity/order or cardinality drift")
    if [o["id"] for o in ops] != ["F08-ACCESS", "F08-TSLOT"]:
        raise InvalidSource("reordered journal operations cannot be silently canonicalized")
    access, slot = ops
    if access.get("kind") != "starter_pocket" or access.get("axis") != "z" or slot.get("kind") != "t_slot_form_sweep":
        raise OpenSource("PB-007-03: changed physical constructor needs reviewed lowering")
    head, neck = q(slot["head_radius"]), q(slot["neck_radius"])
    opening = q(access["radius"])
    if head <= neck or neck <= 0 or opening <= 0:
        raise OpenSource("PB-007-03: unsupported form-tool ordering/degeneracy")
    # Only a fixture-specific insertion margin, not holder/fixture/machine access proof.
    radial_margin = opening - head
    if radial_margin < 0:
        raise OpenSource("PB-007-03: insertion through opening not established")
    access_solid, access_bounds = swept_disk_path([access["center"], access["center"]], opening, access["axial_interval"])
    head_solid, head_bounds = swept_disk_path(slot["path_xy"], head, slot["head_z"])
    neck_solid, neck_bounds = swept_disk_path(slot["path_xy"], neck, slot["neck_z"])
    combined_bounds = {axis: [
        min(q(b[axis][0]) for b in (head_bounds, neck_bounds)),
        max(q(b[axis][1]) for b in (head_bounds, neck_bounds)),
    ] for axis in ("x", "y", "z")}
    return {
        "F08-ACCESS": make_source(f"MC-012:F08-ACCESS:{provenance}", access_solid, access_bounds),
        "F08-TSLOT": make_source(f"MC-012:F08-TSLOT:{provenance}", either(head_solid, neck_solid), combined_bounds),
    }, radial_margin


def load_original_f08(root: Path):
    path = root / FIXTURE_PATH
    raw = path.read_bytes()
    if len(raw) > MAX_FIXTURE_BYTES:
        raise OpenSource("PB-007-03: original fixture byte budget; no silent truncation")
    blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    if blob != FIXTURE_BLOB:
        raise InvalidSource("original fixture Git blob SHA differs from reviewed authority")
    fixture = json.loads(raw)
    return fixture, *lower_f08_operations(fixture)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--contract", action="store_true")
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[4])
    args = p.parse_args()
    if not args.contract:
        p.error("only --contract is supported; outputs are not native geometry")
    fixture, sources, margin = load_original_f08(args.root)
    assert margin == Fraction(1, 2)
    print(json.dumps({"result": "EXACT_NOMINAL_BOUNDED_SUBROUTE", "source_ids": list(sources),
                      "radial_margin": qstr(margin), "PB-007-03": "OPEN",
                      "holder_access_certified": False, "native_or_STEP": False}, sort_keys=True))
