#!/usr/bin/env python3
"""RCS-022 independent STEP Layer-D qualification campaign.

This runner is deliberately fail-closed.  A green harness run can still produce
``interoperability_unqualified``; only measured success in both independent
STEPcode parsing and the independent vcad B-rep consumer yields ``qualified``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "research/rcs-022/profile-v1.json"
FIXTURES_PATH = ROOT / "research/rcs-022/fixtures-v1.json"
SCHEMA_RE = re.compile(r"FILE_SCHEMA\s*\(\s*\((.*?)\)\s*\)\s*;", re.I | re.S)
QUOTED_RE = re.compile(r"'([^']+)'", re.S)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(cmd: list[str], *, allow_fail: bool = False) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(cmd, text=True, capture_output=True)
    if cp.returncode and not allow_fail:
        raise RuntimeError(
            f"command failed ({cp.returncode}): {' '.join(cmd)}\nstdout:\n{cp.stdout}\nstderr:\n{cp.stderr}"
        )
    return cp


def step_schema(text: str) -> str | None:
    m = SCHEMA_RE.search(text)
    if not m:
        return None
    q = QUOTED_RE.search(m.group(1))
    return q.group(1) if q else None


def declared_unit(text: str) -> str:
    upper = text.upper()
    # OCCT metric files use SI_UNIT(.MILLI.,.METRE.).  A deliberately altered
    # SI metre declaration is a scale error, not silently normalized here.
    if "SI_UNIT(.MILLI.,.METRE.)" in upper:
        return "mm"
    if "SI_UNIT($,.METRE.)" in upper or "SI_UNIT(*,.METRE.)" in upper:
        return "m"
    if "'INCH'" in upper or "INCH" in upper and "CONVERSION_BASED_UNIT" in upper:
        return "inch"
    return "unknown"


def close(a: float, b: float, abs_tol: float, rel_tol: float = 0.0) -> bool:
    return abs(a - b) <= max(abs_tol, rel_tol * max(abs(a), abs(b), 1.0))


def geometry_code(expected: dict[str, Any], measured: dict[str, Any], tol: dict[str, Any]) -> str | None:
    if int(measured.get("body_count", -1)) != int(expected["body_count"]):
        return "BODY_COUNT_MISMATCH"
    eb = expected.get("bbox_mm")
    mb = measured.get("bbox_mm")
    if not isinstance(mb, list) or len(mb) != 6 or any(
        not close(float(a), float(b), float(tol["bbox_mm"])) for a, b in zip(eb, mb)
    ):
        return "GEOMETRIC_DEVIATION_EXCEEDED"
    ev = expected.get("volume_mm3")
    mv = measured.get("volume_mm3")
    if ev is not None and (mv is None or not close(float(ev), float(mv), 0.0, float(tol["volume_relative"]))):
        return "GEOMETRIC_DEVIATION_EXCEEDED"
    return None


def analytic_code(expected: dict[str, Any], source: dict[str, Any], step_text: str) -> str | None:
    faces = source.get("analytic_faces", {})
    token = {"plane": "PLANE(", "cylinder": "CYLINDRICAL_SURFACE(", "cone": "CONICAL_SURFACE("}
    upper = step_text.upper()
    for kind, minimum in expected.get("analytic_min", {}).items():
        if int(faces.get(kind, 0)) < int(minimum):
            return "ANALYTIC_GEOMETRY_LOST"
        if kind in token and upper.count(token[kind]) < int(minimum):
            return "ANALYTIC_GEOMETRY_LOST"
    return None


def parse_worker_json(cp: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    lines = [line for line in cp.stdout.splitlines() if line.strip().startswith("{")]
    if not lines:
        raise RuntimeError(f"worker emitted no JSON\nstdout={cp.stdout}\nstderr={cp.stderr}")
    return json.loads(lines[-1])


def parser_probe(p21read: Path, src: Path, out: Path) -> dict[str, Any]:
    cp = run([str(p21read), "-s", str(src), str(out)], allow_fail=True)
    return {
        "pass": cp.returncode == 0 and out.exists(),
        "returncode": cp.returncode,
        "stdout_tail": cp.stdout[-2000:],
        "stderr_tail": cp.stderr[-2000:],
        "roundtrip_sha256": sha256(out) if out.exists() else None,
    }


def vcad_probe(vcad: Path, src: Path) -> dict[str, Any]:
    cp = run([str(vcad), str(src)], allow_fail=True)
    payload: dict[str, Any] | None = None
    if cp.returncode == 0:
        try:
            payload = json.loads(cp.stdout.splitlines()[-1])
        except Exception:
            payload = None
    return {
        "pass": cp.returncode == 0 and payload is not None,
        "returncode": cp.returncode,
        "metrics": payload,
        "stdout_tail": cp.stdout[-2000:],
        "stderr_tail": cp.stderr[-2000:],
    }


def mutate_metric_to_metre(src: Path, dst: Path) -> bool:
    text = src.read_text(errors="strict")
    changed = re.sub(r"SI_UNIT\(\.MILLI\.,\.METRE\.\)", "SI_UNIT($,.METRE.)", text, count=1, flags=re.I)
    if changed == text:
        return False
    dst.write_text(changed)
    return True


def adversarial_self_tests() -> list[dict[str, Any]]:
    tol = {"bbox_mm": 0.02, "volume_relative": 0.005}
    base = {"body_count": 2, "bbox_mm": [0, 0, 0, 40, 30, 10], "volume_mm3": 11400.0}
    tests: list[tuple[str, str, dict[str, Any], dict[str, Any]]] = [
        ("omitted_body_boundary", "BODY_COUNT_MISMATCH", base, {**base, "body_count": 1}),
        ("bbox_just_inside", "PASS", base, {**base, "bbox_mm": [0,0,0,40.019,30,10]}),
        ("bbox_just_outside", "GEOMETRIC_DEVIATION_EXCEEDED", base, {**base, "bbox_mm": [0,0,0,40.021,30,10]}),
        ("volume_just_inside", "PASS", base, {**base, "volume_mm3": 11400.0 * 1.0049}),
        ("volume_just_outside", "GEOMETRIC_DEVIATION_EXCEEDED", base, {**base, "volume_mm3": 11400.0 * 1.0051}),
    ]
    out = []
    for name, expected_code, expected, measured in tests:
        observed = geometry_code(expected, measured, tol) or "PASS"
        out.append({"name": name, "expected_code": expected_code, "observed_code": observed, "pass": observed == expected_code})
    # Unit and analytic gates are tested without depending on any exporter syntax accident.
    out.append({"name":"wrong_unit_contract","expected_code":"UNIT_OR_SCALE_MISMATCH","observed_code":"UNIT_OR_SCALE_MISMATCH","pass":declared_unit("#1=SI_UNIT($,.METRE.);") == "m"})
    fake_source = {"analytic_faces":{"plane":2,"cylinder":0}}
    observed = analytic_code({"analytic_min":{"cylinder":1}}, fake_source, "#1=PLANE('');") or "PASS"
    out.append({"name":"analytic_degradation","expected_code":"ANALYTIC_GEOMETRY_LOST","observed_code":observed,"pass":observed=="ANALYTIC_GEOMETRY_LOST"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=Path, required=True)
    ap.add_argument("--p21read", type=Path, required=True)
    ap.add_argument("--vcad-probe", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ns = ap.parse_args()

    profile = json.loads(PROFILE_PATH.read_text())
    fixtures = json.loads(FIXTURES_PATH.read_text())
    out_dir = ns.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    steps = out_dir / "steps"
    parsed = out_dir / "stepcode-roundtrip"
    steps.mkdir(exist_ok=True)
    parsed.mkdir(exist_ok=True)

    results: dict[str, Any] = {
        "profile_id": profile["id"],
        "profile_sha256": hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest(),
        "fixtures_sha256": hashlib.sha256(FIXTURES_PATH.read_bytes()).hexdigest(),
        "fixtures": [],
        "negatives": adversarial_self_tests(),
        "blockers": [],
        "versions": {
            "occt": profile["exporter"]["commit"],
            "stepcode": profile["layer_d"]["schema_parser"]["commit"],
            "vcad": profile["layer_d"]["solid_consumer"]["commit"],
        },
    }

    source_by_id: dict[str, dict[str, Any]] = {}
    for spec in fixtures["positive"]:
        fid = spec["id"]
        step = steps / f"{fid}.step"
        cp = run([str(ns.worker), "export", fid, str(step)], allow_fail=True)
        entry: dict[str, Any] = {"id": fid, "export_returncode": cp.returncode}
        if cp.returncode != 0 or not step.exists():
            entry["pass"] = False
            entry["error"] = "export_failed"
            entry["stderr_tail"] = cp.stderr[-2000:]
            results["fixtures"].append(entry)
            results["blockers"].append(f"{fid}: exporter failed")
            continue
        source = parse_worker_json(cp)
        source_by_id[fid] = source
        text = step.read_text(errors="strict")
        schema = step_schema(text)
        unit = declared_unit(text)
        p21 = parser_probe(ns.p21read, step, parsed / f"{fid}.step")
        consumer = vcad_probe(ns.vcad_probe, step)
        errors: list[str] = []

        if not schema:
            errors.append("SCHEMA_PROFILE_MISMATCH")
        if not p21["pass"]:
            errors.append("INDEPENDENT_PARSE_FAILED")
        expected_unit = spec.get("export_unit", "mm")
        # Inch syntax varies by protocol; the consumer geometry below is the
        # authoritative physical-unit check. Metric declarations are explicit.
        if expected_unit == "mm" and unit != "mm":
            errors.append("UNIT_OR_SCALE_MISMATCH")
        if analytic_code(spec, source["metrics"], text):
            errors.append("ANALYTIC_GEOMETRY_LOST")
        if consumer["pass"]:
            gcode = geometry_code(spec, consumer["metrics"], profile["tolerances"])
            if gcode:
                errors.append(gcode)
        else:
            errors.append("DOWNSTREAM_CONSUMER_FAILURE")

        if spec.get("require_pre_post_measurement"):
            pre = source.get("pre_heal_metrics")
            post = source.get("metrics")
            if not pre or int(pre["body_count"]) != int(post["body_count"]):
                errors.append("BODY_COUNT_MISMATCH")
            elif not close(float(pre["volume_mm3"]), float(post["volume_mm3"]), 0.0, float(profile["tolerances"]["heal_volume_relative"])):
                errors.append("GEOMETRIC_DEVIATION_EXCEEDED")

        entry.update({
            "sha256": sha256(step),
            "bytes": step.stat().st_size,
            "schema": schema,
            "declared_unit_probe": unit,
            "source": source,
            "stepcode": p21,
            "consumer": consumer,
            "errors": sorted(set(errors)),
            "pass": not errors,
        })
        results["fixtures"].append(entry)
        if errors:
            results["blockers"].append(f"{fid}: {','.join(sorted(set(errors)))}")

    # File-level adversarial cases.  These must prove the gates catch real
    # wrong artifacts rather than merely exercise helper functions.
    metric_step = steps / "metric_block.step"
    if metric_step.exists():
        wrong = steps / "NEG_wrong_unit.step"
        if mutate_metric_to_metre(metric_step, wrong):
            observed = "UNIT_OR_SCALE_MISMATCH" if declared_unit(wrong.read_text()) != "mm" else "PASS"
            results["negatives"].append({"name":"wrong_unit_file","expected_code":"UNIT_OR_SCALE_MISMATCH","observed_code":observed,"pass":observed=="UNIT_OR_SCALE_MISMATCH","sha256":sha256(wrong)})
        else:
            results["negatives"].append({"name":"wrong_unit_file","expected_code":"UNIT_OR_SCALE_MISMATCH","observed_code":"MUTATION_NOT_APPLICABLE","pass":False})

        truncated = steps / "NEG_truncated.step"
        data = metric_step.read_bytes()
        truncated.write_bytes(data[: max(1, len(data)//3)])
        p = parser_probe(ns.p21read, truncated, parsed / "NEG_truncated.step")
        observed = "INDEPENDENT_PARSE_FAILED" if not p["pass"] else "PASS"
        results["negatives"].append({"name":"truncated_parser","expected_code":"INDEPENDENT_PARSE_FAILED","observed_code":observed,"pass":observed=="INDEPENDENT_PARSE_FAILED"})
        v = vcad_probe(ns.vcad_probe, truncated)
        observed = "DOWNSTREAM_CONSUMER_FAILURE" if not v["pass"] else "PASS"
        results["negatives"].append({"name":"truncated_consumer","expected_code":"DOWNSTREAM_CONSUMER_FAILURE","observed_code":observed,"pass":observed=="DOWNSTREAM_CONSUMER_FAILURE"})

    # Omitted-body export is a real valid STEP artifact and must be rejected by
    # expected-body comparison, not by parser failure.
    omitted = steps / "NEG_omitted_body.step"
    cp = run([str(ns.worker), "export", "accepted_mill", str(omitted), "--omit-last-body"], allow_fail=True)
    if cp.returncode == 0 and omitted.exists():
        v = vcad_probe(ns.vcad_probe, omitted)
        expected = next(x for x in fixtures["positive"] if x["id"] == "accepted_mill")
        observed = geometry_code(expected, v["metrics"], profile["tolerances"]) if v["pass"] else "DOWNSTREAM_CONSUMER_FAILURE"
        results["negatives"].append({"name":"omitted_body_file","expected_code":"BODY_COUNT_MISMATCH","observed_code":observed,"pass":observed=="BODY_COUNT_MISMATCH","sha256":sha256(omitted)})
    else:
        results["negatives"].append({"name":"omitted_body_file","expected_code":"BODY_COUNT_MISMATCH","observed_code":"EXPORT_FAILED","pass":False})

    # A shell is deliberately refused before export: no mesh/open substitute is
    # allowed to masquerade as STEP solid output.
    shell = steps / "NEG_open_shell.step"
    cp = run([str(ns.worker), "export", "open_shell", str(shell)], allow_fail=True)
    observed = "VOID_OR_CONNECTIVITY_MISMATCH" if cp.returncode == 20 and "VOID_OR_CONNECTIVITY_MISMATCH" in cp.stderr else "PASS"
    results["negatives"].append({"name":"open_non_solid_refusal","expected_code":"VOID_OR_CONNECTIVITY_MISMATCH","observed_code":observed,"pass":observed=="VOID_OR_CONNECTIVITY_MISMATCH"})

    negative_codes = {n["expected_code"] for n in results["negatives"] if n.get("pass")}
    required_codes = set(fixtures["negative_required_codes"])
    all_negatives = all(n.get("pass") for n in results["negatives"]) and required_codes <= negative_codes
    all_positive = len(results["fixtures"]) == len(fixtures["positive"]) and all(x.get("pass") for x in results["fixtures"])
    results["negative_coverage"] = {"required": sorted(required_codes), "observed": sorted(negative_codes), "pass": all_negatives}
    results["verdict"] = "qualified" if all_positive and all_negatives else "interoperability_unqualified"
    results["campaign_integrity"] = "pass" if all_negatives and len(results["fixtures"]) == len(fixtures["positive"]) else "fail"

    result_path = out_dir / "qualification-results.json"
    result_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": results["verdict"], "campaign_integrity": results["campaign_integrity"], "blockers": results["blockers"]}, indent=2))
    # A qualified campaign requires everything.  An unqualified campaign is a
    # valid research result only if the campaign itself completed and every
    # adversarial gate worked; CI must not turn an interoperability failure into
    # a false pass by skipping tests.
    return 0 if results["campaign_integrity"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
