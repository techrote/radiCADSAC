#!/usr/bin/env python3
"""Normalize RCS-007 evidence semantics after raw experiment execution.

The first-stage campaign deliberately records simple per-model predictions. This pass
makes the research interpretation explicit: a local uncertain-contact deferral is
not a claimed no-op, and geometrically valid accumulation chains can still breach
their analytic physical oracle.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("results root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True, type=Path)
    args = parser.parse_args()

    path = args.results_dir / "results.json"
    data = load(path)
    plan_path = Path(__file__).resolve().parents[1] / "experiment-plan-v1.json"
    plan = load(plan_path)
    volume_tol = float(plan["constants"]["geometry_equivalence_volume_mm3"])

    local_deferred = 0
    local_decisive_mismatch = 0
    for record in data.get("backend_sweeps", []):
        if not isinstance(record, dict):
            continue
        local = record.get("operation_local_interval")
        if not isinstance(local, dict):
            continue
        decision = local.get("decision")
        if decision == "defer_uncertain_contact":
            local["decisive"] = False
            local["matches_physical_oracle"] = None
            local["oracle_interpretation"] = "deferred_without_rewriting_physical_intent"
            local_deferred += 1
        else:
            local["decisive"] = True
            expected = bool(record.get("expected_material_change"))
            predicted = bool(local.get("predicted_material_change"))
            match = predicted == expected
            local["matches_physical_oracle"] = match
            local["oracle_interpretation"] = "decisive_match" if match else "decisive_mismatch"
            if not match:
                local_decisive_mismatch += 1

    accumulation_geometry_breaches = 0
    for chain in data.get("accumulation_chains", []):
        if not isinstance(chain, dict):
            continue
        orders = chain.get("orders")
        if not isinstance(orders, dict):
            continue
        any_breach = False
        for order in ("ascending", "descending"):
            run = orders.get(order)
            payload = run.get("payload") if isinstance(run, dict) else None
            if not isinstance(payload, dict):
                continue
            abs_error = abs(float(payload.get("volume_abs_error_mm3", float("inf"))))
            breach = abs_error > volume_tol
            payload["analytic_volume_oracle_within_tolerance"] = not breach
            payload["analytic_volume_oracle_tolerance_mm3"] = volume_tol
            any_breach = any_breach or breach
        chain["any_order_analytic_volume_breach"] = any_breach
        if any_breach:
            accumulation_geometry_breaches += 1

    summary = data.setdefault("summary", {})
    if not isinstance(summary, dict):
        raise RuntimeError("summary must be an object")
    summary["operation_local_interval_oracle_mismatches"] = local_decisive_mismatch
    summary["operation_local_interval_deferred_cases"] = local_deferred
    summary["accumulation_geometry_breach_cases"] = accumulation_geometry_breaches
    data["evidence_interpretation"] = {
        "local_interval_deferral_is_not_noop": True,
        "chain_validity_does_not_imply_geometric_correctness": True,
        "postprocessor_schema": "rcs-007-evidence-interpretation/1.0",
    }

    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary_path = args.results_dir / "summary.md"
    lines = summary_path.read_text(encoding="utf-8").rstrip().splitlines()
    lines.extend(
        [
            "",
            "## Interpretation correction",
            "",
            f"- Operation-local uncertain-contact deferrals: {local_deferred}; these are unresolved classifications, not asserted no-ops.",
            f"- Decisive operation-local oracle mismatches: {local_decisive_mismatch}.",
            f"- Accumulation cases with an analytic-volume oracle breach in at least one order: {accumulation_geometry_breaches}.",
            "",
        ]
    )
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "operation_local_interval_deferred_cases": local_deferred,
        "operation_local_interval_oracle_mismatches": local_decisive_mismatch,
        "accumulation_geometry_breach_cases": accumulation_geometry_breaches,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
