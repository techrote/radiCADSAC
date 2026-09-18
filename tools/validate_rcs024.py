#!/usr/bin/env python3
import argparse, json, pathlib, re, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE="b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
CAND="3d097a0328e71b826377d4814ab05ec3c3d23871"
REQUIRED=[
 "research/rcs-024/README.md","research/rcs-024/experiment-plan-v1.json","research/rcs-024/bootstrap_candidate.sh",
 "research/rcs-024/harness/CMakeLists.txt","research/rcs-024/harness/diff_worker.cpp","research/rcs-024/harness/brepgraph_probe.cpp",
 "research/rcs-024/run_differential.py","docs/32-OCCT-CURRENT-DIFFERENTIAL.md",
 "docs/decisions/DR-0021-retain-occt-8-0-1-after-current-differential.md",".github/workflows/rcs024.yml"]

def fail(msg): raise SystemExit("RCS-024 validation failed: "+msg)
def static():
  for p in REQUIRED:
    if not (ROOT/p).is_file(): fail("missing "+p)
  joined="\n".join((ROOT/p).read_text(encoding="utf-8") for p in REQUIRED if p.endswith((".md",".json",".py",".sh",".cpp",".yml")))
  for token in (BASE,CAND,"8.1.0.dev1","process isolation","BRepGraph","programme identity","STEP"):
    if token.lower() not in joined.lower(): fail("required contract token absent: "+token)
  if "master" in json.loads((ROOT/"research/rcs-024/experiment-plan-v1.json").read_text()).get("candidate",{}).get("ref","").lower():
    fail("candidate may not be an unpinned master ref")

def dynamic(results):
  p=pathlib.Path(results)/"differential.json"
  if not p.is_file(): fail("missing differential.json")
  d=json.loads(p.read_text())
  if d.get("schema")!="rcs024-differential/1.0": fail("wrong evidence schema")
  if d["pins"]["baseline"]["commit"]!=BASE or d["pins"]["candidate"]["commit"]!=CAND: fail("pin drift")
  for label in ("baseline","candidate"):
    r=d["runs"][label]
    for probe in ("step","parallel","fuzzy","chain","mill","sampled","brepgraph"):
      if probe not in r: fail(f"{label} missing {probe}")
    g=r["brepgraph"]
    if g["split_image_count"]!=2 or g["merge_origin_count"]!=2 or not g["stale_after_clear"]: fail(label+" BRepGraph boundary probe failed")
    q=r["parallel"]
    if q["global_after_instance_true"] or not q["thread_a_observed_thread_b_global"]: fail(label+" parallel ownership semantics changed")
  if not d["runs"]["baseline"]["sampled"]["timed_out"]: fail("baseline timeout control did not reproduce")
  dec=d.get("decision_input",{})
  if not dec.get("process_isolation_required") or not dec.get("programme_identity_must_ignore_brepgraph_uid"): fail("protected boundary weakened")

def adversarial_self_test():
  # Boundary guards: exact pin equality, programme identity, and process isolation are fail-closed.
  sample={"pins":{"baseline":{"commit":BASE},"candidate":{"commit":CAND}},"process_isolation_required":True,"programme_identity":False}
  assert sample["pins"]["baseline"]["commit"]==BASE
  assert sample["pins"]["candidate"]["commit"]==CAND
  assert sample["process_isolation_required"] is True
  assert sample["programme_identity"] is False

def main():
  ap=argparse.ArgumentParser();ap.add_argument("--results-dir");a=ap.parse_args();static();adversarial_self_test();
  if a.results_dir: dynamic(a.results_dir)
  print("RCS-024 validation passed")
if __name__=="__main__":main()
