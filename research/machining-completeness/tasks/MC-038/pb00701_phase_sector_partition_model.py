#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_pointwise_component_cone_model as v26  # noqa: E402

v25 = v26.v25
v24 = v26.v24
v23 = v26.v23
v22 = v26.v22
v21 = v26.v21
v20 = v26.v20
v19 = v26.v19
q = v26.q

V27_ROUTE = "EXACT_FINITE_RATIONAL_PHASE_SECTOR_CERTIFICATE_CUT_COMPOSITION"

# Exact half-magnitude sector endpoints modulo one turn.  These are certificate
# boundaries only; they are never approximated event boundaries.
_HALF_MAGNITUDE_BOUNDARIES = (
    ("SIN", Fraction(1, 12)),
    ("COS", Fraction(1, 6)),
    ("COS", Fraction(1, 3)),
    ("SIN", Fraction(5, 12)),
    ("SIN", Fraction(7, 12)),
    ("COS", Fraction(2, 3)),
    ("COS", Fraction(5, 6)),
    ("SIN", Fraction(11, 12)),
)


class PhaseSectorPartitionRefusal(RuntimeError):
    """Bounded exact-resource refusal. Never a truth value."""


def _trim(poly):
    return v25._trim([q(value) for value in poly])


def _floor(value):
    value = q(value)
    return value.numerator // value.denominator


def _reparameterize_polynomial(poly, left, right):
    """Return p(left + (right-left)u) exactly in the power basis."""
    poly = _trim(poly)
    left = q(left)
    right = q(right)
    width = right - left
    if width <= 0:
        raise ValueError("child interval must have positive width")
    out = [Fraction(0)] * len(poly)
    for degree, coefficient in enumerate(poly):
        for power in range(degree + 1):
            out[power] += (
                coefficient
                * Fraction(comb(degree, power))
                * (left ** (degree - power))
                * (width ** power)
            )
    return _trim(out)


def _power_spline(poly):
    """Encode one exact power polynomial as a single clamped rational B-spline."""
    poly = _trim(poly)
    degree = len(poly) - 1
    if degree == 0:
        return {
            "degree": 0,
            "knots": ["0", "1"],
            "controls": [str(poly[0])],
        }
    controls = []
    for j in range(degree + 1):
        value = Fraction(0)
        for k in range(j + 1):
            value += poly[k] * Fraction(comb(j, k), comb(degree, k))
        controls.append(str(value))
    return {
        "degree": degree,
        "knots": ["0"] * (degree + 1) + ["1"] * (degree + 1),
        "controls": controls,
    }


def _child_spec(cos_polys, sin_polys, offset, rate, source_parameter_id):
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": {
            str(harmonic): _power_spline(poly)
            for harmonic, poly in sorted(cos_polys.items())
            if _trim(poly) != [0]
        },
        "sin_splines": {
            str(harmonic): _power_spline(poly)
            for harmonic, poly in sorted(sin_polys.items())
            if _trim(poly) != [0]
        },
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": str(q(offset)),
        "phase_turn_rate": str(q(rate)),
        "source_parameter_id": source_parameter_id,
    }


