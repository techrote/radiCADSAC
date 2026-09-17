#!/usr/bin/env python3
"""Refine RCS-020 groove/parting evidence with a closed-form material oracle.

The first hosted campaign intentionally exposed that uniform trapezoidal sampling
is a poor oracle at a complete cut-through discontinuity. This post-processing
stage preserves that numerical result as a diagnostic and replaces the
acceptance oracle for groove/parting cases with an independent closed-form
integral of the exact rounded-groove radius function.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def exact_groove_material_volume_mm3(
    *,
    stock_z0_mm: float,
    stock_z1_mm: float,
    stock_outer_radius_mm: float,
    cutting_width_mm: float,
    corner_radius_mm: float,
    bottom_radius_mm: float,
) -> float:
    """Closed-form π∫r(z)^2 dz for a symmetric rounded axial groove.

    The groove consists of a central flat-bottom band of width
    `cutting_width - 2*corner_radius`, plus two quarter-circle corner bands.
    For one corner with x ∈ [0,c] and A=b+c:

      r(x) = A - sqrt(c² - x²)

      ∫r² dx = A²c + 2c³/3 - Aπc²/2

    This is independent of the polygonized candidate and avoids quadrature
    error at the full-stock/groove and complete-parting discontinuities.
    """
    span = stock_z1_mm - stock_z0_mm
    width = cutting_width_mm
    c = corner_radius_mm
    b = bottom_radius_mm
    if span <= 0.0 or width <= 0.0:
        raise ValueError("invalid stock span or groove width")
    if c < 0.0 or 2.0 * c > width:
        raise ValueError("corner radius exceeds groove half-width")
    if b < 0.0 or b >= stock_outer_radius_mm:
        raise ValueError("invalid groove bottom radius")
    if width > span:
        raise ValueError("groove wider than stock")

    outside_integral = stock_outer_radius_mm**2 * (span - width)
    flat_width = width - 2.0 * c
    flat_integral = b**2 * flat_width
    if c == 0.0:
        corner_integral = 0.0
    else:
        a = b + c
        one_corner = a * a * c + (2.0 / 3.0) * c**3 - a * math.pi * c * c / 2.0
        corner_integral = 2.0 * one_corner
    return math.pi * (outside_integral + flat_integral + corner_integral)


def refine_case(case: dict[str, Any], plan_case: dict[str, Any], tool: dict[str, Any], budget: float) -> None:
    if case.get("kind") not in {"groove", "parting"}:
        return
    stock = plan_case["stock"]
    corner = max(float(tool["left_corner_radius_mm"]), float(tool["right_corner_radius_mm"]))
    exact = exact_groove_material_volume_mm3(
        stock_z0_mm=float(stock["z0_mm"]),
        stock_z1_mm=float(stock["z1_mm"]),
        stock_outer_radius_mm=float(stock["outer_radius_mm"]),
        cutting_width_mm=float(tool["cutting_width_mm"]),
        corner_radius_mm=corner,
        bottom_radius_mm=float(plan_case["bottom_radius_mm"]),
    )
    old = case.get("oracle")
    if old is not None:
        case["oracle_numeric_diagnostic"] = old
    candidate = float(case["generator"]["volume_mm3"])
    delta = abs(candidate - exact)
    case["oracle"] = {
        "method": "closed_form_rounded_groove_integral",
        "volume_mm3": exact,
        "convergence_delta_mm3": 0.0,
        "independent_of_candidate_polygonization": True,
    }
    case["material_profile_volume_abs_delta_mm3"] = delta
    case["material_profile_within_budget"] = delta <= budget
    case["oracle_convergence_within_budget"] = True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=HERE / "experiment-plan-v1.json")
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    campaign_path = args.results_dir / "campaign-results.json"
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    plan_cases = {case["id"]: case for case in plan["cases"]}
    budget = float(plan["policies"]["max_material_profile_volume_delta_mm3"])

    refined = 0
    for case in campaign["cases"]:
        case_id = case["case_id"]
        plan_case = plan_cases[case_id]
        tool = plan["tools"][plan_case["tool"]]
        before = json.dumps(case.get("oracle"), sort_keys=True)
        refine_case(case, plan_case, tool, budget)
        if json.dumps(case.get("oracle"), sort_keys=True) != before:
            refined += 1
            (args.results_dir / f"{case_id}.json").write_text(
                json.dumps(case, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )

    campaign["oracle_refinement"] = {
        "schema": "rcs-020-oracle-refinement/1.0",
        "refined_cases": refined,
        "method": "closed_form_rounded_groove_integral",
        "reason": "uniform quadrature is not an acceptance oracle across groove/parting material discontinuities",
    }
    campaign_path.write_text(json.dumps(campaign, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(campaign["oracle_refinement"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
