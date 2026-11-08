# MC-038 / PB-007-01 — commuting exact B-spline insertion with affine source-time transformation

**8 November 2026 · DETERMINISTIC_MODEL · prospective research · no accepted-main integration or capability promotion.**

## Source and ownership

This isolated sibling-composition branch starts from independently Ready [#459](https://github.com/techrote/radiCADSAC/pull/459) exactly at `1ce5f9334fdac8bcd216a21d6b8ee1085ece6b76`, and imports all three ADD-only files of independently Ready [#461](https://github.com/techrote/radiCADSAC/pull/461) unchanged from `64678b89f6e4b0051710fbe63193060a9a929729`. Both descend from Ready [#458](https://github.com/techrote/radiCADSAC/pull/458) and its #457 → #455 → #453 exact H0/H1/H2 event dependencies. The new synthesis is an **additive research integration candidate**. It does not advance, replace, or write [#397](https://github.com/techrote/radiCADSAC/pull/397)'s exclusive accepted-main integration authority.

The two source siblings operate on the same bounded five-field rational B-spline grammar, but have not previously been qualified together. Insertion and source-time reparameterization are individually verified; their **composition** and original-vs-inserted knot provenance under negative orientation were not separately source-certified.

## Falsifiable commuting-square theorem

Let `S` be one admitted clamped rational B-spline H0/C1/S1/C2/S2 source with complete event certificates. Let `I_f(S,t)` insert one permitted structural knot `t` in field `f`, and let `A_{a,b}(S)` represent the exact invertible source-time substitution `t_old=a+b*t_new`, where `b != 0`. The new testable identity is

```text
             I_f(S,t) -- A_(a,b) --> A_(a,b)(I_f(S,t))
               ^                            ||
               |                            ||  identical exact supplied knots,
               |                            ||  controls, all span polynomials,
               |                            ||  physical H0/H1/H2 events
               |                            ||
                 S ----- A_(a,b) -----> A_(a,b)(S)
                                         |
                                     I_f(_, (t-a)/b)
                                         |
                                         v
                              I_f(A_(a,b)(S),(t-a)/b)
```

The implementation constructs both paths independently and refuses unless their **entire canonical supplied source, including every field's rational knot/control vector**, agrees exactly. It also independently lowers both terminals into the canonical rational polynomial source and checks all pieces, source hash, derived identity, and genuine-vs-introduced knot multiplicity. Every intermediate insertion edge is checked against the original's full coefficient polynomials; every affine edge is checked by exact full-piece rational polynomial composition with the transformed moving phase. Negative `b` must reverse both knots and controls and correctly map the inserted coordinate.

For a certified commuting square, all four individual edges carry **separately replay-verifiable exact parent proof receipts**. Each complete-event proof remains bound to its actual supplied source and requested precision, and all eight before/after physical root-count claims must agree. The verifier independently reconstructs the two complete source paths *without rerunning the expensive complete-event generator*, then independently replays the four original leaf certificates rather than assuming a matched hash proves physical truth.

### Decisive falsifiers and guards

- Any difference in terminal knot/control vectors, polynomial coefficients, phase slope or source hashes.
- Wrong signed mapping `(t-a)/b`, mislabeled introduced knot as pre-edit, transformed structural-knot multiplicity drift, or incorrect source-bound event proof.
- Forged top-level precision, a child event's precision/count, child receipt substitution, a mutated source, claimed historical membership, newly closed original, PB/PO discharge, MC-B/MC-1 acceptance, or production authorization.
- Invalid source, unsupported repeated knot, noncanonical rational input, zero scale, or arithmetic/spans outside declared parent budgets. These cases must refuse as **NONTRUTH**, never as a zero-event claim.

### Qualification cases

Six focused tests include exact reverse-time H1/H2 genuine-knot tangency with a newly inserted knot; positive half-rate scaling; insertion at an *already existing simple knot* where multiplicity changes without changing the underlying source; 32 bounded exact diagram challenges across both H0 and degree-zero S1, both affine orientations and multiple knot positions; altered precision, lineage, count, source, and gate claims; and inadmissible knot/map controls. They supplement—not replace—both parent leaf self-test suites and the inherited #458/#457/#455/#453 proofs.

Reproduce on the **literal committed head**:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_bspline_insert_affine_commutation_20261108.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/pb00701_bspline_knot_insertion_lineage_20261108.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/pb00701_bspline_affine_time_covariance_20261108.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
```

The dedicated workflow runs these exact-head checks and inherited proof checks separately from complete frozen V54/V2 producing reconciliation and MC-1 static authority validation. An independent source-critical mathematical review is required before moving the synthesis PR from Draft to Ready. Do not self-merge into accepted main.

## Exact scope and nonclaims

Only the inherited bounded degree-0..3 clamped *non-weighted* coefficient B-splines, at most four union spans, limited rational parameters, one insertion per path, and parent-certifiable physical events. No arbitrary NURBS weights, repeated general refinements, nonlinear time mappings, general event isolation, physical machining-history reversal, STEP, topology, native material or production implementation. A structural source document SHA-256 does **not** imply frozen historical original-corpus membership.

Frozen V54 **121 original sources / 20 historical route refusals / 30 missing ordered premises**, V2 **50 already complete source-specific witnesses**; before/after deltas all zero. Newly closed original IDs `[]`, additional required PB/PO discharges `0`, MC-B and MC-1 both `NOT_ESTABLISHED`. All 26 required operations and native/STEP qualifications remain unchanged. Research acceptance is not programme-gate acceptance.

## Independent integration decisions still needed

The #397 owner must decide whether to accept #459 and #461 independently or to admit this composite source as one guarded dependency, after comparing their exact provenance, passing *merged-head* CI, and securing an independent source-critical review. The two original Ready research siblings remain intact and open; do not infer acceptance from this draft synthesis.