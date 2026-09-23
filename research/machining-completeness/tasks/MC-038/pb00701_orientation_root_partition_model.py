#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from math import gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_orientation_transition_bridge_model as v42  # noqa: E402
import pb00701_phase_sector_partition_model as v27  # noqa: E402

v40 = v42.v40
q = v42.q
v39 = v40.v39
v22 = v40.v22
V41_ROUTE = "EXACT_ROTATED_COORDINATE_ORIENTATION_ROOT_PARTITION_COMPOSITION"


def _trim(poly):
    return v42._trim(poly)


def _peval(poly, x):
    x = q(x)
    out = Fraction(0)
    for value in reversed(_trim(poly)):
        out = out * x + q(value)
    return out


def _pderiv(poly):
    poly = _trim(poly)
    return _trim([Fraction(i) * poly[i] for i in range(1, len(poly))]) if len(poly) > 1 else [Fraction(0)]


def _poly_divmod(a, b):
    a, b = _trim(a), _trim(b)
    if b == [0]:
        raise ZeroDivisionError
    if len(a) < len(b):
        return [Fraction(0)], a
    out = [Fraction(0)] * (len(a) - len(b) + 1)
    rem = list(a)
    while rem != [0] and len(rem) >= len(b):
        k = len(rem) - len(b)
        c = rem[-1] / b[-1]
        out[k] = c
        for j, bv in enumerate(b):
            rem[k + j] -= c * bv
        rem = _trim(rem)
    return _trim(out), _trim(rem)


def _sturm_sequence(poly):
    p0, p1 = _trim(poly), _pderiv(poly)
    if p0 == [0] or p1 == [0]:
        return [p0]
    seq = [p0, p1]
    while seq[-1] != [0]:
        _, rem = _poly_divmod(seq[-2], seq[-1])
        if rem == [0]:
            break
        seq.append(_trim([-x for x in rem]))
    return seq


def _variations(seq, x):
    signs = [(_peval(poly, x) > 0) - (_peval(poly, x) < 0) for poly in seq]
    signs = [s for s in signs if s]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def _strip_endpoint_roots(poly):
    poly = _trim(poly)
    left_mult = 0
    while len(poly) > 1 and poly[0] == 0:
        poly = _trim(poly[1:])
        left_mult += 1
    right_mult = 0
    divisor = [Fraction(-1), Fraction(1)]
    while len(poly) > 1 and _peval(poly, 1) == 0:
        quotient, rem = _poly_divmod(poly, divisor)
        if rem != [0]:
            raise AssertionError("exact endpoint division failed")
        poly = quotient
        right_mult += 1
    return poly, left_mult, right_mult


def _distinct_open_root_count(poly):
    reduced, _, _ = _strip_endpoint_roots(poly)
    if len(reduced) <= 1:
        return 0
    seq = _sturm_sequence(reduced)
    return _variations(seq, Fraction(0)) - _variations(seq, Fraction(1))


def _lcm(a, b):
    return abs(a * b) // gcd(a, b) if a and b else 0


