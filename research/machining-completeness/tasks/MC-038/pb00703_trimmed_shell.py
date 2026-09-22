#!/usr/bin/env python3
"""Exact-rational trimmed convex shell certificate route for PB-007-03 v6.

This is deliberately bounded. It consumes v5 exact-rational parametric
boundary patches only when they reduce to affine bilinear planar patches with
zero source uncertainty. It then validates exact rational convex trim loops,
closed opposite-oriented seams, genus-0 incidence, outward orientation and a
convex half-space witness. It is not authority for arbitrary NURBS/trimmed
B-reps, opaque STEP imports, non-convex shells, or the full PB-007-03 domain.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json

import pb00703_parametric_patch as patch

SCHEMA = "radicadsac-exact-rational-trimmed-convex-shell/1.0"
AUTHORITY_KIND = "CERTIFIED_TRIMMED_CONVEX_SHELL"


def q(value) -> Fraction:
    return patch.q(value)


def qtext(value) -> str:
    return patch.qtext(value)


def _text(value, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _point2(raw, name="point"):
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        raise ValueError(f"{name} must contain exact u/v")
    return (q(raw[0]), q(raw[1]))


def _point3(raw, name="point"):
    if not isinstance(raw, (list, tuple)) or len(raw) != 3:
        raise ValueError(f"{name} must contain exact x/y/z")
    return (q(raw[0]), q(raw[1]), q(raw[2]))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _dot(a, b):
    return sum((x * y for x, y in zip(a, b)), Fraction(0))


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _cross2(a, b, c):
    ab = _sub(b, a)
    bc = _sub(c, b)
    return ab[0] * bc[1] - ab[1] * bc[0]


def _canonical_point3(p):
    return tuple(qtext(v) for v in p)


def _canonical_edge(a, b):
    aa, bb = _canonical_point3(a), _canonical_point3(b)
    return (aa, bb) if aa < bb else (bb, aa)


def _patch_affine_data(descriptor):
    p = patch.normalize_patch(descriptor)
    if p["source_uncertainty"] != 0:
        raise ValueError("bounded shell authority requires zero source_uncertainty")
    if p["degree_u"] != 1 or p["degree_v"] != 1:
        raise ValueError("bounded shell route requires degree-1 x degree-1 patches")
    if len(p["control_points"]) != 2 or len(p["control_points"][0]) != 2:
        raise ValueError("bounded shell route requires a 2x2 control net")
    weights = [w for row in p["weights"] for w in row]
    if any(w != weights[0] for w in weights[1:]):
        raise ValueError("bounded shell route requires equal weights (affine patch)")
    cp00 = p["control_points"][0][0]
    cp01 = p["control_points"][0][1]
    cp10 = p["control_points"][1][0]
    cp11 = p["control_points"][1][1]
    expected11 = tuple(cp10[i] + cp01[i] - cp00[i] for i in range(3))
    if cp11 != expected11:
        raise ValueError("bilinear patch is not affine-planar/parallelogram authority")
    normal = _cross(_sub(cp10, cp00), _sub(cp01, cp00))
    if normal == (Fraction(0), Fraction(0), Fraction(0)):
        raise ValueError("affine patch must have nonzero exact area")
    return p


def _normalize_trim(face, p):
    raw = face.get("trim_uv")
    if not isinstance(raw, list) or len(raw) < 3:
        raise ValueError("trim_uv must be a convex polygon with at least three vertices")
    uv = tuple(_point2(v, "trim vertex") for v in raw)
    if len(set(uv)) != len(uv):
        raise ValueError("trim_uv must not repeat vertices")
    ulo, uhi = p["parameter_domain_u"]
    vlo, vhi = p["parameter_domain_v"]
    if any(not (ulo <= u <= uhi and vlo <= v <= vhi) for u, v in uv):
        raise ValueError("trim vertex lies outside exact active parameter domain")
    turns = [_cross2(uv[i], uv[(i + 1) % len(uv)], uv[(i + 2) % len(uv)]) for i in range(len(uv))]
    if any(t == 0 for t in turns):
        raise ValueError("trim polygon must be strictly convex with no zero-area turn")
    sign = turns[0] > 0
    if any((t > 0) != sign for t in turns):
        raise ValueError("trim polygon must be simple and strictly convex")
    return uv


def _evaluate_trim(descriptor, uv):
    out = []
    for u, v in uv:
        result = patch.evaluate_patch(descriptor, u, v)
        if result["status"] != "EXACT_NOMINAL_BOUNDARY_POINT":
            raise ValueError("trim mapping requires exact nominal zero-uncertainty patch points")
        out.append(tuple(q(c) for c in result["point"]))
    if len(set(out)) != len(out):
        raise ValueError("mapped trim polygon degenerates in 3D")
    return tuple(out)


def _polygon_normal(vertices):
    for i in range(len(vertices)):
        a, b, c = vertices[i], vertices[(i + 1) % len(vertices)], vertices[(i + 2) % len(vertices)]
        n = _cross(_sub(b, a), _sub(c, b))
        if n != (Fraction(0), Fraction(0), Fraction(0)):
            for v in vertices:
                if _dot(n, _sub(v, a)) != 0:
                    raise ValueError("mapped trim vertices are not exactly planar")
            return n
    raise ValueError("mapped trim polygon has zero exact area")


def normalize_shell(source):
    if not isinstance(source, dict):
        raise TypeError("shell descriptor must be an object")
    allowed = {
        "schema", "authority_kind", "shell_id", "source_id", "role", "units", "frame_id",
        "revision_id", "configuration_id", "interior_witness", "faces",
    }
    unknown = set(source) - allowed
    if unknown:
        raise ValueError(f"unreviewed shell fields: {sorted(unknown)}")
    if source.get("schema") != SCHEMA:
        raise ValueError("unsupported trimmed-shell schema")
    if source.get("authority_kind") != AUTHORITY_KIND:
        raise ValueError("authority_kind must identify the bounded certified shell route")
    shell_id = _text(source.get("shell_id"), "shell_id")
    source_id = _text(source.get("source_id"), "source_id")
    role = source.get("role")
    if role not in patch.ROLES:
        raise ValueError("role must be stock, cutting or holder")
    units = _text(source.get("units"), "units")
    frame_id = _text(source.get("frame_id"), "frame_id")
    revision_id = _text(source.get("revision_id"), "revision_id")
    configuration_id = _text(source.get("configuration_id"), "configuration_id")
    interior = _point3(source.get("interior_witness"), "interior_witness")

    faces_raw = source.get("faces")
    if not isinstance(faces_raw, list) or len(faces_raw) < 4:
        raise ValueError("closed shell route requires at least four faces")
    face_ids = set()
    faces = []
    for raw in faces_raw:
        if not isinstance(raw, dict):
            raise TypeError("face descriptor must be an object")
        if set(raw) != {"face_id", "patch", "patch_sha256", "trim_uv"}:
            raise ValueError("face descriptor has missing or unreviewed authority fields")
        face_id = _text(raw["face_id"], "face_id")
        if face_id in face_ids:
            raise ValueError("duplicate face_id")
        face_ids.add(face_id)
        descriptor = raw["patch"]
        p = _patch_affine_data(descriptor)
        expected_hash = patch.source_sha256(descriptor)
        if raw["patch_sha256"] != expected_hash:
            raise ValueError("stale or forged v5 patch_sha256 binding")
        for key, expected in (("source_id", source_id), ("role", role), ("units", units), ("frame_id", frame_id)):
            if p[key] != expected:
                raise ValueError(f"face patch {key} does not match shell authority")
        uv = _normalize_trim(raw, p)
        vertices = _evaluate_trim(descriptor, uv)
        normal = _polygon_normal(vertices)
        offset = _dot(normal, vertices[0])
        if _dot(normal, interior) - offset >= 0:
            raise ValueError("face orientation is not outward relative to strict interior witness")
        faces.append({
            "face_id": face_id,
            "patch": descriptor,
            "patch_sha256": expected_hash,
            "trim_uv": uv,
            "vertices": vertices,
            "normal": normal,
            "offset": offset,
        })

    all_vertices = {v for face in faces for v in face["vertices"]}
    if len(all_vertices) < 4:
        raise ValueError("shell lacks enough distinct vertices for positive volume")

    edge_incidence = {}
    face_adjacency = {f["face_id"]: set() for f in faces}
    for face in faces:
        vs = face["vertices"]
        for i, a in enumerate(vs):
            b = vs[(i + 1) % len(vs)]
            if a == b:
                raise ValueError("zero-length trim seam")
            edge_incidence.setdefault(_canonical_edge(a, b), []).append((face["face_id"], a, b))
    for occurrences in edge_incidence.values():
        if len(occurrences) != 2:
            raise ValueError("every geometric trim seam must have exactly two face incidences")
        (f1, a1, b1), (f2, a2, b2) = occurrences
        if f1 == f2:
            raise ValueError("seam cannot close against the same face")
        if not (a1 == b2 and b1 == a2):
            raise ValueError("paired seam incidences must have exact opposite orientation")
        face_adjacency[f1].add(f2)
        face_adjacency[f2].add(f1)

    seen = set()
    stack = [faces[0]["face_id"]]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(face_adjacency[current] - seen)
    if seen != set(face_adjacency):
        raise ValueError("shell face incidence must be connected")

    if len(all_vertices) - len(edge_incidence) + len(faces) != 2:
        raise ValueError("bounded route requires closed orientable genus-0 shell incidence (Euler V-E+F=2)")

    for face in faces:
        n, d = face["normal"], face["offset"]
        if _dot(n, interior) - d >= 0:
            raise ValueError("interior witness must be strictly inside every exact face half-space")
        for vertex in all_vertices:
            if _dot(n, vertex) - d > 0:
                raise ValueError("shell is not certified convex by exact face half-spaces")

    return {
        "schema": SCHEMA,
        "authority_kind": AUTHORITY_KIND,
        "shell_id": shell_id,
        "source_id": source_id,
        "role": role,
        "units": units,
        "frame_id": frame_id,
        "revision_id": revision_id,
        "configuration_id": configuration_id,
        "interior_witness": interior,
        "faces": tuple(faces),
        "vertex_count": len(all_vertices),
        "edge_count": len(edge_incidence),
        "face_count": len(faces),
    }


def canonical_shell_object(source):
    s = normalize_shell(source)
    faces = []
    for f in sorted(s["faces"], key=lambda item: item["face_id"]):
        faces.append({
            "face_id": f["face_id"],
            "patch_sha256": f["patch_sha256"],
            "patch": patch.canonical_source_object(f["patch"]),
            "trim_uv": [[qtext(u), qtext(v)] for u, v in f["trim_uv"]],
        })
    return {
        "schema": SCHEMA,
        "authority_kind": AUTHORITY_KIND,
        "shell_id": s["shell_id"],
        "source_id": s["source_id"],
        "role": s["role"],
        "units": s["units"],
        "frame_id": s["frame_id"],
        "revision_id": s["revision_id"],
        "configuration_id": s["configuration_id"],
        "interior_witness": [qtext(v) for v in s["interior_witness"]],
        "faces": faces,
    }


def shell_sha256(source) -> str:
    raw = json.dumps(canonical_shell_object(source), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def certify_shell(source):
    s = normalize_shell(source)
    digest = shell_sha256(source)
    planes = []
    for f in sorted(s["faces"], key=lambda item: item["face_id"]):
        planes.append({
            "face_id": f["face_id"],
            "normal": [qtext(v) for v in f["normal"]],
            "offset": qtext(f["offset"]),
            "patch_sha256": f["patch_sha256"],
        })
    core = {
        "schema": "radicadsac-trimmed-convex-shell-certificate/1.0",
        "status": "EXACT_CERTIFIED_TRIMMED_CONVEX_SHELL",
        "shell_sha256": digest,
        "shell_id": s["shell_id"],
        "source_id": s["source_id"],
        "role": s["role"],
        "units": s["units"],
        "frame_id": s["frame_id"],
        "revision_id": s["revision_id"],
        "configuration_id": s["configuration_id"],
        "interior_witness": [qtext(v) for v in s["interior_witness"]],
        "topology": {
            "vertex_count": s["vertex_count"],
            "edge_count": s["edge_count"],
            "face_count": s["face_count"],
            "euler_characteristic": 2,
            "closed_opposite_oriented_seams": True,
            "connected": True,
            "genus": 0,
        },
        "face_planes": planes,
        "solid_membership_authority": "EXACT_CONVEX_HALFSPACE_INTERSECTION",
        "durable_body_or_lineage_authority": False,
        "opaque_import_authority": False,
    }
    encoded = json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    core["certificate_sha256"] = hashlib.sha256(encoded).hexdigest()
    return core


def classify_point(source, point, certificate):
    point = _point3(point, "solid-membership point")
    expected = certify_shell(source)
    if not isinstance(certificate, dict) or certificate != expected:
        return {
            "status": "BLOCKED",
            "blocker": "PB-007-03",
            "reason": "MISSING_STALE_OR_MUTATED_EXACT_SHELL_CERTIFICATE",
            "solid_membership_certified": False,
        }
    s = normalize_shell(source)
    signs = [_dot(f["normal"], point) - f["offset"] for f in s["faces"]]
    if any(v > 0 for v in signs):
        relation = "OUTSIDE"
    elif any(v == 0 for v in signs):
        relation = "BOUNDARY"
    else:
        relation = "INSIDE"
    return {
        "status": "EXACT_SOLID_MEMBERSHIP",
        "relation": relation,
        "shell_id": s["shell_id"],
        "shell_sha256": expected["shell_sha256"],
        "certificate_sha256": expected["certificate_sha256"],
        "point": [qtext(v) for v in point],
        "solid_membership_certified": True,
        "positive_volume_semantics": True,
        "durable_body_or_lineage_authority": False,
    }


def classify_shell_descriptor(descriptor):
    if not isinstance(descriptor, dict) or descriptor.get("schema") != SCHEMA:
        return {
            "status": "BLOCKED",
            "blocker": "PB-007-03",
            "reason": "OPAQUE_OR_UNREVIEWED_SHELL_REQUIRES_EXACT_CERTIFICATE_ROUTE",
        }
    try:
        cert = certify_shell(descriptor)
    except (TypeError, ValueError, ZeroDivisionError, AssertionError) as exc:
        return {
            "status": "SEMANTIC_BLOCKER",
            "blocker": "PB-007-03",
            "reason": "INVALID_EXACT_TRIMMED_CONVEX_SHELL",
            "detail": str(exc),
        }
    return {
        "status": cert["status"],
        "shell_sha256": cert["shell_sha256"],
        "certificate_sha256": cert["certificate_sha256"],
        "solid_membership_certified": True,
        "full_pb00703_closed": False,
    }
