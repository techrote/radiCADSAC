#!/usr/bin/env python3
"""Exact four-child mixed-cut Q(alpha) source restrictions for frozen V44.

DETERMINISTIC_MODEL only. The original rational source, the full source-root
atlas, the positive global derivative and the nonzero irrational-cut sign
are replayed independently. Not a general analytic child zero decider.
"""
from __future__ import annotations

from fractions import Fraction as Q

import pb00701_v44_irrational_cut_source_sign as source_sign

bridge = source_sign.bridge
derivative = source_sign.derivative
v45 = source_sign.v45
trig = source_sign.trig
cut_order = bridge.cut_order

SCHEMA = "radicadsac-pb00701-v44-mixed-cut-child-interface/1.0"
SUCCESS = "EXACT_FROZEN_V44_MIXED_CUT_QALPHA_CHILD_RESTRICTION_RESEARCH"
SIGN_SOURCE_BLOB = "c55a5ee2ab786b2434a717d790a5d35bd109571f"
MAX_REPORT_BYTES = 65536


class Refusal(ValueError):
    pass


class ResourceRefusal(RuntimeError):
    pass


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def pins():
    require(bridge.previous.git_blob(
        bridge.previous.TASK / "pb00701_v44_irrational_cut_source_sign.py"
    ) == SIGN_SOURCE_BLOB, "PINNED_IRRATIONAL_CUT_SIGN_SOURCE_DRIFT")
    source_sign.pins()


def _rational_source_witness(span, t):
    require(type(t) is Q and span.left <= t <= span.right,
            "RATIONAL_BOUNDARY_OUTSIDE_ORIGINAL_SOURCE")
    raw = span.evaluate(t)
    require(type(raw) is tuple and len(raw) == 2
            and all(type(x) is Q for x in raw)
            and raw[0] <= raw[1],
            "INVALID_EXACT_RATIONAL_SOURCE_ENCLOSURE")
    # Preserve full rational containment with compact exact outward bounds.
    lo = derivative._outward_dyadic(raw[0], upward=False)
    hi = derivative._outward_dyadic(raw[1], upward=True)
    require(lo <= raw[0] <= raw[1] <= hi,
            "RATIONAL_BOUNDARY_ENCLOSURE_ROUNDED_INWARD")
    sign = 1 if lo > 0 else (-1 if hi < 0 else 0)
    require(sign != 0, "RATIONAL_BOUNDARY_SIGN_NOT_STRICTLY_DECIDED")
    return {
        "method": "ORIGINAL_RATIONAL_SOURCE_TRIG_OUTWARD_ENCLOSURE",
        "exact_source_coordinate": str(t),
        "outward_enclosure": [str(lo), str(hi)],
        "strict_nonzero_sign": sign,
        "binary_float_or_epsilon_used": False,
    }


def _coordinates(view, field, span, irrational_id):
    boundaries = view["proof_boundaries"]
    require(len(boundaries) == 5
            and [b.get("boundary_id") for b in boundaries] ==
            ["b0", "b1", "b2", "b3", "b4"],
            "FROZEN_FOUR_CHILD_PARTITION_NOT_EXHAUSTIVE")
    alpha = field.element([0, 1])
    out = []
    for i, boundary in enumerate(boundaries):
        if i == 0 or i == len(boundaries) - 1:
            expected = Q(0) if i == 0 else Q(1)
            require(boundary.get("kind") ==
                    ("ORIGINAL_SOURCE_LEFT_ENDPOINT" if i == 0 else
                     "ORIGINAL_SOURCE_RIGHT_ENDPOINT")
                    and Q(boundary["exact_source_coordinate"]) == expected,
                    "ORIGINAL_SOURCE_ENDPOINT_DRIFT")
            out.append((field.element(expected),
                        _rational_source_witness(span, expected)))
        else:
            require(boundary.get("kind") == "EXACT_SOURCE_PROOF_CUT"
                    and boundary.get("is_physical_zero") is False
                    and boundary.get("is_proof_geometry_only") is True,
                    "PHYSICAL_EVENT_FABRICATED_FROM_PROOF_CUT")
            descriptor = boundary["coordinate_descriptor"]
            kind = descriptor["kind"]
            if kind == "ISOLATED_REAL_ROOT":
                require(boundary["boundary_id"] == irrational_id,
                        "UNEXPECTED_OR_MISIDENTIFIED_ALGEBRAIC_CUT")
                out.append((alpha, None))
            else:
                require(kind in ("RATIONAL_ROOT", "RATIONAL_PROOF_CUT"),
                        "UNSUPPORTED_PROOF_CUT_ARITHMETIC")
                rational = cut_order.q(descriptor["local_value"])
                require(Q(0) < rational < Q(1),
                        "RATIONAL_PROOF_CUT_OUTSIDE_SOURCE")
                out.append((field.element(rational),
                            _rational_source_witness(span, rational)))
    require(sum(item[1] is None for item in out) == 1,
            "FROZEN_ALGEBRAIC_CUT_CARDINALITY_DRIFT")
    return out