def _exact_sector_partition(offset, rate, candidate_harmonics):
    """Derive all interior exact rational certificate cuts from the source phase."""
    offset = q(offset)
    rate = q(rate)
    candidate_harmonics = sorted({int(h) for h in candidate_harmonics if int(h) > 0})
    if rate == 0 or not candidate_harmonics:
        return {
            "status": "BLOCKED",
            "reason": "PHASE_SECTOR_PARTITION_NO_NONZERO_AFFINE_PHASE_OR_CANDIDATE",
            "blocker": "PB-007-01",
            "cuts": [],
        }

    by_cut = {}
    for harmonic in candidate_harmonics:
        t0 = Fraction(harmonic) * offset
        t1 = Fraction(harmonic) * (offset + rate)
        low = min(t0, t1)
        high = max(t0, t1)
        start = _floor(low) - 1
        stop = _floor(high) + 1
        for component, residue in _HALF_MAGNITUDE_BOUNDARIES:
            for integer in range(start, stop + 1):
                boundary = Fraction(integer) + residue
                if not (low < boundary < high):
                    continue
                cut = (boundary / Fraction(harmonic) - offset) / rate
                if not (Fraction(0) < cut < Fraction(1)):
                    continue
                by_cut.setdefault(cut, []).append({
                    "harmonic": harmonic,
                    "quadrature": component,
                    "harmonic_phase_boundary_turn": str(boundary),
                    "source_parameter_cut": str(cut),
                })

    cuts = sorted(by_cut)
    return {
        "status": "CERTIFIED" if cuts else "BLOCKED",
        "reason": None if cuts else "PHASE_SECTOR_PARTITION_HAS_NO_INTERIOR_CERTIFICATE_CUT",
        "blocker": None if cuts else "PB-007-01",
        "candidate_harmonics": candidate_harmonics,
        "cuts": [str(value) for value in cuts],
        "cut_provenance": [
            {
                "source_parameter_cut": str(value),
                "crossings": sorted(
                    by_cut[value],
                    key=lambda item: (
                        item["harmonic"],
                        item["quadrature"],
                        item["harmonic_phase_boundary_turn"],
                    ),
                ),
            }
            for value in cuts
        ],
        "exact_rational_only": True,
        "external_endpoint_crossings_omitted": True,
        "duplicate_cuts_collapsed_exactly": True,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
        "arbitrary_subdivision_cap_used": False,
    }


def _extract_child_route(result):
    if not isinstance(result, dict):
        return {
            "status": "BLOCKED",
            "reason": "PHASE_SECTOR_CHILD_CLASSIFIER_RETURNED_NON_RECORD",
            "blocker": "PB-007-01",
        }
    if result.get("status") == "RESOURCE_REFUSAL":
        return {
            **result,
            "reason": "PB00701_V27_CHILD_RESOURCE_REFUSAL",
            "is_truth_value": False,
        }
    if result.get("status") != "CERTIFIED":
        return {
            "status": "BLOCKED",
            "reason": "PHASE_SECTOR_CHILD_REMAINS_UNCERTIFIED",
            "blocker": "PB-007-01",
            "child_result": result,
        }

    spans = result.get("spans", [])
    if len(spans) != 1:
        return {
            "status": "BLOCKED",
            "reason": "PHASE_SECTOR_CHILD_EVENT_SUMMARY_NOT_SINGLE_SPAN_COMPOSABLE",
            "blocker": "PB-007-01",
            "child_span_count": len(spans),
        }
    span = spans[0]
    route = span.get("route", {})
    required = (
        "left_event",
        "right_event",
        "distinct_roots_open",
        "total_distinct_roots_closed",
        "all_roots_simple",
    )
    if route.get("status") != "CERTIFIED" or any(key not in route for key in required):
        return {
            "status": "BLOCKED",
            "reason": "PHASE_SECTOR_CHILD_EVENT_SUMMARY_INCOMPLETE",
            "blocker": "PB-007-01",
            "route_kind": span.get("route_kind"),
            "child_route": route,
        }
    if route.get("all_roots_simple") is not True:
        return {
            "status": "BLOCKED",
            "reason": "PHASE_SECTOR_CHILD_MULTIPLICITY_AUTHORITY_NOT_COMPOSABLE",
            "blocker": "PB-007-01",
            "route_kind": span.get("route_kind"),
            "child_route": route,
        }
    return {
        "status": "CERTIFIED",
        "route_kind": span.get("route_kind"),
        "route": route,
        "child_relation": result.get("relation"),
    }


def _endpoint_relation(event):
    relation = event.get("relation") if isinstance(event, dict) else None
    if relation not in {"NEGATIVE", "ZERO", "POSITIVE"}:
        raise ValueError("child endpoint lacks exact NEGATIVE/ZERO/POSITIVE relation")
    return relation


