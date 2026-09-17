#!/usr/bin/env python3
"""Directional dexel-style material representation for RCS-021."""
from __future__ import annotations

import hashlib
import json
import math
import time
from typing import Any

from field import STOCK, clamp, column_height, segments, xy_distance

try:
    import resource
except ImportError:  # pragma: no cover - Windows diagnostic only
    resource = None


def _rss_kb() -> int:
    if resource is None:
        return -1
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def _cell_height_bounds(case: dict[str, Any], x: float, y: float, halfdiag_xy: float) -> tuple[float, float]:
    lo = hi = STOCK[2]
    r = float(case["tool"]["radius_mm"])
    kind = case["tool"]["kind"]
    for a,b in segments(case):
        d,_ = xy_distance(x,y,a,b)
        if d - halfdiag_xy > r:
            continue
        if kind == "flat":
            zlo = clamp(min(a.z,b.z),0.0,STOCK[2])
            zhi = clamp(max(a.z,b.z),0.0,STOCK[2])
            horizontal = math.hypot(b.x-a.x,b.y-a.y)
            if d + halfdiag_xy <= r:
                if horizontal <= 1e-12 or abs(a.z-b.z) <= 1e-12:
                    slo = shi = zlo
                else:
                    slo,shi = zlo,zhi
            else:
                slo,shi = zlo,STOCK[2]
        elif kind == "ball":
            if abs(a.z-b.z) > 1e-12:
                raise ValueError("rounded dexel bound requires constant-Z path")
            if d + halfdiag_xy <= r:
                d0=max(0.0,d-halfdiag_xy)
                d1=min(r,d+halfdiag_xy)
                slo=clamp(a.z-math.sqrt(max(0.0,r*r-d0*d0)),0.0,STOCK[2])
                shi=clamp(a.z-math.sqrt(max(0.0,r*r-d1*d1)),0.0,STOCK[2])
            else:
                slo,shi=clamp(a.z-r,0.0,STOCK[2]),STOCK[2]
        else:
            raise ValueError(f"unsupported tool kind {kind!r}")
        lo=min(lo,slo)
        hi=min(hi,shi)
    return lo,hi


def _body_count(heights: list[list[float]]) -> int:
    ny=len(heights)
    nx=len(heights[0]) if ny else 0
    cells={(ix,iy) for iy in range(ny) for ix in range(nx) if heights[iy][ix] > 1e-12}
    count=0
    while cells:
        count+=1
        todo=[cells.pop()]
        while todo:
            ix,iy=todo.pop()
            for q in ((ix-1,iy),(ix+1,iy),(ix,iy-1),(ix,iy+1)):
                if q in cells:
                    cells.remove(q); todo.append(q)
    return count


def _interval_count(line: list[bool]) -> int:
    count=0
    active=False
    for value in line:
        if value and not active:
            count+=1
        active=value
    return count


def evaluate(case: dict[str, Any], pitch_mm: float) -> dict[str, Any]:
    started=time.perf_counter()
    rss0=_rss_kb()
    pitch=float(pitch_mm)
    nx=int(math.ceil(STOCK[0]/pitch))
    ny=int(math.ceil(STOCK[1]/pitch))
    nz=int(math.ceil(STOCK[2]/pitch))
    halfdiag_xy=pitch/math.sqrt(2.0)
    heights=[]
    lower=upper=estimate=0.0
    boundary_columns=0
    for iy in range(ny):
        y=min(STOCK[1]-1e-12,(iy+0.5)*pitch)
        row=[]
        for ix in range(nx):
            x=min(STOCK[0]-1e-12,(ix+0.5)*pitch)
            h=column_height(case,x,y)
            hlo,hhi=_cell_height_bounds(case,x,y,halfdiag_xy)
            area=min(pitch,STOCK[0]-ix*pitch)*min(pitch,STOCK[1]-iy*pitch)
            estimate += h*area
            lower += hlo*area
            upper += hhi*area
            if hhi-hlo > 1e-12:
                boundary_columns+=1
            row.append(h)
        heights.append(row)
    z_intervals=sum(1 for row in heights for h in row if h > 1e-12)
    x_intervals=0
    y_intervals=0
    for iz in range(nz):
        z=min(STOCK[2]-1e-12,(iz+0.5)*pitch)
        for iy in range(ny):
            x_intervals += _interval_count([heights[iy][ix] > z for ix in range(nx)])
        for ix in range(nx):
            y_intervals += _interval_count([heights[iy][ix] > z for iy in range(ny)])
    body_count=_body_count(heights)
    signature_payload={
        "pitch_mm":pitch,
        "volume":round(estimate,9),
        "lower":round(lower,9),
        "upper":round(upper,9),
        "body_count":body_count,
        "intervals":[x_intervals,y_intervals,z_intervals],
    }
    signature=hashlib.sha256(json.dumps(signature_payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {
        "schema":"rcs-021-tridexel/1.0",
        "representation":"three-direction interval material field with analytic Z-column heights",
        "pitch_mm":pitch,
        "spatial_support_radius_xy_mm":halfdiag_xy,
        "volume_estimate_mm3":estimate,
        "volume_lower_mm3":lower,
        "volume_upper_mm3":upper,
        "volume_interval_width_mm3":upper-lower,
        "body_count":body_count,
        "grid":[nx,ny,nz],
        "directional_interval_counts":{"x":x_intervals,"y":y_intervals,"z":z_intervals},
        "total_interval_count":x_intervals+y_intervals+z_intervals,
        "boundary_column_count":boundary_columns,
        "semantic_lineage":"external programme operation/body IDs retained; interval indices are non-durable diagnostics",
        "reconciliation_class":"bounded_directional_material_state_requires_brep_before_step",
        "engineering_signature":signature,
        "runtime_ms":(time.perf_counter()-started)*1000.0,
        "peak_rss_kb":max(rss0,_rss_kb()),
    }
