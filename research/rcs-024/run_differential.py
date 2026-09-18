#!/usr/bin/env python3
import argparse, json, pathlib, subprocess, sys, time

PROBES = ("step", "parallel", "fuzzy", "chain", "mill")

def last_json(text):
    for line in reversed(text.splitlines()):
        line=line.strip()
        if line.startswith("{"):
            return json.loads(line)
    raise RuntimeError("no JSON record in worker output")

def run(exe, probe, out, timeout=120):
    cmd=[exe,"--probe",probe,"--out-dir",str(out/probe)]
    started=time.monotonic()
    try:
        cp=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
    except subprocess.TimeoutExpired as e:
        return {"probe":probe,"timed_out":True,"timeout_s":timeout,"wall_s":time.monotonic()-started,
                "stdout":e.stdout or "","stderr":e.stderr or ""}
    rec=last_json(cp.stdout) if cp.returncode==0 else {"probe":probe}
    rec.update({"timed_out":False,"returncode":cp.returncode,"wall_s":time.monotonic()-started,"stderr":cp.stderr})
    if cp.returncode!=0: raise RuntimeError(f"{cmd} failed: {cp.stderr}")
    return rec

def run_graph(exe, timeout=60):
    cp=subprocess.run([exe],text=True,capture_output=True,timeout=timeout)
    if cp.returncode!=0: raise RuntimeError(f"BRepGraph probe failed: {cp.stderr}")
    return last_json(cp.stdout)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--baseline-worker",required=True);ap.add_argument("--candidate-worker",required=True)
    ap.add_argument("--baseline-graph",required=True);ap.add_argument("--candidate-graph",required=True)
    ap.add_argument("--out-dir",required=True);a=ap.parse_args()
    out=pathlib.Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    data={"schema":"rcs024-differential/1.0","pins":{
        "baseline":{"version":"8.0.1","commit":"b8f597c677811d1f9f4d8a97f5ae2825c0353a42"},
        "candidate":{"version":"8.1.0.dev1","commit":"3d097a0328e71b826377d4814ab05ec3c3d23871"}},"runs":{}}
    for label,worker,graph in (("baseline",a.baseline_worker,a.baseline_graph),("candidate",a.candidate_worker,a.candidate_graph)):
        r={p:run(worker,p,out/label) for p in PROBES}
        r["sampled"]=run(worker,"sampled",out/label,timeout=8)
        r["brepgraph"]=run_graph(graph)
        data["runs"][label]=r

    b=data["runs"]["baseline"];c=data["runs"]["candidate"]
    # Fixture continuity: fail rather than silently compare a broken reproducer.
    assert abs(b["step"]["seq_mm"]-1e-5)<1e-10 and b["step"]["seq_valid"]
    assert b["fuzzy"]["expected_removed_mm3"]>1e-6 and abs(b["fuzzy"]["measured_removed_mm3"])<1e-5 and b["fuzzy"]["valid_brep"]
    assert b["chain"]["order_delta_mm3"]>1.0 and b["chain"]["both_valid"]
    assert b["mill"]["delta_mm3"]>100.0 and b["mill"]["batch_valid"] and b["mill"]["segment_valid"]
    assert b["sampled"]["timed_out"], "baseline sampled fallback no longer reproduces bounded timeout"
    for label in ("baseline","candidate"):
        g=data["runs"][label]["brepgraph"]
        assert g["split_image_count"]==2 and g["merge_origin_count"]==2 and g["stamp_valid"] and g["stale_after_clear"]
        p=data["runs"][label]["parallel"]
        assert p["initial_global"] is False and p["global_after_instance_true"] is False and p["thread_a_observed_thread_b_global"] is True

    def step_class(x):
        expected=1e-5
        return "isolated" if abs(x["cross_mm"]-expected)<1e-10 else "cross_talk"
    data["classification"]={
        "step_baseline":step_class(b["step"]),"step_candidate":step_class(c["step"]),
        "fuzzy_baseline_valid_but_wrong":abs(b["fuzzy"]["measured_removed_mm3"]-b["fuzzy"]["expected_removed_mm3"])>1e-4,
        "fuzzy_candidate_valid_but_wrong":abs(c["fuzzy"]["measured_removed_mm3"]-c["fuzzy"]["expected_removed_mm3"])>1e-4,
        "chain_baseline_order_sensitive":b["chain"]["order_delta_mm3"]>1e-4,
        "chain_candidate_order_sensitive":c["chain"]["order_delta_mm3"]>1e-4,
        "mill_baseline_valid_but_wrong":b["mill"]["delta_mm3"]>0.05,
        "mill_candidate_valid_but_wrong":c["mill"]["delta_mm3"]>0.05,
        "sampled_baseline_timeout":b["sampled"]["timed_out"],"sampled_candidate_timeout":c["sampled"]["timed_out"]}
    data["decision_input"]={
        "process_isolation_required": True,
        "programme_identity_must_ignore_brepgraph_uid": True,
        "candidate_is_development_snapshot_not_stable_release": True,
        "recommended_baseline":"8.0.1",
        "recommendation":"retain_8_0_1_preserve_current_findings_and_selectively_use_backend_private_brepgraph_facilities"}
    (out/"differential.json").write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(data["classification"],sort_keys=True))
if __name__=="__main__":main()
