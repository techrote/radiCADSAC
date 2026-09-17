#!/usr/bin/env python3
"""Validate RCS-019 canonicalizer conformance artifacts and adversarial guards."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/rcs-019"
VECTORS = BASE / "vectors-v1.json"
PY_IMPL = BASE / "reference.py"
JS_IMPL = BASE / "independent_verify.mjs"
REQUIRED = (
    ROOT / "docs/27-CANONICALIZER-CONFORMANCE.md",
    BASE / "README.md",
    BASE / "experiment-plan-v1.json",
    BASE / "conformance-spec-v1.json",
    VECTORS,
    PY_IMPL,
    JS_IMPL,
    BASE / "summarize.py",
    ROOT / ".github/workflows/rcs019.yml",
)

errors: list[str] = []

def fail(msg: str) -> None: errors.append(msg)

def load(path: Path) -> Any:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}"); return {}

for path in REQUIRED:
    if not path.is_file(): fail(f"missing required file: {path.relative_to(ROOT)}")

suite = load(VECTORS) if VECTORS.is_file() else {}
if suite:
    if suite.get("schema") != "rcs-019-conformance-vectors/1.0": fail("vector schema mismatch")
    vectors = suite.get("vectors", [])
    ids = [x.get("id") for x in vectors if isinstance(x, dict)]
    if len(ids) != len(set(ids)): fail("vector ids must be unique")
    required_families = {
        "unit_conversion", "ties_to_even", "integer_boundaries", "overflow_refusal",
        "q15_rotation", "transform_composition", "frame_graph", "timestamp_ordering",
        "semantic_segmentation", "subquantization_semantics", "curve_classification",
        "fit_certification", "sampling_invariance", "long_noisy_trace",
    }
    families = {x.get("family") for x in vectors if isinstance(x, dict)}
    missing = required_families - families
    if missing: fail(f"missing required conformance families: {sorted(missing)}")
    counts = {x.get("input", {}).get("sample_count") for x in vectors if x.get("family") == "long_noisy_trace"}
    if not {10000, 100000} <= counts: fail("long/noisy vectors must include 10k and 100k samples")
    sample_rates = [x for x in vectors if x.get("family") == "sampling_invariance"]
    if len(sample_rates) < 2: fail("need at least two equivalent-motion sampling vectors")

plan = load(BASE / "experiment-plan-v1.json") if (BASE / "experiment-plan-v1.json").is_file() else {}
if plan:
    if plan.get("schema") != "rcs-019-experiment-plan/1.0": fail("experiment plan schema mismatch")
    if plan.get("production_boundary") != "research-only": fail("RCS-019 must remain research-only")
    if plan.get("independent_decision_paths") != 2: fail("experiment plan must require two independent decision paths")
    protected = set(plan.get("protected_semantics", []))
    for item in ("canonical-journal-authority", "semantic-boundaries-before-fitting", "positive-removal-intent", "genesis-v1-history"):
        if item not in protected: fail(f"experiment plan missing protected semantic {item}")

spec = load(BASE / "conformance-spec-v1.json") if (BASE / "conformance-spec-v1.json").is_file() else {}
if spec:
    if spec.get("schema") != "rcs-019-canonicalizer-conformance/1.0": fail("conformance spec schema mismatch")
    if spec.get("journal_contract") != "msac-journal/1.0": fail("conformance spec must bind msac-journal/1.0")
    if spec.get("different_sampling_invariant") != "bounded-physical-equivalence": fail("resampled traces must use bounded physical equivalence")


def run(cmd: list[str], timeout: int = 20) -> tuple[int, dict[str, Any], str]:
    try:
        p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return 124, {}, "timeout"
    text = p.stdout.strip()
    try: payload = json.loads(text) if text else {}
    except json.JSONDecodeError: payload = {}
    return p.returncode, payload, p.stderr.strip()

if PY_IMPL.is_file() and JS_IMPL.is_file() and VECTORS.is_file():
    py_rc, py, py_err = run([sys.executable, str(PY_IMPL), str(VECTORS)])
    js_rc, js, js_err = run(["node", str(JS_IMPL), str(VECTORS)])
    if py_rc != 0: fail(f"Python independent path failed: rc={py_rc} {py_err}")
    if js_rc != 0: fail(f"Node independent path failed: rc={js_rc} {js_err}")
    for name, result in (("Python", py), ("Node", js)):
        if result.get("schema") != "rcs-019-run-result/1.0": fail(f"{name} result schema mismatch")
        if result.get("failure_count") != 0: fail(f"{name} reported vector failures")
    if py and js:
        py_map = {x["id"]: x["actual"] for x in py.get("results", [])}
        js_map = {x["id"]: x["actual"] for x in js.get("results", [])}
        if py_map != js_map: fail("independent Python and Node decision paths disagree")

    # Corrupt a known ties-to-even oracle. Both paths must detect the contradiction.
    if suite:
        corrupted = json.loads(json.dumps(suite))
        target = next(x for x in corrupted["vectors"] if x["id"] == "unit-half-nm-even-down")
        target["expected"]["length_nm"] = "1"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.json"
            path.write_text(json.dumps(corrupted), encoding="utf-8")
            prc, pout, _ = run([sys.executable, str(PY_IMPL), str(path)])
            jrc, jout, _ = run(["node", str(JS_IMPL), str(path)])
            if prc == 0 or pout.get("failure_count") != 1: fail("Python path did not reject adversarial wrong ties-to-even oracle")
            if jrc == 0 or jout.get("failure_count") != 1: fail("Node path did not reject adversarial wrong ties-to-even oracle")

        # Erase a material-body transition while leaving expected segmentation unchanged.
        corrupted = json.loads(json.dumps(suite))
        target = next(x for x in corrupted["vectors"] if x["id"] == "semantic-boundaries-all-contexts")
        target["input"]["samples"][-1]["body"] = "B1"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad-boundary.json"
            path.write_text(json.dumps(corrupted), encoding="utf-8")
            prc, pout, _ = run([sys.executable, str(PY_IMPL), str(path)])
            jrc, jout, _ = run(["node", str(JS_IMPL), str(path)])
            if prc == 0 or pout.get("failure_count") != 1: fail("Python path failed to detect erased semantic boundary")
            if jrc == 0 or jout.get("failure_count") != 1: fail("Node path failed to detect erased semantic boundary")

    py_text = PY_IMPL.read_text(encoding="utf-8")
    js_text = JS_IMPL.read_text(encoding="utf-8")
    if "independent_verify.mjs" in py_text or ("node" in py_text.lower() and "subprocess" in py_text):
        fail("Python implementation must not delegate to Node verifier")
    if "reference.py" in js_text or ("python" in js_text.lower() and "spawn" in js_text.lower()):
        fail("Node implementation must not delegate to Python reference")

report = ROOT / "docs/27-CANONICALIZER-CONFORMANCE.md"
if report.is_file():
    text = report.read_text(encoding="utf-8")
    for phrase in (
        "msac-journal/1.0", "ties-to-even", "q15", "100,000", "bounded physical equivalence",
        "Linux", "Windows", "independent", "polyline fallback", "no journal contract revision",
        "positive material-removal intent", "RCS-026",
    ):
        if phrase not in text: fail(f"RCS-019 report missing required phrase {phrase!r}")

workflow = ROOT / ".github/workflows/rcs019.yml"
if workflow.is_file():
    text = workflow.read_text(encoding="utf-8")
    for token in ("ubuntu-24.04", "windows-2022", "actions/setup-python@v5", "actions/setup-node@v4", "cross-platform"):
        if token not in text: fail(f"RCS-019 workflow missing {token!r}")

# Once a measured summary is committed, it becomes part of the acceptance gate.
measured_path = BASE / "measured-summary-v1.json"
if measured_path.is_file():
    measured = load(measured_path)
    if measured.get("schema") != "rcs-019-measured-summary/1.0": fail("measured summary schema mismatch")
    if measured.get("cross_platform_logical_identity") is not True: fail("measured summary lacks cross-platform identity")
    if set(measured.get("platforms", [])) != {"Linux", "Windows"}: fail("measured summary must record Linux and Windows")
    if measured.get("independent_paths_agree") is not True: fail("measured summary must record independent path agreement")
    if measured.get("all_vectors_match_expected") is not True: fail("measured summary must record all vectors pass")
    if measured.get("journal_contract_revision_required") is not False: fail("measured summary contract-revision conclusion mismatch")

if errors:
    for msg in errors: print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)
print("RCS-019 validation passed")
