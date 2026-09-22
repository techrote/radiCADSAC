#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_phase_dominance_model as v11  # noqa: E402

v10 = v11.v10
v9 = v10.v9
v8 = v9.v8
v7 = v9.v7
v6 = v10.v6
EE = v10.EE
q = v10.q

MAX_COMPONENT_ROOTS = 4096
MAX_PARTITION_DEPTH = 256
MAX_ENDPOINT_REFINEMENT = 256
MAX_LATTICE_CANDIDATES = 8192


class ComponentPartitionRefusal(RuntimeError):
    """Bounded resource refusal. Never a truth value."""


def _trim(poly):
    return v9._trim(poly)


def _distinct_roots_closed(poly, left=Fraction(0), right=Fraction(1)):
    poly = _trim(poly)
    left = q(left)
    right = q(right)
    if not left < right:
        raise ValueError("require left < right")
    count = EE.distinct_roots_open(poly, left, right)
    if EE.peval(poly, left) == 0:
        count += 1
    if EE.peval(poly, right) == 0:
        count += 1
    return count


def _affine_reparameter(poly, left, right):
    """Return p(left + (right-left)*t), exactly, in ascending powers of t."""
    left = q(left)
    right = q(right)
    if not Fraction(0) <= left < right <= Fraction(1):
        raise ValueError("cell must be a nonempty subinterval of [0,1]")
    affine = [left, right - left]
    result = [Fraction(0)]
    for coefficient in reversed(_trim(poly)):
        result = v7._padd(v7._pmul(result, affine), [coefficient])
    return _trim(result)


def _nonroot_split(poly, left, right):
    left = q(left)
    right = q(right)
    width = right - left
    probes = [Fraction(1, 2), Fraction(1, 3), Fraction(2, 3)]
    probes.extend(Fraction(k, 257) for k in range(1, 257))
    for ratio in probes:
        source = left + width * ratio
        if left < source < right and EE.peval(poly, source) != 0:
            return source
    raise ComponentPartitionRefusal("PB00701_V12_NONROOT_SPLIT_BUDGET_EXHAUSTED")


def _isolate_open_union_roots(poly, left, right, depth=0):
    if depth > MAX_PARTITION_DEPTH:
        raise ComponentPartitionRefusal("PB00701_V12_ROOT_ISOLATION_DEPTH_EXHAUSTED")
    count = EE.distinct_roots_open(poly, left, right)
    if count == 0:
        return []
    if count > MAX_COMPONENT_ROOTS:
        raise ComponentPartitionRefusal("PB00701_V12_COMPONENT_ROOT_BUDGET_EXHAUSTED")
    if count == 1:
        return [(q(left), q(right))]
    split = _nonroot_split(poly, left, right)
    return (
        _isolate_open_union_roots(poly, left, split, depth + 1)
        + _isolate_open_union_roots(poly, split, right, depth + 1)
    )


def _endpoint_safe_domain(union):
    left_root = EE.peval(union, Fraction(0)) == 0
    right_root = EE.peval(union, Fraction(1)) == 0
    if not left_root and not right_root:
        return Fraction(0), Fraction(1), []
    for power in range(2, MAX_ENDPOINT_REFINEMENT + 2):
        step = Fraction(1, 2**power)
        left_cut = step if left_root else Fraction(0)
        right_cut = Fraction(1) - step if right_root else Fraction(1)
        if not left_cut < right_cut:
            continue
        if left_root:
            if EE.peval(union, left_cut) == 0:
                continue
            if EE.distinct_roots_open(union, Fraction(0), left_cut) != 0:
                continue
        if right_root:
            if EE.peval(union, right_cut) == 0:
                continue
            if EE.distinct_roots_open(union, right_cut, Fraction(1)) != 0:
                continue
        endpoint_neighborhoods = []
        if left_root:
            endpoint_neighborhoods.append((Fraction(0), left_cut))
        if right_root:
            endpoint_neighborhoods.append((right_cut, Fraction(1)))
        return left_cut, right_cut, endpoint_neighborhoods
    raise ComponentPartitionRefusal("PB00701_V12_ENDPOINT_ROOT_REFINEMENT_EXHAUSTED")


