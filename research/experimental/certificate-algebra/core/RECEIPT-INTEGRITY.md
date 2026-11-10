# B1-E6 — Type-strict receipt admission, hostile equality and bounded replay

**10 November 2026; research-only / DETERMINISTIC_MODEL; Draft / HOLD.** Accepted base main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. Existing B1 Draft PR #473; preregistered [#324](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6759826870). No changed source or mathematical authority outside `research/experimental/certificate-algebra/core/**`.

## Decisive actual-B1-code falsifier

Original E2 `_expected`, E3 `verify`, E4 `verify` and E5 `verify` compared a replay-generated Python `dict` to an untrusted proposed `dict` by Python's native nested equality. `type(proposed) is dict` does **not** constrain nested values to primitive JSON. A hostile `str` subclass `AlwaysEqual("FORGED")` returning `True` from `__eq__` makes `{"claim":"VERIFIED"} == {"claim":AlwaysEqual("FORGED")}` true, so the original code admits a noncanonical false receipt if passed an in-process Python object. `{"flag":True} == {"flag":1}` also silently aliases distinct JSON types. These are in-process verifier-contract counterexamples; not attacks against parsed JSON produced by a trusted decoder, not proof that any production consumer currently sends such objects.

## Corrected conditional law and implementation

For **any finite primitive JSON tree** formed solely of exact builtin dict with string keys, list, string, integer, boolean and null, recursive equality with exact type agreement tests canonical structural equality; no custom Python equality methods execute. This follows by structural induction on tree height: primitive leaves use same builtin type and value; lists recurse in order; maps have the same exact string-key set and recursively matching child values. The theorem is a standard typed structural equality fact, not new mathematics. The unrestricted mathematical class is infinite (unbounded finite tree length/integer values). The executable checker admits only a **bounded subset**, refusing excess recursion, nodes, key/string lengths and integer bits; refusal is not inequality of mathematical sources.

`receipt_integrity.admit(expected, proposed)` first audits **both** structures, then performs only exact primitive recursive comparison. It is now used by E2, E3, E4 and E5 verifier boundaries, including E5's explicitly *unbound* signed-affine predictor input. It does not authenticate producer identities, bind a native World epoch, sign a digest, or alter any polynomial/B-spline theorem. External content pins remain externally entrusted; authentic #462 B-spline source/knot custody and A1/A2 phase/implicit-coordinate adapter remain unresolved.

## Resource and reuse account

Admission work is O(N) time and O(depth) call stack over receipt nodes. Limit: 131072 nodes **per expected/proposed tree**, depth 32, 4096 characters per string/key, 4096 bits per integer. E2/E3/E4/E5 still replay exactly the same parent proofs; no leaf recomputation is avoided or added. The new scan adds overhead, **not a measured speedup**; no native, STEP, physical-hash or CyberSand evidence. Invalid input returns typed `Refusal`.

## Verification and falsifiers

Commands from `research/experimental/certificate-algebra/core/`:

```sh
python3 -m unittest -v test_receipt_integrity.py
python3 -m unittest discover -v -p 'test_*.py'
```

Seven integrated test methods are authored: ordinary family, old-equality bypass, E2/E3/E4/E5 adversarial receipts, wrong numeric/bool types, oversized/deep/nonprimitive keys and refusal from unbound E5 prediction. Negative controls deliberately demonstrate that old builtin equality returns true on hostile Python values. **Independent reduced CPython check executed**: 500 canonical nested-tree acceptances, 500 mutated-tree refusals and three hostile/type refusals PASS with only the `Refusal` dependency stub. The full integrated original B1 test suite and all exact-parent module tests **were not run in that reduced check**; require independent exact Git-head replay before any integration acceptance.

**Further falsifiers for A3/B5:** malformed nested source *input* rather than proposed receipt; malicious dict-key object before a different caller's source validation; cyclic lists; a real source-verified receipt whose tree legitimately exceeds these budgets; a hash/phase/time mismatch with separately authenticated #462 source ancestry. This E6 patch does not claim to close those independent boundaries.

## Scientific and programme disposition

GO to independent exact-module qualification; HOLD for any cross-lane certificate consumption. Historical 121/20/30/50, 26 machining operations and all unresolved MC-038/PB obligations unchanged. MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false`. No paid/native campaign, production creation, or merge.
