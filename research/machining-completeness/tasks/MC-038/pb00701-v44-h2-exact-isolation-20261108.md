# MC-038 / PB-007-01 — exact rational isolation of frozen V44's full H1+H2 physical event

**8 November 2026 · DETERMINISTIC_MODEL · bounded constructive source-specific research.** This is a strictly additive successor to [#448](https://github.com/techrote/radiCADSAC/pull/448), whose unchanged original-source verifier and exact uniqueness theorem are used as prerequisites. Coordination: [#324](https://github.com/techrote/radiCADSAC/issues/324). The separate [#397](https://github.com/techrote/radiCADSAC/pull/397) owner retains exclusive main integration. No merge or authority promotion.

## Previously unresolved useful step

#448 correctly disproves deleting a nonzero H2 coefficient and substituting the H1-only root *as the original physical root*. It establishes uniqueness, multiplicity and sign order of the **full** physical event, but leaves its source-coordinate bracket at the coarse open interval (0,1). This successor constructs **strict rational brackets with certified physical signs** at the requested resolution, *using the full unchanged H1+H2 equation*. The bracket, not a rational surrogate root, is the deliverable.

## Exact frozen source and equation

Case `harvested:verify_pb00701_v44:ffaea08e30c9`, source-spec SHA-256 `d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2`, whole-row SHA-256 `7423adadf8c52ff28d47d9f63effbc5a2a7a630bdaf7efe6f8eeb1d2a85c5600`. Frozen V54/V2 Git blobs `5841c331579489b25caef38cd412bdbf286f9134` / `e52d3baf3692a011cf86234eeaa992ef407d99fd`. Original parameter **`pb00701-v44-algebraic-orientation`**, not re-labelled source-time.

For original source coordinate `0<=t<=1`,

```text
C(t) = -3/2 + t + 2t²
S(t) = -1/2 - t + 2t²
theta(t) = pi*(-1/4 + t/8)
epsilon = 1/100000000
F(t) = C(t)*cos(theta) + S(t)*sin(theta)
     + epsilon*cos(2*theta)
```

The frozen original has one clamped quadratic H1 source span and one genuinely nonzero constant H2 cosine. The source and the preexisting historical V2 witness are checked by #448's exact immutable original-source contract. Its proof states that both `F` and the H1-only *control* have exactly one simple root and source signs NEGATIVE/POSITIVE, and that the full root lies strictly before the H1-only root. This successor does **not** treat the control root as a physical event of the original.

## Constructive rational enclosure theorem

1. For positive rational `x=1/k`, the alternating arctangent expansion has an **exact** rational lower partial sum after `2n` terms and an exact upper bound after `2n+1` terms. Machin's identity `pi=16 atan(1/5)-4 atan(1/239)` yields strict rational bounds `pi_lo < pi < pi_hi`.
2. For rational `q` with `|q|<=1/2`, the interval `q*[pi_lo,pi_hi]` encloses the **actual** trigonometric argument. Let its rational midpoint be `z`, radius `rho`. Taylor polynomials of degrees `2n+1` (sine) and `2n` (cosine) have rigorous absolute remainders `|z|^(2n+3)/(2n+3)!` and `|z|^(2n+2)/(2n+2)!` respectively. Both sine and cosine are 1-Lipschitz, so adding `rho` to either error encloses the actual value. The implementation enforces `|z|<2`.
3. Multiplying these rational intervals by **exact original** `C(t), S(t), epsilon`, respecting sign reversal for negative coefficients, then summing, gives an enclosure `[L(t),U(t)]` for the **unmodified** `F(t)`. Only `L>0` or `U<0` yields a proved sign. An enclosure containing zero refuses, never infers absence of a root.
4. The source-specific proof from #448 establishes strict increasing normalized root function and exactly one simple root. Bisection begins with independently proved negative `F(0)` and positive `F(1)`, and updates only after a **strict** certified pivot sign. It tries two alternate interior rational pivots if a midpoint cannot be decided. Once `hi-lo<=2^-bits`, strict endpoint signs and uniqueness prove the root in the open bracket `(lo,hi)`.
5. The same machinery independently isolates the H1-only control by **explicitly setting epsilon=0 for that control alone**. At 40 binary bits its control bracket is disjoint from and strictly after the original full-equation bracket, constructively corroborating #448's exact source-coordinate inequality.

There is **no floating-point computation in the proof**, sampled root-count inference, precision-dependent truth shortcut, or arbitrary-coordinate substitution. Taylor/Machin n and requested binary bits have explicit budgets (maximum 64 each); an undecidable sign or exhausted bracket budget produces typed NONTRUTH. This is a bounded source-specific isolator, **not** a guaranteed total solver for arbitrary analytic functions or H1/H2 source grammars.

## Run and acceptance

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_v44_h2_exact_isolation_20261108.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
```

The research workflow runs these jobs on a literal PR-head checkout. Tests challenge authenticated original provenance, exact rational pi and trigonometric enclosures, full H2 source endpoint signs, nested bracket refinement, distinct H1/H2 versus H1-only exact brackets, reversed hypothetical H2 sign, final endpoint sign recertification and refusal of malformed/oversized requests. Host CI and independent mathematical review must be completed before Ready. A conditional #448 dependency remains; this branch targets #448 rather than accepted `main`.

## Truth limits and historical custody

Historical before=after: **121 original cases, 20 route refusals, 30 missing ordered premises, 50 preexisting complete V2 witnesses**. This V44 source was already complete in V2, so **newly closed original IDs []**, required PB/PO discharged **0**. PB-007-01 and PO-04/05/08 are not established. MC-B and MC-1 remain **NOT_ESTABLISHED**; no native geometry, material/topology, journal, durable bodies, 26-operations guarantee, engineering STEP or production authorization is implied. A proven rational bracket is an exact representation of an implicit physical event, **not** an exact rational root coordinate.
