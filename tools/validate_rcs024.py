#!/usr/bin/env python3
import argparse, json, pathlib, re, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE="b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
CAND="3d097a0328e71b826377d4814ab05ec3c3d23871"
BASE_VERSION="8.0.1"
CAND_VERSION="8.1.0.dev1"
MEASURED="research/rcs-024/measured-result-v1.json"
REQUIRED=[
 "research/rcs-024/README.md","research/rcs-024/experiment-plan-v1.json","research/rcs-024/bootstrap_candidate.sh",
 "research/rcs-024/harness/CMakeLists.txt","research/rcs-024/harness/diff_worker.cpp","research/rcs-024/harness/brepgraph_probe.cpp",
 "research/rcs-024/run_differential.py",MEASURED,"docs/32-OCCT-CURRENT-DIFFERENTIAL.md",
 "docs/decisions/DR-0021-retain-occt-8-0-1-after-current-differential.md",".github/workflows/rcs024.yml"]

def fail(msg): raise SystemExit("RCS-024 validation failed: "+msg)
def close(a,b,tol=1e-9): return abs(float(a)-float(b)) <= tol

def validate_probe_logging(workflow):
  """Fail closed if either probe build can become diagnostically opaque again."""
  required=(
    "Configure and build baseline probes",
    "Configure and build candidate probes",
    ".results/rcs024/probe-build/baseline-probe-build.log",
    ".results/rcs024/probe-build/candidate-probe-build.log",
    "if: always()",
    "path: .results/rcs024",
  )
  for token in required:
    if token not in workflow: fail("probe-build diagnostics contract lost: "+token)
  if workflow.count("set -euo pipefail") < 4:
    fail("probe-build diagnostics must preserve failure status through pipefail")
  for label in ("baseline", "candidate"):
    pattern=(
      rf"Configure and build {label} probes.*?set -euo pipefail.*?"
      rf"{label}-probe-build\.log.*?tee -a .*?{label}-probe-build\.log"
    )
    if not re.search(pattern, workflow, re.S):
      fail(label+" probe configure/build output must be retained across both phases")

def load_frozen():
  p=ROOT/MEASURED
  if not p.is_file(): fail("missing "+MEASURED)
  m=json.loads(p.read_text(encoding="utf-8"))
  if m.get("schema")!="rcs024-measured-result/1.0": fail("wrong frozen measured-result schema")
  if m["pins"]["baseline"]["commit"]!=BASE or m["pins"]["candidate"]["commit"]!=CAND: fail("frozen pin drift")
  if m["source_evidence"]["head_sha"]!="5ee2dda2677ca9f6dc19da8e3210bb19e982819d": fail("frozen source-evidence head drift")
  if m["source_evidence"]["artifact_sha256"]!="65d61055cd637a09aa61ca6ac6bfc3c661adfbd18cceaf17668a794bbd23a3ae": fail("frozen artifact digest drift")
  if m["classification"].get("overall_candidate_delta")!="same_defects_no_upgrade_case": fail("frozen comparative classification weakened")
  dec=m.get("decision",{})
  if dec.get("recommended_baseline")!="8.0.1" or not dec.get("process_isolation_required") or not dec.get("programme_identity_must_ignore_brepgraph_uid"):
    fail("frozen decision weakened")
  return m

