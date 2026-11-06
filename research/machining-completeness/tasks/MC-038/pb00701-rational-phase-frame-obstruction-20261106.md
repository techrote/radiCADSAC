# MC-038 / PB-007-01 — rational source-time phase-frame obstruction on frozen H1 originals

**Date:** 6 November 2026 UTC. **Status:** precisely bounded negative **C candidate**, pending independent mathematical/source admission. **Evidence class:** `DETERMINISTIC_MODEL`; no native geometry, independent engineering oracle or STEP qualification. **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). **Preimplementation claim:** [#324/6686651025](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6686651025).

## Question and falsifier

Can the sine-bearing first harmonic on an **original source-time span** be converted into one cosine-only H1 term by a coefficient-preserving **rational-function phase frame**?

The proposed route `RATIONAL_SOURCE_TIME_PHASE_FRAME_ERASES_H1_SINE` requires, for rational polynomial coefficient functions `C(t), S(t)` on an original open source span, a rational real function `theta(t) ∈ R(t)` and **any** differentiable real scalar amplitude `A(t)` such that

[
(C(t),S(t))=A(t)(cos	heta(t),sin	heta(t)).
]

This would represent `C cos(2πβ)+S sin(2πβ)` as `A cos(2πβ−theta)` without discarding coefficient orientation. Original rational affine phase `β(t)`, knots, harmonic channels and source time are retained. This challenge does **not** claim that #397, #435 or #436 actually use this route. It tests a proposed rational rephasing extension; #434 excludes constant phase, #435 requires rational **amplitude**, and #436 excludes affine phase with arbitrary amplitude.

The proposal fails if a named original first-span H1 coefficient pair cannot admit rational `theta` even with unrestricted differentiable nonzero amplitude. We require original-source SHA-256 and complete source/row provenance, not invented carrier polynomials or a synthetic test as the deciding witness.

## Exact lemma: the simple-complex-residue obstruction

Let `C=a+bt, S=c+dt` be real rational affine polynomials on a nonempty open interval. Put

[
W = CS'-SC'=ad-bc,qquad q=C^2+S^2.
]

If `W ≠ 0`, `q(t)>0` for every real `t`; the coefficient vector never vanishes. Differentiating the proposed representation gives the **necessary identity**

[
	heta'(t)=rac{W}{q(t)}.
]

For affine coefficients,

[
operatorname{disc}(q)=-4W^2<0.
]

Consequently `q` has two distinct simple complex roots `z`, and `W/q` has a nonzero simple-pole residue `W/q'(z)` at each root. By contrast, the derivative of **any rational function** `theta(t)∈R(t)` has zero residue at every finite complex pole: in its Laurent expansion the only term that could differentiate to `(t-z)^{-1}` is the constant term, whose derivative is zero. Equality on the original real open span would imply equality of rational functions; their pole residues contradict.

Therefore **no rational real source-time phase frame exists for any nonproportional affine rational H1 pair**, with no restriction that `A` be rational. The obstruction is algebraically exact and terminates in a fixed number of rational operations. This does **not** exclude a nonrational phase such as `atan2(S,C)`, alternative harmonic representations, general analytic-event algorithms, or any physical root/order/cell result.

If `W=0`, the test reports **no obstruction established**, not universal admission. In particular, a zero coefficient pair gives no defined orientation and is refused. For the actual V24 control, `C=-S` with `S>0` on the first original span, so `theta=3π/4` and `A=√2 S` explicitly give a valid **constant real** frame; this ensures the classifier does not reject every sine-bearing source.

## Original corpus and source semantics

The immutable v54 corpus Git blob is `5841c331579489b25caef38cd412bdbf286f9134`; the executed v2 complete 50-source register blob is `e52d3baf3692a011cf86234eeaa992ef407d99fd`. All ten selected sources are among the frozen **30 missing ordered-premise originals**. Each retains original `source-time-t ∈ [0,2]`, genuine degree-one H1 spline knot `t=1`, H1 knot vector `[0,0,1,1,2,2]`, original four controls per H1 channel, and its own unchanged rational affine phase. The first span is exactly the affine interpolation of the original first two H1 controls; these are not substituted polynomial fixtures. The executable verifies every source SHA-256 and original row hash against the v2 register before any theorem claim.

| Original owner family (all `composite:PB00701_…`) | First-span `W` | `disc(q)` | Obstruction |
|---|---:|---:|---|
| V13 … `tail100` | -5/4 | -25/4 | Yes |
| V14 … `tail100` | -21/16 | -441/64 | Yes |
| V15 … `tail100` | -85/16 | -7225/64 | Yes |
| V17 … `tail100` | -5/4 | -25/4 | Yes |
| V18 Laurent … `tail100` | -5/4 | -25/4 | Yes |
| V24 … `tail0` | 0 | 0 | **No; valid constant-angle control** |
| V38 … `tail0` | -1/50 | -1/625 | Yes |
| V39 … `tail0` | -1/50 | -1/625 | Yes |
| V40 … `tail0` | 1/5 | -4/25 | Yes |
| V43 … `tail0` | 7/240 | -49/14400 | Yes |

The exact full historical IDs, source SHA-256, original row SHA-256, and verdicts are in [the machine receipt](pb00701-rational-phase-frame-obstruction-20261106.json). V13–V18 include multiharmonic category-3 source/owner gaps. The theorem tests **only the necessary H1 substep**; their other harmonic channels remain intact and are not silently projected away.

## Verification, adversaries and resource boundaries

The executable [source-bound verifier](pb00701_rational_phase_frame_obstruction_20261106.py) checks both historical Git blobs; recomputes the full matched 121-case original identity set and 50 existing complete witnesses; authenticates ten source SHA-256 identities and original row SHA-256 identities; checks the original source-time, phase, knot, H1 controls, first-span affine Wronskian and exact discriminant; and refuses a mismatch with no truth assertion. Its byte-bounded JSON decoder rejects duplicate keys and nonfinite constants. A 256-bit rational input budget is an **ingress/refusal bound**, not a proposed proof of mathematical nonexistence outside the admitted class.

Adversarial tests include changed source controls/phase/knot, the V24 positive control, identity-zero orientation, proportional/repeated-norm-root cases, noncanonical rationals, `2^{-120}` near-proportional coefficients and near-coincident complex norm poles. These do **not** invent physical zeros, tangency multiplicities, signed cells or arbitrarily close **real physical** roots. The proof establishes only an information-preserving phase-frame nonexistence claim for the admitted sources. No numerical root scan, timeout or resource cap is used as mathematical truth.

Commands from the repository root:

```sh
python3 research/machining-completeness/tasks/MC-038/pb00701_rational_phase_frame_obstruction_20261106.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
python3 tools/validate_machining_completeness.py
```

## Matched historical blocker census and nonclaims

| Identical original population and evidence class | Before | After | Delta |
|---|---:|---:|---:|
| Frozen original source IDs | 121 | 121 | 0 |
| Historical V54 route refusals | 20 | 20 | 0 |
| Historical missing ordered premises | 30 | 30 | **0** |
| Preexisting complete signed/source-specific V2 witnesses | 50 | 50 | 0 |
| Required PB/PO discharges | 0 | 0 | 0 |

**New historical ordered-premise closures: zero.** Every selected source was already `COMPLETE_SOURCE_SPECIFIC` in v2; this bounded **C** is a theorem-route obstruction, not a new source witness, A closure, B discharge or generic signed physical event/transfer theorem. PB-007-01/02/03/04 and PO-02/04/05/07/08 remain OPEN. MC-B and MC-1 remain `NOT_ESTABLISHED`, all 26 supported operations remain mandatory, and actual native engineering STEP, durable bodies, journal/topology, production authorization and expensive/native execution remain untouched.

**Next critical path:** preserve coefficient orientation and the original phase law in a genuinely new terminating analytic event and ordered owner/consumer sign-transfer theorem. Review and integration must remain separate from the active #397 exclusive main-write owner. This negative result never authorizes a merge, a programme-status promotion, or domain narrowing.
