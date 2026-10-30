#!/usr/bin/env python3
"""MC-038/PB-007-01: exact two-span source-knot root-set composition.

Research-only. Reuses the landed #307 span-local shadow proof and the landed
#298 exact source-knot point/jet primitive. It deduplicates one exact shared
source-coordinate root in a two-span root *set*; it does not invent a global
smooth multiplicity across the source join.
"""
from __future__ import annotations

import copy
import hashlib
import json
from fractions import Fraction
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import pb00701_v27_endpoint_multiplicity as local307  # noqa: E402
import pb00701_rational_phase_point as point  # noqa: E402

SCHEMA = "radicadsac-pb00701-two-span-source-knot-root-set/1.0"
MAX_REPORT_BYTES = 131072

PINS = {
    HERE / "pb00701_v27_endpoint_multiplicity.py":
        "a6ad0144a241d1e914d8862f4f1e0c8600a1a923",
    HERE / "pb00701_rational_phase_point.py":
        "9fc344e045fa800fb24d30902a641e534a1e197b",
    HERE / "pb00701_transverse_trig_interval.py":
        "2320f92efe4316d865a89f6d848737e2c000ca4d",
    HERE / "pb00701-finite-owner-corpus-v54.json":
        "5841c331579489b25caef38cd412bdbf286f9134",
    ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json":
        "23de82f5240a72509f7afe4acd5948b65bc4ff13",
    ROOT / "handoffs/current-authority.json":
        "fa0233323a0804d8a5d3eb7cd892a274a6173fab",
}


class ResearchRefusal(ValueError):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


class ResourceRefusal(RuntimeError):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def require(ok, reason):
    if not ok:
        raise ResearchRefusal(reason)


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()


def pins():
    for path, expected in PINS.items():
        require(git_blob(path) == expected,
                "PINNED_SOURCE_DRIFT:" + path.name)
    local307.pins()


