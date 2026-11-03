# PB-007-01: complete shared-factor squared-amplitude sources

Status: bounded original-source research implementation, 2026-11-03. Evidence class: **DETERMINISTIC_MODEL**. This leaf proves complete supplied-source zero sets within its declared arithmetic and isolation budgets. PB-007-01 remains **OPEN**; MC-B and MC-1 remain **NOT_ESTABLISHED**; production authorization remains false.

Preregistration: [issue #100, comment 6593815602](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6593815602). Measurement base: `384521e111d684a55fe09edfd5ab17c3b41fd426`, whose qualified coprime dependency was accepted in [comment 6593884065](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6593884065). The final integration commit may include disjoint work; these evidence identities remain explicit.

## Result and precise scope

The [model](pb00701_shared_square_source.py) checks an original single-span rational B-spline source of the form

\[
F(t)=C_0(t)+C_1(t)\cos(2\pi\beta(t)),\qquad \beta(t)=b+rt,
\]

against supplied rational polynomial hints P and Q. It reconstructs every original coefficient from its full clamped Bernstein controls in the original global parameter and verifies

\[
C_0=(P^2+Q^2)/2,\qquad C_1=(P^2-Q^2)/2.
\]

Consequently the original source has the exact identity

\[
F=P^2\cos^2(\pi\beta)+Q^2\sin^2(\pi\beta).
\]

Unlike the prerequisite [coprime-square proof](pb00701-coprime-square-source-research.md), the new supplied-source checker preserves nonconstant common factors. For a nonzero pair P,Q, it computes a monic G, verifies exact divisions P=G P0 and Q=G Q0, and proves

\[
F=G^2H,\qquad
H=P0^2\cos^2(\pi\beta)+Q0^2\sin^2(\pi\beta).
\]

The actual qualified generic coprime producer proves the newly constructed H source. A checked bounded Sturm stage proves every closed-interval G root. The original zero set is their ordered union, with source identity and both provenance roles retained at a coincidence. At a G root of multiplicity m, the original order is 2m away from an H root and 2m+2 at an H root. An H-only root has order two. Every nonzero source component is strictly positive.

When P=Q=0, the model verifies the complete original coefficient identity zero and returns a closed-continuum type. Finite events, finite counts and nonzero cells are null, not an empty finite approximation. This branch still checks the same original grammar, moving phase and input envelope; it does not call a residual producer.

Admission is generic within the declared envelope. A supplied source with a new bounded parameter identity, different valid phase, nonunit interval or exact degree elevation can succeed through its own proof. The eight demonstration names are not an allowlist. All examples are separate research sources outside the frozen fifty-source cohort.

## Preregistered hypothesis and falsification criteria

The hypothesis is that exact source reconstruction, a retained common polynomial factor, a freshly proved coprime residual and bounded exact polynomial isolation suffice for complete physical roots, orders and maximal positive cells without an algebraic-field or transcendence engine.

Decisive failures include discarding G, losing its square or nonzero scale, accepting a proper common divisor whose residual remains noncoprime, omitting an open search gap, losing an exact midpoint or exterior root, exporting a G-root endpoint as a nonzero isolator bound, double-counting a coincidence, using a residual report for another source, lowering a claimed order four/six/eight to two, or merging equal-sign cells through a physical zero. Parser exhaustion, excessive bisections, failed actual proof stages or invalid custody must return atomic nontruth. Expected population totals do not discharge any of those obligations.

## Original-source and residual identities

Only explicit cosine channels zero and one are admitted; there are no sine channels. Each coefficient has one fully clamped span over the exact supplied original interval, with degree zero through six. P and Q use ascending rational coefficients in the original global t, with degree at most three. The two coefficient degrees may differ. Correct degree elevation is accepted by exact reconstruction; inaccurate elevation is refused. An explicit zero coefficient channel remains valid.

The qualified producer's bounded lowering reconstructs each Bernstein basis polynomial, verifies partition of unity and uses every original control. The new composition independently checks the returned lowering proof, P/Q square identities, actual gcd divisions and both coefficient identities C0=G²H0 and C1=G²H1. It retains the full original source and hash, the original parameter identifier and affine phase, exact P/Q hints, and the distinct reconstructed residual source/hash.

Monic normalization never discards scale. If a common factor initially has a nonunit leading coefficient, that scale remains in P0 and Q0 and therefore in the residual controls. Fresh residual Bézout evidence establishes that the retained G contains the entire common factor. A caller-supplied gcd label or a source hash alone is not proof.

The residual uses the same global parameter, closed interval, offset and rate as the original source. The model calls `certify_source` on the actual qualified coprime module for this residual. It does not read the saved coprime demonstration report. The returned residual is checked again through the qualified certificate assembler, including complete source reconstruction, coefficientwise Bézout identity, every half-integer candidate and every positive order-two root jet. Formatting a completed replay revalidates these receipts without asking the producer to prove the same residual again.

## Checked polynomial arithmetic and complete root counts

The new routines use the qualified coprime module's bounded rational and polynomial operations. They do not execute the older [MC-032 event engine](../MC-032/event_engine.py), whose source is retained only as a pinned algorithm reference. That older engine has no internal pre-arithmetic bit guard; final-size checks would not justify importing its arithmetic into this leaf's resource contract.

For every Euclidean division, the implementation checks the actual identity A=BQ+R and either R=0 or degree(R)<degree(B). Gcd traces preserve consecutive inputs and terminate at the declared nonzero remainder. The exact reciprocal of its leading coefficient proves the monic normalization. These checks also apply to the gcds used for square-free parts and multiplicities.

For a nonzero polynomial A, the Sturm stage constructs S=A/gcd(A,A') and verifies the exact quotient. Its sequence is S, S', followed by exact negative remainders. It applies no sign-changing rescaling. The returned sequence and every division are checked; a nonconstant square-free sequence must end at a nonzero constant.

The mathematical counting premise is the usual elementary Sturm argument. At a zero of an intermediate sequence member, the adjacent members have opposite signs by the negative-remainder identity, so the total sign variation does not change as that point is crossed. At a simple zero of S, its nonzero derivative gives a decrease of exactly one in variation. Square-freeness and the final nonzero constant exclude common zeros of consecutive members. Therefore the difference of endpoint variations counts exactly the distinct roots between them.

Endpoints use exact one-sided signs. If the first nonzero derivative of a nonzero polynomial at rational q has order k and value v, its right sign is sign(v), and its left sign is (-1)^k sign(v). The checker verifies every lower derivative is zero and the claimed leading derivative is nonzero. Thus `V(a+) - V(b-)` counts the strict open interval even when a or b is a root. The complete closed count adds the two actual original endpoint-root indicators. Boolean/int aliases are rejected for counts, derivative orders and signs.

## Ordered isolation, midpoint roots and boundary cleanup

Before isolating G, the model inserts both original exteriors and every actual rational H root as sorted search boundaries. It evaluates G exactly at each boundary. This identifies all G/H coincidences without comparing arbitrary algebraic extensions or evaluating trigonometric functions at unknown algebraic points.

Every adjacent original open gap receives a checked Sturm count. A zero-count gap is recorded as empty. A gap with one root and nonzero G bounds can be exported as a strict unique open isolator. A linear square-free polynomial supplies its exact rational coordinate directly. Other pending gaps are bisected at exact rational midpoints, with the identity

\[
N(a,b)=N(a,m)+[G(m)=0]+N(m,b)
\]

checked from both actual child count receipts. An exact midpoint root is retained once as a rational root. Source or H boundary roots were already retained and are excluded from the open counts.

There is one global budget of 128 midpoint operations, including splits used only to remove root-valued isolator endpoints. The budget is checked before each split and never resets per root or gap. A constrained internal budget may reduce this ceiling for a negative control; no caller can enlarge it. Exhaustion produces nontruth without a partial successful root list.

The exported G root list is reconstructed from the actual boundary table and every completed trace branch. Its count must equal the complete original closed Sturm count. The trace checker rejects missing, invented or unfinished branches, incorrect midpoint arithmetic, inaccurate work counts and overlapping or duplicated root locators.

A valid algebraic-format coordinate carries the actual square-free polynomial and a proved unique strict rational isolator whose two bounds are nonzeros of G. The polynomial need not be irreducible or minimal; the selected root need not be irrational. Those claims are explicitly false. A rational root not discovered as a boundary, midpoint or linear root may therefore retain this exact descriptor. No exhaustive integer-divisor factorization is needed.

A G isolator bound can itself be an H root, so it can be a zero of the physical F even though it is a nonzero of G. For example, P=0,Q=t²-1/2 and beta=t on [-1,1] admits G isolators (-1,0) and (0,1), while -1,0,1 are residual roots. Their strict-open semantics order the physical events correctly. Shared nonzero G boundaries are valid separators; they do not assert a positive numerical gap between unrelated roots.

## Multiplicity, coincidences and physical components

The finite chain G, gcd(G,G'), and successive gcds with their derivatives strictly decreases in degree. At an isolated G root, each chain member has either one root in that same isolator or none. Divisibility makes this membership nested. The number of containing members equals the G multiplicity. At exact rational coordinates, the model also checks the first nonzero original G derivative directly.

The physical union retains a polynomial-root identifier and, when applicable, a residual event identifier. A coincidence is recognized by exact evaluation of G at the rational H coordinate and contributes one event. Its physical order is the actual sum of twice the polynomial multiplicity and the residual order. H completeness proves positivity at every other G root, including algebraic-format coordinates, so no trigonometric evaluation at such a coordinate is required.

Interior events have smooth even multiplicity and positive signs on both sides. Original exterior events have only the available inward order/sign; outside germs are null and global smooth multiplicity is not claimed. Nonzero exterior values need not be rational: the report records their proven positive sign and leaves the exact scalar null. Root exteriors have exact scalar zero.

Maximal nonzero components use physical root references as boundaries. An algebraic root is never replaced by the endpoint of its isolating bracket. Inclusion is true only at a nonzero original source exterior. Equal positive signs across a touch still produce two separate components.

The admitted class can have physical order eight: P=0,Q=(t-1)³, beta=t gives F=(t-1)^6 sin²(pi t), with order eight at one. It can also have 36 distinct physical roots: P=0, Q=(t-1/10)(t-1/11)(t-1/12), beta=8t on [-2,2] combines 33 residual lattice roots with three additional common-factor roots in a single residual gap. The implementation uses a conservative structural event cap of 68, rather than truncating at an observed demonstration population or the coprime carrier's maximum.

## Demonstration results

The [saved report](pb00701-shared-square-source.json) is generated from actual fresh source proofs. It is a reproducible output to compare, not source authority for later proof calls.

| Research source | P, Q | Complete original roots and orders |
| --- | --- | --- |
| Hidden noncardinal rational | P=Q=t-1/3 | 1/3, order two |
| Polynomial/carrier coincidence | P=(t-1)², Q=t-1 | 1, order four |
| Two algebraic roots | P=Q=t²-1/2 | -sqrt(1/2), +sqrt(1/2), each order two |
| Algebraic/rational ordered union | P=t(t²-1/2), Q=t²-1/2 | -sqrt(1/2), 0, +sqrt(1/2), each order two |
| Repeated common root | P=Q=(t-1/2)² | 1/2, order four |
| Sixth-order coincidence | P=(t-1)³, Q=(t-1)² | 1, order six |
| Complete identity | P=Q=0 | Entire original closed interval; finite counts not applicable |
| Cubic/common source exterior | P=t(t-1)(t+1/2), Q=2P | -1/2, 0, 1, each order two; one right exterior |

The first fresh run derived seven finite sources and one continuum; 12 physical events (eight rational-coordinate and four algebraic-isolator events); 11 interior and one exterior event; 18 maximal positive cells; 11 common-polynomial roots, three residual roots and two coincidences. Nine events have order two, two order four and one order six. Seven actual residual proofs cover 27 half-integer phase candidates. Three actual midpoint operations suffice for these demonstrations. These totals are cross-checks after the individual proofs.

Separate author controls already passed the order-eight example, the clustered 36-root example (two exteriors, 35 cells, four midpoint operations), and the physical-zero/G-nonzero isolator-bound example (five roots, two exteriors, four cells). The distinct-author verifier passed the fresh default contract and all 39 substantive methods. Independent exact-byte review and hosted integration remain separate gates.

## Resource contract and explicit refusals

Raw source and hint tokens must be canonical ASCII integers or reduced ratios, at most 128 characters and 128 bits per operand. Source/hint structures and every raw token are checked before the first input-dependent rational construction. Derived rational tokens have a separate 4096-bit and 2500-character ceiling. The qualified arithmetic checks conservative numerator/denominator growth bounds before each rational addition, multiplication or division; a later cancellation is not permission to exceed the intermediate bound.

The original interval lies in [-2,2]; absolute offset and nonzero rate are at most eight; phase endpoints lie in [-16,16]. The actual residual has at most 65 half-integer candidates, counted before enumeration. Polynomial isolation degree is at most three; coefficient degree is at most six. JSON has a four-MiB, 131072-node, depth-48 envelope, with bounded strings, exact scalar types and no aliased/cyclic containers. Code/reference reads and report paths have independent fixed limits. Direct helper controls cannot enlarge the arithmetic or midpoint ceilings.

The residual producer retains its qualified raw 128-bit coefficient/control envelope. Valid original inputs can therefore receive resource refusal after exact factorization. A concrete example is N=2^100, P=Q=N t on [0,1/N], beta=t. The original C0=N²t² has clamped controls [0,0,1], and C1=0; original hints and knots fit the envelope. Monic G=t leaves P0=Q0=N, so H=N² has a 201-bit constant control. The fresh residual constructor correctly refuses it. The resulting record has `proof_established=false`, `source_zero_set_established=false` and `source_zero_set=null`; it does not report an empty zero set or broaden the dependency contract.

A fixed bisection budget can also refuse a sufficiently difficult admitted polynomial. This is an explicit bounded implementation limit, not a failure of the abstract root-isolation theorem and not a completeness claim about arbitrary rational inputs. Refusal remains atomic and does not promote a partial root list.

## Input custody and exact workflow closure

The model captures and verifies six declared input buffers before executing any project dependency. It compiles only the exact checked qualified coprime source buffer, with no importlib/pyc lookup or preloaded project module. The producer's context-file reads use retained checked buffers and still pass its original exact reference comparisons. A post-read path replacement cannot substitute different executed or parsed bytes. Standard Python and its standard library remain trusted; this is not a hostile-code sandbox.

| Dependency | Exact Git blob | Use |
| --- | --- | --- |
| [Qualified coprime model](pb00701_coprime_square_source.py) | `4db47f79acff3c036e67ba03dd11b9bfb0a96bdb` | Executed generic residual proof and guarded arithmetic |
| [MC-032 event engine](../MC-032/event_engine.py) | `789a709c5141479a343035d1b7055dd4e53534e1` | Nonexecuted algorithm reference |
| [Coupled B-spline boundary](../../../../docs/machining-completeness/31-PB00701-COUPLED-BSPLINE-BOUNDARY.md) | `6005fc55e2d18e71639e6bc31cfbc1597bf4a915` | Nonexecuted grammar context |
| [Coupled original source model](pb00701_coupled_bspline_model.py) | `a086b625e1a6dea8bd202699d161167bb69cc9e7` | Nonexecuted original source context |
| [MTP boundary model](pb00701_mtp_irreducible_boundary.py) | `4f9000549834c8f9b60ebc9925fadb71e9f96acf` | Nonexecuted inherited research context |
| [MTP boundary report](pb00701-mtp-irreducible-boundary.json) | `4840bbca3847962b537684e0dffa871bd6de82a2` | Nonexecuted inherited research context |

The [workflow](../../../../.github/workflows/mc1-pb00701-shared-square-source.yml) lists exactly those six paths and the five owned files in both pull-request and main-push triggers. It uses one Python job, a literal-head checkout and the focused verifier. It consumes no saved coprime report and does not execute MC-032. This leaf does not modify a prior source, fixture, registry, proof producer or workflow.

## Verification and reproducibility

Generate and compare the actual report with:

```console
PYTHONDONTWRITEBYTECODE=1 python3 research/machining-completeness/tasks/MC-038/pb00701_shared_square_source.py --write-report --contract
```

Run the distinct-author [verifier](verify_pb00701_shared_square_source.py) with:

```console
PYTHONDONTWRITEBYTECODE=1 python3 research/machining-completeness/tasks/MC-038/verify_pb00701_shared_square_source.py --contract --self-test
```

The distinct-author verifier passed the fresh default contract and all **39 substantive test methods**, exit zero. The test phase took 11.675 seconds and the full process took 13.306422 seconds; these are local deterministic timings, not native performance qualification. It independently rebuilds original Bernstein identities and exact-Fraction Sturm counts, checks every G/H union and component, and challenges actual stage failures rather than only output strings. Dynamic controls include order eight, 36 physical roots, valid elevated and nonunit sources, typed continuum, G-nonzero/physical-zero isolator bounds, residual-envelope refusal, isolation-budget exhaustion and actual same-buffer custody failures.

Independent review additionally uses known rational/quadratic factorizations for the default G roots and a separate coprime source oracle. Repository validation passed with 360 Markdown files and two RCS-002 fixtures; the machining-completeness self-test passed. Final exact-byte acceptance, hosted literal-head CI, guarded merge and landed-main checks remain the integration owner’s responsibility. No native or paid campaign is involved.

## Alternatives, retained obligations and downstream use

The earlier coprime route remains useful and unchanged for its own sufficient condition. Discarding a common factor would lose real physical zeros, as P=Q=t-1/3 demonstrates. The older product routes do not silently acquire this distinct residual's even-order carrier semantics. The new leaf names its own original source and proof interface.

Executing the unguarded MC-032 engine was rejected for this resource contract. Exhaustive algebraic factorization, minimal-polynomial certification and trigonometric evaluation in algebraic extensions are unnecessary. Square-free polynomial locators plus complete rational residual roots provide the exact ordering needed here. Stationary phase is excluded by the current moving-phase source contract; no altered-rate surrogate certifies a stationary source.

For MSAC, this result supports a precise research representation of touches and persistent zero intervals, without suggesting a production interaction flow. For OpenSimachinist, it supplies a bounded source-bound proof family that preserves original coefficients, source parameter, factors, event identity and physical components. It does not establish native machining geometry, STEP export, an arbitrary coupled B-spline solver, a generic owner route or a production start condition.

The next useful consumers must validate these exact source and dependency receipts, preserve algebraic-locator semantics and honor resource/nontruth results. Further amplitude families, multiple spans and phase laws need separate hypotheses, preregistration and review. The frozen 121-source corpus, fifty-source cohort, historical 20 blocked/30 order-gap dispositions, all 26 operations, PB states and MC/production gates remain unchanged.