def _restrict_polynomials(span, field, left, width):
    """Construct actual Q(alpha)[u] channel coefficients and roundtrip."""
    inv = width.inverse()
    output = {}
    for h, pair in sorted(span.terms.items()):
        channels = []
        for source_poly in pair:
            restricted = v45.compose_affine(source_poly, left, width)
            reconstructed = v45.compose_affine(
                restricted, -left * inv, inv)
            original = v45.compose_affine(
                source_poly, field.element(0), field.element(1))
            require(reconstructed == original,
                    "EXACT_CHILD_POLYNOMIAL_SOURCE_ROUNDTRIP_FAILED")
            channels.append([element.record() for element in restricted])
        output[str(h)] = channels
    require(set(output) == {str(h) for h in span.terms},
            "CHILD_HARMONIC_CHANNEL_LOST")
    return output


def prove(*, supplied_atlas=None):
    pins()
    view, span, root, _ = derivative._source_snapshot(supplied_atlas)
    require(view["parent_source_sha256"] == source_sign.bridge.atlas.SOURCE_SHA256
            and span.left == 0 and span.right == 1,
            "SOURCE_ORIGINAL_IDENTITY_NOT_PRESERVED")
    derivative_report = derivative.prove(cells=16, supplied_atlas=view)
    require(derivative_report.get("status") == derivative.SUCCESS
            and derivative_report.get(
                "whole_closed_source_derivative_strictly_positive") is True
            and derivative_report.get(
                "closed_proof_children_derivative_positive_by_restriction") is True,
            "POSITIVE_GLOBAL_DERIVATIVE_NOT_ESTABLISHED")
    lower = Q(derivative_report["whole_closed_source_strict_derivative_lower_bound"])
    require(lower > 0, "SOURCE_DERIVATIVE_LOWER_NOT_POSITIVE")
    # This sign proof does NOT consume the atlas's irrational-cut physical sign
    # to calculate its transported enclosure; it compares only afterward.
    source_report = source_sign.prove(supplied_atlas=view)
    require(source_report["status"] == source_sign.SUCCESS
            and source_report["independently_certified_irrational_cut_sign"] ==
            "POSITIVE", "INDEPENDENT_ALGEBRAIC_CUT_SIGN_NOT_ESTABLISHED")
    field = bridge._field(source_report["exact_v45_field"])
    irrational_index, irrational, method = bridge._exact_alpha_boundary(
        view, field)
    require(method == "EXACT_POLYNOMIAL_GCD_PLUS_STURM_COMMON_ROOT",
            "ALGEBRAIC_CUT_IDENTITY_NOT_EXACT")
    coordinates = _coordinates(view, field, span,
                               irrational["boundary_id"])
    coordinates[irrational_index] = (
        coordinates[irrational_index][0],
        dict(source_report["source_proof"]["certificate"],
             method="EXACT_STURM_RATIONAL_MIDPOINT_OUTWARD_TRIG_LIPSCHITZ"))
    witnesses = []
    for boundary, (_, witness) in zip(view["proof_boundaries"], coordinates):
        require(witness is not None, "MISSING_PHYSICAL_BOUNDARY_SIGN")
        sign = witness["strict_nonzero_sign"]
        require(sign in (-1, 1), "UNPROVED_BOUNDARY_SIGN")
        witnesses.append(dict(
            witness, boundary_id=boundary["boundary_id"],
            strict_sign_name="POSITIVE" if sign == 1 else "NEGATIVE"))
    signs = [w["strict_nonzero_sign"] for w in witnesses]
    # Compare to historical atlas only AFTER recomputing all signs.
    require(["POSITIVE" if s == 1 else "NEGATIVE" for s in signs] ==
            [b["physical_value_sign"] for b in view["proof_boundaries"]],
            "INDEPENDENT_SOURCE_SIGNS_DISAGREE_WITH_PRESERVED_ATLAS")
    require(signs[0] == -1 and signs[-1] == 1
            and all(a <= b for a, b in zip(signs, signs[1:])),
            "MONOTONE_SOURCE_SIGN_ORDER_CONTRADICTED")
    children = []
    root_counts = []
    for i in range(4):
        left, right = coordinates[i][0], coordinates[i+1][0]
        width = right - left
        require(width.sign() == 1,
                "EXACT_MIXED_PROOF_CHILD_WIDTH_NOT_STRICTLY_POSITIVE")
        child_lower = field.element(lower) * width
        require(child_lower.sign() == 1,
                "CLOSED_CHILD_DERIVATIVE_LOWER_NOT_STRICTLY_POSITIVE")
        count = 1 if signs[i] == -1 and signs[i+1] == 1 else 0
        root_counts.append(count)
        children.append({
            "index": i,
            "source_parameter_id": view["source_parameter_id"],
            "left_boundary_id": view["proof_boundaries"][i]["boundary_id"],
            "right_boundary_id": view["proof_boundaries"][i+1]["boundary_id"],
            "normalized_parameter_interval": ["0", "1"],
            "source_affine_offset_qalpha": left.record(),
            "source_affine_width_qalpha": width.record(),
            "source_affine_right_qalpha": right.record(),
            "phase_offset_qalpha": (
                field.element(span.offset) + left * span.rate).record(),
            "phase_rate_qalpha": (width * span.rate).record(),
            "restricted_cos_sin_polynomials_qalpha":
                _restrict_polynomials(span, field, left, width),
            "strict_child_derivative_lower_qalpha":
                child_lower.record(),
            "positive_width_and_derivative_proved": True,
            "simple_physical_open_root_count": count,
            "irrational_phase_trig_endpoint_evaluated": False,
        })
    require(root_counts == [0, 1, 0, 0]
            and root_counts == [c["physical_open_root_count"]
                                for c in view["source_proof_cells"]]
            and sum(root_counts) == view[
                "complete_original_source_physical_root_count"] == 1
            and root["smooth_multiplicity"] == 1,
            "MIXED_CUT_MONOTONE_ROOT_COUNTS_NOT_CONSERVED")
    pins()
    return {
        "schema": SCHEMA,
        "status": SUCCESS,
        "evidence_class": "DETERMINISTIC_MODEL",
        "frozen_case_id": bridge.previous.CASE_ID,
        "source_sha256": source_sign.bridge.atlas.SOURCE_SHA256,
        "source_parameter_id": view["source_parameter_id"],
        "original_source_interval": ["0", "1"],
        "original_source_phase_turn_law": [
            str(span.offset), str(span.rate)],
        "shared_exact_algebraic_field": field.record(),
        "one_irrational_cut_identity_method": method,
        "global_strict_source_derivative_lower": str(lower),
        "independently_recomputed_boundary_signs": witnesses,
        "closed_mixed_cut_qalpha_children": children,
        "complete_open_simple_physical_root_counts": root_counts,
        "root_counts_derived_from_new_signs_and_global_monotonicity": True,
        "atlas_cut_coordinates_used_as_replayed_premises": True,
        "atlas_signs_and_cell_counts_checked_only_after_new_derivation": True,
        "proof_cut_physical_events": 0,
        "independent_irrational_cut_sign_source_proof":
            source_report["source_proof"],
        "general_multifield_algebraic_compositum_constructed": False,
        "general_irrational_trig_endpoint_zero_decider_constructed": False,
        "historical_v47_v49_analytic_child_route_certified": False,
        "historical_v54_disposition": "BLOCKED",
        "historical_v54_admitted": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_geometry_or_step_qualified": False,
        "production_authorized": False,
    }


