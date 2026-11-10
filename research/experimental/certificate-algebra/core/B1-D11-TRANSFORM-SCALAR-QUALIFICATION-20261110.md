# B1-D11 — exact-rational scalar subclass boundary qualification

**Date:** 10 November 2026. **Status:** RESEARCH GO (bounded Python); CROSS-PRODUCER/NATIVE/STEP HOLD; **DRAFT / DO NOT MERGE**. All work exclusively in `research/experimental/certificate-algebra/core/**`. Parent Draft #473 `4514f337f392393ba60b163f079fed8a96db938a`; accepted main `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. MC-B/MC-1 remain `NOT_ESTABLISHED`, `production_authorized=false`.

## Scope and real consumer falsifiers

The original published `certificate_algebra.py` Git blob `66b2e4e6acb3d330af1de676f370e7a9bd93473b` accepted `fractions.Fraction` subclasses at direct `Piece`, `split`, `affine` and `replace` inputs through `isinstance`. A Python subclass can override arithmetic **after** the base source has been independently checked and an internally minted `Verified` obtained. Therefore the usual internally minted state marker is not enough to make downstream arithmetic sound when transformation scalars remain polymorphic.

Three direct, genuine original-parent demonstrations on CPython 3.13.5:

1. **Affine domain forgery.** `HostileOffset(0).__rsub__` offsets subtraction by +1. The actual original `affine` accepts a correctly imported `P(u)=1+u`, with rate 1 and ostensible offset 0, but produces the domain **[1,2] instead of [0,1]**. This is not the asserted affine source map.
2. **Split source mismatch.** `HostileCut(1/2).__sub__` adds 1/8. The actual `split` accepts and returns a verified-looking right child claiming value **15/8 at t=3/4**, whereas the original source has exact value **7/4** at the same internal time. Source attachment is unsound despite authentic base proof and a successful seam check.
3. **Direct polynomial premise forgery.** `HostileCoefficient(-2).__mul__` returns the absolute value, so the actual original `prove(Piece(0,1,(1,HostileCoefficient(-2))))` certifies `POS` with Bernstein vector (1,3), while the real polynomial `1-2u` has a zero at `u=1/2` and its genuine Bernstein vector is (1,-1).

All four new tests against unmodified original parent **FAIL (4/4)** because no `Refusal` is raised. These are concrete *Python in-process subtype* source-boundary defects, not a refutation of Bernstein positivity, a hash collision, a native geometry exploit, or a physical B-spline event.

## Bounded correction and direct verification

The published actual parent now requires `type(x) is Fraction` for `Piece` interval/coefficients, `split` cut and `affine` offset/rate; it also requires exact integer indices for `split`/`replace` (rejecting `bool`), leaving canonical exact builtin values unchanged. This prevents application-defined arithmetic/equality methods from running on certificate-bearing polynomial and transformation inputs. The new `test_transform_scalar_integrity.py` is parent-imported; tests also prove honest split midpoint evaluation and ordinary identity-affine/update remain unchanged.

- Original complete ten-module source-matched suite: **90/90 PASS** at parent `4514f337f392393ba60b163f079fed8a96db938a`. All **24/24** original B1 Python source/test/benchmark Git blobs matched their published Git identities; the source-identical execution files came from the archived exact-source evidence package.
- Original source with new tests: **4/4 FAIL** for the intended adversarial refusals, while the prior 90 tests remain green.
- Corrected parent with complete 11-module suite: **94/94 PASS**, no skips, CPython **3.13.5**. `python -m compileall -q .` PASS; `python experiment.py` PASS (32 cells, 64 edits, all exact equality controls).
- Five-arm `bench_b1_fair_boundary_20261110.py`, same host, two warmups and five symmetric repeats, 64-edit exact intermediate hash parity: efficient full reproof median **115.808 ms**, trusted incremental **43.999 ms** (2.63x); full+strict readmission **289.355 ms**, incremental+strict readmission **215.316 ms** (1.34x). Performance is CPython **DETERMINISTIC_MODEL**, not native/STEP, and excludes independent producer/code/physical-window custody and real kernel recomputation.
- Fixed source Git blob (prepublication locally tested): `c2f2c5b13bf3f26292a46389ee62e4f4e69056a2`; new test Git blob: `3a5428304bf8f2afd1c72b4a4720cf5d5bb32ac6`. Both must be checked against the published commit before considering them source-verified.

## Trust assumptions, pending laws and native relevance

The accepted grammar is an **untrusted JSON/primitive boundary plus exact builtin Fraction objects only**. This edit does not secure a process against arbitrary Python code using `object.__setattr__`, module globals, monkeypatching or callbacks; no Python in-process guard can act as cryptographic external custody. Externally supplied `Verified` states must still replay the full base proof and ancestry. Nonprimitive `Fraction` subclasses now refuse **before** their mathematical operators execute. The long-running split/affine theorem remains the classical closure law only over exact rational inputs.

Actual A1 Draft #470 has subsequently advanced from previously directly tested `976ec8c...` to `fe0dada7c430053c4c387f17a062909da9aab8bc` (live status at start of this run); current A2 Draft #471 remains `d9cb56e74e876efb203e04003aadcf8bd368a369` with A3-demonstrated source-identity forgery in its real `sparse_phase_germ` verifier. No authenticated current A1/A2 cross-producer admission is claimed: B1 `producer_codec` self-stamps older heads, and physical original B-spline controls/knots/window and independently held source-hash pins are still absent. A1 direct prior receipt is historical relative to now and does not establish current provenance.

The 2.63x/1.34x Python figures demonstrate a potentially reusable certified local-update algorithm, **not** performance gain in the native source-consumer, journal/replay or STEP reconstruction path. To claim economic relevance, independently qualify the authenticated producer and actual native recomputation avoided, then compare every-edit provenance verification, re-proof, source hashing, invalidation and memory under the same physical workload and native build. If cost exceeds saved proof work, the optimization is NO-GO for that consumer even if the algebra remains sound.

**Scoped decision:** **GO** for this newly hardened bounded Python scalar grammar; **HOLD** for independent A3/B5 exact-head challenge, A2 custody, authenticated A1/A2/physical origin, #462 transplants, native savings, merge and MC gates. Frozen original 121/20/30/50 census, 26 operations and immutable historical evidence unchanged.