def _compose_child_summaries(children):
    """Compose exact child root summaries and deduplicate internal cut roots."""
    if not children:
        return {
            "status": "BLOCKED",
            "reason": "PHASE_SECTOR_PARTITION_HAS_NO_CHILDREN",
            "blocker": "PB-007-01",
        }

    open_roots = 0
    for child in children:
        route = child["route"]
        if route.get("status") != "CERTIFIED":
            return {
                "status": "BLOCKED",
                "reason": "PHASE_SECTOR_PARTITION_CONTAINS_UNCERTIFIED_CHILD",
                "blocker": "PB-007-01",
            }
        if route.get("all_roots_simple") is not True:
            return {
                "status": "BLOCKED",
                "reason": "PHASE_SECTOR_PARTITION_CHILD_MULTIPLICITY_NOT_CERTIFIED",
                "blocker": "PB-007-01",
            }
        open_roots += int(route["distinct_roots_open"])

    internal_roots = []
    for index in range(len(children) - 1):
        left = children[index]
        right = children[index + 1]
        cut = left["local_interval"][1]
        if cut != right["local_interval"][0]:
            return {
                "status": "BLOCKED",
                "reason": "PHASE_SECTOR_PARTITION_CHILD_INTERVALS_NOT_CONTIGUOUS",
                "blocker": "PB-007-01",
            }
        left_route = left["route"]
        right_route = right["route"]
        left_relation = _endpoint_relation(left_route["right_event"])
        right_relation = _endpoint_relation(right_route["left_event"])
        if left_relation != right_relation:
            return {
                "status": "BLOCKED",
                "reason": "PHASE_SECTOR_INTERNAL_CUT_ENDPOINT_RELATION_MISMATCH",
                "blocker": "PB-007-01",
                "cut": str(cut),
                "left_relation": left_relation,
                "right_relation": right_relation,
            }
        if left_relation == "ZERO":
            left_mult = left_route.get("endpoint_root_multiplicity", {}).get("right")
            right_mult = right_route.get("endpoint_root_multiplicity", {}).get("left")
            if left_mult != 1 or right_mult != 1:
                return {
                    "status": "BLOCKED",
                    "reason": "PHASE_SECTOR_INTERNAL_CUT_MULTIPLICITY_NOT_EXACTLY_COMPOSABLE",
                    "blocker": "PB-007-01",
                    "cut": str(cut),
                    "left_multiplicity": left_mult,
                    "right_multiplicity": right_mult,
                }
            internal_roots.append({
                "cut": str(cut),
                "relation": "ZERO",
                "multiplicity": 1,
                "deduplicated_from_two_child_endpoints": True,
            })

    first_route = children[0]["route"]
    last_route = children[-1]["route"]
    left_relation = _endpoint_relation(first_route["left_event"])
    right_relation = _endpoint_relation(last_route["right_event"])
    left_root = left_relation == "ZERO"
    right_root = right_relation == "ZERO"
    endpoint_multiplicity = {}
    if left_root:
        left_mult = first_route.get("endpoint_root_multiplicity", {}).get("left")
        if left_mult != 1:
            return {
                "status": "BLOCKED",
                "reason": "PHASE_SECTOR_EXTERNAL_LEFT_MULTIPLICITY_NOT_COMPOSABLE",
                "blocker": "PB-007-01",
            }
        endpoint_multiplicity["left"] = 1
    if right_root:
        right_mult = last_route.get("endpoint_root_multiplicity", {}).get("right")
        if right_mult != 1:
            return {
                "status": "BLOCKED",
                "reason": "PHASE_SECTOR_EXTERNAL_RIGHT_MULTIPLICITY_NOT_COMPOSABLE",
                "blocker": "PB-007-01",
            }
        endpoint_multiplicity["right"] = 1

    distinct_open = open_roots + len(internal_roots)
    total_closed = distinct_open + int(left_root) + int(right_root)
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_CHILD_EVENT_SUMMARY_COMPOSITION_WITH_INTERNAL_CUT_DEDUPLICATION",
        "distinct_roots_open": distinct_open,
        "left_endpoint_root": left_root,
        "right_endpoint_root": right_root,
        "total_distinct_roots_closed": total_closed,
        "all_roots_simple": True,
        "endpoint_root_multiplicity": endpoint_multiplicity,
        "internal_cut_roots": internal_roots,
        "internal_cut_root_count": len(internal_roots),
        "deduplication_rule": (
            "an exact ZERO relation shared by adjacent child endpoints is one parent-open "
            "root and requires exact multiplicity-one authority from both children"
        ),
        "left_event": first_route["left_event"],
        "right_event": last_route["right_event"],
    }