def nontruth(reason, status="BLOCKED"):
    return {
        "schema": SCHEMA, "status": status, "reason": str(reason),
        "is_truth_value": False, "historical_v54_admitted": False,
        "pb00701_certified": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }


def attempt(*, supplied_atlas=None):
    try:
        return prove(supplied_atlas=supplied_atlas)
    except (ResourceRefusal, source_sign.ResourceRefusal,
            bridge.ResourceRefusal, derivative.ResourceRefusal,
            bridge.predecessor.ResourceRefusal,
            bridge.previous.ResourceRefusal, MemoryError,
            RecursionError, OverflowError) as exc:
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (Refusal, source_sign.Refusal, bridge.Refusal,
            derivative.Refusal, bridge.atlas.Refusal,
            bridge.previous.ResearchRefusal,
            cut_order.ResearchRefusal, ValueError, TypeError,
            KeyError, IndexError, AssertionError, AttributeError,
            ZeroDivisionError) as exc:
        return nontruth(str(exc))


def validate_report(submitted, *, supplied_atlas=None):
    try:
        bridge.predecessor._bound_untrusted_report_structure(submitted)
        claimed = bridge.previous.canonical(submitted)
        if len(claimed) > MAX_REPORT_BYTES:
            raise ResourceRefusal("SUBMITTED_MIXED_CUT_CHILD_REPORT_SIZE_LIMIT")
        checked = attempt(supplied_atlas=supplied_atlas)
        require(checked.get("status") == SUCCESS,
                "EXACT_FROZEN_MIXED_CUT_CHILD_PROOF_NOT_ESTABLISHED")
        require(claimed == bridge.previous.canonical(checked),
                "FORGED_FROZEN_MIXED_CUT_CHILD_CERTIFICATE")
        return checked
    except (ResourceRefusal, bridge.predecessor.ResourceRefusal,
            MemoryError, RecursionError, OverflowError) as exc:
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (Refusal, bridge.previous.ResearchRefusal,
            ValueError, TypeError, KeyError) as exc:
        return nontruth(str(exc))