def static():
  for p in REQUIRED:
    if not (ROOT/p).is_file(): fail("missing "+p)
  joined="\n".join((ROOT/p).read_text(encoding="utf-8") for p in REQUIRED if p.endswith((".md",".json",".py",".sh",".cpp",".yml")))
  for token in (BASE,CAND,CAND_VERSION,"process isolation","BRepGraph","programme identity","STEP"):
    if token.lower() not in joined.lower(): fail("required contract token absent: "+token)
  if "master" in json.loads((ROOT/"research/rcs-024/experiment-plan-v1.json").read_text()).get("candidate",{}).get("ref","").lower():
    fail("candidate may not be an unpinned master ref")

  bootstrap=(ROOT/"research/rcs-024/bootstrap_candidate.sh").read_text(encoding="utf-8")
  for token in ('EXPECTED_VERSION_COMPLETE="8.1.0"','EXPECTED_VERSION_DEVELOPMENT="dev1"','OCC_VERSION_COMPLETE','OCC_VERSION_DEVELOPMENT','-DUSE_GIT_HASH=OFF'):
    if token not in bootstrap: fail("candidate bootstrap lost development-version guard: "+token)
  if 'OCC_VERSION_COMPLETE \\"8.1.0.dev1\\"' in bootstrap:
    fail("candidate bootstrap must not treat OCC_VERSION_COMPLETE as the extended development version")
  if re.search(r'-DUSE_GIT_HASH=(?:ON|TRUE|1)', bootstrap, re.I):
    fail("candidate bootstrap must keep OCCT automatic git suffix disabled; exact commit is verified separately")

  for rel in ("research/rcs-024/harness/diff_worker.cpp","research/rcs-024/harness/brepgraph_probe.cpp"):
    text=(ROOT/rel).read_text(encoding="utf-8")
    if "OCC_VERSION_STRING_EXT" not in text: fail(rel+" must bind evidence to the extended OCCT version")
    if "std::string(OCC_VERSION_COMPLETE)!=RCS024_EXPECTED_VERSION" in text:
      fail(rel+" regressed to release-only version comparison")

  graph_probe=(ROOT/"research/rcs-024/harness/brepgraph_probe.cpp").read_text(encoding="utf-8")
  for header in ("BRepGraph_ShapesView.hxx", "BRepGraph_LayerRegistry.hxx", "BRepGraph_UIDsView.hxx"):
    if f"#include <{header}>" not in graph_probe:
      fail("BRepGraph probe lost complete-view include: "+header)
  for token in ("const std::size_t split_image_count", "const std::size_t merge_origin_count", "if(split_image_count!=2 || merge_origin_count!=2)"):
    if token not in graph_probe: fail("BRepGraph borrowed-history boundary guard lost: "+token)
  clear_at=graph_probe.find("graph.Clear()")
  if clear_at < 0: fail("BRepGraph clear/freshness boundary missing")
  if re.search(r"(?:split_images|merge_origins)->", graph_probe[clear_at:]):
    fail("BRepGraph borrowed history pointer escaped across graph.Clear()")

  runner=(ROOT/"research/rcs-024/run_differential.py").read_text(encoding="utf-8")
  for token in ("differential-partial.json", "write_partial()", "def require(condition, message):"):
    if token not in runner: fail("differential failure evidence contract lost: "+token)
  if re.search(r"^\s*assert\s", runner, re.M):
    fail("differential continuity gates must not disappear under python -O")

  docs=(ROOT/"docs/32-OCCT-CURRENT-DIFFERENTIAL.md").read_text(encoding="utf-8")
  dr=(ROOT/"docs/decisions/DR-0021-retain-occt-8-0-1-after-current-differential.md").read_text(encoding="utf-8")
  for token in ("RCS-024 measured and frozen", "same defect", "Retain OCCT 8.0.1", "509.00986225103406"):
    if token.lower() not in docs.lower(): fail("measured differential documentation not frozen: "+token)
  for token in ("accepted by RCS-024 measured evidence", "Retain OCCT 8.0.1", "process-isolated", "numerical UID collision"):
    if token.lower() not in dr.lower(): fail("DR-0021 acceptance evidence missing: "+token)

  load_frozen()
  validate_probe_logging((ROOT/".github/workflows/rcs024.yml").read_text(encoding="utf-8"))

