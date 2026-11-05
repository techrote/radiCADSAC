# MC-046 — PLAN_ONLY proposal descriptor/path identity refusal (5 November 2026)

**Issue:** [MC-046 #108](https://github.com/techrote/radiCADSAC/issues/108). **Evidence class:** deterministic local-filesystem/CI contract test only. **Status:** isolated proposed ingress repair; does **not** establish native geometry, scale, STEP or MC-F.

## Defect and falsifiable criterion

The accepted bounded reader in `readiness.py` previously checked `Path.lstat()` for file type and size, then opened the pathname without comparing the opened file identity with that inspected pathname. A real replacement between the operations could be read as though it were the originally checked file. Hard-linked aliases were likewise not refused. The `PLAN_ONLY` schema's exact-pinned content validation still prevented native authorization or a false T2 qualification; the weakness is *local evidence-file custody and source provenance*, not a production-permit escalation.

**Acceptance criterion:** an ordinary one-link regular proposal is accepted exactly when matching the canonical source-pinned `PLAN_ONLY` plan, while a directory, symlink (where creation is available), hard-link alias (where creation is available), bounded oversize input, and an actual pathname replacement between `lstat` and `open` are refused. Both descriptor and pathname identity and stable size/mtime/link-count fields are checked across the held-descriptor read; POSIX ctime is also checked. Windows path and descriptor ctime observations are not treated as equivalent because actual hosted execution showed otherwise. Failure to obtain a useful filesystem file ID refuses rather than asserting custody.

## Implementation and tests

Write set: `research/machining-completeness/tasks/MC-046/readiness.py` and this task-scoped record only. No changes to mathematical source, MC-004 accepted qualification contract, static workflows, frozen source census, gates, authority, native runtime or production repositories.

`read_proposal` now checks one-link regular-file metadata, descriptor identity via `os.fstat`, pathname identity via `Path.lstat`, and pre/post file metadata (device, inode, link count, size and mtime on both platforms; ctime additionally on POSIX). Read length remains bounded to 1 MiB + 1 byte. Byte-limit controls deliberately run before identity disagreement controls for the after-stat-growth case so that the existing reproducible resource-hazard evidence is preserved.

The self-test tests genuine files and executes a deterministic actual rename/replacement between `lstat` and `open`. The successor pathname is independently accepted once the new file stands alone. Real hard-link and symlink creation are attempted and refused when supported; unsupported creation is printed and not counted as exercised. Existing 26 structural-plan mutation tests, 6 malformed JSON tests, 4 resource/depth tests, regular-file/oversize/growth negative tests and canonical valid plan controls remain. Expected refusal count: 40 plus 0–2 supported alias controls; do not misreport skipped alias cases as executions. The first literal-head Windows run [#42121866136](https://github.com/techrote/radiCADSAC/actions/runs/42121866136) failed on a genuine ordinary file, and diagnostic [#42122094816](https://github.com/techrote/radiCADSAC/actions/runs/42122094816) identified `st_ctime_ns` differing between `lstat` and `fstat` even for that file; the guarded revision excludes only this noncomparable field on Windows while retaining it on POSIX. These failures are retained, not recast as passes.

**Commands:**

```bash
python3 research/machining-completeness/tasks/MC-046/readiness.py --self-test
python3 research/machining-completeness/tasks/MC-046/readiness.py --contract
python3 tools/validate_machining_completeness.py --self-test
python3 tools/mc_workflow.py ready
```

The existing `.github/workflows/mc1-mc046-t2-readiness.yml` Linux/Windows workflow and `mc1-static` must qualify the *literal* branch head; a green workflow against another SHA is not evidence. Record terminal run IDs, exact checked-out commit and any failures in the PR handover.

## Limits, safety and downstream dependency

Metadata snapshots on cooperative local filesystems are **not an atomic authority-file transaction, cryptographic origin proof, hostile-filesystem guarantee, or a defense against a writer able to restore metadata while modifying bytes**. They provide bounded detect-and-refuse custody for supported path/descriptor races. OS-denied replacement and unsupported alias creation are not positive execution evidence.

The result is a prerequisite-quality `PLAN_ONLY` preparatory guard. It does not materialize any real 10/100/1000/10000 geometry-changing sections, qualify an MC-RH-Q1 native run, prove MC-038/PB-007, accept MC-B/D/F/MC-1, authorize paid execution or permit manufacturing. All 26 operation IDs remain mandatory.

## Handoff

Require distinct-session source-level review, literal-head Linux/Windows/static CI, protected integration against refreshed `main`, landed blob identities and merged-main CI. Keep any failing job logs and intermediate failed heads discoverable. Never merge merely because the deterministic MODEL_ONLY controls pass.
