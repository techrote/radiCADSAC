#!/usr/bin/env python3
"""Pinned Manifold external fallback comparator for RCS-021."""
from __future__ import annotations

import importlib.metadata
import time
from typing import Any

from field import P, STOCK, final_field

PINNED_VERSION="3.5.3"
PINNED_COMMIT="0edd9d54876f3135e431575214dd6d8a72866fee"
LICENSE="Apache-2.0"


def evaluate(case: dict[str, Any], edge_length_mm: float, root_tolerance_mm: float, authoritative_min_feature_mm: float) -> dict[str, Any]:
    started=time.perf_counter()
    try:
        installed=importlib.metadata.version("manifold3d")
        if installed != PINNED_VERSION:
            raise RuntimeError(f"manifold3d {installed} != pinned {PINNED_VERSION}")
        from manifold3d import Manifold
        def sdf(x: float,y: float,z: float) -> float:
            return final_field(case,P(float(x),float(y),float(z)))
        result=Manifold.level_set(
            sdf,
            [-0.5,-0.5,-0.5,STOCK[0]+0.5,STOCK[1]+0.5,STOCK[2]+0.5],
            float(edge_length_mm),
            0.0,
            float(root_tolerance_mm),
        )
        status=str(result.status())
        pieces=result.decompose()
        feature=case.get("minimum_positive_feature_mm")
        resolution_refusal=feature is not None and float(feature) < float(authoritative_min_feature_mm)
        classification="refused_resolution_budget" if resolution_refusal else "external_comparator_result"
        return {
            "schema":"rcs-021-manifold-fallback/1.0",
            "candidate":"Manifold LevelSet",
            "package":"manifold3d",
            "version":installed,
            "source_commit":PINNED_COMMIT,
            "license":LICENSE,
            "edge_length_mm":float(edge_length_mm),
            "requested_root_tolerance_mm":float(root_tolerance_mm),
            "reported_tolerance_mm":float(result.get_tolerance()),
            "status":status,
            "classification":classification,
            "resolution_refusal":resolution_refusal,
            "minimum_positive_feature_mm":feature,
            "volume_mm3":float(result.volume()),
            "surface_area_mm2":float(result.surface_area()),
            "body_count":len(pieces),
            "vertex_count":int(result.num_vert()),
            "triangle_count":int(result.num_tri()),
            "bbox_mm":[float(v) for v in result.bounding_box()],
            "runtime_ms":(time.perf_counter()-started)*1000.0,
            "reconciliation_class":"mesh_level_set_requires_analytic_provenance_recovery_and_RCS005_brep_gate",
            "authoritative":False,
        }
    except Exception as exc:
        return {
            "schema":"rcs-021-manifold-fallback/1.0",
            "candidate":"Manifold LevelSet",
            "version":PINNED_VERSION,
            "source_commit":PINNED_COMMIT,
            "license":LICENSE,
            "classification":"external_candidate_error",
            "error":f"{type(exc).__name__}: {exc}",
            "runtime_ms":(time.perf_counter()-started)*1000.0,
            "authoritative":False,
        }
