#!/usr/bin/env python3
"""MC-038/PB-007-01: exact endpoint multiplicity for a live V27 child blocker.

Research-only shadow composition. Missing endpoint multiplicity may be supplied
only by a source-bound exact rational-phase point jet. Historical V27/v54
sources and dispositions are not mutated or promoted.
"""
from __future__ import annotations

import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import pb00701_phase_sector_partition_model as v27  # noqa: E402
import pb00701_rational_phase_point as point  # noqa: E402
import pb00701_rational_turn_model as v6  # noqa: E402

SCHEMA = "radicadsac-pb00701-v27-endpoint-multiplicity/1.0"
MAX_REPORT_BYTES = 131072
TARGET_REASONS = {
    "V27_CHILD_LEFT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE",
    "V27_CHILD_RIGHT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE",
}
PINS = {
    HERE / "pb00701_phase_sector_partition_model.py":
        "6211e658621af7100c2509dcafdaeaf348e48d46",
    HERE / "pb00701_pointwise_component_cone_model.py":
        "a303bba600fa83a1b55c8e113ce1ec7d06f68590",
    HERE / "pb00701_rational_phase_point.py":
        "9fc344e045fa800fb24d30902a641e534a1e197b",
    HERE / "pb00701_rational_turn_model.py":
        "a1316ff0f71b2d7aa80807843a74fd8280779cb2",
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


def source_sha256(spec):
    reject_binary_float(spec)
    return hashlib.sha256(canonical(spec).encode("ascii")).hexdigest()


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


def load_frozen_case(case_id):
    pins()
    corpus = json.loads(
        (HERE / "pb00701-finite-owner-corpus-v54.json").read_text()
    )
    matches = [case for case in corpus["cases"] if case["id"] == case_id]
    require(len(matches) == 1, "FROZEN_CASE_ID_NOT_UNIQUE")
    return copy.deepcopy(matches[0])


def _point_span(child_cos, child_sin, offset, rate):
    terms = {}
    for harmonic in sorted(set(child_cos) | set(child_sin)):
        cp = tuple(q(x) for x in child_cos.get(harmonic, [0]))
        sp = tuple(q(x) for x in child_sin.get(harmonic, [0]))
        if v27._trim(cp) == [0] and v27._trim(sp) == [0]:
            continue
        terms[int(harmonic)] = (cp, sp)
    require(terms, "EMPTY_CHILD_ANALYTIC_FUNCTION")
    try:
        return point.interval.Span(
            Fraction(0), Fraction(1), q(offset), q(rate), terms
        )
    except point.interval.Refusal as exc:
        reason = str(exc)
        if "RESOURCE" in reason or "UNSUPPORTED" in reason:
            raise ResourceRefusal(reason) from exc
        raise ResearchRefusal(reason) from exc


def _exact_endpoint_witness(child_cos, child_sin, offset, rate, side):
    require(side in ("left", "right"), "INVALID_ENDPOINT_SIDE")
    span = _point_span(child_cos, child_sin, offset, rate)
    coordinate = Fraction(0) if side == "left" else Fraction(1)
    try:
        witness = point.point(span, coordinate)
    except (point.Refusal, point.interval.Refusal) as exc:
        reason = str(exc)
        if "RESOURCE" in reason or "UNRESOLVED" in reason or "LIMIT" in reason:
            raise ResourceRefusal(reason) from exc
        raise ResearchRefusal(reason) from exc
    require(
        witness.get("coordinate") == str(coordinate),
        "ENDPOINT_JET_COORDINATE_MISMATCH",
    )
    require(
        witness.get("source_binding_sha256") == point.span_binding(span),
        "ENDPOINT_JET_SOURCE_BINDING_MISMATCH",
    )
    return witness


def _endpoint_relation_sign(event):
    relation = event.get("relation")
    if relation == "POSITIVE":
        return 1
    if relation == "NEGATIVE":
        return -1
    if relation == "ZERO":
        return 0
    return None


def _checked_endpoint_multiplicity(
        side, event, route, child_cos, child_sin, offset, rate):
    """Return exact multiplicity and point witness for a ZERO endpoint.

    Existing route multiplicity is never replaced silently: if present, the
    independent point jet must agree exactly.
    """
    relation = event.get("relation")
    witness = _exact_endpoint_witness(
        child_cos, child_sin, offset, rate, side
    )
    if relation != "ZERO":
        require(
            witness.get("status") == "EXACT_NONZERO_RATIONAL_POINT",
            "ENDPOINT_RELATION_AND_EXACT_POINT_DISAGREE",
        )
        require(
            witness.get("value_sign") == _endpoint_relation_sign(event),
            "ENDPOINT_SIGN_AND_EXACT_POINT_DISAGREE",
        )
        return None, witness, "EXACT_NONZERO_ENDPOINT_RECHECK"

    require(
        witness.get("status") == "EXACT_RATIONAL_POINT_EVENT",
        "ZERO_ENDPOINT_LACKS_EXACT_POINT_EVENT",
    )
    order = witness.get("one_sided_order")
    require(type(order) is int and 1 <= order <= point.MAX_JET_ORDER,
            "INVALID_EXACT_ENDPOINT_ROOT_ORDER")
    require(
        witness.get("first_nonzero_derivative_order") == order,
        "ENDPOINT_JET_ORDER_INCONSISTENT",
    )

    endpoint = route.get("endpoint_root_multiplicity", {})
    route_value = None
    if side in endpoint:
        route_value = int(endpoint[side])
    elif route.get("all_roots_simple") is True:
        route_value = 1

    if route_value is not None:
        require(
            route_value == order,
            "ROUTE_AND_POINT_ENDPOINT_MULTIPLICITY_DISAGREE",
        )
        method = "EXISTING_ROUTE_MULTIPLICITY_RECHECKED_BY_EXACT_POINT_JET"
    else:
        method = "MISSING_ROUTE_MULTIPLICITY_SUPPLIED_BY_EXACT_POINT_JET"
    return order, witness, method


def _endpoint_is_tan_half_pole(turn):
    try:
        v6.rational_turn_endpoint(q(turn))
        return False
    except ValueError as exc:
        if "TAN_HALF_POLE" in str(exc):
            return True
        raise


def _constant_harmonic_coefficients(child_cos, child_sin):
    cos = {}
    sin = {}
    for harmonic in sorted(set(child_cos) | set(child_sin)):
        cp = v27._trim(child_cos.get(harmonic, [0]))
        sp = v27._trim(child_sin.get(harmonic, [0]))
        require(
            len(cp) == 1 and len(sp) == 1,
            "V6_ENDPOINT_POLE_NORMALIZATION_REQUIRES_CONSTANT_MODULATION",
        )
        if cp[0] != 0:
            cos[int(harmonic)] = cp[0]
        if sp[0] != 0:
            sin[int(harmonic)] = sp[0]
    require(cos or sin, "EMPTY_V6_CONSTANT_MODULATION")
    return cos, sin


def _normalized_v6_endpoint_pole_route(
        blocked_child_result, child_cos, child_sin,
        child_offset, child_rate, source_parameter_id):
    """Normalize one endpoint tan-half pole by an exact half-turn source shift."""
    spans = blocked_child_result.get("spans", [])
    require(
        blocked_child_result.get("status") == "BLOCKED"
        and len(spans) == 1
        and spans[0].get("route_kind") == "DELEGATED_V6_CONSTANT_MODULATION"
        and spans[0].get("route", {}).get("status") == "BLOCKED"
        and spans[0].get("route", {}).get("reason")
        == "TAN_HALF_POLE_REQUIRES_EXACT_WINDOW_PARTITION",
        "CHILD_NOT_AT_EXACT_V6_ENDPOINT_POLE_BLOCKER",
    )
    rate = q(child_rate)
    offset = q(child_offset)
    require(rate > 0, "V6_ENDPOINT_POLE_NORMALIZATION_REQUIRES_POSITIVE_PHASE_RATE")
    lo, hi = offset, offset + rate
    require(
        Fraction(0) < hi - lo < Fraction(1, 2),
        "V6_ENDPOINT_POLE_WINDOW_NOT_STRICTLY_SHORTER_THAN_HALF_TURN",
    )
    left_pole = _endpoint_is_tan_half_pole(lo)
    right_pole = _endpoint_is_tan_half_pole(hi)
    require(
        left_pole ^ right_pole,
        "V6_TAN_HALF_POLE_NOT_AT_EXACTLY_ONE_ENDPOINT",
    )
    require(
        v6._pole_in_closed_turn_interval(lo, hi),
        "V6_REPORTED_POLE_NOT_REPRODUCED_EXACTLY",
    )
    pole = lo if left_pole else hi
    normalized_lo = lo - pole
    normalized_hi = hi - pole
    require(
        normalized_lo < normalized_hi
        and not v6._pole_in_closed_turn_interval(normalized_lo, normalized_hi),
        "HALF_TURN_NORMALIZATION_DID_NOT_REMOVE_TAN_POLE",
    )

    cos, sin = _constant_harmonic_coefficients(child_cos, child_sin)
    shifted_cos = {
        harmonic: coefficient * (-1 if harmonic % 2 else 1)
        for harmonic, coefficient in cos.items()
    }
    shifted_sin = {
        harmonic: coefficient * (-1 if harmonic % 2 else 1)
        for harmonic, coefficient in sin.items()
    }
    normalized_spec = {
        "grammar": "RATIONAL_TRIG_POLYNOMIAL_RATIONAL_TURN_WINDOW",
        "cos_coefficients": {
            harmonic: str(value)
            for harmonic, value in shifted_cos.items() if value != 0
        },
        "sin_coefficients": {
            harmonic: str(value)
            for harmonic, value in shifted_sin.items() if value != 0
        },
        "turn_lo": str(normalized_lo),
        "turn_hi": str(normalized_hi),
        "source_parameter_id": source_parameter_id,
    }
    normalized = v6.classify_required_analytic_event(normalized_spec)
    if normalized.get("status") == "RESOURCE_REFUSAL":
        raise ResourceRefusal(
            "NORMALIZED_V6_ENDPOINT_POLE_RESOURCE_REFUSAL:"
            + str(normalized.get("reason"))
        )
    require(
        normalized.get("status") == "CERTIFIED",
        "NORMALIZED_V6_ENDPOINT_POLE_WINDOW_NOT_CERTIFIED:"
        + str(normalized.get("reason")),
    )

    route = {
        "status": "CERTIFIED",
        "relation":
            "EXACT_V6_ENDPOINT_POLE_HALF_TURN_NORMALIZED_RATIONAL_TURN_WINDOW",
        "source_parameter_id": source_parameter_id,
        "original_turn_interval": [str(lo), str(hi)],
        "pole_endpoint": "left" if left_pole else "right",
        "pole_turn": str(pole),
        "normalized_turn_interval": [str(normalized_lo), str(normalized_hi)],
        "exact_coordinate_map": "t_prime=t-pole_turn",
        "harmonic_coefficient_transform": "C_h,S_h -> (-1)^h*(C_h,S_h)",
        "physical_function_identity": (
            "cos(2*pi*h*(t_prime+n+1/2))=(-1)^h*cos(2*pi*h*t_prime);"
            "sin(2*pi*h*(t_prime+n+1/2))=(-1)^h*sin(2*pi*h*t_prime)"
        ),
        "normalized_v6_result": normalized,
        "distinct_roots_open": int(normalized["distinct_roots_open"]),
        "multiple_roots_open": int(normalized["multiple_roots_open"]),
        "caller_certificate_trusted": False,
        "interior_pole_partition_claimed": False,
        "historical_v6_model_modified": False,
    }
    adapted = {
        "status": "CERTIFIED",
        "relation": "RESEARCH_SHADOW_V6_ENDPOINT_POLE_NORMALIZATION",
        "source_parameter_id": source_parameter_id,
        "spans": [{
            "source_interval": ["0", "1"],
            "route_kind": "PB00701_RESEARCH_V6_ENDPOINT_POLE_HALF_TURN_NORMALIZATION",
            "route": route,
        }],
    }
    return adapted, {
        "original_blocker": copy.deepcopy(spans[0]["route"]),
        "original_turn_interval": [str(lo), str(hi)],
        "pole_turn": str(pole),
        "pole_endpoint": "left" if left_pole else "right",
        "normalized_turn_interval": [str(normalized_lo), str(normalized_hi)],
        "shifted_cos_coefficients": {
            str(h): str(v) for h, v in sorted(shifted_cos.items())
        },
        "shifted_sin_coefficients": {
            str(h): str(v) for h, v in sorted(shifted_sin.items())
        },
        "normalized_v6_result": normalized,
        "interior_pole_partition_claimed": False,
    }


def _single_span_child_summary(
        result, child_cos, child_sin, child_offset, child_rate):
    """Shadow V27 summary with exact point-jet endpoint multiplicity."""
    if not isinstance(result, dict):
        raise ResearchRefusal("V27_CHILD_RESULT_NOT_STRUCTURED")
    require(result.get("status") == "CERTIFIED", "V27_CHILD_NOT_CERTIFIED")
    spans = result.get("spans", [])
    require(len(spans) == 1, "V27_CHILD_RELOWERING_NOT_SINGLE_EXACT_SPAN")
    route = spans[0].get("route", {})
    require(route.get("status") == "CERTIFIED", "V27_CHILD_ROUTE_NOT_CERTIFIED")
    require("distinct_roots_open" in route,
            "V27_CHILD_LACKS_EXACT_OPEN_ROOT_COUNT")
    open_roots = int(route["distinct_roots_open"])
    require(open_roots >= 0, "NEGATIVE_CHILD_ROOT_COUNT")

    left_event = v27.v19._endpoint_relation(
        child_cos, child_sin, Fraction(0), q(child_offset)
    )
    right_event = v27.v19._endpoint_relation(
        child_cos, child_sin, Fraction(1),
        q(child_offset) + q(child_rate),
    )
    if left_event.get("status") == "RESOURCE_REFUSAL":
        raise ResourceRefusal(left_event.get("reason", "LEFT_ENDPOINT_RESOURCE_REFUSAL"))
    if right_event.get("status") == "RESOURCE_REFUSAL":
        raise ResourceRefusal(right_event.get("reason", "RIGHT_ENDPOINT_RESOURCE_REFUSAL"))

    left_mult, left_witness, left_method = _checked_endpoint_multiplicity(
        "left", left_event, route, child_cos, child_sin,
        child_offset, child_rate,
    )
    right_mult, right_witness, right_method = _checked_endpoint_multiplicity(
        "right", right_event, route, child_cos, child_sin,
        child_offset, child_rate,
    )

    if open_roots > 0 and route.get("all_roots_simple") is not True:
        require(
            "multiple_roots_open" in route,
            "V27_CHILD_OPEN_ROOT_MULTIPLICITY_NOT_COMPOSABLE",
        )
    multiple_open = int(
        route.get("multiple_roots_open",
                  0 if route.get("all_roots_simple") is True else 0)
    )

    return {
        "status": "CERTIFIED",
        "relation": "EXACT_COMPOSABLE_CHILD_EVENT_SUMMARY_WITH_POINT_JET_ENDPOINT_MULTIPLICITY",
        "child_route_kind": spans[0].get("route_kind"),
        "child_route_relation": route.get("relation"),
        "left_event": copy.deepcopy(left_event),
        "right_event": copy.deepcopy(right_event),
        "left_endpoint_multiplicity": left_mult,
        "right_endpoint_multiplicity": right_mult,
        "left_endpoint_point_witness": left_witness,
        "right_endpoint_point_witness": right_witness,
        "left_endpoint_multiplicity_method": left_method,
        "right_endpoint_multiplicity_method": right_method,
        "distinct_roots_open": open_roots,
        "multiple_roots_open": multiple_open,
        "all_roots_simple": bool(
            route.get(
                "all_roots_simple",
                open_roots == 0 and multiple_open == 0
                and (left_mult in (None, 1))
                and (right_mult in (None, 1)),
            )
        ),
        "multiplicity_invented_from_root_count": False,
    }


def _shadow_partition_route(
        cos_polys, sin_polys, offset, rate,
        source_parameter_id, parent_interval):
    harmonics = v27._active_positive_harmonics(cos_polys, sin_polys)
    require(harmonics and q(rate) != 0,
            "SOURCE_NOT_AT_V27_PHASE_PARTITION_BOUNDARY")
    cut_cert = v27.exact_sector_cuts(offset, rate, harmonics)
    require(cut_cert.get("status") == "CERTIFIED",
            "V27_SECTOR_CUT_CERTIFICATE_NOT_CERTIFIED")
    cuts = [q(value) for value in cut_cert["cuts"]]
    require(cuts, "V27_SOURCE_HAS_NO_PHASE_SECTOR_CUT")

    current = v27._partition_route(
        cos_polys, sin_polys, offset, rate,
        source_parameter_id, parent_interval,
    )
    require(isinstance(current, dict), "CURRENT_V27_PARTITION_ROUTE_MISSING")
    require(
        current.get("status") == "BLOCKED"
        and current.get("reason") in TARGET_REASONS,
        "SOURCE_NOT_AT_CURRENT_V27_ENDPOINT_MULTIPLICITY_BLOCKER",
    )

    boundaries = [Fraction(0), *cuts, Fraction(1)]
    children = []
    parent_lo, parent_hi = map(q, parent_interval)
    parent_width = parent_hi - parent_lo

    for left, right in zip(boundaries, boundaries[1:]):
        if not left < right:
            continue
        child_spec, child_cos, child_sin = v27._child_spec(
            cos_polys, sin_polys, offset, rate,
            left, right, source_parameter_id,
        )
        child_result = v27.v26.classify_required_analytic_event(child_spec)
        if child_result.get("status") == "RESOURCE_REFUSAL":
            raise ResourceRefusal(
                "PB00701_V27_CHILD_RESOURCE_REFUSAL:"
                + str(left) + ":" + str(right) + ":"
                + str(child_result.get("reason"))
            )
        child_offset = q(offset) + q(rate) * left
        child_rate = q(rate) * (right - left)
        historical_child_result = copy.deepcopy(child_result)
        pole_normalization = None
        if child_result.get("status") != "CERTIFIED":
            try:
                child_result, pole_normalization = (
                    _normalized_v6_endpoint_pole_route(
                        child_result, child_cos, child_sin,
                        child_offset, child_rate, source_parameter_id,
                    )
                )
            except ResearchRefusal:
                route_brief = [
                    {
                        "route_kind": span.get("route_kind"),
                        "status": span.get("route", {}).get("status"),
                        "reason": span.get("route", {}).get("reason"),
                        "relation": span.get("route", {}).get("relation"),
                        "source_interval": span.get("source_interval"),
                    }
                    for span in historical_child_result.get("spans", [])
                ]
                raise ResearchRefusal(
                    "V27_SHADOW_REACHED_DEEPER_UNCERTIFIED_CHILD:"
                    + str(left) + ":" + str(right) + ":"
                    + canonical({
                        "status": historical_child_result.get("status"),
                        "reason": historical_child_result.get("reason"),
                        "relation": historical_child_result.get("relation"),
                        "blocker": historical_child_result.get("blocker"),
                        "spans": route_brief,
                    })
                )
        summary = _single_span_child_summary(
            child_result, child_cos, child_sin,
            child_offset, child_rate,
        )
        children.append({
            "parent_local_interval": [str(left), str(right)],
            "parent_source_interval": [
                str(parent_lo + parent_width * left),
                str(parent_lo + parent_width * right),
            ],
            "exact_parent_to_child_map": f"s={left}+({right-left})*u",
            "phase_turn_law_child": {
                "offset": str(child_offset),
                "rate": str(child_rate),
            },
            "child_spec_sha256": source_sha256(child_spec),
            "historical_child_result": historical_child_result,
            "endpoint_pole_normalization": pole_normalization,
            "child_result": child_result,
            "summary": summary,
        })

    composition = v27._compose_child_summaries(children)
    require(composition.get("status") == "CERTIFIED",
            composition.get("reason", "V27_SHADOW_COMPOSITION_NOT_CERTIFIED"))

    supplied = []
    for index, child in enumerate(children):
        summary = child["summary"]
        for side in ("left", "right"):
            if (
                summary[f"{side}_event"].get("relation") == "ZERO"
                and summary[f"{side}_endpoint_multiplicity_method"]
                == "MISSING_ROUTE_MULTIPLICITY_SUPPLIED_BY_EXACT_POINT_JET"
            ):
                supplied.append({
                    "child_index": index,
                    "side": side,
                    "source_interval": child["parent_source_interval"],
                    "multiplicity": summary[f"{side}_endpoint_multiplicity"],
                    "witness": summary[f"{side}_endpoint_point_witness"],
                })
    require(supplied, "NO_MISSING_ENDPOINT_MULTIPLICITY_WAS_ACTUALLY_SUPPLIED")

    return {
        "status": "CERTIFIED",
        "relation": "EXACT_V27_SHADOW_COMPOSITION_WITH_POINT_JET_ENDPOINT_MULTIPLICITY",
        "source_parameter_id": source_parameter_id,
        "parent_source_interval": [str(parent_lo), str(parent_hi)],
        "phase_turn_law_local": {
            "offset": str(q(offset)), "rate": str(q(rate))
        },
        "active_positive_harmonics": harmonics,
        "sector_cut_certificate": cut_cert,
        "current_v27_blocker": {
            "status": current.get("status"),
            "reason": current.get("reason"),
        },
        "children": children,
        "child_count": len(children),
        "composition": composition,
        "point_jet_supplied_endpoint_multiplicity": supplied,
        "endpoint_pole_normalizations": [
            {
                "child_index": index,
                **copy.deepcopy(child["endpoint_pole_normalization"]),
            }
            for index, child in enumerate(children)
            if child["endpoint_pole_normalization"] is not None
        ],
        "multiplicity_invented_from_root_count": False,
        "caller_multiplicity_trusted": False,
        "historical_v27_model_modified": False,
    }


def analyze_source(spec):
    pins()
    reject_binary_float(spec)
    require(isinstance(spec, dict), "SOURCE_RECORD_NOT_OBJECT")
    allowed = {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines",
    }
    require(set(spec) <= allowed, "UNREVIEWED_SOURCE_AUTHORITY_FIELD")
    require(
        spec.get("grammar") ==
        "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "SOURCE_GRAMMAR_OUTSIDE_V27_RESEARCH",
    )
    source_id = spec.get("source_parameter_id")
    require(isinstance(source_id, str) and source_id,
            "MISSING_SOURCE_PARAMETER_ID")

    baseline = v27.classify_required_analytic_event(spec)
    require(isinstance(baseline, dict), "CURRENT_V27_RESULT_NOT_STRUCTURED")
    require(baseline.get("status") == "BLOCKED",
            "SOURCE_NOT_CURRENTLY_BLOCKED_BY_V27")
    spans = baseline.get("spans", [])
    require(spans, "CURRENT_V27_RESULT_HAS_NO_SPANS")

    upgraded = []
    target_count = 0
    for span in spans:
        current_route = span.get("route", {})
        if current_route.get("status") == "CERTIFIED":
            upgraded.append({
                "source_interval": copy.deepcopy(span.get("source_interval")),
                "route_kind": span.get("route_kind"),
                "route": copy.deepcopy(current_route),
                "shadow_upgrade_applied": False,
            })
            continue

        if (
            span.get("route_kind")
            == "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION"
            and current_route.get("reason") in TARGET_REASONS
        ):
            target_count += 1
            phase = span.get("local_phase_turn_law", {})
            cos_polys = {
                int(h): [q(x) for x in values]
                for h, values in span["cos_polynomials"].items()
            }
            sin_polys = {
                int(h): [q(x) for x in values]
                for h, values in span["sin_polynomials"].items()
            }
            replacement = _shadow_partition_route(
                cos_polys, sin_polys,
                q(phase["offset"]), q(phase["rate"]),
                source_id, span["source_interval"],
            )
            upgraded.append({
                "source_interval": copy.deepcopy(span["source_interval"]),
                "route_kind": (
                    "PB00701_RESEARCH_V27_EXACT_ENDPOINT_MULTIPLICITY_SHADOW"
                ),
                "historical_route_kind": span.get("route_kind"),
                "historical_route": copy.deepcopy(current_route),
                "route": replacement,
                "shadow_upgrade_applied": True,
            })
            continue

        upgraded.append({
            "source_interval": copy.deepcopy(span.get("source_interval")),
            "route_kind": span.get("route_kind"),
            "route": copy.deepcopy(current_route),
            "shadow_upgrade_applied": False,
        })

    require(target_count > 0,
            "NO_CURRENT_V27_ENDPOINT_MULTIPLICITY_BLOCKER_FOUND")
    require(
        all(item["route"].get("status") == "CERTIFIED" for item in upgraded),
        "SOURCE_HAS_OTHER_UNRESOLVED_ROUTE_BLOCKERS",
    )

    supplied = [
        evidence
        for item in upgraded if item["shadow_upgrade_applied"]
        for evidence in item["route"]["point_jet_supplied_endpoint_multiplicity"]
    ]
    require(supplied, "NO_EXACT_ENDPOINT_MULTIPLICITY_EVIDENCE")

    pins()
    return {
        "schema": SCHEMA,
        "status": "EXACT_SOURCE_BOUND_V27_ENDPOINT_MULTIPLICITY_COMPOSITION_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_sha256": source_sha256(spec),
        "source_parameter_id": source_id,
        "source_interval": [
            str(q(spec["parameter_lo"])), str(q(spec["parameter_hi"]))
        ],
        "phase_turn_law": {
            "offset": str(q(spec["phase_turn_offset"])),
            "rate": str(q(spec["phase_turn_rate"])),
        },
        "historical_v27_status": baseline.get("status"),
        "historical_blocked_spans": [
            {
                "source_interval": copy.deepcopy(span.get("source_interval")),
                "route_kind": span.get("route_kind"),
                "reason": span.get("route", {}).get("reason"),
            }
            for span in spans
            if span.get("route", {}).get("status") != "CERTIFIED"
        ],
        "shadow_spans": upgraded,
        "point_jet_supplied_endpoint_multiplicity": supplied,
        "endpoint_pole_normalizations": [
            evidence
            for item in upgraded if item["shadow_upgrade_applied"]
            for evidence in item["route"]["endpoint_pole_normalizations"]
        ],
        "all_shadow_span_routes_certified": True,
        "shared_source_knot_double_counted": False,
        "global_cross_span_multiplicity_claimed": False,
        "historical_v54_admitted": False,
        "historical_v54_dispositions_changed": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_brep_or_step_qualified": False,
        "production_authorized": False,
    }


def analyze_frozen_case(case_id):
    case = load_frozen_case(case_id)
    report = analyze_source(case["spec"])
    report["frozen_case_id"] = case_id
    report["frozen_origin"] = case.get("origin")
    report["historical_v54_disposition"] = case["expected"].get("v54_disposition")
    return report


def nontruth(reason, status="BLOCKED"):
    return {
        "schema": SCHEMA,
        "status": status,
        "reason": reason,
        "is_truth_value": False,
        "historical_v54_admitted": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "production_authorized": False,
    }


def attempt(spec, **kwargs):
    try:
        return analyze_source(spec, **kwargs)
    except ResourceRefusal as exc:
        return nontruth(exc.reason, "RESOURCE_REFUSAL")
    except (ResearchRefusal, ValueError, KeyError, IndexError, TypeError,
            ZeroDivisionError) as exc:
        return nontruth(str(exc), "BLOCKED")
    except (MemoryError, RecursionError, OverflowError) as exc:
        return nontruth(type(exc).__name__, "RESOURCE_REFUSAL")


def validate_report(spec, submitted):
    try:
        claimed = canonical(submitted)
        if len(claimed) > MAX_REPORT_BYTES:
            return nontruth("SUBMITTED_REPORT_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
        checked = attempt(spec)
        require(
            checked.get("status") ==
            "EXACT_SOURCE_BOUND_V27_ENDPOINT_MULTIPLICITY_COMPOSITION_RESEARCH",
            "SOURCE_BOUND_V27_ENDPOINT_MULTIPLICITY_PROOF_MISSING",
        )
        require(claimed == canonical(checked),
                "FORGED_V27_ENDPOINT_MULTIPLICITY_REPORT")
        return checked
    except ResearchRefusal as exc:
        return nontruth(exc.reason)
    except (ValueError, TypeError, OverflowError) as exc:
        return nontruth(str(exc))