def _root_owner(a_poly, b_poly, left, right):
    a_count = _distinct_roots_closed(a_poly, left, right)
    b_count = _distinct_roots_closed(b_poly, left, right)
    if (a_count, b_count) == (1, 0):
        return "A"
    if (a_count, b_count) == (0, 1):
        return "B"
    raise AssertionError(
        f"isolated union root does not have unique component owner: A={a_count}, B={b_count}"
    )


def build_component_root_partition(a_poly, b_poly):
    a_poly = _trim(a_poly)
    b_poly = _trim(b_poly)
    if a_poly == [0] or b_poly == [0]:
        return {
            "status": "BLOCKED",
            "reason": "COMPONENT_PARTITION_REQUIRES_TWO_NONZERO_COMPONENTS",
            "blocker": "PB-007-01",
        }
    common = EE.pgcd(a_poly, b_poly)
    if EE.degree(common) > 0:
        return {
            "status": "BLOCKED",
            "reason": "COMPONENT_ROOTS_NOT_COPRIME",
            "blocker": "PB-007-01",
            "gcd": [str(value) for value in _trim(common)],
        }
    union = v7._pmul(a_poly, b_poly)
    total = _distinct_roots_closed(union)
    if total > MAX_COMPONENT_ROOTS:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": "PB00701_V12_COMPONENT_ROOT_BUDGET_EXHAUSTED",
            "is_truth_value": False,
        }
    try:
        safe_left, safe_right, endpoint_neighborhoods = _endpoint_safe_domain(union)
        open_intervals = _isolate_open_union_roots(union, safe_left, safe_right)
    except ComponentPartitionRefusal as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": str(exc), "is_truth_value": False}

    root_intervals = list(endpoint_neighborhoods) + list(open_intervals)
    root_intervals.sort()
    root_neighborhoods = []
    for left, right in root_intervals:
        owner = _root_owner(a_poly, b_poly, left, right)
        root_neighborhoods.append({
            "source_interval": [str(left), str(right)],
            "owner": owner,
            "union_distinct_roots_closed": _distinct_roots_closed(union, left, right),
            "A_distinct_roots_closed": _distinct_roots_closed(a_poly, left, right),
            "B_distinct_roots_closed": _distinct_roots_closed(b_poly, left, right),
            "opposite_component_zero_free_closed": True,
        })

    cells = []
    cursor = Fraction(0)
    for index, neighborhood in enumerate(root_neighborhoods):
        left = q(neighborhood["source_interval"][0])
        right = q(neighborhood["source_interval"][1])
        if cursor < left:
            cells.append({
                "kind": "ROOT_FREE_COMPLEMENT",
                "source_interval": [str(cursor), str(left)],
                "root_neighborhood_index": None,
            })
        if cursor > left:
            raise AssertionError("root isolating neighborhoods overlap")
        cells.append({
            "kind": "COMPONENT_ROOT_NEIGHBORHOOD",
            "source_interval": [str(left), str(right)],
            "root_neighborhood_index": index,
            "owner": neighborhood["owner"],
        })
        cursor = right
    if cursor < 1:
        cells.append({
            "kind": "ROOT_FREE_COMPLEMENT",
            "source_interval": [str(cursor), "1"],
            "root_neighborhood_index": None,
        })
    if not cells:
        cells = [{
            "kind": "ROOT_FREE_COMPLEMENT",
            "source_interval": ["0", "1"],
            "root_neighborhood_index": None,
        }]

    certificate = {
        "status": "CERTIFIED",
        "method": "MC032_EXACT_STURM_FINITE_COMPONENT_ROOT_ISOLATION",
        "coprime_proof": {
            "method": "EXACT_RATIONAL_POLYNOMIAL_GCD",
            "gcd_degree": EE.degree(common),
            "gcd_coefficients": [str(value) for value in _trim(common)],
        },
        "A_polynomial": [str(value) for value in a_poly],
        "B_polynomial": [str(value) for value in b_poly],
        "union_polynomial": [str(value) for value in union],
        "total_distinct_component_roots_closed": total,
        "root_neighborhoods": root_neighborhoods,
        "cells": cells,
        "sampling_used": False,
        "epsilon_used": False,
        "approximate_roots_used": False,
    }
    if not verify_partition_certificate(certificate, a_poly, b_poly):
        raise AssertionError("constructed component partition failed exact self-verification")
    return certificate


