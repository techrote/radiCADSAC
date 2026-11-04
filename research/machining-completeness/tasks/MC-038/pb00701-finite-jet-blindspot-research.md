# PB-007-01 — finite endpoint/knot jets cannot certify arbitrary interior event completeness

**Disposition:** mathematically decisive bounded-route falsification (**negative C**), not a PB-007-01 discharge. **Date:** 4 November 2026. **Evidence:** `DETERMINISTIC_MODEL` in exact original-source rational B-spline/affine moving-phase grammar. **Parent:** [MC-038 #100](https://github.com/techrote/radiCADSAC/issues/100). [Preregistered hypothesis](https://github.com/techrote/radiCADSAC/issues/100#issuecomment-6626785215) and [exclusive scoped write claim](https://github.com/techrote/radiCADSAC/issues/324#issuecomment-6626785906).

## Falsified rule

PB-007-01 needs exhaustive zero events and ordered *physical* sign cells. The proposed shortcut is to compare a **fixed finite** number of exact endpoint/true source-knot derivative jets, plus their genuine knot values, and infer that unexamined interior spans contain no additional roots or signs. For unbounded-degree rational B-spline modulation, this rule is **false**. It is not a counterexample to a degree-aware algorithm, to exact interior event isolation or to a correct complete child-proof composer.

Historical frozen anchor: `composite:DELEGATED_V6_CONSTANT_MODULATION:tail0`, SHA-256 `9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1`, interval `[0,2]`, original knot 1, H1 degree-zero constant cosine, phase turns `t/4`, V27 endpoint-multiplicity historical refusal. The historical source is **already fully source-specifically proved** by PRs #307–309 and registered in the v2 fifty-case census. The new **prospective** pair retains original parameter/interval/two-span B-spline grammar and knot but uses phase turns `t/16`; it cannot change or be conflated with the frozen anchor.

## Family and exact Bernstein reconstruction

For any fixed jet budget `N >= 0` and any rational `0 < ε < 1/2`, define `m=N+1`, `d=2m`, `a=1/2−ε`, `b=1/2+ε`, `E(t)=[t(1−t)]^m`, and `E_a=E(a)>0`. Both sources have a global moving phase in **turns** `θ(t)=t/16`; the H1 physical factor is `cos(πt/8)`, strictly positive over `0<=t<=2`.

Their original degree-`d` B-splines share the knot sequence `[0]^(d+1),[1]^d,[2]^(d+1)` with exactly `2d+1` rational controls. The baseline has all controls 1. The adversary differs at **only global control index `m` (zero-based)**, whose value is `1−1/[binom(2m,m) E_a]`.

The full interior knot multiplicity `d` yields two adjacent degree-`d` Bernstein pieces with a shared endpoint control. In the left piece the single changed basis function is exactly `B_(m,2m)(t)=binom(2m,m)t^m(1−t)^m`. Thus the two entire **physical** sources are proven to be:

```text
F(t) = cos(πt/8),                               0 <= t <= 2

G(t) = [1 - E(t)/E_a] cos(πt/8),                0 <= t <= 1
G(t) = cos(πt/8),                              1 <= t <= 2
```

These formulas are *polynomial coefficient identities*, not interpolation/sampling conjectures. The checker independently expands all Bernstein controls to rational power coefficients on **both** original spans and also tests the representation with a separate exact rational Cox–de Boor evaluator.

### Fixed jets are identical but interior events differ

On `[0,1]`, the difference is `G−F = -t^m(1−t)^m cos(πt/8)/E_a`, hence vanishes to order exactly `m` at source endpoint 0 and from the left at the **true original source knot** 1. Its local leading coefficients (excluding the positive cosine factor) are `−1/E_a` and `(-1)^(m+1)/E_a`: both nonzero. All endpoint and one-sided knot derivative jets through `N=m−1` agree exactly, and the full right original span is identical. Both physical knot values are equal and positive with the explicit right-continuous B-spline knot convention; no false smooth multiplicity is claimed.

But `t(1−t)` is strictly rising on `(0,1/2)`, strictly falling on `(1/2,1)`, with unique maximum at `1/2` and reflection symmetry. Therefore `E(t)=E_a` has exactly the two solutions **`a,b`** and no others. Their derivatives are nonzero, so both physical roots are **simple**, and strict positivity of the cosine implies ordered signs **+ / − / +** across those roots. The baseline has **zero roots and only positive signs**. This proves failure of a fixed-jet-only whole-source completion rule for **every** finite N, not merely the tested small values. Choosing positive rational ε arbitrarily close to zero gives arbitrarily close roots invisible to any such fixed endpoint/knot budget.

### Selected exactly reproducible source

`N=8, m=9, degree=18, epsilon=1/1073741824`. The original-source adversary has roots:

```text
a = 536870911/1073741824
b = 536870913/1073741824
distance = 1/536870912
```

Baseline original-source SHA-256: `e49198f9f123c1a15f0ad3747f58c20bb917d843dede8f4a18a1fdc8708cb723`.

Adversary original-source SHA-256: `52af293fcb0df5a3749ff0f311b06995f35dac88367648ef17b2c79020bcfc34`.

The exact machine contract is [`pb00701-finite-jet-blindspot.json`](pb00701-finite-jet-blindspot.json).

## Termination, falsifiers and nonclaims

The symbolic mathematical construction works for every finite `N`, independently of implementation resource limits. The reference checker intentionally admits only `1<=m<=20`, canonical exact rational epsilon, and rational numerator/denominator bit sizes at most 256. Its Bernstein expansion is a finite polynomial number of `Fraction` operations in `2m`. Exceeding limits is a typed `RESOURCE_REFUSAL`/nontruth, never a mathematical nonexistence result. Neither sampling, floating-point proximity, timeout nor an undecided derivative test proves a root or sign.

Adversarial tests cover wrong control, shifted source knot, mismatched phase, original source parameter mutation, float and noncanonical fractions, invalid epsilon, excessive resource budgets, external forged zeros/sign cells, false gate promotion, low/high order jets, independent Cox–de Boor reductions and extremely close exact roots. The first *unmatched* jet at order m is tested, not silently discarded. Complete open-span truth is proved by rational Bernstein identity and elementary exact monotonicity.

This is a **bounded negative C against fixed endpoint/knot jet-only completion**, not a general analytic-event undecidability/impossibility theorem. Degree-aware jets, interior exact Sturm/analytic isolation and adaptive interval proof methods are not falsified.

## Original-source and programme evidence custody

The immutable 121-case v54 corpus Git blob is `5841c331579489b25caef38cd412bdbf286f9134`; the qualified 50-case v2 evidence Git blob is `e52d3baf3692a011cf86234eeaa992ef407d99fd`. The verifier rehashes all 121 distinct original-source JSON specifications; checks all 50 registered case IDs, source hashes, original producer origins, v54 dispositions, intervals and evidence classes; and rejects invalid denominator/claim substitutions. The independent v2 proof registry verifier is rerun in dedicated CI.

| Historical quantity | Before | After | Delta |
|---|---:|---:|---:|
| Frozen original source denominator | 121 | 121 | 0 |
| Frozen route refusals | 20 | 20 | 0 |
| Frozen missing ordered premises | 30 | 30 | 0 |
| Complete post-v54 source-specific evidence | 50 | 50 | 0 |

**New frozen case IDs resolved:** none. Old raw refusals and all existing complete source proofs remain unchanged. No PB-007-01/02/03/04 acceptance; no MC-B or MC-1 acceptance; no native B-rep, material/topology/lineage, engineering STEP, independent consumer, paid/native campaign, production authorization or 26-operation domain alteration. Evidence is `DETERMINISTIC_MODEL`, not native geometry or STEP qualification.

## Reproduction and exact handoff

```sh
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_finite_jet_blindspot.py --contract --self-test
python3 research/machining-completeness/tasks/MC-038/verify_pb00701_post_v54_evidence_reconciliation_v2.py --contract
```

**Critical-path implication:** a reusable moving-phase source composer must consume **independently certified complete open-piece event partitions** (roots, zero components and signs), plus source-bound exact one-sided knot jets and point-policy semantics. A fixed number of endpoint/knot jets alone is not sufficient to infer the interior event set when source degree is unbounded.