def reject_binary_float(value):
    if isinstance(value, float):
        raise ResearchRefusal("BINARY_FLOAT_SOURCE_AUTHORITY_FORBIDDEN")
    if isinstance(value, dict):
        for key, item in value.items():
            reject_binary_float(key)
            reject_binary_float(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            reject_binary_float(item)


def canonical(obj):
    try:
        return json.dumps(
            obj, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        )
    except (TypeError, ValueError, OverflowError) as exc:
        raise ResearchRefusal("NONCANONICAL_OR_NONJSON_EVIDENCE") from exc


def q(value):
    if isinstance(value, bool) or isinstance(value, float):
        raise ResearchRefusal("NONCANONICAL_RATIONAL")
    try:
        out = Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ResearchRefusal("NONCANONICAL_RATIONAL") from exc
    if isinstance(value, str) and str(out) != value:
        raise ResearchRefusal("NONCANONICAL_RATIONAL")
    return out


def trim(poly):
    out = [q(x) for x in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def peval(poly, x):
    x = q(x)
    acc = Fraction(0)
    for coeff in reversed(trim(poly)):
        acc = acc * x + coeff
    return acc


def local_poly_to_source(poly, source_left, source_right):
    """Exact p(s) -> p((t-L)/(R-L)) coefficient substitution."""
    p = trim(poly)
    left, right = q(source_left), q(source_right)
    width = right - left
    require(width > 0, "INVALID_SOURCE_SPAN_WIDTH")
    out = [Fraction(0)] * len(p)
    for degree, coeff in enumerate(p):
        if coeff == 0:
            continue
        scale = coeff / (width ** degree)
        for source_degree in range(degree + 1):
            out[source_degree] += (
                scale
                * Fraction(comb(degree, source_degree))
                * ((-left) ** (degree - source_degree))
            )
    result = trim(out)
    require(
        peval(result, left) == peval(p, Fraction(0))
        and peval(result, right) == peval(p, Fraction(1)),
        "LOCAL_TO_SOURCE_POLYNOMIAL_ENDPOINT_MISMATCH",
    )
    return result


def _baseline_source_span(span, global_offset, global_rate):
    left, right = map(q, span["source_interval"])
    local_phase = span.get("local_phase_turn_law", {})
    expected_offset = q(global_offset) + q(global_rate) * left
    expected_rate = q(global_rate) * (right - left)
    require(
        q(local_phase.get("offset")) == expected_offset
        and q(local_phase.get("rate")) == expected_rate,
        "LOWERED_SPAN_PHASE_NOT_SOURCE_BOUND",
    )
    cos_local = {
        int(h): trim(values)
        for h, values in span["cos_polynomials"].items()
    }
    sin_local = {
        int(h): trim(values)
        for h, values in span["sin_polynomials"].items()
    }
    terms = {}
    for harmonic in sorted(set(cos_local) | set(sin_local)):
        cp = local_poly_to_source(
            cos_local.get(harmonic, [0]), left, right
        )
        sp = local_poly_to_source(
            sin_local.get(harmonic, [0]), left, right
        )
        if cp == [0] and sp == [0]:
            continue
        terms[harmonic] = (tuple(cp), tuple(sp))
    require(terms, "EMPTY_SOURCE_SPAN_ANALYTIC_FUNCTION")
    try:
        source_span = point.interval.Span(
            left, right, q(global_offset), q(global_rate), terms
        )
    except point.interval.Refusal as exc:
        reason = str(exc)
        if "RESOURCE" in reason or "UNRESOLVED" in reason:
            raise ResourceRefusal(reason) from exc
        raise ResearchRefusal(reason) from exc

    # Independent exact check at both source endpoints: converting local
    # polynomial coordinates cannot change the represented analytic value.
    for harmonic, (cp_source, sp_source) in source_span.terms.items():
        cp_local = cos_local.get(harmonic, [0])
        sp_local = sin_local.get(harmonic, [0])
        require(
            peval(cp_source, left) == peval(cp_local, 0)
            and peval(cp_source, right) == peval(cp_local, 1)
            and peval(sp_source, left) == peval(sp_local, 0)
            and peval(sp_source, right) == peval(sp_local, 1),
            "SOURCE_COORDINATE_REPARAMETERIZATION_NOT_EXACT",
        )
    return source_span


def _exact_point(span, coordinate):
    try:
        result = point.point(span, coordinate)
    except (point.Refusal, point.interval.Refusal) as exc:
        reason = str(exc)
        if "RESOURCE" in reason or "UNRESOLVED" in reason or "LIMIT" in reason:
            raise ResourceRefusal(reason) from exc
        raise ResearchRefusal(reason) from exc
    require(
        result.get("source_binding_sha256") == point.span_binding(span),
        "POINT_WITNESS_SOURCE_BINDING_MISMATCH",
    )
    return result


def _exact_join(left_span, right_span, knot):
    try:
        result = point.compose_knot(left_span, right_span, knot)
    except (point.Refusal, point.interval.Refusal) as exc:
        reason = str(exc)
        if "RESOURCE" in reason or "UNRESOLVED" in reason or "LIMIT" in reason:
            raise ResourceRefusal(reason) from exc
        raise ResearchRefusal(reason) from exc
    require(
        result.get("status") == "EXACT_SINGLE_SOURCE_KNOT_ZERO",
        "SHARED_SOURCE_KNOT_NOT_EXACT_SINGLE_ZERO",
    )
    require(result.get("physical_zero_events") == 1,
            "SHARED_SOURCE_KNOT_EVENT_COUNT_NOT_ONE")
    require(result.get("global_smooth_multiplicity_claimed") is False,
            "SOURCE_KNOT_GLOBAL_MULTIPLICITY_MUST_REMAIN_UNCLAIMED")
    return result


def _endpoint_is_root(event):
    status = event.get("status")
    if status == "EXACT_RATIONAL_POINT_EVENT":
        return True
    if status == "EXACT_NONZERO_RATIONAL_POINT":
        return False
    raise ResearchRefusal("EXTERIOR_ENDPOINT_POINT_STATUS_UNSUPPORTED")


def _route_open_summary(shadow_span):
    route = shadow_span.get("route", {})
    require(route.get("status") == "CERTIFIED",
            "SPAN_LOCAL_ROUTE_NOT_CERTIFIED")
    if shadow_span.get("shadow_upgrade_applied"):
        require(
            route.get("relation")
            == "EXACT_V27_SHADOW_COMPOSITION_WITH_POINT_JET_ENDPOINT_MULTIPLICITY",
            "UNEXPECTED_SHADOW_SPAN_ROUTE",
        )
        source = route.get("composition", {})
        require(source.get("status") == "CERTIFIED",
                "V27_CHILD_COMPOSITION_NOT_CERTIFIED")
        kind = "V27_SHADOW_COMPOSITION"
    else:
        source = route
        kind = shadow_span.get("route_kind")

    open_count = source.get("distinct_roots_open")
    require(
        type(open_count) is int and open_count >= 0,
        "SPAN_LOCAL_EXACT_OPEN_ROOT_COUNT_MISSING",
    )
    multiple_open = source.get("multiple_roots_open")
    if multiple_open is not None:
        require(
            type(multiple_open) is int and 0 <= multiple_open <= open_count,
            "SPAN_LOCAL_MULTIPLE_OPEN_ROOT_COUNT_INVALID",
        )
    return {
        "route_kind": kind,
        "distinct_roots_open": open_count,
        "multiple_roots_open": multiple_open,
        "span_local_route_status": "CERTIFIED",
    }


def _route_endpoint_multiplicity(shadow_span, side):
    route = shadow_span.get("route", {})
    if shadow_span.get("shadow_upgrade_applied"):
        comp = route.get("composition", {})
        root_flag = comp.get(f"{side}_endpoint_root")
        mults = comp.get("endpoint_root_multiplicity", {})
        if root_flag is True:
            value = mults.get(side)
            return int(value) if value is not None else None
        return None

    event = route.get(f"{side}_event")
    if isinstance(event, dict) and event.get("relation") == "ZERO":
        value = event.get("multiplicity")
        return int(value) if value is not None else None
    return None


def _require_local_shared_endpoint_records(
        left_shadow, right_shadow, join):
    left_mult = _route_endpoint_multiplicity(left_shadow, "right")
    right_mult = _route_endpoint_multiplicity(right_shadow, "left")
    require(
        left_mult is not None and right_mult is not None,
        "SPAN_LOCAL_SHARED_ENDPOINT_MULTIPLICITY_MISSING",
    )
    require(
        left_mult == join["left_one_sided_order"]
        and right_mult == join["right_one_sided_order"],
        "SPAN_LOCAL_SHARED_ENDPOINT_MULTIPLICITY_DISAGREES_WITH_EXACT_JOIN",
    )
    return {
        "left_span_right_endpoint_multiplicity": left_mult,
        "right_span_left_endpoint_multiplicity": right_mult,
        "same_source_coordinate_root_records": 2,
        "deduplicated_distinct_source_root_events": 1,
    }


def analyze_source(spec):
    pins()
    reject_binary_float(spec)
    require(isinstance(spec, dict), "SOURCE_RECORD_NOT_OBJECT")

    local_report = local307.attempt(spec)
    if local_report.get("status") == "RESOURCE_REFUSAL":
        raise ResourceRefusal(
            "SPAN_LOCAL_307_RESOURCE_REFUSAL:"
            + str(local_report.get("reason"))
        )
    require(
        local_report.get("status")
        == "EXACT_SOURCE_BOUND_V27_ENDPOINT_MULTIPLICITY_COMPOSITION_RESEARCH",
        "SOURCE_LACKS_307_SPAN_LOCAL_COMPLETENESS",
    )
    require(local_report.get("all_shadow_span_routes_certified") is True,
            "SOURCE_307_SPAN_LOCAL_ROUTES_NOT_ALL_CERTIFIED")

    baseline = local307.v27.classify_required_analytic_event(spec)
    require(isinstance(baseline, dict), "BASELINE_V27_RESULT_NOT_STRUCTURED")
    spans = baseline.get("spans", [])
    shadows = local_report.get("shadow_spans", [])
    require(
        len(spans) == len(shadows) == 2,
        "TWO_SPAN_SOURCE_REQUIRED",
    )
    require(
        [span.get("source_interval") for span in spans]
        == [span.get("source_interval") for span in shadows],
        "BASELINE_AND_SHADOW_SPAN_INTERVAL_MISMATCH",
    )

    source_id = spec.get("source_parameter_id")
    require(
        isinstance(source_id, str)
        and source_id
        and baseline.get("source_parameter_id") == source_id
        and local_report.get("source_parameter_id") == source_id,
        "SOURCE_PARAMETER_ID_MISMATCH",
    )
    source_lo, source_hi = q(spec["parameter_lo"]), q(spec["parameter_hi"])
    offset, rate = q(spec["phase_turn_offset"]), q(spec["phase_turn_rate"])

    left_span = _baseline_source_span(spans[0], offset, rate)
    right_span = _baseline_source_span(spans[1], offset, rate)
    knot = left_span.right
    require(
        left_span.left == source_lo
        and right_span.right == source_hi
        and left_span.right == right_span.left
        and source_lo < knot < source_hi,
        "SOURCE_SPANS_DO_NOT_FORM_EXACT_TWO_SPAN_PARTITION",
    )

    left_roots = _route_open_summary(shadows[0])
    right_roots = _route_open_summary(shadows[1])
    join = _exact_join(left_span, right_span, knot)
    shared_records = _require_local_shared_endpoint_records(
        shadows[0], shadows[1], join
    )

    left_endpoint = _exact_point(left_span, source_lo)
    right_endpoint = _exact_point(right_span, source_hi)
    left_exterior_root = _endpoint_is_root(left_endpoint)
    right_exterior_root = _endpoint_is_root(right_endpoint)

    distinct_open = (
        left_roots["distinct_roots_open"]
        + right_roots["distinct_roots_open"]
    )
    total_distinct = (
        distinct_open
        + int(left_exterior_root)
        + int(right_exterior_root)
        + 1
    )
    require(total_distinct >= 1, "IMPOSSIBLE_GLOBAL_ROOT_COUNT")

    pins()
    return {
        "schema": SCHEMA,
        "status": "EXACT_SOURCE_BOUND_TWO_SPAN_KNOT_ROOT_SET_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_sha256": local307.source_sha256(spec),
        "source_parameter_id": source_id,
        "source_interval": [str(source_lo), str(source_hi)],
        "phase_turn_law": {"offset": str(offset), "rate": str(rate)},
        "span_count": 2,
        "span_local_root_summaries": [left_roots, right_roots],
        "shared_source_knot": {
            **copy.deepcopy(join),
            "source_coordinate": str(knot),
            "span_local_records": shared_records,
        },
        "left_exterior_point": left_endpoint,
        "right_exterior_point": right_endpoint,
        "left_exterior_is_root": left_exterior_root,
        "right_exterior_is_root": right_exterior_root,
        "distinct_roots_in_open_span_interiors": distinct_open,
        "shared_source_knot_distinct_root_events": 1,
        "global_distinct_roots_closed_source": total_distinct,
        "global_source_knot_deduplication_established": True,
        "global_multispan_root_count_established": True,
        "global_smooth_knot_multiplicity_claimed": False,
        "global_multiple_root_count_claimed": False,
        "historical_v54_admitted": False,
        "historical_v54_dispositions_changed": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_brep_or_step_qualified": False,
        "production_authorized": False,
    }


def analyze_frozen_case(case_id):
    case = local307.load_frozen_case(case_id)
    report = analyze_source(case["spec"])
    report["frozen_case_id"] = case_id
    report["frozen_origin"] = case.get("origin")
    report["historical_v54_disposition"] = case["expected"].get(
        "v54_disposition"
    )
    return report


def nontruth(reason, status="BLOCKED"):
    return {
        "schema": SCHEMA,
        "status": status,
        "reason": reason,
        "is_truth_value": False,
        "global_source_knot_deduplication_established": False,
        "global_multispan_root_count_established": False,
        "historical_v54_admitted": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "production_authorized": False,
    }


def attempt(spec):
    try:
        return analyze_source(spec)
    except ResourceRefusal as exc:
        return nontruth(exc.reason, "RESOURCE_REFUSAL")
    except (ResearchRefusal, ValueError, KeyError, IndexError, TypeError,
            ZeroDivisionError, point.Refusal, point.interval.Refusal) as exc:
        reason = str(exc)
        status = (
            "RESOURCE_REFUSAL"
            if any(tag in reason for tag in ("RESOURCE", "UNRESOLVED", "LIMIT"))
            else "BLOCKED"
        )
        return nontruth(reason, status)
    except (MemoryError, RecursionError, OverflowError) as exc:
        return nontruth(type(exc).__name__, "RESOURCE_REFUSAL")


def validate_report(spec, submitted):
    try:
        claimed = canonical(submitted)
        if len(claimed) > MAX_REPORT_BYTES:
            return nontruth("SUBMITTED_REPORT_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
        checked = attempt(spec)
        require(
            checked.get("status")
            == "EXACT_SOURCE_BOUND_TWO_SPAN_KNOT_ROOT_SET_RESEARCH",
            "SOURCE_BOUND_TWO_SPAN_ROOT_SET_PROOF_MISSING",
        )
        require(claimed == canonical(checked),
                "FORGED_TWO_SPAN_SOURCE_KNOT_ROOT_SET_REPORT")
        return checked
    except ResearchRefusal as exc:
        return nontruth(exc.reason)
    except (ValueError, TypeError, OverflowError) as exc:
        return nontruth(str(exc))
