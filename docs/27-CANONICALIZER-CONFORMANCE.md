# RCS-019 — canonicalizer conformance and deterministic normalization qualification

Status: accepted research result — merged via PR #50  
Date: 2026-09-17  
Issue: RCS-019 / GitHub #38  
Journal contract under test: `msac-journal/1.0`  
Conformance suite: `rcs-019-canonicalizer-conformance/1.0`

## Purpose and scope

RCS-002 deliberately defined canonical manufacturing meaning before choosing production persistence or a geometry backend. RCS-019 turns the numerics and normalization portions of that logical contract into executable conformance evidence. It tests durable physical meaning only: fixed quantities, q15 orientation tokens, transforms, stable duplicate-timestamp handling, semantic boundaries, bounded fit/refusal decisions, resampling invariants and long analogue traces.

This work does **not** define a gamepad mapping, database, RPC protocol, production canonicalizer service, OCCT convention, or user-facing machine-control implementation. Genesis-v1 handoffs and accepted source/provenance history remain unchanged.

## Hypotheses and falsification

The primary hypothesis is that two separately implemented exact-integer/rational decision paths can assign the same logical canonical meaning to the same normalized physical trace under one explicit normalization policy. The result is falsified by any unexplained Python/Node disagreement, any Linux/Windows logical-signature divergence, loss of a semantic boundary, hidden signed-64-bit wraparound, or acceptance of an uncertified fit.

For differently sampled traces, the programme invariant remains **bounded physical equivalence**, not arbitrary byte identity. Two deliberately simple physical motions—a line and a two-leg V path—are sampled at 11, 101 and 1,001 points and reduce exactly to the same line/polyline. This is stronger evidence for those fixtures without changing RCS-002's weaker general guarantee.

## Independent decision paths and oracle discipline

`vectors-v1.json` contains hand-authored expected outcomes derived from the accepted RCS-002/DR-0006/DR-0007 rules. The Python implementation and Node.js implementation both consume those expectations; neither generates them. The implementations use different source code and native arbitrary-precision integer mechanisms (`int` and `BigInt`) and do not call each other.

`tools/validate_rcs019.py` also corrupts two expected conditions on purpose. A wrong ties-to-even half-way result must be rejected by both paths, and erasing a target material-body boundary while leaving the expected segmentation unchanged must also be detected. This prevents a mutually self-consistent implementation pair from being mistaken for an independent oracle.

## Exact numeric qualification

The suite checks exact millimetre/inch equivalence (`25.4 mm == 1 in == 25,400,000 nm`), positive and negative signed-64-bit endpoints, one-token overflow on each side, and exact half-way ties-to-even for positive and negative quantities. No binary floating-point number is part of the expected logical result.

Quaternion q15 cases cover sign canonicalization, an independently quantized quarter-turn, the exact zero quaternion, a near-zero invalid quaternion, the inclusive reference-policy norm boundary and one token beyond it. The test policy's admissible q15 norm deviation is explicitly two q15 tokens. That number is a versioned normalization-policy parameter, not manufacturing tolerance.

## Transform and frame qualification

Transform vectors use the RCS-002 child-to-parent, column-vector convention. Exact 180-degree quaternion rotations avoid introducing a floating-point oracle while making composition order observable: reversing either transform changes the expected point. Frame-graph vectors separately require deterministic root-to-child ordering and refusal of a cycle.

A setup/frame revision change is also a semantic segmentation boundary. It cannot be smoothed through as if it were merely a nearby coordinate sample.

## Timestamp and semantic-boundary qualification

Duplicate physical timestamps use the explicit RCS-019 policy rule `stable-source-order`; the vector checks that stable order directly. Fitting segmentation is independently forced at engagement, tool-revision, setup/frame-revision and target material-body changes.

The sub-quantization fixture is deliberately important: two physical samples quantize to the same nanometre token, but an engagement transition remains two semantic sections. Quantization cannot erase an event. This is consistent with DR-0010: **positive material-removal intent** and process meaning are not converted to a no-op because numerical resolution is convenient.

## Curves and certified fitting

Line and polyline behavior is exercised through the equivalent-motion traces. Circular-arc vectors cover an ordinary quarter arc, a near-zero sweep, a near-full-circle sweep and a fit whose measured error exceeds its allowed bound. Ambiguous arc cases take a **polyline fallback** rather than inventing an arc.

