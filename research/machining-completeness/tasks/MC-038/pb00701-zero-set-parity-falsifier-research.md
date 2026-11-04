# MC-038 / PB-007-01 — Original-source zero-set-only sign-transfer falsification

**Status:** bounded exact mathematical negative-C research candidate; integration subject to final-head CI, independent source review and merge checks.  
**Date:** 4 November 2026. **Evidence:** `DETERMINISTIC_MODEL` only.  
**Preregistration:** [MC-038 #100 comment 6622955943](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6622955943).  
**Starting authoritative `main`:** `ca23d722918ec5bd0e2c2a9fddf10c0a66688b6b`.  
**Task:** MC-038 / PB-007-01, category-3 ordered physical sign/event transfer and downstream PO-04/PO-05/PO-08 adjacency, not native material or STEP.

## Precise falsifiable proposal

The **specific unsound shortcut** challenged here is an adapter that obtains an exact complete **distinct closed-source zero set**, original interval, original knot coordinates and affine phase law, then produces ordered physical nonzero sign cells and root multiplicities **without inspecting the source-bound physical amplitude coefficients, exact jets or equivalent parity/sign evidence**.

That information is insufficient. The same exact zero set does not determine physical multiplicity parity or adjacent signs. This is an information-loss counterexample, not a general undecidability theorem; a correct adapter with exact source-bound one-sided jets is not attacked.

## Actual frozen historical anchor

Frozen v54 case `composite:DELEGATED_V6_CONSTANT_MODULATION:tail0`, source SHA-256 `9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1`, original parameter `source-time-t`, closed interval `[0,2]`, real B-spline knot `1`, original phase **turns** `beta=t/4`, and degree-zero H0/H1 cosine spline channels. Both channels are fully clamped with knots `[0,1,2]` and controls H0=`[0,0]`, H1=`[1,1]`.

The physical source is `F_1(t)=cos(pi*t/2)`. Frozen v54 span 0 was V6 CERTIFIED, while span 1 refused `V27_CHILD_LEFT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE`. **Do not amend or call that original refusal solved by this leaf.** Distinct previous accepted PRs #307/#308 supplied exact endpoint jets and source-knot composition: the single physical zero at t=1 has left/right order (1,1), left sign positive, right sign negative. This new negative theorem consumes the same exact frozen original as its m=1 control, not a substitute source.

## Bound original-source family and exact reconstruction

For every integer `1 <= m <= 8`, construct a **different complete original source** on the identical parameter/interval/knot/affine phase:

`F_m(t) = cos(2*pi*beta(t))^m = cos(pi*t/2)^m`.

All amplitudes are rational constants supplied as actual degree-zero two-span full-clamped cosine B-splines. The exact finite Fourier/Laurent identity (with `z=exp(i*x)`, `x=2*pi*beta`) is

`cos(x)^m = ((z+z^(-1))/2)^m = 2^(-m)*SUM_{j=0}^m BINOM(m,j)*z^(m-2j)`.

Pairing terms with exponents ±h gives exact rational cosine coefficients. This is **symbolic algebra**, not evaluation or a numeric trigonometric sample. The separate verifier independently multiplies the two-term Laurent polynomial `(z+z^(-1))/2` m times, rather than trusting the binomial coefficient builder.

Each original channel has equal left/right controls (so both entire original degree-zero pieces have the same value), matching the global analytical `F_m`. The m=1 reconstructed original **must** equal the complete frozen spec byte-canonically and match its source SHA. Each m>1 receives a distinct source SHA and is a NEW prospective source, not one of the 121 frozen cases.

## Exact closed-source roots, multiplicities and signs

Because `x=pi*t/2` maps `t in [0,2]` bijectively to `[0,pi]`, cosine has one and only one zero there: `t=1`. Hence **every m has exactly the same distinct closed-source zero set `{1}` and root cardinality 1**; no extra open-span/exterior zeros or continuum components appear.

Set `u=t-1`. The **exact analytic identity** `cos(pi*(1+u)/2)=-sin(pi*u/2)` yields first nonzero Taylor monomial `(-pi/2)^m*u^m`; `pi/2 != 0`, so its exact root order is `m`. The function is positive on `0<=t<1`; right of the knot it is negative for odd m, positive for even m. The shared actual source-knot zero is one physical zero (not two), with exact left/right orders m, and event CROSSING iff m odd, TOUCHING iff m even.

| m | Same exact distinct zero set | Left order | Right order | Left cell sign | Right cell sign |
|---:|---|---:|---:|---:|---:|
| 1 — actual frozen original | {1} | 1 | 1 | + | − |
| 2 — prospective | {1} | 2 | 2 | + | + |
| 3 — prospective | {1} | 3 | 3 | + | − |
| 4 — prospective | {1} | 4 | 4 | + | + |
| 5–8 — prospective | {1} | m | m | + | (−1)^m |

Thus the exact complete zero set, original knot, source interval, source parameter and phase law **do not functionally determine order or sign transfer**. Source identity/coefficients necessarily differ across the variants, and that difference must be consumed by any sound proof. This cannot be used to falsify a properly source-bound solver that checks complete amplitudes and jets.

## Falsifiers, refusal semantics, reproducibility

Verifier independently checks binomial-vs-convolution Laurent coefficients, replays **actual** pinned v54 and v2 source files and validates all 50 historical case IDs and source SHA-256s, including the exact original source spec, refusal code and 121/20/30 cohort counts. Adversarial mutations modify original controls (including only one side of the knot), phase rate/offset, parameter ID, interval, knots and sine channels; each refuses. Fake root cardinality, physical order, cell sign, historical delta or gate elevation fails full freshly recomputed report equality. Powers outside the bounded 1–8 scope refuse as nontruth; they do not imply zeros are absent.

Run:

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_zero_set_parity_falsifier.py --contract --self-test
```

Machine before/after record: `pb00701-zero-set-parity-falsifier.json`. All calculations require at most eight exact Laurent convolutions and a fixed 121/50 source inventory; the necessary root/sign theorem is analytic and finite, **not** inferred from a resource cap, floating scan, epsilon, timeout or an approximate root isolator.

## Exact historical denominator and evidence classification

Pinned v54 original corpus Git blob: `5841c331579489b25caef38cd412bdbf286f9134`. Pinned v2 supplemental registry Git blob: `e52d3baf3692a011cf86234eeaa992ef407d99`.

| Population | Before | After | Delta |
|---|---:|---:|---:|
| Frozen original sources | 121 | 121 | 0 |
| Historical route-refused sources | 20 | 20 | 0 |
| Historical missing ordered-premise sources | 30 | 30 | 0 |
| Registered complete supplemental original-source proofs | 50 | 50 | 0 |

**Newly changed frozen case IDs:** none. Seven extra prospective variants do **not** increase the historical denominator or the fifty supplemental complete-source witness count. This negative result establishes **C** only upon independent literal-head qualification. It does **not** discharge all required PB-007 grammar or demonstrate fresh frozen-case reduction A; it is not an independent native oracle, material-volume proof, topology or STEP result.

## Programme implications and next critical path

The necessary **new premise** for any full moving-phase original-source zero-component/ordered-cell composition theorem is a source-bound proof object with an exact zero-set type, sorted original-source coordinates, left/right physical root orders or equivalent parity/sign germs at each true knot and exterior, plus explicit continuity and one physical-root deduplication. A polynomial/analytic zero-set set alone is not that object.

PB-007-01, PB-007-02, PB-007-03 and PB-007-04 remain OPEN. MC-B and MC-1 are **NOT_ESTABLISHED**. Preserve all 26 operations, exact journal/source/phase/body/lineage semantics, refusal and UNCERTIFIED states, ordinary engineering STEP obligations and production restrictions. There is no native/paid campaign authorization.
