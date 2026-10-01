#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from functools import cmp_to_key
from math import gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_orientation_root_partition_model as v41  # noqa: E402

q = v41.q
v22 = v41.v22

V44_ROUTE = "EXACT_REAL_ALGEBRAIC_ORIENTATION_CUT_BOUNDARY"
IRRATIONAL_V41_REASON = (
    "IRRATIONAL_ALGEBRAIC_ORIENTATION_ROOT_NOT_REPRESENTABLE_BY_CURRENT_RATIONAL_CHILD_PARAMETER_MODEL"
)
V44_BLOCKER = "ALGEBRAIC_ORIENTATION_COORDINATE_CERTIFIED_BUT_EXACT_CONSUMPTION_AUTHORITY_MISSING"


def _exact(value):
    if isinstance(value, float):
        raise TypeError("binary float is not exact authority")
    return q(value)


def _trim(poly):
    return v41._trim([_exact(value) for value in poly])


def _degree(poly):
    poly = _trim(poly)
    return -1 if poly == [0] else len(poly) - 1


def _monic(poly):
    poly = _trim(poly)
    if poly == [0]:
        return poly
    lead = poly[-1]
    return _trim([value / lead for value in poly])


def _pgcd(a, b):
    a, b = _trim(a), _trim(b)
    while b != [0]:
        _, rem = v41._poly_divmod(a, b)
        a, b = b, rem
    return _monic(a)


def _square_free_part(poly):
    poly = _trim(poly)
    if _degree(poly) <= 0:
        return poly
    common = _pgcd(poly, v41._pderiv(poly))
    quotient, remainder = v41._poly_divmod(poly, common)
    if remainder != [0]:
        raise AssertionError("exact square-free division failed")
    return _monic(quotient)


def _sturm_open_root_count(poly, lo, hi):
    poly = _trim(poly)
    lo, hi = _exact(lo), _exact(hi)
    if not lo < hi:
        raise ValueError("invalid exact interval")
    if _degree(poly) <= 0:
        return 0
    if v41._peval(poly, lo) == 0 or v41._peval(poly, hi) == 0:
        raise ValueError("Sturm open interval endpoint is an exact root")
    seq = v41._sturm_sequence(poly)
    return v41._variations(seq, lo) - v41._variations(seq, hi)


