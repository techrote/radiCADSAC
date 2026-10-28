#!/usr/bin/env python3
"""Read-only post-v54 PB-007-01 frontier census. NOT a theorem or gate verdict."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = {
    "pb00701-finite-owner-corpus-v54.json": "5841c331579489b25caef38cd412bdbf286f9134",
    "pb00701-finite-owner-inventory-v54.json": "8649c20ab77e199f9c3fa351b8b6742218f27abb",
    "pb00701-finite-owner-coverage-v54.json": "600ba29786f50397f29fd435fc5e2c57076088f9",
}
EXPECTED = {"BLOCKED": 20, "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE": 30,
            "CERTIFIED": 40, "FINITE_OWNER_SOURCE_EVIDENCE_CERTIFIED": 26,
            "MIXED_OWNER_SOURCE_EVIDENCE_CERTIFIED": 5}
BLOCKED_REASONS = {
 "DELEGATED_V6_CONSTANT_MODULATION:TRIGONOMETRIC_IDENTITY_ZERO_REQUIRES_SEPARATE_SEMANTIC_HANDLING": 1,
 "PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:NONCONSTANT_AMPLITUDE_PHASE_DEPENDENT_ANCHOR_NOT_CERTIFIED": 1,
 "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:V27_CHILD_LEFT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE": 1,
 "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:V27_CHILD_NOT_CERTIFIED": 4,
 "PB00701_V41_EXACT_ROTATED_COORDINATE_ORIENTATION_ROOT_PARTITION_COMPOSITION:V41_COMPLETE_V43_CHILD_NOT_COMPOSABLE": 1,
 "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF:CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED": 11,
 "PB00701_V44_EXACT_REAL_ALGEBRAIC_ORIENTATION_CUT_BOUNDARY:ALGEBRAIC_ORIENTATION_COORDINATE_CERTIFIED_BUT_EXACT_CONSUMPTION_AUTHORITY_MISSING": 1,
}
STATIC = "PB00701_GENERAL_COUPLED_THEOREM_BOUNDARY"
V6 = "DELEGATED_V6_CONSTANT_MODULATION"
V27 = "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION"
V43 = "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"


def require(ok, reason):
    if not ok:
        raise AssertionError(reason)


def git_blob(path):
    content = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()


def inputs():
    data = []
    for name, digest in PINS.items():
        path = ROOT / name
        require(git_blob(path) == digest, "frozen v54 Git blob identity drift: " + name)
        data.append(json.loads(path.read_text(encoding="utf-8")))
    return data


def check_composite_tail(row):
    """Validate the frozen tail0/tail100 source constructor from source bytes."""
    spec = row["spec"]
    lo, hi = Fraction(spec["parameter_lo"]), Fraction(spec["parameter_hi"])
    require(hi > lo, "composite source interval is not positive")
    mid = (lo + hi) / 2
    tail100 = row["id"].endswith(":tail100")
    if tail100:
        require("0" in spec["cos_splines"],
                "tail100 lacks harmonic-zero cosine ramp")
    for trig, splines in (("cos", spec["cos_splines"]),
                          ("sin", spec["sin_splines"])):
        for harmonic, bs in splines.items():
            degree = bs["degree"]
            require(type(degree) is int and degree >= 0,
                    "composite spline degree is invalid")
            width = degree + 1
            controls = [Fraction(value) for value in bs["controls"]]
            knots = [Fraction(value) for value in bs["knots"]]
            require(len(controls) == 2 * width,
                    "composite spline does not contain exactly two full pieces")
            require(knots == ([lo] * width + [mid] * width + [hi] * width),
                    "composite spline is not fully clamped at the exact midpoint")
            left, tail = controls[:width], controls[width:]
            require(left[-1] == tail[0],
                    "composite tail is not source-continuous at midpoint")
            if tail100 and trig == "cos" and harmonic == "0":
                require(degree > 0 and tail[-1] - tail[0] == 100,
                        "tail100 harmonic-zero ramp does not end at join+100")
                step = tail[1] - tail[0]
                require(all(tail[index] - tail[index - 1] == step
                            for index in range(1, len(tail))),
                        "tail100 harmonic-zero Bernstein controls are not linear")
            else:
                require(all(value == tail[0] for value in tail),
                        "tail0/nonzero-harmonic tail is not constant")


def audit(corpus, inventory, boundary):
    owners = inventory["owners"]
    table = {o["owner"]: o["category"] for o in owners}
    require(len(owners) == len(table) == inventory["owner_count"] == 43,
            "duplicated, missing or unexpected historical owner")
    require(all(type(cat) is int and cat in (1, 2, 3, 4) for cat in table.values()),
            "invalid owner category")
    categories = dict(Counter(str(cat) for cat in table.values()))
    require(categories == {"1": 5, "2": 20, "3": 16, "4": 2} ==
            inventory["category_counts"] == boundary["owner_category_counts"],
            "static owner category count mismatch")
    require(inventory["one_category_per_owner"] is True and
            inventory["counts_promoted_to_order"] is False,
            "invalid inventory authority flags")

    cases = corpus["cases"]
    summary = corpus["summary"]
    require(len(cases) == summary["cases"] == 121, "frozen corpus size mismatch")
    require(len(set(row["id"] for row in cases)) == 121, "duplicate source IDs")
    canonical_sources = [json.dumps(row["spec"], sort_keys=True, separators=(",", ":"))
                         for row in cases]
    require(len(set(canonical_sources)) == 121,
            "distinct case IDs do not bind distinct original source specifications")
    normalized_sources = []
    ignored_projection_annotations = 0
    for row in cases:
        normalized = dict(row["spec"])
        if "parameter_projection" in normalized:
            ignored_projection_annotations += 1
            normalized.pop("parameter_projection")
        normalized_sources.append(json.dumps(
            normalized, sort_keys=True, separators=(",", ":")))
    require(ignored_projection_annotations == 1,
            "historical ignored parameter_projection annotation count changed")
    require(len(set(normalized_sources)) == 121,
            "source uniqueness depends only on ignored parameter_projection annotation")
    dispositions = Counter()
    provenance = Counter()
    failures = Counter()
    v43_kinds = Counter()
    observed = {str(i): set() for i in range(1, 5)}
    missing_v6 = 0
    missing_v27 = 0

    for row in cases:
        require(row["id"] == row["expected"]["id"], "source/observation ID mismatch")
        require(row["kind"] in ("HARVESTED", "COMPOSITE_TAIL"),
                "unknown provenance kind")
        prefix = "harvested:" if row["kind"] == "HARVESTED" else "composite:"
        require(row["id"].startswith(prefix) and
                isinstance(row["origin"], str) and bool(row["origin"]),
                "source case ID contradicts observed provenance")
        if row["kind"] == "HARVESTED":
            require(row["id"].startswith("harvested:" + row["origin"] + ":") and
                    len(row["id"].rsplit(":", 1)[-1]) > 0,
                    "harvested case ID is not bound to its producing verifier origin")
        source = row["spec"]
        require(isinstance(source, dict) and
                source.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
                isinstance(source.get("source_parameter_id"), str) and
                bool(source["source_parameter_id"]),
                "missing original source grammar/identity binding")
        provenance[row["kind"]] += 1
        disp = row["expected"]["v54_disposition"]
        require(disp in EXPECTED, "unknown v54 disposition")
        dispositions[disp] += 1
        spans = row["expected"]["observed"]["spans"]
        require(isinstance(spans, list) and bool(spans), "missing observed source spans")
        owners_here, blocked_here = set(), []
        if row["kind"] == "COMPOSITE_TAIL":
            require(row["id"].endswith(":tail0") or row["id"].endswith(":tail100"),
                    "composite case ID has unknown tail constructor")
            label = row["id"][len("composite:"):].rsplit(":", 1)[0]
            require(label == spans[0][0],
                    "composite case ID owner label differs from first observed owner")
            check_composite_tail(row)
        for span in spans:
            require(isinstance(span, list) and len(span) == 3,
                    "malformed (owner,status,reason) observation")
            owner, status, reason = span
            require(owner in table and status in ("CERTIFIED", "BLOCKED"),
                    "unclassified route owner/status")
            require((reason is None) == (status == "CERTIFIED"),
                    "route reason contradicts status")
            owners_here.add(owner)
            observed[str(table[owner])].add(owner)
            if status == "BLOCKED":
                blocked_here.append(owner + ":" + reason)
                if owner == V43:
                    v43_kinds[row["kind"]] += 1
        # Count reconciliations alone cannot detect a forged parent observation
        # status while the individual span statuses remain unchanged.
        observed_status = row["expected"]["observed"]["status"]
        require(observed_status == ("BLOCKED" if blocked_here else "CERTIFIED"),
                "observed source status contradicts original span statuses")
        require((disp == "BLOCKED") == bool(blocked_here),
                "v54 source disposition contradicts historical route refusal")
        # A count-preserving swap of source dispositions must not relabel a
        # one-span result as a multi-span composition, or give a V53-only
        # category-1 composite a V54 category-2 promotion (and vice versa).
        classes = {table[owner] for owner in owners_here}
        if disp == "CERTIFIED":
            require(len(spans) == 1, "single-span certification has multiple spans")
        elif disp == "MIXED_OWNER_SOURCE_EVIDENCE_CERTIFIED":
            require(len(spans) >= 2 and classes == {1},
                    "preserved V53 composition lacks category-1-only ownership")
        elif disp == "FINITE_OWNER_SOURCE_EVIDENCE_CERTIFIED":
            require(len(spans) >= 2 and 2 in classes and classes <= {1, 2},
                    "new V54 composition lacks eligible category-2 span authority")
        elif disp == "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE":
            require(len(spans) >= 2 and 3 in classes,
                    "ordered-premise gap lacks multi-span category-3 ownership")
        if disp == "BLOCKED":
            require(len(blocked_here) == 1, "ambiguous preserved blocked case")
            failures[blocked_here[0]] += 1
        if disp == "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE":
            require(any(table[owner] == 3 for owner in owners_here),
                    "unjustified ordered-premise disposition")
            missing_v6 += int(V6 in owners_here)
            missing_v27 += int(V27 in owners_here)

    require(dict(dispositions) == EXPECTED == summary["v54_dispositions"],
            "v54 disposition changes")
    require(dict(provenance) == {"HARVESTED": 47, "COMPOSITE_TAIL": 74},
            "harvest/tail case mix changes")
    require(dict(failures) == BLOCKED_REASONS ==
            summary["remaining_uncertified_span_owner_reasons"],
            "source-route blocker reasons change")
    require(dict(v43_kinds) == {"HARVESTED": 1, "COMPOSITE_TAIL": 10},
            "V43 negative provenance split changed")
    require((missing_v6, missing_v27) == (18, 3),
            "category-3 case incidence changed")
    require({cat: sorted(names) for cat, names in observed.items()} ==
            summary["observed_by_category"], "observed owner identity/category mismatch")
    require(sum(map(len, observed.values())) == summary["observed_owner_count"] == 42,
            "42-owner observation count changed")
    require(set(table) - set().union(*observed.values()) == {STATIC} and
            table[STATIC] == 4, "static-only theorem emitter mislabelled")
    task = boundary["next_theorem_task"]
    require(task["issue_created"] is False and
            task["static_only_boundary_owner"] == STATIC,
            "unauthorized theorem issue or observed owner promotion")
    require(boundary["evidence_class"] == "DETERMINISTIC_MODEL" and
            all(boundary[k] is False for k in
                ("general_nonmonotone_solver_claimed", "general_noncommon_factor_solver_claimed",
                 "native_topology_claimed", "mc_b_retry_claimed")),
            "false general solver/native/MC-B promotion")
    return {"cases": 121, "static_owner_counts": categories,
            "observed_owners": 42, "static_only_owner": STATIC,
            "provenance": dict(provenance), "v54_dispositions": dict(dispositions),
            "blocked_route_reasons": dict(failures),
            "V43_blocked_case_provenance": dict(v43_kinds),
            "category3_cases_containing_V6": missing_v6,
            "category3_cases_containing_V27": missing_v27,
            "ignored_parameter_projection_annotations": ignored_projection_annotations,
            "distinct_sources_after_ignored_projection": len(set(normalized_sources)),
            "general_theorem_established": False, "native_or_MC_B_established": False}



def reject_mutation(corpus, inventory, boundary, change):
    """Only the *audit* may reject; malformed test setup must propagate."""
    c, i, b = copy.deepcopy(corpus), copy.deepcopy(inventory), copy.deepcopy(boundary)
    change(c, i, b)
    try:
        audit(c, i, b)
    except AssertionError:
        return
    raise AssertionError("corrupted frontier evidence accepted")


def self_test(corpus, inventory, boundary):
    def reject(change):
        reject_mutation(corpus, inventory, boundary, change)

    reject(lambda c, i, b: c["cases"][0]["expected"].update(
        v54_disposition="BLOCKED"))
    reject(lambda c, i, b: c["cases"][0]["expected"]["observed"]["spans"][0].__setitem__(
        0, "FORGED_OWNER"))
    reject(lambda c, i, b: i["owners"].pop())
    reject(lambda c, i, b: c["cases"][0]["expected"].update(id="OTHER"))
    reject(lambda c, i, b: b["next_theorem_task"].update(issue_created=True))
    reject(lambda c, i, b: b.update(general_nonmonotone_solver_claimed=True))

    def change_tail(c, i, b):
        for row in c["cases"]:
            if row["kind"] == "COMPOSITE_TAIL" and any(
                sp[0] == V43 and sp[1] == "BLOCKED"
                for sp in row["expected"]["observed"]["spans"]
            ):
                row["kind"] = "HARVESTED"
                return
        raise AssertionError("no V43 tail fixture")
    reject(change_tail)

    reject(lambda c, i, b: c["cases"][0]["expected"]["observed"].update(
        status="BLOCKED"))
    reject(lambda c, i, b: c["cases"][0]["spec"].update(
        grammar="FORGED_GRAMMAR"))
    reject(lambda c, i, b: c["cases"][0]["spec"].update(
        source_parameter_id=""))

    def swap_provenance(c, i, b):
        harvested = next(row for row in c["cases"] if row["kind"] == "HARVESTED")
        composite = next(row for row in c["cases"] if row["kind"] == "COMPOSITE_TAIL")
        harvested["kind"] = "COMPOSITE_TAIL"
        composite["kind"] = "HARVESTED"
    reject(swap_provenance)

    # Each swaps two different genuine dispositions, leaving their total
    # histogram untouched. Per-case source-shape/owner checks must reject.
    def swap_dispositions(c, left, right):
        a = next(row for row in c["cases"]
                 if row["expected"]["v54_disposition"] == left)
        b = next(row for row in c["cases"]
                 if row["expected"]["v54_disposition"] == right)
        a["expected"]["v54_disposition"], b["expected"]["v54_disposition"] = (
            b["expected"]["v54_disposition"], a["expected"]["v54_disposition"])

    finite = "FINITE_OWNER_SOURCE_EVIDENCE_CERTIFIED"
    reject(lambda c, i, b: swap_dispositions(c, "CERTIFIED", finite))
    reject(lambda c, i, b: swap_dispositions(
        c, "MIXED_OWNER_SOURCE_EVIDENCE_CERTIFIED", finite))
    reject(lambda c, i, b: swap_dispositions(
        c, "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE", finite))

    # Aggregate-neutral source-provenance corruption controls.
    def duplicate_source_spec(c, i, b):
        c["cases"][1]["spec"] = copy.deepcopy(c["cases"][0]["spec"])
    reject(duplicate_source_spec)
    reject(lambda c, i, b: c["cases"][0].update(origin="FORGED_ORIGIN"))
    def relabel_composite_owner(c, i, b):
        row = next(x for x in c["cases"] if x["kind"] == "COMPOSITE_TAIL")
        suffix = row["id"].rsplit(":", 1)[-1]
        row["id"] = "composite:FORGED_OWNER:" + suffix
        row["expected"]["id"] = row["id"]
    reject(relabel_composite_owner)

    def duplicate_only_by_ignored_annotation(c, i, b):
        c["cases"][1]["spec"] = copy.deepcopy(c["cases"][0]["spec"])
        c["cases"][1]["spec"]["parameter_projection"] = "FORGED_IGNORED_ANNOTATION"
    reject(duplicate_only_by_ignored_annotation)

    def break_tail100_ramp(c, i, b):
        row = next(x for x in c["cases"]
                   if x["kind"] == "COMPOSITE_TAIL" and
                   x["id"].endswith(":tail100"))
        c0 = row["spec"]["cos_splines"]["0"]
        width = c0["degree"] + 1
        c0["controls"][-1] = c0["controls"][width]
    reject(break_tail100_ramp)

    def break_constant_tail(c, i, b):
        row = next(x for x in c["cases"]
                   if x["kind"] == "COMPOSITE_TAIL" and
                   any((trig != "cos" or h != "0")
                       for trig, splines in (("cos", x["spec"]["cos_splines"]),
                                             ("sin", x["spec"]["sin_splines"]))
                       for h in splines))
        for trig, splines in (("cos", row["spec"]["cos_splines"]),
                              ("sin", row["spec"]["sin_splines"])):
            for h, bs in splines.items():
                if trig == "cos" and h == "0":
                    continue
                bs["controls"][-1] = "999"
                return
        raise AssertionError("no nonzero-harmonic composite tail")
    reject(break_constant_tail)

    def break_midpoint_clamp(c, i, b):
        row = next(x for x in c["cases"] if x["kind"] == "COMPOSITE_TAIL")
        bs = next(iter(row["spec"]["cos_splines"].values()))
        width = bs["degree"] + 1
        bs["knots"][width] = row["spec"]["parameter_lo"]
    reject(break_midpoint_clamp)

    # The rejection helper must not silently count an exception from the
    # mutation helper itself as a mathematically relevant audit refusal.
    def defective_setup(c, i, b):
        raise AssertionError("intentional mutation setup error")
    try:
        reject(defective_setup)
    except AssertionError as exc:
        require(str(exc) == "intentional mutation setup error",
                "the test harness masked a mutation setup failure")
    else:
        raise AssertionError("the test harness swallowed a mutation setup failure")
    print("PB-007-01 post-v54 adversarial census: PASS "
          "(21 negative controls; mutation setup errors propagate)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("select --contract and/or --self-test")
    data = inputs()
    result = audit(*data)
    if args.contract:
        print("PB-007-01 post-v54 pinned frontier census: PASS")
        print(json.dumps(result, sort_keys=True))
    if args.self_test:
        self_test(*data)


if __name__ == "__main__":
    main()
