# MC-043 provisional independent-consumer receipt preflight

Status: **PREPARATORY IMPLEMENTATION / NOT MC-043 COMPLETION** (30 October 2026).
Evidence class: **DETERMINISTIC_MODEL / local source-bound structural tests only**.
Coordination: [RAD-READY / Scheduswarm #324](https://github.com/techrote/radiCADSAC/issues/324), [MC-043 #105](https://github.com/techrote/radiCADSAC/issues/105).
Authoritative main when selected: 0b0e5231335e1e88e0b5a29f23c11343779090a3.

## Purpose and falsifiable boundary

MC-043 eventually needs a genuinely independent consumer to read exact native-produced STEP bytes, preserve the MC-054 MC-ENG-OUTPUT/1.0 material/body/lineage profile and execute a real downstream operation. MC-017 established only a source-viable BRL-CAD path, not a measured import. MC-040/MC-042 artifacts remain unaccepted, so native STEP/BRL-CAD qualification is **not dependency-ready**.

This independent RAD-READY subtask adds a small fail-closed *receipt-integrity preflight* under MC-043 without starting a native/paid campaign or claiming capability. The hypothesis is that a proposed manifest+consumer receipt can be rejected if it binds the wrong original STEP bytes, loses/duplicates/fuses body-level STEP items, substitutes producer geometry for the independent import, accepts partial/repair import, invents empty STEP material, or silently discards empty lineage transitions.

The hypothesis is falsified if the checker accepts any of those controlled mutations or returns a native/MC-E success claim merely because the structural checks pass.

## Executable artifact

- **consumer_receipt_preflight.py**: checks an MC-054-profile-inspired manifest and provisional consumer receipt against exact raw manifest SHA-256 and streamed on-disk STEP artifact SHA-256, enforces nonempty source-body/STEP-item inventory consistency and strict/no-repair receipt flags, and applies the manifest-only EMPTY_MATERIAL branch with exhausted lineage, zero STEP artifacts, zero importer calls and EMPTY_NO_GEOMETRY follow-on.
- **verify.py**: constructs two deliberately **synthetic, non-STEP-byte** positive structural controls (two-body exact-zero-contact grouped case and exhausted empty case) and demands rejection of 34 adversarial mutations. No real producer, importer or geometry operation participates.

Both scripts use only the Python standard library. They do not modify existing proof/toolchain/source or shared programme files.

For a future receipt package, run the consumer_receipt_preflight.py script with --manifest, --receipt and --artifact-root pointing respectively to the raw JSON manifest, raw JSON receipt and STEP artifact directory. It returns STRUCTURAL_PREFLIGHT_ONLY on structurally acceptable metadata; exit 2 means rejection. Its receipt representation is **a provisional preflight interchange**, not a promoted global MC-054 output schema. Future MC-042/MC-043 real-run adapters must preserve the invariants and independently supply verified producer/consumer provenance.

## Source-matched checks

Commands executed locally using Python 3 on the exact bytes later submitted to the PR:

- python3 -m py_compile consumer_receipt_preflight.py verify.py
- python3 verify.py --contract --self-test

Observed output:

    MC-043 PROVISIONAL STRUCTURAL_PREFLIGHT_ONLY: 2 positive synthetic controls; 34 rejected corruptions
    No real STEP file, independent consumer process, native permit or MC-E capability qualified

Submitted Git blob SHA-1 identities (rechecked against locally tested exact bytes):

- consumer_receipt_preflight.py: 2333c2050fbad0c3f1a6f987240265f4e7a78ab9
- verify.py: 5cdf9dcf3d8c12873dae7f623101522ba6652ae9

Negative controls cover source/manifest binding drift; missing/duplicated/fused or invented STEP/body items; path traversal, symlink and raw-byte alteration; partial, repair, non-strict, invalid-preserved and nonzero-exit imports; producer replay and dropped/duplicated downstream operands; duplicate representation-piece/STEP-item ownership, uncertified material seam/contact binding; empty fake geometry, importer/follow-on invocation, lineage loss; false capability claims; and duplicate JSON object keys. Negative test definitions are retained in verify.py.

## What this does NOT establish

The verifier **does not parse STEP**, verify STEP schema/B-rep regularity, prove canonical material equality, measure native body identity, independently bind actual BRL-CAD imported object IDs to raw STEP, validate gqa error budgets or prove the downstream operation physically consumed imported geometry. Receipt assertions are still assertions until backed by raw logs and independently observed consumer process evidence. Even synthetic non-STEP bytes can pass a structurally honest self-test: that is intentional to demonstrate this boundary. A STRUCTURAL_PREFLIGHT_ONLY response cannot be promoted to CAPABILITY_ACCEPTED.

It also does not validate underlying material-certificate or lineage file bytes; it checks their declared digest consistency between manifest and receipt. Those source artifacts require a separate custody verifier.

MC-043's actual independent engineering-use acceptance remains **OPEN**. MC-054 blockers RB-016-01 through RB-016-05, XB-017-01, and MC-B/C/D/E/F/MC-1 gates remain unchanged. No native permit, STEP run, resource campaign, provider selection, operation narrowing, global output schema authority change or production authorization is implied.

## Dependencies, integration and next step

Formal MC-043 artifact dependencies: MC-017 (reviewed source-level route), MC-040 (pending real material journey) and MC-042 (pending exact STEP A–C artifact). MC-054 defines output-profile semantics; MC-045 is a static campaign permit/accounting mechanism, not a live permit.

Next distinct useful independent readiness step: adapt a source-bound MC-043 consumer process/evidence adapter to supply immutable importer logs and actual process exit/report bytes to this preflight, while keeping all capability claims blocked until MC-040/MC-042 provide real source-matched inputs. Alternatively construct an independent valid-but-materially-wrong imported-object negative control. No actual native qualification is implied until a separately permitted, source-bound experiment runs.

These new isolated MC-043 files cannot race RAD-PROOF's MC-038/PB-007/V27 proof write set. Shared policy/proof/programme/authority/roadmap registries are untouched.
