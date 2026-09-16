# RCS-003 adversarial manufacturing corpus

Status: accepted research artifact candidate for issue RCS-003  
Corpus schema: `rcs-003-corpus/1.0`

This directory contains the implementation-independent adversarial manufacturing corpus used by later benchmark, tolerance, provenance, topology and solver research.

Authoritative semantics live in [`../../docs/11-ADVERSARIAL-MANUFACTURING-CORPUS.md`](../../docs/11-ADVERSARIAL-MANUFACTURING-CORPUS.md). Machine-readable assets are:

- `corpus.schema.json` — structural schema for corpus manifests;
- `corpus-v1.json` — versioned parameterized fixture-family catalog.

The corpus deliberately describes **physical manufacturing intent and expected result classes**, not expected OCCT/CGAL/mesh-kernel output. A later harness materializes concrete members from the declared parameter axes, records backend-specific observations separately, and never overwrites the fixture's physical oracle with a backend result.

## Reproduction / validation

From repository root:

```text
python tools/validate_repo.py
```

The repository validator checks schema identity, required fields, unique fixture-family IDs, explicit dimensional/frame/tolerance metadata, required coverage classes, expected result policy, parameter axes, connectivity expectations and lifecycle metadata.

## Versioning

`corpus-v1.json` is immutable once consumed by benchmark result records. Corrections that change physical intent, parameter domains, expected result classification, units/frames, or tolerances require a new fixture revision or corpus version. Editorial clarifications may update documentation without silently changing machine-readable semantics.
