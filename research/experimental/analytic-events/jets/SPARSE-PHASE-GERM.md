# A2-SPARSE-001 — Sparse mixed-rate local difference germs

**10 November 2026 · Draft research · DETERMINISTIC_MODEL · not an MC-038 gate result.** This is a third, ADD-only local research increment on A2 [Draft PR #471](https://github.com/techrote/radiCADSAC/pull/471), following phase-gauge normalization. Preregistered [#324 lease #6759663239](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6759663239). Accepted `main=48222d6c40b15ad42cc36d56e6d25f3b284e7fc9`; pre-edit A2 head `d72681cde186730eb54e6db26c2b11891415be9c`.

## Target, falsifier, and existing scope

A3 independently produced [the mixed-rate 31/32 falsifier](https://github.com/techrote/radiCADSAC/pull/471#pullrequestreview-5836736092): the *separately* H1-admissible analytic expressions `cos(2πt/31)` and `cos(2πt/32)` require dense common-frequency harmonic indices 32 and 31, exceeding the eight-harmonic index budget of A2-PHASE-001. This is a **budget refusal**, not a mathematical failure. A1 [#470](https://github.com/techrote/radiCADSAC/pull/470) studies interior event isolation; A2's [original rational-point moment kernel](RESEARCH.md) already proves separated-degree valuation for a **shared** rate; [PHASE-GAUGE.md](PHASE-GAUGE.md) handles exact expression identity for distinct rates but is not a sparse mixed-rate *local-order* certificate. This experiment does not duplicate either claim.

**Preregistered falsifier:** At rational `t0=0`, right-minus-left must have first nonzero Taylor coefficient `(63/492032)π² t²`, order 2, positive on both sides; rational rates `1/n,1/(n+1)` must work without dense lcm-index expansion. Signed rates, phase aliases, pi-polynomial leading-sign ties, malformed inputs and forged receipts must never assert unsound local truth.

## Admitted mathematical grammar and theorem

Let `t0` be rational. Each of **two separately specified** analytic expressions has the form

```text
F(t) = P0(t) + Σ_{h=1}^2 [Ph(t) cos(2πh(a+b t)) + Qh(t) sin(2πh(a+b t))]
```

where `a,b` are rational, `b != 0`, and each amplitude is a rational polynomial; the two expressions **need not have the same rate, sign, phase offset or source hash**. At the chosen point require each nonzero term's `h(a+b*t0)` to be a quarter turn (an element of `(1/4)Z`). Phase rotations are then in `{0,±1}`, so every source coefficient is rational, and a Gaussian extension is not necessary. No assertion is made for a source at a non-quarter local phase; it is typed `NON_QUARTER_LOCAL_PHASE`.

For `s=t-t0`, subtract the left expression from the right. Shift polynomial amplitudes exactly. Rotate each cosine/sine pair by its actual phase at `t0`, convert negative signed rates by flipping the sine coefficient, **then accumulate identical absolute rational frequencies** without forming a dense common lattice. This yields a unique finite decomposition

```text
D(t0+s) = Σ_{j=0}^d s^j Aj(πs)
Aj(z) = Cj,0 + Σ_{q ∈ Sj} [Cj,q cos(qz) + Sj,q sin(qz)],
q ∈ Q_{>0} distinct.
```

For each `j`, put `m_j=|S_j|`, and `δ_j=1` iff the constant channel is nonzero. If `Aj` is not identically zero, it satisfies the constant-coefficient differential equation with annihilator `D^δ_j Π_{q ∈ Sj}(D²+q²)`, order `M_j=δ_j+2m_j`. By ODE uniqueness, its first nonzero derivative is among orders `0..M_j-1`. All its Taylor moment coefficients are **exact rational numbers**. If no moments are nonzero through that finite budget, `Aj` was the zero expression (or the implementation has violated an invariant). The finite first moment order is `r_j`.

At fixed overall Taylor order `n`, contributions from distinct polynomial-amplitude degrees `j` occur as distinct powers `π^{n-j}` with rational coefficients. **Transcendence of π** therefore proves no such nontrivial contributions cancel. Hence

```text
ord_t0(D) = min_j(j+r_j), when D is nonidentity;
ord_t0(D) ≤ max_j(j+M_j−1) ≤ d + δ + 2m−1.
```

For an identity expression every sparse coefficient vanishes, and the output is `ANALYTICALLY_IDENTICAL`, **not** a physical-knot or isolated-zero claim. The result holds for an **infinite rational-rate and rational-polynomial family**; implementation limits below are resource policy, not theoretical impossibility. It does not prove zero isolation away from `t0`.

For a nonidentity germ, its leading coefficient is a nonzero rational polynomial `Σ c_k π^k`. Strict sign is decided using exact rational intervals for Machin's identity `π=16 arctan(1/5)−4 arctan(1/239)` and alternating-series remainder bounds. An exact nonzero rational polynomial in transcendental π is separated from zero, so unbounded interval refinement terminates mathematically. The checker tries at most 64 rational terms and **refuses sign certification** if this budget does not separate zero. Right sign is the leading sign; left sign multiplies by `(-1)^ord`. This is a local analytic germ, not a guarantee of actual physical contact topology.

**Established prior art, not new mathematics:** finite exponential-polynomial annihilators, uniqueness for constant-coefficient ODEs, rational root-of-unity rotations, π transcendence and certified alternating-series bounds. Relevant academic survey: Heittokangas, Ishizaki, Tohge and Wen, *Value distribution of exponential polynomials and their role in the theories of complex differential equations and oscillation theory*, *Bull. London Math. Soc.* 55 (2023), DOI [10.1112/blms.12719](https://doi.org/10.1112/blms.12719). The useful new research **interface scope** is sparse **cross-rate** local comparison under authenticated candidate-expression hashes, not a newly discovered theorem.

## Reproduction and independently checkable results

From A2's exact Draft branch:

```sh
cd research/experimental/analytic-events/jets
python3 -m unittest -v test_sparse_phase_germ.py
```

- **8/8 local CPython test methods PASS**, covering 28 members of `t^p[cos(2πt/(n+1))−cos(2πt/n)]`, `p=0..3`, `n∈{3,7,31,32,101,997,4096}`. For every positive integer `n`, the leading coefficient at `t=0` is `2π²(1/n²−1/(n+1)²)` times `t^{p+2}`, strictly positive; left parity is `(-1)^p`. Rates become arbitrarily close as `n→∞`, with no numeric tolerance.
- The independent SymPy 1.14 differentiation check for A3's original exact pair gives `0, 0, 63π²/492032` for Taylor coefficients of orders 0, 1, 2 respectively; the implemented sparse moments give exactly `[(2, '63/492032')]` as the coefficient of `π²`.
- Exact phase-alias identities `sin(2πt/4)=cos(2π(1/4−t/4))` and `sin(−2πt/31)·(−1)=sin(2πt/31)` refuse to invent an event.
- Leading coefficients `1−2π²/q²` for `q=2` and `q=7` exercise *opposite strict signs* with both `π⁰` and `π²` contributions.
- Full recomputation refuses source substitution, altered derivative order, forged sided sign or falsely claimed B-spline ancestry. Oversized control vectors, non-quarter phases, invalid rates, unsupported harmonics and out-of-interval event times are typed nontruth/refusal.
- **Exact source bytes verified on published Git blobs:** `sparse_phase_germ.py` blob `db97ff3329334be3f095c300aa84cefd3765410b` (8089 bytes), `test_sparse_phase_germ.py` blob `e8b56afb1835b43ddaa29bdfc64e69b04f2e418c` (4863 bytes), matching locally executed test sources. No full original A2 parent suite, native geometry, STEP or literal-head dedicated hosted A2 runner is claimed.

Implementation policy: two sources, `h ∈ {0,1,2}` each, degree at most 3, built-in tuple/list arrays, built-in rational/int inputs of at most 160 bits, and a 4096-bit intermediate guard on moment/group arithmetic. No fixed cap on the **normalized dense harmonic index** because none is constructed. Full receipt replay is `verify(left,right,t0,claimed)`, hashes are ordinary SHA-256 **fingerprints, not signatures**.

## Physical source custody, counterexamples and next obligation

Although source canonicalization binds the **complete supplied analytic expression and interval** as an independent SHA-256 fingerprint, this experiment **does not** authenticate complete originating B-spline knot/control arrays, establish genuine physical-knot ownership or verify that an analytic continuation is the active piece of a physical machining source. It can compare candidate germs at a boundary, but only the externally verified spline-source adapter and #462 transformation ancestry can promote that boundary to a structural knot. Even exact analytic identity of expressions does not make their source histories or physical knots interchangeable.

A3 should challenge the sparse accumulator with coincident/opposite frequencies, high-order rational-polynomial ties, negative-rate phase substitution, malicious input resource limits and independently differentiated exact Taylor coefficients. B1 should challenge the envelope contract: a source hash **cannot** be substituted for #462 verified complete spline ancestry; identity and knot-sided semantics must remain distinct. An additional worthwhile falsifier is whether a proposed consumer mistakenly treats `ANALYTICALLY_IDENTICAL` as equivalent physical source lineage.

**Disposition:** GO for standalone, bounded analytic-model verification; HOLD for independently reviewed parent-module integration and physical source authentication. The historical **121 / 20 / 30 / 50** census, all **26 machining operations**, MC-B/MC-1 `NOT_ESTABLISHED`, `production_authorized=false`, native/STEP and production restrictions remain intact. No original V12/V6 witness was reclassified; newly closed historical IDs: none.

## A2-SPARSE-002b — hostile Python receipt-equality negative result and correction

**10 Nov 2026; source-critical correction, not a new mathematical theorem.** After the initial three-file Draft publication at head `62361034d9b450345b644980c77f38121020c02c`, a local adversary constructed a `class EqualAlways` with `__eq__` returning `True`, replaced the `right_sign` of an otherwise legitimate receipt with an instance, and ran the original `verify(left,right,t0,forged)`. It **incorrectly accepted the forged receipt** (observed `ACCEPTED forged equality object? True`). Root cause: normal recursive Python dictionary equality invokes the attacker's object equality method. This compromises the **research verifier input contract**, not the moment/order theorem, a JSON-safe receipt consumer, historical MC-038 or native geometry. [Scoped corrective lease #6759752565](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6759752565).

**Corrected research verifier:** `same_receipt(expected,claimed)` recursively enforces *exact built-in Python types* (`dict`, `list`, `str`, `int`, `bool`, `None`) before comparing scalar values. It checks dictionary/list lengths before inspecting nested contents, requires string dictionary keys and exact key sets, and refuses any subclass/custom equality object. Thus both adversarial `EqualAlways` and truthy `True` replacing an expected integer are rejected, including forged nested `moment_terms` and a 100,000-item list. It compares the freshly re-derived source-bound expected receipt; it does **not** rely on a supplied hash or signature as proof. Normal receipts still pass.

**Source-matched local verification:** `python3 -m unittest -v test_sparse_phase_germ.py` completed **8/8 PASS** on the exact final `sparse_phase_germ.py` Git blob `db97ff3329334be3f095c300aa84cefd3765410b` (8089 bytes) and test blob `e8b56afb1835b43ddaa29bdfc64e69b04f2e418c` (4863 bytes); local Git object SHA-1 calculations match the published GitHub read-backs. The *pre-fix* source/test blobs `49ae56ae181cbf7c60f6cdaee31d3e501f693343` / `f1ef28f109000f3e48af292a25be61dbe428b097` are retained here as reproducible negative evidence, **not** as acceptable verifier versions.

**Remaining limits:** This guards the returned receipt's Python type/equality boundary, not arbitrary unbounded external network payload ingestion or independently verified physical-source provenance. Exact-head hosted A2-specific Python replay and independent A3/B1 review remain pending; no native or gate authority changes.

