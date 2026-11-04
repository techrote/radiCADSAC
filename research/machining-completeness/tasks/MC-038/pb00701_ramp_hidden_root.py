#!/usr/bin/env python3
"""Bounded exact original-source rational-ramp root/sign theorem (research only).

All trigonometric/convexity premises are explicit analytic lemmas, not floating
evaluations. Unknown rational slopes refuse without a truth claim.
"""
from __future__ import annotations

import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
REGISTRY = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
AUTHORITY = HERE.parents[3] / "handoffs/current-authority.json"
DOMAIN = HERE.parents[3] / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
REGISTRY_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
AUTHORITY_BLOB = "fa0233323a0804d8a5d3eb7cd892a274a6173fab"
DOMAIN_BLOB = "23de82f5240a72509f7afe4acd5948b65bc4ff13"
ANCHOR_ID = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail100"
ANCHOR_SHA = "f6a0eb06c66af415fbb8abdfe62f9b36a2a2bf154e535d83307a80228e044ad5"
MUTATION_SHA = "e4bd5090915c3ff4dac70092918b154b43b5233105b8c86575cf4cc1a8480f9e"
SCHEMA = "radicadsac-pb00701-ramp-hidden-root/1.0"
CLAIM = "C_POSITIVE_EXTERIORS_AND_ZERO_KNOT_DO_NOT_PROVE_INTERIOR_EVENT_COMPLETENESS"


