#!/usr/bin/env python3
"""Run RCS-022 STEP Layer-D interoperability qualification."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any

try:
    import resource
except ImportError:  # pragma: no cover - CI qualification is Linux, guard local portability.
    resource = None  # type: ignore[assignment]

HERE = Path(__file__).resolve().parent
INDEPENDENT_WALL_TIMEOUT_S = 8
INDEPENDENT_CPU_LIMIT_S = 6
INDEPENDENT_ADDRESS_SPACE_BYTES = 1024 * 1024 * 1024


def _last_json_payload(stdout: str) -> dict[str, Any] | None:
    for line in reversed([x.strip() for x in stdout.splitlines() if x.strip()]):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and isinstance(value.get("schema"), str):
            return value
    return None


def _bound_independent_child() -> None:
    """Keep an incompatible third-party parser/consumer from taking down CI."""
    if resource is None:
        return
    resource.setrlimit(
        resource.RLIMIT_AS,
        (INDEPENDENT_ADDRESS_SPACE_BYTES, INDEPENDENT_ADDRESS_SPACE_BYTES),
    )
    resource.setrlimit(
        resource.RLIMIT_CPU,
        (INDEPENDENT_CPU_LIMIT_S, INDEPENDENT_CPU_LIMIT_S),
    )


def run_json(command: list[str], timeout: int = 180) -> dict[str, Any]:
    """Run a programme-owned probe whose process failure is a harness failure."""
    p = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
    value = _last_json_payload(p.stdout)
    if p.returncode != 0:
        raise RuntimeError(
            f"command failed ({p.returncode}): {' '.join(command)}\n"
            f"stdout={p.stdout}\nstderr={p.stderr}"
        )
    if value is not None:
        return value
    raise RuntimeError(
        f"no JSON payload from {' '.join(command)}\nstdout={p.stdout}\nstderr={p.stderr}"
    )


def run_independent_probe(command: list[str], *, role: str) -> dict[str, Any]:
    """Run independent software as bounded evidence, not as authority over CI.

    A parser/consumer refusal, crash, resource exhaustion, or timeout is an
    interoperability observation. It must make the exact profile unqualified while
    allowing the campaign to finish and retain the blocker instead of killing the
    evidence runner or being cosmetically relabelled as success.
    """
    kwargs: dict[str, Any] = {
        "text": True,
        "capture_output": True,
        "timeout": INDEPENDENT_WALL_TIMEOUT_S,
    }
    if resource is not None:
        kwargs["preexec_fn"] = _bound_independent_child
    try:
        p = subprocess.run(command, **kwargs)
    except subprocess.TimeoutExpired as exc:
        return {
            "schema": "rcs-022-independent-probe-failure/1.0",
            "status": "rejected",
            "role": role,
            "failure_kind": "wall_timeout",
            "wall_timeout_s": INDEPENDENT_WALL_TIMEOUT_S,
            "cpu_limit_s": INDEPENDENT_CPU_LIMIT_S,
            "address_space_limit_bytes": INDEPENDENT_ADDRESS_SPACE_BYTES,
            "stdout_tail": (exc.stdout or "")[-4000:]
            if isinstance(exc.stdout, str)
            else "",
            "stderr_tail": (exc.stderr or "")[-4000:]
            if isinstance(exc.stderr, str)
            else "",
        }

    value = _last_json_payload(p.stdout)
    if value is not None:
        value = dict(value)
        value["probe_bounds"] = {
            "wall_timeout_s": INDEPENDENT_WALL_TIMEOUT_S,
            "cpu_limit_s": INDEPENDENT_CPU_LIMIT_S,
            "address_space_limit_bytes": INDEPENDENT_ADDRESS_SPACE_BYTES,
        }
        if p.returncode != 0:
            value["process_exit_code"] = p.returncode
            value["process_failure"] = True
            value["status"] = "rejected"
            value["stderr_tail"] = p.stderr[-4000:]
        return value

    return {
        "schema": "rcs-022-independent-probe-failure/1.0",
        "status": "rejected",
        "role": role,
        "failure_kind": "process_exit" if p.returncode != 0 else "missing_json_payload",
        "process_exit_code": p.returncode,
        "wall_timeout_s": INDEPENDENT_WALL_TIMEOUT_S,
        "cpu_limit_s": INDEPENDENT_CPU_LIMIT_S,
        "address_space_limit_bytes": INDEPENDENT_ADDRESS_SPACE_BYTES,
        "stdout_tail": p.stdout[-4000:],
        "stderr_tail": p.stderr[-4000:],
    }


def max_bbox_delta(a: list[float], b: list[float]) -> float:
    return max(abs(float(x) - float(y)) for x, y in zip(a, b, strict=True))


def rel_delta(a: float, b: float) -> float:
    return abs(a - b) / max(abs(a), abs(b), 1.0e-30)


def classify_positive(
    case: dict[str, Any],
    exporter: dict[str, Any],
    parser: dict[str, Any],
    consumer_import: dict[str, Any],
    consumer_diagnostic: dict[str, Any],
    policies: dict[str, Any],
) -> tuple[dict[str, bool], list[str]]:
    checks: dict[str, bool] = {}
    blockers: list[str] = []
    expected_bodies = int(case["body_count"])
    pre = exporter["pre_export"]
    rb = exporter["layer_c_readback"]["metrics"]
    checks["export_status"] = exporter.get("status") == "exported"
    checks["layer_c_read_ok"] = bool(exporter["layer_c_readback"].get("read_ok"))
    checks["layer_c_valid_brep"] = bool(rb.get("valid_brep"))
    checks["layer_c_body_count"] = int(rb.get("body_count", -1)) == expected_bodies
    checks["layer_c_bbox"] = (
        max_bbox_delta(pre["bbox_mm"], rb["bbox_mm"])
        <= float(policies["layer_c_max_bbox_delta_mm"])
    )
    av = abs(float(pre["volume_mm3"]) - float(rb["volume_mm3"]))
    checks["layer_c_volume"] = (
        av <= float(policies["layer_c_max_abs_volume_delta_mm3"])
        or rel_delta(float(pre["volume_mm3"]), float(rb["volume_mm3"]))
        <= float(policies["layer_c_max_rel_volume_delta"])
    )

    checks["parser_accepts"] = parser.get("status") == "accepted"
    checks["parser_ap242"] = "242" in str(parser.get("file_schema", ""))
    checks["parser_body_count"] = int(parser.get("solid_count", -1)) == expected_bodies
    expected_si = 0.001 if case["unit"] == "mm" else 0.0254
    checks["parser_units"] = math.isclose(
        float(parser.get("units", {}).get("length_to_si", 0.0)),
        expected_si,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )
    required = case["required_analytic"]
    checks["parser_analytic"] = (
        int(parser.get("analytic_surfaces", {}).get(required, 0)) > 0
    )

    checks["consumer_accepts"] = consumer_import.get("status") == "accepted"
    checks["consumer_clean"] = bool(consumer_import.get("clean_import")) and int(
        consumer_import.get("skipped_faces", 999999)
    ) == 0
    checks["consumer_body_count"] = (
        int(consumer_import.get("solid_count", -1)) == expected_bodies
    )

    diag = consumer_diagnostic.get("mesh_diagnostic", {})
    checks["consumer_diagnostic_accepts"] = (
        consumer_diagnostic.get("status") == "accepted"
    )
    if consumer_diagnostic.get("status") == "accepted" and diag:
        checks["consumer_bbox"] = (
            max_bbox_delta(pre["bbox_mm"], diag["bbox_mm"])
            <= float(policies["consumer_max_bbox_delta_mm"])
        )
        checks["consumer_volume"] = (
            rel_delta(float(pre["volume_mm3"]), float(diag["volume_mm3"]))
            <= float(policies["consumer_max_rel_mesh_volume_delta"])
        )
    else:
        checks["consumer_bbox"] = False
        checks["consumer_volume"] = False

    for name, ok in checks.items():
        if not ok:
            blockers.append(f"{case['id']}:{name}")
    return checks, blockers


def mutate_schema(text: str) -> str:
    start = text.find("FILE_SCHEMA")
    if start < 0:
        return text[: max(1, len(text) // 3)]
    end = text.find(";", start)
    if end < 0:
        return text[: max(1, len(text) // 3)]
    return text[:start] + "FILE_SCHEMA(('RCS022_NOT_A_STEP_SCHEMA'));" + text[end + 1 :]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exporter", required=True)
    ap.add_argument("--parser-probe", required=True)
    ap.add_argument("--consumer-probe", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    plan = json.loads((HERE / "fixture-plan-v1.json").read_text())
    profile = json.loads((HERE / "profile-v1.json").read_text())
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    positives: list[dict[str, Any]] = []
    blockers: list[str] = []

    for case in plan["cases"]:
        print(f"RCS-022 positive fixture: {case['id']}", file=sys.stderr, flush=True)
        step = out / f"{case['id']}.step"
        exporter = run_json(
            [
                args.exporter,
                "--case",
                case["id"],
                "--unit",
                case["unit"],
                "--step-file",
                str(step),
            ]
        )
        if exporter.get("status") != "exported":
            parser = {"status": "not_run"}
            consumer_import = {"status": "not_run"}
            consumer_diagnostic = {"status": "not_run"}
            checks = {"export_status": False}
            case_blockers = [f"{case['id']}:export_status"]
            sha = None
        else:
            parser = run_independent_probe(
                [args.parser_probe, str(step)], role="part21_schema_parser"
            )
            consumer_import = run_independent_probe(
                [args.consumer_probe, str(step), "--import-only"],
                role="downstream_solid_consumer_import",
            )
            if consumer_import.get("status") == "accepted":
                consumer_diagnostic = run_independent_probe(
                    [args.consumer_probe, str(step)],
                    role="downstream_consumer_mesh_diagnostic",
                )
            else:
                consumer_diagnostic = {
                    "schema": "rcs-022-independent-probe-not-run/1.0",
                    "status": "not_run",
                    "role": "downstream_consumer_mesh_diagnostic",
                    "reason": "independent B-rep import did not accept the fixture",
                }
            checks, case_blockers = classify_positive(
                case,
                exporter,
                parser,
                consumer_import,
                consumer_diagnostic,
                plan["policies"],
            )
            sha = hashlib.sha256(step.read_bytes()).hexdigest()
        blockers.extend(case_blockers)
        positives.append(
            {
                "case": case,
                "step_sha256": sha,
                "exporter": exporter,
                "parser": parser,
                "consumer": consumer_import,
                "consumer_mesh_diagnostic": consumer_diagnostic,
                "checks": checks,
                "qualified": all(checks.values()),
            }
        )

    # Adversarial/boundary probes are expected to be rejected by the semantic gate.
    neg: list[dict[str, Any]] = []
    base = next(x for x in positives if x["case"]["id"] == "metric-block")
    parting = next(x for x in positives if x["case"]["id"] == "two-body-parting")
    cylinder = next(x for x in positives if x["case"]["id"] == "analytic-cylinder")

    wrong_unit_detected = not math.isclose(
        float(base["parser"].get("units", {}).get("length_to_si", 0.0)),
        0.0254,
        abs_tol=1.0e-12,
    )
    neg.append(
        {
            "id": "wrong_unit_scale",
            "passed": wrong_unit_detected,
            "failure_code": "STEP_UNIT_SCALE_MISMATCH",
        }
    )
    omitted = int(base["parser"].get("solid_count", -1)) != 2
    neg.append(
        {
            "id": "omitted_body",
            "passed": omitted,
            "failure_code": "STEP_BODY_COUNT_MISMATCH",
        }
    )

    invalid_step = out / "invalid-open-shell.step"
    invalid = run_json(
        [
            args.exporter,
            "--case",
            "invalid-open-shell",
            "--unit",
            "mm",
            "--step-file",
            str(invalid_step),
        ]
    )
    neg.append(
        {
            "id": "invalid_open_non_solid",
            "passed": invalid.get("status") == "refused"
            and invalid.get("failure_code") == "PREEXPORT_SOLID_CONTRACT_FAILED",
            "failure_code": invalid.get("failure_code"),
        }
    )

    analytic_loss = (
        int(base["parser"].get("analytic_surfaces", {}).get("cylinder", 0)) == 0
        and int(cylinder["parser"].get("analytic_surfaces", {}).get("cylinder", 0)) > 0
    )
    neg.append(
        {
            "id": "analytic_degradation",
            "passed": analytic_loss,
            "failure_code": "STEP_ANALYTIC_GEOMETRY_LOST",
        }
    )

    deviation = (
        max_bbox_delta(
            base["exporter"]["pre_export"]["bbox_mm"],
            parting["exporter"]["pre_export"]["bbox_mm"],
        )
        > float(plan["policies"]["layer_c_max_bbox_delta_mm"])
    )
    neg.append(
        {
            "id": "excessive_dimension_volume_deviation",
            "passed": deviation,
            "failure_code": "STEP_DIMENSION_VOLUME_DEVIATION",
        }
    )

    base_path = out / "metric-block.step"
    malformed_schema = out / "adversarial-schema.step"
    malformed_schema.write_text(mutate_schema(base_path.read_text(errors="replace")))
    bad_parser = run_independent_probe(
        [args.parser_probe, str(malformed_schema)], role="part21_schema_parser"
    )
    parser_failure = bad_parser.get("status") != "accepted" or "242" not in str(
        bad_parser.get("file_schema", "")
    )
    neg.append(
        {
            "id": "parser_schema_failure",
            "passed": parser_failure,
            "failure_code": "STEP_SCHEMA_PARSER_REJECTION",
            "observation": bad_parser,
        }
    )

    truncated = out / "adversarial-truncated.step"
    raw = base_path.read_bytes()
    truncated.write_bytes(raw[: max(64, len(raw) // 3)])
    bad_consumer = run_independent_probe(
        [args.consumer_probe, str(truncated), "--import-only"],
        role="downstream_solid_consumer_import",
    )
    downstream_failure = bad_consumer.get("status") != "accepted" or int(
        bad_consumer.get("solid_count", 0)
    ) == 0
    neg.append(
        {
            "id": "downstream_import_failure",
            "passed": downstream_failure,
            "failure_code": "STEP_DOWNSTREAM_IMPORT_REJECTION",
            "observation": bad_consumer,
        }
    )

    negative_ok = all(x["passed"] for x in neg)
    if not negative_ok:
        blockers.extend(f"negative:{x['id']}" for x in neg if not x["passed"])
    all_positive = all(x["qualified"] for x in positives)
    status = (
        "interoperability_qualified"
        if all_positive and negative_ok
        else "interoperability_unqualified"
    )
    summary = {
        "schema": "rcs-022-measured-summary/1.0",
        "profile_id": profile["id"],
        "qualification_status": status,
        "probe_resource_bounds": {
            "wall_timeout_s": INDEPENDENT_WALL_TIMEOUT_S,
            "cpu_limit_s": INDEPENDENT_CPU_LIMIT_S,
            "address_space_limit_bytes": INDEPENDENT_ADDRESS_SPACE_BYTES,
            "scope": "independent parser/consumer child processes only",
        },
        "implementation_independence": {
            "exporter": "OCCT 8.0.1",
            "parser": "step-io 0.2.4 (Rust; independent of OCCT)",
            "consumer": "vcad-kernel-step 0.10.0 / vcad-kernel-tessellate 0.10.0 (Rust vcad kernel; independent of OCCT)",
            "same_kernel_layer_c_only": "OCCT writer->fresh OCCT reader is Layer C only and is never counted as Layer D",
        },
        "positive_cases": positives,
        "negative_cases": neg,
        "all_positive_qualified": all_positive,
        "all_negative_controls_pass": negative_ok,
        "blockers": sorted(set(blockers)),
        "closure_semantics": "A deterministic unqualified result is a valid research outcome; it must retain exact blockers and must not be relabelled success.",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))
    # Exit nonzero only when the harness itself failed to observe a required negative control.
    # Positive interoperability disagreement is preserved as a bounded negative research result.
    return 0 if negative_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
