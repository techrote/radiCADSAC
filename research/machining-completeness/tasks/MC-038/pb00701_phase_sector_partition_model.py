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
EE = v26.EE
q = v26.q

V27_ROUTE = "EXACT_FINITE_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION"

# Exact boundary residues (turns modulo one) used by the historical half-magnitude
# sector certificates.  These are certificate cuts, never approximate event roots.
SECTOR_BOUNDARIES = {
    "COS": (Fraction(1, 6), Fraction(1, 3), Fraction(2, 3), Fraction(5, 6)),
    "SIN": (Fraction(1, 12), Fraction(5, 12), Fraction(7, 12), Fraction(11, 12)),
}


class PhaseSectorPartitionRefusal(RuntimeError):
    """Exact-resource refusal.  Refusal is never a mathematical truth value."""


def _trim(poly):
    return v25._trim([q(value) for value in poly])


def _floor(value):
    value = q(value)
    return value.numerator // value.denominator


def _ceil(value):
    return -_floor(-q(value))


def _active_positive_harmonics(cos_polys, sin_polys):
    return sorted(
        int(h) for h in (set(cos_polys) | set(sin_polys))
        if int(h) > 0 and (
            _trim(cos_polys.get(h, [0])) != [0]
            or _trim(sin_polys.get(h, [0])) != [0]
        )
    )


def exact_sector_cuts(offset, rate, harmonics):
    """Return every interior exact-rational crossing of a historical sector boundary."""
    try:
        offset = q(offset)
        rate = q(rate)
        if rate == 0:
            return {"status": "CERTIFIED", "cuts": [], "crossings": []}
        cuts = {}
        for harmonic in sorted(set(int(h) for h in harmonics if int(h) > 0)):
            t0 = Fraction(harmonic) * offset
            tr = Fraction(harmonic) * rate
            t1 = t0 + tr
            lo, hi = min(t0, t1), max(t0, t1)
            for component, residues in SECTOR_BOUNDARIES.items():
                for residue in residues:
                    first = _floor(lo - residue) - 1
                    last = _ceil(hi - residue) + 1
                    for translate in range(first, last + 1):
                        boundary_turn = residue + translate
                        if not lo < boundary_turn < hi:
                            continue
                        source_cut = (boundary_turn - t0) / tr
                        if not Fraction(0) < source_cut < Fraction(1):
                            continue
                        entry = cuts.setdefault(source_cut, [])
                        entry.append({
                            "harmonic": harmonic,
                            "component": component,
                            "boundary_residue": str(residue),
                            "boundary_turn": str(boundary_turn),
                            "harmonic_phase_rate": str(tr),
                        })
        ordered = sorted(cuts)
        return {
            "status": "CERTIFIED",
            "relation": "FINITE_EXACT_RATIONAL_HALF_MAGNITUDE_SECTOR_CROSSINGS",
            "cuts": [str(value) for value in ordered],
            "crossings": [
                {"source_cut": str(value), "causes": cuts[value]}
                for value in ordered
            ],
            "finite_termination": "finite active harmonic lattice times eight rational boundary residues over a bounded rational turn interval",
            "caller_cuts_trusted": False,
            "binary_float_used": False,
            "epsilon_used": False,
            "sampling_used": False,
            "numerical_trigonometry_used": False,
            "adaptive_refinement_used": False,
            "arbitrary_subdivision_cap_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V27_SECTOR_CUT_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _reparameterize_polynomial(poly, left, right):
    """Exact coefficients of p(left + (right-left) u) in ascending powers of u."""
    poly = _trim(poly)
    left, right = q(left), q(right)
    width = right - left
    if width <= 0:
        raise ValueError("child interval must have positive exact width")
    out = [Fraction(0)] * len(poly)
    for k, coefficient in enumerate(poly):
        for j in range(k + 1):
            out[j] += coefficient * Fraction(comb(k, j)) * left ** (k - j) * width ** j
    return _trim(out)


def _power_spline(poly):
    """Encode an exact power-basis polynomial as one clamped rational Bezier span."""
    poly = _trim(poly)
    degree = len(poly) - 1
    if degree == 0:
        return {"degree": 0, "knots": ["0", "1"], "controls": [str(poly[0])]}
    controls = []
    for j in range(degree + 1):
        value = Fraction(0)
        for k in range(j + 1):
            if k < len(poly):
                value += poly[k] * Fraction(comb(j, k), comb(degree, k))
        controls.append(str(value))
    return {
        "degree": degree,
        "knots": ["0"] * (degree + 1) + ["1"] * (degree + 1),
        "controls": controls,
    }


def _child_spec(cos_polys, sin_polys, offset, rate, left, right, source_parameter_id):
    left, right = q(left), q(right)
    width = right - left
    child_cos = {
        int(h): _reparameterize_polynomial(poly, left, right)
        for h, poly in cos_polys.items()
    }
    child_sin = {
        int(h): _reparameterize_polynomial(poly, left, right)
        for h, poly in sin_polys.items()
    }
    spec = {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": {
            str(h): _power_spline(poly)
            for h, poly in sorted(child_cos.items()) if _trim(poly) != [0]
        },
        "sin_splines": {
            str(h): _power_spline(poly)
            for h, poly in sorted(child_sin.items()) if _trim(poly) != [0]
        },
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": str(q(offset) + q(rate) * left),
        "phase_turn_rate": str(q(rate) * width),
        "source_parameter_id": source_parameter_id,
    }
    return spec, child_cos, child_sin


