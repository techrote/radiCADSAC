#!/usr/bin/env python3
from __future__ import annotations

import argparse, copy, hashlib, json
from pathlib import Path
from typing import Any

SCHEMA = {
    "fixture": "radicadsac-mc-fixture/1.0",
    "result": "radicadsac-mc-result/1.0",
    "outcome": "radicadsac-mc-task-outcome/1.0",
    "claim": "radicadsac-mc-claim/1.0",
    "verdict": "radicadsac-mc-programme-verdict/1.0",
}
FAMILIES = {f"F{i:02d}" for i in range(1, 17)}
SCOPES = {"MANDATORY_FAMILY", "INDEPENDENT_CONTROL", "HISTORICAL_IMPORT"}
STAGES = ("material", "topology", "reconstruction", "step_a", "step_b", "step_c", "step_d")
STAGE_STATES = {"PASS", "FAIL", "INCONCLUSIVE", "NOT_EXECUTED"}
TERMINALS = {"SUCCEEDED", "TIMEOUT", "RESOURCE_EXHAUSTED", "REJECTED", "ERROR", "CRASH", "NOT_EXECUTED"}
RESULT_KINDS = {"COMPLETED_RESEARCH", "NEGATIVE_RESULT", "BLOCKED", "CAPABILITY_ACCEPTED"}
CLAIM_STATES = {"OPEN", "REFUTED", "REVIEWED", "ACCEPTED"}
EXPECTED = {"VALID_NONEMPTY", "VALID_EMPTY", "INVALID_CONTROL"}
AUTHORITY = "MC-1-programme"
PREFIX = "sha256:"
FORBIDDEN_VERDICTS = {"programme_verdict", "final_verdict", "gate_verdict", "capability_verdict"}

class EvidenceError(ValueError):
    pass

def fail(msg: str) -> None:
    raise EvidenceError(msg)

def obj(v: Any, where: str) -> dict:
    if not isinstance(v, dict): fail(f"{where} must be an object")
    return v

def arr(v: Any, where: str) -> list:
    if not isinstance(v, list): fail(f"{where} must be an array")
    return v

def text(v: Any, where: str) -> str:
    if not isinstance(v, str) or not v: fail(f"{where} must be a non-empty string")
    return v

def boolean(v: Any, where: str) -> bool:
    if not isinstance(v, bool): fail(f"{where} must be boolean")
    return v

def safe(v: Any, where: str = "root") -> None:
    if isinstance(v, float): fail(f"binary float forbidden at {where}")
    if v is None or isinstance(v, (str, bool, int)): return
    if isinstance(v, list):
        for i, x in enumerate(v): safe(x, f"{where}[{i}]")
        return
    if isinstance(v, dict):
        for k, x in v.items():
            if not isinstance(k, str): fail(f"non-string key at {where}")
            safe(x, f"{where}.{k}")
        return
    fail(f"unsupported binding value at {where}")

