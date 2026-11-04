#!/usr/bin/env python3
"""PB-007-01 original-source non-injectivity of zero-set-only sign transfer.

Negative research C, not a general event solver or historical v54 admission.
Every exact equality is rational polynomial/Laurent algebra, with the sole
transcendental step the elementary local zero/sign theorem for cosine.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
REGISTRY = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
CASE = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0"
CASE_SOURCE_SHA256 = "9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
REGISTRY_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99"
MAX_POWER = 8
SCHEMA = "radicadsac-pb00701-zero-set-only-sign-transfer-falsifier/1.0"
EVIDENCE_CLASS = "DETERMINISTIC_MODEL"


class Refusal(ValueError):
    pass


def require(ok: bool, reason: str):
    if not ok:
        raise Refusal(reason)


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def git_blob_bytes(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii")
                        + b"\\0" + raw).hexdigest()


def read_pinned_json(path: Path, blob: str):
    raw = path.read_bytes()
    require(git_blob_bytes(raw) == blob, "PINNED_SOURCE_DRIFT:" + path.name)
    return json.loads(raw.decode("utf-8"))


def strict_power(m) -> int:
    require(type(m) is int and 1 <= m <= MAX_POWER, "UNADMITTED_POWER_RESOURCE_OR_TYPE")
    return m


def coefficients(m: int) -> dict[int, Q]:
    """Exact Chebyshev/Laurent expansion of cos(x)**m in cos(h*x).

    2**m cos(x)**m = (z+z**-1)**m, z=e**(ix).
    Pair conjugate Laurent monomials; the middle m-even term is constant.
    """
    strict_power(m)
    result = {0: Q(comb(m, m // 2), 2 ** m) if m % 2 == 0 else Q(0)}
    for h in range(1, m + 1):
        if (m - h) % 2 == 0:
            result[h] = Q(comb(m, (m - h) // 2), 2 ** (m - 1))
    return result


def laurent_from_power(m: int) -> dict[int, Q]:
    strict_power(m)
    return {m - 2 * j: Q(comb(m, j), 2 ** m) for j in range(m + 1)}


def laurent_from_cosines(coefs: dict[int, Q]) -> dict[int, Q]:
    result = {}
    for h, weight in coefs.items():
        if h == 0:
            result[0] = result.get(0, Q(0)) + weight
        else:
            result[h] = result.get(h, Q(0)) + weight / 2
            result[-h] = result.get(-h, Q(0)) + weight / 2
    return {k: v for k, v in result.items() if v}


def rational(value: Q) -> str:
    return str(value)


def source_for_power(m: int) -> dict:
    """Two ORIGINAL clamped degree-zero B-spline spans, not a synthetic view.

    t in [0,2], actual knot 1, phase turns t/4 in every piece, all
    channel controls equal on both sides. m=1 reproduces frozen source.
    """
    coefs = coefficients(m)
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0",
        "parameter_hi": "2",
        "phase_turn_offset": "0",
        "phase_turn_rate": "1/4",
        "cos_splines": {
            str(h): {
                "degree": 0,
                "knots": ["0", "1", "2"],
                "controls": [rational(coef), rational(coef)],
            }
            for h, coef in sorted(coefs.items())
        },
        "sin_splines": {},
    }


def source_guard(m: int, supplied: dict):
    require(type(supplied) is dict and supplied == source_for_power(m),
            "ORIGINAL_SOURCE_NOT_EXACT_LAURENT_POWER")
    # Explicit Laurent-polynomial reconstruction: independent of cos(x) samples.
    require(laurent_from_cosines(coefficients(m)) == laurent_from_power(m),
            "TRIG_IDENTITY_NOT_EXACT")
    splines = supplied["cos_splines"]
    require(all(v["knots"] == ["0", "1", "2"]
                and v["degree"] == 0 and v["controls"][0] == v["controls"][1]
                for v in splines.values()), "ORIGINAL_SOURCE_KNOT_UNPROVED")
    return True


def history():
    corpus = read_pinned_json(CORPUS, CORPUS_BLOB)
    v2 = read_pinned_json(REGISTRY, REGISTRY_BLOB)
    cases = corpus["cases"]
    require(len(cases) == 121 and len({c["id"] for c in cases}) == 121,
            "HISTORICAL_121_ID_CENSUS_CHANGED")
    index = {c["id"]: c for c in cases}
    blocked = {c["id"] for c in cases
               if c["expected"]["v54_disposition"] == "BLOCKED"}
    missing = {c["id"] for c in cases
               if c["expected"]["v54_disposition"]
               == "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
    require(len(blocked) == 20 and len(missing) == 30 and not blocked & missing,
            "HISTORICAL_V54_CLASSIFICATION_CHANGED")
    source = index[CASE]
    require(source["kind"] == "COMPOSITE_TAIL"
            and source["origin"] == "verify_pb00701_v7"
            and source["spec"] == source_for_power(1)
            and digest(source["spec"]) == CASE_SOURCE_SHA256,
            "FROZEN_EXACT_ORIGINAL_SOURCE_CHANGED")
    require(source["expected"]["v54_disposition"] == "BLOCKED"
            and source["expected"]["observed"]["spans"][1] ==
            ["PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION",
             "BLOCKED", "V27_CHILD_LEFT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE"],
            "FROZEN_V27_FAILURE_ERASED")
    rows = v2["source_cases"]
    require(len(rows) == 50 and len({r["case_id"] for r in rows}) == 50,
            "SUPPLEMENTAL_FIFTY_ID_CENSUS_CHANGED")
    require({r["case_id"] for r in rows} == blocked | missing,
            "FROZEN_CASE_COHORT_ID_MISMATCH")
    for row in rows:
        src = index[row["case_id"]]
        require(row["source_sha256"] == digest(src["spec"])
                and row["historical_v54_disposition"]
                == src["expected"]["v54_disposition"]
                and row["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC"
                and row["evidence"]["complete_original_source_zero_set"] is True,
                "HISTORICAL_CASE_SOURCE_OR_EVIDENCE_DRIFT")
    require(v2["historical_v54"]["original_source_cases"] == 121
            and v2["historical_v54"]["route_refusals"] == 20
            and v2["historical_v54"]["missing_ordered_span_premises"] == 30,
            "V2_REPORTED_HISTORICAL_CENSUS_CHANGED")
    return {"frozen_corpus_git_blob": CORPUS_BLOB,
            "frozen_sources": 121, "historical_route_refusals": 20,
            "historical_missing_ordered_premises": 30,
            "supplemental_complete_original_sources": 50,
            "supplemental_finite": 49, "supplemental_continuum": 1,
            "frozen_reference_id": CASE,
            "frozen_reference_source_sha256": CASE_SOURCE_SHA256}


def proof(m: int) -> dict:
    strict_power(m)
    src = source_for_power(m)
    source_guard(m, src)
    # For t in [0,2], x=pi*t/2 lies in [0,pi]; cos(x) has exactly one
    # zero at x=pi/2 (t=1), is >0 to the left and <0 to the right.
    # cos(pi*(1+u)/2)=-sin(pi*u/2); nonzero derivative -pi/2 at u=0
    # gives analytic order m for the power. Exact signs are by parity.
    return {
        "power": m,
        "source_sha256": digest(src),
        "source_parameter_id": "source-time-t",
        "original_interval": ["0", "2"],
        "original_knot": "1",
        "original_piece_intervals": [["0", "1"], ["1", "2"]],
        "phase_turn_law": {"offset": "0", "rate": "1/4"},
        "exact_laurent_reconstruction": True,
        "cosine_coefficients": {str(h): rational(v)
                                for h, v in coefficients(m).items()},
        "closed_source_zero_set": ["1"],
        "global_distinct_closed_root_count": 1,
        "knot_root_deduplicated": True,
        "left_one_sided_order": m,
        "right_one_sided_order": m,
        "left_nonzero_cell_sign": 1,
        "right_nonzero_cell_sign": -1 if m % 2 else 1,
        "source_knot_event": "CROSSING" if m % 2 else "TOUCHING",
        "historical_frozen_source": m == 1,
        "new_frozen_case_claim": False,
        "general_pb007_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "production_authorized": False,
    }


def report():
    h = history()
    variants = [proof(m) for m in range(1, MAX_POWER + 1)]
    require(variants[0]["source_sha256"] == CASE_SOURCE_SHA256,
            "FROZEN_SOURCE_SHA_MISMATCH")
    require(len({r["source_sha256"] for r in variants}) == MAX_POWER,
            "NONUNIQUE_PROSPECTIVE_SOURCE_IDENTITIES")
    require(len({r["right_nonzero_cell_sign"] for r in variants}) == 2,
            "NO_EXACT_PARITY_COUNTEREXAMPLE")
    return {
        "schema": SCHEMA,
        "evidence_class": EVIDENCE_CLASS,
        "status": "BOUNDED_NEGATIVE_C_EXACT_ORIGINAL_SOURCE_SIGN_TRANSFER",
        "hypothesis_falsified": "ZERO_SET_ONLY_DETERMINES_ORDERED_SIGN_CELLS",
        "conclusion": "SAME_CLOSED_ROOT_SET_AND_PHASE_KNOT_CANNOT_FIX_ORDER_OR_ONE_SIDED_SIGNS",
        "not_a_general_impossibility_result": True,
        "historical": h,
        "before": dict(h),
        "after": dict(h),
        "historical_delta": {
            "frozen_sources": 0, "route_refusals": 0,
            "missing_ordered_premises": 0, "complete_supplemental_sources": 0,
            "newly_disposed_frozen_case_ids": [],
        },
        "variants": variants,
        "requires_source_bound_one_sided_jets_for_transfer": True,
        "pb00701_certified": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }


def attempt_power(m, source):
    try:
        source_guard(strict_power(m), source)
        return proof(m)
    except (Refusal, TypeError, KeyError, ValueError, OverflowError) as exc:
        return {"status": "RESOURCE_REFUSAL" if m == MAX_POWER + 1
                else "BLOCKED",
                "reason": str(exc), "is_truth_value": False,
                "pb00701_certified": False, "production_authorized": False}


def validate_report(submitted):
    try:
        require(type(submitted) is dict, "REPORT_NOT_OBJECT")
        require(len(canonical(submitted)) <= 65536, "REPORT_RESOURCE_LIMIT")
        require(canonical(submitted) == canonical(report()),
                "FORGED_OR_STALE_SOURCE_REPORT")
        return True
    except (Refusal, TypeError, ValueError, OverflowError):
        return False
