# MC-038 / PB-007-01 — Original V43 affine-H1 Cayley polynomialization boundary

**Status:** exact, original-source **bounded negative result C**, 4 November 2026; draft admission, not a new accepted PB theorem. **Evidence:** DETERMINISTIC_MODEL. **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Coordinator:** [#324 claim 6640564663](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6640564663).

## Purpose, named obligation and falsifiable route

PB-007-01 (dependencies PO-04/05/08) needs complete physical zero events, exact ordering, endpoint/knot semantics and signed open cells for the supported rational B-spline, rational-affine-phase analytic grammar. The previously qualified constant-coefficient first-harmonic Cayley child route is useful but restricted to rational-constant Fourier amplitudes.

**Precisely challenged proposed extension:** `DIRECT_AFFINE_H1_CAYLEY_RATIONAL_POLYNOMIALIZATION`. Replace rational-constant first-harmonic coefficients with degree-one rational B-spline coefficients, use the *same* `z=tan(pi*p)` phase chart, clear rational denominators, and then invoke an ordinary rational-polynomial root/count/order solver **without introducing another nonrational function or proving its zeros**.

The falsifier succeeds if the exact transformed physical numerator contains an essential nonrational function of z on a real open chart interval. It fails if the original source is misidentified, the affine amplitude cancels, or an exact rational/polynomial identity actually eliminates the term. The negative result is about **direct algebraic polynomialization**, not the computability of the full analytic event problem, nor the soundness of qualified constant-amplitude Cayley proofs.

## Original frozen source and custody

The unchanged original [v54 121-case corpus](pb00701-finite-owner-corpus-v54.json), Git blob `5841c331579489b25caef38cd412bdbf286f9134`, contains:

| Field | Original value |
|---|---|
| Case ID | `harvested:verify_pb00701_v9:4e7b85fa122a` |
| Source canonical SHA-256 | `a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10` |
| Historical row SHA-256 | `62346bbddca22c4271a14c10aa130327013ac7cf8daa0b0ae515257e8f28cfad` |
| Original grammar | `RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE` |
| Parameter | `source-time-t`, closed t∈[0,1] |
| Phase in turns | p(t)=t/8 |
| Clamped C1 degree 1 | knots [0,0,1,1], controls [1,1] |
| Clamped S1 degree 1 | knots [0,0,1,1], controls [−1/2,+1/2] |
| Other harmonic channels | absent |
| Internal source knots | none |
| Historical route | V43 `CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED` |

Its physical function follows *directly from the original global source-time Bernstein controls*, without interval remapping:

```text
C1(t) = (1−t)*1 + t*1 = 1
S1(t) = (1−t)*(−1/2) + t*(1/2) = t−1/2
F(t)  = cos(pi*t/4) + (t−1/2)*sin(pi*t/4).
```

The existing [v2 50-source register](pb00701-post-v54-evidence-reconciliation-v2.json), Git blob `e52d3baf3692a011cf86234eeaa992ef407d99fd`, already records this exact source as `COMPLETE_SOURCE_SPECIFIC`. This investigation does **not** create a new original-source proof, restore V43's refused generic route, or change its previously certified zeros.

## The exact obstruction

Write `z=tan(pi*p)=tan(pi*t/8)`. Since the original real t lies in (0,1), we have `0<z<tan(pi/8)`, with **no pole or ambiguity** in the inverse chart. Hence

```text
t = (8/pi)*arctan(z)
cos(pi*t/4) = (1−z²)/(1+z²)
sin(pi*t/4) = 2z/(1+z²).
```

Therefore the *actual original-source* physical function is

```text
F(t(z)) = [1 − z² − z + (16/pi)*z*arctan(z)] / [1+z²].
```

The `(16/pi)*z*arctan(z)` term has a **nonzero coefficient on every open positive z subinterval** and cannot be rationalized by clearing denominators in the Cayley variable.

**Proof of nonrationality.** Suppose the displayed numerator were a rational function R(z) over C(z) on the nonempty real chart interval. Rearranging and dividing by z>0 shows `arctan(z)` equals a rational function on that interval. Differentiate: that rational function would have derivative `1/(1+z²)`. But any derivative of a rational function has **zero residue at every finite pole** (differentiate each term of its finite Laurent principal part). The latter derivative has two simple poles `z=i` and `z=−i`, with nonzero residues

```text
Res(1/(1+z²), i)  =  1/(2i)  = −i/2,
Res(1/(1+z²), −i) = −1/(2i)  = +i/2.
```

Equality on a real interval forces equality of the two rational derivatives as rational functions, contradicting the pole residues. Thus arctan is **not rational**, and the transformed numerator is not rational, over C(z) or Q(pi)(z). In particular, no finite-degree polynomial obtained merely by rational denominator clearing represents the original chart numerator.

This is a strict algebraic falsification, not an unsuccessful solver attempt, floating-point scan or resource limit. It does not establish nonmonotonicity, the exact original-source root count or a universal decision problem. An algorithm retaining `arctan(z)`, using a separate monotonicity/sector proof, or reparametrizing and proving event completeness remains possible.

## Admitted/refused grammar and controls

The public executable checks **one historical source**, with exact canonical source SHA-256, historical row SHA-256, clamped degree-one controls, phase, physical source interval, original V43 refusal, fixed frozen corpus and v2 evidence blobs. Only this source and the fixed bounded nonrationality claim are admitted. Any changed amplitude, phase, source parameter, knot, harmonic inventory, evidence ID, older refusal or continuum status is **REFUSED**; identity-zero and tangent alternatives are therefore negative grammar controls, not claims that they have no roots.

Positive control: the real original source passes the source/evidence admission and exact symbolic derivation. Adversarial controls include changed amplitude to constant (which would admit ordinary Cayley rational polynomialization but must *not* inherit this negative), identity-zero and altered tangency candidates, altered phase and knot semantics, forged V43 status, duplicated source ID, changed denominator, and forged v2 source hashes. This result has no numerical root finder and does not use an isolation budget as a truth criterion. Exact rational work is fixed-size; corpus/evidence enumeration is bounded by 121/50 source records.

Reproduce from repository root:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_v43_cayley_amplitude_boundary.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py --self-test
```

The [machine record](pb00701-v43-cayley-amplitude-boundary.json) binds the same historical identifiers, source grammar, theorem scope and zero-delta before/after ledger. Its claim must be checked against the fresh executable, not used to overwrite the frozen archive.

## Frozen before/after and independent applicability

| Frozen measure | Before | After | Delta |
|---|---:|---:|---:|
| Distinct original v54 cases | 121 | 121 | 0 |
| Refused source routes | 20 | 20 | 0 |
| Missing ordered premises | 30 | 30 | 0 |
| Pre-existing complete source-specific witnesses | 50 | 50 | 0 |

Newly closed historical original IDs: `[]`. All fifty historical original unresolved IDs are already registered source-specifically in v2. The new negative explicitly narrows a proposed **generalization route**, not the supported manufacturing domain or the source-specific source ledger. The original frozen V43 refusal is retained. Evidence is only DETERMINISTIC_MODEL; independent mathematical prose review and CI are not native geometry, independent STEP consumption or engineering-use qualification.

## Implications and critical path

**For OpenSimachinist:** a general event certificate for nonconstant rational B-spline Fourier amplitudes cannot be implemented by direct constant-amplitude Cayley polynomial substitution alone. It needs a genuinely checked analytic completion argument (for instance a source-bounded monotonic/sector isolator, a proved differential-algebraic event algorithm, or independently complete local event producers composed in original time), handling identity-zero, tangencies, close roots and knot sidedness. Do not treat the V43 historical source refusal as mathematical proof of nonmonotonicity.

**For MSAC:** no journal, durable-body, material/topology or output semantics change is authorized. The physical 26-operation coverage and native engineering STEP obligations remain mandatory.

**Remaining:** PB-007-01/02/03/04 and related PO-02/04/05/07/08 OPEN; MC-B/MC-1 NOT_ESTABLISHED; no native/paid or production authorization. Next critical-path step is to specify and qualify an actual *reusable* nonconstant-amplitude event/ordered-sign theorem, then measure newly covered original V43/ordered-premise families against the unmodified frozen corpus. This leaf neither duplicates nor modifies the reserved H0–H2 composer work.
