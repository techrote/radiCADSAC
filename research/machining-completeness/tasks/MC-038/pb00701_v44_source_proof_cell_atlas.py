#!/usr/bin/env python3
"""Frozen V44: original-source proof-cell sign atlas (research shadow only).

Consumes the pinned complete physical-root / proof-cut theorem from PR #310.
No analytic algebraic-child chart, V47 derivative claim or historical admission.
"""
from __future__ import annotations

import copy
import json
from fractions import Fraction as Q

import pb00701_v44_algebraic_cut_root_partition as previous

SCHEMA = "radicadsac-pb00701-v44-source-proof-cell-atlas/1.0"
SOURCE_SHA256 = "d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2"
PREVIOUS_MODEL_BLOB = "5d38a42fd8e23dc7930788e2b0c080caf567e851"
MAX_REPORT_BYTES = 131072
SUCCESS = "EXACT_FROZEN_V44_SOURCE_PROOF_CELL_ATLAS_RESEARCH"

class Refusal(ValueError):
    pass

def require(ok, why):
    if not ok:
        raise Refusal(why)

def name(sign):
    require(type(sign) is int and sign in (-1, 1),
            "PROOF_CELL_SIGN_MUST_BE_STRICT_NONZERO_INTEGER")
    return "POSITIVE" if sign > 0 else "NEGATIVE"

def pins():
    require(previous.git_blob(
        previous.TASK / "pb00701_v44_algebraic_cut_root_partition.py"
    ) == PREVIOUS_MODEL_BLOB, "PINNED_V44_ROOT_PARTITION_MODEL_DRIFT")
    previous.pins()