def verify_partition_certificate(certificate, a_poly, b_poly):
    try:
        if certificate.get("status") != "CERTIFIED":
            return False
        a_poly = _trim(a_poly)
        b_poly = _trim(b_poly)
        if EE.degree(EE.pgcd(a_poly, b_poly)) > 0:
            return False
        union = v7._pmul(a_poly, b_poly)
        cells = certificate.get("cells")
        roots = certificate.get("root_neighborhoods")
        if not isinstance(cells, list) or not cells or not isinstance(roots, list):
            return False
        cursor = Fraction(0)
        counted = 0
        used_root_indexes = []
        for cell in cells:
            left, right = map(q, cell["source_interval"])
            if left != cursor or not left < right or right > 1:
                return False
            if left not in (Fraction(0), Fraction(1)) and EE.peval(union, left) == 0:
                return False
            if right not in (Fraction(0), Fraction(1)) and EE.peval(union, right) == 0:
                return False
            union_count = _distinct_roots_closed(union, left, right)
            a_count = _distinct_roots_closed(a_poly, left, right)
            b_count = _distinct_roots_closed(b_poly, left, right)
            if cell["kind"] == "ROOT_FREE_COMPLEMENT":
                if union_count != 0 or a_count != 0 or b_count != 0:
                    return False
                if cell.get("root_neighborhood_index") is not None:
                    return False
            elif cell["kind"] == "COMPONENT_ROOT_NEIGHBORHOOD":
                index = cell.get("root_neighborhood_index")
                if isinstance(index, bool) or not isinstance(index, int):
                    return False
                if not (0 <= index < len(roots)) or index in used_root_indexes:
                    return False
                n = roots[index]
                if list(cell["source_interval"]) != list(n["source_interval"]):
                    return False
                owner = n.get("owner")
                if union_count != 1:
                    return False
                if owner == "A" and (a_count, b_count) != (1, 0):
                    return False
                if owner == "B" and (a_count, b_count) != (0, 1):
                    return False
                if owner not in {"A", "B"}:
                    return False
                if cell.get("owner") != owner:
                    return False
                used_root_indexes.append(index)
                counted += 1
            else:
                return False
            cursor = right
        if cursor != 1:
            return False
        if sorted(used_root_indexes) != list(range(len(roots))):
            return False
        total = _distinct_roots_closed(union)
        if counted != total or certificate.get("total_distinct_component_roots_closed") != total:
            return False
        if certificate.get("sampling_used") is not False:
            return False
        if certificate.get("epsilon_used") is not False:
            return False
        if certificate.get("approximate_roots_used") is not False:
            return False
        return True
    except (AssertionError, KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def _fraction_floor(value):
    value = q(value)
    return value.numerator // value.denominator


def _fraction_ceil(value):
    value = q(value)
    return -((-value.numerator) // value.denominator)


def _component_root_event(neighborhood, owner_poly, other_poly, u_offset, u_rate):
    left, right = map(q, neighborhood["source_interval"])
    owner = neighborhood["owner"]
    u_offset = q(u_offset)
    u_rate = q(u_rate)
    if u_rate == 0:
        return {
            "status": "BLOCKED",
            "reason": "COMPONENT_ROOT_EVENT_REQUIRES_NONZERO_PHASE_RATE",
            "blocker": "PB-007-01",
        }
    ulo = u_offset + u_rate * left
    uhi = u_offset + u_rate * right
    lo = min(ulo, uhi)
    hi = max(ulo, uhi)
    targets = []
    if owner == "A":
        first = _fraction_ceil(lo)
        last = _fraction_floor(hi)
        targets = [Fraction(n) for n in range(first, last + 1)]
        lattice = "INTEGER_PROJECTIVE_PHASE_FOR_SIN_ZERO"
    elif owner == "B":
        first = _fraction_ceil(lo - Fraction(1, 2))
        last = _fraction_floor(hi - Fraction(1, 2))
        targets = [Fraction(n) + Fraction(1, 2) for n in range(first, last + 1)]
        lattice = "HALF_INTEGER_PROJECTIVE_PHASE_FOR_COS_ZERO"
    else:
        raise ValueError("unknown component owner")
    if len(targets) > MAX_LATTICE_CANDIDATES:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": "PB00701_V12_COMPONENT_LATTICE_BUDGET_EXHAUSTED",
            "is_truth_value": False,
        }
    checked = []
    hits = []
    for target in targets:
        source = (target - u_offset) / u_rate
        if left <= source <= right:
            value = EE.peval(owner_poly, source)
            checked.append({
                "projective_phase": str(target),
                "source": str(source),
                "component_value": str(value),
            })
            if value == 0:
                other_value = EE.peval(other_poly, source)
                if other_value == 0:
                    return {
                        "status": "BLOCKED",
                        "reason": "COINCIDENT_COMPONENT_ROOT_AT_PHASE_LATTICE",
                        "blocker": "PB-007-01",
                    }
                hits.append((source, target, other_value))
    if len(hits) > 1:
        raise AssertionError("one-root neighborhood produced multiple exact lattice root hits")
    if not hits:
        return {
            "status": "CERTIFIED",
            "relation": "COMPONENT_ROOT_IS_NOT_AN_EVENT",
            "owner": owner,
            "root_isolation": [str(left), str(right)],
            "required_phase_lattice": lattice,
            "lattice_candidates_checked": checked,
            "proof": (
                "an event at this component root would require an exact rational phase-lattice "
                "source; every such source in the isolating neighborhood is checked exactly"
            ),
        }
    source, target, other_value = hits[0]
    component_multiplicity = EE.multiplicity_at(owner_poly, source)
    if component_multiplicity is None or component_multiplicity < 1:
        raise AssertionError("exact lattice hit lost component-root multiplicity")
    derivative_owner = EE.peval(EE.deriv(owner_poly), source)
    forced_pi = (
        -derivative_owner / (u_rate * other_value)
        if owner == "A"
        else EE.peval(EE.deriv(owner_poly), source) / (u_rate * other_value)
    )
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_COMPONENT_ROOT_EVENT",
        "owner": owner,
        "source": str(source),
        "projective_phase": str(target),
        "root_isolation": [str(left), str(right)],
        "required_phase_lattice": lattice,
        "component_root_multiplicity": component_multiplicity,
        "event_multiplicity": 1,
        "other_component_value": str(other_value),
        "multiple_event_root_consequence": f"pi={forced_pi}",
        "simplicity_exclusion_theorem": "PI_IS_IRRATIONAL_SO_CANNOT_EQUAL_A_RATIONAL_NUMBER",
        "lattice_candidates_checked": checked,
        "numeric_pi_used": False,
    }


