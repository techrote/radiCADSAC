# A1-F4 — Whole-cell event atlas from exact common polynomial carriers

**10 November 2026. Research only / DETERMINISTIC_MODEL / Draft HOLD.** Accepted main: `48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; existing A1 Draft PR #470; #324 source claim #6757871466. All changes confined to `research/experimental/analytic-events/isolator/**`. Not MC-038 acceptance, native geometry, STEP or production authorization.

## Prior mechanism and missing lemma

MC-038 #453 has a bounded exact rational interval H0/H1/H2 partition that finds simple crossings and can refuse unresolved tangencies or knot zeros. A1-F3 supplies *one signed local algebraic event*, not an exhaustive atlas. A2 owns genuine clamped B-spline sided jets; #462 owns B-spline knot/control transformations; B1 handles Bernstein certificate composition. A new full-domain result is valuable only if it covers a provable infinite class with complete root accounting, rather than re-proving another historical V12/V6 source.

**Admitted class:** 1–3 consecutive rational closed pieces in [-16,16], five rational polynomial channels H0,C1,S1,C2,S2 of degree <=10, coefficient tokens <=128 bits, common rational affine phase `pi*(a+b*t)` with b != 0, and equal values of corresponding coefficient channels at each shared piece boundary. This is a sufficient C0 continuity test, **not** authentication of genuine B-spline controls or knot origin. A2/#453's 2*pi phase convention is not implicitly interchangeable.

## Conditional global carrier theorem

For one piece, define

\[
F(t)=H_0(t)+\sum_{h=1}^2\{C_h(t)\cos(h\pi(a+bt))+S_h(t)\sin(h\pi(a+bt))\}.
\]

If every channel is zero, the whole closed piece is an **IDENTITY_ZERO_CONTINUUM**. Otherwise, compute the exact monic rational polynomial gcd P of all nonzero channels. Exact Euclidean division reconstructs F=P H, with another rational-polynomial Fourier source H. Require an **exhaustive closed interval cover proving H strictly positive or strictly negative**, using A1-F3's existing source-level `signed_cell.cofactor_closed_sign` Machin/Taylor/Lipschitz guard over every tile; all leaves must be contiguous and have the same sign.

**Theorem:** The complete physical zero set of F on that piece is exactly the real-root set of P. Exact Sturm isolation of its square-free part provides all distinct roots in open rational brackets, while exact endpoint linear deflation handles rational endpoint roots. The gcd-with-derivative chain provides each root's multiplicity, and the carrier/cofactor product gives exact left/right signs and CROSS (odd) or TOUCH (even). Sturm count-zero gaps are strictly signed using an exact rational evaluation. Consecutive C0 pieces share **one physical knot** event rather than two independent event occurrences, with distinct left and right analytic orders; a continuum side stays typed and absorbs its boundary.

**Proof:** The strict closed cofactor cover excludes every zero of H, including transcendental zeros, over the *entire* supplied piece. Thus F and P have precisely the same zeros, with identical multiplicities and sided signs up to sgn(H). Exact Sturm variation gives complete distinct-root counts for square-free rational P. A split point is deliberately chosen to be a rational non-root, preserving count additivity even if the midpoint is itself a rational event. Finite root separation ensures rational isolation; exact derivative-gcd repetition recovers multiplicity. C0 channel equality implies identical physical source value on both sides of each supplied join. These are classical Euclidean/Sturm/Rolle and analytic nonvanishing arguments; **not** a novel general trigonometric/exponential-polynomial zero theorem.

Fair interval subdivision and increasing Taylor precision would eventually sign-certify any continuous cofactor bounded away from zero on the compact domain, but the implementation has finite caps and therefore **may refuse even mathematically admissible inputs**. Caps: <=8192 Sturm nodes, 64 requested binary-width bits, <=12 cover levels, 4–32 rational trigonometric series terms, maximum 3 pieces. A refusal is NONTRUTH, never root-free.

## Published deterministic model and falsifiers

- `carrier_partition.py`: exact canonical source reader, rational gcd/derivative/Sturm atlas, strict cofactor tiling, signed event and knot receipts, fully reconstructive verifier. The only imported proof primitive is existing A1-F3 `signed_cell.cofactor_closed_sign`, published blob `f74767532d3bf9dac9d92b7e7f98114eb48eaa80`.
- `test_carrier_partition.py`: ten stdlib adversarial test methods, including mixed H1/H2 nonconstant channels, repeated tangencies, four close-root pairs down to 2^-48, 48 varying rational-family parameters, pure H1 cosine carrier without DC, signed negative phase, true piecewise analytic kink with orders 2/1, identity-zero continuum, real sine-zero cofactor refusal, tamper and malformed-resource controls.
- Execute from this directory: `python3 -m unittest -v test_carrier_partition.py`.

Pre-registered falsifier: any accepted atlas that misses a polynomial root, collapses close roots, invents a zero-free H despite its hidden root, mislabels an even tangency, admits a false C0 seam, duplicates a physical knot, loses a continuum, permits receipt/source/phase mutation or calls a budget refusal a zero-set proof.

**Scratch executed evidence:** 10/10 test methods PASS against an exact-arithmetic local reconstruction of A1-F3's sign kernel; 48 parametric instances, four close-root families. Separately, independent SymPy 1.14 exact-algebra checks matched **120 rational polynomials, 406 distinct interior roots and the tested root multiplicities**, with no disagreement. The *published upstream A1-F3 Python module* was **not** executed locally as exact Git bytes: the workspace had a separate arithmetic mirror. A3 must replay the test suite with exact original sibling source. Neither finite testing nor SymPy is proof of a larger domain.

## Limits and decisive negative control

The source `H(t)=sin(pi*(t-1/2))` on [0,1] has common channel gcd 1 but an interior root at t=1/2. A valid strict closed-sign atlas necessarily refuses, demonstrating that **polynomial carrier extraction is sufficient, not necessary**, for complete H0/H1/H2 event isolation. Some genuine square-lift tangencies studied in A1-F2 also have no common polynomial factor and remain outside this class. Supplied coefficient piece boundaries are not authenticated physical B-spline knots. SHA-256 binds the supplied JSON, not an external trusted producer; arbitrary Boolean/topology composition, native/STEP output, broad interior Skolem decidability and all original-source reclassification remain open.

The mathematical ingredients are established prior art. See Basu–Pollack–Roy, *Algorithms in Real Algebraic Geometry* (Springer, 2006), and Chonev–Ouaknine–Worrell, *On the Skolem Problem for Continuous Linear Dynamical Systems* (ICALP 2016), https://doi.org/10.4230/LIPIcs.ICALP.2016.100 . The broader bounded continuous Skolem problem is not claimed solved.

**A3 challenge:** exact-head replay, Sturm subdivision precisely at rational roots and adjacent true source knots, forged receipt controls, source-germ sign disagreement. **B1 challenge:** closed strict cofactor sign versus Bernstein weak sign and the missing trusted A2/#462 physical source codec. This A1 receipt cannot authorize an imported B-spline source.

All original 121/20/30/50 evidence remains unchanged, 26 machining operations preserved, newly closed original IDs 0, required PB/PO obligations OPEN. MC-B/MC-1 remain `NOT_ESTABLISHED`; `production_authorized=false`. No protected source, gate, production repo or author branch was modified.