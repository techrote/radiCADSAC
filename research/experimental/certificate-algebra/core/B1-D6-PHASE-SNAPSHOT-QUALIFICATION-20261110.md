# B1-D6 — phase source/hash snapshot qualification (10 November 2026)

Status: **PASS WITH LIMITED GRAMMAR** for the corrected, bounded Python phase consumer; **HOLD** for current A1/A2 producer receipt admission, independent review, native/STEP performance and merge. Evidence class: **DETERMINISTIC_MODEL**. This file is not MC-038 proof authority.

## Exact source and ownership

- Accepted main: \`48222d6c40b15ad42cc36d56e6d25f3b284e7fc9\`.
- B1 input Draft #473: \`17dc6fda2d323fb127ae69733fa5afc2e478fc4d\`.
- Actual source input blob: \`phase_bridge.py=155c21003234836a85d0e2ab69cc04474cbcf086\`; actual test input blob \`test_phase_bridge.py=3dfa773ba9d3db58957ac3db140aa6e9660bdc78\`.
- Guarded B1-only source commit: \`47966802b2cea2c0d44d107a807d3cf5a1c76c7e\`; source blob \`dbcb2049d7e3de09f6430e632bee21ce836a1809\`.
- Guarded B1-only test commit: \`f4edf2aaa1f848c48b22512b9f7791107622cd9d\`; test blob \`a0169c08c6ea2a74628d84da5c459fd12616ce3d\`.
- All **22 original or revised Python source/test/benchmark blobs** were compared against the published B1 branch directory; all matched the actual local executable file bytes. The other 20 are unchanged. Work was restricted to \`research/experimental/certificate-algebra/core/**\`; no protected/shared/producer source changes.

## Falsifier and original negative result

Hypothesis attacked: a B1 phase equivalence receipt's source hash binds the *same mathematical source representation* analyzed in \`prove_equivalent\` and \`verify\`.

Two original A1-format envelopes denote \`f(t)=-1+sin(pi*t)\` and agree before inspection. At first entry into the **real imported \`phase_bridge.digest\`**, a deterministic CPython \`sys.settrace\` hook changes only the source harmonic-1 sine amplitude from \`1\` to \`2\`. The algebra had already evaluated the old source, but the SHA-256 now describes \`g(t)=-1+2 sin(pi*t)\`. A verifier call is supplied with a receipt whose *semantic hash describes the old equality* and whose *source hash matches the changed, externally selected source value*. It is not a hash collision or a forged trusted hash.

The original published \`phase_bridge.verify\` **returns True** for this false source-bound claim under the same interleaving. Stable \`prove_equivalent(changed, original)\` correctly raises \`phase-normalized functions are not proven identical\`. Direct unmodified parent run exits **1** with:

\`\`\`
STABLE_CHANGED_SOURCE_REFUSES: phase-normalized functions are not proven identical
FORGED_RECEIPT_ACCEPTED_BY_UNMODIFIED_B1: True
SOURCE_HASH_MATCHES_MUTATED_SEMANTICS: True
AssertionError: B1 SOURCE/HASH TORN-READ: actual verify accepted a false equivalence receipt
\`\`\`

This is **one newly qualified B1 in-process source/hash torn-read defect**, not a mathematical phase-substitution counterexample, an A1/A2/native producer attack, a proof of network exploitation or an issue with SHA-256.

## Minimal repair and exact-module regression

The phase bridge now validates then copies a bounded exact-builtin-primitive envelope into an owned private tree. \`canonical\` runs on that tree; \`prove_equivalent\` uses each *same* captured source for semantic analysis and digest; \`verify\` independently captures once then uses its same source/target snapshots for both recomputed proof and hash-pin check. Source grammar, rational/phase rules, producer whitelist, existing direct receipt verifier and explicit refusals are unchanged.

A new method \`test_phase_bridge.BridgeTests.test_phase_snapshot_digest_torn_read_refuses_false_equivalence\` reproduces the original defect against the real parent (fails: \`AssertionError: Refusal not raised\`), then PASSes against the repaired actual imported parent. It also checks unchanged static positive-source equality, stable changed-source refusal and independently selected final source hashes.

**Direct local CPython 3.13.5 execution, no stubs or hosted CI substitution:**

| Execution | Result |
|---|---|
| Full original published 10-module \`python3 -m unittest discover -s . -p 'test_*.py' -v\` | 86/86 PASS, exit 0 |
| Original actual phase parent with new negative regression | 1 failure, exit 1 (expected falsifier) |
| Repaired current published phase source + entire test suite | **87/87 PASS**, exit 0, 0.886 s |
| Python compilation | PASS |
| Existing deterministic \`experiment.py\` | PASS |
| Existing 32-piece / 64-edit five-arm \`bench_b1_fair_boundary_20261110.py\` | PASS; all intermediate snapshot hashes matched |

The model's existing proof-leaf count and split/affine/cyclic/subclass/oversized tests are retained; the phase fix does not modify them. Research-only fair rerun: efficient full reproof 87.69 ms vs trusted incremental 32.84 ms (**2.67×**); both with strict base readmission, full 227.75 ms versus incremental 173.01 ms (**1.32×**). These arms **do not invoke the phase bridge** and cannot measure the new phase boundary cost. A separate same-host symmetric 7-cycle/250-verify-per-sample Python phase-only comparison found original median **114.56 μs** and owned-snapshot median **152.59 μs** (**1.33× per verification**, ~33% overhead); accepted honest receipt and pins identical in both. The microbenchmark does **not** establish native/STEP value, process-grade synchronization or a broadly general speedup.

## Trust, independent challenge and no-go boundaries

- The owned local copy guarantees consistency between phase semantics and source hash for a **single admitted captured tree**. It does **not** prove a stable external producer object, worker fence, physically authentic knot/control/source ancestry, external writer exclusion or atomic snapshot if an external writer mutates the original *during copying*. Authenticated source/lifetime custody remains a consumer obligation.
- B1's \`phase_bridge.PRODUCERS\` still pins A1 \`281705e947fd7812300d1d2605d3cdf60cdb005e\` and A2 \`3b6eaf70e1e7422b7ac8e8e9ff6f0fef85281978\`. Current A1 Draft #470 \`098517a70e63cb8d5b8bab01b34118fa8439c942\` and A2 Draft #471 \`d9cb56e74e876efb203e04003aadcf8bd368a369\` **are not admitted**, correctly fail-closed. No current producer-issued, source-authenticated A1/A2 receipt was executed here. Historical A1 producer replay and synthetic current-head envelopes are not substitutes.
- A3's real A2 \`sparse_phase_germ\` hostile-key changing harmonic amplitude after analysis but before hash is a separate **CHANGES REQUIRED** upstream boundary at A2's unchanged head; the B1 patch cannot repair it. A1's latest F2/F3 snapshot fix has author-run tests, with independent A3 exact-head review still pending.
- B1's Python recurrence savings do not yet justify a native/STEP verifier. No physically authenticated #462 B-spline ancestry, source-specific MC-038 admission, real native cost, exact-current-head A1/A2 cross-producer proof or independent A3/B5 second-source execution is claimed. No automatic allowlist revision.
- Maintain **Draft/HOLD**. A3/B5: rerun the exact new B1 87-method suite and this deterministic original-vs-fixed falsifier; challenge snapshot capture under an independently controlled external producer identity, then qualify a **genuine** current A1 or A2 receipt only after its own exact-source verifier/physical-window custody succeeds.

Current authority \`handoffs/current-authority.json\` and DR-0026 / MC-1 protocol remain binding. Historical census **121/20/30/50**, all **26** machining operations, MC-B and MC-1 **NOT_ESTABLISHED**, \`production_authorized=false\`. No production repo, native, paid campaign, protected proof register, merge or Ready transition.
