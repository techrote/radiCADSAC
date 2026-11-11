# B1-D17 — E5 affine germ projection snapshot custody (11 November 2026)

Status: **RESEARCH GO / AUTHENTICATED CROSS-PRODUCER, NATIVE, STEP AND MERGE HOLD**. Independent acceptance pending. Scope: B1-owned `research/experimental/certificate-algebra/core/**` in Draft [#473](https://github.com/techrote/radiCADSAC/pull/473). Parent at preregistration `ed75fa1683476bac3504db24448162bbf02fa29a`; accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`.

## Falsifier and actual consumer

The parent B1 Python suite **101/101 PASS** even though actual `quotient_sided_germ.project_signed_affine()` consumed a caller-owned mutable `germ` *after* checking the self-hash. A deterministic patch at the real `digest(...)` boundary modified the original nested `right.leading` from `1` to `-1` **after hashing but before projection**. On the original implementation, the projected signed germ incorrectly returned `-1`, attached to the same old `input_germ_hash` as the valid `+1` projection. A second test changed the event `time` from `1` to `3/2` at the same boundary, producing a displaced event with the unchanged old input hash. Both controls use an actual E4→E5 `family(1,1,1)` source and genuine `derive()` receipt, not a fabricated free-standing receipt.

The two newly imported tests **FAIL 2/2 against the original E5 module**, with exact observed wrong values above. The fix makes an owned, validated primitive deep copy after ingress admission and uses that one snapshot for both self-hash verification and affine projection. It adds no new proof claim or source ancestry.

## Source and execution evidence

- Prepatch parent B1: **101/101 tests PASS** using all 25 Python files from the D16 bundle.
- New tests on that actual original E5 module: **2 failures / 2 executed**. The failure is a false *model prediction*, not a failed native Boolean or physically witnessed spline event.
- Corrected real parent/E1–E7 suite: **103/103 PASS**; `python3 -m compileall -q .` and `python3 experiment.py` PASS.
- Local exact Git blob hashes, independently checked for the two changed files: `quotient_sided_germ.py = 8617d59e1ad4da1034df527bbb9aabf42c5ae0a1`; `test_quotient_sided_germ.py = c2e546987e796a6ca0882bc110f7a1a8b2a636bd`. All 23 unchanged D16 Python Git blobs retain their published manifest identities.
- Source SHA format is Git's `SHA1("blob "+bytesize+"\\0"+content)`, not SHA-256. An executable checkout/CI must rerun all tests on the *final PR head*; a successful generic repository workflow is not a substitute.

Commands from the B1 core directory:

```sh
python3 -m unittest discover -v -p 'test*.py'
python3 -m compileall -q .
python3 experiment.py
python3 bench_b1_fair_boundary_20261110.py
```

## Verification economics

CPython model, 32 pieces, 64 edits, five symmetric benchmark rounds, all intermediate hashes equal: efficient full reproof **81.763 ms** versus incremental **30.590 ms** (**2.67×**); full plus strict readmission **209.914 ms** versus incremental plus strict readmission **153.280 ms** (**1.37×**). The latter saves **56.634 ms per 64-edit workload**, approximately **0.885 ms/edit**, *before* producer custody, E5 application, physical lineage, dependency cones or native/STEP overhead. This is the maximum extra end-to-end overhead the measured Python advantage could absorb before reaching parity in this specific workload, not a native allowance or guarantee.

Seven-repeat, 1,000-call isolated E5 projection microbenchmarks (indicative, not interleaved or native): original **34.819 μs/call** median; snapshot-corrected **61.862 μs/call**, about **77.7% more**. Correctness takes priority; the added proof-boundary work strengthens the case for HOLD on net native benefit.

## Proof scope and consumers

The existing de Casteljau Bernstein split/affine closure laws are unchanged. The newly repaired statement is narrow: a deterministic projection result must derive solely from the **same primitive predecessor germ** whose self-hash was checked. This guards ordinary mutable data passed across the local Python API, not malicious code with arbitrary powers in the same process. Projection stays explicitly `UNBOUND_PREDICTION_REVERIFY_TRANSFORMED_SOURCE`; it is **not** an authenticated transformed-source receipt.

Direct source-matched current A1 #470 `fe0dada7c430053c4c387f17a062909da9aab8bc` was reexecuted separately: `-1+sin(pi*t)` at `t=1/2` is an actual producer-verified `EXACT_ZERO`; `t=0` is `EXACT_NONZERO`; forged result/coefficient swap REFUSED. B1 still internally stamps historical A1 producer head `281705e9...`, and explicitly supplied current A1 head is REFUSED; B1 serialization under research-supplied pins does **not** establish custody. A2 #471 `d9cb56e74e876efb203e04003aadcf8bd368a369` current original receipt has **NOT** been executed by B1. The original physical B-spline controls, knots and window remain unauthenticated. No native/STEP workflow or MC-B optimization is qualified.

## Disposition and independent challenge

**GO:** current bounded Python source model and the two repaired E5 input-snapshot controls. **HOLD:** authenticated current A1/A2 producer admission, genuine current A2 direct-module execution, source ancestry, independent reviewer execution, full native/STEP recomputation economics and merge. Ask A3/B5 to rerun the exact final 103-test suite from a second source, challenge the deterministic post-hash leading/time swaps and alternative nested mutations, and quantify full native consumer custody/verification overhead without paid/native campaigns absent an explicit permit.

This does not modify production, canonical registers or historical fixtures. Retain frozen **121/20/30/50** census and **26 machining operations**, MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false`. No source ownership beyond B1 core.
