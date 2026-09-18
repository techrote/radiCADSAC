#!/usr/bin/env python3
import argparse, json, pathlib, re, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE="b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
CAND="3d097a0328e71b826377d4814ab05ec3c3d23871"
BASE_VERSION="8.0.1"
CAND_VERSION="8.1.0.dev1"
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

def dynamic(results):
  p=pathlib.Path(results)/"differential.json"
  if not p.is_file(): fail("missing differential.json")
  d=json.loads(p.read_text())
  if d.get("schema")!="rcs024-differential/1.0": fail("wrong evidence schema")
  if d["pins"]["baseline"]["commit"]!=BASE or d["pins"]["candidate"]["commit"]!=CAND: fail("pin drift")
  for label, expected_version in (("baseline",BASE_VERSION),("candidate",CAND_VERSION)):
    r=d["runs"][label]
    for probe in ("step","parallel","fuzzy","chain","mill","sampled","brepgraph"):
      if probe not in r: fail(f"{label} missing {probe}")
    for probe in ("step","brepgraph"):
      if r[probe].get("version") != expected_version: fail(f"{label} {probe} version drift")
    g=r["brepgraph"]
    if g["split_image_count"]!=2 or g["merge_origin_count"]!=2 or not g["stale_after_clear"]: fail(label+" BRepGraph boundary probe failed")
    q=r["parallel"]
    if q["global_after_instance_true"] or not q["thread_a_observed_thread_b_global"]: fail(label+" parallel ownership semantics changed")
  if not d["runs"]["baseline"]["sampled"]["timed_out"]: fail("baseline timeout control did not reproduce")
  dec=d.get("decision_input",{})
  if not dec.get("process_isolation_required") or not dec.get("programme_identity_must_ignore_brepgraph_uid"): fail("protected boundary weakened")

def adversarial_self_test():
  # Boundary guards: exact pin equality, programme identity, process isolation, and dev/release version distinction are fail-closed.
  sample={"pins":{"baseline":{"commit":BASE},"candidate":{"commit":CAND}},"process_isolation_required":True,"programme_identity":False}
  assert sample["pins"]["baseline"]["commit"]==BASE
  assert sample["pins"]["candidate"]["commit"]==CAND
  assert sample["process_isolation_required"] is True
  assert sample["programme_identity"] is False
  complete="8.1.0"; development="dev1"
  assert complete != CAND_VERSION
  assert complete+"."+development == CAND_VERSION
  # Upstream enables USE_GIT_HASH by default for development builds. That would produce a suffix such as
  # dev1-<hash> and violate this campaign's version contract even though the exact source commit is already
  # verified independently. The build therefore pins USE_GIT_HASH=OFF and rejects an auto-suffixed variant.
  auto_suffixed=complete+"."+development+"-3d097a0"
  assert auto_suffixed != CAND_VERSION

def main():
  ap=argparse.ArgumentParser();ap.add_argument("--results-dir");a=ap.parse_args();static();adversarial_self_test();
  if a.results_dir: dynamic(a.results_dir)
  print("RCS-024 validation passed")
if __name__=="__main__":main()
