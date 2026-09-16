# RCS-004 OCCT 8.0.1 audit

Status: RCS-004 research artifact  
Audited upstream: `Open-Cascade-SAS/OCCT` `V8_0_1` / `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`

The RAG-quality audit is [`../../docs/12-OCCT-8.0.1-AUDIT.md`](../../docs/12-OCCT-8.0.1-AUDIT.md).

Machine-readable and reproducible assets in this directory are:

- `audit-map.json` — subsystem classification, evidence, reversibility, fork seams and unresolved questions;
- `probes/verify_occt_source.py` — source-layout/API probe for a local checkout of the exact audited OCCT commit.

## What the probe proves

The probe verifies the checkout revision/version and the source/API markers cited by the audit: B-rep entity tolerances, Boolean fuzzy/non-destructive/parallel controls, General Fuse/cell building, same-domain unification, validation, history, sweep machinery, meshing, STEP parameter/session APIs, global `Interface_Static`, atomic transient reference counts, and the shared-library/C++17 build baseline.

It does **not** prove robustness on the RCS-003 manufacturing corpus. Runtime behaviour belongs in RCS-006 onward.

## Reproduction

From repository root:

```text
git clone https://github.com/Open-Cascade-SAS/OCCT.git external/OCCT
git -C external/OCCT checkout b8f597c677811d1f9f4d8a97f5ae2825c0353a42
python research/rcs-004/probes/verify_occt_source.py external/OCCT
python tools/validate_repo.py
python tools/validate_rcs003.py
python tools/validate_rcs004.py
```

The local OCCT checkout is deliberately not vendored into `radiCADSAC`.
