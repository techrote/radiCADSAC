#!/usr/bin/env python3
"""Conservative OCCT-independent material-set oracle for RCS-021."""
from __future__ import annotations

from collections import deque
import math
import time
from typing import Any

from field import P, STOCK, column_height, known_volume, removal_field


def _body_count_xy(case: dict[str, Any], pitch: float) -> int:
    nx = int(math.ceil(STOCK[0] / pitch))
    ny = int(math.ceil(STOCK[1] / pitch))
    occupied = set()
    for iy in range(ny):
        y = min(STOCK[1] - 1e-12, (iy + 0.5) * pitch)
        for ix in range(nx):
            x = min(STOCK[0] - 1e-12, (ix + 0.5) * pitch)
            if column_height(case, x, y) > 1e-12:
                occupied.add((ix, iy))
    count = 0
    while occupied:
        count += 1
        seed = occupied.pop()
        todo = [seed]
        while todo:
            ix, iy = todo.pop()
            for q in ((ix-1,iy),(ix+1,iy),(ix,iy-1),(ix,iy+1)):
                if q in occupied:
                    occupied.remove(q)
                    todo.append(q)
    return count


def evaluate(case: dict[str, Any], max_depth: int, numeric_error_mm: float, connectivity_pitch_mm: float = 0.5) -> dict[str, Any]:
    """Bound remaining material by classifying octree cells with a Lipschitz field.

    `removal_field` is positive inside the swept tool set and is 1-Lipschitz in
    XYZ for every qualified tool segment.  For cell centre c and half diagonal
    d, f(c)>d certifies the full cell is removed and f(c)<-d certifies the full
    cell remains.  Undecided cells are subdivided; leaves at max depth contribute
    a conservative [0, cell-volume] interval.
    """
    started = time.perf_counter()
    stack = [(0.0, STOCK[0], 0.0, STOCK[1], 0.0, STOCK[2], 0)]
    lower_material = 0.0
    upper_material = 0.0
    center_estimate = 0.0
    nodes = 0
    full_material = 0
    full_removed = 0
    boundary_leaves = 0
    max_boundary_halfdiag = 0.0

    while stack:
        x0,x1,y0,y1,z0,z1,depth = stack.pop()
        nodes += 1
        dx,dy,dz = x1-x0,y1-y0,z1-z0
        volume = dx*dy*dz
        cx,cy,cz = (x0+x1)*0.5,(y0+y1)*0.5,(z0+z1)*0.5
        halfdiag = 0.5*math.sqrt(dx*dx+dy*dy+dz*dz)
        cut = removal_field(case, P(cx,cy,cz))
        if cut + numeric_error_mm < -halfdiag:
            lower_material += volume
            upper_material += volume
            center_estimate += volume
            full_material += 1
            continue
        if cut - numeric_error_mm > halfdiag:
            full_removed += 1
            continue
        if depth >= max_depth:
            upper_material += volume
            if cut < 0.0:
                center_estimate += volume
            boundary_leaves += 1
            max_boundary_halfdiag = max(max_boundary_halfdiag, halfdiag)
            continue
        mx,my,mz = cx,cy,cz
        nd = depth + 1
        for xa,xb in ((x0,mx),(mx,x1)):
            for ya,yb in ((y0,my),(my,y1)):
                for za,zb in ((z0,mz),(mz,z1)):
                    stack.append((xa,xb,ya,yb,za,zb,nd))

    known = known_volume(case)
    validation: dict[str, Any] | None = None
    if known is not None:
        exact_volume, exact_bodies = known
        validation = {
            "closed_form_volume_mm3": exact_volume,
            "closed_form_body_count": exact_bodies,
            "contained_by_material_interval": lower_material - 1e-9 <= exact_volume <= upper_material + 1e-9,
            "center_estimate_abs_delta_mm3": abs(center_estimate-exact_volume),
        }
    bodies = _body_count_xy(case, connectivity_pitch_mm)
    return {
        "schema": "rcs-021-material-oracle/1.0",
        "method": "conservative-lipschitz-octree",
        "independent_of": ["OCCT", "Manifold", "tri-dexel candidate"],
        "max_depth": max_depth,
        "numeric_field_error_mm": numeric_error_mm,
        "material_volume_lower_mm3": lower_material,
        "material_volume_upper_mm3": upper_material,
        "material_volume_center_estimate_mm3": center_estimate,
        "material_volume_interval_width_mm3": upper_material-lower_material,
        "boundary_spatial_half_diagonal_mm": max_boundary_halfdiag,
        "body_count_xy_grid": bodies,
        "body_connectivity_pitch_mm": connectivity_pitch_mm,
        "node_count": nodes,
        "certified_full_material_cells": full_material,
        "certified_full_removed_cells": full_removed,
        "boundary_leaf_count": boundary_leaves,
        "runtime_ms": (time.perf_counter()-started)*1000.0,
        "closed_form_validation": validation,
    }
