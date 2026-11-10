# B1-D8 — Producer-codec source/hash snapshot qualification (10 November 2026)

**Disposition: scoped GO for the corrected bounded Python research consumer; HOLD for cross-producer authority, native/STEP value, independent admission and merge.** Draft [#473](https://github.com/techrote/radiCADSAC/pull/473). This is a deterministic research-model result, not a physical-geometry or MC-038 certificate. No authority/production/other-lane edits.

## Fixed source, ownership and hypothesis

- Accepted main source: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; B1 input Draft exact head: `edf5ef44986944b313bd722d6491e52c432f1f43`. Existing B1 source lease: [#324](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6752064357).
- Read existing AGENTS.md/DR-0026/MC-1 protocol, issue #100, #397/#453/#462 and #324. Only B1-owned `research/experimental/certificate-algebra/core/**` changed.
- **Falsifiable claim:** both `producer_codec.a1_envelope` and `a2_envelope` must bind the *same* captured canonical producer representation to (a) the emitted mathematical terms and (b) the `origin_source_sha` pin. If caller-owned source content changes after terms are read but before digest, an adapter must refuse rather than mint inconsistent ancestry.
- **Limit:** capturing a primitive source value is not proof of an upstream Git head, an immutable producer lifetime, a physical knot/window/control source, or independent custody of the supplied SHA pins.

## Before repair: direct actual consumer falsifiers

Original published `producer_codec.py` Git blob `563c445c314309a6198395addbecb59b464182a0`. Complete published ten-module suite: **87/87 PASS** first (CPython 3.13.5). A new regression was then inserted into the *actual* `test_producer_codec.py`, not a standalone surrogate.

In the original `a1_envelope`, initial `c0=['-1']` is parsed into its envelope; at the actual source digest call, deterministic `unittest.mock.patch` changes the caller's `c0[0]` to `'-2'`. Its externally selected SHA is the actual SHA of the mutated canonical raw dict. **Original adapter incorrectly ACCEPTS** an envelope containing the old `-1` coefficient with `origin_source_sha` authenticating the different `-2` source. Independently analogous A2 `terms['0'][0][0]` source swap is **incorrectly ACCEPTED**. This is a source-identity torn read, not SHA collision or bypass of a genuinely entrusted pin. Each original regression subtest failed `AssertionError: Refusal not raised` (two failures).

The original B1 `phase_bridge.verify` had previously been independently repaired with an owned source snapshot; this was a separate **real serialization adapter** boundary left unfixed.

## Repair and exact-source execution

Bounded shape validation now precedes `copy.deepcopy`; its builtin primitive result is revalidated. **Both** `a1_envelope` and `a2_envelope` parse and hash that *same* captured object. `producer_codec.py` new Git blob `d9858061f47df687722eb1069965cd8e03c219b6`. New regression `test_producer_codec.py` Git blob `668509b9de4283b10d9884167b625d649c3ccb1d`. Refusal occurs even when the attack supplies the legitimate digest of the eventually mutated raw source; normal unmodified positive source pairs still pass. The prior A1 replay script was repinned to the new B1 codec (Git blob `a74f390c70b2db4306ca9d3e5c119037bd96eee0`) and explicitly labelled a **dated source-pinned A1** replay, not current producer ancestry.

Commands, executed from a directory containing the exact published B1 sources/tests:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_base_receipt_integrity test_certificate_algebra test_closed_nonzero test_phase_bridge test_producer_codec test_product_cone test_quotient_sided_germ test_rational_quotient test_receipt_integrity test_refined_product
python -m compileall -q .
python experiment.py
python bench_b1_fair_boundary_20261110.py
# For the dated A1 exact source checkout (NOT current A1 HEAD):
python probe_current_a1_receipt_20261110.py --a1-dir /path/to/pinned/A1/isolator
```

- **Repaired full 10-module parent-imported suite 88/88 PASS**, no test skipped or replaced. Before-repair 87/87 PASS; with the new regression against unmodified parent, **one test fails in both A1 and A2 subtests**. Fixed parent: both negative cases correctly REFUSED and the complete 88/88 suite passes.
- Python compilation, deterministic proof-work experiment and existing five-arm fair benchmark: PASS; 64/64 per-edit exact state snapshots agree across every mode. All original B1 code/test/benchmark Git identities were checked against published input head; both modified files and the repinned producer probe also match their final Git blobs.
- Historical A1 `098517a70e63cb8d5b8bab01b34118fa8439c942` actual source and event verifier were replayed from earlier source-pinned artifacts against updated B1 codec: direct `EXACT_ZERO` rational event verify PASS, source mutation REFUSED, explicit unreviewed current producer label REFUSED. **This is a dated A1 head**. A1 has since advanced to `b46eeba40c09f61ef8ac6253d397964651fdea53`; it has **not** been executed here. A2 current head `d9cb56e74e876efb203e04003aadcf8bd368a369` actual `point_germ`/receipt verifier was **not executed here**. Neither source has independently authenticated physical B-spline ancestry.

## Verification cost, native relevance and decision

On CPython 3.13.5, a separate alternating ten-sample/150-iterations-per-sample local codec measurement found A1 old **36.09 μs**, snapshot **44.29 μs** (+22.73%); A2 old **48.51 μs**, snapshot **61.14 μs** (+26.03%). These are microbenchmarks of B1 source parsing/hash admission only; no native consumer execution. The existing fair 32-piece/64-edit deterministic Python benchmark, two warmups and five symmetric repetitions per arm, remeasured one-pass full recomputation at **80.47 ms**, trusted incremental at **31.19 ms** (2.58×), one-pass fully readmitted at **208.90 ms**, incremental fully readmitted at **156.79 ms** (1.33×). This direct B1 work does **not** measure combining either codec snapshot overhead with strict every-edit readmission, nor does it include authenticated upstream source custody.

The native relevance is a *potential* dependency-aware exact leaf/adjacent-seam recomputation reuse contract under a proven complete dependency cone; it is not a measured live native consumer. The historical 2,080 vs 96 leaf count excludes redundant mathematical work in the prior naive reference. Native solver/geometry/STEP performance, rollout, policy epoch, source ownership, pressure/global dependency semantics, memo validity across material updates, and external pin/authenticated head lifetime all remain OPEN. **No claim that verified savings justify native verification overhead**; do not deploy based on this Python 1.33× boundary experiment.

## Open adversarial admission gates

1. Independently rerun at the final source head both genuine A1/A2 producer receipts (with source, window, knot/control ancestry independently held), using the real B1 serialization and phase consumer. The B1 adapters still self-label historically allowed producer heads; do **not** allowlist newer A1/A2 heads without an independent code/producer-source custody review.
2. A3/B5 must replay and challenge the original two-subtest consumer regression, all 88 original-parent tests, and the A2 source-identity/sparse-phase defects under their own source instances. Snapshot-midcapture / externally mutable producer authority is not solved by a local copy.
3. Require native same-consumer A/B recomputation-vs-invalidation-vs-hash/verification-cost parity before any real deployment or architecture change. Preserve mixed-sign UNKNOWN and bounded refusals, never promote to topology/Boolean proof.
4. Preserve frozen 121/20/30/50 census, 26 machining operations, all historical evidence, MC-B/MC-1 **NOT_ESTABLISHED**, `production_authorized=false`. Draft/HOLD; no merge.

**Source/evidence class:** `MEASURED_DETERMINISTIC_MODEL` with direct B1 Python consumer execution. Not native geometry or externally authenticated physical source provenance.
