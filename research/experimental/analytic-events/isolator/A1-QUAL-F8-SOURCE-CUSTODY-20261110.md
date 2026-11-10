# A1-QUAL-010 — F8 complete-event receipt source custody

**10 November 2026 · DETERMINISTIC_MODEL · Draft PR #470 / HOLD · no authority promotion**

## Exact parent, claim and original failing test

Parent: `976ec8c093a17bbe117b7ddd14dc4f391c7ea25c` on `research/a1-algebraic-zero-dichotomy-20261109`; published prepatch F8 `simple_promise.py` Git blob `4a55db0486a4ccc838ca1ee87d214ffc6f6d87c3`. Exclusive write set: `simple_promise.py`, `test_simple_promise.py` and this note. Source lease: [#324/6780449443](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6780449443).

**Preregistered falsifier:** F8 checked a caller-owned frozen `Source` with `valid_source(s)`, then separately read `s.pieces` to compute events. A frozen dataclass is mutable using `object.__setattr__`. A deterministic Python trace hook restoring `s.pieces` immediately before the *actual* `valid_source` call and changing it to an opposite-sign piece on its return made the unmodified published F8 producer emit two `EMPTY, sign=-1` cells for `H0=-4` under the **SHA-256 of `H0=+4`**:

- Positive source SHA-256: `66ad3d90e78730a7a5c44aa2f97680918bf8041bedde161ae41a7dfe2ab202c7`.
- Prepatch direct `partition(s,limit_level=0,max_shifts=1,precision=(4,))` emitted negative cells for [0,1/2] and [1/2,1].
- Prepatch real `verify(s,receipt)` with the same interleaving returned `True`; stable verifier on the unmodified positive source returned `False`.
- The actual original-module probe exited 1: `AssertionError: F8 DIRECT ORIGINAL REAL VERIFIER ACCEPTED SOURCE/TOPOLOGY FALSE RECEIPT`. This was NOT a substituted oracle, not an alleged physical B-spline proof, and not a counterexample to the conditional simple-root theorem.

A separate ingress source/digest interleaving was possible in `source(doc)`: it parsed caller-owned lists and later hashed the independently mutable original dictionary.

## Bounded corrective increment

`source(doc)` now captures one bounded exact-built-in primitive-tree copy before analysis and SHA-256. `owned_source(s)` rebuilds and SHA-validates one privately owned Source/Piece structure with fixed upper bounds before proof computations. Both `partition` and the **actual** `verify` operate exclusively on that snapshot; no one-time admission followed by source rereads. This protects model source/receipt consistency **after capture**, not external writer isolation or original physical source ancestry. Reject oversized forged Fraction values before canonical reconstruction. No root-isolation mathematics or theorem scope changed.

New tests exercise the exact original `valid_source` interleaving boundary, a reversed-sign forged receipt, `json.dumps` ingress mutation, oversized coefficients, and original honest controls. A preexisting mutable-source rejection assertion was strengthened from generic `BUDGET` to the exact `SOURCE_HASH_MISMATCH` refusal.

## Verification matrix

| Distinct gate | Status |
| --- | --- |
| Existing bounded conditional simple-root theorem | **UNCHANGED**, no expansion |
| Complete exact-head 22-Python-file original/imported candidate suite | **113/113 PASS** locally (Python 3.13.5), no skips |
| F8 original false receipt | **REPRODUCED on prepatch published algorithm** |
| Repaired F8 source/receipt, ingress and oversized controls | **PASS** locally |
| F6 negative phase, projective pole, order, multiplicity, sided signs | **PASS** direct original-parent probes |
| F1/F4/F6/F7 forgery and deterministic source races | **PASS** direct imported-parent controls |
| Optional SymPy exact symbolic controls | **PASS** |
| Published-head readback, postpublication complete 113-test replay | **REQUIRED**; do not mark PASS until separately performed |
| Independent A3 exact-current-head run | **PENDING**; second-source independent review requested |
| Authenticated genuine physical B-spline controls/knots | **UNVERIFIED** |
| Arbitrary H0/H1/H2 tangencies, transcendental roots and knots | **NOT_ESTABLISHED** |
| MC-B / MC-1 | **NOT_ESTABLISHED**; `production_authorized=false` |

## Reproduction and custody

From the literal PR commit directory:

```sh
cd research/experimental/analytic-events/isolator
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 challenge_sympy.py
python3 -m unittest -v test_simple_promise.Research.test_hash_bound_source_snapshot_under_interleaving test_simple_promise.Research.test_doc_ingress_hash_matches_parsed_capture test_simple_promise.Research.test_source_snapshot_rejects_oversized_fraction_before_recompute
```

For the failing original algorithm, load `simple_promise.py` from parent `976ec8c093a17bbe117b7ddd14dc4f391c7ea25c` with a trace hook on the real `valid_source`: on its `call`, set caller-owned Source.pieces to `source(H0=+4).pieces`; on its `return True`, set those pieces to `source(H0=-4).pieces`; run its original `partition` and `verify` with the hook, preserving the source SHA-256. Expected original false receipt has two negative EMPTY cells and real verifier True; fixed executable refuses this mismatched source/certificate. Preserve original trace independently, not as a production event witness.

No native/paid campaign, production or cross-lane edits, altered historical evidence, source-specific closure, or merge. Original **121/20/30/50** census and all **26** machining operations remain intact. Claim classification: finite reproducible implementation-source falsifier and repair, not general geometry decidability.
