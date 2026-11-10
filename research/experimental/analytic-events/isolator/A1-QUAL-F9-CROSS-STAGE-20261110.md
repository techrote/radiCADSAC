# A1-QUAL-006 — F9 algebraic germ / signed cofactor source custody (10 November 2026)

**Research-only, Draft/HOLD; no theorem expansion.** Existing A1 [PR #470](https://github.com/techrote/radiCADSAC/pull/470), pre-change head `098517a70e63cb8d5b8bab01b34118fa8439c942`, accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. Scoped source lease [#324 comment 6775948283](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6775948283). Only F9 signed-cell source/test and this research report changed.

## Exact grammar / scope

F9 determines sided signs of an **already F2-verified algebraic germ**, using bounded rational-polynomial H0/H1/H2 coefficients (five Fourier channels, degree ≤16), rational affine phase with nonzero rate, bounded primitive irreducible minimal polynomial and unique algebraic root bracket. It divides each channel by the proved minimal polynomial power and certifies a strict cofactor sign with rational interval bounds. F9 is **not** a universal finite event isolator; tangencies, arbitrary knots, unrestricted transcendental roots, and original physically authenticated B-spline ancestry remain unestablished. #453 supplies separate previously bounded results, not a solution for these classes.

## Direct original-source falsifier

F9 called F2 `algebraic_degree.certify(doc,...)` (which already snapshots its own finite source) then independently passed the *live caller-owned* `doc` into `signed_from_verified_germ`. Its verifier similarly mixed a first F2 source read with a second F9 live-source read. A deterministic `sys.settrace` callback at entry to the **real** F9 signer flips H0 from `5(t²−2)` to `−5(t²−2)`, with `a=0,b=1`, minimal polynomial `(-2,0,1)`, prime 3 and rational root bracket `[707/500,283/200]`. The original published F9 `certify` then returned an **old-source SHA-256** but reversed sided signs. Stable verification against either old or changed source refused this receipt, yet the **real original F9 `verify` returned true when the same interleaving was replayed**. Original direct probe exit 1: `AssertionError: F9 cross-stage source-binding TOCTOU: original real verifier accepts forged signed germ`.

Verified pre-change Git blobs: F9 source `c53b2ee6768f21d321c4dcd901d15a73fded233d`; F9 tests `a1ae1c4f70dc2c5c7a2a120dc7e2ab553dd439c4`; real imported F2 `21f274471519ae775c0d222ef69e39948289bbe4`. This is **an in-process source/value-custody defect**, not a counterexample to exact root mathematics or evidence of a native B-spline exploit.

## Bounded correction

The new F9 `_owned_admitted_doc` calls F2's authoritative **one-snapshot** `admitted(doc)` once, reconstructs a canonical primitive mapping solely from the resulting immutable Fraction values and verifies that its SHA-256 equals F2's admitted digest. Both F9 `certify` stages and both F9 `verify` stages consume that same locally owned mapping. F2 irreducibility and valuation rules, F9 cofactor sign logic and finite budgets are unchanged. A new **original-parent-imported** `test_signed_germ_and_cofactor_share_captured_source` exercises real producer and verifier under the old mutation boundary, honest and opposite-source controls and a deliberately inconsistent forged signed receipt.

Conditional source-coherence lemma: after F2's admitted bounded snapshot, mutations of the original caller mapping cannot change F9's subsequent local germ and signed-cofactor values. Verification computes both from one newly captured mapping. This does **not** authenticate an external producer, make a multi-owner source transaction, or establish physical B-spline provenance. The snapshot adds O(total admitted coefficient tokens) work per F9 call under F2's finite caps, not a native per-cell checker or measured throughput gain. Direct use of `signed_from_verified_germ` remains explicitly premise-bound, not an independent authenticated consumer.

## Reproduction and qualification

```sh
git checkout --detach <new-exact-PR-head>
cd research/experimental/analytic-events/isolator
git hash-object signed_cell.py test_signed_cell.py algebraic_degree.py
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 -m unittest -v test_signed_cell.py
python3 challenge_sympy.py
```

The original pre-fix source can be reconstructed at commit `098517a70e63cb8d5b8bab01b34118fa8439c942`; run the preserved standalone original-parent `a1_signed_cell_race_probe.py` to reproduce the **expected nonzero** false-receipt failure.

| Gate | Result |
|---|---|
| Bounded mathematical lemma | Conditional, unchanged; no general theorem promotion |
| Complete current candidate original/imported test suite | **LOCAL 102/102 PASS**, CPython 3.13.5, zero skips (postpublish exact blob readback required) |
| Direct original F9 interleaving | Negative reproduced pre-fix; real original-parent regression **PASS** after fix |
| Direct F6 negative phase/pole/ordering/multiplicity/sides and F1/F6/F7 forged receipts | **LOCAL PASS**, original parents, plus F4/F6/F7 source-interleaving controls |
| F2/F3 real-parent source-custody regressions, optional SymPy | **LOCAL PASS** |
| A3 independent second-source at new literal head | **PENDING / HOLD** |
| Authenticated original physical B-spline ancestry | **UNVERIFIED** |
| Unrestricted H2 roots, tangencies, arbitrary knots | **NOT_ESTABLISHED** |
| MC-B / MC-1 | **NOT_ESTABLISHED**; `production_authorized=false` |

Preserve frozen **121/20/30/50** census, **26 machining operations**, original/negative evidence and separate MC-038/proof-registries. No native, paid, production, peer-branch, default law or merge/Ready action. Request A3 read-only independent exact-head adversarial execution before any promotion.
