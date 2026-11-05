# MC-045 — Descriptor-pinned permit/plan JSON ingress (5 November 2026)

## Scope, authority and classification

Task **MC-045 #107**, under accepted DR-0026/MC-1 and the current authority `handoffs/current-authority.json`. Base main `e2e824c0bb99e140a4db92adcca49d98fe072627` (post-#415). Existing MC-045 strict JSON, duplicate-key, Unicode, nesting and 1 MiB byte-refusal controls remain in force.

This is **PLATFORM/PROCESS and DETERMINISTIC_MODEL** local-file validation, not native geometry or independent STEP. It does not update the existing MC-045 outcome/gates, any frozen evidence, issue #100, the MC-038 mathematical proof owner, production controls or the 26-operation denominator.

## Hypothesis and falsification criterion

Before this change, `campaign_harness.py::load_json` used `Path.open("rb")`, read a bounded buffer, and parsed it, but did **not** reject a symlink, an unregistered hard link, a special file, or a pathname replaced while its old descriptor was still being read. A valid decoded JSON object alone does not establish which local inode was read. This was a custody limitation, not evidence that a native campaign was actually dispatched through such an attack.

Fail-closed requirement: no accepted permit/plan JSON may be returned if the final pathname is a special file, hard-linked, a symlink, or different between the pre-open name inspection, opened descriptor, and post-read name inspection. Preserve the existing valid MODEL_ONLY permit/plan and exact JSON semantic checks.

## Implementation and executable challenge

`research/machining-completeness/tasks/MC-045/campaign_harness.py` now:
- Inspects `lstat`, demands regular file, a nonzero inode and link count exactly 1, then `os.open` with `O_RDONLY`, binary/no-follow/nonblock flags when provided by the OS.
- Matches regular-file `fstat` identity to pre/post `lstat`, reads the existing bounded buffer from that **one checked descriptor**, checks descriptor and pathname snapshots after read, and converts `OSError` to typed `ContractError`.
- Compares `st_ctime_ns` only within the same observation route (descriptor-to-descriptor; pathname-to-pathname), not Windows descriptor ctime against pathname ctime.
- Retains duplicate-key refusal, byte and nesting limits, canonical scalar validation and all existing permit/plan validation; it is **not** a new authority/signature source.

Run the direct executable controls:

```bash
python3 research/machining-completeness/tasks/MC-045/campaign_harness.py self-test
python3 tools/validate_machining_completeness.py
```

The actual `self_test()` adds:
1. Valid original permit and plan file reads, with accepted depth/size boundary controls unchanged.
2. A directory/nonregular negative refusal (always executed).
3. Hard-link rejection for both names when creation is supported; otherwise skip with no false claim of exercised link creation.
4. Symlink refusal when creation is permitted (unprivileged Windows may deny creation).
5. An injected **same-byte-length, different-permit** `os.replace` immediately **after** opening the original file. On POSIX, where the rename succeeds, identity mismatch must refuse; on Windows, an OS-denied replacement must remain distinguishable from a Python-detected successful swap.

## Limits and downstream prerequisites

This is a cooperative local-filesystem custody check, **not** an atomic authority transaction, malicious-filesystem security boundary, signature/cryptographic authenticity, cross-host synchronization, directory-component traversal guarantee or protection against an adversary able to suppress metadata changes. Repeated in-place mutation with perfectly restored timestamps and inode identities remains beyond the contract. A permit still cannot authorize a paid/native campaign without distinct authority.

PB-007-01..04, MC-B, MC-D/E/F and MC-1 remain **NOT_ESTABLISHED/OPEN as applicable**; no native solids, STEP import, benchmark or manufacturing result follows. Full MC-F and MC-1 acceptance requires separately accepted mathematical, native and independent-consumer evidence and preregistered resource envelopes.

## Source custody and handoff

Files changed: this task-scoped RAG document and `campaign_harness.py` only. Coordinated in [issue #324](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6667128721). All tests are MODEL_ONLY and can run on hosted Linux and Windows; exact-head CI identity, negative observations, review and any merge decision must be recorded on the PR, not inferred from this prospective description.