def _delegate_cell(a_poly, b_poly, harmonic, theta_offset, theta_rate, left, right, source_parameter_id):
    left = q(left)
    right = q(right)
    local_a = _affine_reparameter(a_poly, left, right)
    local_b = _affine_reparameter(b_poly, left, right)
    offset = q(theta_offset) + q(theta_rate) * left
    rate = q(theta_rate) * (right - left)
    cos_polys = {harmonic: local_a}
    sin_polys = {harmonic: local_b}
    first = v10._single_harmonic_dual_route(
        cos_polys, sin_polys, offset, rate, source_parameter_id
    )
    if first is None:
        return {
            "status": "BLOCKED",
            "reason": "LOCAL_DUAL_PROJECTIVE_ROUTE_NOT_APPLICABLE",
            "blocker": "PB-007-01",
        }, "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
    if first.get("status") == "CERTIFIED":
        return first, "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
    if first.get("status") == "RESOURCE_REFUSAL":
        return first, "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
    if first.get("reason") in {
        "OPPOSED_RATIO_MONOTONICITY_NOT_CERTIFIED",
        "OPPOSED_DUAL_PROJECTIVE_MONOTONICITY_NOT_CERTIFIED",
    }:
        second = v11._single_harmonic_phase_dominance_route(
            cos_polys, sin_polys, offset, rate, source_parameter_id
        )
        if second is not None:
            return second, "PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO"
    return first, "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"


