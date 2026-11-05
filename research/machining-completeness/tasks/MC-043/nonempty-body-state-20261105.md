# MC-043 — Nonempty durable-body state coherency refusal (2026-11-05)

**Status:** source-level structural preflight/negative-test increment. **NOT MC-043 completion, native STEP qualification, MC-E acceptance or manufacturing authorization.**

## Authority and source boundary

- Programme: DR-0026 and MC-1, `NOT_ESTABLISHED`; user-mandated 26 machining operations remain intact. Parent [MC-043 #105](https://github.com/techrote/radiCADSAC/issues/105).
- Output profile: `research/machining-completeness/tasks/MC-054/engineering-output-profile-v1.json`, `MC-ENG-OUTPUT/1.0`. EO-054-01 describes regular nonempty manifold material; EO-054-02 describes multiple distinct durable bodies requiring grouped geometry and non-fusion; EO-054-04 permits grouped representations of singular single-body material. Ordinary single-body `NONEMPTY`, multibody `NONEMPTY_GROUPED`, and manifest-only `EMPTY_MATERIAL` are different semantic states.
- Accepted preflight: `consumer_receipt_preflight.py`; executable source-level tests: `verify.py`. This is a provisional consumer **metadata preflight** only. The synthetic files contain deliberate NON-STEP bytes and do not establish imported geometry.
- Claimed isolated source coordination: [#324](https://github.com/techrote/radiCADSAC/issues/324); independent of MC-038/PB-007 proof owner, historical frozen corpora and issue #100.

## Defect, falsifier and repair

The pre-existing nonempty check required a nonzero durable-body inventory and a bijective *coverage* of each body by STEP item IDs, but it did not enforce the distinct state classifier for regular vs grouped material. Consequently the same otherwise internally consistent **two-body** grouped manifest and independent-consumer receipt could be relabelled `material_state: NONEMPTY` without losing an item or breaking any digest and would still pass. This is a semantic false acceptance of a multibody record under the single-body state; byte hashes alone cannot detect it.

The bounded change requires `len(durable_bodies) == 1` **only** for `NONEMPTY`. It intentionally permits a single canonical body represented as grouped pieces under `NONEMPTY_GROUPED`, including the separately governed singular case, and does not reinterpret physical geometry. It leaves nonempty item↔durable-body coverage, lineage digests, exact STEP byte custody, empty-transition handling, strict/no-repair import and follow-on rules unchanged.

Falsification condition: a two-body source/receipt pair relabelled solely to `NONEMPTY` passes; or a fully bound regular one-body `NONEMPTY`, valid two-body `NONEMPTY_GROUPED`, or legitimate empty manifest is rejected.

## Deterministic evidence and scope

`python3 research/machining-completeness/tasks/MC-043/verify.py --contract --self-test` executes the actual `check()` and exact-file hash path on three synthetic positive states (single body; grouped two-body with exact-zero contact; empty material), and forty adversarial controls. The new negative mutation keeps the two-body manifest, receipt item/file inventories, source digests and original synthetic STEP bytes otherwise consistent, changing only `material_state` and requiring a **specific** rejection message. Existing corruption, filesystem alias and Windows/Linux controls remain.

Run `python3 tools/validate_machining_completeness.py` and the existing MC-043 hosted Windows/Linux workflows against the **exact PR head**, retaining any failures. A green deterministic model is not evidence of real native STEP correctness or independent importer execution.

## Handoff and gates

Pending source-matched independent review, exact-head CI and conditional integration. MC-017 consumer route and MC-054 profile are reviewed research inputs; source-authenticated MC-040/MC-042 native inputs and genuine independently measured engineering follow-on remain prerequisites for full MC-043. PB-007-01/02/03/04 and MC-B, MC-E, MC-F and MC-1 remain OPEN / `NOT_ESTABLISHED`. No capability gate, production authority, operation scope, source-corpus census or mathematical evidence changes.
