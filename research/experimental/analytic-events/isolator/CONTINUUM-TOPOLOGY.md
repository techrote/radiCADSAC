# A1-F5 — Maximal zero continua and typed knot topology

**Status:** 10 November 2026; speculative analytic-event research / DETERMINISTIC_MODEL; Draft PR [#470](https://github.com/techrote/radiCADSAC/pull/470); **HOLD for independent A3/B1 exact-head replay**. Accepted main at start: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`. F4 source/test blobs before patch: `d7e2da94343c7f2830b0eca6416b05420876df81` and `5ac83efa23f818078f9fd9e935e004829788e53a`. Scoped preregistration: [#324 comment 6758618812](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6758618812). A3 independent falsifier: [review 5836323988](https://github.com/techrote/radiCADSAC/pull/470#pullrequestreview-5836323988).

## Precise original defect and falsifier

F4's old `SINGLE_PHYSICAL_KNOT_ZERO` was emitted for all four mutually different true-degree-two, clamped C0 B-spline cases with knots `[0,0,0,1,1,2,2,2]`, H0 control vectors `[0,0,0,0,0]`, `[0,0,0,0,1]`, `[1,0,0,0,0]`, and `[1,0,0,0,1]`; the other four channels vanish. Their complete physical zero sets are, respectively, `[0,2]`, `[0,1]`, `[1,2]`, and `{1}`. The old per-knot continuum flags retained this distinction, but `kind` did not, so a consumer treating that kind as a singleton was unsound. This is **a certificate-consumer/type defect**, not a refutation of F4's conditional polynomial-carrier theorem.

**Preregistered falsifier:** any accepted new receipt with mismatched maximal identity interval, a zero knot mislabeled isolated/continuum, component coalescing across a positive-width nonidentity piece, a duplicate continuum from adjacent zero pieces, or a source/receipt forgery that `verify` accepts.

## Theorem — finite analytic pieces, exact continuum topology

Let `[a_0,a_1],...,[a_(n-1),a_n]` be strictly positive-width, contiguous closed rational source pieces. The supplied rational H0/H1/H2 coefficient channels agree at each common boundary, hence the joined source is C0 (though **genuine B-spline source and knot provenance are not authenticated**). Assume each piece has passed F4's **complete** conditional classification: either it is identically zero on the entire closed piece, or it factors as `F_i=P_i H_i` for a nonzero rational polynomial `P_i` and a rigorously closed-sign, everywhere strictly nonzero analytic cofactor `H_i`.

Then:
1. Every positive-length connected component of the physical zero set equals a **maximal union of consecutive identity-zero pieces**. A nonidentity piece has only finitely many zeros and cannot contribute a positive-length zero interval.
2. At a zero join, **neither identity side** gives a locally isolated zero; **one identity side** gives the boundary of a maximal zero continuum; **both identity sides** gives an interior join of a maximal zero continuum. These cases are mutually exclusive and exhaustive.
3. A singleton knot between two nonidentity pieces is locally isolated even if either polynomial carrier has a multiple zero there. The isolated point must be retained only once, with distinct left/right germ orders.

**Proof:** Nonidentity `P_i` has finitely many zeros, and a nonzero `H_i` cannot introduce zeros. The zero set of identity pieces is their closed piece union. Contiguity and positive width permit exactly adjacent identity pieces to merge; inserting any nonidentity piece inserts an open subset free of zeros. At a C0 join, the two endpoint values are equal; the F4 verifier already rejects mismatched zero status. The adjacent piece type therefore determines precisely which of the three topological cases applies. The construction is a finite scan of `n` verified piece records, so complexity is **O(n)** time and **O(n)** worst-case additional receipt space (maximal components); no new trigonometric evaluation or proof engine runs in a hot path.

This is standard connected-component topology of finite piecewise analytic zero sets, applied as a sound typed certificate-composition rule. It is **not a novel mathematical zero theorem** and does not establish unrestricted continuous-Skolem decidability.

## Research-model implementation and refusal semantics

- `carrier_partition.certify` now emits schema **`a1-carrier-partition/2`**, `zero_continua` as exact maximal closed rational interval endpoints, and distinct knot kinds `ISOLATED_PHYSICAL_KNOT_ZERO`, `ZERO_CONTINUUM_BOUNDARY`, `ZERO_CONTINUUM_INTERIOR`, `STRICT_NONZERO_KNOT`.
- `verify` reconstructs the entire version-2 receipt, including schema, components, kinds and existing source/phase/germ evidence. Legacy version-1 receipts are **not silently upgraded**; consumers must reverify/reconstruct. This is intentionally an additive *research* schema change, not a production contract.
- Original F4 Sturm/strict-cofactor sign proof, endpoint multiplicity, crossing/touch and refusal budgets are unchanged. The complete returned zero set is the union of `zero_continua`, existing Sturm-isolated interior root events, and isolated zero knots, with continuum endpoints **absorbed**, not duplicated. Isolating brackets denote exact algebraic singleton roots but are not floating-point root coordinates.
- Identity-zero pieces are recognized from zero Fourier channels, not merely an observed run of zero numerical samples. The explicit A3 four-case fixture uses genuine B-spline Bernstein controls, but the **F4 intake remains untrusted supplied coefficient pieces**. An authenticated #462/A2 source/structural-knot contract is still required before physical acceptance.

## Deterministic verification, evidence and negatives

Command from `research/experimental/analytic-events/isolator`: `python3 -m unittest -v test_carrier_partition.py`. Two newly authored tests reconstruct the exact quadratic B-spline polynomials from all five control values, exercise all four topological kinds, validate positive-width coalescing over three pieces, and attack forged kinds and component intervals. Existing close-root, signed knot orders, identity continuum and receipt-forgery tests are preserved. **The full exact published-module test was not run in this execution environment; its result remains pending**, so the PR stays Draft/HOLD.

A separate executed **MEASURED_INDEPENDENT_ORACLE** using SymPy exact degree-two B-spline basis independently checked **36 rational control pairs × 18 strict-interior rational points = 648 exact equalities**, including signed nonzero controls and all four zero topologies. This controls the mathematical fixture reconstruction, not the new GitHub module or source-intake binding. Existing F4's previously reported 10/10 exact module pass applies only to its **old** source/test blobs and must not be carried forward as a pass for schema 2.

**Negative/limitations retained:** nonidentity analytic cofactor with an unresolved zero refuses F4; a merely coefficient-continuous arbitrary piece break is not proven to be a physical B-spline knot; rational zero intervals do not imply the entire root atlas is physically authenticated; A2's same-local-germ/different-global-zero-set example still requires complete source binding; nonlinear topology/Boolean result composition is unproved. If a downstream consumer expects the old `SINGLE_PHYSICAL_KNOT_ZERO` string, it must fail closed pending requalification. No original V12/V6 proof reopened.

## Source-critical prior art and handoffs

Elementary univariate polynomial zero-set finiteness, Sturm isolation and Bernstein spline construction are established techniques; see Basu, Pollack and Roy, *Algorithms in Real Algebraic Geometry*, 2nd ed. (Springer 2006), and de Boor, *A Practical Guide to Splines* (revised ed., Springer 2001). Broader continuous Skolem zero questions are not solved by this local composition; cf. Chonev, Ouaknine and Worrell, *On the Skolem Problem for Continuous Linear Dynamical Systems*, ICALP 2016, DOI [10.4230/LIPIcs.ICALP.2016.100](https://doi.org/10.4230/LIPIcs.ICALP.2016.100).

**A3 independent request:** execute the literal schema-2 module/test against exact `signed_cell.py` blob; independently compare actual quadratic B-spline basis, test source substitution, and try identity-continuum/nonsmooth-knot counterexamples. **B1 consumer request:** reject legacy untyped F4 knot claims; require complete zero components and source/structural-knot custody before common-refinement/topology composition. No merge pending separate review and source-bound checks.

Original **121/20/30/50** census and all **26** machining operations unchanged; no historical sources reclassified; PB/PO obligations OPEN; MC-B and MC-1 **NOT_ESTABLISHED**; `production_authorized=false`. No MC-038 producers, proof registry, programme authority, native/STEP, production or outside-subtree edits.
