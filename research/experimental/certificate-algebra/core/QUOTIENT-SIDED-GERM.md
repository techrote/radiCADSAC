# B1-E5 — Sided-order transport for a verified rational C0 quotient

**10 November 2026 · DETERMINISTIC_MODEL / experimental research · Draft / HOLD.**
Repository: `techrote/radiCADSAC`; A/B B1-only subtree. Base accepted `main` `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. Existing B1 Draft #473 pre-edit head `1de37944950792ca967db6814cf6db648644e75c`. Falsifier preregistered in coordination issue #324. This is neither a PB-007 acceptance witness nor a physical B-spline producer certificate.

## Precisely admitted grammar and theorem

Take two externally *content-pinned*, independently replayed B1-E4 closed-domain continuous piecewise rational polynomials `N(t)` and `D(t)` over the **same** rational interval `I`. All piecewise power coefficients, rational endpoints and Bernstein weak-cone receipts are checked by the existing B1 E4 parent verifier; `D` has an admitted **strict closed-domain nonzero** sign proof, not just weak POS at interior points. Original parent certificates have a finite bounded piece/degree grammar. Let `t0` be any rational point of `I`. Each available side `s` is one **analytic polynomial extension** of a source cell; interior points use the same cell twice, endpoints have an absent exterior side. The source may have artificial internal partition cuts, which are not authenticated physical knots.

**Conditional sided quotient law.** For each side, write the exact physical-time local expansions `N_s(t0+h)=a_k h^k+O(h^(k+1))`, with the first nonzero `a_k`, and `D_s(t0+h)=d0+O(h)`, where `d0 != 0`. Then `R_s=N_s/D_s` has **exact zero order `k`** on that side and leading coefficient **`a_k/d0`**. If `N_s` is identically zero, so is `R_s` on the side; no isolated event follows. The special case `k=0` is a nonzero value, not a root. Under rational nonzero affine substitution `t=a+b*x`, the order is unchanged, the leading coefficient is multiplied by `b^k`, and for `b<0` physical left and right swap. For any finite source grammar with bounded degree, the algorithm terminates when its parent verifier terminates/accepts; over-budget or mixed-sign parents may refuse and are **not** mathematical counterexamples.

**Proof:** The reciprocal series of `D_s` exists because `d0!=0` and starts `1/d0`; multiplying by `N_s` cannot change its first nonzero order. Substituting `h=b(x-x0)` yields the signed coefficient and swaps the oriented half-neighbourhood when `b<0`. The exact Taylor coefficient of a local power-basis polynomial `P(u)=sum(c_i u^i)`, `u=(t-L)/(R-L)` at `t0` is `sum_{i>=j} c_i binom(i,j) ((t0-L)/(R-L))^(i-j)/(R-L)^j`. This terminates with rational arithmetic and checks all coefficients rather than finite sampling. For an identity-zero polynomial the entire coefficient vector vanishes. The denominator has a single continuous value at the join because its B1 source passes C0 seam verification.

This holds over an **infinite** rational family: `N(t)=0` on `[0,1]`, `N(t)=c(t-1)^k` on `[1,2]`, `D(t)=s*d` on `[0,2]`, with `c` any nonzero rational, `d` positive rational, `s=+1/-1`, and fixed `1<=k<=24` (within the implementation degree budget). Any rational nonzero affine `b` transports the coefficient to `c*b^k/(s*d)` and moves the active side when `b<0`. The fixed finite subset tested does not constitute a completeness claim for arbitrary trigonometric sources.

## Typed verifier and conservative provenance

`quotient_sided_germ.py` calls **the existing** `rational_quotient.verify`, which independently derives the complete E4 quotient receipt from original B1 sources and externally supplied source pins. It then computes the two exact source Taylor germs at the requested point, binds their local claims to the quotient expression hash, parent snapshot pins, exact time and full computational refinement partition. `verify` replays all claims and rejects modified receipts or mismatched expected germ digest. `project_signed_affine` creates only a **non-authoritative prediction**; consumers must separately reauthenticate affine-transformed sources and derive the germ again.

Important source-type distinction: E3/E4's legacy `physical_knots` key actually contains **all common-refinement partition cuts**. This E5 receipt calls them `partition_boundaries` and separately reports whether the original input *piece* boundary occurs at `t0`. Neither proves a genuine structural B-spline knot. `genuine_structural_knot` is always `UNVERIFIED`. Connecting this with #462 requires externally verified complete B-spline controls/knot ancestry, and source identity must not be inferred from mathematical phase normalization. Matching hashes are **content integrity, not authentication** when attacker supplies both payload and pins.

No arbitrary Boolean combination, topology union, physical seam closure, H1/H2 analytic equality, STEP, machining operation, material update, or CyberSand sleeping is implied. A finite sided germ alone does not establish whole-source zero completeness. A1's schema-2 continuum topology and A2's analytic join/knot proof are independently versioned, not implicitly imported.

## Falsifiers and negative tests

1. An accepted strict-nonzero denominator with a local zero, or a quotient sided order differing from the numerator order, disproves the theorem/implementation.
2. Signed negative `b` failing to swap sides or apply `b^k`, or an identity-zero side reclassified as an isolated zero, disproves the transport.
3. A denominator zero exactly at the source seam must yield `Refusal` from E4, never a quotient germ certificate. A mixed-sign or over-budget parent remains unknown.
4. Modified original source with stale external pin, modified E4 receipt, modified E5 sided order, noncanonical rational time, and out-of-domain time must refuse.
5. A computational-only cut or caller-declared source piece seam re-labelled as an authenticated structural knot is an interface failure regardless of correct rational algebra.

## Reproduction and cost limits

At the published Draft head, from `research/experimental/certificate-algebra/core` run:

```sh
python3 -m unittest -v test_quotient_sided_germ.py
```

Nine authored methods check the rational family, signed time reversal against freshly transformed B1 sources, arbitrary refinement, identity-zero continua, isolated tangency, denominator-seam refusal, forged receipts/pins, endpoints and formal Taylor coefficients. **Exact published B1 parent-module execution and independent A3/B5 review remain pending unless separately recorded.** Before publishing, a locally executed independent Fraction oracle (mocked solely for imports) checked **114 formal germs and 456 signed-rate projections**, but did **not** execute E4 parent verification or the entire authored nine-method suite. This is the explicit evidence boundary; no hosted test or exact source replay can be inferred from code compilation.

The new local calculation adds **zero full-leaf Bernstein reproofs after E4 replay**, but reparses O(number of source cells) inputs and performs up to O(degree²) rational operations for each side. A source-independent recomputation would have to reprove leaf signs, seams and quotient provenance, but this comparison counts proof work only, not clock time, memory/allocations, physical performance or trusted source-custody overhead. No speedup is established.

## Dependencies, prior art, review and decisions

- [B1 E4 rational quotient and provenance limitations](RATIONAL-QUOTIENT.md), [B1 E3 refinement](REFINED-PRODUCT.md), B1 E2 closed endpoint sign (`CLOSED-NONZERO.md`). Private B1 helpers are version-coupled; future changes require requalification.
- [A1 Draft #470](https://github.com/techrote/radiCADSAC/pull/470), [A2 Draft #471](https://github.com/techrote/radiCADSAC/pull/471), [#462 knot and affine source transforms](https://github.com/techrote/radiCADSAC/pull/462), [A3's topology finding](https://github.com/techrote/radiCADSAC/pull/470#pullrequestreview-5836323988), [B5 interface warning](https://github.com/techrote/radiCADSAC/pull/473#issuecomment-6758583609).
- Standard formal power series, valuation of a quotient by a unit and polynomial Taylor coefficient identities are **classical**, not claimed novel mathematical theorems. The research contribution is a narrow typed, independently replayable *certificate interface* with explicit refusal and source-seam semantics.

**Current disposition:** research GO for independent challenge; schema/producer integration HOLD. No cross-lane import or core authority promotion. Keep historical 121 original / 20 refused / 30 missing ordered premises / 50 complete original witnesses; 26 operations mandatory; MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false`.