def _checked_source_snapshot(source):
    """Check the report interface independently of its proposed atlas."""
    require(type(source) is dict and source.get("schema") == previous.SCHEMA
            and source.get("status") ==
            "EXACT_FROZEN_V44_PROOF_CUT_ROOT_SET_PARTITION_RESEARCH",
            "MISSING_COMPLETE_FROZEN_V44_SOURCE_ROOT_PARTITION")
    original = previous.frozen_row()["spec"]
    expected_sha = previous.source_sha256(original)
    require(expected_sha == SOURCE_SHA256, "FROZEN_V44_SOURCE_DIGEST_DRIFT")
    require(source.get("source_sha256") == expected_sha
            and source.get("frozen_case_id") == previous.CASE_ID
            and source.get("source_parameter_id") ==
            original["source_parameter_id"]
            and source.get("source_interval") ==
            [original["parameter_lo"], original["parameter_hi"]]
            and source.get("phase_turn_law") == {
                "offset": original["phase_turn_offset"],
                "rate": original["phase_turn_rate"],
            }, "SOURCE_PARAMETER_OR_PHASE_NOT_BOUND")
    require(source.get("historical_v54_disposition") == "BLOCKED"
            and source.get("historical_v44_blocker") ==
            "ALGEBRAIC_ORIENTATION_COORDINATE_CERTIFIED_BUT_EXACT_CONSUMPTION_AUTHORITY_MISSING"
            and source.get("v47_still_certifies_this_frozen_source") is False,
            "FROZEN_HISTORICAL_BOUNDARY_CHANGED")
    require(source.get("complete_physical_root_count") == 1
            and source.get("root_count_conserved_across_proof_cells") is True,
            "COMPLETE_PHYSICAL_ROOT_COUNT_NOT_PROVED")
    r = source["physical_root"]
    lo, hi = (Q(v) for v in r["strict_isolation"])
    require(Q(0) < lo < hi < Q(1) and
            r["smooth_multiplicity"] == 1,
            "SINGLE_SIMPLE_ROOT_SOURCE_ISOLATION_NOT_PROVED")
    left, right = r["left_sign"], r["right_sign"]
    require(type(left) is int and type(right) is int
            and left == -right and left in (-1, 1)
            and r["derivative_sign"] == right
            and source["physical_endpoint_signs"] == [left, right],
            "ORIGINAL_SOURCE_ENDPOINT_OR_CROSSING_SIGN_MISMATCH")

    cuts = source["proof_cut_relations"]
    counts = source["proof_cell_open_root_counts"]
    require(type(cuts) is list and len(cuts) == 3
            and source.get("ordered_proof_cut_count") == 3
            and type(counts) is list and len(counts) == 4,
            "FROZEN_V44_PROOF_CUT_OR_CELL_CARDINALITY_CHANGED")
    require(source.get("all_proof_cuts_are_event_neutral") is True
            and source.get("algebraic_cut_is_physical_event") is False
            and source.get("algebraic_cut_physical_multiplicity") == 0
            and source.get("algebraic_cut_identity_method") ==
            "EXACT_POLYNOMIAL_GCD_PLUS_STURM_COMMON_ROOT",
            "ALGEBRAIC_PROOF_CUT_EVENT_OR_IDENTITY_NOT_CERTIFIED")
    evidence = source.get("source_bound_cut_order_evidence", {})
    require(evidence.get("source_sha256") == expected_sha
            and evidence.get("ordered_cut_count") == 3
            and evidence.get("orientation_roots_are_proof_geometry_only") is True,
            "PROOF_CUT_SOURCE_OR_ORDER_EVIDENCE_NOT_BOUND")

    before = 0
    seen_after = False
    algebraic_count = 0
    ids = set()
    for c in cuts:
        idx = c["proof_cut_index"]
        require(type(idx) is int and idx not in ids,
                "DUPLICATE_OR_INVALID_SOURCE_PROOF_CUT_INDEX")
        ids.add(idx)
        require(c.get("proof_cut_is_physical_event") is False,
                "PROOF_CUT_FABRICATED_AS_PHYSICAL_EVENT")
        relation = c["relation_to_physical_root"]
        require(relation in ("CUT_BEFORE_PHYSICAL_ROOT",
                             "PHYSICAL_ROOT_BEFORE_CUT"),
                "PROOF_CUT_ROOT_RELATION_UNCERTIFIED")
        if relation == "CUT_BEFORE_PHYSICAL_ROOT":
            require(not seen_after, "PROOF_CUTS_NOT_ORDERED_AROUND_ROOT")
            before += 1
            expected_sign = left
        else:
            seen_after = True
            expected_sign = right
        require(type(c.get("physical_value_sign")) is int
                and c["physical_value_sign"] == expected_sign,
                "PROOF_CUT_NONZERO_SIGN_CONFLICTS_WITH_ROOT_ORDER")
        coord = c["coordinate"]
        cut_lo, cut_hi = previous._coord_bounds(coord)
        require(Q(0) < cut_lo <= cut_hi < Q(1),
                "PROOF_CUT_OUTSIDE_ORIGINAL_SOURCE_INTERVAL")
        if coord["kind"] == "ISOLATED_REAL_ROOT":
            algebraic_count += 1
            require(name(expected_sign) ==
                    source["algebraic_cut_endpoint_relation"],
                    "V46_ALGEBRAIC_ENDPOINT_SIGN_MISMATCH")
    require(algebraic_count == 1, "FROZEN_V44_ALGEBRAIC_CUT_COUNT_CHANGED")
    require(type(source.get("root_occupying_proof_cell_index")) is int
            and source["root_occupying_proof_cell_index"] == before,
            "PHYSICAL_ROOT_CELL_INDEX_MISMATCH")
    require(all(type(n) is int and n in (0, 1) for n in counts)
            and counts == [1 if i == before else 0 for i in range(4)],
            "PROOF_CELL_ROOT_COUNTS_NOT_EXACTLY_CONSERVED")
    for flag in (
        "algebraic_child_reparameterization_claimed",
        "closed_child_derivative_theorem_claimed",
        "historical_v54_admitted",
        "historical_v54_dispositions_changed",
        "pb00701_certified",
        "mc_b_established",
        "mc1_established",
        "native_brep_or_step_qualified",
        "production_authorized",
    ):
        require(source.get(flag) is False,
                "PREVIOUS_PROOF_UNJUSTIFIED_CAPABILITY_CLAIM:" + flag)
    return original, r, cuts, counts, before

