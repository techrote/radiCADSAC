#!/usr/bin/env python3
"""MC-038/PB-007-01: exact implicit V41 orientation proof-cut equality/order.

Research-only. This module does not create algebraic child reparameterizations
and does not promote V41/PB-007-01/MC-B/MC-1/native/STEP capability.
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

import pb00701_coupled_bspline_model as lowerer  # noqa: E402
import pb00701_orientation_root_partition_model as v41  # noqa: E402
import verify_pb00701_stationary_polynomial_order as algebraic  # noqa: E402

SCHEMA = "radicadsac-pb00701-v41-algebraic-cut-order/1.0"
MAX_ISOLATION_BISECTIONS = 1024
MAX_COMPARISON_BISECTIONS = 2048
MAX_REPORT_BYTES = 131072

PINS = {
    HERE / "pb00701_coupled_bspline_model.py":
        "a086b625e1a6dea8bd202699d161167bb69cc9e7",
    HERE / "pb00701_orientation_root_partition_model.py":
        "2f96622b5c69655279d66fe2b36f8f3e03414660",
    HERE / "verify_pb00701_stationary_polynomial_order.py":
        "0954c5e1ad63ec1c8dd2acb3202882650b02c516",
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
    # The landed #281 helper has its own transitive source pins and checks them
    # at import/use time. Re-run the immediate helper check here as custody.
    algebraic.load_identity_helper()


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


def poly(values):
    return algebraic.trim([q(x) for x in values])


def serialize_poly(values):
    return [str(x) for x in algebraic.trim(values)]


class ComparisonBudget:
    def __init__(self, limit):
        require(type(limit) is int and 1 <= limit <= MAX_COMPARISON_BISECTIONS,
                "INVALID_COMPARISON_BUDGET")
        self.limit = limit
        self.used = 0

    def spend(self):
        if self.used >= self.limit:
            raise ResourceRefusal("V41_ALGEBRAIC_COMPARISON_BUDGET_EXHAUSTED")
        self.used += 1


def _source_map(local, source_left, source_right):
    return source_left + (source_right - source_left) * local


def _root_descriptor(raw, full_poly, *, harmonic, coordinate,
                     source_left, source_right):
    square_free = algebraic.EE.square_free(full_poly)
    multiplicity = algebraic.multiplicity_in_view(full_poly, raw)
    common = {
        "cause_id": f"H{harmonic}_{coordinate}",
        "cause_kind": "orientation_root",
        "harmonic": int(harmonic),
        "coordinate": coordinate,
        "orientation_polynomial": serialize_poly(full_poly),
        "defining_square_free_polynomial": serialize_poly(square_free),
        "multiplicity": int(multiplicity),
        "proof_cut_is_physical_event": False,
    }
    if raw["kind"] == "RATIONAL_ROOT":
        value = raw["value"]
        coordinate_record = {
            "kind": "RATIONAL_ROOT",
            "local_value": str(value),
            "source_value": str(_source_map(value, source_left, source_right)),
            "defining_square_free_polynomial": serialize_poly(square_free),
            "minimal_polynomial_claimed": False,
        }
    else:
        left, right = raw["interval"]
        coordinate_record = {
            "kind": "ISOLATED_REAL_ROOT",
            "local_isolating_interval": [str(left), str(right)],
            "source_isolating_interval": [
                str(_source_map(left, source_left, source_right)),
                str(_source_map(right, source_left, source_right)),
            ],
            "defining_square_free_polynomial": serialize_poly(square_free),
            "minimal_polynomial_claimed": False,
        }
    return {"coordinate": coordinate_record, "cause": common}


def _coord_kind(record):
    return record["kind"]


def _is_rational(record):
    return _coord_kind(record) in ("RATIONAL_ROOT", "RATIONAL_PROOF_CUT")


def _rational_value(record):
    require(_is_rational(record), "COORDINATE_IS_NOT_RATIONAL")
    return q(record["local_value"])


def _bounds(record):
    if _is_rational(record):
        value = _rational_value(record)
        return value, value
    require(_coord_kind(record) == "ISOLATED_REAL_ROOT",
            "UNKNOWN_PROOF_COORDINATE_KIND")
    left, right = map(q, record["local_isolating_interval"])
    require(Fraction(0) < left < right < Fraction(1),
            "BAD_ROOT_ISOLATING_INTERVAL")
    return left, right


def _defining_poly(record):
    require(_coord_kind(record) in ("RATIONAL_ROOT", "ISOLATED_REAL_ROOT"),
            "RATIONAL_PROOF_CUT_HAS_NO_DEFINING_POLYNOMIAL")
    return poly(record["defining_square_free_polynomial"])


def _same_coordinate(a, b):
    if _is_rational(a) and _is_rational(b):
        same = _rational_value(a) == _rational_value(b)
        return same, "EXACT_RATIONAL_VALUE" if same else None

    if _is_rational(a):
        rational, root = a, b
    elif _is_rational(b):
        rational, root = b, a
    else:
        rational = None
        root = None

    if rational is not None:
        require(_coord_kind(root) == "ISOLATED_REAL_ROOT",
                "UNSUPPORTED_RATIONAL_ROOT_COMPARISON")
        value = _rational_value(rational)
        left, right = _bounds(root)
        if not left < value < right:
            return False, None
        defining = _defining_poly(root)
        if algebraic.EE.peval(defining, value) == 0:
            return True, "EXACT_POLYNOMIAL_EVALUATION_AT_RATIONAL_CUT"
        return False, None

    require(_coord_kind(a) == _coord_kind(b) == "ISOLATED_REAL_ROOT",
            "UNSUPPORTED_IMPLICIT_ROOT_COMPARISON")
    a_left, a_right = _bounds(a)
    b_left, b_right = _bounds(b)
    left, right = max(a_left, b_left), min(a_right, b_right)
    if not left < right:
        return False, None
    gcd = algebraic.EE.pgcd(_defining_poly(a), _defining_poly(b))
    if algebraic.EE.degree(gcd) <= 0:
        return False, None
    count = algebraic.EE.distinct_roots_open(gcd, left, right)
    require(count in (0, 1), "COMMON_ROOT_GCD_INTERVAL_NOT_UNIQUE")
    return (
        (True, "EXACT_POLYNOMIAL_GCD_PLUS_STURM_COMMON_ROOT")
        if count == 1 else (False, None)
    )


def _refresh_source_mapping(record, source_left, source_right):
    result = copy.deepcopy(record)
    if _is_rational(result):
        result["source_value"] = str(
            _source_map(_rational_value(result), source_left, source_right)
        )
    else:
        left, right = _bounds(result)
        result["source_isolating_interval"] = [
            str(_source_map(left, source_left, source_right)),
            str(_source_map(right, source_left, source_right)),
        ]
    return result


def _refine(record, budget, source_left, source_right):
    require(_coord_kind(record) == "ISOLATED_REAL_ROOT",
            "CANNOT_REFINE_RATIONAL_COORDINATE")
    budget.spend()
    defining = _defining_poly(record)
    left, right = _bounds(record)
    require(algebraic.EE.distinct_roots_open(defining, left, right) == 1,
            "ROOT_DESCRIPTOR_LOST_UNIQUENESS")
    mid = (left + right) / 2
    value = algebraic.EE.peval(defining, mid)
    if value == 0:
        return {
            "kind": "RATIONAL_ROOT",
            "local_value": str(mid),
            "source_value": str(_source_map(mid, source_left, source_right)),
            "defining_square_free_polynomial":
                serialize_poly(defining),
            "minimal_polynomial_claimed": False,
        }
    left_count = algebraic.EE.distinct_roots_open(defining, left, mid)
    right_count = algebraic.EE.distinct_roots_open(defining, mid, right)
    require(left_count + right_count == 1,
            "ROOT_REFINEMENT_LOST_STURM_COUNT")
    if left_count:
        right = mid
    else:
        left = mid
    require(algebraic.EE.peval(defining, left) != 0 and
            algebraic.EE.peval(defining, right) != 0,
            "ROOT_REFINEMENT_ENDPOINT_BECAME_ROOT")
    result = copy.deepcopy(record)
    result["local_isolating_interval"] = [str(left), str(right)]
    return _refresh_source_mapping(result, source_left, source_right)


def compare_coordinates(a, b, budget, source_left, source_right):
    left = copy.deepcopy(a)
    right = copy.deepcopy(b)
    same, method = _same_coordinate(left, right)
    if same:
        return "EQUAL", method, left, right

    while True:
        a_left, a_right = _bounds(left)
        b_left, b_right = _bounds(right)
        if a_right <= b_left:
            return "LEFT_BEFORE_RIGHT", "DISJOINT_EXACT_RATIONAL_BOUNDS", left, right
        if b_right <= a_left:
            return "RIGHT_BEFORE_LEFT", "DISJOINT_EXACT_RATIONAL_BOUNDS", left, right

        left_refinable = _coord_kind(left) == "ISOLATED_REAL_ROOT"
        right_refinable = _coord_kind(right) == "ISOLATED_REAL_ROOT"
        if not left_refinable and not right_refinable:
            raise ResearchRefusal("DISTINCT_RATIONAL_COORDINATES_FAILED_TO_ORDER")

        if left_refinable and right_refinable:
            l_width = a_right - a_left
            r_width = b_right - b_left
            if l_width >= r_width:
                left = _refine(left, budget, source_left, source_right)
            else:
                right = _refine(right, budget, source_left, source_right)
        elif left_refinable:
            left = _refine(left, budget, source_left, source_right)
        else:
            right = _refine(right, budget, source_left, source_right)

        same, method = _same_coordinate(left, right)
        if same:
            return "EQUAL", method, left, right


def _rational_cut_record(value, causes, source_left, source_right):
    value = q(value)
    require(Fraction(0) < value < Fraction(1),
            "RATIONAL_PROOF_CUT_NOT_INTERIOR")
    return {
        "coordinate": {
            "kind": "RATIONAL_PROOF_CUT",
            "local_value": str(value),
            "source_value": str(_source_map(value, source_left, source_right)),
        },
        "causes": copy.deepcopy(causes),
    }


def _orientation_records(cos_polys, sin_polys, source_left, source_right,
                         max_isolation_bisections):
    remaining = max_isolation_bisections
    require(type(remaining) is int and
            1 <= remaining <= MAX_ISOLATION_BISECTIONS,
            "INVALID_ISOLATION_BUDGET")
    records = []
    endpoint_records = []
    active_harmonics = sorted(
        h for h in set(cos_polys) | set(sin_polys)
        if int(h) > 0 and (
            algebraic.trim(cos_polys.get(h, [0])) != [0]
            or algebraic.trim(sin_polys.get(h, [0])) != [0]
        )
    )
    orientation_harmonics = []
    for harmonic in active_harmonics:
        c = algebraic.trim(cos_polys.get(harmonic, [0]))
        s = algebraic.trim(sin_polys.get(harmonic, [0]))
        # Match landed V41 exactly: a one-channel harmonic still contributes
        # historical phase/certificate proof cuts, but it does not create an
        # A/B orientation-root partition in the current route.
        if c == [0] or s == [0]:
            continue
        orientation_harmonics.append(harmonic)
        a, b = v41._rotated_polynomials(c, s)
        for coordinate, orientation_poly in (("A", a), ("B", b)):
            if algebraic.trim(orientation_poly) == [0]:
                raise ResearchRefusal(
                    f"H{harmonic}_{coordinate}_IDENTICALLY_ZERO_ORIENTATION_COORDINATE"
                )
            try:
                left_mult, right_mult, roots, used = (
                    algebraic.isolate_open_roots(
                        orientation_poly, max_bisections=remaining
                    )
                )
            except algebraic.IsolationRefusal as exc:
                raise ResourceRefusal(str(exc)) from exc
            remaining -= used
            if remaining < 0:
                raise ResourceRefusal("V41_ALGEBRAIC_ISOLATION_BUDGET_EXHAUSTED")
            for raw in roots:
                records.append(_root_descriptor(
                    raw, orientation_poly, harmonic=harmonic,
                    coordinate=coordinate, source_left=source_left,
                    source_right=source_right,
                ))
            for side, multiplicity in (
                ("LEFT", left_mult), ("RIGHT", right_mult)
            ):
                if multiplicity:
                    endpoint_records.append({
                        "cause_id": f"H{harmonic}_{coordinate}",
                        "harmonic": int(harmonic),
                        "coordinate": coordinate,
                        "side": side,
                        "multiplicity": int(multiplicity),
                        "proof_cut_is_physical_event": False,
                    })
    return active_harmonics, orientation_harmonics, records, endpoint_records, (
        max_isolation_bisections - remaining
    )


def _existing_rational_certificate_cuts(offset, rate, harmonics,
                                        source_left, source_right):
    grouped = {}
    sector = v41.v27.exact_sector_cuts(offset, rate, harmonics)
    require(sector.get("status") == "CERTIFIED",
            "HISTORICAL_PHASE_SECTOR_CUTS_NOT_CERTIFIED")
    for crossing in sector.get("crossings", []):
        x = q(crossing["source_cut"])
        grouped.setdefault(x, []).append({
            "cause_kind": "historical_phase_sector_cut",
            "causes": crossing["causes"],
        })

    rotated = v41.exact_rotated_coordinate_certificate_cuts(
        offset, rate, harmonics
    )
    require(rotated.get("status") == "CERTIFIED",
            "ROTATED_CERTIFICATE_CELL_CUTS_NOT_CERTIFIED")
    for crossing in rotated.get("crossings", []):
        x = q(crossing["source_cut"])
        grouped.setdefault(x, []).extend(copy.deepcopy(crossing["causes"]))

    return [
        _rational_cut_record(x, grouped[x], source_left, source_right)
        for x in sorted(grouped)
    ]


def _cause_list(record):
    if "cause" in record:
        return [copy.deepcopy(record["cause"])]
    return copy.deepcopy(record["causes"])


def _insert_cut(ordered, candidate, budget, source_left, source_right):
    coordinate = copy.deepcopy(candidate["coordinate"])
    causes = _cause_list(candidate)
    for index, existing in enumerate(ordered):
        relation, method, refined_new, refined_existing = compare_coordinates(
            coordinate, existing["coordinate"], budget,
            source_left, source_right,
        )
        if relation == "EQUAL":
            existing["coordinate"] = refined_existing
            existing["causes"].extend(causes)
            existing["coincidence_proofs"].append({
                "method": method,
                "merged_cause_ids": sorted(
                    cause.get("cause_id", cause.get("cause_kind", "certificate"))
                    for cause in causes
                ),
                "interval_overlap_alone_used_as_equality": False,
            })
            return
        if relation == "LEFT_BEFORE_RIGHT":
            ordered.insert(index, {
                "coordinate": refined_new,
                "causes": causes,
                "coincidence_proofs": [],
            })
            return
        coordinate = refined_new
        existing["coordinate"] = refined_existing
    ordered.append({
        "coordinate": coordinate,
        "causes": causes,
        "coincidence_proofs": [],
    })


def _canonical_cut_partition(orientation_records, rational_records,
                             source_left, source_right,
                             max_comparison_bisections):
    budget = ComparisonBudget(max_comparison_bisections)
    ordered = []
    # Deterministic producer ordering is deliberately not coordinate ordering;
    # every insertion must establish its own exact relation.
    for record in [*rational_records, *orientation_records]:
        _insert_cut(
            ordered, record, budget, source_left, source_right
        )

    output = []
    previous = None
    for index, item in enumerate(ordered):
        coord = item["coordinate"]
        if previous is not None:
            relation, _, prev_refined, cur_refined = compare_coordinates(
                previous, coord, budget, source_left, source_right
            )
            require(relation == "LEFT_BEFORE_RIGHT",
                    "CANONICAL_PROOF_CUTS_NOT_STRICTLY_ORDERED")
            output[-1]["coordinate"] = prev_refined
            coord = cur_refined
        output.append({
            "index": index,
            "coordinate": coord,
            "causes": sorted(
                item["causes"],
                key=lambda cause: canonical(cause),
            ),
            "coincidence_proofs": sorted(
                item["coincidence_proofs"],
                key=lambda proof: canonical(proof),
            ),
        })
        previous = coord
    return output, budget.used


def source_bound_view(spec, *,
                      max_isolation_bisections=MAX_ISOLATION_BISECTIONS,
                      max_comparison_bisections=MAX_COMPARISON_BISECTIONS):
    pins()
    reject_binary_float(spec)
    require(isinstance(spec, dict), "SOURCE_RECORD_NOT_OBJECT")
    allowed = {
        "grammar", "cos_splines", "sin_splines", "parameter_lo",
        "parameter_hi", "phase_turn_offset", "phase_turn_rate",
        "source_parameter_id", "parameter_projection",
    }
    require(set(spec) <= allowed, "UNREVIEWED_SOURCE_AUTHORITY_FIELD")
    require(spec.get("grammar") ==
            "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "SOURCE_GRAMMAR_OUTSIDE_V41_RESEARCH")
    source_id = spec.get("source_parameter_id")
    require(isinstance(source_id, str) and source_id,
            "MISSING_SOURCE_PARAMETER_ID")

    lowered = lowerer.classify_required_analytic_event(spec)
    require(lowered.get("status") == "BLOCKED" and
            lowered.get("relation") ==
            "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER",
            "SOURCE_NOT_AT_GENERAL_COUPLED_V41_RESEARCH_BOUNDARY")
    require(lowered.get("source_parameter_id") == source_id,
            "LOWERED_SOURCE_PARAMETER_ID_MISMATCH")
    spans = lowered.get("spans")
    require(isinstance(spans, list) and len(spans) == 1,
            "MULTISPAN_ALGEBRAIC_CHILD_INTERFACE_NOT_CLAIMED")
    span = spans[0]
    require(span.get("route_kind") ==
            "PB00701_GENERAL_COUPLED_THEOREM_BOUNDARY",
            "SOURCE_SPAN_ALREADY_OWNED_BY_PRECEDING_ROUTE")

    source_left, source_right = map(q, span["source_interval"])
    require(source_left < source_right, "INVALID_SOURCE_SPAN")
    global_offset = q(lowered["phase_turn_law"]["offset"])
    global_rate = q(lowered["phase_turn_law"]["rate"])
    local_offset = global_offset + global_rate * source_left
    local_rate = global_rate * (source_right - source_left)

    cos_polys = {
        int(h): poly(values)
        for h, values in span["cos_polynomials"].items()
    }
    sin_polys = {
        int(h): poly(values)
        for h, values in span["sin_polynomials"].items()
    }

    active_harmonics, orientation_harmonics, orientation_records, endpoints, isolation_used = (
        _orientation_records(
            cos_polys, sin_polys, source_left, source_right,
            max_isolation_bisections,
        )
    )
    require(orientation_records,
            "NO_INTERIOR_ORIENTATION_ROOTS_FOR_ALGEBRAIC_ORDER_RESEARCH")

    # Admission is tied to the live V41 boundary, not merely to our choice of
    # descriptor representation. Do this after exact orientation validation so
    # malformed/identity coordinates keep their more specific fail-closed
    # refusal instead of being relabelled as a boundary mismatch.
    current_v41 = v41._orientation_cut_certificate(
        cos_polys, sin_polys, local_offset, local_rate
    )
    require(
        current_v41.get("status") == "BLOCKED"
        and "IRRATIONAL_ALGEBRAIC_ORIENTATION_ROOT_NOT_REPRESENTABLE"
        in current_v41.get("reason", ""),
        "SOURCE_NOT_AT_CURRENT_V41_ALGEBRAIC_ROOT_BOUNDARY",
    )

    rational_records = _existing_rational_certificate_cuts(
        local_offset, local_rate, active_harmonics, source_left, source_right
    )
    ordered, comparison_used = _canonical_cut_partition(
        orientation_records, rational_records,
        source_left, source_right, max_comparison_bisections,
    )

    # At least one truly implicit descriptor must survive source lowering.
    implicit = [
        item for item in orientation_records
        if item["coordinate"]["kind"] == "ISOLATED_REAL_ROOT"
    ]
    require(implicit, "NO_IMPLICIT_ORIENTATION_ROOT_IN_SOURCE")

    pins()
    return {
        "schema": SCHEMA,
        "status": "EXACT_SOURCE_BOUND_V41_IMPLICIT_PROOF_CUT_ORDER_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_sha256": source_sha256(spec),
        "source_parameter_id": source_id,
        "source_interval": [str(source_left), str(source_right)],
        "phase_turn_law": {
            "offset": str(global_offset),
            "rate": str(global_rate),
        },
        "current_v41_boundary": (
            "IRRATIONAL_ALGEBRAIC_ORIENTATION_ROOT_NOT_REPRESENTABLE_"
            "BY_CURRENT_RATIONAL_CHILD_PARAMETER_MODEL"
        ),
        "current_v41_boundary_evidence": {
            key: copy.deepcopy(current_v41[key])
            for key in (
                "reason", "label", "distinct_open_root_count",
                "exact_rational_open_roots_found", "missing_exact_root_count",
                "correctness_weakened",
            )
            if key in current_v41
        },
        "active_positive_harmonics": active_harmonics,
        "orientation_harmonics": orientation_harmonics,
        "orientation_root_causes": orientation_records,
        "endpoint_orientation_root_causes": endpoints,
        "existing_rational_certificate_cut_count": len(rational_records),
        "ordered_proof_cuts": ordered,
        "isolation_bisections_used": isolation_used,
        "comparison_bisections_used": comparison_used,
        "root_equality_rule":
            "EXACT_RATIONAL_VALUE_OR_POLYNOMIAL_EVALUATION_OR_GCD_PLUS_STURM",
        "root_order_rule":
            "EXACT_DISJOINT_RATIONAL_BOUNDS_AFTER_BOUNDED_STURM_REFINEMENT",
        "interval_overlap_alone_is_equality": False,
        "orientation_roots_are_proof_geometry_only": True,
        "algebraic_child_reparameterization_constructed": False,
        "frozen_v41_child_composition_claimed": False,
        "historical_v54_dispositions_changed": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_brep_or_step_qualified": False,
        "production_authorized": False,
    }


def nontruth(reason, status="BLOCKED"):
    return {
        "schema": SCHEMA,
        "status": status,
        "reason": reason,
        "is_truth_value": False,
        "frozen_v41_child_composition_claimed": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "production_authorized": False,
    }


def attempt(spec, **budgets):
    try:
        return source_bound_view(spec, **budgets)
    except ResourceRefusal as exc:
        return nontruth(exc.reason, "RESOURCE_REFUSAL")
    except algebraic.IsolationRefusal as exc:
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (ResearchRefusal, ValueError, KeyError, IndexError, TypeError,
            ZeroDivisionError) as exc:
        return nontruth(str(exc), "BLOCKED")
    except (MemoryError, RecursionError, OverflowError) as exc:
        return nontruth(type(exc).__name__, "RESOURCE_REFUSAL")


def validate_report(spec, submitted, **budgets):
    try:
        claimed = canonical(submitted)
        if len(claimed) > MAX_REPORT_BYTES:
            return nontruth("SUBMITTED_REPORT_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
        checked = attempt(spec, **budgets)
        require(
            checked.get("status") ==
            "EXACT_SOURCE_BOUND_V41_IMPLICIT_PROOF_CUT_ORDER_RESEARCH",
            "SOURCE_BOUND_ALGEBRAIC_ORDER_PROOF_MISSING",
        )
        require(claimed == canonical(checked),
                "FORGED_V41_ALGEBRAIC_PROOF_CUT_REPORT")
        return checked
    except ResearchRefusal as exc:
        return nontruth(exc.reason, "BLOCKED")
    except (ValueError, TypeError, OverflowError) as exc:
        return nontruth(str(exc), "BLOCKED")