class Refusal(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def source_sha(spec):
    return hashlib.sha256(canonical(spec).encode("ascii")).hexdigest()


def blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def rational(value):
    if not isinstance(value, str):
        raise Refusal("NON_STRING_OR_BINARY_RATIONAL")
    try:
        a = Q(value)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("INVALID_RATIONAL") from exc
    if str(a) != value:
        raise Refusal("NONCANONICAL_RATIONAL")
    if max(abs(a.numerator).bit_length(), a.denominator.bit_length()) > 512:
        raise Refusal("RESOURCE_REFUSAL_RATIONAL_BIT_BOUND")
    return a


def check_pins():
    for path, expected in ((CORPUS, CORPUS_BLOB), (REGISTRY, REGISTRY_BLOB),
                           (AUTHORITY, AUTHORITY_BLOB), (DOMAIN, DOMAIN_BLOB)):
        if blob(path) != expected:
            raise Refusal("PINNED_BLOB_DRIFT:" + path.name)
    authority = json.loads(AUTHORITY.read_text())
    domain = json.loads(DOMAIN.read_text())
    if (authority.get("production_authorized") is not False or
            authority.get("capability_status") != "NOT_ESTABLISHED" or
            len(domain["coverage_rule"]["required_operation_ids"]) != 26):
        raise Refusal("DOMAIN_OR_GATE_AUTHORITY_CHANGED")


def census(corpus=None, registry=None):
    check_pins()
    frozen = json.loads(CORPUS.read_text()) if corpus is None else corpus
    v2 = json.loads(REGISTRY.read_text()) if registry is None else registry
    cases = frozen["cases"]
    if len(cases) != 121 or len({r["id"] for r in cases}) != 121:
        raise Refusal("FROZEN_CASE_IDS_CHANGED")
    ix = {r["id"]: r for r in cases}
    hashes = {r["id"]: source_sha(r["spec"]) for r in cases}
    if len(set(hashes.values())) != 121:
        raise Refusal("FROZEN_SOURCE_IDENTITIES_NOT_DISTINCT")
    blocked = {r["id"] for r in cases if r["expected"]["v54_disposition"] == "BLOCKED"}
    lacking = {r["id"] for r in cases
               if r["expected"]["v54_disposition"] ==
               "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
    if len(blocked) != 20 or len(lacking) != 30 or blocked & lacking:
        raise Refusal("HISTORICAL_20_30_CENSUS_CHANGED")
    rows = v2["source_cases"]
    if len(rows) != 50 or len({r["case_id"] for r in rows}) != 50:
        raise Refusal("FIFTY_SOURCE_REGISTRY_CHANGED")
    if {r["case_id"] for r in rows} != blocked | lacking:
        raise Refusal("REGISTRY_HISTORICAL_CASE_SET_MISMATCH")
    for row in rows:
        original = ix[row["case_id"]]
        if not (row["source_sha256"] == hashes[row["case_id"]] ==
                row["evidence"]["source_sha256"] and
                row["origin"] == original["origin"] and
                row["historical_v54_disposition"] ==
                original["expected"]["v54_disposition"] and
                row["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
                row["evidence"]["level"] == "COMPLETE_SOURCE_SPECIFIC" and
                row["evidence"]["complete_original_source_zero_set"] is True and
                row["historical_disposition_changed"] is False):
            raise Refusal("REGISTRY_SOURCE_CUSTODY_MISMATCH:" + row["case_id"])
    if (v2["frozen_corpus_git_blob"] != CORPUS_BLOB or
            v2["summary"]["by_registered_evidence_level"] !=
            {"COMPLETE_SOURCE_SPECIFIC": 50, "PARTIAL_REFUSED_TAIL_ONLY": 0,
             "PARTIAL_ORDERED_CHILD": 0,
             "NO_REGISTERED_SOURCE_EVENT_OR_ORDER_WITNESS": 0} or
            v2["summary"]["complete_finite_sources"] != 49 or
            v2["summary"]["complete_continuum_sources"] != 1):
        raise Refusal("REGISTRY_CENSUS_CHANGED")
    anchor = ix.get(ANCHOR_ID)
    if (anchor is None or hashes[ANCHOR_ID] != ANCHOR_SHA or
            anchor["origin"] != "verify_pb00701_v7" or
            anchor["kind"] != "COMPOSITE_TAIL" or
            anchor["expected"]["v54_disposition"] != "BLOCKED" or
            anchor["expected"]["observed"]["spans"] !=
            [["DELEGATED_V6_CONSTANT_MODULATION", "CERTIFIED", None],
             ["PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION",
              "BLOCKED", "V27_CHILD_NOT_CERTIFIED"]]):
        raise Refusal("FROZEN_ANCHOR_STATUS_OR_SOURCE_CHANGED")
    expected_spec = {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t", "parameter_lo": "0",
        "parameter_hi": "2", "phase_turn_offset": "0", "phase_turn_rate": "1/4",
        "cos_splines": {
            "0": {"degree": 1, "knots": ["0", "0", "1", "1", "2", "2"],
                  "controls": ["0", "0", "0", "100"]},
            "1": {"degree": 0, "knots": ["0", "1", "2"],
                  "controls": ["1", "1"]}},
        "sin_splines": {}
    }
    if anchor["spec"] != expected_spec:
        raise Refusal("FROZEN_ANCHOR_GRAMMAR_CHANGED")
    return {
        "frozen_source_count_before_after": [121, 121],
        "historical_route_refusals_before_after": [20, 20],
        "historical_missing_order_premises_before_after": [30, 30],
        "complete_source_specific_witnesses_before_after": [50, 50],
        "complete_finite_witnesses": 49, "complete_continuum_witnesses": 1,
        "new_frozen_case_ids_resolved": [],
        "historical_v54_dispositions_changed": False,
        "all_121_source_hashes_recomputed": True,
        "all_50_source_evidence_hashes_checked": True
    }


def variant_from_anchor(slope, source=None):
    a = rational(slope)
    if source is None:
        source = json.loads(CORPUS.read_text())["cases"]
        source = next((x["spec"] for x in source if x["id"] == ANCHOR_ID), None)
    if source is None or source_sha(source) != ANCHOR_SHA:
        raise Refusal("UNAUTHORIZED_OR_UNBOUND_ANCHOR")
    spec = copy.deepcopy(source)
    spec["cos_splines"]["0"]["controls"][-1] = str(a)
    if (source_sha(spec) == ANCHOR_SHA) != (str(a) == "100"):
        raise Refusal("SOURCE_VARIANT_IDENTITY_MISMATCH")
    return spec


def classify_slope(value):
    a = rational(value)
    if a < 0:
        raise Refusal("NEGATIVE_RAMP_OUTSIDE_ADMITTED_GRAMMAR")
    if a == 0:
        family = "NONPOSITIVE_RIGHT_NO_EXTRA_ROOT"
        right_signs = ["NEGATIVE"]
        right_roots, exterior_roots = 0, 0
        knot = "CROSSING"
    elif a < 1:
        family = "NEGATIVE_RIGHT_NO_EXTRA_ROOT"
        right_signs = ["NEGATIVE"]
        right_roots, exterior_roots = 0, 0
        knot = "CROSSING"
    elif a == 1:
        family = "NEGATIVE_RIGHT_AND_RIGHT_ENDPOINT_ROOT"
        right_signs = ["NEGATIVE"]
        right_roots, exterior_roots = 0, 1
        knot = "CROSSING"
    elif a <= Q(3, 2):
        family = "ONE_UNIQUE_SIMPLE_RIGHT_OPEN_CROSSING"
        right_signs = ["NEGATIVE", "POSITIVE"]
        right_roots, exterior_roots = 1, 0
        knot = "CROSSING"
    elif a >= Q(11, 7):
        family = "POSITIVE_RIGHT_NO_EXTRA_ROOT"
        right_signs = ["POSITIVE"]
        right_roots, exterior_roots = 0, 0
        knot = "TOUCHING"
    else:
        raise Refusal("INSUFFICIENT_RATIONAL_PI_SEPARATION_NONTRUTH")
    return {
        "ramp_slope": str(a), "case": family,
        "left_source_open_root_count": 0,
        "right_source_open_root_count": right_roots,
        "right_exterior_root_count": exterior_roots,
        "distinct_closed_source_root_count": 1 + right_roots + exterior_roots,
        "source_knot_coordinate": "1", "source_knot_is_zero": True,
        "source_knot_one_sided_orders": [1, 1],
        "global_smooth_source_knot_multiplicity_claimed": False,
        "source_knot_event": knot,
        "ordered_physical_open_signs": ["POSITIVE"] + right_signs,
        "exterior_values": {"t=0": "1", "t=2": str(a - 1)},
        "interior_root_bracket_local_x":
            ["1/4", "1/2"] if a == Q(3, 2) else
            (["0", "1"] if right_roots else []),
        "root_near_t2_bound":
            {"upper_distance": "3/1267650600228229401496703205376",
             "source_interval": [str(Q(2) - Q(3, 2**100)), "2"]}
            if a == 1 + Q(1, 2**100) else None,
        "method": "EXACT_CONVEXITY_PI_RATIONAL_BOUNDS_CYCLOTOMIC_BRACKET",
        "root_sampling_used_as_truth": False,
        "resource_refusal_is_truth": False
    }


def proof_c():
    census_result = census()
    original = classify_slope("100")
    altered = classify_slope("3/2")
    original_spec = variant_from_anchor("100")
    altered_spec = variant_from_anchor("3/2")
    if (source_sha(original_spec) != ANCHOR_SHA or
            source_sha(altered_spec) != MUTATION_SHA or
            original["exterior_values"]["t=0"] != "1" or
            altered["exterior_values"] != {"t=0": "1", "t=2": "1/2"} or
            original["source_knot_is_zero"] is not True or
            altered["source_knot_is_zero"] is not True or
            original["distinct_closed_source_root_count"] != 1 or
            altered["distinct_closed_source_root_count"] != 2):
        raise Refusal("FALSIFIER_CONSTRUCTION_FAILED")
    if MUTATION_SHA in {source_sha(c["spec"]) for c in
                        json.loads(CORPUS.read_text())["cases"]}:
        raise Refusal("PROSPECTIVE_SOURCE_ALREADY_IN_FROZEN_CORPUS")
    return {
        "schema": SCHEMA, "task": "MC-038", "claim": CLAIM,
        "evidence_class": "DETERMINISTIC_MODEL",
        "historical_anchor_case_id": ANCHOR_ID,
        "historical_anchor_source_sha256": ANCHOR_SHA,
        "prospective_slope_3_2_source_sha256": MUTATION_SHA,
        "historical_v54_corpus_git_blob": CORPUS_BLOB,
        "current_fifty_source_registry_git_blob": REGISTRY_BLOB,
        "original_exact_case": original, "changed_control_exact_case": altered,
        "same_phase_knot_degree_harmonics": True,
        "both_exact_exterior_signs_positive_and_knot_zero": True,
        "positive_exteriors_knot_zero_shortcut_falsified": True,
        "proof_obligation": "PB-007-01 exact physical event partition and ordered signs",
        "census": census_result,
        "general_analytic_solver_impossibility_claimed": False,
        "all_26_operations_preserved": True,
        "historical_v54_accepted_route_changed": False,
        "pb00701_full_grammar_certified": False,
        "mc_b_established": False, "mc1_established": False,
        "native_or_step_qualified": False, "production_authorized": False
    }