def canonical_bytes(v: Any) -> bytes:
    safe(v)
    return json.dumps(v, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode()

def object_digest(v: Any) -> str:
    return PREFIX + hashlib.sha256(canonical_bytes(v)).hexdigest()

def digest(v: Any, where: str) -> str:
    if not isinstance(v, str) or len(v) != 71 or not v.startswith(PREFIX) or any(c not in "0123456789abcdef" for c in v[7:]):
        fail(f"{where} must be lower-case sha256:<64-hex>")
    return v

def schema(o: dict, kind: str) -> None:
    if o.get("schema") != SCHEMA[kind]: fail(f"{kind} schema/version mismatch")

def string_array(v: Any, where: str, *, nonempty: bool = False) -> list:
    xs = arr(v, where)
    if nonempty and not xs: fail(f"{where} must not be empty")
    if any(not isinstance(x, str) or not x for x in xs): fail(f"{where} must contain non-empty strings")
    return xs

def validate_fixture(f: dict) -> None:
    f = obj(f, "fixture"); schema(f, "fixture"); safe(f)
    text(f.get("fixture_id"), "fixture.fixture_id")
    if not isinstance(f.get("fixture_version"), int) or isinstance(f.get("fixture_version"), bool) or f["fixture_version"] <= 0: fail("fixture version invalid")
    if f.get("fixture_scope") not in SCOPES: fail("fixture scope invalid")
    fam = f.get("family")
    if f["fixture_scope"] == "MANDATORY_FAMILY" and fam not in FAMILIES: fail("mandatory family must be F01..F16")
    if f["fixture_scope"] != "MANDATORY_FAMILY" and fam is not None and fam not in FAMILIES: fail("control/import family must be null or F01..F16")
    d = obj(f.get("domain"), "fixture.domain"); text(d.get("id"), "fixture.domain.id"); digest(d.get("digest"), "fixture.domain.digest")
    ins = obj(f.get("inputs"), "fixture.inputs")
    if set(ins) != {"stock", "tool", "setup", "history"}: fail("fixture inputs must be stock/tool/setup/history")
    for k, v in ins.items(): digest(v, f"fixture.inputs.{k}")
    w = obj(f.get("physical_witness"), "fixture.physical_witness"); a = text(w.get("authority"), "physical witness authority")
    if a.startswith("candidate:"): fail("candidate cannot be physical witness authority")
    if w.get("disposition") not in {"PHYSICALLY_VALID", "INVALID_CONTROL"}: fail("physical witness disposition invalid")
    digest(w.get("digest"), "physical witness digest")
    p = obj(f.get("exact_parameters"), "fixture.exact_parameters"); text(p.get("encoding"), "exact parameter encoding"); digest(p.get("digest"), "exact parameter digest")
    string_array(f.get("coverage"), "fixture.coverage", nonempty=True)
    r = obj(f.get("request"), "fixture.request"); text(r.get("profile_id"), "profile id"); digest(r.get("profile_digest"), "profile digest")
    accuracy = obj(r.get("accuracy"), "fixture.request.accuracy")
    if not accuracy or r.get("accuracy_digest") != object_digest(accuracy): fail("accuracy digest mismatch")
    req = string_array(f.get("required_stages"), "fixture.required_stages", nonempty=True)
    if len(req) != len(set(req)) or any(x not in STAGES for x in req): fail("required stage inventory invalid")
    string_array(f.get("topology_requirements"), "topology requirements"); string_array(f.get("analytic_requirements"), "analytic requirements")
    oracle = obj(f.get("oracle"), "fixture.oracle"); text(oracle.get("identity"), "oracle identity"); digest(oracle.get("derivation_digest"), "oracle digest")
    if boolean(oracle.get("independent_from_candidate"), "oracle independence") is not True: fail("oracle must be independent from candidate")
    string_array(oracle.get("shared_decisive_components"), "oracle shared components")
    g = obj(f.get("generator"), "fixture.generator"); text(g.get("identity"), "generator identity"); digest(g.get("source_digest"), "generator source")
    if boolean(g.get("candidate_blind"), "generator candidate_blind") is not True: fail("generator must be candidate-blind")
    if g.get("seed_commitment") is not None: digest(g["seed_commitment"], "seed commitment")
    e = obj(f.get("expected"), "fixture.expected")
    if e.get("class") not in EXPECTED: fail("expected class invalid")
    if text(e.get("authority"), "expected authority").startswith("candidate:"): fail("candidate cannot define expected result")
    if e.get("digest") is not None: digest(e["digest"], "expected digest")

def validate_result(r: dict) -> None:
    r = obj(r, "result"); schema(r, "result"); safe(r)
    if FORBIDDEN_VERDICTS & set(r): fail("result may not contain programme/final/gate/capability verdict")
    text(r.get("attempt_id"), "attempt id")
    f = obj(r.get("fixture"), "result.fixture"); text(f.get("id"), "result fixture id")
    if not isinstance(f.get("version"), int) or isinstance(f.get("version"), bool) or f["version"] <= 0: fail("result fixture version invalid")
    digest(f.get("digest"), "result fixture digest"); digest(r.get("domain_digest"), "result domain digest")
    p = obj(r.get("profile"), "result.profile"); text(p.get("id"), "profile id"); digest(p.get("digest"), "profile digest"); digest(r.get("accuracy_digest"), "accuracy digest")
    ins = obj(r.get("input_digests"), "result.input_digests")
    if set(ins) != {"stock", "tool", "setup", "history"}: fail("result input digest inventory invalid")
    for k, v in ins.items(): digest(v, f"result input {k}")
    c = obj(r.get("candidate"), "result.candidate"); text(c.get("identity"), "candidate identity"); digest(c.get("source_digest"), "candidate source"); digest(c.get("config_digest"), "candidate config")
    if "self_verdict" in c or "programme_verdict" in c: fail("candidate self-verdict forbidden")
    checker = obj(r.get("checker"), "result.checker"); text(checker.get("identity"), "checker identity"); digest(checker.get("digest"), "checker digest")
    if checker["identity"] == c["identity"]: fail("candidate cannot be programme binding checker")
    if r.get("terminal_reason") not in TERMINALS: fail("terminal reason invalid")
    stages = obj(r.get("stages"), "result.stages")
    if set(stages) != set(STAGES): fail("all seven stages must be explicit")
    for stage in STAGES:
        rec = obj(stages[stage], f"stage {stage}")
        if rec.get("state") not in STAGE_STATES: fail(f"stage {stage} state invalid")
        if rec.get("evidence_digest") is not None: digest(rec["evidence_digest"], f"stage {stage} evidence")
    boolean(r.get("bounds_validated"), "bounds_validated")
    if r.get("exported_file_digest") is not None: digest(r["exported_file_digest"], "exported file")

def validate_claim(c: dict) -> None:
    c = obj(c, "claim"); schema(c, "claim"); safe(c)
    text(c.get("claim_id"), "claim id"); text(c.get("owner_task"), "claim owner"); text(c.get("statement"), "claim statement")
    if not isinstance(c.get("claim_version"), int) or isinstance(c.get("claim_version"), bool) or c["claim_version"] <= 0: fail("claim version invalid")
    if c.get("state") not in CLAIM_STATES: fail("claim state invalid")
    authority = text(c.get("authority"), "claim authority"); refs = arr(c.get("evidence_refs"), "claim evidence_refs")
    if c["state"] == "ACCEPTED" and (authority != AUTHORITY or not refs): fail("accepted claim requires programme authority and evidence")
    for i, ref in enumerate(refs):
        ref = obj(ref, f"claim evidence {i}"); text(ref.get("kind"), "evidence kind"); text(ref.get("identity"), "evidence identity"); digest(ref.get("digest"), "evidence digest")

def validate_outcome(o: dict) -> None:
    o = obj(o, "outcome"); schema(o, "outcome"); safe(o)
    task = text(o.get("task"), "outcome task")
    if len(task) != 6 or not task.startswith("MC-") or not task[3:].isdigit(): fail("outcome task must be MC-NNN")
    if o.get("result_kind") not in RESULT_KINDS: fail("outcome result kind invalid")
    string_array(o.get("evidence_class"), "outcome evidence class", nonempty=True); text(o.get("source_baseline"), "outcome source baseline")
    if not isinstance(o.get("issue"), int) or isinstance(o.get("issue"), bool) or o["issue"] <= 0: fail("outcome issue invalid")
    for k in ("accepted_claims", "open_claims", "artifacts", "verification"): string_array(o.get(k), f"outcome {k}")
    boolean(o.get("native_execution"), "outcome native_execution")

def validate_verdict(v: dict) -> None:
    v = obj(v, "verdict"); schema(v, "verdict"); safe(v)
    if v.get("authority") != AUTHORITY: fail("programme verdict authority mismatch")
    text(v.get("verdict_id"), "verdict id"); digest(v.get("fixture_digest"), "verdict fixture"); digest(v.get("result_digest"), "verdict result")
    e = obj(v.get("expected"), "verdict.expected")
    keys = {"domain_digest", "profile_id", "profile_digest", "accuracy_digest", "candidate_identity", "candidate_source_digest", "candidate_config_digest", "checker_identity", "checker_digest"}
    if not keys <= set(e): fail("verdict expected bindings incomplete")
    for k in ("profile_id", "candidate_identity", "checker_identity"): text(e.get(k), f"verdict {k}")
    for k in keys - {"profile_id", "candidate_identity", "checker_identity"}: digest(e.get(k), f"verdict {k}")
    if e.get("exported_file_digest") is not None: digest(e["exported_file_digest"], "verdict exported file")
    if v.get("decision") not in {"PASS", "FAIL", "INCOMPLETE", "INVALID"}: fail("verdict decision invalid")
    string_array(v.get("reason_codes"), "verdict reason codes")

def expected_decision(f: dict, r: dict) -> tuple[str, list[str]]:
    reasons = []
    if r["terminal_reason"] != "SUCCEEDED": reasons.append("TERMINAL_NOT_SUCCEEDED")
    if r["bounds_validated"] is not True: reasons.append("BOUNDS_UNVALIDATED")
    for stage in f["required_stages"]:
        state = r["stages"][stage]["state"]
        if state != "PASS": reasons.append(f"REQUIRED_STAGE_{stage.upper()}_{state}")
    return ("INCOMPLETE", reasons) if reasons else ("PASS", ["ALL_REQUIRED_BINDINGS_AND_STAGES_PASS"])

def verify_bundle(f: dict, r: dict, v: dict, *, claim: dict | None = None, outcome: dict | None = None) -> None:
    validate_fixture(f); validate_result(r); validate_verdict(v)
    if claim is not None: validate_claim(claim)
    if outcome is not None: validate_outcome(outcome)
    fd, rd = object_digest(f), object_digest(r)
    if r["fixture"] != {"id": f["fixture_id"], "version": f["fixture_version"], "digest": fd}: fail("result fixture binding mismatch")
    if v["fixture_digest"] != fd or v["result_digest"] != rd: fail("verdict object hash mismatch")
    if r["domain_digest"] != f["domain"]["digest"]: fail("result domain mismatch")
    for k in ("stock", "tool", "setup", "history"):
        if r["input_digests"][k] != f["inputs"][k]: fail(f"result input mismatch: {k}")
    if r["profile"]["id"] != f["request"]["profile_id"] or r["profile"]["digest"] != f["request"]["profile_digest"]: fail("stale/mismatched profile")
    if r["accuracy_digest"] != f["request"]["accuracy_digest"]: fail("altered/mismatched accuracy")
    expected = {
        "domain_digest": r["domain_digest"], "profile_id": r["profile"]["id"], "profile_digest": r["profile"]["digest"], "accuracy_digest": r["accuracy_digest"],
        "candidate_identity": r["candidate"]["identity"], "candidate_source_digest": r["candidate"]["source_digest"], "candidate_config_digest": r["candidate"]["config_digest"],
        "checker_identity": r["checker"]["identity"], "checker_digest": r["checker"]["digest"],
    }
    for k, actual in expected.items():
        if v["expected"].get(k) != actual: fail(f"verdict expected binding mismatch: {k}")
    if v["expected"].get("exported_file_digest") is not None and v["expected"]["exported_file_digest"] != r.get("exported_file_digest"): fail("exported-file mismatch")
    decision, reasons = expected_decision(f, r)
    if v["decision"] != decision or sorted(v["reason_codes"]) != sorted(reasons): fail("programme verdict not derivable from bound result")

def _d(label: str) -> str:
    return PREFIX + hashlib.sha256(label.encode()).hexdigest()

def sample() -> tuple[dict, dict, dict, dict, dict]:
    accuracy = {"boundary_hausdorff_um":"5","dimensional_um":"5","angular_urad":"5","relative_volume":"1/1000000","topology":"exact-required","body_identity":"exact-required"}
    f = {"schema":SCHEMA["fixture"],"fixture_id":"MC009-F02-CONTROL","fixture_version":1,"fixture_scope":"MANDATORY_FAMILY","family":"F02","domain":{"id":"mc-domain/1.0","digest":_d("domain")},"inputs":{"stock":_d("stock"),"tool":_d("tool"),"setup":_d("setup"),"history":_d("history")},"physical_witness":{"authority":"programme:physical-witness","disposition":"PHYSICALLY_VALID","digest":_d("physical")},"exact_parameters":{"encoding":"mc-exact-source/1.0","digest":_d("params")},"coverage":["thin-web","exact-zero"],"request":{"profile_id":"MC-Q-ENGINEERING","profile_digest":_d("profile"),"accuracy":accuracy,"accuracy_digest":object_digest(accuracy)},"topology_requirements":["retain positive-volume web"],"analytic_requirements":[],"required_stages":list(STAGES),"oracle":{"identity":"mc009-control-oracle","derivation_digest":_d("oracle"),"independent_from_candidate":True,"shared_decisive_components":[]},"generator":{"identity":"mc009-fixed-control","source_digest":_d("generator"),"candidate_blind":True,"seed_commitment":_d("seed")},"expected":{"class":"VALID_NONEMPTY","authority":"programme:independent-control","digest":_d("expected")}}
    r = {"schema":SCHEMA["result"],"attempt_id":"attempt-001","fixture":{"id":f["fixture_id"],"version":1,"digest":object_digest(f)},"domain_digest":f["domain"]["digest"],"profile":{"id":f["request"]["profile_id"],"digest":f["request"]["profile_digest"]},"accuracy_digest":f["request"]["accuracy_digest"],"input_digests":dict(f["inputs"]),"candidate":{"identity":"candidate:synthetic","source_digest":_d("candidate-source"),"config_digest":_d("candidate-config")},"checker":{"identity":"programme:mc-evidence-verifier/1.0","digest":_d("checker")},"terminal_reason":"SUCCEEDED","stages":{s:{"state":"PASS","evidence_digest":_d("stage:"+s)} for s in STAGES},"bounds_validated":True,"exported_file_digest":_d("step-file")}
    v = {"schema":SCHEMA["verdict"],"verdict_id":"verdict-001","authority":AUTHORITY,"fixture_digest":object_digest(f),"result_digest":object_digest(r),"expected":{"domain_digest":r["domain_digest"],"profile_id":r["profile"]["id"],"profile_digest":r["profile"]["digest"],"accuracy_digest":r["accuracy_digest"],"candidate_identity":r["candidate"]["identity"],"candidate_source_digest":r["candidate"]["source_digest"],"candidate_config_digest":r["candidate"]["config_digest"],"checker_identity":r["checker"]["identity"],"checker_digest":r["checker"]["digest"],"exported_file_digest":r["exported_file_digest"]},"decision":"PASS","reason_codes":["ALL_REQUIRED_BINDINGS_AND_STAGES_PASS"]}
    c = {"schema":SCHEMA["claim"],"claim_id":"MC009-CONTROL-CLAIM","claim_version":1,"owner_task":"MC-009","statement":"synthetic bundle satisfies binding contract only","state":"ACCEPTED","authority":AUTHORITY,"evidence_refs":[{"kind":"bound-result","identity":r["attempt_id"],"digest":object_digest(r)}]}
    o = {"schema":SCHEMA["outcome"],"task":"MC-009","result_kind":"COMPLETED_RESEARCH","evidence_class":["MEASURED_DETERMINISTIC_MODEL"],"source_baseline":"fa93162caa6e4e16c188674b19bac7a501c5f415","issue":71,"accepted_claims":["binding verifier control"],"open_claims":["geometry remains outside verifier"],"native_execution":False,"artifacts":["tools/mc_evidence_verifier.py"],"verification":["python3 tools/mc_evidence_verifier.py --self-test"]}
    return f, r, v, c, o

def self_test() -> None:
    base = sample(); verify_bundle(base[0], base[1], base[2], claim=base[3], outcome=base[4])
    def reject(name: str, mutate) -> None:
        f,r,v,c,o = copy.deepcopy(base); mutate(f,r,v,c,o)
        try: verify_bundle(f,r,v,claim=c,outcome=o)
        except EvidenceError: return
        raise AssertionError(f"self-test failed to reject {name}")
    attacks = [
        ("fixture hash", lambda f,r,v,c,o: r["fixture"].__setitem__("digest", PREFIX+"0"*64)),
        ("history hash", lambda f,r,v,c,o: r["input_digests"].__setitem__("history", PREFIX+"1"*64)),
        ("stale profile", lambda f,r,v,c,o: r["profile"].__setitem__("digest", PREFIX+"2"*64)),
        ("altered accuracy", lambda f,r,v,c,o: f["request"]["accuracy"].__setitem__("dimensional_um","500")),
        ("missing stage", lambda f,r,v,c,o: r["stages"].pop("step_d")),
        ("candidate self-verdict", lambda f,r,v,c,o: r.__setitem__("final_verdict","PASS")),
        ("candidate verdict authority", lambda f,r,v,c,o: v.__setitem__("authority",r["candidate"]["identity"])),
        ("candidate source", lambda f,r,v,c,o: v["expected"].__setitem__("candidate_source_digest",PREFIX+"3"*64)),
        ("candidate config", lambda f,r,v,c,o: v["expected"].__setitem__("candidate_config_digest",PREFIX+"4"*64)),
        ("checker", lambda f,r,v,c,o: v["expected"].__setitem__("checker_digest",PREFIX+"5"*64)),
        ("exported file", lambda f,r,v,c,o: v["expected"].__setitem__("exported_file_digest",PREFIX+"6"*64)),
        ("candidate physical witness", lambda f,r,v,c,o: f["physical_witness"].__setitem__("authority",r["candidate"]["identity"])),
        ("oracle independence", lambda f,r,v,c,o: f["oracle"].__setitem__("independent_from_candidate",False)),
        ("candidate expected truth", lambda f,r,v,c,o: f["expected"].__setitem__("authority",r["candidate"]["identity"])),
        ("binary float", lambda f,r,v,c,o: f["request"]["accuracy"].__setitem__("dimensional_um",5.0)),
        ("accepted claim without evidence", lambda f,r,v,c,o: c.__setitem__("evidence_refs",[])),
        ("candidate accepted claim", lambda f,r,v,c,o: c.__setitem__("authority",r["candidate"]["identity"])),
    ]
    for name, mutate in attacks: reject(name, mutate)
    f,r,v,c,o = copy.deepcopy(base); r["terminal_reason"]="TIMEOUT"; v["result_digest"]=object_digest(r); v["decision"]="INCOMPLETE"; v["reason_codes"]=["TERMINAL_NOT_SUCCEEDED"]; verify_bundle(f,r,v,claim=c,outcome=o)
    f,r,v,c,o = copy.deepcopy(base); f["expected"]["class"]="VALID_EMPTY"; f["expected"]["digest"]=object_digest({"empty":True}); r["fixture"]["digest"]=object_digest(f); v["fixture_digest"]=object_digest(f); v["result_digest"]=object_digest(r); verify_bundle(f,r,v,claim=c,outcome=o)
    f,r,v,c,o = copy.deepcopy(base); f["fixture_scope"]="INDEPENDENT_CONTROL"; f["family"]=None; r["fixture"]["digest"]=object_digest(f); v["fixture_digest"]=object_digest(f); v["result_digest"]=object_digest(r); verify_bundle(f,r,v,claim=c,outcome=o)
    print("MC evidence verifier self-test passed")

def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main() -> int:
    ap = argparse.ArgumentParser(description="MC-1 evidence binding verifier")
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--fixture"); ap.add_argument("--result"); ap.add_argument("--verdict"); ap.add_argument("--claim"); ap.add_argument("--outcome")
    a = ap.parse_args()
    if a.self_test: self_test(); return 0
    if not (a.fixture and a.result and a.verdict): ap.error("--fixture, --result and --verdict required unless --self-test")
    verify_bundle(load(a.fixture), load(a.result), load(a.verdict), claim=load(a.claim) if a.claim else None, outcome=load(a.outcome) if a.outcome else None)
    print("MC evidence bundle verification passed"); return 0

if __name__ == "__main__":
    raise SystemExit(main())