def _single_span_child_summary(result, child_cos, child_sin, child_offset, child_rate):
    """Extract only composable exact event evidence; otherwise fail closed."""
    if not isinstance(result, dict):
        return {"status": "BLOCKED", "reason": "V27_CHILD_RESULT_NOT_STRUCTURED", "blocker": "PB-007-01"}
    if result.get("status") != "CERTIFIED":
        return {
            "status": result.get("status", "BLOCKED"),
            "reason": "V27_CHILD_NOT_CERTIFIED",
            "blocker": "PB-007-01" if result.get("status") != "RESOURCE_REFUSAL" else None,
            "child_result": result,
            **({"is_truth_value": False} if result.get("status") == "RESOURCE_REFUSAL" else {}),
        }
    spans = result.get("spans", [])
    if len(spans) != 1:
        return {
            "status": "BLOCKED",
            "reason": "V27_CHILD_RELOWERING_NOT_SINGLE_EXACT_SPAN",
            "blocker": "PB-007-01",
            "child_span_count": len(spans),
        }
    route = spans[0].get("route", {})
    if route.get("status") != "CERTIFIED":
        return {"status": "BLOCKED", "reason": "V27_CHILD_ROUTE_NOT_CERTIFIED", "blocker": "PB-007-01"}
    if "distinct_roots_open" not in route:
        return {
            "status": "BLOCKED",
            "reason": "V27_CHILD_LACKS_EXACT_OPEN_ROOT_COUNT",
            "blocker": "PB-007-01",
            "child_route_relation": route.get("relation"),
        }
    open_roots = int(route["distinct_roots_open"])
    if open_roots < 0:
        return {"status": "SEMANTIC_BLOCKER", "reason": "NEGATIVE_CHILD_ROOT_COUNT"}

    left_event = v19._endpoint_relation(child_cos, child_sin, Fraction(0), q(child_offset))
    if left_event.get("status") == "RESOURCE_REFUSAL":
        return left_event
    right_event = v19._endpoint_relation(child_cos, child_sin, Fraction(1), q(child_offset) + q(child_rate))
    if right_event.get("status") == "RESOURCE_REFUSAL":
        return right_event

    def endpoint_multiplicity(side, event):
        if event.get("relation") != "ZERO":
            return None
        endpoint = route.get("endpoint_root_multiplicity", {})
        if side in endpoint:
            return int(endpoint[side])
        if route.get("all_roots_simple") is True:
            return 1
        return None

    left_mult = endpoint_multiplicity("left", left_event)
    right_mult = endpoint_multiplicity("right", right_event)
    if left_event.get("relation") == "ZERO" and left_mult is None:
        return {
            "status": "BLOCKED",
            "reason": "V27_CHILD_LEFT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE",
            "blocker": "PB-007-01",
            "child_route_relation": route.get("relation"),
        }
    if right_event.get("relation") == "ZERO" and right_mult is None:
        return {
            "status": "BLOCKED",
            "reason": "V27_CHILD_RIGHT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE",
            "blocker": "PB-007-01",
            "child_route_relation": route.get("relation"),
        }
    if open_roots > 0 and route.get("all_roots_simple") is not True and "multiple_roots_open" not in route:
        return {
            "status": "BLOCKED",
            "reason": "V27_CHILD_OPEN_ROOT_MULTIPLICITY_NOT_COMPOSABLE",
            "blocker": "PB-007-01",
            "child_route_relation": route.get("relation"),
        }
    multiple_open = int(route.get("multiple_roots_open", 0 if route.get("all_roots_simple") is True else 0))
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_COMPOSABLE_CHILD_EVENT_SUMMARY",
        "child_route_kind": spans[0].get("route_kind"),
        "child_route_relation": route.get("relation"),
        "left_event": left_event,
        "right_event": right_event,
        "left_endpoint_multiplicity": left_mult,
        "right_endpoint_multiplicity": right_mult,
        "distinct_roots_open": open_roots,
        "multiple_roots_open": multiple_open,
        "all_roots_simple": bool(route.get("all_roots_simple", open_roots == 0 and multiple_open == 0)),
    }