def _primitive_integer_polynomial(poly):
    ints = list(v41._primitive_integer_coefficients(_trim(poly)))
    if ints and ints[-1] < 0:
        ints = [-value for value in ints]
    content = 0
    for value in ints:
        content = gcd(content, abs(int(value)))
    if content > 1:
        ints = [int(value) // content for value in ints]
    return ints


def _rational_roots_open(poly):
    work, _, _ = v41._strip_endpoint_roots(_square_free_part(poly))
    if _degree(work) <= 0:
        return []
    ints = _primitive_integer_polynomial(work)
    if not ints or ints[0] == 0:
        raise AssertionError("endpoint stripping left zero constant term")
    roots = set()
    for numerator in v41._divisors(ints[0]):
        for denominator in v41._divisors(ints[-1]):
            if not denominator:
                continue
            root = Fraction(numerator, denominator)
            if 0 < root < 1 and v41._peval(work, root) == 0:
                roots.add(root)
    return sorted(roots)


def _remove_rational_roots_once(poly, roots):
    work = _trim(poly)
    for root in roots:
        quotient, remainder = v41._poly_divmod(work, [-root, Fraction(1)])
        if remainder != [0]:
            raise AssertionError("exact rational-root removal failed")
        work = quotient
    return _trim(work)


def _refine_unique_interval(poly, lo, hi):
    poly = _trim(poly)
    lo, hi = _exact(lo), _exact(hi)
    if _sturm_open_root_count(poly, lo, hi) != 1:
        raise ValueError("interval does not isolate exactly one open root")
    midpoint = (lo + hi) / 2
    if v41._peval(poly, midpoint) == 0:
        raise AssertionError("irrational algebraic root unexpectedly hit a rational midpoint")
    left = _sturm_open_root_count(poly, lo, midpoint)
    right = _sturm_open_root_count(poly, midpoint, hi)
    if left == 1 and right == 0:
        return lo, midpoint
    if left == 0 and right == 1:
        return midpoint, hi
    raise AssertionError("exact unique-root refinement lost conservation")


def _isolate_irrational_roots(poly):
    poly = _trim(poly)
    total = _sturm_open_root_count(poly, Fraction(0), Fraction(1))
    if total == 0:
        return []
    queue = [(Fraction(0), Fraction(1), total)]
    isolated = []
    while queue:
        lo, hi, count = queue.pop(0)
        if count == 1:
            while lo == 0 or hi == 1:
                lo, hi = _refine_unique_interval(poly, lo, hi)
            isolated.append((lo, hi))
            continue
        midpoint = (lo + hi) / 2
        if v41._peval(poly, midpoint) == 0:
            raise AssertionError("irrational-only polynomial has a rational midpoint root")
        left = _sturm_open_root_count(poly, lo, midpoint)
        right = _sturm_open_root_count(poly, midpoint, hi)
        if left + right != count:
            raise AssertionError("exact Sturm subdivision lost a root")
        if left:
            queue.append((lo, midpoint, left))
        if right:
            queue.append((midpoint, hi, right))
    isolated.sort()
    return isolated


def _multiplicity_at_isolated_root(original_poly, lo, hi):
    current = _trim(original_poly)
    if _sturm_open_root_count(_square_free_part(current), lo, hi) != 1:
        raise ValueError("multiplicity interval is not source-root unique")
    multiplicity = 1
    while _degree(current) > 0:
        common = _pgcd(current, v41._pderiv(current))
        if _degree(common) <= 0:
            break
        common_sf = _square_free_part(common)
        if _sturm_open_root_count(common_sf, lo, hi) == 0:
            break
        multiplicity += 1
        current = common
    return multiplicity


def validate_algebraic_root_certificate(certificate, source_poly=None):
    assert certificate["root_type"] == "REAL_ALGEBRAIC_IRRATIONAL"
    defining = [_exact(value) for value in certificate["defining_square_free_polynomial"]]
    assert _primitive_integer_polynomial(defining) == certificate["defining_square_free_polynomial"]
    assert _degree(_pgcd(defining, v41._pderiv(defining))) == 0
    lo, hi = map(_exact, certificate["isolating_interval"])
    assert Fraction(0) < lo < hi < Fraction(1)
    assert v41._peval(defining, lo) != 0
    assert v41._peval(defining, hi) != 0
    assert _sturm_open_root_count(defining, lo, hi) == 1
    assert certificate["unique_root_proof"]["sturm_open_root_count"] == 1
    assert certificate["binary_float_used"] is False
    assert certificate["epsilon_used"] is False
    if source_poly is not None:
        assert _multiplicity_at_isolated_root(source_poly, lo, hi) == certificate["multiplicity"]
    return True


def exact_algebraic_orientation_roots(poly, label):
    """Certify every irrational algebraic interior root without approximating it."""
    try:
        original = _trim(poly)
        if original == [0]:
            return {"status": "BLOCKED", "reason": f"{label}_IDENTICALLY_ZERO", "blocker": "PB-007-01"}
        square_free = _square_free_part(original)
        rational_roots = _rational_roots_open(square_free)
        irrational_part = _remove_rational_roots_once(square_free, rational_roots)
        intervals = _isolate_irrational_roots(irrational_part) if _degree(irrational_part) > 0 else []
        defining = _primitive_integer_polynomial(square_free)
        certificates = []
        for index, (lo, hi) in enumerate(intervals):
            cert = {
                "root_type": "REAL_ALGEBRAIC_IRRATIONAL",
                "label": label,
                "defining_square_free_polynomial": defining,
                "isolating_interval": [str(lo), str(hi)],
                "unique_root_proof": {
                    "method": "EXACT_STURM_OPEN_INTERVAL_COUNT",
                    "sturm_open_root_count": 1,
                    "rational_endpoints_are_not_roots": True,
                },
                "multiplicity": _multiplicity_at_isolated_root(original, lo, hi),
                "source_endpoint_order": "0 < alpha < 1",
                "order_index_within_polynomial": index,
                "binary_float_used": False,
                "epsilon_used": False,
                "sampling_used": False,
                "approximate_root_used": False,
            }
            validate_algebraic_root_certificate(cert, original)
            certificates.append(cert)
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_REAL_ALGEBRAIC_ROOT_CERTIFICATE_BY_SQUARE_FREE_STURM_ISOLATION",
            "label": label,
            "rational_open_roots_retained_by_v41": [str(root) for root in rational_roots],
            "irrational_open_roots": certificates,
            "irrational_open_root_count": len(certificates),
            "all_roots_accounted_exactly": (
                len(rational_roots) + len(certificates)
                == v41._distinct_open_root_count(original)
            ),
            "binary_float_used": False,
            "epsilon_used": False,
            "adaptive_refinement_cap_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V44_ALGEBRAIC_ROOT_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _certificate_polynomial(certificate):
    return [_exact(value) for value in certificate["defining_square_free_polynomial"]]


def _certificate_interval(certificate):
    return tuple(map(_exact, certificate["isolating_interval"]))


def compare_exact_algebraic_roots(certificate_a, certificate_b):
    """Return -1, 0, +1 using exact gcd/Sturm authority only."""
    validate_algebraic_root_certificate(certificate_a)
    validate_algebraic_root_certificate(certificate_b)
    pa, pb = _certificate_polynomial(certificate_a), _certificate_polynomial(certificate_b)
    alo, ahi = _certificate_interval(certificate_a)
    blo, bhi = _certificate_interval(certificate_b)
    common = _pgcd(pa, pb)
    while True:
        overlap_lo, overlap_hi = max(alo, blo), min(ahi, bhi)
        if overlap_lo < overlap_hi and _degree(common) > 0:
            if v41._peval(common, overlap_lo) != 0 and v41._peval(common, overlap_hi) != 0:
                if _sturm_open_root_count(common, overlap_lo, overlap_hi) == 1:
                    return 0
        if ahi <= blo:
            return -1
        if bhi <= alo:
            return 1
        if (ahi - alo) >= (bhi - blo):
            alo, ahi = _refine_unique_interval(pa, alo, ahi)
        else:
            blo, bhi = _refine_unique_interval(pb, blo, bhi)


def exact_algebraic_orientation_cut_certificate(cos_polys, sin_polys):
    """Derive exact irrational A/B cut certificates and exact sibling ordering."""
    try:
        records = []
        rational_records = []
        harmonics = sorted(
            h for h in set(cos_polys) | set(sin_polys)
            if int(h) > 0
            and (_trim(cos_polys.get(h, [0])) != [0] or _trim(sin_polys.get(h, [0])) != [0])
        )
        for harmonic in harmonics:
            c = _trim(cos_polys.get(harmonic, [0]))
            s = _trim(sin_polys.get(harmonic, [0]))
            if c == [0] or s == [0]:
                continue
            a, b = v41._rotated_polynomials(c, s)
            for coordinate, poly in (("A", a), ("B", b)):
                result = exact_algebraic_orientation_roots(poly, f"H{harmonic}_{coordinate}")
                if result.get("status") != "CERTIFIED":
                    return result
                for root in result["rational_open_roots_retained_by_v41"]:
                    rational_records.append({
                        "harmonic": harmonic,
                        "coordinate": coordinate,
                        "source": root,
                        "owner": "v41",
                    })
                for cert in result["irrational_open_roots"]:
                    records.append({
                        "harmonic": harmonic,
                        "coordinate": coordinate,
                        "multiplicity": cert["multiplicity"],
                        "certificate": cert,
                    })

        groups = []
        for record in records:
            matched = None
            for group in groups:
                if compare_exact_algebraic_roots(record["certificate"], group["representative"]) == 0:
                    matched = group
                    break
            if matched is None:
                groups.append({
                    "representative": record["certificate"],
                    "ownership": [{
                        "harmonic": record["harmonic"],
                        "coordinate": record["coordinate"],
                        "multiplicity": record["multiplicity"],
                    }],
                })
            else:
                matched["ownership"].append({
                    "harmonic": record["harmonic"],
                    "coordinate": record["coordinate"],
                    "multiplicity": record["multiplicity"],
                })

        def _cmp(left, right):
            return compare_exact_algebraic_roots(left["representative"], right["representative"])

        groups.sort(key=cmp_to_key(_cmp))
        canonical = []
        for index, group in enumerate(groups):
            canonical.append({
                "order_index": index,
                "certificate": group["representative"],
                "ownership": sorted(
                    group["ownership"],
                    key=lambda item: (item["harmonic"], item["coordinate"], item["multiplicity"]),
                ),
                "deduplication_authority": (
                    "EXACT_POLYNOMIAL_GCD_PLUS_STURM_SHARED_ROOT"
                    if len(group["ownership"]) > 1
                    else "SINGLE_SOURCE_OWNER"
                ),
            })

        pairwise_order = []
        for left, right in zip(canonical, canonical[1:]):
            relation = compare_exact_algebraic_roots(
                left["certificate"], right["certificate"]
            )
            assert relation == -1
            pairwise_order.append({
                "lower_order_index": left["order_index"],
                "higher_order_index": right["order_index"],
                "relation": "STRICTLY_LESS",
                "authority": "EXACT_STURM_REFINEMENT_AND_RATIONAL_INTERVAL_SEPARATION",
            })

        return {
            "status": "CERTIFIED",
            "relation": "EXACT_SOURCE_OWNED_REAL_ALGEBRAIC_ORIENTATION_CUT_COORDINATES",
            "canonical_irrational_cuts": canonical,
            "rational_orientation_roots_retained_by_v41": rational_records,
            "pairwise_exact_order": pairwise_order,
            "source_endpoint_order_proved": True,
            "caller_root_metadata_trusted": False,
            "caller_isolating_intervals_trusted": False,
            "binary_float_used": False,
            "epsilon_used": False,
            "approximate_ordering_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError, OverflowError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V44_ORIENTATION_CERT_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _phase_endpoint_blocker(root_certificate, offset, rate):
    offset, rate = _exact(offset), _exact(rate)
    if rate == 0:
        return {
            "status": "RATIONAL_PHASE_ONLY",
            "phase_turn": str(offset),
            "existing_rational_turn_endpoint_authority_applicable": True,
        }
    return {
        "status": "BLOCKED",
        "reason": "ALGEBRAIC_IRRATIONAL_PHASE_ENDPOINT_SIGN_EQUALITY_MULTIPLICITY_AUTHORITY_MISSING",
        "phase_expression": f"{offset}+({rate})*alpha",
        "alpha_certificate": root_certificate,
        "phase_is_algebraic_irrational": True,
        "required_new_authority": (
            "an exact theorem/algorithm deciding the required rational-coefficient "
            "trigonometric endpoint equality/sign/multiplicity at an algebraic-irrational turn"
        ),
        "existing_v8_gelfond_schneider_scope": (
            "only excludes algebraic-irrational coincidence with a nonzero rational "
            "trigonometric factor under its product-factorization preconditions; it does "
            "not provide a general endpoint sign or multiplicity oracle"
        ),
        "numerical_trigonometry_used": False,
        "approximation_used": False,
    }


def _v44_route_for_span(span, baseline, local_offset, local_rate):
    cos_polys = {
        int(h): [_exact(value) for value in poly]
        for h, poly in span["cos_polynomials"].items()
    }
    sin_polys = {
        int(h): [_exact(value) for value in poly]
        for h, poly in span["sin_polynomials"].items()
    }
    cut_certificate = exact_algebraic_orientation_cut_certificate(cos_polys, sin_polys)
    if cut_certificate.get("status") != "CERTIFIED":
        return cut_certificate
    if not cut_certificate["canonical_irrational_cuts"]:
        return {
            "status": "BLOCKED",
            "reason": "V44_EXPECTED_IRRATIONAL_ORIENTATION_CUT_NOT_REPRODUCED_FROM_SOURCE",
            "blocker": "PB-007-01",
        }

    endpoint_blockers = []
    for cut in cut_certificate["canonical_irrational_cuts"]:
        endpoint_blockers.append({
            "order_index": cut["order_index"],
            "phase_endpoint_authority": _phase_endpoint_blocker(
                cut["certificate"], local_offset, local_rate
            ),
        })

    return {
        "status": "BLOCKED",
        "reason": V44_BLOCKER,
        "blocker": "PB-007-01",
        "relation": V44_ROUTE,
        "source_parameter_id": baseline["source_parameter_id"],
        "source_interval": list(span["source_interval"]),
        "local_phase_turn_law": {
            "offset": str(local_offset),
            "rate": str(local_rate),
        },
        "algebraic_cut_coordinate_authority": cut_certificate,
        "source_interval_restriction": {
            "status": "CERTIFIED",
            "representation": (
                "retain the original rational source polynomials and bind each child "
                "as an exact source-parameter interval with a certified real-algebraic boundary"
            ),
            "normalization_required": False,
            "binary_float_used": False,
        },
        "normalized_child_reparameterization": {
            "status": "BLOCKED",
            "reason": "CURRENT_V27_V41_CHILD_MODEL_REQUIRES_RATIONAL_AFFINE_MAP_COEFFICIENTS",
            "missing_authority": (
                "an exact algebraic-number coefficient representation and canonical "
                "child-map binding for Q(alpha)-valued normalized polynomial coefficients"
            ),
            "approximate_coefficients_allowed": False,
        },
        "phase_endpoint_blockers": endpoint_blockers,
        "consumption_decision": (
            "DO_NOT_PARTITION: coordinate/order/multiplicity are exact, but current "
            "child normalization and general algebraic-irrational phase endpoint semantics "
            "are not established"
        ),
        "caller_child_maps_trusted": False,
        "caller_endpoint_signs_trusted": False,
        "caller_root_counts_trusted": False,
        "correctness_weakened": False,
    }


def analyze_algebraic_orientation_cut_event(spec):
    baseline = v41.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict) or baseline.get("status") == "CERTIFIED":
        return baseline
    if baseline.get("relation") != "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER":
        return baseline

    phase = baseline.get("phase_turn_law", {})
    rate = _exact(phase.get("rate", "0"))
    offset = _exact(phase.get("offset", "0"))
    upgraded = []
    touched = False
    statuses = []

    for original_span in baseline.get("spans", []):
        span = dict(original_span)
        route = dict(span.get("route", {}))
        if (
            route.get("status") == "BLOCKED"
            and route.get("reason") == IRRATIONAL_V41_REASON
            and "cos_polynomials" in span
            and "sin_polynomials" in span
        ):
            left, right = map(_exact, span["source_interval"])
            width = right - left
            local_offset = offset + rate * left
            local_rate = rate * width
            replacement = _v44_route_for_span(
                span, baseline, local_offset, local_rate
            )
            span["route_kind"] = "PB00701_V44_EXACT_REAL_ALGEBRAIC_ORIENTATION_CUT_BOUNDARY"
            span["route"] = replacement
            touched = True
        upgraded.append(span)
        statuses.append(span.get("route", {}).get("status"))

    if not touched:
        return baseline

    result = dict(baseline)
    result["spans"] = upgraded
    result["status"] = (
        "RESOURCE_REFUSAL"
        if "RESOURCE_REFUSAL" in statuses
        else "SEMANTIC_BLOCKER"
        if "SEMANTIC_BLOCKER" in statuses
        else "BLOCKED"
    )
    result["relation"] = "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    result["blocker"] = "PB-007-01"
    result["v44_algebraic_orientation_cut_boundary_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if not isinstance(spec, dict):
        return v41.classify_required_analytic_event(spec)
    source = dict(spec)
    for key in (
        "algebraic_roots",
        "algebraic_root_certificates",
        "isolating_intervals",
        "algebraic_order",
        "algebraic_child_maps",
        "algebraic_reparameterization",
        "algebraic_endpoint_signs",
        "algebraic_endpoint_multiplicity",
        "algebraic_root_counts",
    ):
        source.pop(key, None)
    if source.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
        return analyze_algebraic_orientation_cut_event(source)
    return v41.classify_required_analytic_event(source)


def resource_refusal():
    return {
        "status": "RESOURCE_REFUSAL",
        "reason": "PB00701_V44_EXACT_RESOURCE_REFUSAL",
        "is_truth_value": False,
    }
