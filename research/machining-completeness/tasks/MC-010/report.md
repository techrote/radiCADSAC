# MC-010 — Independent exact controls and oracle-independence foundation

Status: **COMPLETED_RESEARCH**. Issue: #72. Source baseline: `91b91f6d343b19b28c72c2465ef54dd9d0b0c169`.

## Purpose and bounded claim

MC-010 supplies a small exact control stack that can challenge material subtraction, a deliberately narrow class of actual sweeps, and volumetric connectivity without inheriting the historical RCS-021 shared-field decisive mathematics. It is an **independent deterministic control**, not a native geometry result, not a universal machining oracle, and not evidence that MC-B or MC-1 is established.

Hypothesis: finite unions of positive-volume axis-aligned rational cells are sufficient to provide independently derived adversarial controls for exact subtraction, axis-parallel translational sweeps, signed contact boundaries, body splitting, complete removal, retrace idempotence and face-connectivity.

Falsification criterion: MC-010 is not complete if its decisive control path must import/copy the historical shared-field implementation, accept floating/epsilon authority for exact predicates, infer a bridge from edge/point contact, erase positive-volume remnants, derive expected truth from candidate output, or silently claim cases outside its proved cell/sweep domain.

## Dependency and authority reconciliation

The required artifact dependencies are present: MC-002 fixes the machining-domain contract, MC-003 fixes exact-source/numeric semantics, and MC-009 fixes evidence-binding authority. MC-010 does not alter any of those contracts. The mandatory F01–F16 corpus remains `UNBUILT` under MC-011–014, and historical imports remain owned by MC-055.

No pre-existing MC-010 branch or PR existed when work started. No native or paid execution permit was required or used.

## Shared decisive mathematics found in the historical RCS-021 paths

The historical evidence is preserved, but its independence graph is narrower than some old wording suggested:

- `research/rcs-021/field.py` owns path expansion, segment/sweep removal-field functions, column-height mathematics and closed-form helpers.
- `research/rcs-021/material_oracle.py` imports `P`, `STOCK`, `column_height`, `known_volume`, `removal_field` and `segment_count` from that file. Its adaptive octree is representation-independent of candidate B-reps, but its decisive cutter/material field is not independently derived from `field.py`.
- `research/rcs-021/tridexel.py` imports `STOCK`, `clamp`, `column_height`, `segments` and `xy_distance` from the same file. It is a different representation/evaluation path, not an independent derivation of the shared sweep mathematics.
- `research/rcs-021/manifold_fallback.py` imports `final_field` and supplies it as the Manifold LevelSet callback. The external library therefore challenges reconstruction/evaluation behavior downstream of that callback, not the callback's cutter-sweep derivation itself.

This matches the current canonical `docs/machining-completeness/03-ORACLE-AND-CORPUS.md` warning that agreement among those RCS-021 paths cannot independently establish the shared field/sweep. MC-010 does not rewrite or invalidate the accepted historical measurements; it records the shared decisive lineage and adds a structurally separate challenge path.

The task contract pins the four historical blob identities. The cheap verifier fails if those protected historical source blobs are mutated.

## Independent exact control

`independent_exact_oracle.py` uses only Python's exact `Fraction` arithmetic plus small standard-library data structures. Its authority path contains no binary floating point, no epsilon, no import of RCS-021, no candidate geometry code and no MC evidence-verifier geometry logic.

The covered mathematics is deliberately small:

1. material is a finite disjoint union of strictly positive-volume axis-aligned boxes with rational coordinates;
2. box subtraction is an exact intersection followed by a disjoint six-slab partition of the surviving material;
3. a monotone rigid translation of an axis-aligned box along exactly one coordinate axis has an exact swept set equal to the coordinate interval hull;
4. material components connect only across positive-area shared faces. Edge and point contact do not connect 3D volume.

The contract binds the independent implementation by SHA-256 and restricts its import roots. Expected values are literal exact rationals in `oracle-foundation-v1.json`, not values copied from candidate output.

## Boundary and adversarial controls

Nine control groups are frozen:

- exact tangency removes zero positive volume;
- an exact `1e-6` signed gap/contact/penetration triplet keeps zero distinct without epsilon authority;
- a stock-spanning cut retains two bodies at exact volume `800`;
- two cuts preserve an exact positive-volume `1/1000000` web;
- a nonstationary axis-parallel sweep is derived exactly and leaves volume `840`;
- a swept stock-spanning cutter creates the same two-body split through an independently derived swept set;
- complete removal yields explicit empty material, volume zero and zero components;
- face contact connects while edge and point contact do not;
- repeating the identical exact cut is idempotent.

The verifier additionally rejects binary-float coordinates, degenerate material cells, source-digest drift, shared-decisive imports, candidate-defined expected truth and false independence metadata. It runs the MC-009 corrupted-evidence self-test as part of MC-010's cheap contract.

## What this result does not establish

MC-010 deliberately does **not** establish a general exact sweep for curved, rotated, helical, timed or phase-sensitive motion; arbitrary imported/B-rep stock; general topology beyond the exact cell complex; reconstruction; STEP usability; or correctness of any native geometry candidate. It does not convert RCS-021's sampled/field controls into independent proof by relabelling them.

The control's cell indices are ephemeral mathematical cells. They are not durable machining body IDs and do not create or guess lineage. Downstream fixtures must bind physical stock/tool/setup/history and durable identities through the MC-009 contracts.

## Programme and protected-state reconciliation

The full machining denominator remains unchanged. F01–F16 remain mandatory and unbuilt. MC-A remains accepted from MC-005; MC-B, MC-C, MC-D, MC-E, MC-F and MC-1 remain `NOT_ESTABLISHED`. Production remains unauthorized.

No Genesis/source/audio/provenance record, canonical journal meaning, durable body/lineage rule, historical failure, refusal or incomplete result was edited. Positive-volume material remains non-compensating: the `1/1000000` web control exists specifically to prevent tolerance from becoming deletion authority.

## Verification

Cheap deterministic verification:

```bash
python3 research/machining-completeness/tasks/MC-010/verify.py --contract
python3 tools/mc_evidence_verifier.py --self-test
python3 tools/mc_workflow.py verify MC-010
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py sync --check
```

The repository `mc1-static` workflow compiles and executes MC-010 alongside the completed planning/research task verifiers. No native campaign is part of this task.

## Downstream obligations

MC-011 through MC-014 may consume this exact foundation while building the physical F01–F16 fixtures, but they must supply fixture-specific independent oracle paths rather than claim that the small box-cell model covers the corpus. MC-015 still owns the deeper oracle/certificate independence review. General curved/timed/phase-sensitive, imported-geometry and native-candidate correctness remain open.

Any future change to the exact control source, its rational semantics, the pinned historical lineage inventory or the meaning of face-connectivity invalidates dependent MC-010 evidence and requires a reviewed new revision; historical producing evidence must not be rewritten in place.
