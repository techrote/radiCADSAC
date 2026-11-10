# A1-QUAL-004 — F4 signed-carrier source/digest custody repair (10 November 2026)

Status: **research-only; local candidate PASS; A3 independent HOLD**. Accepted main: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. Input Draft #470 exact head: `406e901a1dd8bd9635129e39c6b634279221f8d4`. F4 original blobs: `carrier_partition.py=8e028f39435042ec60a49fb1637168723daf61ed`, `test_carrier_partition.py=ee57c8435b205dfe9884452af676642c6a791ae9`.

## Bounded falsifier

The real F4 `source(doc)` parsed rational nested polynomial lists before separately hashing the mutable caller's `doc` through `json.dumps`. A deterministic CPython `sys.settrace` hook at that actual `json.dumps` entry replaced `pieces[0].H0=['-1/2','1/1']` with `['0/1']`. The original `certify` returned one genuine order-one CROSS at t=1/2 but labelled it with the SHA-256 of an identity-zero source. The original `verify` returned **True** under the same interleaving; direct original-parent adversary exited **1**: `AssertionError: F4 SOURCE/HASH TOCTOU: real verifier accepted false zero-topology receipt`. Static honest/modified-source controls refused the mismatch.

This proves an **in-process source/receipt binding defect**, not a counterexample to the bounded carrier/Sturm mathematical theorem, a native exploit or original B-spline provenance failure.

## Corrective proof scope

`source(doc)` first copies the bounded two-level *exact built-in* primitive tree: exact dict keys, at most three piece rows and five lists of at most eleven rational-token strings per row. The owned copied tree is then used for **both** rational coefficient analysis and the canonical digest. Mutation of the original list at the later digest cannot alter the captured values, hence both generated event topology and declared SHA correspond to the same snapshot. This does not make the capture transactional against a concurrent external writer; exact physical ancestry, lifetime and rollback remain **UNVERIFIED**.

Added `test_original_f4_digest_mutation_uses_captured_source` against imported real F4, with exact hooked digest mutation, honest one-CROSS and identity-zero controls, a forged zero-source hash, static refusal and repaired trace refusal.

## Executed local qualification before commit

CPython 3.13.5, all actual original implementation/test imports from the 21-file Git-blob verified A1 source bundle:
- Input unchanged `406e901` candidate: complete `python3 -m unittest discover -s . -p 'test_*.py' -v` **98/98 PASS**, Git blobs 21/21 matched.
- Before correction, original F4 direct source/hash adversary **FAIL** (expected; real `verify=True` for false topology).
- Corrected F4: `python3 -m unittest -v test_carrier_partition.py` **13/13 PASS**, entire ten-module candidate **99/99 PASS**, no skips. `python3 challenge_sympy.py` PASS.
- Post-correction original-parent F4 digest-boundary check PASS; F1 7 hostile receipts REFUSED, F6 4 REFUSED, F7 2 REFUSED; F6 negative phase/pole/order/sided signs and F6/F7 deterministic source-hash interleavings PASS. The old F6 helper was repinned to the current F6 blob before replay.
- Raw local logs and original failure trace are retained separately in A1-QUAL-004 execution evidence. Hosted exact-new-head CI and **A3 second-source execution remain pending**.

## Admission matrix

| Gate | Evidence / disposition |
|---|---|
| Bounded analytic carrier/Sturm theorem | Conditional; no new mathematical claim |
| Authored complete original/imported A1 suite | Locally 99/99 PASS, post-correction bytes |
| Direct A3-style negative phase, projective pole, ordering/multiplicity, forged receipts, source races | A1 self-replay PASS; **A3 independent pending** |
| Authenticated physical original B-spline controls, knots, provenance | **UNVERIFIED** |
| Arbitrary knot grammar, unrestricted H2 exponential polynomial root partition/tangency | **NOT_ESTABLISHED** |
| MC-B / MC-1 and production | **NOT_ESTABLISHED**; `production_authorized=false` |

Historical 121 originals / 20 refusals / 30 missing premises / 50 complete witnesses, 26 operations and all protected MC-038 authorities remain unchanged. Draft/HOLD, no merge/Ready. **A3 requested:** independently fetch the published new literal head, execute all 99 tests plus F4 exact `sys.settrace` mutation and F1/F6/F7 controls, challenge caller mutation *during* capture, then report one smallest falsifier or scoped acceptance. No wider theorem/consumer admission.