def _compose_child_summaries(children):
    if not children:
        return {"status": "BLOCKED", "reason": "V27_EMPTY_CHILD_PARTITION", "blocker": "PB-007-01"}
    for child in children:
        summary = child.get("summary", {})
        if summary.get("status") != "CERTIFIED":
            return {
                "status": summary.get("status", "BLOCKED"),
                "reason": summary.get("reason", "V27_CHILD_SUMMARY_NOT_CERTIFIED"),
                "blocker": "PB-007-01" if summary.get("status") != "RESOURCE_REFUSAL" else None,
                "failed_child_interval": child.get("parent_local_interval"),
                "failed_child_summary": summary,
                **({"is_truth_value": False} if summary.get("status") == "RESOURCE_REFUSAL" else {}),
            }

    internal_roots = []
    for index in range(len(children) - 1):
        left = children[index]
        right = children[index + 1]
        le = left["summary"]["right_event"]
        re = right["summary"]["left_event"]
        if le.get("relation") != re.get("relation"):
            return {
                "status": "SEMANTIC_BLOCKER",
                "reason": "V27_INTERNAL_CUT_ENDPOINT_RELATION_MISMATCH",
                "cut": left["parent_local_interval"][1],
                "left_relation": le.get("relation"),
                "right_relation": re.get("relation"),
            }
        if le.get("relation") == "ZERO":
            lm = left["summary"].get("right_endpoint_multiplicity")
            rm = right["summary"].get("left_endpoint_multiplicity")
            if lm is None or rm is None or int(lm) != int(rm):
                return {
                    "status": "BLOCKED",
                    "reason": "V27_INTERNAL_CUT_ROOT_MULTIPLICITY_MISMATCH_OR_MISSING",
                    "blocker": "PB-007-01",
                    "cut": left["parent_local_interval"][1],
                    "left_multiplicity": lm,
                    "right_multiplicity": rm,
                }
            internal_roots.append({
                "source_cut": left["parent_local_interval"][1],
                "multiplicity": int(lm),
                "deduplicated_from_two_child_endpoints": True,
            })

    open_roots = sum(child["summary"]["distinct_roots_open"] for child in children) + len(internal_roots)
    multiple_open = sum(child["summary"]["multiple_roots_open"] for child in children)
    multiple_open += sum(1 for root in internal_roots if root["multiplicity"] > 1)
    left_event = children[0]["summary"]["left_event"]
    right_event = children[-1]["summary"]["right_event"]
    left_root = left_event.get("relation") == "ZERO"
    right_root = right_event.get("relation") == "ZERO"
    endpoint_multiplicity = {}
    if left_root:
        endpoint_multiplicity["left"] = children[0]["summary"]["left_endpoint_multiplicity"]
    if right_root:
        endpoint_multiplicity["right"] = children[-1]["summary"]["right_endpoint_multiplicity"]
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_CHILD_EVENT_COMPOSITION_WITH_INTERNAL_CUT_DEDUPLICATION",
        "distinct_roots_open": open_roots,
        "multiple_roots_open": multiple_open,
        "left_endpoint_root": left_root,
        "right_endpoint_root": right_root,
        "total_distinct_roots_closed": open_roots + int(left_root) + int(right_root),
        "endpoint_root_multiplicity": endpoint_multiplicity,
        "all_roots_simple": multiple_open == 0 and all(
            child["summary"].get("all_roots_simple") for child in children
        ) and all(root["multiplicity"] == 1 for root in internal_roots),
        "internal_cut_roots": internal_roots,
        "internal_cut_root_counted_once": True,
        "multiplicity_invented_from_root_count": False,
    }