Cubic-B-spline decision vectors test the exact certified-error boundary and one nanometre beyond it. The latter must also use polyline fallback. The reference arc guards (`100 nrad` near zero/full circle) are test-policy parameters, not a retroactive reinterpretation of historical RCS-002 journals.

## Long/noisy analogue traces

The deterministic analogue generator uses a specified 64-bit LCG solely to create reproducible test noise. Required 10,000- and **100,000**-sample traces vary by at most ±3 nm around a known line, with endpoints fixed. Both implementations must measure the same 3 nm maximum deviation and accept the line only because the declared fit budget is 3 nm.

Each conformance path has a 20-second validation containment budget; hosted CI jobs have a ten-minute outer limit. Runtime is a tractability observation, not a manufacturing-semantic input.

## Cross-platform qualification

Hosted workflow run `35271407927` passed both platform jobs and the final cross-platform logical-identity gate on source head `47e621769a7ac277f400a46f292794566427e214`. All 32 vectors matched their independent expectations on both platforms, the Python and Node decision paths agreed on each platform, and both produced logical signature `120e693501ae003b384831c669a40b3ff980ea9d3e8de65e0d87a63888310405`.

The Linux observation used Ubuntu 24.04.5 LTS / runner image `ubuntu-24.04` version `20260907.300.1`, CPython 3.12.14 and Node.js 22.23.2. The Windows observation used Windows Server 2022 10.0.20348 / runner image `windows-2022` version `20260913.307.1`, CPython 3.12.10 and Node.js 22.23.2. Runtime and host strings were excluded from the logical signature and retained only as evidence metadata.

The workflow also preserved per-platform and combined artifacts. Their IDs and archive digests, along with the run identity and runtime observations, are frozen in `research/rcs-019/measured-summary-v1.json`.

## Contract reconciliation

No accepted RCS-002 semantic rule needed to be weakened to construct or pass this suite. Two values that RCS-002 intentionally leaves to a versioned normalization policy—the admissible q15 norm deviation and exact arc-ambiguity guards—are made explicit in `rcs-019-reference-policy/1.0`. This resolves executable test ambiguity at the policy layer rather than silently editing historical journal meaning.

The hosted evidence showed no cross-platform or independent-implementation divergence, so the recommendation is **no journal contract revision** before Gate 5. Production implementations must, however, version every threshold that affects durable segmentation or fit/refusal output; relying on an implementation default would violate identical-input determinism.

DR-0010 remains unchanged. Manufacturing tolerance, uncertainty, fit error, storage quantization and topology/contact policy are not collapsed into one epsilon.

## Architecture implications

OpenSimachinist can treat a conforming journal as backend-independent physical intent; provider code does not need gamepad/frame-loop semantics. MSAC canonicalization implementations need a vector-conformance gate before they may claim `msac-journal/1.0` logical compatibility. Backend caches and topology IDs remain disposable and are absent from this suite.

RCS-023 can consume the explicit quantization/fit-bound channels. RCS-026 should reuse these vectors unchanged for larger Windows/Linux scale and fault-recovery qualification rather than inventing a new canonicalization oracle.

## Evidence classes and remaining scope

- **ACCEPTED SOURCE:** RCS-002, DR-0006 and DR-0007 define fixed tokens, transform convention, ties-to-even, semantic boundaries and deterministic/bounded normalization.
- **ACCEPTED SOURCE:** DR-0010 forbids collapsing small positive manufacturing intent into a numerical no-op.
- **MEASURED (local):** both independent implementations match all 32 vectors and the adversarial validator rejects deliberately corrupted expectations.
- **MEASURED (hosted):** workflow run `35271407927` passed Linux, Windows and cross-platform identity jobs; both platforms produced the same frozen logical signature, with exact runtime/image observations recorded in `measured-summary-v1.json`.
- **OPEN:** production fitting algorithms may be more sophisticated than these research decisions, but they must expose equivalent certified bounds/fallback semantics and pass policy-specific vectors.

No claim is made that arbitrary differently sampled splines are byte-identical, that a 100,000-sample smoke test is a production scale limit, or that q15 storage precision is manufacturing accuracy.
