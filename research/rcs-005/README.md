# RCS-005 STEP conformance assets

Status: RCS-005 research artifact candidate  
Contract: `msac-step-conformance/1.0`

This directory contains the machine-readable companion to [`docs/13-STEP-CONFORMANCE-CONTRACT.md`](../../docs/13-STEP-CONFORMANCE-CONTRACT.md).

## Files

- `conformance-v1.json` — programme-level export success/refusal contract, AP242-family target, validation layers, body policy, accuracy fields and failure taxonomy.
- `fixtures-v1.json` — minimal conformance matrix for RCS-006 and later backend/export testing.

## Interpretation

The JSON files define the programme oracle. Backend observations belong in later result records and must not rewrite expected physical/export semantics.

`occt-8.0.1-ap242dis` is a **baseline exporter profile identifier**, not a claim that OCCT's `AP242DIS` mode is certified against ISO 10303-242:2025 Edition 4.

The fixture accuracy values are research acceptance budgets for those fixtures. They are not global manufacturing tolerances. Production requests must carry explicit versioned accuracy policy and may be tighter.

## Validation

From repository root:

```text
python3 tools/validate_rcs005.py
```

The validator checks required gates, result/failure taxonomy, AP242 claim boundaries, solid-representation requirements, unit coverage, body-preservation rules, fixture coverage and the negative refusal case.

RCS-006 should additionally implement actual STEP generation/read-back metrics and record exact toolchain/dependency versions.
