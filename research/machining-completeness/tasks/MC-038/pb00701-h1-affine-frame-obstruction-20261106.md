# MC-038 / PB-007-01 — affine H1 phase-frame obstruction on two frozen originals

**6 November 2026.** **Evidence class:** \`DETERMINISTIC_MODEL\`, exact rational source/provenance mathematics. **Disposition:** a bounded negative **C** research candidate, subject to literal-head CI and distinct-session source/mathematical admission. **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Task-local reservation:** [#324/6685257607](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6685257607).

## Falsifiable hypothesis and named obligation

Under **PB-007-01**, affecting **PO-04/05/08**, test the proposed shortcut \`AFFINE_PHASE_FRAME_ERASES_H1_SINE_WITH_UNRESTRICTED_AMPLITUDE\`:

> For the exact original-source H1 Fourier coefficient pair \(C(t),S(t)\) on its original first nonempty open span, find real constants \(a,b\) and a **differentiable real scalar amplitude** \(A(t)\), which may be irrational, radical or nonpolynomial, such that
> \[
> (C(t),S(t))=A(t)(\cos(a+bt),\sin(a+bt)).
> \]
> The source time, original spline controls, true knot, harmonic orientation and original physical phase cannot be altered.

Unlike [#434](https://github.com/techrote/radiCADSAC/pull/434), this hypothesis admits *nonconstant affine rotation*. Unlike [#435](https://github.com/techrote/radiCADSAC/pull/435), it imposes **no rational-function restriction on the scalar amplitude**. It still forbids a nonlinear phase-frame angle. This is an information-preserving coefficient-pair statement, **not** an arbitrary equality after substituting just one physical phase.

**Falsifier:** derive a strict exact obstruction for the same original coefficient pair, not a numerical inability to find a frame. This report exhibits a signed polynomial Wronskian nonzero at every point of both selected original spans, contradicting every affine-frame candidate. Refute this negative result by demonstrating a source/provenance mismatch, an error in the polynomial identity, or an actual affine-frame representation satisfying the equations on an open source interval.

## Exact historical source identities and original semantics

The verifier reads, rehashes and checks **all** original source records from frozen V54 corpus Git blob \`5841c331579489b25caef38cd412bdbf286f9134\`, and all previously accepted complete source-specific V2 witnesses from blob \`e52d3baf3692a011cf86234eeaa992ef407d99fd\`. The 121/50 audit and source SHA-256 conventions are independently reexecuted from the accepted, pinned checker blob \`944565a534adc6703189291ac2cc55b97ad4736c\`.

| Frozen historical original | Canonical source SHA-256 | Original first span and coefficients | Historical V54 status |
| --- | --- | --- | --- |
| \`composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0\` | \`4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2\` | Whole [0,2]; true knot 1; global phase turns \(t/8\); first [0,1] has \(C=t-\frac12,\ S=1\) | Missing ordered premise |
| \`harvested:verify_pb00701_v9:4e7b85fa122a\` | \`a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10\` | Whole [0,1]; no interior knot; global phase turns \(t/8\); first [0,1] has \(C=1,\ S=t-\frac12\) | V43 uncertified route |

The first original's cosine H1 has degree 1, clamped source knots \`[0,0,1,1,2,2]\`, controls \`[-1/2,1/2,1/2,1/2]\`; sine H1 has degree 0, knots \`[0,1,2]\`, controls \`[1,1]\`. Its harmonic-zero cosine coefficient is exactly zero, not a suppressed nonzero contribution. The first-span controls lower to the displayed rational polynomials by the original Bernstein/Cox–de Boor semantics. The distinct right span is **not** removed or relabelled; the falsification requires only one original open span.

The second original has H1 cosine and sine degree-one clamped knots \`[0,0,1,1]\`; controls \`[1,1]\` and \`[-1/2,1/2]\` respectively. Its source interval, parameter ID \`source-time-t\`, exact phase turns and historical refusal are preserved. Original complete-row SHA-256 identities are respectively \`406ec73609a8213051afd3361478416e496c782b2b89ae2a857b772146059279\` and \`62346bbddca22c4271a14c10aa130327013ac7cf8daa0b0ae515257e8f28cfad\`.

Both historical source identities **already have complete V2 source-specific zero-set witnesses**. No new physical root or signed cell is claimed.

## Finite exact obstruction and mathematical termination

For real differentiable coefficients \(C,S\) on an open source interval, the alleged affine frame yields
\[
C=A\cos(a+bt),\quad S=A\sin(a+bt).
\]
Differentiating and subtracting, with all \(A'\) contributions cancelling, gives the necessary **signed Wronskian** identity
\[
W(t):=C(t)S'(t)-S(t)C'(t)
=b\big(C(t)^2+S(t)^2\big)=bq(t).
\]

For both frozen originals,
\[
q(t)=\left(t-\frac12\right)^2+1=t^2-t+\frac54 >0
\]
over every real \(t\). Direct exact rational differentiation establishes
\[
W_{\mathrm{V9}}(t)=-1,\qquad W_{\mathrm{V43}}(t)=+1.
\]
If \(b=0\), the identity demands \(W=0\), contrary to either constant. If \(b\ne0\), it demands a nonzero constant polynomial equal to \(b\) times a genuine degree-two polynomial throughout a nonempty open interval, impossible. Thus **neither original first span admits an affine phase-frame with any differentiable real amplitude**.

The same necessary-condition lemma is valid for *any nonzero real-polynomial pair* \(C,S\) with **nonzero \(W\)**: if \(d=\max(\deg C,\deg S)\), the sum of two real squares \(q=C^2+S^2\) has degree exactly \(2d\), while \(W=C S'-S C'\) has degree **at most \(2d-1\)**, making \(W=bq\) impossible for any real constant \(b\), except in the trivial zero-\(W\), \(b=0\) case. In particular, no nonzero-W polynomial pair can follow a constant-angular-velocity frame. This lemma is a **necessary-condition exclusion**, not a positive classification of all zero-W pairs and not a theorem about analytic physical roots.

**Termination:** polynomial coefficient extraction, exact rational derivatives/products, integer degree and signed coefficient equality are finite by construction. The verifier's small explicit rational/byte/degree caps cause typed nontruth refusal; it does not infer absence of a phase frame, a root or nonmonotonicity from a numeric scan, timeout, rejected certificate or failed resource budget. The signed Wronskian proof is complete for the admitted original H1 pair independently of such caps.

## Independent controls, refusal, and reproduction

The [task-local Python verifier](pb00701-h1-affine-frame-obstruction-20261106.py) checks original source/row digest, creator/grammar, spline degree/knots/controls, original phase and time, complete earlier V2 witness, and all 121/50 original source bindings. It independently recomputes W and q, compares the [full machine receipt](pb00701-h1-affine-frame-obstruction-20261106.json) and rejects malformed or duplicate-key receipt JSON.

Positive controls (no obstruction) include proportional polynomial H1 pairs, a fixed-orientation sine component, a simple signed scalar root, an exact order-two tangency and two extremely close rational scalar zeros separated by \(2^{-120}\). Negative controls are the exact \(-1,+1\) original signed Wronskians. Identity-zero directionless sources, Boolean-as-integer, malformed degree, mutated H1 controls/knots/phase/case status/V2 receipt, spoofed proof sign and false historical reductions are refused. These **synthetic controls are not new frozen cases** and do not themselves prove physical root event coverage.

Reproduce on the exact PR checkout:

~~~sh
python3 research/machining-completeness/tasks/MC-038/pb00701-h1-affine-frame-obstruction-20261106.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract --self-test
python3 tools/validate_machining_completeness.py
~~~

The first command checks frozen provenance and bounded C. The second reexecutes the original full 50-source producing V2 reconciliation. The last checks programme static authority. The dedicated workflow checks literal Git head and invokes these checks; do **not** infer their execution from this text alone.

## Matched historical census and limits

| Same immutable historic cohort | Before | After | Delta |
| --- | ---: | ---: | ---: |
| Frozen original sources | 121 | 121 | 0 |
| Uncertified historical V54 routes | 20 | 20 | 0 |
| Missing ordered-span premises | 30 | 30 | 0 |
| Existing complete V2 original-source witnesses | 50 | 50 | 0 |
| Newly closed original IDs | 0 | 0 | 0 |
| REQUIRED PB/PO discharges | 0 | 0 | 0 |

The historical 50 cover 49 finite zero sets and one typed continuum, unchanged. This **C** only falsifies the specified affine phase-frame shortcut for the named frozen original spans. **It does not rule out** a nonlinear phase rotation with radical amplitude, alternative source/harmonic encodings, correct implicit transcendental root representations, generic analytic event decidability, source-bound full physical sign transfer, or native material/topology/STEP realizability. A quadratic Wronskian obstruction to rephasing does **not** show the physical source is nonmonotone.

PB-007-01/02/03/04 and PO-02/04/05/07/08 remain **OPEN**; MC-B and MC-1 remain **NOT_ESTABLISHED**. Evidence is \`DETERMINISTIC_MODEL\` only, never independent engineering oracle, native geometry or actual usable STEP. Maintain all **26 required operations**, exact original phase/source timing, source-knot semantics, canonical manufacturing journal, durable material bodies and lineage, topology, nontruth refusal, STEP-first output contract and production authorization \`false\`. Do not edit historical failures, the frozen V54/V2 registers, proof/programme registries, current-authority or the separate current-state ledger.

## Integration handoff and next critical path

Only four *new*, task-local files on a scoped branch. [#397](https://github.com/techrote/radiCADSAC/pull/397) retains the **exclusive main-integration reservation**. Leave this a **Draft PR** pending distinct-session source-critical review and exact corrected-head CI. A later authorized owner must recheck live accepted main, collision claims, literal PR head and unresolved review threads, then integrate only with consent and independently qualify landed main. The mathematical critical path remains a reusable orientation-preserving, sine-bearing moving-phase event isolation and physical sign/owner-to-consumer theorem—not more repeat proofs of V2-complete originals.
