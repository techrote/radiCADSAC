#!/usr/bin/env python3
"""PB-007-01 bounded original-source CLOSED continuum-zero semantic certificate.

Mathematical theorem: if every original open B-spline source piece is
identically zero and the *individual* original rational amplitude channels are
continuous at every physical knot, then the whole CLOSED source interval is a
continuum of zeros. This is a separate sum-type from finite root-event lists.
Research-only DETERMINISTIC_MODEL; no general nonidentity root solver.
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
SCHEMA = "radicadsac-pb00701-closed-continuum-zero-source/1.0"
MACHINE = HERE / "pb00701-continuum-zero-source-witness.json"
TARGET = "harvested:verify_pb00701_v53:cb01c327d5f1"
TARGET_SHA256 = "a02ab8d83473f81d47b20c205083403babfc07059ca82303f1e6c92ab7481423"
CORPUS_SHA = "5841c331579489b25caef38cd412bdbf286f9134"
AUDIT_SHA = "12c6efeb667a954ffc5a7e27849ae815d466580a"
DOMAIN_SHA = "23de82f5240a72509f7afe4acd5948b65bc4ff13"
AUTH_SHA = "fa0233323a0804d8a5d3eb7cd892a274a6173fab"
IDENTITY_SHA = "9fd150e97bce84fdb3c4bad075c9938f4df9136c"
FIVE_SOURCE_SHA = "a8aedb83772984831d5aa5c3b9b8d1cead04c345"
FIVE_REPORT_SHA = "4c619ee7011fa2d7a65f3391ff95cd8e7eecf3b0"
MAX_BYTES = 65536
MAX_PIECES = 16
MAX_CHANNELS = 12
MAX_DEGREE = 6
MAX_CONTROLS = 128


class Refusal(ValueError):
    """Failed admission is nontruth, not a root count or zero/nonzero proof."""


def need(ok, reason):
    if not ok:
        raise Refusal(reason)


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def pin(path, expected):
    need(path.is_file() and git_blob(path) == expected,
         "PINNED_SOURCE_OR_PRODUCER_GIT_BLOB_DRIFT: " + str(path))
    return path


def q_exact(raw):
    need(type(raw) is str and 0 < len(raw) <= 128,
         "NONCANONICAL_EXACT_RATIONAL_LITERAL")
    try:
        x = Q(raw)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("INVALID_RATIONAL_LITERAL") from exc
    need(str(x) == raw and x.numerator.bit_length() <= 128 and
         x.denominator.bit_length() <= 128,
         "NONCANONICAL_OR_RESOURCE_RATIONAL")
    return x


def guard_original_source(spec):
    """Finite preflight BEFORE invoking the historical affine identity lowerer."""
    need(type(spec) is dict and set(spec) == {
        "grammar", "cos_splines", "sin_splines", "parameter_lo",
        "parameter_hi", "phase_turn_offset", "phase_turn_rate",
        "source_parameter_id",
    }, "UNREVIEWED_ORIGINAL_SOURCE_FIELDS")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         type(spec["source_parameter_id"]) is str and
         0 < len(spec["source_parameter_id"]) <= 128,
         "INVALID_ORIGINAL_SOURCE_GRAMMAR_OR_ID")
    lo, hi = q_exact(spec["parameter_lo"]), q_exact(spec["parameter_hi"])
    offset, rate = q_exact(spec["phase_turn_offset"]), q_exact(spec["phase_turn_rate"])
    need(-4 <= lo < hi <= 4 and abs(offset) <= 4 and abs(rate) <= 4,
         "UNSUPPORTED_ORIGINAL_SOURCE_INTERVAL_OR_PHASE")
    groups = (spec["cos_splines"], spec["sin_splines"])
    need(all(type(g) is dict for g in groups) and
         1 <= sum(len(g) for g in groups) <= MAX_CHANNELS,
         "UNSUPPORTED_ACTIVE_HARMONIC_COUNT")
    original_edges = {lo, hi}
    for group_name, splines in (("cos", groups[0]), ("sin", groups[1])):
        for h, spline in splines.items():
            need(type(h) is str and h.isdecimal() and
                 h == str(int(h)) and int(h) <= 32 and
                 (group_name == "cos" or int(h) > 0),
                 "UNSUPPORTED_OR_NONCANONICAL_HARMONIC_INDEX")
            need(type(spline) is dict and
                 set(spline) == {"degree", "knots", "controls"},
                 "UNREVIEWED_SPLINE_FIELDS")
            degree = spline["degree"]
            need(type(degree) is int and 0 <= degree <= MAX_DEGREE,
                 "UNSUPPORTED_SPLINE_DEGREE")
            knots, controls = spline["knots"], spline["controls"]
            need(type(knots) is list and type(controls) is list and
                 degree + 1 <= len(controls) <= MAX_CONTROLS and
                 len(knots) == len(controls) + degree + 1,
                 "INVALID_SPLINE_KNOT_CONTROL_COUNT")
            k = [q_exact(v) for v in knots]
            c = [q_exact(v) for v in controls]
            need(all(k[i] <= k[i + 1] for i in range(len(k) - 1)),
                 "NONMONOTONE_ORIGINAL_KNOT_VECTOR")
            # The clamped source endpoint has the same exact B-spline value as
            # the one-sided interior limit. Unclamped/extended support refuses.
            need(k[:degree + 1] == [lo] * (degree + 1) and
                 k[-degree - 1:] == [hi] * (degree + 1) and
                 all(lo <= u <= hi for u in k),
                 "UNPROVED_CLOSED_SOURCE_ENDPOINT_CLAMPING")
            original_edges.update(x for x in k if lo < x < hi)
    edges = sorted(original_edges)
    need(1 <= len(edges) - 1 <= MAX_PIECES,
         "RESOURCE_REFUSAL: ORIGINAL_SOURCE_PIECE_BUDGET")
    # Serialization is only attempted after strict source field/type/size checks.
    packed = json.dumps(spec, sort_keys=True, separators=(",", ":"),
                        allow_nan=False).encode("utf-8")
    need(len(packed) <= MAX_BYTES,
         "RESOURCE_REFUSAL: ORIGINAL_SOURCE_BYTE_BUDGET")
    return lo, hi, offset, rate, edges, hashlib.sha256(packed).hexdigest()


def pinned_module(filename, sha, namespace):
    path = pin(HERE / filename, sha)
    spec = importlib.util.spec_from_file_location(namespace, path)
    need(spec is not None and spec.loader is not None,
         "PINNED_PYTHON_PRODUCER_IMPORT_FAILED")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    need(Path(mod.__file__).resolve() == path.resolve(),
         "PINNED_PYTHON_PRODUCER_PATH_MISMATCH")
    pin(path, sha)
    return mod


def original_piece_channel_continuity(lowerer, spec, edges):
    """Independent exact rational *amplitude* limits, without trig numerics.

    Sufficient, deliberately conservative: individual C_h and S_h channels
    must be continuous at every true source knot. Physically cancelling
    discontinuous channels are not admitted by this particular proof.
    """
    cos = lowerer._normalise_harmonic_splines(spec["cos_splines"], "cos_splines")
    sin = lowerer._normalise_harmonic_splines(spec["sin_splines"], "sin_splines")
    norms = [("COS", h, n) for h, n in sorted(cos.items())]
    norms += [("SIN", h, n) for h, n in sorted(sin.items())]
    master = lowerer._master_boundaries([n for _, _, n in norms], edges[0], edges[-1])
    need(master == edges, "ORIGINAL_BSPLINE_KNOT_PARTITION_CHANGED")
    records = []
    for label, harmonic, normal in norms:
        values = []
        for a, b in zip(edges, edges[1:]):
            piece = lowerer._piece_from_normal(normal, a, b)
            coefficients = tuple(Q(x) for x in piece["coefficients"])
            need(1 <= len(coefficients) <= MAX_CONTROLS and
                 all(x.numerator.bit_length() <= 2048 and
                     x.denominator.bit_length() <= 2048
                     for x in coefficients),
                 "RESOURCE_REFUSAL: LOWERED_COEFFICIENT_BUDGET")
            # Coefficients are for s=(u-a)/(b-a), hence s=0/1 at boundaries.
            values.append((coefficients[0], sum(coefficients, Q(0))))
        for i in range(len(values) - 1):
            need(values[i][1] == values[i + 1][0],
                 "UNPROVED_CHANNEL_CONTINUITY_AT_SOURCE_KNOT")
        records.append({
            "channel": label, "harmonic": harmonic,
            "source_knots_exactly_continuous": [str(x) for x in edges[1:-1]],
            "original_piece_endpoint_values": [
                {"at_left": str(x), "at_right": str(y)} for x, y in values],
        })
    return records


def prove_closed_zero(spec):
    """Sound conditional theorem for the admitted bounded ORIGINAL source."""
    lo, hi, offset, rate, edges, digest = guard_original_source(spec)
    helper = pinned_module("verify_pb00701_affine_identity_frontier.py",
                           IDENTITY_SHA, "mc038_pinned_affine_identity")
    lowerer = helper.original_lowerer()
    # Individual amplitude continuity is verified independently of the
    # analytic zero predicate, which only covers OPEN source spans.
    channels = original_piece_channel_continuity(lowerer, spec, edges)
    identity = helper.inspect_original_source(
        spec, max_order=helper.MAX_STATIONARY_CYCLOTOMIC_ORDER, lowerer=lowerer)
    need(identity.get("source_sha256") == digest and
         identity.get("source_parameter_id") == spec["source_parameter_id"],
         "ORIGINAL_SOURCE_IDENTITY_EVIDENCE_UNBOUND")
    if identity["status"] == "RESOURCE_REFUSAL":
        raise Refusal("RESOURCE_REFUSAL: ORIGINAL_AFFINE_IDENTITY_UNDECIDED")
    need(identity["status"] == "IDENTITY_ZERO_ON_ALL_OPEN_SPANS" and
         len(identity["spans"]) == len(edges) - 1 and
         all(p["identity_status"] == "IDENTITY_ZERO" and
             p["source_interval"] == [str(a), str(b)]
             for p, (a, b) in zip(identity["spans"], zip(edges, edges[1:]))),
         "NONIDENTITY_OR_UNPROVED_ORIGINAL_OPEN_SPAN")
    # Open-span identity + continuous component amplitudes and affine phase
    # gives continuity of F at every original source knot. Clamping proves
    # endpoint values = one-sided limits. F=0 on ALL closed source points.
    return {
        "schema": SCHEMA,
        "status": "COMPLETE_CLOSED_CONTINUUM_ZERO_SOURCE_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_sha256": digest,
        "source_parameter_id": spec["source_parameter_id"],
        "source_interval": [str(lo), str(hi)],
        "phase_turn_law": {"offset": str(offset), "rate": str(rate)},
        "original_source_edges": [str(x) for x in edges],
        "original_open_span_identity": [
            {"source_interval": p["source_interval"],
             "identity_status": p["identity_status"],
             "cyclotomic_order": p["cyclotomic_order"]}
            for p in identity["spans"]],
        "original_amplitude_channel_continuity": channels,
        "zero_set": {
            "kind": "CLOSED_CONTINUUM_ZERO_COMPONENT",
            "closed_source_interval": [str(lo), str(hi)],
            "every_closed_source_point_is_zero": True,
            "cardinality": "UNCOUNTABLY_INFINITE",
            "isolated_finite_root_list_applicable": False,
            "isolated_root_count": None,
            "ordered_sign_cells_applicable": False,
            "source_knot_isolating_root_multiplicity_applicable": False,
        },
        "analytic_nonidentity_root_solver_proved": False,
        "general_PB00701_closed": False,
        "native_or_STEP_qualified": False,
        "production_authorized": False,
    }


def attempt(spec):
    try:
        return prove_closed_zero(spec)
    except Refusal as exc:
        return {"schema": SCHEMA,
                "status": "RESOURCE_REFUSAL" if str(exc).startswith("RESOURCE_REFUSAL")
                          else "BLOCKED",
                "reason": str(exc), "is_truth_value": False,
                "production_authorized": False}
    except (MemoryError, OverflowError, RecursionError) as exc:
        return {"schema": SCHEMA, "status": "RESOURCE_REFUSAL",
                "reason": type(exc).__name__, "is_truth_value": False,
                "production_authorized": False}


def load_original_case():
    pin(HERE / "pb00701-finite-owner-corpus-v54.json", CORPUS_SHA)
    pin(HERE / "verify_pb00701_post_v54_frontier.py", AUDIT_SHA)
    pin(ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json",
        DOMAIN_SHA)
    pin(ROOT / "handoffs/current-authority.json", AUTH_SHA)
    import verify_pb00701_post_v54_frontier as auditor
    c, inv, coverage = auditor.inputs()
    audit = auditor.audit(c, inv, coverage)
    need(audit["cases"] == 121 and
         audit["v54_dispositions"]["BLOCKED"] == 20 and
         audit["v54_dispositions"][
             "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
         "FROZEN_V54_CENSUS_CHANGED")
    auth = json.loads((ROOT / "handoffs/current-authority.json").read_text())
    dom = json.loads((ROOT / "research/machining-completeness/tasks/MC-002/"
                      "domain-contract-v1.json").read_text())
    need(auth["production_authorized"] is False and
         auth["capability_status"] == "NOT_ESTABLISHED" and
         len(dom["coverage_rule"]["required_operation_ids"]) == 26,
         "PRODUCTION_AUTHORITY_OR_REQUIRED_26_DOMAIN_CHANGED")
    rows = [row for row in c["cases"] if row["id"] == TARGET]
    need(len(rows) == 1, "HISTORICAL_IDENTITY_ZERO_SOURCE_NOT_UNIQUE")
    row = rows[0]
    need(row["origin"] == "verify_pb00701_v53" and
         row["kind"] == "HARVESTED" and
         row["expected"] == {
             "id": TARGET, "observed": {"status": "BLOCKED", "spans": [[
                 "DELEGATED_V6_CONSTANT_MODULATION", "BLOCKED",
                 "TRIGONOMETRIC_IDENTITY_ZERO_REQUIRES_SEPARATE_SEMANTIC_HANDLING"]]},
             "v54_disposition": "BLOCKED"},
         "HISTORICAL_IDENTITY_ZERO_ROUTE_REFUSAL_CHANGED")
    _, _, _, _, _, digest = guard_original_source(row["spec"])
    need(digest == TARGET_SHA256,
         "FROZEN_HISTORICAL_IDENTITY_ZERO_SOURCE_SHA256_MISMATCH")
    return row, c


def load_five_original_finite():
    module = pinned_module("pb00701_five_source_evidence_replay.py",
                           FIVE_SOURCE_SHA, "mc038_pinned_five_finite_views")
    path = pin(HERE / "pb00701-five-source-evidence-replay.json", FIVE_REPORT_SHA)
    raw = path.read_bytes()
    need(len(raw) <= MAX_BYTES, "RESOURCE_REFUSAL: FIVE_VIEW_SOURCE_REPORT")
    saved = json.loads(raw)
    need(module.validate_report(saved) is True,
         "FIVE_FINITE_ORIGINAL_SOURCE_REPLAY_UNPROVED")
    need(len(saved["source_attested_views"]) == 5 and
         saved["frozen_v54"]["historical_route_blocked"] == 20 and
         saved["frozen_v54"]["historical_missing_order_premises"] == 30,
         "PINNED_FIVE_SOURCE_CONSUMER_CONTRACT_CHANGED")
    return saved


def expected_record():
    row, corpus = load_original_case()
    continuum = prove_closed_zero(row["spec"])
    finite = load_five_original_finite()
    finite_ids = sorted(v["case_id"] for v in finite["source_attested_views"])
    need(TARGET not in finite_ids and len(set(finite_ids)) == 5,
         "CONTINUUM_ZERO_CASE_ALIASED_WITH_FINITE_SOURCE_EVENT")
    frozen_blocked = sorted(x["id"] for x in corpus["cases"]
                            if x["expected"]["v54_disposition"] == "BLOCKED")
    six_ids = sorted(finite_ids + [TARGET])
    need(len(frozen_blocked) == 20 and len(six_ids) == len(set(six_ids)) == 6
         and set(six_ids) <= set(frozen_blocked),
         "FALSE_SELECTED_SIX_HISTORICAL_SOURCE_COVERAGE")
    other = sorted(set(frozen_blocked) - set(six_ids))
    need(len(other) == 14, "SELECTED_SIX_SOURCE_CENSUS_INCORRECT")
    return {
        "schema": "radicadsac-mc038-finite-and-continuum-original-source-union/1.0",
        "task": "MC-038", "evidence_class": "DETERMINISTIC_MODEL",
        "historical_v54_corpus_blob": CORPUS_SHA,
        "historical_v54": {
            "source_cases": 121, "route_refusals": 20,
            "missing_ordered_span_premises": 30,
            "original_route_dispositions_unchanged": True},
        "separate_source_zero_set_views": {
            "kind": "DISJOINT_FINITE_OR_CONTINUUM_ZERO_SET",
            "selected_prior_finite_case_ids": finite_ids,
            "selected_continuum_original_case_id": TARGET,
            "selected_continuum_source_sha256": TARGET_SHA256,
            "finite_event_semantics_never_used_for_continuum": True,
            "continuum": continuum,
        },
        "selected_six_source_only_overlay": {
            "distinct_historical_original_source_witnesses": 6,
            "finite_source_witnesses": 5,
            "continuum_zero_source_witnesses": 1,
            "historical_route_refusals_not_in_these_six": 14,
            "remaining_historical_case_ids": other,
            "missing_ordered_span_premises": 30,
            "original_source_denominator": 121,
            "not_a_global_reconciled_post_v54_census": True,
            "general_analytic_event_or_V6_route_proved": False,
        },
        "gates": {
            "PB-007-01": "OPEN", "PB-007-02": "OPEN",
            "PB-007-03": "OPEN_PROPAGATED",
            "PB-007-04": "OPEN_PROPAGATED",
            "MC-B": "NOT_ESTABLISHED", "MC-1": "NOT_ESTABLISHED",
            "native_geometry_STEP_qualified": False,
            "production_authorized": False,
        },
    }


def bounded_json(value):
    """Pre-serialization attack surface: no cycles, floats or unbounded records."""
    stack = [(value, 0, False)]
    live = set()
    nodes = 0
    while stack:
        v, depth, leaving = stack.pop()
        if leaving:
            live.remove(id(v))
            continue
        nodes += 1
        need(nodes <= 4096 and depth <= 16,
             "RESOURCE_REFUSAL: UNTRUSTED_RECORD_NODE_OR_DEPTH_BUDGET")
        if type(v) in (dict, list):
            need(id(v) not in live and len(v) <= 128,
                 "RESOURCE_REFUSAL: UNTRUSTED_RECORD_CYCLE_OR_CONTAINER")
            live.add(id(v))
            stack.append((v, depth, True))
            if type(v) is dict:
                for k, x in v.items():
                    need(type(k) is str and len(k) <= 256,
                         "RESOURCE_REFUSAL: UNTRUSTED_RECORD_KEY")
                    stack.append((x, depth + 1, False))
            else:
                stack.extend((x, depth + 1, False) for x in v)
        elif type(v) is str:
            need(len(v) <= 2048, "RESOURCE_REFUSAL: UNTRUSTED_RECORD_STRING")
        elif type(v) is int:
            need(abs(v) < 10**40, "RESOURCE_REFUSAL: UNTRUSTED_RECORD_INTEGER")
        else:
            need(v is None or type(v) is bool, "INVALID_UNTRUSTED_RECORD_SCALAR")
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     allow_nan=False).encode()
    need(len(raw) <= MAX_BYTES, "RESOURCE_REFUSAL: UNTRUSTED_RECORD_BYTES")
    return raw


def verify_record(report):
    need(bounded_json(report) == bounded_json(expected_record()),
         "FORGED_CONTINUUM_ZERO_PROOF_OR_SOURCE_UNION")
    return True