def _phase_sector_partition_route(
    cos_polys,
    sin_polys,
    offset,
    rate,
    source_parameter_id,
    parent_source_interval,
):
    try:
        rate = q(rate)
        if rate == 0:
            return None
        positive_harmonics, candidates = v25._candidate_anchors(cos_polys, sin_polys)
        if len(positive_harmonics) < 2 or not candidates:
            return None

        partition = _exact_sector_partition(offset, rate, candidates)
        if partition.get("status") != "CERTIFIED":
            return {
                "status": "BLOCKED",
                "reason": partition.get(
                    "reason", "PHASE_SECTOR_PARTITION_NOT_CERTIFIED"
                ),
                "blocker": "PB-007-01",
                "partition_certificate": partition,
            }

        cuts = [q(value) for value in partition["cuts"]]
        boundaries = [Fraction(0), *cuts, Fraction(1)]
        parent_left = q(parent_source_interval[0])
        parent_right = q(parent_source_interval[1])
        parent_width = parent_right - parent_left
        children = []

        for index, (left, right) in enumerate(zip(boundaries, boundaries[1:])):
            if not left < right:
                raise AssertionError("exact partition generated a zero-width child")
            child_cos = {
                int(h): _reparameterize_polynomial(poly, left, right)
                for h, poly in cos_polys.items()
            }
            child_sin = {
                int(h): _reparameterize_polynomial(poly, left, right)
                for h, poly in sin_polys.items()
            }
            child_offset = q(offset) + rate * left
            child_rate = rate * (right - left)
            child_spec = _child_spec(
                child_cos,
                child_sin,
                child_offset,
                child_rate,
                source_parameter_id,
            )
            child_result = v26.classify_required_analytic_event(child_spec)
            child_summary = _extract_child_route(child_result)
            if child_summary.get("status") == "RESOURCE_REFUSAL":
                return {
                    **child_summary,
                    "partition_certificate": partition,
                    "failed_child": index,
                    "is_truth_value": False,
                }
            if child_summary.get("status") != "CERTIFIED":
                return {
                    "status": "BLOCKED",
                    "reason": "PHASE_SECTOR_PARTITION_CHILD_REMAINS_UNCERTIFIED",
                    "blocker": "PB-007-01",
                    "partition_certificate": partition,
                    "failed_child": index,
                    "failed_local_interval": [str(left), str(right)],
                    "child_failure": child_summary,
                }

            global_left = parent_left + parent_width * left
            global_right = parent_left + parent_width * right
            children.append({
                "index": index,
                "local_interval": [left, right],
                "local_interval_serialized": [str(left), str(right)],
                "parent_source_interval": [str(global_left), str(global_right)],
                "phase_turn_law": {
                    "offset": str(child_offset),
                    "rate": str(child_rate),
                },
                "route_kind": child_summary["route_kind"],
                "route": child_summary["route"],
                "child_relation": child_summary["child_relation"],
                "source_parameter_id": source_parameter_id,
                "exact_reparameterization": "s=left+(right-left)*u",
            })

        composed = _compose_child_summaries(children)
        if composed.get("status") != "CERTIFIED":
            return {
                **composed,
                "partition_certificate": partition,
                "children": children,
            }

        return {
            "status": "CERTIFIED",
            "relation": V27_ROUTE,
            "source_parameter_id": source_parameter_id,
            "active_positive_harmonics": positive_harmonics,
            "partition_candidate_harmonics": candidates,
            "phase_turn_law_local": {
                "offset": str(q(offset)),
                "rate": str(rate),
            },
            "partition_certificate": partition,
            "child_count": len(children),
            "children": children,
            "composition_certificate": composed,
            "left_event": composed["left_event"],
            "right_event": composed["right_event"],
            "distinct_roots_open": composed["distinct_roots_open"],
            "left_endpoint_root": composed["left_endpoint_root"],
            "right_endpoint_root": composed["right_endpoint_root"],
            "total_distinct_roots_closed": composed["total_distinct_roots_closed"],
            "endpoint_root_multiplicity": composed["endpoint_root_multiplicity"],
            "all_roots_simple": composed["all_roots_simple"],
            "internal_cut_roots": composed["internal_cut_roots"],
            "finite_termination": (
                "all cuts are exact affine preimages of a finite set of rational half-magnitude "
                "sector boundaries; every child is classified once by preserved v8-v26 authority"
            ),
            "certificate_cut_semantics": (
                "internal cuts are exact proof-partition boundaries only and do not alter the "
                "original analytic event or source parameter"
            ),
            "caller_partition_trusted": False,
            "binary_float_used": False,
            "epsilon_used": False,
            "sampling_used": False,
            "numerical_trigonometry_used": False,
            "approximate_root_ordering_used": False,
            "arbitrary_subdivision_cap_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V27_EXACT_PARTITION_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def analyze_phase_sector_partition_event(spec):
    baseline = v26.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict) or baseline.get("status") == "CERTIFIED":
        return baseline
    if baseline.get("relation") != "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER":
        return baseline

    phase = baseline.get("phase_turn_law", {})
    rate = q(phase.get("rate", "0"))
    offset_global = q(phase.get("offset", "0"))
    upgraded = []
    unresolved = False

    for original_span in baseline.get("spans", []):
        span = dict(original_span)
        old_route = span.get("route", {})
        eligible = (
            old_route.get("status") == "BLOCKED"
            and "cos_polynomials" in span
            and "sin_polynomials" in span
        )
        if eligible:
            parent_left = q(span["source_interval"][0])
            parent_right = q(span["source_interval"][1])
            width = parent_right - parent_left
            local_offset = offset_global + rate * parent_left
            local_rate = rate * width
            cos_polys = {
                int(h): [q(value) for value in poly]
                for h, poly in span["cos_polynomials"].items()
            }
            sin_polys = {
                int(h): [q(value) for value in poly]
                for h, poly in span["sin_polynomials"].items()
            }
            replacement = _phase_sector_partition_route(
                cos_polys,
                sin_polys,
                local_offset,
                local_rate,
                baseline["source_parameter_id"],
                (parent_left, parent_right),
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION"
                span["route"] = replacement
                span["local_phase_turn_law"] = {
                    "offset": str(local_offset),
                    "rate": str(local_rate),
                    "local_parameter": "s=(u-lo)/(hi-lo)",
                    "shared_parameter": baseline["source_parameter_id"],
                }
        if span.get("route", {}).get("status") != "CERTIFIED":
            unresolved = True
        upgraded.append(span)

    statuses = [span.get("route", {}).get("status") for span in upgraded]
    if "RESOURCE_REFUSAL" in statuses:
        status = "RESOURCE_REFUSAL"
    elif "SEMANTIC_BLOCKER" in statuses:
        status = "SEMANTIC_BLOCKER"
    elif unresolved:
        status = "BLOCKED"
    else:
        status = "CERTIFIED"

    result = dict(baseline)
    result["status"] = status
    result["spans"] = upgraded
    result["relation"] = (
        "FINITE_EXACT_PIECEWISE_PHASE_SECTOR_PARTITION_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v27_phase_sector_partition_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "phase_sector_partition",
            "phase_sector_partition_certificate",
            "certificate_cuts",
            "cut_provenance",
            "partition_children",
            "child_certificates",
            "child_routes",
            "child_root_summaries",
            "composed_root_count",
            "internal_cut_roots",
            "internal_cut_deduplication",
            "partition_certificate",
            "partition_composition_certificate",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_phase_sector_partition_event(source_spec)
        return v26.classify_required_analytic_event(source_spec)
    return v26.classify_required_analytic_event(spec)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V27_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
