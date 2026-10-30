#!/usr/bin/env python3
"""Source-bound normalized replay of five historical V54 route-refused sources.

This is a FINITE allowlisted evidence-consumption interface. It composes
three previously qualified source-specific producers without claiming their
mathematical methods generalize to any unlisted source or root grammar.
DETERMINISTIC_MODEL only; historic V54 decisions are immutable.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
SCHEMA = "radicadsac-mc038-five-source-evidence-replay/1.0"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
AUDIT_BLOB = "12c6efeb667a954ffc5a7e27849ae815d466580a"
DOMAIN_BLOB = "23de82f5240a72509f7afe4acd5948b65bc4ff13"
AUTH_BLOB = "fa0233323a0804d8a5d3eb7cd892a274a6173fab"
MAX_REPORT_BYTES = 65536
H = "harvested:verify_pb00701_v9:1a5fd052a155"
V8_0 = "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0"
V8_100 = "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail100"
V6_100 = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail100"
V9_100 = "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100"

# Fail closed if source-specific producer *code* OR already qualified report
# drifts. New producer versions must be reviewed and explicitly repinned.
PRODUCERS = {
    "V27_THREE": {
        "code": "verify_pb00701_v27_three_frozen_refusals.py",
        "code_blob": "c88bc20500e67d419ab82ea19ba8762434f2aff8",
        "report": "pb00701-v27-three-frozen-refusals-witness.json",
        "report_blob": "f4961533fab39d423f01983dd05b70f6a599615b",
        "cases": [H, V8_0, V8_100],
    },
    "V6_KNOT": {
        "code": "verify_pb00701_v6_tail100_knot.py",
        "code_blob": "73b3f68bb4ecb8b4f69d073ebb0ee4621796d1a5",
        "report": "pb00701-v6-tail100-knot-post-v54-witness.json",
        "report_blob": "6a5763483bda5103f16617ea269360d4eba26c66",
        "cases": [V6_100],
    },
    "V9_V43": {
        "code": "verify_pb00701_v9_v43_full_source.py",
        "code_blob": "2cde41b799d5468ad84e7e482580fd4351b1d638",
        "report": "pb00701-v9-v43-full-source-witness.json",
        "report_blob": "1882c231f346d0f4622086b6aeee246bb520624b",
        "cases": [V9_100],
    },
}
SOURCE_SHA = {
    H: "710259612833cfe40e73ae528e0d0e944a87123c9bb4b3f4f76cef33c45bcf4d",
    V8_0: "9abbed355812241cdef20f3ce3b3522619bdd682c3a73fb01828d8f95c72f0af",
    V8_100: "8e3af5a5e74c3fc3f364607f5c3c4b03cd1adc2e2dd6e16bfc03ddf870de0d2b",
    V6_100: "f6a0eb06c66af415fbb8abdfe62f9b36a2a2bf154e535d83307a80228e044ad5",
    V9_100: "cc13a39582060e763c573f2665b3ea3b6dfe8b76a6cb0fb77a7b0ec90cf6253a",
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def pin(path, sha):
    need(path.is_file() and git_blob(path) == sha,
         "pinned original source or prover Git blob mismatch: " + str(path))
    return path


def bounded_json(value):
    """Preflight untrusted reports before serialization, including cycle/depth."""
    stack = [(value, 0, False)]
    active = set()
    count = 0
    while stack:
        obj, depth, leaving = stack.pop()
        if leaving:
            active.remove(id(obj))
            continue
        count += 1
        need(count <= 4096 and depth <= 16,
             "RESOURCE_REFUSAL: report node/depth budget")
        if type(obj) in (dict, list):
            need(id(obj) not in active and len(obj) <= 128,
                 "RESOURCE_REFUSAL: report cycle/container budget")
            active.add(id(obj))
            stack.append((obj, depth, True))
            if type(obj) is dict:
                for key, val in obj.items():
                    need(type(key) is str and len(key) <= 256,
                         "RESOURCE_REFUSAL: report key")
                    stack.append((val, depth + 1, False))
            else:
                stack.extend((v, depth + 1, False) for v in obj)
        elif type(obj) is str:
            need(len(obj) <= 2048, "RESOURCE_REFUSAL: report string")
        elif type(obj) is int:
            need(abs(obj) < 10 ** 40, "RESOURCE_REFUSAL: report integer")
        else:
            need(obj is None or type(obj) is bool,
                 "invalid report scalar including binary float")
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     allow_nan=False).encode("utf-8")
    need(len(raw) <= MAX_REPORT_BYTES,
         "RESOURCE_REFUSAL: report serialization exceeds 64 KiB")
    return raw


def read_pinned_json(path, sha):
    pin(path, sha)
    raw = path.read_bytes()
    need(len(raw) <= MAX_REPORT_BYTES,
         "RESOURCE_REFUSAL: producer report exceeds 64 KiB")
    return json.loads(raw)


def import_pinned_producer(key):
    meta = PRODUCERS[key]
    path = pin(HERE / meta["code"], meta["code_blob"])
    spec = importlib.util.spec_from_file_location("mc038_source_bound_" + key, path)
    need(spec is not None and spec.loader is not None,
         "unable to import pinned proof producer")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    need(Path(mod.__file__).resolve() == path.resolve(),
         "unbound producer module source")
    pin(path, meta["code_blob"])
    return mod


def replay_producers():
    """Reexecute mathematical producers, never accept only caller-declared PASS."""
    out = {}
    for key, meta in PRODUCERS.items():
        mod = import_pinned_producer(key)
        saved = read_pinned_json(HERE / meta["report"], meta["report_blob"])
        bounded_json(saved)
        if key == "V27_THREE":
            original_rows = mod.load_frozen()
            recomputed = mod.verify_report(saved, original_rows)
        elif key == "V6_KNOT":
            recomputed = mod.expected_machine_record()
            need(saved == recomputed, "V6 source proof report drift")
        elif key == "V9_V43":
            need(mod.validate_report(saved) is True,
                 "V9/V43 source proof report invalid")
            recomputed = mod.expected_report()
            need(saved == recomputed, "V9/V43 source proof replay mismatch")
        else:
            raise ValueError("unknown proof producer")
        need(saved == recomputed, "producer's original source proof disagrees")
        out[key] = recomputed
    return out


def original_corpus():
    pin(HERE / "pb00701-finite-owner-corpus-v54.json", CORPUS_BLOB)
    pin(HERE / "verify_pb00701_post_v54_frontier.py", AUDIT_BLOB)
    pin(ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json",
        DOMAIN_BLOB)
    pin(ROOT / "handoffs/current-authority.json", AUTH_BLOB)
    import verify_pb00701_post_v54_frontier as audit
    raw, inventory, coverage = audit.inputs()
    census = audit.audit(raw, inventory, coverage)
    need(census["cases"] == 121 and
         census["v54_dispositions"]["BLOCKED"] == 20 and
         census["v54_dispositions"][
             "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
         "frozen V54 denominator/disposition drift")
    domain = json.loads((ROOT / "research/machining-completeness/tasks/MC-002/"
                         "domain-contract-v1.json").read_text())
    auth = json.loads((ROOT / "handoffs/current-authority.json").read_text())
    need(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
         "admissible machining domain narrowed")
    need(auth["capability_status"] == "NOT_ESTABLISHED" and
         auth["production_authorized"] is False,
         "MC-1/production status illegally promoted")
    return {r["id"]: r for r in raw["cases"]}


def rational(value):
    need(type(value) is str, "noncanonical source root coordinate")
    q = Q(value)
    need(str(q) == value, "noncanonical rational")
    return q


def rational_event(t, location, classification, order, left, right):
    return {
        "coordinate": {"kind": "RATIONAL", "value": t},
        "location": location, "classification": classification,
        "order": order, "left_sign": left, "right_sign": right,
    }


def implicit_event(lo, hi, order, left, right):
    return {
        "coordinate": {"kind": "IMPLICIT_STRICT_BRACKET",
                       "lower": lo, "upper": hi,
                       "source_root_unique_by_producer_theorem": True},
        "location": "SPAN_OPEN", "classification": "CROSSING",
        "order": {"kind": "INTEGER", "value": order},
        "left_sign": left, "right_sign": right,
    }


def source_knots(row):
    """Check root locations against the *actual* original-source knot set."""
    s = row["spec"]
    left, right = rational(s["parameter_lo"]), rational(s["parameter_hi"])
    knots = set()
    for channel in ("cos_splines", "sin_splines"):
        for spline in s[channel].values():
            knots.update(rational(x) for x in spline["knots"])
    need(all(left <= v <= right for v in knots), "source knots outside interval")
    internal = sorted(x for x in knots if left < x < right)
    return [left] + internal + [right]


def normalize_one(case_id, reports, row):
    if case_id in (H, V8_0, V8_100):
        producer = "V27_THREE"
        p = reports[producer]["sources"][case_id]
        need(p["original_source_sha256"] == SOURCE_SHA[case_id],
             "V27 original-source SHA mismatch")
        source = p["physical_event_proof"]
        events = []
        for event in source["events"]:
            if event["location"] == "SOURCE_LEFT_ENDPOINT":
                events.append(rational_event(
                    event["t"], "SOURCE_LEFT_ENDPOINT", "BOUNDARY",
                    {"kind": "ONE_SIDED", "right": event["one_sided_order"]},
                    None, event["right_sign"]))
            else:
                events.append(rational_event(
                    event["t"], event["location"], event["kind"],
                    {"kind": "INTEGER", "value": event["order"]},
                    event["left_sign"], event["right_sign"]))
        count_closed = source["closed_source_root_count"]
        count_strict = source["source_interior_root_count"]
        span_counts = source["strict_span_open_root_counts"]
        signs = source["maximal_open_signs"]
    elif case_id == V6_100:
        producer = "V6_KNOT"
        source = reports[producer]["proof"]
        knot = source["source_knot"]
        events = [rational_event(
            knot["coordinate"], "SOURCE_KNOT", knot["event"],
            {"kind": "ONE_SIDED",
             "left": knot["left_one_sided_vanishing_order"],
             "right": knot["right_one_sided_vanishing_order"]},
            knot["left_inward_sign"], knot["right_inward_sign"])]
        need(knot["exact_zero"] is True and
             knot["global_smooth_multiplicity_claimed"] is False,
             "source knot zero / sided order scope inflated")
        count_closed = source["physical_root_count_closed"]
        count_strict = source["physical_root_count_strict_source_interior"]
        span_counts = source["span_open_root_counts"]
        signs = source["maximal_open_physical_signs"]
    elif case_id == V9_100:
        producer = "V9_V43"
        source = reports[producer]["proof"]
        root = source["only_physical_event"]
        need(root["kind"] == "IMPLICIT_UNIQUE_SOURCE_ROOT" and
             root["algebraic_or_rational_root_claimed"] is False,
             "fabricated exact algebraic source root coordinate")
        lo, hi = root["strict_bracket"]
        events = [implicit_event(
            lo, hi, root["multiplicity"], root["left_sign"],
            root["right_sign"])]
        count_closed = source["whole_source_open_root_count"]
        count_strict = count_closed
        span_counts = source["span_open_root_counts"]
        signs = source["maximal_source_sign_cells"]
    else:
        raise ValueError("UNSUPPORTED_SOURCE: no accepted complete-source producer")
    spec = row["spec"]
    return {
        "case_id": case_id, "producer": producer,
        "source_sha256": SOURCE_SHA[case_id],
        "source_parameter_id": spec["source_parameter_id"],
        "source_interval": [spec["parameter_lo"], spec["parameter_hi"]],
        "phase_turn_law": {
            "offset": spec["phase_turn_offset"], "rate": spec["phase_turn_rate"]},
        "historical_disposition": row["expected"]["v54_disposition"],
        "historical_refusal": [
            {"owner": s[0], "reason": s[2]}
            for s in row["expected"]["observed"]["spans"]
            if s[1] == "BLOCKED"],
        "events": events,
        "closed_root_count": count_closed,
        "strict_source_open_root_count": count_strict,
        "strict_span_open_root_counts": span_counts,
        "maximal_open_signs": signs,
        "generic_route_repaired": False,
        "source_specific_mathematics_only": True,
    }


# Independent finite admission oracle (NOT arbitrary-source proof coverage).
# Every admitted event kind/position and sign shape is explicit and adversarially
# enforced. Adding new original sources requires new qualified producer pins.
EXPECTED_SHAPES = {
    H: (1, 0, [0], ["POSITIVE"], ["BOUNDARY"]),
    V8_0: (2, 2, [1, 1],
           ["POSITIVE", "POSITIVE", "NEGATIVE"],
           ["TOUCHING", "CROSSING"]),
    V8_100: (1, 1, [1, 0], ["POSITIVE", "POSITIVE"], ["TOUCHING"]),
    V6_100: (1, 1, [0, 0], ["POSITIVE", "POSITIVE"], ["TOUCHING"]),
    V9_100: (1, 1, [1, 0], ["NEGATIVE", "POSITIVE"], ["CROSSING"]),
}


def validate_view(view, row):
    need(type(view) is dict and view["case_id"] in EXPECTED_SHAPES,
         "UNSUPPORTED_SOURCE: unknown normalized source")
    cid = view["case_id"]
    need(set(view) == {
        "case_id", "producer", "source_sha256", "source_parameter_id",
        "source_interval", "phase_turn_law", "historical_disposition",
        "historical_refusal", "events", "closed_root_count",
        "strict_source_open_root_count", "strict_span_open_root_counts",
        "maximal_open_signs", "generic_route_repaired",
        "source_specific_mathematics_only",
    }, "extra/missing normalized proof-contract fields")
    need(type(row) is dict and row.get("id") == cid and
         row.get("expected", {}).get("id") == cid,
         "source row identifier not bound to normalized proof")
    owners = [key for key, meta in PRODUCERS.items()
              if cid in meta["cases"]]
    need(len(owners) == 1 and view["producer"] == owners[0],
         "cross-producer source proof ownership substituted")
    source_record = row["spec"]
    original_bytes = json.dumps(source_record, sort_keys=True,
                                separators=(",", ":"), allow_nan=False).encode()
    need(hashlib.sha256(original_bytes).hexdigest() == SOURCE_SHA[cid],
         "original source record changed under normalized view")
    expected_refusal = [
        {"owner": span[0], "reason": span[2]}
        for span in row["expected"]["observed"]["spans"]
        if span[1] == "BLOCKED"]
    need(row["expected"]["v54_disposition"] == "BLOCKED" and
         len(expected_refusal) == 1 and
         view["historical_refusal"] == expected_refusal,
         "missing or forged literal historical V54 refusal authority")
    closed, strict, expected_spans, signs, kinds = EXPECTED_SHAPES[cid]
    need(view["historical_disposition"] == "BLOCKED" and
         view["generic_route_repaired"] is False and
         view["source_specific_mathematics_only"] is True,
         "historical route or proof scope falsely promoted")
    need(view["source_sha256"] == SOURCE_SHA[cid] and
         view["source_parameter_id"] == row["spec"]["source_parameter_id"] and
         view["source_interval"] == [row["spec"]["parameter_lo"],
                                     row["spec"]["parameter_hi"]] and
         view["phase_turn_law"] == {
             "offset": row["spec"]["phase_turn_offset"],
             "rate": row["spec"]["phase_turn_rate"]},
         "source/phase identity mismatch")
    need(view["closed_root_count"] == closed and
         view["strict_source_open_root_count"] == strict and
         view["strict_span_open_root_counts"] == expected_spans and
         view["maximal_open_signs"] == signs and
         [ev["classification"] for ev in view["events"]] == kinds,
         "exact selected-source event/count/sign shape mismatch")
    bounds = source_knots(row)
    need(len(expected_spans) == len(bounds) - 1,
         "source-span original knot count mismatch")
    events = view["events"]
    need(len(events) == closed and
         len(signs) == strict + 1,
         "closed-root or sign-cell completeness mismatch")
    prev = None
    interior_index = 0
    counted = [0] * (len(bounds) - 1)
    lo, hi = bounds[0], bounds[-1]
    for ev in events:
        need(type(ev) is dict and set(ev) == {
            "coordinate", "location", "classification", "order",
            "left_sign", "right_sign",
        }, "malformed/extended physical event record")
        position = ev["coordinate"]
        need(type(position) is dict, "invalid physical root coordinate")
        if position["kind"] == "RATIONAL":
            need(set(position) == {"kind", "value"},
                 "rational root record claims unproved source coordinates")
            low = high = rational(position["value"])
        else:
            need(set(position) == {
                "kind", "lower", "upper",
                "source_root_unique_by_producer_theorem"} and
                 position["kind"] == "IMPLICIT_STRICT_BRACKET" and
                 position["source_root_unique_by_producer_theorem"] is True,
                 "unsupported or invented source root descriptor")
            low, high = rational(position["lower"]), rational(position["upper"])
            need(low < high, "invalid implicit strict rational root bracket")
        need(lo <= low <= high <= hi, "root outside original source")
        need(prev is None or prev < low,
             "unseparated, duplicate or reordered physical roots")
        prev = high
        location = ev["location"]
        if location == "SOURCE_LEFT_ENDPOINT":
            need(low == high == lo and
                 ev["classification"] == "BOUNDARY" and
                 ev["left_sign"] is None and
                 ev["right_sign"] == signs[0],
                 "source left endpoint aliased with interior")
        elif location == "SOURCE_RIGHT_ENDPOINT":
            need(low == high == hi and
                 ev["classification"] == "BOUNDARY" and
                 ev["left_sign"] == signs[-1],
                 "source right endpoint aliased with interior")
        else:
            need(lo < low <= high < hi,
                 "interior root is an external endpoint")
            if location == "SOURCE_KNOT":
                need(set(ev["order"]) == {"kind", "left", "right"},
                     "true source knot requires separate one-sided orders")
                need(low == high and low in bounds[1:-1] and
                     ev["order"]["kind"] == "ONE_SIDED" and
                     ev["order"].get("left", 0) > 0 and
                     ev["order"].get("right", 0) > 0,
                     "source-knot double-count or false smooth order")
            else:
                need(set(ev["order"]) == {"kind", "value"},
                     "span-interior root must carry exact integer order")
                need(location == "SPAN_OPEN" and
                     ev["order"]["kind"] == "INTEGER" and
                     type(ev["order"]["value"]) is int and
                     ev["order"]["value"] > 0,
                     "missing complete physical span-root order")
                owners = [i for i in range(len(bounds) - 1)
                          if bounds[i] < low <= high < bounds[i + 1]]
                need(len(owners) == 1, "root does not lie in a unique source span")
                need((ev["order"]["value"] % 2 == 1) ==
                     (ev["classification"] == "CROSSING"),
                     "strict interior root multiplicity/parity contradiction")
                counted[owners[0]] += 1
            need(ev["left_sign"] == signs[interior_index] and
                 ev["right_sign"] == signs[interior_index + 1],
                 "incorrect one-sided physical sign transfer")
            need(ev["classification"] in ("CROSSING", "TOUCHING") and
                 ((ev["left_sign"] != ev["right_sign"]) ==
                  (ev["classification"] == "CROSSING")),
                 "event parity vs signs mismatch")
            interior_index += 1
    need(interior_index == strict and counted == expected_spans,
         "source-knot deduplication or span-local counts corrupted")
    if cid == H:
        need(events[0]["coordinate"] == {"kind": "RATIONAL", "value": "0"} and
             events[0]["order"] == {"kind": "ONE_SIDED", "right": 1},
             "historical harvested endpoint order changed")
    elif cid == V6_100:
        need(events[0]["coordinate"] == {"kind": "RATIONAL", "value": "1"} and
             events[0]["order"] == {"kind": "ONE_SIDED", "left": 1, "right": 1},
             "physical knot one-sided orders changed")
    elif cid == V9_100:
        need(events[0]["coordinate"] == {
            "kind": "IMPLICIT_STRICT_BRACKET",
            "lower": "1/4", "upper": "1/3",
            "source_root_unique_by_producer_theorem": True},
            "implicit source root bracket/identity changed")
    else:
        want = (["1/2", "3/2"] if cid == V8_0 else ["1/2"])
        need([ev["coordinate"] for ev in events] ==
             [{"kind": "RATIONAL", "value": x} for x in want],
             "frozen V8 source-root coordinate changed")
    return True


def expected_report():
    rows = original_corpus()
    producers = replay_producers()
    all_ids = [cid for meta in PRODUCERS.values() for cid in meta["cases"]]
    need(len(all_ids) == len(set(all_ids)) == 5 and
         set(all_ids) == set(SOURCE_SHA) == set(EXPECTED_SHAPES),
         "duplicate/omitted/unreviewed source case in producer union")
    historical_blocked = sorted(cid for cid, row in rows.items()
                                if row["expected"]["v54_disposition"] == "BLOCKED")
    need(len(historical_blocked) == 20 and set(all_ids) <= set(historical_blocked),
         "unsupported historical refused-source promotion")
    admitted = []
    for cid in sorted(all_ids):
        row = rows[cid]
        raw = json.dumps(row["spec"], sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
        need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA[cid],
             "original full-source canonical SHA-256 mismatch")
        view = normalize_one(cid, producers, row)
        need(validate_view(view, row), "failed source-attested normalization")
        admitted.append(view)
    leftovers = sorted(set(historical_blocked) - set(all_ids))
    need(len(leftovers) == 15 and len(admitted) == 5,
         "exact five-source historical census miscount")
    return {
        "schema": SCHEMA, "task": "MC-038",
        "evidence_class": "DETERMINISTIC_MODEL",
        "frozen_original_corpus_git_blob": CORPUS_BLOB,
        "producer_pins": [
            {"key": key, "code_blob": meta["code_blob"],
             "report_blob": meta["report_blob"], "case_ids": meta["cases"]}
            for key, meta in sorted(PRODUCERS.items())],
        "source_attested_views": admitted,
        "frozen_v54": {
            "source_case_count": 121,
            "historical_route_blocked": 20,
            "historical_missing_order_premises": 30,
            "frozen_historical_dispositions_modified": False},
        "selected_five_case_overlay": {
            "qualified_distinct_source_witnesses": 5,
            "qualified_v27_child_not_certified_frozen_source_cases": 4,
            "qualified_v43_refusal_frozen_source_cases": 1,
            "historical_route_refusals_without_only_these_five_proofs": 15,
            "historical_missing_order_premises": 30,
            "frozen_original_denominator": 121,
            "other_historical_refused_case_ids": leftovers,
            "not_an_exhaustive_combined_post_v54_census": True,
            "not_a_generic_V27_or_V43_solver": True},
        "gates": {
            "PB-007-01": "OPEN",
            "PB-007-02": "OPEN",
            "PB-007-03": "OPEN_PROPAGATED",
            "PB-007-04": "OPEN_PROPAGATED",
            "MC-B": "NOT_ESTABLISHED",
            "MC-1": "NOT_ESTABLISHED",
            "native_geometry_or_STEP_qualified": False,
            "production_authorized": False},
    }


def validate_report(report):
    actual = bounded_json(report)
    expected = expected_report()
    need(actual == bounded_json(expected),
         "forged source-ID, root/order/sign, provenance or gate report")
    return True
