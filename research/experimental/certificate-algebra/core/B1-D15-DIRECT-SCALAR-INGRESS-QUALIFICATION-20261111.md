# B1-D15 — Hostile direct scalar ingress at E5 consumer

Status: **bounded Python research GO / cross-producer and native HOLD / do not merge**. Date: 11 November 2026. Owner lane: B1, exclusively `research/experimental/certificate-algebra/core/**`.

## Baseline, evidence identities and provenance

- Accepted repository main on inspection: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. B1 Draft PR #473 started this cycle at `db930b3cff1a49c42b61d26574805eeb25289405`.
- Original 25 source/test/benchmark Python files were reconstructed from the D14 literal-head archived source tree and independently compared against published Git blob SHA-1 values. Original complete B1 suite: **98/98 PASS**, CPython 3.13.5, no skips.
- Changed *only* three existing B1-owned paths:
  - `certificate_algebra.py`: `bdc4858d078ac2039d4b6244017b0c89c971eecc` → `556cced13e13f848a632e4c430fe3e6304236acc`.
  - `test_certificate_algebra.py`: `53772a1e29746242d1d798b926238099ce6bcf86` → `609e8a99d26cef5e1c3d6dfa0e3e894d16e4cca0`.
  - `test_quotient_sided_germ.py`: `a41c49c3b43e1b0bc372bc67b554c83e305b66de` → `15226d9066be1cc1a09201480b1dba4915fda8ff`.
- After guarded B1-only commits, live PR directory listing independently matched all **25/25** local Python Git blobs. No unrelated production, A1/A2, MC-038, native or shared paths touched.

## Hypothesis and falsifier

Hypothesis: the shared `certificate_algebra.frac` parser refuses any untrusted Python subclass *before* invoking user-defined equality hooks; its consumers `quotient_sided_germ.derive` and `project_signed_affine` therefore preserve canonical primitive scalar admission.

**Falsified on the original current B1 source.** `frac` previously checked `isinstance(s, str)`, then compared `enc(q) != s`. The right-side `str` subclass can override `__ne__`. A subclass carrying noncanonical `"-0"` could return `False` and be accepted as rational zero. A subclass raising from `__ne__` executed attacker-defined code before E5 returned an admissible/refusal result. The exact real consumer `derive` first completed genuine E4 parent/quotient replay, then invoked the hostile `time` parser; the affine prediction invoked the hostile `offset` or `rate` parser. This is an **ingress integrity / uncontrolled hook execution defect**, not an independently observed false zero-set theorem or a demonstrated unauthorized producer ancestry.

The **original 98/98 tests passed**, but the two added real-module tests failed, recording four failing subcases (direct canonical parser, E5 time, E5 affine offset, E5 affine rate).

## Minimal correction and verification

Use `type(s) is str` rather than `isinstance(s, str)` at the shared bounded `frac` ingress. Exact builtin strings, strictly canonical fraction encodings, 1024-bit numerator/denominator bounds, and all existing legitimate E5 semantics remain unchanged. The new tests assert rejection of both bypassing and raising subclasses **without invoking their hooks**, plus successful genuine quotient/germ replay and positive signed-affine projection.

From the literal source directory:

```sh
python3 -m unittest discover -p 'test_*.py' -v
python3 -m compileall -q .
python3 experiment.py
python3 bench_b1_fair_boundary_20261110.py
```

**Complete corrected suite 100/100 PASS** in 0.983 s (CPython 3.13.5, 0 failures/skips); compile and deterministic proof experiment PASS. Includes Bernstein parent, all E1–E7 consumer tests, hostile primitive/equality/identity/hash substitutions, deep/nested inputs, affine/split invalidation, 512-piece closure cap, and output rational budgets. The rerun is **all original consumer tests**, not a standalone replacement probe.

The fair 32-piece/64-edit, five-repeat symmetric Python deterministic benchmark retained exact per-edit snapshot hash parity. Median workloads (ms): efficient fresh full reproof **79.1227**, trusted incremental **30.6131**, full reproof plus strict readmission **203.5340**, incremental plus strict readmission **153.4808**. Respective ratios **2.58×** and **1.33×**. These measure *Python model algebra only*; receipt custody, E5 end-to-end cost, native geometry, STEP consumers, nonlocal simulation dependencies and external verification overhead are unmeasured. No native performance, physical zero-set or engineering-export improvement is claimed.

## Producer boundary and independent review

A1 #470 was directly executed in an earlier B1 cycle using literal producer blobs at `fe0dada7c430053c4c387f17a062909da9aab8bc`, but **not rerun in this D15 cycle**. A1's model zero event is not a B1 authenticated current-head source. Current A2 #471 at `d9cb56e74e876efb203e04003aadcf8bd368a369` remains **NOT EXECUTED in B1**, and the previously recorded A2 source-identity falsifier remains unresolved. B1's codec still stamps historical producer-head pins; **do not** treat those as current producer provenance or invent the original B-spline controls, knots or physical window. Request A3/B5 independent exact-current-head B1 and actual current A2 producer execution before any broadened source acceptance.

## Scoped GO / HOLD / NO-GO

- **GO:** bounded static Python B1 parent/certificate and E5 regression only, source-pinned test results with locally reproduced correction.
- **HOLD:** independently authenticated live A1/A2→B1 receipt transfer, original physical spline source lineage, independent A3/B5 second-source execution, native/STEP recomputation economics, reviewer admission and Draft merge.
- **NO-GO:** producer revision self-stamping as ancestry; promoting these deterministic Python results to physical solver, Boolean/topology closure, MC-B/MC-1, or production authorization.

Retain immutable 121/20/30/50 census and all 26 machining operations. MC-B/MC-1 remain **NOT_ESTABLISHED**, `production_authorized=false`. No paid/native run, production bootstrap or source-owner crossover. Distinct theorem/closure results from B1-C1/C2 are unchanged; D15 is an implementation ingress falsifier and bounded repair, not a new mathematical theorem.