def _single_harmonic_component_partition_route(
    cos_polys, sin_polys, offset, rate, source_parameter_id
):
    if q(rate) == 0:
        return None
    cos_nonzero = {
        h: _trim(poly) for h, poly in cos_polys.items() if _trim(poly) != [0]
    }
    sin_nonzero = {
        h: _trim(poly) for h, poly in sin_polys.items() if _trim(poly) != [0]
    }
    harmonics = set(cos_nonzero) | set(sin_nonzero)
    if len(harmonics) != 1:
        return None
    harmonic = next(iter(harmonics))
    if harmonic <= 0 or harmonic not in cos_nonzero or harmonic not in sin_nonzero:
        return None
    a_poly = cos_nonzero[harmonic]
    b_poly = sin_nonzero[harmonic]
    common = EE.pgcd(a_poly, b_poly)
    if EE.degree(common) > 0:
        return {
            "status": "BLOCKED",
            "reason": "COMPONENT_ROOTS_NOT_COPRIME",
            "blocker": "PB-007-01",
        }
    if v9._poly_zero_free_closed(a_poly) is not None or v9._poly_zero_free_closed(b_poly) is not None:
        return None

    partition = build_component_root_partition(a_poly, b_poly)
    if partition.get("status") != "CERTIFIED":
        return partition

    theta_offset = q(offset)
    theta_rate = q(rate)
    projective_offset = 2 * harmonic * theta_offset
    projective_rate = 2 * harmonic * theta_rate

    component_root_events = []
    for neighborhood in partition["root_neighborhoods"]:
        if neighborhood["owner"] == "A":
            owner_poly, other_poly = a_poly, b_poly
        else:
            owner_poly, other_poly = b_poly, a_poly
        event = _component_root_event(
            neighborhood, owner_poly, other_poly, projective_offset, projective_rate
        )
        component_root_events.append(event)
        if event.get("status") != "CERTIFIED":
            return event

    cell_results = []
    endpoint_events = {}
    total_open = 0
    for cell in partition["cells"]:
        left, right = map(q, cell["source_interval"])
        route, route_kind = _delegate_cell(
            a_poly, b_poly, harmonic, theta_offset, theta_rate,
            left, right, source_parameter_id,
        )
        if route.get("status") != "CERTIFIED":
            return {
                "status": route.get("status", "BLOCKED"),
                "reason": route.get("reason", "LOCAL_COMPONENT_PARTITION_CELL_UNRESOLVED"),
                "blocker": "PB-007-01",
                "partition": partition,
                "failed_cell": cell,
                "delegate_route_kind": route_kind,
                "delegate": route,
            }
        total_open += route["open_roots"]["distinct"]
        width = right - left
        converted_endpoints = []
        for endpoint in route.get("endpoint_events", []):
            local_source = q(endpoint["source"])
            global_source = left + width * local_source
            converted = dict(endpoint)
            converted["cell_local_source"] = endpoint["source"]
            converted["source"] = str(global_source)
            converted_endpoints.append(converted)
            key = str(global_source)
            if key in endpoint_events:
                if endpoint_events[key].get("multiplicity") != converted.get("multiplicity"):
                    raise AssertionError("shared partition endpoint changed multiplicity")
            else:
                endpoint_events[key] = converted
        cell_results.append({
            "cell": cell,
            "route_kind": route_kind,
            "route": route,
            "global_endpoint_events": converted_endpoints,
        })

    unique_endpoints = [endpoint_events[key] for key in sorted(endpoint_events, key=q)]
    certified_total = total_open + len(unique_endpoints)
    exact_component_events = [
        event for event in component_root_events
        if event.get("relation") == "EXACT_COMPONENT_ROOT_EVENT"
    ]
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_FINITE_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC_EVENT_DECISION",
        "source_parameter_id": source_parameter_id,
        "harmonic": harmonic,
        "cos_polynomial": [str(value) for value in a_poly],
        "sin_polynomial": [str(value) for value in b_poly],
        "coprime_proof": partition["coprime_proof"],
        "component_root_partition": partition,
        "component_root_event_classification": component_root_events,
        "cell_decisions": cell_results,
        "shared_partition_endpoint_policy": "DEDUPLICATE_BY_EXACT_GLOBAL_RATIONAL_SOURCE",
        "unique_partition_endpoint_events": unique_endpoints,
        "open_roots": {
            "distinct": total_open,
            "multiplicity_sum": total_open,
            "multiple_distinct": 0,
            "all_simple": True,
        },
        "all_certified_events": {
            "open_distinct": total_open,
            "endpoint_distinct": len(unique_endpoints),
            "multiplicity_sum": certified_total,
            "all_simple": True,
        },
        "exact_component_root_event_count": len(exact_component_events),
        "component_root_simplicity_theorem": (
            "at an A=0 integer-phase or B=0 half-integer-phase event, a multiple "
            "event root would force pi to equal an exact rational number"
        ),
        "numeric_pi_used": False,
        "sampling_used": False,
    }


