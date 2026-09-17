#!/usr/bin/env python3
import argparse
import json
import math
import os
import pathlib
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def run(cmd, log_path, timeout=180):
    started = time.perf_counter()
    try:
        cp = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        rc, out, err, timed_out = cp.returncode, cp.stdout, cp.stderr, False
    except subprocess.TimeoutExpired as exc:
        rc, out, err, timed_out = 124, exc.stdout or "", exc.stderr or "", True
        if isinstance(out, bytes): out = out.decode(errors="replace")
        if isinstance(err, bytes): err = err.decode(errors="replace")
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(out + ("\n--- STDERR ---\n" + err if err else ""), encoding="utf-8")
    records = []
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try: records.append(json.loads(line))
        except json.JSONDecodeError: pass
    return {"returncode": rc, "timed_out": timed_out, "elapsed_ms": elapsed_ms, "records": records, "stderr": err}


def job_records(run_result):
    return [r for r in run_result["records"] if r.get("type") == "job"]


def summarize_jobs(records):
    ok = [r for r in records if r.get("ok")]
    wrong_config = 0
    max_volume_delta = 0.0
    for r in ok:
        cfg = r.get("config")
        schema = (r.get("schema") or "").upper()
        if cfg == "inch-ap203":
            if not r.get("inch_marker") or "AP203" not in schema:
                wrong_config += 1
        elif cfg == "mm-ap242":
            if not r.get("mm_marker") or "AP242" not in schema:
                wrong_config += 1
        else:
            wrong_config += 1
        max_volume_delta = max(max_volume_delta, abs(float(r.get("cut_volume_mm3", 0.0)) - float(r.get("readback_volume_mm3", 0.0))))
    return {
        "attempts": len(records),
        "successes": len(ok),
        "failures": len(records) - len(ok),
        "wrong_configuration_observations": wrong_config,
        "max_step_volume_abs_delta_mm3": max_volume_delta,
        "errors": sorted({r.get("error", "") for r in records if r.get("error")}),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--profile", choices=["smoke", "stress"], default="smoke")
    args = ap.parse_args()
    worker = str(pathlib.Path(args.worker).resolve())
    out = pathlib.Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    jobs, iterations = ((4, 3) if args.profile == "smoke" else (8, 20))

    sequential = run([worker, "--mode", "sequential", "--jobs", str(jobs), "--iterations", str(iterations), "--out-dir", str(out / "step-sequential")], out / "sequential.log")
    threaded = run([worker, "--mode", "threads", "--jobs", str(jobs), "--iterations", str(iterations), "--out-dir", str(out / "step-threads")], out / "threads.log")
    global_probe = run([worker, "--mode", "global-race", "--jobs", str(jobs), "--iterations", str(iterations)], out / "global-parallel.log")

    proc_count = 4 if args.profile == "smoke" else 8
    process_runs = []
    process_started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=proc_count) as pool:
        futures = {}
        for p in range(proc_count):
            cmd = [worker, "--mode", "sequential", "--jobs", "2", "--iterations", str(max(2, iterations // 2)), "--out-dir", str(out / f"step-process-{p}")]
            futures[pool.submit(run, cmd, out / f"process-{p}.log")] = p
        for f in as_completed(futures):
            process_runs.append((futures[f], f.result()))
    process_wall_ms = (time.perf_counter() - process_started) * 1000.0
    process_runs.sort(key=lambda x: x[0])

    seq_jobs = job_records(sequential)
    thread_jobs = job_records(threaded)
    proc_jobs = [j for _, r in process_runs for j in job_records(r)]
    gp = next((r for r in global_probe["records"] if r.get("type") == "global_parallel_probe"), {})

    summary = {
        "schema": "rcs017-concurrency-summary/1.0",
        "profile": args.profile,
        "worker": worker,
        "occt": {"version": "8.0.1", "commit": "b8f597c677811d1f9f4d8a97f5ae2825c0353a42", "build_profile": "release-shared-cxx17-worker-only-headless-v4"},
        "sequential": {**summarize_jobs(seq_jobs), "worker_returncode": sequential["returncode"], "wall_ms": sequential["elapsed_ms"], "timed_out": sequential["timed_out"]},
        "threads": {**summarize_jobs(thread_jobs), "worker_returncode": threaded["returncode"], "wall_ms": threaded["elapsed_ms"], "timed_out": threaded["timed_out"]},
        "processes": {**summarize_jobs(proc_jobs), "workers": proc_count, "wall_ms": process_wall_ms, "returncodes": [r["returncode"] for _, r in process_runs], "timeouts": sum(1 for _, r in process_runs if r["timed_out"])},
        "global_parallel_state": {"attempts": gp.get("attempts"), "mismatches": gp.get("mismatches"), "worker_returncode": global_probe["returncode"], "timed_out": global_probe["timed_out"]},
        "shared_shape_read_only_ownership": {
            "expected_volume_mm3": 8000.0,
            "thread_summary_volume_mm3": next((r.get("shared_shape_volume_mm3") for r in threaded["records"] if r.get("type") == "summary"), None),
            "sequential_summary_volume_mm3": next((r.get("shared_shape_volume_mm3") for r in sequential["records"] if r.get("type") == "summary"), None),
        },
        "interpretation_rules": {
            "explicit_step_cross_talk": "nonzero wrong_configuration_observations under threads with correct sequential baseline",
            "global_parallel_cross_talk": "nonzero mismatches demonstrates a process-global setting observable across independent threads",
            "process_isolation": "compare process failures/cross-talk with one-process threaded results; subprocess state is independent by construction",
        },
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))

    # Research campaigns must preserve negative results rather than turn them into CI failures.
    # Fail only when there is no sequential baseline evidence at all or the exact build did not run.
    if not seq_jobs or sequential["returncode"] != 0:
        raise SystemExit("RCS-017 sequential baseline did not execute successfully")

if __name__ == "__main__":
    main()