def _divisors(n):
    n = abs(int(n))
    if n == 0:
        return [0]
    out = set()
    d = 1
    while d * d <= n:
        if n % d == 0:
            out.add(d)
            out.add(n // d)
        d += 1
    return sorted(out)


def _primitive_integer_coefficients(poly):
    den = 1
    for value in _trim(poly):
        den = _lcm(den, q(value).denominator)
    ints = [int(q(value) * den) for value in _trim(poly)]
    content = 0
    for value in ints:
        content = gcd(content, abs(value))
    return [value // content for value in ints] if content else ints


def _root_multiplicity(poly, root):
    current = _trim(poly)
    divisor = [-q(root), Fraction(1)]
    multiplicity = 0
    while len(current) > 1 and _peval(current, root) == 0:
        current, rem = _poly_divmod(current, divisor)
        if rem != [0]:
            raise AssertionError("exact rational root division failed")
        multiplicity += 1
    return multiplicity


def exact_rational_orientation_roots(poly, label):
    """Enumerate every interior root iff all are rational; otherwise fail closed."""
    try:
        poly = _trim(poly)
        if poly == [0]:
            return {"status": "BLOCKED", "reason": f"{label}_IDENTICALLY_ZERO", "blocker": "PB-007-01"}
        if len(poly) <= 1:
            return {"status": "CERTIFIED", "roots": [], "endpoint_roots": [], "all_open_roots_rational": True}
        ints = _primitive_integer_coefficients(poly)
        candidates = set()
        if ints[0] != 0:
            for p in _divisors(ints[0]):
                for d in _divisors(ints[-1]):
                    if d:
                        x = Fraction(p, d)
                        if 0 < x < 1:
                            candidates.add(x)
        roots = sorted(x for x in candidates if _peval(poly, x) == 0)
        total = _distinct_open_root_count(poly)
        if total != len(roots):
            return {
                "status": "BLOCKED",
                "reason": "IRRATIONAL_ALGEBRAIC_ORIENTATION_ROOT_NOT_REPRESENTABLE_BY_CURRENT_RATIONAL_CHILD_PARAMETER_MODEL",
                "blocker": "PB-007-01",
                "label": label,
                "distinct_open_root_count": total,
                "exact_rational_open_roots_found": [str(x) for x in roots],
                "missing_exact_root_count": total - len(roots),
                "correctness_weakened": False,
            }
        endpoint_roots = [
            {"source": str(x), "multiplicity": _root_multiplicity(poly, x)}
            for x in (Fraction(0), Fraction(1)) if _peval(poly, x) == 0
        ]
        return {
            "status": "CERTIFIED",
            "relation": "FINITE_EXACT_RATIONAL_ROOT_THEOREM_PLUS_STURM_COMPLETENESS",
            "roots": [{"source": str(x), "multiplicity": _root_multiplicity(poly, x)} for x in roots],
            "endpoint_roots": endpoint_roots,
            "distinct_open_root_count": total,
            "all_open_roots_rational": True,
            "binary_float_used": False,
            "epsilon_used": False,
            "approximate_root_ordering_used": False,
            "adaptive_refinement_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": f"PB00701_V41_ROOT_RESOURCE_REFUSAL:{type(exc).__name__}", "is_truth_value": False}


def _rotated_polynomials(cos_poly, sin_poly):
    c, s = _trim(cos_poly), _trim(sin_poly)
    a = _trim(v22._pscale(v22._padd(c, s), Fraction(1, 2)))
    b = _trim(v22._pscale(v22._padd(c, v22._pscale(s, -1)), Fraction(1, 2)))
    return a, b


def _orientation_cut_certificate(cos_polys, sin_polys, offset, rate):
    harmonics = sorted(h for h in set(cos_polys) | set(sin_polys) if int(h) > 0 and (_trim(cos_polys.get(h, [0])) != [0] or _trim(sin_polys.get(h, [0])) != [0]))
    cut_causes, roots, endpoints = {}, [], []
    for harmonic in harmonics:
        c, s = _trim(cos_polys.get(harmonic, [0])), _trim(sin_polys.get(harmonic, [0]))
        if c == [0] or s == [0]:
            continue
        a, b = _rotated_polynomials(c, s)
        for name, poly in (("A", a), ("B", b)):
            cert = exact_rational_orientation_roots(poly, f"H{harmonic}_{name}")
            if cert.get("status") != "CERTIFIED":
                return cert
            for root in cert["roots"]:
                x = q(root["source"])
                cause = {"kind": "orientation_root", "harmonic": harmonic, "coordinate": name, "multiplicity": root["multiplicity"]}
                cut_causes.setdefault(x, []).append(cause)
                roots.append({**root, "harmonic": harmonic, "coordinate": name})
            endpoints.extend({**root, "harmonic": harmonic, "coordinate": name} for root in cert["endpoint_roots"])
    sector = v27.exact_sector_cuts(offset, rate, harmonics)
    if sector.get("status") != "CERTIFIED":
        return sector
    for crossing in sector.get("crossings", []):
        x = q(crossing["source_cut"])
        cut_causes.setdefault(x, []).append({"kind": "historical_phase_sector_cut", "causes": crossing["causes"]})
    cuts = sorted(cut_causes)
    return {
        "status": "CERTIFIED",
        "relation": "FINITE_EXACT_SOURCE_OWNED_ORIENTATION_ROOT_AND_HISTORICAL_CERTIFICATE_PARTITION",
        "cuts": [str(x) for x in cuts],
        "cut_records": [{"source_cut": str(x), "causes": cut_causes[x]} for x in cuts],
        "orientation_roots": roots,
        "endpoint_orientation_roots": endpoints,
        "coincident_cuts_deduplicated": True,
        "caller_cuts_trusted": False,
        "finite_termination": "finite harmonic lattice; rational-root theorem enumeration checked complete by exact Sturm distinct-root count; finite historical sector cuts",
    }


def _partition_route(cos_polys, sin_polys, offset, rate, source_parameter_id, parent_interval):
    cert = _orientation_cut_certificate(cos_polys, sin_polys, offset, rate)
    if cert.get("status") != "CERTIFIED":
        return cert
    if not cert["orientation_roots"]:
        return None
    boundaries = [Fraction(0), *[q(x) for x in cert["cuts"]], Fraction(1)]
    children = []
    parent_lo, parent_hi = q(parent_interval[0]), q(parent_interval[1])
    parent_width = parent_hi - parent_lo
    for left, right in zip(boundaries, boundaries[1:]):
        if not left < right:
            continue
        child_spec, child_cos, child_sin = v27._child_spec(cos_polys, sin_polys, offset, rate, left, right, source_parameter_id)
        child_result = v42.classify_required_analytic_event(child_spec)
        if child_result.get("status") == "RESOURCE_REFUSAL":
            return {"status": "RESOURCE_REFUSAL", "reason": "PB00701_V41_CHILD_RESOURCE_REFUSAL", "is_truth_value": False, "failed_child_interval": [str(left), str(right)]}
        summary = v27._single_span_child_summary(child_result, child_cos, child_sin, q(offset) + q(rate) * left, q(rate) * (right - left))
        children.append({
            "parent_local_interval": [str(left), str(right)],
            "parent_source_interval": [str(parent_lo + parent_width * left), str(parent_lo + parent_width * right)],
            "exact_parent_to_child_map": f"s={left}+({right-left})*u",
            "source_parameter_id": source_parameter_id,
            "child_result": child_result,
            "summary": summary,
        })
        if summary.get("status") != "CERTIFIED":
            return {"status": summary.get("status", "BLOCKED"), "reason": "V41_COMPLETE_V42_CHILD_NOT_COMPOSABLE", "blocker": "PB-007-01", "failed_child_interval": [str(left), str(right)], "partition_certificate": cert, "children": children, "child_blocker": summary, **({"is_truth_value": False} if summary.get("status") == "RESOURCE_REFUSAL" else {})}
    composition = v27._compose_child_summaries(children)
    if composition.get("status") != "CERTIFIED":
        return {**composition, "partition_certificate": cert, "children": children}
    return {
        "status": "CERTIFIED",
        "relation": V41_ROUTE,
        "predecessor_authority": "complete v42 classifier (including historical precedence through v40)",
        "source_parameter_id": source_parameter_id,
        "parent_source_interval": [str(parent_lo), str(parent_hi)],
        "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(q(rate))},
        "partition_certificate": cert,
        "children": children,
        "child_count": len(children),
        "all_children_reclassified_by_complete_v42_authority": True,
        "composition": composition,
        **{key: composition[key] for key in ("distinct_roots_open", "multiple_roots_open", "left_endpoint_root", "right_endpoint_root", "total_distinct_roots_closed", "endpoint_root_multiplicity", "all_roots_simple", "internal_cut_roots")},
        "orientation_roots_are_proof_geometry_only": True,
        "zero_adjacent_children_require_v42_or_other_independent_current_authority": True,
        "caller_partition_trusted": False,
        "sampling_used": False,
        "epsilon_used": False,
        "binary_float_used": False,
        "approximate_root_ordering_used": False,
        "arbitrary_subdivision_cap_used": False,
    }


def analyze_orientation_root_partition_event(spec):
    baseline = v42.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict) or baseline.get("status") == "CERTIFIED":
        return baseline
    if baseline.get("relation") != "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER":
        return baseline
    phase = baseline.get("phase_turn_law", {})
    rate, offset_global = q(phase.get("rate", "0")), q(phase.get("offset", "0"))
    upgraded, unresolved = [], False
    for original_span in baseline.get("spans", []):
        span = dict(original_span)
        old_route = span.get("route", {})
        if old_route.get("status") == "BLOCKED" and "cos_polynomials" in span and "sin_polynomials" in span:
            left, right = q(span["source_interval"][0]), q(span["source_interval"][1])
            width = right - left
            local_offset, local_rate = offset_global + rate * left, rate * width
            cos_polys = {int(h): [q(x) for x in poly] for h, poly in span["cos_polynomials"].items()}
            sin_polys = {int(h): [q(x) for x in poly] for h, poly in span["sin_polynomials"].items()}
            replacement = _partition_route(cos_polys, sin_polys, local_offset, local_rate, baseline["source_parameter_id"], (left, right))
            if replacement is not None:
                span["route_kind"] = "PB00701_V41_EXACT_ROTATED_COORDINATE_ORIENTATION_ROOT_PARTITION_COMPOSITION"
                span["route"] = replacement
                span["local_phase_turn_law"] = {"offset": str(local_offset), "rate": str(local_rate), "local_parameter": "s=(u-lo)/(hi-lo)", "shared_parameter": baseline["source_parameter_id"]}
        if span.get("route", {}).get("status") != "CERTIFIED":
            unresolved = True
        upgraded.append(span)
    statuses = [span.get("route", {}).get("status") for span in upgraded]
    status = "RESOURCE_REFUSAL" if "RESOURCE_REFUSAL" in statuses else "SEMANTIC_BLOCKER" if "SEMANTIC_BLOCKER" in statuses else "BLOCKED" if unresolved else "CERTIFIED"
    result = dict(baseline)
    result["status"], result["spans"] = status, upgraded
    result["relation"] = "FINITE_EXACT_PIECEWISE_ORIENTATION_ROOT_PARTITION_EVENT_DECISION" if status == "CERTIFIED" else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v41_orientation_root_partition_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source = dict(spec)
        for key in ("orientation_roots", "orientation_root_certificate", "orientation_partition", "orientation_partition_certificate", "partition", "partition_certificate", "cuts", "root_cuts", "children", "child_certificates", "child_results", "child_root_counts", "child_endpoint_events", "internal_cut_roots", "reparameterization", "root_count", "root_certificate", "multiplicity", "multiplicity_certificate", "sturm_certificate", "sturm_root_count"):
            source.pop(key, None)
        if source.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_orientation_root_partition_event(source)
        return v42.classify_required_analytic_event(source)
    return v42.classify_required_analytic_event(spec)


def resource_refusal():
    return {"status": "RESOURCE_REFUSAL", "reason": "PB00701_V41_EXACT_RESOURCE_REFUSAL", "is_truth_value": False}
