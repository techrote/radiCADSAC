#!/usr/bin/env python3
"""PB-007-03: exact nonconvex planar-patch shell, source-owned, model only.

Triangular exact rational trims of v5 affine patches are ACTUAL planar facets,
not tessellation of a curved source. This checker explicitly does not lower an
opaque STEP/B-rep or an arbitrary curved NURBS source.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json

import pb00703_parametric_patch as patch
import pb00703_trimmed_shell as v6

SCHEMA = "radicadsac-exact-nonconvex-patch-shell/1.0"
KIND = "EXACT_PLANAR_PATCH_SHELL_ONLY"
CERT_SCHEMA = "radicadsac-nonconvex-shell-certificate/1.0"
MAX_SOURCE_BYTES = 200_000
MAX_FACES = 192
MAX_BITS = 512
MAX_PAIR_CHECKS = 18_336  # C(192,2)


class BudgetOpen(Exception):
    """Resource/coverage stop: not an invalid physical source or a proof."""


def sub(a, b):
    return tuple(x-y for x,y in zip(a,b))


def add(a, b):
    return tuple(x+y for x,y in zip(a,b))


def scale(a, t):
    return tuple(x*t for x in a)


def dot(a, b):
    return sum((x*y for x,y in zip(a,b)), Fraction(0))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def point_on_triangle(p, tri):
    a,b,c = tri
    n = cross(sub(b,a),sub(c,a))
    if dot(n,sub(p,a)) != 0:
        return False
    return all(dot(n,cross(sub(v,u),sub(p,u))) >= 0 for u,v in ((a,b),(b,c),(c,a)))


def point_on_segment(p, a, b):
    return cross(sub(p,a),sub(b,a)) == (0,0,0) and dot(sub(p,a),sub(p,b)) <= 0


def _project(p, axis):
    return tuple(p[i] for i in range(3) if i != axis)


def _cross2(a, b):
    return a[0]*b[1]-a[1]*b[0]


def _segment_segment_coplanar(a,b,c,d,axis):
    """Finite exact intersection endpoints (even for overlapping collinear segments)."""
    aa,bb,cc,dd = (_project(v,axis) for v in (a,b,c,d))
    r = sub(bb,aa); s = sub(dd,cc)
    den = _cross2(r,s)
    if den:
        t = _cross2(sub(cc,aa),s)/den
        u = _cross2(sub(cc,aa),r)/den
        return {add(a,scale(sub(b,a),t))} if 0 <= t <= 1 and 0 <= u <= 1 else set()
    if _cross2(sub(cc,aa),r) != 0:
        return set()
    return {p for p in (a,b,c,d) if point_on_segment(p,a,b) and point_on_segment(p,c,d)}


def _segment_triangle(a,b,tri):
    """All segment/triangle intersection endpoints as exact rational 3D points."""
    x,y,z = tri
    n = cross(sub(y,x),sub(z,x))
    da, db = dot(n,sub(a,x)), dot(n,sub(b,x))
    if da == 0 and db == 0:
        out = {p for p in (a,b) if point_on_triangle(p,tri)}
        # Projection is invertible on this plane because the chosen normal
        # component is nonzero. Segment pair intersections are exact in 3D.
        axis = next(i for i in range(3) if n[i])
        for u,v in ((x,y),(y,z),(z,x)):
            out.update(_segment_segment_coplanar(a,b,u,v,axis))
        return out
    if da*db > 0 or da == db:
        return set()
    t = da/(da-db)
    if not (0 <= t <= 1):
        return set()
    p = add(a,scale(sub(b,a),t))
    return {p} if point_on_triangle(p,tri) else set()


def _triangle_intersections(a,b):
    out = set()
    for tri1,tri2 in ((a,b),(b,a)):
        for i in range(3):
            out.update(_segment_triangle(tri1[i],tri1[(i+1)%3],tri2))
    return out


def _check_nonintersections(tris, max_pairs):
    count=0
    boxes=[tuple((min(p[k] for p in t),max(p[k] for p in t)) for k in range(3)) for t in tris]
    for i,a in enumerate(tris):
        for j in range(i+1,len(tris)):
            b=tris[j]
            count += 1
            if count > max_pairs:
                raise BudgetOpen("pairwise exact geometric checks exceeded declared budget")
            if any(boxes[i][k][1]<boxes[j][k][0] or boxes[j][k][1]<boxes[i][k][0] for k in range(3)):
                continue
            common = set(a) & set(b)
            if len(common) == 3:
                raise ValueError("duplicate coincident triangle surface")
            intersections = _triangle_intersections(a,b)
            if intersections - common:
                raise ValueError("unmodelled triangle intersections or overlapping facets")
    return count


def _small_frac(x):
    return x.numerator.bit_length() <= MAX_BITS and x.denominator.bit_length() <= MAX_BITS


def _serialize(obj):
    return json.dumps(obj,sort_keys=True,separators=(",", ":"),ensure_ascii=False).encode("utf-8")


def normalize_shell(source, *, max_faces=MAX_FACES, max_pairs=MAX_PAIR_CHECKS):
    if not isinstance(source,dict):
        raise TypeError("shell must be a source object")
    try:
        size=len(_serialize(source))
    except (ValueError,TypeError,OverflowError) as exc:
        raise ValueError("source is not strict JSON data") from exc
    if size > MAX_SOURCE_BYTES:
        raise BudgetOpen("source encoding exceeds bounded parser budget")
    allowed={"schema","authority_kind","shell_id","source_id","role","units","frame_id","revision_id","configuration_id","faces"}
    if set(source)!=allowed or source["schema"]!=SCHEMA or source["authority_kind"]!=KIND:
        raise ValueError("unsupported schema/fields/authority kind; opaque sources are not certified")
    for key in ("shell_id","source_id","units","frame_id","revision_id","configuration_id"):
        if not isinstance(source[key],str) or not source[key].strip():
            raise ValueError("missing exact source identity: "+key)
    if source["role"] not in patch.ROLES:
        raise ValueError("cutting, holder and stock roles must be explicit")
    raw=source["faces"]
    if not isinstance(raw,list) or len(raw)<4:
        raise ValueError("requires a closed shell of >=4 planar triangular source faces")
    if len(raw)>max_faces:
        raise BudgetOpen("face count exceeds exact pairwise budget; full-domain remains OPEN")
    faces=[]; ids=set()
    for item in raw:
        if not isinstance(item,dict) or set(item)!={"face_id","patch","patch_sha256","trim_uv"}:
            raise ValueError("face lacks exact v5 patch/trim authority")
        fid=item["face_id"]
        if not isinstance(fid,str) or not fid.strip() or fid in ids:
            raise ValueError("duplicate/missing face ID")
        ids.add(fid)
        p=v6._patch_affine_data(item["patch"])
        if item["patch_sha256"]!=patch.source_sha256(item["patch"]):
            raise ValueError("v5 exact patch SHA mismatch")
        for key in ("source_id","role","units","frame_id"):
            if p[key]!=source[key]:
                raise ValueError("patch/source identity or holder role drift: "+key)
        uv=v6._normalize_trim(item,p)
        if len(uv)!=3:
            raise BudgetOpen("only certified triangular affine trims supported; nontriangular source remains OPEN")
        tri=v6._evaluate_trim(item["patch"],uv)
        if not all(_small_frac(coord) for v in tri for coord in v):
            raise BudgetOpen("rational bit-length guard reached; not a physical invalidation")
        n=cross(sub(tri[1],tri[0]),sub(tri[2],tri[0]))
        if n==(0,0,0):
            raise ValueError("zero-area physical face")
        faces.append({"face_id":fid,"patch":item["patch"],"patch_sha256":item["patch_sha256"],"trim_uv":uv,"vertices":tri})
    triangles=[f["vertices"] for f in faces]
    edges={}; adjacent={f["face_id"]:set() for f in faces}
    for f in faces:
        tri=f["vertices"]
        for i in range(3):
            a,b=tri[i],tri[(i+1)%3]
            key=tuple(sorted((a,b)))
            edges.setdefault(key,[]).append((f["face_id"],a,b))
    for incidences in edges.values():
        if len(incidences)!=2:
            raise ValueError("unclosed/T-junction/nonmanifold physical seam")
        (fi,a,b),(fj,c,d)=incidences
        if fi==fj or a!=d or b!=c:
            raise ValueError("facet seam is not oppositely oriented")
        adjacent[fi].add(fj); adjacent[fj].add(fi)
    seen=set(); stack=[faces[0]["face_id"]]
    while stack:
        fid=stack.pop()
        if fid not in seen:
            seen.add(fid); stack.extend(adjacent[fid]-seen)
    if seen!=set(adjacent):
        raise BudgetOpen("multiple shell components require an independently certified nesting route")
    vertices=set(v for t in triangles for v in t)
    if len(vertices)-len(edges)+len(faces)!=2:
        raise BudgetOpen("genus>0 or invalid incidence; topology route remains OPEN")
    pairs=_check_nonintersections(triangles,max_pairs)
    six_volume=sum((dot(a,cross(b,c)) for a,b,c in triangles),Fraction(0))
    if six_volume <= 0:
        raise ValueError("oriented shell must enclose strictly positive signed volume")
    return {"faces":faces,"triangles":triangles,"vertex_count":len(vertices),"edge_count":len(edges),"face_count":len(faces),"six_volume":six_volume,"pair_checks":pairs}


def canonical_object(source, *, _norm=None):
    norm=_norm if _norm is not None else normalize_shell(source)
    out={k:source[k] for k in ("schema","authority_kind","shell_id","source_id","role","units","frame_id","revision_id","configuration_id")}
    out["faces"]=[{
        "face_id":f["face_id"],"patch":patch.canonical_source_object(f["patch"]),
        "patch_sha256":f["patch_sha256"],
        "trim_uv":[[patch.qtext(u),patch.qtext(v)] for u,v in f["trim_uv"]],
    } for f in sorted(norm["faces"],key=lambda d:d["face_id"])]
    return out


def certify_shell(source, *, _norm=None):
    norm=_norm if _norm is not None else normalize_shell(source)
    digest=hashlib.sha256(_serialize(canonical_object(source,_norm=norm))).hexdigest()
    obj={"schema":CERT_SCHEMA,"status":"EXACT_NONCONVEX_PLANAR_PATCH_SHELL",
        "source_sha256":digest,"shell_id":source["shell_id"],"source_id":source["source_id"],
        "role":source["role"],"units":source["units"],"frame_id":source["frame_id"],
        "revision_id":source["revision_id"],"configuration_id":source["configuration_id"],
        "topology":{"vertices":norm["vertex_count"],"edges":norm["edge_count"],
                    "faces":norm["face_count"],"euler":2,"pairwise_checks":norm["pair_checks"]},
        "oriented_six_volume":patch.qtext(norm["six_volume"]),
        "membership":"EXACT_RATIONAL_BOUNDARY_AND_GENERIC_RAY_PARITY",
        "full_pb00703_closed":False,"native_or_step_qualified":False,
        "durable_body_or_lineage_authority":False}
    obj["certificate_sha256"]=hashlib.sha256(_serialize(obj)).hexdigest()
    return obj


def _strict_ray_crosses(p,d,tri):
    a,b,c=tri; n=cross(sub(b,a),sub(c,a)); den=dot(n,d)
    if den==0:
        if dot(n,sub(p,a))==0:
            return None  # direction lies in the face's plane
        return False
    t=dot(n,sub(a,p))/den
    if t<=0:
        return False
    hit=add(p,scale(d,t))
    if not point_on_triangle(hit,tri):
        return False
    if any(point_on_segment(hit,tri[i],tri[(i+1)%3]) for i in range(3)):
        return None  # ray grazes a vertex/edge; try another exact direction
    return True


def classify_point(source, point, certificate, *, max_ray_attempts=None):
    p=v6._point3(point,"membership query")
    norm=normalize_shell(source)
    expected=certify_shell(source,_norm=norm)
    if certificate!=expected:
        return {"status":"BLOCKED","blocker":"PB-007-03","reason":"MISSING_OR_FORGED_SOURCE_CERTIFICATE"}
    tris=norm["triangles"]
    if any(point_on_triangle(p,t) for t in tris):
        relation="BOUNDARY"
    else:
        tries=max_ray_attempts if max_ray_attempts is not None else (8*len(tris)+3)
        if not isinstance(tries,int) or isinstance(tries,bool) or tries<1:
            raise ValueError("ray budget must be positive integer")
        relation=None
        for k in range(1,tries+1):
            direction=(Fraction(1),Fraction(k),Fraction(k*k))
            crosses=[_strict_ray_crosses(p,direction,t) for t in tris]
            if None not in crosses:
                relation="INSIDE" if sum(x is True for x in crosses)%2 else "OUTSIDE"
                break
        if relation is None:
            return {"status":"BLOCKED","blocker":"PB-007-03","reason":"EXACT_RAY_GENERICITY_BUDGET_EXHAUSTED"}
    return {"status":"EXACT_SOLID_MEMBERSHIP","relation":relation,
            "source_sha256":expected["source_sha256"],"certificate_sha256":expected["certificate_sha256"],
            "positive_volume_semantics":True,"full_pb00703_closed":False}


def classify_descriptor(source):
    if not isinstance(source,dict) or source.get("schema")!=SCHEMA:
        return {"status":"BLOCKED","blocker":"PB-007-03","reason":"UNSUPPORTED_OR_OPAQUE_SOURCE"}
    try:
        cert=certify_shell(source)
    except BudgetOpen as exc:
        return {"status":"BLOCKED","blocker":"PB-007-03","reason":"EXACT_CONSTRUCTION_BUDGET_OR_SUBGRAMMAR_OPEN","detail":str(exc)}
    except (TypeError,ValueError,ZeroDivisionError,AssertionError,RecursionError,OverflowError) as exc:
        return {"status":"SEMANTIC_BLOCKER","blocker":"PB-007-03","reason":"INVALID_EXACT_SOURCE_DESCRIPTOR","detail":str(exc)}
    return {"status":cert["status"],"certificate_sha256":cert["certificate_sha256"],"full_pb00703_closed":False}