def compose(source):
    """Produce a source-coordinate sign atlas, not an analytic child solver."""
    # The input is a report, not an unforgeable capability. A plausible cut
    # descriptor (or a rearranged one) can pass local cardinality/sign checks
    # while naming a DIFFERENT exact source coordinate. Require the reviewed
    # producer to reproduce the ENTIRE source report before exporting any
    # boundary as a consumer-visible source-coordinate descriptor.
    original, root, cuts, counts, root_cell = _checked_source_snapshot(source)
    replayed = previous.validate_report(source)
    require(replayed.get("status") ==
            "EXACT_FROZEN_V44_PROOF_CUT_ROOT_SET_PARTITION_RESEARCH" and
            previous.canonical(replayed) == previous.canonical(source),
            "SOURCE_PROOF_CUT_REPORT_NOT_EXACTLY_REPLAY_VERIFIED")

    sid = original["source_parameter_id"]
    signs = source["physical_endpoint_signs"]
    boundaries = [{
        "boundary_id": "b0",
        "kind": "ORIGINAL_SOURCE_LEFT_ENDPOINT",
        "exact_source_coordinate": original["parameter_lo"],
        "physical_value_sign": name(signs[0]),
        "is_physical_zero": False,
    }]
    for j, cut in enumerate(cuts):
        boundaries.append({
            "boundary_id": "b" + str(j + 1),
            "kind": "EXACT_SOURCE_PROOF_CUT",
            "coordinate_descriptor": copy.deepcopy(cut["coordinate"]),
            "physical_value_sign": name(cut["physical_value_sign"]),
            "is_physical_zero": False,
            "is_proof_geometry_only": True,
            "source_cut_index": cut["proof_cut_index"],
        })
    boundaries.append({
        "boundary_id": "b4",
        "kind": "ORIGINAL_SOURCE_RIGHT_ENDPOINT",
        "exact_source_coordinate": original["parameter_hi"],
        "physical_value_sign": name(signs[1]),
        "is_physical_zero": False,
    })
    cells = []
    for i, count in enumerate(counts):
        a, b = boundaries[i], boundaries[i + 1]
        sl, sr = a["physical_value_sign"], b["physical_value_sign"]
        if count == 0:
            require(sl == sr, "ZERO_FREE_CELL_END_SIGN_DISAGREEMENT")
            kind = "EXACT_SOURCE_ROOT_FREE_SIGN_CELL"
            sign = sl
            root_record = None
        else:
            require(i == root_cell and sl != sr
                    and sl == name(root["left_sign"])
                    and sr == name(root["right_sign"]),
                    "SIMPLE_ROOT_CELL_CROSSING_SIGN_DISAGREEMENT")
            kind = "EXACT_SOURCE_ONE_SIMPLE_ROOT_CELL"
            sign = None
            root_record = copy.deepcopy(root)
        cells.append({
            "index": i,
            "source_parameter_id": sid,
            "left_boundary_id": a["boundary_id"],
            "right_boundary_id": b["boundary_id"],
            "physical_open_root_count": count,
            "kind": kind,
            "root_free_constant_sign": sign,
            "left_nonzero_boundary_sign": sl,
            "right_nonzero_boundary_sign": sr,
            "one_simple_physical_root_witness": root_record,
            "analytic_algebraic_child_chart_claimed": False,
            "closed_child_derivative_theorem_claimed": False,
        })
    require(sum(c["physical_open_root_count"] for c in cells) == 1
            and sum(c["kind"] == "EXACT_SOURCE_ONE_SIMPLE_ROOT_CELL"
                    for c in cells) == 1,
            "PROOF_CELL_PHYSICAL_ZERO_CONSERVATION_FAILED")
    return {
        "schema": SCHEMA,
        "status": SUCCESS,
        "evidence_class": "DETERMINISTIC_MODEL",
        "parent_frozen_case_id": previous.CASE_ID,
        "parent_source_sha256": source["source_sha256"],
        "parent_source_root_partition_schema": previous.SCHEMA,
        "source_parameter_id": sid,
        "original_source_interval": copy.deepcopy(source["source_interval"]),
        "original_affine_phase": copy.deepcopy(source["phase_turn_law"]),
        "proof_boundaries": boundaries,
        "source_proof_cells": cells,
        "complete_original_source_physical_root_count": 1,
        "source_proof_cut_count": len(cuts),
        "source_proof_cell_count": len(cells),
        "one_physical_root_cell_index": root_cell,
        "proof_cuts_are_events": False,
        "source_coordinate_restrictions_only": True,
        "actual_algebraic_child_analytic_chart_constructed": False,
        "closed_child_derivative_theorem_proved": False,
        "v41_v47_historical_child_route_certified": False,
        "historical_v54_disposition": "BLOCKED",
        "historical_v54_admitted": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_material_or_step_qualified": False,
        "production_authorized": False,
    }

def prove(**budgets):
    pins()
    source = previous.prove(**budgets)
    out = compose(source)
    pins()
    return out

def nontruth(reason, status="BLOCKED"):
    return {
        "schema": SCHEMA, "status": status, "reason": str(reason),
        "is_truth_value": False, "historical_v54_admitted": False,
        "pb00701_certified": False, "mc_b_established": False,
        "production_authorized": False,
    }

def attempt(**budgets):
    try:
        return prove(**budgets)
    except (previous.ResourceRefusal, MemoryError,
            OverflowError, RecursionError) as exc:
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (Refusal, previous.ResearchRefusal, ValueError,
            KeyError, TypeError, IndexError, ZeroDivisionError,
            AssertionError) as exc:
        return nontruth(str(exc))
        
def validate_report(submitted, **budgets):
    try:
        claimed = previous.canonical(submitted)
        if len(claimed) > MAX_REPORT_BYTES:
            return nontruth("SUBMITTED_ATLAS_RESOURCE_LIMIT",
                            "RESOURCE_REFUSAL")
        checked = attempt(**budgets)
        require(checked.get("status") == SUCCESS,
                "EXACT_SOURCE_PROOF_CELL_ATLAS_NOT_ESTABLISHED")
        require(previous.canonical(checked) == claimed,
                "FORGED_FROZEN_V44_SOURCE_PROOF_CELL_ATLAS")
        return checked
    except (Refusal, previous.ResearchRefusal, ValueError,
            TypeError, OverflowError) as exc:
        return nontruth(str(exc))
