#!/usr/bin/env python3
"""Reexecute registered post-V54 proofs against all 50 historical gaps.

This is a finite evidence reconciliation, not a general event solver or a
historical route reclassification. Only pinned ORIGINAL sources reach legacy
producers. Caller reports are bounded data compared with a fresh exact replay.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
SCHEMA = "radicadsac-mc038-post-v54-evidence-reconciliation/1.0"
MACHINE = HERE / "pb00701-post-v54-evidence-reconciliation.json"
BASE_MAIN = "f69cf47f011fd22bd48687d963d015328fa69e1a"
ARCHAEOLOGY_BASE_MAIN = "45d4a10343ec8161e92e8bbed634f0edb5f16d24"
ORDER_GAP = "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
V6 = "DELEGATED_V6_CONSTANT_MODULATION"
COMPLETE = "COMPLETE_SOURCE_SPECIFIC"
TAIL = "PARTIAL_REFUSED_TAIL_ONLY"
CHILD = "PARTIAL_ORDERED_CHILD"
UNREGISTERED = "NO_REGISTERED_SOURCE_EVENT_OR_ORDER_WITNESS"
LEVELS = (COMPLETE, TAIL, CHILD, UNREGISTERED)
MAX_BYTES = 1024 * 1024
MAX_NODES = 65536
MAX_DEPTH = 32
MAX_STRING = 8192

PINS = {
    "pb00701-finite-owner-corpus-v54.json": "5841c331579489b25caef38cd412bdbf286f9134",
    "pb00701-finite-owner-inventory-v54.json": "8649c20ab77e199f9c3fa351b8b6742218f27abb",
    "pb00701-finite-owner-coverage-v54.json": "600ba29786f50397f29fd435fc5e2c57076088f9",
    "verify_pb00701_post_v54_frontier.py": "12c6efeb667a954ffc5a7e27849ae815d466580a",
}
ROOT_PINS = {
    "research/machining-completeness/tasks/MC-002/domain-contract-v1.json":
        "23de82f5240a72509f7afe4acd5948b65bc4ff13",
    "research/machining-completeness/programme-v1.json":
        "dee7045a1790b2870744df8ae7693429bd1d81a6",
    "handoffs/current-authority.json": "fa0233323a0804d8a5d3eb7cd892a274a6173fab",
}
PRODUCERS = {
    "five": ("pb00701_five_source_evidence_replay.py",
             "a8aedb83772984831d5aa5c3b9b8d1cead04c345"),
    "continuum": ("pb00701_continuum_zero_source.py",
                  "6fff0737c2f7bf8178dd7437c0981f7f3cd50cd0"),
    "knot": ("pb00701_two_span_source_knot_root_set.py",
             "516591fdbe25f4e0b1da00bc8aa70250de74b42c"),
    "trig_fixed": ("pb00701_pinned_trig_child_views.py",
                   "c4a4d865226d01858d93685aa770987b14460e0b"),
    "stationary": ("pb00701_stationary_knot_composition.py",
                   "d0fbe7e189066fd9398958f1b1814b8147a6a64e"),
    "v44": ("pb00701_v44_algebraic_cut_root_partition.py",
            "5d38a42fd8e23dc7930788e2b0c080caf567e851"),
    "v6_ordered": ("verify_pb00701_v6_source_order.py",
                   "6b1e24513146f1cdf1edc2922bc1222dde1efce0"),
    "refusal_cone": ("verify_pb00701_v43_refusal_cone.py",
                     "2a8079ee2cf012bc2a12794c4c5ff19ebd760007"),
    "v10_tail0_crossings": ("verify_pb00701_v43_v10_tail0_crossings.py",
                           "5bf6f85f1432b513ba89d17f5e4da17d1bce212d"),
    "v10_tail_crossing": ("verify_pb00701_v43_v10_tail_crossing.py",
                         "ada50468fe840625bd652c5a0042e0e3d75607d6"),
    "v11_tail_contrast": ("verify_pb00701_v43_v11_tail_contrast.py",
                          "a978284ce2672ce05d0ae45a9e2a9043c227a4f2"),
    "v12_tail_contrast": ("verify_pb00701_v43_v12_tail_contrast.py",
                          "2b2e85f662f4cb2a97b82e264e007c38cada69fd"),
    "v13_even_factor": ("verify_pb00701_v43_v13_even_factor.py",
                        "998130ba26f553237ac261017f3edc13f5f57700"),
    "v16_chebyshev_crossing": ("verify_pb00701_v43_v16_chebyshev_crossing.py",
                              "74bbdb48125f4168308fb6ffcbac4e5a08049c5d"),
    "v17_positive_turn": ("verify_pb00701_v43_v17_positive_turn.py",
                          "e245b13045a96f549747baae1b25556da6cc9808"),
    "v23_bernstein": ("pb00701_v23_bernstein_source.py",
                      "9b83c4485f8251b0649af6402acc9d777e281a96"),
}
SAVED_REPORTS = {
    "five": ("pb00701-five-source-evidence-replay.json",
             "4c619ee7011fa2d7a65f3391ff95cd8e7eecf3b0"),
    "continuum": ("pb00701-continuum-zero-source-witness.json",
                  "6ce9bc63714695b67fb019bee3ad95430c1ea922"),
    "v23_bernstein": ("pb00701-v23-bernstein-source-witness.json",
                      "f5de44d4e7e17d076bc575609d62aeb934d8f4b9"),
}
FIVE_IDS = {
    "harvested:verify_pb00701_v9:1a5fd052a155",
    "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0",
    "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail100",
    "composite:DELEGATED_V6_CONSTANT_MODULATION:tail100",
    "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100",
}
CONTINUUM_ID = "harvested:verify_pb00701_v53:cb01c327d5f1"
KNOT_ID = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0"
V44_ID = "harvested:verify_pb00701_v44:ffaea08e30c9"
V41_ID = "harvested:verify_pb00701_v13:c426f65b5c10"
POSITIVE_ID = "harvested:verify_pb00701_v9:4e7b85fa122a"
V23_ID = "harvested:verify_pb00701_v52:2250401ce435"
TAIL_IDS = {
    "v10_tail0_crossings": {"composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0"},
    "v10_tail_crossing": {"composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail100"},
    "v11_tail_contrast": {"composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail0",
                          "composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail100"},
    "v12_tail_contrast": {"composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0",
                          "composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail100"},
    "v13_even_factor": {"composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail0"},
    "v16_chebyshev_crossing": {"composite:PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER:tail100"},
    "v17_positive_turn": {"composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail0"},
}


class Refusal(ValueError):
    """Invalid evidence or resource exhaustion is nontruth, never coverage."""


def need(ok, reason):
    if not ok:
        raise Refusal(reason)


def bounded_bytes(value):
    """Preflight without recursive serialization or numeric coercion.

    In particular, booleans and integers remain distinct under canonical JSON;
    floats, arbitrary classes, cycles and huge/deep inputs never reach producers.
    """
    stack = [(value, 0, False)]
    active = set()
    visited = 0
    byte_budget = 0
    while stack:
        obj, depth, leaving = stack.pop()
        if leaving:
            active.remove(id(obj))
            continue
        visited += 1
        need(visited <= MAX_NODES and depth <= MAX_DEPTH,
             "RESOURCE_REFUSAL: JSON node/depth budget")
        if type(obj) in (dict, list):
            need(id(obj) not in active and len(obj) <= 1024,
                 "RESOURCE_REFUSAL: JSON cycle/container budget")
            active.add(id(obj))
            byte_budget += 2 + 2 * len(obj)
            stack.append((obj, depth, True))
            if type(obj) is dict:
                for key, child in obj.items():
                    need(type(key) is str and len(key) <= MAX_STRING,
                         "RESOURCE_REFUSAL: JSON key budget")
                    byte_budget += len(json.dumps(key, ensure_ascii=True))
                    stack.append((child, depth + 1, False))
            else:
                stack.extend((child, depth + 1, False) for child in obj)
        elif type(obj) is str:
            need(len(obj) <= MAX_STRING, "RESOURCE_REFUSAL: JSON string budget")
            byte_budget += len(json.dumps(obj, ensure_ascii=True))
        elif type(obj) is int:
            need(obj.bit_length() <= 256, "RESOURCE_REFUSAL: JSON integer budget")
            byte_budget += len(str(obj))
        else:
            need(obj is None or type(obj) is bool,
                 "NONEXACT_JSON_SCALAR: floats and custom classes prohibited")
            byte_budget += 5
        need(byte_budget <= MAX_BYTES, "RESOURCE_REFUSAL: JSON aggregate byte budget")
    data = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")
    need(len(data) <= MAX_BYTES, "RESOURCE_REFUSAL: JSON byte budget")
    return data


def digest(value):
    return hashlib.sha256(bounded_bytes(value)).hexdigest()


def unique_pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def read_json(path):
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    need(len(data) <= MAX_BYTES, "RESOURCE_REFUSAL: JSON file byte budget")
    try:
        result = json.loads(data, object_pairs_hook=unique_pairs,
                            parse_constant=lambda _: (_ for _ in ()).throw(
                                Refusal("NONFINITE_JSON_SCALAR")))
    except (RecursionError, ValueError, UnicodeError) as exc:
        raise Refusal("INVALID_OR_RESOURCE_JSON") from exc
    bounded_bytes(result)
    return result


def git_blob(path):
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    need(len(data) <= MAX_BYTES, "RESOURCE_REFUSAL: pinned-file byte budget")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def pin(path, expected):
    need(Path(path).is_file() and git_blob(path) == expected,
         "PINNED_SOURCE_OR_PRODUCER_DRIFT: " + str(path))


def pinned_module(filename, expected):
    path = HERE / filename
    pin(path, expected)
    spec = importlib.util.spec_from_file_location("reconciliation_" + path.stem, path)
    need(spec is not None and spec.loader is not None, "PRODUCER_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(Path(module.__file__).resolve() == path.resolve(), "PRODUCER_PATH_CHANGED")
    pin(path, expected)
    return module


def producer(key):
    return pinned_module(*PRODUCERS[key])


def pinned_saved(key, recomputed):
    name, sha = SAVED_REPORTS[key]
    pin(HERE / name, sha)
    need(bounded_bytes(read_json(HERE / name)) == bounded_bytes(recomputed),
         "SAVED_PRODUCER_REPORT_DISAGREES_WITH_SOURCE_REPLAY: " + key)


def original_corpus():
    for name, sha in PINS.items():
        pin(HERE / name, sha)
    for name, sha in ROOT_PINS.items():
        pin(ROOT / name, sha)
    audit = pinned_module("verify_pb00701_post_v54_frontier.py",
                          PINS["verify_pb00701_post_v54_frontier.py"])
    raw, inventory, boundary = audit.inputs()
    census = audit.audit(raw, inventory, boundary)
    need(census["cases"] == 121 and census["v54_dispositions"]["BLOCKED"] == 20
         and census["v54_dispositions"][ORDER_GAP] == 30,
         "HISTORICAL_121_20_30_DENOMINATOR_CHANGED")
    auth = read_json(ROOT / "handoffs/current-authority.json")
    prog = read_json(ROOT / "research/machining-completeness/programme-v1.json")
    domain = read_json(ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json")
    need(auth["capability_status"] == prog["capability_status"] == "NOT_ESTABLISHED"
         and auth["production_authorized"] is False
         and prog["production_authorized"] is False,
         "PROGRAMME_AUTHORITY_PROMOTION")
    need({g["id"]: g["state"] for g in prog["gates"]}["MC-B"] == "NOT_ESTABLISHED",
         "MC_B_PROMOTION")
    need(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
         "MACHINING_DOMAIN_CHANGED")
    indexed = {r["id"]: r for r in raw["cases"]}
    need(len(indexed) == 121, "DUPLICATE_ORIGINAL_SOURCE_ID")
    return indexed


def source_metadata(row):
    spec = row["spec"]
    # These rationals come ONLY from the byte-pinned frozen corpus. No caller
    # report is fed to Fraction or any historical source parser.
    from fractions import Fraction
    edges = {spec["parameter_lo"], spec["parameter_hi"]}
    for channel in ("cos_splines", "sin_splines"):
        for spline in spec[channel].values():
            edges.update(spline["knots"])
    edges = sorted(edges, key=Fraction)
    return {
        "source_sha256": digest(spec),
        "original_row_sha256": digest(row),
        "source_parameter_id": spec["source_parameter_id"],
        "source_interval": [spec["parameter_lo"], spec["parameter_hi"]],
        "phase_turn_law": {"offset": spec["phase_turn_offset"],
                           "rate": spec["phase_turn_rate"]},
        "original_source_piece_edges": edges,
    }


def bind_view(view, row, *, hash_field="source_sha256"):
    meta = source_metadata(row)
    need(view[hash_field] == meta["source_sha256"], "PRODUCER_ORIGINAL_SOURCE_HASH_MISMATCH")
    for field in ("source_parameter_id", "source_interval", "phase_turn_law"):
        if field in view:
            need(bounded_bytes(view[field]) == bounded_bytes(meta[field]),
                 "PRODUCER_SOURCE_PARAMETER_INTERVAL_OR_PHASE_MISMATCH")
    return meta


def evidence_entry(key, case_id, row, result, level, interval, kind):
    """Private adapter output; no externally supplied proof receipt is accepted."""
    need(row["id"] == case_id and row["expected"]["v54_disposition"] in
         ("BLOCKED", ORDER_GAP), "EVIDENCE_OUTSIDE_FROZEN_UNRESOLVED_DENOMINATOR")
    meta = source_metadata(row)
    need(level in (COMPLETE, TAIL, CHILD), "INVALID_EVIDENCE_SCOPE")
    if level == COMPLETE:
        need(interval == meta["source_interval"], "PARTIAL_INTERVAL_CANNOT_BE_COMPLETE_SOURCE")
    else:
        edges = meta["original_source_piece_edges"]
        need(interval != meta["source_interval"] and any(
            interval == [a, b] for a, b in zip(edges, edges[1:])),
            "PARTIAL_EVIDENCE_MUST_BE_ONE_ACTUAL_ORIGINAL_PIECE")
    return {
        "producer": key,
        "producer_code": PRODUCERS[key][0],
        "producer_git_blob": PRODUCERS[key][1],
        "level": level,
        "scope": kind,
        "covered_original_source_interval": interval,
        "replayed_result_sha256": digest(result),
        "source_sha256": meta["source_sha256"],
        "complete_original_source_zero_set": level == COMPLETE,
    }


def replay_evidence(indexed):
    """One deterministic replay of every registered original-source proof.

    Registry membership is deliberately finite. Generic primitives or synthetic
    fixtures never earn a source receipt. Refusal/exception aborts the census.
    """
    receipts = {}
    def add(key, cid, result, level, interval, kind):
        need(cid not in receipts, "DUPLICATE_SOURCE_RECEIPT_OR_OVERLAPPING_UNION")
        receipts[cid] = evidence_entry(key, cid, indexed[cid], result, level, interval, kind)

    five = producer("five").expected_report()
    pinned_saved("five", five)
    views = five["source_attested_views"]
    need(len(views) == 5 and {v["case_id"] for v in views} == FIVE_IDS,
         "FIVE_SOURCE_UNION_IDENTITY_DRIFT")
    for view in views:
        cid = view["case_id"]
        meta = bind_view(view, indexed[cid])
        need(view["source_specific_mathematics_only"] is True and
             view["generic_route_repaired"] is False and
             type(view["closed_root_count"]) is int and
             len(view["events"]) == view["closed_root_count"],
             "FIVE_SOURCE_FINITE_EVENT_PROOF_MISSING")
        add("five", cid, view, COMPLETE, meta["source_interval"], "COMPLETE_FINITE_SOURCE_ZERO_SET")

    union = producer("continuum").expected_record()
    pinned_saved("continuum", union)
    selected = union["separate_source_zero_set_views"]
    need(set(selected["selected_prior_finite_case_ids"]) == FIVE_IDS and
         selected["selected_continuum_original_case_id"] == CONTINUUM_ID and
         selected["finite_event_semantics_never_used_for_continuum"] is True,
         "FINITE_CONTINUUM_UNION_IDENTITY_DRIFT")
    view = selected["continuum"]
    meta = bind_view(view, indexed[CONTINUUM_ID])
    zeros = view["zero_set"]
    need(view["status"] == "COMPLETE_CLOSED_CONTINUUM_ZERO_SOURCE_RESEARCH"
         and zeros["kind"] == "CLOSED_CONTINUUM_ZERO_COMPONENT"
         and zeros["every_closed_source_point_is_zero"] is True
         and zeros["closed_source_interval"] == meta["source_interval"]
         and zeros["isolated_root_count"] is None
         and zeros["isolated_finite_root_list_applicable"] is False,
         "CONTINUUM_REPLACED_BY_FINITE_EVENT_OR_NONTRUTH")
    add("continuum", CONTINUUM_ID, view, COMPLETE, meta["source_interval"],
        "COMPLETE_CLOSED_CONTINUUM_ZERO_SET")

    view = producer("knot").analyze_frozen_case(KNOT_ID)
    meta = bind_view(view, indexed[KNOT_ID])
    need(view["status"] == "EXACT_SOURCE_BOUND_TWO_SPAN_KNOT_ROOT_SET_RESEARCH"
         and view["frozen_case_id"] == KNOT_ID
         and view["global_source_knot_deduplication_established"] is True
         and view["global_multispan_root_count_established"] is True
         and type(view["global_distinct_roots_closed_source"]) is int
         and view["global_distinct_roots_closed_source"] == 1,
         "TWO_SPAN_FULL_SOURCE_PROOF_NOT_ESTABLISHED")
    add("knot", KNOT_ID, view, COMPLETE, meta["source_interval"], "COMPLETE_FINITE_SOURCE_ZERO_SET")

    mod = producer("trig_fixed")
    proofs = mod.replay_original_proofs()
    expected_ids = {"composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail0",
                    "composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail100",
                    V41_ID}
    need(set(mod.CASES) == expected_ids, "FIXED_TRIG_PRODUCER_SCOPE_DRIFT")
    for cid in sorted(expected_ids):
        reference = mod.reference_view(cid, proofs)
        need(reference["original_source_binding_sha256"] == mod.source_binding(indexed[cid]),
             "FIXED_TRIG_SOURCE_ROW_BINDING_MISMATCH")
        view = mod.compose(reference)
        need(view["status"] == "PINNED_TRIGONOMETRIC_CHILD_VIEWS_RECONCILED_RESEARCH_ONLY"
             and view["source_case_id"] == cid
             and view["source_binding_sha256"] == mod.source_binding(indexed[cid])
             and type(view["distinct_open_roots_proved_for_this_fixed_source"]) is int
             and view["distinct_open_roots_proved_for_this_fixed_source"] == 2,
             "FIXED_TRIG_SOURCE_COMPOSITION_NOT_ESTABLISHED")
        add("trig_fixed", cid, view, COMPLETE, source_metadata(indexed[cid])["source_interval"],
            "COMPLETE_FINITE_SOURCE_ZERO_SET")

    stationary = producer("stationary").replay_frozen_stationary_cases()
    selected_stationary = [v for v in stationary if v["historical_v54_disposition"] == ORDER_GAP]
    expected_ids = {"composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0",
                    "composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100"}
    need(len(stationary) == 3 and len(selected_stationary) == 2 and
         {v["source_case_id"] for v in selected_stationary} == expected_ids,
         "STATIONARY_CERTIFIED_SOURCE_MUST_NOT_ENTER_50_CASE_DENOMINATOR")
    for view in selected_stationary:
        cid = view["source_case_id"]
        meta = bind_view(view, indexed[cid], hash_field="original_source_sha256")
        need(view["status"] == "CONDITIONAL_EXACT_STATIONARY_POLYNOMIAL_KNOT_COMPOSITION"
             and view["left_physical_endpoint"]["relation"] == "NEGATIVE"
             and view["right_physical_endpoint"]["relation"] == "POSITIVE"
             and len(view["ordered_physical_zero_events"]) == 1
             and type(view["distinct_open_physical_zeros"]) is int
             and view["distinct_open_physical_zeros"] == 1,
             "STATIONARY_FULL_SOURCE_PROOF_NOT_ESTABLISHED")
        add("stationary", cid, view, COMPLETE, meta["source_interval"],
            "COMPLETE_FINITE_SOURCE_ZERO_SET")

    view = producer("v44").prove()
    meta = bind_view(view, indexed[V44_ID])
    need(view["status"] == "EXACT_FROZEN_V44_PROOF_CUT_ROOT_SET_PARTITION_RESEARCH"
         and view["frozen_case_id"] == V44_ID
         and type(view["complete_physical_root_count"]) is int
         and view["complete_physical_root_count"] == 1
         and view["root_count_conserved_across_proof_cells"] is True
         and view["all_proof_cuts_are_event_neutral"] is True,
         "V44_FULL_SOURCE_ROOT_PARTITION_NOT_ESTABLISHED")
    add("v44", V44_ID, view, COMPLETE, meta["source_interval"], "COMPLETE_FINITE_SOURCE_ZERO_SET")

    proof = producer("refusal_cone").contract()
    matches = [v for v in proof["probe_cases"] if v["id"] == POSITIVE_ID]
    need(len(matches) == 1, "HARVESTED_V43_POSITIVE_SOURCE_MISSING")
    view = matches[0]
    need(view["sign"] == "POSITIVE_ON_CLOSED_SOURCE_SPAN" and
         view["strict_lower_bound"] == "7/24", "V43_CLOSED_SOURCE_POSITIVITY_NOT_ESTABLISHED")
    add("refusal_cone", POSITIVE_ID, view, COMPLETE, view["source_interval"],
        "COMPLETE_STRICT_POSITIVE_SOURCE_ZERO_SET_EMPTY")

    view = producer("v23_bernstein").expected_report()
    pinned_saved("v23_bernstein", view)
    meta = bind_view(view, indexed[V23_ID], hash_field="original_source_sha256")
    need(view["case_id"] == V23_ID and
         bounded_bytes(view["original_source"]) == bounded_bytes(indexed[V23_ID]["spec"])
         and bounded_bytes(view["historical_observation"]) ==
             bounded_bytes(indexed[V23_ID]["expected"]),
         "V23_ORIGINAL_SOURCE_OR_REFUSAL_BINDING_MISMATCH")
    events = view["source_specific_proof"]["physical_event_proof"]
    need(events["complete_for_original_closed_source"] is True and
         type(events["closed_distinct_root_count"]) is int and
         events["closed_distinct_root_count"] == 1 and
         events["open_distinct_root_count"] == 0 and
         events["continuum_zero_component"] is False and
         events["events"][0]["analytic_order"] == 2,
         "V23_CLOSED_SOURCE_EVENT_PROOF_MISSING")
    add("v23_bernstein", V23_ID, view, COMPLETE, meta["source_interval"],
        "COMPLETE_FINITE_SOURCE_ZERO_SET")

    # Each record below proves only an actual ORIGINAL second span [1,2].
    # Historical certification of [0,1] cannot supply its missing ordered view.
    tail_specs = {
        "v10_tail0_crossings": (None, "source_case", "physical_source_span"),
        "v10_tail_crossing": (None, "source_case", "source_span"),
        "v11_tail_contrast": ("v11_v43_tail_reports", "case_id", "physical_source_span"),
        "v12_tail_contrast": ("v12_v43_tail_reports", "case_id", "physical_source_span"),
        "v13_even_factor": (None, "case_id", "original_physical_source_span"),
        "v16_chebyshev_crossing": (None, "case_id", "original_physical_source_span"),
        "v17_positive_turn": (None, "case_id", "original_physical_source_span"),
    }
    for key, (container, id_key, span_key) in tail_specs.items():
        proof = producer(key).contract()
        views = proof[container] if container else [proof]
        need(len(views) == len(TAIL_IDS[key]) and
             {v[id_key] for v in views} == TAIL_IDS[key],
             "TAIL_PRODUCER_SOURCE_IDENTITIES_OR_CARDINALITY_DRIFT")
        for view in views:
            cid = view[id_key]
            need(cid in indexed and view[span_key] == ["1", "2"] and
                 indexed[cid]["expected"]["v54_disposition"] == "BLOCKED",
                 "TAIL_PROOF_ORIGINAL_SOURCE_SCOPE_DRIFT")
            add(key, cid, view, TAIL, view[span_key], "COMPLETE_REFUSED_SECOND_SPAN_ONLY")

    # Preserve V6's actual ordered views, including source-local interval and
    # endpoint authority, without turning a checked child into a composed source.
    mod = producer("v6_ordered")
    selected = [r for r in indexed.values() if r["expected"]["v54_disposition"] == ORDER_GAP
                and any(s[0] == V6 for s in r["expected"]["observed"]["spans"])]
    need(len(selected) == 18, "V6_ORDERED_CHILD_DENOMINATOR_CHANGED")
    for row in selected:
        candidate = mod.build_source_candidate(row["spec"])
        bind_view(candidate, row)
        need(candidate["status"] == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
             "V6_REFUSAL_IS_NOT_ORDERED_CHILD_EVIDENCE")
        need(mod.validate_source_candidate(candidate, row["spec"]) is True,
             "V6_ORIGINAL_SOURCE_CANDIDATE_INVALID")
        views = candidate["views"]
        need(len(views) == 1 and candidate["historical_span_count"] == 2 and
             candidate["v6_span_count"] == 1 and views[0]["historical_owner"] == V6,
             "V6_CHILD_SCOPE_CHANGED")
        add("v6_ordered", row["id"], candidate, CHILD, views[0]["source_interval"],
            "ONE_SOURCE_BOUND_V6_ORDERED_CHILD_ONLY")
    # Recheck all direct pins after replay, and preserve each producer's own
    # transitive source/module/report checks rather than substituting a PASS flag.
    for name, sha in PRODUCERS.values():
        pin(HERE / name, sha)
    return receipts


GAPS = {
    COMPLETE: "Selected source-specific zero-set proof exists; historical route and general PB-007 obligations remain unchanged.",
    TAIL: "First original source span needs an ordered event/endpoint view and complete source-knot composition; a tail-only proof does not prove the whole source.",
    CHILD: "Only one V6 child has a checked ordered view; the other original span and cross-owner source-knot composition are not supplied by this registered evidence.",
    UNREGISTERED: "No source event/order witness is registered here; this is not a theorem that no other proof exists.",
}


def expected_report():
    indexed = original_corpus()
    receipts = replay_evidence(indexed)
    historical = [r for r in indexed.values() if r["expected"]["v54_disposition"] in
                  ("BLOCKED", ORDER_GAP)]
    need(len(historical) == 50 and set(receipts) <= {r["id"] for r in historical},
         "EVIDENCE_OUTSIDE_FROZEN_50_CASE_DENOMINATOR")
    rows = []
    for row in sorted(historical, key=lambda r: r["id"]):
        receipt = receipts.get(row["id"])
        level = receipt["level"] if receipt else UNREGISTERED
        rows.append({
            "case_id": row["id"], "origin": row["origin"], "provenance_kind": row["kind"],
            **source_metadata(row),
            "historical_v54_disposition": row["expected"]["v54_disposition"],
            "historical_observed_source_status": row["expected"]["observed"]["status"],
            "historical_spans": row["expected"]["observed"]["spans"],
            "registered_evidence_level": level,
            "evidence": receipt,
            "remaining_requirement": GAPS[level],
            "historical_disposition_changed": False,
        })
    def counts(items):
        counted = Counter(r["registered_evidence_level"] for r in items)
        return {key: counted[key] for key in LEVELS}
    summary = {
        "total_historical_unresolved_source_cases": len(rows),
        "by_registered_evidence_level": counts(rows),
        "historical_route_refusals": counts(r for r in rows if r["historical_v54_disposition"] == "BLOCKED"),
        "historical_missing_ordered_premises": counts(r for r in rows if r["historical_v54_disposition"] == ORDER_GAP),
        "complete_continuum_sources": sum(r["evidence"] is not None and
            r["evidence"]["scope"] == "COMPLETE_CLOSED_CONTINUUM_ZERO_SET" for r in rows),
    }
    report = {
        "schema": SCHEMA, "task": "MC-038", "evidence_class": "DETERMINISTIC_MODEL",
        "purpose": "SOURCE_BOUND_REGISTERED_EVIDENCE_RECONCILIATION_NOT_GENERIC_ROUTE_ACCEPTANCE",
        "source_registry_baseline_main": BASE_MAIN,
        "source_archaeology_baseline_main": ARCHAEOLOGY_BASE_MAIN,
        "frozen_corpus_git_blob": PINS["pb00701-finite-owner-corpus-v54.json"],
        "historical_v54": {"original_source_cases": 121, "route_refusals": 20,
                           "missing_ordered_span_premises": 30, "dispositions_changed": False},
        "registry_scope": {
            "all_50_historical_unresolved_ids_enumerated": True,
            "all_registered_producers_reexecuted_from_pinned_original_sources": True,
            "all_possible_post_v54_proofs_exhaustively_discovered": False,
            "missing_registry_entry_proves_mathematical_impossibility": False,
            "new_general_root_event_or_composition_theorem": False,
            "normalized_universal_root_event_consumer": False,
        },
        "producer_registry": [
            {"producer": key, "code": name, "code_git_blob": sha,
             "saved_report": ({"path": SAVED_REPORTS[key][0],
                               "git_blob": SAVED_REPORTS[key][1]} if key in SAVED_REPORTS else None)}
            for key, (name, sha) in sorted(PRODUCERS.items())],
        "summary": summary,
        "source_cases": rows,
        "gates": {"PB-007-01": "OPEN", "PB-007-02": "OPEN", "PB-007-03": "OPEN_PROPAGATED",
                  "PB-007-04": "OPEN_PROPAGATED", "MC-B": "NOT_ESTABLISHED", "MC-1": "NOT_ESTABLISHED",
                  "native_geometry_or_STEP_qualified": False, "production_authorized": False,
                  "required_machining_operations": 26},
    }
    bounded_bytes(report)
    return report


def _compare_with_replayed_bytes(submitted, expected_bytes):
    need(bounded_bytes(submitted) == expected_bytes,
         "REPORT_DISAGREES_WITH_PINNED_ORIGINAL_SOURCE_PRODUCER_REPLAY")
    return True


def validate_report(submitted):
    # Preflight BEFORE the roughly one-minute trusted proof replay.
    bounded_bytes(submitted)
    return _compare_with_replayed_bytes(submitted, bounded_bytes(expected_report()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    options = parser.parse_args()
    if not (options.contract or options.write_report):
        parser.error("choose --contract or --write-report")
    expected = expected_report()
    if options.write_report:
        MACHINE.write_text(json.dumps(expected, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    if options.contract:
        _compare_with_replayed_bytes(read_json(MACHINE), bounded_bytes(expected))
        print("PASS: exact 50-source registered-evidence reconciliation; frozen V54 dispositions unchanged")
        print(json.dumps(expected["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
