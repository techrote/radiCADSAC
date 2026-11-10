# A2-VERIFY-004 — exact-parent qualification checkpoint (10 November 2026)

Status: **CORRECTIVE PATCH PUBLISHED; FULL EXACT-HEAD QUALIFICATION HOLD**. This is not an A2 mathematics admission, physical-source certification, production handoff, or MC-B/MC-1 gate action.

## Baseline and preregistered falsifier

Repository: `techrote/radiCADSAC`, sole A2 Draft PR [#471](https://github.com/techrote/radiCADSAC/pull/471). Accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; pre-correction A2 head `0b7efdafcef130a7fa8d9d99825b5f02fa909daa`; first four correction commits end at `6dd9da94388346336cb622db97424ca08411b9c8`. Scoped lease: [#324 / 6761556294](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6761556294).

A3's [independent review #5837604840](https://github.com/techrote/radiCADSAC/pull/471#pullrequestreview-5837604840) demonstrated unrestricted `dict == dict` admission with hostile Python `str` subclasses. The exact original consumers were `cyclotomic_moments.verify_receipt`, `cyclotomic_moments.verify_knot_receipt`, and `analytic_join.verify_join`. A3 independently executed **isolated predicates**, not the complete parent modules: 9 hostile fields passed the old predicates. Do not relabel that as an exact-parent test.

**Falsifier:** a genuine source-recomputed receipt accepts a claimed field with a subclass-defined equality operator, `True` substituted for an integer or `0` for `False`, a changed nested field, or changed source binding. Genuine canonical receipts must remain accepted.

## Source-scoped correction

- `cyclotomic_moments.py`: original Git blob `77b79335ffffb8382eb348afd44e7d9416f34583`; corrected blob `649b6dc6d5f74766ae285115dfd7600f2b6f6036`. Adds `strict_receipt_equal` and applies it after full source recomputation at both point and genuine-knot consumers.
- `analytic_join.py`: original blob `9983c0dc8c64ddc41d9ae41114b1735673c90614`; corrected blob `3c03c9552b853697e82d2a9ddb9e9f357706dd3c`. Applies the same source-recomputed guard.
- `test_moments.py`: corrected blob `ea3c5c9843cf617b02401ecc86207b497fcf7acb`. Added direct parent tests for genuine point/knot receipts, hostile scalar and nested fields, authority flags, source identity and `bool` vs `int`.
- `test_analytic_join.py`: corrected blob `aa74f48ae498f427826d5de37b634db2f16663c2`. Added actual analytic-join replay controls including hostile status, signed order, nested germ and false authority claims.

The guard admits only exact built-in `dict`, `list`, `str`, `int`, `bool`, and `None` matching the independently recomputed tree. Its structural type-soundness is a straightforward induction over the *finite trusted expected receipt tree*. It does **not** authenticate the provenance of physical B-spline controls, implement an open-root isolator or establish trust in arbitrary caller-provided producer source.

## Exact-head command ledger and blocker

**NOT EXECUTED in this run:** the full 4-module A2 published Python suite, the 3 additional challenge entry points, or independently replayed A3/B1 direct-module challenges. The available repository connector provided exact remote source blobs, PR/CI metadata and bounded source writes but no remote arbitrary-command runner. The local execution container had no checkout and could not resolve `github.com` or `raw.githubusercontent.com` (Git/curl DNS failure). Copying only cherry-picked functions would repeat A3's isolated-predicate exercise rather than meet the owner's full-parent execution requirement.

After fetching the *literal latest* PR head, independently run from `research/experimental/analytic-events/jets`:

```sh
git fetch origin pull/471/head
git checkout --detach FETCH_HEAD
git rev-parse HEAD
git status --short
cd research/experimental/analytic-events/jets
python3 -m unittest discover -v -p 'test_*.py'
python3 phase_gauge_probe.py
python3 factor_knot_challenge.py
python3 continuum_alias_challenge.py --a2-module ./cyclotomic_moments.py
```

The full suite must import real source modules on disk; check `git hash-object` against the Git blobs above and capture version, stdout/stderr, exit codes, and per-test results. The tests should separately replay A3 close-rate/mixed-rate, phase gauge, sided knot, source substitution, malicious equality and B1 consumer challenges. Any missing import/dependency or failed expectation is **CHANGES REQUIRED**, not a theorem or runtime GO.

At `6dd9da94388346336cb622db97424ca08411b9c8`, GitHub's generic quality workflow had succeeded and some historical workflow jobs were pending. Inspected quality job steps validate generic repository/RCS contracts, **not A2 jets**; thus they cannot substitute for A2's direct tests. CI must be rechecked at the final post-document head.

## Scope and limits

Original analytical proof claims remain hypotheses or bounded mathematical arguments pending exact tests and independent qualification. The source grammar does not independently authenticate original physical B-spline ancestry, arbitrary nonrational knots or phase reparameterisations owned by [#462](https://github.com/techrote/radiCADSAC/pull/462). Budget refusal never means nonzero; a local sided germ never proves full zero-set completeness. [#453](https://github.com/techrote/radiCADSAC/pull/453) and [#397](https://github.com/techrote/radiCADSAC/pull/397) own other integration surfaces; no production or MC-038 source has changed.

**Next action, owner:** independent A3 must run and falsify the exact A2 head; B1 must assess the receipt-type/physical-source bridge with direct consumer tests; A2 author must repair any new failure. No A2 Ready/merge/admission until the exact-source test log and challenges exist. Historical 121/20/30/50, all 26 operations, MC-B/MC-1 NOT_ESTABLISHED and `production_authorized=false` are unchanged.
