#!/usr/bin/env python3
"""MC-038: independently bind finite V27/V41 original trig source to interval proof.

The interval root checker reads the COMPLETE original rational B-spline source
and uses neither historical count-only child roots nor V27/V41 proof conclusions.
Research result only; no frozen v54 or MC-B capability admission.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

import pb00701_transverse_trig_interval as trig
import verify_pb00701_v27_fixed_source_order as v27
import verify_pb00701_v41_v13_fixed_source_order as v41

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research/machining-completeness/tasks/MC-038"
CORPUS = TASK / "pb00701-finite-owner-corpus-v54.json"
DOMAIN = ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json"
AUTH = ROOT / "handoffs/current-authority.json"
PROGRAMME = ROOT / "research/machining-completeness/programme-v1.json"
SCHEMA = "radicadsac-pb00701-bounded-transverse-original-source/1.0"
CASES = (v27.TAIL0, v27.TAIL100, v41.SOURCE_ID)
PINS = {
    CORPUS: "5841c331579489b25caef38cd412bdbf286f9134",
    DOMAIN: "23de82f5240a72509f7afe4acd5948b65bc4ff13",
    AUTH: "fa0233323a0804d8a5d3eb7cd892a274a6173fab",
    TASK / "verify_pb00701_v27_fixed_source_order.py": "006272b173a66bfb53cc4ddf0f5597857a42362b",
    TASK / "verify_pb00701_v41_v13_fixed_source_order.py": "358dd4071ef968635bcd85f61dfa1965e51abda1",
    TASK / "verify_pb00701_v43_refusal_cone.py": "2a8079ee2cf012bc2a12794c4c5ff19ebd760007",
}

class InvalidOriginal(ValueError):
    pass


def require(condition, reason):
    if not condition: raise InvalidOriginal(reason)


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def load(path): return json.loads(path.read_text(encoding="utf-8"))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def custody():
    for path, expected in PINS.items():
        require(git_blob(path) == expected,
                "ORIGINAL_SOURCE_OR_PROOF_BLOB_DRIFT: " + path.name)
    auth, programme, domain = load(AUTH), load(PROGRAMME), load(DOMAIN)
    require(auth["capability_status"] == "NOT_ESTABLISHED" and
            auth["production_authorized"] is False and
            programme["capability_status"] == "NOT_ESTABLISHED" and
            programme["production_authorized"] is False and
            any(x["id"] == "MC-B" and x["state"] == "NOT_ESTABLISHED"
                for x in programme["gates"]), "AUTHORITY_MISMATCH")
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "MACHINING_DOMAIN_DENOMINATOR_MISMATCH")
    corpus = load(CORPUS)
    # Reuse only source/provenance/phase/owner VALIDATION, not the earlier
    # proof drivers' source-specific root-count or root-order conclusions.
    index = v27.select(corpus)
    v41.check_source(corpus)
    return index


def source_binding(row):
    return hashlib.sha256(canonical({k: row[k] for k in
                                  ("id", "origin", "kind", "spec", "expected")})
                          .encode("ascii")).hexdigest()


def original_spans(row, lowerer):
    source = row["spec"]
    is_v27 = row["id"] in (v27.TAIL0, v27.TAIL100)
    edges = (Q(0), Q(1), Q(2)) if is_v27 else (Q(0), Q(1))
    harmonics = sorted(set(source["cos_splines"]) | set(source["sin_splines"]),
                       key=int)
    views = []
    for i, (left, right) in enumerate(zip(edges, edges[1:])):
        terms = {}
        for h in harmonics:
            def channel(name):
                if h not in source[name]: return (Q(0),)
                return lowerer.linear_piece(source, name, h, left, right)
            terms[int(h)] = (channel("cos_splines"), channel("sin_splines"))
        views.append({"interval": (left, right), "terms": terms,
                      "owner": row["expected"]["observed"]["spans"][i][0],
                      "span": trig.Span(left, right,
                                        source["phase_turn_offset"],
                                        source["phase_turn_rate"], terms)})
    for first, second in zip(views, views[1:]):
        knot = first["interval"][1]
        require(knot == second["interval"][0], "SOURCE_KNOT_GAP_OR_OVERLAP")
        for h in set(first["terms"]) | set(second["terms"]):
            for channel in range(2):
                lhs = trig.polynomial(first["terms"][h][channel], knot)
                rhs = trig.polynomial(second["terms"][h][channel], knot)
                require(lhs == rhs, "SOURCE_CHANNEL_KNOT_DISCONTINUITY")
    return views


def original_case(case_id, index, lowerer):
    require(case_id in CASES, "UNSUPPORTED_ORIGINAL_SOURCE")
    row = index[case_id]
    views = original_spans(row, lowerer)
    composed_signs = []
    roots, spans = [], []
    current = None
    for view in views:
        part = view["span"].prove(max_depth=14, max_nodes=20000)
        signs = part["endpoint_signs"]
        if current is None:
            current = signs[0]
            composed_signs.append(current)
        else:
            require(current == signs[0], "SOURCE_KNOT_SIGN_MISMATCH")
        for cell in part["partition"]:
            if cell["kind"] == "ONE_SIMPLE_ROOT":
                require(cell["left_sign"] == current, "WRONG_PHYSICAL_ROOT_ORDER")
                roots.append({
                    "descriptor": "UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE",
                    "strict_bracket": cell["strict_isolation"],
                    "owner": view["owner"], "smooth_multiplicity": 1,
                    "crossing": "POSITIVE_TO_NEGATIVE" if current > 0
                                else "NEGATIVE_TO_POSITIVE",
                })
                current = cell["right_sign"]
                composed_signs.append(current)
        require(current == signs[1], "ORIGINAL_SPAN_SIGN_MISMATCH")
        spans.append({"owner": view["owner"], "proof": part})
    return {"schema": SCHEMA, "source_case_id": case_id,
            "source_binding_sha256": source_binding(row),
            "source_parameter_id": row["spec"]["source_parameter_id"],
            "phase_turns": [row["spec"]["phase_turn_offset"],
                            row["spec"]["phase_turn_rate"]],
            "historical_v54_disposition": row["expected"]["v54_disposition"],
            "status": "CHECKED_BOUNDED_TRANSVERSE_RESEARCH",
            "evidence_class": "DETERMINISTIC_MODEL",
            "per_original_span": spans, "ordered_implicit_roots": roots,
            "maximal_physical_signs": composed_signs,
            "complete_simple_open_roots": len(roots),
            "true_knot_zero_supported": False,
            "historical_child_certified": False, "general_trig_theorem_claimed": False,
            "mc_b_mc1_native_brep_step_claimed": False,
            "production_authorized": False}


def contract():
    index = custody()
    lowerer = v27.exact_lowerer()
    results = {case: original_case(case, index, lowerer) for case in CASES}
    return results


def validate_submitted(case_id, supplied):
    if isinstance(supplied, (str, bytes)) or len(canonical(supplied)) > 100000:
        raise InvalidOriginal("OVERSIZED_OR_NONOBJECT_REPORT")
    index = custody()
    expected = original_case(case_id, index, v27.exact_lowerer())
    require(canonical(supplied) == canonical(expected),
            "FORGED_COUNT_ONLY_OR_UNCHECKED_ROOT_CLAIM")
    return expected
