# RCS-019 canonicalizer conformance harness

This directory contains the research-only executable conformance substrate for RCS-019. It tests the accepted `msac-journal/1.0` normalization semantics without selecting a production serialization, RPC layer, database, game-input mapping, or geometry kernel.

## Files

- `experiment-plan-v1.json` — hypotheses, falsification criteria, protected semantics and resource limits.
- `conformance-spec-v1.json` — executable interpretation of the accepted journal rules plus explicit parameters for the RCS-019 reference normalization policy.
- `vectors-v1.json` — hand-authored expected vectors. The vectors are the oracle; neither implementation is allowed to generate its own expected answers.
- `reference.py` — Python exact-integer/rational decision path.
- `independent_verify.mjs` — separately implemented Node.js/BigInt decision path.
- `summarize.py` — emits per-platform logical signatures and combines Linux/Windows evidence.
- `measured-summary-v1.json` — added only after hosted Linux/Windows evidence has actually passed and been inspected.

## Local validation

```text
python3 tools/validate_rcs019.py
python3 research/rcs-019/reference.py research/rcs-019/vectors-v1.json
node research/rcs-019/independent_verify.mjs research/rcs-019/vectors-v1.json
```

`tools/validate_rcs019.py` runs both paths, requires exact agreement with the independent expected vectors, enforces a 20-second containment limit per path, and then deliberately corrupts a ties-to-even oracle and a material-body semantic boundary. Both implementations must detect those adversarial mutations.

## Cross-platform evidence

`.github/workflows/rcs019.yml` runs the same suite on pinned Python 3.12 and Node 22 setup actions on `ubuntu-24.04` and `windows-2022`. Each platform publishes a normalized logical SHA-256 signature. The final workflow job fails unless Linux and Windows both exist and the logical signatures are identical.

Runtime/platform strings are evidence metadata only. The durable conformance result is the logical decision set, not interpreter object identity or byte-for-byte process output.
