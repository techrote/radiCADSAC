# PB-007-01 — complete bounded source proofs from coprime squared amplitudes

Status: deterministic research implementation, 3 November 2026. Task: [MC-038 / issue #100](https://github.com/techrote/radiCADSAC/issues/100). Preregistered scope: [comment 6593562765](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6593562765). Qualified base: `8190ae2c474fcb6fa9a54851abc03f481a5685d3`. Final exact-byte review, hosted checks and integration acceptance are separate from local results.

## Purpose and new bounded contribution

This leaf checks a supplied complete original single-span B-spline source and rational polynomial hints `P,Q`. It proves a complete finite zero set when exact coefficient reconstruction establishes

\[
F(t)=P(t)^2\cos^2(\pi\beta(t))+Q(t)^2\sin^2(\pi\beta(t)),
\qquad \beta(t)=b+rt,
\]

with a nonzero rational phase rate and an executed, coefficientwise verified polynomial Bézout identity `A P + B Q = 1`. The public checker admits valid bounded inputs outside its saved demonstration inventory. Fixture names and source hashes are not an admission allowlist.

The constructive result is stronger than a numerical sign scan: every physical zero must occur at one of finitely many exact rational phase contacts. Each surviving contact has exact order two, even when a vanishing amplitude has a repeated polynomial root. Positive maximal nonzero components and original exterior germs are then determined exactly.

The source theorem is a bounded sufficient condition. Nonconstant common divisors, stationary phase, unsupported source channels or pieces, malformed data and exhausted limits return nontruth. A refusal does not mean that the function has no zeros or that another method cannot solve it.

## Programme and historical scope

The [MC-1 programme](../../../../docs/machining-completeness/00-PROGRAMME.md), [DR-0026](../../../../docs/decisions/DR-0026-machining-completeness-programme.md) and [execution protocol](../../../../docs/machining-completeness/07-EXECUTION-PROTOCOL.md) govern this research. PB-007-01/02/03/04 remain open, MC-B and MC-1 remain `NOT_ESTABLISHED`, and production remains unauthorized.

No member is added to the frozen fifty-source cohort or 121-source corpus. The historical 20 blocked and 30 order-gap dispositions, all 26 operations, previous reports and qualified/refused routes remain unchanged. The first demonstration re-proves the already qualified [MTP quadratic source](pb00701-mtp-irreducible-boundary-research.md); the other seven are new research examples outside the frozen cohorts. Their roots are per-source occurrences, not sixteen new historical completions.

Polynomial GCD arithmetic and trigonometric carrier methods already occur in the repository. The specific contribution here is complete supplied-source admission for this nonnegative square-sum class, with exact reconstruction, automatically checked coprimality, complete phase enumeration and order-two original-source germs.

## Source grammar and exact admission

An input specification has the established `RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE` grammar and retains its supplied original parameter ID. This slice requires exactly two explicit cosine channels, harmonics 0 and 1, and no sine channels:

\[
F(t)=C_0(t)+C_1(t)\cos(2\pi(b+rt)).
\]

Each coefficient is one fully clamped Bernstein/B-spline span on the full supplied closed interval `[lo,hi]`. The two degrees may differ and may be anywhere from zero through six. The source's knots, controls, degrees, interval, global phase and parameter ID are all validated and bound in its certificate.

The implementation lowers every coefficient in **global original t**, using

\[
B_{i,d}(t)=\binom di
\left(\frac{t-lo}{hi-lo}\right)^i
\left(\frac{hi-t}{hi-lo}\right)^{d-i}.
\]

It verifies the partition of unity, every basis coefficient, the full control-weighted polynomial and both clamped endpoint states. It then proves the coefficient identities

\[
C_0=(P^2+Q^2)/2,\qquad C_1=(P^2-Q^2)/2.
\]

No selected control, endpoint sample or witness label can substitute for those complete identities. The global phase is not evaluated in a local Bernstein coordinate. Nonunit intervals and negative origins therefore retain their actual meaning.

Correct degree elevation is admitted whenever those identities hold within the degree bound; the original elevated controls and distinct source hash remain in the certificate. An inaccurate elevated control fails reconstruction. An explicit identically zero `C1` channel is valid: `P=Q=1` represents the strictly positive constant source. Requiring explicit channels is the interface's representation contract, not a claim that an omitted-zero representation is mathematically impossible.

The parameter ID is an arbitrary bounded nonempty string without NUL, rather than a fixture-specific name. A changed phase, parameter or coefficient specification can be a different valid input and receive its own fresh certificate. Reusing an old certificate after changing any such binding fails canonical validation. Opposite signs of P or Q are also legitimate hints when their squares reconstruct the same source; each supplied witness remains separately bound.

## Coprimality is executed and verified

The bounded extended Euclidean algorithm records exact polynomial dividends, divisors, quotients and remainders. Every division identity and strict degree decrease is checked. The final nonzero constant GCD is normalized, producing rational polynomial A and B. A second exact coefficient calculation verifies `A P + B Q = 1`; a returned success flag or claimed GCD degree is insufficient.

That identity excludes every common real or complex zero of P and Q. Zero P is permitted exactly when Q is a nonzero constant under this condition; zero Q is analogous. Both-zero input refuses. A nonconstant GCD refuses even if another argument might prove no common real root: the present premise is the specific verified Bézout identity.

A decisive negative example is `P=Q=t−1/3`, phase `beta=t`, on `[0,1]`. The original source is `(t−1/3)^2` and has a genuine zero at `1/3`, away from all half-integer phase candidates. Skipping coprimality would allow an incorrect root-free result. The checker instead refuses this input with no established zero set.

## Complete root theorem

Both summands in the reconstructed square sum are nonnegative. At a source zero, both must vanish. Sine and cosine cannot vanish simultaneously, while the verified Bézout identity prevents simultaneous zeros of P and Q. Exactly two branches remain:

1. `beta(t)` is an integer, P(t)=0 and Q(t) is nonzero.
2. `beta(t)` is an odd half-integer, Q(t)=0 and P(t) is nonzero.

These conditions are also sufficient. They exhaust the physical roots, including source exteriors. In particular, a polynomial amplitude zero at a nonmatching phase is not a physical zero.

For the exact closed phase range `[beta_min,beta_max]`, compute

\[
m_{\min}=\lceil2\beta_{\min}\rceil,
\qquad m_{\max}=\lfloor2\beta_{\max}\rfloor.
\]

Before allocating any range or list, check the candidate count `max(0,m_max−m_min+1)` against its finite bound. Each integer m gives the exact original coordinate

\[
t_m=\frac{m/2-b}{r}.
\]

The rate is nonzero, so different m give different coordinates. The candidates are ordered by t, reversing phase-index order when the rate is negative. Exact rational evaluation of P and Q selects the appropriate branch. The returned candidate proof is checked for complete index coverage, exact coordinate/phase binding, parity, closed-source membership, amplitude values and Boolean root decisions.

An empty candidate phase range is a valid positive case. For example, `P=Q=1`, `beta=1/8+t/16` on `[0,1]` has no half-integer candidates and one positive closed nonzero component. Completeness here follows from the theorem, not from an empty numerical sample.

## Why every admitted root has order two

At an integer-phase root t0, expand in the original increment `delta=t−t0`. The quadratic Taylor coefficient of F is

\[
P'(t_0)^2+\pi^2 r^2 Q(t_0)^2.
\]

Its first rational term is nonnegative. Its rational coefficient of pi squared is strictly positive because r and Q(t0) are nonzero. The function value and first derivative vanish, so the source root has exact order two. At an odd half-integer root the same argument gives

\[
Q'(t_0)^2+\pi^2 r^2 P(t_0)^2>0.
\]

The certificate records the rational root coordinate, original phase index and value, the vanishing amplitude and derivative, the nonzero opposite amplitude, the original rate, and both exact rational jet coefficients. The caller rechecks these premises and coefficients for every returned root jet. This argument needs only the standard trigonometric zero sets/identities and pi nonzero; neither pi irrationality nor a transcendence conjecture is used.

For `P=(t−1)^2`, `Q=1`, phase t, the vanishing amplitude has a double polynomial zero, but the source still has order two: the rational jet term is zero and the pi-squared coefficient is one. Assigning source order four would be incorrect.

At an original exterior, the certificate retains only the inward order-two germ and positive inward sign. Outside order and sign remain null. The expression's analytic extension is not substituted for an original-source outside germ.

## Complete nonzero components and exterior values

Every nonroot source point is strictly positive: the reconstructed function is nonnegative, and the exhaustive zero theorem excludes equality there. Ordered rational roots therefore split maximal connected nonzero cells even when both adjacent signs are positive. Interior touches are never merged into a single component.

Original nonzero exteriors belong to their adjacent cells; zero exteriors do not. No empty cells are created outside an exterior zero. Event references and coordinates remain bound to the supplied source hash and original parameter.

At a noncardinal exterior, the function value need not be rational. The output records its exact positive **sign** from the complete square-sum proof and leaves the scalar value unclaimed. It does not invent a rational evaluation. At a proved root, the exact scalar value is zero.

No continuum is admitted under the coprime, moving-phase hypotheses. A rejected shared-factor or stationary source may still have isolated roots or a continuum; the refusal record therefore has `source_zero_set: null` and `source_zero_set_established: false`.

## Default demonstration

The following inventory is a finite demonstration of the generic checker. Each original source is reconstructed and proved afresh; its expected root count is not an admission rule.

| Case | Domain | P | Q | Phase beta | Exact roots |
|---|---|---|---|---|---|
| Prior MTP quadratic touch | [1/2,3/2] | t−1 | 1 | t | 1 |
| Nonmatching amplitude zero | [0,1] | t−1/2 | t+1/4 | t | none |
| Interior/exterior touches | [0,1] | t−1 | t−1/2 | t | 1/2, 1 |
| Three closed touches | [0,1] | t(t−1) | t−1/2 | t | 0, 1/2, 1 |
| Zero P | [0,2] | 0 | 1 | t | 0, 1, 2 |
| Zero Q | [0,2] | 1 | 0 | t | 1/2, 3/2 |
| Negative rate | [0,1] | t(t−1) | t−1/2 | 1−t | 0, 1/2, 1 |
| Nonzero offset | [0,2] | t−3/2 | t−1/2 | 1/4+t/2 | 1/2, 3/2 |

The first fresh executable contract derived 27 phase candidates, 16 per-source closed root occurrences, seven original exterior roots, nine strict-interior roots, 16 order-two jets and 17 maximal positive cells across eight sources. One source is root-free. These totals follow record-level checks; coincident coordinates in different sources are not deduplicated.

Independent positive controls extend beyond the inventory: valid degree-six elevation, arbitrary parameter IDs, `P=Q=1`, repeated vanishing amplitudes, nonunit/negative-origin domains, empty candidate ranges and the maximal phase range. In the latter, `P=0,Q=1,b=0,r=8` on `[-2,2]` yields 65 candidates, 33 roots and 32 positive cells. A derived-coefficient control uses 128-bit-bounded raw inputs whose Bézout coefficients require more than 128 bits, exercising the separate result budget.

## Public interfaces and failure propagation

`check_source(spec,P,Q)` returns a complete fresh certificate or typed atomic nontruth. `certify_source` is the throwing equivalent used by the verifier. `validate_certificate` binds all supplied source and witness data and compares against a fresh proof; a submitted successful certificate never replaces reconstruction or Bézout work.

The actual proof-stage hooks are `lower_source`, `compute_bezout`, `enumerate_phase_candidates` and `prove_root_jet`. Their outputs are separately checked for source identities, Bézout equality, exhaustive candidate coverage and positive jets. Missing or malformed stage output cannot become an empty successful root list. These boundaries also let the independent verifier inject actual computation failures and inaccurate proof data, rather than testing only final report strings.

`source_from_polynomials` creates bounded demonstration inputs but is not admission authority. The verifier constructs controls independently. `replay_sources` executes all default proofs; `report_from_replay` validates the actual retained proof premises and source topology. `expected_report` is a fresh run. Public report validation preflights the candidate before fresh execution and canonical comparison.

## Resource envelope

Every raw source and hint token is validated before the first Fraction constructor on the public proof path. Inputs require canonical ASCII integer/ratio strings, at most 128 characters and 128-bit numerator/denominator operands. Polynomial hints have degree at most three. Source coefficient degrees are at most six, with full clamping and exactly degree-plus-one controls per channel.

Original coordinate endpoints have absolute value at most two; offset and rate at most eight; the rate must be nonzero. Exact phase endpoints must lie in `[-16,16]`, implying at most 65 half-integer candidates. Exact negative floor/ceiling and closed endpoint inclusion are preserved.

All derived rational operands and polynomial arithmetic are bounded by 4,096 bits. Addition, multiplication and division growth is checked before the operation; bounded exact cancellations do not permit an unbounded intermediate. Derived tokens may use up to 2,500 characters. Parser control parameters themselves have exact types and hard ceilings, so callers cannot widen the input/derived budget. Euclidean and division loops have degree-descent limits, and internal polynomial degree is capped at twelve.

The wrapper permits 2 MiB JSON buffers, 65,536 value nodes, depth 32, bounded exact scalar types and 4,096-character strings/report paths. Cycles/shared containers, duplicate JSON keys, floats/exponent numbers, Boolean degree/order/index aliases and noncanonical rationals are refused. Context files are bounded to 256 KiB. These limits are an executable research envelope; resource refusal remains nontruth even when the mathematical source is otherwise meaningful.

## Reference custody and workflow closure

Four qualified files provide bounded **nonexecuted context**:

| Reference | Git blob |
|---|---|
| Coupled B-spline grammar document | `6005fc55e2d18e71639e6bc31cfbc1597bf4a915` |
| Coupled B-spline model | `a086b625e1a6dea8bd202699d161167bb69cc9e7` |
| Qualified MTP boundary model | `4f9000549834c8f9b60ebc9925fadb71e9f96acf` |
| Qualified MTP boundary report | `4840bbca3847962b537684e0dffa871bd6de82a2` |

Their exact paths, blobs, byte counts and SHA-256 values are captured from bounded verified buffers. None of their project code is imported or executed. The first demonstration retains the prior MTP source specification exactly, but its proof is computed by the new generic checker. No saved MTP conclusion or broader MTP theorem is imported as proof authority.

The verifier compiles the new model from its exact checked source buffer, preserving assertions and future flags. Stale bytecode and preloaded modules must not replace that buffer. Python and the standard library are trusted; no hostile-Python sandbox is claimed.

The workflow contains exactly the four context paths plus the five owned paths in each trigger: nine entries. It runs one Python job on the literal requested revision, with the focused fresh contract and adversarial suite. There is no project proof dependency hidden behind a context label.

## Verification commands and remaining qualification

The first fresh model run passed:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/machining-completeness/tasks/MC-038/pb00701_coprime_square_source.py --write-report --contract
```

The distinct-author verifier passed the fresh default contract and all **41 substantive test methods**, including checked-buffer bootstrap controls and inaccurate actual proof-hook outputs. Its test phase took 1.015 seconds and its full process took 1.221768 seconds. These are local deterministic-model timings, not native performance qualification.

The verifier uses separately generated Bernstein controls, an independent exact lowering strategy, Bézout/Euclid checks, exact phase enumeration and a direct jet derivation from original C0/C1 coefficients. A separate standalone reviewer oracle imported no candidate or project code and matched 112 original amplitude-identity nodes, 315 individual basis checks, all 27 candidates, 16 direct source jets, eight coprimality/Bézout checks, seven exterior roots and 17 exact physical cells. Run the focused suite with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/machining-completeness/tasks/MC-038/verify_pb00701_coprime_square_source.py --contract --self-test
```

Decisive failures include the noncardinal shared-factor zero, stationary phase, wrong complete source coefficients, inaccurate degree elevation, old-certificate rebinding, missing/duplicated candidates, false parity, wrong root order, omitted opposite-amplitude nonvanishing, merged equal-sign touches, fabricated exterior values, actual stage failures, oversized inputs, and source/report custody drift.

Repository validation passed with 358 Markdown files and two RCS-002 fixtures. The machining-completeness self-test passed, as did the unchanged 121-case frontier contract and its 21 negative controls. No native or paid campaign is part of this leaf. Independent exact-byte review, hosted CI, guarded merge and main-push qualification remain the integration owner's responsibility.

## Implications

For OpenSimachinist, this gives a new bounded original-source predicate class with complete constructive rational events, including repeated-amplitude touches that a simplicity shortcut would mishandle. It does not establish a general event solver, material construction, three-dimensional topology or engineering output.

For MSAC, retaining original phase, parameter, source identity and inward exterior germs supports future reproducible operation semantics. This adds no application interface, production repository or native capability.

Potential future extensions include other exact nonnegative decompositions, more general source-piece composition or separately proved shared-factor/stationary cases. Such work must retain the current counterexamples and receive its own reviewed specification. The present sufficient-condition checker does not silently broaden itself when a required premise fails.