def _is_upgradeable_component_span(span):
    route = span.get("route", {})
    return (
        span.get("route_kind")
        == "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
        and route.get("status") == "BLOCKED"
        and route.get("reason") == "NO_ZERO_FREE_PROJECTIVE_COMPONENT_FOR_DUAL_RATIO_ROUTE"
    )


def analyze_component_partition_event(spec):
    baseline = v11.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict):
        return baseline
    if baseline.get("status") == "CERTIFIED":
        return baseline
    if baseline.get("relation") != "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER":
        return baseline

    rate = q(baseline["phase_turn_law"]["rate"])
    offset_global = q(baseline["phase_turn_law"]["offset"])
    unresolved = False
    upgraded = []
    for original_span in baseline["spans"]:
        span = dict(original_span)
        if _is_upgradeable_component_span(span):
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
            replacement = _single_harmonic_component_partition_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC"
                span["route"] = replacement
                span["local_phase_turn_law"] = {
                    "offset": str(local_offset),
                    "rate": str(local_rate),
                    "local_parameter": "s=(u-lo)/(hi-lo)",
                    "shared_parameter": baseline["source_parameter_id"],
                }
        if span["route"].get("status") != "CERTIFIED":
            unresolved = True
        upgraded.append(span)

    statuses = [span["route"].get("status") for span in upgraded]
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
        "FINITE_EXACT_PIECEWISE_COMPONENT_ROOT_PARTITION_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v12_component_root_partition_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict) and spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
        return analyze_component_partition_event(spec)
    return v11.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V12_COMPONENT_PARTITION_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
