# PB-007-01 exact rational-turn endpoints

Status: **bounded constructive extension accepted by issue #170 only if exact-head and post-merge CI pass; PB-007-01 remains OPEN**.

This document extends, rather than replaces, `27-PB00701-EXACT-EVENT-BOUNDARY.md`. The v3 evidence remains historical authority for the exact constant-coefficient rational trigonometric-polynomial route on cardinal quarter-turn windows. The v6 route removes the cardinal-endpoint restriction for that same predicate family.

## Exact rational-turn representation

For an exact rational source turn `p/q`, the tangent-half coordinate used by the existing reduction is

`x = tan(pi * p/q)`.

Instead of rounding `x`, v6 represents it as the selected real root of the exact integer polynomial

`Im((1 + i x)^q)`.

The source turn itself selects the root on a pole-free principal tangent branch. An exact rational Sturm bisection isolates that root. The stored rational interval proves which algebraic root is intended; it is not a tolerance interpretation of the geometry.

For an exact event numerator `P(x)`, equality at the endpoint is decided by exact polynomial gcd with the endpoint polynomial. If equality is false, exact rational interval refinement eventually proves a constant nonzero sign. Successive derivatives give exact multiplicity. One-sided derivative signs feed the Sturm variation count, so open-window roots are counted without accidentally including a root exactly at a source endpoint.

No binary floating point, decimal tangent value, epsilon, sampling density, subdivision cap, timeout or resource refusal is correctness authority.

## Covered boundary cases

The deterministic verifier checks non-cardinal exact simple crossing and even-multiplicity tangency at turn `1/6`, a hidden interior root between non-cardinal rational-turn endpoints, exact endpoint equality versus strict open-window root counting, negative-turn and whole-turn-equivalent encodings, pole crossing, malformed source windows, source-parameter mismatch, forged direct tangent-half coordinates and binary-float input.

`RESOURCE_REFUSAL`, `UNCERTIFIED` and `BLOCKED` remain non-success states.

## What remains open

This removes arbitrary rational-turn endpoints as a blocker **only for finite constant-coefficient rational trigonometric polynomials**. The admitted source grammar also contains exact rational B-splines and polynomial path/feed pieces coupled to trigonometric spindle phase. No unconditional finite exact decision route for every required tangential, multiple-root or singular event in that broader coupled analytic grammar is established here.

Therefore:

- `PB-007-01` remains OPEN;
- `PB-007-02` remains OPEN and dependent on the unresolved general PB-007-01 event authority;
- PO-04, PO-05 and PO-08 remain OPEN;
- MC-B remains `NOT_ESTABLISHED`;
- MC-1 remains `NOT_ESTABLISHED`.

The next pre-gate work remains a focused PB-007-01 constructive/theorem pass on polynomial/B-spline-modulated phase predicates, not another MC-B acceptance retry.

## Protected semantics

The frozen denominator remains exactly 26 admitted operations. Historical source/audio/provenance is unchanged. Canonical-journal meaning, exact shared time/path/phase correlation, source uncertainty, positive-volume material, holder/access semantics, durable body/lineage identity and conventional STEP engineering-output semantics are preserved.

No native, paid, production or expensive campaign is authorized by this work.

## Verification

```text
python3 research/machining-completeness/tasks/MC-038/verify_pb00701.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701.py --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v6.py --contract
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_v6.py --self-test
```

The repository `mc1-static` workflow must pass on the exact PR head and again on the exact merged `main` SHA.