def dynamic(results):
  results=pathlib.Path(results)
  p=results/"differential.json"
  if not p.is_file(): fail("missing differential.json")
  d=json.loads(p.read_text())
  frozen=load_frozen()
  if d.get("schema")!="rcs024-differential/1.0": fail("wrong evidence schema")
  if d["pins"]["baseline"]["commit"]!=BASE or d["pins"]["candidate"]["commit"]!=CAND: fail("pin drift")
  expected_class={k:v for k,v in frozen["classification"].items() if k!="overall_candidate_delta"}
  if d.get("classification")!=expected_class: fail("final-head classification differs from frozen measured result")
  for label, expected_version in (("baseline",BASE_VERSION),("candidate",CAND_VERSION)):
    r=d["runs"][label]
    for probe in ("step","parallel","fuzzy","chain","mill","sampled","brepgraph"):
      if probe not in r: fail(f"{label} missing {probe}")
    for probe in ("step","brepgraph"):
      if r[probe].get("version") != expected_version: fail(f"{label} {probe} version drift")
    g=r["brepgraph"]; fg=frozen["observations"]["brepgraph"][label]
    for key in ("split_image_count","merge_origin_count","stamp_valid","stale_after_clear","replay_uid_valid","numerical_uid_collision_across_graph_rebuild"):
      if g.get(key)!=fg[key]: fail(f"{label} BRepGraph measured-result drift: {key}")
    q=r["parallel"]; fq=frozen["observations"]["parallel"][label]
    for key in ("global_after_instance_true","thread_a_observed_thread_b_global"):
      if q.get(key)!=fq[key]: fail(f"{label} parallel measured-result drift: {key}")
    for probe,key in (("step","cross_mm"),("fuzzy","expected_removed_mm3"),("fuzzy","measured_removed_mm3"),("chain","order_delta_mm3"),("mill","delta_mm3")):
      if not close(r[probe][key], frozen["observations"][probe][label][key]): fail(f"{label} {probe} measured-result drift: {key}")
    if r["sampled"].get("timed_out") is not True: fail(label+" sampled fallback no longer reproduces bounded timeout")
  dec=d.get("decision_input",{})
  if not dec.get("process_isolation_required") or not dec.get("programme_identity_must_ignore_brepgraph_uid") or dec.get("recommended_baseline")!="8.0.1":
    fail("protected decision boundary weakened")
  footprint=results/"footprint.json"
  if not footprint.is_file(): fail("missing footprint.json")
  fp=json.loads(footprint.read_text())
  for label in ("baseline","candidate"):
    if fp[label]["install_bytes"]!=frozen["installed_footprint_bytes"][label]: fail(label+" installed footprint drift")

def adversarial_self_test():
  sample={"pins":{"baseline":{"commit":BASE},"candidate":{"commit":CAND}},"process_isolation_required":True,"programme_identity":False}
  assert sample["pins"]["baseline"]["commit"]==BASE
  assert sample["pins"]["candidate"]["commit"]==CAND
  assert sample["process_isolation_required"] is True
  assert sample["programme_identity"] is False
  complete="8.1.0"; development="dev1"
  assert complete != CAND_VERSION
  assert complete+"."+development == CAND_VERSION
  auto_suffixed=complete+"."+development+"-3d097a0"
  assert auto_suffixed != CAND_VERSION

  good="""Configure and build baseline probes\nset -euo pipefail\nbaseline-probe-build.log\ntee -a x/baseline-probe-build.log\nConfigure and build candidate probes\nset -euo pipefail\ncandidate-probe-build.log\ntee -a x/candidate-probe-build.log\nset -euo pipefail\nset -euo pipefail\nif: always()\npath: .results/rcs024\n.results/rcs024/probe-build/baseline-probe-build.log\n.results/rcs024/probe-build/candidate-probe-build.log\n"""
  validate_probe_logging(good)
  for bad in (good.replace("set -euo pipefail\n", "", 1), good.replace("candidate-probe-build.log", "candidate-missing.log")):
    try:
      validate_probe_logging(bad)
    except SystemExit:
      pass
    else:
      raise AssertionError("adversarial diagnostics contract unexpectedly accepted")

def main():
  ap=argparse.ArgumentParser();ap.add_argument("--results-dir");a=ap.parse_args();static();adversarial_self_test()
  if a.results_dir: dynamic(a.results_dir)
  print("RCS-024 validation passed")
if __name__=="__main__":main()