def _partition_route(cos_polys, sin_polys, offset, rate, source_parameter_id, parent_interval):
    harmonics = _active_positive_harmonics(cos_polys, sin_polys)
    if not harmonics or q(rate) == 0:
        return None
    cut_cert = exact_sector_cuts(offset, rate, harmonics)
    if cut_cert.get("status") != "CERTIFIED":
        return cut_cert
    cuts = [q(value) for value in cut_cert["cuts"]]
    if not cuts:
        return None
    boundaries = [Fraction(0), *cuts, Fraction(1)]
    children = []
    for left, right in zip(boundaries, boundaries[1:]):
        if not left < right:
            continue
        child_spec, child_cos, child_sin = _child_spec(
            cos_polys, sin_polys, offset, rate, left, right, source_parameter_id
        )
        child_result = v26.classify_required_analytic_event(child_spec)
        if child_result.get("status") == "RESOURCE_REFUSAL":
            return {
                "status": "RESOURCE_REFUSAL",
                "reason": "PB00701_V27_CHILD_RESOURCE_REFUSAL",
                "is_truth_value": False,
                "failed_child_interval": [str(left), str(right)],
                "child_result": child_result,
            }
        child_offset = q(offset) + q(rate) * left
        child_rate = q(rate) * (right - left)
        summary = _single_span_child_summary(
            child_result, child_cos, child_sin, child_offset, child_rate
        )
        parent_lo, parent_hi = q(parent_interval[0]), q(parent_interval[1])
        parent_width = parent_hi - parent_lo
        children.append({
            "parent_local_interval": [str(left), str(right)],
            "parent_source_interval": [
                str(parent_lo + parent_width * left),
                str(parent_lo + parent_width * right),
            ],
            "exact_parent_to_child_map": f"s={left}+({right-left})*u",
            "phase_turn_law_child": {"offset": str(child_offset), "rate": str(child_rate)},
            "child_result": child_result,
            "summary": summary,
        })
        if summary.get("status") != "CERTIFIED":
            return {
                "status": summary.get("status", "BLOCKED"),
                "reason": summary.get("reason", "V27_CHILD_NOT_COMPOSABLE"),
                "blocker": "PB-007-01" if summary.get("status") != "RESOURCE_REFUSAL" else None,
                "sector_cut_certificate": cut_cert,
                "children": children,
                **({"is_truth_value": False} if summary.get("status") == "RESOURCE_REFUSAL" else {}),
            }
    composition = _compose_child_summaries(children)
    if composition.get("status") != "CERTIFIED":
        return {
            **composition,
            "sector_cut_certificate": cut_cert,
            "children": children,
        }
    return {
        "status": "CERTIFIED",
        "relation": V27_ROUTE,
        "source_parameter_id": source_parameter_id,
        "parent_source_interval": [str(q(parent_interval[0])), str(q(parent_interval[1]))],
        "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(q(rate))},
        "active_positive_harmonics": harmonics,
        "sector_cut_certificate": cut_cert,
        "children": children,
        "child_count": len(children),
        "all_children_reclassified_by_complete_v8_v26_classifier": True,
        "composition": composition,
        **{key: composition[key] for key in (
            "distinct_roots_open", "multiple_roots_open", "left_endpoint_root",
            "right_endpoint_root", "total_distinct_roots_closed", "endpoint_root_multiplicity",
            "all_roots_simple", "internal_cut_roots",
        )},
        "certificate_cuts_are_event_neutral": True,
        "caller_certificate_trusted": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
        "adaptive_refinement_used": False,
        "arbitrary_subdivision_cap_used": False,
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
            left = q(span["source_interval"][0])
            right = q(span["source_interval"][1])
            width = right - left
            local_offset = offset_global + rate * left
            local_rate = rate * width
            cos_polys = {
                int(h): [q(value) for value in poly]
                for h, poly in span["cos_polynomials"].items()
            }
            sin_polys = {
                int(h): [q(value) for value in poly]
                for h, poly in span["sin_polynomials"].items()
            }
            replacement = _partition_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"], (left, right),
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION"
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
            "phase_sector_partition", "phase_sector_partition_certificate", "sector_cuts",
            "sector_cut_certificate", "certificate_cuts", "partition", "partition_certificate",
            "children", "child_certificates", "child_results", "child_root_counts",
            "child_endpoint_events", "internal_cut_roots", "deduplication", "deduplication_assertion",
            "root_count", "root_certificate", "endpoint_events", "multiplicity", "multiplicity_certificate",
            "phase_sector", "sector_certificate", "pointwise_component_cone_certificate",
            "sturm_certificate", "sturm_root_count",
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
